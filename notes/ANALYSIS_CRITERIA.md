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
A fourth message settled the three points the third raised and asked for
a cross-row audit; its decisions are marked "(fourth message)", and the
audit is the section "Decisions made for one row that apply to others".
A fifth message decided the audit's items A1 to A8 and the margin split,
marked "(fifth message)", and asked for the audit to be repeated against
those answers; that is the section's second pass. A sixth message
decided the six points that remained, marked "(sixth message)"; the audit
was run again against it (fourth to sixth passes).

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

**Points the imported fit_slope drops (fourth pass, applied by
Claude).** The archived regimemap.fit_slope that item 0 imports (lines 191
to 196) keeps only grid points with finite E > 0 and fits whatever
remains if at least three points are left. Every trajectory script has
the same mask. That is a data-dependent window. A slope fitted that way
is not a W-full slope, which item 2 defines as using every J in the grid.
So:
- the rerun keeps importing fit_slope unchanged (CLAUDE.md rule 4), and
  checks before each fit that every E on the window is finite and > 0;
- a realization that fails the check has no slope on that window, and is
  handled by item 3's realization rule for that window: dropped, named
  with its key and the number of bad points, the reduced M printed, the
  cell flagged if more than one is dropped, and in a paired cell the key
  dropped from both arms.
This is applied per window, so a realization can lack a W-full slope and
still have a W-ge slope. If Rahul wants a realization that fails on either
window dropped from both, that is a change to this paragraph.
Worked example: in a cell of M = 12, rep 3's E at J = 10 is 0. W-full:
rep 3 is dropped, "rep 3 key ... 1 bad point; M 11 of 12". W-ge at tau_0
0.01 starts at J = 160, so rep 3's W-ge slope exists and that column keeps
M = 12.

**REFSIZE's window (fourth pass, NOT DECIDED).** regime.py Part A fits
all four J_inf on a common grid, J <= min(J_inf)/10 = 1250 (regime.py
docstring lines 25 and 26, code lines 515 to 518), so that the comparison
across J_inf is not confounded by different fitting ranges. RERUN_PLAN
row EXP-REFSIZE records the same. That window is fixed by the design, not
chosen from the data, so item 2's objection to N_vis does not apply. But
item 2 says the full grid is primary for every row. For REFSIZE it is
either the common J <= 1250 window or the full grid. Part A also fits the
extrapolation gamma(J_inf) = gamma_inf + a / J_inf, with a bootstrap
interval (docstring lines 22 to 24). That belongs to the
reference-adequacy reporting the sixth message keeps, and its form and
interval are not decided either.

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

**Paired cells (fourth message).** When a realization is dropped in one
arm of a paired cell (5a), its key is dropped from both arms. The log
prints the key and "dropped from both arms", and the reduced M is printed
for both arms. Rahul's reason: the pairing is the point of 5a, and keeping
an unpaired key would silently turn a paired comparison into a mixed one.
Worked example: in an ANISO cell of M = 12, rep 4's anisotropic slope is
not finite. Key rep 4 is dropped from both arms; both print "M 11 of 12";
the shared bootstrap stream draws 11 indices applied to both arms. The
cell is not flagged (one realization). The pairing check then passes,
because both arms hold the same 11 keys.

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
  INHERITED, and (second message) the comparison is not made at all.
  (Fifth message, A4.) The rerun makes no monotonicity claim in any
  variable, in any row. TAU8 and GEOM report each
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

**Per-cell rate verdict, every row (fourth message).**
- Every row that carried a per-cell rate verdict takes ADAPT's criterion:
  the one-sided 95% upper bound (95th percentile) of the cell's resampled
  S-slope is at most -1, with nothing added. The output prints the bound,
  the two-sided 95% interval and "upper bound <= -1: yes/no".
