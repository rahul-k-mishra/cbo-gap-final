# CBO-GAP defect ledger

Manuscript: JOGO-D-26-00563 (33 pages + 4-page supplement), rejected with
invitation to resubmit. Archive: Zenodo DOI 10.5281/zenodo.22068685, 68 files.
Opened 2026-10-08 from the referee report (ten points), the manuscript, and a
read of the archive. Every item carries: tag, location, fix type, what must be
rerun, status. Fix types: T = text only; P = proof plus text; A = re-analysis
from archived files, no simulation; R = new simulation. Status is OPEN until a
commit closes it, then the commit hash is written here.

Rule for this file: an item is closed only by a verified artefact (rendered
PDF diff, run folder, log). Nobody closes an item by asserting it is done.

## Items settled as non-defects

- X1. "Section 1.2 says J_inf = 35 x 10^4". Text-extraction artefact: page 3
  ends "with the reference at", page 4 begins "J_inf = 5 x 10^4", pdftotext
  inserts the page number 3 between them. Source line 76, archived PDF,
  submitted PDF and every generating script agree on 50000. No action.

## Archive versus Data Availability statement

- ARC1 (new, T). Data Availability and Appendix A claim console logs are
  archived. The archive contains no log file. OPEN.
- ARC2 (new, T, and constrains R6/R9). Appendix A claims "Per-realization CSV
  files are archived for every confirmatory run in Table 2". Only
  exactcal_real.csv, perjcal_real.csv, regimemap_D_real.csv,
  regimemap_M_real.csv and rmapj_real.csv are per-realization. The eight
  *_raw.csv files (boundary, cliff, control, crossed, ess_surface, mechanism,
  sigma, visibility) are per (cell, J) means with a stderr. The four
  regime_*.csv files are per cell only. OPEN.
- ARC3 (new, T). Archived sn-article.tex and sn-article.pdf are the pre-DOI
  build; they differ from the submitted PDF by exactly the Data Availability
  sentence. OPEN (fix in the v2 deposit).
- ARC4 (new, T). regimemap_real.csv is byte-identical to regimemap_D_real.csv
  (md5 950a9c166ae246a8ae54b85dd1b07b6c); the name suggests the Part M file.
  OPEN (document or drop in v2 deposit).
- ARC5 (self, T). Data Availability and Appendix A refer to "rows marked
  dagger in Table 2"; Table 2 has no such rows (moved to Supplementary Table
  S1). OPEN.
- ARC6 (self, declared). ess_extend.py and ess_panel.py present, their CSV
  outputs absent, as declared (EXP-BMATCH, EXP-REFPANEL). No action beyond
  ARC1.
- ARC7 (new, T). The 70-file submission package was the 68 files plus
  cover-letter.tex and cover-letter.pdf; the statement does not promise a
  cover letter. No action.
- See also N30 (2026-10-15): several reported intervals have no generating
  code in the archive. It is the same kind of defect as ARC1 and ARC5, a
  Data Availability claim the deposit does not meet, and is recorded in
  full under "Newly found (2026-10-15)".

## Referee points

- R1 (ref, P + possibly R). Table 1 marks Ackley as satisfying FKR condition
  (6). Verified false: E(t e1) - E(0) = (4/sqrt d)|t| + O(t^2) against C1 t^2.
  Route: existence via GHV Theorem 2.3 (A(0,0,0), rho_0 in P_4), then A1-A2
  for Ackley with constants; see section "Ackley" below. OPEN.
- R2 (ref, P). r_aniso = sigma^2/(2 lambda) used as a boundary with no cited
  theorem. Source: Fornasier-Klock-Riedl 2022 (EvoApplications,
  DOI 10.1007/978-3-031-02462-7_46), Theorem 2, condition 2 lambda > sigma^2;
  A2 there uses l-infinity balls and nu in (0, 1/2]. Not in the reference list.
  OPEN.
- R3 (ref, R). Section 7.13: beta solved per realization on its own reference
  ensemble (exactcal.py one_realisation). Fixed-beta rerun of EXP-CAL needed:
  144 cells, 2160 realizations, 3.7 h on the Win7 machine. OPEN.
- R4 (ref, T + R). Section 7.14 confounding; reorganize and let the R3 rerun
  speak. OPEN.
- R5 (ref, R). Section 7.5 operating level rests on 4000-point probe
  calibration (ESS 40 at tau_0 = 0.01). Fixed-beta rerun of EXP-TAU8 (144
  cells, 2160 realizations, 4.3 h) and, if the 54-cell claim is kept,
  EXP-SYNTH + EXP-NAMED (108 cells, 1296 realizations, 2.6 h). OPEN.
- R6 (ref, A for 7.3, R elsewhere). Table 3 bootstraps 12 hand-picked
  objective-law units. Realization-level intervals are computable for 7.3
  from exactcal_real.csv only; every other headline count lacks
  per-realization data (ARC2). Note: exactcal_real.csv rows 1-2 (Ackley,
  d=2, centred, tau_0=0.5) have per-realization slopes -1.22556 and
  -0.657876; row 1 has E_10 = 0.0568 against E_20 = 0.0019. OPEN.
- R7 (ref, T). "moved the statistic by 0.300" as a measured effect; the two
  runs are not seed-paired (mechanism.py counter from 20260821; exactcal.py
  formula from 20260822). Reword, or pair inside the new design. OPEN.
  Disposition 2026-10-10: dissolved for the main comparison by N17 (MECH
  and CAL collapse into one fixed-beta experiment). The seed-paired probe
  arm (N17) gives a measured probe-versus-fixed difference. OPEN until the
  text is rewritten and verified by a rendered diff.
- R8 (ref, T). sn-article.tex line 348 writes E_J ~ C J^{-gamma} with
  gamma-hat ~ -1 as the fitted slope. Write E_J ~ C J^{gamma}; recheck every
  sign-bearing definition. OPEN.
- R9 (ref, T + A/R). "upper end of a bootstrap 95% interval" is the 97.5th
  percentile in code (regimemap, rmapj, perjcal, partm, reboot: [2.5, 97.5];
  visibility, regime: 97.5). State 97.5%, or recompute at 95% where
  per-realization data exist (7.12, 7.14, 7.15); Table 5 and the other
  verdict counts cannot be recomputed (ARC2). OPEN.
- R10 (ref, T, last). Shorten and reorganize. Deferred until the science is
  settled. OPEN.

## Self-identified in round 1 (already in the manuscript)

- S1. Nine analysis-design errors, supplement S3. Closed in round 1.
- S2. Six withdrawn results, supplement S4. Closed in round 1.
- S3. Lost per-realization files for two exploratory runs. Declared; see ARC1.
- S4. exactcal squared-norm bug. Fixed in the archived file; comment present.
- S5. Table 7 overwrite. Regenerated; partm.py gates completeness. See ARC4.

## Newly found (2026-10-08)

- N1 (new, P, conceptual). The parameter condition 2 lambda > d sigma^2 is a
  hypothesis of FKR's convergence-to-minimizer theorem (arXiv v6 Theorem 12,
  cited as 3.7), whose conclusion (decay of V(rho_t)) the paper never
  measures. The J^-1 exponent the paper measures is the conclusion of the
  mean-field approximation results: FKR Proposition 16 (cited as 3.11), whose
  hypotheses are those of Theorems 6 and 8 and carry no parameter condition,
  and GHV Theorem 2.6, whose dynamics carry no lambda and whose constant is
  unquantified in d and theta. "Non-admissible cells pass" is what GHV 2.6
  predicts; "admissible cells fail" is a finite-window prefactor effect the
  theorem permits. The "fourth result" and "central conceptual point" must be
  withdrawn or restated as prefactor dependence on (r, d, tau_0). Proof
  obligation: confirm against the SIAM text that Proposition 3.11's
  hypotheses contain no parameter condition. OPEN.
- N2 (new, P). Conditions (6)-(7) are the wrong admissibility gate for
  Theorem 12; it needs a weak solution in C([0,T*], P_4), which GHV Theorem
  2.3 supplies for all f in A(s,l,l) with rho_0 in P_{2 v p_M}. Levy becomes
  admissible; Ackley becomes admissible after R1's obligations; Rosenbrock
  (l != u) has no existence theorem in either paper and must be labelled
  "unproven", not admissible or non-admissible (it appears in sigma, crossed
  and cliff under an admissibility label). Table 1 must be rebuilt with
  columns: class; existence via FKR Thm 6; existence via GHV Thm 2.3; A2
  constants (nu, eta, R0, E_inf) in l2 and in l-infinity; Theorem 12
  applicable; GHV 2.6 rate applicable. OPEN.
- N3 (new, T, verify). The note under reference [3] claims FKR numbering is
  common to both versions; against arXiv v6 it is not (Theorem 12, Theorem
  14, Lemma 15, Proposition 16, Remark 25, conditions (25)-(27)). Every
  [3, x.y] must be checked against the SIAM PDF. Section 4's "leading factor
  c^-2" and "(2 lambda - d sigma^2)^-2": in v6 equation (83) the factor is
  8/(c eta^2 eps), one power of c, c otherwise only inside the logarithm.
  Also verify "[4, Subsection 2.6]" and "[4, Table 1]" against the ESAIM
  version (v3 Section 2 has 2.1-2.5). OPEN.
