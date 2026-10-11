# CBO-GAP rerun plan: the full experiment matrix under fixed beta

Decided by Rahul on 2026-10-10. Every row of Table 2 of the submitted
manuscript (JOGO-D-26-00563, printed page 12) is rerun under a fixed beta,
and every rerun archives per-realization, per-J output. The aim is to close
referee points 3, 4, 5, 6 and 9 in one pass. This supersedes section 5 of
notes/REVISION_PLAN.md, which named two reruns.

Nothing here has been run. Every grid below is read from the archived
generating script, at the cited lines of zenodo-v1/<script>. The grids were
checked against the Table 2 design column and agree for every row. Cell and
realization counts come from Table 2. Where the script's grid gives the same
count, that is noted. No wall time is estimated (CLAUDE.md rule 6). Totals are
not computed here. The rerun script prints them in its plan mode (see the
TASK 7 design in the session reply of 2026-10-10).

## What "fixed beta" means per row

Three archived beta protocols exist, read from the scripts:

- P, probe. beta is bisected once per cell on a 4000-point probe with a
  cell-fixed seed, then reused for every realization. This is already a
  fixed-beta design. Its defect is that the realized concentration is far
  from the target (ledger "Facts about the archive"; referee point 5). The
  rerun keeps the design and replaces the 4000-point probe with a beta
  calibrated once per cell on an independent sample of size N_star from
  calprec.py.
- X, exact. beta is solved on each realization's own reference ensemble
  (exactcal.py one_realisation), so beta is random (referee point 3). The
  rerun replaces it with the calprec beta.
- D, design. beta is a stated design value, or a deterministic rule that
  does not target concentration. It is already fixed per cell. The rerun
  keeps the rule and adds per-realization archiving and injective seeds.

Where N_star cannot be declared for a cell (refscale outcome O2), that cell's
beta is a declared fixed value with tau(beta) reported together with its
uncertainty (refscale.py docstring, O2).

## The table

Notation. obj6 = ackley, rastrigin, sphere, griewank, levy, rosenbrock.
obj4 = ackley, rastrigin, sphere, rosenbrock. obj3 = ackley, rastrigin,
sphere. J10 = 10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000. J10b = 10, 20,
40, 80, 160, 320, 640, 1250, 2500, 5000. J_inf = 50000, T = 1, dt = 0.01 and
lambda = 1 unless stated. Initial law centred unless stated.

