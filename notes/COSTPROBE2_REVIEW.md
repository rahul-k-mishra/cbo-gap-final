# Review of scripts/costprobe2.py before its first execution

- Reviewed: scripts/costprobe2.py at commit 3d42589, md5
  c1ef6d574fa0e3f161df28c52f604672, 1089 lines.
- Written 2026-10-10 by the author of the script (Claude), reading it as
  someone else's code, at Rahul's request.
- Nothing has been fixed in response, as instructed.
- The script has never been executed. The only check made was a parse
  under the Python 3.8 grammar (ast.parse with feature_version (3, 8)),
  which proves only that the syntax is valid.

Line numbers refer to that commit. Items are numbered so that a fix can
cite them.

## A. Places where it can produce a wrong number rather than an error

- A1. Projection workers are fixed at 4, whatever --workers is. PROJ_WORKERS
  = 4 (line 283) is used in P5 (lines 831, 841). The walls, though, are
  measured under the load of --workers concurrent probes. A laptop run with
  --workers 2 measures walls at two-way load, and P5 then divides by 4 as if
  four workers ran at that speed. The projection is labelled a Kaggle
  4-worker projection whichever machine produced it. The number is valid
  only for a --workers 4 run.
- A2. Pairs do not share a load. The docstring says A1 and A2 pairs "run at
  the same load" (line 95). The code only queues the two members next to
  each other (line 1035). With imap_unordered, chunksize 1 and
  maxtasksperchild 1, the members start when slots free up, and they can
  share the machine with different neighbours, for example a d = 80 probe
  beside one member and a d = 10 probe beside the other. A ratio can
  therefore exceed 1.25 because of neighbour load and not because of beta,
  and scale a whole module's projection (A7, A8). The docstring claim is
  stronger than the code supports.
- A3. Load varies through the run. Probes are ordered largest first (line
  1036), so the big units run together at the start, with the most memory
  bandwidth contention, and the small units run at the tail with idle
  neighbours. Walls are therefore inflated for large units and deflated for
  small ones relative to a uniformly loaded rerun. P5 sums them as if all
  were measured under one load. The direction of the net error is not
  known.
- A4. One realization per unit. The cost of a unit comes from a single
  seed. A3, the timing-noise check, repeats the same seed, so it measures
  machine noise and not seed-to-seed variation in trajectory cost. Seeds
  whose dynamics diverge at large r, where values grow and overflow, could
  cost differently. Nothing measures this.
- A5. Subnormal arithmetic. Cost may depend on beta through underflow. At a
  large beta, exp(-beta (f - min f)) produces subnormal values for many
  particles, and subnormal arithmetic is slow on x86. Main probes run at
  tau0 = 0.1 (line 279), while the rows contain cells down to tau0 = 0.01
  and design betas up to 1000. A1 tests this for only one unit in each of
  six modules: ess_surface, mechanism, boundary, control (two arms),
  regime and law. sigma, crossed, cliff and regimemap have their r or sigma
  checks but no tau0 check. visibility has no beta check at all, since its
  beta is fixed by the B rule per law, and A2's law check is the only
  variation. Untested cells inherit the tau0 = 0.1 wall.
- A6. The r dependence is tested in few places. Main probes for sigma,
  crossed, cliff and regimemap run at r = 0.5 (line 279). EXP-ONSET's grid
  does not contain r = 0.5, and EXP-CLIFF goes to r = 5. r is tested only
  in:
  - cliff (two pairs, 0.5 against 5.0);
  - regimemap (0.75 against 3.0, d = 80, isotropic only);
  - sigma (0.1 against 0.99, inside the condition only);
  - crossed (sigma 0.1 against 0.4, anisotropic only).
  An anisotropic regimemap cell at r = 3 inherits the r = 0.5 wall,
  untested.
- A7. Only an A1/A2 failure changes the projection. A module whose pairs
  differ by up to 25% is projected at the main-probe value, with no
  adjustment. For example, if tau0 = 0.01 really costs 1.2 times tau0 =
  0.1, every tau0 = 0.01 cell is underestimated by 20% and the check still
  passes.
- A8. After scaling, the projection is no longer a lower bound. A failing
  ratio scales every cell of the module (line 830), including the cells
  whose configuration matches the faster member. The scaled number is then
  neither a lower nor an upper bound. The output still prints "lower
  bounds" (line 841).
