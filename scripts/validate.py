#!/usr/bin/env python3
"""Check examples/index.json against the evidence-index schema.

Stdlib only. Enforces the keywords this schema uses: type, const, required,
properties, additionalProperties, items, $ref, minItems, minLength, pattern,
and format uri. Also checks that each evidence_export.stub file exists.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "evidence-index.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "index.json"


class ValidationError(Exception):
    pass


def resolve(schema: dict, root: dict, seen: set[str]) -> dict:
    while "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise ValidationError(f"unsupported $ref {ref}")
        if ref in seen:
            raise ValidationError(f"circular $ref {ref}")
        seen.add(ref)
        node = root
        for part in ref[2:].split("/"):
            if not isinstance(node, dict) or part not in node:
                raise ValidationError(f"unresolved $ref {ref}")
            node = node[part]
        schema = node
    return schema


def expect_type(instance, expected: str, path: str) -> None:
    ok = {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "boolean": isinstance(instance, bool),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
        "number": isinstance(instance, (int, float)) and not isinstance(instance, bool),
    }.get(expected)
    if ok is None:
        raise ValidationError(f"{path}: unsupported type {expected}")
    if not ok:
        raise ValidationError(f"{path}: expected {expected}")


def validate(instance, schema: dict, root: dict, path: str) -> None:
    schema = resolve(schema, root, set())
    if "const" in schema and instance != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}")
    if "type" in schema:
        expect_type(instance, schema["type"], path)
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise ValidationError(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            raise ValidationError(f"{path}: does not match {schema['pattern']}")
        if schema.get("format") == "uri":
            parsed = urlparse(instance)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValidationError(f"{path}: expected an https URI")
    if isinstance(instance, list) and "minItems" in schema and len(instance) < schema["minItems"]:
        raise ValidationError(f"{path}: fewer than minItems {schema['minItems']}")
    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                raise ValidationError(f"{path}: missing required {key}")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            extra = sorted(set(instance) - allowed)
            if extra:
                raise ValidationError(f"{path}: unexpected {', '.join(extra)}")
        for key, sub in schema.get("properties", {}).items():
            if key in instance:
                validate(instance[key], sub, root, f"{path}.{key}")
    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            validate(item, schema["items"], root, f"{path}[{index}]")


def check_stubs(example: dict) -> None:
    for index, row in enumerate(example.get("rows", [])):
        stub = row.get("evidence_export", {}).get("stub")
        if not isinstance(stub, str):
            continue
        path = ROOT / stub
        if not path.is_file():
            raise ValidationError(f"$.rows[{index}].evidence_export.stub: missing file {stub}")


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text())
    example = json.loads(EXAMPLE_PATH.read_text())
    validate(example, schema, schema, "$")
    check_stubs(example)
    print(f"ok {EXAMPLE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationError, json.JSONDecodeError, OSError) as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
