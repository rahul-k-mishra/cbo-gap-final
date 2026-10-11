# Review of scripts/calprec2.py before its first execution

- Reviewed: scripts/calprec2.py as first written, 2026-10-11, md5
  1a21bae5cc25041248da95acd62e3276, 1377 lines (the docstring is 273 of
  them).
- Written by the author of the script (Claude), reading it as someone
  else's code, at Rahul's request.
- Nothing has been fixed in response, as instructed.
- The script has never been executed in any mode. The only check made was
  a parse under the Python 3.8 grammar (ast.parse, feature_version (3, 8)).
- Line references are to that file.

The findings are in seven groups:

- A: design defects that break the intended workflow or would give wrong
  answers;
- B: places where it can produce a wrong number rather than an error;
- C: criteria that can pass vacuously;
- D: departures from notes/CALPREC_V2_SPEC.md;
- E: archived and imported behaviour, verified or assumed;
- F: stops and hangs;
- G: not tested at all.

The most serious items are A1 to A4.

## A. Design defects (the workflow as written does not work end to end)

- A1. Continuation jobs cannot be finalized together with the job they
  continue.
  - The climb is capped per job by --max-rung, because G-CAP refuses a job
    whose upper bound exceeds 21600 s. Unresolved cells are meant to
    continue in a later job with --cells and --start-rung.
  - That later job recomputes phase A, whose seeds make it identical, so it
    writes rows with the SAME task ids ("A|cell|N|rep") as the first job.
  - read_folders, which finalize uses, accepts a repeated task id only over
    an earlier error row, and exits 2 on a repeated complete row
    (lines 643-647).
  - The first job and its continuation therefore cannot be finalized
    together: finalize stops at the first phase-A row.
  - The same holds for climb rows if the continuation starts at the last
    rung already evaluated, which A2 says it must.
  - Any cell that needs more than one job cannot reach the beta table.
    Given G-CAP, that is every cell whose climb goes high.
- A2. The continuation guidance points at the wrong rung.
  - In-run, an unresolved cell is reported as ("unresolved", hi), where hi
    is the highest rung evaluated and not yet judged (line 855). When
    --start-rung equals --max-rung, it is ("unresolved", hi + 1) instead
    (line 841), which is inconsistent with line 855.
  - finalize labels it "unresolved, continue at rung L_REF[top + 1]"
    (line 1135), one rung higher.
  - Rung top can only be judged once rung top+1 exists. So the right
    continuation is --start-rung top, which re-evaluates top (A1's
    duplicate) and then top+1.
  - Following finalize's label skips the judgement of rung top. If top was
    the smallest adequate rung, n* comes out one rung too large: a wrong
    n*, and therefore wrong C1, N_cell and beta, with no error raised.
- A3. The streamed case-(a) solve at 1G may be infeasible on the laptop.
  - D5a puts every case-(a) solve on the laptop: a plain 200-step streamed
    bisection, each step one full regeneration of the 1G stream.
  - refscale measured one ackley d = 40 1G replicate at 3225.4 to 3236.8 s
    on one Kaggle worker (ledger N18).
  - At that per-worker speed, 200 steps are about 645,000 worker-seconds
    per cell, my arithmetic on the logged wall time, plus E2 at 1M and the
    six 1G evaluation replicates. On the laptop's 2 workers that is at
    least about 89 hours per cell, if a laptop worker matched a Kaggle
    worker; the laptop's speed for this has not been measured.
  - How many cells land in case (a) is unknown until calprec2 runs. The
    tau0 = 0.01 cells of heavy-tailed objectives at large d are the
    candidates (N18).
  - The script prints no projection for laptop mode.
  - This is a feasibility problem in the decided design (D5, D5a), not a
    coding error. It should be decided before the full run, not
    discovered after it.
- A4. Memory of the held solve at 64M is unmeasured and close to the
  budget.
  - The held cap is 1024 MB of values (134217728 doubles). So the largest
    held solve is at n* = 64M (512 MB); 256M goes to the laptop.
  - exactcal.beta_on_ensemble calls log_ess_of. That allocates -beta f, then
    2a, then a - max and exp(...) inside _logsumexp: several temporaries
    the size of the array.
  - At 64M that is plausibly 2 to 3 GB in one worker, against the 3072 MB
    budget.
  - The spec's reason for the 1024 MB cap ("leaving headroom inside the
    budget") ignores those temporaries. No run has measured the peak RSS
    of a 64M beta_on_ensemble.

