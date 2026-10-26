"""
rerun_analysis.py  --  CBO-GAP round 2: the fixed-beta rerun, analysis

WHAT THIS DOES, IN PLAIN LANGUAGE
---------------------------------
It reads the plan written by rerun.py --precheck and the trajectory run
folders written by rerun.py, and computes every slope, interval, verdict,
contrast, regression coefficient, onset, heterogeneity statistic and
audit summary that notes/ANALYSIS_CRITERIA.md specifies (decided by Rahul
in twelve messages of 2026-10-16, and for the three calibrated r rows in
the fourteenth message of 2026-10-26, CAL1 to CAL5 below). It evolves no
trajectory. It writes CSV files into a new run folder and prints
everything.

The criteria below are copied from notes/ANALYSIS_CRITERIA.md before the
first execution of this script; item numbers refer to that file.
Definitions shared with rerun.py (cells, keys, onset estimator) are in
scripts/rerunlib.py.

WHAT IS IMPORTED (CLAUDE.md rule 4)
  regimemap.fit_slope (every slope), regime.fit_curv (curvature),
  regime.fit_predict (P6.3), mechanism.r2_of (P3.4), all from the
  archive. The onset estimator is rerunlib.onset_bp, retyped because it is
  nested in regimemap.py's main; rerun.py's O1 must have passed (the plan
  records it) before it is used here.

INPUTS AND CHECKS BEFORE ANY STATISTIC
  A0  The plan folder and every run folder are read only after their
      sha256.txt verifies. The plan must record PASS for V0, P1, S1, O1,
      A-BETA/A-SIGMA, C2, K1, K2 and K4 (rerun.load_plan). Every complete
      realization (end "ok") must match its plan cell: task id, beta
      (repr), sigma (repr) and bootstrap key equal; a realization not in
      the plan, or a task id complete in two folders, exits 2.
      The seed_key column must equal the key part of the task id, so the two
      arms of a paired cell provably hold the same key (5a; checklist "a
      check in the script stops the run if not").
      Worked example: a SIGMA realization whose beta reads 2.5e2 while the
      plan says 2.4e2: exit 2, naming the task. An anisotropic row whose
      seed_key differs from its task id's key: exit 2.
  A1  ALL TWENTY ROWS COMPLETE (Rahul, D3, 2026-10-16; extended to the
      twenty rows by CAL4, 2026-10-26). A row is
      complete when every realization of every one of its cells (shared
      cells included) is present and complete, and no cell's beta is
      pending. If any row is not complete, the script prints every row's
      count, "INCOMPLETE: analysis refused (D3)", creates no output folder,
      computes no statistic and exits 7. Rahul's reason: analysing the
      thirteen archived-beta rows first would produce a partial set of
      numbers before the calibrated rows exist, and partial numbers invite
      a conclusion drawn before the evidence is in. One stop, no partial
      analysis. The same holds for the calibrated r rows: nothing about
      RMAP-CAL is printed while ONSET-CAL is incomplete.
      Worked example: ONSET with 2148 of 2160 realizations present, or
      CONC with its beta pending, or ONSET-CAL with 2159 of 2160: exit 7,
      nothing computed.

ITEM 0  ESTIMAND. Each realization's slope is regimemap.fit_slope on the
  window. S-slope = the mean of the realization slopes (primary; every
  verdict). S-curve = fit_slope of the mean curve over the same
  realizations (secondary column, read by no verdict).
  Worked example: slopes -1.02, -0.98, -1.00 give S-slope -1.000; if their
  mean curve fits -1.015, that is printed as S-curve only.

ITEM 1  INTERVALS AND VERDICTS.
  - Two-sided 95%: percentiles 2.5 and 97.5 of the B finite resamples.
  - One-sided 95% upper bound: the 95th percentile, labelled "one-sided
    95%".
  - DIFFERENCE iff the 2.5th percentile > 0 or the 97.5th < 0; otherwise
    "95% interval contains 0", never "no difference".
  - EQUIVALENT (diffusion gaps only, margin m of 5b) iff the 5th
    percentile > -m and the 95th < +m, printed as "90% (TOST 5% each
    side)". A gap can be DIFFERENCE and EQUIVALENT: both are printed, with
    "distinguishable from zero and smaller than the margin".
  - No multiplicity adjustment; every cell and verdict is written.
  Worked example: percentiles 2.5, 5, 95, 97.5 of +0.021, +0.026, +0.079,
  +0.083: interval [+0.021, +0.083], DIFFERENCE; one-sided upper bound
  +0.079. A gap with 5th and 95th -0.031 and +0.027 at m 0.040:
  EQUIVALENT.

ITEM 2  WINDOWS.
  - W-full, primary: every J of the cell's grid (J10, J10b or J19, capped
    at J_inf / 10), except REFSIZE, whose primary is J <= 1250 for every
    J_inf (regime.py's common cap), with the capped full grid printed as
    its sensitivity line "W-grid".
  - W-ge, sensitivity: grid J with J x tau_0 >= 1 in exact fractions of
    the tau_0 string; printed only where it drops a point (tau_0 < 0.1).
    No verdict on W-ge or W-grid.
  - Before each fit every E on the window must be finite and > 0; a
    realization that fails has no slope on that window and is handled by
    item 3's realization rule, with its bad-point count.
  Worked example: tau_0 0.01, J10: W-ge = [160, 320, 640, 1280, 2560,
  5000]. tau_0 0.07: 1/tau_0 = 100/7, so J = 20 is kept and J = 10 dropped.

ITEM 3  BOOTSTRAP.
  - B = 10000. Indices for a cell come from
    default_rng(SeedSequence(boot_key)).integers(0, n, size=(B, n)), with
    boot_key the cell's key with kind 71 and no rep (rerunlib.boot_key),
    n the number of realizations kept on that window. The two arms of a
    paired cell share the key and therefore the index matrix, applied to
    the same kept reps (joint resampling by key). A shared cell has one key,
    so every row that reads it sees the same resamples.
  - A multi-cell statistic is recomputed from per-cell resamples drawn
    independently in each cell.
  - A realization with a non-finite slope (or a bad point) is dropped
    before resampling, named with its key, and "M n of M" is printed; more
    than one dropped in a cell flags the cell. In a paired cell its key is
    dropped from both arms ("dropped from both arms").
  - A non-finite resample is excluded and counted per statistic; above 1%
    of B, a FLAG line names it.
  Worked example: M = 12, rep 7's slope non-finite: "M 11 of 12", every
  resample draws 11 indices from the remaining 11, no flag; reps 7 and 9:
  "M 10 of 12", flagged. 37 of 10000 non-finite resamples: printed, no
  flag; 140: FLAG.

ITEM 4  RATE VERDICT, every row, W-full only: "upper bound <= -1: yes" iff
  the one-sided 95% upper bound (95th percentile) of the cell's resampled
  S-slope is at most -1; nothing added to -1. No monotonicity claim, no
  tolerance count, no N_vis, no -0.85, no compound ADAPT verdict, no
  straightness verdict, no SATURATED label.
  Worked example: 95th and 97.5th percentiles -0.93 and -0.90: "upper bound
  <= -1: no".

ITEM 5a  PAIRING. SIGMA, ANISO, RMAP, CLIFF and ONSET: the gap is
  anisotropic minus isotropic, resampled jointly by key (item 3).
  Worked example: ANISO, rastrigin, d 10, r 0.5, tau0 0.1: both arms' rows
  carry the same key for each rep; one index matrix is drawn from the
  cell's bootstrap key and applied to both arms' slopes, so resample b's
  gap is the mean over the drawn reps of (aniso - iso).

ITEM 5b  MARGIN, computed and printed before any gap.
  - S = the median of the per-cell bootstrap SDs (numpy.nanstd, ddof 1, of
    the B resampled S-slopes, W-full; M4's se_boot_slope) over every cell
    arm of the five paired rows; a cell shared by RMAP and ONSET counts
    once. m = 3 x S.
  - The median SD is printed for the calprec2 group (SIGMA, ANISO) and the
    probe group (RMAP, CLIFF, ONSET). REVISIT iff the larger group median
    over the smaller exceeds 1.5. On REVISIT the script prints both medians,
    the ratio and "MARGIN REVISIT REQUIRED", computes no gap, prints no
    DIFFERENCE or equivalence verdict for the paired rows, writes what it
    has and exits 6.
  - Attainability: in each per-cell gap, equivalence is attainable iff the
    90% half-width (p95 - p5) / 2 is below m. Otherwise "equivalence not
    attainable at this margin" and no equivalence verdict.
  - PER CELL ONLY (Rahul, D2, 2026-10-16). The equivalence and
    attainability verdicts apply to the per-cell gap. The pooled diffusion
    gap gets its estimate, its 95% interval, the DIFFERENCE rule and item
    6's heterogeneity, and no equivalence or attainability verdict.
    Rahul's reason: the margin is derived from per-cell SDs, so applying
    it to a pooled quantity compares a number against a scale built for a
    different unit. His H2 wording ("reported the same way") was
    ambiguous; it meant reported alongside with its heterogeneity.
    Worked example: SIGMA d 10 r 0.5 tau0 0.1, four objectives: each
    objective's gap prints DIFFERENCE and the equivalence line; the pooled
    row prints its estimate, interval, DIFFERENCE verdict, k, sd_units and
    I2, and no equivalence line.
  Worked example (Rahul's): group medians 0.026 and 0.030, ratio 1.15, no
  revisit; 0.026 and 0.042, ratio 1.62, REVISIT. With S = 0.026, m =
  0.078; a gap with half-width 0.085 is not attainable; one with 5th and
  95th -0.031 and +0.027 is EQUIVALENT.

ITEM 6  HETEROGENEITY, printed with every pooled figure (units: (objective,
  law) in CONC and PROBEARM except for the law contrast, whose unit is the
  objective; the objective elsewhere).
  - Pooled estimate = the unweighted mean of the per-unit estimates y_i;
    pooled resamples = the mean of the per-unit resamples.
  - v_i = numpy.nanvar(unit resamples, ddof 1); s2 = var(y_i, ddof 1);
    sd_units = sqrt(s2); vbar = mean v_i; tau2_mm = max(0, s2 - vbar),
    printed "tau2 truncated at 0 (s2 ... < vbar ...)" when s2 <= vbar;
    y_w = sum(y_i / v_i) / sum(1 / v_i), used in Q only; Q = sum((y_i -
    y_w)^2 / v_i); I2 = max(0, (Q - (k - 1)) / Q).
  - I2 is printed "undefined" with the reason when Q = 0 or any v_i = 0.
  Worked example: y = -1.00, -0.95, -0.90, v_i = 0.0009 each: s2 0.0025,
  vbar 0.0009, tau2_mm 0.0016, Q 5.56, I2 0.64. Pooled estimate -0.95.

ITEM 7  CONTRASTS (second level minus first; baseline subtracted).
  1  dimension, concentration rows: S(d40) - S(d2); TAU8, GEOM: S(d40) -
     S(d5). Per (objective, law, tau_0), pooled per tau_0.
  2  target: S(0.01) - S(0.5) in CONC, PROBEARM, RMAP; S(0.01) - S(0.3)
     in TAU8, GEOM; S(0.01) - S(0.1) in SIGMA, ANISO (per arm).
  3  diffusion: anisotropic - isotropic per cell, paired; pooled over
     objectives within (row, d, r or sigma, tau_0).
  4  law, CONC and PROBEARM: S(mix-0.1) - S(centred) per (objective, d,
     tau_0); unit the objective.
  5  REFSIZE: S(J_inf 100000) - S(J_inf 12500) on J <= 1250; no W-grid
     line.
  6  ONSET: onset(d80) - onset(d5) per (diffusion, objective) and pooled
     (pooled onsets) per diffusion.
  7  interaction = CON(0.01, 0.5) (TAU8, GEOM: CON(0.01, 0.3)).
  Worked examples (illustrative numbers): S -1.06 at d2 and -1.01 at d40
  gives +0.05 (contrast 1); S -1.01 at tau0 0.5 and -0.85 at 0.01 gives
  +0.16 (2); aniso -0.93 and iso -1.01 give +0.08 (3); mix-0.1 -0.98 and
  centred -1.02 give +0.04 (4); J_inf 100000 -1.04 and 12500 -1.06 give
  +0.02 (5); onsets 1.00 at d80 and 1.50 at d5 give -0.50 (6); changes
  +0.15 at 0.01 and +0.05 at 0.5 give +0.10 (7), whose round-1 orientation
  CON(0.5, 0.01) is -0.10.
  A unit lacking a cell (a cell with no finite S-slope on the window) is
  excluded from that quantity, named, and the reduced k printed (section
  8, common rules). Example: CONC REGF with rastrigin/mix-0.1 lacking its
  d40, tau0 0.01 cell: "excluded units: rastrigin/mix-0.1", k 11.
  Every contrast is printed per unit and pooled, with the W-ge line where
  any cell involved has tau_0 < 0.1. No contrast in ADAPT, LAWPANEL,
  HORIZON, SYNTH, NAMED, BETA-ISO, BETA-ANI, CLIFF (beyond 3).

SECTION 8  (tenth to twelfth messages).
  8.1 CON(t1, t2) = change(t1) - change(t2), change(t) = S(d40, t) -
      S(d2 or d5, t): CON(0.1, 0.5), CON(0.01, 0.5), CON(0.01, 0.1) (TAU8,
      GEOM: 0.3 for 0.5). Round 1's CON(0.5, 0.01) is the negative of
      CON(0.01, 0.5); every CON row prints "round-1 orientation" as the
      negative. TMM = change(0.01) - (change(0.5) + change(0.1)) / 2 (TAU8,
      GEOM: 0.3 for 0.5). Nothing is labelled SEP.
      REGF: OLS of the cell S-slopes on [1, log2 d, log10(1/tau_0), log2 d
      x log10(1/tau_0)] per unit (CONC, PROBEARM: 4 d x 3 tau_0; TAU8,
      GEOM: 3 d x 8 tau_0); b_d, b_tau, b_dtau with intervals, both
      windows. The pooled coefficient is the mean of the unit coefficients
      (equal to OLS on pooled cell means).
      Worked example: gamma = -1.06 + 0.01 log2 d + 0.02 log10(1/tau_0) +
      0.005 log2 d log10(1/tau_0) gives b_d 0.01, b_tau 0.02, b_dtau 0.005.
      Worked example (TMM): changes 0.05, 0.06, 0.15 give TMM +0.095 and
      CON(0.01, 0.1) +0.09.
  8.2 Severity, ONSET: S(1, 3) = S(r 3) - S(r 1), sensitivity S(0.75, 3) =
      S(r 3) - S(r 0.75), per (diffusion, objective, d), pooled per
      (diffusion, d). Trend: OLS slope of the severity on log2 d (five d,
      intercept), per (diffusion, objective) and pooled per diffusion.
      Example: S(1, 3) = 0.09, 0.07, 0.21, 0.46, 0.61 at d 5 to 80: the
      trend is the OLS slope on log2 d = 2.32 .. 6.32, printed with its
      interval; no sentence says the severity grows.
  8.3 Panel model, RMAP: Delta = -1 - S fitted as a + b1 g + b2 h + b3 g h,
      g = log10(0.5 / tau_0), h = log2(r / 0.5), over the 20 cells of a
      (diffusion, d) panel per objective, pooled; b1, b2, b3, both
      windows. Example: Delta = 0.02 + 0.10 g + 0.05 h + 0.01 g h exactly
      gives b1 0.10, b2 0.05, b3 0.01.
  8.4 Onset against 1: each onset's 95% interval and "contains 1: yes/no"
      (lo <= 1 <= hi); counts "k of 30" per objective and "k of 10"
      pooled, and per diffusion. A description of where intervals fall,
      not a claim that the onset is at 1.
      Onset (H3): rerunlib.onset_bp on the S-slopes over r (per
      objective), or on their mean over the objectives (pooled: the onset
      of the mean curve, not the mean of the onsets); heterogeneity from
      the per-objective onsets. Example: intervals [1.00, 2.00], [1.25,
      2.00], [1.00, 1.00]: 2 of 3 contain 1.
  8.5 Finite-J audit (CONC, PROBEARM, TAU8, GEOM; realizations with F1
      ok; a row with any F1 FAILED is not audited and says so): per cell
      and J, mean, SD (ddof 1), 5th and 95th percentiles of ratio(J) =
      ESS_0(J)/J/tau_0 over realizations, the mean reference ratio, and
      the floor 1/(J tau_0) flagged where J tau_0 < 1. Difference
      ratio(J; d40) - ratio(J; d2 or d5) per (unit, tau_0, J) and pooled
      per (tau_0, J), resampled with each cell's index stream over all its
      realizations; DIFFERENCE rule; count "k of n pooled intervals
      exclude 0" per row. Round 1 printed d2 - d40, the negative. No
      PASS/FAIL. Example: tau_0 0.01, J 40: floor 2.5; means 2.6 and 3.4
      give +0.8 (round 1's orientation -0.8).
  L1  audit A2, SIGMA: OLS coefficient of the cell S-slopes on r (six r,
      intercept) per (diffusion, objective, d, tau_0), pooled per
      (diffusion, d, tau_0); W-ge line at tau_0 0.01. Not computed: cliff
      (i), (ii), regimemap "map informative", partm P-M3; P-M4 is
      identically zero under sharing and is printed as vacuous.
      Example: S-slopes -1.02, -1.01, -1.00, -0.99, -0.98, -0.97 at r 0.1,
      0.25, 0.5, 0.75, 0.9, 0.99 give the OLS coefficient of slope on r, with
      its interval and the DIFFERENCE rule (Rahul, D1, 2026-10-16: like
      every other regression coefficient of section 8; treating it
      differently would mean two standards for one kind of quantity).
  L2  R^2, point values only, the fit named: mechanism P3.4 in CONC and
      PROBEARM (OLS of cell S-slopes on log tau_0; plus log d; plus
      objective dummies; mechanism.r2_of); regime P6.3 (regime.fit_predict,
      train SYNTH, test NAMED, models M1, M2, M3 of regime.py lines 451 to
      453, response the cell S-slope, features the cell means of
      regime.one_realisation's values). ess_surface P1.3: the minimum ESS
      (mean over realizations of ess_min_ref and of ess_min_sub per J)
      printed beside each BETA-ISO and BETA-ANI slope.
      Example: "P3.4 target alone (log tau0)  R^2 = 0.2000  (OLS of the 144
      cell S-slopes, W-full)": a number and the fit, with no interval and no
      verdict.
  L3  Curvature, regime rows: the mean over realizations of
      regime.fit_curv on the window, with its interval, no verdict.
      Departure from the archive (regime.py line 362 fitted the mean
      curve), stated in the output.
      Example: per-realization curvatures 0.004, 0.006, 0.002 give 0.004,
      printed with its interval and no straightness verdict.
  Reference adequacy: calprec2's label, tau_ref, adequacy, C5m, D1 and
  both reference medians per calibration cell, from the plan, with no
  pooled verdict; REFSIZE's cells and contrast 5.
  Example: "crossed ackley d=40 centred tau0=0.01 beta (not adequate) C5m
  0.0712 D1 0.031 64M ... 256M ...": copied as calprec2 wrote it; no count
  of adequate cells is turned into a verdict.
  No round-1 interval is reused or compared: the approved key shares no
  realization across d, tau_0 or r.

THE CALIBRATED r ROWS (fourteenth message, 2026-10-26; notes/
ANALYSIS_CRITERIA.md CAL1 to CAL5; ledger N41, N42). RMAP-CAL, CLIFF-CAL
and ONSET-CAL are the cells of RMAP, CLIFF and ONSET run on the N41
calprec2 betas. Everything above applies to them unchanged, except:
  CAL1  MARGIN. m is the seventeen-row m, 3 x S with S the median over
      the cell arms of SIGMA, ANISO, RMAP, CLIFF and ONSET only (MARGIN_ROWS;
      rerunlib.PAIRED now also lists the three new rows and is NOT used
      for S). It is not recomputed with the new rows. This is an exception
      to A8 as worded: the calibrated rows borrow a margin fixed before
      their gaps existed, and the manuscript says so.
      RATIO GUARD. Before any gap of a calibrated row, the script prints
      the median per-cell SD (W-full) over the cell arms of RMAP-CAL,
      CLIFF-CAL and ONSET-CAL, a shared cell once, and its ratio, larger
      over smaller, to the calprec2-group median and to the probe-group
      median. REVISIT iff either ratio > 1.5, or either ratio is not
      finite (a NaN median fails safe). On REVISIT it prints
      "MARGIN REVISIT REQUIRED (calibrated r rows)", computes no phase-3
      statistic for those rows (no gap, contrast, coefficient, onset or
      verdict), writes its files and exits 6.
      Worked example (illustrative): medians 0.026582 (calprec2) and
      0.025384 (probe); calibrated r 0.030: ratios 1.13 and 1.18, no
      revisit. 0.040: ratios 1.50 and 1.58, REVISIT.
  CAL2  CONTRASTS: mirror. RMAP-CAL: contrast 3 per cell, contrast 2
      (0.01 - 0.5 per arm), J3 panel b1, b2, b3. CLIFF-CAL: contrast 3.
      ONSET-CAL: contrast 3, onsets and J4, contrast 6, J2 severity and
      trend. Same signs, windows, DIFFERENCE rule, equivalence rule and
      item 6. Nothing is computed between a probe row and its calibrated
      row: the owner row is in the seed key, so they are independent
      replications (N40). Partm P-M4 for RMAP-CAL against ONSET-CAL is
      vacuous for the same reason as for RMAP against ONSET.
  CAL3  NOT-ADEQUATE FLAG, every row (the seventeen included). A cell is
      not adequate when its plan column cal_adequacy starts with "not
      adequate" (calprec2's adequacy, copied by the precheck). Every
      statistic is computed from all its cells, as before; none is
      excluded or recomputed. Each statistic (analysis_stats.csv), per-cell
      row (_cells), audit summary row (_audit), R^2 row (_r2) and onset
      row (_onsets) carries a column not_adequate naming, as module|
      objective|d|law|tau0, every not-adequate calibration cell among the
      cells it uses ("" when none). A pooled figure names the union over
      its units. analysis_margin_calibrated.csv holds
      not_adequate_in_margin_pool and not_adequate_in_calibrated_r_pool,
      with the ratio guard's values; it is written after the CAL4 check. The column and rows were added after
      the seventeen-row results were seen; they change no value.
      Worked example: RMAP-CAL, isotropic, ackley, d 10, contrast 2 at r
      1.0 uses the cells at tau0 0.01 and 0.5; the first is regimemap|
      ackley|10|centred|0.01, "not adequate (C5m FAIL, D1 FAIL)", so the
      row's not_adequate reads "regimemap|ackley|10|centred|0.01". The
      pooled contrast at d 10, r 1.0 names it too, with any other unit's.
  CAL4  ONE ANALYSIS, AND THE SEVENTEEN-ROW REPRODUCTION CHECK.
      --reproduce DIR names the seventeen-row result folder. It must be
      runs/rerun-analysis-20261025-051314, whose sha256.txt hashes to
      REPRO_MANIFEST_SHA256 (pinned, 01c202c8...29d5e1), and every file
      must verify against that sha256.txt; otherwise exit 2. Worked
      example: --reproduce runs/rerun-analysis-20261025-061500 (another
      folder): exit 2 before anything is read. The script runs in this order:
      (a) A0, A1 over all twenty rows (exit 7 as above);
      (b) phase 1, the margin and phase 3 for the seventeen rows only;
      (c) the check: for each of analysis_completeness, _cells, _margin,
          _stats, _onsets, _audit, _r2 and _adequacy (.csv), the
          seventeen-row rows the run produced, in order, must equal the
          old file's rows: same number of rows, and every value of every
          old column equal as a string. The one column added by this
          version, not_adequate, is not compared; analysis_margin.csv and
          analysis_onsets.csv keep the seventeen rows' content only (the
          calibrated rows' guard and onsets go to their own files).
          The seventeen-row rows are: in _completeness, _cells and
          _stats, the rows whose row is one of the seventeen; in
          _onsets, the rows of ONSET; in _adequacy, the calibration
          cells of CONC, TAU8, SIGMA and ANISO; _margin, _audit and _r2
          in full. analysis_params.csv is not compared (its hashes, plan
          and folder list differ by design).
          On any mismatch it prints "17-ROW REPRODUCTION FAILED" and the
          first twenty differences, writes the seventeen-row files and
          analysis_reproduction.csv, computes nothing for the calibrated
          rows and exits 8. A mismatch is a finding, not something to
          patch. The margin is checked first, as soon as it is computed
          and before any gap: S, the two group medians, m, the ratio, the
          verdict and the cell-arm count must equal analysis_margin.csv
          of DIR (0.026038, 0.026582, 0.025384, 0.078113 as printed in
          N39, at full precision); a mismatch there exits 8 at once.
      (d) only after PASS: phase 1 for the calibrated rows, the ratio
          guard, phase 3 for them, the adequacy report.
      Where it runs: the laptop, Python 3.12.3, NumPy 2.5.3, the
      environment that produced the seventeen-row result. The equality is
      exact, so any other environment is expected to fail it (rule 7).
      Worked example: m prints 0.078113 and every seventeen-row value
      matches: "17-ROW REPRODUCTION PASS", the calibrated rows proceed.
      One SIGMA c3 lo95 reading -0.04121 where the old file has -0.04122:
      FAILED at analysis_stats.csv, that row and column; exit 8; no
      calibrated-row number exists.
  CAL5  TARGET COUNTS SPLIT BY PROVENANCE, every calibrated row. For each
      row of rerunlib.CALROWS, its distinct calibration cells are counted
      by category = label + " | " + provenance, where a provenance
      beginning "beta_prod" is shortened to "beta_prod" (its N_cell
      varies). Printed and written to analysis_adequacy_split.csv. No
      statistic is flagged for it and no value changes. A calibration cell
      shared by RMAP-CAL and ONSET-CAL is counted in both rows.
      Worked example: a row with cells "target" / "beta_prod, calibration
      N_cell 4000000", "target" / "beta_prod, calibration N_cell 64000"
      and "target" / "beta_adq; C1 found no sufficient level" prints
      "target | beta_prod  2" and "target | beta_adq; C1 found no
      sufficient level  1".

GUARD. If rerunlib.ROWS differs from ANALYSIS_ROWS (the twenty rows in
  their order) the script prints both, computes nothing and exits 2.
  Worked example: a twenty-first row in rerunlib: "GUARD: ...", exit 2.

OUTPUT (new folder <outdir>/rerun-analysis-<stamp>/, every file "x")
  analysis_params.csv, analysis_completeness.csv, analysis_cells.csv,
  analysis_margin.csv, analysis_stats.csv (every contrast, coefficient,
  severity, onset contrast, audit difference, pooled figure with item 6),
  analysis_onsets.csv, analysis_audit.csv, analysis_r2.csv,
  analysis_adequacy.csv, analysis_adequacy_split.csv (CAL5),
  analysis_margin_calibrated.csv (CAL1 guard, CAL3 pool flags),
  analysis_onsets_calibrated.csv (ONSET-CAL's onsets and J4 counts),
  analysis_reproduction.csv (CAL4: per file, PASS or FAIL, rows compared,
  differences).

HOW TO RUN (from the repository root, venv active)
    python scripts/rerun_analysis.py --plan-from runs/rerun-plan-<stamp> \
        --reproduce runs/rerun-analysis-20261025-051314 \
        --runs runs/<run folder> --runs runs/<run folder> ... --workers 2
  Exit codes: 0 completed; 2 setup or A0; 6 MARGIN REVISIT REQUIRED
  (seventeen rows, or calibrated r rows); 7 INCOMPLETE, analysis refused
  (A1, D3); 8 17-ROW REPRODUCTION FAILED (CAL4). Each is final when it
  occurs: 2 and 7 stop before any statistic; 8 after the seventeen rows
  and before any calibrated-row statistic; 6 after the margin step that
  triggered it.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import io                                                       # noqa: E402
import json                                                     # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402
from fractions import Fraction                                  # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cbopaths                                                 # noqa: E402
import rerun                                                    # noqa: E402
import rerunlib as rl                                           # noqa: E402

cp = rl.cp
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = cbopaths.output_root(ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

B = 10000
K_TOL = 3.0
REVISIT_RATIO = 1.5
FLAG_FRAC = 0.01
REFSIZE_CAP = 1250
BASE_ROWS = ["BETA-ISO", "BETA-ANI", "LAWPANEL", "CONC", "PROBEARM", "ADAPT", "TAU8", "REFSIZE",
             "SYNTH", "NAMED", "HORIZON", "GEOM", "SIGMA", "ANISO", "RMAP", "CLIFF", "ONSET"]
CALR_ROWS = ["RMAP-CAL", "CLIFF-CAL", "ONSET-CAL"]
ANALYSIS_ROWS = BASE_ROWS + CALR_ROWS
MARGIN_ROWS = ["SIGMA", "ANISO", "RMAP", "CLIFF", "ONSET"]
CALGROUP = ["SIGMA", "ANISO"]
PROBEGROUP = ["RMAP", "CLIFF", "ONSET"]
EXIT_REPRO = 8
REPRO_DIR = "rerun-analysis-20261025-051314"
REPRO_MANIFEST_SHA256 = "01c202c8d2fae83c0fe683d1cc55a802dd59c2e27fdf1fab158578a5e029d5e1"
REPRO_FILES = ["analysis_completeness.csv", "analysis_cells.csv", "analysis_margin.csv", "analysis_stats.csv",
               "analysis_onsets.csv", "analysis_audit.csv", "analysis_r2.csv", "analysis_adequacy.csv"]
REPRO_SHOW = 20

fit_slope = cp.MODS["regimemap"].fit_slope
fit_curv = cp.MODS["regime"].fit_curv
fit_predict = cp.MODS["regime"].fit_predict
FEATNAMES = list(cp.MODS["regime"].FEATNAMES)
r2_of = cp.MODS["mechanism"].r2_of
P63_MODELS = [("M1  dimension + target", ["logd", "logtau"]),
              ("M2  + ESS trajectory", ["logd", "logtau", "le0", "lemin", "lemean", "leint",
                                        "ledecay"]),
              ("M3  + geometry", ["logd", "logtau", "le0", "lemin", "lemean", "leint", "ledecay",
                                  "covtr", "disp", "fvar", "dist0"])]

LOG = []


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "-" * 100)
    say(s)
    say("-" * 100)


def fmt(x, n=4):
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if not np.isfinite(x):
        return "nan"
    return "{:+.{}f}".format(x, n)


def write_csv(outdir, name, cols, rows):
    with open(os.path.join(outdir, name), "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols] if isinstance(r, dict) else r)
        fh.flush()
        os.fsync(fh.fileno())


def as_strings(cols, rows):
    """The rows exactly as write_csv would write them, read back as strings
    (header first). Used by the CAL4 comparison."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(c, "") for c in cols] if isinstance(r, dict) else r)
    buf.seek(0)
    return list(csv.reader(buf))


