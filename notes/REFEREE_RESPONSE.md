# CBO-GAP referee response checklist (JOGO-D-26-00563)

This is a working checklist, not text for the referee. There is one section
per referee point in referee/JOGO_report.pdf. Every section has the same six
fields:

- the demand, in my words;
- what the submitted manuscript says (section and printed page of
  referee/JOGO-D-26-00563.pdf, with the source line of
  manuscript/sn-article.tex);
- the ledger disposition;
- the text that must change;
- what must be recomputed;
- the evidence that will close the point.

The evidence field stays blank until the run or the rendered diff exists
(CLAUDE.md rules 2 and 8). Counts of cells and realizations come from
Table 2 (printed page 12) and from the archived scripts' grids
(notes/RERUN_PLAN.md).

Page numbers are the article's printed page numbers. The submitted PDF puts
two Editorial Manager pages before the article's page 1.

---

## Point 1. Ackley's classification in Table 1

- Demand. Ackley fails condition (6) near the origin. So the Ackley cells
  have not been shown to satisfy the hypotheses of the cited theorem, and
  the "different sets" conclusion needs a well-posedness result that covers
  Ackley, or objectives whose assumptions are fully verified.
- Manuscript.
  - Table 1, Section 3, p. 5 (tex 124) marks Ackley "yes" under (6).
  - Section 2, p. 5 (tex around 106) makes [3, Theorem 3.2], which requires
    (6), the only existence result for [3, Theorem 3.7].
  - Section 7.12, p. 21 (tex 547), "Admissibility does not imply
    observability": the three failing admissible cells are all Ackley.
  - The abstract's "Fourth" result (p. 2; tex 40) and the Conclusions'
    "central conceptual point" (p. 29) rest on this.
- Ledger. R1 (P, possibly R), with obligations O1 to O8, plus N1, N2 and N15.
  The route is existence through GHV Theorem 2.3 (Ackley in A(0,0,0),
  rho_0 in P_4).
  N1 goes further than the referee. The J^-1 exponent comes from FKR
  Proposition 16 (cited as 3.11) and GHV Theorem 2.6, and neither carries a
  parameter condition. So "admissible cells fail" is a finite-window
  prefactor effect that those theorems permit.
- Text to change.
  - Rebuild Table 1 with the N2/O7 columns: class; existence via FKR Thm 6;
    existence via GHV Thm 2.3; A2 constants in l2 and l-infinity; Thm 12
    applicable; GHV 2.6 rate applicable.
  - Prove O1 to O8 line by line. Label Rosenbrock "unproven", including its
    uses in EXP-SIGMA, EXP-ANISO and EXP-CLIFF.
  - Write out the synthetic-family argument (N15).
  - Section 2's existence paragraph: cite GHV 2.3 alongside FKR.
  - Section 7.12: rewrite "Admissibility does not imply observability" as
    prefactor dependence on (r, d, tau0), or withdraw it (N1).
  - Withdraw or restate the abstract's "Fourth" and the Conclusions'
    "central conceptual point".
  - Check every theorem number against the version cited (N3; CLAUDE.md
    rule 9).
- Recompute.
  - The proof itself needs no compute.
  - The Ackley cells are rerun anyway under the full fixed-beta rerun
    (notes/RERUN_PLAN.md).
  - Optional: a demonstration on objectives that satisfy (6), (7) and (27)
    outright. Sphere and Rastrigin are already in EXP-ONSET. Adding Griewank
    is 240 cells, 2880 realizations (ledger, Ackley section). Not decided.
- Evidence. The O1 to O8 proofs, checked against the GHV ESAIM primary text,
  which is not in the repository. A rendered-PDF diff. ______

## Point 2. Isotropic and anisotropic parameter conditions

- Demand. Cite the theorem behind each boundary, r_iso = 1 and r_aniso = 1,
  separately, and audit its assumptions. The admissible/non-admissible split
  in 7.10 to 7.15 must have an unambiguous basis.
- Manuscript.
  - Section 1.2, p. 4 (tex 82) calls both r_iso and r_aniso the ratio "of
    [3, Theorem 3.7]" and says "so r = 1 is the boundary in each case".
  - [3] treats isotropic diffusion only. No anisotropic theorem is cited
    anywhere in the paper.
