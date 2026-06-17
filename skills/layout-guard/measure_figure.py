#!/usr/bin/env python
"""
layout-guard / measure_figure.py

Overlap detection for composed scientific figures — the labels/legends/annotations
that collide when panels are assembled. Two entry points:

  A) check_mpl(fig)  — call BEFORE fig.savefig(). Uses the renderer to get the
     true pixel bbox of every Text artist (titles, labels, tick labels, legend,
     annotations) and reports pairs whose boxes intersect. This is exact — it is
     the renderer's own metrics, not an estimate.

  B) check_pil(boxes) — for PIL-composed panels. PIL has no layout engine, so you
     MUST measure each text with draw.textbbox(...) at draw time and pass the
     boxes here. Returns intersecting pairs.

Run as a script to self-test:  python measure_figure.py

Design note: figure overlap is best caught at GENERATION time inside the plotting
script (import this, call check_mpl(fig) before savefig), not after the PNG exists
— once rasterized, only a vision pass can see it. So the real fix is the
PREVENTION rules (constrained_layout / bbox_inches='tight' / legend outside axes).
This module is the deterministic backstop.
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp949 console safety
except Exception:
    pass


def _intersect(a, b):
    """a, b = (x0, y0, x1, y1). Returns intersection (w, h) in px, or None."""
    ix = min(a[2], b[2]) - max(a[0], b[0])
    iy = min(a[3], b[3]) - max(a[1], b[1])
    if ix > 1 and iy > 1:
        return (round(ix), round(iy))
    return None


def check_mpl(fig, min_overlap_px=2):
    """Return list of overlapping Text-artist pairs in `fig`. Empty = clean."""
    fig.canvas.draw()  # realize the renderer
    rend = fig.canvas.get_renderer()
    import matplotlib.text as mtext

    texts = []
    for ax in fig.get_axes():
        for t in ax.texts + [ax.title, ax.xaxis.label, ax.yaxis.label]:
            if isinstance(t, mtext.Text) and t.get_text().strip():
                texts.append(t)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            if lbl.get_text().strip():
                texts.append(lbl)
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                texts.append(t)
    for t in fig.texts:
        if t.get_text().strip():
            texts.append(t)

    boxes = []
    for t in texts:
        try:
            bb = t.get_window_extent(renderer=rend)
            boxes.append((t, (bb.x0, bb.y0, bb.x1, bb.y1)))
        except Exception:
            pass

    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ov = _intersect(boxes[i][1], boxes[j][1])
            if ov and ov[0] >= min_overlap_px and ov[1] >= min_overlap_px:
                hits.append({
                    "a": boxes[i][0].get_text()[:30],
                    "b": boxes[j][0].get_text()[:30],
                    "overlap_px": ov,
                })
    return hits


def check_pil(boxes):
    """`boxes` = list of (label, (x0, y0, x1, y1)) measured via draw.textbbox().
    Returns intersecting pairs."""
    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ov = _intersect(boxes[i][1], boxes[j][1])
            if ov:
                hits.append({"a": boxes[i][0], "b": boxes[j][0], "overlap_px": ov})
    return hits


def report(hits, kind="figure"):
    if not hits:
        print(f"✓ {kind} clean — no text overlap")
        return 0
    print(f"✗ {kind} — {len(hits)} overlapping text pair(s):")
    for h in hits:
        print(f'    {h["overlap_px"][0]}x{h["overlap_px"][1]}px  "{h["a"]}"  ✕  "{h["b"]}"')
    return 2


if __name__ == "__main__":
    # self-test: two labels forced to collide
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.text(0.5, 0.5, "AAAAAAAAAA", transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.5, "BBBBBBBBBB", transform=ax.transAxes, ha="center")
    code = report(check_mpl(fig), "self-test")
    sys.exit(code)
