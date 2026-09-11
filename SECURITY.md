# Security policy

RackMind is a telemetry review demo. Do not connect it to production control systems without an independent review.

## Dependency and reporting controls

- Dependencies are pinned in `requirements.txt` and checked with `pip-audit --strict` in GitHub Actions.
- The readiness check is `python healthcheck.py`.
- Authentication can use Streamlit OIDC (`RACKMIND_OIDC_PROVIDER`) or local hashed users (`RACKMIND_USERS`).
- Uploads are capped at 10 MB and actions are recorded in append-only JSONL audit logs.

Report vulnerabilities privately to the repository owner before opening a public issue. Never include credentials, facility identifiers, or sensitive telemetry in a report.
