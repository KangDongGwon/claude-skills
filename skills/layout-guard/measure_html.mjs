#!/usr/bin/env node
/*
 * layout-guard / measure_html.mjs
 *
 * GENERIC overlap / overflow detector for ANY HTML artifact — not tied to a
 * specific deck convention. Models slide-audit/measure.mjs but detects the
 * three failure classes structurally, without knowing the author's class names:
 *
 *   1. viewport-overflow  — element extends past the render canvas
 *   2. parent-overflow    — element extends past its own scrollable box
 *   3. text-overlap       — two text-bearing leaf elements whose rects intersect
 *                           (the "글씨 겹침" the user keeps reporting)
 *
 * Rect-based diagnostics are deterministic. If they disagree with a visual
 * subagent, trust the rects (slide-audit lesson: rects don't lie).
 *
 * Usage:
 *   node measure_html.mjs <html-path> [--mode deck|page] [--slide-selector .slide]
 *                                     [--active-class is-active] [--w 1920] [--h 1080]
 *
 *   mode=deck : fixed canvas (e.g. 1920x1080 slides). Each .slide is activated
 *               one at a time; both-axis canvas overflow is an error.
 *   mode=page : scrolling document (reports). Vertical growth is normal, so only
 *               HORIZONTAL viewport overflow is flagged, plus parent-overflow and
 *               text-overlap across the whole document.
 *
 * Output: human lines on stdout + a JSON blob after a `---JSON---` marker so a
 * caller can parse findings. Exit code 2 if any issue found.
 */

import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';

function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const htmlArg = process.argv[2];
if (!htmlArg || htmlArg.startsWith('--')) {
  console.error('Usage: node measure_html.mjs <html-path> [--mode deck|page] [--slide-selector .slide] [--active-class is-active] [--w 1920] [--h 1080]');
  process.exit(1);
}
const mode = arg('mode', 'page');
const slideSel = arg('slide-selector', '.slide');
const activeClass = arg('active-class', 'is-active');
const W = parseInt(arg('w', '1920'), 10);
const H = parseInt(arg('h', '1080'), 10);

const htmlPath = path.resolve(htmlArg);
await fs.access(htmlPath);

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: W, height: H },
  deviceScaleFactor: 1,
  reducedMotion: 'reduce',
});
const page = await context.newPage();
await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle' });