## B. Places that can produce a wrong number rather than an error

- B1. A2's wrong continuation rung (above).
- B2. Incomplete cells are labelled as case (b).
  - In finalize, a cell with an adequate rung whose C1 pass, phase B or C'
    rows are missing or errored gets a flag. It then falls through to the
    solve branch and is labelled "pending (case b, solve at n ...)"
    (lines 1139-1143).
  - Case (b) means "no sufficient N, or C6 failed". An incomplete cell is
    not that. The label is wrong, though the flag is printed.
  - In-run, the same cells drop silently out of both N_cell and case_b
    (lines 876-893, 905-917).
- B3. The projection bounds are not bounds.
  - G-CAP's "upper bound" assumes perfect scaling over workers. The phases
    are separated by barriers, so workers sit idle while the last task of
    a phase finishes.
  - The real wall can exceed the "upper bound". The 6-hour ceiling check
    can therefore pass for a job that does not fit.
  - The "lower bound" assumes adequacy at the start rung and no case-(b)
    solve. It is a best case, not a bound.
- B4. Laptop evaluations can fail R1 spuriously.
  - R1 compares, as repr strings, tau_hat at beta_adq from an S evaluation
    with the climb's value at the same rung.
  - For a case (a) or (b) solved on the laptop, the evaluation runs on
    NumPy 2.5.3 and the climb ran on Kaggle's NumPy 2.1.3.
  - The determinism gate shows agreement within half a unit of the stored
    digits across those versions (ledger K4), not bitwise agreement of
    exp and sum. A last-bit difference makes finalize flag R1 and exit 3,
    though nothing is wrong.
- B5. Reference keys carry tau0 = 0, as the spec says, so cells that differ
  only in tau0 share reference streams.
  - Their adequacy verdicts and tau_ref estimates are therefore correlated,
    not independent.
  - That is intended, but no output says so. An analysis that treats the
    cells' tau_ref values as independent would be wrong.
- B6. Phase A uses the 24 draws at N = 4000000 for beta_adq, which is the
  climb's beta. For tight targets that beta's own tau(beta_adq) can be off
  target (ledger N19). That does not bias the adequacy test, which is a
  test of the reference at that beta, but it should be read as "adequate
  at beta_adq", not "adequate at tau0".
- B7. Smoke unit costs come from one unit per (module, objective, d, law),
  measured at tau0 = 0.1.
  - t_beta is a difference of two walls, (w145 - w1) / (144 n). Timing
    noise can make it small or even negative, which would shrink the
    projection.
  - No check on the sign or size of t_beta exists.

## C. Criteria that can pass vacuously

- C1. V2 checks the module's source line, not this script's sampler.
  - It confirms that one_realisation's first rng line is the expected text.
  - It does not compare that line with what costprobe2.probe_sample, the
    sampler this script actually uses, does. The two are equivalent by my
    reading (section E), but V2 cannot fail if probe_sample were wrong.
- C2. E1 can be skipped entirely.
  - E1 runs only when replicate 0 of the 1M rung is evaluated.
  - A job started with --start-rung above 0 never evaluates 1M, so E1
    never runs for its cells, silently. The streamed composition is then
    unchecked in that job.
- C3. V0(b) partly duplicates costprobe2's P0(b).
  - The count check multiplies my cal_cells lists by my own lists of the
    factors that do not enter beta, all drawn from GRID. GRID is verified
    against the source by V0(a), so the values are checked.
  - But a wrong choice of WHICH factors enter beta, for example leaving
    the law out of a cell while multiplying by the number of laws, could
    still give Table 2's count.
- C4. R1 can be vacuous after a resume.
  - When the C rows of a rung and the P or E rows that regenerate it both
    come from the same earlier folder, R1 compares two values that were
    written together.
  - R1 then shows nothing about regeneration in this run.
- C5. G-CAP passes for any job whose cells lack throughput entries only if
  the check on missing cells is reached. It is (line 1294), but a smoke
  folder that covers the cells with stale or wrong unit costs passes it.
  G-CAP is only as good as the smoke.
