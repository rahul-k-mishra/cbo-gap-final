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
was run again against it (fourth to sixth passes). A seventh message
fixed the pre-specified contrasts (item 7), the concentration rows, the
reference-adequacy reporting and REFSIZE's window, marked "(seventh
message)"; the audit was run again (seventh to ninth passes). An eighth
message fixed the sign rule, two more contrasts, the contrast scope and
the seed-key coordinates, marked "(eighth message)"; the audit was run
again (tenth to twelfth passes), and the seed-key layout is drafted in
its own section for Rahul's approval. A ninth message decided H1 to H3
and approved the layout with one change, marked "(ninth message)"; the
audit was run again (thirteenth to fifteenth passes). A tenth message
put J1 to J5 in scope, marked "(tenth message)", specified in section 8;
the audit was run again (sixteenth to eighteenth passes). An eleventh
message decided K1 and K2, marked "(eleventh message)"; the audit was run
again (nineteenth to twenty-first passes), and the trajectory script was
written. A twelfth message decided L1 to L3, marked "(twelfth
message)"; the twenty-second pass found nothing further, and the analysis
script was written.

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
- Primary window W-full: every J in the row's grid, except REFSIZE
  (below, seventh message) (costprobe2.py lines
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

**REFSIZE's window (seventh message).** REFSIZE is the one row whose
primary window is not the full grid.
- Primary: regime.py's common cap, J <= 1250 = min(J_inf)/10, for all
  four J_inf (regime.py docstring lines 25 and 26, code lines 515 to 518).
  Rahul's reason: the comparison across J_inf is the row's whole purpose,
  and a common fitting range is what makes it a comparison rather than an
  artefact. The cap is fixed by the design, not chosen from the data.
- Sensitivity column: the full grid. For this row the full grid of a cell
  is the J10b grid capped at that cell's J_inf/10 (regime.py line 329, and
  RERUN_PLAN row EXP-REFSIZE: "J10b capped at J <= J_inf/10"). Applied by
  Claude from those two sources: J_inf 12500 gives J up to 1250, the same
  as the primary window; 25000 adds 2500; 50000 and 100000 give the whole
  J10b grid.
- The J_inf extrapolation gamma(J_inf) = gamma_inf + a / J_inf is dropped.
  Rahul's reason: it is a fitted form nobody has justified, and the row's
  point is the comparison, not the limit.

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
  by scripts/ today (corrected in the tenth pass; the first list missed
  1, 2, 11, 12 and 41 to 43): 1 and 2 (calprec), 11 and 12 (refscale),
  31, 32, 33 and 35 (calprec2), 41, 42 and 43 (costprobe2), 51 (c6), 61
  (m1 and memprobe), 62 to 67 (m2 to m7). 71 is used by none. The rerun's
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
- (Thirteenth pass, applied from the ninth message's reason for sharing
  cells.) A cell shared between RMAP and ONSET (layout section) enters the
  median for S and the probe-group median once, not once per row.
  Counting it twice would treat one physical experiment as two pieces of
  evidence, which is what the ninth message's reason excludes.

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

(Ninth message.) Every contrast of item 7, and the onset, is reported
per cell and pooled over units. A pooled figure is never printed without
the statistics above. Rahul's choice; his reasons are in item 7.

Rules for the pooled figures (thirteenth pass; applied by Claude from
the ninth message's stated reason, comparability with round 1, and from
items 3 and 6 as fixed):
- The pooled point estimate is the unweighted mean of the per-unit
  estimates y_i. That is the form of round 1's Table 3: "Table 3's per-d
  entry = the mean over the 12 units at (d, tau_0)" (n30_reconstruct.py
  line 92). The 1/v_i-weighted mean y_w enters Q only, as m6_hetero.py
  defines it, and is never reported as the estimate.
- The pooled interval: each cell is resampled independently (item 3),
  the per-unit estimates and their unweighted mean are recomputed on each
  resample, and the 2.5th and 97.5th percentiles of the B means are
  taken. Shared-key cells are resampled jointly across arms (5a).
- v_i is the bootstrap variance of that unit's own estimate under the
  same resamples.
- I2 is undefined when Q = 0 (all y_i equal) or when any v_i = 0 (a unit
  whose estimate is the same in every resample, which a grid-valued onset
  can be). The script then prints "I2 undefined" with the reason and the
  unit, and prints no substitute value. This follows from rule 2: no
  number is filled in.
- Worked example (illustrative): k = 2 objectives, per-unit contrasts
  +0.04 and +0.06. Pooled estimate (0.04 + 0.06) / 2 = +0.05. If the
  first unit's v_i is 0.0004 and the second's 0.0001, y_w = (0.04 / 0.0004
  + 0.06 / 0.0001) / (1 / 0.0004 + 1 / 0.0001) = 700 / 12500 = +0.056,
  which is used in Q and never printed as the estimate.

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

## 7. Pre-specified contrasts and the rows that make them (seventh message)

**The line between a contrast and a monotonicity claim (Claude's line,
adopted by Rahul).** The difference is pre-specification.
- A contrast between two named levels, fixed in the docstring before the
  run, is a comparison under item 1.
- A claim that a quantity rises, falls or moves across a variable's levels
  is a monotonicity claim under A4 and is not made.

Rahul records that his sixth-message onset ruling (S4) was wrong as
stated: applied consistently, it would have deleted Table 3 and the tau_0
contrasts, which are the main text. Restated: pre-specified two-level
onset contrasts are made; any "onset falls with d" claim is not.

**Rows (seventh message).**
- Concentration-dependence rows: CONC, PROBEARM, TAU8 and GEOM.
- Supplementary: SYNTH and NAMED report estimates and intervals, with no
  contrast.
- Reference-adequacy reporting: REFSIZE, plus calprec2's per-cell
  adequacy verdict, C5m, D1 and both reference medians (calprec2.py lines
  157 to 196). That is the reference-estimability result. It is reported
  as measured, per cell, with no pooled verdict.

**The contrasts (seventh message; scope, sign and the fifth and sixth
contrasts from the eighth message; the seventh contrast, the onset
statistic and per-cell plus pooled reporting from the ninth message). No
other contrast is computed**, apart from the quantities of section 8,
added in the tenth message (J1 to J5).

Sign rule (eighth message), one rule for all contrasts: second level
minus first, with the levels listed in the docstring so that the
subtrahend is the baseline. Rahul's principle: the baseline is the
standard or easiest condition, and the contrast measures departure from
it. Rahul records that his seventh-message wording "A against B" was
ambiguous and, read as A - B, would have given d2 - d40, the reverse of
Table 3.

1. Dimension, every concentration row (CONC, PROBEARM, TAU8, GEOM):
   S-slope(d = 40) - S-slope(d = 2) where both exist, otherwise highest d
   minus lowest d in the row's grid. Matches Table 3's sign (M2: d = 2
   -1.0655, d = 40 -1.0113, change +0.0542).
2. Target, every concentration row and every paired row with more than
   one tau_0: S-slope(tau_0 0.01) - S-slope(tau_0 0.5) where both exist,
   otherwise tightest minus loosest.
3. Diffusion, the five paired rows: anisotropic - isotropic, per cell
   (5a).
4. Law, CONC and PROBEARM only (eighth message): S-slope(mix-0.1) -
   S-slope(centred). Rahul records that the seventh message's law rule
   ("the rows with a law list") over-reached.
5. Reference size, REFSIZE only (eighth message): S-slope(J_inf 100000) -
   S-slope(J_inf 12500), on the common J <= 1250 window. Rahul records
   that he should have listed it in the seventh message, since the
   comparison is the row's purpose.
6. Onset, ONSET only (eighth message): onset(d = 80) - onset(d = 5),
   highest minus lowest by the sign rule, within each diffusion arm. The
   onset statistic is defined below (ninth message, H3).
7. Interaction, every concentration row (CONC, PROBEARM, TAU8, GEOM)
   (ninth message): change(tightest) - change(loosest), where change(tau)
   is contrast 1 computed at that tau_0. In CONC and PROBEARM: [S(d40,
   0.01) - S(d2, 0.01)] - [S(d40, 0.5) - S(d2, 0.5)]. In TAU8 and GEOM:
   [S(d40, 0.01) - S(d5, 0.01)] - [S(d40, 0.3) - S(d5, 0.3)]. Per
   (objective, law) in CONC and PROBEARM, per objective in TAU8 and GEOM.

No contrast in ADAPT, LAWPANEL, HORIZON, SYNTH, NAMED, BETA-ISO or
BETA-ANI (eighth message for the first three). ADAPT reports its bound
and interval only. LAWPANEL and HORIZON are supplementary, like SYNTH and
NAMED, and report estimates and intervals with no law contrast.

Worked example (illustrative numbers): CONC, one cell group at tau_0
0.5, centred: S-slope -1.06 at d = 2 and -1.01 at d = 40, so the
dimension contrast is -1.01 - (-1.06) = +0.05. At d = 40, tau_0 0.5
-1.01 and tau_0 0.01 -0.85 give a target contrast of -0.85 - (-1.01) =
+0.16.

**Undefined contrasts.** Read from costprobe2.py GRID, none is undefined
in a row it applies to.

**Per row (read by Claude from costprobe2.py GRID).**

| Row | Contrasts |
|---|---|
| CONC, PROBEARM | d40 - d2; tau 0.01 - 0.5; mix-0.1 - centred; change(0.01) - change(0.5) |
| TAU8, GEOM | d40 - d5 (no d 2); tau 0.01 - 0.3 (no 0.5); change(0.01) - change(0.3) |
| SIGMA, ANISO | aniso - iso per cell; tau 0.01 - 0.1, per arm |
| RMAP | aniso - iso per cell; tau 0.01 - 0.5, per arm |
| CLIFF | aniso - iso per cell (single tau_0) |
| ONSET | aniso - iso per cell; onset d80 - d5, per objective and pooled |
| REFSIZE | J_inf 100000 - 12500 on J <= 1250 |
| ADAPT, LAWPANEL, HORIZON, SYNTH, NAMED, BETA-ISO, BETA-ANI | none |

The target rule's scope follows from the two messages together: the
seventh message's "every row with more than one tau_0", less ADAPT (no
contrasts) and SYNTH and NAMED (supplementary), leaves the concentration
rows plus SIGMA, ANISO and RMAP. Applied by Claude.

