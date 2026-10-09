# CBO-GAP revision plan: scope of the new manuscript

Agreed with Rahul on 2026-10-09. This file records the decision and nothing
has been acted on yet. It is a plan, not prose for the paper. Every
disposition below is taken from notes/DEFECT_LEDGER.md and cites its entry.
No number appears here that is not already in the ledger.

## 1. Framing

- The referee rejected JOGO-D-26-00563 and invited a new manuscript.
- The referee did not dispute the numbers. The dispute was over the
  estimand of the main experiment: beta solved per realization on its own
  reference ensemble, a random-beta design (ledger R3).
- So this is a new paper, not a revision of the old one. It is built around
  questions the archived and rerun data can answer under a fixed,
  independently calibrated beta. The old text is not patched.

## 2. Main text

Three questions, plus the corrected assumption audit.

- Q1. Concentration dependence under a fixed, independently calibrated beta.
  - Calibration size comes from scripts/calprec.py (stage C1; criterion C1
    and the N_star rule in its docstring).
  - Data: the fixed-beta rerun of the concentration arm (section 5).
  - Replaces the random-beta "exact calibration" result (R3, R4).
- Q2. The limits of calibration.
  - The probe ESS problem at small tau_0 (ledger, "Facts about the archive
    that shape the fixed-beta redesign"; R5).
  - The reference-estimability question, which refscale is to test.
    refscale is not in the repository as of 2026-10-09; its script, its
    pre-specified criterion and its run are still to come.
- Q3. Comparison of the two diffusion regimes, isotropic and anisotropic.
  - The anisotropic boundary needs its source theorem: FKR 2022,
    EvoApplications, Theorem 2, condition 2 lambda > sigma^2 (R2).
- Corrected assumption audit.
  - Table 1 is rebuilt as in N2 and O7: class; existence via FKR Thm 6;
    existence via GHV Thm 2.3; A2 constants in l2 and l-infinity; Theorem 12
    applicable; GHV 2.6 rate applicable.
  - Ackley via GHV Thm 2.3 with obligations O1-O8 (R1).
  - Rosenbrock is labelled "unproven" (N2).
  - The synthetic family argument is written out (N15).
  - Every cited theorem is quoted against the version cited (CLAUDE.md
    rule 9; N3).

## 3. Supplementary material

Carried intact, with all numbers and audit trails. Nothing is deleted. The
main text refers to each item in a sentence or two where relevant.

- The six withdrawn results (ledger S2; old supplement S4).
- The nine analysis-design errors (ledger S1; old supplement S3).
- The constant tracing.
- The geometry model and its negative result.
- The regime map (regimemap D and M; ARC4 on the duplicated file).
- The horizon arm and the initial-law arm.
- The reference-size arm.

Carried with each item:
- the archived per-realization files where they exist;
- the disclosed limits where they do not (ARC2: several arms archived only
  as per-(cell, J) means);
- the bootstrap facts (N8: 400-resample intervals; R9: the 97.5th
  percentile).

## 4. Referee points and their dispositions

Disposition classes: text only; re-analysis only (archived files, no
simulation); rerun required; scope change. The ledger's fix types are
T (text), P (proof plus text), A (re-analysis) and R (new simulation).
A proof counts here as text only.

| Point | Subject | Ledger fix type | Disposition | Ledger |
|---|---|---|---|---|
| 1 | Ackley marked as satisfying FKR condition (6) | P + possibly R | Text only (proof via GHV Thm 2.3, O1-O8). A rerun only if a demonstration on objectives satisfying (6), (7), (27) is added; see the ledger's Ackley section | R1, N2, O1-O8 |
| 2 | r_aniso used as a boundary with no cited theorem | P | Text only (cite and quote FKR 2022 Thm 2) | R2 |
| 3 | Beta solved per realization: random-beta estimand | R | Rerun required: fixed-beta concentration arm (EXP-CAL) | R3 |
| 4 | Section 7.14 confounding | T + R | Text plus the R3 rerun; no separate run | R4 |
| 5 | Operating level rests on a 4000-point probe | R | Rerun required: fixed-beta operating-level sweep (EXP-TAU8). EXP-SYNTH + EXP-NAMED only if the 54-cell claim is kept (N10) | R5 |
| 6 | Bootstrap over 12 hand-picked units | A for 7.3, R elsewhere | Re-analysis only for 7.3 (exactcal_real.csv). Elsewhere: scope change, since counts without per-realization data are disclosed as such (ARC2) or replaced by the reruns | R6, ARC2 |
| 7 | "Moved the statistic by 0.300" from unpaired runs | T | Text only (reword), or pair inside the new design | R7 |
| 8 | Sign of the exponent in E_J ~ C J^-gamma | T | Text only; recheck every sign-bearing definition | R8 |
| 9 | "95% interval" is the 97.5th percentile in code | T + A/R | Text only (state 97.5%). Re-analysis at 95% where per-realization data exist (7.12, 7.14, 7.15); the rest cannot be recomputed (ARC2) | R9, N8 |
| 10 | Shorten and reorganize | T, last | Scope change: this plan (new paper, supplement split) | R10 |

## 5. Compute actually required

Two runs are required. Both use a fixed beta calibrated once per cell on a
sample of the size calprec.py's N_star rule sets:

- the fixed-beta rerun of the concentration arm (EXP-CAL; R3, R4);
- the fixed-beta rerun of the operating-level sweep (EXP-TAU8; R5).

Everything else in the archive stands, under the determinism gate (ledger,
"Determinism gate"; G2).
- Archived numbers are compared only with numbers from a platform where
  detcheck has passed and the pass is recorded in ENVIRONMENT.md.
- Linux box: passed.
- Kaggle: not yet run (G2, K1, K3).

Prerequisites before either rerun:
- calprec.py full run, giving N_star;
- per-worker peak RSS measured for the rerun design (CLAUDE.md rule 6);
- the gate passed on the platform that runs it;
- an injective seed table (N6) and per-realization, per-J output
  (CLAUDE.md rule 5).

Conditional compute. These are not in scope unless decided:
- EXP-SYNTH + EXP-NAMED, if the 54-cell claim is kept (R5, N10);
- the Griewank demonstration (ledger, Ackley section).

## 6. New relative to the submitted version, not from the referee

The largest single text change (ledger N1).

- What the paper measures: the J^-1 exponent. That is the conclusion of the
  mean-field approximation results, FKR Proposition 16 (cited as 3.11) and
  GHV Theorem 2.6.
- Those results carry no parameter condition. The condition
  2 lambda > d sigma^2 is a hypothesis of FKR's convergence-to-minimizer
  theorem (arXiv v6 Theorem 12, cited as 3.7). That theorem's conclusion,
  the decay of V(rho_t), is not measured by the paper.
- So the submitted paper's central conceptual claim compares the hypothesis
  set of one theorem with the finite-window behaviour of another theorem's
  conclusion.
- Consequence: the "fourth result" and the "central conceptual point" are
  withdrawn, or restated as prefactor dependence on (r, d, tau_0).
- Proof obligation before any text is written: confirm against the SIAM
  text that Proposition 3.11's hypotheses contain no parameter condition
  (N1, N3).