- A9. Memory is measured for costprobe2, not for the rerun.
  - P4 measures the probe's own process. The rerun will additionally
    compute log ESS_0(J) for every nested J (RERUN_PLAN F7) and write wider
    rows, so its peak RSS can be higher.
  - The RSS baseline of each fresh worker is inherited from the parent:
    Pool forks replacement workers from the main process, and ru_maxrss in
    a forked child starts at least at the parent's resident size. That
    overstates, which is the safe direction for P4. It is still not the
    rerun's figure.
- A10. Thread environment. The thread variables use os.environ.setdefault
  (lines 194-195). If the Kaggle image already sets OMP_NUM_THREADS or
  OPENBLAS_NUM_THREADS to more than 1, the value is not overridden. Each
  worker could then start several BLAS threads, oversubscribing the four
  cores and inflating every wall. The header prints the values (line 900),
  but nothing checks them.
- A11. Wall clock. Walls use time.time() (lines 591, 598, 622), the wall
  clock, which can step if the system clock is adjusted during the run.
  time.perf_counter() is the monotonic choice. Every round-2 script so far
  uses time.time(), and the risk is small, but it is a path to a wrong wall
  without an error.
- A12. Probe beta comes from samplers I wrote, for six modules. For
  boundary, law, sigma, crossed, cliff and regimemap, the 4000-point sampler
  (lines 551-558) is my line, not the module's. It matches what I read in
  each one_realisation (X0 = rng.standard_normal((Jinf, d)) + x*), but no
  check compares it with the module source; V2 exists only in the calprec
  v2 spec. It affects only the probe beta, and therefore the timing only
  through A5.
- A13. The probe-arm counts are not from Table 2. TABLE2["PROBEARM"] =
  (144, 2160) (line 290) is not in Table 2. It comes from Rahul's
  instruction and EXP-MECH's grid. P0 compares it with my own loop, so for
  this row P0 checks my typing against my typing.
- A14. Every unit runs at the centred law. For visibility (LAWPANEL),
  mechanism (CONC, PROBEARM) and regime (HORIZON), the main probe uses the
  centred law. The other laws are tested only by the three A2 pairs, at one
  objective and one d each.
- A15. The slope is not a result. The slope column (line 628) is fitted on
  the full grid of the unit by exactcal.fit_slope. It is a diagnostic, but
  it sits in a CSV next to E_J values and could later be mistaken for one.
  It comes from one realization at a timing beta.

## B. Criteria that can pass vacuously

- B1. P0 checks only cardinalities. It compares my loop's cell count with
  Table 2's count (lines 926-937). A wrong value with the right count
  passes: d in {5, 10, 20} typed for {5, 10, 40}, or an r list with one
  wrong entry. It also cannot catch a cell mapped to the wrong unit.
  "Realizations" is just cells x M, where M is also typed by me, so the
  second comparison adds nothing beyond the first. P0 does not verify the
  grids against the archived scripts; only the citations in RERUN_PLAN do,
  and those were read by eye.
- B2. P1 hashes a path, not the imported module.
  - It hashes ARCH/<module>.py (line 915), not mod.__file__. The modules
    were imported earlier, at import time (lines 243-249), through sys.path
    with ARCH first. If any other directory earlier on sys.path held a
    same-named module, or a stale bytecode cache were used, P1 would pass
    on the deposited file while the run used something else. I know of no
    such shadowing in the repository or the bundle.
  - P1 runs after the modules have already executed their top-level code.
  - cbopaths.py, imported from the script's own directory, is not hashed.
- B3. P2 tests repeatability, not seed pass-through.
  - Two runs of the same key in one interpreter on one machine (lines
    792-797) match whether or not the seed reaches the dynamics as
    intended. If an archived function ignored its seed argument, or if
    passing a SeedSequence produced an unintended stream, both runs would
    still match.
  - Distinct keys giving distinct streams is not checked.
  - P2 exercises one module, mechanism. The other ten modules' seed
    handling is covered by my reading of their source (section C), not by
    any run.