# --------------------------------------------------------------------------
# CAL3: not-adequate calibration cells
# --------------------------------------------------------------------------

def na_label(c):
    """module|objective|d|law|tau0 of c's calibration cell if calprec2 judged
    it not adequate, else None (also for rows without a calprec2 beta)."""
    pr = c["plan_row"]
    if c["row"] not in rl.CALROWS or not pr.get("cal_adequacy", "").startswith("not adequate"):
        return None
    return "|".join([c["module"], c["obj"], str(c["d"]), c["law"], pr["tau0"]])


def na_flag(cells):
    labs = sorted(set(x for x in (na_label(c) for c in cells) if x is not None))
    return "; ".join(labs)


# --------------------------------------------------------------------------
# windows and indices
# --------------------------------------------------------------------------

def tau_frac(c):
    s = c["plan_row"]["tau0"]
    return None if s == "" else Fraction(s)


def win_full(c):
    jl = rl.jlist_of(c)
    if c["row"] == "REFSIZE":
        return [J for J in jl if J <= REFSIZE_CAP]
    return jl


def win_ge(c):
    t = tau_frac(c)
    jl = win_full(c)
    if t is None:
        return jl
    return [J for J in jl if J * t >= 1]


def window(c, w):
    if w == "full":
        return win_full(c)
    if w == "ge":
        return win_ge(c)
    if w == "grid":
        return rl.jlist_of(c)
    raise ValueError(w)


