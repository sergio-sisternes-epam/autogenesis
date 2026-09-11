from __future__ import annotations

import io
import json
import os
import shutil
import sys
import unittest
import uuid
from pathlib import Path

import module_contract


ROOT = Path(__file__).resolve().parents[1]
SCRATCH_ROOT = ROOT / ".module-contract-test-work"
CONTRACT = module_contract.load_invocation_contract(ROOT)


class ScratchMixin:
    def make_workspace(self, name: str) -> Path:
        SCRATCH_ROOT.mkdir(exist_ok=True)
        workspace = SCRATCH_ROOT / f"{name}-{os.getpid()}-{uuid.uuid4().hex}"
        workspace.mkdir(parents=True, exist_ok=False)
        self.addCleanup(self._cleanup_workspace, workspace)
        return workspace

    def _cleanup_workspace(self, workspace: Path) -> None:
        shutil.rmtree(workspace, ignore_errors=True)
        if SCRATCH_ROOT.exists() and not any(SCRATCH_ROOT.iterdir()):
            SCRATCH_ROOT.rmdir()

    def write(self, root: Path, relative: str, content: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class ModuleContractTests(ScratchMixin, unittest.TestCase):
    def test_frozen_scenario_index_constants(self) -> None:
        self.assertEqual(module_contract.SCENARIO_INDEX_SCHEMA, "autogenesis.scenario-index/v1")
        self.assertEqual(len(module_contract.EXPECTED_HISTORICAL_SCENARIOS), 13)
        self.assertEqual(len(module_contract.EXPECTED_SCENARIO_SUCCESSORS), 9)
        self.assertEqual(len(module_contract.EXPECTED_CURRENT_SCENARIOS), 14)

    def argument_lines(self, module_name: str) -> str:
        inventory = CONTRACT.module_arguments[module_name]
        required = ", ".join(f"`{name}`" for name in inventory["required"])
        optional = (
            ", ".join(f"`{name}`" for name in inventory["optional"])
            if inventory["optional"]
            else "none."
        )
        return f"## Arguments\n\n- Required: {required}.\n- Optional: {optional}\n"

    def build_source_fixture(self, root: Path) -> None:
        modules = CONTRACT.modules
        registry_lines = [module_contract.REGISTRY_HEADER, "|--------|------|-------------|------------|"]
        for module_name, role in modules.items():
            registry_lines.append(
                "| "
                f"{module_name} | {role} | {module_name} contract | "
                f"`references/modules/{module_name}/SKILL.md` |"
            )
        root_skill = (
            "---\n"
            "name: autogenesis\n"
            "description: Root skill fixture.\n"
            "version: 0.5.0\n"
            "activation_card: on\n"
            "---\n\n"
            "# autogenesis\n\n"
            + "\n".join(registry_lines)
            + "\n\nSelect current suites through `references/scenarios/suite-index.json`.\n"
        )
        self.write(root, "SKILL.md", root_skill)
        self.write(root, "apm.yml", "name: autogenesis\nversion: 0.5.0\n")
        self.write(root, "README.md", "See `references/scenarios/suite-index.json`.\n")
        self.write(root, "AGENTS.md", "Autogenesis v0.5.0 fixture.\n")
        self.write(root, "CHANGELOG.md", "## [0.5.0]\n")
        self.write(root, "CONTRIBUTING.md", "Use `references/scenarios/suite-index.json`.\n")
        self.write(root, "atlas-mesh.json", '{"stores":[{"id":"github.com/o/r","ref":"main"}]}\n')
        self.write(root, "references/README.md", "Current suites: `scenarios/suite-index.json`.\n")
        self.write(root, "references/aware-hook-template.md", "aware hook\n")
        self.write(root, "references/behaviour-challenge-template.md", "challenge\n")
        self.write(root, "references/run-record-template.md", "See `references/invocation-contract.md`.\n")
        self.write(root, "references/activation-plan-template.md", "activation\n")
        self.write(root, "references/challenge-success-criteria.md", "criteria\n")
        self.write(root, "references/templates/work-node.md", "Plan: `autogenesis/plans/example.md`\n")
        self.write(
            root,
            "references/modules/workflow-discipline/references/invocation-contract.json",
            json.dumps(CONTRACT.data, indent=2, sort_keys=True) + "\n",
        )
        self.write(
            root,
            "references/modules/workflow-discipline/references/invocation-contract.md",
            (
                "See `references/invocation-contract.json` and `SKILL.md`.\n\n"
                "Render visible cards in fenced Markdown code blocks with the `text` info string.\n"
            ),
        )
        self.write(root, "references/modules/patterns/references/activation-card.md", "See `references/invocation-contract.md`.\n")
        self.write(
            root, module_contract.SKILL_MODULE_PATTERN.as_posix(),
            (ROOT / module_contract.SKILL_MODULE_PATTERN).read_text(encoding="utf-8"),
        )
        self.write(root, "references/modules/patterns/references/template.md", "template\n")
        self.write(root, "references/modules/patterns/references/deprecated/panel-review.md", "deprecated\n")
        self.write(root, "references/modules/patterns/references/deprecated/triage-panel.md", "deprecated\n")

        for module_name, role in modules.items():
            body = f"# module\n\n{self.argument_lines(module_name)}\n"
            if module_name == "workflow-discipline":
                body += (
                    "See `references/invocation-contract.md`, `references/invocation-contract.json`, "
                    "`think-challenge/SKILL.md`, `think-grill/SKILL.md`, "
                    "`think-ramble/SKILL.md`, and `<skill_root>/references/scenarios/suite-index.json`.\n"
                )
            elif module_name == "design":
                body += (
                    "See `<skill_root>/references/scenarios/suite-index.json` and "
                    "`knowledge/skill-nesting-invocation-pattern.md`.\n"
                )
            elif module_name == "implement":
                body += "See `<skill_root>/references/scenarios/suite-index.json`.\n"
            elif module_name == "aware-runtime":
                body += "Use `references/aware-hook-template.md`.\n"
            elif module_name == "reflect-challenge":
                body += "Use `references/behaviour-challenge-template.md`.\n"
            elif module_name == "validate-skill-import-links":
                body += "Read `atlas-mesh.json` and `references/paths/mount.md`.\n"
            elif module_name == "learn-skill":
                body += "Use `atlas-mesh.json`.\n"
            elif module_name == "patterns":
                body += "Load `references/activation-card.md`.\n"
                body += (
                    "| B17 | ACTIVATION CARD | Behavioral | active | `references/activation-card.md` |\n"
                    "| autogenesis:S8 | PARENT-ROUTED SKILL MODULE | Structural | draft | "
                    "`references/parent-routed-skill-module.md` |\n"
                    "Draft is not automatic application or promotion.\n"
                )
            if module_name in {"design", "initialise", "review-package"}:
                body += "autogenesis:S8: pattern_applicability and pattern_admission required.\n"
            frontmatter = (
                "---\n"
                f"name: {module_name}\n"
                f"description: {module_name} fixture.\n"
                "metadata:\n"
                "  autogenesis-parent: autogenesis\n"
                f"  autogenesis-role: {role}\n"
                "---\n\n"
                f"{body}"
            )
            self.write(root, f"references/modules/{module_name}/SKILL.md", frontmatter)

        scenario_index = {
            "schema": module_contract.SCENARIO_INDEX_SCHEMA,
            "current": list(module_contract.EXPECTED_CURRENT_SCENARIOS),
            "historical": list(module_contract.EXPECTED_HISTORICAL_SCENARIOS),
            "successors": module_contract.EXPECTED_SCENARIO_SUCCESSORS,
        }
        self.write(
            root,
            "references/scenarios/suite-index.json",
            json.dumps(scenario_index, indent=2, sort_keys=True) + "\n",
        )
        for filename in module_contract.EXPECTED_HISTORICAL_SCENARIOS:
            self.write(
                root,
                f"references/scenarios/{filename}",
                "path_id: legacy\npath_module: references/paths/legacy.md\nexternal_path: https://example.invalid/x\n",
            )
        for filename in module_contract.EXPECTED_CURRENT_SCENARIOS:
            self.write(root, f"references/scenarios/{filename}", "id: current\n")

    def make_request(
        self,
        request_id: str,
        *,
        module: str | None,
        role: str,
        parent_request_id: str | None,
        arguments: dict[str, object],
        subject: str = "github.com/o/r",
        mode: str = "run",
        operation: str | None = None,
        work_id: str | None = "2026-09-11-work",
        atlas_id: str | None = "github.com/o/r",
        atlas_root: str | None = "/atlas/root",
        approval_ref: str | None = None,
    ) -> dict[str, object]:
        effective_operation = operation
        if effective_operation is None:
            effective_operation = module if role != "root" else "design"
        request = {
            "schema": CONTRACT.data["request_schema"],
            "request_id": request_id,
            "parent_request_id": parent_request_id,
            "target": {
                "skill": "autogenesis",
                "module": module,
                "role": role,
            },
            "arguments": arguments,
            "context": {
                "subject": subject,
                "mode": mode,
                "operation": effective_operation,
                "work_id": work_id,
                "atlas_id": atlas_id,
                "atlas_root": atlas_root,
                "approval_ref": approval_ref,
            },
            "resolved": {
                "skill_root": str(ROOT),
                "module_root": None if role == "root" else str(ROOT / "references" / "modules" / str(module)),
                "entrypoint": str(
                    ROOT / ("SKILL.md" if role == "root" else f"references/modules/{module}/SKILL.md")
                ),
            },
        }
        if role == "root":
            request["resolved"]["module_root"] = None
        return request

    def make_receipt(
        self,
        request: dict[str, object],
        *,
        status: str = "completed",
        attempts: list[dict[str, object]] | None = None,
        result: dict[str, object] | None = None,
        evidence: dict[str, object] | None = None,
        gates: dict[str, str] | None = None,
    ) -> dict[str, object]:
        return {
            "schema": CONTRACT.data["receipt_schema"],
            "request_id": request["request_id"],
            "parent_request_id": request["parent_request_id"],
            "target": request["target"],
            "operation": request["context"]["operation"],
            "status": status,
            "attempts": attempts if attempts is not None else [{"number": 1, "outcome": status if status in {"failed", "running"} else "completed"}],
            "result": result if result is not None else {"artifact": "autogenesis/plans/example.md", "disposition": "ok"},
            "evidence": evidence
            if evidence is not None
            else {
                "loaded_entrypoints": [request["resolved"]["entrypoint"]],
                "tool_results": [f"trace:{request['request_id']}"],
                "atlas_root": request["context"]["atlas_root"],
            },
            "gates": gates if gates is not None else {"Enter": "pass", "Change": "pass", "Exit": "pass"},
        }

    def full_card(self, request: dict[str, object], mode: str = "on") -> dict[str, object]:
        return {
            "request_id": request["request_id"],
            "format": "full",
            "mode": mode,
            "fields": {
                "schema": request["schema"],
                "request_id": request["request_id"],
                "parent_request_id": request["parent_request_id"],
                "target": request["target"],
                "operation": request["context"]["operation"],
                "arguments_summary": json.dumps(request["arguments"], sort_keys=True),
                "context_summary": "protected context",
                "entrypoint": request["resolved"]["entrypoint"],
                "atlas_id": request["context"]["atlas_id"],
                "atlas_root": request["context"]["atlas_root"],
                "approval_ref": request["context"]["approval_ref"],
                "state": "requested",
            },
        }

    def compact_card(
        self,
        request: dict[str, object],
        *,
        mode: str = "on",
        debug: bool = False,
        context_summary: str | None = None,
        redactions: list[str] | None = None,
    ) -> dict[str, object]:
        fields: dict[str, object] = {
            "request_id": request["request_id"],
            "parent_request_id": request["parent_request_id"],
            "module": request["target"]["module"],
            "role": request["target"]["role"],
            "operation": request["context"]["operation"],
            "entrypoint": request["resolved"]["entrypoint"],
            "context_ref": f"request:{request['parent_request_id']}",
            "intent": json.dumps(request["arguments"], sort_keys=True),
            "state": "requested",
        }
        if debug:
            fields["context_summary"] = context_summary or "approval_ref=[REDACTED]"
            fields["redactions"] = redactions or ["approval_ref"]
        return {
            "request_id": request["request_id"],
            "format": "compact",
            "mode": mode,
            "fields": fields,
        }

    def make_valid_trace(self, *, activation_mode: str = "on") -> dict[str, object]:
        root_request = self.make_request(
            "root-1",
            module=None,
            role="root",
            parent_request_id=None,
            arguments={"objective": "validate contract"},
            subject="github.com/o/r",
        )
        design_request = self.make_request(
            "design-1",
            module="design",
            role="operation",
            parent_request_id="root-1",
            arguments={"objective": "validate contract"},
            subject="github.com/o/r",
            work_id="2026-09-11-work",
            atlas_id="github.com/o/r",
            atlas_root="/atlas/root",
        )
        support_request = self.make_request(
            "support-1",
            module="workflow-discipline",
            role="support",
            parent_request_id="design-1",
            arguments={"request": {"request_id": "design-1"}, "phase": "enter"},
            subject="github.com/o/r",
            mode="run",
            operation="design",
            work_id="2026-09-11-work",
            atlas_id="github.com/o/r",
            atlas_root="/atlas/root",
        )
        support_receipt = self.make_receipt(
            support_request,
            result={"status": "validated"},
            evidence={
                "loaded_entrypoints": [support_request["resolved"]["entrypoint"]],
                "tool_results": ["validator:ok"],
                "atlas_root": "/atlas/root",
            },
        )
        design_receipt = self.make_receipt(
            design_request,
            result={"artifact": "autogenesis/plans/example.md", "disposition": "awaiting-approval"},
            evidence={
                "loaded_entrypoints": [design_request["resolved"]["entrypoint"]],
                "tool_results": ["plan:persisted"],
                "atlas_root": "/atlas/root",
                "remember": True,
                "compile": True,
            },
        )
        root_receipt = self.make_receipt(
            root_request,
            result={"dispatch": "design"},
            evidence={
                "loaded_entrypoints": [root_request["resolved"]["entrypoint"]],
                "tool_results": ["root:dispatch"],
            },
            gates={"Enter": "pass"},
        )
        trace = {
            "schema": CONTRACT.data["trace_schema"],
            "requests": [root_request, design_request, support_request],
            "receipts": [support_receipt, design_receipt, root_receipt],
            "cards": [],
        }
        if activation_mode in {"on", "debug"}:
            trace["meta"] = {"activation_card": activation_mode}
            trace["cards"] = [
                self.full_card(root_request, activation_mode),
                self.full_card(design_request, activation_mode),
                self.compact_card(
                    support_request,
                    mode=activation_mode,
                    debug=activation_mode == "debug",
                ),
            ]
        elif activation_mode == "off":
            trace["meta"] = {"activation_card": "off"}
        return trace

    def test_inventory_and_owned_exports(self) -> None:
        workspace = self.make_workspace("inventory")
        self.build_source_fixture(workspace)

        report = module_contract.validate_source_tree(workspace)

        self.assertTrue(report.ok, report.as_dict())
        self.assertEqual(report.details["module_count"], 21)
        self.assertEqual(report.details["registry_rows"], 21)
        self.assertEqual(report.details["module_entrypoints"], 21)
        self.assertEqual(report.details["scenario_files"], 27)

    def test_skill_module_pattern_admission(self) -> None:
        workspace = self.make_workspace("pattern-admission")
        self.build_source_fixture(workspace)
        baseline = module_contract.validate_source_tree(workspace)
        self.assertTrue(baseline.ok, baseline.as_dict())
        pattern = workspace / module_contract.SKILL_MODULE_PATTERN
        original = pattern.read_text(encoding="utf-8")
        for old, new in (
            ("status: draft", "status: active"),
            ("catalogue_id: autogenesis:S8", "catalogue_id: genesis:S8"),
        ):
            with self.subTest(change=new):
                pattern.write_text(original.replace(old, new), encoding="utf-8")
                report = module_contract.validate_source_tree(workspace)
                self.assertIn("pattern-admission", {error.code for error in report.errors})
        pattern.write_text(original, encoding="utf-8")
        injector = workspace / "references/modules/patterns/SKILL.md"
        injector.write_text(
            injector.read_text(encoding="utf-8").replace("| active |", "| deprecated |"),
            encoding="utf-8",
        )
        report = module_contract.validate_source_tree(workspace)
        self.assertIn("pattern-index", {error.code for error in report.errors})

    def test_skill_module_pattern_boundaries(self) -> None:
        workspace = self.make_workspace("pattern-boundaries")
        self.build_source_fixture(workspace)
        baseline = module_contract.validate_source_tree(workspace)
        self.assertTrue(baseline.ok, baseline.as_dict())
        pattern = workspace / module_contract.SKILL_MODULE_PATTERN
        original = pattern.read_text(encoding="utf-8")
        for replacement, expected_code in (
            (
                original.replace("The parent owns protected context", "The child owns context"),
                "pattern-boundary",
            ),
            (
                original + "\n```yaml\nschema: autogenesis.invocation-request/v1\n```\n",
                "pattern-schema-copy",
            ),
        ):
            pattern.write_text(replacement, encoding="utf-8")
            report = module_contract.validate_source_tree(workspace)
            self.assertIn(expected_code, {e.code for e in report.errors}, report.as_dict())
        pattern.unlink()
        report = module_contract.validate_source_tree(workspace)
        self.assertIn("pattern-missing", {error.code for error in report.errors})

    def test_skill_module_pattern_selection(self) -> None:
        workspace = self.make_workspace("pattern-selection")
        self.build_source_fixture(workspace)
        report = module_contract.validate_source_tree(workspace)
        self.assertTrue(report.ok, report.as_dict())
        for module in ("design", "initialise", "review-package"):
            with self.subTest(module=module):
                caller = workspace / f"references/modules/{module}/SKILL.md"
                original = caller.read_text(encoding="utf-8")
                caller.write_text(original.replace("pattern_applicability", "unconditional"), encoding="utf-8")
                report = module_contract.validate_source_tree(workspace)
                self.assertIn("pattern-selection", {e.code for e in report.errors})
                caller.write_text(original, encoding="utf-8")
        pattern = workspace / module_contract.SKILL_MODULE_PATTERN
        original = pattern.read_text(encoding="utf-8")
        for clause in (
            "Do not split a short single-purpose procedure",
            "Choose external distribution modules",
        ):
            with self.subTest(near_miss=clause):
                pattern.write_text(original.replace(clause, "Always use S8"), encoding="utf-8")
                report = module_contract.validate_source_tree(workspace)
                self.assertIn("pattern-boundary", {e.code for e in report.errors})

    def test_card_only_completion_rejected(self) -> None:
        trace = self.make_valid_trace()
        design_receipt = trace["receipts"][1]
        design_receipt["evidence"] = {
            "loaded_entrypoints": [trace["requests"][1]["resolved"]["entrypoint"]],
            "atlas_root": "/atlas/root",
        }

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        self.assertIn("card-or-read-only-success", {error.code for error in report.errors})

    def test_retry_safety_budget_and_parent_amplification(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        replay = self.make_request(
            "support-2",
            module="workflow-discipline",
            role="support",
            parent_request_id="design-1",
            arguments={"request": {"request_id": "design-1"}, "phase": "enter"},
            subject="github.com/o/r",
            operation="design",
        )
        trace["requests"].append(replay)
        trace["receipts"][0] = self.make_receipt(
            trace["requests"][2],
            status="failed",
            attempts=[
                {
                    "number": 1,
                    "outcome": "failed",
                    "transient": True,
                    "repeat_safe": True,
                    "retry_owner": "design-1",
                    "reason": "network blip",
                    "repeat_safety_evidence": "read-only validator",
                },
                {"number": 2, "outcome": "failed"},
                {"number": 3, "outcome": "failed"},
            ],
            gates={},
        )
        trace["receipts"].append(
            self.make_receipt(replay, status="blocked", attempts=[], result={"reason": "replayed"}, gates={})
        )

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("max-attempts", codes)
        self.assertIn("request-replay-reset", codes)
        self.assertIn("child-blocks-parent", codes)

    def test_context_override_and_unapproved_implement_rejected(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        implement_without_approval = self.make_request(
            "implement-plain",
            module="implement",
            role="operation",
            parent_request_id="design-1",
            arguments={"plan_ref": "autogenesis/plans/example.md"},
            subject="github.com/o/r",
            work_id="2026-09-11-work",
            atlas_id="github.com/o/r",
            atlas_root="/atlas/root",
            approval_ref=None,
        )
        implement_request = self.make_request(
            "implement-1",
            module="implement",
            role="operation",
            parent_request_id="design-1",
            arguments={"plan_ref": "autogenesis/plans/example.md", "approval_ref": "spoofed"},
            subject="github.com/o/r",
            work_id="2026-09-11-work",
            atlas_id="github.com/o/r",
            atlas_root="/atlas/root",
            approval_ref=None,
        )
        implement_request["context"]["mode"] = "run"
        trace["requests"].append(implement_without_approval)
        trace["requests"].append(implement_request)
        trace["receipts"].append(
            self.make_receipt(
                implement_without_approval,
                evidence={
                    "loaded_entrypoints": [implement_without_approval["resolved"]["entrypoint"]],
                    "tool_results": ["edited:file"],
                    "atlas_root": "/atlas/root",
                    "remember": True,
                    "compile": True,
                },
            )
        )
        trace["receipts"].append(
            self.make_receipt(
                implement_request,
                evidence={
                    "loaded_entrypoints": [implement_request["resolved"]["entrypoint"]],
                    "tool_results": ["edited:file"],
                    "atlas_root": "/atlas/root",
                    "remember": True,
                    "compile": True,
                },
            )
        )

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("protected-context-override", codes)
        self.assertIn("unknown-module-argument", codes)
        self.assertIn("implement-without-approval", codes)

    def test_root_cannot_dispatch_implement_or_change_protected_context(self) -> None:
        root_request = self.make_request(
            "root-direct-implement",
            module=None,
            role="root",
            parent_request_id=None,
            arguments={"objective": "apply a change"},
        )
        implement_request = self.make_request(
            "implement-direct",
            module="implement",
            role="operation",
            parent_request_id="root-direct-implement",
            arguments={"plan_ref": "autogenesis/plans/example.md"},
            work_id="2026-09-11-other-work",
            approval_ref="approved",
        )
        trace = {
            "schema": CONTRACT.data["trace_schema"],
            "requests": [root_request, implement_request],
            "receipts": [
                self.make_receipt(
                    root_request,
                    status="blocked",
                    attempts=[],
                    result={"reason": "direct implement rejected"},
                    evidence={},
                    gates={},
                ),
                self.make_receipt(
                    implement_request,
                    status="blocked",
                    attempts=[],
                    result={"reason": "approved design parent required"},
                    evidence={},
                    gates={},
                ),
            ],
            "cards": [],
            "meta": {"activation_card": "off"},
        }

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("root-implement-transition", codes)
        self.assertIn("root-transition-context", codes)

    def test_live_cutover_external_and_history_boundaries(self) -> None:
        workspace = self.make_workspace("cutover")
        self.build_source_fixture(workspace)
        self.write(
            workspace,
            "references/modules/design/SKILL.md",
            (
                "---\n"
                "name: design\n"
                "description: design fixture.\n"
                "metadata:\n"
                "  autogenesis-parent: autogenesis\n"
                "  autogenesis-role: operation\n"
                "---\n\n"
                "# module\n\n"
                f"{self.argument_lines('design')}\n"
                "See `<skill_root>/references/scenarios/suite-index.json` and `knowledge/skill-nesting-invocation-pattern.md`.\n"
                "autogenesis:S8: pattern_applicability and pattern_admission required.\n"
            ),
        )

        baseline = module_contract.validate_source_tree(workspace)
        self.assertTrue(baseline.ok, baseline.as_dict())

        self.write(workspace, "references/paths/design.md", "legacy path\n")
        report = module_contract.validate_source_tree(workspace)

        self.assertFalse(report.ok)
        self.assertIn("legacy-path-entrypoints", {error.code for error in report.errors})

    def test_source_allows_external_links_and_old_field_names_in_rejection_prose(self) -> None:
        workspace = self.make_workspace("prose-boundary")
        self.build_source_fixture(workspace)
        self.write(
            workspace,
            "README.md",
            (
                "Reject structured `path_id`, `path`, and `path_module` requests.\n"
                "External guidance: https://example.invalid/invocation\n"
            ),
        )

        report = module_contract.validate_source_tree(workspace)

        self.assertTrue(report.ok, report.as_dict())

    def test_source_rejects_argument_inventory_mismatch(self) -> None:
        workspace = self.make_workspace("argument-mismatch")
        self.build_source_fixture(workspace)
        self.write(
            workspace,
            "references/modules/research/SKILL.md",
            (
                "---\n"
                "name: research\n"
                "description: research fixture.\n"
                "metadata:\n"
                "  autogenesis-parent: autogenesis\n"
                "  autogenesis-role: operation\n"
                "---\n\n"
                "# module\n\n"
                "## Arguments\n\n"
                "- Required: `question`.\n"
                "- Optional: `source_material`, `atlas_id`.\n"
            ),
        )

        report = module_contract.validate_source_tree(workspace)

        self.assertFalse(report.ok)
        self.assertIn("module-arguments-mismatch", {error.code for error in report.errors})

    def test_unexpected_module_reports_without_crashing(self) -> None:
        workspace = self.make_workspace("unexpected-module")
        self.build_source_fixture(workspace)
        self.write(
            workspace,
            "references/modules/unexpected/SKILL.md",
            "---\nname: unexpected\ndescription: unexpected fixture.\n---\n",
        )

        report = module_contract.validate_source_tree(workspace)

        self.assertFalse(report.ok)
        self.assertIn("extra-modules", {error.code for error in report.errors})

    def test_current_scenario_references_are_checked_without_rewriting_history(self) -> None:
        workspace = self.make_workspace("scenario-references")
        self.build_source_fixture(workspace)
        baseline = module_contract.validate_source_tree(workspace)
        self.assertTrue(baseline.ok, baseline.as_dict())
        current = "references/scenarios/module-invocation-happy-v1.yaml"
        for reference in (
            "references/modules/missing/SKILL.md",
            "$PKG_subject/references/modules/missing/SKILL.md",
            "references/paths/design.md",
            "references/missing/suite-index.json",
        ):
            with self.subTest(reference=reference):
                self.write(workspace, current, f"cmd: cat {reference}\n")
                report = module_contract.validate_source_tree(workspace)
                self.assertFalse(report.ok)
                self.assertTrue(any(
                    error.code == "missing-reference" and error.location == current
                    for error in report.errors
                ), report.as_dict())

    def test_missing_index_and_removed_owned_path_links_are_rejected(self) -> None:
        workspace = self.make_workspace("missing-live-references")
        self.build_source_fixture(workspace)
        for reference in (
            "suite-index.json",
            "references/missing/suite-index.json",
            "references/paths/design.md",
        ):
            with self.subTest(reference=reference):
                self.write(workspace, "README.md", f"Read `{reference}`.\n")
                report = module_contract.validate_source_tree(workspace)
                self.assertFalse(report.ok)
                self.assertTrue(any(
                    error.code == "missing-reference" and error.location == "README.md"
                    for error in report.errors
                ), report.as_dict())

    def test_external_atlas_paths_remain_allowed_in_current_scenarios(self) -> None:
        workspace = self.make_workspace("external-scenario-references")
        self.build_source_fixture(workspace)
        self.write(
            workspace,
            "references/scenarios/module-invocation-happy-v1.yaml",
            "description: External Atlas uses references/paths/remember.md\n"
            "cmd: cat references/modules/design/SKILL.md\n",
        )
        report = module_contract.validate_source_tree(workspace)
        self.assertTrue(report.ok, report.as_dict())

    def test_card_modes_compact_context_and_redaction(self) -> None:
        absent = self.make_valid_trace(activation_mode="off")
        absent.pop("meta")
        report = module_contract.validate_trace_payload(absent)
        self.assertTrue(report.ok, report.as_dict())

        debug_trace = self.make_valid_trace(activation_mode="debug")
        debug_report = module_contract.validate_trace_payload(debug_trace)
        self.assertTrue(debug_report.ok, debug_report.as_dict())

        leaked = self.make_valid_trace(activation_mode="debug")
        leaked["cards"][2] = self.compact_card(
            leaked["requests"][2],
            mode="debug",
            debug=True,
            context_summary="approval_ref=secret-token",
            redactions=None,
        )
        leaked["requests"][2]["context"]["approval_ref"] = "secret-token"
        leak_report = module_contract.validate_trace_payload(leaked)
        self.assertFalse(leak_report.ok)
        leak_codes = {error.code for error in leak_report.errors}
        self.assertIn("compact-card-debug-context", leak_codes)
        self.assertIn("compact-card-secret-leak", leak_codes)

        disabled = self.make_valid_trace(activation_mode="on")
        disabled["meta"]["activation_card"] = "off"
        disabled_report = module_contract.validate_trace_payload(disabled)
        self.assertFalse(disabled_report.ok)
        self.assertIn("cards-disabled", {error.code for error in disabled_report.errors})

    def test_valid_operation_support_trace(self) -> None:
        trace = self.make_valid_trace()

        report = module_contract.validate_trace_payload(trace)

        self.assertTrue(report.ok, report.as_dict())
        self.assertEqual(report.details["request_count"], 3)
        self.assertEqual(report.details["receipt_count"], 3)
        self.assertEqual(report.details["card_count"], 3)

    def test_one_safe_retry_success(self) -> None:
        trace = self.make_valid_trace()
        trace["receipts"][0] = self.make_receipt(
            trace["requests"][2],
            attempts=[
                {
                    "number": 1,
                    "outcome": "failed",
                    "transient": True,
                    "repeat_safe": True,
                    "retry_owner": "design-1",
                    "reason": "transient cache miss",
                    "repeat_safety_evidence": "read-only validation",
                    "tool_retries": 0,
                },
                {"number": 2, "outcome": "completed"},
            ],
            evidence={
                "loaded_entrypoints": [trace["requests"][2]["resolved"]["entrypoint"]],
                "tool_results": ["validator:retried"],
                "atlas_root": "/atlas/root",
            },
        )

        report = module_contract.validate_trace_payload(trace)

        self.assertTrue(report.ok, report.as_dict())

    def test_trace_rejects_unknown_fields_and_missing_parent(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        trace["unexpected"] = True
        trace["requests"][1]["context"]["extra"] = "nope"
        trace["requests"][2]["parent_request_id"] = "missing-parent"

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("trace-extra-key", codes)
        self.assertIn("request-context-extra", codes)
        self.assertIn("unknown-parent-request", codes)

    def test_source_rejects_unsupported_frontmatter_form(self) -> None:
        with self.assertRaisesRegex(
            module_contract.ContractValidationError,
            "nested mappings deeper than one level are unsupported",
        ):
            module_contract.parse_frontmatter(
                "---\nname: bad\nmetadata:\n  nested:\n    too: deep\n---\n",
                "fixture.md",
            )

    def test_trace_rejects_unknown_module_arguments_for_known_inventory(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        trace["requests"][1]["arguments"]["unexpected"] = True

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        self.assertIn("unknown-module-argument", {error.code for error in report.errors})

    def test_help_and_cli_json_output(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        workspace = self.make_workspace("cli")
        self.build_source_fixture(workspace)
        trace_file = self.write(workspace, "trace.json", json.dumps(self.make_valid_trace(), indent=2))

        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout = stdout
            sys.stderr = stderr
            with self.assertRaises(SystemExit) as help_exit:
                module_contract.main(["--help"])
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr
        self.assertEqual(help_exit.exception.code, 0)
        self.assertIn("source", stdout.getvalue())
        self.assertIn("trace", stdout.getvalue())

        source_stdout = io.StringIO()
        source_stderr = io.StringIO()
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout = source_stdout
            sys.stderr = source_stderr
            source_code = module_contract.main(["source", "--root", str(workspace)])
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr
        self.assertEqual(source_code, 0)
        self.assertTrue(json.loads(source_stdout.getvalue())["ok"])
        self.assertEqual(source_stderr.getvalue(), "")

        trace_stdout = io.StringIO()
        trace_stderr = io.StringIO()
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout = trace_stdout
            sys.stderr = trace_stderr
            trace_code = module_contract.main(["trace", "--input", str(trace_file)])
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr
        self.assertEqual(trace_code, 0)
        self.assertTrue(json.loads(trace_stdout.getvalue())["ok"])
        self.assertEqual(trace_stderr.getvalue(), "")

    def test_completed_receipt_requires_substantive_evidence_and_loaded_entrypoint(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        receipt = trace["receipts"][1]
        receipt["evidence"] = {}

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("missing-loaded-entrypoints", codes)
        self.assertIn("missing-tool-results", codes)
        self.assertIn("operation-atlas-root-mismatch", codes)
        self.assertIn("operation-exit-evidence", codes)

        trace = self.make_valid_trace(activation_mode="off")
        trace["receipts"][1]["evidence"]["loaded_entrypoints"] = ["/other/SKILL.md"]
        report = module_contract.validate_trace_payload(trace)
        self.assertFalse(report.ok)
        self.assertIn("loaded-entrypoint-mismatch", {error.code for error in report.errors})

        deferred = self.make_valid_trace(activation_mode="off")
        deferred["receipts"][1]["evidence"] = {
            "loaded_entrypoints": [deferred["requests"][1]["resolved"]["entrypoint"]],
            "tool_results": ["atlas:remembered"],
            "atlas_root": "/atlas/root",
        }
        deferred["receipts"][1]["result"] = {
            "artifact": "autogenesis/work/2026-09-11-work.md",
            "deferred": "compile deferred pending external maintenance window",
        }
        deferred_report = module_contract.validate_trace_payload(deferred)
        self.assertTrue(deferred_report.ok, deferred_report.as_dict())

    def test_resolved_paths_must_match_target_and_parent_skill_root(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        trace["requests"][2]["resolved"]["entrypoint"] = str(
            ROOT / "references" / "modules" / "implement" / "SKILL.md"
        )
        sibling = self.make_request(
            "support-2",
            module="workflow-discipline",
            role="support",
            parent_request_id="design-1",
            arguments={"request": {"request_id": "design-1"}, "phase": "enter"},
            operation="design",
        )
        sibling["resolved"]["skill_root"] = "/other/root"
        sibling["resolved"]["module_root"] = "/other/root/references/modules/workflow-discipline"
        sibling["resolved"]["entrypoint"] = "/other/root/references/modules/workflow-discipline/SKILL.md"
        trace["requests"].append(sibling)
        trace["receipts"].append(
            self.make_receipt(
                sibling,
                status="blocked",
                attempts=[],
                result={"reason": "validation stopped"},
                evidence={},
                gates={},
            )
        )

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("request-entrypoint-match", codes)
        self.assertIn("parent-skill-root", codes)

    def test_invalid_nested_types_and_missing_trace_file_report_json_errors(self) -> None:
        trace = {
            "schema": CONTRACT.data["trace_schema"],
            "meta": {"activation_card": []},
            "requests": [
                {
                    "schema": CONTRACT.data["request_schema"],
                    "request_id": "broken-request",
                    "parent_request_id": None,
                    "target": {"skill": "autogenesis", "module": None},
                    "arguments": {},
                    "context": [],
                    "resolved": {
                        "skill_root": str(ROOT),
                        "module_root": None,
                        "entrypoint": str(ROOT / "SKILL.md"),
                    },
                }
            ],
            "receipts": [
                {
                    "schema": CONTRACT.data["receipt_schema"],
                    "request_id": "broken-request",
                    "parent_request_id": None,
                    "target": {"skill": "autogenesis", "module": None},
                    "operation": "design",
                    "status": [],
                    "attempts": [{"number": 1, "outcome": []}],
                    "result": {},
                    "evidence": {},
                    "gates": {},
                }
            ],
            "cards": [
                {
                    "request_id": "broken-request",
                    "format": [],
                    "fields": {"request_id": "broken-request", "state": "requested"},
                    "mode": "debug",
                }
            ],
        }

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("trace-meta-mode", codes)
        self.assertIn("request-target-missing", codes)
        self.assertIn("request-context", codes)
        self.assertIn("receipt-status", codes)
        self.assertIn("card-format", codes)

        stdout = io.StringIO()
        stderr = io.StringIO()
        missing_path = ROOT / "does-not-exist-trace.json"
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout = stdout
            sys.stderr = stderr
            exit_code = module_contract.main(["trace", "--input", str(missing_path)])
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr
        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["errors"][0]["code"], "trace-input")
        self.assertIn("unable to read trace input", stderr.getvalue())

    def test_blocked_receipts_allow_attempt_history_but_require_reason(self) -> None:
        root_request = self.make_request(
            "root-blocked",
            module=None,
            role="root",
            parent_request_id=None,
            arguments={"objective": "validate contract"},
        )
        design_request = self.make_request(
            "design-blocked",
            module="design",
            role="operation",
            parent_request_id="root-blocked",
            arguments={"objective": "validate contract"},
        )
        support_request = self.make_request(
            "support-blocked",
            module="workflow-discipline",
            role="support",
            parent_request_id="design-blocked",
            arguments={"request": {"request_id": "design-blocked"}, "phase": "enter"},
            operation="design",
        )
        trace = {
            "schema": CONTRACT.data["trace_schema"],
            "requests": [root_request, design_request, support_request],
            "receipts": [
                self.make_receipt(
                    root_request,
                    status="blocked",
                    attempts=[],
                    result={"reason": "routing paused"},
                    evidence={},
                    gates={},
                ),
                self.make_receipt(
                    design_request,
                    status="blocked",
                    attempts=[],
                    result={"reason": "waiting on support validation"},
                    evidence={},
                    gates={},
                ),
                self.make_receipt(
                    support_request,
                    status="blocked",
                    attempts=[{"number": 1, "outcome": "failed"}],
                    result={"reason": "interrupted after partial tool response"},
                    evidence={
                        "loaded_entrypoints": [support_request["resolved"]["entrypoint"]],
                        "tool_results": ["validator:partial"],
                        "atlas_root": "/atlas/root",
                    },
                    gates={},
                ),
            ],
            "cards": [],
            "meta": {"activation_card": "off"},
        }

        report = module_contract.validate_trace_payload(trace)

        self.assertTrue(report.ok, report.as_dict())

        trace["receipts"][2] = self.make_receipt(
            support_request,
            status="blocked",
            attempts=[],
            result={},
            gates={},
        )
        report = module_contract.validate_trace_payload(trace)
        self.assertFalse(report.ok)
        self.assertIn("blocked-reason", {error.code for error in report.errors})

    def test_failed_and_rejected_receipts_require_reason(self) -> None:
        for status, attempts, expected_code in (
            ("failed", [{"number": 1, "outcome": "failed"}], "failed-reason"),
            ("rejected", [], "rejected-reason"),
        ):
            with self.subTest(status=status):
                trace = self.make_valid_trace(activation_mode="off")
                trace["receipts"][0] = self.make_receipt(
                    trace["requests"][2],
                    status=status,
                    attempts=attempts,
                    result={},
                    evidence={},
                    gates={},
                )

                report = module_contract.validate_trace_payload(trace)

                self.assertFalse(report.ok)
                self.assertIn(expected_code, {error.code for error in report.errors})

    def test_implement_attempts_require_approval_but_preflight_block_remains_valid(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        implement_request = self.make_request(
            "implement-running",
            module="implement",
            role="operation",
            parent_request_id="design-1",
            arguments={"plan_ref": "autogenesis/plans/example.md"},
            approval_ref=None,
        )
        trace["requests"].append(implement_request)
        trace["receipts"].append(
            self.make_receipt(
                implement_request,
                status="running",
                attempts=[{"number": 1, "outcome": "running"}],
                result={"reason": "applying plan"},
                evidence={
                    "loaded_entrypoints": [implement_request["resolved"]["entrypoint"]],
                    "tool_results": ["edit:started"],
                    "atlas_root": "/atlas/root",
                },
                gates={},
            )
        )

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        self.assertIn("implement-without-approval", {error.code for error in report.errors})

        root_request = self.make_request(
            "root-preflight",
            module=None,
            role="root",
            parent_request_id=None,
            arguments={"objective": "validate contract"},
        )
        design_request = self.make_request(
            "design-preflight",
            module="design",
            role="operation",
            parent_request_id="root-preflight",
            arguments={"objective": "validate contract"},
        )
        implement_request = self.make_request(
            "implement-blocked",
            module="implement",
            role="operation",
            parent_request_id="design-preflight",
            arguments={"plan_ref": "autogenesis/plans/example.md"},
            approval_ref=None,
        )
        preflight = {
            "schema": CONTRACT.data["trace_schema"],
            "requests": [root_request, design_request, implement_request],
            "receipts": [
                self.make_receipt(
                    root_request,
                    status="blocked",
                    attempts=[],
                    result={"reason": "routing paused"},
                    evidence={},
                    gates={},
                ),
                self.make_receipt(
                    design_request,
                    status="blocked",
                    attempts=[],
                    result={"reason": "waiting for explicit approval"},
                    evidence={},
                    gates={},
                ),
            ],
            "cards": [],
            "meta": {"activation_card": "off"},
        }
        preflight["receipts"].append(
            self.make_receipt(
                implement_request,
                status="blocked",
                attempts=[],
                result={"reason": "missing explicit approval"},
                evidence={},
                gates={},
            )
        )
        report = module_contract.validate_trace_payload(preflight)
        self.assertTrue(report.ok, report.as_dict())

    def test_discussion_mode_requires_discuss_and_forbids_internal_probe_supports(self) -> None:
        root_request = self.make_request(
            "root-discuss",
            module=None,
            role="root",
            parent_request_id=None,
            arguments={"objective": "explore options"},
            mode="discussion",
            operation="discuss",
            work_id=None,
            atlas_id=None,
            atlas_root=None,
        )
        discuss_request = self.make_request(
            "discuss-1",
            module="discuss",
            role="operation",
            parent_request_id="root-discuss",
            arguments={
                "objective": "explore options",
                "discussion_root": "notes/discussion",
                "current_branch": "feature/x",
            },
            mode="discussion",
            operation="discuss",
            work_id=None,
            atlas_id=None,
            atlas_root=None,
        )
        forbidden_support = self.make_request(
            "grill-1",
            module="think-grill",
            role="support",
            parent_request_id="discuss-1",
            arguments={"topic": "what are we missing?"},
            mode="discussion",
            operation="discuss",
        )
        forbidden_challenge = self.make_request(
            "challenge-1",
            module="think-challenge",
            role="support",
            parent_request_id="discuss-1",
            arguments={"artifact": "autogenesis/plans/example.md"},
            mode="discussion",
            operation="discuss",
        )
        invalid_operation = self.make_request(
            "implement-in-discussion",
            module="implement",
            role="operation",
            parent_request_id="root-discuss",
            arguments={"plan_ref": "autogenesis/plans/example.md"},
            mode="discussion",
            operation="implement",
            approval_ref="approved-but-illegal",
        )
        trace = {
            "schema": CONTRACT.data["trace_schema"],
            "requests": [
                root_request,
                discuss_request,
                forbidden_support,
                forbidden_challenge,
                invalid_operation,
            ],
            "receipts": [
                self.make_receipt(root_request, status="blocked", attempts=[], result={"reason": "routing paused"}, evidence={}, gates={}),
                self.make_receipt(
                    discuss_request,
                    result={"artifact": "autogenesis/work/2026-09-11-work.md", "deferred": "discussion stored without compile"},
                    evidence={
                        "loaded_entrypoints": [discuss_request["resolved"]["entrypoint"]],
                        "tool_results": ["discuss:recorded"],
                        "atlas_root": "/atlas/root",
                    },
                ),
                self.make_receipt(forbidden_support, status="blocked", attempts=[], result={"reason": "forbidden while discuss active"}, evidence={}, gates={}),
                self.make_receipt(forbidden_challenge, status="blocked", attempts=[], result={"reason": "run-only support"}, evidence={}, gates={}),
                self.make_receipt(invalid_operation, status="blocked", attempts=[], result={"reason": "discussion must stay in discuss"}, evidence={}, gates={}),
            ],
            "cards": [],
            "meta": {"activation_card": "off"},
        }

        report = module_contract.validate_trace_payload(trace)

        self.assertFalse(report.ok)
        codes = {error.code for error in report.errors}
        self.assertIn("discussion-support-forbidden", codes)
        self.assertIn("discussion-operation", codes)
        self.assertIn("discussion-target", codes)
        self.assertIn("discussion-implement-effect", codes)

    def test_design_may_transition_to_discussion_and_discuss_requires_discussion_mode(self) -> None:
        trace = self.make_valid_trace(activation_mode="off")
        discuss_request = self.make_request(
            "discuss-from-design",
            module="discuss",
            role="operation",
            parent_request_id="design-1",
            arguments={
                "objective": "resolve a design concern",
                "discussion_root": "notes/discussion",
                "current_branch": "problem",
            },
            mode="discussion",
            operation="discuss",
        )
        trace["requests"].append(discuss_request)
        trace["receipts"].append(
            self.make_receipt(
                discuss_request,
                result={
                    "artifact": "autogenesis/work/2026-09-11-work.md",
                    "deferred": "discussion recorded without additional changes",
                },
                evidence={
                    "loaded_entrypoints": [discuss_request["resolved"]["entrypoint"]],
                    "tool_results": ["discuss:recorded"],
                    "atlas_root": "/atlas/root",
                },
            )
        )

        report = module_contract.validate_trace_payload(trace)
        self.assertTrue(report.ok, report.as_dict())

        discuss_request["context"]["mode"] = "run"
        invalid_report = module_contract.validate_trace_payload(trace)
        self.assertFalse(invalid_report.ok)
        codes = {error.code for error in invalid_report.errors}
        self.assertIn("discuss-mode", codes)
        self.assertIn("design-discussion-mode", codes)


if __name__ == "__main__":
    unittest.main()
