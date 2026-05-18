**English** · [한국어](README.md)

# Claude Code Skills & Agents

A collection of custom [Claude Code](https://claude.com/claude-code) skills and
subagents built and used in a real research workflow — scientific writing,
presentation QA, figure/document tooling, and media pipelines.

These are modular: each skill is self-contained in its own folder with a
`SKILL.md` (and an optional helper script). Take what is useful, ignore the
rest.

## Install

```
# copy into the Claude Code user directory
cp -r skills/*  ~/.claude/skills/
cp    agents/*  ~/.claude/agents/
```

Windows PowerShell:

```
Copy-Item skills\* "$HOME\.claude\skills\" -Recurse
Copy-Item agents\* "$HOME\.claude\agents\"
```

Restart Claude Code after copying so the skills and agents are picked up.

## Skills vs. Agents

This repo ships both **skills** and **agents**. They are different roles:

- **Skill** = reusable knowledge / rules. It defines *how* a task is done.
- **Agent** = an autonomous subagent that *executes* using a skill.

So some appear as pairs — `paper-sections` (skill) with
`paper-section-drafter` (agent), `paper-style` (skill) with
`paper-style-enforcer` (agent). This is not duplication: it is a
deliberate split between the "rules" and the "executor that runs them".
Use a skill on its own, or let the agent automate it.

## Catalog

### Scientific Writing & Citation

- **paper-sections** `skill` — Playbooks for drafting IMRAD sections
  (Introduction, Methods, Results, Discussion, Outlook) plus
  numeric-superscript citation formatting rules.
- **paper-style** `skill` — Load the author's STYLE_PROFILE, or run a
  light AI-ism cleanup (humanize) on a paragraph.
- **paper-section-drafter** `agent` — Draft a specific IMRAD section in the
  author's voice under STYLE_PROFILE, returning the draft plus assumptions
  and data gaps.
- **paper-scientific-critic** `agent` — Critique a paragraph or section for
  methodological rigor, claim–evidence alignment, logical gaps, and
  overclaims.
- **paper-style-enforcer** `agent` — Mechanical STYLE_PROFILE compliance
  check (banned words, sentence length, rhetorical questions, hedge stacks,
  figure-reference patterns).
- **paper-ref-hunter** `agent` — Reference resolver in two modes: HUNT (a
  specific citation → verified Crossref DOI) and DISCOVERY (a topic →
  ranked OpenAlex candidates). Never fabricates a DOI.
- **reference-crosscheck** `skill` — Citation ↔ reference cross-check for
  `.hwp` (binary), `.hwpx` (OWPML), and `.docx`. Detects phantom, orphan,
  numbering mismatch, duplicate, and multi-location references, plus
  optional Tier-2 Crossref existence verification (calls paper-ref-hunter).
  Source never modified; annotated copy + Markdown/JSON report. 757-line
  engine `refcheck.py`. (python-docx, lxml)

### Data Analysis & Figures

- **analysis-protocol** `skill` — An evidence gate for spectroscopic
  peak-fitting. Validates an lmfit result with quant/visual (hard) and
  sanity (soft) checks so a bad fit never leaks into a figure or a written
  claim. Generic across NH3-TPD / Py-DRIFTS / TPO / XPS / XRD.
  (numpy, lmfit)
- **matplotlib-scientific** `skill` — Rules for publication-grade
  matplotlib figures (font stack, 300 DPI SVG export, explicit layout
  control). (matplotlib)

### Documents & Reports

- **docx-scientific-formatting** `skill` — Normalize chemistry/physics
  notation in `.docx` files (subscripts, superscripts, italic orbitals,
  chemical formulae). (python-docx, lxml)
- **html-minimal** `skill` — A minimal HTML document design system
  (restrained typography, line + whitespace structure) for reports and
  briefings.

### Presentation

- **slide-audit** `skill` — Render an HTML slide deck to PNGs with
  Playwright, run a bounding-rect diagnostic, and dispatch subagents for
  visual review. Catches text overlap, clipping, and overflow.
  (Node.js, Playwright)

### Media

- **youtube** `skill` — Extract a YouTube transcript + metadata + smart
  frame captures (heatmap peaks / chapters / uniform interval) as
  timestamped Markdown. (yt-dlp, ffmpeg)
- **youtube2mp4** `skill` — Download a YouTube video as MP4 (resolution
  cap, audio-only, time-trim). (yt-dlp, ffmpeg)
- **transcript2html** `skill` — Convert a YouTube `transcript.md` into a
  cleaned Markdown + dark-mode HTML document with embedded frames and
  translated captions. Dark template included.

### 3D / Utility

- **blender-atom-render** `skill` — Render individual atom spheres from
  structure files (traj/xyz) with Blender and build a per-system legend.
  (Blender, ASE, Pillow)
- **smart-compact** `skill` — Save session state to
  `.claude/session-state.md` so work can be recovered after `/clear`.

## Dependencies

Per-skill — see the parentheses above. Python 3.9+ is assumed in general;
only `slide-audit` needs Node.js + Playwright.

## Notes

- The `paper-*` skills and agents reference a user-authored
  `~/.claude/paper-team/STYLE_PROFILE.md` (your own writing rules). That
  profile is **not** included here — supply your own.
- Some skills reference other skills/slash commands (e.g. `transcript2html`
  ← `youtube`). They work standalone but compose more smoothly together.

## License

MIT — see [LICENSE](LICENSE).