- N4 (new, T). Supplement numbering: main text cites S2 for the error log
  (lines 477, 690) and S3 for withdrawn results; printed numbers are S3 and
  S4. Appendix A says "three blocks"; there are four sections. OPEN.
- N5 (new, T). Section 1.2 line 78: two sentences restate 0.0219 after
  0.0260 was chosen as the yardstick, and say "Effects are compared against
  this value". OPEN.
- N6 (new, T, design). exactcal.py seed = 20260822 + 7919 m + 131 d +
  17 len(obj) + 3 len(init) + round(1000 tau) is not injective: Ackley and
  Sphere share every seed. perjcal.py imports exactcal; check. Enumerate all
  collisions with a script. Disclose; use an injective seed table in round 2.
  OPEN.
- N7 (new, T). EXP-PERJ uses J >= 1/tau_0 only (perjcal_real.csv: six sizes
  at tau_0 = 0.01), which explains 2880 = 180*10 + 180*6; the text never
  says so. OPEN.
- N8 (new, T). "every interval reported in this paper is the 4000-resample
  value" is false for Table 4, Table 5, the 7.10/7.11 counts and every
  verdict column: those are the 400-resample intervals of the generating
  scripts (N_BOOT = 400), with no per-realization data to redo them. OPEN.
- N9 (new, T). Section 7.12 says the three failing admissible cells are "of
  Section 7.15"; Conclusions say "three of the thirty in Section 7.12". They
  are EXP-ONSET r = 0.75 cells in rmapj_real.csv. OPEN.
- N10 (new, T). Two different "54 cells": Table 5 caption (3 tau_0 rows x 18
  named cells) and Section 7.5 (18 configurations x 3 dimensions at
  tau_0 = 0.1). OPEN.
- N11 (new, T). Table 2: EXP-RMAPJ's 6.8 h are inside the 74.2 h total; its
  2160 realizations are outside the 31320 total; the abstract quotes both.
  OPEN.
- N12 (new, T). Section 7.15 quotes r = 5 cells (d = 10 iso, d = 40 aniso)
  without naming the source experiment; r = 5 exists only in EXP-CLIFF. OPEN.
- N13 (new, T). Section 1.2: tau-bar/tau_0 "between 0.003 and 4.0" from
  Section 7.10; 7.10 reports neither endpoint. Trace to sigma_summary.csv or
  delete. OPEN.
- N14 (new, T). Garbled sentences: end of 7.3 ("no formal causal mediation
  model is fitted, under a control in which..."); 7.13 ("0.300, The earlier
  estimate"); 3.4 lower-case "the moment condition" and "all four" after
  "three separate points". OPEN.
- N15 (new, P). Synthetic family (10) asserted to satisfy (6) as "a quadratic
  plus a bounded Lipschitz perturbation"; the actual argument is
  |rho omega sin(omega x_i)| <= rho omega^2 |x_i|, which must be written.
  OPEN.

## Newly found (2026-10-10)

- N16 (new, repo, seeding). The docstring of scripts/calprec.py says its
  seeds are "Injective by construction: SeedSequence over a tuple of small
  integers". But seed_for returns
  int(np.random.SeedSequence(list(key)).generate_state(1, dtype=np.uint32)[0]),
  which reduces the key to one 32-bit integer. A map from the key tuples
  onto 2^32 values is not injective, so distinct keys can collide.
  Scope:
  - refscale.py is unaffected. It passes the full key to
    numpy.random.default_rng(SeedSequence(key)) and says so in its
    docstring.
  - calprec's completed runs are smoke, timing and refcheck runs only:
    runs/calprec-20261009-065642, -065734, -071626, -071815, -072623 and
    -092252 (logs/calprec-*.log). None is the production stage C1, and no
    number in the manuscript, the ledger's dispositions or a declared
    N_star rests on them.
  Fix: in the extended calprec (notes/CALPREC_V2_SPEC.md), which uses the
  full SeedSequence key. The finished runs and scripts/calprec.py at
  7f5e257 are not edited, and the finished runs are not rerun to correct
  it. OPEN until the extended calprec is committed.
- N17 (design decision, Rahul 2026-10-10, RERUN_PLAN F2). EXP-MECH
  (mechanism.py: probe beta) and EXP-CAL (exactcal.py: beta solved per
  realization) have the same grid (mechanism.py 294-297, exactcal.py
  262-265): 6 objectives x d {2, 5, 10, 40} x 2 laws x tau0 {0.5, 0.1,
  0.01} x 15 realizations. Under a beta calibrated once per cell on an
  independent sample, both become the same experiment, so it is run once,
  as the concentration arm.
  This also dissolves referee point 7 (R7) for the main comparison. The
  "probe versus exact" contrast, and the 0.300 it produced, existed only
  because two protocols were run. Neither protocol is the design of the
  new paper. Both archived runs move to the supplement as the record of two
  superseded protocols, and no causal reading of their difference is made.
  A seed-paired probe arm is added on the same grid (144 cells, 2160
  realizations; Rahul, 2026-10-10). Each realization of it runs with the
  same seed key as its fixed-beta counterpart, at the archived 4000-point
  probe beta. That turns "the protocols differ" into a measured, paired
  difference. Recorded in notes/RERUN_PLAN.md. OPEN until both arms have
  run.
- N18 (result, refscale full run). This is a verdict under the criteria
  pre-registered in scripts/refscale.py (c6dc0cb).
  Sources:
  - runs/refscale-kaggle-20261010-094820/cbo-refscale.log, written by
    kgrun's fetch (logs/kgrun-refscale-full.log: "finished after 9435 s");
  - runs/refscale-kaggle-20261010-101146/, byte-identical to 094820 (same
    sha256 for every file; origin not shown in any repository log).
  Run: Python 3.13.15, NumPy 2.1.3, workers 4, ladder 4M to 1G, six
  replicates, "E1 PASSED on every replicate and beta at rungs [4000000,
  16000000]".
  - ackley at beta = 6.028534528294139 (nominal tau0 0.01): "no adequate
    rung in the ladder".
    - C5 ratio 0.6670, 0.3669, 0.1729, 0.0867, 0.3000 at 4M, 16M, 64M,
      256M, 1G.
    - Medians 0.00963929, 0.00919193, 0.00922234, 0.00924136, 0.009123.
    - F1: "slope -0.2193; extrapolated required size 2.59e+12
      (extrapolation from a 5-point fit, not a measurement)".
    - At 1G, replicate 2 has tau_hat 0.00678988 with largest-term share
      0.235 (S1).
  - sphere at beta = 0.40654222121074113 (nominal tau0 0.01, exact tau
    0.011213257): "no adequate rung in the ladder".
    - C5 ratio 0.1318, 0.0841, 0.0476, 0.0296, 0.0117. 1G passes C5 but is
      the top rung, so its D1 is untested.
    - relerr(median) +0.0236, +0.0015, +0.0030, -0.0013, -0.0027.
    - F1: "extrapolated required size 2.54e+08 (extrapolation from a
      5-point fit, not a measurement)".
  - ackley at beta = 4.117791730834002 (tau0 0.1): smallest adequate rung
    64000000.
  - sphere at beta = 0.2461457179039086 (tau0 0.1): smallest adequate rung
    4000000.
  - Cost:
    - 1G replicate walls 3225.4 to 3236.8 s for ackley (RSS 269 MB) and
      1416.3 to 1426.5 s for sphere (RSS 193 MB);
    - "MEASURED peak RSS of any reference task 647 MB";
    - throughput 3.16e+05 (ackley) and 7.13e+05 (sphere) points per second
      per worker.
  Verdict against the outcomes fixed in advance:
  - O2 for both tight-target cells. No adequate size was reached at
    beta(0.01) for either objective. Both cells are therefore redefined by
    a declared fixed beta, labelled by beta, with tau(beta) and its
    replicate spread (notes/CALPREC_V2_SPEC.md section 6). The manuscript
    states that the tightest target is not identifiable by direct Monte
    Carlo on this problem.
  - O3 is NOT established under the pre-registered criteria. O3 requires
    sphere to be adequate where ackley is not, and at beta(0.01) sphere has
    no adequate rung either. Two things are consistent with O3: sphere's
    1G rung passes C5 (0.0117) with a median within -0.0027 of the exact
    value, and ackley's 1G rung fails C5 (0.3000). Whether sphere's 1G rung
    is adequate depends on its D1, which needs a 4G rung (proposed, not
    run). At tau0 0.1 both objectives are adequate, sphere at 4M and ackley
    at 64M.
  OPEN for O3; O2 is recorded.
