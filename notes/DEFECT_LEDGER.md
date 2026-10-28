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
  ARC1. 2026-10-15: round1-zip holds ess_extend_raw.csv,
  ess_extend_summary.csv, ess_panel_raw.csv and ess_panel_summary.csv
  (N34). Whether they produce the Section 7.2 exponents (0.608, 0.519,
  0.565) has not been checked.
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
  2026-10-25: the seed-paired arm was not implemented (N40). The second
  half of the disposition does not hold as written.
- R8 (ref, T). sn-article.tex line 348 writes E_J ~ C J^{-gamma} with
  gamma-hat ~ -1 as the fitted slope. Write E_J ~ C J^{gamma}; recheck every
  sign-bearing definition. OPEN.
- R9 (ref, T + A/R). "upper end of a bootstrap 95% interval" is the 97.5th
  percentile in code (regimemap, rmapj, perjcal, partm, reboot: [2.5, 97.5];
  visibility, regime: 97.5). State 97.5%, or recompute at 95% where
  per-realization data exist (7.12, 7.14, 7.15); Table 5 and the other
  verdict counts cannot be recomputed (ARC2). OPEN.
  2026-10-15: the interval level each logged quantity carries is
  tabulated in N34, from the round-1 logs.
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
  Addendum 2026-10-15, from round1-zip (N34):
  - round1-zip/cbo-gap/logs_reboot.log (Python 3.8.10, NumPy 1.24.4) is a
    console of reboot.py. It prints the 30 Part D paired gaps at 400 and
    4000 resamples side by side: "largest endpoint shift: 0.0163",
    "verdicts changed: 0". This supports tex 309's "move an interval
    endpoint by less than 0.02 and no equivalence verdict changes", for
    those 30 cells only.
  - The same log ends: "NOT RECOMPUTED ... The tolerance table of Section
    7.5 comes from boundary.py ... Its intervals cannot be recomputed
    here." So the script tex 309 calls the single re-analysis script says,
    in its own output, that it did not recompute the Section 7.5 intervals.
    N8 is confirmed by a log.
  - Which value the manuscript quotes:
    - The severity trends (+0.1440 [+0.1232,+0.1637]; +0.1330
      [+0.1169,+0.1497]; -0.0019 [-0.0302,+0.0270]; -0.0014
      [-0.0263,+0.0225]), the onset intervals of the Part D onset table
      (tex 605-) and the four b3 intervals (tex 545) equal the log's
      4000-resample lines. The log prints those only at 4000.
    - For the paired gaps the manuscript quotes point gaps, which do not
      depend on B, and the qualitative "paired intervals excluding the 0.05
      margin at d = 20, 40, 80" (tex 650). At r = 0.75 that holds at both
      400 and 4000 (d = 20 lower ends +0.0874 and +0.0871; d = 40 +0.0558
      and +0.0562; d = 80 +0.1308 and +0.1304). No paired-gap endpoint is
      quoted, so the log cannot show which B the text used for them.
    - The Part M counts of tex 549 (13/15/19, 38/49/54, 10/12/13, 7/15/22;
      Bonferroni 13, 43, 11, 10) equal logs_M_full.log section P11.4. That
      section comes from regimemap.py, whose N_BOOT is 400. The manuscript
      therefore quotes 400-resample values there, against tex 309.
  - Not settled: Tables 4 and 5 and the 7.10 and 7.11 counts. No round-1
    log of control, boundary, sigma or crossed exists in round1-zip.
  - tex 309's claim that the re-analysis ran on two installations,
    "NumPy 1.24.4 with Python 3.8.10 and NumPy 2.4.4 with Python 3.12.3",
    agreeing "to four decimals", has one log behind it: the NumPy 1.24.4
    one. No second log was found.
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
  - Result, 2026-10-23: the calibration is complete. Sources:
    - logs/calprec2-finalize.log (calprec2.py --finalize on the laptop);
    - runs/calprec2-finalize-20261023-112503/calprec2_beta.csv, sha256
      0fc98d23...2668 (logs/calprec2-finalize-manifest.log), committed in
      b663797;
    - the 26 long shards, runs/calprec2-long-s0of26-a1-kaggle-20261012-074403
      through runs/calprec2-long-s25of26-a1-kaggle-20261023-085912, every
      one attempt 1; Rahul reports every shard exited 0.

    Environment and code (log header):
    - Python 3.12.3, NumPy 2.5.3, Linux, 2 workers;
    - calprec2.py sha256 c339ca9d...c14d, costprobe2.py ea5cb2e1...f64b;
    - criteria as pre-registered: C5m <= 0.054682 at 64M, D1 <= 0.025
      between 64M and 256M, C1 <= 0.05, C6 <= 0.05, E1 <= 1e-12 at 64M
      rep 0, RSS <= 3072 MB.

    Checks: V1 (twelve archived modules) PASS, V0 (grid values and the
    Table 2 counts CONC 144, TAU8 144, SIGMA 288, ANISO 288) PASS, V2
    (sampler lines) PASS. Cells: boundary 144, crossed 24, mechanism 144,
    sigma 24, total 336. Every shard folder read reports all its rows
    complete; 56132 rows in all.

    Finalize (log lines, verbatim counts):
    - labels: target 309, beta 27;
    - adequacy: adequate 309; not adequate (C5m FAIL) 14; not adequate
      (C5m FAIL, D1 FAIL) 13;
    - no FLAG line, so no cell carries E1 FAIL, E1 not run, R1 FAIL or
      R1 not applicable; no cell is labelled incomplete. With neither, the
      finalize return code is 0, which matches the exit Rahul reports
      (the log does not print the exit code itself).

    What the counts imply, from calprec2.py finalize() alone: a cell
    judged not adequate is always labelled "beta, not adequate (...)", so
    the 27 beta cells are exactly the 14 + 13 not-adequate cells, and every
    one of the 309 adequate cells is labelled target. No adequate cell
    fell back to a beta label through C1 or C6.

    What the log does not say:
    - which rows or cells the 27 beta cells are (calprec2_beta.csv, label
      column);
    - how many of the 309 targets carry beta_prod (C6 passed) and how many
      beta_adq with dev_adq <= 0.05 (provenance column). Neither split may
      be quoted until a script prints it.

    The 27 beta-labelled cells are a finding about reference adequacy, not
    a failure (design above; N18 O2). Their tau_ref is the 256M median.
  CLOSED by b663797 (finalize run folder and log). The table's use in the
  rerun is N35's second precheck.
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
      assurance is false for them. [Qualified 2026-10-16 by
      logs/n30-20261015-2201.log, below: the code is still absent, but
      every point estimate except one is recomputable from the deposited
      per-realization files. The intervals' construction is not
      identified.]
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
  - Search of round1-zip, 2026-10-15 (N34): a round-1 working directory
    from Rahul's earlier laptop, read and hashed in full by Claude.
    - Its 21 root .py files, and the 24 .py files of the copy under
      Paper/version_1/Latex/cbo-gap-final/, are byte-identical to the
      deposit's. The nested zips hold the same 70-file package and
      nothing else. The two .pyc files under __pycache__ (exactcal,
      regimemap; cpython-38) record source sizes 16596 and 27824 bytes,
      equal to the archived .py sizes. So round1-zip holds no code beyond
      the deposit, and none that computes an N30 number.
    - No N30 number appears in any of its eight logs:
      - Table 3's upper-block intervals [0.021,0.083], [0.005,0.126],
        [0.003,0.199] and the d = 5 and d = 10 entries;
      - the middle-block intervals [0.022,0.083], [0.006,0.124],
        [0.117,0.381];
      - b_dtau, b_tau, b_d with their intervals;
      - the pairwise contrasts and +0.1940 [+0.0682,+0.3105];
      - 0.0260 [0.0191,0.0341].
    - What the logs do contain. logs_exact_full.log (exactcal.py P-E2)
      prints, at tau_0 = 0.5, 0.1, 0.01: d = 2 slopes -1.0655, -1.0629,
      -1.1299; d = 40 slopes -1.0113, -1.0037, -0.8766; changes 0.0542,
      0.0592, 0.2533; intervals [0.0132,0.0965], [0.0155,0.1031],
      [0.1985,0.3101].
      - The d = 2 and d = 40 entries and the changes of Table 3's middle
        block (-1.066, -1.011, +0.054; -1.063, -1.004, +0.059; -1.130,
        -0.877, +0.253) are these values rounded. Their intervals are not.
      - The tau_0 = 0.5 and 0.1 rows of the upper block have the same
        points, as they must: at those targets J >= 1/tau_0 is the full
        grid.
    - 0.078. It is in no log as a computed value. It appears in
      perjcal.py as a typed constant, NESTED = {0.5: 0.054, 0.01: 0.078}
      with the comment "exactcal, same window, for comparison". perjcal's
      log prints it back in the column "nested". So the J >= 1/tau_0
      value at tau_0 = 0.01 existed before perjcal.py was written
      (round1 timestamp 2026-08-23 00:05), and the code that computed it
      is not in round1-zip either.
    - Also without a generating log or code: tex 593's "[0.0069,0.2087]",
      perjcal's contrast "on the finer (objective, realization) unit".
      perjcal.py's own bootstrap is over objectives (lines 233-240), and
      its log prints only [0.0059,0.2265]. Added to this entry 2026-10-15.
  - Forensic reconstruction: scripts/n30_reconstruct.py (2026-10-15)
    evaluates every N30 number under an enumeration fixed in its
    docstring before any run. RESULT, recorded 2026-10-16 from
    logs/n30-20261015-2201.log; run folder runs/n30-20261015-220127/
    (n30_points.csv, n30_intervals.csv, n30_se.csv, n30_verdicts.csv).
    - Header: Python 3.12.3, NumPy 2.5.3, Linux, 2 workers. The laptop
      passed the determinism gate (ENVIRONMENT.md,
      logs/detcheck-v3-full-repo.log). Ten archive files were checked
      against zenodo-v1.sha256, and logs_exact_full.log against
      round1-zip.sha256; all ok. Exit 0.
    - R6 positive control: PC PASS. All fifteen values of exactcal.py's
      P-E2 (three rows: d = 2, d = 40, change and interval at tau_0 0.5,
      0.1, 0.01), as printed in round1-zip's logs_exact_full.log, are
      reproduced. So the machinery reproduces a Windows-7 round-1
      bootstrap exactly, seed and draw order included, when the
      construction is known.
    - Match rule (R3): within half a unit of the last printed digit. That
      is 0.0005 for 3-decimal values and 0.00005 for 4-decimal ones. For an
      interval, both ends must match under one specification. "Spec" below
      is the log's own label.
    OUTCOME 1. POINT ESTIMATES REPRODUCED. These are deterministic: no seed
    enters. The count is the number of matching specifications, out of
    the 2 estimands x 5 windows (x the V variants).
          T3M tau 0.01  d2 -1.130, d5 -1.048, d10 -0.968, d40 -0.877
                        1 each (E=slope, W-full); change +0.253: 2
                        (W-full, signed and abs)
          T3M/T3U tau 0.1   d2 -1.063, d5 -1.036, d10 -0.999, d40 -1.004
                        2 each (W-full, W-ge); change +0.059: 4
          T3M/T3U tau 0.5   d2 -1.066, d5 -1.001, d10 -1.041, d40 -1.011
                        3 each (W-full, W-ge, W-gt); change +0.054: 6
          T3U tau 0.01  d2 -1.071, d5 -1.091, d10 -1.006, d40 -0.994
                        2 each (W-ge, W-gt)
          REGR          b_dtau +0.0073, b_tau -0.0288, b_d +0.0069
                        1 each (E=slope, W-ge, resp gamma)
          REGF          b_dtau +0.0305: 1 (E=slope, W-full, gamma)
          CON           0.1-0.01 -0.0182: 1 (W-ge, signed);
                        0.5-0.01 -0.0233: 2 (W-ge, W-gt);
                        0.5-0.1 -0.0050: 2 (W-full, W-ge)
          SEP           +0.1940: 2 (E=slope, W-full, def S1, signed/abs)
      - Every reproduced point is E=slope (S-mean-slope), and no point is
        reproduced by E=curve. This bears on N33.
      - Claude's reasoning, not tested by the script. The multiple matches
        at tau_0 0.5 and 0.1 are not ambiguity. The grid starts at J = 10
        (docstring, W-full), so at tau_0 0.5 the windows W-full, W-ge and
        W-gt select the same J, and at tau_0 0.1 W-full and W-ge do. These
        are one specification under several names. Signed and abs agree
        whenever the change is positive. So the point estimates pin down
        the estimand (S-mean-slope) and the window: full grid for the
        "full grid" rows, J >= 1/tau_0 for the restricted rows. The log
        does not separate W-ge from W-gt at tau_0 0.01.
      - The SE statistics of tex 78 are bootstrap outputs, so they are
        seed-dependent and listed separately. Median 0.0260: 18
        specifications. q25 0.0191: 18. q75 0.0341: 4. The "IQR"
        [0.0191,0.0341] as a pair: 1 (SE-a, B 400, ddof 0, S 20260822).
        That one specification is NOT among the 18 that give the median.
        So no single specification reproduces tex 78's "0.0260, IQR
        [0.0191,0.0341]" as stated. Each part is reproduced separately.
    OUTCOME 2. INTERVALS REPRODUCED. Each count is the number of matching
    specifications, with the R5 count of consistent families (seed and
    scope left free) after it.
          REGR b_d CI    [-0.0025,+0.0160]    1   (R5 19)
                         W-ge, O=A, U12p, B 2000, L95, S 20260824
          REGR b_dtau CI [-0.0091,+0.0227]    1   (R5 11)
                         W-gt, O=X, U12p, B 400, L95, S 11
          REGR b_tau CI  [-0.0754,+0.0208]    1   (R5 26)
                         W-ge, O=A, U12p, B 4000, L95, S 20260821
          SE IQR         [0.0191,0.0341]      1   (see above)
          T3U tau 0.01 CI [0.003,0.199]      10   (R5 12)
          T3U tau 0.1 CI  [0.005,0.126]      16   (R5 32)
          T3M tau 0.1 CI  [0.006,0.124]      34   (R5 40)
          T3U tau 0.5 CI  [0.021,0.083]      96   (R5 54)
          T3M tau 0.5 CI  [0.022,0.083]      96   (R5 60)
      - A match under ninety-six specifications identifies no method. A
        "REPRODUCED" verdict on T3M/T3U tau 0.5 (96), T3M tau 0.1 (34),
        T3U tau 0.1 (16) or T3U tau 0.01 (10) says the interval is
        insensitive to the choices enumerated: unit, order, B, seed, scope,
        sign. It does not say that the original construction has been
        recovered. These intervals are computable from the deposit. Their
        construction is unknown.
      - A match under one specification is not evidence in this log either.
        Claude's reading of the log lines, not a criterion of the script:
        - The three REGR intervals come from one regression, which in any
          construction is fitted to one set of resamples. They matched
          under three different specifications: windows W-ge, W-gt, W-ge;
          orders A, X, A; B 2000, 400, 4000; seeds 20260824, 11,
          20260821. No single specification reproduces all three.
        - The b_dtau interval matched only under W-gt. The b_dtau point
          estimate is reproduced only under W-ge. The specification that
          gives the interval does not give the point it surrounds.
        - Each interval target was tried under every enumerated
          combination: 80 (E, W, O, U) combinations per target, each under
          4 B, 7 seeds, 2 levels and the variant and scope options. The log
          reports "interval tasks: 8960". Among that many draws, a
          single coincidence within half a unit in the fourth decimal is
          what chance can produce. R5 shows 11 to 26 families consistent
          with each REGR interval. These one-specification matches are
          therefore best read as coincidences, not identifications. The log
          does not measure the chance rate, so this reading is not tested.
        - The SE IQR match is subject to the same point. Its specification
          does not reproduce the median quoted with it.
      - What IS stable across the matches (description of the log lines):
        - every reproduced T3 or REGR interval is L95, never L90;
        - every match of T3M tau 0.1, T3U tau 0.1 and T3U tau 0.01 is
          V=abs: no signed specification reproduces those three. In this
          enumeration, the published intervals at those targets behave as
          bootstraps of an absolute value. That is the N32 error. At
          tau 0.5 the matches come in signed/abs pairs: the two variants
          gave the same interval there. This is consistent with the absolute-value construction; it is
          not proof of it.
    OUTCOME 3. NOT REPRODUCED. Seven quantities, with the nearest
    specification's maximum endpoint error, against the R3 tolerance, and
    the R5 count:
          CON 0.1-0.01 CI  [-0.1096,+0.0480]  nearest error 0.00788  R5 0
          CON 0.5-0.01 CI  [-0.1482,+0.0567]  nearest error 0.01272  R5 0
          CON 0.5-0.1 CI   [-0.0701,+0.0545]  nearest error 0.00087  R5 16
          REGF b_dtau CI   [+0.0123,+0.0479]  nearest error 0.00016  R5 10
          SEP CI           [+0.0682,+0.3105]  nearest error 0.00045  R5 82
          T3M tau 0.01 CI  [0.117,0.381]      nearest error 0.00060  R5 16
          T3U tau 0.01 change +0.078 (a point) nearest +0.07747,
                           E=slope, W-ge, signed; error 0.00053 against
                           tolerance 0.0005
      - Two kinds. CON 0.1-0.01 CI and CON 0.5-0.01 CI have no
        consistent family (R5 0) and miss by 0.008 and 0.013, so their
        construction lies outside the enumeration altogether. The other
        four intervals have consistent families (R5 10 to 82): some
        enumerated construction, under some seed, could give them, but no
        enumerated seed does. The script cannot tell a construction it
        lacks from a seed or draw order it lacks.
      - Where they are quoted:
        - Abstract (tex 34): 0.078, and "+0.0305 with interval
          [+0.0123,+0.0479]". The REGF point is reproduced, its interval
          is not.
        - Conclusions (tex 703): 0.078. It does not quote the CON
          intervals, but it states the verdict they carry: "with no
          difference detected between any pair and no pair shown
          equivalent".
        - Body: 0.078 at tex 371 (Table 3), 394, 396 (twice), 593, 595.
          The CON and SEP intervals at tex 394. REGF at tex 392. [0.117,
          0.381] at tex 376 (Table 3) and 563.
        - The abstract and the Conclusions also quote +0.0073
          [-0.0091,+0.0227], whose interval is one of the
          one-specification matches discussed under outcome 2.
    ANALYSIS: 0.078, the only point estimate not reproduced.
      - Facts:
        - Every other number in its table row (tex 371) is reproduced under
          E=slope, W-ge: d2 -1.07110, d5 -1.09096, d10 -1.00588, d40
          -0.99362 (log).
        - Under that same specification, the change from the deposited
          data is +0.07747. The published +0.078 differs by 0.00053, just
          outside the 0.0005 tolerance.
        - In code, 0.078 exists only as the constant typed into perjcal.py
          line 101, NESTED = {0.5: 0.054, 0.01: 0.078}, commented
          "exactcal, same window, for comparison". The same value appears
          in perjcal.py's docstring (lines 10, 55). No deposited or round-1
          script emits it (above).
        - round1-zip's MANIFEST.txt lists an exactcal_real.csv (ebf4cdff…)
          that is in neither source (N34).
      - What this supports:
        - 0.078 was carried into the text and into perjcal.py by hand,
          from a computation not in the deposit or in round1-zip.
        - That computation used the same estimand and window as the rest of
          the row, or something very close. The deposit reproduces the four
          slopes of the row and comes within 0.00053 of the change.
        - The value the deposited data give under the specification that
          reproduces the row is +0.07747. If the new paper quotes this
          round-1 change at all, the deposit supports that value, not
          +0.078.
      - What it does not support:
        - Which of several causes produced the difference. Each of the
          following is consistent with the facts above, and the log cannot
          separate them:
          - an earlier version of the per-realization data, such as the
            unrecovered exactcal_real.csv in MANIFEST.txt;
          - a window or estimand outside the enumeration;
          - rounding of a value computed elsewhere;
          - a transcription slip.
        - That the difference matters substantively. It is 0.00053 against
          an interval of [0.003,0.199].
        - Anything about intent.
    STATUS AFTER THE RUN. The defect stands and its scope narrows.
      - Still true:
        - The deposit lacks the code that produced every N30 number.
        - tex 309's "no reported interval originates from a computation
          that is not in the archive" is false. So is tex 719's claim that
          each criterion is in the archived scripts, for these numbers.
      - Now shown:
        - Every published N30 point estimate except 0.078 is computable from
          the deposited per-realization files, under a named estimand
          (S-mean-slope) and window (full grid or J >= 1/tau_0).
        - The published intervals other than the six in outcome 3 are
          computable from the deposit under at least one specification.
          For most of them "computable" means insensitive to the
          construction, not recovered.
        - No single specification reproduces the three REGR intervals
          together, nor the 0.0260 median together with its IQR.
      - Not evaluated by n30_reconstruct.py: tex 593's [0.0069,0.2087]
        (perjcal's "finer unit" contrast). It was not in the script's
        quantity list.
    WHAT THE NEW PAPER SHOULD STATE about round-1 reproducibility, on this
    basis (guidance for the text, no manuscript edit made):
      - Drop tex 309's assurance and tex 719's claim as they stand. Neither
        can be repeated.
      - Say what holds:
        - the round-1 point estimates of Table 3, the Section 7.3
          regression, the pairwise contrasts and the separation recompute
          from the deposited per-realization file under the stated
          estimand and window;
        - the one exception, the restricted tau_0 = 0.01 change printed as
          0.078, recomputes as 0.07747 from the deposit (log value).
      - Say what does not hold:
        - the round-1 intervals were produced by code that was not
          deposited;
        - their construction cannot be identified from the deposit;
        - several match many constructions; two match no enumerated
          construction under any seed, and four more match no enumerated
          seed.
      - The new paper does not reuse any round-1 interval. Every interval it
        reports comes from its own archived rerun under the criteria of
        ANALYSIS_CRITERIA_DRAFT, once decided.
      - The 0.0260 scale cannot serve as a stated basis for anything,
        including the equivalence margin (draft item 5). Its median and its
        IQR are not reproduced together by any one construction.
    Note on Rahul's message of 2026-10-16. It says "all three exactcal
    values reproduced". The log reproduces three rows of five values,
    fifteen in all, as R6 requires.
  OPEN. The scope is narrowed by logs/n30-20261015-2201.log. Closing needs
  the new paper's text on round-1 reproducibility, verified by the rule 8
  diff.
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
  - WITHDRAWN 2026-10-15 (Rahul's instruction, on the M7 log). This
    bullet used to say that differencing by position estimates the variance
    of a difference of two independent means, "So the intervals themselves
    are not invalidated by this". That sentence was reasoning and was never
    checked. M7 measured it and it is false in three of the thirty Part D
    cells. The measurement follows.
  - What M7 measured. Source: logs/m7-20261015-2146.log, run folder
    runs/m7-20261015-214629/ (m7_cells.csv). The log names itself
    m7-20261015-2146.log, not -214629; the run folder has the longer stamp.
    - Setup, from its header: Python 3.12.3, NumPy 2.5.3, Linux, 2 workers;
      archive files regimemap.py, reboot.py and regimemap_D_real.csv
      verified against zenodo-v1.sha256; 30 (d, r) cells, 36 keys per arm,
      tau_0 0.1. Exit 0.
    - M7-0 PASS: C-ARCH reproduces all ten gaps printed in tex 650 within
      0.0005. M7 was reading the comparison the paper reports.
    - Decision line: "N31 MUST BE CORRECTED". M7-A width: 3 of 30 cells
      material. M7-B verdict: 0 of 30.
    - The three material cells (rho = archived C-ARCH 90% width over the
      independent-arm C-IND width; criterion |rho - 1| > 0.1 and > 3 sd_mc):
          d 5   r 1.25  rho 0.900  sd_mc 0.017  rho - 1 -0.1003
          d 5   r 1.5   rho 0.868  sd_mc 0.018  rho - 1 -0.1321
          d 10  r 2.0   rho 0.870  sd_mc 0.017  rho - 1 -0.1299
      Archived against independent-arm intervals in those cells:
          d 5   r 1.25  C-ARCH [+0.0887,+0.1693]  C-IND [+0.0841,+0.1737]
          d 5   r 1.5   C-ARCH [+0.0956,+0.1933]  C-IND [+0.0873,+0.1998]
          d 10  r 2.0   C-ARCH [+0.1252,+0.2019]  C-IND [+0.1199,+0.2080]
    - Over all 30 cells (log, "FULL DISTRIBUTION"): rho - 1 min -0.1321,
      q25 -0.0353, median -0.0046, q75 +0.0281, max +0.0979, mean -0.0034.
      Cells with |rho - 1| above 0.02: 20 of 30; above 0.05: 8 of 30;
      above 0.10: 3 of 30; above 0.20: 0 of 30.
  - Direction. All three material cells are narrowings: the archived
    interval is shorter than the independent-arm interval. Read with
    C-IND as the interval the independent-arm design supports, the
    archived intervals are anti-conservative in those cells, not merely
    different. M7 measured widths, not coverage; the anti-conservative
    reading rests on C-IND being the right reference for independent arms,
    which is the construction's premise, not something the log tests.
    The two largest widenings, d 40 r 1.25 (rho - 1 +0.0979, sd_mc 0.0186)
    and d 40 r 1.5 (+0.0965, 0.0241), exceed 3 sd_mc but fall below the
    0.10 threshold, so they are not material under M7-A. In those two cells
    the archived intervals are wider than C-IND, which is conservative.
  - Mechanism, as the log shows it. The corr column of the log (the
    within-objective index correlation of isotropic and anisotropic slopes,
    objective means removed, pooled over the 36 keys; m7_pairing.py lines
    243-245) reads +0.19, +0.28 and +0.24 for the three material cells.
    - REASONING, NOT MEASUREMENT, and it is Rahul's (his message of
      2026-10-15), not Claude's: for independent arms the true correlation
      is zero, and its sampling spread at this size is near 1/sqrt(36). A
      chance positive index correlation makes the bootstrap of
      by-index differences subtract a covariance that the independent
      design does not have, so the interval narrows.
    - Claude's notes on that reasoning, also not measurement: the corr is
      computed after removing three objective means, so 1/sqrt(36) is an
      approximation to its null spread; M7 tested neither that spread nor
      whether +0.28 is unusual for it. The log shows the sign pattern is
      not one-to-one with the width change: d 80 r 1.0 has corr +0.23 and
      rho 0.963, d 80 r 1.25 has +0.27 and 0.940 (not material); d 80 r 2.0
      has -0.35 and 0.992, d 20 r 1.25 has -0.38 and 1.065; the two d 40
      widenings have -0.31 and -0.41.
  - What is NOT affected, per the log.
    - M7-B: 0 of 30 verdicts change under the archived rule (margin 0.05).
      Every cell is DIFF or incon under both C-ARCH and C-IND; no cell is
      EQUIV under either, so Part D carries no equivalence conclusion that
      could change.
    - The five cells tex 650 describes as excluding the 0.05 margin
      (r 0.75 at d 20, 40, 80; r 3.0 at d 40, 80) are DIFF under both
      constructions. The three material cells are at r 1.25, 1.5 and 2.0;
      tex 650 prints no interval for them. Whether fig:severity (right)
      draws their intervals has not been checked.
    - The width change is not small in general: 20 of 30 cells move by
      more than 0.02 in |rho - 1|. [Rahul's instruction said "20 of 30
      cells within 2%". The log line is "cells with |rho - 1| > 0.02: 20 of
      30", the reverse. Recorded from the log.]
  - ALIGN ranks at the extremes (log, "context"; the rank is the fraction
    of 200 random within-objective relabellings of the anisotropic reps,
    each run through C-ARCH's algorithm with C-ARCH's seed, whose width is
    at most the archived width):
          d 40  r 1.5   rank 0.99   ALIGN as rho - 1 [-0.0631,+0.0677]
          d 40  r 1.25  rank 0.98   ALIGN as rho - 1 [-0.1119,+0.0927]
          d 80  r 1.25  rank 0.04   ALIGN as rho - 1 [-0.0659,+0.0549]
          d 5   r 1.5   rank 0.05   ALIGN as rho - 1 [-0.1430,+0.1675]
    - What they show: the archived width depends on which arbitrary rep
      alignment the seed counter happened to produce. In these four cells
      that alignment gave one of the widest (d 40) or narrowest (d 80
      r 1.25, d 5 r 1.5) widths among the 200 relabellings. At d 40 r 1.25
      and r 1.5 the archived rho - 1 lies above the 97.5th percentile of
      ALIGN. The ALIGN ranges also show how far relabelling alone moves a
      width: as far as [-0.2206,+0.1449] at d 10 r 2.0.
    - What they do not show: any selection or tuning of the alignment. The
      alignment came from the seed counter, and some ranks near 0 or 1
      among 30 cells are what an arbitrary alignment produces; M7 did not
      test the distribution of the ranks. They are context, not a
      criterion.
  - Scope, as the log states it: "COVERS the probe-beta Part D diffusion
    gaps only". Not tested: the r and d index pairings of the next bullet;
    calprec betas; shared seed keys across diffusions; the 7.11 "3 of 18"
    result.
  - What the rerun must do (no choice made here). Either share seed keys
    across the two arms, so that the pairing is real and a paired bootstrap
    is valid, or keep the arms independent, difference them as independent
    samples (no by-index differencing), and say so in the text. The archive
    did neither: it differenced independent arms by index and called them
    paired. ANALYSIS_CRITERIA_DRAFT items 3 and 5 carry the decision.
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
    The word "paired" and any implied variance reduction are false here as
    well. This part goes beyond Rahul's instruction of 2026-10-15 and was
    added by Claude on reading the seeds. [Corrected 2026-10-15 after M7:
    this bullet used to end "The same reasoning applies: the intervals
    stand". That reasoning failed its only test (Part D, above). Whether
    these intervals stand is UNTESTED: the same chance index correlation
    can narrow or widen them, and M7 does not cover them.]
  - 2026-10-15: "the intervals themselves are not invalidated" was put to
    test by scripts/m7_pairing.py on the Part D diffusion gaps. The result
    is recorded above (logs/m7-20261015-2146.log). [Correction, later the
    same day: in commit 2cf22ee this note was inserted before the sentence
    attributing the r and d part to Claude, which then read as part of
    this note. The sentence is restored to its bullet above.]
  - Evidence that the pairing claim was believed at run time, not merely
    mis-written afterwards (round1-zip, N34). logs_M_full.log, the console
    of the Part M run on Windows 7 (Python 3.8.10, NumPy 1.24.4, workers 3),
    prints in its header: "Bootstrap unit: the independent coupled
    realization; the two-arm comparison resamples PAIRED on the shared
    realization index", and above section P11.3: "Paired on the shared
    realization index, which the earlier files could not support". The
    same lines appear in logs_M_smoke.log. reboot.py's log heads its table
    "PAIRED anisotropic minus isotropic". The claim was printed by the
    scripts themselves at execution.
  - control.py does share seeds between its fixed and adaptive arms (line
    345 and the comment after it). Its pairing (Section 7.4, Table 4) is
    not affected.
  - Open decision for the rerun: whether the seed key omits the diffusion
    coordinate, so that the two arms share X0 and the Brownian increments,
    or the arms stay independent and are analysed as independent (see
    "What the rerun must do" above). No such decision has been made
    (ANALYSIS_CRITERIA_DRAFT items 3 and 5).
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
- N34 (record; second read-only source). round1-zip/, a round-1 working
  directory from Rahul's earlier laptop, extracted by Rahul and made
  read-only (dr-xr-xr-x throughout). Treated exactly as zenodo-v1: read,
  never written. Manifest round1-zip.sha256 (143 files, sha256sum format,
  paths relative to round1-zip/), written by Claude on 2026-10-15 and
  verified with sha256sum -c.
  Contents, checked by Claude against zenodo-v1.sha256:
  - round1-zip/cbo-gap/ holds 64 files:
    - 50 byte-identical to deposit files, including all 21 .py files.
    - 14 not in the deposit under their own names: eight console logs
      (logs_M_full, logs_M_smoke, logs_exact_full, logs_exact_smoke,
      logs_finitej, logs_perjcal_full, logs_reboot, logs_rmapj_full),
      ess_extend_raw.csv, ess_extend_summary.csv, ess_panel_raw.csv,
      ess_panel_summary.csv, regimemap_D_summary.csv and MANIFEST.txt.
    - regimemap_D_summary.csv is byte-identical to the deposit's
      regimemap_summary.csv, so only its name is new (cf. ARC4).
    - Absent there, present in the deposit: the figures, mkfig2/4/5.py,
      regimemap_real.csv, regimemap_summary.csv and the LaTeX files.
  - __pycache__/exactcal.cpython-38.pyc and regimemap.cpython-38.pyc. Their
    headers record source sizes equal to the archived .py sizes. The code
    objects were not compared.
  - Paper/version_1/Latex/cbo-gap-final/ holds 70 files, the submission
    package (ARC7):
    - 66 are byte-identical to the deposit;
    - cover-letter.tex and cover-letter.pdf;
    - sn-article.tex and sn-article.pdf, which differ from the deposit.
      That sn-article.tex is byte-identical to manuscript/sn-article.tex,
      the submitted text with the DOI sentence (ARC3).
  - Paper/version_1/Latex.zip holds sn-article.tex, sn-article.pdf,
    cover-letter.pdf and cbo-gap-final.zip. Each is byte-identical to the
    file of that name in Paper/version_1/Latex/. That cbo-gap-final.zip
    has 70 members: 66 identical to the deposit, plus sn-article.tex,
    sn-article.pdf, cover-letter.tex and cover-letter.pdf, as in the
    folder above. Read in memory by Claude; nothing extracted.
  - Paper/version_1/sn-supplementary.tex and "sn-supplementary (2).pdf"
    are byte-identical to the deposit's.
  - MANIFEST.txt is a CertUtil record of ten hashes. Eight equal the
    deposit's. It also lists an EARLIER exactcal_real.csv (sha256
    ebf4cdff...2e87d0) and exactcal_summary.csv (c0d1990f...320cb8) before
    the deposited pair. That earlier run's files are in neither round1-zip
    nor the deposit. Which run it was is not recorded. exactcal.py's
    comment on a sigma = 0.1 run is consistent with it but does not
    identify it.
  What the eight logs reproduce (all Windows-7, Python 3.8.10, NumPy
  1.24.4):
  - logs_exact_full.log: Table 3 middle-block d = 2 and d = 40 values and
    changes (rounded); tex 563's 0.253 and the "moved ... by 0.300" (P-E3
    prints -0.2997). Not the Table 3 intervals (N30).
  - logs_exact_smoke.log: a 24-realization smoke; nothing reported.
  - logs_finitej.log: tex 587's numbers: the p5 values 10.000, 5.000,
    2.500; "22 of 30"; -0.123, -0.057; -1.449, -10.070; -0.050, -0.456.
  - logs_perjcal_full.log: tex 593's 0.0156 [0.0010,0.0576], 0.0964
    [0.0059,0.2265], width 0.2206 (tex: 0.221), outcome (c).
  - logs_rmapj_full.log: P-R1 "largest absolute slope discrepancy:
    4.998e-07" (tex 624: "within 5.0 x 10^-7"); tex 626's at most 0.045
    (0.0454), 0.1440 to 0.1617, 0.0019 to 0.0025, shifts 0.018 and 0.001.
    The log prints the severity as gamma(r=1) - gamma(r=3), so negative
    (trend -0.1440 [-0.1632,-0.1229]). The manuscript quotes reboot's
    gamma(3) - gamma(1) version, +0.1440 [+0.1232,+0.1637], whose interval
    comes from a different seed. tex 626 drops the sign. This is a sign
    convention difference between two scripts, recorded under R8, not a
    numerical error.
  - logs_reboot.log: tex 650's gaps (+0.016 ... -0.212, the sign change
    between r = 1.5 and 2.0 at d = 40 and 80); the S(1,3) and S(0.75,3)
    values and trends of tex 648; the onset table and "nine of ten"; the
    b3 intervals of tex 545. See N8 for the 400/4000 question.
  - logs_M_full.log: Table 7's map values (tex 514-532); the Part M counts
    of tex 549; "MAP VERDICT: both axes matter"; P11.3 paired gaps at
    90% (1000 resamples, seed 7). Run wall 26512.8 s.
  - logs_M_smoke.log: a 96-realization smoke; nothing reported.
  Interval level each logged quantity carries (code read, not assumed):
  - Rate-consistency verdicts and counts (logs_M_full P11.1 stars and
    P11.4): labelled "bootstrap 95% upper bound". regimemap.boot_ci at
    level 95 compares the 97.5th percentile of 400 resampled mean slopes
    with -0.85.
  - Bonferroni column: upper end at the 100 - 2.5/nb percentile.
  - Equivalence (logs_M_full P11.3; logs_reboot paired table): two-sided
    90%, the 5th and 95th percentiles, that is TOST at 5% per side. 1000
    resamples in regimemap, 400 and 4000 in reboot.
  - Severity trends, onset, b3 (reboot), rmapj trend, exactcal P-E2,
    finitej P-F3, perjcal P-C2: two-sided 95%, 2.5th and 97.5th
    percentiles.
  - The 97.5th-percentile path of item 1 is visible in no log as a
    number. The logs print only verdict symbols and counts for rate
    consistency, never the upper bound itself. It is visible only in the
    code (regimemap.py lines 250-257; the boot_ci of every other script).
  OPEN as a record. Its role is evidence for N8, N30, N31 and ARC6.