**How each contrast is computed (follows from items 1 to 3; applied by
Claude).**
- Every contrast is on S-slope (item 0), on the primary window (item 2;
  REFSIZE's common cap), with a two-sided 95% percentile interval and the
  DIFFERENCE rule of item 1. No contrast here is an equivalence claim, so
  none touches the margin pool of 5b.
- (Eighth message.) The trajectory seed key includes tau_0 and the law,
  so cells that differ in tau_0 or in law are independent. Diffusion is
  the single exception, where sharing is deliberate and 5a governs it.
  Rahul's reason: the target is the quantity under study in the
  concentration rows, and sharing increments across targets would make a
  contrast's variance depend on a coupling with no physical meaning in
  the claim; the same holds for law. This is Rahul's judgement, and it
  costs the variance reduction that sharing would give.
- Applied by Claude, from "diffusion is the single exception": every
  other coordinate is in the key too (d, J_inf, T, r, sigma, beta, arm,
  row), so contrasts 1, 2, 4, 5, 6 and 7 are all between independent cells.
  Each is resampled independently in each cell (item 3) and never called
  "paired". The seed-key layout section below lists the fields.
- Precision guide (eighth message): for these independent contrasts,
  Rahul names M5's independent-arm half-widths as the relevant guide
  (per-cell median 0.0668, pooled median 0.0533). Two notes by Claude.
  M5 measured the diffusion gap on archived probe-beta designs, so it
  guides the other contrasts by analogy only. And there are no "paired
  figures" for 5a to set against it: the variance reduction from shared
  keys has never been measured (5a, Judgement). M7 measured by-index
  differencing of independent arms, which is a different thing.
- Where a contrast involves a tau_0 below 0.1, it is also printed on the
  W-ge window as a sensitivity line with no verdict, as item 2 does for
  slopes. Round 1's Table 3 W-ge value (+0.0775) is a contrast of that
  kind.
- REFSIZE's contrast 5 gets no sensitivity line on the full grid. Its
  sensitivity windows differ by J_inf (up to 1250 at 12500, the whole
  J10b grid at 100000), which is the confounding Rahul's reason for the
  common cap rules out. Applied by Claude from that reason.

**Resolved in the eighth message.** 7-S (sign rule), 7-A (contrast 5),
7-B (no contrasts in ADAPT, LAWPANEL, HORIZON), 7-C (contrast 6), G6
(tau_0 and law in the key).

**Decided in the ninth message: H1, H2, H3.**

H1, the interaction (contrast 7 above).
- Raised by the tenth pass: round 1's "tau_0 contrasts" were interaction
  contrasts, not target contrasts. scripts/n30_reconstruct.py lines 146
  to 148 and 337 to 338 (from the archive's construction): change(tau) =
  S(d40) - S(d2) at that tau, and CON(t1, t2) = change(t1) - change(t2);
  SEP and REGF b_dtau are of the same family. They ask whether the
  dimension effect depends on the target. Contrast 2 asks whether the
  slope depends on the target at fixed d.
- Decision: added as contrast 7, scoped to the concentration rows,
  change(tightest) - change(loosest).
- Rahul records that he omitted the interaction, and that "no other
  contrast is computed" would have deleted the quantity the abstract
  rests on.
  - Claude's note on that record (thirteenth pass, J1): the abstract's
    interaction figure (tex line 34, "+0.0305 with interval
    [+0.0123,+0.0479]" over the full grid, "+0.0073 with
    [-0.0091,+0.0227]" over the restricted one) is REGF b_dtau, the
    coefficient of log2 d x log10(1/tau_0) in an OLS fit to the twelve
    (d, tau_0) cell means (tex line 392; n30_reconstruct.py's regression
    family). Contrast 7 is the CON family of tex line 394, which is in
    the body, not the abstract. So contrast 7 restores CON(0.5, 0.01)
    and does not restore the abstract's figure. Whether b_dtau is
    computed is J1 below.
- Orientation, stated once here and once in the eventual text (Rahul's
  instruction), so that no reader sees a reversal that is only a
  convention:
  - Round 1: CON(0.5, 0.01) = change(0.5) - change(0.01). Published
    -0.0233 with [-0.1482,+0.0567] (tex line 394). N30 reproduced the
    point estimate under E=slope, W=W-ge, V=signed, and did not reproduce
    the interval (logs/n30-20261015-2201.log lines 62, 67 and 1030 to
    1031).
  - New: contrast 7 = change(0.01) - change(0.5) = -CON(0.5, 0.01). The
    same quantity in the two conventions carries opposite signs: on the
    same data, a round-1 value of -0.0233 is the new convention's
    +0.0233.
  - Two further limits on comparing the numbers, from the logs and the
    design, not from the orientation (Claude):
    - round 1's published CON(0.5, 0.01) is the W-ge value (N30 above).
      The rerun's primary is W-full (item 2), so the round-1-comparable
      figure is the rerun's W-ge sensitivity line, which carries no
      verdict.
    - round 1's CON came from exactcal (random beta, solved on each
      realization's reference); CONC runs on calprec2 fixed betas. The
      two are the same contrast in definition, on different designs.
- Window: contrast 7 involves tau_0 0.01, so item 2's W-ge sensitivity
  line applies (eleventh pass). On that line, both changes are computed
  on each cell's own W-ge window (the 0.01 cells on J >= 100, the 0.5 or
  0.3 cells on the full grid, since J >= 1/tau_0 removes no J there).
- Worked example (illustrative numbers): CONC, one (objective, law)
  unit. S(d40, 0.01) = -0.85, S(d2, 0.01) = -1.00, so change(0.01) =
  +0.15. S(d40, 0.5) = -1.01, S(d2, 0.5) = -1.06, so change(0.5) = +0.05.
  Contrast 7 = +0.15 - (+0.05) = +0.10. Round 1's CON(0.5, 0.01) on the
  same numbers would be +0.05 - (+0.15) = -0.10.

H2, per cell and pooled.
- Decision: every contrast is computed per cell and pooled over units,
  and both are reported. Per cell is primary: it is where the
  measurement lives and where heterogeneity is visible. The pooled
  figure is reported beside it with item 6's statistics (sd_units, I2
  and the rest), because that is the form the round-1 numbers took and
  comparability matters.
- Reporting both is Rahul's choice. The pooled figure is never reported
  without its heterogeneity.
- Units (item 6): (objective, law) in CONC and PROBEARM for contrasts 1,
  2 and 7; the objective alone for the law contrast 4 (law is the factor
  contrasted) and in every other row. The pooled diffusion gap is
  reported the same way, unit the objective, within each (row, d, r,
  tau_0 and the row's other coordinates).
- "Per cell" for a contrast means per unit: the contrast within one
  (objective, law) or one objective, every other coordinate fixed.
- How the pooled figure is formed, and when I2 is undefined: item 6,
  "Rules for the pooled figures".

H3, the onset statistic.
- Decision: computed per objective, and pooled per (diffusion, d) as the
  archive did; both reported under the rule of H2. Per objective is
  primary.
- The estimator (regimemap.py lines 496 to 505, retyped; see the
  positive control below): x = log of ONSET's r grid (0.75, 1.0, 1.25,
  1.5, 2.0, 3.0). For y, the S-slope at each r, fit by least squares y =
  a + b1 x + b2 max(x - c, 0), for each candidate c in x without its
  last value, and take the c with the smallest residual sum of squares.
  The onset is exp(c), so it is one of 0.75, 1.0, 1.25, 1.5, 2.0. Ties go
  to the smaller c (Python's min returns the first minimum, the archive's
  rule).
  - Per objective: y is that objective's S-slope at each r.
  - Pooled: y is the mean over OBJ3 of the per-objective S-slopes at each
    r, the archive's ms (lines 436 to 438). The pooled onset is the onset
    of the mean curve. It is not the mean of the three per-objective
    onsets. Item 6's statistics are computed from the per-objective
    onsets, with that difference stated beside them.
  - Interval: item 3, resampling realizations within each cell, never the
    archive's pool over objectives (second pass, P4). On each resample
    the S-slopes are recomputed and the onset refitted.
  - The onset takes grid values only, so its interval endpoints are grid
    values, and a unit whose onset never moves under resampling has v_i =
    0 (item 6: I2 is then undefined).
  - Worked example (illustrative numbers): y = (-1.04, -1.03, -1.04,
    -1.06, -0.99, -0.94) at r = 0.75 .. 3.0. If c = log 1.5 gives the
    smallest residual sum of squares of the five candidates, the onset is
    1.5. Contrast 6 for an objective with onset 1.0 at d = 80 and 1.5 at
    d = 5 is 1.0 - 1.5 = -0.5.
- Rule 4 does not cover this estimator: bp is a function nested inside
  regimemap.py's main (lines 499 to 505) and cannot be imported. The
  positive control below replaces the import (ninth message).
- Positive control (Claude's proposal of the eighth message, adopted by
  Rahul and not optional): before the retyped estimator is used for
  anything, the script recomputes the archived onsets from
  zenodo-v1/regimemap_D_real.csv and stops if they do not match.
  - Input: the rows with part D. For each (diffusion, objective, d, r,
    tau 0.1), the mean of the archived slope column over rep (the
    archive's rec mean, a nanmean); then the mean over OBJ3 at each r
    (ms); then the retyped estimator on that curve.
  - Reference: the archive holds no onset values, only the slopes. The
    archived onsets are the r_onset column of the submitted manuscript's
    onset table, zenodo-v1/sn-article.tex lines 608 to 612 (iso) and 615
    to 619 (aniso): ten values, one per (diffusion, d), printed to two
    decimals.
  - Criterion: every one of the ten recomputed onsets equals the
    table's value exactly (the onset is a grid value, so no tolerance
    applies). Any mismatch: the script prints the cell, both values and
    "ONSET CONTROL FAILED", and stops before any trajectory runs.
  - The sixty per-r means are printed beside the table's values (three
    decimals) as a diagnostic, with no stop: a disagreement in the third
    decimal can come from rounding.
  - The control checks the point estimate only. The archive's interval
    used 300 panel resamples with a fixed seed and is not reproduced or
    compared.
  - Worked example: iso, d = 40. The table gives r_onset 1.25 (tex line
    611). If the recomputed onset is 1.25, that cell passes; if it is
    1.0, the run stops with "ONSET CONTROL FAILED iso d 40: computed 1.0,
    archived 1.25".

---

## 8. Main-text estimands added in the tenth message (J1 to J5)

A tenth message put J1 to J5 in scope, marked "(tenth message)". Runtime
is not a constraint (Rahul).

**The estimand/shape line (Claude's line, adopted by Rahul in the tenth
message).** A regression coefficient fixed in the docstring before the
run and reported with its interval is an estimand. What A4 forbids is
the text claiming a shape: "rises with d", "falls with r". The number is
reported; a sentence asserting a direction is not written. This completes
item 7's line between a contrast and a monotonicity claim.

**No round-1 interval is reused (tenth message).** No round-1 interval
for any quantity in this section, or in item 7, is carried into the new
paper. Round 1's intervals for these quantities resampled realizations
shared across d, tau_0 and r: "a bootstrap over the 36
objective-realization pairs shared across all five dimensions" (tex line
648), "paired on the 36 objective-realization indices and resampled
jointly across the panel" (tex line 545), "paired on the same twelve
objective-law cells" (tex line 394). The approved key puts d, tau_0 and r
in the key, so no realization is shared across them. Every interval here
resamples realizations within each cell independently (item 3) and
recomputes the statistic from the per-cell resamples.

**Common rules for every quantity in this section** (from items 0 to 3,
6 and 7; applied by Claude):
- Input: per-cell S-slopes (item 0).
- Windows: W-full primary; where any cell entering the quantity has tau_0
  < 0.1, the quantity is also computed with each cell's S-slope on its
  own W-ge window, as a sensitivity line with no verdict (item 2).
- Interval: two-sided 95% percentile over B = 10000 resamples, each cell
  resampled independently with its own bootstrap key; shared cells
  (layout section) use their one key in every row.
- Verdict: DIFFERENCE iff the 95% interval excludes zero, otherwise "95%
  interval contains 0" (item 1). No other verdict.
- Per unit and pooled (H2): each quantity is computed per unit (item 6's
  unit for the row) and pooled as the unweighted mean of the per-unit
  values, with item 6's statistics.
- For an OLS coefficient the pooled value equals the coefficient of the
  same OLS on the per-cell means pooled over units, because OLS is linear
  in the response and every unit has the same design. That is round 1's
  form (n30_reconstruct.py: "OLS of the 12 cell means"). If a unit lacks
  a cell (a dropped realization does not remove a cell; a cell with no
  finite slope does), the unit is excluded from that coefficient, named,
  and the reduced k printed.
- No shape sentence (the line above).

### 8.1 J1: REGF, the CON pairs and SEP (tenth message)

**REGF.** Rows and design:
- CONC and PROBEARM: the 4 d (2, 5, 10, 40) x 3 tau_0 (0.5, 0.1, 0.01)
  cells of each (objective, law) unit, per unit and pooled over the
  twelve units of each row.
- TAU8 and GEOM: the 3 d (5, 10, 40) x 8 tau_0 (0.3, 0.2, 0.1, 0.07,
  0.05, 0.03, 0.02, 0.01) cells of each objective.
- Model (tex line 392; n30_reconstruct.py design()): OLS of the cells'
  S-slopes gamma on [1, log2 d, log10(1/tau_0), log2 d x log10(1/tau_0)].
  Response gamma, not Delta, as round 1's REGF and REGR (N30 log lines
  1034 to 1041: resp=gamma).
- Reported: b_d, b_tau and b_dtau, each with its interval and the
  DIFFERENCE rule, on W-full (primary) and on W-ge (sensitivity), in all
  four rows (every row has tau_0 < 0.1).
- Round-1 reference: REGF b_dtau +0.0305 was reproduced on W-full; REGR
  b_d +0.0069, b_tau -0.0288 and b_dtau +0.0073 on W-ge (N30 log lines
  1034 to 1041). Round 1 did not report REGF's b_d and b_tau.
- Worked example (illustrative numbers): one CONC unit whose twelve
  S-slopes are exactly gamma = -1.06 + 0.01 log2 d + 0.02 log10(1/tau_0)
  + 0.005 log2 d log10(1/tau_0) gives b_d = +0.01, b_tau = +0.02, b_dtau
  = +0.005. If the 95% interval of b_dtau is [-0.004, +0.014], it is
  printed as "95% interval contains 0", and no sentence says the
  interaction rises or falls with d.

**The three CON pairs.** Rahul records that contrast 7 is one CON pair,
that covering only one was his oversight, and that the other two are now
added; round 1's reason for reporting all three (tex line 394, "rather
than reporting the first alone") was sound.
- Sign rule (item 7): tighter target minus looser, so each pair is the
  negative of round 1's orientation, as for contrast 7.
- CONC and PROBEARM, per (objective, law) and pooled:
  - P1 = change(0.1) - change(0.5) = -CON(0.5, 0.1);
  - P2 = change(0.01) - change(0.5) = -CON(0.5, 0.01) = contrast 7;
  - P3 = change(0.01) - change(0.1) = -CON(0.1, 0.01).