- C6. No exit code reflects errored tasks or incomplete cells.
  - The exit code is 3 only for E1 or R1, and 2 for setup.
  - A job in which every phase-A task errored exits 0. The errors are
    printed, but nothing fails.

## D. Departures from notes/CALPREC_V2_SPEC.md

- D1. Case (b) is solved on an independent kind-34 stream and evaluated on
  all six replicates. The spec says to solve on one replicate and evaluate
  on the other five. Stated in the docstring (CB); needs Rahul's decision.
- D2. A chunk index is appended to every seed key (SeedSequence(key +
  (chunk,))). This lets a chunk be regenerated alone, and lets laptop
  passes run in parallel. Stated in the docstring; not in spec 7.
- D3. The outputs are merged.
  - The spec's calprec2_cal.csv, calprec2_ref.csv and calprec2_prod.csv
    are one file, calprec2_tasks.csv.
  - That file has one row per task, with per-beta values as ";"-joined
    repr lists, instead of one row per (cell, n, rep, beta).
  - Done so that a task is a single row with one end marker.
- D4. C5m at beta_prod is not computed or reported. Spec 5 says it is
  "evaluated afterwards, in Phase C', and reported"; C' computes only C6.
- D5. Some reporting is missing.
  - The beta table carries no G-RSS verdict: rss_flag is set on task rows
    but not propagated.
  - X1/X2 relative errors are not computed. Only the exact value of the
    final beta is written.
  - S1 shares are written per task but never summarised.
- D6. Progress is printed every 50 tasks, not one line per task with
  projected time (spec 10). The largest RSS per module is not printed at
  the end.
- D7. Plan mode does not refuse oversized held arrays (spec 5, G-RSS).
  values_held raises at run time instead, which is an error row.
- D8. calprec2_plan.csv lists each cell's shard and rows, but not V0's
  counts.

## E. Archived and imported behaviour

Verified by reading the source this session:

- exactcal.beta_on_ensemble, log_ess_of and _logsumexp (exactcal.py
  146-180): the bracket 1e-10 to 1e10, 200 geometric steps, the comparison
  "log_ess_of(fvals, mid) > goal", and the return sqrt(lo hi) with the
  achieved fraction. streamed_bisect mirrors these (lines 974-995).
- regime.SYNTH_PARAMS and make_synth (regime.py 172-180; law.py 191-212):
  (kappa, rho, omega) and a_i = kappa^(i / max(d-1, 1)), as X2 uses.
- mechanism.draw_initial and control.draw_initial: any law other than
  "centred" is the 0.1 mixture. regime.draw_initial takes x* explicitly.
- The first rng line of each one_realisation, which V2 checks (read for
  all nine modules used).

Exercised by the costprobe2 Kaggle smoke and full run (N22), but not under
this script:

- costprobe2.probe_sample and objective_of for every module.
- default_rng(SeedSequence(...)) on NumPy 2.1.3.

Assumed, not verified:

- E1. Every module's objective is row-wise, so f evaluated chunk by chunk
  equals f on the whole array. I read sphere, rastrigin and the synthetic
  family. I did not read ackley, griewank, levy or rosenbrock in every
  module line by line for any cross-row term.
- E2. inspect.getsource returns one_realisation's source when the archive
  is the read-only Kaggle mount.
- E3. exactcal._logsumexp, a private helper, behaves on chunk vectors as
  on whole arrays. It does by its two lines, but no test here confirms the
  composition beyond E1.
- E4. multiprocessing on Kaggle forks, so costprobe2's import (which loads
  twelve modules) is not repeated per task. Fork was observed in
  costprobe2's runs, not this script's.

## F. Stops and hangs

- F1. There is no per-task timeout.
  - run_pool uses imap_unordered with maxtasksperchild = 1, the pattern
    costprobe2 replaced after review item E3.
  - A worker killed by the out-of-memory killer, for example a 64M held
    solve (A4), can leave the pool waiting forever. On Kaggle that runs to
    the 12-hour cap, and the output is lost (K5).
- F2. A1's finalize stop: exit 2 on every multi-job cell.
- F3. R1's spurious stop on laptop evaluations: exit 3 (B4).

## G. Not tested at all

