---
name: reference-crosscheck
description: Universal reference / citation cross-check for HWP, HWPX, and Word documents. Verifies every in-text citation has a backing reference-list entry (phantom), flags uncited entries (orphan), numbering mismatches, duplicate reference entries, and the same reference appearing in multiple locations (body list + footnote/endnote, or more than one reference list). Two-stage existence check - Tier 1 internal consistency always runs offline; Tier 2 optionally verifies real-world existence of flagged entries via the paper-ref-hunter subagent (Crossref/DOI). Produces an annotated copy of the source plus a markdown + JSON findings report. Triggers - reference cross check, refer 중복, 인용 검증, 참고문헌 점검, citation cross-check, phantom citation, orphan reference, 중복 참고문헌, refer 실제로 있는지, hwp word 인용 점검, bibliography check, reference 정합성.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
dependencies: paper-ref-hunter
---

# reference-crosscheck

Universal reference cross-check across `.hwp` (binary HWP 5.0), `.hwpx`
(OWPML), and `.docx` (Word). Format handling is isolated in an extraction
layer; all cross-check logic is format-independent.

The engine is `refcheck.py` (next to this file). Do not reimplement its
logic inline - call the script.

## What it detects (Tier 1, always, offline)

- **phantom**  - cited in text but no matching reference-list entry
- **orphan**   - in the reference list but never cited
- **numbering** - cited number exceeds list size / list has gaps / reused number
- **duplicate** - the same source listed more than once (exact + near-dup
  by DOI / normalized signature)
- **multiloc** - the same reference present in more than one location:
  body bibliography + a footnote/endnote spelling it out, or more than one
  reference-list block (per-section + global). This is the
  "refer가 여러 위치에 있을 수도 있어서" requirement.

Citation style (`numeric` bracket `[12]`, numeric superscript, or
`author-year (Kim et al., 2020)` incl. Korean `(홍길동 외, 2020)`) is
auto-detected; override with `--style`.

## Two-stage existence check

Requirement 3 ("refer가 실제로 있는지 확인") is two-stage by design:

1. **Tier 1 (default)** - internal existence: does each in-text citation
   actually resolve to a real entry in the reference list? Runs offline,
   deterministic, no network.
2. **Tier 2 (opt-in)** - real-world existence: do the flagged entries
   correspond to papers that actually exist? `refcheck.py --tier2-queue`
   emits `*.crossref_queue.json` (high-priority = duplicate / orphan /
   no-DOI entries). Dispatch the **paper-ref-hunter** subagent in HUNT mode
   on each high-priority item, then fold verified DOIs / "not found" back
   into the report. Never fabricate a DOI - if paper-ref-hunter cannot
   resolve it, label the entry `unverified`.

## Workflow

1. Confirm the target file path and format. If `.doc` (legacy binary
   Word) or a scanned PDF, tell the user it is out of scope and offer to
   convert (`.doc` -> `.docx` via Word/LibreOffice) first - do not guess.
2. Run Tier 1:
   ```
   python "~/.claude/skills/reference-crosscheck/refcheck.py" \
       "<INPUT>" --outdir "<OUTDIR>" [--tier2-queue]
   ```
   Outputs: `<stem>.refcheck.md`, `<stem>.refcheck.json`, annotated copy
   (`.annotated.docx` / `.annotated.hwpx` / `.annotated.txt`), and
   `<stem>.crossref_queue.json` when `--tier2-queue` is set.
3. Read `<stem>.refcheck.md`. Summarize phantom / orphan / duplicate /
   multiloc / numbering counts to the user with the concrete offending
   tokens (not just counts).
4. If the user asks for real-existence (Tier 2): for each
   `priority: high` queue item, dispatch `paper-ref-hunter` (HUNT mode)
   with the entry's author/year/title/DOI. Append a "Tier 2 verification"
   section to the report: `verified (DOI)`, `mismatch`, or `unverified`.
5. Hand back: the annotated copy as the primary deliverable, the markdown
   report for re-review, and an escalation list of anything ambiguous
   (e.g. author-year keys that fuzzy-matched but are not exact).

## Per-format annotation fidelity (be honest about limits)

- **.docx** - real Word comments anchored on the offending citation runs
  (`Document.add_comment`) + yellow highlight. Source untouched; a copy
  `*.annotated.docx` is produced.
- **.hwpx** - best-effort visible marker `〔refcheck:...〕` injected next
  to the token in the section XML, repackaged as `*.annotated.hwpx`.
  Positional fidelity is lower than docx; always rely on the report too.
- **.hwp** (binary) - cannot be safely rewritten. A `*.annotated.txt`
  sidecar with inline markers is produced instead. State this explicitly
  to the user; do not claim the .hwp itself was annotated.

In every case the markdown + JSON findings are authoritative; annotation
is an aid, not the source of truth.

## Guardrails

- Never overwrite the source. All outputs are new files (version guard).
- If extraction falls back to `hwp-preview` (olefile PrvText), warn the
  user the text is a truncated preview and the check is partial - offer
  to convert the `.hwp` to `.hwpx` for a full pass.
- Report counts AND the offending tokens with their location, never a
  bare "N issues found".
- Tier 2 DOIs come only from paper-ref-hunter. No invented identifiers.