- Ledger. R2 (P). The source is Fornasier-Klock-Riedl 2022 (EvoApplications,
  DOI 10.1007/978-3-031-02462-7_46), Theorem 2, condition 2 lambda >
  sigma^2. Its A2 uses l-infinity balls with nu in (0, 1/2]. It is not in the
  reference list. N1 (which theorem owns the exponent) and O2 (Ackley's
  anisotropic A2 constants) also bear on this point.
- Text to change.
  - Section 1.2: give each r its own theorem, quoted with that version's
    numbering, and add FKR 2022 to the references.
  - State that both are hypotheses of convergence-to-minimizer theorems, not
    of the mean-field rate results (N1).
  - Audit every "admissible", "in-condition" and "out-of-condition" label in
    Sections 7.10 to 7.15, Tables 7, 9 and 10, Figs 4 and 5, the abstract and
    the Conclusions.
- Recompute. None.
- Evidence. Quoted theorem statements from the FKR 2022 and FKR 2024 primary
  texts (neither is in the repository). A rendered-PDF diff. ______

## Point 3. The "exact calibration" changes the estimand

- Demand. beta solved on each realization's own reference makes beta random.
  Fix one beta per (f, d, rho_0, tau0) from an independent, large enough
  calibration sample, or from an accurate estimate of the population tau.
  Hold it fixed over every realization and every J, and rerun the main
  dimension/concentration experiment.
- Manuscript.
  - Section 7.13, pp. 22-23 (tex 551 onward): the exact-calibration protocol
    and its random-beta description.
  - Section 6 "Calibration", p. 11.
  - Section 7.3 and Table 3, pp. 13-15 (tex 360-396): the headline numbers.
  - Abstract, first result. Conclusions, p. 29.
- Ledger. R3 (R). Facts that shape the redesign are in the ledger section of
  that name. The probe protocol is already fixed-beta but imprecise: the
  probe ESS is 40 at tau0 = 0.01.
- Text to change.
  - Section 7.3, Table 3 and Fig. 2 are rebuilt on the fixed-beta rerun.
  - The exact-calibration and probe results move to the supplement as two
    superseded protocols.
  - Section 6 states the calibration: the size N_star from calprec C1, or a
    declared beta under refscale outcome O2.
  - Abstract and Conclusions follow.
- Recompute.
  - The concentration arm under a calprec beta: the EXP-MECH/EXP-CAL grid,
    144 cells, 2160 realizations, run once (RERUN_PLAN F2).
  - Prerequisites: the refscale outcome, calprec stage C1 with N_star, and
    measured RSS.
- Evidence.
  - refscale run folder ______
  - calprec C1 run folder ______
  - rerun run folders ______
  - rendered diff ______

## Point 4. Confounding in the finite-J audit (Section 7.14)

- Demand. Calibrating the reference does not calibrate the nested
  subensembles. The per-J beta design changes the algorithm along the curve.
  So the residual 0.054, 0.059, 0.078 is not yet a dimension effect. State
  the limitation before the claim, and let the fixed-beta experiment decide
  what survives.
- Manuscript.
  - Section 7.14, pp. 23-24 (tex 583 onward).
  - Section 7.3, pp. 13-14: the attainability floor.
  - Abstract, "Second". Conclusions, p. 30.
- Ledger. R4 (T + R).
- Text to change.
  - Reorder so that the limitation comes before the numbers.
  - Under a fixed beta, ESS_0(J)/J is a property of the algorithm at size J.
    Report it descriptively per J from the rerun's per-realization columns
    (RERUN_PLAN F7).
  - Move EXP-PERJ to the supplement as a different estimand (RERUN_PLAN F4).
- Recompute. Covered by point 3's rerun, which writes log ESS_0(J) for
  every nested J.
- Evidence. ______

## Point 5. The operating level in Section 7.5

- Demand. "tau0 >= 0.1 is sufficient in all 54 cells" holds under the probe
  protocol, and Section 7.13 shows that protocol misses its target. Recompute
  under a defensible fixed beta, or restrict the claim to the protocol.