- G1. Every mode and every code path: plan, smoke, full, shard, resume,
  streamed and finalize.
- G2. The barrier scheduler and the climb state machine across rounds.
- G3. The finalize verdict logic, against any real or constructed rows.
- G4. The memory of every phase (A4) and the run time of every phase. The
  smoke is designed to measure the run time.

## What I would want decided before any fix

- A1 and A2: how a multi-job cell should be represented. Options:
  - task ids that carry the job and accept identical recomputed rows;
  - finalize accepting a repeated complete row when its values are
    identical;
  - continuation jobs that skip phase A by reading beta_adq from an
    argument.
- A3: whether the case-(a) streamed solve stays on the laptop (D5a), given
  the per-cell cost implied by refscale's 1G walls. The alternatives are
  fewer bisection steps, or a different case-(a) rule. Both would be
  Rahul's decision, as D5a was.
- A4: a measured peak RSS for a 64M held solve before the cap is relied
  on.
- D1: the case (b) interpretation.
- F1: whether to adopt costprobe2's process-per-task scheduler with a
  timeout.

---

## 2026-10-11, second pass: Rahul's decisions applied, items closed and left

What changed:

- scripts/calprec2.py went from md5 1a21bae5cc25041248da95acd62e3276
  (1377 lines, 203a564) to md5 0b82f0805700b449f2d6faf836fa5649 (1515
  lines). Diff against 203a564: 888 lines inserted, 750 deleted.
- New script: scripts/memprobe.py, md5 1919354565689574db411a42e40a48a6.
- Nothing was executed. Both scripts were parsed under the Python 3.8
  grammar only.

### Decisions applied

- A3. D5a and E2 are withdrawn (ledger N24). The case (a) and (b) solves
  are a streamed grid solve on Kaggle:
  - 64 betas per pass, on one pass over an independent kind-34 stream;
  - passes stop at relative width <= 1e-6;
  - E3 checks the grid solve against beta_on_ensemble on a held 1M
    stream, within 1e-6.
  Rahul's "two passes, below 1e-4" was corrected: two passes give about
  1.2e-2. The rule needs five, and the script prints the number.
- A1, A2. Phase A goes to its own file. Continuation jobs read it, and the
  climb rows, through --inputs (verified). Each cell's rung range is
  derived from the inputs, and the continuation point is the highest
  evaluated rung. No task id is written twice.
- A4. A held solve above 1M no longer exists: case (b) also uses the grid
  solve. scripts/memprobe.py measures the 64M held solve before any held
  solve is reintroduced. Using the grid solve for case (b) as well was my
  choice, and it is put to Rahul for approval.
- D1 (case (b)). The independent stream with all six replicates stands. It
  is recorded in the spec (section 6) with the reason: the median of six
  matches c6, and judging is kept separate from choosing.
- F1. costprobe2's process-per-task scheduler with a timeout is adopted:
  error rows for timeouts and dead workers, and exit codes 3 and 4.

### Closed by this pass

- A1, A2: closed by design. See new item N1 for a remaining edge.
- A3: closed by design. The cost is now about eleven 1G passes per
  case-(a) cell, not 200; see N5.
- A4: no held solve above 1M remains to need the number. The probe is
  written.
- B2: finalize labels a cell with missing rows "incomplete (<phase>)",
  never as a case.
- B3: the projection is called an "estimate (perfect scaling; barrier idle
  and tails ignored; NOT a bound)" and a "best case", never a bound. See N3
  for a gap in the estimate itself.
- B4: R1 compares rows only when their env (Python and NumPy) is equal.
  Otherwise it reports "not applicable (env differs)", which is not a
  failure. With D5a gone, all rows should come from Kaggle anyway.
- B5: the correlation of reference streams across tau0 is stated in the
  docstring.
- C2: every cell's first job starts at 1M, so E1 always runs. finalize
  flags "E1 not run" (exit 4) if it is absent.
- C6: an errored or timed-out task gives exit 4. Exit 3 takes precedence.
- D1: recorded in spec and review, with the reason.
- D2: the chunk index in the seed key is now in the spec (11b).
- F1: closed by the adopted scheduler.

### Left, not in this pass's list

