# CBO-GAP session state

Read this file first in a new session, after CLAUDE.md. It records where the
project stands and cites a log or a commit for every claim. Every number here
is copied from a file in logs/ or runs/. If this file and a log disagree, the
log is right and this file is stale.

Written 2026-10-10, at commit 7592b03. While this was written the refscale full
run was still in progress on Kaggle.

## 1. Settled

### 1.1 Determinism gate

- The gate is scripts/detcheck.py. Its criteria D1 to D3 are pre-registered in
  its docstring (ledger, section "Determinism gate"; G3 closed by acf1786).
- Linux laptop (Python 3.12.3, NumPy 2.5.3): PASS with the repository archive
  and with a separate read-only copy. Logs: logs/detcheck-v3-full-repo.log and
  logs/detcheck-v3-full-separate.log, line 86 of each: "VERDICT   D1+D2: PASS
  D3: PASS   OVERALL: PASS". Recorded in ENVIRONMENT.md (061a58d). The v2
  logs pass as well (64c37a9).
- Kaggle (Python 3.13.15, NumPy 2.1.3, 4 workers): PASS. Log:
  runs/detcheck-kaggle-20261009-094955/cbo-detcheck.log, same VERDICT line.
  Recorded in ENVIRONMENT.md (23a46c8). Ledger G2 closed.
- Correction to the brief. The gate has passed on two platforms, not three.
  The archive's platform (Windows 7, Python 3.8.10, NumPy 1.24.4) is the
  reference the gate compares against. The gate was never run there, and the
  archive stores no X0 to compare (ledger K4(b), K4(c)).
- Consequence (ledger K4): numbers from the laptop and from Kaggle may be
  compared with archived numbers (CLAUDE.md rules 7 and 16).

### 1.2 Archive reconciliation

- zenodo-v1/ holds the 68 deposited files, read-only. Manifests:
  zenodo-v1.sha256 and zenodo-v1-manifest-claude.sha256 (423a4d4).
- The archive's disagreements with the Data Availability statement are ledger
  ARC1 to ARC7, opened 2026-10-08 (423a4d4). ARC1 to ARC5 are still open.
- The archive bytes the gate reads are identical on the laptop and on Kaggle,
  and equal to zenodo-v1.sha256 (ledger K4(a)).

### 1.3 Kaggle pipeline

- scripts/kgrun.py runs the whole cycle: bundle, dataset version, ready-wait,
  runner, push, poll, fetch, manifest. The runner finds the mount instead of
  assuming it (ledger K3, closed by 4c9824c). On 2026-10-09 and 2026-10-10
  Kaggle mounted the dataset at candidate 2,
  /kaggle/input/datasets/ericsom/cbo-gap-archive (detcheck log above;
  runs/refscale-smoke-kaggle-20261009-102942/cbo-refscale-smoke.log).
- Fetch writes sha256.txt through manifest.write_manifest (a256c4d).
- Every kaggle command is denied to Claude (061a58d; CLAUDE.md rule 14).
- One complete round trip after the gate: the refscale smoke, 131 s on Kaggle
  (logs/kgrun-refscale-smoke.log: "finished after 131 s"; committed in
  7592b03).

### 1.4 Scope

- notes/REVISION_PLAN.md (7483dcd) sets the scope. The resubmission is a new
  paper on three questions (Q1 concentration dependence under fixed beta, Q2
  limits of calibration, Q3 isotropic against anisotropic) plus the corrected
  assumption audit. The exploratory history goes to the supplement intact.
- Amended 2026-10-10 by Rahul's decision, recorded in notes/RERUN_PLAN.md:
  the whole experiment matrix of Table 2 is rerun under fixed beta, with
  per-realization archiving. This replaces REVISION_PLAN section 5, which
  named two reruns.

## 2. In flight

### 2.1 refscale full run, Kaggle job "refscale"

- Script: scripts/refscale.py, unchanged since c6dc0cb (md5
  cdb5763e9080450d84cda69b5226d532 on 2026-10-10).
- Launched with:
  kgrun.py run --job refscale --script refscale.py --args "--workers 4
  --ladder 4000000,16000000,64000000,256000000,1024000000"
  (logs/kgrun-refscale-full.log, header and "runner will call" line). The
  dataset version was pushed at 2026-10-10T07:08:55, and the kernel was
  RUNNING at the last poll in that log.