- TAU8 and GEOM, per objective and pooled, with the loosest target 0.3
  in place of 0.5 as contrasts 2 and 7 do: change(0.1) - change(0.3);
  change(0.01) - change(0.3) (= contrast 7); change(0.01) - change(0.1).
  change(tau) = S(d40, tau) - S(d5, tau). Applied by Claude from the
  "otherwise loosest" substitution already used by contrasts 2 and 7.
- Both windows. Round-1 references, in round 1's orientation (N30 log
  lines 1028 to 1033): CON(0.1, 0.01) -0.0182 and CON(0.5, 0.01) -0.0233
  reproduced on W-ge; CON(0.5, 0.1) -0.0050 on W-full.
- Each pair is printed once with both orientations, as contrast 7 is.

**Naming of the pairs (eleventh message, from K1).** CON keeps round 1's
definition, CON(t1, t2) = change(t1) - change(t2); under the sign rule
the arguments are written tighter first. The three pairs are reported as
CON(0.1, 0.5), CON(0.01, 0.5) and CON(0.01, 0.1) (in TAU8 and GEOM:
CON(0.1, 0.3), CON(0.01, 0.3), CON(0.01, 0.1)). Contrast 7 is CON(0.01,
0.5) (CON(0.01, 0.3) in TAU8 and GEOM). Round 1's CON(0.5, 0.01) is the
same function with its arguments reversed. Applied by Claude from the
eleventh message's "CON(0.01, 0.1)".

**SEP is retired (eleventh message, K1).** Rahul's decision: both
quantities are reported, and neither is called SEP.
- Round 1's SEP has no definition in the manuscript (n30_reconstruct.py
  docstring: "The text does not define it"). Its published +0.1940
  reproduces only as the third CON pair, c(0.01) - c(0.1) on W-full (N30
  log lines 280 to 283 and 1046). The text's wording ("the tightest
  target appeared to differ from the moderate ones", tex line 394)
  describes the mean-based quantity instead. The label covered two
  different things, and is retired so the ambiguity cannot recur.
- The third CON pair is reported as CON(0.01, 0.1), never as SEP. It is
  already computed under J1.
- The mean-based quantity is added with its own name, TMM (tight minus
  moderate mean; name chosen by Claude):
    TMM = change(0.01) - (change(0.5) + change(0.1)) / 2
  in CONC and PROBEARM, and, by the loosest-target substitution,
    TMM = change(0.01) - (change(0.3) + change(0.1)) / 2
  in TAU8 and GEOM. Per unit and pooled, both windows, interval and
  DIFFERENCE rule, as every section-8 quantity.
- Worked example (illustrative numbers): change(0.5) = +0.05, change(0.1)
  = +0.06, change(0.01) = +0.15. TMM = 0.15 - (0.05 + 0.06) / 2 = +0.095.
  CON(0.01, 0.1) = 0.15 - 0.06 = +0.09.

### 8.2 J2: severity and its trend (tenth message)

- Row: ONSET (r grid 0.75, 1.0, 1.25, 1.5, 2.0, 3.0; tau_0 0.1; d 5,
  10, 20, 40, 80; OBJ3; both diffusions).
- Severity S(1, 3) = S-slope(r = 3) - S-slope(r = 1), per (diffusion,
  objective, d) and pooled over OBJ3 per (diffusion, d). The baseline is
  r = 1, the boundary, so the sign rule gives the archive's orientation
  (tex line 685: "Positive values mean the exponent has flattened toward
  zero"). Sensitivity: S(0.75, 3) = S-slope(r = 3) - S-slope(r = 0.75),
  the same way, labelled boundary-spanning.
- Trend: per diffusion, the OLS slope of S(1, 3) on log2 d over the five
  d, with intercept; per objective and pooled (the pooled trend equals
  the OLS on the pooled severities). The same for S(0.75, 3), as
  sensitivity. Each with its interval and the DIFFERENCE rule.
- Cells r = 1 and r = 3 have different keys (r is in the key), so the
  two ends of a severity are independent cells. Cells at d 10 and 40, r
  1.0 and 3.0, are shared with RMAP (layout section); that changes no
  computation.
- tau_0 is 0.1, so no W-ge line.
- Round-1 reference (tex lines 648 and 38): isotropic +0.1440 per
  doubling, [+0.1232,+0.1637]; anisotropic -0.0019, [-0.0302,+0.0270].
  The interval is not reused (above).
- Worked example (illustrative numbers): one objective, isotropic,
  S(1, 3) = 0.09, 0.07, 0.21, 0.46, 0.61 at d = 5, 10, 20, 40, 80.
  log2 d = 2.32, 3.32, 4.32, 5.32, 6.32, so the OLS slope is the
  covariance over the variance of log2 d, reported per doubling. The
  text prints the coefficient and its interval; it does not say the
  severity "grows with d".

### 8.3 J3: the RMAP panel model (tenth message)

- Row: RMAP. A panel is one (diffusion, d): 4 tau_0 (0.5, 0.1, 0.03,
  0.01) x 5 r (0.5, 1.0, 1.5, 2.0, 3.0) = 20 cells per objective.
- Model (tex lines 540 to 545): Delta = -1 - gamma, fitted by OLS as
  Delta = a + b1 g(tau_0) + b2 h(r) + b3 g h, with g = log10(0.5/tau_0)
  and h = log2(r/0.5), so both vanish at (0.5, 0.5). Response Delta, as
  archived. A positive b means a larger deficit, a flatter slope.
- Reported: b1, b2, b3 per (diffusion, d), per objective and pooled over
  OBJ3, each with its interval and the DIFFERENCE rule, on W-full and on
  W-ge (tau_0 0.03 and 0.01 are below 0.1).
- The three-of-four counting rule (partm P-M2) stays dropped (sixth
  message, confirmed in the tenth). No count of panels is made.
- Worked example (illustrative numbers): a panel whose twenty Delta are
  exactly 0.02 + 0.10 g + 0.05 h + 0.01 g h gives b1 = 0.10, b2 = 0.05,
  b3 = 0.01. At (0.01, 3.0), g = log10(50) = 1.699 and h = log2(6) =
  2.585.

### 8.4 J4: the onset against r = 1 (tenth message)

- For each onset (H3: per (diffusion, objective, d), and pooled per
  (diffusion, d)), print its 95% interval and "contains 1: yes/no".
- Report the count with its denominator: "k of 30 per-objective
  intervals contain 1" (2 diffusions x 5 d x 3 objectives) and "k of 10
  pooled intervals contain 1". Also per diffusion.
- That is a description of where the intervals fall, not a claim that
  the onset is at 1 (Rahul). A6 holds: an interval containing 1 does not
  show the onset is at 1.
- The onset is grid-valued, so an interval such as [1.00, 1.00] or
  [1.25, 2.00] has grid endpoints; "contains 1" means lo <= 1 <= hi.
- Worked example: intervals [1.00, 2.00] (contains 1), [1.25, 2.00]
  (does not), [1.00, 1.00] (contains 1). Count: 2 of 3.

### 8.5 J5: the finite-J concentration audit (tenth message)

Rahul's framing: the reference-estimability result in new form, in the
main text.

**Which rows the grid needs: none.** Round 1's audit (zenodo-v1/finitej.py)
ran no trajectory. It redrew each realization's initial ensemble from its
seed and beta and computed the initial ESS fraction of each nested
subensemble. The rerun draws every realization's initial ensemble anyway.
So the audit is computed from the rerun's own seeds and betas, with no
new cell, no new row and no trajectory. Nothing is written into the
grid.

**Rows it covers (Claude's reading, for Rahul to reverse if wrong).** The
concentration rows CONC, PROBEARM, TAU8 and GEOM, whose dimension
contrast the audit checks, as round 1's covered exactcal's. Each at its
own betas: calprec2 betas in CONC and TAU8, archived probe betas in
PROBEARM and GEOM.

**Cost: not measured.** The audit adds no trajectory; it adds one redraw
of the (J_inf, d) initial ensemble per realization and one log-ESS per
nested J. costprobe2's projection covers trajectories only and gives no
figure for it, and round 1's logs_finitej.log records no time. The
script prints the audit phase's wall time and peak RSS.

**Computation (rule 4: everything imported).**
- For each realization: rng = default_rng(SeedSequence(key)), then the
  module's own first draw: mechanism.draw_initial(rng, J_inf, d,
  objective, law) (mechanism.py line 222); for boundary.py and law.py the
  inline line X0 = rng.standard_normal((Jinf, d)) + x* (boundary.py line
  181, law.py line 452), checked against the module source as calprec2's
  V2 does.
- fv = the module's objective on X0; ratio(J) = finitej.ess_frac(fv[:J],
  beta) / tau_0 for each J of the row's grid; ref = finitej.ess_frac(fv,
  beta) / tau_0 (zenodo-v1/finitej.py lines 133 to 138, imported).
- Identity check F1 (replaces round 1's P-F1, which required the
  reference ratio to be 1.000; under a fixed beta it is not 1 by
  design): each module's one_realisation returns the reference's initial
  log-ESS (mechanism le0, line 242; boundary les[0], line 204; law
  les[0], line 475). The redrawn log-ESS at J_inf must equal it to within
  1e-12 relative, the tolerance of calprec2's E1. A failure prints the
  key and "F1 FAILED" and stops the audit.

