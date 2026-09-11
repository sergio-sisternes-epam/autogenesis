#!/usr/bin/env python3
"""Validate the Autogenesis module source contract and invocation traces."""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROOT_NAME = "autogenesis"
EXPECTED_ROOT_VERSION = "0.5.0"
REGISTRY_HEADER = "| Module | Role | Description | Entrypoint |"
SCENARIO_INDEX_SCHEMA = "autogenesis.scenario-index/v1"
EXPECTED_HISTORICAL_SCENARIOS = (
    "activation-card-extend-adversarial-v1.yaml",
    "atlas-migrate-activation-adherence-v1.yaml",
    "atlas-migrate-activation-adherence-v2.yaml",
    "atlas-storage-semantics-adversarial-v1.yaml",
    "autogenesis-adversarial-v1.yaml",
    "autogenesis-adversarial-v2.yaml",
    "autogenesis-adversarial-v3.yaml",
    "catalogue-review-gate-adversarial-v1.yaml",
    "discuss-activation-adversarial-v1.yaml",
    "discuss-activation-adversarial-v2.yaml",
    "patterns-as-genesis-extension-adversarial-v1.yaml",
    "patterns-module-adversarial-v1.yaml",
    "specify-only-adversarial-v1.yaml",
)
EXPECTED_SCENARIO_SUCCESSORS = {
    "autogenesis-adversarial-v3.yaml": "autogenesis-adversarial-v4.yaml",
    "atlas-migrate-activation-adherence-v2.yaml": (
        "atlas-migrate-activation-adherence-v3.yaml"
    ),
    "discuss-activation-adversarial-v2.yaml": "discuss-activation-adversarial-v3.yaml",
    "activation-card-extend-adversarial-v1.yaml": (
        "activation-card-extend-adversarial-v2.yaml"
    ),
    "atlas-storage-semantics-adversarial-v1.yaml": (
        "atlas-storage-semantics-adversarial-v2.yaml"
    ),
    "catalogue-review-gate-adversarial-v1.yaml": (
        "catalogue-review-gate-adversarial-v2.yaml"
    ),
    "patterns-as-genesis-extension-adversarial-v1.yaml": (
        "patterns-as-genesis-extension-adversarial-v2.yaml"
    ),
    "patterns-module-adversarial-v1.yaml": "patterns-module-adversarial-v2.yaml",
    "specify-only-adversarial-v1.yaml": "specify-only-adversarial-v2.yaml",
}
EXPECTED_NEW_CURRENT_SCENARIOS = (
    "derived-skill-modules-adversarial-v1.yaml",
    "module-invocation-adversarial-v1.yaml",
    "module-invocation-happy-v1.yaml",
    "skill-module-pattern-adversarial-v1.yaml",
    "skill-module-pattern-happy-v1.yaml",
)
SKILL_MODULE_PATTERN = Path(
    "references/modules/patterns/references/parent-routed-skill-module.md"
)
EXPECTED_CURRENT_SCENARIOS = tuple(
    sorted(
        set(EXPECTED_SCENARIO_SUCCESSORS.values())
        | set(EXPECTED_NEW_CURRENT_SCENARIOS)
    )
)
FRONTMATTER_DELIMITER = "---"
KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
LOCAL_REFERENCE_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)|`([^`\n]+)`")
SCENARIO_REFERENCE_PATTERN = re.compile(
    r"(?<![\w/])(?:\$PKG_subject/)?"
    r"(references/[A-Za-z0-9_./-]+\.(?:md|json|yaml|yml))\b"
)
EXTERNAL_ATLAS_REFERENCES = {
    f"references/paths/{name}.md"
    for name in ("mount", "migrate", "remember", "query", "work")
}
MODULE_TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")
ATTEMPT_OUTCOMES = {"running", "failed", "completed"}
ARGUMENT_NAME_PATTERN = re.compile(r"`([^`]+)`")


class ContractValidationError(RuntimeError):
    """Raised when an authority file cannot be loaded."""


@dataclass(frozen=True)
class ValidationMessage:
    code: str
    message: str
    location: str | None = None

    def as_dict(self) -> dict[str, str]:
        data = {"code": self.code, "message": self.message}
        if self.location is not None:
            data["location"] = self.location
        return data


@dataclass
class ValidationReport:
    command: str
    errors: list[ValidationMessage] = field(default_factory=list)
    warnings: list[ValidationMessage] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, code: str, message: str, location: str | None = None) -> None:
        self.errors.append(ValidationMessage(code, message, location))

    def add_warning(self, code: str, message: str, location: str | None = None) -> None:
        self.warnings.append(ValidationMessage(code, message, location))

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "validation_scope": "structural",
            "command": self.command,
            "errors": [item.as_dict() for item in self.errors],
            "warnings": [item.as_dict() for item in self.warnings],
            "details": self.details,
        }


@dataclass(frozen=True)
class ModuleRow:
    module: str
    role: str
    description: str
    entrypoint: str


@dataclass(frozen=True)
class FrontmatterDocument:
    fields: dict[str, Any]
    body: str


@dataclass(frozen=True)
class InvocationContract:
    data: dict[str, Any]

    @property
    def modules(self) -> dict[str, str]:
        value = self.data.get("modules")
        if not isinstance(value, dict):
            raise ContractValidationError("invocation-contract.json: modules must be an object")
        modules = {str(key): str(role) for key, role in value.items()}
        if len(modules) != 21:
            raise ContractValidationError(
                f"invocation-contract.json: expected 21 modules, found {len(modules)}"
            )
        return modules

    @property
    def module_arguments(self) -> dict[str, dict[str, list[str]]]:
        value = self.data.get("module_arguments")
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ContractValidationError(
                "invocation-contract.json: module_arguments must be an object"
            )
        result: dict[str, dict[str, list[str]]] = {}
        for module, inventory in value.items():
            if not isinstance(inventory, dict):
                raise ContractValidationError(
                    f"invocation-contract.json: module_arguments.{module} must be an object"
                )
            required = inventory.get("required")
            optional = inventory.get("optional")
            if not isinstance(required, list) or not all(
                isinstance(item, str) for item in required
            ):
                raise ContractValidationError(
                    f"invocation-contract.json: module_arguments.{module}.required must be a string list"
                )
            if not isinstance(optional, list) or not all(
                isinstance(item, str) for item in optional
            ):
                raise ContractValidationError(
                    f"invocation-contract.json: module_arguments.{module}.optional must be a string list"
                )
            result[str(module)] = {"required": required, "optional": optional}
        if set(result) != set(self.modules):
            missing = sorted(set(self.modules) - set(result))
            extra = sorted(set(result) - set(self.modules))
            pieces = []
            if missing:
                pieces.append(f"missing inventories for {', '.join(missing)}")
            if extra:
                pieces.append(f"unexpected inventories for {', '.join(extra)}")
            raise ContractValidationError(
                "invocation-contract.json: module_arguments must cover all 21 modules"
                + (f" ({'; '.join(pieces)})" if pieces else "")
            )
        return result

    def required_list(self, key: str) -> list[str]:
        value = self.data.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ContractValidationError(
                f"invocation-contract.json: {key} must be a string list"
            )
        return list(value)

    def mapping(self, key: str) -> dict[str, Any]:
        value = self.data.get(key)
        if not isinstance(value, dict):
            raise ContractValidationError(
                f"invocation-contract.json: {key} must be an object"
            )
        return value


@dataclass(frozen=True)
class ParsedRequest:
    data: dict[str, Any]
    index: int


@dataclass(frozen=True)
class ParsedReceipt:
    data: dict[str, Any]
    index: int


@dataclass(frozen=True)
class ParsedCard:
    data: dict[str, Any]
    index: int


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str, location: str) -> FrontmatterDocument:
    if not text.startswith(f"{FRONTMATTER_DELIMITER}\n"):
        raise ContractValidationError(f"{location}: missing opening frontmatter delimiter")
    lines = text.splitlines()
    try:
        end_index = lines.index(FRONTMATTER_DELIMITER, 1)
    except ValueError as error:
        raise ContractValidationError(f"{location}: missing closing frontmatter delimiter") from error
    fields: dict[str, Any] = {}
    current_parent: dict[str, str] | None = None
    current_parent_name: str | None = None
    for line_number, raw_line in enumerate(lines[1:end_index], start=2):
        if not raw_line.strip():
            continue
        if raw_line.startswith("\t"):
            raise ContractValidationError(f"{location}:{line_number}: tabs are not supported")
        if raw_line.startswith("  "):
            if current_parent is None or current_parent_name is None:
                raise ContractValidationError(
                    f"{location}:{line_number}: unexpected indentation"
                )
            if raw_line.startswith("    "):
                raise ContractValidationError(
                    f"{location}:{line_number}: nested mappings deeper than one level are unsupported"
                )
            key, value = split_key_value(raw_line.strip(), location, line_number)
            if key in current_parent:
                raise ContractValidationError(
                    f"{location}:{line_number}: duplicate metadata key {key}"
                )
            current_parent[key] = parse_scalar(value, location, line_number)
            continue
        current_parent = None
        current_parent_name = None
        key, value = split_key_value(raw_line, location, line_number)
        if key in fields:
            raise ContractValidationError(
                f"{location}:{line_number}: duplicate frontmatter key {key}"
            )
        if not value:
            if key != "metadata":
                raise ContractValidationError(
                    f"{location}:{line_number}: unsupported block value for {key}"
                )
            metadata: dict[str, str] = {}
            fields[key] = metadata
            current_parent = metadata
            current_parent_name = key
            continue
        fields[key] = parse_scalar(value, location, line_number)
    body = "\n".join(lines[end_index + 1 :])
    return FrontmatterDocument(fields=fields, body=body)


def split_key_value(line: str, location: str, line_number: int) -> tuple[str, str]:
    if ":" not in line:
        raise ContractValidationError(f"{location}:{line_number}: expected key: value")
    key, value = line.split(":", 1)
    key = key.strip()
    if not KEY_PATTERN.fullmatch(key):
        raise ContractValidationError(
            f"{location}:{line_number}: unsupported key {key!r}"
        )
    return key, value.strip()


