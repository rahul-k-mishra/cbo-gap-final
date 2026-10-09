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

## Determinism gate (pre-registered 2026-10-08)

scripts/detcheck.py imports exactcal.py and regimemap.py from zenodo-v1 and
reruns three archived realizations with their archived seeds: exactcal_real.csv
row 1 (ackley, d = 2, centred, tau_0 = 0.5, seed 20261707), one exactcal row at
d = 40, and the first isotropic d = 80 row of rmapj_real.csv. Criteria:
D1, first entries of X0 and the solved beta match the archived beta to full
double precision; D2, all ten E_J match the archived %.8g values to relative
5e-8 and the slope to 5e-7 absolute; D3, one worker and two workers give
byte-identical output. PASS requires all three realizations to pass D1-D3.
Until PASS is recorded in ENVIRONMENT.md, no number from this machine is
compared with an archived number.

## Repository defects

- G1 (repo, history). Commit 7f5e257 ("Kaggle pipeline: kgrun driver,
  detcheck archive/outdir flags, ...") has a message naming the detcheck
  --archive and --outdir flags, but scripts/detcheck.py in that commit's tree
  contains neither (zero occurrences of --archive). The flags landed in the
  following commit, e945d17, which contains scripts/detcheck.py alone. History
  is not rewritten: 7f5e257 is pushed and stays as it is, and this entry is
  the record. CLOSED by e945d17.