def has_ge(c):
    return win_ge(c) != win_full(c)


def boot_idx(bkey, n):
    rng = np.random.default_rng(np.random.SeedSequence(list(bkey)))
    return rng.integers(0, n, size=(B, n))


def pct(v):
    f = v[np.isfinite(v)]
    nf = int(v.size - f.size)
    if f.size == 0:
        return dict(lo=float("nan"), p5=float("nan"), p95=float("nan"), hi=float("nan"), nf=nf)
    p = np.percentile(f, [2.5, 5, 95, 97.5])
    return dict(lo=float(p[0]), p5=float(p[1]), p95=float(p[2]), hi=float(p[3]), nf=nf)


def diff_verdict(q):
    if not (np.isfinite(q["lo"]) and np.isfinite(q["hi"])):
        return "no finite interval"
    return "DIFFERENCE" if (q["lo"] > 0 or q["hi"] < 0) else "95% interval contains 0"


# --------------------------------------------------------------------------
# phase 1 worker: one (cell group, window)
# --------------------------------------------------------------------------

def cw_task(a):
    """a: dict with bkey, Js, diffs, reps, E (diff -> {rep: {J: E}}), keys
    (rep -> key string), curv (bool). Returns per-diff stats and slopes."""
    Js = a["Js"]
    Jarr = np.array(Js, dtype=float)
    out = {"id": a["id"], "diffs": {}, "dropped": [], "M": len(a["reps"])}
    valid = {}
    per = {}
    for df in a["diffs"]:
        per[df] = {}
        for rep in a["reps"]:
            e = a["E"][df][rep]
            vals = [e.get(J, float("nan")) for J in Js]
            bad = sum(1 for v in vals if not (np.isfinite(v) and v > 0))
            if bad:
                per[df][rep] = (float("nan"), bad)
                continue
            s = fit_slope(Jarr, np.array(vals))
            per[df][rep] = (s, 0) if np.isfinite(s) else (float("nan"), -1)
    for rep in a["reps"]:
        ok = all(np.isfinite(per[df][rep][0]) for df in a["diffs"])
        valid[rep] = ok
        if not ok:
            why = "; ".join("{} {}".format(df, ("non-finite slope" if per[df][rep][1] == -1 else
                                                 "{} bad point(s)".format(per[df][rep][1])))
                            for df in a["diffs"] if not np.isfinite(per[df][rep][0]))
            out["dropped"].append((rep, a["keys"][rep], why,
                                   "dropped from both arms" if len(a["diffs"]) > 1 else ""))
    kept = [rep for rep in a["reps"] if valid[rep]]
    out["kept"] = kept
    n = len(kept)
    idx = boot_idx(a["bkey"], n) if n > 0 else None
    for df in a["diffs"]:
        r = {}
        if n == 0:
            out["diffs"][df] = {"n": 0}
            continue
        sl = np.array([per[df][rep][0] for rep in kept])
        Em = np.array([[a["E"][df][rep][J] for J in Js] for rep in kept])
        r["slopes"] = sl
        r["S"] = float(sl.mean())
        r["Sc"] = float(fit_slope(Jarr, Em.mean(axis=0)))
        vs = sl[idx].mean(axis=1)
        r["sd"] = float(np.nanstd(vs, ddof=1))
        r["q"] = pct(vs)
        Eb = Em[idx].mean(axis=1)
        vc = np.array([fit_slope(Jarr, Eb[b]) for b in range(B)])
        r["qc"] = pct(vc)
        if a["curv"]:
            cv = np.array([fit_curv(Jarr, Em[i]) for i in range(n)])
            r["C"] = float(np.mean(cv))
            r["qC"] = pct(cv[idx].mean(axis=1))
        out["diffs"][df] = r
    return out


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_runs(folders, expected):
    """tid -> realization dict. A0."""
    real = {}
    where = {}
    for f in folders:
        rels = rl.verify_folder(f)
        path = rl.find_file(f, rels, "rerun_real.csv")
        n = 0
        for r in csv.DictReader(open(path, newline="")):
            if r["end"] != "ok":
                continue
            tid = r["tid"]
            if tid in where:
                sys.stderr.write("A0: task {} complete in {} and {}\n".format(tid, where[tid], f))
                sys.exit(2)
            if tid not in expected:
                sys.stderr.write("A0: task {} in {} is not in the plan\n".format(tid, f))
                sys.exit(2)
            c, df = expected[tid]
            bad = []
            if r["beta"] != repr(c["beta"]):
                bad.append("beta {} vs plan {!r}".format(r["beta"], c["beta"]))
            if r["sigma"] != repr(c["sigma"][df]):
                bad.append("sigma {} vs plan {!r}".format(r["sigma"], c["sigma"][df]))
            if r["boot_key"] != rl.key_str(rl.boot_key(c, c["owner"])):
                bad.append("boot key")
            if r["seed_key"] != tid.rsplit("|", 1)[0]:
                bad.append("seed_key {} differs from the task id's key".format(r["seed_key"]))
            if bad:
                sys.stderr.write("A0: task {}: {}\n".format(tid, "; ".join(bad)))
                sys.exit(2)
            E = {}
            for J in rl.JCOLS:
                v = r["E_{}".format(J)]
                if v != "":
                    E[J] = float(v)
            aud = None
            if r["audit_ratios"]:
                aud = (float(r["audit_ref_ratio"]),
                       dict((int(k), float(v)) for k, v in json.loads(r["audit_ratios"]).items()))
            real[tid] = {"E": E, "extras": json.loads(r["extras"]) if r["extras"] else {},
                         "audit": aud, "F1": r["F1"], "key": r["seed_key"]}
            where[tid] = f
            n += 1
        say("  read {}  complete realizations {}".format(f, n))
    return real