**Reported.**
- Per cell and J: mean, SD, 5th and 95th percentiles of ratio(J) over
  realizations (finitej.py's P-F2 form), and the reference ratio.
- The attainability floor: where J tau_0 < 1, ratio(J) >= 1/(J tau_0)
  holds by construction (ESS >= 1); such J are flagged "floor", as tex
  line 587 describes.
- The dimension difference, the check that matters (finitej.py P-F3):
  ratio(J; d40) - ratio(J; d2) at each (tau_0, J), per unit and pooled
  (CONC, PROBEARM: unit (objective, law), d40 - d2; TAU8, GEOM: unit
  objective, d40 - d5), each with its 95% interval and the DIFFERENCE
  rule.
  - Sign: second level minus first (item 7). Round 1 printed d2 - d40;
    the new figure is its negative. Shown once in both orientations, as
    for contrast 7.
  - Count, as J4: "k of n pooled intervals exclude 0", per row, with n
    the number of (tau_0, J) pairs. Round 1's compound P-F3 PASS/FAIL is
    not inherited: it is a pass/fail over many intervals, of the kind
    item 4 dropped. Applied by Claude.
- Worked example (illustrative numbers): CONC, tau_0 0.01, J = 40. The
  floor is 1/(40 x 0.01) = 2.5. Mean ratio 2.6 at d = 2 and 3.4 at d =
  40 gives a difference of +0.8 (round 1's orientation: -0.8).

**The per-J-beta experiment, perjcal (eleventh message, K2: in
scope).** The abstract's second result also rests on "a dedicated
experiment that controls finite-ensemble concentration exactly, at the
cost of one inverse temperature per ensemble size" (tex line 36). That is
perjcal.py (tex lines 591 to 593; zenodo-v1/perjcal.py,
perjcal_real.csv), not the audit.
- perjcal is a different estimand from the fixed-beta results, as the
  archive itself says ("The fitted exponent is a different estimand ...
  the two should not be pooled or compared as if they were the same
  quantity", perjcal.py docstring; tex line 591, "It is a different
  estimand and we do not pool it with the rest of the paper"). It is
  reported separately and never pooled with them (Rahul).
- Its rows need trajectories. Rule 6: no design whose cost and peak RSS
  are unmeasured. scripts/perjcalprobe.py times one call of the archived
  perjcal.one_J for every unit of perjcal's archived design and projects
  its cost. Rahul approves the rows only after seeing that projection.
- Until then perjcal is in no grid and in no rerun script. Its analysis
  criteria are listed under "Decisions still needed", to be decided with
  the rows.

**Correction to the fifteenth pass's J5 (Claude's error).** J5 named "the
whole-run experiment, tex line 398". Tex line 398 is "Holding
concentration for the whole run", the beta re-solved at every step: that
is control.py, the ADAPT row, already in the grid. The experiment J5
should have named is perjcal (above).

---

## Trajectory seed-key layout (approved in the ninth message, with one change)

Drafted by Claude at the eighth message's request. It implements the
eighth message's rule that every coordinate except diffusion is in the
key, and items 3 and 5a. Rahul approved it in the ninth message with one
change: cells that appear identically in two rows are run once and
shared, not run independently in each row. The change is applied below
(field 3 and "Shared cells").

**Constants.**
- ENTROPY 20261016. Entropies used by scripts/ today: 20261009 (calprec,
  refscale), 20261010 (calprec2, costprobe2), 20261011 (c6, memprobe) and
  20261015 (measlib). 20261016 is used by none.
- Kind 81 for trajectories (unused, see item 3's list); kind 71 for the
  bootstrap (item 3).

**The key, all integers, in this order.**

| # | Field | Encoding |
|---|---|---|
| 1 | ENTROPY | 20261016 |
| 2 | kind | 81 trajectory, 71 bootstrap |
| 3 | row | index in costprobe2.py ROW_ORDER of the cell's owner row (see "Shared cells") |
| 4 | module | index in costprobe2.py MODULES |
| 5 | objective | index in costprobe2.py OBJ_NAMES |
| 6 | d | the integer |
| 7 | law | index in costprobe2.py LAWS |
| 8 | tau_0 | round(tau_0 x 1e6); 0 where the row has none |
| 9 | r | round(r x 1e6); 0 where the row has none |
| 10 | sigma (design) | round(sigma x 1e6); 0 where not a design factor |
| 11 | beta (design) | round(beta x 1e6); 0 where not a design factor |
| 12 | J_inf | the integer the cell runs with |
| 13 | T | round(T x 1e6), the value the cell runs with |
| 14 | arm | index in costprobe2.py ARMS ("", fixed, adaptive) |
| 15 | ANISO sub-arm | 0 none, 1 arm A (sigma levels), 2 arm B (r levels) |
| 16 | rep | 0 .. M - 1; absent from the bootstrap key |

- Diffusion is absent (5a), so the isotropic and anisotropic arms of a
  paired cell have the same key.
- Fields 8 to 11 use 0 for "none". 0 is never a grid value of tau_0, r,
  sigma or beta in costprobe2.py GRID, so the encoding is unambiguous.
- Field 15 exists because ANISO's two arms vary different factors. Without
  it, an arm-A cell and an arm-B cell with equal (sigma, r) would collide.
  Whether they can is not checked here; the field makes it impossible.
- Field 3 holds the owner row, not the row being reported, so a cell
  shared between rows has one key (ninth message; "Shared cells" below).
  For every cell that is not shared the owner row is its own row, and
  the key is as drafted.

**Shared cells (ninth message).** Cells that appear identically in two
rows are run once and shared. Rahul's reason: they are the same physical
experiment, and running them twice spends compute to produce two draws
of one quantity while inviting a reader to treat them as independent
evidence.

Identity, the test for sharing (Claude, from the code): two cells are the
same experiment iff they call the same archived module's one_realisation
with identical arguments other than the seed: objective, d, initial law,
diffusion, sigma, beta, dt, K, J_inf, J list, and the same M. Cells of
different modules are never shared, even where the dynamics might
coincide, because no check has shown the modules' code to be
equivalent.

Which rows share cells, read from costprobe2.py GRID and the archived
source:
- regime.py (REFSIZE, NAMED, HORIZON). A regime cell is (objective, d,
  law, tau_0, J_inf, T) (regime.py lines 316 to 333). Its beta depends on
  (objective, d, law, tau_0) only (lines 321 to 326), sigma is 0.2 and M
  is 12 in every part (lines 479 and 483), and the J list is
  J10b capped at J_inf / 10 (line 329), the whole grid at J_inf 50000.
  REFSIZE's cells at J_inf 50000 (line 513), NAMED's at d 10 and tau_0
  0.1 (line 578) and HORIZON's at law centred and T 1.0 (line 601) are
  all (objective, 10, centred, 0.1, 50000, 1.0). Shared:
  - ackley, sphere, rosenbrock: in REFSIZE, NAMED and HORIZON; owner
    REFSIZE.
  - rastrigin: in NAMED and HORIZON (REFSIZE has no rastrigin); owner
    NAMED.
  No SYNTH cell is shared: the synthetic names (regime.py line 171,
  "syn_k...") are not named objectives.
- regimemap.py (RMAP, ONSET). A cell is (diffusion, objective, d, r,
  tau_0) with beta keyed (objective, d, tau_0) (lines 337 to 344), sigma
  from sigma_of(diffusion, d, r) (line 371), J_inf 50000, the same J10
  grid and M 12 in both parts. RMAP (d 10, 40; r 0.5, 1.0, 1.5, 2.0, 3.0;
  tau_0 0.5, 0.1, 0.03, 0.01) and ONSET (d 5, 10, 20, 40, 80; r 0.75,
  1.0, 1.25, 1.5, 2.0, 3.0; tau_0 0.1) share every cell with d in {10,
  40}, r in {1.0, 1.5, 2.0, 3.0}, tau_0 0.1, for each objective of OBJ3
  and both diffusions. Owner RMAP.
- No other pair of rows uses the same module, except CONC and PROBEARM
  (mechanism.py), which differ in beta (calprec2 against probe) and so are
  not the same experiment, and are not shared.

Implementation:
- The owner row is the first row in ROW_ORDER that contains the cell.
  Field 3 of the key is the owner's index, so every row that uses the
  cell computes the same key.
- The task list is built from the set of distinct keys: each shared cell
  is run once, M realizations. Every row that uses it reads the same
  per-realization records.
- The output CSV writes each realization once, with a column listing the
  rows that use it, so the sharing is visible in the record.
- The bootstrap key is built from the same key (item 3), so a shared
  cell is resampled with the same index stream in every row that reads
  it. Its per-cell estimate on a given window is therefore the same
  number in every row.
- Rows still apply their own windows: REFSIZE fits the shared cells on J
  <= 1250 (its primary window), NAMED and HORIZON on the full grid. One
  set of trajectories, two fits.
- The script prints, per row, its cell count, the number of its cells
  owned by another row, and the owner of each; and the total number of
  distinct cells and realizations run.
- In pooled statistics across rows, a shared cell counts once: the
  margin pool of 5b (thirteenth pass). No other statistic pools across
  rows.
- Worked example: NAMED's (rastrigin, d 10, centred, tau_0 0.1, J_inf
  50000, T 1.0) has owner NAMED, and HORIZON's identical cell gets the
  same key with field 3 = index of NAMED. HORIZON's (ackley, ...) cell
  has owner REFSIZE, as has NAMED's. ONSET's (anisotropic, sphere, d 40,
  r 1.5, tau_0 0.1) has owner RMAP; ONSET's (anisotropic, sphere, d 40,
  r 1.25, tau_0 0.1) is not in RMAP and is owned by ONSET.

**How a seed is used.**
- Trajectory: numpy.random.SeedSequence(key) is passed unchanged as the
  seed argument of the archived one_realisation, which calls
  default_rng(seed) on it. This is costprobe2's construction (its
  docstring lines 96 and 97; line 958), at full width, with no
  generate_state reduction (ledger N16).
- Bootstrap: default_rng(SeedSequence(boot_key)), where boot_key is the
  key with kind 71 and field 16 removed (item 3).

**Checks the script runs before any trajectory; each stops the run.**
- K1 injectivity: no two distinct (cell, rep) tasks share a key, where a
  shared cell is one task.
- K4 identity (ninth message): every row that reads a shared cell
  passes identical arguments (the identity list above, the beta value
  included) to one_realisation; the script compares them before the run
  and stops on any difference, printing the cell and the rows.
- K2 pairing: in SIGMA, ANISO, RMAP, CLIFF and ONSET, each cell's
  isotropic and anisotropic tasks have identical keys.
- K3 printed: the seed table (key and cell) is written to the output CSV,
  as CLAUDE.md rule 5 requires.

**Shared draws (tenth pass, from the code).** 5a says the two arms draw
"the same X0 and the same Brownian increments". In sigma.py (lines 169,
170 and 190), crossed.py (174, 175, 193), cliff.py (177, 178, 196) and
regimemap.py (201, 202, 228), one_realisation draws X0 as one (J_inf, d)
standard normal array and then one (J_inf, d) array per step, in the
same order in both diffusion branches, with no other draws. So a shared
seed gives identical X0 and identical increments in both arms. The
branches differ only in how the increment is scaled. At matched r the two
arms run with different sigma (crossed.py line 168), so the paired arms
share randomness, not parameters.

**Worked example (illustrative).** ANISO, rastrigin, d 10, arm B, r 0.5,
tau_0 0.1, rep 3: (20261016, 81, [ANISO], [crossed], [rastrigin], 10,
[centred], 100000, 500000, 0, 0, 50000, 1000000, 0, 2, 3), the same for
both diffusions. Its bootstrap key is (20261016, 71, [ANISO], [crossed],
[rastrigin], 10, [centred], 100000, 500000, 0, 0, 50000, 1000000, 0, 2).
Bracketed entries are the list indices. The J_inf and T values here are
illustrative; the script takes them from the row.

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
      DIFFERENCE rule; Claude's reading, to confirm. [Rejected in S4,
      then restored in the seventh message as pre-specified two-level
      contrasts only (item 7).]
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
    [Superseded in the seventh message: Rahul records the ruling as wrong
    as stated. Pre-specified two-level onset contrasts are made; "onset
    falls with d" is not (item 7).]
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
F7 to F9 went to Rahul and were decided in the seventh message, below.

### Seventh message: F7 to F9 decided

- F7: the two-level contrast line adopted; S4 restated; the four
  contrasts fixed (item 7).
- F8: concentration rows CONC, PROBEARM, TAU8, GEOM; SYNTH and NAMED
  supplementary; reference adequacy is REFSIZE plus calprec2's per-cell
  adequacy verdict, C5m, D1 and both reference medians (item 7).
- F9: REFSIZE's common cap is primary, the full grid is its sensitivity
  column, and the extrapolation is dropped (item 2).
- F2 and F4 confirmed, and F1, F3, F5 and F6 too ("all correct").

### Seventh pass (against the seventh message)

Applied, as following from fixed rules:
G1. Each contrast's computation: S-slope, primary window, item 1's
    interval and DIFFERENCE rule, item 3's resampling (independent unless
    keys are shared, A7), and a W-ge sensitivity line with no verdict
    where tau_0 < 0.1 (item 7).
G2. SYNTH and NAMED take no target contrast. The specific rule governs
    the general wording (item 7).
G3. REFSIZE's sensitivity column is each cell's grid capped at J_inf/10,
    per regime.py line 329 and RERUN_PLAN (item 2).
G4. No contrast in item 7 is an equivalence claim, so 5b's pool stays the
    five paired rows.
G5. The rows reporting estimates without contrast (SYNTH, NAMED, BETA-ISO,
    BETA-ANI, and the factors not in item 7: r, sigma, beta, T, J_inf
    unless 7-A) still print item 4's per-cell rate verdict (F4, confirmed).

Needs Rahul's decision (item 7, NOT DECIDED): 7-S (the sign of each
contrast), 7-A (REFSIZE's J_inf comparison against "no other contrast"),
7-B (ADAPT, LAWPANEL, HORIZON reached by the wording but absent from S3),
7-C (the onset contrast's two levels).
G6. Raised by G1: whether the trajectory seed key carries tau_0. If it
    does not, cells that differ only in tau_0 share X0 and Brownian
    increments, and every target contrast becomes paired, with 5a's rules
    (A7). If it does, they are independent. That is a design choice with
    the same trade-off 5a settled for diffusion, and it changes the
    analysis. NOT DECIDED. The same question arises for law: X0 differs
    by law, but the Brownian increments could be shared.

### Eighth pass (against G1 to G6)

- G1's W-ge line applies to target contrasts with 0.01 (CONC, PROBEARM,
  TAU8, GEOM, SIGMA, ANISO, RMAP, ADAPT if 7-B) and to dimension
  contrasts in rows at tau_0 0.01, whose W-ge cells are already printed
  by item 2. No new rows.
- G3: at J_inf 12500 the sensitivity window equals the primary one, so
  that cell's sensitivity line repeats the primary value. That is what
  the definition gives, and it is printed, not suppressed.
- G6 bears on 7-B: if ADAPT's arms share keys (control.py did) and its
  target contrast is made per arm, the arms are not being compared, so
  A7 does not apply to them either way.

### Ninth pass

Nothing new. The audit stops on 7-S, 7-A, 7-B, 7-C and G6, which need
Rahul. All five were decided in the eighth message, below.

### Eighth message: 7-S, 7-A, 7-B, 7-C and G6 decided

- 7-S: one sign rule, second level minus first, the subtrahend being the
  baseline (standard or easiest condition). Rahul records that "A against
  B" was ambiguous (item 7).
- 7-A: contrast 5, J_inf 100000 - 12500 on J <= 1250. Rahul records the
  omission (item 7).
- 7-B: no contrasts in ADAPT, LAWPANEL or HORIZON. The law contrast is in
  CONC and PROBEARM only. Rahul records that the law rule over-reached
  (item 7).
- 7-C: contrast 6, onset d80 - d5 (item 7).
- G6: tau_0 and law in the seed key; diffusion the single exception;
  Rahul's judgement, at the cost of variance reduction; M5 named as the
  guide (item 7).

### Tenth pass (against the eighth message)

Applied, as following from fixed rules:
I1. The target contrast's scope is the concentration rows plus SIGMA,
    ANISO and RMAP. It follows from "every row with more than one tau_0"
    less the rows given no contrast (item 7).
I2. Every coordinate other than diffusion is in the key: d, J_inf, T, r,
    sigma, beta, arm and row. This follows from "diffusion remains the
    single exception". It makes ADAPT's arms independent, unlike
    control.py's shared seeds; no ADAPT comparison is made, so nothing
    depends on them (item 7, layout section).
I3. No full-grid sensitivity line for contrast 5, by Rahul's own reason
    for the common cap (item 7).
I4. M5 guides the independent contrasts by analogy only, and there are no
    measured paired figures to set against it (item 7).
I5. Item 3's list of used seed kinds corrected: 1, 2, 11, 12 and 41 to 43
    were missing. Kind 71 is still unused.
I6. 5a's "same X0 and same Brownian increments" was confirmed from the
    code of all four paired-row modules (layout section).

Needs Rahul's decision: H1 (interaction contrasts, round 1's CON), H2 (per
cell or pooled), H3 (the onset statistic, and the fact that bp cannot be
imported). Also the seed-key layout, which is a draft.