- B4. A check whose members both fail disappears.
  - A1 and A2 work only on completed rows: the "by" dict is built from ok
    rows only (lines 780-783). An incomplete pair is reported as
    INCOMPLETE only if at least one member completed (lines 786-789).
  - If both members of a check error, the check produces no line at all,
    no FAIL, and its module keeps scale 1.
  - Likewise, if both A3 rows error, P2 stays "not run" (line 776), the
    exit code is 0, and the A3 noise yardstick is absent with no warning.
- B5. A3 is one pair. A single repeated pair is the noise yardstick for
  every A1 and A2 verdict. One quiet pair can understate the noise and make
  marginal A1 verdicts look sharp.
- B6. P4 cannot fail for most units. Every unit is small: the largest is
  d = 80 at J_inf 50000, with 330 MB measured on Kaggle in the gate's R3
  (ENVIRONMENT.md), or d = 10 at J_inf 100000. P4 is informative only for
  units whose memory has never been measured: J_inf = 100000, d = 80
  anisotropic, the visibility J19 grid. It passing elsewhere says nothing
  new.
- B7. P3 decides nothing, by design. It is reported only. Its test points,
  3 N(0, I) + 0.5, are not any row's initial law, so "same" says the
  functions agree on those points, not over each row's support.
- B8. Smoke projects nothing and finalizes only its checks. Smoke calls
  finalize with an empty row list (line 1076), so it reports P2, A3 and the
  per-module walls, and no P4 verdict per row. A smoke "success" means the
  imports and the plumbing work, not that the full run will fit in time.
- B9. The 6-hour ceiling is not checked for costprobe2 itself. Nothing
  projects costprobe2's own run time before it starts. The two-shard
  recommendation rests on judgement and on logs/costprobe.log (24 probes,
  d up to 40, 3 min 6 s on two laptop workers), not on a criterion.

## C. Archived functions and attributes: verified against the source, or assumed

Verified this session by reading the archived source in zenodo-v1. For
each: the signature, the first use of rng, and the return structure.

| Name used | Verified at | What I checked |
|---|---|---|
| ess_surface.one_realisation | ess_surface.py 140-196 | args (objective, diffusion, beta, d, sigma, dt, K, Jinf, J_list, seed); default_rng(seed); X0 standard normal, no x*; returns ({J: (E, ess_min)}, ess_min_ref); objectives ackley and rastrigin only |
| visibility.one_realisation | visibility.py 218-241 | (objective, beta, d, init, sigma, dt, K, Jinf, J_list, seed); returns ({J: E}, log_ess_min) |
| visibility.scales_of | visibility.py 186-195 | (objective, d, init, n=40000, seed=12345); returns (std, robust) |
| visibility.draw_initial | visibility.py 167-179 | all four laws handled |
| mechanism.one_realisation | mechanism.py 219-242 | (objective, beta, d, init, sigma, dt, K, Jinf, J_list, seed); returns ({J: E}, le0, le_min) |
| mechanism.beta_for_target | mechanism.py 200-216 | (objective, d, init, tau, n_probe=4000, seed=999); returns (beta, achieved) |
| mechanism.draw_initial | mechanism.py 172-179 | any law other than "centred" is treated as the 0.1 mixture, and offset and mix-0.01 do not exist. Correct for mechanism's two laws; relevant only if a caller passes another law |
| control.one_realisation | control.py 211-250 | (objective, d, init, tau, arm, beta0, sigma, dt, K, Jinf, J_list, seed); arm "adaptive" re-solves beta each step; returns a 6-tuple, [0] = {J: E} |
| control.solve_beta | control.py 181-191 | (fc, goal_log, lo=1e-12, hi=1e12, iters=90) |
| control.draw_initial | control.py 158-165 | same structure as mechanism's |
| boundary.one_realisation | boundary.py 178-204 | (objective, d, tau, beta, sigma, dt, K, Jinf, J_list, seed); X0 = standard normal + MINIMIZER; returns a 4-tuple |
| boundary.solve_beta | boundary.py 165-175 | (fc, goal_log, iters=90), bracket 1e-12 to 1e12 |
| regime.one_realisation, objective, draw_initial, SYNTH | regime.py 167-188, 215-269 | (name, d, init, beta, sigma, dt, K, Jinf, J_list, seed); no lambda argument (unit drift); returns ({J: E}, feats) |
| law.one_realisation, objective, SYNTH | law.py 191-212, 449-475 | (name, d, beta, sigma, dt, K, Jinf, J_list, seed); X0 = standard normal + xs; returns a 4-tuple |
| law.solve_beta, regimemap.solve_beta | law.py 438-446, regimemap.py 180-188 | bracket 1e-14 to 1e14 (signature lines and bracket lines read; loop bodies not read line by line) |
| sigma, crossed, cliff one_realisation | sigma.py 166-200, crossed.py 171-203, cliff.py 174-209 | (name, d, diff, beta, sigma, lam, dt, K, Jinf, J_list, seed); returns tuples with [0] = {J: E} |
| sigma_of in sigma, crossed, cliff, regimemap | sigma.py 136-142, crossed.py 167-168, cliff.py 149-150, regimemap.py 162-167 | (diff, d, r, lam=1.0) |
| regimemap.one_realisation | regimemap.py 199-241 | returns a dict with "E" an array in J_list order |
| exactcal.fit_slope, exactcal.OBJECTIVES | exactcal.py 127, 228-233 | (J, E) |
| OBJ, OBJECTIVES, XSTAR, MINIMIZER dicts | grep of each module | names and keys |

