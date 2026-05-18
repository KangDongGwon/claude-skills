# Catalyst Characterization — Analysis Methodology (generic)

A vendor-neutral, project-agnostic methodology reference for the
characterization techniques common in heterogeneous catalysis. It pairs
with `fit_validator.py` (the evidence gate): this file says *how* to run
each analysis; the script enforces that any peak fit is trustworthy before
it becomes a figure or a claim.

> Generic best practice only. No instrument-, dataset-, or system-specific
> tuning. Treat the numbers below as textbook defaults, not recommendations
> for a particular sample.

Each technique follows the same template: **Purpose → Workflow →
Common pitfalls → Cross-checks**.

---

## XPS — X-ray Photoelectron Spectroscopy

**Purpose.** Surface (top ~5–10 nm) elemental composition, oxidation
states, and chemical environment.

**Workflow.**
1. Charge-reference: adventitious C 1s at 284.8 eV (insulators), or the
   Fermi edge for conductors. State the choice.
2. Survey scan → identify all elements; high-resolution scans on regions
   of interest.
3. Background: Shirley for most core levels, linear for flat backgrounds,
   Tougaard when quantitative accuracy matters.
4. Peak fit with Voigt / pseudo-Voigt. Constrain spin–orbit doublets:
   area ratio 2:1 for p (2p₃/₂:2p₁/₂), 3:2 for d, 4:3 for f; tie
   FWHM and splitting to physical values.
5. Quantify with sensitivity factors; report atomic %.

**Common pitfalls.** Differential charging; overfitting (more components
than the data supports); ignoring spin–orbit constraints; X-ray-induced
reduction of labile cations; variable adventitious carbon.

**Cross-checks.** Component binding energies vs reference compounds;
FWHM physically reasonable; structured fit residual = wrong model;
compare with a bulk probe (XRD / EXAFS).

---

## XRD — Powder X-ray Diffraction

**Purpose.** Crystalline phase identification, crystallite size, lattice
parameters, microstrain.

**Workflow.**
1. Background subtraction; phase ID against reference patterns
   (ICDD / COD).
2. Peak fit (pseudo-Voigt).
3. Crystallite size by Scherrer: `D = Kλ / (β cosθ)`, K ≈ 0.9, β =
   FWHM in radians **after** subtracting instrumental broadening.
4. Lattice parameters from calibrated peak positions; Rietveld for
   quantitative phase / structure refinement when needed.

**Common pitfalls.** Instrumental broadening not removed; Scherrer used
beyond ~100 nm; preferred orientation; amorphous fraction ignored;
unresolved peak overlap.

**Cross-checks.** Crystallite size vs TEM; multiple reflections agree on
the lattice parameter; phase fractions sum to 100 %; bond lengths
consistent with EXAFS.

---

## H₂-TPR — Temperature-Programmed Reduction

**Purpose.** Reducibility, reduction temperatures, metal–support
interaction, quantity of reducible species.

**Workflow.**
1. Pretreat (oxidative clean) under controlled conditions.
2. Subtract a blank/empty-cell baseline.
3. Calibrate the detector (e.g. a known reducible standard) for H₂
   consumption.
4. Assign peaks by temperature; deconvolute overlapping features.
5. H₂ uptake → reducible fraction / stoichiometry.

**Common pitfalls.** Ramp rate and sample mass shift Tmax (always report
them); condensables not trapped; baseline drift; spillover
misread as a separate species; uncalibrated detector.

**Cross-checks.** H₂ consumed vs theoretical stoichiometry; Tmax trend
consistent with particle size / interaction strength; reproducibility.

---

## NH₃-TPD — Temperature-Programmed Desorption of Ammonia

**Purpose.** Acid-site density and acid-strength distribution.

**Workflow.**
1. Saturate with NH₃; purge physisorbed NH₃ to a stable baseline.
2. Ramp; record desorption.
3. Deconvolute into weak / medium / strong regions by desorption
   temperature (define the cuts explicitly and keep them fixed).
4. Quantify with a calibrated detector → sites per mass or area.

**Common pitfalls.** Physisorbed NH₃ not removed; readsorption (carrier
flow too low / bed too deep); NH₃ decomposition on metal sites;
arbitrary temperature windows; no calibration.

**Cross-checks.** Total NH₃ vs surface area; pyridine-IR for
Brønsted/Lewis split; reproducibility.

---

## BET — N₂ Physisorption (surface area & porosity)

**Purpose.** Specific surface area, pore volume, pore-size distribution.

**Workflow.**
1. Degas adequately (time/temperature without altering the solid).
2. Measure the full isotherm.
3. Apply the BET equation only over a valid relative-pressure window
   (commonly 0.05–0.30) with the Rouquerol consistency criteria; the
   BET C constant must be positive.
4. Pore analysis: BJH (mesopores, correct branch), t-plot (micropores),
   or DFT for a refined distribution. Classify isotherm/hysteresis by
   IUPAC type.

**Common pitfalls.** BET range applied blindly to microporous solids;
insufficient degassing; wrong isotherm branch for BJH; hysteresis type
ignored.

**Cross-checks.** C constant positive and reasonable; total pore volume
vs single-point value; isotherm type consistent with the pore model.

---

## CO Chemisorption (metal dispersion)

**Purpose.** Active-metal surface area, dispersion, mean particle size.

**Workflow.**
1. Reduce/clean under controlled conditions.
2. Pulse or volumetric uptake at the appropriate temperature;
   double-isotherm method to isolate irreversible uptake.