### Eleventh pass (against I1 to I6 and H1 to H3)

- H2 also reaches the diffusion contrast. 5a fixes it per cell. Round 1
  also pooled it over three objectives per arm (M5's L-pool-u). If the
  paper states any pooled diffusion gap, item 6 applies to it. Folded
  into H2.
- H1: if an interaction contrast is added, it involves tau_0 0.01, so
  item 2's W-ge sensitivity line applies to it, as it did to round 1's
  CON on W-ge (N30). This follows from item 2; no further decision.
- I2 and the layout: regime cells that repeat across rows run
  independently. That follows from I2 and is stated in the layout, open
  to Rahul at approval.
- Contrast 6 is at tau_0 0.1, so it has no W-ge line.

### Twelfth pass

Nothing new. The audit stops on H1, H2, H3 and the layout's approval.

### Ninth message: H1, H2, H3 and the layout decided

- H1: contrast 7, the interaction change(tightest) - change(loosest), in
  the concentration rows; the orientation against round 1's CON stated
  in the file and in the eventual text; Rahul records the omission
  (item 7).
- H2: every contrast per cell and pooled over units, both reported, per
  cell primary; the pooled figure never without its heterogeneity;
  Rahul's choice (items 6 and 7).
- H3: the onset per objective and pooled per (diffusion, d), both
  reported; the positive control against the archived onsets is
  mandatory and stops the run on failure; rule 4 does not cover the
  nested estimator and the control replaces the import (item 7).
- Layout approved, with repeated cells run once and shared (layout
  section).

### Thirteenth pass (against the ninth message)

Applied, as following from fixed rules:
L1. The pooled point estimate is the unweighted mean over units, Table
    3's form (n30_reconstruct.py line 92), from the ninth message's
    comparability reason. y_w enters Q only (item 6).
L2. I2 is printed as undefined when Q = 0 or any v_i = 0, with no
    substitute (rule 2). The grid-valued onset makes v_i = 0 possible
    (item 6).
L3. The pooled onset is the onset of the mean curve, not the mean of the
    per-objective onsets; item 6's statistics are computed from the
    per-objective onsets with that stated (item 7, H3).
L4. Onset control: the reference is the manuscript's onset table, since
    the archive stores slopes and no onsets; ten exact matches required;
    the per-r means printed as a diagnostic without a stop; the interval
    not compared (item 7, H3).
L5. Contrast 7's W-ge line computes each change on its own cells' W-ge
    window (item 7).
L6. Sharing: the identity test, the shared cells (four regime cells; the
    RMAP-ONSET overlap), owner row in field 3, check K4, one record per
    realization with its rows listed (layout section).
L7. A shared cell counts once in 5b's margin pool (5b).
L8. Two limits on comparing contrast 7 with round 1's CON, besides the
    orientation: the published CON(0.5, 0.01) is a W-ge value, so the
    comparable rerun figure is the sensitivity line; and the designs
    differ (exactcal random beta against calprec2 fixed beta) (item 7).

Needs Rahul's decision. The ninth message's record says "no other
contrast" would have deleted the quantity the abstract rests on. Checking
the abstract (zenodo-v1/sn-article.tex lines 32 to 40) against item 7
shows that contrast 7 is not that quantity, and that three more
main-text results are still excluded:
J1. The abstract's interaction is REGF b_dtau, not CON (item 7, H1 note).
J2. The abstract's third result is the severity trend, which is not a
    two-level contrast.
J3. The panel interaction b_3 of the joint sweep, which the conclusions
    open with.
J4. The onset compared with r = 1, also in the abstract's third result.
Details under "Decisions still needed".

### Fourteenth pass (against L1 to L8 and J1 to J4)

- J2 and J3 are regression coefficients over more than two levels. Item
  7's line, as drafted, separates a two-level contrast from "a claim that
  a quantity rises, falls or moves across a variable's levels", and does
  not say on which side a single pre-specified regression coefficient
  falls. J1 is the same question for b_dtau. Folded into J1 to J3.
- J2's archived interval came from "a bootstrap over the 36
  objective-realization pairs shared across all five dimensions" (tex
  line 648). Under the approved key, d is in the key, so no realization
  is shared across dimensions, and item 3 forbids resampling objectives.
  If J2 is made, its interval resamples realizations within each cell
  independently. That follows from items 3 and the layout; no further
  decision.
- The same holds for J3: the archive's "bootstrap paired on the 36
  objective-realization indices and resampled jointly across the panel"
  (tex line 545) relied on keys shared across tau_0 and r, which the
  eighth message removed. If J3 is made, its interval resamples
  realizations within cells independently.
- "The two diffusion types cross" (tex line 650): the per-cell gaps are
  computed under contrast 3. A statement that the gap changes sign
  between two r values is a claim about how the gap moves across r, which
  A4 excludes as a claim. The text can report each cell's gap and
  verdict. This follows from A4; no decision.
- The abstract's second result (the finite-J concentration audit, tex
  lines 587 to 589, and the whole-run experiment of tex line 398) is in
  no row of the
  rerun's grid (costprobe2.py ROW_ORDER). This file does not cover it.
  Whether the new paper repeats it is a scope question outside this
  file; I do not know whether it is intended. Listed as J5 for Rahul to
  confirm.

### Fifteenth pass

Nothing new. The audit stops on J1 to J5, which need Rahul. The rerun
script is not started.

### Tenth message: J1 to J5 in scope

- The estimand/shape line adopted, recorded as Claude's (section 8).
- J1: REGF in CONC, PROBEARM, TAU8 and GEOM; b_d, b_tau, b_dtau on both
  windows; all three CON pairs; SEP. Rahul records that contrast 7 is one
  CON pair and the others are now added (8.1).
- J2: S(1, 3) per (diffusion, d), S(0.75, 3) as sensitivity, and the
  trend coefficient (8.2).
- J3: b1, b2, b3 of the RMAP panel model; the counting rule stays dropped
  (8.3).
- J4: the onset intervals against 1, as a count with its denominator
  (8.4).
- J5: the finite-J audit in scope, in the main text; rows and cost to be
  reported to Rahul before anything enters the grid (8.5).
- No round-1 interval reused, and why (section 8).

### Sixteenth pass (against the tenth message)

Applied, as following from fixed rules:
M1. The pooled OLS coefficient is the unweighted mean of the per-unit
    coefficients, which equals the OLS on the pooled cell means (round
    1's form); a unit missing a cell is excluded from that coefficient
    and named (section 8, common rules).
M2. TAU8 and GEOM's three CON pairs use 0.3 for 0.5, by the substitution
    contrasts 2 and 7 already use (8.1).
M3. REGF's response is gamma and the panel model's is Delta, as each was
    archived (N30 resp=gamma; tex line 540) (8.1, 8.3).
M4. J5 needs no grid row: the audit reads the initial ensembles the rerun
    draws anyway. Its cost is unmeasured; the script prints it (8.5).
M5. The audit covers CONC, PROBEARM, TAU8 and GEOM (Claude's reading, for
    Rahul to reverse) (8.5).
M6. Round 1's P-F1 (reference ratio 1.000) cannot hold under a fixed
    beta; it is replaced by F1, the redrawn reference log-ESS against
    the value one_realisation returns (8.5).
M7. Round 1's P-F3 PASS/FAIL over thirty intervals is not inherited (the
    item 4 kind); the per-(tau_0, J) differences are reported with the
    DIFFERENCE rule and a count, as J4 (8.5).
M8. The audit's dimension difference follows the sign rule, d40 - d2, the
    negative of round 1's d2 - d40; both orientations shown once (8.5).
M9. Correction: the fifteenth pass's J5 named tex line 398 as the
    whole-run experiment. That section is control.py, the ADAPT row,
    already in the grid. The experiment the abstract names is perjcal
    (8.5).

Needs Rahul's decision:
K1. SEP's definition (8.1). N30 reproduced the published +0.1940 only
    under S1 = c(0.01) - c(0.1), which is P3, already computed. The
    text's words ("differ from the moderate ones") fit S3 = c(0.01) -
    (c(0.5) + c(0.1)) / 2, which no round-1 point estimate matches.
K2. perjcal (8.5): the per-J-beta experiment behind the abstract's
    second result. It needs trajectory rows that are not in the grid and
    whose cost costprobe2 does not project. In scope or not?

### Seventeenth pass (against M1 to M9, K1 and K2)

- No section-8 quantity is an equivalence claim, so 5b's margin pool is
  unchanged.
- J2's severity reads cells shared with RMAP at d 10 and 40; the sharing
  rule already covers it.
- If K2 is in scope, perjcal's per-J beta varies beta along the J-curve,
  which tex line 591 calls "a different estimand" and does not pool. It
  would be reported apart from every fixed-beta quantity, and its rows
  would need a cost probe that Rahul runs before they enter any grid
  (CLAUDE.md rule 6). That follows from rule 6 and the archive's own
  statement; no further decision.

### Eighteenth pass

Nothing new. The audit stops on K1 and K2. The rerun script is not
started.

### Eleventh message: K1 and K2 decided

- K1: SEP retired; the third CON pair is reported as CON(0.01, 0.1); the
  mean-based quantity added as TMM, with its formula; Rahul records that
  the label covered two different things (8.1).
- K2: perjcal in scope, a different estimand, reported separately and
  never pooled with the fixed-beta results; its cost probe first, its
  rows approved after the projection (8.5).

### Nineteenth pass (against the eleventh message)

Applied, as following from fixed rules:
N1. CON keeps round 1's function, CON(t1, t2) = change(t1) - change(t2),
    with the tighter target written first, for all three pairs; contrast 7
    is CON(0.01, 0.5) (8.1).
N2. TMM in TAU8 and GEOM uses 0.3 for 0.5, by the substitution already used
    (8.1).
N3. scripts/perjcalprobe.py written: one call of the archived perjcal.one_J
    per unit of perjcal's archived design (6 objectives x d 2, 40 x tau_0
    0.5, 0.01, J >= 1/tau_0), plan identity read from perjcal.py, seed
    pass-through and determinism, RSS budget, seed-dependence evidence,
    projection at the archived M. Seed kind 91 (new; no other script uses
    it).
N4. perjcal's analysis criteria are not specified until Rahul approves its
    rows; they are listed under "Decisions still needed".

### Twentieth pass (the trajectory script against this file)

scripts/rerun.py and scripts/rerunlib.py written. Choices made in
writing them, each following from a fixed rule or from the code:
O1. The Kaggle bundle ships two archived CSVs only (kgrun.py
    ARCHIVE_CSVS). So every check that reads the archive's CSVs or the
    manuscript runs once on the laptop (--precheck) and writes a plan
    folder; Kaggle runs read the plan. The onset control is in the
    precheck, so no trajectory can run before it passes.
O2. The archived betas of the non-calprec2 rows are recomputed by each
    module's own code; only the 4000-point probe samplers are retyped, and
    A-BETA checks every recomputed beta against the archived CSV, to half
    a unit in the last printed digit. The same for sigma (A-SIGMA).
O3. A shared cell is run by the job whose --rows contain its owner row,
    so it is run once whichever jobs run.
O4. Owners are computed over all seventeen rows in every plan, so keys do
    not depend on which rows a job selects, or on whether calprec2's table
    exists yet. Its four rows are "beta pending" until a plan is built
    with the table.
O5. Shards by longest-processing-time first over costprobe2's measured unit
    walls; G-STOP at 36000 s, as calprec2; resume under rule 17.
O6. A determinism smoke (kind 83) per module, bitwise.
O7. The trajectory script prints no slope, interval or verdict. Its output
    is per-realization E_J only, so running it shows no result before the
    analysis criteria are complete.