| Row | Sec. | Archived script, grid lines | Grid read from the script | Cells | Real. | beta now | Rerun | Archived now |
|---|---|---|---|---|---|---|---|---|
| EXP-BETA-ISO | 7.2 | ess_surface.py 241-246, 273-279 | ackley, rastrigin x beta {1, 3, 10, 30, 100, 300, 1000} x d {2, 5, 10}, isotropic, sigma 0.2, M 20, J10 | 42 | 840 | D (design values) | yes: same beta values, new seeds, per-realization | per (cell, J) mean (ess_surface_raw.csv) |
| EXP-BETA-ANI | 7.2 | ess_surface.py 246, 280-286 | ackley, rastrigin x beta {3, 30, 300} x d {2, 10}, anisotropic, M 20, J10 | 12 | 240 | D | yes, as above | per (cell, J) mean |
| EXP-LAWPANEL | 7.2 | visibility.py 164, 314, 321-326, 363-371 | obj6 x d {2, 3, 5, 10, 20, 40} x law {centred, offset, mix-0.1, mix-0.01} x M 20; J grid of 19 sizes 10 to 5000 (line 322); beta = B / robust spread, B = 30, spread from scales_of (n 40000, seed 12345 + 1000 d + 7 law index) | 144 | 2880 | D (B-matching rule) | FLAG F1 | per (cell, J) mean (visibility_raw.csv) |
| EXP-MECH | 7.3 | mechanism.py 200-205, 294-297, 341-349 | obj6 x d {2, 5, 10, 40} x law {centred, mix-0.1} x tau0 {0.5, 0.1, 0.01} x M 15, J10; probe 4000, seed 999 + 131 d + 7919 len(obj) | 144 | 2160 | P | yes, calprec beta. Same cells as EXP-CAL: FLAG F2 | per (cell, J) mean (mechanism_raw.csv) |
| EXP-ADAPT | 7.4 | control.py 297-305, 327-348 | obj6 x d {5, 10, 40} x tau0 {0.1, 0.01} x arm {fixed, adaptive} x M 15, J10; probe 4000, seed 999 + 131 d; the adaptive arm re-solves beta at every step | 72 | 1080 | P (fixed arm); time-varying (adaptive arm) | fixed arm yes; adaptive arm FLAG F3 | per (cell, J) mean (control_raw.csv) |
| EXP-TAU8 | 7.5 | boundary.py 252-256, 280-304 | obj6 x d {5, 10, 40} x tau0 {0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01} x M 15, J10; probe 4000, seed 999 + 131 d | 144 | 2160 | P | yes, calprec beta | per (cell, J) mean (boundary_raw.csv) |
| EXP-REFSIZE | 7.6 | regime.py 316-325, 484, 508-516 | ackley, sphere, rosenbrock x J_inf {12500, 25000, 50000, 100000}, d 10, tau0 0.1, M 12; J10b capped at J <= J_inf/10, slopes fitted on J <= 1250; probe 4000, seed 4242 + 131 d + 17 len(name) | 12 | 144 | P | yes, one calprec beta per objective, shared across J_inf; RSS at J_inf = 100000 not measured: FLAG F6 | per cell only (regime_A_reference.csv) |
| EXP-SYNTH | 7.9 | regime.py 167-172, 548-554 | 12 synthetic: kappa {1, 100} x rho {0, 5, 20} x omega {1, 3} x d {5, 10, 40} x tau0 {0.1, 0.01} x M 12, J10b | 72 | 864 | P | yes, calprec beta on regime.py's synthetic objectives: FLAG F5 | per cell only (regime_B_synth.csv) |
| EXP-NAMED | 7.5 | regime.py 575-579 | obj6 x d {5, 10, 40} x tau0 {0.1, 0.01} x M 12, J10b | 36 | 432 | P | yes, calprec beta | per cell only (regime_C_named.csv) |
| EXP-HORIZON | 7.7 | regime.py 596-602 | obj4 x law {centred, mix-0.1} x T {0.5, 1, 2}, d 10, tau0 0.1, M 12, J10b | 24 | 288 | P | yes, calprec beta (beta does not depend on T) | per cell only (regime_D_horizon.csv) |
| EXP-GEOM | 7.9 | law.py 125-126, 191-196, 521-547 (J grid 523) | 14 synthetic: kappa {1, 100} x (rho, omega) in {(0,1), (5,1), (5,3), (5,7), (20,1), (20,3), (20,7)} x d {5, 10, 40} x tau0 {0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01} x M 12, J10b; probe 4000, seed 4242 + 131 d | 336 | 4032 | P | yes, calprec beta on law.py's synthetic objectives: FLAG F5 | per cell only (law_synth.csv; not in ARC2's list) |
| EXP-SIGMA | 7.10 | sigma.py 253-258, 300-320 | 2 diffusion x obj4 x d {5, 10, 40} x r {0.1, 0.25, 0.5, 0.75, 0.9, 0.99} x tau0 {0.1, 0.01} x M 12, J10; sigma = sigma_of(diff, d, r); probe 4000, seed 4242 + 131 d + 7 len(name) | 288 | 3456 | P | yes, calprec beta (beta does not depend on sigma or the diffusion) | per (cell, J) mean (sigma_raw.csv) |
| EXP-ANISO | 7.11 | crossed.py 255-258, 282-297, 314-328 | arm A: 2 diffusion x obj4 x d {5, 10, 40} x sigma {0.1, 0.2, 0.4} x tau0 {0.1, 0.01}; arm B: the same with r {0.1, 0.5, 0.9} in place of sigma; M 12, J10 | 288 | 3456 | P | yes, calprec beta | per (cell, J) mean (crossed_raw.csv) |
| EXP-RMAP | 7.12 | regimemap.py 300-304, 336-343 | Part M: 2 diffusion x obj3 x d {10, 40} x r {0.5, 1.0, 1.5, 2.0, 3.0} x tau0 {0.5, 0.1, 0.03, 0.01} x M 12, J10; probe 4000, seed 4242 + 131 d + 7 len(name) | 240 | 2880 | P | yes, calprec beta | per-realization slope, no per-J (regimemap_M_real.csv) |
| EXP-CAL | 7.13 | exactcal.py 259-265, 293-301 | obj6 x d {2, 5, 10, 40} x law {centred, mix-0.1} x tau0 {0.5, 0.1, 0.01} x M 15, J10; beta solved per realization; seed formula not injective (N6) | 144 | 2160 | X (random) | yes, calprec beta. Same cells as EXP-MECH: FLAG F2 | per realization, per J (exactcal_real.csv) |
| EXP-FINITEJ | 7.14 | finitej.py 75-78, 150-200 | no trajectories: redraws the 2160 EXP-CAL initial ensembles from exactcal_real.csv and computes ESS_0(J)/J at every J of J10 | none | none (2160 redraws) | reads X | not a trajectory run; superseded by writing log ESS_0(J) per J per realization in the rerun itself: FLAG F7 | per (tau, d, J) summary (finitej_summary.csv; not in ARC2's list) |
| EXP-PERJ | 7.14 | perjcal.py 100, 148-176 | obj6 x d {2, 40} x tau0 {0.5, 0.01} x M 15; J in J10 with J >= 1/tau0 (10 sizes at 0.5, 6 at 0.01); beta_J solved on the first J particles of each realization; 2880 reference evolutions | 24 | 360 | X, per J (random, and one beta per J) | FLAG F4 | per (realization, J) (perjcal_real.csv) |
| EXP-RMAPJ | 7.15 | rmapj.py 85-99 | deterministic rerun of EXP-ONSET with the same seeds and the same probe beta, archiving per-J errors | none in Table 2 (180 by the script's grid) | none in Table 2 (2160 by the script) | P | not rerun separately: the EXP-ONSET rerun archives per-J errors directly: FLAG F7 | per realization, per J (rmapj_real.csv) |
| EXP-CLIFF | 7.15 | cliff.py 260-264, 304-324 | 2 diffusion x obj4 x d {10, 40} x r {0.5, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0} x tau0 0.1 x M 12, J10; probe 4000, seed 4242 + 131 d + 7 len(name) | 144 | 1728 | P | yes, calprec beta | per (cell, J) mean (cliff_raw.csv) |
| EXP-ONSET | 7.15 | regimemap.py 302-304, 336-343 | Part D: 2 diffusion x obj3 x d {5, 10, 20, 40, 80} x r {0.75, 1.0, 1.25, 1.5, 2.0, 3.0} x tau0 0.1 x M 12, J10 | 180 | 2160 | P | yes, calprec beta | per-realization slope (regimemap_D_real.csv) and per J (rmapj_real.csv) |

The script grid gives the Table 2 counts in every row where Table 2 states
them. EXP-FINITEJ and EXP-RMAPJ carry "—" in Table 2.

Grid recovery. Every row's grid is recovered from the archive. Two items
were not recovered:

- Table 2's hours column, which this plan does not use.
- The source of the Section 7.2 power-law exponents (p = 0.608, 0.519, 0.565
  at three B, "stable across reference sizes"). By their docstrings these
  come from ess_extend.py (2 obj x 6 d x 3 B x 20; EXP-BMATCH) and
  ess_panel.py (EXP-REFPANEL), both outside Table 2 (Supplementary Table S1),
  and their outputs are not archived (ARC6). I do not know which output
  produced those three values.

## Flags: decisions needed before the rerun script is written

- F1. EXP-LAWPANEL is the B-matching control that Section 7.2 withdraws as
  confounded. Its beta is already fixed per cell by a rule that does not
  target concentration. Option (a): rerun it under the B rule unchanged,
  with archiving. The estimand stays the same, and the row documents the
  artefact. Option (b): rerun it at calprec beta for a tau0 target. That is
  a different experiment (four initial laws under concentration control).
  It also needs calprec for d {3, 20} and the laws offset and mix-0.01,
  which calprec does not cover. Recommendation: (a). Point 7.2 is a
  withdrawn result kept in the supplement.
- F2. EXP-MECH and EXP-CAL have identical grids (mechanism.py 294-297,
  exactcal.py 262-265). Under a calprec beta both become the same
  experiment. Option (a): run it once, as the concentration arm. Option (b):
  run it twice with distinct seed kinds, as two independent replications.
  Recommendation: (a), with the archived probe and exact runs kept as the
  record of the two superseded protocols.
- F3. The adaptive arm of EXP-ADAPT re-solves beta at every time step on the
  reference ensemble (control.py 194-231). It cannot be a fixed-beta design.
  The manuscript already labels it diagnostic (Table 4 caption). Option (a):
  rerun it with its initial beta from calprec, labelled diagnostic, paired on
  seed with the fixed arm as now (control.py 346). Option (b): drop it from
  the main text and keep the archived arm in the supplement.
- F4. EXP-PERJ solves one beta per (realization, J). It is random by
  construction, and the curve is a family of algorithms indexed by J
  (Section 7.14; perjcal.py docstring). There is no fixed-beta version that
  answers the same question. Option (a): drop it. Referee point 4 asks for
  the fixed-beta experiment itself, and finite-J concentration under a fixed
  beta is then a property of the algorithm, reported through F7's columns.
  Option (b): calibrate a population beta_J per (cell, J) with calprec at
  size J. That needs a calprec mode that does not exist, and it is still a
  family of algorithms. Recommendation: (a).
- F5. The synthetic objectives are defined in regime.py (12 landscapes) and
  law.py (14 landscapes), not in exactcal.OBJECTIVES, which calprec
  calibrates against. calprec has to import them from those modules
  (CLAUDE.md rule 4), and a gate has to show that the function used in
  calibration and in evolution is the same object or agrees bitwise.
- F6. EXP-REFSIZE at J_inf = 100000 has no measured peak RSS (rule 6). The
  costprobe extension must measure it before this row is launched.
- F7. EXP-FINITEJ and EXP-RMAPJ exist only because the archived runs did not
  store what was needed: ESS_0(J) per nested ensemble, and per-J errors. The
  rerun writes both per realization, so neither needs a separate run. Is it
  acceptable that the rerun's Table 2 has no such rows?

## Decisions, Rahul, 2026-10-10

- F1: keep the B rule for EXP-LAWPANEL. It becomes a labelled historical
  arm in the supplement, because it is what the withdrawn result rests on.
- F2: run EXP-MECH and EXP-CAL once, as the concentration arm. This
  dissolves referee point 7 for the main comparison (ledger N17).
- F3: keep the adaptive arm of EXP-ADAPT, labelled a diagnostic and not
  fixed-beta, as the submitted paper labels it.
- F4: EXP-PERJ is not rerun. Its result stands in the supplement under its
  own estimand, with perjcal_real.csv.
- F5: calibrate the synthetic objectives with their own module, regime.py or
  law.py, never with exactcal's.
- F6: measure the peak RSS at J_inf 100000 in the extended costprobe
  (scripts/costprobe2.py) before EXP-REFSIZE runs.
- F7: agreed. ESS_0(J) per nested J and the per-J errors become output
  columns of every rerun row.
- Added row PROBEARM: a seed-paired probe-calibrated arm on the
  concentration-arm grid, 144 cells and 2160 realizations, beta from the
  archived 4000-point probe (ledger N17; calprec v2 spec D6).
- Realization counts and J grids stay as archived, row by row.
- Memory budget: 3 GB per worker. Ceiling: 6 hours projected per shard.
  Kaggle output is treated as lost at the cap, and resumption recovers only
  from fetched output.
- calprec is extended per notes/CALPREC_V2_SPEC.md. Under refscale O2, the
  declared beta is the one solved at the largest adequate reference size,
  or at the top rung if none is adequate, and the cell is labelled by beta.

## Measured cost: seventeen single-shard jobs (ledger N22, 2026-10-11)

- costprobe2 measured every rerun row on Kaggle:
  runs/costprobe2-finalize-20261011-101659/costprobe2_projection.csv.
- Every one of the seventeen rows projects to one shard at the 6-hour
  ceiling ("shards_at_6h" = 1 in every row).
  - The largest is GEOM, at wall_s 10500.1 against 21600.
  - The smallest is REFSIZE, at 194.6.
- The rerun is therefore seventeen independent single-shard Kaggle jobs,
  one per row, each with its own job name, run one at a time.
- The projections are lower bounds: perfect scaling, one realization per
  unit, at a timing beta. A1 and A2 are evidence, not measurement
  ("neighbour load uncontrolled; evidence, not a measurement"), and A5 and
  A6 remain untested by decision. The rerun's own plan mode must re-project
  each job, including its extra per-J ESS_0(J) output, before launch; the
  margin under the ceiling is smallest for GEOM.

Ledger K5, the Kaggle resumption gap, does not bind for this rerun:
- No row needs more than one session, so no job has to resume from an
  earlier session's output.
- If a job fails, it is rerun whole, as a new run folder.

K5 stays open as a limit, for these reasons:
- A job that hits the cap or is pre-empted loses its whole output (answer 7
  of 2026-10-10).
- A row whose real cost exceeds its lower bound by enough to pass the
  ceiling would have to be split into shards, and those shards could not
  resume on Kaggle either.
- calprec v2's streamed solves already run on the laptop because of K5
  (D5a).

## Calibration scope narrowed, rerun not narrowed (Rahul, 2026-10-11; ledger N27)

- calprec v2 calibrates four rows: CONC, TAU8, SIGMA and ANISO, 336
  calibration cells by the plan's count (CALPREC_V2_SPEC section 2).
- THE RERUN STILL COVERS THE FULL MATRIX: all seventeen rows of the
  costprobe2 projection, as seventeen single-shard jobs (N22).
  - CONC, TAU8, SIGMA and ANISO take calprec v2 betas.
  - PROBEARM takes the archived probe beta, by design.
  - BETA-ISO and BETA-ANI keep their design betas.
  - LAWPANEL keeps the B rule.
  - ADAPT, REFSIZE, SYNTH, NAMED, HORIZON, GEOM, RMAP, CLIFF and ONSET keep
    their archived probe betas and are reported as probe-calibrated at
    nominal tau0.
- A future session must not read this as dropping rows from the rerun.
  No row is dropped.
- The "calprec coverage" list below is superseded where it concerns rows
  other than the four. Their deviation from nominal is quantified as
  stated in CALPREC_V2_SPEC section 2: archived per-cell achieved
  concentration, calprec v1's single C2 cell, and refscale's adequacy
  evidence. A per-cell measurement of tau(probe beta) on an adequate
  reference is not designed.

## calprec coverage the rerun needs and calprec does not have

calprec.py now covers obj6 x d {2, 5, 10, 40} x law {centred, mix-0.1} x
tau0 {0.5, 0.1, 0.01}, with a --taus second invocation (calprec.py
docstring, "GRIDS"). The rows above also need:

- d 20 and 80 (EXP-ONSET), obj3, centred;
- tau0 0.03 (EXP-RMAP) and 0.3, 0.2, 0.07, 0.05, 0.02 (EXP-TAU8, EXP-GEOM);
- the 12 regime.py and 14 law.py synthetic objectives at d {5, 10, 40}
  (F5);
- d 3 and 20 and the laws offset and mix-0.01, only if F1 is (b).

The tau0 = 0.01 cells depend on refscale's outcome. Under O2 they are
redefined by a declared beta.

## What every rerun row archives per realization

At minimum, one row per (cell, realization) holds:

- the cell coordinates and the row ID;
- the full SeedSequence key, written out;
- beta (repr), its calprec provenance (run folder and row), and the nominal
  tau0;
- the realized log ESS_0 of the reference and of every nested J;
- log ESS min and mean over time;
- E_J at every J of the row's grid (%.17g);
- the slope on the row's pre-specified window;
- the realized diffusion trace (for the diffusion rows);
- the final spread;
- the wall time and peak RSS of the worker.

From this file every interval, count and contrast is recomputed at the
realization level (referee points 6 and 9) without another trajectory.

## Prerequisites, in order

1. refscale full run returns, and O1, O2 or O3 is recorded.
2. calprec is extended for the coverage above (F5 included) and its 32-bit
   seed reduction is fixed (notes/SESSION_STATE.md, section 4). Stage C1 then
   runs and N_star is declared, or O2 is applied per cell.
3. A costprobe extension measures wall time and peak RSS on Kaggle for every
   (row, objective, d, diffusion, J_inf, T) combination above (rule 6).
4. The rerun script is written, smoke-tested, and launched in shards under
   the amended rule 17.