// The detector runs entirely in the browser for one "scene" (either the whole
// page, or one activated slide). Returns {viewport, parent, overlap} findings.
const detect = (canvasW, canvasH, pageMode) =>
  page.evaluate(
    ({ canvasW, canvasH, pageMode }) => {
      const vis = (el) => {
        const s = getComputedStyle(el);
        if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0)
          return false;
        const r = el.getBoundingClientRect();
        return r.width > 0.5 && r.height > 0.5;
      };
      // direct non-whitespace text node => this element renders a text run itself
      const hasOwnText = (el) =>
        [...el.childNodes].some(
          (n) => n.nodeType === 3 && n.textContent.trim().length > 0,
        );
      const rectOf = (el) => {
        const r = el.getBoundingClientRect();
        return { l: r.left, t: r.top, r: r.right, b: r.bottom, w: r.width, h: r.height };
      };
      const label = (el) => {
        const id = el.id ? `#${el.id}` : '';
        const cls = el.className && typeof el.className === 'string'
          ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.')
          : '';
        const txt = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 28);
        return `${el.tagName.toLowerCase()}${id}${cls}"${txt}"`;
      };

      const all = [...document.querySelectorAll('body *')].filter(vis);
      const findings = { viewport: [], parent: [], overlap: [] };

      // 1 + 2: overflow
      for (const el of all) {
        const r = rectOf(el);
        // viewport overflow
        const overR = r.r - canvasW;
        const overB = r.b - canvasH;
        const overL = -r.l;
        const overT = -r.t;
        if (overR > 1 || overL > 1) {
          findings.viewport.push({ el: label(el), axis: 'x', by: Math.round(Math.max(overR, overL)) });
        }
        if (!pageMode && (overB > 1 || overT > 1)) {
          findings.viewport.push({ el: label(el), axis: 'y', by: Math.round(Math.max(overB, overT)) });
        }
        // parent content overflow (element's own content spills its clip box)
        const cs = getComputedStyle(el);
        const clipsX = cs.overflowX !== 'visible';
        const clipsY = cs.overflowY !== 'visible';
        if (clipsX && el.scrollWidth - el.clientWidth > 2)
          findings.parent.push({ el: label(el), axis: 'x', by: el.scrollWidth - el.clientWidth });
        if (clipsY && el.scrollHeight - el.clientHeight > 2)
          findings.parent.push({ el: label(el), axis: 'y', by: el.scrollHeight - el.clientHeight });
      }

      // 3: text-leaf overlap — the core "글씨 겹침" check.
      // Exclude pure inline elements (em/strong/a/span in running text): when they
      // wrap across lines their rects legitimately overlap inline siblings — that's
      // normal flow, not a collision. Real overlap = BLOCK boxes colliding
      // (absolute positioning, column encroachment, negative margins).
      const isInline = (el) => getComputedStyle(el).display === 'inline';
      const leaves = all
        .filter((el) => hasOwnText(el) && !isInline(el))
        .map((el) => ({ el, r: rectOf(el) }));
      const contains = (a, b) => a.el.contains(b.el) || b.el.contains(a.el);
      for (let i = 0; i < leaves.length; i++) {
        for (let j = i + 1; j < leaves.length; j++) {
          const A = leaves[i], B = leaves[j];
          if (contains(A, B)) continue;
          const ix = Math.min(A.r.r, B.r.r) - Math.max(A.r.l, B.r.l);
          const iy = Math.min(A.r.b, B.r.b) - Math.max(A.r.t, B.r.t);
          // require a real 2-D overlap, not a 1px border kiss
          if (ix > 3 && iy > 3) {
            findings.overlap.push({
              a: label(A.el),
              b: label(B.el),
              overlap: `${Math.round(ix)}x${Math.round(iy)}px`,
            });
          }
        }
      }
      return findings;
    },
    { canvasW, canvasH, pageMode },
  );

let report = [];
let hadIssue = false;

if (mode === 'deck') {
  const count = await page.$$eval(slideSel, (els) => els.length);
  for (let i = 0; i < count; i++) {
    await page.evaluate(
      ({ sel, cls, t }) => {
        const slides = document.querySelectorAll(sel);
        slides.forEach((s) => s.classList.remove(cls));
        slides[t].classList.add(cls);
      },
      { sel: slideSel, cls: activeClass, t: i },
    );
    await page.waitForTimeout(40);
    const f = await detect(W, H, false);
    const n = f.viewport.length + f.parent.length + f.overlap.length;
    if (n) hadIssue = true;
    report.push({ scene: `slide ${i + 1}`, ...f });
  }
} else {
  // page mode: measure full scroll height so the whole document is in view
  const fullH = await page.evaluate(() => document.documentElement.scrollHeight);
  await page.setViewportSize({ width: W, height: Math.max(H, fullH) });
  await page.waitForTimeout(60);
  const f = await detect(W, fullH, true);
  const n = f.viewport.length + f.parent.length + f.overlap.length;
  if (n) hadIssue = true;
  report.push({ scene: 'page', ...f });
}

await browser.close();

for (const r of report) {
  const n = r.viewport.length + r.parent.length + r.overlap.length;
  console.log(`${n ? '✗' : '✓'} ${r.scene}  ${n ? n + ' issue(s)' : 'ok'}`);
  for (const v of r.viewport) console.log(`    overflow-canvas ${v.axis} by ${v.by}px  ${v.el}`);
  for (const p of r.parent) console.log(`    overflow-parent  ${p.axis} by ${p.by}px  ${p.el}`);
  for (const o of r.overlap) console.log(`    TEXT-OVERLAP ${o.overlap}  ${o.a}  ✕  ${o.b}`);
}
const bad = report.filter((r) => r.viewport.length + r.parent.length + r.overlap.length).length;
console.log(`\n${report.length - bad}/${report.length} scene(s) clean, ${bad} with issues`);
console.log('---JSON---');
console.log(JSON.stringify(report));
process.exit(hadIssue ? 2 : 0);