Assumed, not verified:

- C1. The solve_beta bodies of regime, sigma, crossed and cliff. I read
  their def lines (grep), not their loops. I assumed they are the same
  geometric bisection as boundary's. They affect the probe beta only.
- C2. That numpy.random.default_rng accepts a SeedSequence instance as its
  seed argument, on NumPy 2.1.3 (Kaggle) and 2.5.3 (laptop). This is
  documented NumPy behaviour since 1.17, and refscale and calprec construct
  generators this way, but they do so in their own code, not through an
  archived function. If it fails, every probe errors (an error, not a wrong
  number).
- C3. That multiprocessing on Kaggle's Python 3.13.15 uses the fork start
  method. On the laptop, get_start_method() returns fork (checked
  2026-10-10). Kaggle's has not been checked. Under spawn or forkserver,
  each worker would re-import the script and all twelve modules. That costs
  time outside the measured wall, and it changes the RSS baseline (A9).
- C4. That the bundled archive modules import without error on Python
  3.13. detcheck imported exactcal, regimemap and rmapj there. The other
  nine (ess_surface, visibility, mechanism, control, boundary, regime, law,
  sigma, crossed, cliff) have never been imported on Kaggle. A failure
  exits 2 (lines 243-249), an error and not a wrong number.
- C5. That the archived OBJ, XSTAR and MINIMIZER dicts contain every
  objective my grids pass. I read the keys by grep. A missing key raises
  KeyError inside the worker and becomes an err row (the B4 path).

## D. Errors I expect to hit (stops, not wrong numbers)

- D1. Finalize after a resumed error refuses to merge. A task whose row
  ended "err" is rerun on resume (only "ok" rows are skipped, line 1013),
  so its task id appears in both folders. Finalize treats any repeated id
  as fatal (lines 956-960) and exits 2, so finalize over the original
  folder and the resumed one cannot succeed whenever an error was
  recovered. Rule 17 says a key found in two folders stops the run, so this
  is "correct" under the rule as written. In practice it makes error
  recovery impossible without a rule for superseded err rows.
- D2. Finalize defaults to all rows. If the run used --rows with a subset,
  finalize without the same --rows prints NOT PROJECTED for every other
  row. That is noisy but correct.
- D3. Folder discovery is fragile. A Kaggle-fetched folder holds the run
  folder nested one level down. read_folder relies on sha256.txt at the
  top listing the nested path. That matches what kgrun's fetch wrote for
  refscale-smoke, but it has not been exercised with costprobe2's file
  names.

## E. Not tested at all

- E1. Every code path. The script has never run in any mode: plan, smoke,
  full, shard, resume or finalize.
- E2. Overflow and NaN behaviour at large r (cliff r = 5, anisotropic
  sigma about 3.16). If the archived dynamics produce inf or NaN E_J there,
  the probe ends "ok" with non-finite E_J and a finite wall. The wall is
  still a usable cost, but the slope column will be NaN. No criterion looks
  at E_J finiteness.
- E3. The interaction between imap_unordered, maxtasksperchild=1 and a
  worker that dies, for example from an out-of-memory kill. A killed worker
  can leave imap_unordered waiting forever, so the run hangs rather than
  failing, and on Kaggle that runs to the 12-hour cap with output lost
  (ledger K5).