def task_tid(c, df, rep):
    return "{}|{}".format(rl.key_str(rl.traj_key(c, c["owner"], rep)), df)


# --------------------------------------------------------------------------
# statistics on resample vectors
# --------------------------------------------------------------------------

class Ctx(object):
    def __init__(self, cells_by_row, results, real):
        self.rows = cells_by_row
        self.res = results
        self.real = real
        self.idx_cache = {}
        self.index = {}
        for row, cs in cells_by_row.items():
            for c in cs:
                self.index[(row,) + ckey(c)] = c

    def cell(self, row, **kw):
        k = (row,) + ckey_kw(**kw)
        if k not in self.index:
            raise KeyError("no cell {} {}".format(row, kw))
        return self.index[k]

    def S(self, c, df, w):
        """(point S-slope, B resamples) on window w ('full' or 'ge')."""
        Js = tuple(window(c, w))
        r = self.res[(rl.key_str(rl.boot_key(c, c["owner"])), Js)]
        d = r["diffs"][df]
        if d.get("n", 1) == 0 or "slopes" not in d:
            return float("nan"), np.full(B, np.nan)
        ck = (rl.key_str(rl.boot_key(c, c["owner"])), len(r["kept"]))
        if ck not in self.idx_cache:
            if len(self.idx_cache) > 64:
                self.idx_cache.clear()
            self.idx_cache[ck] = boot_idx(rl.boot_key(c, c["owner"]), len(r["kept"]))
        idx = self.idx_cache[ck]
        return d["S"], d["slopes"][idx].mean(axis=1)


def ckey(c):
    return (c["obj"], c["d"], c["law"], c["tau"], c["r"], c["sigma_design"], c["subarm"],
            c["jinf"], c["T"], c["arm"])


def ckey_kw(obj, d, law="centred", tau=None, r=None, sd=None, sub=0, jinf=50000, T=1.0, arm=""):
    return (obj, int(d), law, None if tau is None else float(tau), None if r is None else float(r),
            None if sd is None else float(sd), int(sub), int(jinf), float(T), arm)


def hetero(y, v):
    y = np.asarray(y, float)
    v = np.asarray(v, float)
    k = int(y.size)
    out = {"k": k}
    if k < 2:
        out.update({"sd_units": float("nan"), "vbar": float("nan"), "tau2_mm": float("nan"),
                    "Q": float("nan"), "I2": "undefined (k < 2)", "trunc": ""})
        return out
    s2 = float(np.var(y, ddof=1))
    vbar = float(np.mean(v))
    out.update({"sd_units": math.sqrt(s2), "vbar": vbar, "tau2_mm": max(0.0, s2 - vbar),
                "trunc": ("tau2 truncated at 0 (s2 {:.6g} < vbar {:.6g})".format(s2, vbar)
                          if s2 <= vbar else "")})
    zero = [i for i in range(k) if not (v[i] > 0)]
    if zero:
        out["Q"] = float("nan")
        out["I2"] = "undefined (v_i = 0 in unit index {})".format(",".join(str(i) for i in zero))
        return out
    w = 1.0 / v
    yw = float(np.sum(w * y) / np.sum(w))
    Q = float(np.sum((y - yw) ** 2 / v))
    out["Q"] = Q
    if Q == 0:
        out["I2"] = "undefined (Q = 0)"
    else:
        out["I2"] = "{:.4f}".format(max(0.0, (Q - (k - 1)) / Q))
    return out


STAT_COLS = ["row", "quantity", "group", "level", "unit", "window", "estimate", "lo95", "hi95",
             "p5", "p95", "verdict", "equivalence", "half_width_90", "nonfinite", "flag", "k",
             "sd_units", "vbar", "tau2_mm", "Q", "I2", "trunc", "round1_orientation", "note",
             "not_adequate"]


class Stats(object):
    def __init__(self):
        self.rows = []
        self.flags = []
        self.margin = None

    def one(self, row, quantity, group, level, unit, wlabel, point, vec, primary, equiv=False,
            orient=False, note="", het=None, cells=None):
        q = pct(vec)
        d = {"row": row, "quantity": quantity, "group": group, "level": level, "unit": unit,
             "window": wlabel, "estimate": point, "lo95": q["lo"], "hi95": q["hi"], "p5": q["p5"],
             "p95": q["p95"], "nonfinite": "{} of {}".format(q["nf"], B), "note": note,
             "not_adequate": na_flag(cells or [])}
        if q["nf"] > FLAG_FRAC * B:
            d["flag"] = "FLAG non-finite above 1%"
            self.flags.append("{} {} {} {}".format(row, quantity, group, unit))
        if primary:
            d["verdict"] = diff_verdict(q)
            if equiv and self.margin is not None:
                m = self.margin
                half = (q["p95"] - q["p5"]) / 2.0
                d["half_width_90"] = half
                if not (half < m):
                    d["equivalence"] = "equivalence not attainable at this margin"
                elif q["p5"] > -m and q["p95"] < m:
                    d["equivalence"] = "EQUIVALENT (90%, TOST 5% each side)"
                    if d["verdict"] == "DIFFERENCE":
                        d["note"] = (note + "; " if note else "") + \
                            "distinguishable from zero and smaller than the margin"
                else:
                    d["equivalence"] = "equivalence not established"
        else:
            d["verdict"] = "sensitivity, no verdict"
        if orient:
            d["round1_orientation"] = -point if np.isfinite(point) else float("nan")
        if het is not None:
            d.update(het)
        self.rows.append(d)
        extra = ""
        if d.get("equivalence"):
            extra += "  90% (TOST 5% each side) [{}, {}] half-width {} m {}: {}".format(
                fmt(q["p5"]), fmt(q["p95"]), fmt(d.get("half_width_90")), fmt(self.margin),
                d["equivalence"])
        if orient:
            extra += "  round-1 orientation {}".format(fmt(d["round1_orientation"]))
        if het is not None:
            extra += "  k {} sd_units {} vbar {} tau2_mm {} I2 {} {}".format(
                het["k"], fmt(het["sd_units"]), fmt(het["vbar"], 6), fmt(het["tau2_mm"], 6), het["I2"],
                het["trunc"])
        if d["not_adequate"]:
            extra += "  [not adequate: {}]".format(d["not_adequate"])
        say("  {:<9} {:<26} {:<34} {:<7} {:<22} {:<7} {} [{}, {}] {}{}".format(
            row, quantity[:26], group[:34], level, unit[:22], wlabel, fmt(point), fmt(q["lo"]),
            fmt(q["hi"]), d["verdict"], extra))
        return d

    def family(self, row, quantity, group, units, wlabel, primary, equiv=False, orient=False,
               note=""):
        """units: list of (label, point, vec, cells), cells the plan cells the
        unit's value is computed from (CAL3). Emits each unit and the pooled
        unweighted mean with item 6's statistics; the pooled row's
        not_adequate names the union over the units it pools."""
        excl = [u[0] for u in units if not np.isfinite(u[1])]
        units = [u for u in units if np.isfinite(u[1])]
        if excl:
            note = (note + "; " if note else "") + "excluded units (a cell without a finite S-slope): " + \
                ",".join(excl)
            say("  {} {} {}: excluded units {}; k {}".format(row, quantity, group, ",".join(excl), len(units)))
        for lab, p, v, cs in units:
            self.one(row, quantity, group, "unit", lab, wlabel, p, v, primary, equiv, orient, note, cells=cs)
        if len(units) >= 1:
            pts = np.array([u[1] for u in units])
            vecs = np.vstack([u[2] for u in units])
            vi = [float(np.nanvar(u[2], ddof=1)) for u in units]
            het = hetero(pts, vi)
            self.one(row, quantity, group, "pooled", "mean of {} units".format(len(units)), wlabel,
                     float(np.mean(pts)), vecs.mean(axis=0), primary, False, orient,
                     note + ("; " if note and equiv else "") +
                     ("equivalence per cell only (D2)" if equiv else ""), het,
                     cells=[c for u in units for c in u[3]])


def windows_for(cs):
    """[('full', 'W-full', True)] plus ('ge', 'W-ge', False) if any cell
    involved has a W-ge window shorter than W-full."""
    out = [("full", "W-full", True)]
    if any(has_ge(c) for c in cs):
        out.append(("ge", "W-ge", False))
    return out


def ols_coef(X, Y):
    """Coefficients of OLS of Y (n, or n x B) on X (n x p), by lstsq."""
    sol, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
    return sol


# --------------------------------------------------------------------------
# row analyses
# --------------------------------------------------------------------------

def conc_like(ctx, st, row):
    g = rl.GRID[row]
    objs, dims = g["objs"], g["dims"]
    laws = g.get("laws", ["centred"])
    taus = g["taus"]
    dlo, dhi = min(dims), max(dims)
    tloose, ttight = max(taus), min(taus)
    tmid = 0.1
    units = [(o, law) for o in objs for law in laws]
    ulab = lambda u: u[0] if len(laws) == 1 else "{}/{}".format(u[0], u[1])

    def C(u, d, t):
        return ctx.cell(row, obj=u[0], d=d, law=u[1], tau=t)

    def change(u, t, w):
        p1, v1 = ctx.S(C(u, dhi, t), "none", w)
        p0, v0 = ctx.S(C(u, dlo, t), "none", w)
        return p1 - p0, v1 - v0

    hdr("{}  contrasts 1, 2, 4, 7; CON pairs; TMM; REGF".format(row))
    # contrast 1
    for t in taus:
        cs = [C(u, d, t) for u in units for d in (dlo, dhi)]
        for w, wl, prim in windows_for(cs):
            us = [(ulab(u),) + change(u, t, w) + ([C(u, dhi, t), C(u, dlo, t)],) for u in units]
            st.family(row, "c1 dimension d{}-d{}".format(dhi, dlo), "tau0={}".format(t), us, wl, prim)
    # contrast 2
    for d in dims:
        cs = [C(u, d, t) for u in units for t in (ttight, tloose)]
        for w, wl, prim in windows_for(cs):
            us = []
            for u in units:
                p1, v1 = ctx.S(C(u, d, ttight), "none", w)
                p0, v0 = ctx.S(C(u, d, tloose), "none", w)
                us.append((ulab(u), p1 - p0, v1 - v0, [C(u, d, ttight), C(u, d, tloose)]))
            st.family(row, "c2 target {}-{}".format(ttight, tloose), "d={}".format(d), us, wl, prim)
    # contrast 4 (law), unit objective
    if row in ("CONC", "PROBEARM"):
        for d in dims:
            for t in taus:
                cs = [ctx.cell(row, obj=o, d=d, law=lw, tau=t) for o in objs for lw in laws]
                for w, wl, prim in windows_for(cs):
                    us = []
                    for o in objs:
                        c1 = ctx.cell(row, obj=o, d=d, law="mix-0.1", tau=t)
                        c0 = ctx.cell(row, obj=o, d=d, law="centred", tau=t)
                        p1, v1 = ctx.S(c1, "none", w)
                        p0, v0 = ctx.S(c0, "none", w)
                        us.append((o, p1 - p0, v1 - v0, [c1, c0]))
                    st.family(row, "c4 law mix-0.1-centred", "d={} tau0={}".format(d, t), us, wl, prim)
    # CON pairs and TMM
    allc = [C(u, d, t) for u in units for d in (dlo, dhi) for t in (ttight, tmid, tloose)]
    pairs = [(tmid, tloose), (ttight, tloose), (ttight, tmid)]
    for t1, t2 in pairs:
        cs = [C(u, d, t) for u in units for d in (dlo, dhi) for t in (t1, t2)]
        for w, wl, prim in windows_for(cs):
            us = []
            for u in units:
                a1, b1 = change(u, t1, w)
                a2, b2 = change(u, t2, w)
                us.append((ulab(u), a1 - a2, b1 - b2, [C(u, d, t) for d in (dlo, dhi) for t in (t1, t2)]))
            name = "CON({}, {})".format(t1, t2)
            if (t1, t2) == (ttight, tloose):
                name += " = contrast 7"
            st.family(row, name, "change = d{}-d{}".format(dhi, dlo), us, wl, prim, orient=True,
                      note="round-1 CON(t2, t1) is the negative")
    for w, wl, prim in windows_for(allc):
        us = []
        for u in units:
            a, va = change(u, ttight, w)
            b, vb = change(u, tloose, w)
            c_, vc = change(u, tmid, w)
            us.append((ulab(u), a - (b + c_) / 2.0, va - (vb + vc) / 2.0,
                       [C(u, d, t) for d in (dlo, dhi) for t in (ttight, tloose, tmid)]))
        st.family(row, "TMM", "change({}) - mean(change({}), change({}))".format(ttight, tloose, tmid),
                  us, wl, prim)
    # REGF
    cells_u = [(d, t) for d in dims for t in taus]
    X = np.array([[1.0, math.log2(d), math.log10(1.0 / t), math.log2(d) * math.log10(1.0 / t)]
                  for d, t in cells_u])
    allr = [C(u, d, t) for u in units for d, t in cells_u]
    for w, wl, prim in windows_for(allr):
        coefs = {}
        for u in units:
            pts, vecs = [], []
            for d, t in cells_u:
                p, v = ctx.S(C(u, d, t), "none", w)
                pts.append(p)
                vecs.append(v)
            cp_ = ols_coef(X, np.array(pts))
            cv_ = ols_coef(X, np.vstack(vecs))
            coefs[u] = (cp_, cv_)
        for j, nm in ((1, "REGF b_d"), (2, "REGF b_tau"), (3, "REGF b_dtau")):
            us = [(ulab(u), float(coefs[u][0][j]), coefs[u][1][j], [C(u, d, t) for d, t in cells_u])
                  for u in units]
            st.family(row, nm, "{} d x {} tau0".format(len(dims), len(taus)), us, wl, prim)


