# Decision 0004: Naming conventions for document types

**Status:** Accepted
**Date:**   2026-04-22

## Context

Colophon defines five document types. Each needs a *name* for use in
prose ("add a Decision", "update the Brief") and a *filename* for
use on disk.

The filenames could not be chosen freely. `README.md` and
`CHANGELOG.md` are universal conventions recognised by GitHub, GitLab,
npm, PyPI, and nearly every docs platform. Renaming them would lose
automatic rendering and break developer expectations. `runbook.md` is
an informal but strong convention in ops and SRE. The ADR filename
pattern (`NNNN-kebab-case.md`) comes from the wider ADR community.

The role-names, however, were open. The first draft of Colophon used
metaphors ("the door", "the memory", "the notebook") which read well
in marketing copy but were not usable as working vocabulary. A later
draft considered `-doc` suffixes (`maindoc`, `designdoc`, `researchdoc`,
`rundoc`, `changedoc`) for visual consistency but this introduced two
problems: "designdoc" collides with an existing software term for
long upfront design documents (exactly what Colophon replaces), and
uniform suffixes read as bureaucratic rather than purposeful.

## Decision

Colophon uses five role-names, distinct from the filenames, chosen
for clarity and compatibility with existing conventions where they
are strong:

| Role           | Filename                |
|----------------|-------------------------|
| **Brief**      | `README.md`             |
| **Decision**   | `docs/adr/NNNN-*.md`    |
| **Log**        | `docs/research-log.md`  |
| **Runbook**    | `docs/runbook.md`       |
| **Changelog**  | `CHANGELOG.md`          |

Role-names are capitalised when used as Colophon terms ("add a
Decision") and lowercased in generic use ("the decision was made
last week").

## Considerations

**Pro:**
- Each role-name is a single word, readable as a noun in a sentence.
- Three roles (**Log**, **Runbook**, **Changelog**) reuse existing
  industry terms; users already know them.
- Two roles (**Brief**, **Decision**) are Colophon-specific but
  unambiguous and collision-free.
- Filenames remain standard, preserving tooling behaviour.

**Con:**
- Users must learn that the filename and role-name differ. Mitigated
  by a vocabulary table in the Brief.
- "Decision" is slightly more generic than "ADR". Accepted because
  "ADR" is opaque to readers outside the docs-as-code subculture.

Rejected alternatives:
- **Metaphors** ("door", "memory", "notebook"): good in copy, bad as
  working vocabulary.
- **`-doc` suffixes** (`maindoc`, `designdoc`, ...): `designdoc`
  actively conflicts with existing meaning; uniform suffixes feel
  bureaucratic.
- **`-book` suffixes** (`Decisionbook`, `Logbook`): longer without
  added clarity, except where the convention already exists (Runbook).
- **Keeping "ADR"**: precise but opaque for newcomers.

## Consequences

- All Colophon documentation uses the role-names in prose.
- Filenames remain unchanged from established conventions.
- The Brief includes a vocabulary table.
- Future Colophon extensions must pick role-names that fit this
  pattern: short, noun-form, collision-free, compatible with existing
  conventions where they are strong.
