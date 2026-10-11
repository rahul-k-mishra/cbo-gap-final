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
