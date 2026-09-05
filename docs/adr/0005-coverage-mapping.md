# Decision 0005: Coverage of plan-of-approach content

**Status:** Accepted
**Date:**   2026-04-23

## Context

A traditional project plan — sometimes called a "plan of approach" or
PvA in the Dutch/European tradition — contains many sections that the
first version of Colophon did not address explicitly: functional
requirements, non-functional requirements, roles and responsibilities,
stakeholders, planning and milestones, and risks.

In v0.1 and v0.2 of Colophon, users hitting these needs had no
obvious place to put them. The five files (Brief, Decisions, Log,
Runbook, Changelog) covered architecture, operations, history, and
exploration — but the project-management surface area was
underspecified. Users either skipped the content (losing useful
information) or wrote a separate PvA next to Colophon (defeating the
methodology).

Three options were considered:

1. **Add a sixth core file type** (Spec or Charter) to cover
   requirements, roles, and risks. Cost: breaks the "five files"
   promise that makes Colophon distinctive; opens the door to further
   accretion.

2. **Distribute the content across existing files and external tools.**
   Most PvA content has a natural home: requirements live in issue
   trackers, roles in the Brief, milestones in tracker milestones,
   non-functional choices and significant risks become Decisions.
   Cost: assumes an issue tracker; less discoverable for users coming
   from a PvA-first background.

3. **Hybrid.** Distribute by default, with one optional sixth document
   (Spec) for projects that genuinely need rich requirements
   documentation upfront — typically prototypes exploring many
   capabilities before any are built, or projects with stakeholders
   who require formal specifications.

## Decision

Adopt the hybrid approach (option 3).

By default, PvA content is distributed:

| Content                       | Lives in                                         |
|-------------------------------|--------------------------------------------------|
| Functional requirements (top) | Brief — *Capabilities* section                   |
| Functional requirements (detail) | Issue tracker (issues, milestones, labels)    |
| Non-functional baseline       | Brief — *Non-functional baseline* section        |
| Non-functional trade-offs     | Decisions                                        |
| Roles and responsibilities    | Brief — *Stakeholders & roles* section           |
| Stakeholders                  | Brief — *Stakeholders & roles* section           |
| Planning / milestones (high)  | Brief — *Status & milestones* section            |
| Planning / milestones (detail)| Issue tracker milestones                         |
| Risks (short)                 | Brief — *Risks* section                          |
| Risks (significant, mitigated)| Decisions                                        |
| Test strategy                 | Brief paragraph or a Decision; tests in code     |

A project may add an optional **Spec** (`docs/spec.md`) when:

- It is in a prototype phase exploring many capabilities before
  implementing any of them — listing them as issues feels premature.
- A stakeholder formally requires a written requirements document.
- The project domain is unusually complex and a denser reference is
  genuinely useful.

A project should *not* add a Spec when:

- The capabilities can be expressed as 5–15 bullets in the Brief.
- An issue tracker is already in use — duplicating requirements there
  is waste.
- "It feels more professional" — the absence of a Spec is not
  unprofessional; it is *deliberate*.

## Considerations

**Pro:**
- The Brief becomes meaningfully more useful without becoming long.
- The "five files" promise stands for the default case.
- Optional Spec exists for the genuine cases without becoming default.
- Distribution to issue trackers reflects how teams actually work.
- Coverage table makes Colophon defensible to PvA-trained reviewers.

**Con:**
- A "five files plus one optional" formulation is slightly less crisp
  than "five files".
- The Brief grows from a one-pager to a one-or-two-pager. The "one
  page" claim weakens.
- Users without an issue tracker have to choose between the optional
  Spec or capability bullets in the Brief.

Rejected: option 1 (mandatory sixth file). Pure five-file purity
would have forced users to write a Spec they often do not need.
Rejected: option 2 (distribute only). For prototyping and formal
contexts the lack of any rich-requirements option pushed users
outside Colophon.

## Consequences

- The Brief gains a documented structure with ten suggested sections.
- A `templates/SPEC.template.md` is provided for projects that opt in.
- The README documents the Colophon-vs-PvA coverage mapping.
- The marketing line remains "five files, not fifty pages" with a
  parenthetical "(plus one optional Spec)" where space allows.
- Future Colophon extensions follow the same pattern: optional and
  opt-in, never default.
