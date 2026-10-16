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

Claude wrote this file from Rahul's two decision messages of 2026-10-16
and the logs below, and has decided nothing in it. Where the logs
contradicted the first message, the log value is used. Rahul accepted all
seven corrections in his second message; they are listed at the end. The
second message also decided most of what the first left open. Each
decision taken in it is marked "(second message)". A third message of the
same day decided the rest; its decisions are marked "(third message)".

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
describes the round-1 designs. The rerun's own numbers may differ.

Which betas the rerun uses (calprec2.py docstring, lines 68 to 75;
correcting this file's earlier "the rerun runs under calprec2 betas"):
calprec2 calibrates only four rows, CONC, TAU8, SIGMA and ANISO. "No other
row is calibrated by calprec v2; those rows keep their archived betas."
So the rerun mixes calprec2-beta rows with rows on archived betas: fixed
design betas (BETA-ISO, BETA-ANI), the B / spread rule (LAWPANEL) and
probe betas (the rest).

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

**Limit on the stated reason (from the archive, not a log; correction 6,
accepted).** Comparability under S-slope holds only for the round-1
numbers that came from exactcal, regimemap and reboot. The nine round-1
simulation scripts (mechanism, control, boundary, sigma, crossed, cliff,
regime, law and visibility) fitted the mean curve (S-curve;
ANALYSIS_CRITERIA_DRAFT item 3 table). For rows inherited from those
scripts, S-slope breaks comparability, and the secondary S-curve column is
the comparable one.

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
- (Second message.) A difference is declared when the two-sided 95%
  interval excludes zero. The archive's DIFF rule, a 90% interval
  excluding the margin, is not inherited.
- (Second message.) No Bonferroni or other multiplicity correction. The
  rerun reports intervals, not a battery of tests. Multiplicity is handled
  by reporting every cell, not by selecting the cells whose interval
  excludes zero.

**Criterion (docstring text).**
- Two-sided 95%: numpy.percentile(v, [2.5, 97.5]) over the B resampled
  values v of item 3.
- One-sided 95% upper bound: numpy.percentile(v, 95). One-sided 95% lower
  bound: numpy.percentile(v, 5). Each is labelled "one-sided 95%".
- Equivalence (TOST, 5% each side) at margin m (item 5): EQUIVALENT iff
  numpy.percentile(v, 5) > -m and numpy.percentile(v, 95) < +m. The
  interval is printed as "90% (TOST 5% each side)".
- DIFFERENCE iff numpy.percentile(v, 2.5) > 0 or numpy.percentile(v,
  97.5) < 0, on the signed statistic. Otherwise the cell is printed as "95%
  interval contains 0", never as "no difference" or "equivalent" (CLAUDE.md
  rule 10).
- No interval is adjusted for multiplicity. Every cell's interval and
  verdict is written to the output, whatever its verdict.

**Worked example (illustrative numbers).**
- The resampled changes give 2.5th, 5th, 95th and 97.5th percentiles of
  +0.021, +0.026, +0.079 and +0.083.
- The reported interval is [+0.021, +0.083] (two-sided 95%).
- A one-sided bound, if wanted, is +0.079, called "one-sided 95% upper
  bound". It is never called "95% upper bound" at +0.083.
- For a gap whose 5th and 95th percentiles are -0.031 and +0.027 under a
  margin m = 0.040: -0.031 > -0.040 and +0.027 < +0.040, so EQUIVALENT,
  printed with [-0.031, +0.027] as "90% (TOST 5% each side)".
- The change above, [+0.021, +0.083], excludes zero: DIFFERENCE. A change
  with interval [-0.004, +0.061] contains zero and is printed "95% interval
  contains 0".

**Decided by.** No measurement. This is a convention, fixed together with
referee point 9 and ledger R9 (the archive's mislabelled 97.5th percentile,
N34).

