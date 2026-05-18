"""
fit_validator.py
================
Mandatory validator for analysis-protocol Phase 1 (Evidence gate).

Run after every lmfit (or equivalent) deconvolution. If `quant` or `visual`
fail lists are non-empty: HARD FAIL — do NOT emit figure/bar/narrative.
Self-iterate (loosen bounds, change peak count, change function, expand
fit window) up to 5 times, then escalate to user.

`sanity_flag` is SOFT — surface warning to user but do NOT auto-correct
the fit. It exists to catch cases where fit rank disagrees with expected
activity/stability rank, prompting human decision between:
  (a) fit is wrong → re-fit
  (b) fit is correct → narrative needs different descriptor

Categories
----------
1. Quant: parameter boundary, amplitude vestigiality, residual norm, χ²_red
2. Visual: raw↔envelope correlation, amplitude positivity
3. Sanity: rank mismatch flag (soft)

Generic across NH3-TPD / Py-DRIFTS / TPO / XPS / XRD deconv.

Usage
-----
    from fit_validator import validate_fit

    report = validate_fit(
        result=lmfit_result,
        raw_y=y_raw,
        envelope_y=result.eval(x=x_raw),
        peaks=[(p.name, p.value) for p in lmfit_result.params.values()
               if 'amplitude' in p.name],
        sample_values={"SampleA": 1.0e6, "SampleB": 1.5e6, "SampleC": 1.2e6, "Ref": 0.9e6},
        expected_rank={"SampleA": 1, "SampleB": 2, "SampleC": 3, "Ref": 4},
        descriptor_name="total acid site density",
    )
    if report['quant'] or report['visual']:
        # HARD FAIL: do NOT output. Self-iterate or escalate.
        print("FIT FAILED:", report)
    else:
        for w in report['sanity_flag']:
            print("WARN (human review needed):", w)
        # OK to output figure/bar/narrative
"""

from typing import Optional, Sequence, Tuple, Mapping, Any

import numpy as np


def validate_fit_quant(
    result: Any,
    raw_y: Sequence[float],
    envelope_y: Sequence[float],
    *,
    chi2_red_max: Optional[float] = None,
    residual_max_pct: float = 0.10,
    amplitude_min_frac: float = 0.05,
    boundary_tol: float = 1e-6,
) -> list:
    """
    Category 1 — quantitative fit checks.

    Parameters
    ----------
    result : lmfit MinimizerResult (must expose .params and .redchi)
    raw_y : raw signal values
    envelope_y : sum of fitted peaks evaluated at the same x
    chi2_red_max : optional upper bound on reduced χ². If None, skip χ² check.
    residual_max_pct : max allowed |raw - envelope| / max(|raw|)
    amplitude_min_frac : amplitude params below this fraction of the
                         largest amplitude are flagged as vestigial
    boundary_tol : numerical tolerance for "parameter at bound"

    Returns
    -------
    list[str] of failure messages (empty list = pass)
    """
    fails = []

    # 1.1 boundary 도달
    if hasattr(result, "params"):
        for p in result.params.values():
            if not getattr(p, "vary", True):
                continue
            if p.min is not None and abs(p.value - p.min) < boundary_tol:
                fails.append(
                    f"[bound] {p.name}={p.value:.4g} hit lower bound {p.min}"
                )
            if p.max is not None and abs(p.value - p.max) < boundary_tol:
                fails.append(
                    f"[bound] {p.name}={p.value:.4g} hit upper bound {p.max}"
                )

    # 1.2 amplitude vestigial (over-parameterization)
    amps = {}
    if hasattr(result, "params"):
        for p in result.params.values():
            name_l = p.name.lower()
            if "amplitude" in name_l or name_l.startswith("a_") or name_l.startswith("amp"):
                amps[p.name] = p.value
    if amps:
        max_amp = max(amps.values())
        if max_amp > 0:
            for name, v in amps.items():
                if v < amplitude_min_frac * max_amp:
                    fails.append(
                        f"[over-param] {name}={v:.3g} < "
                        f"{amplitude_min_frac*100:.0f}% of max ({max_amp:.3g})"
                    )

    # 1.3 residual / max(raw)
    raw_y = np.asarray(raw_y, dtype=float)
    envelope_y = np.asarray(envelope_y, dtype=float)
    if raw_y.shape != envelope_y.shape:
        fails.append(
            f"[shape] raw_y {raw_y.shape} vs envelope_y {envelope_y.shape}"
        )
    else:
        resid = raw_y - envelope_y
        raw_max = float(np.abs(raw_y).max())
        resid_max = float(np.abs(resid).max())
        if raw_max > 0 and resid_max / raw_max > residual_max_pct:
            fails.append(
                f"[residual] max|resid|/max|raw| = {resid_max/raw_max:.3f} "
                f"> {residual_max_pct}"
            )

    # 1.4 χ²_red
    redchi = getattr(result, "redchi", None)
    if chi2_red_max is not None and redchi is not None:
        if redchi > chi2_red_max:
            fails.append(
                f"[chi2] reduced χ² = {redchi:.3g} > {chi2_red_max}"
            )

    return fails


