# Security policy

## Supported versions

The latest CXP minor release receives security fixes. The immediately previous
minor receives critical fixes for 90 days after the newer minor is published.
Older minors and major versions are unsupported unless a separate maintenance
agreement says otherwise.

| Version | Support |
| --- | --- |
| 4.1.x | Current |
| 4.0.x | Critical fixes during the 90-day transition |
| < 4.0 | Unsupported |

## Reporting a vulnerability

Do not disclose a suspected vulnerability in a public issue. Use GitHub's
[private vulnerability report](https://github.com/menudoproblema/cxp/security/advisories/new)
and include the affected version, impact, reproduction and any suggested
mitigation. If that channel is unavailable, open a public issue requesting a
private contact without including security details.

The maintainer aims to acknowledge a complete report within five business days.
That target is not a contractual SLA. Publication timing depends on impact,
available mitigations and coordination with affected consumers.

## Scope

Reports about parsers, canonicalization, catalog integrity, requirement
evaluation, package artifacts and the release pipeline are in scope. A CXP
compatibility verdict is not a safety certification, production authorization
or proof that a physical device is safe to operate.