def paired_gaps(ctx, st, row):
    g = rl.GRID[row]
    hdr("{}  contrast 3, anisotropic - isotropic, paired by key".format(row))
    groups = {}
    for c in ctx.rows[row]:
        gk = (c["d"], c["r"], c["sigma_design"], c["subarm"], c["tau"])
        groups.setdefault(gk, []).append(c)
    for gk in sorted(groups, key=lambda z: tuple(-1 if v is None else v for v in z)):
        cs = sorted(groups[gk], key=lambda c: g["objs"].index(c["obj"]))
        lab = "d={} {}tau0={}".format(gk[0], ("r={} ".format(gk[1]) if gk[1] is not None else
                                            "sigma={} ".format(gk[2]) if gk[2] is not None else ""),
                                      gk[4])
        for w, wl, prim in windows_for(cs):
            us = []
            for c in cs:
                pa, va = ctx.S(c, "anisotropic", w)
                pi, vi = ctx.S(c, "isotropic", w)
                us.append((c["obj"], pa - pi, va - vi, [c]))
            st.family(row, "c3 aniso-iso", lab, us, wl, prim, equiv=True)


def target_contrast_paired(ctx, st, row):
    g = rl.GRID[row]
    taus = g["taus"]
    ttight, tloose = min(taus), max(taus)
    hdr("{}  contrast 2, target {} - {}, per arm".format(row, ttight, tloose))
    groups = {}
    for c in ctx.rows[row]:
        if c["tau"] != ttight:
            continue
        groups.setdefault((c["d"], c["r"], c["sigma_design"], c["subarm"]), []).append(c)
    for df in g["diffs"]:
        for gk in sorted(groups, key=lambda z: tuple(-1 if v is None else v for v in z)):
            cs = sorted(groups[gk], key=lambda c: g["objs"].index(c["obj"]))
            pairs = [(c, ctx.cell(row, obj=c["obj"], d=c["d"], tau=tloose, r=c["r"],
                                  sd=c["sigma_design"], sub=c["subarm"])) for c in cs]
            lab = "{} d={} {}".format(df, gk[0], ("r={}".format(gk[1]) if gk[1] is not None else
                                                  "sigma={}".format(gk[2])))
            for w, wl, prim in windows_for([x for p in pairs for x in p]):
                us = []
                for c1, c0 in pairs:
                    p1, v1 = ctx.S(c1, df, w)
                    p0, v0 = ctx.S(c0, df, w)
                    us.append((c1["obj"], p1 - p0, v1 - v0, [c1, c0]))
                st.family(row, "c2 target {}-{}".format(ttight, tloose), lab, us, wl, prim)


def sigma_a2(ctx, st):
    row = "SIGMA"
    g = rl.GRID[row]
    rs = g["rs"]
    X = np.array([[r, 1.0] for r in rs])
    hdr("SIGMA  audit A2: OLS coefficient of S-slope on r (L1)")
    for df in g["diffs"]:
        for d in g["dims"]:
            for t in g["taus"]:
                cs = [ctx.cell(row, obj=o, d=d, tau=t, r=r) for o in g["objs"] for r in rs]
                for w, wl, prim in windows_for(cs):
                    us = []
                    for o in g["objs"]:
                        pts, vecs = [], []
                        for r in rs:
                            p, v = ctx.S(ctx.cell(row, obj=o, d=d, tau=t, r=r), df, w)
                            pts.append(p)
                            vecs.append(v)
                        us.append((o, float(ols_coef(X, np.array(pts))[0]), ols_coef(X, np.vstack(vecs))[0],
                                   [ctx.cell(row, obj=o, d=d, tau=t, r=r) for r in rs]))
                    st.family(row, "A2 coef of slope on r", "{} d={} tau0={}".format(df, d, t), us, wl, prim)


def rmap_panel(ctx, st, row, partner):
    """J3 for RMAP (partner ONSET) and, mirrored (CAL2), RMAP-CAL (partner
    ONSET-CAL)."""
    g = rl.GRID[row]
    cells_u = [(t, r) for t in g["taus"] for r in g["rs"]]
    X = np.array([[1.0, math.log10(0.5 / t), math.log2(r / 0.5),
                   math.log10(0.5 / t) * math.log2(r / 0.5)] for t, r in cells_u])
    hdr("{}  panel model Delta = a + b1 g + b2 h + b3 g h (J3)".format(row))
    for df in g["diffs"]:
        for d in g["dims"]:
            cs = [ctx.cell(row, obj=o, d=d, tau=t, r=r) for o in g["objs"] for t, r in cells_u]
            for w, wl, prim in windows_for(cs):
                coefs = {}
                for o in g["objs"]:
                    pts, vecs = [], []
                    for t, r in cells_u:
                        p, v = ctx.S(ctx.cell(row, obj=o, d=d, tau=t, r=r), df, w)
                        pts.append(-1.0 - p)
                        vecs.append(-1.0 - v)
                    coefs[o] = (ols_coef(X, np.array(pts)), ols_coef(X, np.vstack(vecs)))
                for j, nm in ((1, "panel b1"), (2, "panel b2"), (3, "panel b3")):
                    us = [(o, float(coefs[o][0][j]), coefs[o][1][j],
                           [ctx.cell(row, obj=o, d=d, tau=t, r=r) for t, r in cells_u]) for o in g["objs"]]
                    st.family(row, nm, "{} d={}".format(df, d), us, wl, prim)
    say("  partm P-M4 ({} against {} at tau0 0.1, r 1.0): vacuous; those cells are shared,".format(
        row, partner))
    say("  so the comparison is identically zero by construction. No number.")


def onset_block(ctx, st, onset_rows, row):
    """H3, J4, contrast 6 and J2 for ONSET and, mirrored (CAL2), ONSET-CAL."""
    g = rl.GRID[row]
    rs, objs, dims = g["rs"], g["objs"], g["dims"]
    t = g["tau"]
    hdr("{}  onsets (H3), contrast 6, onset against 1 (J4), severity (J2)".format(row))
    ons = {}

    def ocells(o, d):
        objs_ = objs if o == "pooled" else [o]
        return [ctx.cell(row, obj=x, d=d, tau=t, r=r) for x in objs_ for r in rs]
    for df in g["diffs"]:
        for d in dims:
            per = []
            for o in objs:
                pts, vecs = [], []
                for r in rs:
                    p, v = ctx.S(ctx.cell(row, obj=o, d=d, tau=t, r=r), df, "full")
                    pts.append(p)
                    vecs.append(v)
                Y = np.vstack(vecs)
                pt = rl.onset_bp(rs, pts)
                vv = np.array([rl.onset_bp(rs, Y[:, b]) if np.all(np.isfinite(Y[:, b])) else np.nan
                               for b in range(B)])
                ons[(df, o, d)] = (pt, vv)
                per.append((pts, Y))
            mp = list(np.mean(np.array([p[0] for p in per]), axis=0))
            MY = np.mean(np.stack([p[1] for p in per]), axis=0)
            pt = rl.onset_bp(rs, mp)
            vv = np.array([rl.onset_bp(rs, MY[:, b]) if np.all(np.isfinite(MY[:, b])) else np.nan
                           for b in range(B)])
            ons[(df, "pooled", d)] = (pt, vv)
    cnt = {}
    for (df, o, d), (pt, vv) in sorted(ons.items(), key=lambda z: (z[0][0], str(z[0][1]), z[0][2])):
        q = pct(vv)
        con = (q["lo"] <= 1.0 <= q["hi"])
        lvl = "pooled" if o == "pooled" else "objective"
        cnt.setdefault((lvl, df), [0, 0])
        cnt[(lvl, df)][0] += 1 if con else 0
        cnt[(lvl, df)][1] += 1
        rec = {"row": row, "diffusion": df, "objective": o, "d": d, "onset": pt, "lo95": q["lo"],
               "hi95": q["hi"], "contains_1": "yes" if con else "no", "nonfinite": "{} of {}".format(q["nf"], B),
               "not_adequate": na_flag(ocells(o, d))}
        if o != "pooled":
            rec["v_i"] = float(np.nanvar(vv, ddof=1))
        onset_rows.append(rec)
        say("  onset {:<11} {:<9} d={:<3} {:.2f}  95% [{:.2f}, {:.2f}]  contains 1: {}".format(
            df, o, d, pt, q["lo"], q["hi"], "yes" if con else "no"))
    for df in g["diffs"]:
        for d in dims:
            y = [ons[(df, o, d)][0] for o in objs]
            v = [float(np.nanvar(ons[(df, o, d)][1], ddof=1)) for o in objs]
            h = hetero(y, v)
            say("  pooled onset {} d={} (onset of the mean curve, not the mean of onsets): "
                "per-objective heterogeneity k {} sd_units {} I2 {} {}".format(
                    df, d, h["k"], fmt(h["sd_units"]), h["I2"], h["trunc"]))
            onset_rows.append(dict({"row": row, "diffusion": df,
                                    "objective": "heterogeneity of per-objective onsets", "d": d,
                                    "not_adequate": na_flag(ocells("pooled", d))}, **h))
    say("")
    for lvl in ("objective", "pooled"):
        tot = [0, 0]
        for df in g["diffs"]:
            k, n = cnt[(lvl, df)]
            tot[0] += k
            tot[1] += n
            say("  J4 {:<9} {:<11} {} of {} intervals contain 1".format(lvl, df, k, n))
            onset_rows.append({"row": row, "diffusion": df, "objective": "J4 count " + lvl,
                               "contains_1": "{} of {}".format(k, n),
                               "not_adequate": na_flag([c for d in dims for c in ocells("pooled", d)])})
        say("  J4 {:<9} {:<11} {} of {} intervals contain 1".format(lvl, "both", tot[0], tot[1]))
        onset_rows.append({"row": row, "diffusion": "both", "objective": "J4 count " + lvl,
                           "contains_1": "{} of {}".format(tot[0], tot[1]),
                           "not_adequate": na_flag([c for d in dims for c in ocells("pooled", d)])})
    say("  (a description of where the intervals fall, not a claim that the onset is at 1)")
    # contrast 6
    for df in g["diffs"]:
        us = [(o, ons[(df, o, max(dims))][0] - ons[(df, o, min(dims))][0],
               ons[(df, o, max(dims))][1] - ons[(df, o, min(dims))][1]) for o in objs]
        for lab, p, v in us:
            st.one(row, "c6 onset d{}-d{}".format(max(dims), min(dims)), df, "unit", lab, "W-full", p, v, True,
                   cells=ocells(lab, max(dims)) + ocells(lab, min(dims)))
        het = hetero([u[1] for u in us], [float(np.nanvar(u[2], ddof=1)) for u in us])
        pp = ons[(df, "pooled", max(dims))]
        p0 = ons[(df, "pooled", min(dims))]
        st.one(row, "c6 onset d{}-d{}".format(max(dims), min(dims)), df, "pooled",
               "pooled onsets (mean curve)", "W-full", pp[0] - p0[0], pp[1] - p0[1], True,
               note="pooled = onset of mean curve; heterogeneity of per-objective contrasts", het=het,
               cells=ocells("pooled", max(dims)) + ocells("pooled", min(dims)))
    # severity and trend
    hdr("{}  severity S(1,3), sensitivity S(0.75,3), and their trend on log2 d (J2)".format(row))
    Xd = np.array([[math.log2(d), 1.0] for d in dims])
    for nm, rlo in (("severity S(1,3)", 1.0), ("severity S(0.75,3) boundary-spanning", 0.75)):
        sev = {}
        for df in g["diffs"]:
            for d in dims:
                us = []
                for o in objs:
                    c3_ = ctx.cell(row, obj=o, d=d, tau=t, r=3.0)
                    c1_ = ctx.cell(row, obj=o, d=d, tau=t, r=rlo)
                    p3, v3 = ctx.S(c3_, df, "full")
                    p1, v1 = ctx.S(c1_, df, "full")
                    sev[(df, o, d)] = (p3 - p1, v3 - v1)
                    us.append((o, p3 - p1, v3 - v1, [c3_, c1_]))
                st.family(row, nm, "{} d={}".format(df, d), us, "W-full", True)
            us = []
            for o in objs:
                pts = np.array([sev[(df, o, d)][0] for d in dims])
                Y = np.vstack([sev[(df, o, d)][1] for d in dims])
                us.append((o, float(ols_coef(Xd, pts)[0]), ols_coef(Xd, Y)[0],
                           [ctx.cell(row, obj=o, d=d, tau=t, r=rr) for d in dims for rr in (3.0, rlo)]))
            st.family(row, nm + " trend per doubling of d", df, us, "W-full", True,
                      note="coefficient only; no shape is claimed")