3. Apply an explicit CO : metal stoichiometry (state the assumption).
4. Dispersion → particle size.

**Common pitfalls.** Assumed (not measured) stoichiometry; support
adsorption / spillover; incomplete reduction; carbonyl formation.

**Cross-checks.** Particle size vs TEM / XRD; dispersion ≤ 100 %;
consistency with H₂ chemisorption if available.

---

## CO-DRIFTS — CO-probe in situ DRIFTS

**Purpose.** Surface-site identification (linear / bridged CO, cation
sites), electronic state, in situ evolution.

**Workflow.**
1. Collect a clean background; dose CO; work with difference spectra.
2. Assign bands: linear M–CO ~2000–2100, bridged ~1800–1950,
   cation carbonyls shifted higher (cm⁻¹).
3. Kubelka–Munk transform; run temperature / pressure series;
   deconvolute overlapping bands.

**Common pitfalls.** Gas-phase CO rotational lines not subtracted;
dilution / particle size affecting DRIFTS quantitation; assignment
without a reference; reduction state uncontrolled.

**Cross-checks.** Band shifts consistent with the XPS oxidation state;
reproducible dosing; isotopic labeling when assignment is ambiguous.

---

## GC — Catalytic Activity Quantification

**Purpose.** Conversion, selectivity, yield, and rate / TOF from product
analysis.

**Workflow.**
1. Calibrate response factors with an internal or external standard.
2. Sample at steady state; verify a carbon / mass balance.
3. Conversion `X = (C_in − C_out)/C_in`; selectivity per product.
4. Normalize to catalyst mass or active-site count → rate, TOF.
5. Exclude transport limitations (Weisz–Prater, Mears criteria).

**Common pitfalls.** No carbon balance; sampling before steady state;
blank / homogeneous activity ignored; transport limitations not
excluded; TOF on an uncharacterized site count.

**Cross-checks.** Carbon balance ≈ 100 ± 5 %; empty-reactor blank;
reproducibility; vary contact time.

---

## Raman Spectroscopy

**Purpose.** Phase / polymorph ID, defects (e.g. oxygen vacancies),
supported-oxide structure, carbon D/G analysis.

**Workflow.**
1. Check laser power — avoid local heating / photoreduction (report it).
2. Baseline-correct (suppress fluorescence); normalize.
3. Assign bands; analyze defect/host band ratios on normalized spectra;
   run in situ / operando series if relevant.

**Common pitfalls.** Laser-induced damage or phase change; fluorescence
background; power not reported; intensity ratios over-interpreted
without normalization.

**Cross-checks.** Phase consistent with XRD; stable at lower power;
defect picture consistent with XPS.

---

## TEM / STEM

**Purpose.** Particle-size distribution, morphology, lattice fringes /
d-spacing, elemental mapping (EDS/EELS), atomic-scale (HAADF) imaging.

**Workflow.**
1. Sample many representative regions; count ≥150–200 particles for a
   size distribution.
2. Use calibrated magnification; report distribution statistics.
3. FFT / d-spacing for phase; EDS line/map for composition or structure;
   control beam dose on sensitive materials.

**Common pitfalls.** Non-representative sampling; beam damage; 2-D
projection bias; EDS quantified without standards; counting bias.

**Cross-checks.** Mean size vs XRD / chemisorption; d-spacing vs XRD;
composition vs XPS / bulk analysis.

---

## TGA — Thermogravimetric Analysis

**Purpose.** Mass-loss events (moisture, decomposition, combustion),
thermal stability, coke or loading quantification.

**Workflow.**
1. Apply a blank / buoyancy baseline correction.
2. Choose the atmosphere deliberately (inert vs oxidative); set the ramp.
3. Resolve steps with the DTG curve; confirm assignments with coupled
   MS / FTIR when available.
4. Quantify (coke, hydration, residual = loading).

**Common pitfalls.** Buoyancy not corrected; overlapping events;
atmosphere / ramp not reported; condensation; sample mass so large that
gradients form.

**Cross-checks.** DTG peak vs known decomposition temperature;
evolved-gas MS confirms the assignment; reproducibility.

---

## XAS — XANES / EXAFS

**Purpose.** Oxidation state and local coordination: element-specific,
bulk-averaged. XANES → oxidation state / site symmetry; EXAFS → bond
distances, coordination numbers, disorder.

**Workflow.**
1. Calibrate energy with a reference foil measured simultaneously.
2. Normalize (pre-edge / post-edge).
3. XANES: edge position and white-line vs standards; linear-combination
   fitting for mixtures with complete, correct standards.
4. EXAFS: background removal, k-weighting, Fourier transform, fit
   theoretical paths constraining S₀², coordination number, R, σ².
   Report k- and R-ranges and fit quality; keep free parameters below
   the number of independent points (Nyquist).

**Common pitfalls.** Self-absorption in thick fluorescence samples; poor
high-k signal-to-noise; overfitting; LCF with wrong / incomplete
standards; multiple scattering ignored.

**Cross-checks.** Coordination / R vs XRD / TEM; oxidation state vs XPS;
free parameters < independent points; reasonable EXAFS R-factor.

---

## Using this with `fit_validator.py`

For any technique that ends in a peak fit (XPS, XRD, H₂-TPR, NH₃-TPD,
CO-DRIFTS, Raman, EXAFS), run the result through `fit_validator.py`
before drawing the figure or writing the sentence. If the quant/visual
gate fails: loosen bounds, change the peak count or function, or widen
the fit window — then re-validate. A bad fit must never reach a figure.