Nothing in the trajectory script needs Rahul's decision.

### Twenty-first pass (the analysis script against this file)

Writing rerun_analysis.py against the checklist found three points that
need Rahul's decision. The analysis script is not written; it will be
written in one piece once they are settled, and committed before its
first execution.
L1. The sixth message (S3) says the comparisons not made report "estimates
    and intervals for these quantities, with no verdict" (checklist:
    "their quantities are printed with intervals only"). Item 7 says "no
    other contrast is computed". The two conflict, because those
    quantities are contrasts or regressions. Read from the code:
    (a) cliff (i): S(r) - S(0.5) at r = 0.9 and 1.0; (ii): S(5.0) -
        S(0.5); on the objective-mean slope, per (diffusion, d) (cliff.py
        lines 62, 63, 120, 121);
    (b) regimemap "map informative": per (diffusion, d), the largest range
        (max - min) of the objective-mean slope over tau_0 at fixed r, and
        over r at fixed tau_0 (regimemap.py lines 466 to 482): a range
        between levels the data select, not two named levels;
    (c) crossed small_A: the ANISO arm-A diffusion gaps, which contrast 3
        already reports. Nothing to add;
    (d) audit.py A2: per (diffusion, d, tau_0) in SIGMA, the OLS
        coefficient of slope on r (audit.py lines 174 to 215);
    (e) partm P-M2 is J3, already specified. P-M3 compares RMAP's d40 - d10
        change at r <= 1 with Section 7.3's published values (partm.py
        lines 330 to 353), that is with round-1 numbers from another
        design. P-M4 compares RMAP with ONSET at tau_0 0.1, r 1.0, and
        those cells are now shared, so the comparison is identically zero
        by construction (applied: reported as vacuous, no number).
L2. The variance-explained quantities "printed with no verdict" (item 4;
    sixth message S5): mechanism P3.4's three R^2 (OLS of cell slopes on
    log tau_0; plus log d; plus objective dummies; mechanism.py lines 432
    to 456); regime P6.3's in-sample and out-of-sample R^2 of three nested
    models trained on SYNTH and tested on NAMED (regime.py lines 441 to
    470); ess_surface P1.3. Item 1 gives every reported interval at 95%,
    but no message says whether these carry an interval. And P1.3 defines
    "slope breakdown" by the retired rule abs(slope + 1) < 0.15
    (ess_surface.py docstring lines 33 to 40; item 4), so it cannot be
    computed as specified.
L3. Straightness: "the quadratic term is printed with its interval only".
    regime.fit_curv is importable. The archive applied it to the mean curve
    (regime.py line 362), the S-curve analogue. Item 0 makes the
    per-realization mean primary for slopes and says nothing about
    curvature.
Applied, no decision: ess_surface's minimum ESS, reference and
subensemble, is printed per cell as the mean over realizations of the
values one_realisation returns, with no SATURATED label.

The audit stops on L1 to L3 for the analysis script. The trajectory
script is complete.

### Twelfth message: L1 to L3 decided

L1. Where the sixth message (S3) and item 7 conflict, item 7 governs.
    Rahul records that his sixth-message wording created the conflict:
    "quantities printed with intervals" meant the row's estimates, not
    reconstructed comparisons.
    - cliff (i) and (ii): not computed. They are contrasts between r
      levels that item 7 does not list, and listing them now would be
      adding comparisons after seeing which ones exist. CLIFF prints its
      per-cell S-slopes with intervals and its diffusion contrast, nothing
      else.
    - regimemap "map informative": not computed. A max-minus-min over
      levels the data choose is the objection item 2 made to N_vis.
    - audit A2, the coefficient of slope on r: computed, a regression
      coefficient fixed in the docstring, with its interval, under the
      estimand/shape line. Per (diffusion, d, tau_0) in SIGMA, per
      objective and pooled; OLS of the cell S-slopes on r with intercept
      over SIGMA's six r (audit.py lines 174 to 215); W-ge line at tau_0
      0.01.
    - partm P-M3: not computed. Comparing with round-1 published numbers
      from another design is the comparability error N30 and N33 record.
    - P-M4: vacuous under sharing (twenty-first pass); no number.
L2. R^2 values carry no interval: they are descriptive, and an interval
    would invite the verdict the estimand/shape line forbids. Each is
    printed as a point value with the fit it comes from named
    (mechanism P3.4 for CONC and PROBEARM; regime P6.3, train SYNTH,
    test NAMED).
    ess_surface P1.3 is reduced to printing the minimum ESS beside each
    slope. Redefining "breakdown" would invent a criterion after the fact;
    dropping it would lose a real measurement.
L3. The curvature estimand is the mean of per-realization curvatures
    (regime.fit_curv per realization), matching item 0. Departure from the
    archive, stated explicitly: regime.py line 362 applied fit_curv to the
    mean curve, the S-curve analogue, which is one of the two-estimand
    defects N33 records. Rows: the regime rows (REFSIZE, SYNTH, NAMED,
    HORIZON), with its interval only.
perjcal's P-C1 to P-C3 wait for its rows.

### Twenty-second pass (against the twelfth message)

Applied, as following from fixed rules:
Q1. P6.3's response is the cell S-slope on W-full (item 0), where the
    archive's regime_B and regime_C files held the mean-curve slope
    (regime.py cell_summary). The features are the cell means of the
    values regime.one_realisation returns, as cell_summary took them.
    regime.fit_predict is imported; the three feature lists are copied
    from regime.py lines 451 to 453.
Q2. mechanism P3.4's response is the cell S-slope on W-full; the design is
    mechanism.py lines 436 to 450 (log tau_0, log d, objective dummies);
    mechanism.r2_of is imported.
Q3. The minimum ESS printed beside each BETA-ISO and BETA-ANI slope is
    the mean over realizations of ess_min_ref and of ess_min_sub at each
    J, as ess_surface.one_realisation returns them.
Nothing needs Rahul's decision. The analysis script is written.

### Thirteenth message: D1 to D3 (from notes/RERUN_REVIEW.md, first pass)

D1. Audit A2's coefficient takes the DIFFERENCE rule, like every other
    regression coefficient of section 8. Rahul's reason: treating it
    differently would mean two standards for the same kind of quantity,
    which is the failure the whole audit exists to prevent.
D2. Equivalence and attainability verdicts are per cell only. The pooled
    diffusion gap gets its estimate, interval, DIFFERENCE rule and item 6's
    heterogeneity, and no equivalence or attainability verdict. Rahul's
    reason: the margin is derived from per-cell SDs, so applying it to a
    pooled quantity compares a number against a scale built for a
    different unit. Rahul records that his H2 wording ("reported the same
    way") was ambiguous; the reading that governs is "reported alongside
    with its heterogeneity", not "given the per-cell verdicts".
D3. The analysis runs only when all seventeen rows are complete. Rahul's
    reason: analysing the thirteen archived-beta rows first would produce a
    partial set of numbers before the calibrated rows exist, and partial
    numbers invite a conclusion drawn before the evidence is in. One stop,
    no partial analysis: rerun_analysis.py exits 7 before creating any
    output.
The review's noted items N1 to N5 are accepted as recorded. The ONSET
ownership point (N2) goes into the rerun runbook when it is written.

### Fourteenth message (2026-10-26): the calibrated r rows (ledger N41, N42)

Rows RMAP-CAL, CLIFF-CAL and ONSET-CAL (rerunlib.py, CALIBRATED r ROWS):
the cells of RMAP, CLIFF and ONSET, run on the N41 calprec2 betas
(runs/calprec2-ext-finalize-a2-kaggle-20261026-204714). The questions are
put one at a time, and each is decided before any code is written. Until
all are decided, rerun_analysis.py keeps its guard (exit 2).

CAL1. Margin. DECIDED: keep m = 0.078113, with a ratio guard.
    - m = 3 x S, S = 0.026038, as fixed by the seventeen-row analysis
      (logs/rerun-analysis-20261025-0513.log, analysis_margin.csv;
      ledger N39). It is not recomputed. Every equivalence verdict of the
      calibrated rows uses it, and the seventeen rows' verdicts are not
      reissued.
    - Ratio guard (docstring text). Before any gap of a calibrated row is
      computed, the analysis prints the median per-cell S-slope bootstrap
      SD over the cell arms of RMAP-CAL, CLIFF-CAL and ONSET-CAL. A cell
      shared by RMAP-CAL and ONSET-CAL counts once, as in 5b. It then
      prints the ratio of that median to each existing group's median:
      calprec2 (SIGMA, ANISO) 0.026582 and probe (RMAP, CLIFF, ONSET)
      0.025384 (N39). Each ratio is larger median / smaller median.
      REVISIT iff either ratio > 1.5, the 5b threshold. On REVISIT the
      script prints "MARGIN REVISIT REQUIRED" for the calibrated rows and
      computes no gap, DIFFERENCE verdict or equivalence verdict for them.
      Worked example (illustrative numbers): median 0.030 gives ratios
      0.030 / 0.026582 = 1.13 and 0.030 / 0.025384 = 1.18, no revisit.
      Median 0.040 gives 1.50 and 1.58: 1.58 > 1.5, so REVISIT.
    - Rahul's reason: 5b fixes S before any gap is seen. Recomputing now
      would change the margin of verdicts whose gaps are already in the
      seventeen-row result, which is the thing 5b exists to prevent. A8's
      concern, that one beta design's scale should not set another's
      margin, is met by the ratio guard rather than by recomputation.
    - Recorded as Rahul instructed:
      - This is an exception to A8 as worded. A8 says a row that makes an
        equivalence claim joins the pool that defines S and does not
        borrow the margin. The calibrated rows borrow it.
      - The calibrated rows borrow a margin fixed before their gaps
        existed.
      - The manuscript must say both.
    - On REVISIT (Rahul, 2026-10-26, review item R1): no phase-3 output at
      all for the calibrated rows. That is no gap, contrast, coefficient
      or verdict, and also no onsets and no J4 counts, though those carry
      no verdict. Rahul's reason: 5b already does this for the seventeen
      rows, and onsets printed alone are the partial set D3 exists to
      prevent. A reader would have numbers from a row whose margin is in
      doubt, with nothing to place them against.
CAL2. Contrasts. DECIDED: mirror.
    - Each calibrated row gets exactly its base row's contrasts and
      section-8 quantities, with the same signs, windows and DIFFERENCE
      rule:
      - RMAP-CAL: anisotropic - isotropic per cell (contrast 3); tau_0
        0.01 - 0.5 per arm (contrast 2); J3, b1, b2 and b3 per
        (diffusion, d).
      - CLIFF-CAL: anisotropic - isotropic per cell.
      - ONSET-CAL: anisotropic - isotropic per cell; onset d 80 - d 5
        (contrast 6); J2, severity and its trend; J4, the onset against
        r = 1.
      Each also gets the per-cell rate verdicts of its base row. Nothing
      new is defined.
    - Nothing is computed between a probe row and its calibrated row. The
      two designs are reported side by side, with no contrast and no
      verdict between them. The manuscript must say so.
    - Rahul's reason: the rows exist because probe-beta results reopen
      referee point 5. The onset, the severity trend and the RMAP panel
      are probe-beta results in the same way the diffusion gap is.
      Diffusion only would calibrate the gap and leave those exposed. A
      probe-against-calibrated contrast is not a paired comparison: the
      owner row is in the seed key (owners 17 to 19 against 0 to 16), so
      a probe cell and its calibrated twin are independent replications.
      That is N40 and referee point 7.
    - Input to CAL3, recorded as Rahul instructed: RMAP-CAL's target
      contrast and its panel model rest partly on cells whose reference
      failed C5m. Six of the seven not-adequate cells, regimemap ackley d
      10 and 40 and rastrigin d 40, each at tau_0 0.01 and 0.03, are RMAP
      cells (section 2: tau_0 0.03 and 0.01 occur in RMAP only).
      ONSET-CAL (tau_0 0.1 only) contains none of them. The seventh,
      cliff ackley d 10 tau_0 0.1, is CLIFF-CAL's.
CAL3. Sensitivity analysis excluding the not-adequate cells. DECIDED:
    flag, do not exclude.
    - All cells enter every statistic. Every statistic that uses a cell
      whose calprec2 adequacy is "not adequate" carries a flag naming
      those cells. Per-cell adequacy is reported as before
      (analysis_adequacy.csv). No statistic is recomputed without them.
    - A calibration cell has no r or diffusion coordinate, so one
      not-adequate cell reaches every r and both arms at its (objective,
      d, tau_0). In RMAP-CAL that is 5 r values per arm for each of its
      six cells; in CLIFF-CAL, 9 r values per arm for cliff ackley d 10
      (cliff.py line 263).
    - The flag extends to the seventeen rows: CONC, TAU8, SIGMA and ANISO
      have not-adequate cells (N39, C6). It was added after the
      seventeen-row results were seen, and it changes no value. It names,
      at the point of use, what analysis_adequacy.csv already records.
    - Worked example (illustrative): RMAP-CAL, isotropic, ackley, d 10,
      contrast tau_0 0.01 - 0.5 at r 1.0. It uses the calibration cell
      regimemap ackley d 10 tau_0 0.01, "beta, not adequate (C5m FAIL,
      D1 FAIL)". The statistic is printed with its value, interval and
      verdict as usual, and with the flag "not adequate: regimemap|
      ackley|10|centred|0.01". A pooled figure that includes that cell
      carries the same flag.
    - Rahul's reasons:
      - Exclusion changes the estimand. It alters the pooled target
        contrast's composition and fits the J3 panels on half their
        design, so the excluded number would not be a sensitivity of the
        same quantity.
      - The seventeen rows included their not-adequate cells, so one
        standard requires the same here. One set flagged and the other
        not would be the two-standards error.
      - The flag reports precisely what is uncertain: the tau_0
        coordinate of named cells, not their slopes. Their trajectories
        are valid fixed-beta runs at the beta used. The failed checks
        are on the reference (C5m, and D1 in three cells).
    - What this costs, recorded as Rahul instructed: no single number
      shows how much the six cells move RMAP-CAL's target contrast or
      panel coefficients; only the per-objective values show it. The
      manuscript must state that the tau_0 0.01 and 0.03 end of RMAP-CAL
      rests partly on cells whose tau is not established.