## Newly found (2026-10-16)

- N35 (result, rerun precheck). What scripts/rerun.py --precheck
  established on the laptop, before any trajectory of the fixed-beta rerun.
  Sources:
  - logs/rerun-precheck-20261016-1935.log;
  - runs/rerun-plan-20261016-193630 (rerun_plan_params.csv,
    rerun_plan.csv, rerun_archive_check.csv, rerun_onset_control.csv),
    whose manifest Claude verified with sha256sum -c.

  Environment and code:
  - Python 3.12.3, NumPy 2.5.3, Linux, 2 workers.
  - Script hashes printed: rerun.py a314dce4...8813, rerunlib.py
    5d55050e...9b06, costprobe2.py ea5cb2e1...f64b. These equal the files
    at commit 7270807, so the run used the reviewed code (notes/RERUN_REVIEW.md,
    first and second passes).

  Results:
  - V0 (plan identity). Every GRID factor of the seventeen rows reads "ok"
    against the archived source, and every row's cell and realization
    count equals Table 2 (BETA-ISO 42/840 through ONSET 180/2160).
  - P1 (archive identity). Twelve archived modules and finitej.py hash to
    zenodo-v1.sha256. S1: the X0 line of mechanism, boundary and law equals
    the expected line.
  - O1, the onset positive control (ninth message; it replaces the import
    rule 4 cannot cover). The retyped estimator reproduced all ten
    archived onsets exactly, against the manuscript's onset table
    (tex lines 608 to 612 and 615 to 619):
    - isotropic d 5, 10, 20, 40, 80: 1.50, 1.25, 2.00, 1.25, 1.00;
    - anisotropic: 2.00, 1.00, 1.25, 1.00, 2.00.

    The sixty per-r means, recomputed from regimemap_D_real.csv, equal the
    table's three-decimal values in 60 of 60 (log lines 172 to 191;
    rerun_onset_control.csv). The control checks point estimates only; the
    archive's onset intervals are not reproduced or compared.
  - A-BETA and A-SIGMA: 2034 ok, 0 FAIL, 288 not applicable. The 288 are
    CONC (144) and TAU8 (144), whose betas are calprec2's and have no
    archived counterpart. Per row:
    - ADAPT 72 ok;
    - BETA-ISO 42, BETA-ANI 12;
    - LAWPANEL 144, PROBEARM 144;
    - REFSIZE 12, SYNTH 72, NAMED 36, HORIZON 24;
    - GEOM 336;
    - RMAP 240, ONSET 180, CLIFF 144: beta and sigma;
    - SIGMA 288, ANISO 288: sigma only, their betas being calprec2's.

    The tolerance is half a unit in the sixth significant digit of the
    archive's "{:.6g}" columns, which is the stricter form after review
    fix F2.
    - ADAPT: all 72 cells, both arms, agree with the fixed arm's archived
      beta_first. That is review fix F1 (85ec11d). The check never ran in
      its earlier form against the adaptive arm's row. The statement that
      it would have failed rests on the archived values alone
      (control_summary.csv: adaptive 2.17581 against fixed 2.19167, ackley
      d 5 tau0 0.01), not on a run.
  - C2: PASS with no calprec2 table given. CONC, TAU8, SIGMA and ANISO are
    "beta pending" in this plan (calprec2_rows pending).
  - K4 (sharing): 28 groups with more than one row, exactly the expected
    set:
    - ackley, sphere and rosenbrock in REFSIZE, NAMED and HORIZON, owned
      by REFSIZE;
    - rastrigin in NAMED and HORIZON, owned by NAMED;
    - 24 regimemap cells in RMAP and ONSET, owned by RMAP.
  - K1: 23748 distinct (group, rep) keys. K2 PASS.

  What it does not establish:
  - anything about calprec2's betas. A second precheck with --calprec2 is
    needed after the finalize step;
  - anything about trajectories: no realization has been evolved under
    this plan.

  Repository note: the precheck's last line printed "Next: python
  scripts/manifest.py <folder>", but manifest.py takes no folder argument.
  The hint and the docstring line are corrected in rerun.py (cosmetic).
  The run mode checks the hashes of rerunlib.py and costprobe2.py against
  the plan, not that of rerun.py, so this plan stays valid.
  - Second precheck, 2026-10-23, with --calprec2
    runs/calprec2-finalize-20261023-112503. Sources:
    logs/rerun-precheck2-20261023-1126.log; plan
    runs/rerun-plan-20261023-112643, committed in a7f4256, whose manifest
    Claude verified with sha256sum -c (four files OK).
    - Script hashes printed: rerun.py 756c4069...818e, rerunlib.py
      5d55050e...9b06, costprobe2.py ea5cb2e1...f64b, the values
      notes/RERUN_RUNBOOK.md pins and the files at HEAD.
    - The table read is the finalize table: sha256 0fc98d23...2668, 336
      cells.
    - V0, P1, S1 and O1 as in the first precheck (O1: the same ten onsets
      and sixty per-r means).
    - C2 PASS: every cell of CONC, TAU8, SIGMA and ANISO found one table
      row with a beta and a label not "incomplete"; no C2 FAIL line.
    - A-BETA and A-SIGMA: 2034 ok, 0 FAIL, 288 not applicable, the same
      as the first precheck. Confirmed from the code that this is by
      design, not a check failing silently:
      - rerun.py build_plan sends a cell to rerunlib.archive_check
        whenever its beta is known. archive_check returns "not
        applicable" for any row with no entry in rerunlib.ARCH_CHECK.
        CONC and TAU8 have no entry: their betas are calprec2's, and the
        archive holds no beta to compare against;
      - CONC and TAU8 cells carry the single diffusion "none"
        (rerunlib._cell default), so 144 + 144 = 288 entries;
      - SIGMA and ANISO have entries with beta column None and sigma
        column "sigma": only their sigma is compared, which is why they
        read ok with or without the table;
      - the calprec2 betas themselves are checked by C2 only, for
        presence and label. Nothing compares them with an archived value,
        and nothing can.
    - K4 PASS (the same 28 groups), K1 23748 distinct keys, K2 PASS.
    - Plan comparison, by Claude, reading the two rerun_plan.csv files:
      1752 rows each, same columns; every archived-beta row identical;
      every calibrated row identical outside beta, beta_source and the
      cal_ columns. So the archived-beta shard set (N37) may run from
      either plan, and the seed keys of the calibrated rows did not move.
  CLOSED as a record by this commit. Nothing about trajectories under
  either plan is established yet.

