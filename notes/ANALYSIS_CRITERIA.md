# CBO-GAP analysis criteria for the fixed-beta rerun: decided

Status: decided by Rahul, 2026-10-16. These criteria become binding when
they are copied into the rerun script's docstring before its first
execution. Until then this file is the record of the decision, and
notes/ANALYSIS_CRITERIA_DRAFT.md is the record of the options considered.

Each item gives:
- the decision;
- the criterion as the docstring will state it;
- a worked numerical example (CLAUDE.md rule 5);
- one line naming the measurement that decided it;
- the part that measurement cannot settle, which is Rahul's judgement;
- anything still undecided, marked NOT DECIDED.

Claude wrote this file from Rahul's decision message of 2026-10-16 and
the logs below, and has decided nothing in it. Where the logs contradict
the message, the log value is used and the correction is listed at the
end.

Measurements cited (all exit 0, all P0 PASS; Python 3.12.3, NumPy 2.5.3,
Linux, 2 workers; the laptop passed the determinism gate, ENVIRONMENT.md):

| Id | Log | Run folder |
|---|---|---|
| M1 | logs/m1-20261016-0524.log | runs/m1-20261016-052412/ |
| M2 | logs/m2-20261016-0527.log | runs/m2-20261016-052740/ |
| M3 | logs/m3-20261016-0555.log | runs/m3-20261016-055516/ |
| M4 | logs/m4-20261016-0547.log | runs/m4-20261016-054755/ |
| M5 | logs/m5-20261016-0549.log | runs/m5-20261016-054952/ |
| M6 | logs/m6-20261016-0552.log | runs/m6-20261016-055203/ |
| M7 | logs/m7-20261015-2146.log | runs/m7-20261015-214629/ |
| N30 | logs/n30-20261015-2201.log | runs/n30-20261015-220127/ |

The limit that applies to every measurement: M1 to M7 ran on archived
random-beta (exactcal) and probe-beta (rmapj, regimemap) designs. Each log
says it "says nothing about calprec betas". So every measured number below
describes the round-1 designs. The rerun runs under calprec2 betas, and
its own numbers may differ.

---

## 0. Estimand (ledger N33)

**Decision.** The primary per-cell statistic is S-slope: the mean over
realizations of each realization's fitted slope. S-curve is the slope fitted
to the realization-averaged error curve. It is reported as a secondary
column wherever it exists, and is never mixed into a claim.

**Criterion (docstring text).**
- For a cell with realizations i = 1..M, fit each realization's slope s_i
  with the archived regimemap.fit_slope on the window of item 2.
- S-slope = mean of s_i. Every verdict, interval and comparison uses
  S-slope.
- S-curve, the archived fit_slope applied to the mean curve over i, is
  printed in its own column, labelled secondary. No verdict reads it.

**Worked example (illustrative numbers).** Three realizations with fitted
slopes -1.02, -0.98 and -1.00 give S-slope = (-1.02 - 0.98 - 1.00) / 3 =
-1.000. If the slope of their averaged curve is -1.015, that value is
printed in the S-curve column and enters no claim.

**Decided by.** N30: every reproduced round-1 point estimate is E=slope,
and none is E=curve. M2's Table 3 reconstruction agrees: under S-slope it
gives d=2 -1.0655, d=40 -1.0113, change +0.0542 at tau_0 0.5, which is
Table 3. M1 shows the choice is detectable:
- the S-slope minus S-curve gap has median +0.0108 for exactcal and +0.0203
  for rmapj;
- its interval excludes zero in 48 of 144 exactcal cells and in 129 of 180
  rmapj cells.

