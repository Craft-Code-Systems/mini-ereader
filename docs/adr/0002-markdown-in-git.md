# Decision 0002: Markdown files in git, not a docs platform

**Status:** Accepted
**Date:**   2026-04-22

## Context

Documentation can live in many places: wikis (Confluence, Notion),
dedicated docs platforms (BookStack, GitBook), issue trackers
(GitHub Issues, Linear), or plain markdown files in a git repository.

Each location has trade-offs around authoring friction, searchability,
review, versioning, and proximity to the code being documented.

## Decision

Colophon docs live as markdown files in the project's own git
repository, under `docs/`.

## Considerations

**Pro:**
- Documentation travels with the code it describes. Clone the repo,
  get the docs.
- Changes go through pull requests and are reviewed alongside code.
- History is preserved without extra tooling.
- Works offline. Works in any editor.
- GitHub, GitLab, and similar platforms render markdown for free.

**Con:**
- Less rich than purpose-built platforms (no comments, no WYSIWYG).
- Non-developers cannot easily contribute.
- Search across many projects is weaker than a central wiki.

Rejected: central wikis for project-specific docs. They drift from
the code and require context-switching to update.

## Consequences

- Every Colophon project has a `docs/` folder in its repo.
- Broader organisational knowledge (business processes, multi-project
  reference material, client information) belongs in a wiki — Colophon
  has nothing to say about that.
- A documentation site (MkDocs, Docusaurus, etc.) can be added later,
  rendering the same markdown files, without changing the source.