def parse_scalar(value: str, location: str, line_number: int) -> Any:
    if value in {"[]", "{}"}:
        raise ContractValidationError(
            f"{location}:{line_number}: list and object literals are unsupported in constrained frontmatter"
        )
    if value.startswith("[") or value.startswith("{"):
        raise ContractValidationError(
            f"{location}:{line_number}: list and object literals are unsupported in constrained frontmatter"
        )
    if value.startswith("|") or value.startswith(">"):
        raise ContractValidationError(
            f"{location}:{line_number}: multiline scalars are unsupported in constrained frontmatter"
        )
    if value.startswith(("'", '"')):
        quote = value[0]
        if not value.endswith(quote) or len(value) == 1:
            raise ContractValidationError(
                f"{location}:{line_number}: unterminated quoted scalar"
            )
        return value[1:-1]
    return value


def build_module_inventory(root_body: str, location: str = "SKILL.md") -> list[ModuleRow]:
    lines = root_body.splitlines()
    try:
        header_index = lines.index(REGISTRY_HEADER)
    except ValueError as error:
        raise ContractValidationError(f"{location}: missing module registry header") from error
    if header_index + 1 >= len(lines) or not lines[header_index + 1].startswith("|-"):
        raise ContractValidationError(f"{location}: malformed module registry separator")
    rows: list[ModuleRow] = []
    for raw_line in lines[header_index + 2 :]:
        if not raw_line.startswith("|"):
            break
        match = MODULE_TABLE_ROW.match(raw_line)
        if not match:
            raise ContractValidationError(f"{location}: malformed module registry row {raw_line!r}")
        module, role, description, entrypoint = [item.strip() for item in match.groups()]
        entrypoint = entrypoint.strip("`")
        rows.append(ModuleRow(module, role, description, entrypoint))
    return rows


def extract_markdown_section(body: str, heading: str) -> str | None:
    lines = body.splitlines()
    header = f"## {heading}"
    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == header:
            start_index = index + 1
            break
    if start_index is None:
        return None
    collected: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip("\n")


def parse_argument_inventory(body: str, location: str) -> dict[str, list[str]]:
    section = extract_markdown_section(body, "Arguments")
    if section is None:
        raise ContractValidationError(f"{location}: missing ## Arguments section")
    bullets = collect_markdown_bullets(section)
    required: list[str] | None = None
    optional: list[str] | None = None
    for bullet in bullets:
        normalized = " ".join(part.strip() for part in bullet.splitlines()).strip()
        if normalized.startswith("- Required"):
            if required is not None:
                raise ContractValidationError(f"{location}: duplicate Required arguments bullet")
            required = extract_argument_names(bullet, location, "Required")
            continue
        if normalized.startswith("- Optional"):
            if optional is not None:
                raise ContractValidationError(f"{location}: duplicate Optional arguments bullet")
            optional = extract_argument_names(bullet, location, "Optional")
    if required is None:
        raise ContractValidationError(f"{location}: missing Required arguments bullet")
    if optional is None:
        raise ContractValidationError(f"{location}: missing Optional arguments bullet")
    return {"required": required, "optional": optional}


def collect_markdown_bullets(section: str) -> list[str]:
    bullets: list[str] = []
    current: list[str] = []
    for raw_line in section.splitlines():
        if raw_line.startswith("- "):
            if current:
                bullets.append("\n".join(current))
            current = [raw_line]
            continue
        if current and (raw_line.startswith("  ") or raw_line.startswith("\t") or not raw_line.strip()):
            current.append(raw_line)
            continue
        if current:
            bullets.append("\n".join(current))
            current = []
    if current:
        bullets.append("\n".join(current))
    return bullets


def extract_argument_names(bullet: str, location: str, label: str) -> list[str]:
    lines = bullet.splitlines()
    filtered_lines = [
        line
        for index, line in enumerate(lines)
        if not (index > 0 and line.strip().startswith("("))
    ]
    names = ARGUMENT_NAME_PATTERN.findall("\n".join(filtered_lines))
    if names:
        return names
    if label == "Optional" and re.search(r"\bnone\b", bullet, re.IGNORECASE):
        return []
    raise ContractValidationError(
        f"{location}: {label} arguments bullet must name fields with backticks"
    )


def load_invocation_contract(root: Path = ROOT) -> InvocationContract:
    root = root.resolve()
    json_path = (
        root
        / "references"
        / "modules"
        / "workflow-discipline"
        / "references"
        / "invocation-contract.json"
    )
    prose_path = json_path.with_suffix(".md")
    module_path = json_path.parents[1] / "SKILL.md"
    for required in (json_path, prose_path, module_path):
        if not required.is_file():
            raise ContractValidationError(f"missing authority file: {required.relative_to(root)}")
    try:
        data = json.loads(read_text(json_path))
    except json.JSONDecodeError as error:
        raise ContractValidationError(
            f"{json_path.relative_to(root)}:{error.lineno}:{error.colno}: invalid JSON"
        ) from error
    if not isinstance(data, dict):
        raise ContractValidationError("invocation-contract.json: top-level JSON value must be an object")
    return InvocationContract(data)


def validate_source_tree(root: Path) -> ValidationReport:
    root = root.resolve()
    report = ValidationReport(command="source")
    report.details["root"] = str(root)
    try:
        contract = load_invocation_contract(root)
    except ContractValidationError as error:
        report.add_error("authority-load", str(error))
        return report

    root_skill_path = root / "SKILL.md"
    if not root_skill_path.is_file():
        report.add_error("missing-root-skill", "SKILL.md is required at the repository root", "SKILL.md")
        return report
    try:
        root_skill = parse_frontmatter(read_text(root_skill_path), "SKILL.md")
        registry_rows = build_module_inventory(root_skill.body)
    except ContractValidationError as error:
        report.add_error("root-structure", str(error), "SKILL.md")
        return report
    validate_root_frontmatter(root_skill, report)
    report.details["registry_rows"] = len(registry_rows)
    validate_registry_rows(root, registry_rows, contract, report)
    validate_apm_manifest(root, report)
    validate_module_entrypoints(root, registry_rows, contract, report)
    validate_legacy_entrypoints(root, report)
    validate_skill_module_pattern(root, report)
    current_suites = validate_scenario_index(root, report)
    validate_references(root, report, current_suites)
    report.details.setdefault("module_count", len(contract.modules))
    return report


def validate_skill_module_pattern(root: Path, report: ValidationReport) -> None:
    relative = SKILL_MODULE_PATTERN.as_posix()
    path = root / SKILL_MODULE_PATTERN
    if not path.is_file():
        report.add_error("pattern-missing", "S8 draft pattern asset is required", relative)
        return
    try:
        document = parse_frontmatter(read_text(path), relative)
    except ContractValidationError as error:
        report.add_error("pattern-frontmatter", str(error), relative)
        return
    expected = {
        "id": "parent-routed-skill-module",
        "catalogue_id": "autogenesis:S8",
        "category": "Structural / Composition",
        "status": "draft",
    }
    for key, value in expected.items():
        if document.fields.get(key) != value:
            report.add_error(
                "pattern-admission", f"S8 {key} must remain {value!r}", relative
            )
    for heading in (
        "Context", "Problem", "Applicability", "Solution", "Invariants",
        "Consequences", "Anti-patterns", "Known uses", "Related patterns", "Sketch",
    ):
        if not extract_markdown_section(document.body, heading):
            report.add_error("pattern-section", f"S8 requires {heading}", relative)
    body = " ".join(document.body.split())
    for clause in (
        "distribution module",
        "no independent module exports or releases",
        "The parent owns protected context",
        "Module reads do not spawn threads or create context isolation",
        "not a security sandbox",
        "not approval or execution evidence",
        "Do not split a short single-purpose procedure",
        "Choose external distribution modules",
        "Draft is not automatic application or promotion",
        "<skill_root>/references/modules/workflow-discipline/SKILL.md",
    ):
        if clause not in body:
            report.add_error("pattern-boundary", f"S8 must state: {clause}", relative)
    if re.search(
        r'(?m)^\s*(?:schema:|"schema":)\s*["\']?autogenesis\.invocation-',
        document.body,
    ):
        report.add_error(
            "pattern-schema-copy", "S8 must reference, not copy, the invocation schema",
            relative,
        )
    injector_path = root / "references/modules/patterns/SKILL.md"
    if injector_path.is_file():
        injector = read_text(injector_path)
        rows = [
            [column.strip().strip("`") for column in line.strip("|").split("|")]
            for line in injector.splitlines() if line.startswith("|")
        ]
        for identity, status, asset in (
            ("B17", "active", "references/activation-card.md"),
            ("autogenesis:S8", "draft", "references/parent-routed-skill-module.md"),
        ):
            matches = [row for row in rows if row[0] == identity]
            if len(matches) != 1 or len(matches[0]) != 5 or matches[0][3:] != [status, asset]:
                report.add_error(
                    "pattern-index", f"Extension index must retain one {identity} {status} entry",
                    "references/modules/patterns/SKILL.md",
                )
        if "Draft is not automatic application or promotion" not in " ".join(injector.split()):
            report.add_error(
                "pattern-admission", "Injector must preserve the draft admission boundary",
                "references/modules/patterns/SKILL.md",
            )
    for module in ("design", "initialise", "review-package"):
        caller_path = root / f"references/modules/{module}/SKILL.md"
        if not caller_path.is_file():
            continue  # Module inventory validation reports missing entrypoints.
        caller = read_text(caller_path)
        for field_name in ("autogenesis:S8", "pattern_applicability", "pattern_admission"):
            if field_name not in caller:
                report.add_error(
                    "pattern-selection", f"{module} must surface {field_name}",
                    caller_path.relative_to(root).as_posix(),
                )


def validate_root_frontmatter(document: FrontmatterDocument, report: ValidationReport) -> None:
    name = document.fields.get("name")
    if name != EXPECTED_ROOT_NAME:
        report.add_error(
            "root-name",
            f"root SKILL.md name must be {EXPECTED_ROOT_NAME!r}, found {name!r}",
            "SKILL.md",
        )
    version = document.fields.get("version")
    if version != EXPECTED_ROOT_VERSION:
        report.add_error(
            "root-version",
            f"root SKILL.md version must be {EXPECTED_ROOT_VERSION!r}, found {version!r}",
            "SKILL.md",
        )
    activation_card = document.fields.get("activation_card")
    if activation_card not in {"off", "on", "debug"}:
        report.add_error(
            "root-activation-card",
            "root SKILL.md activation_card must be off, on, or debug",
            "SKILL.md",
        )
    description = document.fields.get("description")
    if not isinstance(description, str) or not description:
        report.add_error(
            "root-description",
            "root SKILL.md must declare a non-empty description",
            "SKILL.md",
        )