- N19 (new, calibration finding, both from N18's log). A 1,000,000-point
  calibration sample at nominal tau0 = 0.01 does not give tau(beta) = 0.01,
  and the direction of the error depends on the objective.
  - Sphere: the calibrated beta = 0.40654222121074113 has exact (closed
    form, X1) tau(beta) = 0.011213257 ("exact tau(beta) 0.0112133" in
    Phase A), above the target 0.01. The 1G median, 0.0111832 (relerr
    -0.0027), agrees with the closed form.
  - Ackley: the calibrated beta = 6.028534528294139 gives a realized
    concentration whose reference medians are 0.00919193 to 0.00924136 at
    16M to 256M and 0.009123 at 1G, below the target. Every one of the six
    1G replicates is below 0.01 (max 0.00952705).
  This ackley value is not adequate (C5 fails at every rung, N18), so it is
  an estimate, not a measured tau. By the argument in refscale.py's
  docstring, a finite reference that misses the rare points near the
  minimum understates sum w^2 and so overstates tau; the true value would
  then lie further below 0.01. That is reasoning, not a measurement.
  Consequence: a fixed beta calibrated on 1,000,000 points at tau0 = 0.01
  has an error large enough to matter, and of opposite sign for sphere and
  ackley. Cells at the tight target are labelled by beta (O2), and their
  tau(beta) is reported with its uncertainty rather than assumed to equal
  the target. OPEN (to be written into the manuscript's calibration
  section).
- N20 (finding, not a defect; P3 of the costprobe2 smoke). Source:
  runs/costprobe2-smoke-kaggle-20261010-101736/cbo-costprobe2-smoke.log,
  section P3 ("126 comparisons, 22 differ"). File:
  costprobe2-20261010-044642-smoke/costprobe2_objcheck.csv.
  - Rastrigin differs from exactcal's in all eleven other modules, with
    max |diff| 1.421e-14 at d = 2 and 2.274e-13 at d = 40. Every other
    objective in the comparison matches bitwise.
  - The two expressions, read in the archived source:
    - exactcal.py, f_rastrigin (def at line 98):
          np.sum(X * X - 10.0 * np.cos(2.0 * np.pi * X) + 10.0, axis=1)
    - the other eleven modules (ess_surface 105, visibility 124,
      mechanism 134, control 122, boundary 118, regime 132, law 140,
      sigma 118, crossed 124, cliff 131, regimemap 151; def lines):
          np.sum(X * X + 10.0 * (1.0 - np.cos(2.0 * np.pi * X)), axis=1)
  - Algebraically these are the same function, x^2 + 10 (1 - cos 2 pi x).
    They group and order the floating-point operations differently:
    x^2 - 10 cos + 10 against x^2 + 10 (1 - cos). Different roundings can
    therefore give results that differ in the last bits. This is an
    arithmetic-ordering difference in one formula, not a different
    objective.
  - The cause of the observed size, beyond "different evaluation order", is
    not established. I did not trace the rounding.
  - Consequence: a beta calibrated through exactcal's rastrigin and a
    trajectory evolved through another module's rastrigin would use
    objectives that are equal only up to rounding. This is evidence for
    RERUN_PLAN F5 and CALPREC_V2_SPEC section 3 (calibrate through each
    row's own module), not a defect in either.
  No action beyond that rule. CLOSED as a record.
- N21 (repo, amendment of a pre-registered script). scripts/refscale.py was
  amended after its first full execution (N18; first executed at c6dc0cb).
  - The amendment adds one flag, --objectives, which selects a subset of
    the objectives {ackley, sphere}. It is additive:
    - no criterion, threshold, seed rule, ladder rule or default is
      changed;
    - with the flag absent, objs = OBJS in the original order, so every
      task, seed key, print and output file is as in the version first
      executed;
    - seed keys depend on the objective's code, not on the selection, so a
      sphere-only run draws the same calibration and reference streams as
      a run of both objectives.
  - Purpose: the follow-up 4G rung on sphere only (N18, "O3 open"). That
    run is a follow-up decided by Rahul on 2026-10-10 AFTER seeing refscale's
    result. C5 (range/median <= 0.025) and D1 (drift <= 0.025) are
    unchanged, and the run's verdicts are read under them.
  - Recorded in refscale.py's docstring ("AMENDMENT (2026-10-10, ...)").
  OPEN until the follow-up run is fetched.
- N22 (result, costprobe2 full run). The measured cost of every rerun row.
  Sources:
  - runs/costprobe2-s0-kaggle-20261010-103952 and
    runs/costprobe2-s1-kaggle-20261011-101343, the shards, each with a
    verified manifest;
  - runs/costprobe2-finalize-20261011-101659 (costprobe2_projection.csv,
    costprobe2_checks.csv) and logs/costprobe2-finalize-2.log.
  logs/costprobe2-finalize.log is an earlier attempt that stopped with
  "runs/costprobe2-s1-kaggle-TIMESTAMP1 has no sha256.txt" (the placeholder
  path) before creating any folder.
  - Shards. Both report Python 3.13.15, NumPy 2.1.3, workers 4, script
    sha256 ea5cb2e1...f64b (2c20653), P1 PASS and P0 PASS.
    - Shard 0: 166 main and 52 check probes, "probes finished in 603.7 s".
    - Shard 1: 165 main probes, 439.5 s.
    - Each has TIMEOUT_S 2440.0 s. The longest single probe was 46.776 s
      (regimemap, rastrigin, d = 80, anisotropic).
    - The shards ran in two Kaggle sessions, on 2026-10-10 and 2026-10-11.
      Their walls are combined on the assumption that the sessions ran on
      comparable machines. That assumption is not tested.
  - Rows. Finalize read 218 and 165 rows, 383 in all, with 0 errors read
    from the CSVs. No non-finite E_J was found.
  - P2 PASS: all eleven A3 pairs are bitwise identical. Noise ratios run
    from 1.0005 to 1.0227.
  - A1 and A2: every check PASS. The largest ratio is 1.0246
    (A2-mechanism-law); the largest A1 ratio is 1.0245
    (A1-ess_surface-beta). No module was scaled (scale 1.0000 for every
    row). In the script's own words, every ratio is "neighbour load
    uncontrolled; evidence, not a measurement". A5 and A6, the beta and r
    dependence of wall time beyond these pairs, remain untested by decision
    (notes/COSTPROBE2_REVIEW.md). Every row carries the label "lower bound
    (perfect scaling; beta and r dependence partly untested)".
  - P4 PASS for every row. Largest peak RSS by row: ONSET 354.2 MB; LAWPANEL
    220.3; ADAPT 216.6; CONC and PROBEARM 215.2; NAMED 213.9; TAU8 213.2;
    GEOM 207.0; SYNTH 206.5; ANISO 202.6; SIGMA 202.5; CLIFF 200.1; RMAP
    197.7; REFSIZE 128.7; HORIZON 88.6; BETA-ANI 87.3; BETA-ISO 85.1. At
    J_inf = 100000 (RERUN_PLAN F6) the walls were 13.209, 9.148 and
    11.228 s and the RSS 124.2, 123.2 and 128.7 MB (ackley, sphere,
    rosenbrock).
  - P5 at W = 4, per row as core h / wall h / shards at the 6-hour
    ceiling:
    - BETA-ISO 1.01 / 0.25 / 1; BETA-ANI 0.28 / 0.07 / 1;
    - LAWPANEL 6.26 / 1.56 / 1; CONC 4.44 / 1.11 / 1;
      PROBEARM 4.44 / 1.11 / 1; ADAPT 4.10 / 1.02 / 1;
    - TAU8 5.72 / 1.43 / 1; REFSIZE 0.22 / 0.05 / 1; SYNTH 2.72 / 0.68 / 1;
      NAMED 1.27 / 0.32 / 1; HORIZON 0.60 / 0.15 / 1;
    - GEOM 11.67 / 2.92 / 1; SIGMA 8.76 / 2.19 / 1; ANISO 8.74 / 2.19 / 1;
      RMAP 10.50 / 2.62 / 1; CLIFF 5.77 / 1.44 / 1; ONSET 9.40 / 2.35 / 1.
    The largest is GEOM, wall_s 10500.1, against the 21600 s ceiling.
  - Totals, computed by Claude from costprobe2_projection.csv, not printed
    by the script:
    - 17 rows, 2322 cells, 30960 realizations;
    - core_s 309229.4 (85.90 h);
    - summed per-row wall_s 77307.4 (21.47 h) at 4 workers, one row at a
      time.
    These are rerun-matrix totals: they include PROBEARM and exclude PERJ,
    FINITEJ and RMAPJ, so they are not Table 2's totals.
  What the numbers are: lower bounds from one realization per unit at a
  timing beta. They do not include the rerun's extra per-J ESS output or
  any calibration time. CLOSED as a measurement; the consequence is in
  notes/RERUN_PLAN.md.
- N23 (result, c6). The constant of calprec v2's criterion C5m. Sources:
  logs/c6.log and runs/c6-20261011-102531/ (c6_summary.csv, c6_chunks.csv;
  manifest verified).
  - Run: Python 3.12.3, NumPy 2.5.3, the laptop, workers 2, N 10000000 in
    K 40 chunks; "10000000 draws in 2.5 s"; per-worker peak RSS max
    53.5 MB.
  - Results:
    - c6_hat = 0.463495, se 0.000094 (relative 2.02e-04);
    - d6_hat = 2.534504, se 0.000274, against the spec's 2.534;
    - T_spec = 0.01 x 2.534 / c6_hat = 0.054672, se 0.000011;
    - T_mc = 0.01 x d6_hat / c6_hat = 0.054682, se 0.000013.
  - Verdicts: M1 PASS. M2 PASS ("d6_hat is consistent with 2.534").
  - Consequence: the C5m threshold is fixed at 0.054682 (T_mc, from the
    measured d6 and c6) in notes/CALPREC_V2_SPEC.md. The 2.534 the spec had
    assumed was confirmed independently by this run; it was not reused.
  CLOSED.
- N24 (decision withdrawn, Rahul 2026-10-11). CALPREC_V2_SPEC D5a,
  calprec v2's 200-step streamed bisection for case (a) cells on the
  laptop, is withdrawn.
  - Reason: D5a was decided on 2026-10-10, before refscale measured a 1G
    replicate. refscale's full run (N18) measured one ackley d = 40 1G
    replicate at 3225.4 to 3236.8 s on one Kaggle worker. 200 passes are
    then about 645,000 worker-seconds per cell (notes/CALPREC_V2_REVIEW.md
    A3). That is not viable anywhere.
  - Replacement: a streamed grid solve, run on Kaggle with the climb.
    - 64 betas per pass, on one pass over an independent stream.
    - It stops when the relative bracket width is at most 1e-6, which
      needs five passes by the rule. The instruction's "two passes, below
      1e-4" does not hold: two passes give about 1.2e-2.
    - New criterion E3: |beta_grid / beta_held - 1| <= 1e-6 against
      exactcal.beta_on_ensemble on a held 1M stream.
    - E2 is withdrawn with D5a.
  - Recorded in CALPREC_V2_SPEC sections 6, 11 and 11b. CLOSED.
  - Addendum, 2026-10-11: Rahul confirmed the correction. The stop rule
    (relative width <= 1e-6) stands, and five passes of 64 is the answer;
    his "two passes, below 1e-4" was wrong. Also his decision of
    2026-10-11: case (b) is solved by the same grid solve, which removes
    the last held solve above 1M (CALPREC_V2_SPEC 11b).
  - Addendum, 2026-10-11 (N28): the grid solve and E3 are REMOVED from
    calprec v2 by the design change of that day. The design above is kept
    here, in CALPREC_V2_SPEC 11b and in scripts/calprec2.py at 0bd7011,
    in case a later study needs it.
- N25 (result, memory probe; resolves notes/CALPREC_V2_REVIEW.md A4).
  Sources: logs/memprobe.log and runs/memprobe-20261011-110235/memprobe.csv
  (manifest verified).
  - Run: Python 3.12.3, NumPy 2.5.3, the laptop, one worker, sizes run one
    at a time. ackley d = 40, centred law, tau0 0.01, through
    exactcal.draw_initial and exactcal.beta_on_ensemble. Baseline 20.7 MB
    at every size.
  - 4M: held 294.3 MB, solve peak 294.3 MB, draw 13.4 s, solve 47.4 s.
  - 16M: held 386.0 MB, solve peak 641.7 MB, draw 52.0 s, solve 222.4 s.
  - 64M: held 752.2 MB, solve peak 2472.8 MB, draw 219.9 s, solve 710.1 s.
    "M-RSS 64M solve peak 2472.8 MB: within budget" (3072 MB).
  - The safety gate let 64M run: its linear extrapolation gave 2031 MB
    against a limit of 6264 MB (0.8 x MemAvailable 7830 MB). The measured
    peak, 2472.8 MB, is above that extrapolation. A linear gate from 4M and
    16M under-predicts the 64M peak, so it would not be a safe gate for a
    larger size.
  - Consequence: the design no longer holds anything above 1M (CALPREC_V2
    SPEC 11b: phase A at most 4M values, E1 and E3 at 1M). SUPERSEDED by
    N28: E1 now holds replicate 0 of the 64M reference, so this figure
    bounds a path the design does take, one log_ess_of on a held 64M array. This figure
    therefore bounds a path the design does not take. It is recorded so
    that a future held solve can be sized without rerunning the probe.
  - 128M: arithmetic on the probe's numbers, NOT a measurement. The solve
    peak rose by 1831.1 MB from 16M to 64M, about 38.1 MB per million
    values. Continuing that slope from 64M to 128M gives about 4900 MB,
    above the 3072 MB budget. Plain proportional scaling of the 64M peak
    gives the same order. So a held 128M solve would exceed the budget, on
    this arithmetic.
  CLOSED (A4 resolved).
- N26 (repo, a crash removed before any execution). In scripts/calprec2.py
  at 03d0174, grid_solve_round checked a pass's stored betas against
      [float(repr(x)) for x in s["grid"]]
  where s["grid"] was list(np.geomspace(...)), a list of numpy.float64.
  - Under NumPy 2, repr of a numpy scalar is the string
    "np.float64(<value>)", not the bare number. float() of that string
    raises ValueError.
  - The check ran in the job's parent process after the first grid pass,
    outside any task's try block. On Kaggle (NumPy 2.1.3), the first grid
    pass of the first E3 would therefore have crashed the whole job. The
    task rows written before it would remain, and no solve would complete.
  - Found by Claude while re-reading the diff on 2026-10-11, outside
    Rahul's list of items to fix.
  - The N2 rework REMOVED the code rather than patching it: grid_of now
    returns Python floats, and the shared grid_step compares the stored
    list with the replayed grid directly (calprec2.py at 0bd7011).
  - It never executed. Recorded in notes/CALPREC_V2_REVIEW.md (third
    pass). CLOSED by 0bd7011.
- N27 (scope decision, Rahul 2026-10-11, after the calprec2 plan:
  logs/calprec2-plan.log, 861 cells over 13 rows, "could become case (a)
  at worst: 861"). calprec v2 calibrates FOUR rows only:
  - CONC (mechanism, 144 cells);
  - TAU8 (boundary, 144);
  - SIGMA (sigma, 24);
  - ANISO (crossed, 24).
  That is 336 cells, the counts read from that plan.
  - Reasons:
    - referee points 3, 4 and 5 concern the concentration arm and the
      operating level, and the diffusion comparison is main text under the
      agreed scope (REVISION_PLAN);
    - the supplementary rows' estimand is the archived protocol, so
      recalibrating them would change what the supplement reports rather
      than correct it;
    - 861 cells all reaching case (a) is unaffordable, and no referee
      asked for it.
  - This narrows RERUN_PLAN's CALIBRATION coverage only. The rerun still
    covers the full matrix. The four rows take calprec v2 betas; every
    other row keeps its archived probe beta (or design beta or B rule) and
    is reported as probe-calibrated at nominal tau0. PROBEARM is
    unaffected. No row is dropped from the rerun.
  - The deviation of the kept probe betas cannot be quantified per cell
    from calprec v1 and refscale alone:
    - calprec v1 covers one cell (ackley d = 40, C2);
    - refscale evaluates no probe beta;
    - the archive's per-cell achieved initial concentrations (on 50000-
      point references) are the per-cell record available, with refscale's
      evidence on their precision at tight targets.
    See CALPREC_V2_SPEC section 2.
  OPEN until calprec v2 has run on the four rows.
- N28 (design change, Rahul 2026-10-11, before calprec v2's full run).
  calprec v2 drops the climb, the adequacy search and the per-cell solve
  for two fixed reference sizes.
  - Reason: a full run would be refused by G-CAP.
    logs/calprec2-plan-4rows-thr.log (script 4c7f2950...b36d96 = 0bd7011,
    --throughput runs/calprec2-smoke-kaggle-20261011-121225) prints, for the
    336 cells of N27:
    - "best case 301529 s   worst-case estimate 7672526 s   at 2 workers
      ceiling 21600 s";
    - "case (a) solves if all 336 cells became case (a): 5461019 s at 2
      workers";
    - "largest single task, estimated 5207 s".
    Plan mode itself only reports; a full run with these estimates exits 2.
    (The commit message of 34ba973 says the plan was "refused by G-CAP".
    Strictly, the plan reports the estimates and a full run would be
    refused.)
    The cause is structural: 336 cells each searching a six-rung ladder to
    1G, while refscale (N18) had already answered what that search asks,
    on the hardest cell.
  - Design (CALPREC_V2_SPEC 11c):
    - phase A unchanged, giving beta_adq;
    - phase C at 64M and 256M, six replicates each, at beta_adq, with no
      ladder and no stopping rule;
    - adequate at 64M = C5m at 64M (<= 0.054682) and D1 between the 64M
      and 256M medians (<= 0.025), as refscale judged it;
    - C1, B and C' as before, at 64M;
    - cells that fail are labelled by beta (O2, N18), with both sizes'
      medians and ranges reported. This is a finding, not a failure.
  - Removed from calprec v2, not disabled: case (a), case (b), the grid
    solve, E3, kind 34, the multi-job continuation (--inputs, --max-rung,
    the phase-A file) and the nine rows outside N27. Reason: with no climb
    there is nothing to solve at a climbed rung, and every cell fits in one
    job. The grid solve design is preserved in N24 and CALPREC_V2_SPEC 11b,
    and in scripts/calprec2.py at 0bd7011, in case a later study needs it.
  - E1 moves to replicate 0 of the 64M size, held in phase C. Its memory is
    the allocation N25 measured at 64M (2472.8 MB, within 3072 MB). That it
    carries over to calprec2's processes is an inference: the smoke's 4M
    peak for ackley d = 40, 301.8 MB, matches memprobe's 294.3 MB. Lost
    against the old 1M E1: no held check at 256M (over budget), E1 at
    beta_adq only, and E1 never run at 64M before (refscale held 4M and
    16M).
  - Decisions made by Claude in the rewrite, put to Rahul: BA (an
    adequate cell failing C1 or C6 takes beta_adq, labelled by the old CB
    rule); O2's tau_ref is the 256M median; the C1 pass stays a separate
    regeneration with R1; finalize expects every cell of the rows.
  - Correction recorded: Rahul's instruction said refscale measured
    adequacy for two cells. N18 has four (ackley and sphere, d = 40, at
    tau0 0.01 and 0.1).
  - The smoke (runs/calprec2-smoke-kaggle-20261011-121225; kgrun runner
    exit code 0; 90 units; Python 3.13.15, NumPy 2.1.3) stays a valid
    throughput table: the smoke task and the primitives it times are
    unchanged.
  Script: scripts/calprec2.py, md5 dd3aa2508be868906c34e40266d2467e, not
  executed. Review: notes/CALPREC_V2_REVIEW.md, fourth pass. OPEN until the
  new plan's G-CAP estimate is read and the full run is done.
  - Addendum, 2026-10-11, Rahul's decisions:
    - The full design runs: 64M and 256M, 336 cells, no size and no
      replicate dropped. Runtime is not a constraint; losing work is.
    - logs/calprec2-plan-fixed2-thr.log (script a3f18560...a0c2, 4
      workers):
      - "best case (no cell adequate) 368357 s   worst-case estimate
        (every cell adequate) 699034 s";
      - "largest single task, estimated 1289 s";
      - "smallest --nshards with every shard within the ceiling: 40
        (largest shard 19968 s at 4 workers, over the 336 selected cells)".
    - Answers to the five put questions:
      1. BA confirmed. Reason: a beta_prod that fails C6 has been measured
         to miss the target, so carrying it forward would label a cell by
         a beta just shown to be wrong.
      2. The 256M median for not-adequate cells is confirmed: it is the
         larger reference, and D1 could not vouch for it against
         anything bigger.
      3. The separate C1 pass and R1 are kept.
      4. finalize expecting every cell is confirmed.
      5. C5m at beta_prod is reported, with no threshold.
    - U4: E1's 1e-12 at 64M is not pre-loosened. A failure exits 3, and
      the number is examined.
    - U3: G-MEM added. A full job refuses below 2 x 2472.8 = 4945.6 MB
      MemAvailable, saying it belongs on Kaggle.
    - Shard margin: --shard-target (default 0.5 of 21600 s). The plan
      prints the count at the target (recommended) and at the full ceiling.
      G-CAP still refuses only against the full ceiling.
    - Kaggle resumption, with K5 closed above; runbook
      notes/CALPREC2_RUNBOOK.md.
    scripts/calprec2.py is now md5 c0801f490fa49d6d35e0f7c007a4cee0, not
    executed.
  - Second addendum, 2026-10-11, Rahul's decisions on the fifth review
    pass:
    - --stop-after added, default 32400 s (nine hours). The default is a
      margin choice, not a measurement.
      - Once the time elapsed since the job's first task exceeds it, no
        new task starts. Running tasks finish under the per-task timeout.
      - The job builds no later phase and exits 5, "stopped early, output
        complete as far as it goes". Exit 5 is not a failure.
      - A resume recomputes nothing complete and continues from the first
        incomplete task.
      - Added with it, G-STOP: a full job refuses when --stop-after +
        TIMEOUT_S exceeds the 43200 s cap. Rahul did not ask for this
        check.
    - G-MEM corrected to --workers x 2472.8 MB. Rahul: "My figure was
      wrong; a four-worker job holds four of those arrays, not two." The
      2 x 2472.8 = 4945.6 MB of the first addendum is superseded.
    - The cross-shard resume instruction is withdrawn (Rahul: "my
      instruction was wrong"). Resume inputs come from the same shard only,
      and notes/CALPREC2_RUNBOOK.md says so.
    - The flat shipping with an index and the runner-side rebuild and
      re-verification are accepted.
    scripts/calprec2.py is now md5 ec8dbe3afbe414395fb9ca5f0de3cd74, not
    executed.
  - Third addendum, 2026-10-11, Rahul's decision after shards 0 and 1 of
    94 exited 0 (2379728, 434d484): each Kaggle job runs near the 12-hour
    cap instead of about 1.5 hours.
    - The ceiling is a parameter, --ceiling SECONDS, default 21600. It is
      used by G-CAP, by shards_needed and by both printed shard counts,
      printed at the head of every run and stored in calprec2_params.csv,
      so a resume must match it.
    - 21600 s was a margin choice, never Kaggle's limit. Kaggle's limit
      is the 43200 s cap, and G-STOP, unchanged, keeps the final say: it
      refuses when --stop-after + TIMEOUT_S exceeds 43200 s.
    - --stop-after default 36000 s (was 32400). At the current
      largest-task estimate of 1289 s (logs/calprec2-plan-fixed2-thr.log)
      TIMEOUT_S is 6445 s and 36000 + 6445 = 42445 s, leaving 755 s for
      Kaggle's start-up and shutdown, which G-STOP does not count and
      nobody has measured. A larger largest-task estimate makes G-STOP
      refuse the default; the fix is a smaller --stop-after, never a
      larger cap.
    - A job sized near ten hours (--ceiling 36000 --shard-target 1.0)
      relies on --stop-after and a resume for safety, not on margin. A job
      that dies without producing rows now loses up to ten hours rather
      than about ninety minutes. Rahul accepted that trade.
    - The plan prints the shard count at --shard-target x --ceiling, the
      ceiling that produced it, and a G-STOP preview: the largest task
      estimate, TIMEOUT_S and the G-STOP sum against 43200 s.
    - Consequence for the two completed shards, decided by Rahul: the edit
      changes calprec2.py's sha256 (7a44dc5c...6207 in both shard folders),
      and finalize requires one script hash across folders; a new --nshards
      also moves their eight cells to other shards. The long-job sequence
      therefore covers all 336 cells from shard 0 of the new count.
      runs/calprec2-s0of94-a1-kaggle-20261011-193148 and
      runs/calprec2-s1of94-a1-kaggle-20261011-212722 stay committed as
      records and are never passed to finalize. Seeds are keyed by cell,
      so their eight cells, recomputed on the same image, should reproduce
      the same tau_hat values; a comparison is possible and not yet
      written.
    scripts/calprec2.py is now md5 9ee2436b14c152df9d63c690eae3be36, not
    executed.
- N29 (repo, defect found before execution; calprec2 with kgrun). Every
  calprec2 full job on Kaggle would have exited 2 before any draw.
  - calprec2's full mode requires --throughput, a verified smoke folder.
    load_throughput reads it with costprobe2.verify_folder.
  - That folder, runs/calprec2-smoke-kaggle-20261011-121225, existed only
    on the laptop. kgrun bundled only the archive's .py files, two
    archive CSVs and scripts/*.py, so no run folder ever reached Kaggle.
  - On Kaggle, "--throughput runs/calprec2-smoke-kaggle-..." would have
    named a path that does not exist. verify_folder would have written
    "<folder> has no sha256.txt" and exited 2, before phase A.
  - The cost would have been one wasted Kaggle launch per shard, with no
    rows lost: the stop comes before any output.
  - Why it was not seen earlier: the smoke takes no --throughput, and the
    plan runs on the laptop, where the folder exists. No full job had been
    launched.
  - Found by Claude on 2026-10-11 while writing kgrun's resumption (review
    fifth pass). Fixed by kgrun --data-dirs: the folder is verified,
    shipped and rebuilt on Kaggle, and "runs/<name>" in --args is replaced
    by the rebuilt path. The runbook passes the smoke folder through
    --data-dirs on every attempt.
  CLOSED by f83eefb (kgrun md5 d8a053691f3a5774d2975f5cde07ee44). Not yet
  exercised on Kaggle.

## Newly found (2026-10-15)

Found by Claude while reading the archive for
notes/ANALYSIS_CRITERIA_DRAFT.md (ef57dc4), section 0. Entered on Rahul's
instruction of 2026-10-15.

- N30 (archive, T; same kind as ARC1 and ARC5). Reported intervals with no
  generating code in the archive.
  - The claims in the submitted manuscript:
    - Supplementary information (tex 719): "Each pre-specified criterion
      is stated in the docstring of the script that applies it and is
      present in the archived copy of that script".
    - Data availability (tex 728): "scripts and result files are deposited
      ... with one exception", the dagger rows.
    - Section 6, "Uncertainty" (tex 309): "every interval reported in this
      paper is the 4,000-resample value emitted by the single archived
      re-analysis script, so that no reported interval originates from a
      computation that is not in the archive".
  - What the archive holds. The only archived 4000-resample re-analysis
    script covering more than one claim is reboot.py. It reads only
    regimemap_D_real.csv and regimemap_M_real.csv (docstring; main, lines
    285-305). It covers:
    - the 7.15 paired gaps;
    - the severity trends;
    - the onset intervals;
    - the 7.12 b3 intervals.
  - Reported numbers for which no file in zenodo-v1 contains the computing
    code. Every .py file in zenodo-v1 was searched:
    - Table 3 upper block (tex 363-370): the d = 2 to d = 40 changes on
      J >= 1/tau_0 with their intervals, bootstrapped over twelve
      objective-law units.
    - Section 7.3 regression on J >= 1/tau_0 and on the full grid (tex 392):
      b_dtau +0.0073 [-0.0091,+0.0227], b_tau, b_d, and the full-grid
      b_dtau +0.0305 [+0.0123,+0.0479]. The abstract (tex 34) and the
      Conclusions (tex 703) quote these.
    - Section 7.3 pairwise target contrasts (tex 394) and the full-grid
      separation +0.1940 [+0.0682,+0.3105].
    - Table 3 middle block, full grid, with the twelve-unit intervals.
      exactcal.py P-E2 fits the full grid, but it bootstraps pooled
      realizations of an absolute value (lines 352-372), not twelve units.
      tex 563 attributes 0.253 [0.117,0.381] to the Table 3 unit.
    - The bootstrap slope-SE reference scale 0.0260, IQR [0.0191,0.0341],
      over 420 cells (tex 78). The constant 0.026 appears in the archive
      only as an input (rmapj.py lines 51, 254). The 0.0219 delta-method
      floor is computed by audit.py A1, so it is not in this list.
  - Code evidence. J >= 1/tau_0 appears in archived code only in
    perjcal.py line 168, a different experiment. rmapj.py refits on
    J >= 20 (line 193). exactcal.py fits every slope on the full grid
    (lines 266, 315).
  - Consequences:
    - Those numbers cannot be reproduced from the deposit. tex 309's
      assurance is false for them.
    - The rmapj P-R3 rule and the stated basis of the 0.05 equivalence
      margin (tex 309) rest on 0.0260.
  - Not known: what code produced them.
  - Search of the laptop, 2026-10-15, by file and directory names only. No
    file was opened.
    - Searched: /home/rahul (Research, Downloads, Desktop, Documents, the
      home directory), /media, /mnt and /tmp, for the archived script
      names, sn-article*, *cbo*, *zenodo*, *JOGO*, and every zip, tar, 7z,
      rar, *backup* and *.bak file.
    - Found: no round-1 working directory.
    - /home/rahul/cbo-archive-test holds 68 files with the same names as
      zenodo-v1. It is the separate read-only copy used by the determinism
      gate (ENVIRONMENT.md; logs/detcheck-v2-full-separate.log), so it
      holds no code beyond the deposit.
    - /home/rahul/Downloads/cbo-gap-final.zip (2033498 bytes, 2026-10-08)
      is unopened; its contents are not known.
    - Every other archive found belongs to other projects (ERL, PLEF,
      por_project). /media/rahul is empty and no external drive is
      mounted.
    The archive was produced on a Windows 7 machine (CLAUDE.md rule 7), so
    the round-1 working directory, if it survives, is most likely there.
    That is an inference, not a finding.
  OPEN.
- N31 (manuscript, T; same class as R7). The isotropic and anisotropic arms
  are not paired, although the text says they are.
  - The claims:
    - tex 650: "Paired on the shared realization index, the
      anisotropic-minus-isotropic gap ...";
    - tex 309: "Where two arms share seeds the resample is paired on the
      realization index";
    - the docstrings of regimemap.py ("PAIRED on the shared realization
      index"), reboot.py ("Two-arm comparisons resample PAIRED on the
      shared realization index") and audit.py ("which shared seeds", of
      the crossed.py arms).
  - The code. In each of these scripts the diffusion loop sits outside the
    seed counter, so realization k of the isotropic arm and realization k
    of the anisotropic arm receive different seeds:
    - regimemap.py: diffusion loop line 367, "s += 1" line 375;
    - crossed.py: 327 and 334;
    - sigma.py: 311 and 318;
    - cliff.py: 315 and 322.
    rmapj.py rebuilds Part D's task list in the same order, so its seeds
    follow the same pattern.
  - Specimen, from the archived seed column of rmapj_real.csv: ackley,
    d = 5, r = 0.75, tau 0.1:
        isotropic    rep 0 seed 20260830   rep 1 seed 20260831
        anisotropic  rep 0 seed 20261910   rep 1 seed 20261911
  - Consequence. Every paired diffusion comparison in the paper compares
    independent runs under a pairing claim. That covers:
    - the 7.15 paired gaps and their equivalence verdicts (regimemap.py
      paired_ci; reboot.py paired_gaps);
    - the 7.11 "3 of 18" equivalence, which the text itself calls unpaired
      (tex 497) but whose basis audit.py describes as shared seeds.
  - Same class as referee point 7 (R7). There, two runs without shared
    seeds were described as a measured effect of a protocol change; here,
    arms without shared seeds are described as paired.
  - What it does not invalidate. Differencing independent realizations by
    position and bootstrapping the differences estimates the variance of a
    difference of two independent means with equal counts. So the
    intervals themselves are not invalidated by this. This is reasoning
    and has not been checked numerically. What is false is the pairing
    claim, and with it any implied common-random-number variance
    reduction.
  - The same holds for pairings across r, tau_0 and d within one
    diffusion. The seed counter also runs across those loops. Specimen,
    rmapj_real.csv, isotropic ackley, rep 0:
        d = 5:  r = 0.75 seed 20260830, r = 1.0 seed 20260842;
        d = 10: r = 0.75 seed 20260902, r = 1.0 seed 20260914.
    So these are index pairings of independent runs too:
    - tex 545, "a bootstrap paired on the 36 objective-realization indices
      and resampled jointly across the panel" (b3, Part M);
    - tex 648, "a bootstrap over the 36 objective-realization pairs shared
      across all five dimensions" (severity trend);
    - the reboot.py severity and onset bootstraps;
    - the rmapj.py trend bootstrap.
    The same reasoning applies: the intervals stand, but the word "paired"
    and any implied variance reduction do not.
  - 2026-10-15: "the intervals themselves are not invalidated" is to be
    tested by scripts/m7_pairing.py on the Part D diffusion gaps (decision
    rule in its docstring). Until its log exists, the sentence is reasoning,
    not a finding. M7 does not test the r and d pairings. This part goes beyond
    Rahul's instruction of 2026-10-15 and was added by Claude on reading
    the seeds.
  - control.py does share seeds between its fixed and adaptive arms (line
    345 and the comment after it). Its pairing (Section 7.4, Table 4) is
    not affected.
  - Open decision for the rerun: whether the seed key omits the diffusion
    coordinate, so that the two arms share X0 and the Brownian increments.
    No such decision has been made (ANALYSIS_CRITERIA_DRAFT items 3 and
    5).
  OPEN.
- N32 (archive, criteria; record and rule). Three archived criteria repeat
  analysis-design errors catalogued in supplement S3 (ledger S1):
  - boundary.py line 373, monotonicity in tau_0 as "np.all(diffs >= -0.02)":
    a monotonicity tolerance fixed by hand below the measured spread. The
    error is named in law.py's docstring ("the previous phase set a
    monotonicity tolerance of 0.02 against a measured floor of 0.055 and
    the test could not have passed").
  - control.py criterion (iii), "mean slope within 0.15 of -1" (docstring;
    line 313): a two-sided criterion for a one-sided bound.
  - exactcal.py P-E2 (lines 365-369) and perjcal.py P-C2 (lines 235-239)
    bootstrap the absolute value of the d = 2 to d = 40 change. A
    percentile interval of an absolute value cannot extend below zero and
    is biased away from it when the true change is near zero.
  Rule: none of the three is inherited by the rerun. The rerun analysis
  docstring states its replacement for each, or states that the comparison
  is not made. The archived results computed under them stay in the
  supplement, labelled with this entry. OPEN until the rerun analysis
  docstring is committed.
- N33 (archive and manuscript, T; design rule). Two per-cell slope
  estimands, reported without distinction.
  - Slope of the averaged curve: E_J averaged over realizations at each J,
    one slope fitted, the bootstrap refitting per resample. Used by
    mechanism, control, boundary, sigma, crossed, cliff, regime, law and
    visibility (each boot_ci; for example sigma.py lines 218-230).
    Reported in Tables 4 and 5 and in the 7.5, 7.10 and 7.11 counts.
  - Mean of per-realization slopes: a slope fitted within each realization
    and averaged, the bootstrap resampling slopes. Used by regimemap.py
    (boot_ci lines 250-257; one_realisation lines 237-238), and so by
    partm, reboot and rmapj, and by exactcal P-E2 and perjcal P-C2.
    Reported in Tables 7 and 9 and in the 7.12 and 7.15 counts.
  - The two are different estimands: the log of a mean is not the mean of
    the logs. The manuscript never says which a given number is.
  Rule: the rerun chooses one per-cell slope, or declares one primary and
  the other secondary, and states the choice in the rerun analysis
  docstring with a worked example before the first rerun number exists
  (ANALYSIS_CRITERIA_DRAFT, "A choice that comes before items 1 to 6").
  The rerun files store E_J per realization, so either can be computed.
  OPEN until that docstring is committed.

## Checked and found sound

Theorem 4 (seven steps) and Corollary 5; Lemma 6; Proposition 1 (Levy);
Proposition 2 (Rosenbrock, both cases, d >= 2); Proposition 3 (Schwefel);
Table 2 sums (2346 cells, 31320 realizations, 74.2 h).

## Ackley: the route and the proof obligations

The referee is right about Table 1. A covering well-posedness result exists:
GHV Theorem 2.3 (arXiv v3, 25 Nov 2024): f in A(s,l,l), rho_0 in P_p with
p >= 2 v p_M(s,l), p_M = s+2 if l = 0, gives a strong solution of the
mean-field SDE, t -> rho_t in C([0,T], P_p), weak Fokker-Planck (2.5), for any
globally Lipschitz diffusion operator S (so both sigma|u| I and sigma diag(u)).
With p = 4 and Gaussian rho_0 this is the standing hypothesis of FKR Theorem
12 and of FKR-aniso Theorem 2. Obligations, all proofs, no compute:

- O1. Ackley in A(0,0,0): L_f = (4 + 2 pi e)/sqrt d; 0 <= f <= 20 + e;
  unique minimizer at 0.
- O2. FKR A1-A2 with constants: on ||v|| <= R0, U = 0.2 R0/sqrt d,
  E(v) >= eta1 ||v|| with eta1 = 4(1 - e^-U)/(U sqrt d) (nu = 1); far-field
  E(v) > 20(1 - e^-U) =: E_inf for ||v|| > R0. Anisotropic (nu <= 1/2,
  l-infinity balls): ||v||_inf <= (R0/eta1)^{1/2} E^{1/2}.
- O3. Equation matching: GHV (1.1)/(2.5) with unit drift and S equals FKR
  (8)/(9) with lambda = 1 and sigma = sqrt(2 theta); every experiment uses
  lambda = 1; state the restriction.
- O4. Weak-solution sense: GHV (4.9) test class = FKR Definition 5; initial
  condition from continuity in P_p; test-function extension via FKR Remark 7
  using P_4 regularity.
- O5. Theorem 12 is stated for any weak solution; uniqueness not needed; say so.
- O6. Verify Theorem 2.3's numbering and wording in ESAIM COCV 31, Paper 74.
- O7. Rebuild Table 1 (see N2) with proofs: Sphere (C1 = 1, C2 = 1, C3 = 1,
  nu = 1/2, eta = 1); Rastrigin (|sin 2 pi x_i| <= 2 pi |x_i| gives
  C1 = 2 + 40 pi^2; C2 = 20 d; f >= ||x||^2 gives C3 = 1, nu = 1/2, eta = 1);
  Griewank (|sin(x_i/sqrt i)| <= |x_i|/sqrt i gives C1 = 1 + 1/2000;
  C2 = 2; f >= ||x||^2/4000 gives C3 = 1/4000, nu = 1/2, eta = 4000^{-1/2});
  Levy (fails (6); GHV 2.3 with p_M = 1; A2 global from
  f >= ||x - 1||^2/16, nu = 1/2, eta = 1/4); synthetic family (N15);
  Rosenbrock (A2 holds, existence unproven, label accordingly).
- O8. State that FKR Proposition 16 requires Theorem 6's hypotheses, so for
  Ackley and Levy the J^-1 rate is sourced from GHV Theorem 2.6 (q >= 6 for
  the exponent 1/2 at p = 2; Gaussian rho_0 qualifies), and that neither
  rate theorem has a parameter condition (N1).

Cost of a demonstration on objectives that satisfy (6), (7), (27) outright:
Sphere and Rastrigin are in EXP-ONSET at r = 0.75 (rmapj_real.csv, per
realization), reported as never failing; re-reading them under the 95th
percentile criterion is analysis only. Adding Griewank: 2 x 4 x 5 x 6 = 240
cells x 12 = 2880 realizations, about 8.5 h at the Win7 EXP-ONSET throughput,
more under the fixed-beta protocol.

## Facts about the archive that shape the fixed-beta redesign

- Probe-calibrated runs are already fixed-beta designs: beta is bisected once
  per cell on a 4000-point probe with a cell-fixed seed (mechanism.py seed 999;
  cliff.py 4242 + 131 d + 7 len(name)) and reused for every realization.
- At tau_0 = 0.01 the probe's effective sample size is 40, which is why the
  achieved/target ratio spans a factor of forty.
- The "exact calibration" rerun replaced fixed beta with random beta; the
  remedy is a large calibration sample with measured precision, not a new idea.
- Round-2 scripts must archive per-realization per-J errors and use an
  injective seed table. A no-dynamics calibration study with a pre-specified
  precision criterion and a measured memory footprint precedes any trajectory
  run.

## Determinism gate (pre-registered 2026-10-08 in the docstring of scripts/detcheck.py)

The operative criteria are the ones in the docstring of scripts/detcheck.py,
section "PRE-REGISTERED CRITERIA (fixed 2026-10-08, before first execution)".
That docstring is where the gate is pre-registered, and this section only
summarizes it. An earlier draft criterion carried here until 2026-10-09 is
recorded as G3 below.

What it runs. detcheck.py imports exactcal.py, regimemap.py and rmapj.py from
the archive (zenodo-v1 by default, or the path given by --archive), prints
the sha256 of five archive files (exactcal.py, regimemap.py, rmapj.py,
exactcal_real.csv, rmapj_real.csv), and reruns three archived realizations
with their archived seeds through the archived functions:
  R1  exactcal_real.csv, first data row: ackley, d = 2, centred,
      tau_0 = 0.5, seed 20261707;
  R2  exactcal_real.csv, first row with d = 40;
  R3  rmapj_real.csv, first row with diffusion = isotropic and d = 80.

Tolerance rule, per quantity: |computed - archived| <= half a unit in the
last digit the archive stored for that quantity. Examples from the docstring:
"0.056786325" gives 5e-10; "5.398521e-05" gives 5e-12; "-1.22556" gives 5e-6;
"0.5397402043" gives 5e-11.
  D1  CALIBRATION. The solved beta, the achieved initial ESS fraction and the
      stored log-ESS values meet the tolerance rule.
  D2  TRAJECTORY. Every per-J coupled error E_J (stored %.8g) and the fitted
      slope (%.6g in exactcal_real.csv, %.6f in rmapj_real.csv) meet the
      tolerance rule.
  D3  WORKER INDEPENDENCE. A single-worker repeat gives bitwise identical
      results for every quantity.
  PASS = D1 and D2 for every quantity of R1, R2 and R3, and D3. The first
  three coordinates of X0 are printed and stored for future cross-platform
  diagnosis; the archive did not store X0, so X0 is compared with nothing.

Until PASS is recorded in ENVIRONMENT.md for a platform, no number from that
platform is compared with an archived number.

Status (2026-10-09). Linux box: PASS, tasks R1,R2,R3, with the repository
archive (logs/detcheck-v2-full-repo.log) and with the archive in a separate
read-only directory (logs/detcheck-v2-full-separate.log); recorded in
ENVIRONMENT.md. Kaggle: PASS, tasks R1,R2,R3, workers 4, NumPy 2.1.3
(runs/detcheck-kaggle-20261009-094955/cbo-detcheck.log); recorded in
ENVIRONMENT.md (G2 closed).

## Repository defects

- G1 (repo, history). Commit 7f5e257 ("Kaggle pipeline: kgrun driver,
  detcheck archive/outdir flags, ...") has a message naming the detcheck
  --archive and --outdir flags, but scripts/detcheck.py in that commit's tree
  contains neither (zero occurrences of --archive). The flags landed in the
  following commit, e945d17, which contains scripts/detcheck.py alone. History
  is not rewritten: 7f5e257 is pushed and stays as it is, and this entry is
  the record. CLOSED by e945d17.
- G2 (repo, gate). The determinism gate is per platform (CLAUDE.md rules 7
  and 16). On the Linux box it passes with detcheck v2, tasks R1,R2,R3, both
  with the repository archive (logs/detcheck-v2-full-repo.log) and with the
  archive in a separate read-only directory outside the repository
  (logs/detcheck-v2-full-separate.log). The Kaggle gate has not been run, so
  no number from a Kaggle run may be compared with an archived number until
  detcheck passes D1-D3 on Kaggle and the verdict is recorded in
  ENVIRONMENT.md with its log path. OPEN until that Kaggle log exists.
  CLOSED 2026-10-09: detcheck passed D1-D3 on Kaggle, tasks R1,R2,R3,
  workers 4 (runs/detcheck-kaggle-20261009-094955/cbo-detcheck.log:
  "VERDICT   D1+D2: PASS   D3: PASS   OVERALL: PASS"); recorded in the
  Kaggle section of ENVIRONMENT.md.
- G3 (repo, gate criteria). Until 2026-10-09 the section "Determinism gate"
  above carried, as if pre-registered, a draft criterion: D1 X0 and beta to
  full double precision, D2 E_J to relative 5e-8 and the slope to 5e-7
  absolute. History, as stated by Rahul: the draft was written on 2026-10-07
  in chat, before detcheck.py existed, as a description of the intended
  check. Its 5e-8 and 5e-7 came from the manuscript's statement that the
  rmapj rerun reproduced 2160 archived slopes to within 5.0e-7, the rounding
  of that stored file. When detcheck.py was written on 2026-10-08, the draft
  was replaced by the per-quantity rule (half a unit in the last stored
  digit). That rule was in the docstring before the script's first
  execution, so the draft was superseded before any run. The ledger was never
  updated. The draft is unachievable as written: the archive stores no X0 and
  stores beta to 10 decimals. For R1's slope the archive stores six
  significant figures (-1.22556), so the smallest discrepancy the archive can
  resolve is 5e-6 (the tolerance printed for R1's slope in
  logs/detcheck-v2-full-repo.log), not 5e-7. The section now states the
  script's rule as the operative criterion. CLOSED by acf1786.
- K1 (Kaggle, launch). The first Kaggle launch failed before detcheck ran.
  Log: runs/detcheck-kaggle-20261009-092908/cbo-detcheck.log. The runner
  printed its header (python 3.13.15) and then raised FileNotFoundError on
  /kaggle/input/cbo-gap-archive at its os.listdir line, 0.92 s into the run.
  Stated by Rahul, from the kgrun console, which is not in the repository:
  kgrun pushed the kernel immediately after "Your private Dataset is being
  created", the kernel errored 66 s later, and kaggle datasets status
  ericsom/cbo-gap-archive later reported ready, with kaggle datasets files
  listing the uploaded files. Cause: the kernel was pushed before the
  dataset finished processing, so there was nothing to mount. Fix:
  kgrun.py now waits after dataset-create or dataset-version until
  "kaggle datasets status" reports ready (--ready-poll 30 s,
  --ready-timeout 1800 s; on timeout it does not push). The generated
  runner now lists /kaggle/input and exits 2 if the archive path is
  missing. Kaggle's Python is 3.13.15; its NumPy version is unknown,
  because no script has executed there. CLOSED by the commit that adds this
  entry; the Kaggle gate itself stays open under G2.
  CORRECTED 2026-10-09 (see K3); the text above is kept as first written.
  Its Cause and Fix are wrong. The diagnosis of a processing delay was
  mistaken. In the second launch (runs/detcheck-kaggle-20261009-094052), kgrun
  waited until "kaggle datasets status" reported ready, which it did after
  3 s (logs/kgrun-detcheck-relaunch-1.log), and the kernel failed the same
  way. Its listing shows the dataset mounted and complete at a different path.
  The dataset-ready wait did not address the cause; it is retained only as a
  guard against pushing a kernel against a version that is genuinely still
  being processed. The real cause was the mount path (K3). The first
  launch's log has no listing of /kaggle/input, so it does not show the
  nested path by itself. The first failure is attributed to the mount path
  because both runs looked for the same missing path, and Rahul reports the
  dataset ready with its files listed afterwards. The CLOSED above is
  withdrawn: K1 is closed by K3's fix.
- K3 (Kaggle, mount path). Both failed launches looked for the archive at
  /kaggle/input/cbo-gap-archive, the path the runner hard-coded. Kaggle
  mounted the dataset at /kaggle/input/datasets/ericsom/cbo-gap-archive.
  Evidence: runs/detcheck-kaggle-20261009-094052/cbo-detcheck.log, the
  runner's listing of /kaggle/input at t = 1.176 s:
      /kaggle/input/datasets/ericsom/cbo-gap-archive/   31 file(s): audit.py, boundary.py, calprec.py, cbopaths.py, cliff.py, control.py, costprobe.py, crossed.py, detcheck.py, ess_extend.py ...
  31 is the bundle kgrun uploaded: "26 archive files + 5 round-2 scripts"
  in logs/kgrun-detcheck-relaunch-1.log. So the dataset was mounted and
  complete, at a path the runner did not look at. Fix, in the commit that
  adds this entry: the generated runner no longer hard-codes the path. kgrun
  passes in the user and the dataset slug, and the runner tries
  /kaggle/input/<dataset>, then /kaggle/input/datasets/<user>/<dataset>, then
  a sorted walk of /kaggle/input to depth 3 for the first directory named
  exactly <dataset>. It prints which candidate matched and passes that path
  as --archive. If none matches, it lists /kaggle/input and exits 2. CLOSED
  by the commit that adds this entry, pending a Kaggle launch that finds the
  archive.
  CLOSED 2026-10-09 by 4c9824c, confirmed: the third launch
  (runs/detcheck-kaggle-20261009-094955/cbo-detcheck.log) printed
  "found by candidate 2, /kaggle/input/datasets/<user>/<dataset>" and ran
  detcheck against /kaggle/input/datasets/ericsom/cbo-gap-archive.
- K4 (Kaggle, cross-platform facts; record, not a defect). Established by
  runs/detcheck-kaggle-20261009-094955/cbo-detcheck.log, compared line by
  line with logs/detcheck-v2-full-repo.log, logs/detcheck-v2-full-separate.log,
  logs/detcheck-v3-full-repo.log and logs/detcheck-v3-full-separate.log:
  (a) Archive bytes. The five archive sha256 lines (exactcal.py,
      regimemap.py, rmapj.py, exactcal_real.csv, rmapj_real.csv) are
      identical in the Kaggle log and all four local logs, and equal the
      corresponding entries of zenodo-v1.sha256. The archive Kaggle mounted
      is byte-identical to the deposit for every file the gate reads.
  (b) Random stream. The printed X0[0,:3] of R1, R2 and R3 is identical, to
      every printed digit, on the laptop (NumPy 2.5.3) and on Kaggle (NumPy
      2.1.3). That is two platforms, not three: the archive did not store
      X0, so the Windows 7 platform that produced it has no X0 to compare
      (detcheck docstring; ledger "Determinism gate").
  (c) Reproduction across NumPy versions. The archived values were produced
      with NumPy 1.24.4 (CLAUDE.md rule 7). They are reproduced within the
      gate's tolerance (half a unit in the last stored digit) with NumPy
      2.5.3 on the laptop and NumPy 2.1.3 on Kaggle. The gate itself was not
      run on the archive's platform; the archive is the reference it checks
      against.
  Consequence: under CLAUDE.md rules 7 and 16, numbers from either platform
  may be compared with archived numbers.
- K5 (Kaggle, resumption; record of a limit, not fixed by decision). kgrun.py
  bundles only the archive's .py files, exactcal_real.csv and
  rmapj_real.csv, and scripts/*.py except kgrun.py (build_bundle). It never
  uploads earlier run folders. CLAUDE.md rule 17 (amended 2026-10-10) allows
  resumption from the completed task keys of previous run folders. Locally
  that works, but on Kaggle a resumed job cannot see the folders it would
  resume from.
  Consequences, decided by Rahul on 2026-10-10:
  - every Kaggle shard is sized to the 6-hour projected ceiling, half the
    12-hour cap;
  - Kaggle output is treated as lost if a session hits the cap, because it
    is not known whether /kaggle/working survives;
  - resumption is a recovery from fetched output only.
  kgrun is not changed. It is fixed only if a shard actually needs to
  resume on Kaggle. OPEN as a known limit.
  CLOSED 2026-10-11 (Rahul: "every Kaggle job must be resumable"; losing
  work, not runtime, is the constraint). scripts/kgrun.py md5
  d8a053691f3a5774d2975f5cde07ee44, not executed.
  - --resume-dirs ships earlier fetched run folders, which the runner
    passes as --resume-from. --data-dirs ships input folders and replaces
    runs/<name> in --args (the calprec2 smoke folder is --throughput).
  - Before upload, every shipped folder must be a direct subfolder of
    runs/; its sha256.txt must list exactly the files present, with
    matching hashes; and it must be tracked and unmodified in git.
  - Files go into the bundle flat, with an index. The reason: kgrun
    versions with --dir-mode skip, which drops subdirectories, and Kaggle's
    handling of uploaded archives is not recorded here.
  - The runner rebuilds each folder under /tmp/kgrun-ship, verifies it
    against its sha256.txt (exit 2 on mismatch), and prints each folder
    with its rows and complete rows. /tmp is not /kaggle/working, so the
    inputs are not fetched back as output.
  - The bundle's size and file count are printed. A warning appears above
    --warn-mb (1000 MB by default), a local choice and not Kaggle's limit,
    which is not recorded here.
  - A git guard refuses run and push while runs/ has uncommitted paths
    or HEAD is ahead of its upstream.
  What it now permits: a Kaggle job of a script with rule-17 resumption
  (calprec2 --resume-from) can continue from any attempt that was fetched
  and committed. The runbook is notes/CALPREC2_RUNBOOK.md.
  What it still does not do:
  - recover an attempt whose /kaggle/working is lost at the cap. Whether
    it survives is still not known; the first death will show it. The loss
    is bounded by one attempt;
  - let one shard resume from another. Their tasks are disjoint, and
    calprec2 refuses differing parameters;
  - pin Kaggle's image. A Python or NumPy change between attempts makes
    calprec2 refuse the resume (exit 2), and rule 16 then needs detcheck
    on the new image;
  - stop a job cleanly before the cap. [Superseded the same day: calprec2
    --stop-after, default 32400 s, exit 5, with G-STOP; N28 second
    addendum.]
  - check that logs/ is committed. The guard covers runs/ and HEAD only.
  - Nothing of this has run on Kaggle yet.