- Manuscript.
  - Section 7.5, pp. 16-17 (tex 418-442), and Table 5, p. 16.
  - Fig. 1, p. 27.
  - Conclusions, p. 30: "operationally sufficient in all 54 cells".
  - The two different "54 cells" are N10.
- Ledger. R5 (R), N10.
- Text to change.
  - Restate the operating level in terms of the calibrated concentration
    tau(beta), with its uncertainty.
  - Resolve N10 (the 3 x 18 named cells of Table 5 against the 18
    configurations x 3 d of Section 7.5).
  - Correct the Conclusions.
- Recompute.
  - EXP-TAU8: 144 cells, 2160 realizations.
  - EXP-SYNTH: 72 cells, 864 realizations.
  - EXP-NAMED: 36 cells, 432 realizations.
  - All three are in the full rerun.
- Evidence. ______

## Point 6. Uncertainty for the headline dimension contrasts

- Demand. Table 3 bootstraps 12 "hand-selected" objective-law combinations,
  which are not a sample from a defined population. The main contrasts need
  a realization-level analysis. Variation across the chosen objectives and
  laws is reported separately, as heterogeneity over the test set.
- Manuscript.
  - Table 3 caption, p. 14 (tex 363): "the twelve combinations are
    resampled with replacement and each contributes the mean of its fifteen
    realizations".
  - The Section 7.3 regression and the pairwise target contrasts, pp. 14-15,
    use the same 12 units.
  - Section 6 "Uncertainty", p. 11 (tex 309), declares the realization as
    the resampling unit everywhere else.
  - Section 7.10, p. 19, uses "bootstrap intervals over objectives".
  - Section 7.14, p. 24, uses "the pre-specified objective unit".
- Ledger. R6 (A for 7.3, R elsewhere), ARC2, N6, N8.

### 6a. What the archive can and cannot support

Five archived files carry per-realization data (ARC2):

- exactcal_real.csv: per realization, per J;
- perjcal_real.csv: per realization, per J;
- rmapj_real.csv: per realization, per J;
- regimemap_M_real.csv: per-realization slope only, no per-J errors;
- regimemap_D_real.csv: per-realization slope only, no per-J errors.

Everything else is per (cell, J) mean with a standard error, or per cell
only. The rows are read from the generating scripts (notes/RERUN_PLAN.md).

Realization-level intervals CAN be computed from the archive for:

| Claim (section, page) | Source file | What is computable | Caveat |
|---|---|---|---|
| Table 3 upper and middle blocks; 7.3 regression b_d, b_tau, b_dtau; pairwise target contrasts; per-objective changes; within-block spreads (7.3, pp. 13-15) | exactcal_real.csv | All of it, on any window, because E_J is stored per realization | The estimand is the random-beta one of point 3. Ackley and sphere share every seed (N6), so their realizations must be resampled jointly by index. Supplement use only. |
| 7.12 Table 7, Fig. 4, axis ranges, b3 interaction, rate-consistency counts (pp. 20-21) | regimemap_M_real.csv | Cell-mean slopes, contrasts, counts at any percentile level | No refit on another window (no per-J errors). Probe-calibrated. |
| 7.15 Tables 9 and 10, S(1,3) and S(0.75,3) trends, paired gaps, onset intervals, counts (pp. 24-27) | regimemap_D_real.csv, rmapj_real.csv | All of it, on any window | Probe-calibrated. |
| 7.11 realized trace ratios (p. 19) | regimemap_D_real.csv, regimemap_M_real.csv | Realized trace ratio per pair | Descriptive. |
| 7.14 per-J control (EXP-PERJ) (p. 24) | perjcal_real.csv | All of it | A different estimand (point 4). |
| 7.14 finite-J audit, 22 of 30 intervals (p. 24) | finitej.py rerun from exactcal_real.csv seeds and beta | Recomputable, no trajectories | Random-beta estimand. |

Realization-level intervals CANNOT be computed from the archive for the
claims below. Each needs a trajectory rerun of the listed row:

