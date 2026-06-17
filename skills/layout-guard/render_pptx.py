#!/usr/bin/env python
"""
layout-guard / render_pptx.py

AUTHORITATIVE PPTX check: render each slide to a real PNG so a visual audit can
give a true pass/fail verdict (the XML engine measure_pptx.py is only triage —
it cannot see font inheritance, autofit growth, or text wrapping). After this
produces PNGs + manifest.json, dispatch the slide-audit visual-subagent prompt
on them exactly like an HTML deck.

Two render backends, preferred in this order:

  1. LibreOffice (soffice) — headless, no session risk. PPTX -> PDF -> PNG.
     Preferred whenever installed.
  2. PowerPoint COM (win32com) — uses the installed PowerPoint. PowerPoint is a
     SINGLE-INSTANCE app, so if the user already has it open, automating + Quit
     would CLOSE THEIR SESSION. Therefore
     this backend ABORTS if PowerPoint is already running. It only spawns/quits
     an instance when none exists.

Usage:
    python render_pptx.py <pptx> [outdir]

Output:
    <outdir>/slide_NN.png  +  <outdir>/manifest.json
Exit codes: 0 rendered, 3 no backend / refused (caller falls back to triage only).
"""
import os
import sys
import json
import shutil
import subprocess


def find_soffice():
    cand = shutil.which("soffice") or shutil.which("soffice.exe")
    if cand:
        return cand
    for p in (
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ):
        if os.path.exists(p):
            return p
    return None


def powerpoint_running():
    """True if a POWERPNT.EXE process exists (Windows)."""
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=20).stdout
        return "POWERPNT.EXE" in out.upper()
    except Exception:
        return False  # can't tell -> assume not, COM guard below still applies


def render_with_soffice(soffice, pptx, outdir):
    import fitz  # PyMuPDF
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, pptx],
        check=True, capture_output=True, timeout=180,
    )
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    if not os.path.exists(pdf):
        raise RuntimeError("soffice did not produce a PDF")
    doc = fitz.open(pdf)
    pngs = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1920 / page.rect.width, 1920 / page.rect.width))
        out = os.path.join(outdir, f"slide_{i:02d}.png")
        pix.save(out)
        pngs.append(out)
    doc.close()
    return pngs


def render_with_powerpoint(pptx, outdir):
    if powerpoint_running():
        sys.exit(
            "REFUSED: PowerPoint is already running. Automating it could close your "
            "open session. Close PowerPoint and retry, or install LibreOffice for a "
            "headless render. (XML triage via measure_pptx.py still works meanwhile.)"
        )
    import win32com.client
    app = win32com.client.DispatchEx("PowerPoint.Application")
    pngs = []
    pres = None
    try:
        try:
            app.Visible = 1  # PowerPoint refuses some ops while fully hidden
        except Exception:
            pass
        pres = app.Presentations.Open(os.path.abspath(pptx), ReadOnly=1, Untitled=0, WithWindow=0)
        for i in range(1, pres.Slides.Count + 1):
            # PowerPoint COM needs a native Windows path (backslashes, drive). A
            # POSIX/git-bash path like /tmp/x makes Slide.Export fail.
            out = os.path.normpath(os.path.abspath(os.path.join(outdir, f"slide_{i:02d}.png")))
            pres.Slides(i).Export(out, "PNG", 1920, 1080)
            pngs.append(out)
    finally:
        if pres is not None:
            pres.Close()
        app.Quit()  # safe: we created this isolated instance (none was running)
    return pngs


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python render_pptx.py <pptx> [outdir]")
    pptx = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(pptx)),
        "_render_" + os.path.splitext(os.path.basename(pptx))[0],
    )
    outdir = os.path.normpath(os.path.abspath(outdir))  # native path for COM/soffice
    os.makedirs(outdir, exist_ok=True)

    soffice = find_soffice()
    if soffice:
        backend = "libreoffice"
        pngs = render_with_soffice(soffice, pptx, outdir)
    else:
        backend = "powerpoint-com"
        try:
            import win32com.client  # noqa: F401
        except ImportError:
            sys.exit("No render backend: install LibreOffice, or `pip install pywin32`.")
        pngs = render_with_powerpoint(pptx, outdir)

    manifest = {"source": os.path.abspath(pptx), "backend": backend, "slides": pngs}
    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"rendered {len(pngs)} slide(s) via {backend} -> {outdir}")
    print("Next: dispatch the slide-audit visual-subagent prompt on these PNGs for pass/fail.")


if __name__ == "__main__":
    main()
