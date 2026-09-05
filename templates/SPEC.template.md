# Spec — Project Name

> Detailed functional and non-functional specification.
>
> **This file is optional.** Most Colophon projects do fine with
> capabilities listed in the Brief and tracked as issues thereafter.
> Add a Spec only when (a) you are prototyping and exploring many
> capabilities before implementing any, (b) a stakeholder formally
> requires it, or (c) the domain is dense enough that a single
> reference document genuinely helps. See
> [Decision 0005](https://github.com/Craft-Code-Systems/colophon/blob/main/docs/adr/0005-coverage-mapping.md)
> in the upstream Colophon repository.

---

## Functional requirements

Each requirement has a stable identifier (`F-NN`) so it can be
referenced from issues, Decisions, and tests.

### F-01 — Short title

**Description:** what the system must do, in one or two sentences.

**Acceptance:** how we know this is met. Concrete and testable.

**Priority:** must-have | should-have | nice-to-have

**Notes:** edge cases, assumptions, open questions.

### F-02 — Short title

...

---

## Non-functional requirements

Targets the system must meet beyond functional behaviour. Each one
has an identifier (`N-NN`).

### N-01 — Performance

- API response time: 95th percentile under 200ms for read endpoints
- Page load: under 2s on 4G connection
- Concurrent users: target 100, design ceiling 500

### N-02 — Availability

- Uptime target: 99.5% (≈ 3.6 hours downtime per month)
- Planned maintenance: outside business hours, announced 48h in advance

### N-03 — Security

- All traffic over HTTPS; HSTS enabled
- Authentication via established provider (no homegrown auth)
- Secrets in vault, never in code or logs
- Dependencies scanned weekly

### N-04 — Accessibility

- WCAG 2.2 Level AA compliance for public-facing pages
- Keyboard navigation for all primary flows

### N-05 — ...

---

## Constraints

External constraints the project must respect — not chosen by the team.

- Regulatory: GDPR; user data must remain in EU
- Budget: under €X infrastructure cost per month
- Timeline: live before [date] for [reason]
- Compatibility: must work with [existing system] via [interface]

---

## Out of scope

What this spec explicitly does *not* cover. Often more valuable than
the in-scope list.

- Native mobile apps (web-only for v1)
- Multi-tenancy (single-tenant for v1)
- Real-time collaboration (read-only sharing only)

---

## Open questions

Unresolved items that need answers before or during implementation.
Move them out of this section as they get answered — into Decisions
if they were design choices, into the Log if they were investigations,
or simply remove if they became obsolete.

- [ ] Does requirement F-04 apply to admin users?
- [ ] What is the data retention policy for N-03?
- [ ] Are we targeting iOS Safari ≥ 16 or ≥ 17?

---

## Glossary

Terms specific to this project that a new reader would not know.

| Term         | Meaning                                           |
|--------------|---------------------------------------------------|
| *Cohort*     | A group of users who joined within the same week. |
| *Manifest*   | The package metadata file shipped with each build.|

---

*Once implementation begins, individual requirements typically get
mirrored into the issue tracker for working state. The Spec stays as
the canonical reference; the tracker handles "what is being done now".*

*If a requirement evolves significantly mid-project, update it here
and note the change in the Log. Major reframings warrant a Decision.*
