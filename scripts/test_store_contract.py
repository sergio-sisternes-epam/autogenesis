from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import store_contract


class StoreContractTests(unittest.TestCase):
    def write_contract(self, root: Path) -> None:
        store = root / store_contract.STORE_PATH
        store.mkdir(parents=True)
        (root / ".gitmodules").write_text(
            '[submodule ".atlas/github.com/sergio-sisternes-epam/autogenesis-atlas"]\n'
            "\tpath = .atlas/github.com/sergio-sisternes-epam/autogenesis-atlas\n"
            "\turl = https://github.com/sergio-sisternes-epam/"
            "autogenesis-atlas.git\n"
            "\tbranch = main\n",
            encoding="utf-8",
        )
        (root / "atlas-mesh.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "stores": [
                        {
                            "id": store_contract.STORE_ID,
                            "ref": "main",
                            "path": store_contract.STORE_PATH.as_posix(),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def test_store_config_and_checkout_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_contract(root)
            with mock.patch.object(
                store_contract,
                "run_git",
                return_value=store_contract.STORE_COMMIT,
            ):
                store_contract.verify_store(root)

    def test_mutable_ref_or_wrong_gitlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_contract(root)
            mesh = root / "atlas-mesh.json"
            mesh.write_text(
                mesh.read_text(encoding="utf-8").replace('"main"', '"v0.9.0"'),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(store_contract.StoreContractError, "not exact"):
                store_contract.verify_store(root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_contract(root)
            with mock.patch.object(store_contract, "run_git", return_value="0" * 40):
                with self.assertRaisesRegex(
                    store_contract.StoreContractError,
                    "checkout",
                ):
                    store_contract.verify_store(root)

    def test_atlas_warning_policy_is_explicit_and_bounded(self) -> None:
        clean = {
            "ok": True,
            "critical": [],
            "warnings": [],
            "staging_count": 0,
        }
        self.assertEqual(
            store_contract.validate_payload(clean, 0, set(), "compile"),
            (),
        )
        warning = {
            **clean,
            "warnings": [{"id": "atlas_uri_unmounted"}],
        }
        with self.assertRaisesRegex(store_contract.StoreContractError, "unreviewed"):
            store_contract.validate_payload(warning, 1, set(), "compile")
        self.assertEqual(
            store_contract.validate_payload(
                warning,
                1,
                {"atlas_uri_unmounted"},
                "compile",
            ),
            ("atlas_uri_unmounted",),
        )


if __name__ == "__main__":
    unittest.main()
