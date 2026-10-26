# Review of the fixed-beta rerun scripts before their first execution

## 2026-10-16, first pass

- Reviewed, as first committed: scripts/rerun_analysis.py (db25e41),
  scripts/rerun.py and scripts/rerunlib.py (3360664). After this pass's
  fixes: rerun.py 1002 lines (md5 5b3045b59f9e98bbe6a58eca852cf3b4),
  rerunlib.py 739 lines (md5 77693d4face2d2feffe66c39a216dbfa),
  rerun_analysis.py 1411 lines (md5 b7ab98affd9cc9028987825dfe2417b7).
- Written by the author of the scripts (Claude), reading them as someone
  else's code, at Rahul's request.
- None of the three has been executed in any mode. The only checks made:
  - a parse of each file under the Python 3.8 grammar (ast.parse,
    feature_version (3, 8)), as for calprec2;
  - a static walk of each file's syntax tree for names read but never
    defined. Its only reports were closures, __file__ and an exception
    name, all false positives;
  - a grep that every rl., rerun. and cp. attribute used exists in its
    module.
- The pass is against notes/ANALYSIS_CRITERIA.md, section by section.
  For each criterion it checks three things: that the docstring states it,
  that a worked example is given, and that the code implements it.

### Analysis script, section by section

| Criterion (file section) | Docstring | Example | Code | Result |
|---|---|---|---|---|
| A0 inputs verified, realization matches plan | yes | yes | load_runs | the pairing stop was missing: fixed (F8) |
| A1 complete rows only | yes | added (F9) | main | ok |
| Item 0 S-slope primary, S-curve secondary | yes | yes | cw_task | ok |
| Item 1 percentiles, one-sided bound, DIFFERENCE, TOST | yes | yes | pct, diff_verdict, Stats.one | the 90% interval and half-width were in the CSV only: fixed (F10) |
| Item 1 both verdicts on one gap | yes | yes | Stats.one note | ok |
| Item 2 W-full, REFSIZE J <= 1250, W-grid, W-ge exact fractions, pre-check | yes | yes | win_full, win_ge, cw_task | ok |
| Item 3 B, key-derived indices, joint arms, drops, flags | yes | yes | boot_idx, cw_task, Ctx.S | ok |
| Item 4 rate verdict W-full only, nothing added to -1 | yes | yes | phase 1 | ok |
| Item 5a joint gap | yes | added (F11) | paired_gaps | ok |
| Item 5b margin before gaps, groups, shared once, revisit stops, attainability | yes | yes | phase 2, Stats.one | ok; exit 6 after the margin file is written |
| Item 6 unweighted pooled mean, v_i, Q, I2 undefined, truncation | yes | yes | hetero, Stats.family | ok |
| Section 8 common rule: unit lacking a cell excluded and named | no | no | no | missing: fixed (F12) |
| Item 7 contrasts 1 to 7, signs | yes | only contrast 1 | conc_like, paired_gaps, target_contrast_paired, refsize_block, onset_block | examples added for 2 to 7 (F13); signs ok (below) |
| 8.1 CON pairs, both orientations; TMM; REGF | yes | yes | conc_like | the round-1 orientation was in the CSV only: fixed (F10) |
| 8.2 severity, sensitivity, trend | yes | added (F13) | onset_block | ok |
| 8.3 panel b1, b2, b3, both windows | yes | yes | rmap_panel | ok |
| 8.4 onset per objective and pooled, contains 1, counts | yes | yes | onset_block | per-diffusion counts printed but not written: fixed (F14) |
| 8.5 finite-J audit, F1 gate, floor, differences, count | yes | yes | audit_block | the floor flag used floats where item 2 uses exact fractions: fixed (F15); window label (F16) |
| L1 A2 coefficient; cliff, map, P-M3 not computed; P-M4 vacuous | yes | added (F13) | sigma_a2, rmap_panel | ok; verdict question D1 |
| L2 R^2 point values; P1.3 minimum ESS | yes | added (F13) | r2_blocks, phase 1 | ok |
| L3 curvature, mean per realization, departure stated | yes | added (F13) | cw_task, phase 1 | ok |
| Reference adequacy, no pooled verdict | yes | added (F13) | main | ok |
| Onset estimator gated by O1 | yes | yes | plan PASS, rerunlib hash | the GRID's hash (costprobe2) was not checked: fixed (F17) |