- N36 (result, perjcal probe smoke; ledger K2 of notes/ANALYSIS_CRITERIA.md).
  Sources:
  - logs/perjcalprobe-plan-20261016-1934.log;
  - logs/perjcalprobe-smoke-20261016-1935.log;
  - runs/perjcalprobe-20261016-193516-smoke, manifest verified with
    sha256sum -c.

  Python 3.12.3, NumPy 2.5.3, Linux, 2 workers; script sha256
  c13734ea...7e48.
  - P1 (exactcal.py, perjcal.py) ok. P0: every constant equals perjcal.py
    main()'s literal: objs, dims [2, 40], taus [0.5, 0.01], M 15, Jinf
    50000, J10 grid, lam 1.0, sigma 0.2, dt 0.01, T 1.0, centred.
  - The plan has 192 units: ten sizes at tau0 0.5 and six at 0.01.
  - P2 PASS: two members on (ackley, d 2, tau0 0.5, J 10) give bitwise
    identical E 0.0055531100089299835, beta 1.03186349519711 and achieved
    fraction 0.50000000000000011.
    - Walls 3.8 s and 4.1 s, A3 ratio 1.074.
    - RSS 34.7 MB each.
    - Achieved / tau0 1.000000.
  - No projection: the smoke runs the pair only. The full probe is the
    next run.
  OPEN until the full probe.