def refsize_block(ctx, st):
    row = "REFSIZE"
    g = rl.GRID[row]
    jhi, jlo = max(g["jinfs"]), min(g["jinfs"])
    hdr("REFSIZE  contrast 5, J_inf {} - {} on J <= {}".format(jhi, jlo, REFSIZE_CAP))
    us = []
    for o in g["objs"]:
        c1 = ctx.cell(row, obj=o, d=g["d"], tau=0.1, jinf=jhi)
        c0 = ctx.cell(row, obj=o, d=g["d"], tau=0.1, jinf=jlo)
        p1, v1 = ctx.S(c1, "none", "full")
        p0, v0 = ctx.S(c0, "none", "full")
        us.append((o, p1 - p0, v1 - v0, [c1, c0]))
    st.family(row, "c5 J_inf {}-{}".format(jhi, jlo), "J <= {}".format(REFSIZE_CAP), us, "W-full", True)


def audit_block(ctx, st, row, audit_rows):
    g = rl.GRID[row]
    cs = ctx.rows[row]
    hdr("{}  finite-J audit (8.5)".format(row))
    bad = []
    for c in cs:
        for rep in range(c["M"]):
            r = ctx.real[task_tid(c, "none", rep)]
            if r["F1"] != "ok" or r["audit"] is None:
                bad.append(task_tid(c, "none", rep))
    if bad:
        say("  F1 FAILED in {} realization(s), e.g. {}: the audit of {} is not reported.".format(
            len(bad), bad[0], row))
        return
    R = {}
    for c in cs:
        reps = list(range(c["M"]))
        mats = dict((J, np.array([ctx.real[task_tid(c, "none", rep)]["audit"][1][J] for rep in reps]))
                    for J in rl.jlist_of(c))
        ref = np.array([ctx.real[task_tid(c, "none", rep)]["audit"][0] for rep in reps])
        R[id(c)] = mats
        tf = tau_frac(c)
        for J, v in sorted(mats.items()):
            fl = float(1 / (J * tf))
            audit_rows.append({"row": row, "objective": c["obj"], "d": c["d"], "law": c["law"],
                               "tau0": c["tau"], "J": J, "n": v.size, "mean": float(v.mean()),
                               "sd": float(np.std(v, ddof=1)), "p5": float(np.percentile(v, 5)),
                               "p95": float(np.percentile(v, 95)), "ref_ratio_mean": float(ref.mean()),
                               "floor": fl, "floor_flag": "floor (J tau0 < 1)" if J * tf < 1 else "",
                               "not_adequate": na_flag([c])})
    say("  per-cell ratio summaries written to analysis_audit.csv ({} rows)".format(len(audit_rows)))
    dims = g["dims"]
    dlo, dhi = min(dims), max(dims)
    laws = g.get("laws", ["centred"])
    units = [(o, law) for o in g["objs"] for law in laws]
    nex = [0, 0]
    for t in g["taus"]:
        J_list = rl.jlist_of(ctx.cell(row, obj=units[0][0], d=dhi, law=units[0][1], tau=t))
        for J in J_list:
            us = []
            for u in units:
                c1 = ctx.cell(row, obj=u[0], d=dhi, law=u[1], tau=t)
                c0 = ctx.cell(row, obj=u[0], d=dlo, law=u[1], tau=t)
                i1 = boot_idx(rl.boot_key(c1, c1["owner"]), c1["M"])
                i0 = boot_idx(rl.boot_key(c0, c0["owner"]), c0["M"])
                a1, a0 = R[id(c1)][J], R[id(c0)][J]
                us.append((u[0] if len(laws) == 1 else "{}/{}".format(*u),
                           float(a1.mean() - a0.mean()), a1[i1].mean(axis=1) - a0[i0].mean(axis=1), [c1, c0]))
            st.family(row, "audit ratio(J) d{}-d{}".format(dhi, dlo), "tau0={} J={}".format(t, J), us,
                      "audit", True, orient=True, note="round 1 printed d{} - d{}".format(dlo, dhi))
            pooled = st.rows[-1]
            nex[1] += 1
            nex[0] += 1 if pooled["verdict"] == "DIFFERENCE" else 0
    say("  {} audit: {} of {} pooled intervals exclude 0 (no PASS/FAIL)".format(row, nex[0], nex[1]))


def r2_blocks(ctx, complete, r2_rows):
    for row in ("CONC", "PROBEARM"):
        if row not in complete:
            continue
        g = rl.GRID[row]
        cs = ctx.rows[row]
        y = np.array([ctx.S(c, "none", "full")[0] for c in cs])
        ltau = np.log(np.array([c["tau"] for c in cs]))
        ld = np.log(np.array([c["d"] for c in cs], float))
        one = np.ones(len(cs))
        Dobj = np.zeros((len(cs), len(g["objs"]) - 1))
        for i, c in enumerate(cs):
            j = g["objs"].index(c["obj"])
            if j > 0:
                Dobj[i, j - 1] = 1.0
        vals = [("P3.4 target alone (log tau0)", r2_of(np.vstack([ltau, one]).T, y)),
                ("P3.4 target + dimension (log tau0, log d)", r2_of(np.vstack([ltau, ld, one]).T, y)),
                ("P3.4 target + dimension + objective dummies",
                 r2_of(np.column_stack([ltau, ld, one, Dobj]), y))]
        hdr("{}  mechanism P3.4 R^2, point values, no interval, no verdict (L2)".format(row))
        for nm, v in vals:
            say("  {:<48} R^2 = {:.4f}   (OLS of the {} cell S-slopes, W-full)".format(nm, v, len(cs)))
            r2_rows.append({"row": row, "fit": nm, "R2": v, "R2_out": "", "RMSE_out": "",
                            "note": "response: cell S-slope on W-full; mechanism.r2_of", "not_adequate": na_flag(cs)})
    if "SYNTH" in complete and "NAMED" in complete:
        hdr("SYNTH -> NAMED  regime P6.3, nested models, point values, no verdict (L2)")

        def rows_of(row):
            out, keys = {}, []
            for c in ctx.rows[row]:
                k = (c["obj"], c["d"], c["law"], c["tau"], c["jinf"], c["T"])
                d = {"slope": ctx.S(c, "none", "full")[0]}
                for f in FEATNAMES:
                    v = [ctx.real[task_tid(c, "none", rep)]["extras"]["feats." + f] for rep in range(c["M"])]
                    d[f] = float(np.mean(v))
                out[k] = d
                keys.append(k)
            return out, keys
        rb, kb = rows_of("SYNTH")
        rc, kc = rows_of("NAMED")
        for nm, fs in P63_MODELS:
            a, b, c_ = fit_predict(rb, kb, rc, kc, fs)
            say("  {:<26} R^2 in {:.4f}  R^2 out {:.4f}  RMSE out {:.4f}".format(nm, a, b, c_))
            r2_rows.append({"row": "SYNTH->NAMED", "fit": "P6.3 " + nm, "R2": a, "R2_out": b,
                            "RMSE_out": c_, "note": "regime.fit_predict; response cell S-slope (item 0), "
                                                     "where the archive used the mean-curve slope",
                            "not_adequate": na_flag(ctx.rows["SYNTH"] + ctx.rows["NAMED"])})


# --------------------------------------------------------------------------
# phase 1, per-cell records, margin, the CAL4 check, CAL5 counts
# --------------------------------------------------------------------------

CCOLS = ["row", "cell", "owner", "diffusion", "window", "J", "M", "S_slope", "sd_boot", "lo95", "hi95",
         "one_sided_upper95", "upper_bound_le_minus1", "nonfinite", "S_curve_secondary", "S_curve_lo95",
         "S_curve_hi95", "curvature_mean_per_realization", "curvature_lo95", "curvature_hi95",
         "ess_min_ref_mean", "ess_min_sub_mean", "beta", "beta_source", "flag", "not_adequate"]
ONSET_COLS = ["diffusion", "objective", "d", "onset", "lo95", "hi95", "contains_1", "nonfinite", "v_i", "k",
              "sd_units", "vbar", "tau2_mm", "Q", "I2", "trunc", "not_adequate"]
AUDIT_COLS = ["row", "objective", "d", "law", "tau0", "J", "n", "mean", "sd", "p5", "p95", "ref_ratio_mean",
              "floor", "floor_flag", "not_adequate"]
R2_COLS = ["row", "fit", "R2", "R2_out", "RMSE_out", "note", "not_adequate"]
ADQ_COLS = ["module", "objective", "d", "law", "tau0", "label", "beta", "tau_ref", "tau_ref_n", "range",
            "adequacy", "C5m", "D1", "med_64M", "med_256M", "provenance", "flags"]


def phase1(rows, by_row, real, workers, results):
    """Per-cell computations for the given rows; fills results and returns
    the cell-window instances in emission order."""
    jobs = {}
    inst = []
    for row in rows:
        for c in by_row[row]:
            wins = [("full", "W-full")]
            if has_ge(c):
                wins.append(("ge", "W-ge"))
            if row == "REFSIZE" and rl.jlist_of(c) != win_full(c):
                wins.append(("grid", "W-grid"))
            bk = rl.key_str(rl.boot_key(c, c["owner"]))
            for w, wl in wins:
                Js = tuple(window(c, w))
                jid = (bk, Js)
                inst.append((row, c, w, wl, jid))
                if jid in jobs or jid in results:
                    continue
                E = dict((df, dict((rep, real[task_tid(c, df, rep)]["E"]) for rep in range(c["M"])))
                         for df in c["diffs"])
                keys = dict((rep, rl.key_str(rl.traj_key(c, c["owner"], rep))) for rep in range(c["M"]))
                jobs[jid] = {"id": jid, "bkey": rl.boot_key(c, c["owner"]), "Js": list(Js),
                             "diffs": c["diffs"], "reps": list(range(c["M"])), "E": E, "keys": keys,
                             "curv": c["module"] == "regime"}
    say("  {} cell-window instances, {} distinct computations, {} workers".format(len(inst), len(jobs), workers))
    pool = multiprocessing.Pool(processes=workers)
    try:
        for o in pool.imap_unordered(cw_task, list(jobs.values()), chunksize=1):
            results[o["id"]] = o
    finally:
        pool.close()
        pool.join()
    return inst


