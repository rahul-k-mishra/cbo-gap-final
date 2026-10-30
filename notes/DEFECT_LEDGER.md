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
  UPDATE 2026-10-30 (Riedl's dissertation, ~/cbo-refs/riedl-dissertation.pdf,
  "Mathematical Foundations of Interacting Multi-Particle Systems for
  Optimization", TUM, submitted 10.04.2024, accepted 02.09.2024, 448 pp.,
  https://mediatum.ub.tum.de/doc/1738466/1738466.pdf; text layer read).
  - "nu in (0, 1/2]" above is WRONG: the conference paper (reprinted as
    P2, LNCS 13224, Definition 2, (5)-(6)) has nu in (0, inf), l-infinity
    balls. Its Theorem 2: rho_0 in P4 with rho_0(B^inf_r(v*)) > 0 for all
    r, 2 lambda > sigma^2, conclusion min V <= eps and exponential decay.
  - The dissertation states before the reprint: "The proof of [CBO-II,
    Theorem 2] in the print below contains a subtle technical mistake. A
    corrected version of it is available both on arXiv and at the end of
    Section 3.1.1, where we prove Theorem 3.6, which strengthens the
    original result". So the conference Theorem 2 must not be the result
    relied on. (The corrected arXiv version's identifier is not given
    there; I do not know it.)
  - Dissertation Theorem 3.6 (anisotropic; dynamics (3.2) with D = diag,
    (2.5), no cutoff H): Assumption 3.5 A1, A2 ((3.26) local coercivity in
    l-infinity, nu in (0, inf); (3.27) far field outside B^inf_{R0}); rho_0
    in P4, x* in supp(rho_0), V(rho_0) > 0; eps in (0, V(rho_0)), theta in
    (0,1); lambda, sigma > 0 with 2 lambda > sigma^2; T* (3.28).
    Conclusion for ANY weak solution rho in C([0,T*], P4) of (3.3)
    (Remark 3.7): V(rho_T) = eps for some T in [(1-theta)/(1+theta/2) T*,
    T*], with (3.30)-(3.31). Proof given in the dissertation ("Proof of
    Theorem 3.6", Section 3.1.1). This is the auditable theorem for the
    anisotropic boundary that referee point 2 asks for.
  - Existence for it: Remark 3.7 points to Theorem 3.4 under W1-W2
    (Assumption 3.3). W1 is (3.7), C1(1 + ||x|| + ||x'||)||x - x'||, with
    the additive 1 (the dissertation calls its omission "an unnecessary
    restriction"); W2 is bounded above or quadratic far-field growth.
    Theorem 3.4's proof is by reference ("follows verbatim ... [Car+18]"),
    so GHV Theorem 2.3 stays the audited existence route for both
    diffusions.
  - Citability: a TUM doctoral dissertation, accepted, publicly hosted; it
    can be cited in its own right for Theorem 3.6, which carries its own
    proof. The conference paper is cited as the origin, not as the theorem
    relied on. Its mean-field approximation, Proposition 3.16 ((3.72),
    under W1-W2, no parameter condition), has the sup-E-conditioned form
    of FKR 3.11 and does not own the measured exponent either (N1).
  - For O2: the anisotropic part need not use nu <= 1/2; it must be
    redone against Assumption 3.5 (l-infinity balls B^inf_{R0}), with
    constants. Not checked here.
  Still OPEN (manuscript text; O2 constants).
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
  CORRECTION 2026-10-29 (sup-E finding; arXiv v6 read in the PDF, page 16,
  eyeballed; numbering re-mapped under N3). The measured exponent is NOT
  the conclusion of FKR Proposition 3.11 (the "Proposition 16" above).
  (32) bounds max_i sup_t E[ ||V^i_t - Vbar^i_t||^2 | Omega_M ] <= C_MFA
  N^-1: supremum outside the expectation, conditioned on Omega_M. The
  estimator, manuscript (9), is the mean over realizations and particles
  of sup_t ||.||^2: supremum inside, unconditioned. sup E <= E sup, so
  (32) does not bound the measured quantity. The only cited result that
  does is GHV Theorem 2.6 at p = 2 ((2.11): (E sup |.|^2)^(1/2) <= C
  J^(-1/2)), for every objective in A(s,l,l), with no parameter
  condition and no lambda. FKR v6 p. 17 says the same: [31] (GHV)
  improves (32) by removing the conditioning and "obtaining a pathwise
  estimate". The rest of N1 stands and is strengthened: the theorem that
  carries 2 lambda > d sigma^2 (3.7) owns no J exponent, and the theorem
  that owns the measured exponent (GHV 2.6) has no parameter condition.
  The manuscript's attributions of the measured quantity to FKR (line 60
  and others) are listed in the reply of 2026-10-29 and are to be fixed
  with N1. The SIAM obligation above stays OPEN.
  SETTLED BY THE AUTHOR (2026-10-30; by email from Konstantin Riedl to
  Rahul, in reply to Rahul's request of 2026-10-29; words as relayed by
  Rahul): the condition 2*lambda > d*sigma^2 "is needed to obtain decay of
  the functional V(rho_t) in Lemma 4.1, the Lyapunov functional analysed
  for global convergence to the minimiser"; Proposition 3.11 "does not
  need it per se"; "since Theorem 3.8 combines the two results, the
  condition is needed again there". He also said the latest arXiv version
  has more detail, in particular an appendix not in SIOPT because of page
  limits, and that they tried to keep the same numbering in both versions,
  at least for the main theorems. The numbering was then checked against
  the SIOPT PDF itself (N3 update of 2026-10-30), not taken from this.
  The SIAM obligation of this item is CLOSED: SIOPT Proposition 3.11,
  (3.13), p. 2988, is stated under "the assumptions of Theorem 3.2" with no
  parameter condition (read in the rendered page).
  SINGLE GROUND FOR WITHDRAWAL (recorded 2026-10-29, Rahul's decision).
  The conceptual claim at manuscript lines 40, 547 and 698 ("the
  theorem-admissible region and the observability region are different
  sets") is withdrawn on ONE ground: this item, N1. The referee's ground
  (R1, the Ackley misclassification) is distinct but not independent: it
  is evidential and curable (route under "Ackley: the route"), and once
  cured the claim still fails on N1. Full assessment in N45.
  HOW THE WITHDRAWAL MUST BE WRITTEN (Rahul's instruction 2026-10-29;
  identical text in N1 and N45):
  - The reason given is N1, not the Ackley misclassification. Written the
    other way it implies the claim would survive with valid objectives,
    which is false, and invites the referee to ask why it was not simply
    rerun on Sphere or Rastrigin.
  - The Ackley correction (R1) is reported separately, in the assumption
    audit, as a fix to Table 1.
  - One sentence states that even with the classification corrected the
    claim does not survive, and why: the condition 2 lambda > d sigma^2 is
    a hypothesis of FKR Theorem 3.7, which owns no J exponent, and the
    result that owns the measured exponent, GHV Theorem 2.6, has no
    parameter condition, so there is no admissible region to compare.
  - The referee's suggested demonstration on fully verified objectives
    (costed at the end of "Ackley: the route", "Cost of a demonstration on
    objectives that satisfy (6), (7), (27) outright") is NOT run: it would
    demonstrate an ill-posed claim.
  WHAT REPLACES THE CLAIM: cells inside the hypotheses of GHV Theorem 2.6
  can fail the finite-window criterion. This is a statement about the
  prefactor, not about an admissible region. It still needs O1 (Ackley in
  A(0,0,0)) proved, since the three failing cells are all Ackley.
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
  UPDATE 2026-10-29 (read from Rahul's local copies in ~/cbo-refs/, kept
  outside the repository because they are not his to redistribute:
  2103.15130v6.pdf, "arXiv:2103.15130v6 [math.NA] 2 Aug 2024", 42 pages;
  2312.07373v4.pdf, "arXiv:2312.07373v4 [math.PR] 13 Apr 2025", 42 pages).
  - The v6 numbering stated above is wrong. v6 numbers by section, not
    sequentially, and contains no Theorem 12, Theorem 14, Lemma 15,
    Proposition 16 or Remark 25. In v6: Definition 3.1 (weak solution),
    Theorem 3.2 (well-posedness, H = 1, conditions (19)-(21), citing [12,
    Theorems 3.1, 3.2]), Remark 3.3 (test-function extension), Theorem 3.4
    (H not 1), Definition 3.5 (A1-A3, conditions (24)-(26)), Theorem 3.7
    (convergence in mean-field law; hypothesis 2 lambda > d sigma^2; T* is
    (27)), Theorem 3.8 (convergence in probability, under the assumptions
    of Theorem 3.7 and Proposition 3.11), Lemma 3.10, Proposition 3.11
    (E[||V - Vbar||^2 | Omega_M] <= C_MFA N^-1, (32), under the assumptions
    of Theorem 3.2; C_MFA depends on alpha, lambda, sigma, T, ...; no
    parameter condition). Equation (83) of v6 is a Gronwall step in the
    proof of Proposition 3.11, not the factor 8/(c eta^2 eps). The
    sequential numbers above, and those in N1, R1 and O4-O8 (Theorems 6,
    8, 12, Proposition 16, Remark 7, Definition 5), come from some other
    version that is not on this machine; I do not know which. Every one of
    them must be re-mapped to v6 by content before use.
  - The manuscript's 3.7, 3.11 and (19)-(20) agree with v6 in number and
    content. Whether SIAM J. Optim. 34(3) uses the same numbering is not
    answerable from the preprint: v6 states no journal correspondence.
    That half stays open until the SIAM PDF is read. The c^-2 claim was not
    re-checked.
  - GHV: the local copy is v4, not v3. v4 Section 2 has Subsections
    2.1-2.6 (2.6 "Numerical experiment") and a Table 1 (parameters of that
    experiment), so "[4, Subsection 2.6]" and "[4, Table 1]" exist in v4;
    the ESAIM numbering is still unchecked (O6). Theorem 2.3 and Theorem
    2.6 are stated for f in A(s,l,l) and any globally Lipschitz S (2.1,
    (2.10)); the drift has unit coefficient (1.1), no lambda. v4
    Subsection 5.2 sketches, without a stated theorem, well-posedness and
    a mean-field estimate for u > l > 0 up to a finite time T < T+, where
    the Bihari-LaSalle bound becomes singular. Rosenbrock is A(3,1,4)
    (manuscript Proposition 2), so it is in that sketched case: N2's "no
    existence theorem in either paper" holds for stated theorems, but the
    text must mention 5.2. Still OPEN (SIAM comparison).
  RE-MAPPING 2026-10-29 (Rahul's request; by content, from the v6 text,
  extracted with pdftotext; formulas should be eyeballed in the PDF).
  Old reference -> v6 result -> verdict.
  - N1 "Theorem 12 (cited as 3.7)", convergence to the minimizer with
    hypothesis 2 lambda > d sigma^2 -> Theorem 3.7 (hypothesis verbatim;
    conclusions (28), (29)). HOLDS.
  - N1 "Proposition 16 (cited as 3.11)", no parameter condition ->
    Proposition 3.11. No parameter condition: HOLDS (C_MFA depends on
    lambda, sigma). "Hypotheses are those of Theorems 6 and 8": 3.11 names
    only Theorem 3.2; "6" -> 3.2 HOLDS; "8" CANNOT BE MATCHED (Section 3.3
    restricts to H = 1, so Theorem 3.4 is not among 3.11's hypotheses).
  - N1 "the J^-1 exponent the paper measures is the conclusion of ... FKR
    Proposition 16" -> DOES NOT SURVIVE. (32) bounds
    max_i sup_t E[ ||V - Vbar||^2 | Omega_M ] (sup outside the expectation,
    conditioned on Omega_M). The estimator, manuscript (9), is the mean of
    sup_t ||.||^2, i.e. E sup. sup E <= E sup, so (32) does not bound the
    measured quantity. v6 itself (p. 17) says [31] (GHV) improves (32) by
    removing the conditioning and "obtaining a pathwise estimate, see [31,
    Theorem 2.6]". Only GHV Theorem 2.6 at p = 2 owns the measured exponent.
  - N2 "Conditions (6)-(7)" -> these are the MANUSCRIPT's equations (6),
    (7) (labels eq:F19, eq:F20 in sn-article.aux), i.e. v6 (19), (20); not
    FKR numbers. "Wrong gate for Theorem 12": Theorem 3.7 assumes A1-A2,
    rho_0 in P4 with v* in supp, and a weak solution in C([0,T*],P4); it
    does not impose (19)-(20). HOLDS.
  - N2 "existence via FKR Thm 6" -> Theorem 3.2 (H = 1; 3.4 for H not 1).
    HOLDS.
  - R1 "FKR condition (6)" -> manuscript (6) = v6 (19). Ackley fails it
    (linear growth at w = 0 against C1 ||v||^2). HOLDS; cite as (19).
    "A1-A2" -> Definition 3.5, (24)-(25). HOLDS.
  - Ackley route "standing hypothesis of FKR Theorem 12" (p = 4, Gaussian
    rho_0) -> Theorem 3.7. HOLDS (full support from manuscript line 301).
    "FKR-aniso Theorem 2" is the 2022 paper, not on this machine: NOT
    CHECKED.
  - O2 "FKR A1-A2, nu = 1" -> (24) with nu in (0, inf); nu = 1 gives
    E - E_min >= eta ||v - v*||, the form O2 uses. Form HOLDS; constants
    not checked. The anisotropic part (nu <= 1/2, l-infinity) is the 2022
    paper: NOT CHECKED.
  - O3 "FKR (8)/(9)" (mean-field SDE / Fokker-Planck) -> v6 (7) / (8); v6
    (9) is the informal N^-1 estimate of Remark 1.2. Matching with
    lambda = 1, sigma = sqrt(2 theta) HOLDS FOR THE ISOTROPIC ARM AND H = 1
    ONLY: v6 has no anisotropic equation, and its drift carries H. O3 must
    say both.
  - O4 "FKR Definition 5" -> Definition 3.1 (test class C_c^inf, rho_t ->
    rho_0 pointwise). Same test class as GHV (4.9). HOLDS; note GHV (4.9)
    is written with the CBS generator and carried to CBO by GHV Remark
    4.3. "FKR Remark 7" -> Remark 3.3 (extension to C_*^2 under P4
    regularity). HOLDS.
  - O5 "Theorem 12 is stated for any weak solution" -> Theorem 3.7 ("if
    rho in C([0,T*],P4) is a weak solution ..."). HOLDS.
  - O7 "Levy (fails (6)" -> manuscript (6) = v6 (19). HOLDS.
  - O8 "FKR Proposition 16 requires Theorem 6's hypotheses" -> 3.11
    requires 3.2's. HOLDS. "For Ackley and Levy the rate is sourced from
    GHV 2.6": HOLDS but is too narrow; by the N1 finding above, GHV 2.6 is
    the source of the measured exponent for every objective.
  - Cost paragraph "(6), (7), (27)": (6), (7) are manuscript equations;
    (27) is not a manuscript equation (the manuscript has ten) and v6 (27)
    defines T*, not a condition on an objective. CANNOT BE MATCHED.
  - N3 "Theorem 14, Lemma 15, Remark 25" and "conditions (25)-(27)": no
    content recorded with them. CANNOT BE MATCHED.
  - N3 "(83): factor 8/(c eta^2 eps), one power of c" -> by content the
    alpha_0 lower bound, Remark 4.8, (68)/(69): alpha_0 =
    -8/(c(theta,lambda,sigma)^2 eta^2 eps) log(...). Two powers of c.
    DOES NOT SURVIVE. The manuscript's "leading factor c^-2" (line 211)
    agrees with v6.
  UPDATE 2026-10-30: SIOPT COMPARED (Rahul's copy ~/cbo-refs/
  fkr2024-siopt.pdf, SIAM J. Optim. 34(3) 2973-3004, 32 pp., sent by
  Riedl; pages 2984, 2985, 2987, 2988 and 2999 read as rendered images,
  the rest, including Theorem 3.8 on p. 2986, from the text layer).
  - Result numbers, SIOPT = v6, same content: Definition 3.1 (p. 2984),
    Theorem 3.2, Remark 3.3, Theorem 3.4 (p. 2984), Definition 3.5,
    Theorem 3.7 (p. 2985), Theorem 3.8, Remark 3.9, Lemma 3.10 (pp.
    2986-87), Proposition 3.11 (p. 2988), Remark 4.8 (p. 2999), Section 3.3.
    Every result the manuscript cites by number exists under that number in
    SIOPT.
  - Equation numbers all DIFFER: SIOPT numbers by section. v6 (18) ->
    (3.1); (19) -> (3.2); (20) -> (3.3); (21) -> (3.4); (24) -> (3.5);
    (25) -> (3.6); (26) -> (3.7); (27) -> (3.8); (31) -> (3.12); (32) ->
    (3.13); (68) -> (4.30); (69) -> (4.31); v6 (34) -> (3.15). The
    manuscript uses no bare FKR equation number; keep it so, or cite
    SIOPT's.
  - (4.30)/(4.31) read in the rendered page: -8/(c(theta,lambda,sigma)^2
    eta^2 eps), two powers of c, as in v6.
  - ARXIV-ONLY (v6 "Appendix: Extended proof details of Section 3.3", p.
    36 on): the values b1 = 0, b2 = exp(alpha(sup E - E_min)) and b1 =
    C4^2 + b2, b2 = 2(C2/C3)(1 + 1/(alpha C3 C4^2)) (v6 (77)); c_M =
    exp(alpha C2 (1 + sqrt M)) (v6 (84)) and the three consensus-point
    bounds in c_M (v6 (81)-(83)). SIOPT Section 5 (pp. 3000-3001,
    (5.1)-(5.3)) has neither. The BDG dimension remark ("the constant ...
    depends on the dimension d") IS in SIOPT Section 5. The alpha_0 in
    O(d log(eps)/eps) sentence IS in SIOPT (after (3.15)).
  - Manuscript consequences (to N45): main line 201 and supplement lines
    27 and 29 (b1, b2, c_M, the three terms) must cite arXiv v6, Appendix,
    not SIOPT, and say so. The note under reference [3] must name v6 (the
    dissertation reprints v5, numbered differently), state that results
    are cited by numbers common to v6 and SIOPT, and that proof details
    from the v6 appendix are cited to arXiv.
  - THE OLD SEQUENTIAL NUMBERS ARE v5. Riedl's dissertation (Paper P1)
    reprints arXiv:2103.15130v5 (23 Mar 2024), numbered sequentially:
    Definition 5, Theorem 6, Remark 7, Theorem 8, Definition 9 (A1-A3,
    (23)-(25)), Theorem 12 ((26) T*, (27), (28)), Theorem 13, Remark 14,
    Lemma 15, Proposition 16 ((31)), Remark 24 (alpha_0, (63)-(64)),
    Lemma 25, FKR (8) SDE, (9) Fokker-Planck. Against v5:
    Theorem 6, Theorem 12, Proposition 16, Definition 5, Remark 7 and
    (8)/(9) MATCH in number and content (so O3's "(8)/(9)" was correct for
    v5). "Theorems 6 and 8" in N1: v5 Proposition 16 also names only
    Theorem 6, so "and 8" was wrong in v5 too. N3's "Theorem 14" and
    "Remark 25" do not exist in v5 (Remark 14, Lemma 25; the alpha_0
    remark is Remark 24). v5 (83) is a bound in the proof of Lemma 25, and
    v5 (63)-(64) carry c^2, so "one power of c" has no source in any
    version: it was a misreading. "(25)-(27)" in v5 are A3, T*, and
    V(rho_T) = eps; the cost paragraph's "(27)" is not an objective
    condition in v5 either and stays UNMATCHED.
  N3 is CLOSED on numbering. The manuscript work it implies is in N45.
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
  Addendum 2026-10-30 (full extent; Rahul: "a disclosure, not a
  correction"). Sentences of the deposited text that rest on evidence
  that does not exist or is misdescribed:
  - Evidence absent: tex 309, the two-installation agreement (one log,
    NumPy 1.24.4, round1-zip only); tex 719, "Console output ... together
    with a reanalysis script that recomputes ... the tolerance and
    Bonferroni tables" (no console output deposited, ARC1; reboot.py's log
    says NOT RECOMPUTED for 7.5; the sentence has no verb); tex 719 and
    728, the dagger rows' console log (ARC1, ARC5); tex 719, per-realization
    files for every confirmatory run (eight experiments are cell means,
    ARC2).
  - Provenance misdescribed: tex 309, "every interval reported in this
    paper is the 4000-resample value ... no reported interval originates
    from a computation that is not in the archive", and "every trend
    interval ... at 4000 resamples". The deposited code sets: control.py,
    boundary.py, sigma.py, regimemap.py N_BOOT 400 (Table 4, Table 5, 7.10
    counts, 7.12 counts); audit.py A2 range(500) in r_regression (7.10
    coefficients); audit.py A3 N_BOOT 2000 (7.11 equivalence counts).
  - No generating code: the N30 list, and tex 719's "Each pre-specified
    criterion is stated in the docstring ... present in the archived copy"
    for those numbers.
  - Contradicted by the code (N31): tex 309, 495, 650, the pairing.
  - Correction to Claude's reply of 2026-10-30: it gave the 7.10
    coefficient intervals as 2000 resamples. audit.py's r_regression draws
    range(500); N_BOOT 2000 is used by A3 only. A3 resamples the 4
    objectives of each crossed_summary.csv cell (8 rows: 2 diffusions x 4
    objectives), at 90%.
  - scripts/depositcheck.py (written 2026-10-30, Rahul's instruction):
    tallies control_summary.csv against Table 4, boundary_summary.csv
    against Table 5 and sigma_summary.csv against the 7.10 counts, and runs
    audit.py unchanged against the 7.10 coefficients and 7.11 counts, at
    the deposited code's resample counts; no setting searched (R0). Writes
    nothing. Pre-run checks, as run by Claude: (1) inputs read from their
    writers (control.py 378 and 400, boundary.py 334 and 357, sigma.py 361
    and 382, audit.py A2 and A3 print formats); (2) every failure a named
    exit (fixture: manifest mismatch 2, unknown verdict 2, audit.py with a
    write mode 2, audit.py exit 7 gives 3, silent audit.py gives 4, bad
    --workers 2, missing archive 2); (3) input contact on the real deposit,
    structural only: 68 files match zenodo-v1.sha256, all nine published
    patterns found as expected in zenodo-v1/sn-article.tex, audit.py has no
    write call, five N_BOOT assignments and both range() arguments found;
    control 72 rows in 4 groups of 18, boundary 144 in 8 of 18, sigma 288 in
    2 of 144, every verdict string known; (4) synthetic fixture end to end
    (fake summaries, the deposited audit.py and tex copied into the
    scratchpad), exit 0, both the reproduces and the does-not-reproduce
    paths reached. Python 3.8 grammar parse passes. Nothing synthetic is
    committed.
  - RESULT 2026-10-30. Source: logs/depositcheck-20261030.log (run by
    Rahul on the laptop, exit 0; Python 3.12.3, NumPy 2.5.3, 2 workers;
    script sha256 d1e70972...f356). P1 "68 files hash to
    zenodo-v1.sha256: PASS"; P2, P3 PASS. P4 as printed: control.py,
    boundary.py, sigma.py N_BOOT = 400; audit.py A2 range(500); A3
    range(N_BOOT), N_BOOT = 2000; crossed.py N_BOOT = 400 (A3 uses only
    its slopes). audit.py wall 11.1 s, exit 0. SUMMARY block:
    - Table 4: reproduces (control.py, 400). All four means within R2
      (deposited -1.00169, -0.99801, -0.83201, -0.81480) and all twelve
      counts equal.
    - Table 5: reproduces (boundary.py, 400). All eight means, SDs and
      counts; "all" 117/144, 107/144, 125/144; caption 123/144. ci_hi <=
      -0.85 gives 117/144, as the verdict column.
    - 7.10 counts: reproduces (sigma.py, 400). Isotropic 71/93/115,
      Bonferroni cost 11 (93 - 82); anisotropic 57/77/86, cost 9 (77 -
      68).
    - 7.10 coefficients: reproduces (audit.py A2, 500, NumPy 2.5.3).
      Isotropic d 10: tau_0 0.1 -0.0470 [-0.102, -0.002]; tau_0 0.01
      -0.0575 [-0.121, -0.015]; the three verdict claims hold (6 of 6, 2
      of 2, 2 of 2). Isotropic d 40, about which the text says nothing:
      "effect of practical size possible" at both tau_0.
    - 7.11 counts: reproduces (audit.py A3, 2000, NumPy 2.5.3). Arm A 18
      cells: equivalent 3, inconclusive 13, outside 2.
    - NOT LOCATED: the six gaps of tex 497 (+0.004, +0.009, +0.024;
      -0.005, +0.034, +0.014) are "within R2 at no level" of A3's arm-A
      gaps in every one of the six (d, tau_0). For example d 40, tau_0 0.1:
      published +0.024, audit 0.0187, 0.0300, -0.4365 at sigma 0.1, 0.2,
      0.4. Per R7 no other construction was tried. They are untraced,
      and they belong with the N30 list (group C of the disclosure).
    - Reading. The published counts follow from the deposited files and
      code at the resample counts that code sets. What was false at tex 309
      is "4000 resamples" and "the single archived re-analysis script",
      not the traceability of these numbers. Tables 4, 5 and the 7.10
      counts are tallies with no random draw; the 7.10 coefficients and
      the 7.11 counts are a resampling reproduction on NumPy 2.5.3, and
      the NumPy of the original audit run is not recorded. A tally shows
      the counts follow from the stored per-cell intervals; it does not
      re-derive those intervals (no per-realization data, ARC2).
  PROPOSED DISCLOSURE TEXT (Rahul's instruction 2026-10-30; not applied;
  groups A, C and D as in the reply of 2026-10-30, group B rewritten
  from this result; the tex 497 gaps moved from B to C, Rahul
  2026-10-30, because they are numbers with no identifiable source and
  keeping them in B would soften the finding):
    The deposit of the earlier version does not support several statements
    made about it. That version said every reported interval was a
    4000-resample value from one archived re-analysis script, and that no
    interval came from a computation outside the archive. Both statements
    are false, but most of the numbers they describe can be traced. The
    re-analysis script recomputed at 4000 resamples only the paired gaps,
    severity trends, onset intervals and interaction intervals of the
    regime-map experiments. The remaining counts were computed by the
    deposited generating scripts and by a second deposited script,
    audit.py, at the resample counts that code sets, and they follow from
    the deposited files. The means and verdict counts of the whole-run
    control table (Table 4) and the operating-level table, and the
    tolerance and Bonferroni counts of the condition sweep, are tallies of
    the per-cell intervals that the generating scripts stored at 400
    resamples. The tally involves no random draw. It shows that the
    published counts follow from the stored intervals, but it does not
    re-derive those intervals, for which the deposit holds no
    per-realization data. The regression coefficients of the condition
    sweep (500 resamples) and the equivalence counts of the diffusion
    comparison (2000 resamples) are reproduced by running audit.py
    unchanged on NumPy 2.5.3. The NumPy version of the original run is not
    recorded, so this reproduction comes from one installation. The
    regime-map counts equal the console output of regimemap.py at 400
    resamples, a log that was not deposited.
    The intervals of the calibrated-concentration table (Table 3), its
    regression and its pairwise contrasts, including the separation of
    +0.1940 and the interval [0.117, 0.381], the slope-SE reference scale,
    the value 0.078 and the interval [0.0069, 0.2087] of the
    per-size-temperature experiment were produced by code that was not
    deposited, and the statement that every pre-specified criterion is in
    the docstring of an archived script does not hold for them. Their
    point estimates recompute from the deposited files, except 0.078,
    which the deposited data give as 0.07747. The construction of those
    intervals cannot be identified. The six per-dimension gaps quoted for
    the diffusion comparison at matched noise level have no identifiable
    source either: none equals the gap the deposited code reports at any
    of the three noise levels.
    The earlier version also said the re-analysis had been run on two
    installations that agreed to four decimals. One such run has a console
    log, and that log was not deposited. It said that a re-analysis script
    recomputes the noise floor, the fitting-window sensitivity, the
    equivalence tests, the change-point intervals and the tolerance and
    Bonferroni tables. audit.py prints them but writes no file and was run
    with no deposited log, and the re-analysis script itself states that
    it does not recompute the operating-level tolerance table. It said
    console logs are archived for the rows marked with a dagger in the
    experiment table; that table marks no rows. It said console logs and
    per-realization files were archived for every confirmatory run. The
    deposit contains no console log, and eight experiments are deposited
    as cell-level means.
    It described the isotropic and anisotropic arms as paired, but the
    scripts gave them different seeds. No number from the earlier version
    is reused here. Every number in this paper comes from the rerun
    described in Section X, whose scripts, console logs and
    per-realization files are deposited at [DOI].
    (Paragraphs: B, C, A, D. Four fixes applied 2026-10-30 at Rahul's
    instruction: Table 4 / Table 3 naming; C completed to the N30 list
    and the 719 docstring claim; A withdraws the 719 recompute sentence,
    with "audit.py prints them" (Rahul's wording); A adds the dagger
    rows, ARC5.)
  DECIDED (Rahul, 2026-10-30): the disclosure appears in three places.
  PLACEMENT: inside the paper's account of its relationship to the
  earlier version, as the first part of that account, under its own
  heading, before any results. The scientific withdrawals follow it,
  separately, each with its own reason (the claim withdrawn on the N1
  ground; round 1's onset claim, N43). Reason: the account answers
  what of the earlier version still stands, and the disclosure's last
  sentence (no earlier number used) is its premise; a separate section
  would leave two lists to reconcile and read as an erratum; kept
  separate inside it because deposit failures and wrong scientific
  claims are different kinds and blended each would dilute the other.
  MAIN-TEXT VERSION (about 150 words; not applied):
    The deposit of the earlier version (DOI 10.5281/zenodo.22068685) does
    not support four kinds of statement that version made about it. It
    said every reported interval was a 4000-resample value from one
    archived re-analysis script. Most of its counts were in fact computed
    by other deposited scripts at 400, 500 or 2000 resamples. They follow
    from the deposited files and code, but only from per-cell intervals
    that the deposit stores and cannot re-derive, and two of them have
    been reproduced on a single installation only. Some intervals and
    values, among them those of the calibrated-concentration experiment
    and the value 0.078, came from code that was not deposited, and how
    they were computed cannot be identified. The earlier version also said
    console logs, per-realization files and a check on a second
    installation were archived; none of these is in the deposit. It
    described the two diffusion arms as paired, and they were not. No
    number from the earlier version is used in this paper. Supplementary
    Section S1 lists each statement, what the deposit holds, and how this
    was established.
  WHY THE SHORT VERSION OMITS WHAT IT OMITS. It leaves out the
  table-by-table mapping and resample counts; the untraced items other
  than 0.078; 0.07747; reboot.py's NOT RECOMPUTED; the 30-gap scope of
  the resample claim; the dagger rows; the docstring and change-point
  sentences; the undeposited regime-map log. Three rules:
  1. Every kind of false statement is named, in its true direction
     (provenance; no deposited code; absent evidence; pairing). Only
     instances are omitted, never a kind of failure.
  2. No qualification of a favourable statement is dropped. "They
     follow from the deposited files" keeps both limits (stored
     intervals not re-derivable; two items on one installation).
     Omitting a failure's detail is compression; omitting a limit on a
     favourable claim would be concealment.
  3. Nothing in this paper depends on the omitted detail: no earlier
     number is used, so the detail bears on the earlier version, and
     the paragraph names where it is.
  Test: a reader of the paragraph alone holds no belief that S1
  contradicts. Checked sentence by sentence against S1.
  SUPPLEMENT VERSION, S1 (about 900 words; not applied):
    S1. The deposit of the earlier version
    S1.1 How this was established. Each statement below was checked
    against the 68 files of the deposit, after verifying them against
    their checksums. Where a console log is named, it comes from the
    author's earlier machine. The two scripts written for this check,
    depositcheck.py and n30_reconstruct.py, are deposited with this paper
    together with their console logs. Each one fixed its comparison rules
    before it was first run, and neither searched for a setting that would
    make a published number match.
    S1.2 Numbers that trace, under a false description.
    (a) Section 6 said: "every interval reported in this paper is the
    4000-resample value emitted by the single archived re-analysis script,
    so that no reported interval originates from a computation that is not
    in the archive." The re-analysis script, reboot.py, recomputes at 4000
    resamples only these, from Sections 7.12 and 7.15: the paired gaps,
    the severity trends, the onset intervals and the interaction
    intervals. The other numbers come from elsewhere:
    - Table 4 (Section 7.4): the means and verdict counts follow from
    control_summary.csv. control.py computed the per-cell intervals at 400
    resamples. This is a tally, with no random draw.
    - Table 5 (Section 7.5), including the caption's 123/144: these follow
    from boundary_summary.csv. boundary.py computed them at 400 resamples.
    This is a tally.
    - Section 7.10, tolerance and Bonferroni counts: these follow from
    sigma_summary.csv. sigma.py computed them at 400 resamples. This is a
    tally.
    - Section 7.10, regression coefficients and intervals: these come from
    audit.py at 500 resamples. Running audit.py unchanged on NumPy 2.5.3
    reproduces them.
    - Section 7.11, equivalence counts (3 equivalent, 13 inconclusive, 2
    outside): these come from audit.py at 2000 resamples. It resamples
    over objectives and does not pair the arms. Running it on NumPy 2.5.3
    reproduces them.
    - Section 7.12 counts: these come from regimemap.py at 400 resamples.
    They equal that script's console output on the earlier machine, and
    that log was not deposited.
    A tally shows that the published counts follow from the per-cell
    intervals stored in the deposit. It does not re-derive those
    intervals, because the deposit holds no per-realization data for these
    experiments. The NumPy version used for the original audit.py run is
    not recorded.
    (b) Section 6 said: "every trend interval in this paper is recomputed
    ... at 4000 resamples." This is true for the severity trends of
    Section 7.15. It is false for Section 7.10, which used 500 resamples,
    and for Section 7.3, which is covered in S1.3.
    (c) Section 6 said that moving from 400 to 4000 resamples moves an
    interval endpoint "by less than 0.02 and no equivalence verdict
    changes". The reboot.py log shows this only for the 30 paired gaps of
    Section 7.15: "largest endpoint shift: 0.0163", "verdicts changed: 0".
    It was not shown for any other interval.
    S1.3 Numbers with no identifiable source. The following were produced
    by code that is not in the deposit:
    - (a) the intervals of Table 3 (Section 7.3);
    - (b) the regression intervals of Section 7.3, which the abstract and
    conclusions also quote; its three pairwise contrasts; and the
    full-grid separation +0.1940 [+0.0682, +0.3105];
    - (c) the interval [0.117, 0.381] (Sections 7.3 and 7.13);
    - (d) the value 0.078 (abstract, Sections 7.3 and 7.14, conclusions),
    which the deposited data give as 0.07747;
    - (e) the slope-SE reference scale 0.0260, with interquartile range
    [0.0191, 0.0341] (Section 1.2). The 0.05 equivalence margin of Section
    6 was based on it, and no single specification reproduces the value
    and the range together;
    - (f) the interval [0.0069, 0.2087] of the per-size-temperature
    experiment (Section 7.14);
    - (g) the six per-dimension anisotropic-minus-isotropic gaps of
    Section 7.11. None of them equals the gap the deposited code reports
    at any of the three noise levels.
    Where these items have point estimates, those recompute from the
    deposited files, except in (d), (e) and (g). How the intervals were
    computed cannot be identified. Appendix A said every pre-specified
    criterion is stated in the docstring of an archived script; that does
    not hold for any of (a) to (g).
    S1.4 Statements about evidence that does not exist.
    - (a) Section 6 said the re-analysis was run on two installations,
    NumPy 1.24.4 with Python 3.8.10 and NumPy 2.4.4 with Python 3.12.3,
    and that they agree to four decimals. There is one console log, from
    NumPy 1.24.4 on the earlier machine, and it was not deposited. No log
    of a NumPy 2.4.4 run exists.
    - (b) Appendix A said a re-analysis script recomputes the noise floor,
    the fitting-window sensitivity, the equivalence tests, the
    change-point intervals, and the tolerance and Bonferroni tables.
    audit.py prints them, but it writes no file, and no log of it was
    deposited. reboot.py states in its own output that it does not
    recompute the Section 7.5 table. The change-point intervals audit.py
    prints are not quoted anywhere in the earlier version.
    - (c) Appendix A and the Data availability statement said console logs
    are archived for the rows of Table 2 marked with a dagger. Table 2
    marks no rows, and the deposit contains no console log.
    - (d) Appendix A said per-realization CSV files are archived for every
    confirmatory run in Table 2. Eight experiments (control, boundary,
    sigma, crossed, cliff, mechanism, ess_surface, visibility) are
    deposited as means per cell and ensemble size, and the regime files
    hold one row per cell.
    S1.5 Statements the deposited code contradicts. The pairing claims are
    false: Section 6, "Where two arms share seeds the resample is paired";
    Section 7.11, the trace ratio "paired on the shared realization
    index", over 180 pairs; Section 7.15, the paired gaps and their
    intervals. The archived scripts gave the isotropic and anisotropic
    arms different seeds, so every one of these comparisons is between
    independent runs.
    S1.6 What this paper does. No number from the earlier version is
    reused. Every number comes from the rerun described in Section X. Its
    scripts, console logs and per-realization files, and the checks in
    S1.1, are deposited at [DOI].
  V2 DEPOSIT DESCRIPTION (not applied):
    Version 2 accompanies a new manuscript that replaces the one version 1
    supported. The version 1 files are unchanged. The paper they
    accompanied made several statements about them that the files do not
    support. It said every reported interval was a 4000-resample value
    from one re-analysis script; console logs and per-realization files
    were archived for every confirmatory run; the re-analysis had been
    checked on a second installation; and the isotropic and anisotropic
    arms were paired. Some of its numbers came from code that is not in
    version 1. Supplementary Section S1 of the new paper lists each
    statement and what the files show. This version holds the scripts,
    console logs and per-realization files of the rerun on which every
    number in the new paper rests, together with the scripts and logs of
    the checks in S1. It also holds four console logs from the author's
    earlier machine that S1 cites, unchanged and with their original
    checksums: logs_reboot.log, logs_M_full.log, logs_perjcal_full.log and
    logs_exact_full.log.
  V2 DEPOSIT MUST HOLD, for S1 (Rahul, 2026-10-30). Reason: a
  disclosure resting on logs the reader cannot see repeats the defect it
  discloses. Every log S1 cites, and what it supports:
  - round1-zip/cbo-gap/logs_reboot.log, sha256 bc3fb23c...e616e: S1.2(a)
    (what reboot.py recomputes at 4000), S1.2(c) (0.0163, verdicts
    changed 0), S1.4(a) (the one NumPy 1.24.4 run), S1.4(b) (NOT
    RECOMPUTED).
  - round1-zip/cbo-gap/logs_M_full.log, sha256 797f48a1...a0a5: S1.2(a),
    the Section 7.12 counts equal regimemap.py's console output.
  - round1-zip/cbo-gap/logs_perjcal_full.log, sha256 ac41b574...d471:
    S1.3(f), the intervals perjcal.py does print (0.0156 [0.0010,0.0576],
    0.0964 [0.0059,0.2265]), against which [0.0069, 0.2087] is untraced.
  - round1-zip/cbo-gap/logs_exact_full.log, sha256 690256de...89afc: the
    positive control (R6) of n30_reconstruct.py reads it, so S1.3 rests
    on it. Not named in Rahul's list; found from the script's R6.
  - logs/n30-20261015-2201.log with scripts/n30_reconstruct.py: S1.1,
    S1.3(a) to (e) (0.07747; specifications tried).
  - logs/depositcheck-20261030.log with scripts/depositcheck.py: S1.1,
    S1.2(a) (Tables 4, 5, 7.10, 7.11), S1.3(g), S1.4(b) (audit.py
    prints them; appendix).
  - n30_reconstruct.py imports measlib.py, which imports cbopaths.py and
    detcheck.py; all three go in with it, or it does not run.
    depositcheck.py imports nothing outside the standard library and
    NumPy.
  - S1.5 (pairing) rests on the version 1 scripts' seed tables, which are
    in version 1; no log.
  Full checksums are in round1-zip.sha256 lines 110, 112, 115, 116.
  OPEN until the disclosure is written in the manuscript pass (N45).
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
  CLOSED 2026-10-30 (stale condition met): scripts/calprec2.py, committed
  in 203a564, derives every stream as default_rng(SeedSequence(key +
  (chunk,))) over the full key (docstring, line 406 at the time of this
  entry); no 32-bit reduction. Its production table is b663797 (N28).
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
  CLOSED 2026-10-30 (stale condition met): calprec v2 ran on the four rows;
  finalize b663797, calprec2_beta.csv, 336 cells (309 target, 27 beta).
  The later extension to the regimemap cells is N41.
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
  CLOSED 2026-10-30 as to the rerun: decided in notes/ANALYSIS_CRITERIA.md
  5a ("This settles the decision N31 left open"; commit aaf7aa4): the
  rerun's seed key omits the diffusion coordinate in the paired rows
  (rerunlib PAIRED). Checked by Claude on ONSET-R only: across the ten
  shard rerun_real.csv files, 24480 ok rows, all 12240 (objective, d, r,
  rep) pairs carry the same seed_key in both arms. The manuscript
  consequence (round 1's pairing claims at tex 309 and 650 were false
  for the archived runs) is carried to N45.
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
  CLOSED 2026-10-30 (stale condition met): scripts/rerun_analysis.py,
  committed in db25e41 before its first execution, ITEM 4: the rate
  verdict is the one-sided 95% upper bound <= -1, with "No monotonicity
  claim, no tolerance count, no N_vis, no -0.85"; dimension changes are
  signed (contrast 1, d40 - d2) and resampled within cells, never an
  absolute value. The supplement labelling is carried to N45.
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
  CLOSED 2026-10-30 (stale condition met): scripts/rerun_analysis.py
  (db25e41, before first execution), ITEM 0: S-slope, the mean of the
  realization slopes, is primary for every verdict; S-curve, the slope of
  the mean curve, is a secondary column read by no verdict; worked
  example given. The manuscript must name the estimand of every number
  (carried to N45).
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
  CLOSED 2026-10-30, not run (Rahul's decision, C2; recorded in N45).
  The full probe and perjcal's rows are not run. Reason: referee point
  4 says the per-J-beta design "controls this quantity, but then the
  fitted curve is obtained from a family of different algorithms rather
  than from one algorithm at different ensemble sizes", and that "the
  fixed-beta experiment suggested above seems necessary". A per-J-beta
  rerun, at any precision, measures that family of algorithms, so it
  cannot answer the question the referee asked. The fixed-beta experiment
  is CONC, and it has run (N39, N44). Round 1's run was inconclusive
  (0.0964 [0.0059, 0.2265] at tau_0 0.01, N34), and P-C1 to P-C3 would
  be set only now, after the fixed-beta results have been seen.

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
  DECIDED (Rahul, 2026-10-30, C1): the comparison is dropped. Reasons:
  the new paper's estimand is the fixed-beta algorithm at the
  concentration it reaches, and the comparison answers only round 1's
  question (how far the protocol change moved the result, "moved the
  statistic by 0.300"); its value was as a paired measurement, which N40
  shows does not exist; an unpaired interval (referee point 7's other
  option) still cannot be read causally. Removing the sentence answers
  referee point 7. PROBEARM is a legitimate fixed-beta algorithm (one
  probe beta per cell, fixed seed 999 in mechanism.beta_for_target), at
  a concentration other than its nominal tau_0; its results go to the
  supplement as a record of the probe protocol, not as wrong.
  The supplement must say, about the probe protocol:
  1. What it was: mechanism.beta_for_target bisects beta until a probe
     sample of 4000 particles (fixed seed) has ESS fraction tau_0; that
     beta is used unchanged for the reference ensemble and its
     subensembles.
  2. Why that does not calibrate the reference: the probe's fraction
     belongs to that sample and that size; target concentration is not
     achieved concentration, and the protocol never checked the second.
  3. How large the miss is, from the rerun (scripts/refratio.py, the
     section 8.5 reference ratios), not round 1's untraced [0.117, 0.381]
     (N8, S1.3(c)).
  4. What it did to round 1: the probe-calibrated results (0.553
     residual, 0.174 spread) were at an unknown concentration; "moved by
     0.300" compared independent runs; both withdrawn, neither reused.
  5. What the rerun's PROBEARM row is: designed as paired (N17), the
     layout prevented it (N40); its results are a record of the probe
     protocol, labelled by achieved concentration, with no contrast
     against CONC.
  CLOSED 2026-10-30 as a decision; the text is under N45.
  - scripts/refratio.py (written 2026-10-30, Rahul's instruction): reads
    audit_ref_ratio (rerunlib.audit_one: ESS_0(J_inf)/J_inf/tau_0 of the
    redrawn reference under the row's beta) for PROBEARM, GEOM and CONC
    from the committed shard folders; gate R2 against
    runs/rerun-analysis-20261030-144722/analysis_audit.csv; per cell, mean
    with a 95% bootstrap interval over realizations (B 10000) against 1;
    each row against 1, no row-against-row contrast. Writes nothing.
    Pre-run checks, as run by Claude: (1) inputs read from their writers
    (rerun.py REAL_COLS; rerunlib.audit_one; rerun_analysis AUDIT_COLS
    and its ref.mean() in rep order); (2) every failure a named exit
    (fixture: gate mismatch 3, F1 not ok 2, duplicate (cell, rep) 2,
    tampered file 2, no --runs 2, folder given twice 2, a row absent 2);
    (3) input contact on the six real folders (rerun-arch s0 to s3,
    rerun-cal s0 and s1), structural only: every sha256.txt verifies;
    PROBEARM 2160 rows in 144 cells, GEOM 4032 in 336, CONC 2160 in 144,
    every row end ok, F1 ok; the cell keys and n equal
    analysis_audit.csv's; reps 0..n-1 in every cell; no mean compared or
    printed; (4) synthetic fixture end to end (fake ratios, real schema),
    exit 0, reaching above 1, below 1 and contains 1. Python 3.8 grammar
    parse passes. Nothing synthetic is committed.
  - RESULT 2026-10-30. Source: logs/refratio-20261030.log (run by Rahul,
    exit 0; Python 3.12.3, NumPy 2.5.3, 2 workers; script sha256
    b6ee1ca5...082a). Six folders verified; R2 PASS for PROBEARM 144,
    GEOM 336, CONC 144 cells. SUMMARY, copied (cells; above 1 / below 1 /
    contains 1; median, min, max of cell means):
    - PROBEARM tau_0 0.5: 48; 25/16/7; 1.0027, 0.9041, 1.0446. tau_0 0.1:
      48; 17/22/9; 0.9977, 0.5584, 1.1247. tau_0 0.01: 48; 13/28/7;
      0.9071, 0.1373, 1.2973; by d at 0.01, medians 1.0138 (d 2), 0.8754
      (5), 0.9021 (10), 0.6154 (40). Lowest cells are centred-law: ackley
      d 40 0.1373 [0.0987, 0.1768], d 10 0.1965, d 5 0.2226; rosenbrock d
      40 0.1894; levy d 40 0.2090. All 144: 55/66/23.
    - GEOM tau_0 0.01: 42; 10/26/6; 0.8282, 0.1989, 1.6591; d 5 median
      0.8517 (3/9/2), d 10 1.1858 (7/3/4), d 40 0.4105 (0/14/0, range
      0.1989 to 0.8028). d 40 medians by tau_0 0.01 to 0.3: 0.4105,
      0.5926, 0.6820, 0.7780, 0.8337, 0.8829, 0.9492, 0.9757. d 10 is
      above 1 in 7 to 12 of 14 cells at tau_0 0.01 to 0.1. All 336:
      107/184/45.
    - CONC tau_0 0.5: 48; 16/26/6; 0.9958, 0.9656, 1.0352. tau_0 0.1: 48;
      21/10/17; 1.0062, 0.9417, 1.0641. tau_0 0.01: 48; 10/3/35; 1.0155,
      0.9597, 1.6217; d 40 5/0/7, median 1.1191. Highest: ackley centred
      d 10 1.6217 [1.2344, 1.9948] (sd 0.7643, realizations 0.3957 to
      2.7532), d 5 1.4153, d 40 1.3905; rastrigin centred d 40 1.2876;
      griewank d 40 1.2305 and 1.1852. All 144: 47/39/58.
  - Reading (Claude, 2026-10-30). The script tests means; calprec2
    calibrates the median reference fraction over six draws to within 5%
    (calprec2.py C6, line 213). CONC's spread at tau_0 0.5 and 0.1 lies
    within 0.94 to 1.07; its above-1 means at tau_0 0.01 have large SDs
    and are consistent with a right-skewed fraction whose median is on
    target, but the log prints no per-cell median, so that is not shown.
    The probe misses grow as tau_0 falls; at tau_0 0.01 they are mostly
    below 1 (the reference more concentrated than intended), largest in
    the centred law and at d 40, not monotone in d (PROBEARM d 5 median
    below d 10's; GEOM d 10 above 1, d 5 and d 40 below).
  - CORRECTION TO RAHUL'S WORDING (2026-10-30, recorded at his
    request): his "the probe protocol misses its target at tight targets
    and high dimension" overstates the second part. The miss grows as
    tau_0 falls, but it is not monotone in d: PROBEARM's d 5 median
    (0.8754) is below its d 10 median (0.9021) at tau_0 0.01, and GEOM's
    d 10 misses above 1 while d 5 and d 40 miss below. The largest misses
    are at d 40 in both probe rows. The supplement must not say the miss
    worsens with dimension. Supported wording: the miss grows as tau_0
    falls; at tau_0 0.01 single cells reach 0.14 of target; it goes in both
    directions; it is largest at d 40 in both probe rows.
  - scripts/refratio2.py (written 2026-10-30, Rahul's instruction; a
    second script, refratio.py and logs/refratio-20261030.log are kept).
    Adds per-cell medians with their own bootstrap interval (same
    resamples), a point reading "median within 5%" mirroring calprec2 C6
    in form only, and TAU8. Rows audited, read from the code rather than
    assumed: rerunlib.AUDIT_ROWS = CONC, PROBEARM, TAU8, GEOM; SIGMA and
    ANISO were not audited (audit_ref_ratio empty in every shard row), so
    they cannot be added. v1's seed rule and row codes are kept, so the
    PROBEARM, GEOM and CONC means and intervals equal v1's by
    construction. Same gate as v1 against the twenty-one-row analysis.
    Pre-run checks, as run by Claude: (1) inputs from their writers, as
    v1 plus AUDIT_ROWS (rerunlib line 183); (2) named exits on fixtures:
    gate mismatch 3, F1 not ok 2, duplicate 2, tampered file 2, no --runs
    2, a row absent 2; (3) input contact on the six real folders,
    structural only: manifests verify; PROBEARM 144, GEOM 336, CONC 144,
    TAU8 144 cells (TAU8 2160 rows, n 15); cell keys and n equal
    analysis_audit.csv's; reps 0..n-1; no statistic computed or printed;
    (4) synthetic fixture end to end, exit 0, including a right-skewed
    cell whose mean interval is above 1 while its median interval
    contains 1. Python 3.8 grammar parse passes. Nothing synthetic is
    committed.
  - RESULT v2 2026-10-30. Source: logs/refratio2-20261030.log (run by
    Rahul, exit 0; Python 3.12.3, NumPy 2.5.3). R2 PASS for PROBEARM 144,
    GEOM 336, CONC 144, TAU8 144 cells. The mean verdict totals equal v1's
    (PROBEARM 55/66/23, GEOM 107/184/45, CONC 47/39/58), as the shared
    seed rule requires. SUMMARY, copied (mean a/b/c; median a/b/c; cells
    with median within 5%; median, min, max of cell medians):
    - CONC tau_0 0.5: 16/26/6; 16/25/7; 48 of 48; 0.9959, 0.9650, 1.0380.
      tau_0 0.1: 21/10/17; 18/9/21; 44 of 48; 1.0066, 0.9408, 1.1449.
      tau_0 0.01: 10/3/35; 7/1/40; 33 of 48; 1.0156, 0.9713, 1.6771; by
      d, within 5%: 12 (d 2), 11 (5), 7 (10), 3 (40); d 40 median 1.1323.
      Highest medians: ackley centred d 10 1.6771 [1.0529, 2.4114], d 5
      1.4644 [0.7892, 1.8313], d 40 1.3596 [1.0030, 1.9053]; rastrigin
      centred d 40 1.3161. All 144: median within 5% 125.
    - TAU8, median within 5% (of 18; of 6 at d 40) by tau_0 0.01, 0.02,
      0.03, 0.05, 0.07, 0.1, 0.2, 0.3: 10, 11, 11, 12, 14, 14, 17, 18; d 40:
      1, 2, 2, 2, 4, 4, 6, 6. d 40 medians of cell medians: 1.2662,
      1.1087, 1.0712, 1.0410, 1.0287, 1.0245, 0.9927, 0.9846. tau_0 0.1,
      all d: 0.9711 to 1.1423. tau_0 0.01, d 40: ackley 1.7082 [1.4028,
      1.8459], sphere 1.3265, rastrigin 1.2791, levy 1.2534 [1.1592,
      1.3361], griewank 1.2188, rosenbrock 0.9504. tau_0 0.02, d 40: all
      six medians >= 1.0031 (ackley 1.5367, rastrigin 1.3368, levy 1.1453,
      sphere 1.0722, griewank 1.0125, rosenbrock 1.0031); three median
      intervals above 1 (ackley, rastrigin, levy). All 144: within 5% 107.
    - PROBEARM tau_0 0.01 medians by d: 1.0149, 0.8744, 0.9158, 0.6234;
      lowest cell median 0.1355. GEOM tau_0 0.01 d 40: medians 0/13/1,
      none within 5%, median of medians 0.4584.
  - Reading (Claude, 2026-10-30):
    - The medians do not show a right tail behind CONC's high means: the
      high cells are as high in the median (ackley centred d 10 mean
      1.6217, median 1.6771). It is a miss at the run's reference size.
      calprec2 calibrates on six references of 64,000,000 particles (C5m,
      D1 and C6 at N_LO; calprec2.py 115 to 129, 213); every CONC and TAU8
      run uses J_inf 50000 (plan). At tight targets and d 40 the fraction
      at 50000 lies above the 64M value. Not adequate cells contribute
      (CONC tau_0 0.01: 4 of 12 at d 40 and 2 of 12 at d 10 are "beta, not
      adequate"; ackley d 40 centred among them), but adequate cells miss
      too (TAU8 levy d 40 tau_0 0.01, label "target", median 1.2534).
    - TAU8 at d 40 misses above target for tau_0 0.01 to 0.1, shrinking
      as tau_0 loosens; the six 0.02 medians all lie above 1. Systematic,
      not noise. At tau_0 0.2 and 0.3 every d 40 median is within 5%.
    - The PROBEARM wording and the GEOM decision stand on the medians.
  - ADAPT (read 2026-10-30, control.py and the shards):
    - Fixed arm's beta: beta0, bisected on a 4000-particle probe drawn
      with default_rng(999 + 131 d) so that its ESS fraction is tau_0
      (control.py 333 to 336), then held for the whole run. The adaptive
      arm starts from the same beta0 but re-solves on the reference
      ensemble before the first step (control.py 230 to 231, goal
      log(tau_0 J_inf)), so at t = 0 it is on target on its reference and
      the fixed arm is at the probe's miss.
    - The fixed arm's achieved initial concentration is recorded for every
      realization: rerun.py stores one_realisation's le0 (log ESS of the
      run's own reference at the first step) in the extras column of every
      ADAPT row, both arms (example: fixed, tau_0 0.1, le0 8.441383...).
      Ratio = exp(le0) / (tau_0 J_inf). No redraw and no audit are needed;
      the adaptive arm's ratio is 1 by construction, a positive control.
      CORRECTION: Claude's reply of 2026-10-30 said measuring ADAPT would
      need new redraw code for control.py. It does not.
    - The rerun's ADAPT arms are not seed-paired: of 540 (objective, d,
      tau_0, rep) pairs, 0 share seed_key (round 1's control.py shared
      seeds between arms, line 346). No fixed-against-adaptive contrast
      was pre-registered (ANALYSIS_CRITERIA, "No contrast in ADAPT").
    - DECIDED (Rahul, 2026-10-30): the fixed-against-adaptive comparison
      is dropped. Reasons: the arms are not seed-paired in the rerun; no
      contrast was pre-registered; they differ at t = 0 by construction
      (fixed arm at the probe's miss, adaptive on target). None is fixable
      by running more of the same design. Each arm's own pre-registered
      slope and bound stay; the adaptive arm is a diagnostic (a
      time-varying beta is not the analysed algorithm); the fixed arm's
      tau_0 is labelled by its measured starting ratio (adapt0.py).
    - scripts/adapt0.py (written 2026-10-30): from extras le0, le_min,
      le_max of every ADAPT realization, ratio0 = exp(le0)/(tau_0 J_inf)
      and control.py's drift. Gates: adaptive |ratio0 - 1| <= 1e-6 (a
      positive control, exit 3); fixed b_first equal to the row's beta
      (exit 3). Fixed arm per cell: mean and median with 95% bootstrap
      intervals, verdicts against 1, median within 5% as a point value;
      drift per arm described, no comparison. Writes nothing. Pre-run
      checks, as run by Claude: (1) inputs from their writers
      (control.one_realisation's return, control.py 230 to 231, 333 to
      336 and 377; rerun.py's extras); (2) named exits on fixtures:
      positive control off 3, b_first mismatch 3, missing extras key 2,
      unpaired arms 2, tampered file 2, no --runs 2; (3) input contact on
      the four rerun-arch folders, structural only: 1080 ADAPT rows, 36
      cells, both arms with reps 0..14 in every cell, R3 holds in every
      fixed realization, tau_0 0.01 and 0.1, d 5, 10, 40, J_inf 50000;
      no ratio computed or printed; (4) synthetic fixture end to end,
      exit 0, reaching above 1, below 1 and contains 1. Python 3.8 grammar
      parse passes. Nothing synthetic is committed.
    - RESULT 2026-10-30. Source: logs/adapt0-20261030.log (run by Rahul,
      exit 0; Python 3.12.3, NumPy 2.5.3, 2 workers). 36 cells, 540
      realizations per arm. "R2 PASS: every adaptive realization within
      1e-06 of 1 (largest |ratio0 - 1| 1.553e-11)"; R3 PASS. Adaptive
      drift 0.0000 (median of cell medians) at both tau_0. Fixed arm,
      SUMMARY (mean a/b/c; median a/b/c; median within 5%; median, min,
      max of cell medians; fixed drift):
      - tau_0 0.01: d 5 2/3/1, 2/3/1, 1 of 6, 0.9426, 0.7688, 1.1617,
        2.9447; d 10 5/1/0, 5/1/0, 0 of 6, 1.7788, 0.2591, 4.6460,
        2.9982; d 40 0/6/0, 0/6/0, 0 of 6, 0.3117, 0.0935, 0.7634,
        2.4794; all 18: 1 within 5%, median 0.8582, 0.0935 to 4.6460.
      - tau_0 0.1: d 5 4 of 6 within 5%, median 0.9784; d 10 2 of 6,
        1.0252, max 1.7330; all 18: 4/12/2 on medians, 7
        within 5%, median 0.9632, 0.5707 to 1.7330; d 40 0/6/0, median
        0.7635.
      - Extremes, per cell: levy d 40 tau_0 0.01 median 0.0935 [0.0794,
        0.1130]; ackley d 10 tau_0 0.01 median 4.6460 [4.0371, 5.8895]
        (realizations 2.0222 to 6.2960); smallest single realization
        rastrigin d 40 tau_0 0.01, 0.0105.
      - In all, 8 of 36 cells have a median within 5% (1 at tau_0 0.01, 7
        at 0.1).
    - Reading (Claude, 2026-10-30): at tau_0 0.01 the fixed arm's cell
      medians under one nominal label run from 0.0935 to 4.6460 of target,
      wider than the tenfold step between the two nominal levels. CONC
      and TAU8 rows also store le0 and le_min in extras (TAU8 also
      le_mean), so the fall of concentration during a fixed-beta run is
      recorded for the calibrated rows themselves. The ADAPT plan rows
      share J_inf 50000, T 1.0, K 100, J10 and M 15 with CONC; the
      control and mechanism realizations use the same update (control.py
      211 to 250, mechanism.py 219 to 240); sigma and dt defaults of the
      two modules were not compared line by line. (Compared 2026-10-31:
      identical, and the rerun passes 0.2 and 0.01 to both; see N45,
      ADAPT.)
  - scripts/sizetest.py (written 2026-10-30, Rahul's instruction: test
    the size reading rather than accept it). --mode plan reads and draws
    nothing; --mode run adds PC and E1. READ: the run's CONC and TAU8
    ratios (refratio2's readers and gate, G1); calprec2_beta.csv's beta,
    label and tau_ref (G2: table beta equals the run beta in every cell);
    E0, calprec2 phase A's 24 beta_solved per (cell, N) at N 4000 to
    4,000,000 against the run beta, with a pre-registered direction
    prediction; measured costs (calprec2 throughput, calprec2 phase C
    peak RSS, costprobe2 trajectory walls at J_inf 50000). MEASUREMENT
    (run mode only): E1, fresh t = 0 draws with calprec2's sampler and
    streamed evaluation at the run beta, keys calprec2.key_of(41, cell,
    N, rep); no trajectory. PC: a committed calprec2 phase C row at 64M
    recomputed to 1e-12 before E1. Classes per cell (SIZE; SIZE, NOT
    CONVERGED; NOT A MISS AT 50000; ELSEWHERE) and J_needed (J1), fixed in
    the docstring. The plan step prints E1's cost per ladder size and the
    larger-reference plan (affected d 40 groups, their measured J_inf
    50000 walls and RSS, what is not measured, the probe needed, the
    rerun's realization count). Writes nothing.
    Pre-run checks, as run by Claude: (1) inputs from their writers
    (calprec2 key_of, f_chunk, chunk_terms, combine_terms, tau_of,
    load_throughput, task columns; finitej.ess_frac and exactcal.
    log_ess_of are the same quantity; costprobe2_results columns); (2)
    named exits on fixtures: PC mismatch 3, G2 beta mismatch 3, 23 phase
    A draws 2, ladder without 50000 2, missing arguments 2; (3) input
    contact, structural only: G3 holds for mechanism, boundary, exactcal;
    calprec2_beta.csv 336 cells; 26 record folders (the NOT A RECORD s2
    attempt excluded), phase A 24 draws per (cell, N), phase C 4032 rows,
    no duplicate task; throughput 90 entries; costprobe2 42 main units
    (mechanism d 2 to 40, boundary d 5 to 40); CONC 144 and TAU8 144 run
    cells all in the table, G2 identity holds; no ratio, median or beta
    ratio computed or printed; (4) synthetic fixture end to end in both
    modes (fake betas, ratios and tables; the real archived samplers;
    calprec2.N_LO patched to 200000 in the fixture process only), reaching
    PC PASS and all four classes. Python 3.8 grammar parse passes.
    Nothing synthetic is committed. OPEN until the plan log.
  - sizetest plan RESULT (Rahul ran it 2026-10-31, laptop, python
    3.12.3, numpy 2.5.3, 2 workers; logs/sizetest-plan-20261031.log;
    exit 0, nothing drawn):
    - G3 PASS; G1 PASS for CONC 144 and TAU8 144 cells; G2 PASS.
    - SEL: 109 selected, affected 56, controls 53 (log line 164).
    - E0: 26 calprec2 folders, phase A tasks 48384, phase C tasks 4032.
      Affected: agrees 48, mixed 5, disagrees 3 (log line 281).
    - Disagrees: TAU8 ackley d 5 tau_0 0.02 (s 0.9259; q 16000 1.0426, q
      64000 1.0261), rastrigin d 10 0.01 (s 0.9259; 1.0423, 1.0169),
      rastrigin d 40 0.05 (s 0.9151; 1.0306, 1.0103). Mixed: CONC levy d
      40 centred 0.1, CONC sphere d 10 centred 0.01, TAU8 ackley d 5 0.05,
      rastrigin d 10 0.07, rastrigin d 40 0.07.
    - E1 plan, Kaggle throughput (calprec2-smoke-kaggle-20261011-121225):
      core s per ladder size 705.0 (50000), 2819.9 (200000), 14099.4
      (1000000), 56397.5 (4000000), 5232 tasks each; PC 70.5 s; total
      core s 74092.2.
    - Larger-reference plan: 31 affected d 40 cells in 15 groups; 5
      mechanism mix-0.1 groups have no costprobe2 unit ("not measured");
      probe of 45 units required first; rerun 465 realizations.
    Reading (Claude, 2026-10-31), read from the log and from
    logs/refratio2-20261030.log, nothing computed:
    - q(4000000) prints 1.0000 in most cells by construction: calprec2's
      beta_adq is the median of the 24 phase A betas at 4,000,000
      (calprec2.py 118), so where the run beta is beta_adq the top rung
      is the run beta itself. The informative levels are 16000 and 64000.
    - The fall of q towards 1 is not monotone in every cell. Example:
      CONC ackley d 40 centred 0.01, q 1.2216, 1.1059, 1.0180, 1.0294,
      0.9890, 1.0000.
    - The three disagrees: each run median is below 1, but its 95%
      interval contains 1 and reaches above it (refratio2, TAU8 per cell:
      ackley d 5 0.02 median 0.9300 [0.8734, 1.1025], sd 0.2574;
      rastrigin d 10 0.01 0.9142 [0.7452, 1.1046], sd 0.3100; rastrigin d
      40 0.05 0.9198 [0.7852, 1.1138], sd 0.2591). Their neighbours at the
      adjacent tau_0 have run medians above 1 (ackley d 5 0.01 1.2050,
      0.03 1.1145; rastrigin d 10 0.02 1.0849; rastrigin d 40 0.03
      1.2800, 0.07 1.0586). They are not misses resolved by 15
      realizations; SEL selected them on the point median (refratio2 R5:
      "a point value, not a test"). E1's H1 at 50000 tests this reading.
    - The five mixed: four have run-median intervals containing 1 (CONC
      sphere d 10 0.01 [0.9527, 1.0674]; TAU8 ackley d 5 0.05 [0.8329,
      1.2338]; rastrigin d 10 0.07 [0.9715, 1.0799]; rastrigin d 40 0.07
      [0.9923, 1.1269]). CONC levy d 40 centred 0.1 is resolved above 1
      (1.0594 [1.0155, 1.0883]) while its q is 1.0088, 0.9905, 1.0075,
      1.0043, 1.0016, 1.0009 from 4000 to 4000000: E0 cannot explain it.
    - CORRECTION (Claude): the plan's "peak RSS bound, calprec2's
      measured peak for the same streamed evaluation (phase C, N 64M)"
      is mislabelled. Phase C at 64M holds replicate 0 in memory for
      calprec2's streaming-equivalence check (calprec2.py E1), and that
      held array is what the 2497.5 to 2560.7 MB peaks are. E1 here
      streams only. The streamed-only figure is not printed by this
      version; the rewrite prints it from calprec2's rows that hold
      nothing. The label is fixed in the rewrite.
  - DECIDED (Rahul, 2026-10-31): E1 runs on Kaggle, CPU only, in the
    resumable queue; smoke first; a shard's exit 5 resumes from its own
    folders; the same halt rules. Ladder 50000, 200000, 1000000, 4000000
    and 48 draws kept (not trimmed).
  - scripts/sizetest.py rewritten 2026-10-31, before any E1 draw (the
    single-process --mode run was never executed and is removed). Modes:
    plan (laptop; as before, plus the corrected RSS figure, the shard
    schedule S1/S2/T1/G-STOP, and --write-plan, which writes
    runs/sizetest-plan-<stamp>/ with sizetest_e1_plan.csv and
    sizetest_plan_params.csv, PF); smoke (Kaggle; G-FORK, G3, V2S, PF,
    PC, one kind-42 draw per unit at the largest N, SM1); e1 (Kaggle; one
    shard; PC first; calprec2's scheduler with timeout and --stop-after;
    resume RS under rule 17; one row per draw in sizetest_e1.csv); analyse
    (laptop; A1 completeness, then H1, J1 and the classes). E1 keys
    unchanged (kind 41). Rules and worked examples in its docstring.
  - scripts/rerunq.py: family sizetest added (items smoke and shard; pins
    sizetest.py, calprec2.py, costprobe2.py; LDZ, R1Z, SMZ, F2Z, R2Z in
    its docstring). No change to the rerun or calprec2 families: the
    three committed definitions validate and give the same job names.
  - Pre-run checks, as run by Claude 2026-10-31: (1) inputs read from
    their writers (calprec2 Runner, Out, base_row, error_row, TASKS,
    key_of, f_chunk, chunk_terms, combine_terms, load_throughput,
    verify_folder; kgrun ships every scripts/*.py but kgrun.py and
    rerunq.py; rerunq's existing family functions); (2) named exits on
    fixtures: smoke 0 SMOKE PASS; e1 stopped 5; resume chain a1 -> a2 ->
    a3 skips 2 then 4 complete rows; resume with other workers 2, other
    shard 2, a folder twice 2; G-STOP 2; missing resume folder 2; PC
    mismatch 3 before any folder is written; analyse complete 0,
    incomplete 4, a complete row in two folders 2, a smoke folder mixed
    in 2, a folder given twice 2; (3) input contact, structural only:
    the 26 calprec2-long folders hold phase C rows at 256M for every
    (module, d) the plan selects (counts only); (4) synthetic fixture end
    to end (plan --write-plan, smoke, e1 stop and resume, analyse, all
    outputs under the scratchpad, calprec2.N_LO patched in the fixture
    process only), and rerunq's sizetest functions on the fixture's
    fetched-folder layout: 21 checks pass (job names, arguments, clean
    headers, F2Z, wrong shard, stop_after, missing read line, PC FAIL,
    numpy, pin, row count, finalize refused). Python 3.8 grammar parse
    passes for both files. Nothing synthetic is committed.
  - Not yet done: the plan rerun with --write-plan on the committed
    inputs (Rahul), its folder's manifest, the shard count read from
    that log, the queue definition notes/queues/sizetest-e1.json, and
    CLAUDE.md rule 22's sentence "A definition's items are rerun.py or
    calprec2.py jobs", which needs Rahul's amendment to include
    sizetest.py.

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

- N43 (finding, design of the onset estimator; found 2026-10-28; revised
  2026-10-28 from logs/onsetclass-20261028.log). The H3 onset is the
  location of the best single bend of the S-slope curve over log r. The
  estimator cannot tell the start of a rise from its end, and nothing in
  its output says which a bend is. On these data it is a start in most
  cases and an end only at 2.00 and once at 1.25. At 2.00 it is not
  interpretable without the curve.
  - First wording, withdrawn: "the estimand is not an onset as reported".
    That rested on the 25 onsets at 2.00 alone. The classification of all
    80 (below) does not support it as a statement about the whole grid.
  - Sources:
    - logs/onsetdiag-20261028-b.log (exit 0): R1 40 of 40 and D 40 of
      40 in each row. The committed onsets of N39 and N42 are what H3
      specifies, computed correctly.
    - logs/onsetclass-20261028.log (scripts/onsetclass.py, sha256 in its
      header; run by Rahul on the laptop, exit 0): manifests and both
      archive files verified; "R ONSET 40 of 40 equal", "R ONSET-CAL 40
      of 40 equal"; "O1 PASS: 10 of 10"; m = 0.07811313532738592 from
      N39's analysis_margin.csv.
    The first onsetdiag run crashed on input (N42) and gave no result.
  - Mechanism (from the algebra, onsetdiag docstring F1 and F2).
    - The candidates are r 0.75, 1.0, 1.25, 1.5, 2.0. A bend at 0.75 is
      a straight line.
    - A bend at 2.0 has only r 3.0 to its right and fits that point
      exactly, so it is judged on a straight line through the first five
      points. A curve that rises from r 1 to r 2 and then stops is close
      to such a line and lands at 2.0, the end of its rise. A curve flat
      to r 2 that jumps at r 3 also lands at 2.0, the start of its rise.
  - The rule, as printed in the log. It is post hoc: fixed by Claude on
    2026-10-28 after the curves of the 25 onsets at 2.00 had been seen;
    its extension to bends below 2.0 was written before any of the other
    55 was computed. before = y(onset) - y(0.75); after = y(3.0) -
    y(onset); against m:
    - start: after > m, before <= m;
    - end: before > m, after <= m;
    - continues: both > m;
    - no rise: both <= m;
    - line: onset 0.75 (no case).
    It works on point slopes, with no interval, and describes rather than
    tests. "start" says the net rise lies after the bend. It does not say
    the rise begins at the bend.
  - Counts, as printed (COUNTS block):
    - ONSET, objective: start 19, end 3, continues 6, no rise 2, of 30.
      Pooled: start 8, end 0, continues 1, no rise 1, of 10.
    - ONSET-CAL, objective: start 21, end 4, continues 3, no rise 2, of
      30. Pooled: start 9, end 0, continues 1, no rise 0, of 10.
    - By onset value, ONSET: 1.00 start 6, no rise 1 (of 7); 1.25 start
      8, continues 1, no rise 2 (of 11); 1.50 start 9, continues 2 (of
      11); 2.00 start 4, end 3, continues 4 (of 11).
    - By onset value, ONSET-CAL: 1.00 start 4 (of 4); 1.25 start 11, end
      1 (of 12); 1.50 start 9, no rise 1 (of 10); 2.00 start 6, end 3,
      continues 4, no rise 1 (of 14).
    - The one end below 2.00 is ONSET-CAL anisotropic d 5 rastrigin, onset
      1.25, before +0.0837, after +0.0684, dist 0.0056.
    - These supersede Claude's hand counts of the first wording.
  - Where the estimator is sound, and where not, on these data.
    - Bends at 1.00 to 1.50: no end at 1.00 or 1.50 in either row, and
      the one end at 1.25 sits 0.0056 from m. A bend there has the net
      rise after it, so it can be read as "the rise lies at or after this
      r". Whether it starts at the bend is not established by the rule.
      Several of these curves wobble by a few hundredths with no clear
      rise before r 2 (for example ONSET isotropic d 5 rastrigin, onset
      1.25, y -1.038, -1.039, -1.089, -1.077, -1.035 at r 0.75 .. 2.0).
      There the bend is located by noise, which the wide intervals
      reflect.
    - Bends at 2.00: start, end and continues all occur (ONSET 4, 3, 4;
      ONSET-CAL 6, 3, 4, plus one no rise). A 2.00 is not interpretable
      without its curve. Isotropic d 80 is the clearest case. Ackley and
      sphere end their rise at 2.00, while rastrigin starts its rise
      there, in both rows. That is the onsetdiag DETAIL, now confirmed by
      onsetclass.
    - Pooled bends: no end in 20. The isotropic d 80 pooled bend, 1.00, is
      a start of the mean curve's rise. It is not the bend of any
      objective (onsetdiag SCOPE).
  - Consequences for the reported quantities. Each J4 or contrast-6
    interval is an interval of bend locations over resamples. The
    classification above is of the point curves only, so whether
    resampled bends are starts is not measured.
    - J4 "contains 1: yes" rests on resamples with bends at 1.00, the
      value at which no point curve is an end. J4 "no" at [2.00, 2.00]
      for ackley and sphere at isotropic d 80 is the end of a rise and
      cannot be read as a late onset.
    - N42's "isotropic onset separated from r = 1" rests on pooled bends
      that are starts at the point level: ONSET isotropic d 5 1.50, d 20
      1.50, d 40 1.25; ONSET-CAL d 5 1.25 (dist 0.0036), d 20 1.50, d 40
      1.50. Its interval upper ends reach 2.00, the ambiguous value.
    - Contrast 6, pooled, compares two pooled starts at d 80 and d 5. Per
      objective, isotropic, it compares d 80 ends (ackley, sphere) with d
      5 bends and cannot be read.
    - Not onset-dependent and unaffected: contrast 3 (including the sign
      change at d 40 and d 80), severity S(1,3), S(0.75,3) and their
      trend (J2), the per-cell slopes and rate verdicts, and the RMAP
      panel.
  - Round 1 (tab:onset, ten pooled bends, the same estimator; O1 PASS).
    ROUND-1 counts: start 7, end 0, continues 2 (anisotropic d 5 and d 80,
    both at 2.00), no rise 1 (isotropic d 10, 1.25, dist 0.0036).
    - The point estimates are not ends. Claude's earlier argument that
      round 1's intervals are wide because bends move between start and
      end knees is not supported at the point level and is withdrawn.
    - The claim itself (abstract, line 38; line 628) is about intervals:
      "nine of ten bootstrap intervals containing" r = 1. Those intervals
      came from 300 resamples pooled over objectives and realizations.
      The revision rejected that unit (ANALYSIS_CRITERIA item 3, P4), and
      O1 reproduces the points only, not the intervals.
    - The rerun's intervals with the approved unit (realizations within
      cells) give J4 pooled "6 of 10 intervals contain 1" in ONSET (N39)
      and in ONSET-CAL (N42); isotropic d 5, d 20 and d 40 exclude 1 in
      both. Nine of ten does not replicate. A new run (ONSET) and a new
      bootstrap unit differ from round 1 at once, so which of the two
      causes the difference is not separable.
    - Round 1's "not resolvable from r = 1" does not survive into the
      revision as a claim. The defect is not the start/end confusion
      here; it is that the claim does not replicate under the approved
      bootstrap, on bends that are mostly starts.
  - Near the threshold (NEAR block). dist is the smaller of |before - m|
    and |after - m|.
    - ONSET: dist <= 0.005 in 1, <= 0.01 in 5, <= 0.02 in 12, <= 0.05 in
      20, of 40.
    - ONSET-CAL: 3, 6, 11 and 17 of 40.
    - ROUND-1: 1, 1, 1 and 5 of 10.
    - m was set as 3 x the median per-cell bootstrap SD of a slope, for
      diffusion-arm differences. before and after are differences of two
      cells, so their noise is larger than one cell's. A call within a
      few hundredths of m can therefore be moved by sampling noise.
    - Invariance, from the definitions and Claude's reading of the
      printed values; not printed by a script. Under any single threshold
      applied to both before and after:
      - start implies before < after, and end implies before > after, so
        no threshold turns a start into an end or an end into a start;
      - a no rise or continues can become an end only if before > after.
        In the log that holds for one curve, ONSET-CAL anisotropic d 5
        sphere (continues, +0.1285 / +0.1212), and for round 1
        anisotropic d 80 (continues, +0.1160 / +0.1046).
      So "start-like against end-like" is fixed by the sign of after -
      before, whatever the threshold. How many are start rather than
      continues or no rise depends on the threshold. Separate thresholds
      for before and after (for example each scaled by its own SD) break
      this invariance.
  - No amendment of the estimator is proposed (Rahul's instruction).
  - Decision (Rahul, 2026-10-28): drop onset intervals; no resample-level
    classification script, no threshold sweep. Recorded in
    notes/ANALYSIS_CRITERIA.md, "Fifteenth message (2026-10-28)".
    - Reason (Rahul): the script's best outcome would still be
      exploratory evidence for a claim the paper does not need, using a
      rule chosen after the curves were seen and a threshold borrowed
      from another purpose. The organising contrast rests on the
      per-cell rate verdicts by region and contrast 3; the severity
      result rests on slopes at fixed r. Neither uses an onset.
    - Dropped as claims: J4, contrast 6, the onset interval column and
      the onset heterogeneity rows, in ONSET and ONSET-CAL. The committed
      CSVs (analysis_onsets.csv, analysis_onsets_calibrated.csv, the c6
      rows of analysis_stats.csv) keep them as computations, unchanged.
    - The paper reports the curves and point bends as exploratory, with
      no location estimated and no interval. It states as a limitation
      that it cannot say, with an interval, where along r the slope
      begins to degrade. It withdraws round 1's "nine of ten intervals
      contain r = 1" in one sentence. That sentence names that the rerun
      gives 6 of 10 in both designs under the approved bootstrap, names
      both changes (the realizations and the bootstrap unit), and assigns
      no cause.
    - Wording: "does not hold on the rerun", never "changed
      significantly". 6 of 10 appears only as the reason for the
      withdrawal, never as a finding that the onset is separated from
      r = 1.
  OPEN until that text is written and verified by the rule-8 diff.
  Addendum 2026-10-30 (source of round 1's onset claim; audit.py A4).
  - CORRECTIONS TO RAHUL'S READING (2026-10-30; recorded at his
    request as corrections):
    - He read round 1's "not resolvable from r = 1" as coming from
      audit.py A4. It came from reboot.py's onset function on the Part D
      regime-map runs (regimemap_D_real.csv) at 4000 resamples.
    - He read A4's intervals as containing 1.0 in three of four panels.
      They contain it in two of four (the d 40 panels).
    - No A4 number appears anywhere in the deposited text. Its only trace
      is tex 719's "the change-point intervals", in the sentence group A
      of the disclosure already withdraws.
  - Round 1's "not resolvable from the boundary" (tex 628; abstract 38;
    conclusions 707; Table tab:onset, 602 to 620) comes from reboot.py's
    onset(): the free breakpoint of regimemap.py at tau_0 0.1 on
    regimemap_D_real.csv, d 5 to 80, r 0.75 to 3.0, 4000 resamples.
    round1-zip/cbo-gap/logs_reboot.log, block "ONSET: free breakpoint in
    log r at tau_0 = 0.1, 4000 resamples", prints the ten breakpoints and
    intervals of Table tab:onset and "intervals excluding r = 1: 1 of 10"
    (isotropic d 20, [1.25,2.00]). It is the estimator H3 retyped and that
    this entry found unable to tell the start of a rise from its end.
  - It does not come from audit.py A4. A4 is a different run of the same
    kind of estimator: a single free hinge in log r by profile least
    squares, on cliff_summary.csv (EXP-CLIFF), d 10 and 40 only,
    candidates r 0.9 to 3.0, 400 resamples over objectives. Its output
    (logs/depositcheck-20261030.log, appendix): anisotropic d 10 2.000
    [2.00,3.00], d 40 1.500 [1.00,1.50]; isotropic d 10 1.500
    [1.25,3.00], d 40 1.100 [1.00,1.50]. Its intervals contain 1.0 in 2 of
    4 panels (the two d 40 panels), not 3. No A4 number is quoted in the
    deposited text. Its only trace is tex 719's "the change-point
    intervals" among what the re-analysis script recomputes, and audit.py
    is the script that does so.
  - ONSET-R REPLACES the free-breakpoint onset, in both its forms
    (regimemap/reboot and audit A4); it does not correct it. ONSET-R has
    a different estimand: a sustained threshold crossing against the
    unit's own baseline, not the best single bend. It has a different
    design (r grid 0.3 to 4.8, M 48) and a different interval (N44). No
    ONSET-R number is compared with a breakpoint estimate (O-R8). The
    text must not describe r_delta as a corrected or refined breakpoint.
    The A4 "change-point intervals" claim at tex 719 is withdrawn with
    the rest of that sentence (N8, group A).

- N44 (design, 2026-10-28; Rahul approved the onset-resolution
  experiment). A new row, ONSET-R, on a dense r grid with a pre-registered
  threshold-crossing estimand (notes/ANALYSIS_CRITERIA.md, "Sixteenth
  message"). Nothing has run beyond the projection.
  - Projection. Source: logs/onsetr-projection-20261028.log (commit
    4f18cfd; run by Rahul on the laptop; reads only committed files).
    - "ONSET-CAL tasks read: 2160 (expected 2160)".
    - Measured Kaggle wall per task, by d, over r 0.75 to 3.0: d 5 3.60 to
      3.77 s; d 10 6.04 to 6.41; d 20 10.54 to 10.78; d 40 19.96 to
      20.72; d 80 38.78 to 39.85. Rahul's reading: flat in r at every d,
      so the no-r-dependence assumption holds and no cost probe is
      needed.
    - "projection (r grid of 14 points, M 48): tasks 20160, summed wall
      323508 s"; "at 4 workers, perfect scaling: 80877 s; shards at 21600
      s: 4; at 10800 s: 8".
    - Basis: ONSET-CAL's measured Kaggle per-task walls, extrapolated to
      the new r values and to M 48. The queue's own schedule will use
      costprobe2's walls; the unit key (module, objective, d, diffusion,
      J_inf, T, J grid, arm) has no r, so they cover every new task.
  - Betas, checked in code (Claude, 2026-10-28):
    - rerunlib reads calprec2_beta.csv by (module, objective, d, law,
      tau0), with no r and no diffusion;
    - calprec2 solves beta on the t = 0 ensemble, regimemap sampler "X0 =
      rng.standard_normal((Jinf, d))" (regimemap.py line 202), before r or
      sigma enter.
    The N41 table covers all fifteen (objective, d) cells at tau0 0.1. No
    calprec2 run is needed.
  - Memory: the cal3 shards, on these units, printed "peak RSS max 350.0
    MB" and "344.0 MB" (budget 3072 MB); r does not change array sizes.
  - Untested: r above 3.0 has never run in the regimemap module. The
    queue smoke runs the smallest task, so r 4.8 at d 80 first runs in a
    shard. A non-finite slope there is counted and flagged by the
    analysis (O-R5), not a crash.
  - Decisions (Rahul, 2026-10-28):
    - M = 48. Reason: at M = 12 the per-cell SD is about the size of a
      step's rise at low d, which would leave the dense grid unreadable
      and reproduce the problem in a new form.
    - delta = 0.10 primary; 0.05 and 0.20 sensitivity with no verdict;
      all three fixed before any data.
    - Upper end 4.8. Reason: without points beyond 3.0 the row reproduces
      the exact defect it exists to fix, a crossing near the top of the
      grid with nothing to its right.
    - 8 shards at the 10800 s target. Reason: as N37, N38 and N42, the
      estimates assume perfect scaling and the measured shards have
      overrun by up to 30%; one shard at 80877 s is far over the ceiling.
    - Order: criteria first, approved before any code; then the code with
      the four pre-run checks; then the precheck with K5; then the
      schedule; then the queue definition. The estimator's positive
      control (O2) must be committed and passing before the plan is
      built: it runs inside the precheck, which writes no plan unless it
      passes.
  - Constraints: nothing already computed changes. ONSET-R is appended
    (owner index 20). The new plan must pass K5 against
    runs/rerun-plan-20261026-210435. The analysis reproduces the twenty
    rows against runs/rerun-analysis-20261027-185918. Everything runs
    through the queue, smoke first, resumable.
  - Read-back and amendments (Rahul, 2026-10-28); criteria APPROVED with
    them (ANALYSIS_CRITERIA, "Sixteenth message", rewritten):
    - Baseline check: range >= delta, replacing Claude's delta / 2. Reason
      (Rahul): it ties the check to the estimand's own unit rather than a
      fraction chosen without derivation, and it is less strict than delta
      / 2, so fewer units lose a verdict for a reason that could not be
      justified. delta / 2 was arbitrary and was replaced for that reason.
    - Interval: hybrid. It interpolates as every other row does when both
      order statistics are finite, and gives the censoring label otherwise.
      ONSET-R then differs only in the censored case, which is forced
      rather than chosen. pct() must not be reused: it drops non-finite
      values and would silently discard censored resamples. The paper must
      state how the interval differs, and that a censored limit is
      reported as a bound, not a value.
    - Grid: 17 points, 0.3 to 4.8; baseline 0.3, 0.35, 0.42, 0.5; the
      search starts at 0.6. Reason (Rahul): an assumed-clean region below
      the baseline is the same blind spot as a bend with nothing to its
      right, the defect this row exists to fix. Measuring down to 0.5,
      instead of assuming no degradation below 0.85, is worth 4320 extra
      tasks; runtime is not the constraint. Tasks: 24480.
    - The 14-point projection and its 8 shards no longer apply. The
      17-point projection is rerun by Rahul (logged), and the shard count
      is fixed from the new plan's schedule.
    - The synthetic expected values were re-derived for the new grid and
      baseline (C1 to C9, with C5b added). O2 must pass in the precheck
      before the plan is written.
  - Code (Claude, 2026-10-28; nothing executed by Claude on project data):
    - rerunlib.py: the ONSET-R row (ONSETR_RS, GRID, ROW_COUNTS, PAIRED,
      CALROWS, BETA_SOURCE, cells_of), the A-SIGMA exception for r not in
      ONSET's archived grid, crossing() (O-R2, O-R3), hybrid_limits()
      (O-R5), onsetr_verdict() (O-R6) and onsetr_control() (O2: C1 to C7 at
      three deltas, C9).
    - rerun.py: V0 counts ONSET-R against ROW_COUNTS; O2 runs after O1 and
      before build_plan, with no plan written unless it passes; plans record
      O2 and load_plan requires it.
    - rerun_analysis.py: ANALYSIS_ROWS includes ONSET-R; the reproduction
      pin is moved to runs/rerun-analysis-20261027-185918 (sha256.txt
      036bbbbe...ffdcab); one twenty-row check over eleven files, after the
      calibrated rows and before ONSET-R (exit 8); O2 plus C8 before any
      data is read (exit 2); onsetr_block (O-R2 to O-R8) writing
      analysis_onsetr.csv.
    - Pre-run checks, as run by Claude:
      - (1) Inputs were read from their writers: the plan columns
        (PLAN_COLS, including tau0) and the eleven reproduction files
        (write_all).
      - (2) Every new failure is a named exit, never a traceback.
      - (3) Input contact on committed files, structural output only.
        GUARD matches; V0 PASS with ONSET-R 510 / 24480. A-SIGMA for ONSET-R
        gives 60 ok (r 1.0 and 2.0) and 450 not applicable. The twenty-row
        folder's manifest hash equals the pin, and all eleven files compare
        PASS against themselves with 0 differences.
      - (4) Synthetic only: O2 passes on its cases and C8 passes. A fixture
        of the ONSET-R block (fake realizations, B reduced to 200) ran end
        to end through phase 1, onsetr_block and analysis_onsetr.csv. It
        exercised above 1, below 1, baseline not flat, right-censored,
        pooled, and pooled not computed. Its first attempt stopped on a
        fixture omission (plan rows without tau0), not a code defect.
      - The main() wiring of rerun_analysis (the twenty-row check, then
        ONSET-R) was read, not executed; no end-to-end fixture covers it.
      Python 3.8 grammar parse passes for all three files.
  - 17-point projection. Source: logs/onsetr-projection17-20261028.log
    (commit 256c420). "ONSET-CAL tasks read: 2160 (expected 2160)";
    "projection (r grid of 17 points, M 48): tasks 24480, summed wall
    392831 s"; "at 4 workers, perfect scaling: 98208 s; shards at 21600 s:
    5; at 10800 s: 10".
  - Precheck. Source: logs/rerun-precheck4-20261028.log (commit 256c420);
    plan runs/rerun-plan-20261028-212945, manifest verified by Claude
    (sha256sum -c OK), rerun_plan.csv sha256 5fc3b0b2...42ea.
    - Header: rerun.py 52864b42...dacbd, rerunlib.py 31f4b360...e430,
      costprobe2.py ea5cb2e1...f64b; python 3.12.3, numpy 2.5.3.
    - V0(b): "ONSET-R cells 510 realizations 24480 design (N44) (510,
      24480) ok". "merged calprec2 cells 377". O1 PASS (ten of ten).
    - O2: 26 control lines, all "ok", then "O2 PASS", before the plan was
      built.
    - "archive check: 2658 ok, 0 FAIL, 738 not applicable"; "K4 PASS (52
      groups with more than one row)"; "K1 PASS (39084 distinct (group,
      rep) keys)"; K2 PASS.
    - K5: "old plan runs/rerun-plan-20261026-210435/rerun_plan.csv: 2034
      rows over 20 row names; new plan has 2034 rows of those names", "K5
      PASS".
  - Schedule. Source: logs/rerun-schedule-onsetr-20261028-2130.log
    (commit ce6a032); rows ONSET-R, "tasks 24480", --nshards 8, 10, 12 and
    14 at 4 workers, the same script hashes and plan.
    - At 10 shards: 2447 to 2449 tasks each, summed wall 38333 to 38336 s,
      "estimate 9583" or "9584 s at 4 workers"; all labelled lower bounds.
    - Rahul's sum over the ten shard lines: 383344 s. Against the
      projection's 392831 s from ONSET-CAL's Kaggle walls, two independent
      bases agree to 2.5% (Rahul's figure).
  - Decision (Rahul, 2026-10-28): 10 shards at 9584 s each, 44% of the
    21600 s ceiling (Rahul's figure). Reason: as for every previous set,
    the estimates assume perfect scaling and the measured shards have
    overrun by up to 30%, so a shard should be able to run at better than
    twice its estimate and still finish.
  - Queue definition: notes/queues/rerun-onsetr.json. Profile rerun-onsetr
    (family rerun, workers 4, plan runs/rerun-plan-20261028-212945 with
    its sha256, the timing folders costprobe2-s0 20261010-103952 and s1
    20261011-101343, expect python 3.13.15 and numpy 2.1.3). Items:
    smoke-onsetr, then onsetr-s0of10 to onsetr-s9of10, rows ONSET-R,
    ledger N44. Shard exit 5 resumes from the shard's own earlier attempt
    folders (rerunq R2, max_attempts 5). It passes
    rerunq.validate_definition (Claude).
  - Untested path (Claude): rerun_analysis.py's main() from the twenty-row
    check (O-R10) to the ONSET-R stage and the final write has been read
    and not executed. A1 refuses any run without ONSET-R complete (exit 7), so
    without a rehearsal its first execution is the real analysis.
  - Rehearsal before the load (Rahul, 2026-10-28). scripts/onsetr_rehearsal.py
    writes SYNTHETIC ONSET-R realizations, keyed as the plan's tasks, into
    ~/cbo-rehearsal/REHEARSAL-SYNTHETIC-onsetr-<stamp>/ with a README. It
    refuses any --out inside the repository (exit 2). rerun_analysis then
    runs on the eight real shard folders plus that folder, with --outdir
    under ~/cbo-rehearsal. The real evidence is the twenty-row
    reproduction check (O-R10) and that main() runs from it through the
    ONSET-R stage to the write. Its ONSET-R numbers are synthetic and never
    quoted; nothing synthetic goes into runs/ or a commit.
    - Pre-run checks (Claude):
      - (1) Inputs were read from their writers: rerun.py's REAL_COLS and
        plan_row; load_runs's checks.
      - (2) The refusal is a named exit 2.
      - (3) Input contact: the generator, run into the session scratchpad
        on the real plan, wrote 24480 rows. rerun_analysis.load_runs (A0)
        accepted 24480 of 24480 against the plan's ONSET-R tasks. --out runs
        was refused, exit 2.
      - (4) Synthetic: phase 1 and onsetr_block on that folder, B reduced to
        200, reached every path: above 1, including a crossing inside a
        rise; below 1; not distinguishable; right-censored; left-censored;
        baseline not flat; a non-finite cell with FLAG, in both arms by
        pairing; pooled computed and not computed.
      - One printed label, "point is censored" for a pooled line whose
        objective was non-finite, was corrected in rerun_analysis.py (not
        pinned by the queue).
    - Not reachable by construction: FLAG with a finite point. A resample is
      non-finite only if its cell kept no realization, and then the point
      is non-finite too, so the verdict reads "point non-finite" (checked
      first) while the FLAG is still raised.
  - Rehearsal output. Source: logs/rerun-analysis-rehearsal-OR10-20261028.log
    (commit ae6e174): rerun_analysis sha256 f5c1dbef...56d7, python 3.12.3,
    numpy 2.5.3; "O2 PASS (C1 to C9)"; "20-ROW REPRODUCTION PASS: 11
    files"; "rerun_analysis exit 0". Its ONSET-R numbers are synthetic and
    are not quoted anywhere.
  - Queue. Smoke and shards s0of10 to s9of10 exit 0 (Rahul). Read by Claude
    from the committed folders: every shard's sha256.txt verifies; headers
    show python 3.13.15, numpy 2.1.3, plan runs/rerun-plan-20261028-212945,
    rows ONSET-R; last "peak RSS max" per shard 356.4 to 377.9 MB, "OVER
    BUDGET 0" in all ten (budget 3072 MB, O-R9).
  - Analysis. Source: logs/rerun-analysis21-20261030-1446.log, folder
    runs/rerun-analysis-20261030-144722 (commit 08edb0a; run by Rahul on
    the laptop; sha256.txt verified by Claude). Header: rerun_analysis
    sha256 f5c1dbef...56d7 (the rehearsal's), python 3.12.3, numpy 2.5.3,
    workers 2, plan 20261028-212945, reproduce
    runs/rerun-analysis-20261027-185918.
    - "O2 PASS (C1 to C9)". A0 per shard: 2449, 2449, 2448 x 6, 2447,
      2447 complete realizations; A1 "ONSET-R realizations 24480 present
      24480 complete".
    - "margin equals runs/rerun-analysis-20261027-185918's
      analysis_margin.csv, every value as a string (O-R10)"; "20-ROW
      REPRODUCTION PASS: 11 files, every value of every old column equal
      as a string".
    - "no FLAG"; "wall 3708.4 s"; "rerun_analysis exit 0".
  - ONSET-R RESULT, W-full, delta 0.10 (primary). Every value below is from
    runs/rerun-analysis-20261030-144722/analysis_onsetr.csv, rounded to
    three decimals by Claude for this entry; full precision is in the file
    and in the log. Format: r_0.10 [lo95, hi95], verdict (O-R6); adq marks
    "beta_adq; C1 found no sufficient level". No unit's baseline is "not
    flat" at 0.10, none is non-finite, none is FLAG.
    isotropic
      d 5   ackley 3.028 [2.676, beyond 4.8] above 1 (1483 of 10000
            resamples right-censored); rastrigin 3.921 [3.642, 4.606] above
            1; sphere 3.670 [2.529, 4.315] above 1; pooled 3.519 [3.178,
            beyond 4.8], I2 0.0000 (tau2 truncated at 0).
      d 10  ackley 2.431 [2.259, 3.515] above 1, adq; rastrigin beyond 4.8
            [beyond 4.8, beyond 4.8], no verdict (point beyond 4.8; 9852 of
            10000 resamples right-censored); sphere 3.575 [3.076, 4.176]
            above 1; pooled not computed (O-R7).
      d 20  ackley 1.856 [1.781, 1.949] above 1, adq; rastrigin 3.703
            [3.552, 3.866] above 1; sphere 2.009 [1.904, 2.095] above 1;
            pooled 2.399 [2.336, 2.462], I2 0.9966.
      d 40  ackley 1.434 [1.376, 1.476]; rastrigin 2.759 [2.718, 2.806];
            sphere 1.458 [1.433, 1.481]; all above 1; pooled 1.793 [1.766,
            1.815], I2 0.9994.
      d 80  ackley 1.107 [1.070, 1.151] adq; rastrigin 2.266 [2.240, 2.293]
            adq; sphere 1.183 [1.148, 1.212]; all above 1; pooled 1.437
            [1.415, 1.461], I2 0.9993.
    anisotropic
      d 5   ackley 1.619 [1.474, 2.434]; rastrigin 2.008 [1.650, 2.873];
            sphere 1.457 [1.309, 2.034]; all above 1; pooled 1.680 [1.548,
            1.997], I2 0.4081.
      d 10  ackley 1.243 [0.989, 2.087] not distinguishable from 1, adq;
            rastrigin 1.933 [1.655, 3.080] above 1; sphere 1.638 [1.354,
            1.845] above 1; pooled 1.579 [1.433, 2.097], I2 0.2113.
      d 20  ackley 1.471 [1.177, 1.831] above 1, adq; rastrigin 2.028
            [1.523, 2.645] above 1; sphere 1.396 [1.270, 1.718] above 1;
            pooled 1.609 [1.408, 1.869], I2 0.4436.
      d 40  ackley 1.201 [0.954, 1.392] not distinguishable from 1;
            rastrigin 1.981 [1.833, 2.176] above 1; sphere 1.516 [1.321,
            1.844] above 1; pooled 1.533 [1.379, 1.691], I2 0.8945.
      d 80  ackley 0.982 [0.819, 1.076] not distinguishable from 1, adq;
            rastrigin 2.114 [1.879, 2.497] above 1, adq; sphere 1.437
            [1.139, 1.636] above 1; pooled 1.440 [1.287, 1.560], I2 0.9598.
    Counts (log, O-R6, no multiplicity correction, no family-wise claim):
    isotropic 14 above 1, 1 no verdict (point beyond 4.8); anisotropic 12
    above 1, 3 not distinguishable from 1; all 26, 1, 3; none below 1.
  - Reading of the result (Claude, 2026-10-30; for Rahul to reverse):
    - The right-censored unit, isotropic Rastrigin d 10: its slope stays at
      or below the baseline -1.045 at every r up to 4.0 (-1.033 there) and
      is -0.988 at 4.8, short of baseline + 0.10. No
      crossing exists on the grid; the label is a bound, "beyond 4.8".
    - The three not-distinguishable units are anisotropic Ackley at d 10,
      40 and 80; the other two anisotropic Ackley units (d 5 and 20) are
      above 1. What they share is a curve shape, not a beta: d 40 has a
      production beta, while d 20 has adq and is above 1. Their slopes rise
      steadily from r 0.3 with no step, so the 0.10 crossing lands near r
      1 and the resamples straddle it. At d 80 the four baseline slopes are
      -0.825, -0.813, -0.801, -0.782, already rising inside the baseline
      window, with a range of 0.043, under delta, so O-R3 calls it flat.
    - Phase 1 of ONSET-R (analysis_cells.csv): at r 0.3 the rate criterion
      (one-sided upper 95% bound <= -1) holds in 2 of the 30 cells
      (isotropic Rastrigin d 5 and d 10). The baseline is therefore each
      unit's own slope at small r, not the J^-1 slope; r_delta measures
      departure from it.
    - W-ge sensitivity (O-R8) is empty by construction, not omitted: at
      tau0 0.1, W-ge keeps J with J tau0 >= 1, which is every J of the grid
      (10 to 5000), so windows_for gives W-full only and the file has no
      W-ge line. The paper must say so.
    - Delta sensitivity, no verdict. At 0.05, anisotropic Ackley d 40 is
      0.760 [0.653, 0.859] and d 80 is 0.651 [0.610, 0.693], both
      intervals below 1. Anisotropic Ackley d 10 is 0.800 [0.622, 1.201],
      with 3 resamples left-censored. Anisotropic Sphere d 20 is 0.934
      [0.770, 1.271] and d 80 is 0.879 [0.790, 1.038]. Isotropic Ackley d
      80 is 1.024 [0.967, 1.059]. Anisotropic pooled d 80 is
      0.970 [0.898, 1.055]. Isotropic Rastrigin d 80's baseline range,
      0.058, makes it "not flat" at 0.05. At 0.20 every anisotropic point
      is finite (the smallest is Ackley d 80, 1.726 [1.580, 2.070]); the
      isotropic points at d 5 (Ackley, Rastrigin) and d 10 (Rastrigin,
      Sphere) are beyond 4.8, and pooled d 5 and d 10 are not computed.
      Read from these values, not computed: between 0.05 and 0.20 the
      anisotropic crossings move much further than the isotropic ones at
      d 40 and 80 (Ackley d 80: 0.651 and 1.726 anisotropic, 1.024 and
      1.268 isotropic). That is the ramp-versus-step difference above.
    - Pooled isotropic I2 is 0.9966 to 0.9994 at d 20 to 80: the three
      objectives disagree far beyond their bootstrap error, and the pooled
      value is a geometric mean of different crossings, not a common one.
    - Trends across d: not computed and not claimed (O-R8). Pattern
      notes, not claims: isotropic Rastrigin is not monotone in d (3.921
      at d 5, beyond 4.8 at d 10). The pooled isotropic sequence has no d
      10 value. "Flat" for anisotropic would be an equivalence claim
      (rule 10).
    - Scope: tau0 0.1, centred law, regimemap module, three objectives, d
      5 to 80, J_inf 50000, T 1.0, fixed calprec2 betas, M 48, a grid down
      to r 0.3. No comparison with ONSET or ONSET-CAL (O-R8; N40, N43).
    - The boundary r = 1 is the condition 2 lambda > d sigma^2 of FKR
      Theorem 3.7 (isotropic) and 2 lambda > sigma^2 of dissertation
      Theorem 3.6 (anisotropic; regimemap.sigma_of). Neither theorem owns
      the J^-1 exponent, and GHV 2.6, which does, has no such condition
      (N1). For Ackley the other hypotheses are not verified (R1, O1).
  - Manuscript consequences, for the single editing pass with N45 (not
    applied): 38 (abstract, Third), 628 and 707 state that the onset "is
    not resolvable" or "cannot be distinguished" from r = 1; 602-620
    (Table tab:onset, the free-breakpoint r_onset, dropped in N43) and 722
    ("change-point analysis") rest on the withdrawn estimator. Wording is
    Rahul's decision; see the reply of 2026-10-30.
  CLOSED 2026-10-30 (commit 08edb0a for the run; this entry for the
  record). The manuscript text it implies is OPEN under N45.

- N45 (manuscript, P + T; standing set of corrections; recorded
  2026-10-29). The measured exponent is attributed to FKR where its only
  source is GHV Theorem 2.6 at p = 2 (N1 correction of 2026-10-29: FKR
  Proposition 3.11, (32), bounds sup_t E[.|Omega_M]; the estimator (9) is
  E sup_t). Rahul's decision 2026-10-29: NO manuscript edit until the
  ONSET-R shards and the twenty-one-row analysis are in, because several
  of these lines will be rewritten again then; one editing pass, under
  rule 8. Line numbers are of manuscript/sn-article.tex at commit 9042beb.
  WRONG
  - 60: "addresses the mean-field approximation component" of FKR Theorem
    3.8; that component is Proposition 3.11, which bounds sup E
    conditioned on Omega_M, not the measured E sup.
  - 40 (abstract, Fourth): "the region in which the theorem applies and
    the region in which its exponent is visible"; the theorem carrying the
    condition (FKR 3.7) owns no J exponent, and the one owning it (GHV 2.6)
    has no parameter condition.
  - 547: "Admissibility does not imply observability ... the region
    satisfying the theorem's parameter condition and the region satisfying
    ... rate-consistency ... are not the same set"; same conflation.
  - 698: "theorem-admissible ... the paper's central conceptual point";
    same conflation.
  - 654: "Outside the condition [FKR 3.7] says nothing, so failures there
    are not evidence against any theorem"; the reason is wrong (GHV 2.6
    predicts J^-1 for every r); the conclusion holds for a different
    reason (a finite-window slope cannot contradict an asymptotic bound).
  IMPRECISE
  - 66: the J^-1 benchmark is stated with no source; cite GHV 2.6, p = 2.
  - 32 (abstract opening): frames the measured slope as the exponent of
    the assembled FKR guarantee.
  - 54: "the proven mean-field rate", "observability of the classical
    theory": no theorem named.
  - 352: "the proven rate switches on": no source.
  - 211, last sentence: "Sections sigma-onset measure this axis" ties the
    measured exponent to alpha_0 of Remark 4.8, which belongs to 3.7.
  - 213 and 715: "a mean-field constant" is C_MFA of (32), the constant of
    a weaker quantity than the one measured; say so.
  - 450: compares the Section 4 constants (C_MFA) with the observable
    exponent; also contradicts 205 ("none is used in Section 7").
  - 38, 485, 508, 549, 634, 648, 685, 707: "admissible" / "non-admissible"
    labels read as admissibility of the exponent's theorem (rule 10);
    use "inside / outside the condition of FKR Theorem 3.7".
  - sn-supplementary.tex S1 title and line 27: say it traces the constant
    of FKR (32), not of the measured quantity.
  CITATION SOURCE (added 2026-10-30, N3 SIOPT comparison): main 201 and
  supplement 27, 29 cite proof details (b1, b2, c_M, the three terms)
  that exist only in the arXiv v6 appendix: cite "arXiv v6, Appendix" and
  say so; rewrite the note under reference [3] to name v6, state the
  shared numbering, and the appendix exception. Add the dissertation
  (Theorem 3.6) and the EvoApplications paper for the anisotropic
  boundary (R2, referee point 2).
  FINE: 50, 56, 62, 80, 88, 104-109, 215, 259, 284, 290, 301, 403,
  495, 694, 700, 703, 705, 709; supplement line 33.
  PROPOSED LINE 60 (not applied): "This paper does not measure the
  end-to-end guarantee of \cite[Theorem 3.8]{fkr2024}, nor its mean-field
  component \cite[Proposition 3.11]{fkr2024}, which bounds the supremum
  over time of a mean-square error conditioned on a bounded event. The
  estimator \eqref{eq:est} takes the supremum over time inside the
  expectation and is not conditioned; the result that bounds it is the
  pathwise estimate \cite[Theorem 2.6]{ghv2025} with $p=2$, and that is the
  source of the $J^{-1}$ benchmark used throughout. A flatter fitted slope
  is therefore not evidence against either result." followed by the
  existing discretization sentences unchanged.
  GROUNDS FOR WITHDRAWING THE CLAIM AT 40, 547, 698 (assessment
  2026-10-29, Rahul's question; how the withdrawal is written is his
  decision). The referee's ground (R1) and N1 are distinct, but they are
  not two independent reasons to drop the claim. R1 is evidential and
  curable: the three cells were not shown to satisfy the hypotheses, and
  the route of "Ackley: the route" (GHV 2.3 existence, A1-A2 with
  constants) would cure it. N1 is about what the claim means and cannot be
  cured: with every hypothesis verified, the claim still compares the
  condition region of a theorem that owns no exponent with the visibility
  of an exponent owned by a theorem that has no condition. N1 alone
  suffices; R1 alone would only require repair. Consequence: the
  "demonstration on objectives that satisfy (6), (7), (27) outright"
  costed under "Ackley: the route" (the referee's alternative) would
  demonstrate an ill-posed claim and should not be run for that purpose.
  Rahul's decision 2026-10-29: N1 is the single ground (recorded in N1).
  HOW THE WITHDRAWAL MUST BE WRITTEN (Rahul's instruction 2026-10-29;
  identical text in N1 and N45):
  - The reason given is N1, not the Ackley misclassification. Written the
    other way it implies the claim would survive with valid objectives,
    which is false, and invites the referee to ask why it was not simply
    rerun on Sphere or Rastrigin.
  - The Ackley correction (R1) is reported separately, in the assumption
    audit, as a fix to Table 1.
  - One sentence states that even with the classification corrected the
    claim does not survive, and why: the condition 2 lambda > d sigma^2 is
    a hypothesis of FKR Theorem 3.7, which owns no J exponent, and the
    result that owns the measured exponent, GHV Theorem 2.6, has no
    parameter condition, so there is no admissible region to compare.
  - The referee's suggested demonstration on fully verified objectives
    (costed at the end of "Ackley: the route", "Cost of a demonstration on
    objectives that satisfy (6), (7), (27) outright") is NOT run: it would
    demonstrate an ill-posed claim.
  WHAT REPLACES THE CLAIM: cells inside the hypotheses of GHV Theorem 2.6
  can fail the finite-window criterion. This is a statement about the
  prefactor, not about an admissible region. It still needs O1 (Ackley in
  A(0,0,0)) proved, since the three failing cells are all Ackley.
  ONSET-R (added 2026-10-30): the twenty-one-row analysis is in (N44,
  CLOSED). Its manuscript consequences (38, 602-620, 628, 707, 722) join
  this pass; listed in N44.
  PROPOSED ONSET TEXT (Rahul's instruction 2026-10-30; not applied;
  numbers from runs/rerun-analysis-20261030-144722/analysis_onsetr.csv):
    "On a 17-point grid from r = 0.3 to 4.8, at tau_0 = 0.1 with 48
    realizations per cell, we estimate for each of 30 units the smallest r
    beyond which the fitted slope stays at least 0.10 above the unit's own
    slope at r <= 0.5. That threshold and the verdict rule were fixed before
    the runs. For 26 units the 95% interval of this crossing lies above
    r = 1, the boundary of the condition 2 lambda > d sigma^2 of [FKR,
    Theorem 3.7] (2 lambda > sigma^2 for anisotropic diffusion); none lies
    below. Three, all anisotropic Ackley, are not distinguishable from 1.
    One, isotropic Rastrigin at d = 10, shows no crossing up to r = 4.8.
    No multiplicity correction is applied. The anisotropic verdicts depend
    on the threshold: at 0.05, two anisotropic Ackley intervals lie below
    1. Below r = 0.5 the slope is not the J^-1 slope in most units, so the
    crossing locates a further departure, not the start of one."
  Reason: it replaces Rahul's phrasing "degradation begins above the
  boundary at 26 of 30 units", which overstates in three ways:
  - "begins" is wrong: r_delta is where a sustained excess of delta is
    first reached, not where departure starts; in the ramp units
    (anisotropic Ackley) departure starts earlier, possibly inside the
    baseline window;
  - "degradation" needs its reference: the unit's own small-r slope, not
    -1 (the rate criterion holds at r 0.3 in 2 of 30 cells);
  - "the boundary" must be named: the condition of FKR Theorem 3.7
    (isotropic) or of dissertation Theorem 3.6 (anisotropic), neither of
    which owns the J^-1 exponent (N1).
  DECIDED (Rahul, 2026-10-30), ONSET-R presentation:
  - No trend of r_delta across d is claimed or computed, and no trend
    analysis is run: the pattern has now been seen, so any such analysis
    would be post hoc by construction. Reasons that go with it: isotropic
    Rastrigin is non-monotone in d (3.921 at d 5, beyond 4.8 at d 10); the
    pooled isotropic sequence has no d 10 value (not computed, O-R7);
    pooled isotropic I2 is 0.9966 to 0.9994 at d 20 to 80, so the pooled
    value is not a common crossing; "flat" for anisotropic would be an
    equivalence claim (rule 10). The paper shows the table and says only
    that no trend across d was specified or assessed.
  - The paper shows all three deltas (0.05, 0.10, 0.20), not the primary
    alone, because at 0.05 two anisotropic Ackley intervals lie below 1
    (d 40 0.760 [0.653, 0.859], d 80 0.651 [0.610, 0.693]). 0.10 stays the
    only delta with verdicts.
  - W-ge is empty by construction at tau_0 0.1 (J tau_0 >= 1 holds for
    every J of the grid, 10 to 5000), so analysis_onsetr.csv has no W-ge
    line. The paper must say so, since O-R8 promises W-ge as sensitivity.
  CARRIED FROM ENTRIES CLOSED 2026-10-30 (text only):
  - N31: round 1's "paired on the shared realization index" (tex 309,
    650) was false for the archived runs; say so where round-1 paired
    figures are mentioned. The rerun's pairing is real (5a).
  - N32: the archived results computed under boundary.py's 0.02
    monotonicity tolerance, control.py's two-sided 0.15 criterion and the
    absolute-value P-E2 / P-C2 stay in the supplement, labelled as such.
  - N33: every reported slope names its estimand (S-slope primary).
  DECIDED (Rahul, 2026-10-30), CONC against PROBEARM (C1): dropped
  (N40). Remove the "moved the statistic by 0.300" / "measured effects
  of two protocol decisions" sentences (tex 396) and any other
  probe-against-exact contrast. The supplement carries N40's five items.
  NOMINAL TAU_0 LABELLING (Rahul, 2026-10-30): the rows run on probe betas
  (PROBEARM, mechanism probe; GEOM, law probe; ADAPT, control probe;
  REFSIZE, SYNTH, NAMED, HORIZON, regime probe; RMAP, ONSET, regimemap
  probe; CLIFF, cliff probe) reach a concentration other than the probe's
  target. Wherever one is reported, its tau_0 is called nominal (the
  probe's target, not the concentration reached). PROBEARM and GEOM
  carry measured reference ratios (refratio.py); the other eight are
  labelled, not measured, unless one carries a main-text claim that
  depends on the concentration it reached (Rahul to settle, from the
  list in Claude's reply of 2026-10-30).
  DECIDED (Rahul, 2026-10-30), GEOM: its contrasts leave the main text
  (d40 - d5, tau 0.01 - 0.3, the interaction, REGF b_d, b_tau, b_dtau,
  the CON pairs, TMM, and its finite-J audit contrasts read as
  concentration effects). Reason: they compare cells as if at equal
  concentration, and the achieved reference fractions differ by d at
  nominal tau_0 0.01 (medians of cell means 0.8517 at d 5, 1.1858 at d 10,
  0.4105 at d 40; logs/refratio-20261030.log), so a dimension contrast is
  partly a calibration difference. Labelling tau_0 nominal does not repair
  a contrast whose meaning needs equal concentration. Per-cell slopes
  stay, read as fixed-beta results at the law probe's beta. TAU8 carries
  the concentration-dependence result. GEOM is not recalibrated and not
  re-expressed against achieved concentration.
  DECIDED (Rahul, 2026-10-30), SYNTH and NAMED: to the supplement (already
  supplementary in ANALYSIS_CRITERIA F8), tau_0 labelled nominal, their
  miss described as unmeasured (the regime probe was never audited), not
  small. Lost: the synthetic breadth of the operating-level claim, which
  now covers TAU8's six named objectives at three dimensions. P6.3's
  SYNTH -> NAMED point values go with them.
  DECIDED (Rahul, 2026-10-31), ADAPT: supplement only, labelled
  diagnostic, supporting no claim. It carries the fixed arm's measured
  starting ratios and both arms' drift (logs/adapt0-20261030.log, N40).
  Reasons:
  - The fixed-against-adaptive comparison is dropped (N40, 2026-10-30).
  - The fixed arm is a worse-calibrated duplicate of CONC cells that
    already exist on calprec2 betas with identical run settings. Read
    2026-10-31, not assumed:
    - Archived defaults, control.py 285 to 291 and mechanism.py 282 to
      288: sigma 0.2, dt 0.01, T 1.0, lambda 1.0 in both; K = T/dt = 100.
    - The rerun passes neither default. rerunlib.realise calls both
      modules with rerunlib.DT (0.01) and sigma_for(c, diff), which
      returns SIGMA_ISO (0.2) for both modules, because every CONC and
      ADAPT plan row has sigma_design empty and neither module is in
      the r-indexed list (rerunlib 184, 426 to 431, 923, 926).
    - runs/rerun-plan-20261028-212945/rerun_plan.csv: CONC 144 cells
      (mechanism, centred 72, mix-0.1 72), ADAPT 72 cells (control,
      centred, fixed 36, adaptive 36); both J_inf 50000, T 1.0, K 100,
      M 15, J10. All 36 ADAPT (objective, d, tau_0) cells are CONC
      centred cells.
    - Objectives, MINIMIZER, OFFSET_SCALE and draw_initial are textually
      identical in the two modules. Both realizations draw X0 then one
      standard_normal((J_inf, d)) increment per step, in the same order,
      and apply the same update with the same weighting (control.py 211
      to 250, mechanism.py 193 to 197 and 219 to 240). Bitwise equality
      of the two modules at a shared seed and beta has not been run.
    - The fixed arm differs from CONC only in its beta (a 4000-particle
      probe, control.py 333 to 336, against calprec2) and its seeds.
  - The adaptive arm is a time-varying beta, not the analysed algorithm
    (control.py's own header says so).
  - The fall of concentration during a run is already recorded in CONC's
    extras (le0, le_min) and TAU8's (le0, le_mean, le_min).
  The redesigned adaptive arm (beta_cal start, per-realization target
  exp(le0)/J_inf, CONC seeds) is not written and not run unless the
  paper chooses to explain the tau_0 0.01 departure (settled below).
  DECIDED (Rahul, 2026-10-31), THE TAU_0 0.01 DEPARTURE FROM -1: reported
  as a measured property of the fixed-beta estimand, not explained.
  Reasons:
  - The paper is about whether the rate can be observed at finite
    ensemble sizes, so the departure is a finding, not a defect to
    explain.
  - The explaining version needs a proof of how the cited theorem's
    constants depend on beta, which neither Rahul nor Claude can point to
    yet (primary-text check below), and a factorial design over three
    rival mechanisms (finite-J starting concentration, concentration
    fall during the run, a pre-asymptotic J window at high beta), one of
    whose arms (the adaptive arm) is not the analysed algorithm.
  - One of its tests, round 1's per-J calibration (perjcal), was already
    inconclusive (N36, C2).
  Discipline the reporting version commits the paper to:
  - no explanatory verbs about the departure ("due to", "caused by",
    "collapse" and the like);
  - the drift (le0 - le_min) and the finite-J ratios ESS_0(J)/J/tau_0
    reported as descriptions only;
  - a fitted slope never called a rate;
  - the window (J 10 to 5000, J_inf 50000) named every time a slope is
    quoted.
  On this decision the redesigned adaptive arm is never run.
  DECIDED IN PRINCIPLE (Rahul, 2026-10-31), WINDOW EXTENSION: the same
  fixed-beta algorithm over a wider J window, so that the referee's
  first question (is the departure a finite-window effect; does the
  slope approach -1 at larger J) is answered by measurement rather than
  left open. It runs the same fixed-beta algorithm at the same beta, so
  it does not change the estimand. COST NOT YET APPROVED. Not measured:
  any trajectory at d 40 with J_inf above 50000, any trajectory above
  J_inf 100000 (REFSIZE, d 10, J <= 1250, is the largest measured). The
  J grid keeps J <= J_inf/10 (control.py and mechanism.py), so a window
  to J = 50000 needs J_inf 500000. Under rule 6 a probe measuring wall
  and per-worker peak RSS at each candidate J_inf comes before any
  design. sizetest's plan step prices only the d 40 affected cells'
  larger-reference rerun, not the window extension (sizetest.py 559 to
  591).
  PRIMARY-TEXT CHECK (Claude, 2026-10-31; ~/cbo-refs: fkr2024-siopt.pdf,
  2103.15130v6.pdf, 2312.07373v4.pdf): does either cited theorem state
  how its constant depends on beta (FKR's alpha) in a quotable form?
  - FKR 2024, SIAM J. Optim. 34(3):2973-3004, Theorem 3.8 (p. 2986):
    "C_MFA > 0 depends exponentially on the parameters alpha, lambda,
    and sigma, on T, and on delta^-1." Proposition 3.11 (p. 2988), the
    N^-1 bound (3.13), gives only C_MFA = C_MFA(alpha, lambda, sigma, T,
    C1, C2, M, K, M2, b1, b2). The discussion (p. 2989) refers to "the
    exponential dependence of C_MFA on the parameter alpha". The proof
    (arXiv v6 appendix, Proof of Proposition 3.11) takes a constant
    C(alpha, C1, C2, M, M2, b1, b2) from Carrillo-Choi-Totzeck-Tse 2018
    Lemma 3.2 and applies Groenwall; no explicit form in alpha is
    written. arXiv v6 has the same statements (Theorem 3.8 p. 15,
    Proposition 3.11 p. 16 with (32), discussion p. 17).
  - GHV, arXiv 2312.07373v4 (the ESAIM COCV version cited is still not
    in hand): Theorem 2.6 (p. 10) gives "a constant C > 0 independent of
    J"; Lemma 3.7 (p. 22) "C depending only on (f, beta, p, r) and the
    r-th moment of mu". No explicit beta dependence. Section 2.6 (p. 15),
    about its own Ackley experiment, says the J^-1 scaling "holds only
    for relatively large J", with small-J ESS "close to 1 in the early
    stages": an observation, not a result.
  - Reading: neither text states the beta dependence in a form the paper
    could use to explain a slope departure. FKR states a qualitative
    exponential dependence of an upper-bound constant; an upper bound's
    constant says nothing about the fitted exponent in a finite window.
    The explaining version was never available from these texts.
    Carrillo 2018 (where FKR's alpha constant originates) and the
    Riedl dissertation (in ~/cbo-refs) were not read for this.
  DECIDED (Rahul, 2026-10-30), perjcal (C2): not run (N36 CLOSED).
  - Remove the sentence at tex 703 ("A dedicated experiment controlling
    that concentration exactly at every ensemble size does not make the
    contrast vanish, but is inconclusive about the mechanism of the
    residual"), and the abstract's matching clause at 36 ("a dedicated
    experiment that controls finite-ensemble concentration exactly ...
    is inconclusive about the mechanism of the residual"). The 7.14
    per-J-beta paragraphs (591 to 595) leave the main text.
  - State the finite-J concentration deviation as a property of the
    fixed-beta estimand: under one beta per cell, ESS_0(J)/J of the nested
    subensembles departs from tau_0, by an amount that depends on d. That
    is what one algorithm at different ensemble sizes does, and the
    estimand includes it. The limitation is stated before the principal
    claim, as the referee asks ("stated before").
  - The limitation carries numbers, from the CONC finite-J audit (8.5),
    not from ess_min_sub_mean. Source: logs/rerun-analysis21-20261030-1446.log,
    block "CONC  finite-J audit (8.5)" (line 3822), per-cell summaries in
    runs/rerun-analysis-20261030-144722/analysis_audit.csv (CONC 1440
    rows); the same result as N39's. "CONC audit: 26 of 30 pooled
    intervals exclude 0" (log line 4215). The quantity is ratio(J) =
    ESS_0(J)/J/tau_0, difference d40 - d2, pooled over 12 units. All 30
    pooled differences are positive (higher ratio at d 40). Examples
    copied from the log: tau_0 0.1, J 10 +1.4113 [+1.0867, +1.7383], J
    5000 +0.0350 [+0.0105, +0.0588]; tau_0 0.01, J 5000 +0.4677 [+0.3742,
    +0.5653]. The four that contain 0 are tau_0 0.5, J 40 to 320. At tau_0
    0.01 the points J 10 to 80 have J tau_0 < 1 and are floor-flagged
    (attainability); the text must say so where they are quoted.
  - Why not ess_min_sub_mean: analysis_cells.csv fills it only for
    BETA-ISO (42 rows) and BETA-ANI (12 rows); every CONC row has it
    empty. It is also a different quantity: the minimum over time of the
    subensemble ESS in ess_surface (rerun_analysis.py docstring, L2), not
    ESS_0(J)/J at t = 0.
  - Round-1 perjcal goes to the supplement as a record: labelled a
    different estimand (its own docstring and tex 591 say so) and
    inconclusive, with N30's note that "[0.0069,0.2087]" (tex 593) has no
    generating code and N34's log values (0.0156 [0.0010,0.0576], 0.0964
    [0.0059,0.2265]).
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
  CORRECTED 2026-10-29 (v6 numbering, N3 re-mapping; sup-E finding, N1).
  Replace by: the measured exponent, of E sup_t ||.||^2, is sourced from
  GHV Theorem 2.6 at p = 2 for EVERY objective, not only Ackley and Levy.
  FKR Proposition 3.11 (requires Theorem 3.2's hypotheses, so excludes
  Ackley and Levy) bounds the weaker conditioned quantity sup_t E[.|Omega_M]
  and is cited only as the mean-field component of FKR Theorem 3.8 and as
  the source of the constant traced in Section 4 and S1, never as the
  source of the measured exponent. Theorem 2.6 needs rho_0 with bounded
  moments of all orders (Gaussian qualifies); the q >= 6 reading of GHV
  Remark 2.7 is not re-checked and is not needed. Neither result has a
  parameter condition.

NOT TO BE RUN for the admissible-region claim (N1, N45, 2026-10-29): it
would demonstrate an ill-posed claim. Kept as a record of the costing.
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