CAL4. A1 over twenty rows. DECIDED: one analysis over all twenty rows,
    with a reproduction check.
    - A1 becomes "all twenty rows complete". Its definition and exit 7
      are unchanged: if any row is incomplete, every row's count is
      printed with "INCOMPLETE: analysis refused (D3)", no output folder
      is created and nothing is computed.
    - The run recomputes the seventeen rows. Before any statistic of a
      calibrated row is printed, it checks that this part reproduces N39
      (runs/rerun-analysis-20261025-051314):
      - margin: S, the calprec2-group median, the probe-group median and
        m print as 0.026038, 0.026582, 0.025384 and 0.078113, as in that
        folder's analysis_margin.csv;
      - statistics: every seventeen-row value equals that folder's value
        as a string. The CAL3 flag column is the only permitted
        difference.
      On any mismatch the script prints "17-ROW REPRODUCTION FAILED" and
      the first differences. It computes nothing for the calibrated rows
      and exits with its own code. A mismatch is a finding, not
      something to patch.
    - Worked example: m prints 0.078113 and every seventeen-row statistic
      matches, so the calibrated rows proceed to the CAL1 ratio guard. If
      one SIGMA c3 interval endpoint prints -0.0412 where N39 has
      -0.0413, the check fails at that row and no calibrated-row number
      is printed.
    - Constraint on where it runs, recorded as Rahul instructed: the
      twenty-row analysis runs on the laptop with Python 3.12.3 and NumPy
      2.5.3. The string-equality check holds only in the environment that
      produced N39. This constraint is not to be relaxed.
    - Rahul's reasons:
      - D3 applies to the new rows as it did to the old, so nothing about
        RMAP-CAL is printed while ONSET-CAL is incomplete.
      - One run gives one output folder, so the CAL3 flags sit in both
        sets of rows under the same code.
      - The check turns "nothing changed for the seventeen rows" from a
        claim into a tested fact. The analysis code changes for the new
        rows, the flags and the guard; without the check, that those
        changes left the old path untouched would be an assertion.
CAL5. Target cells whose beta is beta_adq. DECIDED: report, do not flag;
    split the target counts.
    - The cells: target-labelled, adequate calibration cells whose beta is
      beta_adq under calprec2's BA rule (calprec2.py lines 217 to 227,
      confirmed by Rahul 2026-10-11). Provenance is "beta_adq; C1 found no
      sufficient level" or "beta_adq; C6 failed for beta_prod". In the N41
      table there are seven, all of the first kind:
      - cliff ackley d 40 tau0 0.1;
      - regimemap ackley d 10, 20 and 80, tau0 0.1;
      - regimemap rastrigin d 10 tau0 0.01;
      - regimemap rastrigin d 80 tau0 0.1;
      - regimemap sphere d 40 tau0 0.01.
      The 336-cell table has cells of both kinds in boundary, crossed,
      mechanism and sigma.
    - Docstring text: for each calibrated row (rerunlib.CALROWS, the
      seventeen-row ones included), its distinct calibration cells are
      counted by category = label + " | " + provenance, with a provenance
      beginning "beta_prod" shortened to "beta_prod". The counts are
      printed and written to analysis_adequacy_split.csv. No statistic is
      flagged and no value changes. The ledger's tallies (N39 C6, N41) are
      corrected the same way, from that output.
    - Worked example: cells "target" / "beta_prod, calibration N_cell
      4000000", "target" / "beta_prod, calibration N_cell 64000" and
      "target" / "beta_adq; C1 found no sufficient level" give "target |
      beta_prod 2" and "target | beta_adq; C1 found no sufficient level
      1".
    - Rahul's reasons: these cells' tau0 is established by the same 5%
      criterion as every other target cell, so flagging them would put
      them in the same class as cells that failed a check, which they did
      not. CAL3's flag marks cells whose tau0 is not established; this is
      a different thing. His objection was that the summary counts hide
      them, and splitting the counts answers it.
    - What this costs, recorded as Rahul instructed: a reader of a
      statistic does not see at the point of use that the beta came from
      the median rule and was verified on the same replicates that judged
      adequacy. It is visible only in the per-cell adequacy table and the
      split counts. The manuscript must say so where it describes
      calibration.

CAL1 to CAL5 are decided. They are implemented in
scripts/rerun_analysis.py (docstring "THE CALIBRATED r ROWS"); the review
of that change is notes/RERUN_REVIEW.md, 2026-10-26.

---

### Fifteenth message (2026-10-28): onsets (ledger N43)

Decided by Rahul, 2026-10-28: drop onset intervals. No resample-level
classification script is written.

- Rahul's reason: the script's best outcome would still be exploratory
  evidence for a claim the paper does not need. It would use a rule chosen
  after the curves were seen and a threshold (m, 5b) borrowed from another
  purpose. The organising contrast rests on the per-cell rate verdicts by
  region (C2) and on contrast 3. The severity result rests on slopes at
  fixed r (S(1,3), S(0.75,3), J2). Neither uses an onset.
- Dropped as claims, for ONSET and ONSET-CAL alike:
  - J4 (onset against r = 1: every "k of n intervals contain 1", per
    objective and pooled);
  - contrast 6 (onset d 80 - d 5);
  - the 95% interval column of the onsets (H3);
  - the onset heterogeneity rows (H2 applied to onsets).
  H3, J4 and contrast 6 stay in the committed analysis as computations.
  analysis_onsets.csv, analysis_onsets_calibrated.csv and the c6 rows of
  analysis_stats.csv are unchanged and are not rerun. Nothing in this
  file's earlier text that defines them is deleted; this entry overrides
  their use as claims.
- What the paper does:
  - reports the slope-against-r curves and their point bends (H3 point
    estimates) as exploratory, with no location estimated and no
    interval;
  - states as a limitation that it cannot say, with an interval, where
    along r the slope begins to degrade;
  - withdraws round 1's "nine of ten bootstrap intervals contain r = 1"
    (zenodo-v1/sn-article.tex lines 38 and 628) in one sentence. The
    sentence names that the rerun gives 6 of 10 in both designs (ONSET,
    N39; ONSET-CAL, N42; J4 pooled) under the approved bootstrap, and
    names both changes, the realizations and the bootstrap unit, with no
    cause assigned.
- Wording held:
  - "does not hold on the rerun", never "changed significantly" or any
    comparative test language (the two counts are not tested against
    each other);
  - 6 of 10 appears only as the reason the earlier statement is
    withdrawn, never as a finding that the onset is separated from r = 1,
    and with no per-dimension list of which intervals exclude 1;
  - the point bends are never called onsets of degradation; a bend at
    2.00 is not interpreted without its curve (N43).
- Worked example of the withdrawal sentence's content, not its final
  wording: the earlier version stated that nine of ten bootstrap
  intervals for the breakpoint contained r = 1. On the rerun, with
  realizations resampled within cells, six of ten do, in both designs.
  The rerun changed both the realizations and the bootstrap unit, and the
  statement is withdrawn without attributing the difference to either.

### Sixteenth message (2026-10-28): ONSET-R, the onset-resolution row (ledger N44)

PROPOSED by Claude, 2026-10-28. Rahul approves this section before any
code is written. Every rule below is fixed before any ONSET-R trajectory
exists; nothing in it was chosen after seeing ONSET-R data. It was
written after the ONSET and ONSET-CAL curves had been seen (N43), and it
uses those curves for nothing but the grid range and M.

Decided by Rahul, 2026-10-28: M = 48; delta 0.10 primary, 0.05 and 0.20
sensitivity with no verdict; grid upper end 4.8; 8 shards at the 10800 s
target. Reasons are in N44.

O-R1. The row. ONSET-R, appended after the twenty rows (owner index 20;
  every existing key and owner index unchanged).
  - Module regimemap; objectives ackley, rastrigin, sphere; d 5, 10, 20,
    40, 80; diffusions isotropic and anisotropic; law centred; tau0 0.1;
    J_inf 50000, T 1.0, the J10 grid, DT and LAM as ONSET-CAL.
  - r grid (14 points): 0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.4, 1.7, 2.0, 2.4,
    2.8, 3.4, 4.0, 4.8. sigma = sigma_of(diffusion, d, r) as for ONSET.
  - M = 48 realizations per cell (reps 0 to 47). 2 x 3 x 5 x 14 = 420
    cells, 20160 tasks.
  - beta from calprec2_beta.csv (the N41 table) at (regimemap, objective,
    d, centred, 0.1); the beta does not depend on r or the diffusion
    (N44). The cells whose provenance is "beta_adq; C1 found no sufficient
    level" (ackley d 10, 20, 80; rastrigin d 80) are reported with that
    caveat, never excluded (CAL3 practice).
  - Fresh realizations everywhere: no cell is shared with any existing
    row (no K4 share group), including r 1.0 and 2.0, which ONSET-CAL
    also has.

O-R2. The estimand: the sustained threshold crossing r_delta, per unit
  (diffusion, objective, d).
  - gamma(r): the cell's S-slope (fit_slope over the window, the existing
    S statistic), W-full primary.
  - Baseline gamma_adm: the mean of gamma at the four admissible points
    r = 0.5, 0.6, 0.7, 0.85.
  - Excess g(r) = gamma(r) - gamma_adm. A rise of the slope toward 0 is
    degradation; g > 0.
  - k: the smallest grid index with r_k >= 1.0 such that g(r_j) >= delta
    for every j >= k (sustained). Comparisons are on the floating values
    as computed, with no tolerance.
  - If k exists and g(r_(k-1)) < delta: log r_delta = log r_(k-1) +
    f (log r_k - log r_(k-1)), with f = (delta - g(r_(k-1))) / (g(r_k) -
    g(r_(k-1))); that is, r_delta = r_(k-1) (r_k / r_(k-1))^f.
  - If k exists and g(r_(k-1)) >= delta (possible only when r_k = 1.0):
    left-censored, "at or below 0.85".
  - If no k exists: right-censored, "beyond 4.8".
  - delta = 0.10 primary (a loss of one tenth of the J^-1 exponent);
    0.05 and 0.20 sensitivity, computed identically, no verdict.
  - Why there is no start/end ambiguity: r_delta is a level crossing of
    the curve against its own admissible baseline, not a bend location.
    A curve that rises from r 1 to 2 and then flattens crosses during its
    rise; a curve flat to 2.4 that then jumps crosses inside the jump.
    It always reads "the smallest r beyond which the slope stays
    degraded by at least delta".
  - Worked example: baseline -1.00; gamma -0.97 at 1.2 and -0.87 at 1.4,
    and >= -0.87 from there on. g(1.2) = 0.03, g(1.4) = 0.13; delta 0.10:
    f = 0.07 / 0.10 = 0.7; r_delta = 1.2 x (1.4/1.2)^0.7 = 1.336731
    (control C2 below).

O-R3. Baseline check. If max - min of gamma over the four baseline
  points exceeds delta / 2 (0.05 at the primary delta), the unit is
  "baseline not flat": r_delta is printed, no verdict is given.
  Example: baseline -1.00, -1.00, -1.00, -0.94: range 0.06 > 0.05: not
  flat (control C6).