def cell_records(inst, results, real, cell_rows, cflags):
    for row, c, w, wl, jid in inst:
        r = results[jid]
        for d_ in r["dropped"]:
            say("  {} {} {} rep {} key {}: {} {}".format(row, rl.cell_label(c), wl, d_[0], d_[1], d_[2], d_[3]))
        nk = len(r["kept"])
        flag = "FLAG: {} realizations dropped".format(len(r["dropped"])) if len(r["dropped"]) > 1 else ""
        if flag:
            cflags.append("{} {} {}".format(row, rl.cell_label(c), wl))
        naf = na_flag([c])
        for df in c["diffs"]:
            s = r["diffs"][df]
            if "S" not in s:
                cell_rows.append({"row": row, "cell": rl.cell_label(c), "diffusion": df, "window": wl,
                                  "M": "0 of {}".format(c["M"]), "flag": "no realization kept",
                                  "not_adequate": naf})
                continue
            q, qc = s["q"], s["qc"]
            ver = ("yes" if q["p95"] <= -1.0 else "no") if w == "full" else "sensitivity, no verdict"
            rec = {"row": row, "cell": rl.cell_label(c), "owner": c["owner"], "diffusion": df,
                   "window": wl, "J": " ".join(str(J) for J in window(c, w)),
                   "M": "{} of {}".format(nk, c["M"]), "S_slope": s["S"], "sd_boot": s["sd"],
                   "lo95": q["lo"], "hi95": q["hi"], "one_sided_upper95": q["p95"],
                   "upper_bound_le_minus1": ver, "nonfinite": "{} of {}".format(q["nf"], B),
                   "S_curve_secondary": s["Sc"], "S_curve_lo95": qc["lo"], "S_curve_hi95": qc["hi"],
                   "beta": repr(c["beta"]), "beta_source": rl.BETA_SOURCE[row], "flag": flag,
                   "not_adequate": naf}
            if q["nf"] > FLAG_FRAC * B:
                rec["flag"] = (flag + "; " if flag else "") + "FLAG non-finite above 1%"
                cflags.append("{} {} {} non-finite".format(row, rl.cell_label(c), wl))
            if "C" in s:
                rec["curvature_mean_per_realization"] = s["C"]
                rec["curvature_lo95"] = s["qC"]["lo"]
                rec["curvature_hi95"] = s["qC"]["hi"]
            if row in ("BETA-ISO", "BETA-ANI") and w == "full":
                ex = [real[task_tid(c, df, rep)]["extras"] for rep in range(c["M"])]
                rec["ess_min_ref_mean"] = float(np.mean([e["ess_min_ref"] for e in ex]))
                rec["ess_min_sub_mean"] = json.dumps(dict(
                    (str(J), float(np.mean([e["ess_min_sub.{}".format(J)] for e in ex])))
                    for J in rl.jlist_of(c)))
            cell_rows.append(rec)
            say("  {:<9} {:<60} {:<11} {:<6} M {:<8} S {} [{}, {}] ub95 {} <=-1: {}  S-curve {}{}{}".format(
                row, rl.cell_label(c)[:60], df, wl, rec["M"], fmt(s["S"]), fmt(q["lo"]), fmt(q["hi"]),
                fmt(q["p95"]), ver, fmt(s["Sc"]),
                ("  curv " + fmt(s["C"], 5)) if "C" in s else "",
                ("  [not adequate: {}]".format(naf)) if naf else ""))


def arm_sds(rows, by_row, results):
    """(boot key, diffusion) -> (row, SD), a shared cell once (5b)."""
    sds = {}
    for row in rows:
        for c in by_row[row]:
            bk = rl.key_str(rl.boot_key(c, c["owner"]))
            r = results[(bk, tuple(win_full(c)))]
            for df in c["diffs"]:
                if (bk, df) in sds:
                    continue
                sds[(bk, df)] = (row if c["owner"] == row else c["owner"], r["diffs"][df].get("sd", float("nan")))
    return sds


def adequacy_rows(cells, rows):
    """analysis_adequacy.csv records for the calibration cells of the given
    rows, in plan order, each calibration cell once."""
    adq = []
    seen = set()
    for c in cells:
        if c["row"] not in rows:
            continue
        pr = c["plan_row"]
        k = rl.calprec2_key(c)
        if k in seen or pr["cal_label"] == "":
            continue
        seen.add(k)
        adq.append({"module": k[0], "objective": k[1], "d": k[2], "law": k[3], "tau0": k[4],
                    "label": pr["cal_label"], "beta": pr["beta"], "tau_ref": pr["cal_tau_ref"],
                    "tau_ref_n": pr["cal_tau_ref_n"], "range": pr["cal_range"], "adequacy": pr["cal_adequacy"],
                    "C5m": pr["cal_C5m"], "D1": pr["cal_D1"], "med_64M": pr["cal_med_64M"],
                    "med_256M": pr["cal_med_256M"], "provenance": pr["cal_provenance"], "flags": pr["cal_flags"]})
    return adq


def split_category(pr):
    """CAL5: label + " | " + provenance, beta_prod's N_cell dropped."""
    prov = pr["cal_provenance"]
    if prov.startswith("beta_prod"):
        prov = "beta_prod"
    return "{} | {}".format(pr["cal_label"], prov)


