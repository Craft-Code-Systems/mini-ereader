# Project Name

> One-sentence description of what this project does and for whom.

## Why

The problem this project solves. Two or three sentences. Who cares,
and why now.

## Scope

**In scope (v1):** what this project *will* do.

**Not in scope:** what this project explicitly *will not* do.
The non-scope is often more valuable than the scope.

## Success criteria

How we know this is done. Measurable, not aspirational.

- [ ] Outcome 1 (concrete, observable)
- [ ] Outcome 2
- [ ] Outcome 3

## Capabilities

What the system does, at a top level. Five to fifteen bullets — the
*shape* of the product, not the user stories.

- View, create, and edit X
- Receive notifications when Y happens
- Export Z to format W
- ...

Detailed user stories and tickets live in the issue tracker, not here.
For projects that need a richer functional/non-functional spec upfront
(prototypes, formal contracts), see `docs/spec.md` (optional).

## Non-functional baseline

Targets the system must meet beyond what it does.

- **Performance:** [e.g. p95 API response < 200ms]
- **Availability:** [e.g. 99.5% uptime]
- **Security:** [e.g. HTTPS only; auth via established provider]
- **Accessibility:** [e.g. WCAG 2.2 AA on public pages]

When a non-functional choice involves a real trade-off, it becomes a
Decision in `docs/adr/`.

## Stakeholders & roles

Who is involved and what they do. Three to five lines.

- **Product owner:** [name] — sets priorities, accepts work
- **Tech lead:** [name] — owns architecture, signs off on Decisions
- **Maintainers:** [names] — review and merge
- **Stakeholders:** [team/department] — periodic review

## Risks

Top three to five risks with a one-line mitigation each. If a risk
grows large enough to warrant deep analysis, it becomes a Decision.

- **Risk:** Third-party API rate limits could throttle peak usage.
  **Mitigation:** Cache aggressively; design fallback path.
- **Risk:** ...

## Stack

- **Language / framework:**
- **Data store:**
- **Infrastructure:**
- **Deploy target:**

## Status & milestones

Current state in one or two sentences, dated. Followed by the next
two or three milestones — high-level only; tracker has the detail.

*April 2026 — prototype working locally, not yet deployed.*

- **M1 (May):** First end-to-end flow live in staging
- **M2 (June):** Closed beta with 10 users
- **M3 (July):** Public launch

## Getting started

How a new contributor (or future-you) gets the project running. Three
to seven commands.

```
git clone ...
cd project-name
make setup
make run
```

## More

- [Runbook](./docs/runbook.md) — run, deploy, unbreak
- [Decisions](./docs/adr/) — why design choices were made
- [Log](./docs/research-log.md) — exploration notes
- [Spec](./docs/spec.md) — detailed requirements (optional, if present)
- [Changelog](./CHANGELOG.md)

---

<sub>This project uses [Colophon](https://usecolophon.dev) for its
documentation. *Brief* (this file), *Decisions*, *Log*, *Runbook*,
and *Changelog* — plus an optional *Spec* if needed.</sub>
