# CBO-GAP analysis criteria: draft for decision

Written 2026-10-15, while calprec2 long shard 6 of 26 is running. Nothing in
this file is decided. It sets out six open items for the rerun analysis. For
each it gives what the submitted manuscript did, what the referee asked, what
the archive can and cannot support, the options and their consequences, and
what cannot be decided without a measurement. Rahul chooses. His choices then
become the pre-specified criteria of the rerun analysis script. Each goes
into that script's docstring with a worked numerical example (CLAUDE.md
rule 5) before the first rerun number exists.

No option here is recommended. Where an option repeats an archived
convention, that is said so the provenance is visible. It is not an
endorsement.

Sources, all read for this draft:

- the archived scripts in zenodo-v1/, cited as file and line;
- manuscript/sn-article.tex (the submitted text), cited as "tex" and line;
- referee/JOGO_report.pdf, points 6 and 9;
- notes/DEFECT_LEDGER.md, notes/REFEREE_RESPONSE.md, notes/RERUN_PLAN.md,
  notes/CALPREC_V2_SPEC.md and notes/SESSION_STATE.md.

Numbers below are copied from those files. No number here was computed for
this draft, except grid counts read off the archived J grids (marked "grid
arithmetic").

Row names follow notes/RERUN_PLAN.md and the costprobe2 projection:
BETA-ISO, BETA-ANI, LAWPANEL, CONC, PROBEARM, ADAPT, TAU8, REFSIZE, SYNTH,
NAMED, HORIZON, GEOM, SIGMA, ANISO, RMAP, CLIFF, ONSET.

---

## 0. Found while reading for this draft (not yet in the ledger)

These came up while I read the archive for items 1 to 6. They bear on the
choices below. I have not added them to the ledger. Whether they become
ledger entries is Rahul's decision.

### 0.1 Several reported intervals have no generating code in the archive

- tex 309 says: "every interval reported in this paper is the 4,000-resample
  value emitted by the single archived re-analysis script". The only
  archived re-analysis script at 4000 resamples that covers more than one
  claim is reboot.py. It reads only regimemap_D_real.csv and
  regimemap_M_real.csv (reboot.py docstring and main, lines 285-305). It covers
  the paired gaps, severity trends, onset intervals and b3 of Sections 7.12
  and 7.15, and nothing else.
- Table 3's upper block (tex 363-370), the Section 7.3 regression b_d,
  b_tau, b_dtau (tex 392) and the pairwise target contrasts (tex 394) are
  fitted on J >= 1/tau_0 with the twelve objective-law combinations as the
  bootstrap unit. I searched every .py file in zenodo-v1/. J >= 1/tau_0
  appears in code only in perjcal.py line 168, which is a different
  experiment, and rmapj.py uses J >= 20 (line 193). exactcal.py fits every
  slope on the full grid (lines 266 and 315) and bootstraps pooled
  realizations, not twelve units (lines 352-372). No archived script
  computes those numbers.
- The 0.0260 "bootstrap slope-SE reference scale" (tex 78, median over 420
  cells with per-realization slopes) also has no generating code in the
  archive. The constant 0.026 appears only in rmapj.py lines 51 and 254, as
  an input. The 0.0219 delta-method floor is computed by audit.py, section
  A1.
- I do not know what code produced these numbers. A search of Rahul's
  machine for the round-1 working directory would settle it. This matters
  for items 3 and 4: 0.0260 underlies the rmapj P-R3 rule and the stated
  basis of the 0.05 equivalence margin (item 5).

### 0.2 The isotropic and anisotropic arms never shared seeds

- tex 650 says "Paired on the shared realization index". regimemap.py's
  paired_ci (lines 260-271) and reboot.py's paired_gaps pair the two arms
  by realization index. audit.py's docstring says the crossed.py arms
  "shared seeds".
- They did not. In regimemap.py (diffusion loop line 367, counter line
  375), crossed.py (327, 334), sigma.py (311, 318) and cliff.py (315, 322),
  the diffusion loop is outside the seed counter. So realization k of the
  isotropic arm and realization k of the anisotropic arm received
  different seeds.
- The archived seeds confirm it. In rmapj_real.csv, ackley, d = 5,
  r = 0.75, rep 0 has seed 20260830 for isotropic and 20261910 for
  anisotropic.
- So the "paired" intervals pair independent realizations by position. As
  far as I can see this does not make the intervals wrong for a difference
  of means with equal counts, but the pairing gave no common-random-number
  benefit and the word is wrong. I have not checked this numerically.
- control.py does share seeds between its fixed and adaptive arms (line
  345, "same seed s in both arms").
- Consequence for the rerun: whether iso and aniso share a seed key is a
  design choice of the rerun script, and it has not been made. See items 3
  and 5.

### 0.3 Two archived criteria carry errors already named in supplement S3

- boundary.py tests monotonicity with a fixed tolerance of 0.02 (line 373:
  "np.all(diffs >= -0.02)"). law.py's docstring names this error: "the
  previous phase set a monotonicity tolerance of 0.02 against a measured
  floor of 0.055 and the test could not have passed".
- control.py criterion (iii), "mean slope within 0.15 of -1" (docstring and
  line 313), is two-sided for a one-sided bound.
- exactcal.py P-E2 bootstraps the absolute value of the d = 2 to d = 40
  change (lines 365-369, "abs(...)"). perjcal.py P-C2 does the same (lines
  235-239). A percentile interval of an absolute value cannot extend below zero
  and is biased away from it when the true change is near zero.
- None of these should be inherited by default. Item 4 lists them.

---

## A choice that comes before items 1 to 6: the per-cell slope

The archive uses two different per-cell slopes. Every item below depends on
which one the rerun reports.

- S-mean-curve. Average E_J over the realizations of a cell at each J, then
  fit one slope to the averaged curve. The bootstrap resamples
  realizations, re-averages and refits. Used by mechanism, control,
  boundary, sigma, crossed, cliff, regime, law and visibility (each script's
  boot_ci; for example sigma.py lines 218-230).
- S-mean-slope. Fit a slope within each realization, then average the
  slopes. The bootstrap resamples per-realization slopes. Used by regimemap
  (boot_ci lines 250-257; one_realisation lines 237-238), and therefore by
  partm, reboot and rmapj, and by exactcal P-E2 and perjcal P-C2.

These are different estimands. The log of a mean is not the mean of the
logs, and a single realization's curve is noisier than the averaged one.
The manuscript reports both without distinguishing them: Table 5 and the
Section 7.10 and 7.11 counts are S-mean-curve, while Table 7, Table 9 and
the Section 7.15 counts are S-mean-slope.

Options:

- S0a. S-mean-curve everywhere.
- S0b. S-mean-slope everywhere.
- S0c. One declared primary, the other reported alongside.

Consequence: under S0a, the RMAP and ONSET reruns are not on the same
estimand as Tables 7 and 9 of the submitted paper. Under S0b, the same holds
for every other row. The rerun files store E_J per realization (RERUN_PLAN,
"What every rerun row archives"), so either can be computed later. The
choice must still be fixed before the first number.

Not decidable from the archive: how far the two differ under fixed calprec
betas. exactcal_real.csv and rmapj_real.csv store E_J per realization, so an
analysis-only script could measure the gap on archived data (random-beta and
probe-beta designs respectively) as a proxy.

---

## Item 1. The interval level and its sign (referee point 9)

### What the manuscript did

- tex 66: a cell is rate-consistent at tolerance 0.15 "when the upper end of
  a bootstrap 95% interval for gamma-hat is at most -0.85".
- tex 421 (Table 5 caption): "the one-sided reading of a one-sided bound".
- tex 309: "bootstrap percentile interval"; Bonferroni-adjusted intervals
  "reported alongside"; equivalence "by two one-sided tests at a margin of
  0.05".
- Table 9 header "95% CI" (tex 605). The scripts print "bootstrap 95% upper
  bound" (for example crossed.py line 268).

### What the code computes

- Rate-consistency verdict: boot_ci(level=95.0) sets lo = 2.5 and returns
  the 2.5th and 97.5th percentiles. The verdict compares the 97.5th
  percentile with -0.85. Same construction in mechanism.py 259-268,
  control.py 268-277, boundary.py 222-231, sigma.py 218-230, crossed.py
  221-231, cliff.py 227-237, regime.py 300-309, law.py 493-502,
  visibility.py 262-273 and regimemap.py 250-257.
- Bonferroni: bonf = 100 (1 - 0.05/nb) (sigma.py 342, crossed.py 359,
  cliff.py 347, regimemap.py 408), passed as the two-sided level. The upper
  end is therefore the 100 - 2.5/nb percentile.
- Estimation intervals, two-sided 2.5/97.5: exactcal.py 369, perjcal.py
  240, partm.py 306, reboot.py (trends, onset, b3), rmapj.py (trend),
  finitej.py 227, audit.py A2 and A4.
- Equivalence intervals, two-sided 90% (5th and 95th percentiles): audit.py
  A3 (line 259), regimemap.py paired_ci (level 90.0), reboot.py
  paired_gaps.
- visibility.py and regime.py use the same 97.5th-percentile upper end for
  their verdicts (ledger R9).

### What the referee asked

"If the reported percentile interval is the usual two-sided 95% interval,
its upper endpoint corresponds to the 97.5th percentile rather than a 95%
one-sided limit. This may simply make the criterion more conservative, but
the actual confidence level and construction should be stated
consistently."

### The sign

The theory gives an upper bound on the error, of order J^-1. Decay faster
than J^-1 is consistent with it. So the criterion is one-sided, and its tail
depends on the convention fixed under referee point 8:

- slope convention, E_J ~ C J^gamma with benchmark gamma = -1: the
  criterion is on the UPPER tail of gamma-hat, "upper bound <= -1 + tol";
- exponent convention, E_J ~ C J^-gamma with benchmark gamma = 1: the
  criterion is on the LOWER tail, "lower bound >= 1 - tol";
- deficit convention, Delta = -1 - gamma-hat (tex 66): the criterion is on
  the LOWER tail of Delta, "lower bound >= -tol". law.py line 122 writes
  TOL = -0.15 in exactly this sense.

The three are the same rule. The point-8 choice decides which sentence the
paper writes. The sign-inversion incident in CLAUDE.md ("Severity defined as
gamma(r1) - gamma(r2) in the text while the reported numbers were
gamma(r2) - gamma(r1)") is why the tail must be named in the docstring with a
worked example in the chosen convention.

### Options for the verdict level

- 1A. Keep the archived construction and name it: a one-sided upper
  confidence bound at nominal level 97.5%, the 97.5th percentile of the
  bootstrap distribution.
  - No archived verdict changes.
  - Every "95% interval", "95% upper bound" and "95% CI" in the text and
    captions that refers to the verdict is rewritten.
  - Bonferroni is restated as one-sided at nominal 1 - 0.025/nb.
  - Archived and rerun counts are then on the same level.
- 1B. Redefine the criterion as a one-sided 95% bound, the 95th
  percentile.
  - For the same resamples the 95th percentile is never above the 97.5th,
    so a cell's verdict can only move from fail to pass. Every count at 1B
    is at least the count at 1A.
  - Archived verdicts from the per-(cell, J) files (Tables 4 and 5, the
    7.10 and 7.11 counts, the 7.5 counts) cannot be recomputed at 95%
    (ARC2). In the supplement they stay at 97.5% and are labelled so.
  - An archive-versus-rerun comparison of counts then mixes two levels
    unless the rerun also reports 97.5%.
- 1C. Report both, one declared primary before the run.
  - Two counts per row. The secondary is a sensitivity, not a choice made
    after seeing which is better.
- 1D. Drop per-cell pass/fail verdicts as headline quantities. Report each
  cell's slope with its interval, and give counts only as descriptive
  sensitivity at all three tolerances.
  - This changes what the paper claims, not only how it labels it.

### Separate sub-decisions

The verdict level does not settle these:

- 1(ii). The level of two-sided estimation intervals: contrasts, trends,
  regression coefficients, breakpoints. Archived: 95%, 2.5/97.5. A verdict
  level under 1B does not force these to change.
- 1(iii). The TOST level for equivalence. Archived: a 90% two-sided
  interval, that is two one-sided tests at 5% each, which is the standard
  correspondence. Changing 1(ii) does not change this unless chosen.
- 1(iv). Whether a Bonferroni family is reported, and over what: the
  archive used every cell in one script's run (nb = len(agg)). A rerun
  row's family size differs from the archived script's when rows are
  split or merged.

### What each option implies for claims that cite an interval today

| Claim (tex line) | Producing code | Interval as computed | Recomputable from archive at another level? |
|---|---|---|---|
| Rate-consistency counts, Table 4 (control) | control.py boot_ci | 97.5th pct, 400 | No (per (cell, J) means; ARC2) |
| Table 5 and Fig. 1 (boundary), tex 421 | boundary.py | 97.5th pct, 400 | No |
| 7.10 counts 71/93/115 and 57/77/86 (tex 491) | sigma.py | 97.5th pct, 400; Bonferroni | No |
| 7.11 counts (crossed) | crossed.py | 97.5th pct, 400; Bonferroni | No |
| 7.5 synthetic and named counts; 7.6 reference-size intervals | regime.py | 2.5/97.5, 400 | No (per cell only) |
| 7.9 rate-consistency in the law fit | law.py | 97.5th pct, 400 | No (per cell only) |
| N_vis (7.2) | visibility.py | 97.5th pct, 400 | No |
| 7.12 counts and Table 7 (tex 549) | regimemap.py, Part M | 97.5th pct of S-mean-slope, 400 | Yes, from regimemap_M_real.csv (slopes only, no refit on another window) |
| 7.15 counts (tex 652); three failing admissible cells (tex 547) | regimemap.py, Part D | 97.5th pct of S-mean-slope, 400 | Yes, from regimemap_D_real.csv or rmapj_real.csv |
| Trend +0.144 [+0.123,+0.164] and anisotropic (tex 38, 648) | reboot.py, rmapj.py | two-sided 95%, 4000 | Yes |
| b3 intervals (tex 545) | partm.py, reboot.py | two-sided 95%, 4000 | Yes |
| Onset intervals, "nine of ten" (tex 38, 628) | reboot.py (4000), regimemap.py (300) | two-sided 95% | Yes |
| Paired gaps and equivalence, 7.15 (tex 650) | reboot.py, regimemap.py | 90%, 4000 and 1000 | Yes (but see 0.2) |
| 7.11 "3 of 18 equivalent" (tex 497) | audit.py A3 | 90%, 2000, four objectives as units, unpaired | Only by audit.py's own unit |
| r-coefficients at d = 10 (tex 487) | audit.py A2 | two-sided 95%, 500, objectives as units | Same |
| Table 3, 7.3 regression, pairwise contrasts (tex 363-394) | no archived code (0.1) | stated two-sided 95% | From exactcal_real.csv only by new code |
| Residual 0.253 [0.117,0.381] (tex 563) | caption says the Table 3 unit; exactcal.py P-E2 uses a different one | two-sided 95% | From exactcal_real.csv by new code |
| 22 of 30 intervals (tex 587) | finitej.py | two-sided 95%, 4000 | Yes |
| perjcal change intervals (tex 593) | perjcal.py | two-sided 95%, 4000, objectives as units, abs value | Yes, from perjcal_real.csv |

Under the agreed scope these claims are either rerun (main text) or kept in
the supplement under their archived construction. So for the archive the
consequence of item 1 is labelling. For the rerun it is the criterion itself.

### What cannot be decided from the archive alone

The actual coverage of a percentile bootstrap bound at 12 to 15
realizations per cell, for this statistic, is not known. The manuscript
itself says "with 12 realizations in the smallest cells their tails are
coarse" (tex 309). Whether nominal 97.5% or 95% is near the real level
would need a coverage measurement: a simulation with known truth, or
repeated cells. Without it, any stated level is nominal and should be called
so.

---

## Item 2. The fit window for the slope, per rerun row

### What each archived script actually used, read from its source

Every script caps the grid at J <= J_inf/10 (for example mechanism.py line
300, "J_list = [J for J in J_list if J <= Jinf // 10]"). The rest of the
window is as follows.

| Row | Archived script | Window in the source | tau_0 values in the row |
|---|---|---|---|
| BETA-ISO, BETA-ANI | ess_surface.py | full J10 (lines 242, 248); point slope only, no bootstrap (341) | none (design beta) |
| LAWPANEL | visibility.py | full 19-size grid 10 to 5000 (322-329) for slope and verdict (408-410); N_vis fits every suffix J >= J0 with at least 4 points (276-286) | none (B rule) |
| CONC | mechanism.py | full J10 (300, 372-374) | 0.5, 0.1, 0.01 |
| CONC (EXP-CAL record) | exactcal.py | full J10 per realization (266, 315); fit_slope has no finite mask (228-232) | 0.5, 0.1, 0.01 |
| CONC, Table 3 upper block | none archived (0.1) | J >= 1/tau_0 per the text (tex 363, 368) | 0.5, 0.1, 0.01 |
| PROBEARM | new row; mechanism's design | not yet defined | 0.5, 0.1, 0.01 nominal |
| ADAPT | control.py | full J10 (303, 373-375) | 0.1, 0.01 |
| TAU8 | boundary.py | full J10 (259, 328-330) | 0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01 |
| REFSIZE | regime.py Part A | common cap J <= min(J_inf)/10 = 1250 (515-516; cell_summary 355-361) | 0.1 |
| SYNTH, NAMED, HORIZON | regime.py | full J10b (329, 361) | 0.1, 0.01 (HORIZON 0.1) |
| GEOM | law.py | full J10b (527, 576-578) | the eight TAU8 values |
| SIGMA | sigma.py | full J10 (258, 346-349) | 0.1, 0.01 |
| ANISO | crossed.py | full J10 (259) | 0.1, 0.01 |
| RMAP | regimemap.py Part M | full J10, per realization (303, 237-238) | 0.5, 0.1, 0.03, 0.01 |
| CLIFF | cliff.py | full J10 (265, 351-354) | 0.1 |
| ONSET | regimemap.py Part D; rmapj.py | full J10; rmapj also refits on J >= 20 (193) and reports the restricted window only if the trend moves by more than 0.026 (P-R3, line 254) | 0.1 |
| PERJ (not rerun, F4) | perjcal.py | J >= 1/tau_0 (168) | 0.5, 0.01 |

Also recorded: audit.py A5 printed a window sensitivity grid (J_min in {10,
20, 40, 80}, J_max in {1280, 2560, 5000}) on mechanism_raw.csv, centred law,
tau_0 = 0.1 only. tex 352 reports its spread as 0.037 and says "This was not
tested at tighter targets".

### What the referee asked

Point 4 asks that the fixed-beta experiment decide what survives of the
finite-J contrasts. No referee point prescribes a window. The window enters
through the attainability argument of tex 390: a target tau_0 is attainable
only when J >= 1/tau_0.

### Options

- 2A. Full grid, J <= J_inf/10, as every archived trajectory script used.
  At tau_0 = 0.01, four of the ten J10 sizes (10 to 80) lie where the
  target is arithmetically unattainable (tex 390).
- 2B. J >= 1/tau_0, non-strict, as perjcal.py and the Table 3 text.
- 2C. J > 1/tau_0, strict, as rmapj.py's J >= 20 at tau_0 = 0.1. tex 624
  explains it: at J = 1/tau_0 the target is reached only when ESS equals
  one.
- 2D. J > 4(1/tau - 1), the range on which the manuscript's own
  discarded-event bound is non-vacuous (tex 255). Here tau is the
  population 1/rho_beta. This option rests on that corollary, which must be
  proved line by line (CLAUDE.md rule 10) before it can be used.
- 2E. A per-realization window from the realized ESS_0(J)/J the rerun
  stores (F7). The window would then differ across realizations of one
  cell, and slopes fitted on different J sets would be averaged.
- 2F. Two windows, one declared primary, with a pre-specified rule for
  which is reported. rmapj P-R3 is a precedent: the threshold there was
  0.026, which has no archived source (0.1).
- 2G. One common window for every tau_0 in a row, set by that row's
  tightest tau_0. For example, J >= 100 everywhere in CONC.

Retained J10 sizes under 2B and 2C (grid arithmetic; J10b gives the same
counts):

| tau_0 | 1/tau_0 | 2B | 2C |
|---|---|---|---|
| 0.5, 0.3, 0.2 | 2, 3.3, 5 | 10 (all) | 10 (all) |
| 0.1 | 10 | 10 (10 to 5000) | 9 (20 to 5000) |
| 0.07 | 14.3 | 9 | 9 |
| 0.05 | 20 | 9 (20 to 5000) | 8 (40 to 5000) |
| 0.03 | 33.3 | 8 | 8 |
| 0.02 | 50 | 7 | 7 |
| 0.01 | 100 | 6 (160 to 5000) | 6 |

So 2B and 2C differ only at tau_0 = 0.1 and 0.05, where 1/tau_0 is a grid
point. Under 2D at tau_0 = 0.01, four J10 sizes remain (640 to 5000).
Every archived fit_slope requires at least 3 finite points.

### Consequences common to 2B to 2E

- The window differs across tau_0. A contrast across tau_0 (CONC's three
  targets, TAU8's eight, RMAP's four) then compares slopes fitted on
  different J ranges, so window and target are confounded. The Table 3
  upper block did exactly this. 2G removes it at the cost of discarding
  attainable points at loose targets.
- Which tau? Nominal tau_0, or the calibrated tau_ref from calprec2?
  - Cells labelled "beta" (labels BA and O2, CALPREC_V2_SPEC section 11c)
    by construction do not sit at their nominal target. For example, N19
    records sphere's exact tau(beta) = 0.011213257 at nominal 0.01.
  - PROBEARM, and the probe-calibrated rows (ADAPT, REFSIZE, SYNTH, NAMED,
    HORIZON, GEOM, RMAP, CLIFF, ONSET), run at nominal tau_0 with an
    achieved concentration that differs per cell (exactcal.py docstring:
    the archived achieved/target range at 0.01 was [0.106, 1.363]).
  - Whether a measured tau moves 1/tau across a grid point can be read
    from calprec2's output once finalize has run. I have not computed it.
- Rows with no tau_0 (BETA-ISO, BETA-ANI, LAWPANEL) have no 1/tau_0 window.
  They need their own rule, or the full grid.
- The upper end. All archived windows end at J_inf/10. REFSIZE caps at
  1250 so that four reference sizes share a grid. That is also a choice,
  and it stays open unless confirmed.

### What cannot be decided from the archive alone

Whether the fitted slope under fixed calprec betas is window-sensitive at
tight targets. The only archived sensitivity check is at tau_0 = 0.1, on
probe-calibrated cell means (audit A5). An analysis-only script on
exactcal_real.csv (per realization, per J, random beta) and rmapj_real.csv
(probe beta, tau_0 = 0.1) could measure window sensitivity on archived data
as a proxy. The rerun answers it only after its numbers exist, which is too
late to choose the window from it.

---

## Item 3. The bootstrap: unit, resamples, stratification

### What the manuscript did

- tex 309: "The bootstrap resampling unit is the independent coupled
  realization ... bootstrap percentile interval, fixed seed. The simulation
  scripts use 400 resamples; every interval reported ... is recomputed ...
  at 4,000 resamples."
- Table 3 caption (tex 363): twelve objective-law combinations as the unit.
- tex 593: "the pre-specified objective unit" for perjcal.
- tex 545 and 648: "(objective, realization)" pairs, resampled jointly.

### What the archive actually used

| Construction | Where | Resamples | Seed |
|---|---|---|---|
| Realizations within one cell, S-mean-curve refit | mechanism, control, boundary, sigma, crossed, cliff, regime, law, visibility | 400 | 7, the same for every cell |
| Per-realization slopes within one cell, S-mean-slope | regimemap.py boot_ci | 400 | 7 |
| "Paired" iso/aniso by index, slopes pooled over 3 objectives | regimemap.py paired_ci | 1000 | 7 |
| (objective, rep) keys resampled jointly across a panel | partm.py, reboot.py, rmapj.py trend | 4000 | 20260821, 20260822, 20260827 |
| Pooled per-realization slopes over objectives and laws, d = 2 and d = 40 resampled independently, absolute value | exactcal.py P-E2 | 4000 | 20260822 |
| Objectives as units | perjcal.py P-C2 (4000); audit.py A2 (500), A3 (2000), A4 (400) | as listed | 20260828; 11 |
| Pooled realizations, d = 2 vs d = 40 independent | finitej.py P-F3 | 4000 | 20260824 |
| Free breakpoint, (objective, rep) pool | regimemap.py Part D | 300 | 7 |
| Twelve objective-law units | Table 3 text | not archived (0.1) | not archived |

Ledger N8 records that "every interval reported in this paper is the
4000-resample value" is false. The sentence in tex 309 claiming that the
re-analysis "was executed on two independent installations ... and the two
runs agree to four decimals" refers to output that is not archived (ARC1).

Two further facts from the code:

- Every simulation script seeds its bootstrap with 7 in every cell. With
  equal realization counts, every cell therefore resamples the identical
  index sequence, so bootstrap errors are correlated across cells.
- The boot_ci functions drop non-finite resampled slopes and return NaN if
  fewer than 20 remain (for example crossed.py lines 227-229). The rerun
  needs its own rule for this.

### What the referee asked

"For the principal numerical comparisons, uncertainty arising from the
independent simulation realizations seems more directly interpretable.
Variation across the selected objectives and initial laws can then be
reported separately as heterogeneity over the chosen test set." The
twelve-unit bootstrap is withdrawn (Rahul).

### Options: resampling unit

- 3A. Realization within cell, each cell resampled independently: a
  stratified bootstrap with the design fixed. A multi-cell statistic (a
  contrast, a trend over d, a regression over tau_0 and d) is recomputed
  from the per-cell resamples. This is REFEREE_RESPONSE 6b as drafted.
  Its interval is conditional on the chosen objectives and laws. It says
  nothing about other objectives.
- 3B. As 3A, but resampled jointly by seed key across arms that share one.
  - Applies to CONC and PROBEARM, which share keys by decision (N17).
  - Applies to ADAPT's fixed and adaptive arms, if the rerun keeps
    control.py's shared seeds.
  - Applies to iso and aniso only if the rerun keys the seed without the
    diffusion coordinate. The archive never did (0.2). This decision
    belongs to the rerun script's seed table and is open.
- 3C. (objective, realization) keys resampled jointly across a panel, as
  partm, reboot and rmapj did.
  - A resample can then contain one objective several times and another
    not at all. The interval therefore carries between-objective variation.
    That is a partial form of what referee point 6 objects to.
  - Where seeds differ across objectives, tying "rep k" across objectives
    pairs unrelated realizations.
- 3D. Objectives as units. This is withdrawn by the referee point 6
  decision and is listed only because perjcal and audit used it.

### Options: number of resamples

- 400, as in the simulation scripts. 2000, as in audit A3; reboot.py's
  docstring says the round-1 referee asked for "2000 or more". 4000, as in
  partm, reboot, rmapj, perjcal and finitej, and as the manuscript claimed.
  Or a larger fixed number.
- Or a rule: the smallest B at which the Monte Carlo error of the decision
  endpoint is below a stated fraction of the tolerance.
- Cost is negligible beside the trajectories, at any of these sizes.

### Options: bootstrap seeding

- One fixed seed for all cells (archived).
- A SeedSequence keyed by cell and statistic, written to the output as the
  simulation seeds are. With this, cells do not share resample indices.

### Options: interval method

- Percentile (archived; tex 309 says "not BCa").
- Basic, BCa or studentized. These behave differently at 12 to 15
  realizations. I do not know which is best for this statistic at that
  size. Item 1's coverage measurement would answer this as well.

### What cannot be decided from the archive alone

- The Monte Carlo error of a percentile endpoint at a given B for the
  rerun's statistic. It can be measured on archived per-realization data
  (exactcal_real.csv, rmapj_real.csv) by repeating the bootstrap with
  independent seeds. That is an analysis-only script.
- Coverage at 12 to 15 realizations (item 1).
- The variance reduction from a shared iso/aniso seed key. It would need a
  pilot with shared keys; the archive has none.

---

## Item 4. Tolerances for every comparison

### Already fixed by existing pre-specified criteria (not open)

These belong to the calibration and gate scripts. They are fixed in
docstrings that ran before their results existed:

- calprec2 (CALPREC_V2_SPEC sections 5 and 11c; N23, N28):
  - C5m: range / tau_ref <= 0.054682;
  - D1: drift <= 0.025;
  - C1: sufficiency, max |tau_ref / tau0 - 1| <= 0.05;
  - C6: |tau_ref(beta_prod) / tau0 - 1| <= 0.05;
  - BA label: "target" if |tau_ref / tau0 - 1| <= 0.05, otherwise "beta";
  - E1: relative 1e-12.
- refscale: C5 <= 0.025 and D1 <= 0.025 (N18, N21).
- detcheck: half a unit in the last stored digit (D1 to D3).

These decide which beta each cell gets and how it is labelled. They are not
analysis tolerances of the rerun, and nothing here reopens them.

### Archived analysis tolerances: open for the rerun until re-adopted

| Comparison | Archived tolerance or rule | Source | Note |
|---|---|---|---|
| Rate consistency | tolerance 0.15 (bound -0.85); counts also at 0.10 and 0.20 | every trajectory script; tex 66 | tex 66: "0.15 is arbitrary" |
| Multiplicity | Bonferroni over the script's cells, reported alongside | sigma, crossed, cliff, regimemap | family definition open (1(iv)) |
| Collapse across objectives | sd of slope across objectives <= 0.10 | mechanism.py 122; control.py 110 | a heterogeneity threshold (item 6) |
| Concentration as mechanism | adding objective identity raises R^2 by < 0.05 | mechanism.py 123 | control.py docstring: R^2 "should not have been" a criterion; S3 category |
| Control drift (adaptive arm) | drift < 0.05 log units | control.py 111 | |
| Mean slope near -1 | within 0.15 of -1 | control.py criterion (iii) | two-sided (0.3) |
| Monotonicity in tau_0 | diffs >= -0.02 | boundary.py 373 | named error (0.3) |
| Monotonicity, onset, cliff (iii) | within a noise floor measured from the run: median over cells of the slope range over the three loosest levels | law.py 589-596; cliff.py 398-407 | a rule, not a number |
| Cliff | (i) within 0.10 of the r = 0.5 value for r <= 1; (ii) at least 0.30 flatter at r = 5 | cliff.py 120-121 | |
| Map informative | range > 0.10 along each axis | regimemap.py; partm P-M1 | |
| Interaction | b3 interval excludes 0 in at least 3 of 4 panels, same sign | partm P-M2 | |
| External and boundary agreement | within 2 x 0.0219 = 0.0438 | partm P-M3, P-M4 | 0.0219 is the delta-method floor, which tex 78 says is biased downward |
| Window choice | report the restricted window if the trend shifts by > 0.026 | rmapj P-R3 | 0.026 has no archived source (0.1) |
| r has no effect of practical size | interval inside +-0.10 | audit A2 | |
| Diffusion gap rule | point-estimate gap < 0.05 at every d, and "grows with d" as d_max > d_min with no tolerance | crossed.py 114, 457-458 | no interval enters |
| Equivalence | TOST at 0.05 | audit A3, regimemap, reboot | item 5 |
| Onset differs from r = 1 | breakpoint interval excludes 1 | regimemap, reboot, audit A4 | |
| Calibration achieved | within 1% of target; P-C1 fails if > 5% of points miss | exactcal P-E1; perjcal P-C1 | random-beta designs; not used in the rerun |
| Straightness | quadratic-term interval contains 0 | regime.py | |
| Law useful | leave-one-landscape-out CV R^2 > 0.5 and held-out R^2 > 0 | law.py | |
| Visibility | N_vis, at least 4 points per suffix | visibility.py 281 | |
| Saturation | ESS >= 1.01; and abs(slope + 1) < 0.15 on point estimates | ess_surface.py 344, 375-378 | two-sided point rule |

### Which comparisons the rerun analysis makes

This list is open. It depends on which claims the new paper keeps under
REVISION_PLAN Q1 to Q3. Each kept claim needs a tolerance or an explicit
statement that it is reported without one. The candidates:

- Q1, CONC:
  - per-cell rate consistency;
  - the d = 2 to d = 40 change per tau_0 and per (objective, law);
  - a trend in d;
  - contrasts across tau_0;
  - the CONC minus PROBEARM paired difference (N17);
  - ESS_0(J)/J reported descriptively (F7).
- Q2:
  - calprec2's own criteria, which are fixed;
  - TAU8: the per-cell bracket, the universality rule and the three
    currencies of boundary.py's docstring;
  - the attainability window (item 2).
- Q3:
  - SIGMA: slope against r;
  - ANISO: the arm A and arm B gaps;
  - RMAP: map informativeness and b3;
  - CLIFF: criteria (i) to (iii);
  - ONSET: the onset interval, the severity contrasts and their trend in
    d, and the paired gaps.
- Supplement rows: two options.
  - Analyse them under the archived criteria verbatim, so they stay
    comparable with what was published, errors in 0.3 included and
    labelled.
  - Or analyse them under the new criteria, so the whole rerun is on one
    rule set but differs from the record.

### Options for how a tolerance is set

- 4A. A fixed number now, for each comparison: for example the archived
  values above, re-adopted one by one.
- 4B. A rule evaluated on the rerun's own replicates, fixed now as a rule:
  for example "k times the median realization-level bootstrap SE of the
  slope over the row's cells". law.py and cliff.py did this. The number is
  then known only after the run, but the rule is not chosen after it.
- 4C. No tolerance: the estimate and its interval are reported, and no
  verdict is drawn.

### What cannot be decided from the archive alone

The realization-level slope SE under fixed calprec betas. The two archived
scales were computed under other protocols:

- 0.0219, delta method, probe-calibrated cell means, biased downward per
  tex 78;
- 0.0260, per-realization slopes, probe-calibrated, no archived code.

Any tolerance tied to a noise scale is therefore either a number carried
over from a different design (4A) or a rule whose value appears only with
the rerun (4B). An analysis-only script on exactcal_real.csv and
rmapj_real.csv could give the realization-level SE under those two
archived designs as bracketing proxies. It would not give the value under
calprec betas.

---

## Item 5. The equivalence margin for the diffusion comparison

### What the manuscript did

- tex 309: TOST "at a margin of 0.05 fixed before the run". The basis
  given: "approximately twice the realization-level bootstrap slope-SE
  reference scale of 0.0260 and ... one third of the 0.15 rate-consistency
  tolerance ... It is not a claim that a slope difference of 0.05 is
  scientifically negligible."
- tex 497 (Section 7.11, matched sigma): "Unpaired equivalence testing at
  that margin declares 3 of the 18 cells equivalent, leaves 13
  inconclusive, and classifies 2 as lying outside".
- tex 650 (Section 7.15): paired gaps with intervals "excluding the 0.05
  margin" at several d.

### What the archive did

- audit.py A3 (lines 224-266): per (arm, level, d, tau), the gap is the
  mean over four objectives of the per-objective slope difference (cell
  slopes from crossed_summary.csv). It is bootstrapped over the four
  objectives, 2000 resamples, 90% interval. EQUIVALENT if the interval
  lies inside +-0.05; DIFFERENT if it lies wholly outside.
- regimemap.py paired_ci (260-271) and reboot.py paired_gaps: the
  per-realization slopes of three objectives are pooled (36 values per
  arm), differenced by index, bootstrapped (1000 or 4000), 90% interval,
  same rule. The index pairing is not a seed pairing (0.2).
- crossed.py's own decision rule (line 457) compares point-estimate gaps
  with 0.05. No interval enters it.
- The margin's stated basis, 0.0260, has no archived generating code
  (0.1).

### What the referee asked

No referee point addresses the margin. Point 2 asks for an unambiguous
theoretical basis for each diffusion's boundary. Point 6 asks for
realization-level uncertainty. The margin is the author's own convention.

### What theory offers

Ledger N1 records that the J^-1 exponent comes from FKR Proposition 16 and
GHV Theorem 2.6, and that neither carries a parameter condition. On that
reading, both diffusions have the same asymptotic exponent, and any
finite-window slope difference is a prefactor or pre-asymptotic effect for
which the theorems give no scale. I have not checked this against the
primary texts, which are not in the repository (CLAUDE.md rule 9). If it
holds, no margin can be derived from theory. Any margin is a declared
convention, as tex 309 already says.

### Options

- 5A. 0.05, kept as a declared convention. Its stated basis has to be
  rewritten, because 0.0260 has no archived source and was measured under
  the probe protocol.
- 5B. A stated fraction of the rate-consistency tolerance chosen in item
  4. This ties the margin to the one scale the paper already declares.
  The fraction itself is still a convention.
- 5C. A rule on the rerun's own realization-level slope SE, fixed now (as
  in 4B). The margin's value is then known only after the run.
- 5D. No equivalence claims. Report each gap with its interval, say
  whether a difference is detected, and state the largest difference the
  interval rules out. tex 648 does this for the anisotropic trend: "the
  interval bounds any trend that exists below about 0.027 per doubling".
  This makes no equivalence claim at all.

Sub-decisions that are not the margin but determine what it means:

- 5(i). The comparison unit: per cell (objective, d, level, tau), or
  aggregated over objectives as audit and regimemap did. An aggregate gap
  mixes objectives, and its heterogeneity is item 6.
- 5(ii). Pairing: whether the rerun's seed table gives iso and aniso the
  same seed key (3B). With independent arms, the 90% interval for a gap
  at 12 realizations per arm may be too wide for any cell to be declared
  equivalent at a small margin. That is a power question, and the archive
  cannot answer it for the rerun's design.
- 5(iii). Which comparisons are equivalence comparisons at all: ANISO arm A
  (matched sigma), arm B (matched r), and the ONSET and RMAP gaps. tex 497
  applies equivalence to arm A only.
- 5(iv). The TOST level (1(iii)).

### What cannot be decided from the archive alone

Whether the chosen margin is attainable at 12 realizations per arm under
calprec betas: that is, whether the half-width of the 90% interval for a
gap can be smaller than the margin. regimemap_D_real.csv and rmapj_real.csv
give the realization-level slope spread under probe betas with independent
arms. An analysis-only script could report the achieved half-widths there
as a proxy. The answer under the rerun design needs the rerun or a pilot.

---

## Item 6. The heterogeneity statistic across the chosen objectives

### What the manuscript did

- Table 3 and the 7.3 regression bootstrapped the twelve objective-law
  combinations. This is withdrawn.
- Per-objective changes were quoted as point estimates: "0.456 for Ackley,
  0.429 for Levy and 0.347 for Sphere against 0.167, 0.094 and 0.027"
  (tex 396).
- Fig. 1 shows "standard deviation across cells" (tex 659).
- mechanism.py and control.py used the sd of the slope across objectives
  with a threshold of 0.10 as the COLLAPSE criterion.

### What the referee asked

"Variation across the selected objectives and initial laws can then be
reported separately as heterogeneity over the chosen test set. If the
author intends to make an inference over a population of optimization
problems, that population and the sampling mechanism would first need to
be defined."

### The units per row

- CONC and PROBEARM: 6 objectives x 2 laws = 12 combinations.
- TAU8, ADAPT, NAMED: 6 objectives.
- SIGMA, ANISO, CLIFF: 4.
- RMAP, ONSET: 3.
- SYNTH and GEOM: designed synthetic factors (kappa, rho, omega). For
  these a regression on the generating parameters is available, as law.py
  did, so "heterogeneity" there may instead mean a fitted dependence.

### Options

- 6A. No summary statistic. Show every per-unit estimate with its
  realization-level interval (3A), plus min and max. This is fully
  descriptive and no inference is drawn beyond the units.
- 6B. The sd across units of per-unit point estimates (the archived
  COLLAPSE statistic). It mixes true between-unit spread with within-unit
  sampling noise, so it grows when realizations are few.
- 6C. Between-unit variance net of within-unit sampling variance, by
  method of moments, with the within-unit variances from the
  realization-level bootstrap, optionally with I^2.
  - Read as descriptive dispersion over the test set, not as a population
    parameter.
  - With 3 to 12 units it is imprecise, and a negative estimate is
    truncated at zero.
  - Any interval on it implies a sampling model for units, which is what
    the referee warns against.
- 6D. Cochran's Q test of homogeneity across the chosen units: a
  fixed-effects statement about these units only.
  - With many realizations it detects small differences.
  - Non-rejection is not homogeneity (CLAUDE.md rule 10).
- 6E. The range across units, with a stratified realization-level
  interval. I do not know how a percentile bootstrap of a range behaves at
  12 to 15 realizations per unit. A range of noisy means is biased upward.
  This would need checking.

Sub-decisions:

- 6(i). Which contrasts carry a heterogeneity statement: Q1 only, or every
  main contrast (including the Q3 gaps of item 5)?
- 6(ii). Whether a threshold attaches, as COLLAPSE's 0.10 did, or the
  statistic is purely descriptive.
- 6(iii). The main contrast itself: an equally weighted mean over the chosen
  units, with a stratified realization-level interval (3A), conditional on
  the test set. That is what the referee's "realization-level analysis"
  supports. It needs stating as such in the docstring.

### What cannot be decided from the archive alone

The ratio of within-unit sampling variance to between-unit spread under
fixed calprec betas. It decides whether 6C is estimable at all, and how far
6B overstates spread. exactcal_real.csv gives it under random beta, and
regimemap_M_real.csv under probe beta (slopes only). Both are proxies, and
an analysis-only script could compute them.

---

## Decisions needed from Rahul

Each answer goes into the rerun analysis docstring with a worked example
before the rerun script runs.

1. S0: the per-cell slope (S-mean-curve, S-mean-slope, or one primary).
2. Item 1:
   - the verdict level and its construction (1A to 1D);
   - the convention and tail, fixed together with referee point 8;
   - 1(ii) the estimation-interval level;
   - 1(iii) the TOST level;
   - 1(iv) the Bonferroni family.
3. Item 2:
   - the window per row (2A to 2G);
   - nominal tau_0 or calibrated tau_ref;
   - the rule for rows with no tau_0;
   - the upper cap.
4. Item 3:
   - the unit (3A to 3C);
   - the seed-key sharing between iso and aniso in the rerun seed table;
   - B or a rule for B;
   - bootstrap seeding;
   - interval method;
   - the handling of non-finite resamples.
5. Item 4:
   - the list of comparisons the new paper makes;
   - for each, a fixed number, a rule, or no tolerance (4A to 4C);
   - whether supplement rows use the archived criteria verbatim.
6. Item 5:
   - the margin and its basis (5A to 5D);
   - 5(i) the unit;
   - 5(ii) pairing;
   - 5(iii) which comparisons are equivalence comparisons.
7. Item 6:
   - the statistic (6A to 6E);
   - 6(i) its scope;
   - 6(ii) any threshold.
8. Section 0: whether 0.1, 0.2 and 0.3 become ledger entries.

## Measurements that could inform these before deciding

All of these are analysis-only, on archived per-realization files. None
evolves a trajectory. Each answers a question for a proxy design (random
beta or probe beta), not for calprec betas. None is written. Each would
need its own script, criteria and run under CLAUDE.md rules 2, 3 and 21,
if Rahul wants any of them.

- M1. The S-mean-curve against S-mean-slope gap (S0): exactcal_real.csv,
  rmapj_real.csv.
- M2. Window sensitivity at tau_0 = 0.01 and 0.1 (item 2):
  exactcal_real.csv, rmapj_real.csv.
- M3. The Monte Carlo error of percentile endpoints against B (item 3):
  the same files.
- M4. The realization-level slope SE per cell (items 4 and 5):
  exactcal_real.csv, rmapj_real.csv, regimemap_D_real.csv,
  regimemap_M_real.csv.
- M5. The achievable 90% half-width of an iso/aniso gap at 12 realizations
  with independent arms (item 5): rmapj_real.csv, regimemap_D_real.csv.
- M6. Within-unit against between-unit variance (item 6):
  exactcal_real.csv, regimemap_M_real.csv.

Coverage at 12 to 15 realizations (items 1 and 3) cannot be measured from
the archive. It needs a simulation with a known slope.

Written 2026-10-15, not executed: scripts/m1_estimands.py,
m2_window.py, m3_bootmc.py, m4_slopese.py, m5_gapwidth.py and
m6_hetero.py, with shared helpers in scripts/measlib.py. Also
scripts/m7_pairing.py (M7), which tests ledger N31's claim that the
archived "paired" diffusion intervals stand. M2 also reconstructs the
point estimates of Table 3 on the full grid and on J >= 1/tau_0 (N30), and
M4 prints three candidate reconstructions of the 0.0260 scale (N30). Each
docstring states what its result can and cannot inform. None of them
covers calprec betas.