def compare_old(old_dir, rels, tables, names=None):
    """CAL4. tables: file name -> (cols, rows). Returns (per-file records,
    differences). Every value of every column of the old file must equal
    the new value of the same column, as a string, row by row."""
    recs, diffs = [], []
    for name in (names or REPRO_FILES):
        old = list(csv.reader(open(rl.find_file(old_dir, rels, name), newline="")))
        cols, rows = tables[name]
        new = as_strings(cols, rows)
        oh, nh = old[0], new[0]
        miss = [h for h in oh if h not in nh]
        nd = 0
        if miss:
            diffs.append((name, "header", "", "columns {} absent from the new table".format(miss), ""))
            nd += 1
        elif len(old) != len(new):
            diffs.append((name, "rows", "", "{} old rows".format(len(old) - 1), "{} new rows".format(len(new) - 1)))
            nd += 1
        else:
            pos = [nh.index(h) for h in oh]
            for i in range(1, len(old)):
                for j, h in enumerate(oh):
                    if old[i][j] != new[i][pos[j]]:
                        diffs.append((name, "row {}".format(i), h, old[i][j], new[i][pos[j]]))
                        nd += 1
        recs.append([name, "PASS" if nd == 0 else "FAIL", len(old) - 1, len(new) - 1, nd])
    return recs, diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--plan-from", required=True)
    ap.add_argument("--reproduce", required=True,
                    help="the seventeen-row result folder (CAL4), runs/rerun-analysis-20261025-051314")
    ap.add_argument("--runs", action="append", default=[])
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    a.runs = [f for x in a.runs for f in x.split(",") if f]
    t_start = time.time()

    say("=" * 100)
    say("CBO-GAP rerun_analysis -- fixed-beta rerun, analysis (no trajectories)")
    say("=" * 100)
    me = rl.file_sha(os.path.abspath(__file__))
    hs = rerun.script_hashes()
    say("  rerun_analysis sha256 {}".format(me))
    for k, v in sorted(hs.items()):
        say("  {:<20} {}".format(k, v))
    say("  python {}   numpy {}   platform {}   workers {}".format(
        platform.python_version(), np.__version__, platform.platform(), a.workers))
    say("  B {}   intervals: two-sided 95% percentile; one-sided 95% = 95th percentile;"
        " TOST 5% each side".format(B))
    say("  bootstrap indices: default_rng(SeedSequence(boot key, kind {})).integers(0, n, (B, n))".format(
        rl.KIND_BOOT))
    say("  margin m = {} x median per-cell SD over {}; revisit ratio > {}; calibrated r rows {} borrow m"
        " (CAL1)".format(K_TOL, ",".join(MARGIN_ROWS), REVISIT_RATIO, ",".join(CALR_ROWS)))
    say("  rate verdict: one-sided 95% upper bound <= -1, W-full; non-finite flag above {:.0%} of B".format(
        FLAG_FRAC))
    say("  plan {}".format(a.plan_from))
    say("  reproduce {}  (CAL4: the seventeen rows must equal it, as strings)".format(a.reproduce))
    for f in a.runs:
        say("  run  {}".format(f))

    if list(rl.ROWS) != ANALYSIS_ROWS:
        say("\n  GUARD: rerunlib.ROWS is {}".format(",".join(rl.ROWS)))
        say("  this analysis has criteria for {} only.".format(",".join(ANALYSIS_ROWS)))
        say("  Nothing computed, no folder written.")
        sys.exit(2)
    if not rerun.check_p1():
        sys.stderr.write("P1 failed\n")
        sys.exit(2)
    pparams, cells, plan_sha = rerun.load_plan(a.plan_from)
    say("  plan rerun_plan.csv sha256 {}   calprec2 rows {}".format(plan_sha, pparams.get("calprec2_rows")))
    for k in ("rerunlib_sha256", "costprobe2_sha256"):
        if pparams.get(k) != hs[k]:
            sys.stderr.write("plan built with a different {} ({} vs {})\n".format(k, pparams.get(k), hs[k]))
            sys.exit(2)
    old_rels = rl.verify_folder(a.reproduce)
    msha = rl.file_sha(os.path.join(a.reproduce, "sha256.txt"))
    if os.path.basename(os.path.normpath(a.reproduce)) != REPRO_DIR or msha != REPRO_MANIFEST_SHA256:
        sys.stderr.write("--reproduce {}: expected {} with sha256.txt {}, found sha256.txt {}\n".format(
            a.reproduce, REPRO_DIR, REPRO_MANIFEST_SHA256, msha))
        sys.exit(2)
    for name in REPRO_FILES:
        rl.find_file(a.reproduce, old_rels, name)
    say("  reproduce folder verified against its sha256.txt ({} files)".format(len(old_rels)))

    expected = {}
    for c in cells:
        if c["beta"] is None or c["row"] != c["owner"]:
            continue
        for df in c["diffs"]:
            for rep in range(c["M"]):
                expected[task_tid(c, df, rep)] = (c, df)
    hdr("A0  reading run folders")
    real = load_runs(a.runs, expected)

    hdr("A1  completeness per row (all twenty, CAL4)")
    by_row = {}
    for c in cells:
        by_row.setdefault(c["row"], []).append(c)
    complete = []
    comp_rows = []
    for row in rl.ROWS:
        need = [(c, df, rep) for c in by_row[row] for df in c["diffs"] for rep in range(c["M"])]
        pending = any(c["beta"] is None for c in by_row[row])
        have = sum(1 for (c, df, rep) in need if task_tid(c, df, rep) in real)
        ok = (not pending) and have == len(need)
        if ok:
            complete.append(row)
        comp_rows.append([row, len(need), have, "complete" if ok else
                          ("beta pending" if pending else "INCOMPLETE")])
        say("  {:<9} realizations {:>5} present {:>5}  {}".format(row, len(need), have, comp_rows[-1][3]))
    if len(complete) != len(rl.ROWS):
        say("\n  INCOMPLETE: analysis refused (D3). Rows not complete: {}".format(
            ",".join(r for r in rl.ROWS if r not in complete)))
        say("  No output folder is created and no statistic is computed. Exit 7.")
        sys.exit(7)

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(OUTROOT, "rerun-analysis-{}".format(stamp))
    os.makedirs(outdir)
    write_csv(outdir, "analysis_params.csv", ["name", "value"],
              [["rerun_analysis_sha256", me], ["plan", a.plan_from], ["plan_sha256", plan_sha],
               ["runs", ";".join(a.runs)], ["reproduce", a.reproduce], ["B", B],
               ["python", platform.python_version()], ["numpy", np.__version__], ["workers", a.workers]] +
              [[k, v] for k, v in sorted(hs.items())])
    write_csv(outdir, "analysis_completeness.csv", ["row", "realizations", "present", "status"], comp_rows)
    say("  run dir {}".format(outdir))

    results = {}
    cell_rows, cflags = [], []
    onset_rows, onset_rows_cal, audit_rows, r2_rows = [], [], [], []
    margin_rows, guard_rows = [], []
    ctx = Ctx(dict((row, by_row[row]) for row in complete), results, real)
    st = Stats()

    def write_all(adq, split_rows, repro_rows):
        write_csv(outdir, "analysis_cells.csv", CCOLS, cell_rows)
        write_csv(outdir, "analysis_margin.csv", ["name", "value"], margin_rows)
        write_csv(outdir, "analysis_stats.csv", STAT_COLS, st.rows)
        write_csv(outdir, "analysis_onsets.csv", ONSET_COLS, onset_rows)
        write_csv(outdir, "analysis_onsets_calibrated.csv", ONSET_COLS, onset_rows_cal)
        write_csv(outdir, "analysis_margin_calibrated.csv", ["name", "value"], guard_rows)
        write_csv(outdir, "analysis_audit.csv", AUDIT_COLS, audit_rows)
        write_csv(outdir, "analysis_r2.csv", R2_COLS, r2_rows)
        write_csv(outdir, "analysis_adequacy.csv", ADQ_COLS, adq)
        write_csv(outdir, "analysis_adequacy_split.csv", ["row", "category", "cells"], split_rows)
        write_csv(outdir, "analysis_reproduction.csv", ["file", "verdict", "old_rows", "new_rows", "differences"],
                  repro_rows)

    # ================= the seventeen rows =================
    hdr("PHASE 1  the seventeen rows: per-cell S-slope, S-curve, intervals, rate verdict (items 0 to 4)")
    inst = phase1(BASE_ROWS, by_row, real, a.workers, results)
    cell_records(inst, results, real, cell_rows, cflags)
    say("\n  curvature (regime rows): mean of per-realization regime.fit_curv values (L3); the archive")
    say("  fitted the mean curve (regime.py line 362). No straightness verdict.")

    hdr("PHASE 2  margin (5b), before any gap; pool {}".format(",".join(MARGIN_ROWS)))
    sds = arm_sds(MARGIN_ROWS, by_row, results)
    allsd = np.array([v[1] for v in sds.values()])
    S = float(np.nanmedian(allsd))
    gm = {}
    for gname, grows in (("calprec2", CALGROUP), ("probe", PROBEGROUP)):
        v = np.array([sd for (bk, df), (row, sd) in sds.items() if row in grows])
        gm[gname] = float(np.nanmedian(v))
        say("  group {:<9} rows {:<18} cell arms {:>4}  median SD {:.6f}".format(
            gname, ",".join(grows), v.size, gm[gname]))
    ratio = max(gm.values()) / min(gm.values())
    st.margin = K_TOL * S
    revisit = ratio > REVISIT_RATIO
    say("  S = median over {} cell arms = {:.6f};  m = 3 x S = {:.6f}".format(allsd.size, S, st.margin))
    say("  group ratio {:.4f}  {}".format(ratio, "MARGIN REVISIT REQUIRED" if revisit else
                                          "no revisit (ratio <= 1.5)"))
    margin_rows.extend([["S", S], ["m", st.margin], ["median_calprec2", gm["calprec2"]],
                        ["median_probe", gm["probe"]], ["ratio", ratio],
                        ["verdict", "MARGIN REVISIT REQUIRED" if revisit else "no revisit"],
                        ["cell_arms", allsd.size]])
    base_cal = [r for r in rl.CALROWS if r in BASE_ROWS]
    mrec, mdiff = compare_old(a.reproduce, old_rels, {"analysis_margin.csv": (["name", "value"], margin_rows)},
                              ["analysis_margin.csv"])
    if mdiff:
        say("\n  17-ROW REPRODUCTION FAILED at the margin (CAL4):")
        for d_ in mdiff[:REPRO_SHOW]:
            say("    {}  {}  {}  old {!r}  new {!r}".format(*d_))
        say("  No gap is computed. A mismatch is a finding, not something to patch. Exit {}.".format(EXIT_REPRO))
        write_all(adequacy_rows(cells, base_cal), [], mrec)
        say("\n  files {}".format(outdir))
        sys.exit(EXIT_REPRO)
    say("  margin equals {}'s analysis_margin.csv, every value as a string (CAL4)".format(a.reproduce))
    if revisit:
        say("\n  MARGIN REVISIT REQUIRED: no gap computed, no verdict for the paired rows. Exit 6.")
        write_all(adequacy_rows(cells, base_cal), [], [])
        sys.exit(6)

    hdr("PHASE 3  the seventeen rows: contrasts, coefficients, onsets, audit (items 6 to 8)")
    for row in ("CONC", "PROBEARM", "TAU8", "GEOM"):
        conc_like(ctx, st, row)
        audit_block(ctx, st, row, audit_rows)
    for row in MARGIN_ROWS:
        paired_gaps(ctx, st, row)
    for row in ("SIGMA", "ANISO", "RMAP"):
        target_contrast_paired(ctx, st, row)
    sigma_a2(ctx, st)
    rmap_panel(ctx, st, "RMAP", "ONSET")
    onset_block(ctx, st, onset_rows, "ONSET")
    refsize_block(ctx, st)
    r2_blocks(ctx, complete, r2_rows)

    # ================= CAL4: the reproduction check =================
    hdr("CAL4  the seventeen rows against {} (every value, as a string)".format(a.reproduce))
    adq17 = adequacy_rows(cells, base_cal)
    tables = {"analysis_completeness.csv": (["row", "realizations", "present", "status"],
                                            [r for r in comp_rows if r[0] in BASE_ROWS]),
              "analysis_cells.csv": (CCOLS, cell_rows),
              "analysis_margin.csv": (["name", "value"], margin_rows),
              "analysis_stats.csv": (STAT_COLS, st.rows),
              "analysis_onsets.csv": (ONSET_COLS, onset_rows),
              "analysis_audit.csv": (AUDIT_COLS, audit_rows),
              "analysis_r2.csv": (R2_COLS, r2_rows),
              "analysis_adequacy.csv": (ADQ_COLS, adq17)}
    repro_rows, diffs = compare_old(a.reproduce, old_rels, tables)
    for r in repro_rows:
        say("  {:<28} {}  old rows {:>6}  new rows {:>6}  differences {}".format(*r))
    if diffs:
        say("\n  17-ROW REPRODUCTION FAILED: {} difference(s); the first {}:".format(len(diffs), REPRO_SHOW))
        for d_ in diffs[:REPRO_SHOW]:
            say("    {}  {}  {}  old {!r}  new {!r}".format(*d_))
        say("  Nothing is computed for the calibrated r rows. The seventeen-row files are written for")
        say("  inspection. A mismatch is a finding, not something to patch. Exit {}.".format(EXIT_REPRO))
        write_all(adq17, [], repro_rows)
        say("\n  files {}".format(outdir))
        sys.exit(EXIT_REPRO)
    say("\n  17-ROW REPRODUCTION PASS: {} files, every value of every old column equal as a string".format(
        len(repro_rows)))

    # ================= the calibrated r rows =================
    hdr("PHASE 1  calibrated r rows {}: per-cell statistics".format(",".join(CALR_ROWS)))
    inst = phase1(CALR_ROWS, by_row, real, a.workers, results)
    cell_records(inst, results, real, cell_rows, cflags)

    pool_na = na_flag([c for row in MARGIN_ROWS for c in by_row[row]])
    guard_rows.append(["not_adequate_in_margin_pool", pool_na])
    say("  margin pool cells not adequate (CAL3; S and m unchanged): {}".format(pool_na or "none"))

    hdr("CAL1  ratio guard for the calibrated r rows, before any of their gaps; m stays {:.6f}".format(st.margin))
    csds = arm_sds(CALR_ROWS, by_row, results)
    cv = np.array([v[1] for v in csds.values()])
    cmed = float(np.nanmedian(cv))
    r_cal = max(cmed, gm["calprec2"]) / min(cmed, gm["calprec2"])
    r_probe = max(cmed, gm["probe"]) / min(cmed, gm["probe"])
    undefined = not (np.isfinite(r_cal) and np.isfinite(r_probe))
    crevisit = undefined or r_cal > REVISIT_RATIO or r_probe > REVISIT_RATIO
    if undefined:
        say("  a ratio is undefined (median {!r}): treated as REVISIT".format(cmed))
    say("  calibrated r rows: cell arms {}  median SD {:.6f}".format(cv.size, cmed))
    say("  ratio to calprec2 group ({:.6f}) {:.4f};  ratio to probe group ({:.6f}) {:.4f}".format(
        gm["calprec2"], r_cal, gm["probe"], r_probe))
    say("  {}".format("MARGIN REVISIT REQUIRED (calibrated r rows)" if crevisit else
                      "no revisit (both ratios <= 1.5)"))
    guard_rows.extend([["median_calibrated_r", cmed], ["cell_arms_calibrated_r", cv.size],
                        ["not_adequate_in_calibrated_r_pool", na_flag([c for row in CALR_ROWS for c in by_row[row]])],
                        ["ratio_calibrated_r_to_calprec2", r_cal], ["ratio_calibrated_r_to_probe", r_probe],
                        ["verdict_calibrated_r",
                         "MARGIN REVISIT REQUIRED (calibrated r rows)" if crevisit else "no revisit"]])

    if not crevisit:
        hdr("PHASE 3  calibrated r rows: the base rows' quantities, mirrored (CAL2)")
        for row in CALR_ROWS:
            paired_gaps(ctx, st, row)
        target_contrast_paired(ctx, st, "RMAP-CAL")
        rmap_panel(ctx, st, "RMAP-CAL", "ONSET-CAL")
        onset_block(ctx, st, onset_rows_cal, "ONSET-CAL")
        say("\n  No quantity compares a probe row with its calibrated row (CAL2; N40).")

    # ---------------- reference adequacy and CAL5 ----------------
    hdr("REFERENCE ADEQUACY  calprec2 per calibration cell, as measured, no pooled verdict")
    adq = adequacy_rows(cells, rl.CALROWS)
    for rec in adq:
        say("  {:<10} {:<11} d={:<3} {:<8} tau0={:<5} {:<24} C5m {} D1 {} 64M {} 256M {}".format(
            rec["module"], rec["objective"], rec["d"], rec["law"], rec["tau0"], rec["label"][:24], rec["C5m"],
            rec["D1"], rec["med_64M"], rec["med_256M"]))
    hdr("CAL5  calibration cells per calibrated row, by label and provenance")
    split_rows = []
    for row in rl.CALROWS:
        cnt = {}
        seen = set()
        for c in by_row[row]:
            k = rl.calprec2_key(c)
            if k in seen:
                continue
            seen.add(k)
            cat = split_category(c["plan_row"])
            cnt[cat] = cnt.get(cat, 0) + 1
        for cat in sorted(cnt):
            split_rows.append([row, cat, cnt[cat]])
            say("  {:<10} {:<72} {:>4}".format(row, cat, cnt[cat]))

    write_all(adq, split_rows, repro_rows)
    if crevisit:
        say("\n  MARGIN REVISIT REQUIRED (calibrated r rows): no phase-3 statistic for {}. Exit 6.".format(
            ",".join(CALR_ROWS)))
        say("\n  files {}".format(outdir))
        sys.exit(6)
    say("\n  Not computed (L1): cliff (i) and (ii), regimemap 'map informative', partm P-M3.")
    say("  No contrast in ADAPT, LAWPANEL, HORIZON, SYNTH, NAMED, BETA-ISO, BETA-ANI; CLIFF and CLIFF-CAL")
    say("  have contrast 3 only. No round-1 interval is reused or compared.")

    hdr("SUMMARY")
    say("  rows analysed: {}".format(",".join(complete)))
    say("  statistics written: {} ({} in the seventeen rows)".format(
        len(st.rows), sum(1 for r in st.rows if r["row"] in BASE_ROWS)))
    say("  statistics naming a not-adequate cell: {}".format(sum(1 for r in st.rows if r["not_adequate"])))
    for f in cflags + st.flags:
        say("  FLAG {}".format(f))
    if not (cflags or st.flags):
        say("  no FLAG")
    say("  wall {:.1f} s   peak RSS (main process) {:.1f} MB".format(
        time.time() - t_start, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0))
    say("\n  files {}".format(outdir))
    sys.exit(0)


if __name__ == "__main__":
    main()
