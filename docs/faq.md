# FAQ

Questions that come up often, with short answers.

---

**Is Colophon just ADRs with extra steps?**
No. Decisions (the Colophon term for ADRs) are one of the five
document types. Colophon also defines the Brief, the Log, the
Runbook, and the Changelog. Each fills a role that Decisions
alone do not.

---

**Where do functional requirements, roles, and planning live?**
Distributed across the right places. Top-level capabilities go in the
Brief; detailed user stories go in the issue tracker. Roles and
stakeholders go in the Brief. High-level milestones go in the Brief;
detailed planning lives in tracker milestones. Risks short enough to
list go in the Brief; risks that need analysis become Decisions.

The full map of where each kind of content lives is in
[adoption.md](./adoption.md#a-place-for-everything).

---

**What if my project genuinely needs a detailed requirements document?**
Use the optional Spec (`docs/spec.md`). A template is in
`templates/SPEC.template.md`. It is opt-in — most projects do fine
without it. Add a Spec when you are prototyping and exploring many
capabilities before implementing any, when a stakeholder formally
requires it, or when the domain is dense enough to warrant a single
reference document. See [Decision 0005](./adr/0005-coverage-mapping.md).

---

**Doesn't an optional sixth document break the "five files" promise?**
The five core files remain unchanged. The Spec is an *opt-in
extension* — the default Colophon project does not have one, and the
methodology's promise is that those five suffice for the majority of
projects. The Spec exists for the genuine minority where the Brief
plus an issue tracker is not enough.

---

**Why the separate vocabulary — why not just use the filenames?**
Because talking about Colophon in prose reads better with named roles.
"Add a Decision" is clearer than "add a file in the ADR folder".
"Update the Brief" is clearer than "update the README". The filenames
stay standard so tooling keeps working; the role-names make
conversation about the methodology concrete. See
[Decision 0004](./adr/0004-naming-conventions.md) for the full reasoning.

---

**How do I adopt Colophon in a project that already exists?**
You do not document the past. Colophon is adopted forward: set up the
skeleton, make the Brief current, and add new Decisions as you make
them. Within 30 days you will have organically captured what matters.
See [adoption.md](./adoption.md) for the 30-minute bootstrap.

---

**What happens when I change a major design choice?**
You write a new Decision that supersedes the old one. Accepted
Decisions are never edited — their reasoning stays as historical
record, the new Decision links back. This preserves the *why* of past
choices and prevents re-litigating the same trade-offs. See
[adoption.md](./adoption.md#when-a-structural-design-choice-changes)
for a worked example.

---

**How is this different from Diátaxis?**
Different scope. Diátaxis organises *user-facing* documentation into
four types (tutorial, how-to, reference, explanation). Colophon
organises *project-internal* documentation — the stuff developers
and their future selves rely on. They are complementary; use both if
your project needs user-facing docs.

---

**Can I add more document types?**
For your own project, yes. For the published methodology, no — see
[Decision 0001](./adr/0001-minimal-by-default.md). If you find a gap
the five types cannot fill for most projects, open an issue.

---

**Does Colophon work for non-software projects?**
The principles transfer (docs next to work, just-in-time, one doc
one job). The specific files assume a git repository. For non-code
projects, adapt; the methodology is small enough to port.

---

**What if my stakeholders demand a formal project plan or requirements document?**
Write one, on top of Colophon, as a separate deliverable. Colophon is
how you actually run the project internally; external artefacts are
their own concern. Often a well-kept Brief plus the optional Spec is
enough, once shown.

---

**How does this fit with Agile / Scrum?**
Comfortably. Colophon replaces the parts of Agile documentation that
tend toward clutter (long running specs, duplicated design docs)
while keeping what matters (Decisions, history, operational knowledge).
It is compatible with any iterative process.

---

**Is the Log supposed to be rough?**
Yes. Think of it as a dated notebook, not an edited essay. When
something in the Log crystallises into a real choice, promote it to
a Decision. The Log itself stays raw.

---

**Should every change get a Decision?**
No. Reserve Decisions for *choices* — things where a reasonable
alternative existed. Bug fixes, refactors, and minor dependency
bumps do not qualify. See the table in
[adoption.md](./adoption.md#what-does-not-deserve-a-decision).

---

**Should I lint or enforce anything in CI?**
Optional. Markdown linting and broken-link checks are cheap and catch
rot. Enforcing numbering or file presence tends to add more friction
than value for small teams. Start without; add when it saves pain.

---

**How do I handle secrets or sensitive operational info?**
Not in Colophon. The Runbook should say *where* to find credentials
(password manager, vault), not contain them. Never commit secrets,
even to private repos — it is a policy worth keeping inviolable.

---

**What if I am working solo — do I still need this?**
Especially then. Future-you is the most forgetful colleague you will
ever have. A minimal Colophon setup costs nothing upfront and pays
off the first time you return to a project after a month away.

---

**What is the "Colophon" name from?**
A colophon is the short note at the back of a book recording how it
was made — printer, typeface, paper, date. The methodology takes the
same spirit: a small set of files documenting how the project was
made and how to keep making it.

---

**Where should I report issues or suggest changes?**
[github.com/Craft-Code-Systems/colophon/issues](https://github.com/Craft-Code-Systems/colophon/issues).
Especially welcome: real-world adoption stories, stack-specific
integration notes, and translations.