- B6: beta_adq's own tau.
- B7: the smoke's t_beta sign.
- C1: V2 checks the module line, not probe_sample.
- C3: the V0(b) factor choice.
- C4: R1 after a resume.
- C5: G-CAP is only as good as the smoke.
- D3: merged output files. There are now two: phaseA and tasks.
- D4: C5m at beta_prod is still not reported.
- D5: the G-RSS verdict is not in the beta table, X1/X2 relative errors
  are not computed, and S1 shares are not summarised.
- D6, D7, D8: reporting and plan details.
- E1 to E4: the assumptions.
- G1 to G4: nothing has run.

### New issues found re-reading the diff

- N1. A cell already resolved in an earlier job keeps climbing if it is
  given to a continuation job.
  - starts = highest climbed + 1 does not look at whether the inputs
    already show an adequate rung or case (a). The job then climbs past
    n*, judges the wrong pair of rungs in-run, and can run a C1 pass at a
    higher rung (new task ids, wasted work).
  - finalize recomputes n* as the first adequate rung from all rows, so
    the beta table is right. The in-run status is wrong, and compute is
    wasted.
  - Fix would be: judge every pair of rungs already in the inputs before
    choosing the start.
- N2. finalize does not recompute E3, or check that beta_s came from a
  grid solve that met its stop rule.
  - It trusts the E rows' first beta, and a cell whose E3 failed in-run
    simply lacks E rows.
  - Such a cell gets "incomplete (solve, ...)" and exit 4 in finalize, not
    "E3 FAIL" and exit 3. The job itself exits 3.
- N3. The worst-case estimate omits a C1 pass at 256M when --max-rung is
  1G.
  - With --max-rung 5, the estimate counts the climb and a 1G solve, but
    not the C1 pass, C' and an n* solve at 256M, which happen if the cell
    is adequate at 256M.
  - The same gap is in the largest-task figure that sets TIMEOUT_S. A
    256M C1 pass at 145 betas can exceed a 1G climb replicate at one beta
    when t_beta x 145 > 3 t_draw. TIMEOUT_S would then be too short, and
    those tasks would time out (error rows, exit 4).
- N4. Process-per-task overhead in phase A.
  - Phase A is 144 tasks per cell (6 levels x 24 draws). With one fresh
    process per task, a job of many cells forks one process for every
    small task, at N = 4000 too, where the work takes milliseconds.
  - The fork overhead is not in the estimate. Its size has not been
    measured.
- N5. A case-(a) cell is still expensive.
  - Climb rungs up to 1G (six replicates each), E3, five grid passes over
    a 1G stream, and six 1G evaluation replicates.
  - At refscale's ackley d = 40 1G wall (3225.4 to 3236.8 s per replicate),
    that is of the order of tens of thousands of worker-seconds per cell.
    This is arithmetic on logged walls, not a measurement of calprec2.
  - The number of case-(a) cells is unknown until calprec2 runs. The
    calprec2 smoke and plan will give the job estimate.
- N6. finalize finds the grid passes by splitting task ids on "|p". That
  works because no module, objective or law name contains "|p", but it is
  fragile.
- N7. The grid solve requires the first grid point to lie above the goal
  and takes the largest index above it. If the computed log-ESS were not
  monotone across the grid (rounding in a flat region), this choice could
  differ from the bisection's path. E3 would catch the difference only at
  1M, not at the solve size.
- N8. Smoke timeout. TIMEOUT_S is max(600 s, 5 x 2 x (6e6 points /
  3.16e5)), from refscale's ackley rate. The solve and the 145-beta pass are
  not modelled; the doubling and the 600 s floor are judgement, not
  measurement.

### What the first executions must show

- calprec2 --plan: V0, V1 and V2 PASS; the cell count per module; each
  cell's rung range.
- memprobe: the 4M and 16M solve peaks; the gate decision; and, if 64M
  ran, its solve peak against 3072 MB.

---

## 2026-10-11, third pass: N1 to N5 decided and applied

What changed:

- scripts/calprec2.py went from md5 0b82f0805700b449f2d6faf836fa5649
  (03d0174) to md5 c5b6052f181fed72a6c8d92a63cb69a8 (1636 lines). Diff
  against 03d0174: 222 lines inserted, 101 deleted.
- Not executed; parsed under the Python 3.8 grammar.

### Closed

