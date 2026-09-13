# evidence-index

Synthetic reference. Not a client repository, not an audit conclusion, and not a certification.

A control id points at an enforcing artifact, the steps to reproduce it, the export an assessor opens, and an owner role. Not a person.

License: MIT. See [LICENSE](LICENSE).

## What this is

[`schema/evidence-index.schema.json`](schema/evidence-index.schema.json) is the row shape. [`examples/index.json`](examples/index.json) is one filled index for tenant `sample-tenant` (Northline Sample Co.). Those names are synthetic.

The example walks a CC-style id into the other two reference repos:

| Control id | Enforcing artifact | Export |
| --- | --- | --- |
| CC8.1 | `ci-security-gates` `.github/workflows/security-gates.yml` | `semgrep-sarif` (run URL placeholder in `examples/export-stub.json`) |
| CC8.1 | `policy-as-code` `policies/change/exception.rego` | `opa-test-output` |
| CC6.3 | `policy-as-code` `policies/iam/wildcard.rego` | `opa-test-output` |
| CC6.1 | `policy-as-code` `policies/storage/encryption.rego` | `opa-test-output` |

Two CC8.1 rows are intentional. One control, two artifacts: the workflow that fails a pull request, and the exception rule that fails a test.

A control id is a filing label. A filled row does not mean the criterion is met.

On this repository, `validate` is required to merge into `main`. Repository admins can bypass the ruleset to ship a reference fix. The same job runs on every push and pull request.

## What this is not

- Not a client evidence binder and not a vault of customer artifacts.
- Not a conclusion that CC8.1, CC6.3, or CC6.1 is satisfied.
- Owner is a role (`engineering`, `security engineering`). Do not put a person in that field.

## How an assessor uses it

Start at the control id. Open the repo URL and path. Follow `reproduce`. Open the named export. The workflow evidence is a run URL plus a SARIF artifact name. The policy evidence is `opa test` output. A screenshot is not either export.

The stub files are placeholders. `examples/export-stub.json` uses `actions/runs/0` so it cannot be mistaken for a real run.

## Check the example

```bash
make validate
```

That runs `python3 scripts/validate.py`. No extra package. It checks the example against the schema’s required fields and confirms each stub file exists.

## Companion repos

This index is the map. The other two repos are the artifacts it points at.

- [ci-security-gates](https://github.com/yellow-theme/ci-security-gates)
- [policy-as-code](https://github.com/yellow-theme/policy-as-code)
- [evidence-index](https://github.com/yellow-theme/evidence-index)
