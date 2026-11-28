# Security Policy

## Supported deployment

DiscoveryAI is an actively developed research prototype. The public demo is provided for evaluation and is not a production security certification.

## Reporting a vulnerability

Please do not publish credentials, access tokens, private papers, or exploitable vulnerability details in public issues.

Use GitHub's private vulnerability reporting feature for this repository when available. Include:
- affected component and version;
- impact and conditions required to reproduce;
- a minimal reproduction or proof of concept that does not expose real user data;
- suggested mitigation, if known.

We will acknowledge reports and assess severity as time and project scope permit. No response-time SLA is implied.

## Secret handling

- Never commit `.env` files, API keys, database credentials, JWT secrets, or private research documents.
- Use GitHub Actions secrets and deployment-provider environment variables for credentials.
- Rotate any credential that may have been exposed.
- Keep public demo endpoints read-only and avoid uploading confidential material.

## Dependency security

Frontend dependencies are checked with `npm audit --audit-level=moderate` in CI. Backend Python dependencies are checked with `pip-audit` in CI. These checks cover known advisories in the resolved environment; they do not prove the application is free of vulnerabilities.