- N37 (decision, Rahul 2026-10-16; the archived-beta shard set). Source:
  logs/rerun-schedule-20261016-1945.log. That is rerun.py --schedule on
  the laptop, for --nshards 1 to 8, against runs/rerun-plan-20261016-193630
  and costprobe2's measured walls (runs/costprobe2-s0-kaggle-20261010-103952,
  runs/costprobe2-s1-kaggle-20261011-101343). Script hashes printed:
  rerun.py 756c4069...818e, rerunlib.py 5d55050e...9b06, costprobe2.py
  ea5cb2e1...f64b.

  The thirteen archived-beta rows are BETA-ISO, BETA-ANI, LAWPANEL,
  PROBEARM, ADAPT, REFSIZE, SYNTH, NAMED, HORIZON, GEOM, RMAP, CLIFF and
  ONSET:
  - 19068 tasks;
  - summed measured unit wall 201542 s, or 50385 s at 4 workers in one
    shard;
  - per-shard estimates at 4 workers, labelled lower bounds (perfect
    scaling; walls from costprobe2's timing beta): 2 shards 25193 s; 3
    shards 16795 s; 4 shards 12596 s; 5 shards 10077 s.

  Decision: 4 shards. Rahul's reason: the estimate is a stated lower
  bound, and calprec2's shards have consistently run above their
  estimates. 3 shards leaves too little margin under the 21600 s per-shard
  ceiling for the saving of one launch.
  - The launch procedure is notes/RERUN_RUNBOOK.md: one job at a time,
    smoke first, every shard with the same --rows list, and RMAP launched
    with ONSET. A shared cell is run by its owner's job.
  OPEN until the four shards have exited 0.
  CLOSED 2026-10-25: all four exited 0 ("completed 4767  errors 0  not
  started 0" in each kernel log; K6 lists the folders), and
  rerun_analysis.py's A0 read 4767 complete realizations from each
  (N39).

- N38 (decision, 2026-10-23; the calibrated-row shard set). Source:
  logs/rerun-schedule-cal-20261023-1332.log. That is rerun.py --schedule
  on the laptop for --rows CONC,TAU8,SIGMA,ANISO, --nshards 1 to 12,
  against runs/rerun-plan-20261023-112643 (rerun_plan.csv sha256
  4aec4b1e...72f2) and costprobe2's measured walls. Python 3.12.3, NumPy
  2.5.3, --workers 4; nothing was run or written. Script hashes printed:
  rerun.py 756c4069...818e, rerunlib.py 5d55050e...9b06, costprobe2.py
  ea5cb2e1...f64b, the values notes/RERUN_RUNBOOK.md pins.

  The four calibrated rows:
  - 11232 tasks;
  - summed measured unit wall 99616 s, or 24904 s at 4 workers in one
    shard;
  - per-shard estimates at 4 workers, labelled lower bounds (perfect
    scaling; walls from costprobe2's timing beta): 2 shards 12452 s; 3
    shards 8301 s; 4 shards 6226 s.

  Decision: 2 shards, as stated in the 2026-10-23 instruction for the
  rerun queue. One shard, at 24904 s, is above the 21600 s per-shard
  ceiling. Two shards, at 12452 s each, sit at about the per-shard load
  of the archived-beta set, 12596 s, which Rahul chose under N37 for the
  same reason: the estimate is a lower bound, and calprec2's shards ran
  above their estimates.
  - Both shards use the identical --rows list and --nshards 2
    (notes/RERUN_RUNBOOK.md, "The rule that ties RMAP and ONSET
    together"). Job names: rerun-cal-s0of2-a<A>, rerun-cal-s1of2-a<A>.
  OPEN until both shards have exited 0.
  CLOSED 2026-10-25: both exited 0 ("completed 5616  errors 0  not
  started 0" in each kernel log; K6 lists the folders), and
  rerun_analysis.py's A0 read 5616 complete realizations from each
  (N39).

## Newly found (2026-10-25)

- N39 (result, the fixed-beta rerun analysis). Source: commit 8c9b799,
  run folder runs/rerun-analysis-20261025-051314 (sha256.txt, 9 files),
  console log logs/rerun-analysis-20261025-0513.log. Run by Rahul on the
  laptop. Everything below is copied from the log or the CSVs. No count
  here was made by Claude.
  - Header (rule 18): rerun_analysis sha256 21a26205...67a5; rerun.py
    756c4069...818e, rerunlib.py 5d55050e...9b06, costprobe2.py
    ea5cb2e1...f64b, the hashes N37 and N38 pin; python 3.12.3, numpy
    2.5.3, Linux-7.0.0-38-generic, workers 2; B 10000; plan
    runs/rerun-plan-20261023-112643, rerun_plan.csv sha256
    4aec4b1e...72f2. P1 printed "ok" for all thirteen archived modules.
    The trajectories ran on Kaggle (python 3.13.15, numpy 2.1.3, K6),
    and the analysis ran on the laptop. Both platforms have a recorded
    detcheck PASS in ENVIRONMENT.md.
  - A0: the six shard folders read 4767, 4767, 4767, 4767, 5616 and 5616
    complete realizations. No exit 2.
  - A1, completeness (analysis_completeness.csv; every row "complete",
    present equal to realizations): BETA-ISO 840, BETA-ANI 240, LAWPANEL
    2880, CONC 2160, PROBEARM 2160, ADAPT 1080, TAU8 2160, REFSIZE 144,
    SYNTH 864, NAMED 432, HORIZON 288, GEOM 4032, SIGMA 3456, ANISO
    3456, RMAP 2880, CLIFF 1728, ONSET 2160.
  - Beta source per row (analysis_cells.csv, beta_source): calprec2
    fixed betas in CONC, TAU8, SIGMA and ANISO only; design values in
    BETA-ISO and BETA-ANI; archived rules or probes in the other eleven
    (LAWPANEL visibility B-matching; PROBEARM mechanism probe; ADAPT
    control probe; REFSIZE, SYNTH, NAMED and HORIZON regime probe; GEOM
    law probe; RMAP and ONSET regimemap probe; CLIFF cliff probe).
  - Phase 1: "2451 cell-window instances, 2420 distinct computations, 2
    workers".
  - Margin, 5b (analysis_margin.csv): calprec2 group (SIGMA, ANISO) 576
    cell arms, median SD 0.026582; probe group (RMAP, CLIFF, ONSET) 516
    cell arms, median SD 0.025384; S = 0.026038 over 1092 cell arms; m
    = 3 x S = 0.078113; ratio 1.0472, "no revisit".
  - Finite-J audit, 8.5: "CONC audit: 26 of 30 pooled intervals exclude
    0", "PROBEARM audit: 24 of 30", "TAU8 audit: 64 of 80", "GEOM audit:
    63 of 80" (no PASS/FAIL). All four rows were audited; the log has no
    "F1 FAILED" line. The four CONC intervals that
    contain 0 are all at tau_0 0.5, J 40, 80, 160 and 320. At tau_0
    0.01, J 5000 the pooled d40 - d2 ratio difference is +0.4677
    [+0.3742, +0.5653] (round-1 orientation -0.4677).
  - Onset against 1, J4: per objective 8 of 15 (isotropic), 14 of 15
    (anisotropic), 22 of 30 (both); pooled 2 of 5, 4 of 5, 6 of 10.
  - R^2, L2 (analysis_r2.csv; point values, no interval, no verdict;
    response the cell S-slope on W-full):
    - CONC P3.4: target alone 0.0002 (0.00017713...); + dimension
      0.1005; + objective dummies 0.1316.
    - PROBEARM P3.4: 0.0361; 0.2243; 0.2714.
    - P6.3, SYNTH -> NAMED: M1 in 0.6917, out 0.3432, RMSE out 0.0820;
      M2 in 0.8713, out 0.6741, RMSE 0.0578; M3 in 0.9152, out 0.6157,
      RMSE 0.0628.
  - REFSIZE contrast 5, J_inf 100000 - 12500 on J <= 1250, W-full:
    ackley +0.0530 [-0.0409, +0.1505]; sphere +0.0563 [-0.0540,
    +0.1685]; rosenbrock +0.0086 [-0.0760, +0.0937]; pooled +0.0393
    [-0.0176, +0.0970], k 3, sd_units 0.0266, I2 0.0000, "tau2
    truncated at 0 (s2 0.000707427 < vbar 0.00253616)". Every interval
    contains 0.
  - Summary lines: "statistics written: 6282", "no FLAG", "wall 2945.6
    s   peak RSS (main process) 229.1 MB". Per-worker RSS is not printed.
    No measurement in this run governs a trajectory design (rule 6).
  - Counts. Source: logs/rerun-tally-20261025-0622.log (commit 415a166).
    That is scripts/rerun_tally.py (sha256 0594a212...d5007), run by
    Rahul on the laptop: python 3.12.3, numpy 2.5.3, 2 workers. V1
    printed "ok" for all nine files, and the tally read 3225 cell rows,
    6282 statistic rows, 336 adequacy rows and 7680 audit rows. The full
    table is in the log; what follows is copied from it.
    - C1, rate verdict "upper bound <= -1", W-full, yes of total. A cell
      whose slope is exactly -1 reads "no" about 95% of the time.
      - ADAPT 6 of 72. BETA-ISO 11 of 42. BETA-ANI 5 of 12. LAWPANEL 25
        of 144. CONC 36 of 144. PROBEARM 31 of 144. TAU8 21 of 144.
        GEOM 43 of 336. SYNTH 5 of 72. NAMED 4 of 36. HORIZON 10 of 24.
        REFSIZE 1 of 12.
      - SIGMA isotropic 20 of 144, anisotropic 2 of 144. ANISO isotropic
        11 of 144, anisotropic 6 of 144. RMAP isotropic 19 of 120,
        anisotropic 1 of 120. CLIFF isotropic 19 of 72, anisotropic 0 of
        72. ONSET isotropic 30 of 90, anisotropic 1 of 90.
      - TAU8 by tau_0: 0.3 4, 0.2 4, 0.1 6, 0.07 2, 0.05 2, 0.03 1, 0.02
        0, 0.01 2, each of 18.
      - CONC by tau_0: 0.5 7, 0.1 13, 0.01 16, each of 48.
      - PROBEARM by tau_0: 0.5 9, 0.1 11, 0.01 11, each of 48.
      - ADAPT: fixed 0.1 2, fixed 0.01 1, adaptive 0.1 3, adaptive 0.01
        0, each of 18.
      - HORIZON by T: 0.5 2, 1.0 4, 2.0 4, each of 8.
      - REFSIZE: one "yes", at J_inf 50000; none at 12500, 25000 or
        100000.
      - SYNTH: tau_0 0.1 5 of 36, 0.01 0 of 36. NAMED: 0.1 3 of 18, 0.01
        1 of 18.
    - C2, by region (r < 1 admissible, r = 1 boundary, r > 1 outside),
      yes of total:
      - ONSET isotropic 6 of 15, 6 of 15, 18 of 60; anisotropic 1 of 15,
        0 of 15, 0 of 60.
      - RMAP isotropic 4 of 24, 5 of 24, 10 of 72; anisotropic 1 of 24,
        0 of 24, 0 of 72.
      - CLIFF isotropic 5 of 16, 3 of 8, 11 of 48; anisotropic 0 of 16,
        0 of 8, 0 of 48.
      - SIGMA admissible only: isotropic 20 of 144, anisotropic 2 of 144.
      - ANISO arm B (admissible): isotropic 7 of 72, anisotropic 3 of 72.
        Arm A (no r): isotropic 4 of 72, anisotropic 3 of 72.
    - C3: no cell row in any window has M below full, a nonfinite count
      above 0 or a flag.
    - C4, selected (pooled unless stated, W-full):
      - CONC c1: 1 of 3 pooled DIFFERENCE, 13 of 36 per unit.
      - CONC REGF b_dtau: pooled DIFFERENCE; 7 of 12 units.
      - TAU8 c1: 7 of 8 pooled. GEOM c1: 6 of 8 pooled.
      - ONSET c3: 28 of 30 pooled, 64 of 90 per unit. RMAP c3: 29 of
        40 pooled. SIGMA c3: 26 of 36. ANISO c3: 18 of 36. CLIFF c3: 15
        of 18.
      - RMAP panel b3: 1 of 4 pooled, 3 of 12 units. b1: 4 of 4 pooled,
        11 of 12 units. b2: 3 of 4 pooled, 8 of 12 units.
      - SIGMA A2: 9 of 12 pooled, 19 of 48 units.
      - ONSET severity S(1,3): 10 of 10 pooled; trend 1 of 2 pooled.
      - ONSET c6: 1 of 2 pooled, 0 of 6 units.
      - REFSIZE c5: 0 of 1 pooled, 0 of 3 units.
      - Audit per unit: CONC 203 of 360, PROBEARM 173 of 360, TAU8 261
        of 480, GEOM 462 of 1120.
    - C5, equivalence (c3 per unit, W-full), EQUIVALENT / not
      attainable / not established:
      - SIGMA 48 / 9 / 87 of 144 (d 5: 14 / 7 / 27; d 10: 17 / 0 / 31;
        d 40: 17 / 2 / 29).
      - ANISO 73 / 6 / 65 of 144 (d 5: 23 / 4 / 21; d 10: 30 / 1 / 17;
        d 40: 20 / 1 / 27).
      - RMAP 13 / 28 / 79 of 120. CLIFF 8 / 17 / 47 of 72. ONSET 6 / 19
        / 65 of 90.
    - C6, reference adequacy, calprec2 cells (label as printed):
      - mechanism (CONC): target adequate 137 of 137; "beta, not
        adequate (C5m FAIL)" 4; "beta, not adequate (C5m FAIL, D1 FAIL)"
        3.
      - boundary (TAU8): target adequate 130; C5m FAIL 8; C5m and D1
        FAIL 6.
      - crossed (ANISO): target adequate 21; C5m FAIL 1; C5m and D1 FAIL
        2.
      - sigma (SIGMA): target adequate 21; C5m FAIL 1; C5m and D1 FAIL
        2.
    - C7, audit floor flags: CONC 192 of 1440, PROBEARM 192 of 1440,
      TAU8 198 of 1440, GEOM 462 of 3360.
    - Correction to C6 (2026-10-26, criteria CAL5). "target adequate"
      above counts every target cell, including those whose beta is
      beta_adq under calprec2's BA rule (provenance "beta_adq; C1 found no
      sufficient level" or "beta_adq; C6 failed for beta_prod"). The
      336-cell table has such cells in all four modules. The split by
      label and provenance, per calibrated row, is printed by the
      twenty-row analysis (analysis_adequacy_split.csv) and is copied
      here from its log when it has run. No count is filled in before
      then.
      - Filled 2026-10-28 from logs/rerun-analysis20-20261027.log, block
        "CAL5" (the same counts are in
        runs/rerun-analysis-20261027-185918/analysis_adequacy_split.csv).
        Cells per row, label | provenance:
        - CONC: target | beta_prod 125; target | beta_adq; C1 found no
          sufficient level 11; target | beta_adq; C6 failed for beta_prod
          1; beta C5m FAIL 4; beta C5m and D1 FAIL 3.
        - TAU8: beta_prod 107; C1 found no sufficient level 21; C6 failed
          for beta_prod 2; beta C5m FAIL 8; beta C5m and D1 FAIL 6.
        - SIGMA: beta_prod 15; C1 found no sufficient level 6; beta C5m
          FAIL 1; beta C5m and D1 FAIL 2.
        - ANISO: beta_prod 16; C1 found no sufficient level 5; beta C5m
          FAIL 1; beta C5m and D1 FAIL 2.
        "target adequate" in C6 above is therefore not "production beta"
        in any of the four rows. The manuscript reports the split, not
        the C6 line alone (CAL5, report and do not flag).
  - Observation, not decided (Claude, from the archive source).
    regime.fit_predict (zenodo-v1/regime.py lines 409 to 422) standardizes
    the features but takes no log of covtr, disp, fvar or dist0, the
    geometry features M3 adds (lines 451 to 453), and checks no support.
    Supplementary S3 names that defect for a predictive model ("without
    log-transforming scale features or checking support"). The rerun
    imports the function unchanged (ANALYSIS_CRITERIA.md Q1), so M3's
    R^2 out carries the same property. Whether S3's item is this
    function, I do not know. Neither zenodo-v1 nor round1-zip has a file
    containing "P6.3" other than regime.py itself, so no round-1 console
    log of it is available. The lines quoted are identical in both copies
    of regime.py. Rahul to decide whether M3 is reported as is, with the
    property stated, or not at all.
  OPEN until the manuscript text that uses these numbers is written and
  verified by the rule-8 diff. The tally is recorded above.

- N40 (defect, design; found 2026-10-25). CONC and PROBEARM are not
  seed-paired. N17 (Rahul, 2026-10-10) decided that the probe arm "runs
  with the same seed key as its fixed-beta counterpart", so that the
  probe-versus-fixed difference becomes a measured, paired one. R7's
  disposition rests on that. The approved key layout
  (notes/ANALYSIS_CRITERIA.md, seed-key layout, field 3) puts the owner
  row's index in the key, and says CONC and PROBEARM "are not the same
  experiment, and are not shared". The run follows the layout.
  - Evidence: in the shard CSVs, ackley, d 2, centred, tau_0 0.5, rep 0
    carries seed_key 20261016-81-3-2-0-2-0-500000-... in CONC and
    20261016-81-4-2-0-2-0-500000-... in PROBEARM. Field 3 differs (3
    against 4) and the rest agree. One cell was read; the layout implies
    every cell.
  - No CONC-against-PROBEARM contrast was pre-registered in
    rerun_analysis.py, and none was computed.
  - Consequence: there is no paired measurement of the probe-versus-fixed
    difference. Any comparison of CONC with PROBEARM is between
    independent replications, which is what referee point 7 objects to.
  - Decision needed (Rahul): either drop the comparison, or report it as
    unpaired with an interval for the difference of independent arms,
    pre-registered before it is computed. A paired version would need a
    new probe arm run with CONC's keys.
  OPEN.

- N41 (scope proposal, 2026-10-25; Rahul's instruction to calibrate the
  diffusion rows, "a diffusion comparison on probe beta hands the
  referee back point 5"). Calibrate RMAP, ONSET and CLIFF with calprec2
  and rerun their trajectories on those fixed betas. This reverses N27's
  exclusion of the three rows. Nothing has run.
  - scripts/calprec2.py extended (docstring "SCOPE EXTENSION
    2026-10-25"). --rows accepts RMAP, ONSET and CLIFF; the default
    selection is still the four N27 rows. Keys carry the module code, so
    no key of the four calibrated rows changes. V0(b) checks the new rows
    against Table 2, and V2 has the regimemap and cliff sampler lines
    (regimemap.py 202, cliff.py 178). The file's hash changes;
    calprec2_hashaudit pins records to their launch commits, so the
    audited shards are unaffected.
  - Measured, usable for the projection: costprobe2's trajectory walls
    and peak RSS for every unit of RMAP, ONSET and CLIFF (N22). Peak RSS
    of every rerun unit is at most 354.2 MB (rerun.py docstring, from
    runs/costprobe2-finalize-20261011-101659).
  - Not measured: calprec2 unit costs (t_draw, t_solve, t_beta) for the
    regimemap and cliff modules at any d, and for d = 20 and d = 80 in
    any module. Without them the plan has no estimate for those cells. A
    smoke over the three rows measures them, with per-unit peak RSS. The
    64M held peak (N25, 2472.8 MB) is a d = 40 measurement. Values are
    chunked by 250000 points, so d should enter only through the chunk;
    that is a reading of the code, not a measurement.
  - The trajectory rerun on calibrated betas needs new row definitions
    in costprobe2, rerunlib, rerun.py and rerun_analysis.py. They are not
    written. That changes pinned files, so the analysis of the existing
    seventeen rows stays reproducible only at its own commit (8c9b799).
    The design of that change is for Rahul to approve after the
    projections.
  OPEN until the projections are read and Rahul decides.
  - Projections, read 2026-10-25 (commit b50af47):
    logs/calprec2-plan-ext-thr-20261025-0715.log and
    logs/calprec2-plan-ext-s30000-20261025-0715.log.
    - Header: script sha256 3947d7ba...e511a; throughput
      runs/calprec2-smoke-ext-kaggle-20261025-065222, whose kernel log
      printed python 3.13.15, numpy 2.1.3, bundle d65d7355adcc0649 "51
      files verified" and the same script sha256.
    - V0, V1 and V2 PASS. Cells: cliff 8, regimemap 33, total 41.
    - "best case (no cell adequate) 53920 s   worst-case estimate (every
      cell adequate) 93365 s   at 4 workers"; "largest single task,
      estimated 1779 s" (regimemap rastrigin d 80).
    - Shard counts: "at the target (10800 s): smallest --nshards 15
      largest shard 10272 s = 47.6% of 21600 s"; "at the full ceiling
      (21600 s): smallest --nshards 5   largest shard 20612 s = 95.4%".
    - G-STOP: TIMEOUT_S 8897 s. At --stop-after 36000 the sum is 44897 s,
      "REFUSE". At --stop-after 30000 it is 38897 s, "PASS", margin 4303 s.
    - Smoke peak RSS at 4M (calprec2_throughput.csv): regimemap rastrigin
      374.2 MB at d 40 and 679.4 MB at d 80; ackley 299.7 and 528.7;
      sphere 220.9 and 373.5. d enters the peak beyond the chunk, so N25's
      64M figure (d 40) does not cover d 80 (N42).
  - Result, 2026-10-26: the calprec2-ext queue (N42) ran to DONE.
    Sources: the fifteen shard folders runs/calprec2-ext-s<S>of15-a1-
    kaggle-*, the finalize folder
    runs/calprec2-ext-finalize-a2-kaggle-20261026-204714 (sha256.txt
    verified by Claude with sha256sum -c, two files OK), its kernel log
    and its calprec2_beta.csv (sha256 2783222b...e6adb3).
    - Every shard: attempt a1, runner exit 0, no resume. Rows read by the
      finalize ("read" lines, every row complete): s0 494, s1 500, s2
      507, s3 500, s4 500, s5 500, s6 507, s7 507, s8 494, s9 481, s10
      487, s11 338, s12 331, s13 325, s14 318. The finalize header:
      "FINALIZE  6789 rows, 41 cells expected".
    - Finalize header: python 3.13.15, numpy 2.1.3, script sha256
      3947d7ba...e511a, costprobe2.py sha256 ea5cb2e1...f64b, mode
      finalize rows RMAP,CLIFF,ONSET, bundle a2acdd5234024989 "127 files
      verified"; V1, V0 and V2 PASS; cells "cliff 8", "regimemap 33",
      "total 41". The header's "workers 2" and "--stop-after 36000" are
      the script's defaults; finalize evolves nothing and applies
      --stop-after in full mode only (the header says so).
    - Finalize counts, as printed: "beta 7", "target 34", "adequate 34",
      "not adequate (C5m FAIL) 4", "not adequate (C5m FAIL, D1 FAIL) 3".
      The table has 41 rows, 41 distinct cells, law centred throughout,
      flags empty throughout.
    - The seven beta-labelled cells. Each reference is at 256M, and
      provenance is "beta_adq; reference not adequate". Values are copied
      from calprec2_beta.csv; the thresholds printed in the header are C5m
      <= 0.054682 and D1 <= 0.025.
      - cliff ackley d 10 tau0 0.1: C5m FAIL; beta 2.156446757379671,
        C5m 0.072804, D1 0.004777.
      - regimemap ackley d 10 tau0 0.01: C5m FAIL, D1 FAIL; beta
        2.97022812927044, C5m 0.232261, D1 0.071867.
      - regimemap ackley d 10 tau0 0.03: C5m FAIL, D1 FAIL; beta
        2.642023441647725, C5m 0.104912, D1 0.047283.
      - regimemap ackley d 40 tau0 0.01: C5m FAIL, D1 FAIL; beta
        6.072471132304663, C5m 0.178233, D1 0.027953.
      - regimemap ackley d 40 tau0 0.03: C5m FAIL; beta 5.17711087320572,
        C5m 0.065455, D1 0.013074.
      - regimemap rastrigin d 40 tau0 0.01: C5m FAIL; beta
        0.049901042257534715, C5m 0.214455, D1 0.010541.
      - regimemap rastrigin d 40 tau0 0.03: C5m FAIL; beta
        0.042876230428251914, C5m 0.081208, D1 0.004416.
    - Seven target-labelled, adequate cells have provenance "beta_adq; C1
      found no sufficient level": their beta is the adequacy beta, not a
      production-level beta. "target 34" above includes them (CAL5: the
      split per row comes from the twenty-row analysis). They are cliff ackley d 40 tau0 0.1;
      regimemap ackley d 10, 20 and 80 at tau0 0.1; regimemap rastrigin
      d 10 tau0 0.01 and d 80 tau0 0.1; regimemap sphere d 40 tau0 0.01.
      Every other target cell has provenance "beta_prod, calibration
      N_cell <n>". This is a record, not a finding; how the
      analysis treats these cells belongs to the criteria amendment
      (N42).
    - Split per calibrated row, 2026-10-28 (CAL5; logs/rerun-analysis20-
      20261027.log, block "CAL5"), cells, label | provenance:
      - RMAP-CAL: target | beta_prod 15; target | beta_adq; C1 found no
        sufficient level 3; beta C5m FAIL 3; beta C5m and D1 FAIL 3.
      - CLIFF-CAL: beta_prod 6; C1 found no sufficient level 1; beta C5m
        FAIL 1.
      - ONSET-CAL: beta_prod 11; C1 found no sufficient level 4. No
        beta-labelled cell.
      These are per row. RMAP-CAL and ONSET-CAL share the regimemap cells
      at tau0 0.1, d 10 and d 40, so the RMAP-CAL and ONSET-CAL counts are
      not a partition of the 33 regimemap cells and are not to be added.
  CLOSED 2026-10-26 as to the calibration. The trajectory rerun on these
  betas is N42's.

- N42 (design, 2026-10-25; Rahul's instructions of 2026-10-25: choose the
  shard count, extend the queue to calprec2, write the calibrated-row
  changes). Nothing below has run.
  - Shard count: 15 at the 10800 s target, --stop-after 30000 for every
    shard (Claude's recommendation; Rahul to approve). Reason: the
    estimate assumes perfect scaling and ignores barrier idle and phase
    tails. The project's measured overruns of comparable estimates reach
    16255.0 s against 12596 s (arch-s1of4, K6), and calprec2's long shards
    ran over theirs (N37). At 5 shards the estimate already takes 95.4% of
    the ceiling, so the margin the ceiling exists to provide is gone
    before any of that. At 15 a shard can run at more than twice its
    estimate before reaching 21600 s. What 15 costs is ten more launches,
    and runtime is not a constraint (rule 6).
  - Before the queue: scripts/memprobe.py extended (--module, --objective,
    --d, --tau; the defaults are N25's cell). It measures the 64M peak for
    regimemap rastrigin d 80, the largest 4M peak of the smoke, on Kaggle.
    The queue is not loaded until that peak is read against the 3072 MB
    budget.
  - rerunq.py, schema 2 (docstring "SCHEMA 2 AND THE CALPREC2 FAMILY").
    Profiles; a calprec2 family with shard and finalize items; P1C, R1C,
    F2C, R2C, FIN, R1F and F2F; and "load", which archives a DONE state and
    starts a committed definition. L1 to L5, F1, R2's exit handling and K1
    are unchanged. R1 itself does not apply to calprec2 jobs: its regexes,
    hashes, plan sha256, modes and run-dir names are rerun.py's. R1C and
    R1F are its calprec2 equivalents, read from what calprec2.py prints:
    - the header after its banner;
    - "files  <dir>" with calprec2-full-<stamp>-s<S>of<K>;
    - calprec2_params.csv;
    - the rule-17 line "read <folder>: shard S of K, N rows, M complete",
      which calprec2's read_folders already prints, so calprec2.py is not
      changed.
    Definition: notes/queues/calprec2-ext.json, with 15 shards and the
    finalize. CLAUDE.md rule 22 amended with it.
  - kgrun.py: the runner now rewrites "runs/<name>" inside comma-joined
    --args tokens too. calprec2's --finalize takes "runs/A,runs/B", which
    the whole-token rule could not ship. A token without a comma is
    handled exactly as before.
  - Calibrated r rows: rerunlib.py and rerun.py (docstrings "CALIBRATED r
    ROWS" and "N42 AMENDMENTS"):
    - RMAP-CAL, CLIFF-CAL and ONSET-CAL are appended after the seventeen
      rows, so every existing key is unchanged;
    - their betas come from calprec2, and their sigma is checked against
      the base row's archive file;
    - K4's expected sharing is a list per share key;
    - --calprec2 accepts several tables;
    - the new K5 (--same-as PLAN) requires the old plan's rows to reappear
      unchanged.
  - costprobe2.py is NOT changed, although the instruction named it. It is
    pinned inside calprec2: its sha256 is in every calprec2 header and in
    calprec2_params.csv, which resume and finalize compare. The 17-row plan
    pins it too. Editing it would break the calibration this queue runs and
    the 17-row plan at once. The three rows live in rerunlib instead.
  - rerun_analysis.py: a guard only. It exits 2 while rerunlib defines rows
    it has no criteria for. The criteria for the new rows are an amendment
    to notes/ANALYSIS_CRITERIA.md, for Rahul to decide:
    - the margin: keep m = 0.078113 or recompute;
    - which contrasts the -CAL rows get;
    - no probe-against-calibrated comparison (N40);
    - the sensitivity analysis without the not-adequate cells;
    - A1 over twenty rows.
  - Pins this breaks, and what keeps the 17-row result verifiable:
    - rerunlib.py (5d55050e...9b06), rerun.py (756c4069...818e) and
      rerun_analysis.py (21a26205...67a5) change. At HEAD, rerun.py and
      rerun_analysis.py refuse runs/rerun-plan-20261023-112643, because
      its recorded rerunlib hash differs; the analysis also refuses
      through the guard.
    - calprec2.py (3947d7ba..., unchanged since 5864729) and costprobe2.py
      (ea5cb2e1...f64b) do not change.
    - The 17-row result is reproduced at commit 8c9b799 in a git worktree,
      with the same .venv (Python 3.12.3, NumPy 2.5.3). The check is
      "sha256sum -c" of the new folder against the committed
      runs/rerun-analysis-20261025-051314/sha256.txt. Byte-identical is
      the criterion; any difference is a finding.
    - The run folders and the plan never change, and the trajectories are
      not rerun: the 26 calprec2 shards are pinned to their launch commits
      (K7) and the rerun shards to their recorded hashes (K6).
    - The new 20-row plan must pass K5 against the old one. That makes the
      old shard folders valid task by task under it, which a combined
      analysis needs.
  OPEN until the memprobe peak is read, the reproduction passes, Rahul
  approves the shard count, and the queue runs.
  - The calprec2 queue ran to DONE on 2026-10-26 (N41, result).
  - Twenty-row precheck, 2026-10-26. Source:
    logs/rerun-precheck3-20261026.log; plan runs/rerun-plan-20261026-210435
    (commit e6d891f), whose manifest Claude verified with sha256sum -c
    (four files OK).
    - Header: rerun.py de28b69a...aca1, rerunlib.py 6a7ddf42...5b07,
      costprobe2.py ea5cb2e1...f64b; python 3.12.3, numpy 2.5.3, Linux
      laptop, workers 2.
    - Tables read: runs/calprec2-finalize-20261023-112503, sha256
      0fc98d23...2668, 336 cells; the N41 table, sha256 2783222b...e6adb3,
      41 cells; "merged calprec2 cells 377".
    - O1 PASS; "archive check: 2598 ok, 0 FAIL, 288 not applicable";
      "K4 PASS (52 groups with more than one row)"; "K1 PASS (26844
      distinct (group, rep) keys)"; K2 PASS.
    - K5: "old plan runs/rerun-plan-20261023-112643/rerun_plan.csv: 1752
      rows over 17 row names; new plan has 1752 rows of those names",
      "K5 PASS". The completed seventeen-row shard folders are therefore
      valid task by task under the new plan.
    - PLAN WRITTEN: A, C2, K1, K2, K4 and K5 PASS.
  - Shard count for RMAP-CAL, CLIFF-CAL and ONSET-CAL (decision, Rahul,
    2026-10-26). Source: logs/rerun-schedule-cal3-20261026-2107.log
    (commit 1833708). That is rerun.py --schedule on the laptop for those
    rows, --nshards 1 to 8, --workers 4, against plan
    runs/rerun-plan-20261026-210435 (rerun_plan.csv sha256
    1d9b4031...9c64), with the same script hashes as the precheck;
    nothing was run or written.
    - "tasks 6192"; one shard: summed wall 84845 s, "estimate 21211 s at
      4 workers"; two shards: 3096 tasks each, summed wall 42422 s,
      estimate 10606 s each. All estimates are labelled lower bounds
      (perfect scaling; walls from costprobe2's timing beta).
    - Decision: 2 shards. Rahul's reason: one shard's estimate, 21211 s,
      is 98% of the 21600 s per-shard ceiling (Rahul's figure). The
      estimates assume perfect scaling, and the archived shards overran
      theirs by up to 30% (Rahul's figure; the ledger's largest recorded
      overrun is arch-s1of4, 16255.0 s against its 12596 s estimate, K6).
      Same reasoning as N37 and N38.
    - Both shards use the identical --rows list and --nshards 2, RMAP-CAL
      launched with ONSET-CAL (notes/RERUN_RUNBOOK.md, the rule that ties
      RMAP and ONSET together; the shared cells are owned by RMAP-CAL).
    - Decided by Rahul, 2026-10-26: through the rerun queue, a smoke
      first, as the last two sets ran. The definition is
      notes/queues/rerun-cal3.json (commit 5a94392). Its timing folders
      are runs/costprobe2-s0-kaggle-20261010-103952 and
      runs/costprobe2-s1-kaggle-20261011-101343. Rahul confirmed that his
      schedule run used these two, the same two as every schedule in this
      project.
  - The rerun-cal3 queue ran to DONE (Rahul, 2026-10-27): smoke exit 0;
    runs/rerun-cal3-s0of2-a1-kaggle-20261027-011714 and
    runs/rerun-cal3-s1of2-a1-kaggle-20261027-043215, runner exit 0, each
    kernel log "completed 3096  errors 0  not started 0"; no resume. Timer
    disabled.
  - Result, the twenty-row analysis (CAL1 to CAL5). Source: commit
    91a10de, run folder runs/rerun-analysis-20261027-185918 (sha256.txt,
    13 files, verified by Claude with sha256sum -c), console log
    logs/rerun-analysis20-20261027.log. Run by Rahul on the laptop.
    Everything below is copied from the log or the CSVs.
    - Header: rerun_analysis sha256 b241fe15...fa0a7 (the file committed
      in 5a94392), rerun.py de28b69a...aca1, rerunlib.py 6a7ddf42...5b07,
      costprobe2.py ea5cb2e1...f64b; python 3.12.3, numpy 2.5.3,
      Linux-7.0.0-38-generic, workers 2; B 10000; plan
      runs/rerun-plan-20261026-210435, rerun_plan.csv sha256
      1d9b4031...9c64; reproduce runs/rerun-analysis-20261025-051314,
      "verified against its sha256.txt (9 files)". P1 "ok" for all
      thirteen modules. The CAL4 environment holds.
    - Run folders: the four arch shards, the two cal shards and the two
      cal3 shards. A0 read 4767, 4767, 4767, 4767, 5616, 5616, 3096 and
      3096 complete realizations. No smoke folder was passed.
    - A1: all twenty rows complete; RMAP-CAL 2880, CLIFF-CAL 1728,
      ONSET-CAL 2160, the seventeen as in N39.
    - Margin: identical to N39 (calprec2 576 cell arms, 0.026582; probe
      516, 0.025384; S 0.026038 over 1092; m 0.078113; ratio 1.0472),
      and "margin equals runs/rerun-analysis-20261025-051314's
      analysis_margin.csv, every value as a string (CAL4)".
    - CAL4: all eight files PASS with differences 0 (completeness 17,
      cells 3225, margin 7, stats 6282, onsets 56, audit 7680, r2 9,
      adequacy 336); "17-ROW REPRODUCTION PASS: 8 files, every value of
      every old column equal as a string". The not_adequate column and the
      CAL rows change no seventeen-row value.
    - CAL1 guard: "calibrated r rows: cell arms 516  median SD 0.025827";
      ratio to the calprec2 group 1.0292, to the probe group 1.0174; "no
      revisit". m stays 0.078113 for RMAP-CAL, CLIFF-CAL and ONSET-CAL.
    - CAL3, margin pool: six SIGMA and ANISO cells are not adequate
      (crossed and sigma, ackley d 10 and 40 and rastrigin d 40, all tau0
      0.01). "S and m unchanged".
    - Phase 1, calibrated rows: "342 cell-window instances, 318 distinct
      computations".
    - CAL5: the split is copied into N39 (C6 correction) and N41
      (result).
    - Summary: "statistics written: 7092 (6282 in the seventeen rows)";
      "statistics naming a not-adequate cell: 1012"; "no FLAG"; "wall
      3641.8 s   peak RSS (main process) 235.2 MB".
    - Not yet tallied: the C1 to C7 counts for the three calibrated rows.
      The log prints J4's counts and nothing else of that kind, and
      scripts/rerun_tally.py knows only the seventeen rows (REGION_ROWS).
      No count over the calibrated rows is recorded until a script Rahul
      runs prints it.
    - What the calibrated rows show against N39's probe-beta rows, read
      line by line from the log (Claude, 2026-10-28). The two designs are
      independent replications (N40) and CAL2 forbids a contrast or a
      verdict between them, so this is a side-by-side reading, not a
      test.
      - Contrast 3, ONSET-CAL, pooled, W-full, d 40: positive DIFFERENCE
        at r 0.75 to 1.5; r 2.0 +0.0099 [-0.0291, +0.0467], contains 0;
        r 3.0 -0.1268 [-0.1803, -0.0739], DIFFERENCE. N39's ONSET: r 2.0
        +0.0102 [-0.0256, +0.0437]; r 3.0 -0.1390 [-0.1964, -0.0825].
      - d 80: positive DIFFERENCE at r 0.75 to 1.25; r 1.5 +0.0112
        [-0.0205, +0.0427], contains 0; r 2.0 -0.1424 [-0.1896,
        -0.0977] and r 3.0 -0.1667 [-0.2292, -0.1104], DIFFERENCE. N39:
        r 1.5 +0.0054 [-0.0428, +0.0522]; r 2.0 -0.0845 [-0.1325,
        -0.0375]; r 3.0 -0.2009 [-0.2996, -0.1195].
      - Per objective (order ackley, rastrigin, sphere), in both designs
        rastrigin's gap is positive DIFFERENCE where ackley's and
        sphere's are negative: ONSET-CAL d 40 r 2.0 -0.1039, +0.3770,
        -0.2436; d 80 r 1.5 -0.0775, +0.4023, -0.2912; d 80 r 2.0
        -0.2868, +0.3321, -0.4724. rastrigin turns negative only at d 80
        r 3.0 (-0.2213). ONSET-CAL has no not-adequate cell.
      - A4 holds for both: a sign change across r is not a claim; each
        cell's gap and verdict is reported.
      - Onsets, isotropic, pooled: ONSET-CAL d 5 1.25 [1.25, 2.00]; d 10
        1.00 [1.00, 2.00]; d 20 1.50 [1.25, 2.00]; d 40 1.50 [1.25,
        1.50]; d 80 1.00 [1.00, 1.00]. N39: 1.50 [1.50, 2.00]; 1.25
        [1.00, 2.00]; 1.50 [1.25, 2.00]; 1.25 [1.25, 1.50]; 1.00 [1.00,
        1.25].
      - J4, ONSET-CAL: objective isotropic 9 of 15, anisotropic 13 of
        15, both 22 of 30; pooled 2 of 5, 4 of 5, 6 of 10. N39: 8 of
        15, 14 of 15, 22 of 30; 2 of 5, 4 of 5, 6 of 10.
      - Contrast 6, onset d80 - d5, isotropic pooled: ONSET-CAL -0.2500
        [-1.0000, +0.0000], contains 0; N39 -0.5000 [-1.0000, -0.2500],
        DIFFERENCE. Anisotropic pooled: +0.7500 [-0.5000, +1.0000]; N39
        +0.0000 [-0.7500, +0.7500]. Every per-objective interval
        contains 0 in both.
      - J2, severity S(1,3) trend on log2 d, pooled: isotropic +0.1542
        [+0.1389, +0.1695] (N39 +0.1292 [+0.1148, +0.1432]); anisotropic
        +0.0230 [-0.0032, +0.0501] (N39 -0.0078 [-0.0330, +0.0165]).
        S(1,3) isotropic d 5: +0.0219 [-0.0447, +0.0867], contains 0
        (N39 +0.1357 [+0.0824, +0.1892]).
      - Observation, not decided: at d 80 every isotropic per-objective
        onset is 2.00 [2.00, 2.00], and the pooled onset is 1.00 in both
        designs (H3 pools the mean curve, not the onsets, as the log
        says). Whether that is a property of the fit on averaged curves
        or a defect, I do not know. A check of the pooled curve at d 80
        against the three objectives' curves would settle it.
        scripts/onsetdiag.py (read-only, writes nothing) is that check.
        Its first run crashed before any result
        (logs/onsetdiag-20261028.log, exit 1): read_onsets took every
        row of analysis_onsets.csv for an onset, but onset_block also
        writes 10 heterogeneity rows and 6 J4 count rows (d empty), and
        N39's file has no not_adequate column. Fixed: every row is
        classified by kind, the header and kind counts are checked per
        folder, R1 compares the 40 onset rows only. Not yet rerun.
      - Caveat on every d 80 reading of ONSET-CAL (Rahul, 2026-10-28).
        Two of its three d 80 calibration cells do not carry a
        production beta. From the N41 finalize's calprec2_beta.csv
        (runs/calprec2-ext-finalize-a2-kaggle-20261026-204714):
        regimemap|ackley|80|centred|0.1 and
        regimemap|rastrigin|80|centred|0.1 are label "target",
        provenance "beta_adq; C1 found no sufficient level", adequacy
        "adequate"; regimemap|sphere|80|centred|0.1 is "beta_prod,
        calibration N_cell 1000000". The ackley and rastrigin betas at d 80
        are therefore the adequacy beta: the reference is adequate, but no
        production level met C1. The d 80 contrast-3 gaps, onsets, J4 and
        severity of ONSET-CAL rest on these two cells for two of three
        objectives, and every pooled d 80 figure averages over them. The
        text must say so wherever a d 80 ONSET-CAL number
        appears. CAL3's not_adequate flag does not mark these cells
        (they are adequate), so the log's flags do not show this.
  OPEN until the manuscript text that uses these numbers is written and
  verified by the rule-8 diff, and until the calibrated rows are tallied.

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
- K6 (Kaggle, the rerun queue on GitHub Actions; decision, 2026-10-23).
  The eight jobs of the fixed-beta rerun are driven from GitHub Actions so
  that nothing on the laptop has to stay awake. A Kaggle shard takes three
  to twelve hours and an Actions job is capped at six, so the driver does
  not wait for a job. It is a scheduled workflow: every 15 minutes one
  tick reads committed state, takes at most one action and exits.
  - Files: .github/workflows/rerun-queue.yml; scripts/rerunq.py (its
    docstring carries every decision rule, each with a worked example);
    notes/rerun_queue.json (the state and the lock); a new kgrun.py
    subcommand, launch, which is run without poll and fetch. kgrun's bundle
    now leaves out rerunq.py as it leaves out kgrun.py.
  - Queue: smoke (13 archived-beta rows); archived-beta shards 0 to 3 of
    4 (N37); smoke (CONC, TAU8, SIGMA, ANISO); calibrated shards 0 and 1
    of 2 (N38). Both sets use runs/rerun-plan-20261023-112643. N35's
    comparison found its archived-beta rows identical to the first plan's,
    and the analysis runs against this plan.
  - Halts on: runner exit 2, 3 or 4, or no runner exit line; a smoke
    without D-SMOKE PASS; a header that is not the pinned Python, NumPy,
    script hashes and plan; a manifest mismatch or an incomplete
    download; a kgrun exit other than 0; a push failure after a Kaggle
    side effect; the same unclassifiable observation twice for one job; a
    G-STOP with no progress; a fifth attempt. Exit 5 relaunches the same
    shard as attempt A + 1, resuming from every earlier attempt folder.
  - Rule changes, made in CLAUDE.md with this entry: rules 3, 14 and 21
    each gain one exception, and rule 22 is new. The Kaggle key is stored as
    an Actions secret. The workflow, not Rahul, launches and commits the
    queue's jobs. The state file is rewritten in place.
  - Kernel check (rule K1, at Rahul's request): "release --mode
    next-attempt" is refused unless the halted job's kernel status was
    checked since the halt, by "rerunq.py check" or by Rahul with
    --checked-by-hand. That closes the review's residual double-launch
    risk. Edit(/notes/rerun_queue.json) is denied to Claude in
    .claude/settings.json.
  - Status reply for a kernel that does not exist, measured by Rahul on
    the laptop on 2026-10-23 with kaggle 2.2.4 (requirements.lock), from
    kgrun status --job rerun-smoke-arch-a1, as he pasted it (the "..." is
    his elision; the full text is not yet stored under logs/):
      Cannot access kernel 'ericsom/cbo-rerun-smoke-arch-a1' (Permission
      'kernels.get' was denied). The most likely cause is a wrong kernel
      slug. ... It can also occur if the notebook is private.
    There is no "404" in it. This replaces the first draft's assumption
    that the reply contains "404", which was wrong: under it the first
    launch would have halted on its second tick. The reply, by its own
    wording, covers both "no such kernel" and "exists but not readable",
    and the CLI gives no way to tell them apart from that reply alone.
    L4 now counts it as ABSENT only when a status request for a private
    kernel of the same account that is known to exist
    (calprec2-long-s25of26-a1), made in the same tick right after it,
    succeeds. That shows the key is a working key of ericsom, whose own
    private kernels it has always been able to read. A denial with a
    failing control (an expired, revoked or wrong-account key) is UNKNOWN,
    never ABSENT.
  - Review: notes/RERUNQ_REVIEW.md. Nothing of this has run. Not known
    until the first ticks: whether GITHUB_TOKEN may disable the workflow
    and push to main (Rahul has set workflow permissions to read and
    write, and there are no branch rules); what the CLI prints for an
    expired or revoked key (L4 does not depend on it).
  - First scheduled tick, run 39960530374.1, 2026-10-23 18:51 IST
    (logs/rerunq-rerun-smoke-arch-a1-anomaly-20261023-185159.log, commit
    a647085): anomaly preflight-status, nothing launched. The target
    rerun-smoke-arch-a1 was denied, and the control
    calprec2-long-s25of26-a1 was denied too: the log line "kaggle status
    of ericsom/cbo-calprec2-long-s25of26-a1: DENIED" is printed only when
    the denial pattern matched with exactly the control's kernel id. The
    same request from the laptop returns COMPLETE
    (logs/kgrun-status-control-20261023.log). So the parser did not miss a
    status line; on Actions the kaggle CLI was refused the control, which
    is L4's "wrong-account, expired or revoked key" case, and L4 did what
    it was written to do. The anomaly detail quoted "(==...==)" because
    raw_status reported the last non-blank line of kgrun's output, which
    is kgrun's closing banner. Both streams were read (kgrun merges the
    CLI's stderr into its stdout; rerunq merges kgrun's), and the status
    pattern scans every line, not the last. Fixed in scripts/rerunq.py:
    every line kgrun status prints now goes into the tick log, and the
    detail quotes the judged line (status line, else the denial line,
    else the CLI's reply between kgrun's echo and banner). Which of the
    three key failures it is, and whether the secrets KAGGLE_USERNAME
    and KAGGLE_KEY are ericsom's current key, is not known from this log:
    the raw CLI text of that tick was not recorded.
  - Cause, found by Rahul on the laptop the same day (reported by him; no
    console log of it is stored under logs/): with ~/.kaggle/access_token
    moved aside, kgrun status for the control is refused on the laptop
    exactly as on Actions. Every Kaggle call of this project, by kgrun and
    by hand, has authenticated through ~/.kaggle/access_token, not through
    kaggle.json; this was never written down before. The workflow wrote
    only kaggle.json. Fixed: a third secret, KAGGLE_ACCESS_TOKEN, stored
    from the laptop's file; the workflow's credentials step writes
    ~/.kaggle/access_token from it with mode 600 beside kaggle.json,
    prints only each file's name and mode, and the last step removes both.
    CLAUDE.md rule 14, the rerunq.py and kgrun.py docstrings and
    notes/RERUNQ_REVIEW.md updated to match. Not yet confirmed on Actions:
    the next tick must show the denial for rerun-smoke-arch-a1, the
    control's COMPLETE, then "L3: kernel absent on Kaggle, name unused".
  - Scheduled ticks never fired (2026-10-23; read by Claude through the
    GitHub API with gh). The workflow was created 12:37Z (02d071c). Its
    whole run history is three workflow_dispatch runs started by Rahul:
    13:18Z (failed, disabled itself), 13:21Z (anomaly), 13:51Z (launch).
    No run has event "schedule". The workflow's state last changed at
    13:50:59Z (Rahul's re-enable) and read "active" at 14:31Z. So the
    14:00, 14:15 and 14:30 slots were missed while it was certainly
    enabled, and 12:45, 13:00 and 13:15 too if it was enabled on creation.
    Ruled out:
    - the workflow file: on main, the default branch; the trigger parses
      as schedule "*/15 * * * *" plus workflow_dispatch; last changed in
      7ec761f, pushed by Rahul;
    - the repository: private, not a fork, not archived (the 60-day
      inactivity rule is for public repositories only);
    - Actions availability: the manual runs start and finish;
    - a reported outage: githubstatus.com's history for 22 and 23
      October lists no incident covering 12:37Z to 14:31Z, and none that
      names scheduled workflows.
    Documented factors that might fit, neither established. GitHub's
    documentation says the schedule event "can be delayed during
    periods of high loads", "High load times include the start of every
    hour", and "some queued jobs may be dropped"; every slot of */15
    falls on a quarter-hour. It also says a deactivated scheduled
    workflow is reactivated by a commit that changes its cron line,
    without saying what deactivates one.
    The cause is not established either way.
  - Schedule test, Rahul's decision 2026-10-23. In this commit the cron
    line becomes "7,22,37,52 * * * *". That is still every 15 minutes,
    off the quarter-hours, and it is a commit changing the cron line.
    Stated prediction, fixed before the result: if at least one run with
    event "schedule" appears within 60 minutes of this commit's push,
    the cause was the quarter-hour load or a dormant schedule. The test
    cannot tell those two apart, since the one commit changes both. If
    none appears, the cause is a question for GitHub Support, and the
    queue runs on manual ticks (gh workflow run rerun-queue.yml) until it
    is answered. The workflow must be enabled during the hour for the
    test to mean anything. The scheduled tick's own action is
    unaffected: it reads the committed state like any tick.
    Interim observation, not the result: Rahul's run list at 14:40:41Z
    (date -u in his paste; the list was pasted in summary form) shows
    the three workflow_dispatch runs only, so the 14:37Z slot produced no
    scheduled run. Claude's own read at 14:41:35Z (gh api
    repos/.../actions/runs) agrees: total_count 3 for the whole
    repository, and 0 runs with event=schedule of any status. The 14:52,
    15:07 and 15:22Z slots remain, and GitHub's documentation allows
    for delay.
    Also read at 14:41Z through the API. Actions is enabled for the
    repository, allowed_actions "all", default workflow permissions
    "write". It is the only workflow in the repository, state "active".
    No commit message in the history holds a skip-CI marker. The
    account's billing usage could not be read with the CLI's token
    scopes.
    Result, 2026-10-23: the prediction's second branch. Rahul's run list
    at 15:52:22Z (date -u in his paste; the list pasted in summary form),
    past the 15:34:40Z deadline, shows the three workflow_dispatch runs
    only, with "gh workflow list" giving rerun-queue active 394021389.
    So none of the four slots in the window (14:37, 14:52, 15:07,
    15:22Z) produced a scheduled run. Claude's own read at 16:00:21Z
    agrees: the same three runs, 0 runs with event=schedule, workflow
    active. The workflow read active at every check (14:31, 14:41Z by
    Claude; 15:52Z by Rahul; 16:00Z by Claude). Nothing shows it
    disabled in between, but the API keeps no state history.
    Consequences, Rahul's decision:
    - the off-peak cron and a reactivation by a commit changing the cron
      line are both ruled out as the fix;
    - the cause is not established; it is a question for GitHub Support;
    - until it is answered, the queue runs on manual ticks
      (gh workflow run rerun-queue.yml).
    The cron line "7,22,37,52 * * * *" stays; it does no harm.
  - Conclusion under review, 2026-10-23, after the result above. Two of
    Rahul's other private repositories have working scheduled workflows,
    racma (orchestrator.yml) and rbudget (rbudget_kaggle.yml; cron
    "*/15 * * * *", the same line rerun-queue had). Claude read their run
    lists through the API. Neither fires at its cron interval: their
    scheduled runs come hours apart, and each first scheduled run came
    hours after its workflow was created. If that holds, a 60-minute
    window was not a fair test. "No scheduled run within 60 minutes" is
    what a working schedule on this account also shows, and the
    referral to GitHub Support above is premature. The figures enter
    this entry only from logs/gh-schedule-cadence-20261023.log, run by
    Rahul. Not established: whether disabling and re-enabling a workflow
    restarts the delay before its first scheduled run. rerun-queue's
    longest continuously enabled stretch before its halt at about 16:02Z
    began with the 13:50:59Z re-enable.
  - Why the 60-minute test was not a fair test, from
    logs/gh-schedule-cadence-20261023.log (read at 2026-10-23T16:16:05Z,
    Rahul's run).
    - racma: 34 scheduled runs; first run 175 min after the workflow was
      created; gap minutes min 127, median 273, max 486 (n 33).
    - rbudget, with the same cron line "*/15 * * * *": 42 scheduled runs;
      first run 156 min after creation; gap minutes min 103, median 248,
      max 435 (n 41).
    - cbo-gap-final: 0 scheduled runs; rerun-queue.yml disabled_manually,
      updated 2026-10-23T21:31:47+05:30 (the halt of tick 39983265158).
    On this account, a working private-repository schedule fires hours
    apart whatever its cron line, and its first run came 156 to 175
    minutes after creation. A 60-minute window is shorter than the
    shortest gap measured (103 min). rerun-queue's longest continuously
    enabled stretch before the halt ran from 13:50:59Z (the re-enable,
    from the API's updated_at) to 16:01:47Z (the halt's disable). That
    is shorter than either first-run delay. The test's result line
    above stands as an observation. Its conclusion, a referral to GitHub
    Support, is withdrawn as premature. Whether rerun-queue's schedule
    fires is untested: it needs the workflow left enabled for longer than
    486 minutes.
  - Dispatcher, Rahul's decision 2026-10-23: cron-job.org POSTs a
    workflow_dispatch to rerun-queue.yml every 15 minutes, so ticks do
    not depend on GitHub's schedule. CLAUDE.md rule 22 amended.
    - Request: POST
      https://api.github.com/repos/rahul-k-mishra/cbo-gap-final/actions/workflows/rerun-queue.yml/dispatches,
      body {"ref":"main"}; headers Accept application/vnd.github+json,
      Authorization Bearer <token>, X-GitHub-Api-Version 2022-11-28,
      Content-Type application/json. Any 2xx is success.
    - Token: fine-grained personal access token. Resource owner
      rahul-k-mishra, only the repository cbo-gap-final, repository
      permission Actions read and write (Metadata read is added by
      GitHub), nothing else, with an expiry. GitHub's permission table
      lists the dispatch endpoint under Actions (write). Actions write
      also allows enabling and disabling workflows, cancelling,
      re-running and deleting runs, and deleting logs, artifacts and
      caches. It gives no access to repository contents or secrets.
      Stored only in cron-job.org; Claude never sees it.
    - Halts: a halt disables the workflow. A dispatch to a disabled
      workflow starts no run; GitHub's reference page does not document
      the error it returns, which the first halt will show in
      cron-job.org's history. Re-enabling by any means, including a
      leaked token, cannot continue past a halt, because the tick reads
      HALTED from the committed state, exits 3 and disables the workflow
      again. Not verified: whether cron-job.org disables a job after
      repeated failures. Its job settings say.
    - Double launch: the workflow's concurrency group (rerun-queue,
      cancel-in-progress false) keeps one run executing and at most one
      pending, a newer pending run cancelling an older one (GitHub's
      concurrency documentation, queue single). Scheduled and dispatched
      runs share the group. A pending run checks out main's tip when it
      starts (checkout ref main), so it reads the state the previous tick
      committed. Independently of the group, L1 and L2 cover it: the
      LAUNCHING intent is committed and pushed before kgrun launch; a
      tick whose push is rejected because the state on main changed
      reports "lock lost" and launches nothing; L3 refuses a kernel name
      already on Kaggle or in runs/; F1 refuses a second fetch folder.
    - Cost: every tick is a billed Actions run on a private repository,
      at least one minute each, so a 15-minute dispatch is at least 96
      billed minutes a day, more on launch and fetch ticks. That comes
      out of the same account allowance as racma and rbudget. Exhausted
      minutes make runs fail, and a failed run disables the workflow: the
      queue stops safely, it does not misbehave.
    - Fallbacks: if the token expires or cron-job.org stops, GitHub's own
      schedule, if it fires, still ticks hours apart, and a manual
      "gh workflow run rerun-queue.yml" always works.
  - Laptop driver, Rahul's decision 2026-10-23. GitHub's schedule has
    still never fired for rerun-queue, and Rahul keeps the laptop awake.
    It is a systemd user timer running the same "rerunq.py tick" every 15
    minutes, at minutes 2, 17, 32 and 47, in a separate clone
    ~/cbo-gap-queue. The Actions workflow stays enabled as a slower
    second driver. CLAUDE.md rule 22 amended. Units:
    scripts/rerunq-tick.timer (OnCalendar *:2/15, Persistent true),
    scripts/rerunq-tick.service and scripts/rerunq-stop.service; they
    pass "systemd-analyze --user verify". Not yet installed or run.
    - Why a separate clone: a tick runs only from a clean checkout at
      main's tip, and the working copy is rarely that while it is being
      edited.
    - Why the clone is reset to origin/main before each tick: unlike an
      Actions runner, the clone keeps what a tick leaves. After a lock
      lost to the other driver (L1), it would hold an unpushed commit, and
      every later tick would print "HEAD ... is not main's tip; nothing
      done" and exit 0 forever, a silent stall. The reset runs only after
      a tick that exited 0, since any other exit disables the timer, and
      after exit 0 a local commit can only be a stale one.
    - Why the timer is disabled, not only stopped, on any nonzero exit
      (OnFailure, rerunq-stop.service): a stopped but enabled timer comes
      back at the next login. Its reset would then discard a halt commit
      whose push failed, and the queue would act on the state from before
      the halt.
    - No network, or GitHub unreachable: the unit's ExecCondition (git
      fetch) fails, and systemd skips that tick rather than failing it,
      so a wake without network does not disable the timer. The same
      skip would also hide a broken GitHub credential, so the progress
      check reads the journal and the time of the last commit.
    - Two drivers. Neither the workflow's concurrency group nor any other
      lock spans the laptop; the committed state file is the lock (L1),
      as for two Actions ticks. A launch race is safe: the loser's intent
      push is rejected, it reports "lock lost", launches nothing and
      exits 0. A fetch race (both see the job finished) is safe for the
      state, but the loser has downloaded a second copy, its push is
      rejected, and it exits 3 (do_fetch: a publish other than "ok"
      returns 3), so the losing driver disables itself. That means
      re-enabling it and, if it was the laptop, discarding the clone's
      duplicate commit. The minutes 2, 17, 32 and 47 keep the laptop off
      the workflow's scheduled minutes, which makes such a race unlikely
      but not impossible, given cron-job.org's minutes.
    - Environment: Python and the kaggle CLI from the main working copy's
      .venv (requirements.lock), named in the unit's PATH; Kaggle
      credentials from ~/.kaggle as for every laptop run; pushes through
      the existing gh credential helper. The clone commits as "Rahul
      Kumar Mishra (rerunq laptop timer)".
    - Not verified until Rahul runs it: that the gh credential helper
      works from a systemd user service, which the install sequence
      checks with a git push --dry-run inside a transient user unit
      before the timer is enabled.
    - Installed, 2026-10-23, as reported by Rahul (from the journal; no
      copy stored under logs/ yet). The first tick, run
      laptop.20261023T170947Z: ExecCondition and both ExecStartPre steps
      exited 0; it polled rerun-arch-s0of4-a1, judged RUNNING from the
      status line, printed "nothing to do" and exited 0. list-timers
      shows one timer, next run 22:47 IST.
      Credential helper: half verified. The ExecCondition step is a git
      fetch of this private repository, so the gh credential helper
      authenticated a read from inside the systemd user service. A
      "nothing to do" tick pushes nothing, so the write was not exercised
      by the tick. The step-2 git push --dry-run is the evidence for it,
      and its output has not been reported. Fully verified once that
      output, or the first commit made by "Rahul Kumar Mishra (rerunq
      laptop timer)", is on record.
    - Install log, logs/rerunq-laptop-install-20261023.log (Rahul,
      committed in 7711062).
      - Journal: the first tick, run laptop.20261023T170947Z, started
        22:39:45 IST. It polled rerun-arch-s0of4-a1, judged 'has status
        "KernelWorkerStatus.RUNNING"', printed "RUNNING: nothing to do",
        and systemd logged "Finished". This replaces the reported account
        above as the source.
      - Push dry-run in a transient user unit: "! [rejected] HEAD -> main
        (non-fast-forward)", "the tip of your current branch is behind its
        remote counterpart", exit status 1. The clone's local main was
        behind: the command's git fetch updates origin/main, not main, and
        main had moved since the clone. A real tick resets main to
        origin/main first, so this cannot arise there.
      - What the rejection shows. A dry run never uploads anything; git
        decides "non-fast-forward" on the client by comparing its HEAD
        with the refs GitHub advertises for the push service. To get that
        advertisement for this private repository, the gh credential
        helper had to supply a credential from inside the systemd user
        service, and GitHub had to accept it. A credential failure would
        have stopped before any ref comparison, with an authentication
        error. So the helper works from the service on the push path.
        That the credential carries write access is shown separately:
        it is the same gh login whose pushes from the working copy succeed
        throughout this ledger, and whose token scopes include repo
        (gh auth status, read by Claude on this laptop, 2026-10-23).
        Verdict: the credential path for pushing is verified. Not
        exercised: an actual upload from the service. No dry run can show
        that; the first commit by "Rahul Kumar Mishra (rerunq laptop
        timer)" will. If it failed, that tick would exit 3 and disable
        the timer (OnFailure), not fail unseen.
    - Upload from the service: verified, 2026-10-24. Commit 6fbebc6,
      author "Rahul Kumar Mishra (rerunq laptop timer)", made by the
      laptop tick run laptop.20261023T203212Z, is on origin/main. It
      carries the fetched folder runs/rerun-arch-s0of4-a1-kaggle-
      20261024-020220, logs/kgrun-rerun-arch-s0of4-a1-fetch.log,
      logs/rerunq-rerun-arch-s0of4-a1-halt-20261024-020230.log and the
      HALTED state. The tick exited 3 (the halt below), the OnFailure
      unit disabled the timer, as designed (reported by Rahul).
  - R1 defect: a shard check that no shard could pass (2026-10-24).
    The tick laptop.20261023T203212Z fetched rerun-arch-s0of4-a1 and
    halted: "R1: header of runs/rerun-arch-s0of4-a1-kaggle-20261024-
    020220: run dir /kaggle/working/rerun-s0of4-20261023-164555,
    expected a name ending -s0of4" (commit 6fbebc6, halt log above).
    - Source. rerun.py builds a shard's output folder as
      tag = "-s{}of{}".format(a.shard, a.nshards), then
      new_outdir("rerun" + tag), and new_outdir returns
      "{}-{}".format(name, stamp) with stamp %Y%m%d-%H%M%S. A shard's
      folder is therefore always rerun-s<S>of<K>-<YYYYMMDD>-<HHMMSS>:
      the tag comes before the stamp. rerunq.py's header_problems
      required the run dir to END with -s<S>of<K>, which no folder
      rerun.py writes can do. All six remaining shard jobs would have
      halted the same way. The cause is rerun.py's own docstring
      (OUTPUT: "run: <outdir>/rerun-<stamp>[-smoke][-s<i>of<k>]/"),
      which gives the wrong order; R1 was written from the docstring,
      not the code. The smoke folder is likewise rerun-smoke-<stamp>,
      not rerun-<stamp>-smoke. The docstring is not edited now: rerun.py
      is code-pinned (P1; rerun_sha256 756c4069...) until both shard
      sets are done, and editing it would halt the next launch. OPEN as
      a documentation defect of rerun.py, to fix after the last shard.
    - Not a defect of rerun.py's output. The run dir
      rerun-s0of4-20261023-164555 is the name the code gives shard 0 of
      4, and the folder's rerun_params.csv records shard 0, nshards 4,
      mode run, the pinned rerun, rerunlib and costprobe2 hashes, the
      plan sha256 4aec4b1e... and env python 3.13.15 numpy 2.1.3. The
      halt reason lists no other R1 problem, and header_problems
      collects every problem before halting, so python, numpy, the three
      code hashes, the plan hash and the mode all passed. F1 passed
      ("manifest verified, 3 files"). F2 was NOT run: the R1 halt comes
      before it in do_fetch. The halt log prints "runner exit 0 ...
      completed 4767", and Rahul reports from the kernel log "completed
      4767  errors 0  not started 0" and "kgrun runner: exit code 0".
    - Fix (scripts/rerunq.py; R1 in its docstring rewritten with worked
      examples). R1 for a shard now checks what it is meant to check,
      that the output belongs to the shard the queue launched, and no
      longer by a suffix: (a) the run dir's basename is exactly
      rerun-s<S>of<K>-YYYYMMDD-HHMMSS (re.fullmatch; another shard,
      another split such as s0of2, s0of40, an unsharded or a smoke folder
      all fail); (b) the fetched folder holds exactly one rerun-* folder,
      with that basename, so the header and the rows F2 counts are from
      one run (the old check never tied the two); (c) that folder's
      rerun_params.csv records shard S and nshards K. Each is at least as
      strict as what the old check meant; none accepts another shard's
      output. rerunq.py is not among the pinned files (P1), so the fix
      does not disturb the shard set.
    - New subcommand "rerunq.py verify" (reads only, writes nothing):
      while HALTED, re-runs F1, R1, R2 and F2 on the current item's last
      fetched folder as a fetch tick would. "release --mode next-item"
      does not re-check anything, so without it shard 0's F2 count would
      never have been executed by the queue's code.
    - Release: after "verify" prints PASS for runs/rerun-arch-s0of4-a1-
      kaggle-20261024-020220 (log to be committed under logs/),
      "release --mode next-item": READY at arch-s1of4, attempt 1. Not
      next-attempt, which would rerun shard 0 with the a1 folder as
      resume input; not start, which is refused because a job is
      recorded.
  The condition first written here ("OPEN until the first tick has
  launched the smoke and a later tick has fetched and committed it") was
  met by 48e5c71 (the a2 smoke); the item was kept open to the end of the
  queue.
  - Queue completed, 2026-10-25. The tick that fetched
    rerun-cal-s1of2-a1 printed "runner exit 0; state now DONE"
    (logs/rerunq-rerun-cal-s1of2-a1-fetched-20261025-050254.log; commit
    17e0598). Rahul reports state DONE and the laptop timer turned off.
    All eight items, as committed (counts from each kernel log in the
    run folder, and for the shards also the F2 line of the queue's
    fetch log):
    - smoke-arch: a1 halted (K7, exit 2 before any trajectory,
      runs/rerun-smoke-arch-a1-kaggle-20261023-213143); a2
      runs/rerun-smoke-arch-a2-kaggle-20261023-221109, "D-SMOKE  16
      task(s) on 4 worker(s)", "D-SMOKE PASS", exit code 0.
    - arch-s0of4 a1, runs/rerun-arch-s0of4-a1-kaggle-20261024-020220:
      "completed 4767  errors 0  not started 0", "finished 4767 task(s)
      in 13430.6 s". Halted on the R1 defect above, then
      logs/rerunq-rerun-arch-s0of4-a1-verify-20261024.log "F2: 4767 rows
      end ok; runner summary completed 4767", released next-item
      (cdb8761). No second attempt.
    - arch-s1of4 a1, runs/rerun-arch-s1of4-a1-kaggle-20261024-133226:
      "completed 4767  errors 0  not started 0", 16255.0 s; F2 4767.
    - arch-s2of4 a1, runs/rerun-arch-s2of4-a1-kaggle-20261024-160215:
      "completed 4767  errors 0  not started 0", 7375.2 s; F2 4767.
    - arch-s3of4 a1, runs/rerun-arch-s3of4-a1-kaggle-20261024-200233:
      "completed 4767  errors 0  not started 0", 12285.0 s; F2 4767.
    - smoke-cal a1, runs/rerun-smoke-cal-a1-kaggle-20261024-203231:
      "D-SMOKE  8 task(s) on 4 worker(s)", "D-SMOKE PASS", exit code 0.
    - cal-s0of2 a1, runs/rerun-cal-s0of2-a1-kaggle-20261025-003238:
      "completed 5616  errors 0  not started 0", 12676.9 s; F2 5616.
    - cal-s1of2 a1, runs/rerun-cal-s1of2-a1-kaggle-20261025-050238:
      "completed 5616  errors 0  not started 0", 14107.7 s; F2 5616.
    Totals as printed by the shard headers: "tasks    19068" for the
    archived-beta set (four shards of 4767) and "tasks    11232" for the
    calibrated set (two shards of 5616). Every shard header printed
    python 3.13.15 and numpy 2.1.3 (fetch logs, R1). No shard was
    resumed; no exit 4 or 5 occurred.
  - Not established by this entry: that the six shard folders together
    hold every task of all seventeen rows with no duplicate. That is
    rerun_analysis.py's A0 and A1 (exit 2 or 7), run by Rahul on the
    laptop (notes/RERUN_RUNBOOK.md section 7).
  CLOSED 2026-10-25 by the commit that adds this paragraph; the
  artefacts are the run folders and logs named above, the last of them
  committed in 17e0598.
- K7 (Kaggle, dataset version race in kgrun launch; 2026-10-23). The smoke
  rerun-smoke-arch-a1, launched by the queue (commit ea5e6a1,
  logs/kgrun-rerun-smoke-arch-a1.log), stopped on Kaggle with "kgrun
  runner: SETUP ERROR, folder rerun-plan-20261023-112643 is not in
  /kaggle/input/datasets/ericsom/cbo-gap-archive/kgrun-ship-index.json",
  exit 2, before any trajectory (as reported by Rahul; the kernel log is
  not yet fetched).
  - The bundle was right. --data-dirs reached build_bundle ("ship data
    rerun-plan-20261023-112643 5 files, manifest verified"), the five
    kgrun-ship-000-* files and kgrun-ship-index.json (646 B) were
    uploaded, and the runner was generated to rebuild that folder.
  - The kernel did not mount that upload. The runner found a
    kgrun-ship-index.json (otherwise its message is "folders were
    requested but ... is not in the mounted dataset"), and the one it
    found did not list the folder. Every earlier launch that shipped a
    folder shipped calprec2-smoke-kaggle-20261011-121225 with an index of
    750 B (logs/kgrun-calprec2-long-s*-a1.log). The index read is
    consistent with the previous version's, not this one's.
  - Why: wait_ready asks "kaggle datasets status", which reports the
    dataset, not the version just uploaded. Here it said ready at 0 s,
    right after "Dataset version is being created", and the kernel was
    pushed at once. wait_ready was kept after K1 as a guard against an
    unprocessed version; it was never measured to do that.
  - Not a stale listing and not a lost --data-dirs: the index was built
    from this launch's folder list. The stale thing was the mounted
    dataset version.
  - Consequence for earlier runs, CLOSED 2026-10-23: the stale-mount
    risk did not materialise for any calprec2-long shard. Every shard
    shipped the same folder, so a stale mount would not have stopped it;
    it would have run the previous version's scripts. Audited by
    scripts/calprec2_hashaudit.py (rules A1 to A9 in its docstring), run
    by Rahul on the laptop at HEAD 539fcd2, Python 3.12.3, 2 workers;
    log logs/calprec2-hashaudit-20261023.log. From the log:
    - "VERDICT: PASS -- all 26 shards ran the code of their launch
      commits";
    - "LEDGER PIN: PASS -- every record printed calprec2.py
      c339ca9d...c14d and costprobe2.py ea5cb2e1...f64b";
    - 26 record folders, one per shard, each "shard verdict PASS
      ledger pin PASS"; 364 hash lines PASS (calprec2.py, costprobe2.py
      and the twelve V1 modules, for each of the 26 records) and 52
      params lines PASS (script_sha256 and costprobe2_sha256 equal to the
      header, for each of the 26); no FAIL, no INCOMPLETE, no WINDOW line;
    - one NOT A RECORD, runs/calprec2-long-s2of26-a1-kaggle-20261013-213019
      (no sha256.txt, 0 entries; the aborted fetch), skipped under A1;
    - launch commits from ee2b155f50 (s0, launched 2026-10-11T21:47:51
      local) to bcd5ba18ba (s25, launched 2026-10-23T02:27:15 local).
    What this establishes: each shard ran calprec2.py, costprobe2.py and
    the twelve archived modules byte-identical to the files at its launch
    commit, and those calprec2.py and costprobe2.py are the ones the N28
    result names. It does not say which dataset version each kernel
    mounted. A stale version holding the same bytes would pass, and
    would be harmless for the same reason.
    Not covered by a printed hash: scripts/cbopaths.py, the --archive and
    --outdir resolver both scripts import. Its git history (git log --
    scripts/cbopaths.py) shows its last change on 2026-10-09 (23a46c8),
    before the first launch commit. So the committed file was the same at
    every launch commit. Whether a mounted copy could have been older is
    not established by any log.
    The log also carries two Python 3.12 DeprecationWarnings for
    datetime.utcfromtimestamp at scripts/calprec2_hashaudit.py:263, on
    stderr. They do not affect any comparison.
  - Fix (scripts/kgrun.py, docstring BUNDLE IDENTITY): each bundle holds
    kgrun-bundle-<id>.sha256, listing every uploaded file and its hash;
    <id> is a hash of that list. Before the push, kgrun waits until
    "kaggle datasets files <dataset> --page-size 200" lists that name.
    The runner refuses (exit 2, before the script starts) unless that
    file is in the mounted dataset and every file it lists hashes as
    listed. The printed line "bundle <id>: N files verified" in the
    runner header then shows the code run is the code uploaded.
  - Not measured: what "kaggle datasets files" of kaggle 2.2.4 prints,
    and whether it accepts --page-size. Measured by Rahul before the
    next launch (output stored under logs/).
  - What would have caught it before a twelve-hour shard: the smoke did,
    being item 0 and failing in seconds. Without the smoke, a shard
    whose folder name matched the stale index would have run the old
    code for its full length with nothing in kgrun or rerunq to notice;
    rerunq's R1 hash check would have caught a changed rerun.py,
    rerunlib.py or costprobe2.py only after the fetch.
  - kaggle datasets files, measured (logs/kaggle-datasets-files-20261023.log,
    Rahul, before the a2 launch): kaggle 2.2.4 accepts --page-size 200 and
    printed a table of 55 names. The listed version was the a1 upload
    (creation dates 2026-10-23 13:52 UTC, kgrun-ship-index.json 646 B), so
    by then the a1 version had become current.
  - The race, observed directly in the a2 launch
    (logs/kgrun-rerun-smoke-arch-a2.log): bundle id 2f72505d691cfde7;
    after "VERSION DATASET", "WAIT FOR DATASET READY" passed, and then
    "WAIT FOR THIS BUNDLE" printed "0 s: not listed; kgrun-bundle files
    listed: none" and "31 s: kgrun-bundle-2f72505d691cfde7.sha256
    listed"; only then "PUSH KERNEL". A push right after the ready check
    would have gone out while Kaggle still served the previous version,
    which is what a1 did.
  - The a1 kernel log (runs/rerun-smoke-arch-a1-kaggle-20261023-213143)
    printed "listing 55 files in the mounted dataset". The a1 upload and
    the previous calprec2 bundles both had 55 files, so the count does not
    say which version was mounted.
  - Closed by the a2 smoke (runs/rerun-smoke-arch-a2-kaggle-20261023-221109,
    committed by the queue in 48e5c71). Its kernel log prints "listing 57
    files in the mounted dataset" and "bundle 2f72505d691cfde7: 56 files
    verified against kgrun-bundle-2f72505d691cfde7.sha256", then "D-SMOKE
    PASS" and "kgrun runner: exit code 0". The mounted dataset was the
    a2 upload, and every uploaded file hashed as listed.
  CLOSED 2026-10-23.

- K8 (Kaggle, kgrun pre-launch check; defect in the N42 change; found
  2026-10-26). The queue halted at calprec2-ext-finalize-a1 (commit
  1151836, "kgrun launch exit 1"). logs/kgrun-calprec2-ext-finalize-a1.log
  holds one line: "data folder
  runs/calprec2-ext-s0of15-a1-kaggle-20261025-103225 is not named in
  --args as runs/calprec2-ext-s0of15-a1-kaggle-20261025-103225". Rahul's
  kgrun status for the kernel: "Cannot access kernel
  'ericsom/cbo-calprec2-ext-finalize-a1'", the ABSENT reply.
  - Cause, read from the source at 1151836: N42 taught the runner
    (RUNNER_TEMPLATE) to rewrite runs/<name> inside comma-joined --args
    tokens, but main() still checked each --data-dirs folder against
    a.args.split(), whole tokens only. The finalize passes its folders as
    one token, "--finalize runs/A,runs/B,...", so the check refused the
    first folder.
  - Nothing was pushed. That check runs in main() before the banner and
    before build_bundle; the log holds no banner and no "$ kaggle" line.
    So no dataset version and no kernel were created, consistent with the
    ABSENT status.
  - Fix (scripts/kgrun.py, arg_members): the check splits every
    whitespace token on commas, the same rule the runner applies. A token
    without a comma is handled exactly as before. kgrun.py is not a P1
    code pin of the calprec2 profile, so the queue's pins are unchanged.
  - Rest of the N42 change, read for the same whole-token assumption:
    the runner's rewrite counts and replaces comma members; ship_list
    splits --data-dirs on commas; rerunq.py builds the finalize args and
    data_dirs from one list (job_spec) and compares R1F's "read" lines by
    basename, which the runner's /tmp/kgrun-ship/<name> paths keep;
    calprec2.py splits --finalize on commas. None has it. The one other
    whole-token test in kgrun.py, "--resume-from" in a.args.split(),
    predates N42 and concerns a flag, not a folder.
  - Closed by calprec2-ext-finalize-a2 (released next-attempt in
    1ea189d after "rerunq.py check"; launched cd941b0; fetched 8b44675).
    logs/kgrun-calprec2-ext-finalize-a2.log has 15 "ship data" lines.
    The kernel log
    (runs/calprec2-ext-finalize-a2-kaggle-20261026-204714/cbo-calprec2-ext-finalize-a2.log)
    prints, for each of the 15 folders, "args: runs/<name> ->
    /tmp/kgrun-ship/<name> (1 occurrence(s))". The command it ran passes
    all 15 rebuilt paths in one --finalize token, and calprec2 printed a
    "read" line for each. The fetch tick
    (logs/rerunq-calprec2-ext-finalize-a2-fetched-20261026-204718.log)
    prints no R1F problem, "F2F: 41 rows, 41 distinct cells, 0
    incomplete; expected 41 cells" and "runner exit 0; state now DONE".
    The tick halts on any R1F problem, so none was found.
  CLOSED 2026-10-26.
