# calprec v2: specification of the extended calibration study

Status: specification only, approved in outline by Rahul on 2026-10-10
(answer 2 of that day). No script exists yet. Nothing here has been run.
The criteria below become binding only when they are copied into the
script's docstring before its first execution (CLAUDE.md rule 5). Rahul's
decisions are recorded in section 11.

Sources: notes/RERUN_PLAN.md (grids and flags F1 to F7, decided
2026-10-10), scripts/calprec.py (v1, at 7f5e257), scripts/refscale.py
(c6dc0cb) and ledger N16 and N17.

## 1. What it produces

One beta per calibration cell, written to a beta table that the fixed-beta
rerun script reads. A calibration cell is

    (module, objective, d, initial law, tau0)

where the module is the archived script that evolves the row (F5 and
answer 2: "calibration through each row's own module"). The table also
records, for each beta:

- tau(beta) on an adequate independent reference, with its replicate
  spread;
- every verdict below;
- the provenance of beta: calibration-sample size and seed key, or
  reference-solved size and key;
- the label of the cell, "target" or "beta" (section 6).

## 2. Coverage

Only rows whose beta targets a concentration need calprec. These are the P
and X rows of RERUN_PLAN. The D rows are excluded: EXP-BETA-ISO and
EXP-BETA-ANI use design beta values, and EXP-LAWPANEL uses the B rule (F1).
EXP-PERJ is dropped (F4).

Beta depends only on (module, objective, d, law, tau0). The other factors
of a row (realization, diffusion, r, sigma, J_inf, T, arm) do not enter it.
One beta per calibration cell therefore serves every Table 2 cell that
shares those five coordinates within the same module. No beta is shared
across modules.

| Row | Module | Calibration grid | Factors that do not enter beta |
|---|---|---|---|
| EXP-MECH/CAL concentration arm (N17) | mechanism.py | obj6 x d {2, 5, 10, 40} x law {centred, mix-0.1} x tau0 {0.5, 0.1, 0.01} | realization |
| probe arm (N17) | mechanism.py | not calibrated by calprec: beta = mechanism.beta_for_target (the archived 4000-point probe), D6, confirmed | |
| EXP-ADAPT | control.py | obj6 x d {5, 10, 40} x centred x tau0 {0.1, 0.01} | arm (both arms start at this beta; the adaptive arm re-solves it in flight, F3) |
| EXP-TAU8 | boundary.py | obj6 x d {5, 10, 40} x centred x tau0 {0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01} | |
| EXP-REFSIZE | regime.py | ackley, sphere, rosenbrock x d 10 x centred x tau0 0.1 | J_inf |
| EXP-SYNTH | regime.py | 12 regime.py synthetic x d {5, 10, 40} x centred x tau0 {0.1, 0.01} | |
| EXP-NAMED | regime.py | obj6 x d {5, 10, 40} x centred x tau0 {0.1, 0.01} | |
| EXP-HORIZON | regime.py | obj4 x d 10 x law {centred, mix-0.1} x tau0 0.1 | T |
| EXP-GEOM | law.py | 14 law.py synthetic x d {5, 10, 40} x centred x tau0 (8 targets as TAU8) | |
| EXP-SIGMA | sigma.py | obj4 x d {5, 10, 40} x centred x tau0 {0.1, 0.01} | diffusion, r |
| EXP-ANISO | crossed.py | obj4 x d {5, 10, 40} x centred x tau0 {0.1, 0.01} | arm, diffusion, sigma or r |
| EXP-RMAP | regimemap.py | obj3 x d {10, 40} x centred x tau0 {0.5, 0.1, 0.03, 0.01} | diffusion, r |
| EXP-CLIFF | cliff.py | obj4 x d {10, 40} x centred x tau0 0.1 | diffusion, r |
| EXP-ONSET | regimemap.py | obj3 x d {5, 10, 20, 40, 80} x centred x tau0 0.1 | diffusion, r |

Within a module, identical calibration cells from different rows are
calibrated once. Examples: regime.py ackley d 10 centred 0.1 in REFSIZE,
NAMED and HORIZON; regimemap.py d 10 and 40 at 0.1 in RMAP and ONSET. The
script's plan mode prints the deduplicated cell count per module. That is
the count. This document states none.