**Judgement (Rahul's).** The whole item, including the difference rule and
the absence of a multiplicity correction.

**Consequence of no multiplicity correction.**
- Rahul's statement: multiplicity is handled by reporting every cell, not
  by selecting the cells whose interval excludes zero.
- Claude's reading of what that implies, to be checked: each interval has
  nominal 95% coverage on its own, and nothing controls the chance that
  some cell among many excludes zero by chance; among cells with no true
  difference, about 1 in 20 is expected to show DIFFERENCE at the nominal
  level. So a cell showing DIFFERENCE is not presented as a finding on
  that basis alone, and the text says no correction was applied.

**Two verdicts on one cell (Claude's observation).** The DIFFERENCE rule
reads the 95% interval against zero; equivalence reads the 90% interval
against the margin. A gap with 95% interval [+0.004, +0.030] and 90%
interval inside (-m, +m) is both DIFFERENCE and EQUIVALENT: a detectable
gap smaller than the margin. (Third message.) The output prints both
verdicts, and the text states it plainly: the gap is distinguishable from
zero and smaller than the margin. Rahul's judgement: that is a real and
reportable finding, not a contradiction.

**Not settled by measurement.** Coverage of a percentile interval at 12 to
20 realizations per cell. M3 measured Monte Carlo error, not coverage (its
log: "nothing about coverage"). Coverage needs a simulation with a known
slope.

---

## 2. Fit window (draft item 2)

**Decision.**
- The full J grid is primary for every row.
- (Extended in the second message.) At every tau_0 where the restricted
  window J >= 1/tau_0 drops at least one grid point, that window is
  reported alongside as a sensitivity column, never as a substitute. The
  first message named only tau_0 = 0.01.
- The paper says plainly that the result depends on the window.

**Criterion (docstring text).**
- Primary window W-full: every J in the row's grid (costprobe2.py lines
  340 to 343: J10 = 10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000; J10b
  with 1250 and 2500 in place of 1280 and 2560; J19 for LAWPANEL).
- Sensitivity window W-ge: every grid J with J >= 1/tau_0, compared in
  exact fraction arithmetic from the tau_0 string. It is printed for every
  (row, tau_0) where W-ge is shorter than W-full.
- Both slopes are printed side by side for those rows. Every verdict reads
  W-full. The W-ge column carries no verdict.

**Which tau_0 that is, read from the rerun grid (costprobe2.py GRID and
TAU8, lines 359 and 402 to 434).** Every grid starts at J = 10, so W-ge
drops points exactly when 1/tau_0 > 10, that is tau_0 < 0.1. At tau_0 0.1,
1/tau_0 = 10 is the first grid point and nothing is dropped; at 0.5, 0.3
and 0.2 nothing is dropped either.

| tau_0 | 1/tau_0 | W-ge starts at (J10, J10b) | Grid points dropped |
|---|---|---|---|
| 0.07 | 100/7 | 20 | 10 |
| 0.05 | 20 | 20 | 10 |
| 0.03 | 100/3 | 40 | 10, 20 |
| 0.02 | 50 | 80 | 10, 20, 40 |
| 0.01 | 100 | 160 | 10, 20, 40, 80 |

The rows that carry a W-ge column, by their GRID tau_0 lists:
- tau_0 0.07, 0.05, 0.03, 0.02 and 0.01: TAU8 and GEOM.
- tau_0 0.03 and 0.01: RMAP.
- tau_0 0.01 only: CONC, PROBEARM, ADAPT, SYNTH, NAMED, SIGMA and ANISO.
- None: CLIFF and ONSET (tau_0 0.1 only).
- BETA-ISO, BETA-ANI, LAWPANEL, REFSIZE and HORIZON list no tau_0 in
  GRID. Read from the code (third message asked for it):
  - BETA-ISO and BETA-ANI: module ess_surface (costprobe2.py row_cells).
    Beta is the design variable itself, from the lists at ess_surface.py
    lines 243 and 246; the script contains no tau_0. No 1/tau_0 window
    exists, so no W-ge column.
  - LAWPANEL: module visibility. Beta = B / robust spread with B = 30.0
    (visibility.py lines 314 and 367); the script contains no tau_0. No
    W-ge column. (ANALYSIS_CRITERIA_DRAFT line 390 already said so for
    these three rows.)
  - REFSIZE: module regime, tau_0 0.1, fixed inside the cells list
    (regime.py line 513; costprobe2.py SOURCE note). At 0.1, W-ge equals
    W-full: no column.
  - HORIZON: module regime, d 10 and tau_0 0.1, fixed inside the cells
    list (regime.py line 601). No column.
  So no W-ge column is added by these five rows.

**Worked example (J10 grid).** At tau_0 0.01, 1/tau_0 = 100. W-full is
the ten J from 10 to 5000. W-ge is [160, 320, 640, 1280, 2560, 5000],
because the grid has no J = 100. At tau_0 0.07, 1/tau_0 = 100/7, and
the exact comparison keeps J = 20 and drops J = 10. At tau_0 0.1, W-ge
equals W-full and no sensitivity column is printed.

**Decided by.** M2, at tau_0 0.01 on exactcal, W-ge against W-full. For
S-slope, the primary estimand (correction 1, accepted: Rahul's first
message quoted the S-curve column):
- |shift|/SD median 1.4546;
- in 16 of 48 cells the paired-shift interval excludes zero;
- Table 3's change is +0.2533 on W-full and +0.0775 on W-ge.

For S-curve, the secondary column, the same comparison gives median
1.5964 and 22 of 48.

**Judgement (Rahul's).**
- Which window is primary. M2 measures how much the window matters, not
  which window is right.
- Round 1 argued that the tightest target cannot be realized below
  J = 100 (tex 703). Making W-full primary means reporting the slope over
  ensemble sizes where the target is unattainable. That is the judgement
  being made, and the text must say so.

**Limit of the measurement.** M2 measured only tau_0 0.5, 0.1 and 0.01.
How much the window matters at 0.07, 0.05, 0.03 and 0.02 is unmeasured;
the sensitivity column there is reported because the window differs, not
because a shift was measured.

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
- (Second message.) Seeding. Each cell's resample indices come from
  numpy.random.default_rng(SeedSequence(boot_key)) at full width, where
  boot_key is the cell's own full-width seed key with the kind field set
  to one fixed bootstrap kind and the realization index removed. This is
  calprec2's construction (calprec2.py lines 370 to 381 and key_of, line
  537), whose kinds 31 to 35 are taken (34 retired).
- (Third message: Claude's to fix.) The bootstrap kind is 71. Kinds used
  by scripts/ today: 31, 32, 33 and 35 (calprec2), 51 (c6), 61 (m1 and
  memprobe), 62 to 67 (m2 to m7). 71 is used by none. The rerun's
  trajectory kinds must not use it, and the script prints it.
- Consequences of that rule (Claude's reading, to be checked in review):
  - Every statistic that uses a cell uses that cell's one index stream, so
    S-slope and S-curve are resampled with the same indices, and two
    contrasts that share a cell are correlated through it, as they are in
    the data.
  - The diffusion coordinate is absent from the key (item 5), so the two
    arms of a paired cell get the same stream. Joint-by-key resampling
    then follows from the seed rule, provided both arms hold the same keys
    in the same order. The script checks this and stops if not.
  - No cell shares a stream with another cell, because no two cells share
    a key. The archive's fixed seed 7 in every cell is not inherited.
- (Third message.) Non-finite realizations. A realization whose own
  fitted slope (on the window in use) is not finite is excluded from its
  cell before any resampling. The log names it with its seed key, and the
  cell's realization count is printed as reduced (for example "M 11 of
  12"). If more than one realization in a cell is excluded, the cell is
  flagged. Rahul's reason: this keeps the 1% resample flag measuring
  what it was meant to measure.
- (Second message.) Non-finite resamples. A resample whose statistic is
  not finite is counted and excluded, and the percentiles are taken over
  the finite resamples. The count is printed per cell. If any cell has
  more than 1% of its B resamples excluded, the run is flagged: a FLAG
  line naming every such cell is printed in the summary.

**Worked example (illustrative numbers).**
- A cell with M = 12 realizations: one resample draws indices such as
  (3, 3, 7, 0, 11, 5, 5, 2, 9, 1, 8, 6). S-slope of the resample is the
  mean of those 12 slopes. 10000 such values give the interval of item 1.
- A d = 2 to d = 40 change: each resample draws d = 2 and d = 40 indices
  independently and takes the difference of the two resampled S-slopes.
- An iso/aniso gap with shared keys: one draw of 12 keys gives both arms'
  slopes for the same keys, and the resampled gap is the mean of
  (aniso - iso) over those keys.
- Seeding: an ANISO cell's key (row, objective, d, sigma, r, tau_0) with
  the bootstrap kind gives one stream; the isotropic and anisotropic arms
  of that cell both draw from it, so resample 1 uses the same 12 indices
  in both arms.
- Non-finite realization: in a cell of M = 12, rep 7's slope is not
  finite. It is dropped, the log prints its key and "M 11 of 12", and
  every resample draws 11 indices from the remaining 11. No flag. Had
  reps 7 and 9 both been dropped, the cell would print "M 10 of 12" and be
  flagged.
- Non-finite: of B = 10000 resamples in a cell, 37 give a non-finite
  statistic. They are excluded, the percentiles use the other 9963, and
  the cell prints "non-finite 37 of 10000". 37 is below 1% (100), so no
  flag. At 140 the cell is named in the FLAG line.

**Decided by.** M3: the Monte Carlo SD of a percentile endpoint divided
by the statistic's bootstrap SD (the log's "ratio"; m3_bootmc.py line 29).
It is not a share of the interval width (correction 2, accepted). For
S-slope, across exactcal and rmapj and the 2.5, 5, 95 and 97.5
percentiles:

| B | median ratio | maximum ratio |
|---|---|---|
| 400 | 0.0944 to 0.1270 | up to 0.2114 |
| 4000 | 0.0314 to 0.0413 | up to 0.0724 |
| 10000 | 0.0202 to 0.0267 | up to 0.0435 |

Including S-curve, the B = 10000 maximum is 0.0522 (rmapj, 97.5th
percentile).

**What B = 10000 rests on.** M3's Monte Carlo figures alone. The cost of
the analysis step at B = 10000 has never been measured. The 21.5 hours in
Rahul's first message is withdrawn as a justification (correction 3,
accepted): it was a projection of trajectory time, not a measurement, and
B does not enter trajectory time.

**Judgement (Rahul's).**
- That a Monte Carlo SD near 2 to 3% of the bootstrap SD at the median is
  small enough. M3 measures the error; it does not set an acceptable
  level.
- The seed rule and the non-finite rules, including the 1% resample flag
  and the more-than-one-realization flag. No measurement sets them. M1
  and M3 found no non-finite slopes in the archive.
- The bootstrap kind 71 is Claude's choice, as Rahul asked.

**Limits of the measurement.** M3 measured on archived designs with 12 to
15 realizations per cell, not under calprec2 betas, and not coverage.

**NOT DECIDED.**
- (Raised by the third message's realization rule.) A paired cell where
  a realization is excluded in one arm only. The two arms then no longer
  hold the same keys, and the check above stops the run. Whether the key
  is dropped from both arms (keeping the pairing, losing one valid
  realization) or the stop stands is not decided.

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
  INHERITED, and (second message) the comparison is not made at all. The
  rerun makes no monotonicity claim in tau_0. TAU8 and GEOM report each
  tau_0's S-slope with its interval; the text describes them and does not
  call the sequence monotone or non-monotone.
- control.py criterion (iii), "within 0.15 of -1", which is two-sided for a
  one-sided bound: NOT INHERITED. (Second message.) Replaced by a
  one-sided 95% bound, consistent with item 1: the 95th percentile of the
  ADAPT adaptive arm's resampled S-slope, labelled "one-sided 95% upper
  bound".
  - (Third message.) The criterion: the one-sided 95% upper bound is at
    most -1. Nothing is added to -1. The output prints the bound, the
    two-sided 95% interval, and "upper bound <= -1: yes" or "no".
  - k = 3 (item 4's general rule) does NOT apply here. Reason (Claude's,
    adopted by Rahul, who records that he made the error): the one-sided
    bound already carries the sampling error, so -1 + 3 x SE would count
    it twice.
  - (Third message.) ADAPT keeps no compound "control artefact" verdict.
    control.py's criterion (i), drift below 0.05 log units, and (ii), SD
    across objectives at most 0.10, are dropped. (ii) is a heterogeneity
    threshold, which item 6 forbids. (i) was never examined by either
    party, so it is not inherited by default. control.py's RECOVERED rule,
    "95 percent upper bound at most -0.85" (docstring line 72), is dropped
    with them: it rests on the same hand-fixed 0.15 and on a 97.5th
    percentile labelled 95% (control.py line 277).
  - ADAPT reports its one-sided bound and its interval, and the text
    describes what they show.
  - Worked example (illustrative numbers): the adaptive arm's resampled
    S-slopes have 2.5th, 95th and 97.5th percentiles -1.12, -1.03 and
    -1.01. Printed: interval [-1.12, -1.01], one-sided 95% upper bound
    -1.03, "upper bound <= -1: yes". With 95th and 97.5th percentiles
    of -0.97 and -0.95 it prints "no"; the archive's rule (97.5th
    percentile at most -0.85) would have called that cell RECOVERED.
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
- (Second message.) k = 3.

**Worked example (illustrative numbers).** If the measured SE of a
quantity is 0.020, then t = 3 x 0.020 = 0.060, and a deviation of 0.045
lies within it. The archive's 0.02 against a measured floor of 0.055
(law.py's docstring, quoted in N32) is the failure this rule forbids:
there t < SE.

**Where k = 3 applies.** With the monotonicity comparison dropped, the
rule governs any tolerance a later docstring introduces, and the margin of
item 5, which uses the same k. It does not apply to a one-sided bound
compared with a fixed value, such as ADAPT's, because the bound already
carries the sampling error.

**Decided by.** N32 (the archived errors) and N30 (the absolute-value
matches). The general rule rests on supplement S3 error 4, "a monotonicity
tolerance smaller than the measured spread".

**Unchanged and not reopened.** These fix which beta each cell gets, not
how the rerun's results are judged:
- calprec2: C5m 0.054682, D1 0.025, C1 0.05, C6 0.05, BA 0.05, E1 1e-12;
- refscale: C5 and D1 at 0.025;
- detcheck: half a unit in the last stored digit.

**Judgement (Rahul's).** k = 3, dropping the monotonicity comparison,
the one-sided criterion "upper bound at most -1" for ADAPT, and dropping
control.py's (i), (ii) and RECOVERED. No measurement sets any of them.

**Inconsistency raised by the third message (Claude's finding, NOT
DECIDED).** The RECOVERED or "rate-consistent" rule dropped for ADAPT, a
bootstrap upper bound at most -0.85, is also the per-cell verdict of nine
other archived scripts, with the same constant: visibility (line 109),
regime (117), law (123), boundary (107), mechanism (121), sigma (106),
crossed (111), cliff (117) and regimemap (137). visibility.py and
regime.py take the 97.5th percentile for it (draft line 180). Rahul's
reason for dropping it in control.py applies to all of them, and the
general rule above already forbids the hand-fixed 0.15. Not decided:
whether every row's per-cell rate verdict becomes "one-sided 95% upper
bound at most -1", as for ADAPT, or no row carries one. LAWPANEL's N_vis
(visibility.py lines 276 to 286: the smallest J0 whose fit on J >= J0
meets -0.85) is built on the same rule and falls with it; it also chooses
a window, which item 2 does not provide for.

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

**Compatibility checked (code, not a log).** Both arms receive the same
beta in all five paired rows:
- SIGMA and ANISO are calibrated by calprec2, whose calibration cell is
  (module, objective, d, law, tau_0), with no diffusion coordinate
  (calprec2.py cal_cells).
- RMAP, CLIFF and ONSET keep archived probe betas (calprec2.py lines 74
  and 75), keyed (objective, d, tau_0) with no diffusion coordinate
  (regimemap.py lines 337 to 343; cliff.py lines 305 to 312).
calprec2 evolves no trajectories, so no completed rerun output is affected
by this decision.

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
- The margin m = k x S. S is computed and printed before any gap is
  computed.
- (Second message.) k = 3, and S is one pooled number, not a per-cell
  value. So one margin applies to every equivalence comparison.
- (Third message.) S is the median of the per-cell S-slope bootstrap SDs
  over every cell of the whole rerun: one S. This replaces this file's
  earlier "over the cells entering equivalence comparisons".
  - Median rather than mean (Rahul's reason): the SD distribution has a
    long right tail, and a mean would be pulled by it.
  - One pool rather than per row (Rahul's reason): a single margin in
    slope units then applies everywhere, the reason per-cell scaling was
    rejected.
  - The M4 figures behind the tail argument, corrected from the third
    message: its "maxima 0.12 to 0.34 against medians near 0.026" mixes
    estimands. For se_boot_slope, the S-slope SD that S is built from, M4
    gives medians 0.0257 to 0.0261 on the probe-beta sources (rmapj,
    regimemap_D, regimemap_M) and 0.0435 on exactcal, with maxima 0.0927
    to 0.1250 and q75 at most 0.0568. The 0.3430 maximum is rmapj's
    se_boot_curve (S-curve). The right tail is there under S-slope too, so
    the reason for the median stands.
- Attainability: in a cell, equivalence is attainable iff the 90%
  half-width of the gap, (p95 - p5) / 2, is below m. Where it is not, the
  cell is reported as "equivalence not attainable at this margin", not
  "inconclusive", and no equivalence verdict is given. The wording is
  Claude's; Rahul confirmed it in the second message.

**Worked example (illustrative numbers).** Suppose the median of the
per-cell S-slope SDs over the whole rerun is 0.026, so S = 0.026.
Then m = 3 x 0.026 = 0.078.
- A cell whose gap has 90% half-width 0.085 is not attainable: 0.085 >
  0.078. It is reported as such whatever its interval is.
- A cell with half-width 0.040 and 90% interval [-0.031, +0.027] is
  attainable, and it is EQUIVALENT by item 1: -0.031 > -0.078 and
  +0.027 < +0.078.

**Why per-cell scaling is rejected (Claude's reasoning, not measured;
adopted by Rahul).** If the margin is set per cell as k times that cell's
own SE, the margin grows with the cell's noise. Equivalence then becomes a
statement about the gap in units of its own SE, not a bound in slope
units. A noisier cell gets a wider margin, which is the opposite of what
an equivalence claim is meant to deliver. One pooled margin, fixed before
the gaps, avoids this.

**Tension raised by the third message (Claude's finding, NOT DECIDED).**
M4, the measurement this item rests on, found that the SD scale depends
on the design: medians near 0.026 for probe betas against 0.0435 for
random betas. The whole-rerun pool mixes designs. calprec2 betas in CONC,
TAU8, SIGMA and ANISO; archived betas elsewhere, including the paired
rows RMAP, CLIFF and ONSET (probe betas), and rows outside the paired
set of 5a, such as BETA-ISO, BETA-ANI (design betas) and LAWPANEL (the
B / spread rule). So S, and with it the margin, depends on how many cells
each design contributes, and cells that enter no equivalence comparison
still set the margin of those that do. That is
what "the scale depends on design, so one design's scale cannot set
another's margin" (correction 4) warns against, now applied inside the
rerun. Options: keep the whole-rerun pool and say so; pool over the cells
entering equivalence comparisons (SIGMA, ANISO, RMAP, CLIFF, ONSET), as
the earlier text had it; or both, the second governing. Rahul's to
decide.

**Decided by.** M4: the three candidate constructions of tex 78's scale
give medians 0.0259 (C-a), 0.0270 (C-b) and 0.0275 (C-c). M5: half-widths
of the Part D gap under S-slope. Both are read as follows.
- M4 (correction 4, accepted). The first message's "no single scale
  supports it" is withdrawn: the log does not show that. The decision
  stands on a different reason: the scale depends on the design, so a
  probe-beta scale cannot set the margin for calprec2 betas.
  - Probe-beta sources agree with each other. Medians across
    constructions: rmapj 0.0261 to 0.0275, regimemap_D 0.0261 to 0.0273,
    regimemap_M 0.0257 to 0.0270. C-a reproduces tex 78 closely: 0.0259,
    IQR [0.0191,0.0337], against 0.0260 [0.0191,0.0341].
  - The random-beta source differs: exactcal 0.0435 to 0.0454.
  - Across all the subgroups printed, medians run from 0.0255
    (regimemap_M at tau_0 0.1 and 0.01) to 0.0486 (exactcal tau_0 0.1,
    se_boot_curve).
  - The rerun's calprec2-beta rows are neither of these. Its other rows
    keep archived betas (see the note under the measurements table).
- M5 (correction 5, accepted). The first message's 0.067 is withdrawn as
  the archive's figure. It is the per-cell half-width with independent
  arms (median 0.0668). The archive's Part D comparison pooled three
  objectives per arm; the comparable M5 figure is L-pool-u, median 0.0533,
  q25 0.0464, p10 0.0432. What that supports: at the archive's pooled
  level the median comparison could not have reached equivalence at 0.05
  (0.0533 > 0.05), but at least a quarter could have (q25 0.0464 < 0.05).
  So at the pooled level 0.05 was out of reach for at least half of the
  comparisons and within reach for at least a quarter. Per cell, the
  median half-width 0.0668 was out of reach. M7 found no Part D cell
  EQUIV under either construction.
- M5 covers independent arms only. Under shared keys (5a) the half-widths
  may be smaller, and that is unmeasured. Hence the attainability check
  is run on the rerun's own intervals.

**Judgement (Rahul's).** Any margin is a declared convention; no theorem
gives a scale (draft item 5). k = 3 and a single pooled S are that
convention.

---

## 6. Heterogeneity (draft item 6)

**Decision.**
- For each claim, report the between-unit SD of the per-unit estimates and
  I-squared, both computed from the per-realization files, with the
  within-unit sampling variance stated alongside.
- (Second message.) The unit is the (objective, initial law) pair wherever
  a row has both; otherwise the objective. By costprobe2.py GRID, the rows
  with a law list are LAWPANEL, CONC, PROBEARM and HORIZON; every other
  row's unit is the objective.
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

**Worked example of the unit.** A CONC claim at d = 10, tau_0 0.1 pools
OBJ6 x {centred, mix-0.1}: each (objective, law) pair is one unit with its
own y_i and v_i. A TAU8 claim pools the six objectives of OBJ6, one unit
each.

**Decided by.** M6 (correction 7, accepted: M6 reports groups, not
cells):
- I2 medians are 0.5883 to 0.9273 across the seven (source, estimand)
  groupings.
- The median of vbar/s2 is 0.0845 to 0.4330 in every grouping. Below 0.5,
  the between-unit component exceeds the within-unit sampling variance,
  so this holds in at least half the groups of every grouping. The first
  message's "in most cells" is replaced by that.
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
with no threshold, and the unit per claim (draft 6(i), 6(ii)). M6
measured both kinds of unit, (objective, initial law) for exactcal and the
objective for rmapj and regimemap_M (its header, "units"), but does not
say which is right.

---

## Corrections to the first decision message, from the logs

All seven accepted by Rahul in the second message (2026-10-16) and
applied in the items above.

1. **Item 2.** "A median of 1.60 SD with 22 of 48 cells" are M2's S-curve
   figures (1.5964; 22 of 48): Rahul quoted the wrong column. For S-slope,
   the primary estimand of item 0, M2 gives 1.4546 and 16 of 48. And "22
   of 48 cells shifting beyond their own interval" is not what the log
   counts. It counts cells whose paired-shift interval excludes zero.
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
   no log has measured for the rerun's 2322 cells. The 21.5 hours is
   dropped as a justification; B = 10000 stands on M3 alone.
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
   0.0533 (q25 0.0464). "Largely unattainable" holds per cell. At the
   pooled level it is replaced by: out of reach for at least half of the
   comparisons, within reach for at least a quarter.
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
- [ ] Every (row, tau_0) with tau_0 < 0.1 prints the J >= 1/tau_0 slope
      beside the primary one, carrying no verdict, with the window computed
      in exact fractions: TAU8 and GEOM at 0.07, 0.05, 0.03, 0.02, 0.01;
      RMAP at 0.03 and 0.01; CONC, PROBEARM, ADAPT, SYNTH, NAMED, SIGMA,
      ANISO at 0.01. Archive: the restricted window existed only in
      uncommitted code (N30).
- [ ] No W-ge column for BETA-ISO, BETA-ANI and LAWPANEL (no tau_0) or
      REFSIZE and HORIZON (tau_0 0.1); the docstring says why, per row.

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
- [ ] DIFFERENCE iff the two-sided 95% interval excludes zero; otherwise
      "95% interval contains 0", never "no difference". Archive: DIFF as
      a 90% interval excluding the margin.
- [ ] No multiplicity adjustment, and every cell's interval and verdict is
      written, whatever the verdict.
- [ ] A cell that is both DIFFERENCE and EQUIVALENT prints both verdicts.
- [ ] Changes are bootstrapped signed, never as absolute values. Archive:
      exactcal P-E2, perjcal P-C2 (N32).
- [ ] Bootstrap indices come from default_rng(SeedSequence(boot_key)) at
      full width; boot_key is the cell's key with bootstrap kind 71
      (printed) and no realization index. Archive: fixed seed 7
      shared by every cell.
- [ ] Both arms of a paired cell hold the same keys in the same order, so
      they draw the same index stream; the script stops if not.
- [ ] A realization with a non-finite slope is dropped before resampling,
      named with its key, the reduced M printed; more than one dropped in
      a cell flags the cell. [one-arm drop in a paired cell pending]
- [ ] Non-finite resamples are counted, excluded and printed per cell; a
      FLAG line names every cell above 1% of B.

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
- [ ] No monotonicity comparison in tau_0, with or without a tolerance.
      Archive: boundary.py 0.02 (N32).
- [ ] No two-sided "within 0.15 of -1" criterion; the ADAPT adaptive arm
      prints its one-sided 95% upper bound (95th percentile), its 95%
      interval and "upper bound <= -1: yes/no", with nothing added to -1.
      Archive: control.py (N32).
- [ ] ADAPT prints no compound verdict, no drift criterion, no SD-across-
      objectives criterion and no RECOVERED at -0.85. Archive: control.py
      (i), (ii), RECOVERED.
- [ ] [pending] The per-cell -0.85 "rate-consistent"/RECOVERED verdict of
      the nine other archived scripts, and LAWPANEL's N_vis: replaced by
      "upper bound <= -1" or absent.
- [ ] Every tolerance in the docstring is 3 x SE with the SE's source named.
- [ ] The equivalence margin is 3 x S, S the median of the per-cell
      S-slope bootstrap SDs over the whole rerun, printed before any gap
      is computed: the log order shows margin before gaps. [pool pending:
      the design-mixing tension of item 5b]
- [ ] The margin's stated basis is not 0.0260. Archive: tex 309 (N30).
- [ ] Every equivalence comparison prints its 90% half-width and the
      attainability flag before any verdict.

Heterogeneity
- [ ] Every pooled estimate prints k, sd_units, vbar, tau2_mm, I2 and the
      truncation flag. Archive: COLLAPSE sd only, or nothing.
- [ ] tau2_mm = 0 is printed as "truncated at 0", with s2 and vbar.
- [ ] The unit is the (objective, initial law) pair in LAWPANEL, CONC,
      PROBEARM and HORIZON, and the objective in every other row.

General (CLAUDE.md rule 5)
- [ ] Every criterion above appears in the docstring with its worked
      example, before first execution.
- [ ] Per-realization, per-J errors are written to the output CSV.
- [ ] The header prints every parameter, the seed rule, Python, NumPy,
      platform and workers; the run prints per-worker peak RSS.
- [ ] Every output file is opened with mode "x" in a new runs/<run-id>/.

## Decisions still needed from Rahul

The third message decided every item the second left open. The tau_0 of
the five rows was read from the code (item 2). What remains was raised by
the third message's answers or by that reading:

1. Item 4: the per-cell "rate-consistent" or RECOVERED verdict, upper
   bound at most -0.85, in visibility, regime, law, boundary, mechanism,
   sigma, crossed, cliff and regimemap. The reason ADAPT's was dropped
   applies to all of them. Each row either takes ADAPT's "one-sided 95%
   upper bound at most -1" or carries no per-cell rate verdict. LAWPANEL's
   N_vis is built on the same rule and goes with it.
2. Item 5b: the whole-rerun pool for S mixes calprec2, probe and design
   betas, which M4 says have different SD scales, and lets cells that are
   never compared set the margin. Keep it, or pool over the five paired
   rows.
3. Item 3 with 5a: a paired cell where a realization is dropped in one arm
   only. Drop the key from both arms, or let the pairing check stop the
   run.