### The seven checks Rahul named

1. **Every quantity specified is computed, and nothing else.** Each
   quantity in items 0 to 8 and L1 to L3 maps to code (table above). The
   remaining extra outputs are the S-curve interval (item 3 specifies it),
   the one-sided bound printed on W-ge rows (a number with "sensitivity, no
   verdict"), and the pooled onset's heterogeneity (H3 specifies it). None
   is beyond the file.
2. **Signs.** Each is second level minus first:
   - c1 is d40 - d2 (d40 - d5 in TAU8 and GEOM);
   - c2 is 0.01 - 0.5, or 0.01 - 0.3 in TAU8 and GEOM, or 0.01 - 0.1 in
     SIGMA and ANISO;
   - c3 is aniso - iso; c4 is mix-0.1 - centred; c5 is 100000 - 12500;
     c6 is d80 - d5;
   - c7 is CON(0.01, 0.5) = change(0.01) - change(0.5); the pairs are
     CON(0.1, 0.5) and CON(0.01, 0.1); TMM is change(0.01) minus the mean
     of the other two changes;
   - the severity is S(3) - S(1) and S(3) - S(0.75); the audit difference
     is d40 - d2 (d40 - d5).

   The regression coefficients follow their stated models: REGF on gamma,
   the panel on Delta, the trend and A2 on S. Both orientations are
   printed for every CON pair, contrast 7 and the audit difference: in the
   CSV column round1_orientation and, after F10, on the console.
3. **Bootstrap key.**
   - The layout is rerunlib.boot_key: (20261016, 71, owner row) followed
     by key fields 4 to 15, with rep removed. That is the approved layout
     field for field, kind 71 and no field 16.
   - A shared cell has one owner, hence one key and one index stream in
     every row.
   - The paired arms share the key, so they share one index matrix,
     applied to the same kept reps (cw_task, Ctx.S).
   - The audit difference draws from the same stream at n = M.
4. **Margin before any gap; revisit stops.**
   - Phase 1 prints per-arm cell slopes only.
   - Phase 2 then prints S, both group medians and the ratio.
   - On a ratio above 1.5 it prints "MARGIN REVISIT REQUIRED", writes
     analysis_margin.csv and exits 6 before phase 3, so no gap and no
     verdict for any comparison is computed.
   - If any paired row is incomplete, no margin and no gap are computed.
5. **Onset control first, stop on failure.**
   - rerun.py --precheck runs O1 after V0, P1 and S1 (none runs a
     trajectory or the estimator) and before the plan is built.
   - On failure it exits 2 and writes no plan, so no trajectory run and no
     analysis can start: both refuse a plan without "O1 PASS".
   - The analysis also refuses a plan built with a different rerunlib.py,
     which holds the estimator.
6. **Exit codes.**
   - rerun.py: 0, 2, 3, 4, 5.
   - rerun_analysis.py: 0, 2, 6.
   - perjcalprobe.py: 0, 2, 3, 4.

   Each is documented. rerun.py did not say which code wins when several
   apply: fixed (F5).
7. **No verdict where the file says none.** None is computed for:
   - R^2, curvature and S-curve;
   - the W-ge and W-grid lines;
   - the onsets themselves (only "contains 1", a description);
   - the audit summaries, the adequacy table and heterogeneity.

   Two quantities carry a DIFFERENCE or equivalence verdict that the file
   does not state explicitly: D1 and D2 below.

### Fixed in this pass

rerunlib.py and rerun.py:
- F1. **A-BETA would have failed every ADAPT adaptive cell.**
  - control_summary.csv's beta_first is the mean of b_first. In the
    adaptive arm b_first is the beta after the first re-solve, not beta0
    (control.py lines 223 to 250; archived values 2.17581 adaptive against
    2.19167 fixed for ackley d 5 tau0 0.01).
  - Both arms start from the same beta0 (control.py line 347), so ADAPT is
    now checked against the fixed arm's row for both arms.
  - Without the fix the precheck exits 2 and no plan can be written.
- F2. **The A-BETA and A-SIGMA tolerance was looser than the archive's
  precision.** Every checked column except ess_surface's design beta was
  written with "{:.6g}", which drops trailing zeros. "1.9047" is 1.90470,
  precise to 5e-6, but the string alone gave 5e-5. The tolerance is now
  half a unit in the sixth significant digit for those columns. The format
  of each source is cited in the ARCH_CHECK comment. The docstring's worked
  example is corrected: under the old rule 1.904731 agreed with "1.9047";
  it now fails.
- F3. Worked examples added for K1, K2, K3, D-SMOKE, G-RSS, G-STOP and
  RESUME. CLAUDE.md rule 5 requires one for every criterion.
- F4. **A new stall guard, T1.**
  - Problem: a Pool worker killed outside Python, for example for memory,
    leaves its AsyncResult pending forever, and the run hangs until the
    Kaggle cap.
  - Fix: if tasks are in flight and none has completed for STALL_S
    seconds, the pool is terminated, the in-flight tasks are written as
    error rows ("stalled"), and the run exits 4.
  - STALL_S is 5 x the shard's largest measured unit wall, at least 600 s,
    or 7200 s without --timing-from. It is a guard, not a cost criterion.
  - The docstring and the summary say so.
- F5. The precedence of exit codes is now stated: 5, then 3, then 4. Every
  condition is also printed in the summary.

rerun_analysis.py:
- F8. A0 now requires each realization's seed_key to equal the key part
  of its task id. This makes "both arms hold the same key" a checked stop,
  as the checklist requires; before, it held only by construction.
- F9. Worked example added for A1.
- F10. The console line of every gap now shows:
  - the 90% (TOST) interval, the half-width, m and the equivalence
    verdict;
  - the round-1 orientation, for every CON pair, contrast 7 and the
    audit;
  - the full set of item 6 statistics.
- F11. Worked example added for item 5a.
- F12. The section 8 common rule was not implemented: "a unit lacking a
  cell is excluded, named, and the reduced k printed". Stats.family now
  excludes units with a non-finite estimate, names them in the output and
  the note, and pools the rest.
- F13. Worked examples added for:
  - contrasts 2 to 7;
  - 8.2, A2, L2, L3 and reference adequacy.
- F14. The J4 per-diffusion counts are now written to
  analysis_onsets.csv, not only printed.
- F15. The audit floor flag now uses J x tau0 < 1 in exact fractions of
  the tau0 string, as item 2's W-ge does. On this grid the float
  comparison gives the same answer at every (J, tau0), including the exact
  boundaries 100 x 0.01 and 20 x 0.05, so this changes no output. It removes
  a second, different rule for the same boundary.
- F16. The audit difference rows carry window "audit" instead of a J
  label in the window column; J is in the group column.
- F17. The analysis now refuses a plan built with a different
  costprobe2.py (GRID), as rerun.py's run mode already did. It previously
  checked rerunlib.py only.

### Needs Rahul's decision

- D1. **Does audit A2's coefficient carry the DIFFERENCE verdict?**
  - The twelfth message says "a regression coefficient with its interval
    under the estimand/shape line".
  - Section 8's common rules give every coefficient there the DIFFERENCE
    rule: REGF, the panel coefficients and the trends.
  - A2 is recorded in the audit section, not section 8. The code applies
    the DIFFERENCE rule, by analogy with the other coefficients.
- D2. **Does the pooled diffusion gap carry an equivalence verdict?**
  - H2 says "the pooled diffusion gap is reported the same way": per cell
    and pooled, the pooled figure with its heterogeneity.
  - Item 5b's equivalence verdict and attainability were specified for
    the per-cell gap.
  - The code gives the pooled gap the same DIFFERENCE, equivalence and
    attainability treatment as a cell, reading "the same way" as "as the
    per-cell gap". The other reading gives it estimate, interval and
    heterogeneity only.
- D3. **May the analysis run before every row is complete?**
  - A1 analyses complete rows and skips the rest, so the script can run
    on the thirteen archived-beta rows while calprec2's table is pending.
  - The criteria are fixed in its docstring either way.
  - But a partial run shows results before the calibrated rows exist. A
    rule "run only when all seventeen rows are complete" would be a
    one-line stop.
  - Even with partial runs allowed, no diffusion gap is computed until
    SIGMA and ANISO are complete, because 5b's margin needs all five
    paired rows.

### Left, noted, not fixed

- N1. G-STOP's clock starts when the pool starts, not when the Kaggle
  session starts. Bundle rebuild, plan reading and P1 take place before
  it. 36000 s leaves 7200 s of the 43200 s cap for them, the margin
  calprec2 uses.
- N2. A shared cell is run by the job whose --rows contain its owner. An
  ONSET-only job does not run the RMAP-owned cells, so ONSET is incomplete
  until RMAP's job has run. That is a scheduling fact, not a defect.
- N3. G-RSS reports a worker's running maximum. A flagged row can reflect
  an earlier task in the same worker. costprobe2 measured every unit at
  354.2 MB or less against a 3072 MB budget.
- N4. RESUME compares every parameter except the folder list, including
  workers and stop_after. That is a strict reading of rule 17.
- N5. CONC and TAU8 have no archive check of their betas, because they are
  calprec2's new betas. calprec2's own criteria govern them; their sigma is
  the module default, 0.2.
- N6. perjcalprobe.py was not part of this pass.

### What the first executions must show

- rerun.py --precheck:
  - V0: every factor "ok" and every Table 2 count "ok";
  - P1 and S1: every line "ok";
  - O1: ten lines "ok" (computed onset equal to the table's);
  - A-BETA/A-SIGMA: 0 FAIL;
  - K1, K2 and K4 PASS, with K4 listing exactly the expected sharing;
  - a plan folder written.
  - Any FAIL is reported as it stands; no tolerance is loosened without
    Rahul.
- rerun.py --smoke: "identical" for every module.
- rerun.py run: no ERROR, OVER BUDGET, F1 FAILED or T1 STALL line.
- rerun_analysis.py, first run: every row present in its run folders
  marked complete; no A0 stop.

## 2026-10-16, second pass: D1 to D3 decided and applied

- Rahul's decisions (recorded in notes/ANALYSIS_CRITERIA.md, thirteenth
  message):
  - D1: A2 takes the DIFFERENCE rule, for consistency with every other
    section-8 coefficient;
  - D2: equivalence and attainability per cell only;
  - D3: no analysis until all seventeen rows are complete.
- N1 to N5 accepted as recorded. N2, the ONSET ownership point, is to be
  stated in the rerun runbook: a job running ONSET alone does not run the
  cells RMAP owns (d 10 and 40, r 1.0 to 3.0, tau0 0.1), so ONSET reads as
  incomplete until RMAP's job has run. Launch them together, or RMAP first.

### Applied (scripts/rerun_analysis.py only)

- D1: no code change; the code already applied the DIFFERENCE rule to A2.
  The docstring now states the rule and Rahul's reason, in place of "see
  the review note".
- D2: Stats.family passes no equivalence to the pooled row. The note
  "equivalence per cell only (D2)" is written on it. Docstring item 5b
  states the rule, the reason, the reading of H2 that governs, and a worked
  example.
- D3: after the completeness table, any row that is not complete stops
  the run. The script prints "INCOMPLETE: analysis refused (D3)" with the
  rows, creates no output folder and exits 7.
  - The A1 docstring is rewritten to state the rule, the reason and an
    example.
  - Exit code 7 is added to the documented list, and each code says when
    it fires: 2 and 7 before any statistic, 6 after the per-cell phase and
    the margin.

### Re-review of the changed code

- With D3, every later statistic sees all seventeen rows. Two branches
  are now unreachable: the "paired rows incomplete" branch of the margin,
  and the "not analysed: incomplete" lines of phase 3. They are left as
  defensive code; their messages cannot appear in a run that passes A1.
- The pooled diffusion gap still prints its 95% interval and DIFFERENCE
  verdict. Item 1's DIFFERENCE rule applies to every reported interval,
  and D2 removes only equivalence and attainability.
- Exit codes: rerun_analysis.py 0, 2, 6, 7; rerun.py 0, 2, 3, 4, 5;
  perjcalprobe.py 0, 2, 3, 4. Distinct within each script and documented.
- rerun.py and rerunlib.py are unchanged by this pass.
- The parse under the 3.8 grammar was repeated after the edit.

### Before the precheck

Nothing further needs Rahul's decision before rerun.py --precheck runs.
The precheck reads no analysis criterion. Its own criteria (V0, P1, S1,
A-BETA, A-SIGMA, C2, O1, K1, K2, K4) are fixed, and on any failure it
stops and reports the numbers without loosening a tolerance.

## 2026-10-26, third pass: the calibrated r rows (CAL1 to CAL5)

- Reviewed: scripts/rerun_analysis.py as changed for RMAP-CAL, CLIFF-CAL
  and ONSET-CAL (1807 lines, md5 a2d75624c0231233f415de951f907344), and
  notes/queues/rerun-cal3.json. Against notes/ANALYSIS_CRITERIA.md,
  fourteenth message, CAL1 to CAL5.
- Not changed, deliberately: rerun.py, rerunlib.py and costprobe2.py. The
  plan runs/rerun-plan-20261026-210435 records rerunlib's and costprobe2's
  hashes, the analysis refuses a plan built with different ones, and the
  queue pins all three. A change to any of them would need a new precheck
  and would break the K5 link to the seventeen-row plan.
- Written by the author of the change (Claude). A second, independent read
  was made by a separate agent, given the code and the criteria but not
  this review; its findings and their disposition are below.
- Nothing was executed in any mode. The checks made:
  - a parse under the Python 3.8 grammar (ast.parse, feature_version
    (3, 8));
  - a static walk for names read but never bound: only __file__;
  - a grep that every rl. and rerun. attribute used is defined in its
    module (the two the grep missed, JCOLS and KIND_BOOT, are bound by
    tuple assignment in rerunlib.py);
  - the CAL4 comparison functions (as_strings, compare_old), extracted
    from the file and run against runs/rerun-analysis-20261025-051314 fed
    to itself through the new column lists: every file PASS, 0
    differences. Negative control: one value in analysis_stats.csv
    lengthened by one digit gives FAIL with that row and column. This tests
    the comparison, not the analysis;
  - the queue definition, passed through rerunq.py's own
    validate_definition (extracted from the file): it validates. Its job
    names rerun-smoke-cal3-a1, rerun-cal3-s0of2-a1, rerun-cal3-s1of2-a1
    match nothing under runs/ or logs/ (L3);
  - the seventeen-row plan is a byte prefix of the new plan (cmp), so
    cells load in the same order.

### Criteria against docstring, example and code

| Criterion | Docstring | Example | Code | Result |
|---|---|---|---|---|
| A1 over twenty rows (CAL4) | yes | yes | main, A1 | ok; exit 7 unchanged |
| CAL1 m not recomputed; pool = the five rows | yes | yes | MARGIN_ROWS, arm_sds | ok; rerunlib.PAIRED now has eight rows and is no longer used for S |
| CAL1 ratio guard, both ratios, 1.5, shared cell once | yes | yes | main, CAL1 block | NaN passed silently: fixed (G4) |
| CAL2 mirror, per row | yes | yes | paired_gaps, target_contrast_paired, rmap_panel, onset_block | ok; rmap_panel and onset_block take the row; the J2 header was hard-coded "ONSET": fixed (G5) |
| CAL2 nothing between probe and calibrated rows | yes | n/a | none computed | ok |
| CAL3 flag on every statistic, unit and pooled | yes | yes | na_label, na_flag, Stats.one, Stats.family | audit, R^2, J4 counts and the margin pool were missing in the first draft: fixed before the review (G1) |
| CAL4 order: 17 rows, margin check, full check, then calibrated rows | yes | yes | main | ok |
| CAL4 the flag column the only difference | yes | n/a | ONSET_COLS, guard file | a row column in _onsets and seven rows in _margin: fixed (G2) |
| CAL4 the reference folder | yes | added (G3) | main | not pinned: fixed (G3) |
| CAL4 exit 8, nothing for the calibrated rows | yes | yes | main | ok; the margin is checked first and exits 8 before any gap |
| CAL5 split per calibrated row | yes | yes | split_category, main | ok; a shared cell counts in both rows, stated |

### The seventeen-row path, function by function

- Emission order: BASE_ROWS is costprobe2.ROW_ORDER, the old rl.ROWS.
  MARGIN_ROWS is the old rl.PAIRED in the same order. The old rl.CALROWS
  equals base_cal. Phase 3 calls the same functions in the same order.
- Phase 1: the same jobs, the same instance order. A calibrated-row job
  cannot collide with a seventeen-row one: the owner index is in the boot
  key.
- Values: every unit tuple gains a fourth element (its cells), which only
  feeds not_adequate. Notes, verdicts, orientations and estimates are
  computed as before. Both readers found every family() call site passing
  four-tuples.
- At the check, every in-memory table holds seventeen-row records only.

### Found and fixed in this pass

- G1. CAL3 coverage, first draft: the not_adequate column covered
  analysis_stats and analysis_cells only. Added: audit summary rows, R^2
  rows, the onset rows and J4 counts, and the margin pools.
- G2. CAL4's "the flag column is the only permitted difference" was
  broken twice (independent read): analysis_onsets.csv had a new row
  column, and analysis_margin.csv grew from 7 to 14 rows. The calibrated
  rows' onsets now go to analysis_onsets_calibrated.csv, and the guard
  values and pool flags to analysis_margin_calibrated.csv. Every old file
  now differs from N39's only by not_adequate (checked by header
  comparison against the old folder).