O-R4. Positive control (O2), on synthetic curves with known crossings.
  It runs in rerun.py's precheck before the plan is written (no plan
  unless it passes) and again at the start of rerun_analysis.py (exit 2
  unless it passes). Curves are values of gamma at the 14 grid points;
  expected r_delta at delta 0.05 / 0.10 / 0.20; a computed value passes
  if it is within 1e-12 of the closed form r_(k-1) (r_k/r_(k-1))^f, and
  a censored case passes only if the same censoring is returned.
  - C1 step: -1.00 up to r 1.7, -0.75 from 2.0. f = 0.2 / 0.4 / 0.8
    between 1.7 and 2.0: 1.756164 / 1.814184 / 1.936038.
  - C2 rise then plateau: -1.00 up to 1.0; -0.97, -0.87, -0.77 at 1.2,
    1.4, 1.7; -0.72 from 2.0. 1.2 to 1.4, f 0.2: 1.237572; 1.2 to 1.4, f
    0.7: 1.336731; 1.4 to 1.7, f 0.7: 1.603809. The crossing lies inside
    the rise, not at its end (the N43 failure of H3).
  - C3 no crossing: -1.00 up to 4.0, -0.97 at 4.8: right-censored at all
    three.
  - C4 transient: as C1 with -0.85 at 1.2 (g 0.15, then 0 at 1.4 and
    1.7): same values as C1. The sustained rule ignores the excursion; a
    first-crossing rule would give 1.0 to 1.2.
  - C5 at the boundary: -1.00 at the baseline, -0.75 from 1.0. 0.85 to
    1.0: 0.878082 / 0.907092 / 0.968019, below 1.
  - C6 baseline not flat: baseline -1.00, -1.00, -1.00, -0.94 (mean
    -0.985, range 0.06); -1.00 at 1.0 to 1.7, -0.75 from 2.0. f 0.26 /
    0.46 / 0.86: 1.773373 / 1.831961 / 1.955008; flagged not flat at
    0.10 (range 0.06 > 0.05) and at 0.05 (0.06 > 0.025), not at 0.20.
  - C7 left-censored: baseline -1.00, -1.00, -1.00, -0.85 (mean -0.9625,
    range 0.15); -0.75 from 1.0. Left-censored at 0.05 and 0.10; at 0.20
    g(0.85) = 0.1125 < 0.20, crossing 0.85 to 1.0, f 0.875: 0.979890.
  - C8 bootstrap: a unit whose realizations are identical within each
    cell gives lo95 = hi95 = the point value.
  Values are printed to six decimals here; the control compares at full
  precision against the closed form.

O-R5. Bootstrap. Realizations resampled within each cell, independently
  across cells (each r is its own cell with its own keys), B = 10000,
  indices from default_rng(SeedSequence(boot key, kind 71)) as every
  other row. On each resample all 14 slopes of the unit are recomputed,
  then gamma_adm, g and r_delta.
  - Interval: nearest-rank order statistics, because censored values make
    interpolated percentiles undefined. Left-censored resamples rank
    below every finite value, right-censored above. lo95 = the 250th
    smallest of B, hi95 = the 9750th. A limit that falls on a censored
    resample reads "at or below 0.85" or "beyond 4.8".
  - A resample with a non-finite slope in any of the 14 cells gives a
    non-finite r_delta; it is excluded and counted; above 1% of B the unit
    is FLAG (the existing FLAG_FRAC rule) and gets no verdict.
  - Example: 260 of 10000 resamples right-censored, the rest finite:
    hi95 is the 9750th smallest, which is finite (9740 finite values lie
    below the 260 censored), so the interval is finite at the top only if
    fewer than 251 resamples are right-censored. Here 260 > 250: hi95
    reads "beyond 4.8".

O-R6. Verdict per unit, delta 0.10, W-full only.
  - "above 1": lo95 > 1.0 (a lo95 of "beyond 4.8" counts as above).
  - "below 1": hi95 < 1.0 (an hi95 of "at or below 0.85" counts as
    below).
  - "not distinguishable from 1": otherwise.
  - No verdict: point estimate censored (reported "no crossing up to
    4.8" or "at or below 0.85"), baseline not flat (O-R3), or FLAG.
  - Examples: [1.12, 1.70]: above 1. [0.92, 1.40]: not distinguishable.
    [at or below 0.85, 0.97]: below 1.
  - 30 units. Verdicts are reported as counts per diffusion and in all;
    no multiplicity correction and no family-wise claim. The point value
    and both limits are reported for every unit.

O-R7. Pooled, per (diffusion, d): the mean over the three objectives of
  log r_delta, with the existing heterogeneity statistics on the
  per-objective log r_delta (bootstrap variances). Descriptive: interval
  reported, no verdict. Not computed if any objective's point value is
  censored; in a resample, any right-censored objective makes the pooled
  value right-censored, any left-censored (and none right) left-censored,
  both together non-finite. It is not the crossing of a mean curve.

O-R8. Also computed for ONSET-R: phase 1 per cell (S-slope, interval,
  rate verdict, S-curve) as for every row; W-ge for O-R2 to O-R7 as
  sensitivity, no verdict.
  Not computed, and not claimed: H3 bends, J4, contrast 6, contrast 3,
  severity, any trend of r_delta across d, any comparison with ONSET or
  ONSET-CAL (independent replications, N40; onsets dropped, N43). ONSET-R
  does not enter the 5b margin pool, and m plays no part in it.

O-R9. What counts as a failure.
  - Before any trajectory: O2 fails (precheck writes no plan); K5 fails
    against runs/rerun-plan-20261026-210435; any existing precheck check
    fails.
  - Queue: the smoke's determinism check fails (exit 3); a shard ends
    incomplete after resumes; per-worker peak RSS above 3072 MB.
  - Analysis:
    - O2 fails, or any setup check fails: exit 2;
    - any row incomplete: exit 7, nothing computed;
    - the twenty-row reproduction fails: exit 8, nothing about ONSET-R is
      computed.
  - Unit level: the no-verdict cases of O-R6, each counted and listed.

O-R10. Reproduction. rerun_analysis.py's reproduction pin moves to
  runs/rerun-analysis-20261027-185918. Every old row and old column of
  each of its CSVs must equal the new run's, as strings, before ONSET-R is
  computed: analysis_completeness, cells, margin, stats, onsets, audit,
  r2, adequacy, margin_calibrated, onsets_calibrated, adequacy_split.
  That folder matched N39 on the seventeen rows (CAL4), so the chain back
  to N39 holds. Like CAL4, the run is on the laptop (Python 3.12.3, NumPy
  2.5.3).

O-R11. Order of work. Criteria approved; code with the four pre-run
  checks; O2 committed and passing in the precheck, which then writes the
  plan and runs K5; the schedule (8 shards at the target, Rahul's
  decision); the queue definition notes/queues/rerun-onsetr.json (smoke,
  then 8 shards, resumable on exit 5 as the existing profiles), then
  "rerunq.py load"; the analysis after the queue is DONE.

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
- [ ] Every row's primary window is the full grid except REFSIZE.
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
      objectives. Onsets are printed per d with intervals, per objective
      and pooled per (diffusion, d); no trend in d; only the onset
      contrast d80 - d5.
- [ ] The onset estimator's docstring states the candidate set (r grid
      without its last value), the tie rule (smaller c) and that the
      pooled onset is the onset of the mean curve.
- [ ] Before any trajectory, the onset control recomputes the ten
      archived onsets from regimemap_D_real.csv and matches the
      manuscript's onset table (tex lines 608 to 612, 615 to 619)
      exactly, or prints "ONSET CONTROL FAILED" and stops; the per-r
      means are printed beside the table's as a diagnostic.
- [ ] The seven contrasts of item 7 and no others, each stated in the
      docstring as second level minus first with the baseline as
      subtrahend (d40 - d2, tau 0.01 - 0.5, aniso - iso, mix-0.1 -
      centred, J_inf 100000 - 12500, onset d80 - d5, change(tightest) -
      change(loosest)), with its 95% interval, DIFFERENCE verdict, and a
      W-ge sensitivity line where tau_0 < 0.1 (none for contrast 5).
      Plus the quantities of section 8.
- [ ] Contrast 7's docstring shows both orientations once: round 1's
      CON(0.5, 0.01) = change(0.5) - change(0.01), published -0.0233 on
      W-ge, and the new change(0.01) - change(0.5), its negative.
- [ ] Every contrast is printed per cell and pooled over units; the
      pooled figure is the unweighted mean of the per-unit estimates and
      is printed with k, sd_units, vbar, tau2_mm, I2 and the truncation
      flag, or "I2 undefined" with its reason.
- [ ] No contrast in ADAPT, LAWPANEL, HORIZON, SYNTH, NAMED, BETA-ISO,
      BETA-ANI.
- [ ] Section 8: REGF b_d, b_tau, b_dtau (CONC, PROBEARM, TAU8, GEOM; both
      windows); the three CON pairs named CON(tighter, looser), both orientations; TMM; no quantity labelled SEP;
      S(1, 3) and S(0.75, 3) per (diffusion, d) and their trends in
      log2 d; RMAP b1, b2, b3 per (diffusion, d), both windows; onset
      intervals against 1 with counts and denominators; each per unit
      and pooled, with interval and DIFFERENCE rule, and no shape
      sentence anywhere in the output or docstring.
- [ ] No round-1 interval is printed as, or compared with, a rerun
      interval; the docstring says why.
- [ ] Finite-J audit in CONC, PROBEARM, TAU8, GEOM: F1 per realization;
      ratio(J) summaries; floor flags; d40 - d2 (d40 - d5) differences
      per (tau_0, J) per unit and pooled, with counts; no PASS/FAIL; its
      wall time and RSS printed.
- [ ] The seed key follows the approved layout: diffusion absent, every
      other coordinate present, field 3 the owner row; K1, K2 and K4 stop
      the run on failure; the key is written per realization.
- [ ] Shared cells (four regime cells; the RMAP-ONSET overlap at d 10
      and 40, r 1.0 to 3.0, tau_0 0.1) are run once; each realization is
      written once with the rows that use it; per row, the owned-elsewhere
      count and owners are printed.
- [ ] A shared cell enters 5b's margin pool once.
- [ ] SYNTH and NAMED: estimates and intervals only, no contrast.
- [ ] REFSIZE: primary window J <= 1250 for all J_inf; sensitivity column
      on each cell's J_inf/10-capped grid; no J_inf extrapolation.
- [ ] calprec2's per-cell adequacy verdict, C5m, D1 and both reference
      medians are printed per cell, with no pooled verdict.
- [ ] Before each fit, every E on the window is checked finite and > 0; a
      realization failing it is handled by item 3's realization rule for
      that window, with the bad-point count printed.
- [ ] Not computed (twelfth message, L1): cliff (i) and (ii), regimemap
      "map informative", partm P-M3; P-M4 reported as vacuous; crossed
      small_A is contrast 3. Computed: audit A2's coefficient of slope on
      r, with its interval.
- [ ] mechanism P3.4's three R^2 and regime P6.3's R^2 printed as point
      values with the fit named, no interval, no verdict; ess_surface P1.3
      reduced to the minimum ESS beside each slope (L2).
- [ ] Curvature in the regime rows is the mean of per-realization
      fit_curv values, with its interval; the departure from the
      archive's mean-curve value is stated (L3).
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

The twelfth message decided L1 to L3; a thirteenth decided D1 to D3,
raised by the first review of the scripts (notes/RERUN_REVIEW.md). Left,
after the perjcal projection, with its rows:

1. perjcal's analysis criteria. Its archived rules: P-C1, control within
   1% at every point and more than 5% misses stopping the analysis;
   P-C2, the absolute value of the d2 to d40 change bootstrapped over
   objectives (items 3 and 4 already replace that with the signed change
   resampled within cells); P-C3, a three-branch decision comparing the
   tight-target change with the moderate-target interval; and P-C2's
   printing of the nested-design values beside its own, which compares
   two estimands the archive says not to compare.

## What the rerun needs that this file does not yet give

For the trajectories: nothing. The order of work is:
- the precheck on the laptop, which writes the plan (O1 to O4); then the
  schedule, the smoke and the shards of the thirteen rows on archived
  betas;
- calprec2's beta table (shards 0 to 7 committed, 8 running), then a
  second precheck with --calprec2, and the four calibrated rows.

For the analysis: nothing. scripts/rerun_analysis.py is written and is
committed before its first execution.

For perjcal: the projection from scripts/perjcalprobe.py, Rahul's approval
of the rows, then item 1 above.

Already in place: item 3's bootstrap key (fixed by the approved layout);
the Kaggle determinism gate passed (ENVIRONMENT.md line 49); peak RSS at
J_inf 100000 measured (SESSION_STATE.md line 206, RERUN_PLAN F6); every
unit of every row measured by costprobe2 at 354.2 MB or less
(runs/costprobe2-finalize-20261011-101659).