The rerun's calprec v1 targets that were missing (RERUN_PLAN, "calprec
coverage") are all inside this table: d 20 and 80; tau0 0.3, 0.2, 0.07,
0.05, 0.03, 0.02; both synthetic families.

## 3. Calibration through each row's own module

For every cell the script takes three things from the row's module:

- The objective. This is OBJECTIVES[name] (mechanism, control, boundary,
  visibility), OBJ[name] (sigma, crossed, cliff, regimemap), or the f of
  objective(name) (regime, law; this covers both synthetic families, F5).
- The initial law. Where the module defines a sampler, it is used:
  mechanism.draw_initial, control.draw_initial and regime.draw_initial
  (with regime's xstar).
  Where the module draws X0 inline in one_realisation (boundary, law,
  sigma, crossed, cliff, regimemap), the script uses the same expression,
  rng.standard_normal((n, d)) + x*, with x* from the module's own MINIMIZER
  or XSTAR dict, or 0 for regimemap and objective(name)[1] for law. This
  one line is the only code not imported, and criterion V2 checks it
  against the module source.
- The bisection. This is not module-specific: exactcal.beta_on_ensemble,
  as in v1 and refscale. The ESS fraction is invariant to adding a constant
  to f, so the modules' f - min(f) does not change the target (calprec v1
  docstring).

## 4. Procedure per calibration cell

