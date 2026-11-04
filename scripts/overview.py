#!/usr/bin/env python3
"""Build a one-page overview of a Colophon project.

Reference generator for Decision 0006: generated views are tooling,
not documents. Every fact on the page is read from the Colophon files,
git history, or the GitHub milestones API. Nothing is inferred, and
the output is never edited by hand: fix the source file instead.

Run from anywhere inside the repository:

    python3 scripts/overview.py --out _site

Needs Python 3.8+ and git, nothing else. Milestones are fetched when a
repository is known (--repo, or GITHUB_REPOSITORY in GitHub Actions);
GITHUB_TOKEN is used when set.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import posixpath
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

BRIEF = "README.md"
CHANGELOG = "CHANGELOG.md"
LOG = "docs/research-log.md"
RUNBOOK = "docs/runbook.md"
SPEC = "docs/spec.md"
DECISIONS = "docs/adr"

# Role-name and path of each document whose freshness is reported.
DOCUMENTS = [
    ("Brief", BRIEF),
    ("Decisions", DECISIONS),
    ("Log", LOG),
    ("Runbook", RUNBOOK),
    ("Changelog", CHANGELOG),
    ("Spec", SPEC),
]
# Commits touching anything outside these paths count as "elsewhere".
DOC_PATHSPECS = [BRIEF, CHANGELOG, "docs"]
# A document is flagged when it is older than this and the rest of the
# repository has changed since. A fixed rule, not a judgement.
STALE_AFTER_DAYS = 90

HEADING = re.compile(r"(#{1,6})\s+(.*)")
BULLET = re.compile(r"[-*+]\s+(.*)")
NUMBERED = re.compile(r"\d+\.\s+(.*)")
INLINE = re.compile(
    r"`([^`]+)`|\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)|\*([^*\s][^*]*)\*"
)
RELEASE = re.compile(r"^##\s+\[([^\]]+)\](?:\s*[—–-]\s*(\S+))?", re.M)
LOG_ENTRY = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*[—–-]\s*(.+)$", re.M)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {args[0]} failed")
    return result.stdout.strip()


def read(path: str) -> str | None:
    file = Path(path)
    return file.read_text(encoding="utf-8") if file.is_file() else None


class Links:
    """Turns repository paths into URLs that work from the published page."""

    def __init__(self, repo: str | None, sha: str, out_dir: Path):
        server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        self.repo_url = f"{server}/{repo}" if repo else None
        self.sha = sha
        self.out_dir = out_dir

    def to(self, path: str) -> str:
        if self.repo_url:
            kind = "tree" if Path(path).is_dir() else "blob"
            return f"{self.repo_url}/{kind}/{self.sha}/{path}"
        try:
            return Path(os.path.relpath(path, self.out_dir)).as_posix()
        except ValueError:  # different drive on Windows
            return Path(path).resolve().as_uri()

    def commit(self) -> str | None:
        return f"{self.repo_url}/commit/{self.sha}" if self.repo_url else None

    def resolve(self, href: str, source: str) -> str:
        """Resolves a link found in `source` the way GitHub would."""
        if re.match(r"[a-z][a-z0-9+.-]*:|#", href, re.I):
            return href
        target, _, fragment = href.partition("#")
        path = posixpath.normpath(
            posixpath.join(posixpath.dirname(source), target)
        )
        return self.to(path) + (f"#{fragment}" if fragment else "")


class Markdown:
    """Renders the small subset of markdown that Colophon files use."""

    def __init__(self, links: Links, source: str):
        self.links = links
        self.source = source

    def inline(self, text: str) -> str:
        out, pos = [], 0
        for m in INLINE.finditer(text):
            out.append(esc(text[pos:m.start()]))
            code, bold, label, href, em = m.groups()
            if code is not None:
                out.append(f"<code>{esc(code)}</code>")
            elif bold is not None:
                out.append(f"<strong>{self.inline(bold)}</strong>")
            elif label is not None:
                url = self.links.resolve(href, self.source)
                out.append(f'<a href="{esc(url)}">{self.inline(label)}</a>')
            else:
                out.append(f"<em>{self.inline(em)}</em>")
            pos = m.end()
        out.append(esc(text[pos:]))
        return "".join(out)

    def table(self, rows: list[str]) -> str:
        cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
        cells = [
            r for r in cells
            if not all(re.fullmatch(r":?-+:?", c) for c in r if c)
        ]
        if not cells:
            return ""
        head, *body = cells
        th = "".join(f"<th>{self.inline(c)}</th>" for c in head)
        trs = "".join(
            "<tr>" + "".join(f"<td>{self.inline(c)}</td>" for c in r) + "</tr>"
            for r in body
        )
        return (
            f'<div class="scroll"><table><thead><tr>{th}</tr></thead>'
            f"<tbody>{trs}</tbody></table></div>"
        )

    def block(self, text: str) -> str:
        out: list[str] = []
        para: list[str] = []
        items: list[str] = []
        rows: list[str] = []
        code: list[str] | None = None
        list_tag = "ul"

        def close_code() -> None:
            source = "\n".join(code or [])
            out.append(f"<pre><code>{esc(source)}</code></pre>")

        def flush() -> None:
            if para:
                out.append(f"<p>{self.inline(' '.join(para))}</p>")
                para.clear()
            if items:
                lis = "".join(f"<li>{self.inline(i)}</li>" for i in items)
                out.append(f"<{list_tag}>{lis}</{list_tag}>")
                items.clear()
            if rows:
                out.append(self.table(rows))
                rows.clear()

        for line in text.splitlines():
            s = line.strip()
            if s.startswith("```"):
                if code is None:
                    flush()
                    code = []
                else:
                    close_code()
                    code = None
                continue
            if code is not None:
                code.append(line)
                continue
            if s.startswith("|"):
                if para or items:
                    flush()
                rows.append(s)
                continue
            if rows or not s or s == "---":
                flush()
                if not s or s == "---":
                    continue
            heading = HEADING.match(s)
            if heading:
                flush()
                out.append(f"<h4>{self.inline(heading.group(2))}</h4>")
                continue
            item = BULLET.match(s) or NUMBERED.match(s)
            if item:
                tag = "ul" if BULLET.match(s) else "ol"
                if para or (items and tag != list_tag):
                    flush()
                list_tag = tag
                items.append(item.group(1))
                continue
            if items and line[:1].isspace():
                items[-1] += " " + s
                continue
            if items:
                flush()
            para.append(s)
        if code is not None:
            close_code()
        flush()
        return "".join(out)


def find_section(text: str, title: str) -> tuple[str, str] | None:
    """Returns the heading and body of the first section whose heading
    matches `title`, up to the next heading of the same or higher level."""
    lines = text.splitlines()
    in_fence = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else HEADING.match(line)
        if not m or not re.search(title, m.group(2), re.I):
            continue
        level, body, fenced = len(m.group(1)), [], False
        for nxt in lines[i + 1:]:
            if nxt.strip().startswith("```"):
                fenced = not fenced
            h = None if fenced else HEADING.match(nxt)
            if h and len(h.group(1)) <= level:
                break
            body.append(nxt)
        return m.group(2).strip(), "\n".join(body).strip()
    return None


def decisions(links: Links) -> list[dict]:
    found = []
    for path in sorted(Path(DECISIONS).glob("[0-9][0-9][0-9][0-9]-*.md")):
        if path.name.startswith("0000-"):
            continue
        text = path.read_text(encoding="utf-8")
        source = path.as_posix()
        title = re.search(r"^#\s+(?:Decision\s+\d+:\s*)?(.+)$", text, re.M)
        status = re.search(r"^\*\*Status:\*\*\s*(.+)$", text, re.M)
        date = re.search(r"^\*\*Date:\*\*\s*(.+)$", text, re.M)
        status_text = status.group(1).strip() if status else "Unknown"
        found.append({
            "number": path.name[:4],
            "title": title.group(1).strip() if title else path.stem,
            "status": Markdown(links, source).inline(status_text),
            "kind": status_text.split()[0].lower(),
            "date": date.group(1).strip() if date else "",
            "url": links.to(source),
        })
    return found


def freshness(today: dt.date) -> list[dict]:
    excludes = [f":(exclude){p}" for p in DOC_PATHSPECS]
    rows = []
    for role, path in DOCUMENTS:
        if not Path(path).exists():
            continue
        last = git("log", "-1", "--format=%H %cs", "--", path)
        if not last:
            rows.append({"role": role, "path": path, "date": None})
            continue
        sha, date = last.split()
        age = (today - dt.date.fromisoformat(date)).days
        since = int(git("rev-list", "--count", f"{sha}..HEAD", "--", ".", *excludes))
        rows.append({
            "role": role, "path": path, "date": date, "age": age,
            "since": since,
            "review": age > STALE_AFTER_DAYS and since > 0,
        })
    return rows


def milestones(repo: str) -> list[dict]:
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    request = urllib.request.Request(
        f"{api}/repos/{repo}/milestones"
        "?state=open&sort=due_on&direction=asc&per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "colophon-overview",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def section(title: str, body: str, source: str | None = None,
            links: Links | None = None) -> str:
    origin = ""
    if source and links:
        origin = f' <a class="origin" href="{esc(links.to(source))}">{esc(source)}</a>'
    return f"<section><h2>{esc(title)}{origin}</h2>{body}</section>"


def fact(value: str, label: str) -> str:
    return f'<div class="fact"><b>{value}</b><span>{label}</span></div>'


def plural(count: int, word: str) -> str:
    return word if count == 1 else word + "s"


def build(repo: str | None, out_dir: Path) -> str:
    today = dt.datetime.now(dt.timezone.utc).date()
    sha = git("rev-parse", "HEAD")
    links = Links(repo, sha, out_dir)
    brief = read(BRIEF) or ""
    name_match = re.search(r"^#\s+(.+)$", brief, re.M)
    name = name_match.group(1).strip() if name_match else Path.cwd().name
    notes = []
    if git("rev-parse", "--is-shallow-repository") == "true":
        notes.append("History is shallow, so dates and counts below are "
                     "incomplete. Check out with full history.")

    parts, facts = [], []

    status = find_section(brief, r"^status\b")
    if status:
        body = f'<div class="md">{Markdown(links, BRIEF).block(status[1])}</div>'
        parts.append(section(status[0], body, BRIEF, links))
    else:
        parts.append(section("Status & milestones",
                             '<p class="note">The Brief has no status section.</p>'))

    if repo:
        try:
            rows = []
            for m in milestones(repo):
                done, total = m["closed_issues"], m["closed_issues"] + m["open_issues"]
                pct = round(100 * done / total) if total else 0
                due = (m.get("due_on") or "")[:10] or "—"
                rows.append(
                    f'<tr><td><a href="{esc(m["html_url"])}">{esc(m["title"])}</a></td>'
                    f"<td>{due}</td><td>{done} / {total}</td>"
                    f'<td><div class="bar"><i style="width:{pct}%"></i></div></td></tr>'
                )
            body = (
                '<div class="scroll"><table><thead><tr><th>Milestone</th><th>Due</th>'
                f"<th>Closed</th><th>Progress</th></tr></thead><tbody>{''.join(rows)}"
                "</tbody></table></div>"
                if rows else '<p class="note">No open milestones.</p>'
            )
        except Exception as error:  # the page still builds without them
            body = f'<p class="note">Milestones unavailable: {esc(str(error))}</p>'
        parts.append(section("Milestones", body))

    found = decisions(links)
    if found:
        rows = "".join(
            f'<tr><td>{d["number"]}</td><td><a href="{esc(d["url"])}">{esc(d["title"])}</a></td>'
            f'<td><span class="badge {esc(d["kind"])}">{d["status"]}</span></td>'
            f'<td>{esc(d["date"])}</td></tr>'
            for d in found
        )
        parts.append(section("Decisions", (
            '<div class="scroll"><table><thead><tr><th>#</th><th>Decision</th>'
            f"<th>Status</th><th>Date</th></tr></thead><tbody>{rows}</tbody></table></div>"
        ), DECISIONS, links))
        counts: dict[str, int] = {}
        for d in found:
            counts[d["kind"]] = counts.get(d["kind"], 0) + 1
        facts.append(fact(str(len(found)), " · ".join(
            f"{n} {kind}" for kind, n in sorted(counts.items()))))

    changelog = read(CHANGELOG)
    if changelog:
        released = [m for m in RELEASE.finditer(changelog)
                    if m.group(1).lower() != "unreleased"]
        if released:
            version, date = released[0].group(1), released[0].group(2) or ""
            facts.insert(0, fact(esc(version), f"latest release {esc(date)}".strip()))
        unreleased = find_section(changelog, r"^\[unreleased\]")
        if unreleased and unreleased[1]:
            count = len(re.findall(r"^[-*+]\s", unreleased[1], re.M))
            facts.insert(1, fact(str(count), f"unreleased {plural(count, 'change')}"))
            body = f'<div class="md">{Markdown(links, CHANGELOG).block(unreleased[1])}</div>'
            parts.append(section("Unreleased changes", body, CHANGELOG, links))

    log = read(LOG)
    entries = sorted(LOG_ENTRY.findall(log or ""), key=lambda e: e[0])
    if entries:
        date, topic = entries[-1]
        facts.append(fact(esc(date), f"latest Log entry: {esc(topic)}"))

    rows, review = [], 0
    for r in freshness(today):
        if r["date"] is None:
            cells = '<td colspan="3">not committed yet</td><td></td>'
        else:
            review += r["review"]
            flag = '<span class="badge review">review</span>' if r["review"] else ""
            cells = (f'<td>{r["date"]}</td><td>{r["age"]} days</td>'
                     f'<td>{r["since"]}</td><td>{flag}</td>')
        rows.append(f'<tr><td><a href="{esc(links.to(r["path"]))}">{r["role"]}</a></td>{cells}</tr>')
    facts.append(fact(str(review), f"{plural(review, 'document')} to review"))
    parts.append(section("Doc freshness", (
        '<div class="scroll"><table><thead><tr><th>Document</th><th>Last changed</th>'
        "<th>Age</th><th>Commits elsewhere since</th><th></th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
        f'<p class="note">Flagged when older than {STALE_AFTER_DAYS} days while '
        "the rest of the repository has changed since.</p>"
    )))

    commit_url = links.commit()
    commit = (f'<a href="{esc(commit_url)}">{sha[:7]}</a>' if commit_url
              else f"<code>{sha[:7]}</code>")
    note_html = "".join(f'<p class="note warn">{esc(n)}</p>' for n in notes)
    return PAGE.format(
        title=esc(name),
        facts="".join(facts),
        notes=note_html,
        sections="".join(parts),
        footer=(f"Generated from commit {commit} on {today.isoformat()}. "
                "Do not edit this page: change the source files and it rebuilds."),
    )


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — overview</title>
<style>
:root {{
  --bg: #fbfaf7; --card: #ffffff; --fg: #1d1d1b; --muted: #6b6a65;
  --line: #e4e1d8; --accent: #2f5d50; --ok: #2f6f3e; --info: #2c5f8a;
  --off: #7a7a7a; --warn: #9a5b00;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #151514; --card: #1d1c1a; --fg: #e9e7e1; --muted: #9c9a93;
    --line: #2f2e2b; --accent: #8fc1b0; --ok: #7cc48f; --info: #86b6dd;
    --off: #8d8d8d; --warn: #e0a650;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width: 920px; margin: 0 auto; padding: 32px 16px 64px; }}
h1 {{ font-size: 1.8rem; margin: 0 0 20px; }}
h2 {{ font-size: .85rem; text-transform: uppercase; letter-spacing: .07em;
  color: var(--muted); border-bottom: 1px solid var(--line);
  padding-bottom: 6px; display: flex; justify-content: space-between; gap: 12px; }}
h2 .origin {{ text-transform: none; letter-spacing: 0; font-weight: 400; }}
section {{ margin-top: 36px; }}
a {{ color: var(--accent); }}
code {{ font-family: ui-monospace, Consolas, monospace; font-size: .9em; }}
pre {{ background: var(--card); border: 1px solid var(--line); border-radius: 6px;
  padding: 10px 12px; overflow-x: auto; }}
.facts {{ display: grid; gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); }}
.fact {{ background: var(--card); border: 1px solid var(--line);
  border-radius: 8px; padding: 12px 14px; }}
.fact b {{ display: block; font-size: 1.3rem; }}
.fact span {{ color: var(--muted); font-size: .85rem; }}
.scroll {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--line);
  vertical-align: top; }}
th {{ color: var(--muted); font-size: .85rem; font-weight: 600; }}
.badge {{ display: inline-block; padding: 0 8px; border-radius: 999px;
  border: 1px solid currentColor; font-size: .8rem; white-space: nowrap; }}
.badge a {{ color: inherit; }}
.accepted {{ color: var(--ok); }}
.proposed {{ color: var(--info); }}
.superseded, .deprecated, .rejected {{ color: var(--off); }}
.review, .warn {{ color: var(--warn); }}
.bar {{ min-width: 80px; height: 6px; margin-top: 9px; border-radius: 3px;
  background: var(--line); overflow: hidden; }}
.bar i {{ display: block; height: 100%; background: var(--accent); }}
.md h4 {{ margin: 18px 0 6px; }}
.note {{ color: var(--muted); font-size: .9rem; }}
footer {{ margin-top: 48px; padding-top: 12px; border-top: 1px solid var(--line);
  color: var(--muted); font-size: .85rem; }}
</style>
</head>
<body>
<main>
<h1>{title}</h1>
<div class="facts">{facts}</div>
{notes}
{sections}
<footer>{footer}</footer>
</main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="_site",
                        help="output directory (default: _site)")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"),
                        help="owner/name on GitHub, for links and milestones")
    args = parser.parse_args()
    out_dir = Path(args.out).resolve()
    try:
        os.chdir(git("rev-parse", "--show-toplevel"))
        page = build(args.repo, out_dir)
    except RuntimeError as error:
        sys.exit(f"overview: {error}")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    print(f"overview: wrote {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