- The archived rule it replaces, "bootstrap upper bound at most -0.85"
  (RECOVERED or "rate-consistent"), appears with the same constant in nine
  scripts besides control.py: visibility (line 109), regime (117), law
  (123), boundary (107), mechanism (121), sigma (106), crossed (111), cliff
  (117) and regimemap (137). All nine change. (Fifth message.) A tenth
  carrier, ess_surface.py line 348, "J^-1 recovered" iff abs(slope + 1)
  < 0.15 on the point estimate (BETA-ISO, BETA-ANI), takes the same
  criterion; Rahul records that his count of nine was wrong. Rerun rows
  affected:
  LAWPANEL (visibility), REFSIZE, SYNTH, NAMED, HORIZON (regime), GEOM
  (law), TAU8 (boundary), CONC, PROBEARM (mechanism), SIGMA (sigma), ANISO
  (crossed), CLIFF (cliff), RMAP, ONSET (regimemap), ADAPT (control),
  and BETA-ISO, BETA-ANI (ess_surface): every rerun row.
- (Fifth message.) Nothing is added to -1 anywhere. The archived counts at
  tolerances 0.10, 0.15 and 0.20 (cliff.py 115 and 467, crossed.py 109
  and 482, regimemap.py 135 and 580) are not inherited.
- Where visibility and regime took the 97.5th percentile for that
  one-sided bound (visibility.py line 273; draft line 180), that is the R9
  error and is not inherited.