| Claim (section, page) | Archived file and level | Rerun row | Cells | Realizations |
|---|---|---|---|---|
| Table 3 lower block (probe); 7.3 "0.174"; 7.8 Table 6 and the per-d moves (pp. 14, 17-18) | mechanism_raw.csv, per (cell, J) | EXP-MECH | 144 | 2160 |
| 7.2 B-matched slopes; 7.3 "0.379 over 144 B-matched cells"; 7.7 initial-law slopes at d = 40; 7.1 half-range comparison over 144 cells (pp. 13, 17) | visibility_raw.csv, per (cell, J) | EXP-LAWPANEL | 144 | 2880 |
| 7.2 beta surface (Table 2 rows only; not quoted in 7.3 onward) | ess_surface_raw.csv, per (cell, J) | EXP-BETA-ISO / EXP-BETA-ANI | 42 / 12 | 840 / 240 |
| Table 4 verdict counts and drift (7.4, p. 15) | control_raw.csv, per (cell, J) | EXP-ADAPT | 72 | 1080 |
| Table 5, Fig. 1, the 7.5 named crossings 0.0105-0.0786 (pp. 16-17) | boundary_raw.csv, per (cell, J) | EXP-TAU8 | 144 | 2160 |
| 7.5 "36 of 36 synthetic and 18 of 18 named", "16 of 36 and 9 of 18"; 7.1 quadratic-term intervals (pp. 13, 16) | regime_B_synth.csv, regime_C_named.csv, per cell | EXP-SYNTH / EXP-NAMED | 72 / 36 | 864 / 432 |
| 7.6 reference-size extrapolation and its intervals (p. 17) | regime_A_reference.csv, per cell | EXP-REFSIZE | 12 | 144 |
| 7.7 horizon, 24 cells (p. 17) | regime_D_horizon.csv, per cell | EXP-HORIZON | 24 | 288 |
| 7.9 tau_crit, its regression and cross-validation (pp. 18-19) | law_synth.csv, per cell (not in ARC2's list) | EXP-GEOM | 336 | 4032 |
| 7.10 coefficient intervals and counts 71/93/115 and 57/77/86 (p. 19) | sigma_raw.csv, per (cell, J) | EXP-SIGMA | 288 | 3456 |
| 7.11 equivalence verdicts, 3 of 18 equivalent, 2 outside (pp. 19-20) | crossed_raw.csv, per (cell, J) | EXP-ANISO | 288 | 3456 |
| 7.15 r = 5 cells (p. 27) | cliff_raw.csv, per (cell, J) | EXP-CLIFF | 144 | 1728 |

One number has no identified source. The Section 7.2 power-law exponents
(p. 13) come, by their docstrings, from ess_extend.py and ess_panel.py
(Supplementary Table S1). Their outputs are not archived (ARC6). No interval
of any kind can be recomputed for them.

### 6b. What closes point 6 in the new paper

Every rerun row archives per realization and per J (RERUN_PLAN). The
analysis script pre-specifies the following in its docstring, with worked
examples (CLAUDE.md rule 5):

- Primary uncertainty. A stratified bootstrap over realizations within each
  cell, with the design (objectives, laws, d, tau0) held fixed. The slope is
  refitted per resample on the pre-specified window. Seed-paired arms are
  resampled jointly by realization index.
- Heterogeneity. The per-(objective, law) contrasts are reported with their
  spread over the chosen test set, described as heterogeneity over that set.
  No population inference is claimed, and no sampling mechanism is asserted.
- Level and resamples. The confidence level and the number of resamples are
  stated, and match the code (point 9; N8).

Text to change:

- the Table 3 caption, Sections 6 and 7.3, and every "interval over
  objectives" in 7.10 and 7.14;
- N8 ("every interval reported in this paper is the 4000-resample value" is
  false);
- the Appendix A claim that per-realization CSVs exist for every
  confirmatory run (ARC2).

Recompute: the full rerun (RERUN_PLAN). The re-analysis of exactcal_real.csv
is for the supplement only.

Evidence: ______

## Point 7. "Moved the statistic by 0.300"

- Demand. The probe and exact runs used different random streams, so their
  difference mixes the protocol with sampling variation. Change the wording,
  or provide a paired rerun or an interval for the difference.
- Manuscript.
  - Section 7.3, p. 15 (tex 396): "Changing the calibration procedure moved
    the statistic by 0.300 ... These are measured effects of two protocol
    decisions".
  - Section 7.13, p. 23 (around tex 563): "moved the point estimate by
    0.300", "the measured effect of a protocol change".
- Ledger. R7 (T). The runs are not seed-paired: mechanism.py's counter
  starts from 20260821 and exactcal.py's formula from 20260822.
- Text to change.
  - Remove "measured effect" and "moved". Report the two numbers as coming
    from independent experiments under different protocols, with no
    attribution.
  - In the new paper this comparison belongs in the supplement.
- Recompute.
  - None for the wording.
  - Optional: a probe-calibrated arm seed-paired with the fixed-beta
    concentration arm (same seed key, two betas), 144 cells and 2160
    realizations more. This would give a paired protocol contrast. Not
    decided.
- Evidence. A rendered-PDF diff. ______

## Point 8. Sign of the fitted exponent

- Demand. With gamma-hat the fitted slope and about -1, write E_J ~ C
  J^gamma. Otherwise, with C J^-gamma, the theoretical gamma is 1. Make it
  consistent everywhere, including the quantities defined from signs of
  gamma-hat.
- Manuscript.
  - Section 7 opening, p. 12 (tex 348): "E_J approx C J^{-gamma}".
  - Section 1.2, p. 3 (tex 66) defines gamma-hat as the fitted slope and
    Delta = -1 - gamma-hat.
  - Sign-bearing definitions elsewhere:
    - Section 7.9 delta and tau_crit, p. 18;
    - Section 7.12 Delta regression, p. 20;
    - Section 7.15 S(r1, r2), p. 25;
    - "change 2 -> 40" in Table 3, p. 14;
    - Fig. 3 left, "-gamma-hat", p. 28.
- Ledger. R8 (T).
- Text to change.
  - Write E_J ~ C J^gamma, with gamma = -1 the benchmark.
  - Recheck every item listed above. The severity sign incident in CLAUDE.md
    ("Known failure modes") is why every one must be checked.
- Recompute. None.
- Evidence. A rendered-PDF diff, and a list of every occurrence checked.
  ______

## Point 9. The level of the bootstrap bound

- Demand. If the interval is a two-sided 95% percentile interval, its upper
  end is the 97.5th percentile, not a one-sided 95% bound. State the level
  and the construction consistently.
- Manuscript.
  - Section 1.2, p. 3: "the upper end of a bootstrap 95% interval".
  - Table 5 caption, p. 16: "the one-sided reading of a one-sided bound".
  - Table 9, p. 25: "95% CI".
  - The scripts print "bootstrap 95% upper bound".
- Ledger. R9 (T + A/R). In code the upper end is the 97.5th percentile
  (regimemap, rmapj, perjcal, partm, reboot use [2.5, 97.5]; visibility and
  regime use 97.5). N8 also applies: most intervals use 400 resamples, not
  4000.
- Text to change.
  - State the criterion as an upper one-sided 97.5% percentile bound, or
    redefine it as one-sided 95% (the 95th percentile).
  - Either way, fix the choice in the rerun's analysis docstring before
    execution, with a worked example.
  - Correct N8.
- Recompute. Every verdict count, at the declared level, from the rerun's
  per-realization files. Archived counts can be recomputed only where
  per-realization data exist (6a).
- Evidence. ______

## Point 10. Shorten and reorganize

- Demand. Move the history of withdrawn hypotheses, failed criteria, lost
  files and superseded analyses to the supplement. Build the main paper on a
  few cleanly posed questions: concentration dependence, finite-J
  observability under a fixed algorithm, and the two diffusion regimes.
- Manuscript.
  - The whole of Section 7, pp. 12-27.
  - Section 8, p. 27.
  - The Supplement.
- Ledger. R10 (T, last).
- Text to change. The new paper per notes/REVISION_PLAN.md sections 1 to 3:
  Q1, Q2, Q3 and the corrected assumption audit, with the supplement
  carrying the record intact. This is written last, after the science is
  settled.
- Recompute. None of its own.
- Evidence. The new manuscript and its rendered PDF. ______