**Judgement (Rahul's).** Comparability with round 1 is the reason for the
choice. No measurement says which estimand is closer to the mean-field
rate. That cannot be measured from the archive.

**Limit on the stated reason (from the archive, not a log).** S-slope
matches the round-1 numbers that came from exactcal, regimemap and reboot.
It does not match the round-1 simulation scripts mechanism, control,
boundary, sigma, crossed, cliff, regime, law and visibility. Those fitted
the mean curve (S-curve; ANALYSIS_CRITERIA_DRAFT item 3 table). For rows
inherited from those scripts, S-slope primary breaks comparability, and
the secondary S-curve column is the comparable one.

**Also from M1.** The gap depends on design. Across the rmapj subgroups
its median runs from +0.0007 (isotropic d 80) to +0.0626 (anisotropic
d 5); across the exactcal tau_0 groups, from -0.0015 (tau_0 0.5) to
+0.0256 (tau_0 0.01). So an S-slope
against S-curve difference can change a diffusion comparison. Hence
"never mixed into a claim".

---

## 1. Interval level and sidedness (referee point 9; ledger R9)

**Decision.**
- Every reported interval is a two-sided 95% bootstrap percentile
  interval.
- Equivalence uses two one-sided tests at 5% each side, reported as the 90%
  interval.
- No one-sided bound is labelled by a two-sided level. The archive's "95%
  upper bound" computed as the 97.5th percentile is not inherited.
- Where a one-sided bound is wanted, it is the 95th percentile, and it is
  called a one-sided 95% bound.

**Criterion (docstring text).**
- Two-sided 95%: numpy.percentile(v, [2.5, 97.5]) over the B resampled
  values v of item 3.
- One-sided 95% upper bound: numpy.percentile(v, 95). One-sided 95% lower
  bound: numpy.percentile(v, 5). Each is labelled "one-sided 95%".
- Equivalence (TOST, 5% each side) at margin m (item 5): EQUIVALENT iff
  numpy.percentile(v, 5) > -m and numpy.percentile(v, 95) < +m. The
  interval is printed as "90% (TOST 5% each side)".

**Worked example (illustrative numbers).**
- The resampled changes give 2.5th, 5th, 95th and 97.5th percentiles of
  +0.021, +0.026, +0.079 and +0.083.
- The reported interval is [+0.021, +0.083] (two-sided 95%).
- A one-sided bound, if wanted, is +0.079, called "one-sided 95% upper
  bound". It is never called "95% upper bound" at +0.083.
- For a gap whose 5th and 95th percentiles are -0.031 and +0.027 under a
  margin m = 0.040: -0.031 > -0.040 and +0.027 < +0.040, so EQUIVALENT,
  printed with [-0.031, +0.027] as "90% (TOST 5% each side)".

**Decided by.** No measurement. This is a convention, fixed together with
referee point 9 and ledger R9 (the archive's mislabelled 97.5th percentile,
N34).

**Judgement (Rahul's).** The whole item.

**Not settled by measurement.** Coverage of a percentile interval at 12 to
20 realizations per cell. M3 measured Monte Carlo error, not coverage (its
log: "nothing about coverage"). Coverage needs a simulation with a known
slope.

**NOT DECIDED.**
- The verdict rule for "difference detected". Claude's reading of the
  decision, to be confirmed: a difference is detected iff the two-sided 95%
  interval excludes zero. The archive's DIFF rule, a 90% interval
  excluding the margin, is not inherited.
- ANALYSIS_CRITERIA_DRAFT 1(iv), the Bonferroni family, if any.

---

## 2. Fit window (draft item 2)

**Decision.**
- The full J grid is primary for every row.
- For every tau_0 = 0.01 row, the restricted window J >= 1/tau_0 is
  reported alongside it as a sensitivity column, never as a substitute.
- The paper says plainly that the result depends on the window.

**Criterion (docstring text).**
- Primary window W-full: every J in the row's grid (J10 = 10, 20, 40, 80,
  160, 320, 640, 1280, 2560, 5000, or J10B with 1250 and 2500).
- Sensitivity window W-ge, for tau_0 = 0.01 rows: every grid J with
  J >= 1/tau_0, compared in exact fraction arithmetic from the tau_0
  string.
- Both slopes are printed side by side for those rows. Every verdict reads
  W-full. The W-ge column carries no verdict.

**Worked example (from M2's header, J10 grid).** At tau_0 0.01,
1/tau_0 = 100. W-full is the ten J from 10 to 5000. W-ge is [160, 320,
640, 1280, 2560, 5000], because the grid has no J = 100. At tau_0 0.1,
W-ge equals W-full: 1/tau_0 = 10 is the first grid point.

**Decided by.** M2, at tau_0 0.01 on exactcal, W-ge against W-full. For
S-slope, the primary estimand:
- |shift|/SD median 1.4546;
- the paired shift interval excludes zero in 16 of 48 cells;
- Table 3's change is +0.2533 on W-full and +0.0775 on W-ge.

For S-curve the same comparison gives median 1.5964 and 22 of 48.

**Judgement (Rahul's).**
- Which window is primary. M2 measures how much the window matters, not
  which window is right.
- Round 1 argued that the tightest target cannot be realized below
  J = 100 (tex 703). Making W-full primary means reporting the slope over
  ensemble sizes where the target is unattainable. That is the judgement
  being made, and the text must say so.

**NOT DECIDED.** The rerun's tau_0 grid is wider than 0.01. TAU8 and
GEOM run tau_0 0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01, and RMAP
includes 0.03 (costprobe2.py ROWS). At 0.07, 0.05, 0.03 and 0.02, W-ge
also excludes the smallest grid points: at tau_0 0.03 it starts at J = 40.
As written, the decision covers only tau_0 = 0.01 rows. Whether the
sensitivity column is also reported at every tau_0 where W-ge differs from
W-full is Rahul's to decide. M2 measured only tau_0 0.5, 0.1 and 0.01.

---

## 3. Bootstrap (draft item 3)

**Decision.**
- B = 10000 resamples.
- Resampling is by realization within a cell.
- There is no panel-level joint resampling across objectives.
  Heterogeneity across objectives is reported separately under item 6.

**Criterion (docstring text).**
- Single cell: draw M realization indices with replacement, recompute
  S-slope as the mean of the drawn slopes (S-curve, for its secondary
  column, by refitting the drawn mean curve), and repeat B = 10000 times.
- A multi-cell statistic, such as a d = 2 to d = 40 change, a contrast
  across tau_0, or a mean over objectives, is recomputed from per-cell
  resamples drawn independently in each cell: a stratified bootstrap with
  the design fixed.
- Two arms that share seed keys, as the diffusion arms do (item 5), are
  resampled jointly by key: one index vector per resample, applied to both
  arms. Arms that do not share keys are resampled independently and never
  differenced by index (ledger N31).
- Intervals: percentile, at the levels of item 1.

**Worked example (illustrative numbers).**
- A cell with M = 12 realizations: one resample draws indices such as
  (3, 3, 7, 0, 11, 5, 5, 2, 9, 1, 8, 6). S-slope of the resample is the
  mean of those 12 slopes. 10000 such values give the interval of item 1.
- A d = 2 to d = 40 change: each resample draws d = 2 and d = 40 indices
  independently and takes the difference of the two resampled S-slopes.
- An iso/aniso gap with shared keys: one draw of 12 keys gives both arms'
  slopes for the same keys, and the resampled gap is the mean of
  (aniso - iso) over those keys.

**Decided by.** M3: the Monte Carlo SD of a percentile endpoint as a
fraction of the statistic's bootstrap SD (the log's "ratio"; m3_bootmc.py
line 29). For S-slope, across exactcal and rmapj and the 2.5, 5, 95 and
97.5 percentiles:

| B | median ratio | maximum ratio |
|---|---|---|
| 400 | 0.0944 to 0.1270 | up to 0.2114 |
| 4000 | 0.0314 to 0.0413 | up to 0.0724 |
| 10000 | 0.0202 to 0.0267 | up to 0.0435 |

Including S-curve, the B = 10000 maximum is 0.0522 (rmapj, 97.5th
percentile).

**Judgement (Rahul's).** That a Monte Carlo SD near 2 to 3% of the
bootstrap SD at the median is small enough. M3 measures the error; it does
not set an acceptable level.

**Limits of the measurement.** M3 measured on archived designs with 12 to
15 realizations per cell, not under calprec2 betas, and not coverage.

**NOT DECIDED.**
- Bootstrap seeding. CLAUDE.md rule 5 requires SeedSequence keys for
  simulation seeds. Whether the bootstrap uses a SeedSequence keyed by
  (cell, statistic) was not stated. The archive's fixed seed 7 in every
  cell made all cells resample the same index sequence (draft item 3).
- The handling of non-finite resampled slopes. M1 and M3 found none in the
  archive, but the rerun needs its own rule.

---

## 4. Tolerances (draft item 4; ledger N32)

**Decision.**
- None of the three N32 criteria is inherited.
- For each comparison, the replacement is stated explicitly, or the
  comparison is not made.
- No tolerance is fixed by hand below a measured spread. Where a tolerance
  is needed, it is set from the measured SE of the quantity it governs,
  and the measurement is cited.

**Criterion (docstring text), per N32 item.**
- boundary.py line 373, monotonicity in tau_0 with tolerance 0.02: NOT
  INHERITED. NOT DECIDED: no replacement has been stated. Until one is
  fixed in the docstring before the run, the rerun makes no monotonicity
  claim.
- control.py criterion (iii), "within 0.15 of -1", which is two-sided for a
  one-sided bound: NOT INHERITED. NOT DECIDED: no replacement has been
  stated. Until one is fixed before the run, the rerun makes no claim
  against -1 for ADAPT.
- exactcal.py P-E2 and perjcal.py P-C2, bootstraps of the absolute value of
  the change: NOT INHERITED. Replacement: the signed change, bootstrapped
  as in item 3 and reported with its two-sided 95% interval (item 1),
  which may contain zero. This follows from items 1 and 3; it is not a
  separate tolerance. N30 found that every reproduced round-1 interval at
  tau_0 0.1, and at tau_0 0.01 on J >= 1/tau_0, matched only under the
  absolute value.

**General rule for any tolerance (docstring text).**
- A tolerance t on a quantity q is t = k x SE(q), where SE(q) is the
  bootstrap SD of q measured in the rerun (or in a named pilot) and
  computed before q is compared with anything.
- The docstring states k and the source of SE(q).
- NOT DECIDED: k. Rahul's decision fixes the form, not the multiplier.

**Worked example (illustrative numbers; k is not decided).** If the
measured SE of a monotonicity step is 0.030 and k were 2, then t = 0.060,
and a step of -0.045 would pass. The archive's 0.02 against a measured
floor of 0.055 (law.py's docstring, quoted in N32) is the failure this
rule forbids: there t < SE.

**Decided by.** N32 (the archived errors) and N30 (the absolute-value
matches). The general rule rests on supplement S3 error 4, "a monotonicity
tolerance smaller than the measured spread".

**Unchanged and not reopened.** These fix which beta each cell gets, not
how the rerun's results are judged:
- calprec2: C5m 0.054682, D1 0.025, C1 0.05, C6 0.05, BA 0.05, E1 1e-12;
- refscale: C5 and D1 at 0.025;
- detcheck: half a unit in the last stored digit.

**Judgement (Rahul's).** The choice of k, when made, and which comparisons
the paper makes at all (draft item 4).

---

## 5. Equivalence margin and pairing (draft item 5; ledgers N31, N30)

### 5a. Pairing

**Decision.** The rerun shares seed keys across the two diffusion arms, so
the pairing is real and a paired bootstrap is valid. This settles the
decision N31 left open.

**Criterion (docstring text).**
- The rerun's seed key omits the diffusion coordinate. For a given
  (row, objective, d, r or sigma, tau_0, rep), the isotropic and
  anisotropic runs draw the same X0 and the same Brownian increments from
  the same SeedSequence key.
- The rows affected are those with two diffusions: SIGMA, ANISO, RMAP,
  CLIFF and ONSET (costprobe2.py ROWS).
- Gaps are bootstrapped by key, jointly across arms (item 3).
- The seed table written to the output carries the key, so the pairing
  can be checked from the CSV: both arms' rows show the same seed.

**Worked example (illustrative numbers).** ANISO, rastrigin, d = 10,
r = 0.5, tau_0 0.1, rep 3: the isotropic and anisotropic rows both carry
the seed derived from that key. The archive's specimen, isotropic 20260830
against anisotropic 20261910 for the same rep (N31), must not occur.

**Decided by.** M7: by-index differencing of independent arms gave
intervals materially narrower than the independent-arm interval in 3 of
30 Part D cells (rho 0.900, 0.868, 0.870), with 0 of 30 verdict changes.

**Compatibility checked (code, not a log).** calprec2's calibration cell
is (module, objective, d, law, tau_0), with no diffusion coordinate
(calprec2.py cal_cells). Both arms therefore already receive the same
beta. calprec2 evolves no trajectories, so no completed rerun output is
affected by this decision.

**Judgement (Rahul's).**
- Sharing keys rather than analysing independent arms.
- M7 measured the cost of a false pairing, not the benefit of a real one.
  The variance reduction from shared keys is unmeasured, because the
  archive has no shared-key pair (draft item 3).

### 5b. Margin

**Decision.**
- The margin is not 0.05 on the basis of 0.0260.
- It is declared from the rerun's own measured per-cell slope SE, computed
  before any gap is examined. The rule for deriving it goes in the
  docstring.
- Attainability is checked before any equivalence verdict is claimed.

**Criterion (docstring text).**
- The margin m = k x S, where S summarises the rerun's per-cell S-slope
  bootstrap SDs over the cells entering equivalence comparisons. S is
  computed and printed before any gap is computed.
- NOT DECIDED: k, and whether S is one pooled number (for example the
  median over those cells) or a per-cell value.
- Attainability: in a cell, equivalence is attainable iff the 90%
  half-width of the gap, (p95 - p5) / 2, is below m. Where it is not, the
  cell is reported as "equivalence not attainable at this margin", not
  "inconclusive", and no equivalence verdict is given. This is Claude's
  wording of Rahul's "check attainability", to be confirmed.

**Worked example (illustrative numbers; k is not decided).** Suppose the
median S-slope SD over the comparison cells is 0.026 and k were 2. Then
m = 0.052.
- A cell whose gap has 90% half-width 0.067 is not attainable: 0.067 >
  0.052. It is reported as such whatever its interval is.
- A cell with half-width 0.040 and 90% interval [-0.031, +0.027] is
  attainable, and it is EQUIVALENT by item 1.

**Why per-cell scaling needs care (Claude's reasoning, not measured).** If
the margin is set per cell as k times that cell's own SE, the margin grows
with the cell's noise. Equivalence then becomes a statement about the gap
in units of its own SE, not a bound in slope units. A noisier cell gets a
wider margin, which is the opposite of what an equivalence claim is meant
to deliver. One pooled margin, fixed before the gaps, avoids this. The
choice is Rahul's.

**Decided by.** M4: the three candidate constructions of tex 78's scale
give medians 0.0259 (C-a), 0.0270 (C-b) and 0.0275 (C-c). M5: the
per-cell 90% half-width of the Part D gap under S-slope has median
0.0668, against a 0.05 margin. Both are read as follows.
- M4: the scale depends on design, so a scale measured under one protocol
  cannot set the margin for another.
  - Probe-beta sources agree with each other. Medians across
    constructions: rmapj 0.0261 to 0.0275, regimemap_D 0.0261 to 0.0273,
    regimemap_M 0.0257 to 0.0270. C-a reproduces tex 78 closely: 0.0259,
    IQR [0.0191,0.0337], against 0.0260 [0.0191,0.0341].
  - The random-beta source differs: exactcal 0.0435 to 0.0454.
  - Across all the subgroups printed, medians run from 0.0255
    (regimemap_M at tau_0 0.1 and 0.01) to 0.0486 (exactcal tau_0 0.1,
    se_boot_curve).
  - The rerun's calprec2 design is neither of these.
- M5: equivalence at 0.05 was largely unattainable in single cells with
  independent arms. The archive's Part D comparison was not per cell; it
  pooled three objectives per arm (L-pool-u). There the half-width median
  is 0.0533, with q25 0.0464 and p10 0.0432, so a minority of pooled
  comparisons could have reached 0.05. M7 found no Part D cell EQUIV
  under either construction.
- M5 covers independent arms only. Under shared keys (5a) the half-widths
  may be smaller, and that is unmeasured. Hence the attainability check
  is run on the rerun's own intervals.

**Judgement (Rahul's).** Any margin is a declared convention; no theorem
gives a scale (draft item 5). The multiplier k and the summary S are that
convention.

---

## 6. Heterogeneity (draft item 6)

**Decision.**
- For each claim, report the between-unit SD of the per-unit estimates and
  I-squared, both computed from the per-realization files, with the
  within-unit sampling variance stated alongside.
- No pooled interval is reported without them.
- Where tau-squared truncates at zero, report it as truncated, not as zero
  heterogeneity.

**Criterion (docstring text; the statistics as defined in
m6_hetero.py).** For a claim pooling k units (objectives, or (objective,
law) pairs) with per-unit estimates y_i:
- v_i: the bootstrap variance of y_i over B resamples of the unit's
  realizations (item 3);
- s2: the sample variance of y_i, ddof 1; sd_units = sqrt(s2);
- vbar: the mean of v_i;
- tau2_mm = max(0, s2 - vbar);
- Q = sum of (y_i - y_w)^2 / v_i, with y_w the 1/v_i-weighted mean;
- I2 = max(0, (Q - (k - 1)) / Q).

Printed with every pooled estimate and its interval: k, sd_units, vbar,
tau2_mm, I2, and "tau2 truncated at 0" whenever s2 <= vbar.

**Worked example (m6_hetero.py's own, illustrative numbers).**
- k = 3 units with y = -1.00, -0.95 and -0.90 have s2 = 0.0025.
- With v_i = 0.0009 each: vbar = 0.0009, tau2_mm = 0.0016, y_w = -0.95,
  Q = (0.0025 + 0 + 0.0025) / 0.0009 = 5.56, and I2 = (5.56 - 2) / 5.56 =
  0.64.
- Had s2 been 0.0006, then s2 < vbar and tau2_mm = 0. That is printed as
  "tau2 truncated at 0 (s2 0.0006 < vbar 0.0009)", not as "no
  heterogeneity".

**Decided by.** M6:
- I2 medians are 0.5883 to 0.9273 across the seven (source, estimand)
  groupings.
- The median of vbar/s2 is 0.0845 to 0.4330 in every grouping. Below 0.5,
  the between-unit component exceeds the within-unit sampling variance,
  so this holds in at least half the groups of every grouping.
- tau2_mm truncates at zero in 0 to 12 groups per grouping: 12 of 60 for
  rmapj under each estimand, 8 of 80 for regimemap_M.

**Limits of the measurement.**
- With k = 3 objectives (rmapj, regimemap_M), s2, Q and I2 rest on three
  numbers and are very imprecise. In the rerun, the named-objective rows
  have 2 (BETA-ANI), 3, 4 or 6 objectives (costprobe2.py ROWS). The sizes
  of the synthetic lists REG_SYNTH and LAW_SYNTH were not checked.
- M6's exactcal groups violate the independence these statistics assume,
  because Ackley and Sphere share seeds (N6; flagged in the log). The
  rerun's injective seed table removes that.
- No inference to objectives outside the test set (M6 log).

**Judgement (Rahul's).** That heterogeneity is reported descriptively,
with no threshold, and the choice of unit per claim (draft 6(i), 6(ii)).

---

## Corrections to the decision message, from the logs

1. **Item 2.** "A median of 1.60 SD with 22 of 48 cells" are M2's S-curve
   figures (1.5964; 22 of 48). For S-slope, the primary estimand of item
   0, M2 gives 1.4546 and 16 of 48. And "22 of 48 cells shifting beyond
   their own interval" is not what the log counts. It counts cells whose
   paired shift interval excludes zero.
2. **Item 3.** M3's ratio is the Monte Carlo SD over the statistic's
   bootstrap SD (m3_bootmc.py line 29), not over the interval width.
   - At B = 400 the median ratio runs from 0.0912 to 0.1330 over both
     estimands, that is 9 to 13%, not 10 to 13%.
   - At B = 10000 the maximum is 0.0522 over both estimands and 0.0435
     for S-slope. "At most 5%" holds for S-slope only.
   - The 4000 and 400-maximum figures are right.
3. **Item 3.** "The rerun is 21.5 hours measured." No log measures it.
   SESSION_STATE.md records 21.47 h summed wall at 4 workers, "computed
   from the projection CSV" of costprobe2, and calls it a lower bound.
   That is trajectory time. B affects only the analysis step, whose cost
   no log has measured for the rerun's 2322 cells.
4. **Item 5, M4.** "No single scale supports it" overstates the log.
   - The probe-beta sources agree closely: 0.0257 to 0.0275.
   - C-a reproduces tex 78's 0.0260 [0.0191,0.0341] as 0.0259
     [0.0191,0.0337].
   - The spread to 0.0486 comes from the random-beta exactcal source.
   - What the log supports: the scale depends on the design, so a
     probe-beta scale cannot set a calprec2 margin. The decision stands
     on that reason.
5. **Item 5, M5.** The 0.067 median (0.0668) is the per-cell half-width
   with independent arms, not "the archive's" construction. The archive
   compared pooled arms. The comparable M5 figure is L-pool-u, median
   0.0533 (q25 0.0464). "Largely unattainable" holds per cell, and less
   strongly at the archive's pooled level.
6. **Item 0.** "The new numbers stay comparable with the round-1 ones"
   holds for the exactcal, regimemap and reboot numbers. The round-1
   simulation scripts used S-curve (draft item 3 table), so for rows
   inherited from them the secondary column is the comparable one.
7. **Item 6.** "Exceeds sampling variance in most cells": M6 reports
   groups, not cells. The median vbar/s2 below 0.5 in every grouping
   supports "in at least half the groups of every grouping".

---

## Checklist for the rerun script's review

Each line is a yes/no check against the script and its output.
"Archive:" names what round 1 did instead.

Estimand and window
- [ ] Each realization's slope is fitted with the imported archived
      regimemap.fit_slope, never retyped. Archive: exactcal.fit_slope used
      np.linalg.norm (rule 4).
- [ ] S-slope is the statistic of every verdict; S-curve is printed in a
      column labelled secondary and read by no verdict. Archive: S-curve in
      nine scripts and S-slope in others, without distinction (N33).
- [ ] The primary window is the full grid for every row.
- [ ] Every tau_0 = 0.01 row prints the J >= 1/tau_0 slope beside it,
      carrying no verdict, with the window computed in exact fractions.
      Archive: the restricted window existed only in uncommitted code (N30).
- [ ] [Pending the item 2 NOT DECIDED] the sensitivity column at tau_0
      0.07, 0.05, 0.03 and 0.02.

Intervals and bootstrap
- [ ] B = 10000 for every interval. Archive: 400, 1000, 2000 or 4000 by
      script (N8).
- [ ] Resampling is by realization within each cell; multi-cell statistics
      are recomputed from independent per-cell resamples. Archive: panel
      resampling of (objective, rep) keys, twelve-unit and objective-unit
      bootstraps.
- [ ] No resampling unit is an objective or an objective-law pair. Archive:
      perjcal and audit (draft 3D).
- [ ] Two-sided 95% percentile for every reported interval.
- [ ] Every one-sided bound is the 95th or 5th percentile and is labelled
      "one-sided 95%". Archive: the 97.5th percentile labelled "95% upper
      bound" (R9).
- [ ] Equivalence printed as "90% (TOST 5% each side)", and only there.
- [ ] Changes are bootstrapped signed, never as absolute values. Archive:
      exactcal P-E2, perjcal P-C2 (N32).
- [ ] [Pending item 3 NOT DECIDED] the bootstrap seed rule; not the archive's
      fixed seed 7 shared by every cell.
- [ ] [Pending item 3 NOT DECIDED] the non-finite resample rule; the count is
      printed.

Seeds and pairing
- [ ] The seed key omits the diffusion coordinate in SIGMA, ANISO, RMAP,
      CLIFF and ONSET. Archive: the diffusion loop sat outside the seed
      counter (N31).
- [ ] The output CSV shows, for each paired key, the same seed in both arm
      rows. A check in the script stops the run if not.
- [ ] Paired gaps are resampled by key jointly across arms.
- [ ] No two arms are differenced by index unless they share keys. Archive:
      regimemap paired_ci and reboot paired_gaps (N31; M7).
- [ ] The word "paired" appears in the text and logs only where keys are
      shared. Archive: printed for independent arms (N31).
- [ ] Every seed comes from a SeedSequence keyed by the cell, and the table
      is injective. Archive: exactcal's formula collided (N6).

Tolerances and margin
- [ ] No monotonicity criterion with a hand-fixed tolerance. Archive:
      boundary.py 0.02 (N32).
- [ ] No two-sided "within 0.15 of -1" criterion. Archive: control.py (N32).
- [ ] Every tolerance in the docstring is k x SE with the SE's source named.
      [k pending]
- [ ] The equivalence margin is computed from the rerun's S-slope SDs and
      printed before any gap is computed: the log order shows margin before
      gaps. [k and S pending]
- [ ] The margin's stated basis is not 0.0260. Archive: tex 309 (N30).
- [ ] Every equivalence comparison prints its 90% half-width and the
      attainability flag before any verdict.

Heterogeneity
- [ ] Every pooled estimate prints k, sd_units, vbar, tau2_mm, I2 and the
      truncation flag. Archive: COLLAPSE sd only, or nothing.
- [ ] tau2_mm = 0 is printed as "truncated at 0", with s2 and vbar.

General (CLAUDE.md rule 5)
- [ ] Every criterion above appears in the docstring with its worked
      example, before first execution.
- [ ] Per-realization, per-J errors are written to the output CSV.
- [ ] The header prints every parameter, the seed rule, Python, NumPy,
      platform and workers; the run prints per-worker peak RSS.
- [ ] Every output file is opened with mode "x" in a new runs/<run-id>/.

## Decisions still needed from Rahul

1. Item 1: the "difference detected" rule (Claude's reading: the 95%
   interval excludes zero), and the Bonferroni family.
2. Item 2: the sensitivity column at tau_0 0.07, 0.05, 0.03 and 0.02.
3. Item 3: bootstrap seeding, and the non-finite rule.
4. Item 4: replacements for the boundary monotonicity criterion and the
   control.py criterion (iii), or confirmation that those comparisons are
   not made; the multiplier k.
5. Item 5: k, and whether S is pooled or per cell; confirmation of the
   attainability wording.
6. Item 6: the unit per claim.