- The rule now reads -1, not -0.85.
- What that changes (Rahul's statement): -0.85 admitted slopes a long way
  from -1 as "rate-consistent", so the new criterion is stricter, and some
  archived verdicts will not survive it. That is expected and is a
  finding, not a failure.
- A qualification (Claude's, from the definitions, not measured;
  accepted by Rahul in the fifth message, and to be stated wherever the
  change of rule is described): the
  change has two parts that pull in opposite directions. The threshold
  moves from -0.85 to -1, which is stricter. The percentile moves from the
  97.5th to the 95th, which is more lenient at a fixed threshold. A cell
  passes the new rule and fails the old one only if its 95th and 97.5th
  percentiles lie more than 0.15 apart (95th at most -1, 97.5th above
  -0.85). So the new rule is stricter in every cell except those with a
  wide upper tail; it is not stricter in every cell by construction. A
  cell with a wide upper tail can pass now having failed before.
- LAWPANEL's N_vis (visibility.py lines 276 to 286) and (fifth message)
  ess_surface's P1.2 beta threshold, the largest beta still "recovered"
  (ess_surface.py lines 372 to 379), carry no verdict under the new rule.
  Both were built on the old rule and lose their basis.
- (Sixth message.) N_vis's window selection is dropped too. It chose a
  window by fitting every suffix with at least four points, a
  data-dependent window choice of the kind item 2 was written to prevent.
  LAWPANEL reports its slopes on the full grid with intervals and no
  N_vis. Its other role, choosing a fit window
  (the smallest J0 whose suffix fit meets the bound), is a separate matter
  that item 2 does not cover. NOT DECIDED; no rule is proposed here.
- Worked example (illustrative numbers): a TAU8 cell with 95th and 97.5th
  percentiles -0.93 and -0.90. Archive: -0.90 <= -0.85, RECOVERED. Rerun:
  -0.93 > -1, "upper bound <= -1: no".

**Judgement (Rahul's).** Extending ADAPT's criterion to every row, so that
one claim has one standard.

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
- (Fourth message.) S is the median of the per-cell S-slope bootstrap
  SDs over the cells of SIGMA, ANISO, RMAP, CLIFF and ONSET, plus the
  cells of any row that joins under A8 (fifth message): one S. This
  reverses the third message's "whole rerun". Rahul's reason: it is the
  objection of correction 4, that one design's scale cannot set another's
  margin, applied inside the rerun; cells that enter no equivalence
  comparison do not set the margin for cells that do.
  - Median rather than mean (Rahul's reason): the SD distribution has a
    long right tail, and a mean would be pulled by it.
  - One pool rather than per row (Rahul's reason, third message): a
    single margin in slope units then applies everywhere, the reason
    per-cell scaling was rejected.
  - The M4 figures behind the tail argument (correction accepted in the
    fourth message: Rahul cited S-curve maxima where S-slope was the
    relevant column): the third message's "maxima 0.12 to 0.34 against
    medians near 0.026" mixes estimands. For se_boot_slope, the S-slope
    SD that S is built from, M4 gives medians 0.0257 to 0.0261 on the
    probe-beta sources (rmapj, regimemap_D, regimemap_M) and 0.0435 on
    exactcal, with maxima 0.0927
    to 0.1250 and q75 at most 0.0568. The 0.3430 maximum is rmapj's
    se_boot_curve (S-curve). The right tail is there under S-slope too, so
    the reason for the median stands.
- Attainability: in a cell, equivalence is attainable iff the 90%
  half-width of the gap, (p95 - p5) / 2, is below m. Where it is not, the
  cell is reported as "equivalence not attainable at this margin", not
  "inconclusive", and no equivalence verdict is given. The wording is
  Claude's; Rahul confirmed it in the second message.

**Worked example (illustrative numbers).** Suppose the median of the
per-cell S-slope SDs over the cells of the five paired rows is 0.026, so
S = 0.026.
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

**One margin over the five rows (fifth message).**
- One margin applies over all five paired rows, although SIGMA and ANISO
  run on calprec2 betas and RMAP, CLIFF and ONSET on archived probe betas.
  Rahul's reason: a single margin in slope units is the point of 5b, and
  splitting it by design would reintroduce the per-cell problem at the
  row level.
- Known limitation, stated in the text: the pool mixes two beta designs,
  and M4 never measured calprec2 betas, so whether their SD scale differs
  from the probe-beta scale is unknown until the rerun prints it.
- Revisit condition (docstring text): the rerun prints the median per-cell
  S-slope bootstrap SD separately for the calprec2 rows and the probe
  rows, before any gap is computed. If they differ materially, the margin
  is revisited before any equivalence verdict is claimed.
- Because S is printed before any gap (criterion above), the revisit, if
  triggered, happens with no gap yet computed. Otherwise the margin would
  be chosen with the gaps in view.
- (Sixth message.) "Differ materially": the median per-cell SD of one
  design group differs from another's by more than a factor of 1.5. The
  threshold is Rahul's judgement; no measurement sets it.
  - Docstring text: for every pair of design groups in the pool, ratio =
    larger median / smaller median. REVISIT iff any ratio > 1.5. The pool
    is the five paired rows, since no other row makes an equivalence
    claim (sixth message, item 3), so there are two groups: calprec2
    (SIGMA, ANISO) and probe (RMAP, CLIFF, ONSET).
  - Worked example (Rahul's): calprec2 0.026 against probe 0.030, ratio
    1.15, no revisit; 0.026 against 0.042, ratio 1.6, revisit before any
    equivalence verdict.
  - What the script does on REVISIT (follows from the two fixed rules
    "revisited before any equivalence verdict" and "S printed before any
    gap"; applied by Claude): it prints both medians, the ratio and
    "MARGIN REVISIT REQUIRED", computes no gap in the pooled rows, prints
    no DIFFERENCE or equivalence verdict for them, and stops there with
    its own exit status. DIFFERENCE verdicts stop too, although they do
    not use the margin, because computing them would put the gaps in view
    before the margin is revisited.
- (Fifth message, A8.) Any equivalence claim anywhere uses this margin. A
  row outside the five that needs an equivalence claim joins the pooled
  set that defines S; it does not borrow the margin. The revisit condition
  then covers every beta design present in the pool, not only calprec2
  against probe (second-pass finding P7 below). (Sixth message.) No row
  outside the five makes an equivalence claim, so none joins.

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

## Decisions made for one row that apply to others (audit)

Rahul asked for every place where a decision made for one row should
apply to all, as the -0.85 rule did. Claude checked each decision against
the archived criteria table (ANALYSIS_CRITERIA_DRAFT, "Archived analysis
tolerances") and the archived scripts of every rerun row.

### First pass (fourth message), decided in the fifth message

Already general before the audit: item 0 (S-slope), item 2 (W-ge wherever
tau_0 < 0.1), item 3 (B, seeding, both non-finite rules), item 6 (unit
rule), item 1 (no multiplicity correction: the archived Bonferroni counts
in sigma, crossed, cliff and regimemap are not inherited), and item 2's
supersession of rmapj's P-R3 window rule.

A1. ess_surface's "J^-1 recovered" (line 348) is a tenth rate verdict.
    Decided: it takes the one-sided 95% upper bound at most -1. Its P1.2
    beta threshold carries no verdict, as N_vis carries none (item 4).
A2. Decided: the counts at tolerances 0.10, 0.15 and 0.20 are not
    inherited. Nothing is added to -1 anywhere (item 4).
A3. Decided: mechanism.py's COLLAPSE_SD = 0.10 (line 122) is dropped, for
    the reason control.py (ii) was: item 6 forbids heterogeneity
    thresholds. MECHANISM_DR2 = 0.05 (line 123), a variance-explained
    criterion that no decision covered, is dropped too. It was dropped so
    as not to inherit it unexamined, not because it was shown wrong.
A4. Decided: the rerun makes no monotonicity claim in any variable. Not in
    TAU8 (boundary.py line 373), not in GEOM (law.py lines 75 to 78 and
    589 to 596), not in CLIFF (cliff.py criterion (iii), lines 64, 65,
    398 to 407). law.py's crossing at 0.15 goes with it.
A5. Decided: every hand-fixed tolerance listed is dropped. Where the
    comparison is still made, it is made under item 4's 3 x SE rule with
    the SE measured in the rerun; where it is not, the row reports its
    estimates and intervals and makes no verdict. Per item (whether each
    comparison is made at all is the draft's open question "Which
    comparisons the rerun analysis makes", so where that is all that
    remains, it is marked NOT DECIDED):
    - cliff.py (i), FLAT_TOL 0.10 (line 120): the slope for r <= 1 stays
      within 0.10 of its r = 0.5 value. This is a claim of no change, an
      equivalence claim, so if made it falls under A8 (TOST at the 5b
      margin; CLIFF is in the pool), not under 3 x SE. Whether made: NOT
      DECIDED.
    - cliff.py (ii), DROP_MIN 0.30 (line 121): at least 0.30 flatter at
      r = 5. A minimum-size difference. Whether made, and how: NOT
      DECIDED. Claude's concern: "difference > 3 x SE" is a significance
      test at a level other than item 1's, the ADAPT double-counting
      problem in another form; item 1's DIFFERENCE rule may be the
      consistent replacement.
    - regimemap "map informative", range > 0.10 along each axis
      (regimemap.py lines 98 to 100): a claim that the exponent varies,
      a difference claim. Whether made, and whether under 3 x SE or item
      1's DIFFERENCE rule between axis levels: NOT DECIDED.
    - crossed.py's gap rule (lines 114, 457, 458): "small_A", every gap
      below 0.05 in absolute value, is a claim of no difference, so if
      made it is an equivalence claim under A8 (ANISO is in the pool).
      "grows_B", the d = 40 gap above the smallest-d gap, is a
      monotonicity claim in d and is dropped by A4. Whether small_A is
      made: NOT DECIDED.
    - law.py's "law useful", cross-validated R^2 > 0.5 and held-out R^2
      > 0 (lines 89 to 91): not made. The quantity the law predicts is
      the crossing at 0.15, which A4 drops, and the criterion is
      variance-explained, which A3 drops. Determined.
A6. Decided: regime.py's straightness claim (lines 70 to 73) is dropped.
    An interval containing zero is not evidence of straightness, and
    CLAUDE.md rule 10 forbids reading it so. The quadratic term is
    reported with its interval and no verdict.
A7. Decided, as a general rule: if a comparison between two arms is made
    at all, every rule of 5a applies to it: shared keys (the key omits the
    arm coordinate), joint resampling, the one-arm drop rule, the pairing
    check, and the word "paired" only where keys are shared. Arm pairs the
    rerun compares:
    - the isotropic and anisotropic arms of SIGMA, ANISO, RMAP, CLIFF and
      ONSET: compared, decided in 5a;
    - ADAPT fixed against adaptive (control.py lines 345 and 346 share
      seeds): NOT DECIDED;
    - BETA-ISO against BETA-ANI: NOT DECIDED;
    - CONC against PROBEARM: NOT DECIDED;
    - ANISO's arm A (sigma levels) against arm B (r levels): different
      factor levels, not one key in two treatments; Claude's reading is
      that A7 does not apply. To confirm.
A8. Decided: any equivalence claim anywhere uses the margin of item 5b. A
    row outside the five that needs one joins the pooled set that defines
    S, rather than borrowing a margin (item 5b).

### Second pass (against the fifth message's answers)

Each fifth-message decision was checked for other places it belongs.

P1. A4, "no monotonicity in any variable", reaches three more claims:
    - sigma.py P8.1: "the isotropic rows should degrade from left to
      right" (lines 403 to 405), monotone in r. Dropped by A4.
    - regimemap.py Part D: "r_onset falls with d" (lines 65 to 67, 526 to
      528), monotone in d. Dropped by A4. "Onset moves with d", read as a
      difference between two d values, remains available under item 1's
      DIFFERENCE rule; Claude's reading, to confirm.
    - crossed.py "grows_B": already dropped under A5.
P2. A1 and N_vis, "a quantity built on the old rule carries no verdict":
    law.py's crossing at 0.15 is the third such quantity, already dropped
    by A4. sigma.py, regimemap.py and cliff.py also mark or count cells
    that are "not rate-consistent" (sigma.py line 399, regimemap.py lines
    456 to 458, cliff.py 467 and 468). Those are displays of the per-cell
    verdict and change with it to the -1 rule; their Bonferroni versions
    ("bhi") go under item 1. No new decision.
P3. A3, "a variance-explained criterion no decision covers is dropped",
    reaches two more analyses:
    - regime.py P6.3 (lines 440 to 465): nested models scored by
      out-of-sample R^2, with "the paper must say so" if it is negative.
      No numeric threshold but zero. NOT DECIDED: dropped by A3's reason,
      or reported descriptively with no verdict.
    - ess_surface.py P1.3, ESS as a predictor of slope breakdown
      (docstring lines 34 to 40), defines breakdown through the old rate
      verdict and asks whether ESS predicts it. NOT DECIDED, for the same
      reason; its definition of breakdown also changes with A1.
P4. Item 3's no-panel-resampling rule, against regimemap's onset interval:
    regimemap.py lines 94 to 96 bootstrap the onset "over objectives and
    realizations", a panel resampling that item 3 forbids. If the onset
    is estimated, its interval resamples realizations within cells. This
    follows from item 3 as decided; no new decision. The onset's
    "interval excludes r = 1" rule is item 1's form already.
P5. A6, "an interval containing zero is not evidence": item 1 already
    states it for every row ("95% interval contains 0, never no
    difference"). The same holds for the onset: an interval containing 1
    does not show the onset is at 1. No new decision.
P6. A7: ess_surface also prints a verdict "outside FKR hypothesis" for d
    failing 2 lambda > d sigma^2 (lines 346, 347), and a "SATURATED" label
    for ESS below 1.01 (line 344). Neither is a rate verdict or a
    tolerance on a slope. The 1.01 is a hand-fixed threshold of the A5
    kind, not in the A5 list. NOT DECIDED: whether it is inherited.
    Separately, whether "FKR hypothesis" names a hypothesis of the cited
    theorem is a rule 9 and ledger N1 question for the text, not for this
    file.
P7. A8 with the 5b revisit condition: if a row joins the pool under A8,
    it may bring a third beta design (design betas in BETA-ISO and
    BETA-ANI, the spread rule in LAWPANEL). The revisit condition then
    compares every design group in the pool, not only calprec2 against
    probe. Recorded in 5b.
P8. A8 against A5: the A5 items that are claims of no change (cliff (i),
    crossed small_A) fall under A8's margin, not under 3 x SE. Recorded
    per item in A5. audit.py A2, "r has no effect of practical size"
    (interval inside +-0.10), and partm P-M3 and P-M4, "agreement within
    2 x 0.0219", are equivalence claims of the same kind: if made, they
    use the 5b margin and TOST. Whether made: NOT DECIDED. partm P-M2's
    "at least 3 of 4 panels" is a counting rule of the A5 kind; whether
    made: NOT DECIDED.

### Third pass

Claude checked the second pass's findings for further places they belong.
P1 and P4 add no rows: the trend-in-d and onset claims are in RMAP and
ONSET, already in the pool. Of P8's equivalence claims, partm reads
regimemap Parts M and D (partm.py line 86), which are the RMAP and ONSET
rows, so it needs no join. Which data audit.py A2's r comparison reads
was not checked; if it lies outside the five rows, A8 makes that row
join. The third pass found nothing new. The NOT DECIDED items above went to
Rahul and were decided in the sixth message, below.

### Sixth message: the open items decided

S1. Margin revisit: ratio of design-group medians above 1.5 (item 5b).
S2. N_vis's window selection dropped (item 4).
S3. Which comparisons the rerun makes. Rule, applied uniformly: a
    comparison is made only if it answers a question the new paper asks.
    The main text is fixed-beta concentration dependence, the limits of
    calibration including reference-estimability, two diffusion regimes,
    and the corrected assumption audit.
    - MADE: the five paired diffusion comparisons (SIGMA, ANISO, RMAP,
      CLIFF, ONSET), the concentration-dependence rows, and the
      reference-adequacy reporting.
    - NOT MADE: cliff (i) and (ii), regimemap "map informative", crossed
      small_A, audit.py A2, partm P-M2 to P-M4. Those rows report
      estimates and intervals for these quantities, with no verdict.
    - Arm pairs compared: none beyond the five. ADAPT reports its bound;
      BETA-ISO against BETA-ANI and CONC against PROBEARM are not
      compared. ANISO arm A against arm B is outside A7, being different
      factor levels, not one key in two treatments (Claude's reading,
      accepted).
    This resolves every A5 and P8 item to "not made", and A7's list to the
    five rows.
S4. "Onset moves with d" does not survive: Rahul's ruling is that it is a
    monotonicity claim in a different costume, which A4 forbids. The
    onsets are reported per d with intervals, and the text describes them.
S5. regime P6.3 and ess_surface P1.3: reported with no verdict. Rahul's
    reason: A3's reason covers both, and dropping the verdict while
    keeping the numbers is the honest form.
S6. ess_surface's ESS 1.01 saturation threshold is not inherited. ESS is
    reported with no saturation label.

### Fourth pass (against the sixth message)

Items that follow from rules already fixed are applied, as Rahul asked.

Applied:
F1. S1's REVISIT action. The script stops before any gap in the pooled
    rows (item 5b). Follows from "S before any gap" and "revisited before
    any equivalence verdict".
F2. fit_slope's point mask. W-full needs every grid point, so a
    realization with a bad point has no slope on that window and falls
    under item 3's realization rule (item 2). Follows from item 2's
    definition of W-full, from rule 4, and from item 3.
F3. S5's "drop the verdict, keep the numbers" also governs mechanism's R^2
    values. A3 dropped MECHANISM_DR2 as a criterion. The three R^2 values
    (target, + dimension, + objective; mechanism.py lines 448 to 450) are
    printed with no verdict.
F4. S3's "those rows report estimates and intervals with no verdict"
    refers to the dropped comparisons. Item 4's per-cell rate verdict was
    decided for every row and still prints in CLIFF, RMAP, ONSET and
    ANISO. That is Claude's reading of S3 against item 4; say if S3 was
    meant to remove the rate verdict there too.
F5. ess_surface's "outside FKR hypothesis" label (lines 346 and 347).
    Ledger N1: 2 lambda > d sigma^2 is a hypothesis of FKR's
    convergence-to-minimizer theorem, not of the result that owns the J^-1
    exponent. CLAUDE.md rule 10 forbids calling it that theorem's
    admissibility. So the label is not inherited. Those cells get item 4's
    -1 rule like every cell, and the condition, if printed, is printed as
    the parameter fact "2 lambda > d sigma^2: holds" or "fails".
F6. S4 and F5 together. regimemap.py and cliff.py split cells into "in"
    and "OUT" at r = 1 (regimemap.py lines 460 and 461; cliff.py lines
    461 to 463). The script labels these regions "r < 1" and "r >= 1",
    never "in", "admissible" or "inside the hypothesis" (rule 10, N1).
    Counts per region are summaries of the per-cell verdict, not
    comparisons between regions.

Needs Rahul's decision:
F7. S4 against the concentration-dependence comparisons that S3 keeps.
    S4 rules that "onset moves with d", read as differences between d
    values, is monotonicity in a costume. The concentration-dependence
    rows are about exactly that kind of claim. Round 1's were "the slope
    changes from d = 2 to d = 40" (Table 3; exactcal P-E2) and the tau_0
    contrasts (N30's CON 0.1-0.01, 0.5-0.01, 0.5-0.1). If a difference
    between two levels of an ordered variable is monotonicity in a
    costume, these fall too, and the main text has no comparison left. If
    they stand, the line between them and the onset needs stating. One
    candidate line, Claude's, not decided: a contrast between two named
    levels, fixed in the docstring before the run and answering a paper
    question, is a comparison under item 1; a statement that a quantity
    rises, falls or moves with a variable across its levels is a
    monotonicity claim under A4. Under that line the onset could keep
    pre-specified two-level contrasts, so S4 would also need restating.
    Either way, the list of contrasts in the concentration-dependence
    rows is needed, and it does not exist yet.
F8. Which rows are "the concentration-dependence rows", and what "the
    reference-adequacy reporting" consists of. Both are needed to decide
    which comparisons the script computes. Candidates by name: CONC,
    PROBEARM, TAU8, GEOM, SYNTH and NAMED for the first; REFSIZE and
    calprec2's target/beta labels for the second. Not decided.
F9. REFSIZE's window and its J_inf extrapolation (item 2).

### Fifth pass (against F1 to F6)

- F1 affects only the pooled rows' gaps. Per-cell outputs and the other
  rows are unaffected, so it creates nothing elsewhere.
- F2 feeds item 3's flags, which are already general. For REFSIZE, the
  window that F2 checks is whichever F9 decides.
- F5 and F6: visibility.py drops dimensions that fail the same condition
  (lines 342 and 343). In the rerun grid this removes nothing, because
  LAWPANEL's GRID dims stop at 40 (visibility prints "grid stops before
  failure at d=50"). Its printed wording, "FKR condition", falls under
  F5's rule if the script prints it.
- F3 and S5 cover every R^2 analysis found: mechanism, regime P6.3, and
  ess_surface P1.3. law.py's R^2 has no target left (A5).

### Sixth pass

Claude checked the fifth pass's findings again and found nothing new.
F7 to F9 need Rahul's decision, so the audit is not closed on them.

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
      a cell flags the cell.
- [ ] In a paired cell, a key dropped in one arm is dropped from both;
      the log prints the key, "dropped from both arms", and both arms'
      reduced M.
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
- [ ] No monotonicity claim in any variable, in any row, with or without
      a tolerance. Archive: boundary.py 0.02 (N32); law.py and cliff.py
      (iii) noise floors; sigma P8.1; regimemap "r_onset falls with d";
      crossed "grows_B".
- [ ] No two-sided "within 0.15 of -1" criterion; the ADAPT adaptive arm
      prints its one-sided 95% upper bound (95th percentile), its 95%
      interval and "upper bound <= -1: yes/no", with nothing added to -1.
      Archive: control.py (N32).
- [ ] ADAPT prints no compound verdict, no drift criterion, no SD-across-
      objectives criterion and no RECOVERED at -0.85. Archive: control.py
      (i), (ii), RECOVERED.
- [ ] Every row's per-cell rate verdict is "one-sided 95% upper bound
      (95th percentile) <= -1", nothing added. No -0.85, no 97.5th
      percentile labelled one-sided. Archive: ten scripts plus control.py.
- [ ] BETA-ISO and BETA-ANI use the -1 rule, not abs(slope + 1) < 0.15.
- [ ] N_vis and the P1.2 beta threshold carry no verdict; no N_vis window
      selection; LAWPANEL slopes on the full grid.
- [ ] No counts at tolerances 0.10, 0.15, 0.20; nothing added to -1.
- [ ] No COLLAPSE_SD and no MECHANISM_DR2 criterion in CONC/PROBEARM; no
      "law useful" R^2 criterion; no straightness verdict (the quadratic
      term is printed with its interval only).
- [ ] No hand-fixed tolerance anywhere; a comparison that survives uses
      3 x SE (rerun SE) or, for a claim of no change, the 5b margin and
      TOST.
- [ ] Any compared arm pair follows every 5a rule.
- [ ] Any interval for the onset resamples realizations within cells, not
      objectives. Onsets are printed per d with intervals; no trend in d.
- [ ] Before each fit, every E on the window is checked finite and > 0; a
      realization failing it is handled by item 3's realization rule for
      that window, with the bad-point count printed.
- [ ] Not computed as verdicts: cliff (i), (ii), map informative, crossed
      small_A, audit A2, partm P-M2 to P-M4; their quantities are printed
      with intervals only.
- [ ] mechanism's three R^2 values, regime P6.3 and ess_surface P1.3 are
      printed with no verdict.
- [ ] ESS printed with no SATURATED label; no "outside FKR hypothesis"
      label; regions labelled "r < 1" and "r >= 1", never "in",
      "admissible" or "inside the hypothesis".
- [ ] No comparison and no "paired" for ADAPT fixed/adaptive,
      BETA-ISO/BETA-ANI or CONC/PROBEARM.
- [ ] Every tolerance in the docstring is 3 x SE with the SE's source named.
- [ ] The equivalence margin is 3 x S, S the median of the per-cell
      S-slope bootstrap SDs over the cells of SIGMA, ANISO, RMAP, CLIFF
      and ONSET, printed before any gap is computed: the log order shows
      margin before gaps.
- [ ] Before any gap, the median per-cell SD is printed per beta design in
      the pool (calprec2, probe, and any design a joining row brings), and
      the revisit condition is evaluated: REVISIT iff any pairwise ratio
      of group medians > 1.5; on REVISIT the script prints "MARGIN REVISIT
      REQUIRED", computes no gap in the pooled rows and stops.
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

The sixth message decided the six points that remained. The fourth to
sixth passes applied F1 to F6 as following from fixed rules, and left:

1. F7: whether a contrast between two levels of an ordered variable (d =
   2 against d = 40; tau_0 contrasts) is a comparison or a monotonicity
   claim in a costume, given S4's ruling on the onset. Then the list of
   pre-specified contrasts in the concentration-dependence rows.
2. F8: which rows are "the concentration-dependence rows", and what "the
   reference-adequacy reporting" consists of.
3. F9: REFSIZE's window (the common J <= 1250, or the full grid) and its
   J_inf extrapolation, form and interval.
4. F4 and F2 were applied on Claude's reading. They need a word only if
   Rahul meant otherwise.

## What the rerun script needs that this file does not yet give

From this file:
- F7, F8 and F9 above. Without them the script does not know which
  comparisons to compute in the rows the paper's main text rests on.

From outside this file (state as of 2026-10-16, from the repository):
- calprec2's beta table, calprec2_beta.csv, written by its finalize step
  after all 26 long shards (0 to 25). Run folders for shards 0 to 6 are
  under runs/ (shard 2 in two folders), and shard 7's log is uncommitted,
  so the table does not exist yet.
  CONC, TAU8, SIGMA and ANISO cannot run without it.
- The trajectory seed-key layout: the fields of the key (row, module,
  objective, d, law, tau_0, r or sigma or beta, J_inf, T, arm, rep), with
  the diffusion coordinate omitted (5a), an ENTROPY, and trajectory kinds
  that avoid 31 to 35 (calprec2), 51, 61 to 67 and 71 (this file's
  bootstrap kind). Item 3's bootstrap key is defined from it, so it must
  be fixed first.
- The archived-beta rows: how each row's archived beta is reproduced by
  importing the archived module (rule 4), checked against costprobe2's
  P0 constants.
- Already in place, no action: the Kaggle determinism gate passed
  (ENVIRONMENT.md line 49); peak RSS at J_inf 100000 was measured
  (SESSION_STATE.md line 206, RERUN_PLAN F6).
