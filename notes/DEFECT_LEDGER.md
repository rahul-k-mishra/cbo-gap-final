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