def validate_fit_visual(
    raw_y: Sequence[float],
    envelope_y: Sequence[float],
    peaks: Optional[Sequence[Tuple[str, float]]] = None,
    *,
    corr_min: float = 0.97,
    require_positive_amp: bool = True,
) -> list:
    """
    Category 2 — visual sanity checks.

    Parameters
    ----------
    raw_y, envelope_y : signal arrays
    peaks : iterable of (name, amplitude) for sign check
    corr_min : minimum Pearson r between raw and envelope
    require_positive_amp : amplitudes must be > 0

    Returns
    -------
    list[str] of failure messages
    """
    fails = []
    raw_y = np.asarray(raw_y, dtype=float)
    envelope_y = np.asarray(envelope_y, dtype=float)

    # 2.1 envelope ↔ raw correlation
    if raw_y.size > 1 and envelope_y.size == raw_y.size:
        if raw_y.std() > 0 and envelope_y.std() > 0:
            corr = float(np.corrcoef(raw_y, envelope_y)[0, 1])
            if not np.isfinite(corr) or corr < corr_min:
                fails.append(
                    f"[corr] envelope-raw corr = {corr:.3f} < {corr_min}"
                )
        else:
            fails.append("[corr] zero std in raw or envelope (degenerate fit)")

    # 2.2 amplitude positivity
    if require_positive_amp and peaks:
        for name, amp in peaks:
            if amp is None or amp <= 0:
                fails.append(f"[amp_sign] {name} amplitude = {amp} (must be > 0)")

    return fails


def sanity_flag_rank(
    sample_values: Mapping[str, float],
    expected_rank: Optional[Mapping[str, int]] = None,
    descriptor_name: str = "metric",
) -> list:
    """
    Category 3 — sanity flag (SOFT warning, never auto-correct).

    Surfaces the case where computed rank disagrees with user-expected rank.
    Possible interpretations the human must decide:
      (a) fit error → re-fit
      (b) fit correct, descriptor isn't the driver → narrative pivot

    NEVER tune the fit to match `expected_rank`. That's data fabrication.

    Parameters
    ----------
    sample_values : {sample_label: metric_value}
    expected_rank : {sample_label: rank}  (1 = highest, N = lowest)
                    If None, this check is skipped.
    descriptor_name : human label for the metric, e.g. "total acid site density"

    Returns
    -------
    list[str] of warning messages (empty if matches or expected_rank None)
    """
    if not expected_rank:
        return []

    flags = []
    sorted_actual = sorted(sample_values.items(), key=lambda kv: -kv[1])
    actual_rank = {k: r for r, (k, _) in enumerate(sorted_actual, start=1)}

    mismatches = [
        k for k in sample_values
        if k in expected_rank and expected_rank[k] != actual_rank.get(k)
    ]

    if mismatches:
        actual_str = " > ".join(
            f"{k} ({v:.3g})" for k, v in sorted_actual
        )
        expected_str = " > ".join(
            sorted(expected_rank, key=lambda k: expected_rank[k])
        )
        flags.append(
            f"[rank-flag] {descriptor_name}: actual {actual_str}; "
            f"expected {expected_str}. "
            f"Mismatch on {mismatches}. "
            f"Possible: (a) fit error → re-fit, "
            f"(b) descriptor not the driver → narrative pivot. "
            f"DO NOT tune fit to match expectation. Human review required."
        )

    return flags