## Recommended order, if you agree; not done

1. Run --plan on the laptop. It needs no dynamics, and it shows whether
   the imports, P1 and P0 work at all.
2. Decide which of A1, A2, A5, B1, B3, B4, D1 and E3 to fix before the
   smoke.
3. Then the Kaggle smoke, with --workers 4 so that A1 does not bite.

---

## 2026-10-10, second pass: fixes made, items left, and a re-review of the diff

What changed:

- scripts/costprobe2.py went from 3d42589 (md5
  c1ef6d574fa0e3f161df28c52f604672, 1089 lines) to the commit that adds this
  section (md5 8e44de92f16cff52a9ff45b5096f4268, 1586 lines).
- Diff against 3d42589: 896 lines inserted, 399 deleted.
- Fixes were made only to the items Rahul listed. Nothing was executed. The
  only check made was a parse under the Python 3.8 grammar.

### Closed by the fixes

- A1. P5 divides by W, the --workers of the run that measured the walls:
  - the in-run finalize uses --workers;
  - --finalize uses the workers value stored in the folders' params file,
    which merge_folders requires to be the same in every folder.
- A2, A3. The claim that pairs run at the same load is withdrawn. The
  docstring now says the pairs are queued adjacently and that neighbour
  load is uncontrolled. Every check line, printed and in
  costprobe2_checks.csv, carries "neighbour load uncontrolled; evidence, not
  a measurement". Load is not equalised.
- A7, A8. A row whose module was scaled by a failing check is labelled
  "SCALED, not a bound". An unscaled row is labelled "lower bound (perfect
  scaling; beta and r dependence partly untested)". The blanket "lower
  bounds" line is gone. Both labels are in the projection CSV.
- A10. The thread variables are set unconditionally (os.environ[v] = "1")
  before numpy is imported. The multiprocessing start method is now
  printed in the header as well.
- B1. P0(a) reads each factor from the archived source with ast, at the
  line ranges in SOURCE:
  - non-quick branch only;
  - Names, list(NAMED), comprehensions over SYNTH, argparse defaults and a
    dict indexed by an argparse flag are resolved;
  - exactly one value is required.
  It compares the result with the list the row loops over. row_cells now
  builds every row from GRID, the same lists P0(a) checks. Literals that sit
  inside comprehensions are printed as "not checked against source" (the
  NOT_CHECKED list).
- B2. P1 hashes os.path.realpath(module.__file__) after import, and
  requires that file to lie in the archive directory and end in .py.
- B3. P2 now has one A3 pair per module in the plan: each module's
  smallest unit, run twice with the same key. P2 passes only if every pair
  is complete and bitwise identical. The docstring states that P2 tests
  repeatability per module, not that distinct keys give distinct streams.
- B4. An expected check whose member errored, timed out or is missing is a
  FAIL, with the error text; it is never dropped.
  - The expected checks come from build_plan, not from the rows that
    happen to exist.
  - An errored A3 pair is a P2 FAIL (exit 3).
  - An errored A1 or A2 check gives exit 4 (A-ERR), labels the module's
    rows "check errored", and leaves their scale unchanged.
- D1. merge_folders accepts a repeated task id only when every earlier
  occurrence is an error row; the later row replaces it. A repeat after a
  complete row exits 2. This is stated in the docstring.
- E3. multiprocessing.Pool is replaced by one Process per task, at most W
  at once, each sending its result through a Pipe:
  - a task past TIMEOUT_S is terminated and written as an error row
    ("timeout");
  - a process that exits without a result is written as an error row
    ("worker exited with code ...").
  - TIMEOUT_S = 5 x the projected wall of the largest unit in the queue,
    printed at the head of the run with the rate, its source and the unit
    (criterion T1).

### Partly closed

- B5. There is now one A3 noise pair per module instead of one overall, and
  each module's A1/A2 verdicts are labelled noise-limited by that module's
  own pair. It is still a single pair per module.
- B8. Smoke is now the A3 pair of every module, so it exercises P2 and the
  dynamics of every module. It still projects nothing.

### Left, by decision (Rahul, 2026-10-10)

