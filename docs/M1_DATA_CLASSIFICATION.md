# Milestone 1 Test Data Classification

Status: Initial M1 fixture policy

## Classification

| Classification | Meaning | Allowed in committed M1 fixtures? |
| --- | --- | --- |
| `PUBLIC_TEST` | Fully synthetic, non-sensitive data safe for public documentation and repositories | Yes |
| `INTERNAL_TEST` | Synthetic, non-sensitive operational test detail intended for authorised project contributors | Yes, when minimised |
| `SENSITIVE` | Personal, confidential, commercially sensitive, regulated, or security-relevant data | No |
| `RESTRICTED` | Secrets, credentials, highly regulated data, or data whose exposure could cause serious harm | No |

All M1 fixtures use synthetic `PUBLIC_TEST` or, only when necessary, minimised `INTERNAL_TEST` data. Classification is metadata for policy and handling; it does not grant access or override vertical, tenant, purpose, consent, or retention rules.

## Prohibited milestone data

The following must never be placed into M1 prompts, fixtures, logs, telemetry, or audit payloads:

- passwords
- API keys or other secrets
- access tokens
- private keys
- real payment data
- real banking data
- real health data
- real relationship or private-message data
- real customer personally identifiable information (PII)
- production credentials
- unrestricted raw vertical data

Synthetic strings must not resemble usable credentials. Test identifiers must not encode names, email addresses, account numbers, or other sensitive facts.

## Minimisation and redaction

Include only fields needed to prove a contract behavior. Prompts and tool arguments use synthetic values. Logs and telemetry record operational metadata rather than prompt or response content by default. Audit records store classifications, field names, outcomes, and protected references rather than full payloads.

If unexpected sensitive content reaches a boundary, redact or reject it before logging, telemetry, fixture capture, or audit persistence. Redaction must not silently convert prohibited production data into approved fixture data; use newly generated synthetic replacements. Raw provider errors and stack traces remain out of public errors because they may contain request content or infrastructure detail.

These rules govern M1.1 fixtures only and do not establish production data classification or retention policy.
