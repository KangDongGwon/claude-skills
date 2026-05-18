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

## Catalog

### Skills

- **slide-audit** — Render an HTML slide deck to PNGs with Playwright, run a
  bounding-rect diagnostic, and dispatch subagents for visual review.
  Catches text overlap, clipping, and overflow. (Node.js, Playwright)
- **matplotlib-scientific** — Rules for publication-grade matplotlib figures
  (font stack, 300 DPI SVG export, explicit layout control). (matplotlib)
- **docx-scientific-formatting** — Normalize chemistry/physics notation in
  `.docx` files (subscripts, superscripts, italic orbitals, chemical
  formulae). (python-docx, lxml)
- **html-minimal** — A minimal HTML document design system (restrained
  typography, line + whitespace structure) for reports and briefings.
- **transcript2html** — Convert a YouTube `transcript.md` into a cleaned
  Markdown + dark-mode HTML document with embedded frames and translated
  captions. Dark template included.
- **youtube** — Extract a YouTube transcript + metadata + smart frame
  captures (heatmap peaks / chapters / uniform interval) as timestamped
  Markdown. (yt-dlp, ffmpeg)
- **youtube2mp4** — Download a YouTube video as MP4 (resolution cap,
  audio-only, time-trim). (yt-dlp, ffmpeg)
- **blender-atom-render** — Render individual atom spheres from structure
  files (traj/xyz) with Blender and build a per-system legend.
  (Blender, ASE, Pillow)
- **reference-crosscheck** — Citation ↔ reference cross-check for `.hwp`
  (binary), `.hwpx` (OWPML), and `.docx`. Detects phantom (cited but not
  listed), orphan, numbering mismatch, duplicate, and multi-location
  references, plus optional Tier-2 Crossref existence verification. Source
  is never modified; produces an annotated copy + Markdown/JSON report.
  757-line engine `refcheck.py`. (python-docx, lxml; Tier 2 uses
  paper-ref-hunter)
- **analysis-protocol** — An evidence gate for spectroscopic peak-fitting.
  Validates an lmfit result with quant/visual (hard) and sanity (soft)
  checks so a bad fit never leaks into a figure or a written claim. Generic
  across NH3-TPD / Py-DRIFTS / TPO / XPS / XRD. (numpy, lmfit)
- **paper-sections** — Playbooks for drafting IMRAD sections (Introduction,
  Methods, Results, Discussion, Outlook) plus numeric-superscript citation
  formatting rules.
- **paper-style** — Load the author's STYLE_PROFILE, or run a light AI-ism
  cleanup (humanize) on a paragraph.
- **smart-compact** — Save session state to `.claude/session-state.md` so
  work can be recovered after `/clear`.

### Agents (subagents)

- **paper-section-drafter** — Draft a specific IMRAD section in the author's
  voice under STYLE_PROFILE, returning the draft plus assumptions and data
  gaps.
- **paper-scientific-critic** — Critique a paragraph or section for
  methodological rigor, claim–evidence alignment, logical gaps, and
  overclaims.
- **paper-style-enforcer** — Mechanical STYLE_PROFILE compliance check
  (banned words, sentence length, rhetorical questions, hedge stacks,
  figure-reference patterns).
- **paper-ref-hunter** — Reference resolver in two modes: HUNT (a specific
  citation → verified Crossref DOI) and DISCOVERY (a topic → ranked
  OpenAlex candidates). Never fabricates a DOI. Called by
  reference-crosscheck for Tier-2 verification.

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
