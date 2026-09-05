# Colophon

> Just-enough documentation for solo developers and small teams.
> Five files, not fifty pages.

**Colophon** is a lightweight documentation methodology. It replaces
traditional phase documents (project plans, requirements documents,
design documents, test plans) with five living files that sit next to
the code and grow with it.

This repository *is* the methodology: it documents Colophon using
Colophon. Fork it as a starting point for your own project.

— Website: [usecolophon.dev](https://usecolophon.dev)
— License: methodology under [CC BY 4.0](./LICENSE-TEXT), template under [MIT](./LICENSE)

---

## Why

Traditional documentation works well for waterfall projects with large
teams and external stakeholders. For solo developers and small teams it
creates overhead without proportional value:

- Long documents that nobody re-reads
- Context lost across multiple files
- Writing effort that dwarfs the project itself
- Docs that rot the moment the project changes direction

Colophon assumes you are building software, not writing about building
software. Every file earns its place.

---

## The five principles

1. **Docs live next to code.** In git, in markdown, reviewed in pull
   requests. Documentation that lives elsewhere rots elsewhere.

2. **Just-in-time, never upfront.** Write when a decision is made, a
   bug threatens to repeat, or someone will soon ask. Before that,
   you are guessing.

3. **One document, one job.** No mega-documents that try to be
   everything. Small files with a single focus stay accurate;
   sprawling ones don't.

4. **If nothing breaks when it's gone, don't write it.** The reverse
   test. Documents that cost time to maintain and solve no real
   problem are waste, no matter how professional they look.

5. **Five files beat fifty pages.** A Brief, a folder of Decisions, a
   Log, a Runbook, a Changelog. Together they cover what waterfall
   tried to, with a fraction of the drag.

---

## The five document types

Colophon has its own vocabulary for talking about its documents. The
*role-name* is used in prose; the *filename* follows established
conventions so tooling keeps working.

| Role          | Filename                 | Purpose                                    |
|---------------|--------------------------|--------------------------------------------|
| **Brief**     | `README.md`              | The project's orientation document.        |
| **Decision**  | `docs/adr/NNNN-*.md`     | One per significant design choice.         |
| **Log**       | `docs/research-log.md`   | Dated, append-only exploration notes.      |
| **Runbook**   | `docs/runbook.md`        | How to run, deploy, and unbreak the thing. |
| **Changelog** | `CHANGELOG.md`           | Human-readable history of what changed.    |

When speaking of Colophon you "add a Decision", "update the Brief",
"append to the Log". The filenames keep their standard form because
GitHub, GitLab, and every common tool expect them — nothing is gained
by breaking that convention.

See [Decision 0004](./docs/adr/0004-naming-conventions.md) for the
reasoning behind these choices.

### Optional sixth: the Spec

Some projects need a richer requirements artefact than the Brief can
hold — typically prototypes that explore many capabilities before
implementation, or projects with stakeholders who expect a formal
specification. For those cases, Colophon allows an optional **Spec**
(`docs/spec.md`) covering functional and non-functional requirements
in detail.

This is *opt-in*. The default Colophon project does not have one.
Most projects do fine with capabilities listed in the Brief and tracked
as issues thereafter. See
[Decision 0005](./docs/adr/0005-coverage-mapping.md) for when to add
one and when not to.

---

## What the Brief should cover

The Brief is more than a "getting started" file — it is the project's
orientation document. A complete Brief typically contains:

| Section                    | What goes here                                                   |
|----------------------------|------------------------------------------------------------------|
| **Why**                    | The problem and why now. Two or three sentences.                 |
| **Scope & non-scope**      | What this will and explicitly will not do.                       |
| **Success criteria**       | Measurable outcomes that say "we are done".                      |
| **Capabilities**           | Top-level functional requirements (5–15 bullets, not user stories). |
| **Non-functional baseline**| Performance, security, uptime, accessibility targets.            |
| **Stakeholders & roles**   | Who decides, who builds, who reviews. Three to five lines.       |
| **Risks**                  | Top three to five risks with mitigation. One line each.          |
| **Stack**                  | Language, framework, infra, deploy target.                       |
| **Status & milestones**    | Where we are now and the next two or three milestones.           |
| **Getting started**        | Three to seven commands to get the project running.              |

A complete Brief is one or two screens long, not thirty. Detail goes
elsewhere: capabilities become issues once implementation starts;
non-functional choices become Decisions when they involve trade-offs;
risks that grow large enough to warrant their own consideration also
become Decisions.

For projects that genuinely need more upfront detail on requirements,
add the optional Spec.

---

## A place for everything

What about requirements, roles, planning, and risks? They have homes.
The Brief summarises and orients; Decisions capture trade-offs; the
issue tracker manages live work; the Runbook handles operations. The
optional Spec, when present, holds rich requirements detail.

The map below shows where each kind of content lives. The two
columns reflect the same content seen from different angles —
**traditional section** for readers used to project plans, **in
Colophon** for everyone.

| Traditional section          | In Colophon                                              |
|------------------------------|----------------------------------------------------------|
| Purpose / problem statement  | Brief — *Why*                                            |
| Scope                        | Brief — *Scope & non-scope*                              |
| Goals / success criteria     | Brief — *Success criteria*                               |
| Functional requirements      | Brief (top-level) → issue tracker (detail) → Spec (optional) |
| Non-functional requirements  | Brief (baseline) → Decisions (where trade-offs are made) |
| Stakeholders                 | Brief — *Stakeholders & roles*                           |
| Project organisation / roles | Brief — *Stakeholders & roles*                           |
| Planning / milestones        | Brief (high-level) → issue tracker milestones (detail)   |
| Risks                        | Brief (short list) → Decisions (where mitigation is chosen) |
| Architecture / design        | Decisions                                                |
| Test plan                    | Tests in the codebase + a *Test strategy* paragraph in the Brief or a Decision |
| Deployment plan              | Runbook                                                  |
| Communication plan           | Outside Colophon — wiki, project tracker, or team handbook |

The principle: **Colophon documents what the project *is*. The issue
tracker manages what the project *does next*.** Mixing them produces
documents that drift and trackers that go stale.

---

## How to adopt it

### Starting fresh

1. Click **Use this template** on GitHub, or:
   ```
   gh repo create my-project --template Craft-Code-Systems/colophon
   ```
2. Rewrite the Brief (`README.md`) for your project — see the
   "What the Brief should cover" section above.
3. Delete Colophon's own Decisions in `docs/adr/`. Keep
   `0000-template.md`.
4. Empty the Log and Changelog.
5. Rewrite the Runbook for your project.
6. Start writing. Add a Decision the first time you make a real
   design choice.

Total setup: about ten minutes.

### Adopting in an existing project

Different approach: do not try to document the past. Colophon is
adopted forward. See [`docs/adoption.md`](./docs/adoption.md) for the
30-minute bootstrap and the 30-day rule.

### Handling structural changes

Decisions are immutable once accepted. When a design choice changes,
you write a new Decision that supersedes the old one — keeping the
full reasoning trail. See
[`docs/adoption.md`](./docs/adoption.md#when-a-structural-design-choice-changes)
for a worked example.

---

## What Colophon is *not*

- **Not a replacement for user-facing documentation.** If your project
  needs tutorials or API reference for external users, combine
  Colophon with [Diátaxis](https://diataxis.fr). Colophon covers the
  internal, project-running docs; Diátaxis covers the external ones.
- **Not suitable for compliance-heavy environments.** If you work in
  regulated industries with mandatory documentation structures, treat
  Colophon as an internal layer and keep the formal docs on top.
- **Not a silver bullet for large teams.** It scales up to perhaps a
  dozen people; beyond that, more structure pays off.
- **Not anti-documentation.** It is pro-*useful*-documentation.

---

## Further reading

- [Adoption guide](./docs/adoption.md) — existing projects and structural changes
- [FAQ](./docs/faq.md) — common questions
- [Runbook](./docs/runbook.md) — how to use this repo
- [Decisions](./docs/adr/) — the reasoning behind Colophon itself
- [Log](./docs/research-log.md) — how Colophon came to be
- [Changelog](./CHANGELOG.md) — methodology versions

---

## Contributing

This is an open methodology. Issues and pull requests are welcome,
especially:

- Real-world examples of Colophon in use
- Translations of the core files
- Integration notes for specific stacks (Rails, .NET, Django, etc.)

Please open an issue before large changes.