- logs/kgrun-refscale-full.log is not committed. The local kgrun process
  still has it open. Commit it with the fetched run folder once kgrun exits.
- Cells: ackley and sphere, d = 40, centred law, nominal tau0 0.01 and 0.1.
  N_CAL = 1,000,000. Six replicates per rung. Ladder 4M, 16M, 64M, 256M, 1G.
- Pre-specified criteria (refscale.py docstring, fixed 2026-10-09):
  - E1, equivalence gate: streamed and held log-ESS agree to relative 1e-12
    on the two lowest rungs, or the run stops with exit 3.
  - C5, precision: range/median over six replicates <= 0.025.
  - D1, drift: |median_n - median_next| / median_next <= 0.025. The top rung
    is untested.
  - Adequate rung: passes both C5 and D1.
  - S1: share of sum w^2 carried by the largest term. Reported, no threshold.
  - X1: sphere exact tau(beta) = (1+4b)^(d/2) / (1+2b)^d, with the relative
    error of each median.
  - F1: extrapolate a required size only if the fitted slope of
    log(range/median) on log n is negative and the second-highest rung
    passes D1.
- Outcomes, fixed in advance (2026-10-09):
  - O1: an adequate size is reachable. calprec C4 is rerun at that reference
    size and N_star becomes declarable.
  - O2: no adequate size is reachable. The tau0 = 0.01 cells are redefined by
    a declared fixed beta with tau(beta) and its uncertainty, and the paper
    states that the tightest target cannot be identified by direct Monte
    Carlo. This is an estimand change, decided before the run.
  - O3: sphere is adequate where ackley is not. The limit is the
    objective's tail, and X1 is the evidence.
  - "Within reach of a real run" is judged by Rahul from the printed wall
    times and peak RSS. The script does not decide it.
- Before any number from it is used: read the header (CLAUDE.md rule 18), and
  check exit code 0 and "E1 PASSED".

## 3. Measured so far about the science

Every item is a measurement under the stated protocol. Smoke verdicts are
not results.

### 3.1 calprec, the calibration-size question (laptop)

- logs/calprec-refcheck-v2.log is the current version, with check C4. It
  covers one cell (ackley, d = 40, centred), 2 replicates and a 4,000,000
  reference. It is not the production stage C1, which uses REPS = 24 over 48
  cells and has never been run.
  - C1 statistic at tau0 = 0.5: 0.0323 at N = 4000, 0.0020 at N = 1,000,000.
  - C1 statistic at tau0 = 0.1: 0.1796 at N = 4000, 0.0482 at 256,000,
    0.0343 at 1,000,000.
  - C1 statistic at tau0 = 0.01: 0.8897 at 4000, 0.5215 at 64,000, 0.1308 at
    256,000, 0.3187 at 1,000,000. No level passes.
  - C4 fails at tau0 = 0.01 at every level: "worst half-to-half disagreement
    0.3455 at ackley d=40 centred tau0=0.01 N=4000", "rows marked UNRELIABLE:
    5 of 15".
  - C2, the archived 4000-point probe: realized/target spread [0.1103,
    0.1107] at tau0 = 0.01.
  - Verdict printed: "The reference is not adequate everywhere (C4)" and
    "N_star: NO level in [4000, 16000, 64000, 256000, 1000000] satisfies C1
    in every cell."
- logs/calprec-quick-cbopaths.log (quick smoke, labelled "not a result")
  shows the same pattern at d = 40: C4 bad in 2 cells at tau0 = 0.01.

### 3.2 refscale smoke (Kaggle, 2 replicates; C5, D1 and F1 are not results)

Source: runs/refscale-smoke-kaggle-20261009-102942/cbo-refscale-smoke.log.

- Header: python 3.13.15, numpy 2.1.3, cpus 4, workers 4, mode SMOKE.
- Calibration on 1,000,000 points:
  - ackley tau0 0.01: beta = 6.028534528294139
  - ackley tau0 0.1: beta = 4.117791730834002
  - sphere tau0 0.01: beta = 0.40654222121074113, exact tau(beta) 0.0112133
  - sphere tau0 0.1: beta = 0.2461457179039086, exact tau(beta) 0.0998249
