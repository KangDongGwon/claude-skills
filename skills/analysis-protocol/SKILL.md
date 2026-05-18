---
name: analysis-protocol
description: Evidence gate for spectroscopic peak-fitting / deconvolution. Run fit_validator.py after every lmfit (or equivalent) deconvolution before emitting any figure, bar chart, or written claim. Hard-fails on bad fits (parameter at bound, vestigial amplitude, large residual, high reduced chi-square, raw-envelope mismatch); soft-flags rank disagreement for human review. Generic across NH3-TPD, Py-DRIFTS, TPO, XPS, XRD deconvolution.
allowed-tools: Read, Bash, Write
---

# analysis-protocol — fit validation gate

This is the shareable, self-contained core of a larger experimental-data
analysis protocol: a **mandatory validator** that decides whether a
peak-fitting result is trustworthy enough to be turned into a figure or a
written claim.

> The full protocol also wires a private methodology library (per-technique
> YAML parameter databases, figure standards, project configs) that is **not
> included here** — it is workflow-specific. `fit_validator.py` is the
> reusable engine and works standalone.

## When to use

After **every** `lmfit` (or equivalent) deconvolution — XPS, NH3-TPD,
Py-DRIFTS, TPO, XRD, etc. — and before you draw the figure or write the
sentence that depends on it.

## How it works

`fit_validator.py` runs three check categories:

1. **Quant (hard)** — parameter pinned at its boundary, vestigial peak
   amplitude, residual norm over threshold, reduced chi-square over
   threshold.
2. **Visual (hard)** — raw signal vs. fitted envelope correlation, peak
   amplitude positivity.
3. **Sanity (soft)** — fitted-quantity rank vs. an expected
   activity/stability rank. Surfaced as a warning, never auto-corrected:
   it forces a human decision between "the fit is wrong" and "the fit is
   right but the narrative needs a different descriptor".

If `quant` or `visual` fail lists are non-empty: **HARD FAIL** — do not
emit anything. Loosen bounds / change peak count / change peak function /
expand the fit window, retry up to ~5 times, then escalate.

## Usage

```python
from fit_validator import validate_fit

report = validate_fit(
    result=lmfit_result,
    raw_y=y_raw,
    envelope_y=lmfit_result.eval(x=x_raw),
    peaks=[(p.name, p.value) for p in lmfit_result.params.values()
           if 'amplitude' in p.name],
    sample_values={"SampleA": 1.0e6, "SampleB": 1.5e6},   # optional
    expected_rank={"SampleA": 1, "SampleB": 2},            # optional
    descriptor_name="total acid site density",             # optional
)
if report['quant'] or report['visual']:
    ...  # HARD FAIL: do not output; self-iterate or escalate
else:
    for w in report['sanity_flag']:
        ...  # WARN: human review
    ...  # OK to output figure / bar / narrative
```

The `sample_values` / `expected_rank` / `descriptor_name` arguments are
optional — omit them to run only the hard quant + visual gates.

## Dependencies

`numpy`, and an `lmfit` (or compatible) result object exposing `.params`
and `.redchi`.