- Phase A, calibration samples. For each level N in the calibration ladder
  L_cal (D3: 4000 to 4000000) and each
  of R = 24 draws (v1's REPS), draw N values (values only), solve beta-hat,
  and store it as repr.
- Phase B, production beta. Draw one further calibration sample, of the
  cell's own size N_cell, with its own seed kind, and solve beta_prod.
  N_cell is defined in section 5 (D2: per cell). Phase
  B therefore runs after Phase C has fixed N_cell. The order is A, C, B, C'
  as in section 8.
- Phase C, references. A reference ladder L_ref (D4: 1M to 1G), six
  independent replicates per rung. Each reference is streamed in chunks
  (the refscale composition of exactcal._logsumexp) and evaluates every
  beta-hat of the cell on the same stream.
  It climbs rung by rung and stops at the first rung judged adequate by C5m
  and D1 at beta_adq (section 5), which needs the next rung as well, or at
  the cap n_max (D1: 1G, fixed from refscale, ledger N18).
- Phase C', production check. beta_prod is evaluated on six new replicates
  at the adequate rung's size (kind 32, reps 6 to 11), so the check does
  not reuse the streams that chose the rung.

## 5. Criteria, each with its worked example (to be copied into the docstring)

- V0, plan identity. For every row, the number of calibration cells
  multiplied by the levels of the factors that do not enter beta must
  equal Table 2's cell count for that row. Otherwise the script exits 2
  before any computation. Worked example, EXP-SIGMA: obj4 x d {5, 10, 40} x
  tau0 {0.1, 0.01} gives 24 calibration cells. Times 2 diffusions times 6 r
  gives 288, Table 2's count: pass. A transcription error in the r list of
  five values would give 240: exit 2.
- V1, archive identity. The sha256 of every imported archive module equals
  its entry in zenodo-v1.sha256, embedded in the script. Otherwise exit 2.
- V2, sampler identity. For each module with an inline X0, the source of
  one_realisation (inspect.getsource) must contain the exact line the
  script reproduces, and that line must be the first use of rng. Otherwise
  exit 2. The script prints the matched line. Worked example:
  sigma.one_realisation contains "X0 = rng.standard_normal((Jinf, d)) +
  xs" before any other rng call: pass.
- E1, streaming equivalence, from refscale. On the lowest reference rung
  of every cell, one replicate is also held. The streamed and held log-ESS
  (exactcal.log_ess_of on the held array) must agree to relative 1e-12 at
  every beta, or the run stops (exit 3). Worked example as in refscale.py:
  streamed 10.596634733096073, held 10.596634733096080, relative difference
  6.6e-16, pass.
- C5m, precision of the reference ESTIMATE. This replaces refscale's C5;
  see section 11a.
  - The estimate of tau at a rung is tau_ref, the MEDIAN of the six
    independent replicate tau_hat values: the mean of the 3rd and 4th
    sorted values. No single reference is used as the estimate.
  - Requirement: the relative standard error of tau_ref is at most 0.01,
    a fifth of C1's 0.05 margin, as in refscale's derivation.
  - Under approximate normality of tau_hat across replicates, with
    replicate standard deviation sigma:
    - SE(tau_ref) = c6 sigma, where c6 is the standard deviation of the
      median of six independent standard normals;
    - E[range of six] = d6 sigma, with d6 = 2.534 (refscale used 2.53).
    So the requirement becomes
          range / tau_ref <= 0.01 x d6 / c6
    at beta_adq.
  - c6 is NOT stated here from memory. Before calprec v2's first execution
    it is computed by a no-dynamics Monte Carlo that Rahul runs (at least
    10^7 medians of six standard normals, fixed seed). The value and its
    log are written into the docstring, and the resulting threshold is
    printed at the head of every run.
  - Worked example, with an ILLUSTRATIVE c6 = 0.46 (not the value to be
    used): threshold 0.01 x 2.534 / 0.46 = 0.0551.
    - Sorted replicates 0.00970 0.00980 0.00985 0.00990 0.01000 0.01010:
      tau_ref 0.009875, range 0.00040, ratio 0.0405, at most 0.0551: pass.
    - Sorted 0.00940 0.00960 0.00975 0.00985 0.00995 0.01010: tau_ref
      0.00980, range 0.00070, ratio 0.0714: fail.
  - beta_adq is the median of the cell's R beta-hat values at the top
    level of L_cal. It is used because beta_prod does not exist until the
    adequate rung has fixed N_cell. C5m at beta_prod is evaluated
    afterwards, in Phase C', and reported.
- D1, reference drift, from refscale. |median_n - median_4n| / median_4n
  must be at most 0.025. Worked example: 0.00995 at 64M and 0.01003 at
  256M give 0.0080: pass.
- Adequate rung. The smallest rung that passes C5m and D1 at beta_adq. C4 of v1 (two halves within 0.10) is not used: C5m with six
  replicates and D1 is the stronger test of the same thing. v1's verdicts
  are not reinterpreted.
- C1, sufficiency, from v1, evaluated on the adequate rung. A level N is
  sufficient for the cell when max over r of |tau_ref(beta-hat_r)/tau0 - 1|
  is at most 0.05, where tau_ref is the median over the six replicates.
  Worked example as in v1: realized values from 0.0098 to 0.0104 at tau0 =
  0.01 give a maximum deviation of 0.04: sufficient.
- N_cell. The smallest sufficient level in L_cal for that cell (D2;
  v1's rule was one global N_star over all cells).
- C6, production check. |tau_ref(beta_prod)/tau0 - 1| must be at most
  0.05, where tau_ref is the median over the six Phase C' replicates. A failure is reported, and the cell goes to
  section 6, case (b). Worked example: tau0 = 0.1, tau_ref(beta_prod) =
  0.1042: deviation 0.042, pass.
- S1, largest-term share, from refscale. Reported per replicate and beta,
  no threshold.
- X1 and X2, exact accuracy, reported, no threshold.
  - X1, centred sphere: tau(beta) = (1+4b)^(d/2) / (1+2b)^d (refscale).
  - X2, the synthetic family with rho = 0, a diagonal quadratic sum a_i
    x_i^2 under N(0, I), from the same Gaussian moment generating function:
    tau(beta) = prod_i (1 + 4 b a_i)^(1/2) / (1 + 2 b a_i). Worked example:
    d = 2, a = (1, 1), b = 0.5 gives (3^(1/2)/2)^2 = 0.75, the X1 value, as
    it must be. This covers kappa = 1 and 100 at rho = 0 in both synthetic
    families, at every d. It is the only accuracy check beyond sphere.
- G-RSS. The measured peak RSS of every task must be at most 3072 MB
  (answer 5). Plan mode refuses any held size whose value array exceeds
  1024 MB (8 bytes x n), leaving headroom inside the budget. A measured
  excess is printed as a FAIL line for that task, and the task's rows are
  marked.

## 6. Cells that cannot be labelled by a target

- Case (a), no adequate rung up to n_max. This is answer 3. The declared
  beta is the one solved on the reference at the largest adequate rung, or
  at the top rung if none is adequate. It is recorded with tau(beta)
  (median over the six replicates) and the replicate range, and the cell is
  labelled by beta, never by a target. Solving beta on a reference needs
  the reference held. If that rung exceeds the held cap of G-RSS, see
  D5 (streamed bisection, criterion E2).
- Case (b), adequate reference, but no level of L_cal is sufficient (C1),
  or C6 fails. Accepted (D5): solve beta on one replicate of the
  adequate rung and evaluate it on the other five. If the median of those
  five passes C6's 0.05, label the cell by target with that beta;
  otherwise label it by beta, as in case (a).

## 7. Seeding

- Every stream is numpy.random.default_rng(SeedSequence(key)), with the
  key at full width and never reduced (N16).
- Key: (ENTROPY 20261010, kind, module code, objective code, d, law code,
  tau0 in millionths, n, rep). Kinds: 31 calibration draw, 32 reference, 33
  production draw, 34 case (b) reference solve.
- The ENTROPY and kinds differ from calprec v1 (20261009, kinds 1 and 2)
  and from refscale (20261009, kinds 11 and 12), so no stream can coincide
  with one there.
- References carry tau0 = 0 in the key, because one stream serves every
  beta of the cell. Their key does carry the law and the module, so
  modules never share a reference.
- Every key is written out in full in every CSV row.

## 8. Order of work, sharding, resumption

- Task units: (cell, N, rep) for Phase A; (cell, n, rep) for each
  reference; (cell) for Phase B; (cell, case b) for the case (b) solve.
  Phases A, C, B and C' are ordered within a cell. A shard owns whole
  cells. Cells go to shards by index modulo k over the sorted list of cell
  keys, so every shard gets a fixed, input-determined set.
- Shard size: plan mode prints a projected time per shard from a measured
  throughput table. That table is the output folder of a calprec v2 smoke
  run, named by --throughput and hash-checked. No shard is launched whose
  projection exceeds 6 h (answer 5). Kaggle output is treated as lost at
  the cap (answer 7).
- Resumption follows CLAUDE.md rule 17 as amended. Previous folders are
  read only after sha256.txt verifies. A key counts as completed only if
  its row has the end marker. A duplicate key stops the run. Parameters
  must match. Folders read and keys skipped are printed. A cell whose Phase
  A rows came from an earlier folder reads its beta-hat values from those
  rows (repr), so Phase C evaluates exactly those betas.
- Finalize (no draws, no dynamics): reads one or more verified run
  folders, concatenates the rows, recomputes every verdict, and writes the
  beta table into a new folder. Verdicts never come from a partial folder.

## 9. Outputs (each in a new folder, every file opened "x", rows flushed and fsynced)

- calprec2_plan.csv: every task key, its shard, the deduplication map from
  Table 2 rows to calibration cells, and V0's counts.
- calprec2_cal.csv: one row per (cell, N, rep): key, beta-hat (repr),
  fraction achieved on its own sample, wall, peak RSS, end marker.
- calprec2_ref.csv: one row per (cell, n, rep, beta): key, streamed
  log-ESS, tau_hat, S1 share, X1 or X2 exact value and relative error, E1
  values where held, wall, peak RSS, end marker.
- calprec2_prod.csv: one row per cell: production key, beta_prod (repr),
  and the case (b) key and beta where used.
- calprec2_beta.csv (finalize only): one row per calibration cell with
  module, objective, d, law, tau0, beta (repr), provenance, label, tau_ref
  median and range, the adequate rung, N_cell, and the C1, C5m, D1, C6 and
  G-RSS verdicts. The rows the fixed-beta rerun may use are those with
  label "target", or label "beta" from section 6.

## 10. Printed at the head and the end of every run

- Head: every parameter; Python, NumPy and platform; workers; the thread
  environment; the sha256 of the script, of every archive module and of
  the throughput table; the seed rule; the deduplicated cell count per
  module and per row; and the V0, V1 and V2 lines.
- During the run: one line per task, with wall, peak RSS, elapsed and
  projected time.
- End: the per-cell verdict table (in finalize), the largest RSS per
  module, and the rows flagged by G-RSS.

## 11a. Amendment after refscale: the median-of-six reference estimate

- Decided by Rahul on 2026-10-10, AFTER seeing the refscale full run
  (ledger N18). This is a forward-looking design decision for calprec v2.
- The reference estimate of tau at a rung is the median of six
  independent references, not a single reference. C5 is restated against
  that estimator as C5m (section 5).
- Refscale's own verdict stands as recorded: O2 for both tight-target
  cells, under refscale's pre-registered C5, which bounds the spread of
  single references (range/median of six at most 0.025). The median
  estimator is NOT applied retroactively to refscale. No refscale verdict
  is recomputed, relabelled or reinterpreted under C5m.
- C5m and its constant c6 are fixed in calprec v2's docstring before
  calprec v2's first execution, and they apply only to calprec v2's own
  runs.
- D1 (drift between rung medians), C1 and C6 already use the median over
  six replicates and are unchanged.

## 11. Decisions (Rahul, 2026-10-10)

- D1, the reference cap n_max = 1G (1024000000). Fixed 2026-10-10 from the
  refscale full run (ledger N18; runs/refscale-kaggle-20261010-094820).
  - 1G is the largest rung refscale measured. Its replicates took 3225.4
    to 3236.8 s for ackley and 1416.3 to 1426.5 s for sphere on one Kaggle
    worker, at a peak RSS of 269 and 193 MB.
  - A larger cap would not rescue the hardest cell. For ackley at the tight
    beta, F1 printed "extrapolated required size 2.59e+12 (extrapolation
    from a 5-point fit, not a measurement)". That is an extrapolation, not
    a measured requirement, and it lies far beyond any reachable rung.
  - Whether 1G is adequate for sphere at the tight beta is untested,
    because 1G was the top rung and its D1 needs a 4G rung.
- D2, the calibration size. One size N_cell per cell. A single global N_star
  would over-calibrate the easy cells and under-calibrate the hard ones, and
  the per-cell size is itself a reportable result.
- D3, the calibration ladder. L_cal = 4000, 16000, 64000, 256000, 1000000,
  4000000. R = 24 draws per level, as in v1.
- D4, the reference ladder. L_ref = 1M, 4M, 16M, 64M, 256M, 1G, six
  replicates per rung. From 4M upward the rungs coincide with refscale's
  ladder, so the two studies are directly comparable.
- D5, the fallback solves. Case (b) as proposed in section 6. For case (a),
  when the rung exceeds the 1024 MB held cap, beta is solved by a STREAMED
  bisection, not capped at the held size. The docstring states the
  following:
  - Each bisection step is one streamed pass over the same reference
    stream, regenerated from its seed key. The log-ESS of that pass is
    computed with the same chunked composition of exactcal._logsumexp that
    E1 verifies against exactcal.log_ess_of.
  - The bracket and the iteration count are those of
    exactcal.beta_on_ensemble: lo = 1e-10, hi = 1e10, 200 geometric
    bisections.
  - Added criterion E2, streamed-solve equivalence. On the cell's lowest
    held rung, the streamed bisection and exactcal.beta_on_ensemble on the
    held array must agree to |beta_streamed / beta_held - 1| <= 1e-9.
    Otherwise the streamed solve is not used and the cell is reported. Why
    the tolerance is not bitwise: E1 guarantees the streamed and held
    log-ESS only to relative 1e-12, so a bisection comparison that falls
    within that margin of the goal can branch differently. Worked example (illustrative values):
    held beta 6.028534528294139, streamed 6.028534528294161, ratio - 1 =
    3.6e-15: pass.
  - D5a (Rahul, 2026-10-10). The streamed solve of a case (a) cell runs on
    the laptop, not on Kaggle. On the laptop, CLAUDE.md rule 17 resumption
    works (ledger K5), there is no 12-hour cap, and the solve is one cell at
    a time rather than a matrix. It keeps the plain 200-step bisection of
    exactcal.beta_on_ensemble; betas are NOT packed into one pass. calprec
    v2 therefore marks case (a) cells in its Kaggle output as "streamed
    solve pending, laptop". A separate laptop invocation, which takes the
    list of such cells from a verified Kaggle folder, performs the solve
    with E2. Its bisection state is written after every step, so that rule
    17 resumption can continue it.
- D6, the probe arm. Confirmed: its beta is the archived
  mechanism.beta_for_target, which reproduces the archived probe protocol
  exactly. The arm must be the archived protocol, not a reimplementation of
  it.
- D7, the throughput run. A calprec v2 smoke on Kaggle produces the
  throughput table. It runs only after costprobe2's smoke and after
  refscale has finished, with one Kaggle job at a time.