- N1. A continuation job skips a cell whose inputs already show an
  adequate rung or case (a).
  - The status comes from judge_rungs, which judges every pair of climbed
    rungs; finalize uses the same function.
  - The rung-range table prints "skipped: adequate at <n> in the inputs"
    or "skipped: case (a) in the inputs". It notes that the cell's
    unfinished later phases, if any, are completed only by a rule-17
    resume of the job that resolved it.
- N2. finalize replays the E3 grid solve (G3 rows) and the solve (G rows)
  with grid_step, the pass function the job itself uses.
  - E3 is recomputed against the held 1M solve. A failure is labelled
    "E3 FAIL (case x)", flagged, exit 3.
  - beta_s is taken from the replay, not from the evaluation rows. If the
    evaluation rows evaluated a different beta, the cell is flagged, exit
    3.
  - The fragile "|p" task-id parsing (old N6) is gone: replay builds each
    block's task id directly.
- N3. cell_costs computes, per cell:
  - the climb from the cell's start to --max-rung;
  - the adequate branch at the rung below --max-rung: the C1 pass with 145
    betas, B, C', and a case (b) solve;
  - the case (a) branch at 1G, only when --max-rung is 1G.
  The worst case takes the larger branch. The largest single task, which
  sets TIMEOUT_S, ranges over every task type in both branches.
- N5. The plan's rung-range table prints each cell's worst case and its
  case (a) solve cost (worker-seconds) when --throughput is given. It
  prints "could become case (a) at worst: k": all cells run, when
  --max-rung is 1G. G-CAP refuses the job (exit 2) when the case (a)
  solves, summed over those k cells and divided by workers, exceed 21600 s.

### Left, by decision

- N4. One process per task for phase A's 144 small tasks per cell (Rahul,
  2026-10-11). The overhead is bounded by the task count times a few
  milliseconds, and the scheduler's uniformity is worth more than the
  saving. Revisit if the smoke shows otherwise. Recorded in the docstring
  (T1) and the spec (11b).

### Found and fixed while re-reading the diff (not in Rahul's list)

- R1 (this pass). The grid-consistency check in grid_solve_round compared
  stored betas with [float(repr(x)) for x in grid], where grid held numpy
  float64 values. Under NumPy 2, repr of a numpy scalar is
  "np.float64(...)", so float() of it raises ValueError. That would have
  crashed the job's parent process at the first grid pass.
  - Fixed in the N2 refactor: grid_of returns Python floats, and
    grid_step compares the lists directly.
  - I am reporting it because the instruction for this pass was to fix
    the listed items, and this is outside them. It is a crash, not a
    wrong number, and leaving it would make every grid solve fail.

### New issues found re-reading the diff

- T1. calprec2_plan.csv still lists skipped cells with a start rung, and
  does not mark them as skipped. Only the console table says "skipped".
- T2. The worst case charges every cell the adequate branch at the rung
  below --max-rung, even a cell whose start is already above it. That
  over-estimates, which is the safe direction.
- T3. "Could become case (a) at worst" counts every cell run when
  --max-rung is 1G. That is the honest worst case. It may make G-CAP
  refuse jobs that would in fact fit, which can only be resolved with
  fewer cells per job.
- T4. The in-run E3 (in job) and the finalize E3 (replay) compute the same
  thing by two code paths that share grid_step. A disagreement between
  them is possible only through the held 1M solve or the comparison, and
  is not checked.

### Still left from earlier passes

- B6, B7, C1, C3, C4, C5, D3, D4, D5, D6, D7, D8, E1 to E4, G1 to G4.
- Second-pass N7 (grid monotonicity) and N8 (the smoke timeout's judgement
  constants).

## 2026-10-11: A4 resolved by measurement (ledger N25)

- logs/memprobe.log: the 64M held beta_on_ensemble peaked at 2472.8 MB,
  within the 3072 MB budget (held array 752.2 MB; solve 710.1 s on the
  laptop). The 4M and 16M peaks were 294.3 and 641.7 MB.
- The design holds nothing above 1M, so the number bounds an unused path.
- 128M would exceed the budget, by arithmetic on the probe's numbers (not
  measured).
- The probe's linear gate under-predicted 64M (2031 MB extrapolated against
  2472.8 MB measured).