- A5, A6. The beta and r dependence of wall time stays partly untested.
  The cure would be a combinatorial sweep that costs more than the
  measurement is worth, so the projection carries the caveat instead. It
  is written into the docstring's cost-model section and into the
  lower-bound label.
- C1 to C5, the remaining signature and platform assumptions: the
  solve_beta bodies; default_rng accepting a SeedSequence; the start method
  on Kaggle; the nine modules never imported on Kaggle; the dict keys. The
  smoke run tests them for real, which is what a smoke run is for. A
  failure there is an error row, P2 FAIL or exit 2, not a silent number.

### Left, not in the list to fix (unchanged since the first review)

- A4: one seed per unit.
- A9: P4 measures costprobe2, not the rerun, and the RSS baseline is
  inherited from the parent.
- A11: walls use time.time(); the timeout itself uses time.monotonic().
- A12: my samplers for the probe beta.
- A13: PROBEARM counts are not from Table 2.
- A14: only the centred law in main probes.
- A15: the slope column. It is now described in the docstring as "a
  diagnostic of one realization at a timing beta, not a result", but it is
  still written.
- B6: P4 cannot fail for most units.
- B7: P3 points are not each row's initial law.
- B9: no projected total run time for costprobe2 itself. The plan mode now
  prints the timeout but not a total.
- D2, D3: finalize's default rows and folder discovery.
- E1: nothing has run.
- E2: non-finite E_J is not examined.

### New issues found re-reading the diff

- R1. P0(a) is vacuous for two factors.
  - The objective lists of SYNTH and GEOM: GRID takes REG_SYNTH and
    LAW_SYNTH from the modules' SYNTH, and the source reader resolves the
    archived comprehension from the same SYNTH. Both sides are the same
    object, so the comparison cannot fail.
  - The line ranges in SOURCE were typed by me. A range that points at the
    wrong line gives "NOT READ" (a FAIL, exit 2) or a wrong variable with a
    different value (a MISMATCH, exit 2). It could read a wrong variable
    only if that variable has the same name and the same value. P1 pins
    the archive bytes, so the line numbers cannot drift.
- R2. The P0 source reader is about 110 new lines that have never run.
  Most failure modes in it end in FAIL and exit 2 rather than in a silent
  pass: wrong node types, Python 3.8 ast.Index, the IfExp branch choice.
  One that would not: _in_quick_branch decides the branch by looking for
  "quick" anywhere in the dump of an If test. A test that mentions quick in
  some other way would be misread. I know of none in the cited ranges.
- R3. The timeout model is crude.
  - Without --timing-from, the rate comes from the laptop's exactcal
    probes, not from each module. A platform more than five times slower
    than the laptop on the largest unit would time it out.
  - The adaptive-arm proxy factor of 4 is a guess. If the adaptive arm
    costs more than about 20 times its non-adaptive proxy (5 x 4), its
    probes time out.
  - Either way the result is error rows, A-ERR or P2 FAIL, and NOT
    PROJECTED. That is visible, not silent, but it can waste a Kaggle job.
    The smoke's folder can be passed as --timing-from to the full run to
    base the timeout on measured walls.
- R4. finalize takes the planned checks and projected rows from its own
  --rows, not from the rows stored in the folders' params.
  - If --finalize is called with a different --rows than the run used,
    checks can be reported missing (a spurious FAIL), or a run's checks can
    go unreported.
  - merge_folders requires the folders to agree with each other on rows,
    but does not compare them with the finalize invocation.
  - Not fixed: it was found after the fix pass and is outside the list.
    The workaround is to pass the same --rows, or none, to both.
- R5. Process-per-task means each task forks the parent once, as
  maxtasksperchild=1 did. The parent's RSS, including the growing
  rows_written list, still sets the baseline of each child's ru_maxrss
  (A9).
- R6. Walls are measured inside the child and exclude process start. The
  0.2 s polling interval of the scheduler delays reuse of a free slot by up
  to 0.2 s. That affects neighbour load, not the measured walls.

### What the first execution must show before any number is used

The header must show:
- workers 4;
- start fork;
- all thread variables equal to 1;
- P1 PASS, with every module path inside the archive;
- P0 PASS, every factor "ok", and the NOT_CHECKED lines;
- the T1 rate source, the largest unit and TIMEOUT_S.

The end must show P2 PASS for every module, and no A-ERR.