- G3. --reproduce accepted any folder whose sha256.txt verified
  (independent read). It is now pinned: basename
  rerun-analysis-20261025-051314 and sha256.txt hashing to
  01c202c8d2fae83c0fe683d1cc55a802dd59c2e27fdf1fab158578a5e029d5e1;
  otherwise exit 2.
- G4. A NaN median in the ratio guard gave "no revisit" (independent
  read). An undefined ratio is now treated as REVISIT and says so.
- G5. The J2 section header read "ONSET" for ONSET-CAL (console only).

### Needs Rahul's decision

- R1. On a calibrated-row REVISIT, the code withholds ALL of their
  phase-3 output: gaps, contrast 2, the J3 panel, contrast 6, J2, and also
  the onsets and J4 counts, which carry no verdict. CAL1 as recorded says
  "no gap, DIFFERENCE verdict or equivalence verdict". Every contrast and
  coefficient carries a DIFFERENCE verdict, so withholding those follows
  from the wording. Withholding the onsets and J4 counts goes further
  (independent read). The code matches its docstring; the criterion does
  not authorize the extra step explicitly.
  Recommendation: keep it. It is what 5b does for the seventeen rows
  (exit 6 before phase 3, onsets included), so one rule covers both. A
  REVISIT means the margin is in question, and onsets printed alone would
  be a partial set, which D3 exists to prevent.
  DECIDED by Rahul, 2026-10-26: withhold them; the code stays as written.
  His reason: 5b already does this for the seventeen rows, and onsets
  printed alone are the partial set D3 exists to prevent. A reader would
  have numbers from a row whose margin is in doubt, with nothing to place
  them against.

### What the first execution must show

- The smoke and both shards: exit 0, D-SMOKE PASS, the header hashes the
  queue pins.
- The analysis, on the laptop (Python 3.12.3, NumPy 2.5.3), with all eight
  run folders (the four arch shards, the two cal shards, the two cal3
  shards): "margin equals ...", then "17-ROW REPRODUCTION PASS", then the
  calibrated rows' ratio guard printed before any of their gaps.