- "E1 PASSED on every replicate and beta at rungs [4000000, 16000000]."
- Rung medians at 4M and 16M:
  - ackley beta(0.01): 0.010302 and 0.009744; ratios 0.2768 and 0.3318;
    largest-term share up to 0.127.
  - ackley beta(0.1): 0.101387 and 0.101326; ratios 0.0507 and 0.0189.
  - sphere beta(0.01): 0.011319 and 0.0114212; ratios 0.1336 and 0.0087;
    relerr(median) +0.0094 and +0.0185.
  - sphere beta(0.1): 0.100223 and 0.0998912; ratios 0.0123 and 0.0017;
    relerr(median) +0.0040 and +0.0007.
- Cost and memory: peak RSS of any reference task 646 MB. Throughput
  2.9e+05 (ackley) and 5.98e+05 (sphere) points per second per worker.
  Projection, a lower bound and not a measurement: at least 2.91 h for the
  ladder to 1G with 6 replicates on 4 workers.

### 3.3 costprobe, per-realization trajectory cost (laptop only)

- logs/costprobe.log: 24 (objective, d) probes, isotropic, sigma 0.2,
  J_inf 50000, tau0 0.1. Walls run from 3.7 s (sphere d = 2) to 52.8 s (levy
  d = 40). Peak RSS over workers 177 MB.
- Projections printed, lower bounds with perfect scaling: EXP-CAL-FIX
  core-time 9h 08m 49s; EXP-TAU8-FIX core-time 11h 16m 24s.
- costprobe has never run on Kaggle.

### 3.4 Trajectory memory on Kaggle

- From the Kaggle gate (ENVIRONMENT.md): peak RSS of the worker was 42 MB for
  R1 (d = 2), 180 MB for R2 (d = 40) and 330 MB for R3 (rmapj, isotropic,
  d = 80), each at J_inf = 50000.

## 4. Not known

- N_star. It has not been declared. Whether the tau0 = 0.01 concentration is
  estimable at all is what refscale is measuring now (O1, O2 or O3).
- Kaggle trajectory throughput. costprobe has not run there.
- Peak RSS at J_inf = 100000 (EXP-REFSIZE). No script has measured it.
- Peak RSS and wall time for every design outside costprobe's 24 probes. These
  are d = 3, 20 and 80 in the isotropic named arms, anisotropic diffusion,
  the synthetic objectives, the T = 2 horizon, and the adaptive arm.
- Whether the objective functions and initial laws defined separately in each
  archived script equal exactcal's. calprec calibrates with exactcal's, so
  this matters for the fixed-beta rerun (notes/RERUN_PLAN.md). Not checked.
- calprec's seed_for reduces the SeedSequence to one uint32
  (generate_state(1, dtype=np.uint32)). Its docstring says "injective by
  construction", but a 32-bit reduction is not injective. refscale.py uses
  the full key. This is not yet in the ledger, and no run is known to be
  affected.
- The kgrun runner does not print a hash of the script it runs. The header
  check of CLAUDE.md rule 18 therefore confirms the Python and NumPy
  versions, but not the script version.
- The primary texts of FKR 2024 (SIAM), FKR 2022 (EvoApplications), GHV 2025
  (ESAIM) and CCTT 2018 are not in the repository. N1, N3, R2 and O6 need
  them (CLAUDE.md rule 9).

## 5. Open ledger entries (notes/DEFECT_LEDGER.md)

- Referee points: R1, R2, R3, R4, R5, R6, R7, R8, R9, R10. All open.
- Ackley proof obligations under R1: O1 to O8. All open.
- Archive: ARC1, ARC2, ARC3, ARC4, ARC5 open. ARC6 and ARC7 need no action.
  S3 is declared and folded into ARC1.
- Newly found: N1 to N15. All open.
- Closed: G1 (e945d17), G2 (23a46c8), G3 (acf1786), K1 (closed through K3),
  K3 (4c9824c). K4 is a record, not a defect.
- ARC2's list of per-cell files omits law_synth.csv (EXP-GEOM) and
  finitej_summary.csv. Both are per cell, not per realization (read from
  law.py and finitej.py). No ledger entry yet.

## 6. Files that carry the plan

- notes/REFEREE_RESPONSE.md: the checklist per referee point.
- notes/RERUN_PLAN.md: every Table 2 row, its script, its grid, and its rerun.
- notes/REVISION_PLAN.md: the scope. Section 5 is superseded by RERUN_PLAN.