def validate_registry_rows(
    root: Path,
    rows: list[ModuleRow],
    contract: InvocationContract,
    report: ValidationReport,
) -> None:
    expected_modules = contract.modules
    if len(rows) != len(expected_modules):
        report.add_error(
            "registry-count",
            f"root module registry must contain {len(expected_modules)} rows, found {len(rows)}",
            "SKILL.md",
        )
    seen: set[str] = set()
    for row in rows:
        if row.module in seen:
            report.add_error(
                "registry-duplicate",
                f"module registry contains duplicate row for {row.module}",
                "SKILL.md",
            )
            continue
        seen.add(row.module)
        expected_role = expected_modules.get(row.module)
        if expected_role is None:
            report.add_error(
                "registry-unknown-module",
                f"module registry lists unknown module {row.module}",
                "SKILL.md",
            )
            continue
        if row.role != expected_role:
            report.add_error(
                "registry-role",
                f"module registry role for {row.module} must be {expected_role}, found {row.role}",
                "SKILL.md",
            )
        if not row.description:
            report.add_error(
                "registry-description",
                f"module registry row for {row.module} must have a description",
                "SKILL.md",
            )
        expected_entrypoint = f"references/modules/{row.module}/SKILL.md"
        if row.entrypoint != expected_entrypoint:
            report.add_error(
                "registry-entrypoint",
                f"module registry entrypoint for {row.module} must be {expected_entrypoint}, found {row.entrypoint}",
                "SKILL.md",
            )
        if not (root / expected_entrypoint).is_file():
            report.add_error(
                "missing-module-entrypoint",
                f"module registry entrypoint {expected_entrypoint} does not exist",
                expected_entrypoint,
            )
    missing = sorted(set(expected_modules) - seen)
    for module in missing:
        report.add_error(
            "registry-missing-module",
            f"module registry is missing {module}",
            "SKILL.md",
        )


def validate_apm_manifest(root: Path, report: ValidationReport) -> None:
    path = root / "apm.yml"
    if not path.is_file():
        report.add_error("missing-manifest", "apm.yml is required at the repository root", "apm.yml")
        return
    content = read_text(path)
    if "name: autogenesis\n" not in content:
        report.add_error("manifest-name", "apm.yml must declare name: autogenesis", "apm.yml")
    if f"version: {EXPECTED_ROOT_VERSION}\n" not in content:
        report.add_error(
            "manifest-version",
            f"apm.yml must declare version: {EXPECTED_ROOT_VERSION}",
            "apm.yml",
        )


def validate_module_entrypoints(
    root: Path,
    registry_rows: list[ModuleRow],
    contract: InvocationContract,
    report: ValidationReport,
) -> None:
    expected_modules = contract.modules
    actual_files = sorted((root / "references" / "modules").glob("*/SKILL.md"))
    report.details["module_entrypoints"] = len(actual_files)
    actual_names = {path.parent.name for path in actual_files}
    expected_names = set(expected_modules)
    if actual_names != expected_names:
        extra = sorted(actual_names - expected_names)
        missing = sorted(expected_names - actual_names)
        if extra:
            report.add_error(
                "extra-modules",
                f"unexpected module entrypoints: {', '.join(extra)}",
                "references/modules",
            )
        if missing:
            report.add_error(
                "missing-modules",
                f"missing module entrypoints: {', '.join(missing)}",
                "references/modules",
            )
    row_map = {row.module: row for row in registry_rows}
    for path in actual_files:
        module_name = path.parent.name
        relative = path.relative_to(root).as_posix()
        if module_name not in expected_modules:
            # The structural check above already reports the unexpected module.
            # Do not let an unknown entrypoint crash the rest of source validation.
            continue
        try:
            document = parse_frontmatter(read_text(path), relative)
        except ContractValidationError as error:
            report.add_error("module-frontmatter", str(error), relative)
            continue
        if document.fields.get("name") != module_name:
            report.add_error(
                "module-name",
                f"{relative} frontmatter name must be {module_name!r}",
                relative,
            )
        description = document.fields.get("description")
        if not isinstance(description, str) or not description:
            report.add_error(
                "module-description",
                f"{relative} must declare a non-empty description",
                relative,
            )
        metadata = document.fields.get("metadata")
        if not isinstance(metadata, dict):
            report.add_error(
                "module-metadata",
                f"{relative} must declare metadata",
                relative,
            )
            continue
        if metadata.get("autogenesis-parent") != EXPECTED_ROOT_NAME:
            report.add_error(
                "module-parent",
                f"{relative} metadata.autogenesis-parent must be {EXPECTED_ROOT_NAME!r}",
                relative,
            )
        expected_role = expected_modules[module_name]
        if metadata.get("autogenesis-role") != expected_role:
            report.add_error(
                "module-role",
                f"{relative} metadata.autogenesis-role must be {expected_role!r}",
                relative,
            )
        for forbidden in (*contract.data.get("legacy_owned_fields_rejected", []), "internal", "default", "subject_scope"):
            if forbidden in document.fields:
                report.add_error(
                    "legacy-frontmatter-field",
                    f"{relative} must not declare legacy frontmatter field {forbidden}",
                    relative,
                )
        row = row_map.get(module_name)
        if row is not None:
            expected_entrypoint = f"references/modules/{module_name}/SKILL.md"
            if row.entrypoint != expected_entrypoint:
                report.add_error(
                    "row-entrypoint-mismatch",
                    f"registry and file layout disagree for {module_name}",
                    relative,
                )
        try:
            actual_arguments = parse_argument_inventory(document.body, relative)
        except ContractValidationError as error:
            report.add_error("module-arguments", str(error), relative)
            continue
        expected_arguments = contract.module_arguments[module_name]
        if actual_arguments != expected_arguments:
            report.add_error(
                "module-arguments-mismatch",
                f"{relative} Arguments section must match invocation-contract.json for {module_name}",
                relative,
            )


def validate_legacy_entrypoints(root: Path, report: ValidationReport) -> None:
    paths_dir = root / "references" / "paths"
    if paths_dir.exists():
        legacy_paths = sorted(
            path.relative_to(root).as_posix() for path in paths_dir.rglob("*") if path.is_file()
        )
        if legacy_paths:
            report.add_error(
                "legacy-path-entrypoints",
                "legacy references/paths entrypoints must be removed from the live source tree",
                legacy_paths[0],
            )
    loose_modules = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "references" / "modules").glob("*.md")
    )
    if loose_modules:
        report.add_error(
            "legacy-loose-modules",
            "legacy loose references/modules/*.md entrypoints must be removed",
            loose_modules[0],
        )


def live_reference_files(root: Path, current_suites: list[Path]) -> list[Path]:
    files = [
        root / "SKILL.md",
        root / "README.md",
        root / "AGENTS.md",
        root / "CHANGELOG.md",
        root / "CONTRIBUTING.md",
    ]
    references_root = root / "references"
    if references_root.exists():
        files.extend(path for path in references_root.rglob("*.md") if path.is_file())
        suite_index = references_root / "scenarios" / "suite-index.json"
        if suite_index.is_file():
            files.append(suite_index)
    files.extend(current_suites)
    return [path for path in files if path.is_file()]


def validate_references(
    root: Path, report: ValidationReport, current_suites: list[Path]
) -> None:
    for source in live_reference_files(root, current_suites):
        relative = source.relative_to(root).as_posix()
        content = read_text(source)
        tokens = extract_reference_tokens(content)
        if source.suffix == ".yaml":
            tokens.update(SCENARIO_REFERENCE_PATTERN.findall(content))
        for token in sorted(tokens):
            resolved = resolve_reference_target(root, source, token)
            if resolved is None:
                continue
            try:
                resolved.relative_to(root)
            except ValueError:
                report.add_error(
                    "reference-escape",
                    f"{relative} references a path outside the repository: {token}",
                    relative,
                )
                continue
            if not resolved.exists():
                report.add_error(
                    "missing-reference",
                    f"{relative} references missing local asset {token}",
                    relative,
                )


def extract_reference_tokens(content: str) -> set[str]:
    tokens: set[str] = set()
    for match in LOCAL_REFERENCE_PATTERN.finditer(content):
        target = match.group(1) or match.group(2)
        cleaned = target.strip()
        if cleaned:
            tokens.add(cleaned)
    return tokens


