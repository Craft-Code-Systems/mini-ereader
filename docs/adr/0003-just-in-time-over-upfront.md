# Decision 0003: Just-in-time writing over upfront documentation

**Status:** Accepted
**Date:**   2026-04-22

## Context

Traditional project documentation is written upfront, at the start of
a phase: plans of approach, requirements specifications, design
documents. The assumption is that a clear written plan reduces risk
and aligns stakeholders.

For small teams, this assumption often fails. Upfront documents are
written when knowledge is lowest, revised rarely, and read little.
The effort of writing them competes directly with the project itself.

## Decision

Colophon is written just-in-time. Files are added or updated when a
decision is made, a bug threatens to repeat, or a specific reader
needs the information. Not before.

## Considerations

**Pro:**
- Writing happens when knowledge is highest.
- No wasted effort on documents that become obsolete before being read.
- Each addition is triggered by a real need, not a template slot.

**Con:**
- Requires discipline: it is tempting to skip writing in the moment.
- Less reassuring to stakeholders accustomed to upfront artefacts.
- Offers no predicted project-plan view at kickoff.

Rejected: upfront templates to be filled in at project start. They
reward filling boxes over capturing useful information.

## Consequences

- Colophon provides no project-kickoff template.
- The Log (`docs/research-log.md`) captures exploration as it happens.
- New Decisions are added as design choices are reached — one commit at a time.
- For stakeholders who need upfront artefacts for approval, a brief
  scope section in the Brief usually suffices; anything more formal
  lives outside Colophon.