def validate_fit(
    result: Any = None,
    raw_y: Optional[Sequence[float]] = None,
    envelope_y: Optional[Sequence[float]] = None,
    *,
    peaks: Optional[Sequence[Tuple[str, float]]] = None,
    sample_values: Optional[Mapping[str, float]] = None,
    expected_rank: Optional[Mapping[str, int]] = None,
    descriptor_name: str = "metric",
    chi2_red_max: Optional[float] = None,
    residual_max_pct: float = 0.10,
    amplitude_min_frac: float = 0.05,
    corr_min: float = 0.97,
) -> dict:
    """
    Combined validator. Call after every deconvolution.

    Returns
    -------
    dict with keys:
        'quant'        : list[str] hard-fail messages
        'visual'       : list[str] hard-fail messages
        'sanity_flag'  : list[str] soft warnings
        'pass'         : bool — True iff quant + visual both empty

    Hard-fail (quant or visual non-empty): do NOT emit figure / bar / narrative.
    Self-iterate (≤5 retries with adjusted bounds, peak count, function shape,
    fit window) or escalate to user.

    Sanity flag: surface to user as warning. Do not auto-correct.
    """
    quant = (
        validate_fit_quant(
            result, raw_y, envelope_y,
            chi2_red_max=chi2_red_max,
            residual_max_pct=residual_max_pct,
            amplitude_min_frac=amplitude_min_frac,
        )
        if (result is not None and raw_y is not None and envelope_y is not None)
        else []
    )
    visual = (
        validate_fit_visual(
            raw_y, envelope_y, peaks=peaks, corr_min=corr_min,
        )
        if (raw_y is not None and envelope_y is not None)
        else []
    )
    sanity = (
        sanity_flag_rank(sample_values, expected_rank, descriptor_name)
        if sample_values is not None
        else []
    )
    return {
        "quant": quant,
        "visual": visual,
        "sanity_flag": sanity,
        "pass": (len(quant) == 0 and len(visual) == 0),
    }


def format_report(report: dict) -> str:
    """Pretty-print a validator report for console / log."""
    lines = []
    status = "PASS" if report["pass"] else "FAIL"
    lines.append(f"[validate_fit] {status}")
    for cat in ("quant", "visual", "sanity_flag"):
        items = report.get(cat, [])
        if items:
            lines.append(f"  {cat}:")
            for m in items:
                lines.append(f"    - {m}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Smoke test — synthetic Gaussian
    try:
        import lmfit
    except ImportError:
        print("lmfit not installed, skipping smoke test")
    else:
        rng = np.random.default_rng(0)
        x = np.linspace(0, 10, 200)
        y_clean = 1.0 * np.exp(-((x - 5) ** 2) / (2 * 1.0 ** 2))
        y = y_clean + 0.02 * rng.standard_normal(200)

        m = lmfit.models.GaussianModel()
        p = m.make_params(amplitude=1.0, center=5.0, sigma=1.0)
        res = m.fit(y, p, x=x)
        env = res.eval(x=x)

        rep = validate_fit(
            result=res,
            raw_y=y,
            envelope_y=env,
            peaks=[("g_amplitude", res.params["amplitude"].value)],
            sample_values={"A": 1.0, "B": 0.7},
            expected_rank={"A": 1, "B": 2},
            descriptor_name="demo",
        )
        print(format_report(rep))