def resolve_reference_target(root: Path, source: Path, token: str) -> Path | None:
    cleaned = token.strip()
    if not cleaned:
        return None
    cleaned = cleaned.split()[0]
    cleaned = cleaned.split("#", 1)[0]
    cleaned = cleaned.split("?", 1)[0]
    if not cleaned:
        return None
    if cleaned.startswith(("http://", "https://", "mailto:", "/", "~/")):
        return None
    if cleaned in {"SCHEMA.json"}:
        return None
    if cleaned.startswith(("autogenesis/", "work/", "knowledge/", "assets/")):
        return None
    # These unqualified references belong to the external Atlas contract.
    if cleaned in EXTERNAL_ATLAS_REFERENCES:
        return None
    if any(
        marker in cleaned
        for marker in (
            "<subject>",
            "<candidate-root>",
            "<atlas_root>",
            "<atlas-skill>",
            "<skill>",
            "<module>",
            "$PKG_",
            "*",
        )
    ):
        return None
    if any(char in cleaned for char in ("<", ">")) and not cleaned.startswith("<skill_root>/"):
        return None
    if not (
        cleaned.endswith((".md", ".json", ".yaml", ".yml"))
        or cleaned in {"SKILL.md", "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "AGENTS.md", "apm.yml"}
    ):
        return None
    if "/" not in cleaned and cleaned not in {
        "SKILL.md",
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "AGENTS.md",
        "apm.yml",
        "suite-index.json",
    }:
        return None
    if cleaned.startswith("<skill_root>/"):
        return (root / cleaned.removeprefix("<skill_root>/")).resolve()
    if cleaned.startswith("./") or cleaned.startswith("../"):
        return (source.parent / cleaned).resolve()
    module_local = source.parent / cleaned
    if module_local.exists():
        return module_local.resolve()
    if cleaned.startswith("references/invocation-contract."):
        workflow_companion = (
            root
            / "references"
            / "modules"
            / "workflow-discipline"
            / cleaned
        )
        if workflow_companion.exists():
            return workflow_companion.resolve()
    if cleaned.endswith("/SKILL.md") and "references/modules/" not in cleaned:
        module_sibling = root / "references" / "modules" / cleaned
        if module_sibling.exists():
            return module_sibling.resolve()
    root_relative = root / cleaned
    if root_relative.exists():
        return root_relative.resolve()
    return root_relative.resolve()


def validate_scenario_index(root: Path, report: ValidationReport) -> list[Path]:
    scenarios_root = root / "references" / "scenarios"
    suite_index = scenarios_root / "suite-index.json"
    on_disk = sorted(path.name for path in scenarios_root.glob("*.yaml")) if scenarios_root.exists() else []
    report.details["scenario_files"] = len(on_disk)
    if not suite_index.is_file():
        report.add_error(
            "missing-scenario-index",
            "references/scenarios/suite-index.json is required to classify current and historical suites",
            "references/scenarios/suite-index.json",
        )
        return []
    try:
        payload = json.loads(read_text(suite_index))
    except json.JSONDecodeError as error:
        report.add_error(
            "scenario-index-json",
            f"suite-index.json is not valid JSON ({error.msg})",
            "references/scenarios/suite-index.json",
        )
        return []
    if not isinstance(payload, dict):
        report.add_error(
            "scenario-index-shape",
            "suite-index.json must contain a JSON object",
            "references/scenarios/suite-index.json",
        )
        return []
    allowed_keys = {"schema", "current", "historical", "successors"}
    extra_keys = sorted(set(payload) - allowed_keys)
    if extra_keys:
        report.add_error(
            "scenario-index-extra-key",
            f"suite-index.json has unsupported keys: {', '.join(extra_keys)}",
            "references/scenarios/suite-index.json",
        )
    if payload.get("schema") != SCENARIO_INDEX_SCHEMA:
        report.add_error(
            "scenario-index-schema",
            f"suite-index.json schema must be {SCENARIO_INDEX_SCHEMA!r}",
            "references/scenarios/suite-index.json",
        )
    current = payload.get("current")
    historical = payload.get("historical")
    successors = payload.get("successors")
    if not is_string_list(current):
        report.add_error(
            "scenario-index-current",
            "suite-index.json current must be a string list",
            "references/scenarios/suite-index.json",
        )
        return []
    if not is_string_list(historical):
        report.add_error(
            "scenario-index-historical",
            "suite-index.json historical must be a string list",
            "references/scenarios/suite-index.json",
        )
        return []
    if not isinstance(successors, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in successors.items()
    ):
        report.add_error(
            "scenario-index-successors",
            "suite-index.json successors must be an object mapping strings to strings",
            "references/scenarios/suite-index.json",
        )
        return []
    if len(set(current)) != len(current) or len(set(historical)) != len(historical):
        report.add_error(
            "scenario-index-duplicates",
            "suite-index.json current and historical lists must not contain duplicates",
            "references/scenarios/suite-index.json",
        )
    if set(current) & set(historical):
        report.add_error(
            "scenario-index-overlap",
            "suite-index.json current and historical lists must be disjoint",
            "references/scenarios/suite-index.json",
        )
    if tuple(sorted(historical)) != tuple(sorted(EXPECTED_HISTORICAL_SCENARIOS)):
        report.add_error(
            "scenario-index-historical-set",
            "suite-index.json historical must list the 13 preserved scenario files",
            "references/scenarios/suite-index.json",
        )
    if tuple(sorted(current)) != EXPECTED_CURRENT_SCENARIOS:
        report.add_error(
            "scenario-index-current-set",
            "suite-index.json current must list the approved successors and new scenario suites",
            "references/scenarios/suite-index.json",
        )
    if successors != EXPECTED_SCENARIO_SUCCESSORS:
        report.add_error(
            "scenario-index-successor-map",
            "suite-index.json successors must match the approved 9-family mapping",
            "references/scenarios/suite-index.json",
        )
    indexed_files = set(current) | set(historical)
    disk_files = set(on_disk)
    missing_files = sorted(indexed_files - disk_files)
    extra_files = sorted(disk_files - indexed_files)
    for filename in missing_files:
        report.add_error(
            "missing-scenario-file",
            f"suite-index.json references missing scenario file {filename}",
            f"references/scenarios/{filename}",
        )
    for filename in extra_files:
        report.add_error(
            "unindexed-scenario-file",
            f"scenario file {filename} is not classified by suite-index.json",
            f"references/scenarios/{filename}",
        )
    return [
        scenarios_root / filename
        for filename in current
        if filename in EXPECTED_CURRENT_SCENARIOS
    ]


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def has_non_empty_string_reference(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip()) and "\n" not in value.strip()
    if isinstance(value, list):
        return any(isinstance(item, str) and item.strip() for item in value)
    return False


def has_explicit_deferral_reason(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    for key, item in value.items():
        if "defer" not in str(key).lower():
            continue
        if isinstance(item, str) and item.strip() and "\n" not in item:
            return True
    return False


def has_durable_reference(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    durable_markers = ("artifact", "path", "page", "record", "ref", "memory", "experience")
    for key, item in value.items():
        if any(marker in str(key).lower() for marker in durable_markers) and has_non_empty_string_reference(item):
            return True
    return False


def validate_trace_payload(payload: Any, root: Path = ROOT) -> ValidationReport:
    root = root.resolve()
    report = ValidationReport(command="trace")
    try:
        contract = load_invocation_contract(root)
    except ContractValidationError as error:
        report.add_error("authority-load", str(error))
        return report
    if not isinstance(payload, dict):
        report.add_error("trace-shape", "trace input must be a JSON object")
        return report
    allowed_trace_keys = set(contract.required_list("trace_fields")) | {"meta"}
    extra_keys = sorted(set(payload) - allowed_trace_keys)
    if extra_keys:
        report.add_error(
            "trace-extra-key",
            f"trace envelope has unsupported keys: {', '.join(extra_keys)}",
        )
    if payload.get("schema") != contract.data.get("trace_schema"):
        report.add_error(
            "trace-schema",
            f"trace schema must be {contract.data.get('trace_schema')!r}",
        )
    requests_value = payload.get("requests")
    receipts_value = payload.get("receipts")
    cards_value = payload.get("cards")
    if not isinstance(requests_value, list):
        report.add_error("trace-requests", "trace requests must be a list")
        return report
    if not isinstance(receipts_value, list):
        report.add_error("trace-receipts", "trace receipts must be a list")
        return report
    if not isinstance(cards_value, list):
        report.add_error("trace-cards", "trace cards must be a list")
        return report
    meta = payload.get("meta")
    activation_mode = validate_trace_meta(meta, contract, report)

    requests: list[ParsedRequest] = []
    requests_by_id: dict[str, ParsedRequest] = {}
    request_fingerprints: dict[str, str] = {}
    for index, item in enumerate(requests_value):
        parsed = validate_request(item, index, contract, report)
        if parsed is None:
            continue
        request_id = parsed.data["request_id"]
        if request_id in requests_by_id:
            report.add_error(
                "duplicate-request-id",
                f"request_id {request_id!r} appears more than once",
                f"requests[{index}]",
            )
            continue
        fingerprint = request_fingerprint(parsed.data)
        prior_request = request_fingerprints.get(fingerprint)
        if prior_request is not None:
            report.add_error(
                "request-replay-reset",
                f"request {request_id!r} replays the same parent/module/context as {prior_request!r}; aliases must not reset retry budgets",
                f"requests[{index}]",
            )
        else:
            request_fingerprints[fingerprint] = request_id
        requests.append(parsed)
        requests_by_id[request_id] = parsed

    for parsed in requests:
        validate_request_parent_and_context(parsed, requests_by_id, contract, report)

    receipts: list[ParsedReceipt] = []
    receipts_by_id: dict[str, ParsedReceipt] = {}
    for index, item in enumerate(receipts_value):
        parsed = validate_receipt(item, index, requests_by_id, contract, report)
        if parsed is None:
            continue
        request_id = parsed.data["request_id"]
        if request_id in receipts_by_id:
            report.add_error(
                "duplicate-receipt",
                f"receipt for request_id {request_id!r} appears more than once",
                f"receipts[{index}]",
            )
            continue
        receipts.append(parsed)
        receipts_by_id[request_id] = parsed

    for request_id, request in requests_by_id.items():
        if request_id not in receipts_by_id:
            report.add_error(
                "missing-receipt",
                f"request {request_id!r} is missing a matching receipt",
            )

    cards: list[ParsedCard] = []
    cards_by_id: dict[str, ParsedCard] = {}
    for index, item in enumerate(cards_value):
        parsed = validate_card(item, index, activation_mode, requests_by_id, contract, report)
        if parsed is None:
            continue
        request_id = parsed.data["request_id"]
        if request_id in cards_by_id:
            report.add_error(
                "duplicate-card",
                f"card for request_id {request_id!r} appears more than once",
                f"cards[{index}]",
            )
            continue
        cards.append(parsed)
        cards_by_id[request_id] = parsed

    if activation_mode in {None, "off"} and cards:
        report.add_error(
            "cards-disabled",
            "cards must be absent when activation_card is omitted or off",
        )
    if activation_mode in {"on", "debug"}:
        for request_id, request in requests_by_id.items():
            if request_id not in cards_by_id:
                report.add_error(
                    "missing-card",
                    f"request {request_id!r} is missing its required rendered card",
                )
                continue
            validate_card_correlation(
                cards_by_id[request_id], request, activation_mode, contract, report
            )

    validate_receipt_invariants(requests_by_id, receipts_by_id, report)

    report.details.update(
        {
            "request_count": len(requests_value),
            "receipt_count": len(receipts_value),
            "card_count": len(cards_value),
            "activation_card": activation_mode or "absent",
        }
    )
    return report


def validate_trace_meta(
    meta: Any,
    contract: InvocationContract,
    report: ValidationReport,
) -> str | None:
    if meta is None:
        return None
    if not isinstance(meta, dict):
        report.add_error("trace-meta", "trace meta must be an object when present")
        return None
    allowed = {"activation_card"}
    extra = sorted(set(meta) - allowed)
    if extra:
        report.add_error(
            "trace-meta-extra",
            f"trace meta has unsupported keys: {', '.join(extra)}",
        )
    activation_card = meta.get("activation_card")
    if activation_card is None:
        return None
    valid_modes = set(contract.required_list("card_modes"))
    if not isinstance(activation_card, str) or activation_card not in valid_modes:
        report.add_error(
            "trace-meta-mode",
            f"trace meta activation_card must be one of {sorted(valid_modes)}",
        )
        return None
    return activation_card


def validate_request(
    item: Any,
    index: int,
    contract: InvocationContract,
    report: ValidationReport,
) -> ParsedRequest | None:
    location = f"requests[{index}]"
    if not isinstance(item, dict):
        report.add_error("request-shape", "each request must be an object", location)
        return None
    allowed_keys = set(contract.required_list("request_fields"))
    extra = sorted(set(item) - allowed_keys)
    missing = sorted(allowed_keys - set(item))
    if extra:
        report.add_error(
            "request-extra-key",
            f"request has unsupported keys: {', '.join(extra)}",
            location,
        )
    if missing:
        report.add_error(
            "request-missing-key",
            f"request is missing required keys: {', '.join(missing)}",
            location,
        )
        return None
    if item.get("schema") != contract.data.get("request_schema"):
        report.add_error(
            "request-schema",
            f"request schema must be {contract.data.get('request_schema')!r}",
            location,
        )
    if not isinstance(item.get("request_id"), str) or not item["request_id"]:
        report.add_error(
            "request-id",
            "request_id must be a non-empty string",
            location,
        )
        return None
    target_ok = validate_target(item.get("target"), index, contract, report)
    context_ok = validate_context(item.get("context"), index, contract, report)
    resolved_ok = validate_resolved(
        item.get("resolved"),
        index,
        contract,
        item.get("target"),
        report,
    )
    arguments_ok = validate_arguments(item, index, contract, report)
    if not (target_ok and context_ok and resolved_ok and arguments_ok):
        return None
    return ParsedRequest(item, index)


def validate_target(
    target: Any,
    index: int,
    contract: InvocationContract,
    report: ValidationReport,
) -> bool:
    location = f"requests[{index}].target"
    if not isinstance(target, dict):
        report.add_error("request-target", "target must be an object", location)
        return False
    allowed = set(contract.required_list("target_fields"))
    extra = sorted(set(target) - allowed)
    missing = sorted(allowed - set(target))
    if extra:
        report.add_error("request-target-extra", f"target has unsupported keys: {', '.join(extra)}", location)
    if missing:
        report.add_error("request-target-missing", f"target is missing keys: {', '.join(missing)}", location)
        return False
    if target.get("skill") != EXPECTED_ROOT_NAME:
        report.add_error("request-target-skill", f"target.skill must be {EXPECTED_ROOT_NAME!r}", location)
    role = target.get("role")
    module = target.get("module")
    modules = contract.modules
    if not isinstance(role, str):
        report.add_error("request-target-role-type", "target.role must be a string", location)
        return False
    if role == "root":
        if module is not None:
            report.add_error("root-target-module", "root request target.module must be null", location)
        return module is None
    if not isinstance(module, str) or module not in modules:
        report.add_error("request-target-module", f"target.module must name one of the 21 modules, found {module!r}", location)
        return False
    if role != modules[module]:
        report.add_error("request-target-role", f"target.role for {module} must be {modules[module]!r}", location)
        return False
    return True


def validate_context(
    context: Any,
    index: int,
    contract: InvocationContract,
    report: ValidationReport,
) -> bool:
    location = f"requests[{index}].context"
    if not isinstance(context, dict):
        report.add_error("request-context", "context must be an object", location)
        return False
    allowed = set(contract.required_list("context_fields"))
    extra = sorted(set(context) - allowed)
    missing = sorted(allowed - set(context))
    if extra:
        report.add_error("request-context-extra", f"context has unsupported keys: {', '.join(extra)}", location)
    if missing:
        report.add_error("request-context-missing", f"context is missing keys: {', '.join(missing)}", location)
        return False
    for field_name, value in context.items():
        if value is not None and not isinstance(value, str):
            report.add_error(
                "request-context-type",
                f"context.{field_name} must be a string or null",
                location,
            )
            return False
    return True


def normalize_path_text(value: str) -> str:
    normalized = value.replace("\\", "/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    if len(normalized) > 1:
        normalized = normalized.rstrip("/")
    return normalized


def is_lexically_safe_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    normalized = normalize_path_text(value)
    parts = PurePosixPath(normalized).parts
    return ".." not in parts and "." not in parts


def validate_resolved(
    resolved: Any,
    index: int,
    contract: InvocationContract,
    target: Any,
    report: ValidationReport,
) -> bool:
    location = f"requests[{index}].resolved"
    if not isinstance(resolved, dict):
        report.add_error("request-resolved", "resolved must be an object", location)
        return False
    if not isinstance(target, dict):
        return False
    role = target.get("role")
    module = target.get("module")
    allowed = set(contract.required_list("resolved_fields"))
    extra = sorted(set(resolved) - allowed)
    missing = sorted(allowed - set(resolved))
    if extra:
        report.add_error("request-resolved-extra", f"resolved has unsupported keys: {', '.join(extra)}", location)
    if missing:
        report.add_error("request-resolved-missing", f"resolved is missing keys: {', '.join(missing)}", location)
        return False
    skill_root = resolved.get("skill_root")
    module_root = resolved.get("module_root")
    entrypoint = resolved.get("entrypoint")
    if not is_lexically_safe_path(skill_root):
        report.add_error("request-skill-root", "resolved.skill_root must be a non-empty string", location)
        return False
    if not is_lexically_safe_path(entrypoint):
        report.add_error("request-entrypoint", "resolved.entrypoint must be a portable SKILL.md path", location)
        return False
    normalized_skill_root = normalize_path_text(skill_root)
    normalized_entrypoint = normalize_path_text(entrypoint)
    if role == "root":
        if module_root is not None:
            report.add_error("request-module-root", "root requests must set resolved.module_root to null", location)
            return False
        expected_entrypoint = f"{normalized_skill_root}/SKILL.md"
        if normalized_entrypoint != expected_entrypoint:
            report.add_error(
                "request-entrypoint-match",
                "root resolved.entrypoint must be <skill_root>/SKILL.md",
                location,
            )
            return False
        return True
    if not isinstance(module, str):
        return False
    if not is_lexically_safe_path(module_root):
        report.add_error(
            "request-module-root",
            "resolved.module_root must be a portable module path for non-root requests",
            location,
        )
        return False
    normalized_module_root = normalize_path_text(module_root)
    expected_module_root = f"{normalized_skill_root}/references/modules/{module}"
    expected_entrypoint = f"{expected_module_root}/SKILL.md"
    valid = True
    if normalized_module_root != expected_module_root:
        report.add_error(
            "request-module-root-match",
            f"resolved.module_root must match the target module path for {module}",
            location,
        )
        valid = False
    if normalized_entrypoint != expected_entrypoint:
        report.add_error(
            "request-entrypoint-match",
            f"resolved.entrypoint must match the target module entrypoint for {module}",
            location,
        )
        valid = False
    return valid


def validate_arguments(
    request: dict[str, Any],
    index: int,
    contract: InvocationContract,
    report: ValidationReport,
) -> bool:
    location = f"requests[{index}].arguments"
    arguments = request.get("arguments")
    if not isinstance(arguments, dict):
        report.add_error("request-arguments", "arguments must be an object", location)
        return False
    target = request.get("target")
    if not isinstance(target, dict):
        return False
    role = target.get("role")
    module = target.get("module")
    valid = True
    for forbidden in contract.data.get("legacy_owned_fields_rejected", []):
        if forbidden in arguments:
            report.add_error(
                "legacy-argument-field",
                f"arguments must not use removed owned field {forbidden}",
                location,
            )
            valid = False
    protected = set(contract.required_list("context_fields"))
    protected.update({"path", "path_id", "path_module"})
    illegal_overrides = sorted(protected & set(arguments))
    if illegal_overrides:
        report.add_error(
            "protected-context-override",
            f"arguments must not override protected context fields: {', '.join(illegal_overrides)}",
            location,
        )
        valid = False
    if role == "root":
        return validate_argument_inventory(
            arguments,
            contract.data.get("root_arguments"),
            location,
            report,
        ) and valid
    if not isinstance(module, str):
        return False
    inventory = contract.module_arguments.get(module)
    if inventory is not None:
        return validate_argument_inventory(arguments, inventory, location, report) and valid
    return valid


def validate_argument_inventory(
    arguments: dict[str, Any],
    inventory: Any,
    location: str,
    report: ValidationReport,
) -> bool:
    if not isinstance(inventory, dict):
        report.add_error("argument-inventory", "argument inventory must be an object", location)
        return False
    required = inventory.get("required")
    optional = inventory.get("optional")
    if not is_string_list(required) or not is_string_list(optional):
        report.add_error("argument-inventory-shape", "argument inventory must use required/optional string lists", location)
        return False
    allowed = set(required) | set(optional)
    unknown = sorted(set(arguments) - allowed)
    valid = True
    if unknown:
        report.add_error(
            "unknown-module-argument",
            f"arguments contain unsupported keys: {', '.join(unknown)}",
            location,
        )
        valid = False
    missing = sorted(set(required) - set(arguments))
    if missing:
        report.add_error(
            "missing-module-argument",
            f"arguments are missing required keys: {', '.join(missing)}",
            location,
        )
        valid = False
    return valid


def request_fingerprint(request: dict[str, Any]) -> str:
    payload = {
        "parent_request_id": request.get("parent_request_id"),
        "target": request.get("target"),
        "arguments": request.get("arguments"),
        "context": request.get("context"),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def validate_request_parent_and_context(
    parsed: ParsedRequest,
    requests_by_id: dict[str, ParsedRequest],
    contract: InvocationContract,
    report: ValidationReport,
) -> None:
    request = parsed.data
    location = f"requests[{parsed.index}]"
    parent_request_id = request.get("parent_request_id")
    target = request.get("target")
    context = request.get("context")
    if not isinstance(target, dict) or not isinstance(context, dict):
        return
    role = target.get("role")
    module = target.get("module")
    mode = context.get("mode")
    operation = context.get("operation")
    if mode not in {"run", "discussion"}:
        report.add_error(
            "request-mode",
            "context.mode must be an explicit 'run' or 'discussion' string",
            location,
        )
        return
    if mode == "discussion":
        if operation != "discuss":
            report.add_error(
                "discussion-operation",
                "discussion mode must keep context.operation set to discuss",
                location,
            )
        if module == "implement":
            report.add_error(
                "discussion-implement-effect",
                "discussion mode has zero implement authority or implement effects",
                location,
            )
        if role == "operation" and module != "discuss":
            report.add_error(
                "discussion-target",
                "discussion mode operation requests must target the discuss module",
                location,
            )
        if role == "support" and module in {
            "think-challenge",
            "think-grill",
            "think-ramble",
        }:
            report.add_error(
                "discussion-support-forbidden",
                "Run-only think support modules are forbidden while discuss is active",
                location,
            )
    elif role == "operation" and module == "discuss":
        report.add_error(
            "discuss-mode",
            "the discuss operation must run in discussion mode",
            location,
        )
    if role == "root":
        if parent_request_id is not None:
            report.add_error("root-parent", "root request parent_request_id must be null", location)
        operation_modules = {
            name for name, module_role in contract.modules.items() if module_role == "operation"
        }
        if operation not in operation_modules:
            report.add_error(
                "root-operation",
                "root context.operation must select a registered operation module",
                location,
            )
        elif (mode == "discussion") != (operation == "discuss"):
            report.add_error(
                "root-operation-mode",
                "root must select discuss only in discussion mode and must select discuss in that mode",
                location,
            )
        return
    if not isinstance(parent_request_id, str) or not parent_request_id:
        report.add_error(
            "missing-parent-request",
            "non-root requests must reference an earlier parent_request_id",
            location,
        )
        return
    parent = requests_by_id.get(parent_request_id)
    if parent is None:
        report.add_error(
            "unknown-parent-request",
            f"parent_request_id {parent_request_id!r} does not reference an earlier request",
            location,
        )
        return
    if parent.index >= parsed.index:
        report.add_error(
            "parent-order",
            f"parent_request_id {parent_request_id!r} must refer to an earlier request",
            location,
        )
        return
    parent_target = parent.data.get("target")
    parent_context = parent.data.get("context")
    parent_resolved = parent.data.get("resolved")
    resolved = request.get("resolved")
    if (
        not isinstance(parent_target, dict)
        or not isinstance(parent_context, dict)
        or not isinstance(parent_resolved, dict)
        or not isinstance(resolved, dict)
    ):
        return
    if normalize_path_text(str(resolved.get("skill_root"))) != normalize_path_text(
        str(parent_resolved.get("skill_root"))
    ):
        report.add_error(
            "parent-skill-root",
            "child requests must preserve the loaded parent skill_root",
            location,
        )
    if parent_target.get("role") == "support" and role == "operation":
        report.add_error(
            "support-transition",
            "support requests may not directly spawn a new operation request",
            location,
        )
    if parent_target.get("role") == "root" and role == "support":
        report.add_error(
            "root-support-transition",
            "root may not dispatch support directly without an active operation",
            location,
        )
    protected_fields = contract.required_list("context_fields")
    if role == "support":
        for field_name in protected_fields:
            if context.get(field_name) != parent_context.get(field_name):
                report.add_error(
                    "support-context-override",
                    f"support request changed protected context field {field_name}",
                    location,
                )
        active_operation = parent_context.get("operation")
        if context.get("operation") != active_operation:
            report.add_error(
                "support-operation-override",
                "support requests must preserve the active parent operation",
                location,
            )
        if context.get("operation") == module:
            report.add_warning(
                "support-operation-shadow",
                "support requests should preserve the parent operation rather than replacing it with the support module",
                location,
            )
        if context.get("operation") == "discuss" and module in {"think-grill", "think-ramble"}:
            report.add_error(
                "discussion-support-forbidden",
                "think-grill and think-ramble are forbidden while discuss is active",
                location,
            )
        return
    if role == "operation":
        validate_operation_transition(
            module,
            context,
            parent_target,
            parent_context,
            location,
            report,
        )


def validate_operation_transition(
    module: Any,
    context: dict[str, Any],
    parent_target: dict[str, Any],
    parent_context: dict[str, Any],
    location: str,
    report: ValidationReport,
) -> None:
    if context.get("operation") != module:
        report.add_error(
            "operation-context",
            "operation requests must set context.operation to the target module",
            location,
        )
    parent_role = parent_target.get("role")
    parent_module = parent_target.get("module")
    if parent_role == "root":
        if context.get("subject") in (None, ""):
            report.add_error(
                "root-transition-subject",
                "root-to-operation transitions must declare a subject in protected context",
                location,
            )
        if module == "implement":
            report.add_error(
                "root-implement-transition",
                "root may not dispatch implement directly; implement requires an approved design parent",
                location,
            )
        if module != parent_context.get("operation"):
            report.add_error(
                "root-transition-operation",
                "root must dispatch the operation selected in its protected context",
                location,
            )
        for field_name in ("subject", "mode", "work_id", "atlas_id", "atlas_root"):
            if context.get(field_name) != parent_context.get(field_name):
                report.add_error(
                    "root-transition-context",
                    f"root transition changed protected field {field_name}",
                    location,
                )
        if module == "design" and context.get("work_id") in (None, ""):
            report.add_error(
                "root-transition-work-id",
                "root must assign work_id before dispatching a formal design operation",
                location,
            )
        return
    allowed = {
        ("discuss", "design"),
        ("design", "discuss"),
        ("design", "implement"),
    }
    if (parent_module, module) not in allowed:
        report.add_error(
            "operation-transition",
            f"operation transition {parent_module!r} -> {module!r} is not one of the explicit allowed transitions",
            location,
        )
        return
    for field_name in ("subject", "work_id", "atlas_id", "atlas_root"):
        if context.get(field_name) != parent_context.get(field_name):
            report.add_error(
                "operation-context-ownership",
                f"operation transition changed protected field {field_name}",
                location,
            )
    if parent_module == "discuss" and (
        parent_context.get("mode") != "discussion" or context.get("mode") != "run"
    ):
        report.add_error(
            "discussion-return-mode",
            "discuss -> design must transition from discussion mode back to run",
            location,
        )
    if parent_module == "design" and module == "discuss" and (
        parent_context.get("mode") != "run" or context.get("mode") != "discussion"
    ):
        report.add_error(
            "design-discussion-mode",
            "design -> discuss must transition from run mode into discussion mode",
            location,
        )


def validate_receipt(
    item: Any,
    index: int,
    requests_by_id: dict[str, ParsedRequest],
    contract: InvocationContract,
    report: ValidationReport,
) -> ParsedReceipt | None:
    location = f"receipts[{index}]"
    if not isinstance(item, dict):
        report.add_error("receipt-shape", "each receipt must be an object", location)
        return None
    allowed = set(contract.required_list("receipt_fields"))
    extra = sorted(set(item) - allowed)
    missing = sorted(allowed - set(item))
    if extra:
        report.add_error("receipt-extra-key", f"receipt has unsupported keys: {', '.join(extra)}", location)
    if missing:
        report.add_error("receipt-missing-key", f"receipt is missing required keys: {', '.join(missing)}", location)
        return None
    if item.get("schema") != contract.data.get("receipt_schema"):
        report.add_error(
            "receipt-schema",
            f"receipt schema must be {contract.data.get('receipt_schema')!r}",
            location,
        )
    request_id = item.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        report.add_error("receipt-request-id", "receipt request_id must be a non-empty string", location)
        return None
    status = item.get("status")
    valid_statuses = set(contract.required_list("states")) - {"requested"}
    if not isinstance(status, str) or status not in valid_statuses:
        report.add_error(
            "receipt-status",
            f"receipt status must be one of {sorted(valid_statuses)}",
            location,
        )
        return None
    request = requests_by_id.get(request_id)
    attempts = item.get("attempts")
    if not isinstance(attempts, list):
        report.add_error("receipt-attempts", "receipt attempts must be a list", location)
        return None
    attempts_ok = validate_attempts(attempts, status, request, contract, location, report)
    result = item.get("result")
    evidence = item.get("evidence")
    gates = item.get("gates")
    if not isinstance(result, dict):
        report.add_error("receipt-result", "receipt result must be an object", location)
    if not isinstance(evidence, dict):
        report.add_error("receipt-evidence", "receipt evidence must be an object", location)
    if not isinstance(gates, dict):
        report.add_error("receipt-gates", "receipt gates must be an object", location)
    if request is None:
        report.add_error(
            "receipt-without-request",
            f"receipt {request_id!r} does not match any request",
            location,
        )
        return None
    if item.get("parent_request_id") != request.data.get("parent_request_id"):
        report.add_error(
            "receipt-parent",
            "receipt parent_request_id must match the request",
            location,
        )
    if item.get("target") != request.data.get("target"):
        report.add_error(
            "receipt-target",
            "receipt target must match the request target",
            location,
        )
    if item.get("operation") != request.data.get("context", {}).get("operation"):
        report.add_error(
            "receipt-operation",
            "receipt operation must match request context.operation",
            location,
        )
    if not attempts_ok or not isinstance(result, dict) or not isinstance(evidence, dict) or not isinstance(gates, dict):
        return None
    return ParsedReceipt(item, index)


def validate_attempts(
    attempts: list[Any],
    status: Any,
    request: ParsedRequest | None,
    contract: InvocationContract,
    location: str,
    report: ValidationReport,
) -> bool:
    max_attempts = contract.data.get("max_attempts")
    if not isinstance(max_attempts, int):
        report.add_error("attempt-ceiling", "invocation contract max_attempts must be an integer", location)
        return False
    if status == "rejected":
        if attempts:
            report.add_error(
                "blocked-rejected-attempts",
                "rejected receipts must not record execution attempts",
                location,
            )
            return False
        return True
    if not attempts:
        if status != "blocked":
            report.add_error(
                "missing-attempts",
                f"{status} receipts must record at least one actual attempt",
                location,
            )
            return False
        return True
    valid = True
    if len(attempts) > max_attempts:
        report.add_error(
            "max-attempts",
            f"receipts may record at most {max_attempts} attempts",
            location,
        )
        valid = False
    parent_request_id = request.data.get("parent_request_id") if request is not None else None
    allowed_attempt_fields = set(contract.required_list("attempt_fields"))
    required_attempt_fields = set(contract.required_list("attempt_required_fields"))
    for position, attempt in enumerate(attempts, start=1):
        attempt_location = f"{location}.attempts[{position - 1}]"
        if not isinstance(attempt, dict):
            report.add_error("attempt-shape", "each attempt must be an object", attempt_location)
            valid = False
            continue
        extra = sorted(set(attempt) - allowed_attempt_fields)
        if extra:
            report.add_error(
                "attempt-extra-key",
                f"attempt has unsupported keys: {', '.join(extra)}",
                attempt_location,
            )
            valid = False
        missing_required = sorted(required_attempt_fields - set(attempt))
        if missing_required:
            report.add_error(
                "attempt-missing-key",
                f"attempt is missing required keys: {', '.join(missing_required)}",
                attempt_location,
            )
            valid = False
            continue
        number = attempt.get("number")
        outcome = attempt.get("outcome")
        if number != position:
            report.add_error(
                "attempt-number",
                f"attempt numbers must be consecutive starting at 1; found {number!r}",
                attempt_location,
            )
            valid = False
        if outcome not in ATTEMPT_OUTCOMES:
            report.add_error(
                "attempt-outcome",
                f"attempt outcome must be one of {sorted(ATTEMPT_OUTCOMES)}",
                attempt_location,
            )
            valid = False
    last_outcome = attempts[-1].get("outcome") if isinstance(attempts[-1], dict) else None
    if status == "completed" and last_outcome != "completed":
        report.add_error(
            "receipt-completed-outcome",
            "completed receipts must end with a completed attempt",
            location,
        )
        valid = False
    if status == "failed" and last_outcome != "failed":
        report.add_error(
            "receipt-failed-outcome",
            "failed receipts must end with a failed attempt",
            location,
        )
        valid = False
    if status == "running" and last_outcome != "running":
        report.add_error(
            "receipt-running-outcome",
            "running receipts must end with a running attempt",
            location,
        )
        valid = False
    if status == "blocked" and last_outcome not in {"failed", "running"}:
        report.add_error(
            "receipt-blocked-outcome",
            "blocked receipts with attempts must end with a failed or running attempt",
            location,
        )
        valid = False
    if len(attempts) == 2:
        first = attempts[0]
        if not isinstance(first, dict):
            return False
        if first.get("outcome") != "failed":
            report.add_error(
                "retry-first-outcome",
                "a second attempt is legal only after an observed failed first attempt",
                location,
            )
            valid = False
        required_retry_fields = contract.required_list("retry_evidence_fields")
        missing = [field for field in required_retry_fields if field not in first]
        if missing:
            report.add_error(
                "retry-evidence-fields",
                f"a second attempt requires explicit first-attempt retry evidence: {', '.join(missing)}",
                location,
            )
            valid = False
        if first.get("transient") is not True:
            report.add_error(
                "retry-transient",
                "a second attempt requires transient=true on the failed first attempt",
                location,
            )
            valid = False
        if first.get("repeat_safe") is not True:
            report.add_error(
                "retry-repeat-safe",
                "a second attempt requires repeat_safe=true on the failed first attempt",
                location,
            )
            valid = False
        retry_owner = first.get("retry_owner")
        if not isinstance(retry_owner, str) or not retry_owner:
            report.add_error(
                "retry-owner",
                "a second attempt requires a non-empty retry_owner",
                location,
            )
            valid = False
        elif parent_request_id is not None and retry_owner != parent_request_id:
            report.add_error(
                "retry-owner-parent",
                "retry_owner must be the immediate parent request_id",
                location,
            )
            valid = False
        reason = first.get("reason")
        if not isinstance(reason, str) or not reason:
            report.add_error(
                "retry-reason",
                "a second attempt requires a concrete retry reason",
                location,
            )
            valid = False
        evidence = first.get("repeat_safety_evidence")
        if not isinstance(evidence, str) or not evidence:
            report.add_error(
                "retry-safety-evidence",
                "a second attempt requires repeat_safety_evidence",
                location,
            )
            valid = False
    return valid

def validate_card(
    item: Any,
    index: int,
    activation_mode: str | None,
    requests_by_id: dict[str, ParsedRequest],
    contract: InvocationContract,
    report: ValidationReport,
) -> ParsedCard | None:
    location = f"cards[{index}]"
    if not isinstance(item, dict):
        report.add_error("card-shape", "each card must be an object", location)
        return None
    allowed = set(contract.required_list("card_fields"))
    extra = sorted(set(item) - allowed)
    missing = sorted(set(contract.required_list("trace_card_required_fields")) - set(item))
    if extra:
        report.add_error("card-extra-key", f"card has unsupported keys: {', '.join(extra)}", location)
    if missing:
        report.add_error("card-missing-key", f"card is missing required keys: {', '.join(missing)}", location)
        return None
    request_id = item.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        report.add_error("card-request-id", "card request_id must be a non-empty string", location)
        return None
    format_value = item.get("format")
    valid_formats = set(contract.required_list("card_formats"))
    if not isinstance(format_value, str) or format_value not in valid_formats:
        report.add_error(
            "card-format",
            f"card format must be one of {sorted(valid_formats)}",
            location,
        )
        return None
    fields = item.get("fields")
    if not isinstance(fields, dict):
        report.add_error("card-fields", "card fields must be an object", location)
        return None
    if request_id not in requests_by_id:
        report.add_error("card-unknown-request", f"card request_id {request_id!r} does not match any request", location)
        return None
    mode = item.get("mode")
    if mode is not None:
        if not isinstance(mode, str) or mode not in set(contract.required_list("card_modes")):
            report.add_error("card-mode", "card mode must be off, on, or debug", location)
            return None
        if activation_mode is not None and mode != activation_mode:
            report.add_error(
                "card-mode-mismatch",
                "per-card mode must agree with trace meta activation_card",
                location,
            )
        if activation_mode is None and mode != "off":
            report.add_error(
                "card-hidden-enable",
                "per-card mode cannot enable cards when trace meta omits activation_card",
                location,
            )
    return ParsedCard(item, index)


def validate_card_correlation(
    parsed: ParsedCard,
    request: ParsedRequest,
    activation_mode: str,
    contract: InvocationContract,
    report: ValidationReport,
) -> None:
    card = parsed.data
    request_data = request.data
    target = request_data["target"]
    fields = card["fields"]
    location = f"cards[{parsed.index}]"
    role = target["role"]
    expected_format = "compact" if role == "support" else "full"
    if card.get("format") != expected_format:
        report.add_error(
            "card-role-format",
            f"{role} requests must render {expected_format} cards",
            location,
        )
    required_fields_map = contract.mapping("card_required_fields")
    required_fields = required_fields_map[expected_format]
    allowed_extra = set(contract.mapping("permitted_additional_keys")["card_fields_object"])
    keys = set(fields)
    missing = sorted(set(required_fields) - keys)
    if missing:
        report.add_error(
            "card-required-fields",
            f"card fields are missing required entries: {', '.join(missing)}",
            location,
        )
    unsupported = sorted(keys - set(required_fields) - allowed_extra)
    if unsupported:
        report.add_error(
            "card-fields-extra",
            f"card fields contain unsupported render keys: {', '.join(unsupported)}",
            location,
        )
    if fields.get("state") != "requested":
        report.add_error(
            "card-state",
            "cards are request views and must render state: requested",
            location,
        )
    if expected_format == "full":
        if fields.get("schema") != request_data.get("schema"):
            report.add_error("full-card-schema", "full card schema must match the request schema", location)
        if fields.get("request_id") != request_data.get("request_id"):
            report.add_error("full-card-request-id", "full card request_id must match the request", location)
        if fields.get("parent_request_id") != request_data.get("parent_request_id"):
            report.add_error("full-card-parent", "full card parent_request_id must match the request", location)
        if fields.get("target") != request_data.get("target"):
            report.add_error("full-card-target", "full card target must match the request", location)
        if fields.get("operation") != request_data["context"].get("operation"):
            report.add_error("full-card-operation", "full card operation must match context.operation", location)
        if fields.get("entrypoint") != request_data["resolved"].get("entrypoint"):
            report.add_error("full-card-entrypoint", "full card entrypoint must match resolved.entrypoint", location)
        if fields.get("atlas_id") != request_data["context"].get("atlas_id"):
            report.add_error("full-card-atlas-id", "full card atlas_id must match protected context", location)
        if fields.get("atlas_root") != request_data["context"].get("atlas_root"):
            report.add_error("full-card-atlas-root", "full card atlas_root must match protected context", location)
        if fields.get("approval_ref") != request_data["context"].get("approval_ref"):
            report.add_error("full-card-approval", "full card approval_ref must match protected context", location)
        return
    if fields.get("request_id") != request_data.get("request_id"):
        report.add_error("compact-card-request-id", "compact card request_id must match the request", location)
    if fields.get("parent_request_id") != request_data.get("parent_request_id"):
        report.add_error("compact-card-parent", "compact card parent_request_id must match the request", location)
    if fields.get("module") != target.get("module"):
        report.add_error("compact-card-module", "compact card module must match target.module", location)
    if fields.get("role") != target.get("role"):
        report.add_error("compact-card-role", "compact card role must match target.role", location)
    if fields.get("operation") != request_data["context"].get("operation"):
        report.add_error("compact-card-operation", "compact card operation must match inherited context.operation", location)
    if fields.get("entrypoint") != request_data["resolved"].get("entrypoint"):
        report.add_error("compact-card-entrypoint", "compact card entrypoint must match resolved.entrypoint", location)
    context_ref = fields.get("context_ref")
    if not isinstance(context_ref, str) or request_data["parent_request_id"] not in context_ref:
        report.add_error(
            "compact-card-context-ref",
            "compact support cards must expose a context_ref to the inherited parent context",
            location,
        )
    if activation_mode == "on" and "context_summary" in fields:
        report.add_error(
            "compact-card-on-context",
            "support cards in mode=on must use context_ref instead of inline context_summary",
            location,
        )
    if activation_mode == "debug":
        context_summary = fields.get("context_summary")
        redactions = fields.get("redactions")
        if not isinstance(context_summary, str) or "REDACT" not in context_summary.upper():
            report.add_error(
                "compact-card-debug-context",
                "debug support cards must show a redacted inherited context summary",
                location,
            )
        if redactions is None:
            report.add_error(
                "compact-card-redactions",
                "debug support cards must declare their redactions",
                location,
            )
        approval_ref = request_data["context"].get("approval_ref")
        if (
            isinstance(approval_ref, str)
            and approval_ref
            and isinstance(context_summary, str)
            and approval_ref in context_summary
        ):
            report.add_error(
                "compact-card-secret-leak",
                "debug support cards must not reveal raw protected context values",
                location,
            )


def validate_receipt_invariants(
    requests_by_id: dict[str, ParsedRequest],
    receipts_by_id: dict[str, ParsedReceipt],
    report: ValidationReport,
) -> None:
    for request_id, receipt in receipts_by_id.items():
        request = requests_by_id.get(request_id)
        if request is None:
            continue
        receipt_data = receipt.data
        status = receipt_data["status"]
        evidence = receipt_data.get("evidence")
        gates = receipt_data.get("gates")
        if not isinstance(evidence, dict) or not isinstance(gates, dict):
            continue
        attempts = receipt_data.get("attempts")
        if not isinstance(attempts, list):
            continue
        validate_receipt_reasoning(request, receipt, attempts, report)
        validate_implement_approval_provenance(
            request,
            receipt,
            attempts,
            requests_by_id,
            receipts_by_id,
            report,
        )
        if status == "completed":
            validate_completed_receipt(request, receipt, report)
        if status in {"failed", "blocked", "rejected"}:
            passed = [name for name, value in gates.items() if value == "pass"]
            if passed:
                report.add_error(
                    "failed-gates-pass",
                    f"{status} receipt must not claim completed gates: {', '.join(passed)}",
                    f"receipts[{receipt.index}]",
                )
    children: dict[str, list[str]] = {}
    for request_id, request in requests_by_id.items():
        parent = request.data.get("parent_request_id")
        if isinstance(parent, str):
            children.setdefault(parent, []).append(request_id)
    for parent_id, child_ids in children.items():
        parent_receipt = receipts_by_id.get(parent_id)
        if parent_receipt is None or parent_receipt.data.get("status") != "completed":
            continue
        blocked_children = [
            child_id
            for child_id in child_ids
            if receipts_by_id.get(child_id) is not None
            and receipts_by_id[child_id].data.get("status") != "completed"
        ]
        if blocked_children:
            report.add_error(
                "child-blocks-parent",
                f"completed parent {parent_id!r} depends on incomplete child receipts: {', '.join(blocked_children)}",
                f"receipts[{parent_receipt.index}]",
            )


def validate_completed_receipt(
    request: ParsedRequest,
    receipt: ParsedReceipt,
    report: ValidationReport,
) -> None:
    request_data = request.data
    receipt_data = receipt.data
    location = f"receipts[{receipt.index}]"
    target = request_data.get("target", {})
    context = request_data.get("context", {})
    evidence = receipt_data.get("evidence", {})
    loaded_entrypoints = evidence.get("loaded_entrypoints")
    tool_results = evidence.get("tool_results")
    remember = evidence.get("remember")
    compile_ok = evidence.get("compile")
    result = receipt_data.get("result", {})
    expected_entrypoint = request_data.get("resolved", {}).get("entrypoint")
    if not is_string_list(loaded_entrypoints) or not loaded_entrypoints:
        report.add_error(
            "missing-loaded-entrypoints",
            "completed receipts must record loaded_entrypoints",
            location,
        )
        has_loaded_entrypoints = False
    else:
        has_loaded_entrypoints = True
        if expected_entrypoint not in loaded_entrypoints:
            report.add_error(
                "loaded-entrypoint-mismatch",
                "completed receipts must include the request resolved.entrypoint in loaded_entrypoints",
                location,
            )
    has_tool_results = is_string_list(tool_results) and bool(tool_results)
    if not has_tool_results:
        report.add_error(
            "missing-tool-results",
            "completed receipts must carry non-empty tool_results references",
            location,
        )
    evidence_atlas_root = evidence.get("atlas_root")
    if target.get("role") == "operation":
        if not isinstance(context.get("atlas_root"), str) or not context.get("atlas_root"):
            report.add_error(
                "operation-missing-atlas-root",
                "completed operation receipts require a resolved context.atlas_root",
                location,
            )
        if evidence_atlas_root != context.get("atlas_root"):
            report.add_error(
                "operation-atlas-root-mismatch",
                "completed operation receipts must retain the resolved atlas_root in evidence",
                location,
            )
        durable_deferral = has_explicit_deferral_reason(result) and (
            has_durable_reference(result) or has_durable_reference(evidence)
        )
        compile_path = remember is True and compile_ok is True
        if not compile_path and not durable_deferral:
            report.add_error(
                "operation-exit-evidence",
                "completed operation receipts must prove either remember+compile or an explicit durable deferral reference",
                location,
            )
    elif context.get("atlas_root") in {None, ""} and evidence_atlas_root in {None, ""} and (remember is True or compile_ok is True):
        report.add_error(
            "missing-atlas-root-evidence",
            "completed receipts that claim remember/compile must carry a resolved atlas_root",
            location,
        )
    if has_loaded_entrypoints and not has_tool_results and remember is not True and compile_ok is not True:
        report.add_error(
            "card-or-read-only-success",
            "completed receipts must prove more than card rendering or entrypoint reads",
            location,
        )


def validate_receipt_reasoning(
    request: ParsedRequest,
    receipt: ParsedReceipt,
    attempts: list[Any],
    report: ValidationReport,
) -> None:
    request_data = request.data
    receipt_data = receipt.data
    location = f"receipts[{receipt.index}]"
    target = request_data.get("target", {})
    context = request_data.get("context", {})
    result = receipt_data.get("result", {})
    status = receipt_data.get("status")
    if (
        target.get("module") == "implement"
        and attempts
        and status in {"running", "failed", "blocked", "completed"}
        and not context.get("approval_ref")
    ):
        report.add_error(
            "implement-without-approval",
            "implement cannot record actual attempts without an explicit non-null approval_ref",
            location,
        )
    if status in {"blocked", "failed", "rejected"}:
        reason = result.get("reason") if isinstance(result, dict) else None
        if not isinstance(reason, str) or not reason:
            report.add_error(
                f"{status}-reason",
                f"{status} receipts must carry a concrete reason in result.reason",
                location,
            )
        if status == "blocked" and not attempts:
            return
    if status == "running":
        return


def validate_implement_approval_provenance(
    request: ParsedRequest,
    receipt: ParsedReceipt,
    attempts: list[Any],
    requests_by_id: dict[str, ParsedRequest],
    receipts_by_id: dict[str, ParsedReceipt],
    report: ValidationReport,
) -> None:
    request_data = request.data
    target = request_data.get("target", {})
    if target.get("module") != "implement" or not attempts:
        return
    location = f"receipts[{receipt.index}]"
    approval_ref = request_data.get("context", {}).get("approval_ref")
    parent_request_id = request_data.get("parent_request_id")
    parent_request = requests_by_id.get(parent_request_id)
    parent_receipt = receipts_by_id.get(parent_request_id)
    if (
        not isinstance(approval_ref, str)
        or not approval_ref
        or parent_request is None
        or parent_request.data.get("target", {}).get("module") != "design"
        or parent_receipt is None
    ):
        return
    parent_result = parent_receipt.data.get("result", {})
    approved = (
        parent_receipt.data.get("status") == "completed"
        and isinstance(parent_result, dict)
        and parent_result.get("disposition") == "approved"
        and parent_result.get("approval_ref") == approval_ref
    )
    if not approved:
        report.add_error(
            "implement-approval-provenance",
            "implement approval_ref must match an explicitly approved parent design receipt",
            location,
        )


def load_trace_input(path: Path) -> Any:
    return json.loads(read_text(path))


def emit_report(report: ValidationReport, stderr: io.TextIOBase | None = None) -> int:
    if stderr is None:
        stderr = sys.stderr
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if report.ok:
        return 0
    for error in report.errors:
        prefix = f"{error.location}: " if error.location else ""
        print(f"error: {prefix}{error.code}: {error.message}", file=stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    source_parser = subparsers.add_parser("source", help="validate a candidate source tree")
    source_parser.add_argument("--root", type=Path, required=True, help="repository root to validate")

    trace_parser = subparsers.add_parser("trace", help="validate a captured invocation trace JSON file")
    trace_parser.add_argument("--input", type=Path, required=True, help="trace JSON file")

    args = parser.parse_args(argv)
    if args.command == "source":
        report = validate_source_tree(args.root.resolve())
        return emit_report(report)
    if args.command == "trace":
        try:
            payload = load_trace_input(args.input.resolve())
        except OSError as error:
            report = ValidationReport(command="trace")
            report.add_error(
                "trace-input",
                f"unable to read trace input ({error.strerror})",
                str(args.input),
            )
            return emit_report(report)
        except json.JSONDecodeError as error:
            report = ValidationReport(command="trace")
            report.add_error(
                "trace-json",
                f"trace input is not valid JSON ({error.msg})",
                str(args.input),
            )
            return emit_report(report)
        report = validate_trace_payload(payload)
        return emit_report(report)
    parser.error(f"unsupported command {args.command!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
