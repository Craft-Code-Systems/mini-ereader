# Runbook — Adopting Colophon

How to turn this template into a working Colophon project, and how
to keep it healthy over time.

For applying Colophon to an existing project, see
[adoption.md](./adoption.md).

---

## Setting up a new project

1. **Create from template**
   ```
   gh repo create my-project --template Craft-Code-Systems/colophon --public
   cd my-project
   ```
   Or click **Use this template** on GitHub.

2. **Rewrite the Brief (`README.md`)**
   - Replace the Colophon description with your project's purpose.
   - Fill in scope, non-scope, success criteria, stack.
   - Keep it to one or two screens.

3. **Clean the Decisions folder**
   - Delete Colophon's own Decisions (`0001-` through `0005-`).
   - Keep `0000-template.md` — it is the template for your first
     Decision.

4. **Rewrite the Runbook**
   - This file. Replace with how *your* project runs and deploys.
   - Include "how to unbreak at 3am" notes.

5. **Reset the Log and Changelog**
   - Empty `docs/research-log.md` — keep the header only.
   - Empty `CHANGELOG.md` down to the header and an `[Unreleased]`
     section.

6. **Optional: add a Spec**
   - If your project genuinely needs richer requirements documentation
     (prototyping many capabilities, formal stakeholder requirement),
     copy `templates/SPEC.template.md` to `docs/spec.md`.
     Otherwise skip — most projects do not need one. See
     [adoption.md](./adoption.md#when-to-add-the-optional-spec).

Total time: around ten minutes. You now have a working Colophon setup.

---

## Daily use

- **Made a real design choice?** → add a Decision in `docs/adr/`.
  Copy `0000-template.md`, increment the number, fill it in.
  Keep it to roughly one screen.
- **Explored something, found facts worth keeping?** → append a
  dated entry to the Log. Do not rewrite older entries.
- **Shipped something?** → add a line to the Changelog under
  `[Unreleased]`. Group by *Added / Changed / Fixed / Removed*.
- **Changed how you run or deploy?** → update the Runbook.
- **Project direction shifted?** → update the Brief. It should
  always reflect current reality.

---

## Writing a Decision (the ritual)

1. Copy `docs/adr/0000-template.md` to
   `docs/adr/NNNN-short-title.md`.
2. Increment `NNNN` by one over the highest existing number.
3. Fill in *Context*, *Decision*, *Considerations*, *Consequences*.
4. Commit in the same pull request as the code change, where possible.
5. Never edit an accepted Decision's *Decision* section. If you
   change your mind, write a new Decision that supersedes it, and
   update the old one's Status to `Superseded by Decision NNNN`.
   See [adoption.md](./adoption.md#when-a-structural-design-choice-changes)
   for a full worked example.

---

## Keeping it healthy

Signs your Colophon setup is drifting:

- The Brief no longer reflects what the project does → update it.
- `docs/adr/` has design choices you never wrote down → write them
  retroactively if still relevant; skip if not.
- The Runbook is out of date → fix the next time it bites you,
  not before.
- The Changelog has not been touched in months → you are either not
  shipping, or not recording. Both worth attention.

Rule of thumb: if a file has not been touched in a long time *and*
nobody has needed it in a long time, consider deleting it.
Colophon files earn their place or leave.

---

## Integration notes

- **With Diátaxis**: Colophon covers project-internal docs. If your
  project needs user-facing tutorials and reference, put those in a
  separate `user-docs/` folder (or a dedicated site) structured per
  Diátaxis. The two do not overlap.
- **With Doxygen / Sphinx / JSDoc**: these generate API reference
  from source comments. That is different from Colophon and
  complementary. Link to the generated output from the Brief.
- **With compliance documents**: keep those in whatever system the
  regulator requires. Do not try to fold them into Colophon.
