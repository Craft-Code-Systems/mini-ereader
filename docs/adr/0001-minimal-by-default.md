# Decision 0001: Colophon is minimal by default

**Status:** Accepted
**Date:**   2026-04-22

## Context

Documentation methodologies tend toward accretion: more templates,
more sections, more mandatory fields. Each addition is individually
justifiable, but the cumulative effect is documents nobody reads and
processes nobody follows.

Colophon targets solo developers and small teams. In that context the
constraint is attention and time, not thoroughness. A methodology
that adds friction is worse than no methodology.

## Decision

Colophon defines exactly five file types. It does not add more.
Additions belong in forks, extensions, or companion methodologies —
not in Colophon itself.

## Considerations

**Pro:** The five-file structure is small enough to hold in memory,
explain in one page, and set up in ten minutes. Users will actually
use it rather than opt out.

**Con:** Some projects have real needs Colophon does not address
(user documentation, compliance artifacts, formal specifications).
Those users must combine Colophon with other methodologies.

Rejected: adding optional "advanced" file types. Optional quickly
becomes expected.

## Consequences

- Requests to add file types to the core methodology will be declined.
- The Brief lists what Colophon is *not* to set expectations.
- Diátaxis and similar frameworks are referenced as companions,
  not competitors.
- Version bumps should remove complexity more often than add it.
