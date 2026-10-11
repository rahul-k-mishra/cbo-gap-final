"""
calprec2.py  --  CBO-GAP round 2: calprec v2, one fixed beta per calibration
                 cell for the fixed-beta rerun, calibrated through each row's
                 own archived module, and measured on a fixed pair of
                 reference sizes

WHAT THIS PRODUCES, IN PLAIN LANGUAGE
-------------------------------------
The specification is notes/CALPREC_V2_SPEC.md (cited as "spec 5" and so
on; the design in force is spec 11c). For every calibration cell

    (module, objective, d, initial law, tau0)

of the four calibrated rows (spec 2, ledger N27), this script calibrates a
fixed beta on independent calibration samples. It then measures the
concentration tau(beta) that this beta actually delivers, on large
independent reference samples of two fixed sizes, 64M and 256M. The
finalize step writes the beta table (calprec2_beta.csv) that the rerun
script reads.

Each cell is labelled:
  - "target": tau(beta) is within 5% of tau0, measured on a reference
    judged adequate;
  - "beta": it is not, or the reference is not adequate, so it cannot be
    shown. The cell is then labelled by its beta, never by a target, and
    both reference sizes are reported (spec 6, ledger N18 O2).

No trajectories are evolved. Nothing in the archive is written to.

DESIGN CHANGE 2026-10-11 (Rahul; ledger N28; spec 11c), before any full
execution. This replaces the earlier versions' rung climb to 1G, the
adequacy search and the per-cell solves. Removed entirely:
  - the climb;
  - case (a) and case (b);
  - the streamed grid solve, and E3 with it;
  - the multi-job continuation (--inputs, --max-rung, calprec2_phaseA.csv);
  - the nine rows outside N27's scope.
The grid-solve design is preserved in ledger N24, spec 11b, and in this
file at commit 0bd7011.

Reason: logs/calprec2-plan-4rows-thr.log. For the 336 cells under the
earlier design, G-CAP estimated:
  - best case 301529 s;
  - worst case 7672526 s;
  - case (a) branch alone 5461019 s.
These are at 2 workers, against a 21600 s ceiling. refscale (ledger N18)
had already answered, on the hardest cell, what the climb asks.

WHAT IS IMPORTED, AND WHAT IS NOT
  * Archive modules and grids come from scripts/costprobe2.py:
    - MODS (hashed by V1);
    - GRID and SOURCE (checked against the archived source by V0);
    - objective_of and probe_sample.
    costprobe2.py's sha256 is printed and stored in the params file.
  * The objective of a cell is its own module's (spec 3, RERUN_PLAN F5).
  * The initial law:
    - mechanism draws it with the module's own draw_initial;
    - boundary, sigma and crossed draw X0 inline in one_realisation, so it
      is drawn as rng.standard_normal((n, d)) + x*, with x* from the
      module's own dict.
    V2 checks that line against the module source.
  * Phase A's bisection is exactcal.beta_on_ensemble.
  * The streamed log-ESS is the refscale composition: exactcal._logsumexp
    is applied per chunk to -beta f and to -2 beta f, and then to the
    vector of chunk results (E1).

CELLS (spec 2, ledger N27)
  The four rows, each with its module:
    CONC  mechanism;
    TAU8  boundary;
    SIGMA sigma;
    ANISO crossed.
  Identical cells of one module are calibrated once. The plan prints the
  deduplicated count. No other row is calibrated by calprec v2; those rows
  keep their archived betas (RERUN_PLAN, scope section).

PROCEDURE PER CELL (barriers between phases; parallel over cells,
replicates and draws)
  A   CALIBRATION.
      - For each N in L_CAL = 4000, 16000, 64000, 256000, 1000000,
        4000000 and each of R = 24 draws: N values (kind 31), then
        beta_hat = beta_on_ensemble(values, tau0, N).
      - beta_adq = the median of the 24 beta_hat at N = 4000000.
  C   REFERENCES AT TWO FIXED SIZES.
      - N_LO = 64000000 and N_HI = 256000000, six independent replicates
        each (kind 32, reps 0 to 5).
      - Each replicate is streamed in chunks of 250000 and evaluated at
        beta_adq.
      - There is no ladder, no climbing and no stopping rule. Every cell
        gets both sizes.
      - Replicate 0 of N_LO is also held, for E1.
  ADEQUACY, judged as refscale judged it:
      - C5m at N_LO: range / median of its six <= 0.054682;
      - AND D1 between the N_LO and N_HI medians <= 0.025.
      A cell that passes both is "adequate at 64M".
  C1  SUFFICIENCY PASS, adequate cells only.
      - The six N_LO replicates are regenerated and evaluated at the 144
        beta_hat and at beta_adq (R1).
      - N_cell = the smallest L_CAL level whose 24 beta_hat all pass C1,
        or none.
  B   PRODUCTION, cells with an N_cell.
      - beta_prod = beta_on_ensemble on a size-N_cell sample (kind 33).
  C'  PRODUCTION CHECK.
      - beta_prod is evaluated on six NEW N_LO replicates (kind 32, reps 6
        to 11): C6.
      - C5m of those six is reported, without a threshold (review D4;
        confirmed by Rahul 2026-10-11).

PRE-SPECIFIED CRITERIA (fixed 2026-10-11, before first execution)
------------------------------------------------------------------
  V0  PLAN IDENTITY.
      (a) costprobe2's P0(a): every grid factor equals the archived
          source's constant.
      (b) Per row, the calibration cells times the levels of the factors
          that do not enter beta equal Table 2's cell count.
      Otherwise exit 2.
      Worked example: SIGMA has 24 cells; 24 x (2 diffusions x 6 r) = 288,
      which is Table 2's count: pass. With five r values the product would
      be 240: exit 2.
  V1  ARCHIVE IDENTITY. Every imported archive module's __file__ lies in the
      archive and hashes to its zenodo-v1.sha256 entry. Otherwise exit 2.
      Worked example: boundary.py hashes to 93d2eb04...b3e4: ok.
  V2  SAMPLER IDENTITY. For every module used, the first line after
      "rng = np.random.default_rng(seed)" in one_realisation that mentions
      "rng" must equal SAMPLER_LINE. Otherwise exit 2.
      Worked example: sigma's line is "X0 = rng.standard_normal((Jinf, d))
      + xs": ok.
  E1  STREAMING EQUIVALENCE, now on the 64M rung (spec 11c).
      - Replicate 0 of N_LO in phase C is held while it is streamed.
      - exactcal.log_ess_of is evaluated on the held array at beta_adq.
      - Requirement: |logESS_streamed - logESS_held| / |logESS_held| <=
        1e-12, against exactcal.log_ess_of.
      - Every cell has that row, so E1 runs for every cell. In finalize, a
        cell without an E1 verdict is flagged "E1 not run", exit 4.
      - A failure gives exit 3.
      Only phase C's replicate 0 is held. The C1 and C' passes over the
      same size are streamed only.
      What E1 does NOT check:
      - the 256M rung. Holding it would take four times the 64M array,
        over the budget;
      - the 145 C1 betas and beta_prod. Those passes use the same
        functions, chunk_terms and combine_terms, at other betas.
      E1 has not been run at 64M before. refscale ran it at 4M and 16M
      (ledger N18). If it fails at 1e-12, the run exits 3. The tolerance is
      not loosened in advance (Rahul, 2026-10-11: "if it fails, exit 3 and
      we look at the number").
      Worked example (refscale): 10.596634733096073 against
      10.596634733096080 gives 6.6e-16: pass.
  R1  REGENERATION IDENTITY.
      - When the C1 pass re-evaluates the six N_LO replicates, tau_hat at
        beta_adq must equal phase C's, compared as repr strings.
      - It applies only when both rows were computed under the same Python
        and NumPy (the "env" column). Otherwise the comparison is reported
        as "R1 not applicable (env differs)", and is not a failure.
      - A failure gives exit 3.
      Worked example: 0.0099834716023 against 0.0099834716023: pass.
  C5m range / tau_ref <= 0.054682, at beta_adq, on the six N_LO replicates.
      tau_ref is the median of the six. The threshold comes from ledger
      N23.
      Worked examples (spec 5):
      - 0.00970 0.00980 0.00985 0.00990 0.01000 0.01010: ratio 0.0405,
        pass;
      - 0.00940 0.00960 0.00975 0.00985 0.00995 0.01010: ratio 0.0714,
        fail.
  D1  |tau_ref(N_LO) - tau_ref(N_HI)| / tau_ref(N_HI) <= 0.025, at
      beta_adq.
      Worked example: 0.00995 at 64M against 0.01003 at 256M gives 0.0080:
      pass.
  ADEQUATE  Passes C5m and D1.
      Worked example: C5m ratio 0.0405 and D1 0.0080: adequate. C5m 0.0405
      with D1 0.031: not adequate (D1 FAIL).
  C1  On the six N_LO replicates, for each level N:
          max over the level's 24 draws of |tau_ref(beta_hat)/tau0 - 1|
          <= 0.05.
      N_cell = the smallest level that passes.
      Worked example: 0.0098 to 0.0104 at tau0 = 0.01 gives 0.04:
      sufficient.
  C6  |tau_ref(beta_prod)/tau0 - 1| <= 0.05, where tau_ref is the median
      over the six C' replicates.
      Worked example: tau0 0.1, tau_ref 0.1042: 0.042, pass.
  LABELS (finalize; each cell gets exactly one of these):
      T   Adequate, N_cell found and C6 passes: "target" with beta_prod.
          tau_ref and its range are the C' median and range.
      BA  Adequate, but C1 finds no N_cell or C6 fails: beta_adq.
          tau_ref and range are those of the six phase-C N_LO replicates.
          Label "target" if |tau_ref/tau0 - 1| <= 0.05, otherwise "beta".
          (Rule CB of the earlier design, applied to beta_adq because no
          solve exists.) Confirmed by Rahul, 2026-10-11. A beta_prod that
          fails C6 has been measured to miss the target, so carrying it
          forward would label the cell by a beta just shown to be wrong.
          Worked example: tau0 0.1, tau_ref(beta_adq) 0.0962: deviation
          0.038, so "target". At 0.0941 the deviation is 0.059: "beta".
      O2  Not adequate: "beta" with beta_adq (ledger N18 O2).
          - The median and range of BOTH sizes are reported, with C5m and
            D1 and which of them failed.
          - tau_ref and its range are those of N_HI, the larger reference.
            The label says "not adequate". Confirmed by Rahul, 2026-10-11:
            N_HI is the larger reference, and D1 could not vouch for it
            against anything bigger.
          This is the expected outcome at the tight targets. It is a
          finding, not a failure, and it does not change the exit code.
      INCOMPLETE  A cell whose rows for a phase are missing or errored is
          labelled "incomplete (<phase>)" and never given a label above.
          Exit 4.
          Finalize expects every cell of the folders' rows. A cell with no
          rows at all (a shard folder not given) is "incomplete (phase A)".
  S1  Largest-term share: reported, no threshold.
  X1  Exact tau for the centred sphere, prod over d of (1 + 4 beta)^(1/2) /
      (1 + 2 beta). Reported for the cell's final beta, no threshold.
      Worked example: d = 2, beta = 0.5 gives 0.75.
  G-RSS  Peak RSS of each task <= 3072 MB. Otherwise a FAIL line and a
      flagged row. The held arrays are:
      - phase A and B (at most 4000000 values);
      - E1's 64M replicate.
      ledger N25 measured this allocation, exactcal.log_ess_of on a held
      64M ackley d = 40 array within beta_on_ensemble: peak 2472.8 MB,
      within budget. The smoke's 4M peaks agree with memprobe's 4M peak:
      301.8 MB for ackley d = 40 against memprobe's 294.3 MB.
      The full job must therefore run on Kaggle, not on the laptop, whose
      free memory can be 1.5 GB (CLAUDE.md rule 6).
  G-CAP  A full run needs --throughput (a verified smoke folder). The
      WORST-CASE ESTIMATE must be at most 21600 s, or exit 2.
      Per cell:
          phase A
        + phase C (6 x N_LO and 6 x N_HI at one beta)
        + E1's held log_ess_of on N_LO
        + the adequate branch:
          - the C1 pass (6 x N_LO at 145 betas);
          - B (a 4M draw and solve, the largest N_cell);
          - C' (6 x N_LO at one beta).
      The worst case assumes every cell is adequate. The best case assumes
      none is.
      The job's estimate is the sum over its cells, divided by workers.
      - A pass costs n x (t_draw + n_beta x t_beta). A held solve costs
        n x (t_draw + t_solve).
      - One held log_ess_of costs n x t_solve / 201, because
        beta_on_ensemble calls log_ess_of 200 times in its loop and once at
        return (exactcal.py 176-183).
      SHARD COUNT. The plan prints two shard counts. Cells are assigned to
      shards by index modulo k.
      - The count at the TARGET: the smallest k for which every shard's
        estimate is at most --shard-target x 21600 s (default 0.5, so
        10800 s). This is the recommended count, because the estimate
        ignores barrier idle and phase tails and is not a bound.
      - The count at the full ceiling, 21600 s.
      G-CAP itself still refuses a job only against the full ceiling,
      never against the target.
      Worked example (illustrative values): shard estimates must fall to
      10800 s at the target. A count of 40 that leaves a largest shard of
      19968 s fits the ceiling but not the target; the target needs more.
      The estimate assumes perfect scaling. It ignores barrier idle time
      and the tail of each phase. It is an estimate, NOT a bound.
      Worked example (illustrative values): 6 x 64M at one beta with
      t_draw 3e-6 and t_beta 5e-8 costs 6 x 6.4e7 x 3.05e-6 = 1171 s.
  G-MEM  MEMORY GUARD, full mode only (Rahul, 2026-10-11; review U3).
      Before any draw, MemAvailable is read from /proc/meminfo. The job
      refuses (exit 2) when it is below 2 x 2472.8 = 4945.6 MB, or cannot
      be read. 2472.8 MB is N25's measured peak of one held 64M
      beta_on_ensemble. The message says the job belongs on Kaggle.
      Worked example: MemAvailable 30000 MB passes; 3900 MB refuses.
      The guard does not scale with --workers: with 4 workers, up to four
      held 64M tasks can run at once.
  T1  PER-TASK TIMEOUT (costprobe2's scheduler).
      - Each task runs in its own process, at most --workers at once.
      - A task still running after TIMEOUT_S is terminated and written as
        an error row ("timeout"). A process that exits without a result is
        written as an error row ("worker exited").
      - TIMEOUT_S = 5 x the estimated wall of the job's largest task.
        - Task types: a phase-A or B solve, an N_LO pass at one beta with
          E1, an N_HI pass at one beta, and an N_LO pass at 145 betas.
        - The estimate is from the throughput table, printed at the head
          of the run.
      - In smoke mode, where no table exists yet, the projection is
        (4000000 + 2 x 1000000) points / 3.16e5 points per second. It is
        doubled for the solve and the 145-beta pass, and the timeout is
        floored at 600 s. 3.16e5 is refscale's measured ackley throughput
        (runs/refscale-kaggle-20261010-094820).
      Worked example (illustrative values): largest task estimated at
      700 s gives TIMEOUT_S = 3500 s.

EXIT CODES
  0  completed, every task ok, and no flag. O2 cells are not flags;
  2  setup error (V0, V1, V2, G-CAP, G-MEM, resume, finalize merge);
  3  E1 or R1 failed;
  4  a task errored or timed out, or (in finalize) a cell is incomplete
     or "E1 not run".
  Exit 3 takes precedence over exit 4.

SEEDS (spec 7)
  Every stream is numpy.random.default_rng(SeedSequence(key + (chunk,)))
  at full width (ledger N16), with
      key = (ENTROPY 20261010, kind, module code, objective code, d,
             law code, tau0 x 1e6, n, rep)
  Kinds: 31 calibration, 32 reference, 33 production, 35 smoke.
  - Kind 34, the old design's solve stream, is retired and not reused.
  - Reference keys (kind 32) carry tau0 = 0, as spec 7 says. Cells
    differing only in tau0 therefore share reference streams, and their
    tau_ref values are correlated, not independent.
  - The chunk index is appended to the key, so any chunk can be
    regenerated alone.
  Codes are indices in costprobe2's MODULES, OBJ_NAMES and LAWS.

MODES
  --plan            V0, V1, V2, the cells and, with --throughput, the
                    estimates and the shard count. No draws; nothing
                    written.
  --smoke           Unit costs t_draw, t_solve and t_beta per (module,
                    objective, d, law), written to calprec2_throughput.csv.
                    Not results.
                    The smoke task is unchanged from 0bd7011, so a smoke
                    folder from that version is a valid --throughput.
  (default)         The job.
  --finalize DIR[,DIR]
                    No draws. Merges the verified folders, recomputes every
                    verdict per cell and writes calprec2_beta.csv.
  Selection: --rows, --cells, --shard i --nshards k, --shard-target f.
  Resumption: --resume-from DIR[,DIR] (CLAUDE.md rule 17; every parameter
  must be equal).

OUTPUT (new folder <outdir>/calprec2-<mode>-<timestamp>[-s<i>of<k>]/, every
        file opened "x", every row flushed and fsynced, a task's row
        written once the task completes)
  calprec2_params.csv      the parameters resume and finalize compare
  calprec2_plan.csv        the cells, their shard and rows
  calprec2_tasks.csv       one row per task, with these columns:
                           - tid, phase, cell, key, n, rep;
                           - betas, the per-beta log-ESS, tau_hat and S1
                             share, and the E1 values (";"-joined repr
                             lists);
                           - beta solved, achieved, env, wall, peak RSS,
                             G-RSS flag, error, end
  calprec2_throughput.csv  smoke only
  calprec2_beta.csv        finalize only

HOW TO RUN (from the repository root, venv active)
    python scripts/calprec2.py --plan --workers 4 --throughput DIR
    python scripts/calprec2.py --workers 4 --smoke
    python scripts/calprec2.py --workers 4 --throughput DIR --shard 0 --nshards K
    python scripts/calprec2.py --workers 4 --throughput DIR --shard 0 --nshards K --resume-from DIR[,DIR]
  On Kaggle, kgrun.py ships DIR (--data-dirs) and the resume folders
  (--resume-dirs). notes/CALPREC2_RUNBOOK.md gives the sequence.
    python scripts/calprec2.py --finalize DIR[,DIR]
  --archive and --outdir are resolved by scripts/cbopaths.py.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import inspect                                                  # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cbopaths                                                 # noqa: E402
import costprobe2 as cp                                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = cbopaths.output_root(ROOT)
EC = cp.MODS["exactcal"]
ENV = "python {} numpy {}".format(platform.python_version(), np.__version__)

ENTROPY = 20261010
K_CAL, K_REF, K_PROD, K_SMOKE = 31, 32, 33, 35
L_CAL = [4000, 16000, 64000, 256000, 1000000, 4000000]
R_CAL = 24
N_LO, N_HI = 64000000, 256000000
REF_SIZES = [N_LO, N_HI]
REPS = 6
PRODCHECK_REPS = list(range(6, 12))
CHUNK = 250000
C5M_MAX = 0.054682
D1_MAX = 0.025
C1_MAX = 0.05
C6_MAX = 0.05
E1_TOL = 1e-12
LOG_ESS_PER_SOLVE = 201            # exactcal.beta_on_ensemble: 200 in the loop, 1 at return
RSS_BUDGET_MB = 3072.0
N25_HELD64_PEAK_MB = 2472.8        # ledger N25, logs/memprobe.log: 64M solve peak
MEM_GUARD_FACTOR = 2.0             # Rahul, 2026-10-11 (review U3)
SHARD_CEIL_S = 21600.0
TIMEOUT_FACTOR = 5.0
TIMEOUT_FLOOR_SMOKE = 600.0
REFSCALE_ACKLEY_RATE = 3.16e5     # points/s/worker, runs/refscale-kaggle-20261010-094820
N_SMOKE_DRAW, N_SMOKE_REF, SMOKE_NBETA = 4000000, 1000000, 145
NLEV = len(L_CAL) * R_CAL + 1

ROWMOD = {"CONC": "mechanism", "TAU8": "boundary", "SIGMA": "sigma", "ANISO": "crossed"}
CALROWS = ["CONC", "TAU8", "SIGMA", "ANISO"]

SAMPLER_LINE = {
    "mechanism": "X0 = draw_initial(rng, Jinf, d, objective, init)",
    "boundary": "X0 = rng.standard_normal((Jinf, d)) + MINIMIZER[objective]",
    "sigma": "X0 = rng.standard_normal((Jinf, d)) + xs",
    "crossed": "X0 = rng.standard_normal((Jinf, d)) + xs",
}


# --------------------------------------------------------------------------
# cells and keys
# --------------------------------------------------------------------------

def cal_cells(row):
    """(calibration cells of a row, product of the levels that do not enter beta)."""
    g = cp.GRID[row]
    m = ROWMOD[row]
    if row == "CONC":
        return [(m, o, d, law, t) for o in g["objs"] for d in g["dims"]
                for law in g["laws"] for t in g["taus"]], 1
    if row == "TAU8":
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], 1
    if row == "SIGMA":
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], len(g["diffs"]) * len(g["rs"])
    if row == "ANISO":
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], len(g["diffs"]) * (len(g["sigmas"]) + len(g["rs"]))
    raise ValueError(row)


def all_cells(rows):
    return sorted(set(c for r in rows for c in cal_cells(r)[0]), key=cell_id)


def cell_id(c):
    return "{}|{}|{}|{}|{!r}".format(c[0], c[1], c[2], c[3], float(c[4]))


def cell_from_id(s):
    m, o, d, law, t = s.split("|")
    return (m, o, int(d), law, float(t))


def micro(x):
    return int(round(float(x) * 1000000))


def key_of(kind, c, n, rep):
    tau_m = 0 if kind == K_REF else micro(c[4])
    return (ENTROPY, kind, cp.MODULES.index(c[0]), cp.OBJ_NAMES.index(c[1]), int(c[2]),
            cp.LAWS.index(c[3]), tau_m, int(n), int(rep))


def key_str(k):
    return "-".join(str(x) for x in k)


def tid_of(label, c, n, rep):
    return "{}|{}|{}|{}".format(label, cell_id(c), n, rep)


# --------------------------------------------------------------------------
# drawing and evaluating
# --------------------------------------------------------------------------

def f_chunk(c, key, ci, m):
    mod = cp.MODS[c[0]]
    rng = np.random.default_rng(np.random.SeedSequence(list(key) + [ci]))
    X = cp.probe_sample(c[0], mod, c[1], c[2], c[3], rng, m)
    return cp.objective_of(c[0], mod, c[1])(X)


def chunks_of(n):
    out, done, ci = [], 0, 0
    while done < n:
        m = min(CHUNK, n - done)
        out.append((ci, m))
        done += m
        ci += 1
    return out


def values_held(c, key, n):
    out = np.empty(n, dtype=np.float64)
    pos = 0
    for ci, m in chunks_of(n):
        out[pos:pos + m] = f_chunk(c, key, ci, m)
        pos += m
    return out


def chunk_terms(fv, betas):
    out = []
    for b in betas:
        a = -b * fv
        a2 = 2.0 * a
        out.append((EC._logsumexp(a), EC._logsumexp(a2), float(np.max(a2))))
    return out


def combine_terms(per_chunk, nb):
    """per_chunk: list over chunks of [(l1, l2, mx) per beta]."""
    res = []
    for i in range(nb):
        l1 = EC._logsumexp(np.asarray([t[i][0] for t in per_chunk]))
        l2 = EC._logsumexp(np.asarray([t[i][1] for t in per_chunk]))
        mx = max(t[i][2] for t in per_chunk)
        res.append((l1, l2, mx))
    return res


def log_ess_from(term):
    return 2.0 * term[0] - term[1]


def tau_of(log_ess, n):
    return math.exp(min(log_ess, 700.0)) / n


def exact_tau(c, beta):
    """X1: centred sphere only; None otherwise."""
    if c[3] != "centred" or c[1] != "sphere":
        return None
    d = int(c[2])
    return float(math.exp(d * (0.5 * math.log1p(4.0 * beta) - math.log1p(2.0 * beta))))


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def jl(xs):
    return ";".join(repr(float(x)) for x in xs)


def floats(s):
    return [float(x) for x in s.split(";")] if s else []


def median(v):
    return float(np.median(np.asarray(v, dtype=np.float64)))


# --------------------------------------------------------------------------
# tasks: each takes a dict and returns a row dict
# --------------------------------------------------------------------------

def base_row(t):
    return {"tid": t["tid"], "phase": t["phase"], "cell": cell_id(t["c"]),
            "n": t.get("n", ""), "rep": t.get("rep", ""), "env": ENV}


def task_cal(t):
    """Phase A and B: beta_on_ensemble on a held sample."""
    row = base_row(t)
    t0 = time.time()
    try:
        key = key_of(t["kind"], t["c"], t["n"], t["rep"])
        row["key"] = key_str(key)
        fv = values_held(t["c"], key, t["n"])
        beta, ach = EC.beta_on_ensemble(fv, t["c"][4], t["n"])
        row.update({"beta_solved": repr(float(beta)), "achieved": repr(float(ach)), "end": "ok"})
    except Exception as exc:
        row.update({"error": "{}: {}".format(type(exc).__name__, exc), "end": "err"})
    row["wall_s"] = "{:.3f}".format(time.time() - t0)
    row["rss_mb"] = "{:.1f}".format(rss_mb())
    return row


def task_ref(t):
    """One whole replicate, streamed, at a list of betas; held for E1 when t["hold"]."""
    row = base_row(t)
    t0 = time.time()
    try:
        c, n, rep, betas, hold = t["c"], t["n"], t["rep"], t["betas"], t["hold"]
        key = key_of(K_REF, c, n, rep)
        row["key"] = key_str(key)
        row["betas"] = jl(betas)
        held = np.empty(n, dtype=np.float64) if hold else None
        per, pos = [], 0
        for ci, m in chunks_of(n):
            fv = f_chunk(c, key, ci, m)
            if hold:
                held[pos:pos + m] = fv
            pos += m
            per.append(chunk_terms(fv, betas))
        res = combine_terms(per, len(betas))
        les = [log_ess_from(r) for r in res]
        row["log_ess"] = jl(les)
        row["tau_hat"] = jl([tau_of(x, n) for x in les])
        row["share"] = jl([math.exp(r[2] - r[1]) for r in res])
        if hold:
            rd = []
            for b, le in zip(betas, les):
                lh = float(EC.log_ess_of(held, b))
                rd.append(abs(le - lh) / abs(lh) if lh != 0.0 else float("inf"))
            row["e1_reldiff"] = jl(rd)
            row["e1"] = "PASS" if all(x <= E1_TOL for x in rd) else "FAIL"
        else:
            row["e1"] = "not applied"
        row["end"] = "ok"
    except Exception as exc:
        row.update({"error": "{}: {}".format(type(exc).__name__, exc), "end": "err"})
    row["wall_s"] = "{:.3f}".format(time.time() - t0)
    row["rss_mb"] = "{:.1f}".format(rss_mb())
    return row


def task_smoke(t):
    c = t["c"]
    row = base_row(t)
    try:
        k = key_of(K_SMOKE, c, N_SMOKE_DRAW, 0)
        t0 = time.time()
        fv = values_held(c, k, N_SMOKE_DRAW)
        t_draw = (time.time() - t0) / N_SMOKE_DRAW
        t0 = time.time()
        beta, _ach = EC.beta_on_ensemble(fv, c[4], N_SMOKE_DRAW)
        t_solve = (time.time() - t0) / N_SMOKE_DRAW
        del fv
        walls = []
        for nb in (1, SMOKE_NBETA):
            betas = [beta] if nb == 1 else list(beta * np.geomspace(0.5, 2.0, nb))
            k2 = key_of(K_SMOKE, c, N_SMOKE_REF, nb)
            t0 = time.time()
            combine_terms([chunk_terms(f_chunk(c, k2, ci, m), betas) for ci, m in chunks_of(N_SMOKE_REF)],
                          len(betas))
            walls.append(time.time() - t0)
        t_beta = (walls[1] - walls[0]) / ((SMOKE_NBETA - 1) * N_SMOKE_REF)
        row.update({"t_draw": repr(t_draw), "t_solve": repr(t_solve), "t_beta": repr(t_beta),
                    "beta_solved": repr(float(beta)), "end": "ok"})
    except Exception as exc:
        row.update({"error": "{}: {}".format(type(exc).__name__, exc), "end": "err"})
    row["rss_mb"] = "{:.1f}".format(rss_mb())
    return row


TASKS = {"cal": task_cal, "ref": task_ref, "smoke": task_smoke}

TASK_COLS = ["tid", "phase", "cell", "key", "n", "rep", "betas", "log_ess", "tau_hat", "share",
             "e1_reldiff", "e1", "beta_solved", "achieved", "env", "wall_s", "rss_mb", "rss_flag",
             "error", "end"]
THR_COLS = ["tid", "phase", "cell", "t_draw", "t_solve", "t_beta", "beta_solved", "env", "rss_mb",
            "error", "end"]


# --------------------------------------------------------------------------
# the scheduler (costprobe2's, adopted): one process per task, a timeout
# --------------------------------------------------------------------------

def child_main(fn_name, t, conn):
    try:
        conn.send(TASKS[fn_name](t))
    finally:
        conn.close()


def error_row(t, msg):
    row = base_row(t)
    row.update({"error": msg, "end": "err", "rss_mb": "nan", "wall_s": "nan"})
    return row


class Out(object):
    def __init__(self, path, cols):
        self.cols = cols
        self.fh = open(path, "x", newline="")
        self.w = csv.DictWriter(self.fh, fieldnames=cols, extrasaction="ignore")
        self.w.writeheader()
        self.sync()

    def sync(self):
        self.fh.flush()
        os.fsync(self.fh.fileno())

    def write(self, row):
        self.w.writerow(dict((k, row.get(k, "")) for k in self.cols))
        self.sync()

    def close(self):
        self.fh.close()


class Runner(object):
    def __init__(self, workers, timeout_s, out, store):
        self.workers, self.timeout_s, self.out, self.store = workers, timeout_s, out, store
        self.errors = 0

    def run(self, items, label):
        """items: list of (fn_name, task dict). Tasks already in the store
        (from --resume-from) are not run. Rows go to the store and the file."""
        todo = [x for x in items if x[1]["tid"] not in self.store]
        print("  [{}] {} task(s) to run, {} already in the resumed folders".format(
            label, len(todo), len(items) - len(todo)))
        sys.stdout.flush()
        pending, running, nout, t0 = list(todo), [], 0, time.time()
        try:
            while pending or running:
                while pending and len(running) < self.workers:
                    fn, t = pending.pop(0)
                    rc, sc = multiprocessing.Pipe(duplex=False)
                    pr = multiprocessing.Process(target=child_main, args=(fn, t, sc))
                    pr.start()
                    sc.close()
                    running.append([pr, rc, t, time.monotonic()])
                progressed = False
                for entry in list(running):
                    pr, rc, t, ts = entry
                    row = None
                    if rc.poll():
                        try:
                            row = rc.recv()
                        except EOFError:
                            pr.join()
                            row = error_row(t, "worker exited with code {} without a result".format(pr.exitcode))
                        pr.join()
                    elif not pr.is_alive():
                        pr.join()
                        row = error_row(t, "worker exited with code {} without a result".format(pr.exitcode))
                    elif time.monotonic() - ts > self.timeout_s:
                        pr.terminate()
                        pr.join()
                        row = error_row(t, "timeout after {:.0f} s (TIMEOUT_S {:.0f} s)".format(
                            time.monotonic() - ts, self.timeout_s))
                    if row is None:
                        continue
                    rc.close()
                    running.remove(entry)
                    progressed = True
                    nout += 1
                    try:
                        rss = float(row.get("rss_mb") or "nan")
                    except ValueError:
                        rss = float("nan")
                    if rss > RSS_BUDGET_MB:
                        row["rss_flag"] = "G-RSS FAIL"
                        print("  G-RSS FAIL {} {:.1f} MB".format(row["tid"], rss))
                    row["env"] = row.get("env") or ENV
                    self.out.write(row)
                    self.store[row["tid"]] = row
                    if row["end"] != "ok":
                        self.errors += 1
                        print("  ERROR {}: {}".format(row["tid"], row.get("error", "")))
                    else:
                        print("  [{} {:>5}/{:<5}] {:<60} wall {:>9} s  RSS {:>7} MB  elapsed {:>7.0f} s".format(
                            label, nout, len(todo), row["tid"][:60], row.get("wall_s", ""), row.get("rss_mb", ""),
                            time.time() - t0))
                    sys.stdout.flush()
                if not progressed:
                    time.sleep(0.2)
        finally:
            for pr, rc, _t, _ts in running:
                pr.terminate()
                pr.join()


# --------------------------------------------------------------------------
# folders
# --------------------------------------------------------------------------

def read_folders(folders, compare_keys):
    """Verified rows from folders: (list of params, rows in order). A repeated
    tid is accepted only over an earlier error row."""
    params, store, order, ref = [], {}, [], None
    for f in folders:
        rels = cp.verify_folder(f)
        pr, rows = None, []
        for rel in rels:
            base = os.path.basename(rel)
            p = os.path.join(f, rel)
            if base == "calprec2_params.csv":
                pr = dict((r[0], r[1]) for r in csv.reader(open(p, newline="")) if r)
            elif base == "calprec2_tasks.csv":
                rows.extend(csv.DictReader(open(p, newline="")))
        if pr is None:
            sys.stderr.write("{} has no calprec2_params.csv\n".format(f))
            sys.exit(2)
        cmp_ = dict((k, pr.get(k)) for k in compare_keys)
        if ref is None:
            ref = cmp_
        elif cmp_ != ref:
            sys.stderr.write("{} differs in {} from the first folder: {} vs {}\n".format(f, compare_keys, cmp_, ref))
            sys.exit(2)
        params.append(pr)
        for r in rows:
            t = r["tid"]
            if t in store:
                if store[t]["end"] == "ok":
                    sys.stderr.write("task {} is complete in an earlier folder and repeated in {}\n".format(t, f))
                    sys.exit(2)
            else:
                order.append(t)
            store[t] = r
        print("  read {}: shard {} of {}, {} rows, {} complete".format(
            f, pr.get("shard"), pr.get("nshards"), len(rows), sum(1 for r in rows if r.get("end") == "ok")))
    return params, [store[t] for t in order]


# --------------------------------------------------------------------------
# V0, V1, V2
# --------------------------------------------------------------------------

def check_v(rows):
    cp.hdr("V1 -- ARCHIVE IDENTITY (imported modules' own files)")
    ok = True
    arch_real = os.path.realpath(cp.ARCH)
    for m in cp.MODULES:
        f = os.path.realpath(cp.MODS[m].__file__)
        h = cp.sha256_file(f)
        good = os.path.dirname(f) == arch_real and f.endswith(".py") and h == cp.ARCHIVE_SHA256[m]
        ok &= good
        print("  {:<12} {}  {}".format(m, h, "ok" if good else "MISMATCH"))
    print("  V1 {}".format("PASS" if ok else "FAIL"))
    if not ok:
        sys.exit(2)
    cp.hdr("V0 -- PLAN IDENTITY: (a) grid values against the archived source, (b) counts")
    okv = cp.p0_values(rows)
    for r in rows:
        cells, nb = cal_cells(r)
        want = cp.TABLE2[r][0]
        good = len(cells) * nb == want
        okv &= good
        print("  {:<8} {:>4} calibration cells x {:>3} = {:>4}  (Table 2 {:>4})  {}".format(
            r, len(cells), nb, len(cells) * nb, want, "ok" if good else "MISMATCH"))
    print("  V0 {}".format("PASS" if okv else "FAIL"))
    if not okv:
        sys.exit(2)
    cp.hdr("V2 -- SAMPLER IDENTITY (first rng line of each module's one_realisation)")
    okw = True
    for m in sorted(set(ROWMOD[r] for r in rows)):
        lines = [s.strip() for s in inspect.getsource(cp.MODS[m].one_realisation).splitlines()]
        try:
            i = lines.index("rng = np.random.default_rng(seed)")
            nxt = next(s for s in lines[i + 1:] if "rng" in s)
        except (ValueError, StopIteration):
            nxt = "(not found)"
        good = (nxt == SAMPLER_LINE[m])
        okw &= good
        print("  {:<10} {}  {}".format(m, nxt, "ok" if good else "MISMATCH, expected " + SAMPLER_LINE[m]))
    print("  V2 {}".format("PASS" if okw else "FAIL"))
    if not okw:
        sys.exit(2)


# --------------------------------------------------------------------------
# throughput, estimates, timeout
# --------------------------------------------------------------------------

def load_throughput(folder):
    rels = cp.verify_folder(folder)
    thr = {}
    for rel in rels:
        if os.path.basename(rel) == "calprec2_throughput.csv":
            for r in csv.DictReader(open(os.path.join(folder, rel), newline="")):
                if r["end"] == "ok":
                    m, o, d, law, _t = cell_from_id(r["cell"])
                    thr[(m, o, d, law)] = (float(r["t_draw"]), float(r["t_beta"]), float(r["t_solve"]))
    return thr


def cell_costs(c, thr):
    """Estimated worker-seconds for one cell: (best case, worst case, largest
    single task). The worst case assumes the cell is adequate (G-CAP)."""
    td, tb, ts = thr[(c[0], c[1], c[2], c[3])]

    def pas(n, nb):
        return n * (td + nb * tb)

    solve4m = L_CAL[-1] * (td + ts)
    e1 = N_LO * ts / LOG_ESS_PER_SOLVE
    a = R_CAL * sum(L_CAL) * (td + ts)
    ref = REPS * pas(N_LO, 1) + REPS * pas(N_HI, 1) + e1
    adequate = REPS * pas(N_LO, NLEV) + solve4m + REPS * pas(N_LO, 1)
    big = max(solve4m, pas(N_LO, 1) + e1, pas(N_HI, 1), pas(N_LO, NLEV))
    return a + ref, a + ref + adequate, big


def estimates(cells, thr):
    """Totals: (best, worst, largest task, cells lacking throughput)."""
    best, worst, big, missing = 0.0, 0.0, 0.0, []
    for c in cells:
        if (c[0], c[1], c[2], c[3]) not in thr:
            missing.append(cell_id(c))
            continue
        b, w, g = cell_costs(c, thr)
        best += b
        worst += w
        big = max(big, g)
    return best, worst, big, missing


def shards_needed(cells, thr, workers, limit):
    """Smallest k for which every shard (index modulo k) has a worst-case
    estimate at most limit: (k, its largest shard estimate) or (None, x)."""
    w = [cell_costs(c, thr)[1] / workers for c in cells]
    for k in range(1, len(cells) + 1):
        top = max(sum(w[i::k]) for i in range(k))
        if top <= limit:
            return k, top
    return None, max(w) if w else 0.0


def mem_available_mb():
    try:
        with open("/proc/meminfo") as fh:
            for ln in fh:
                if ln.startswith("MemAvailable:"):
                    return float(ln.split()[1]) / 1024.0
    except (IOError, OSError, ValueError):
        return None
    return None


# --------------------------------------------------------------------------
# the job
# --------------------------------------------------------------------------

def rung_stats(store, label, c, n, idx=0, reps=None):
    vals = []
    for rep in (reps if reps is not None else range(REPS)):
        r = store.get(tid_of(label, c, n, rep))
        if r is None or r["end"] != "ok":
            return None
        vals.append(floats(r["tau_hat"])[idx])
    return median(vals), max(vals) - min(vals), vals


def judge(store, c):
    """Adequacy from the phase-C rows: (verdict, lo stats, hi stats, c5m, d1).
    verdict is "adequate", "not adequate (...)" or "incomplete (phase C)".
    The job and finalize both use it."""
    lo = rung_stats(store, "C", c, N_LO)
    hi = rung_stats(store, "C", c, N_HI)
    if lo is None or hi is None:
        return "incomplete (phase C)", lo, hi, None, None
    c5m = lo[1] / lo[0]
    d1 = abs(lo[0] - hi[0]) / hi[0]
    fails = []
    if not c5m <= C5M_MAX:
        fails.append("C5m FAIL")
    if not d1 <= D1_MAX:
        fails.append("D1 FAIL")
    return ("adequate" if not fails else "not adequate ({})".format(", ".join(fails))), lo, hi, c5m, d1


def r1_check(store, label, c, n, idx):
    """R1 between phase-C rows and re-evaluation rows at size n; same env only."""
    res = []
    for rep in range(REPS):
        cl = store.get(tid_of("C", c, n, rep))
        ev = store.get(tid_of(label, c, n, rep))
        if cl is None or ev is None or cl["end"] != "ok" or ev["end"] != "ok":
            continue
        if cl.get("env") != ev.get("env"):
            res.append("not applicable (env differs)")
            continue
        a = cl["tau_hat"].split(";")[0]
        b = ev["tau_hat"].split(";")[idx]
        res.append("PASS" if a == b else "FAIL")
    if "FAIL" in res:
        return "FAIL"
    if res and all(x == "PASS" for x in res):
        return "PASS"
    return "not applicable" if res else "no rows"


def n_cell_of(store, c):
    """C1 from the six P rows: (N_cell or None, {N: max deviation}) or None if incomplete."""
    rows = [store.get(tid_of("P", c, N_LO, rep)) for rep in range(REPS)]
    if any(r is None or r["end"] != "ok" for r in rows):
        return None
    taus = [floats(r["tau_hat"]) for r in rows]
    devs, ncell = {}, None
    for li, N in enumerate(L_CAL):
        devs[N] = max(abs(median([t[li * R_CAL + j] for t in taus]) / c[4] - 1.0) for j in range(R_CAL))
        if ncell is None and devs[N] <= C1_MAX:
            ncell = N
    return ncell, devs


def job(cells, runner, store):
    flags3 = []
    cmap = dict((cell_id(c), c) for c in cells)

    cp.hdr("PHASE A  calibration samples")
    runner.run([("cal", {"tid": tid_of("A", c, N, rep), "phase": "A", "c": c, "n": N, "rep": rep,
                         "kind": K_CAL})
                for c in cells for N in L_CAL for rep in range(R_CAL)], "A")
    betas, badq = {}, {}
    for c in cells:
        rows = [store.get(tid_of("A", c, N, rep)) for N in L_CAL for rep in range(R_CAL)]
        if all(r is not None and r["end"] == "ok" for r in rows):
            bl = [float(r["beta_solved"]) for r in rows]
            betas[cell_id(c)] = bl
            badq[cell_id(c)] = median(bl[-R_CAL:])
    live = sorted(badq)
    print("  {} of {} cells have a complete phase A".format(len(live), len(cells)))

    cp.hdr("PHASE C  references at {} and {}, six replicates each, at beta_adq".format(N_LO, N_HI))
    runner.run([("ref", {"tid": tid_of("C", cmap[cid], n, rep), "phase": "C", "c": cmap[cid], "n": n,
                         "rep": rep, "betas": [badq[cid]], "hold": (n == N_LO and rep == 0)})
                for cid in live for n in REF_SIZES for rep in range(REPS)], "C")
    adq = []
    for cid in live:
        v, lo, hi, c5m, d1 = judge(store, cmap[cid])
        if c5m is None:
            print("  {:<48} {}".format(cid, v))
            continue
        print("  {:<48} C5m {:.6f}  D1 {:.6f}  {}".format(cid, c5m, d1, v))
        if v == "adequate":
            adq.append(cid)
    print("  adequate at {}: {} of {} cells".format(N_LO, len(adq), len(live)))

    cp.hdr("PHASE C1  sufficiency pass at {}, {} cells".format(N_LO, len(adq)))
    runner.run([("ref", {"tid": tid_of("P", cmap[cid], N_LO, rep), "phase": "P", "c": cmap[cid], "n": N_LO,
                         "rep": rep, "betas": betas[cid] + [badq[cid]], "hold": False})
                for cid in adq for rep in range(REPS)], "C1")
    ncell = {}
    for cid in adq:
        if r1_check(store, "P", cmap[cid], N_LO, NLEV - 1) == "FAIL":
            flags3.append("R1 FAIL " + cid)
        nc = n_cell_of(store, cmap[cid])
        if nc is not None and nc[0] is not None:
            ncell[cid] = nc[0]

    cp.hdr("PHASE B and C'  production beta and its check, {} cells".format(len(ncell)))
    runner.run([("cal", {"tid": tid_of("B", cmap[cid], ncell[cid], 0), "phase": "B", "c": cmap[cid],
                         "n": ncell[cid], "rep": 0, "kind": K_PROD}) for cid in sorted(ncell)], "B")
    items = []
    for cid in sorted(ncell):
        r = store.get(tid_of("B", cmap[cid], ncell[cid], 0))
        if r is None or r["end"] != "ok":
            continue
        for rep in PRODCHECK_REPS:
            items.append(("ref", {"tid": tid_of("Q", cmap[cid], N_LO, rep), "phase": "Q", "c": cmap[cid],
                                  "n": N_LO, "rep": rep, "betas": [float(r["beta_solved"])], "hold": False}))
    runner.run(items, "C'")
    for r in list(store.values()):
        if r.get("e1") == "FAIL":
            flags3.append("E1 FAIL " + r["tid"])
    return sorted(set(flags3))


# --------------------------------------------------------------------------
# finalize
# --------------------------------------------------------------------------

def finalize(rows, cells, outdir):
    cp.hdr("FINALIZE  {} rows, {} cells expected".format(len(rows), len(cells)))
    st = dict((r["tid"], r) for r in rows)
    out, any3, any4 = [], False, False
    for c in cells:
        cid = cell_id(c)
        rec = {"cell": cid, "module": c[0], "objective": c[1], "d": c[2], "law": c[3], "tau0": repr(c[4])}
        flags = []
        label, beta, prov, tref, tn, rng = None, None, "", None, None, None
        arows = [st.get(tid_of("A", c, N, rep)) for N in L_CAL for rep in range(R_CAL)]
        if any(r is None or r["end"] != "ok" for r in arows):
            label = "incomplete (phase A)"
        else:
            badq = median([float(r["beta_solved"]) for r in arows][-R_CAL:])
            rec["beta_adq"] = repr(badq)
            e1 = st.get(tid_of("C", c, N_LO, 0))
            if e1 is None or e1.get("e1") not in ("PASS", "FAIL"):
                flags.append("E1 not run")
                any4 = True
            elif e1["e1"] == "FAIL":
                flags.append("E1 FAIL")
                any3 = True
            v, lo, hi, c5m, d1 = judge(st, c)
            for nm, s in (("64M", lo), ("256M", hi)):
                if s is not None:
                    rec["med_" + nm], rec["range_" + nm] = repr(s[0]), repr(s[1])
            rec["adequacy"] = v
            if c5m is None:
                label = v
            else:
                rec["C5m"], rec["D1"] = "{:.6f}".format(c5m), "{:.6f}".format(d1)
            if label is None and v != "adequate":
                label, beta, prov = "beta, {}".format(v), badq, "beta_adq; reference not adequate"
                tref, tn, rng = hi[0], N_HI, hi[1]
            elif label is None:
                nc = n_cell_of(st, c)
                if nc is None:
                    label = "incomplete (C1 pass)"
                else:
                    r1 = r1_check(st, "P", c, N_LO, NLEV - 1)
                    if r1 == "FAIL":
                        flags.append("R1 FAIL")
                        any3 = True
                    elif r1.startswith("not applicable"):
                        flags.append("R1 not applicable (env differs)")
                    for N in L_CAL:
                        rec["C1_" + str(N)] = "{:.6f}".format(nc[1][N])
                    rec["N_cell"] = "" if nc[0] is None else nc[0]
                    why = "C1 found no sufficient level"
                    if nc[0] is not None:
                        b = st.get(tid_of("B", c, nc[0], 0))
                        q = rung_stats(st, "Q", c, N_LO, reps=PRODCHECK_REPS)
                        if b is None or b["end"] != "ok" or q is None:
                            label = "incomplete (production or C')"
                        else:
                            rec["beta_prod"] = b["beta_solved"]
                            dev = abs(q[0] / c[4] - 1.0)
                            rec["C6"] = "{:.6f}".format(dev)
                            rec["C5m_prod"] = "{:.6f}".format(q[1] / q[0])
                            if dev <= C6_MAX:
                                label, beta = "target", float(b["beta_solved"])
                                prov = "beta_prod, calibration N_cell {}".format(nc[0])
                                tref, tn, rng = q[0], N_LO, q[1]
                            else:
                                why = "C6 failed for beta_prod"
                    if label is None:
                        dev = abs(lo[0] / c[4] - 1.0)
                        label = "target" if dev <= C6_MAX else "beta"
                        beta, prov = badq, "beta_adq; {}".format(why)
                        tref, tn, rng = lo[0], N_LO, lo[1]
                        rec["dev_adq"] = "{:.6f}".format(dev)
        if label.startswith("incomplete"):
            any4 = True
        rec.update({"label": label, "beta": "" if beta is None else repr(beta), "provenance": prov,
                    "tau_ref": "" if tref is None else repr(tref), "tau_ref_n": "" if tn is None else tn,
                    "range": "" if rng is None else repr(rng),
                    "exact_tau": "" if beta is None or exact_tau(c, beta) is None else repr(exact_tau(c, beta)),
                    "flags": ";".join(flags)})
        out.append(rec)
    cols = ["cell", "module", "objective", "d", "law", "tau0", "label", "beta", "provenance", "tau_ref",
            "tau_ref_n", "range", "exact_tau", "beta_adq", "adequacy", "med_64M", "range_64M", "med_256M",
            "range_256M", "C5m", "D1"] + ["C1_" + str(N) for N in L_CAL] + \
        ["N_cell", "beta_prod", "C6", "C5m_prod", "dev_adq", "flags"]
    with open(os.path.join(outdir, "calprec2_beta.csv"), "x", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for rec in out:
            w.writerow(dict((k, rec.get(k, "")) for k in cols))
    counts = {}
    for rec in out:
        k = rec["label"].split(" (")[0].split(",")[0]
        counts[k] = counts.get(k, 0) + 1
    for k in sorted(counts):
        print("  {:<12} {}".format(k, counts[k]))
    adc = {}
    for rec in out:
        if rec.get("adequacy"):
            adc[rec["adequacy"]] = adc.get(rec["adequacy"], 0) + 1
    for k in sorted(adc):
        print("  {:<40} {}".format(k, adc[k]))
    for rec in out:
        if rec.get("flags"):
            print("  FLAG {}: {}".format(rec["cell"], rec["flags"]))
    return 3 if any3 else (4 if any4 else 0)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--rows", default=None)
    p.add_argument("--cells", default=None)
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--nshards", type=int, default=1)
    p.add_argument("--shard-target", type=float, default=0.5)
    p.add_argument("--plan", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--throughput", default=None)
    p.add_argument("--resume-from", default="")
    p.add_argument("--finalize", default="")
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    a = p.parse_args()
    rows = CALROWS if a.rows is None else [r for r in a.rows.split(",") if r]
    for r in rows:
        if r not in ROWMOD:
            sys.stderr.write("setup error: {} is not a calibrated row (spec 2, ledger N27)\n".format(r))
            return 2
    if not (0 <= a.shard < a.nshards) or a.workers < 1 or not (0.0 < a.shard_target <= 1.0):
        sys.stderr.write("setup error: shard, worker or shard-target arguments out of range\n")
        return 2
    mode = "finalize" if a.finalize else "plan" if a.plan else "smoke" if a.smoke else "full"
    me = cp.sha256_file(os.path.abspath(__file__))
    cps = cp.sha256_file(os.path.abspath(cp.__file__))

    print("=" * 96)
    print("CBO-GAP calprec2 -- calprec v2: one fixed beta per calibration cell, measured at 64M and 256M")
    print("=" * 96)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {}   start {}".format(
        platform.platform(), platform.machine(), os.cpu_count(), a.workers, multiprocessing.get_start_method()))
    print("  threads  " + "  ".join("{}={}".format(v, os.environ.get(v)) for v in cp.THREAD_VARS))
    print("  archive  {}".format(cp.ARCH))
    print("  script   sha256 {}".format(me))
    print("  costprobe2.py sha256 {}".format(cps))
    print("  mode     {}   rows {}   shard {} of {}   shard target {} x {:.0f} s".format(
        mode, ",".join(rows), a.shard, a.nshards, a.shard_target, SHARD_CEIL_S))
    print("  L_CAL {}  R {}   reference sizes {} and {}, reps {}   C' reps {}   chunk {}".format(
        L_CAL, R_CAL, N_LO, N_HI, REPS, PRODCHECK_REPS, CHUNK))
    print("  C5m <= {} at {}  D1 <= {} between {} and {}  C1 <= {}  C6 <= {}  E1 <= {:g} at {} rep 0  "
          "RSS <= {:.0f} MB".format(C5M_MAX, N_LO, D1_MAX, N_LO, N_HI, C1_MAX, C6_MAX, E1_TOL, N_LO, RSS_BUDGET_MB))
    print("  seeds    default_rng(SeedSequence(key + (chunk,))), full width; key = (ENTROPY {}, kind, module, "
          "objective, d, law, tau0e6 (0 for kind {}), n, rep); kinds A {} C {} B {} smoke {}".format(
              ENTROPY, K_REF, K_CAL, K_REF, K_PROD, K_SMOKE))
    if a.throughput:
        print("  throughput  {}".format(a.throughput))

    check_v(rows)

    allcells = all_cells(rows)
    serves = {}
    for r in rows:
        for c in cal_cells(r)[0]:
            serves.setdefault(cell_id(c), []).append(r)
    cp.hdr("CELLS")
    bym = {}
    for c in allcells:
        bym[c[0]] = bym.get(c[0], 0) + 1
    for m in sorted(bym):
        print("  {:<10} {:>4} deduplicated calibration cells".format(m, bym[m]))
    print("  total {}".format(len(allcells)))

    params = [["script_sha256", me], ["costprobe2_sha256", cps], ["mode", mode], ["rows", ",".join(rows)],
              ["cells", a.cells or ""], ["shard", a.shard], ["nshards", a.nshards],
              ["ref_sizes", "{};{}".format(N_LO, N_HI)], ["workers", a.workers],
              ["python", platform.python_version()], ["numpy", np.__version__]]

    if mode == "finalize":
        fp, trows = read_folders([x for x in a.finalize.split(",") if x], ["script_sha256", "costprobe2_sha256", "rows"])
        frows = [r for r in fp[0]["rows"].split(",") if r]
        if any(r not in ROWMOD for r in frows):
            sys.stderr.write("finalize: the folders' rows {} are not all calibrated rows\n".format(frows))
            return 2
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir = os.path.join(OUTROOT, "calprec2-finalize-" + stamp)
        os.makedirs(outdir)
        code = finalize(trows, all_cells(frows), outdir)
        print("\nfiles  {}".format(outdir))
        return code

    sel = allcells
    if a.cells:
        want = set(x for x in a.cells.split(",") if x)
        bad = want - set(cell_id(c) for c in allcells)
        if bad:
            sys.stderr.write("setup error: unknown cell ids {}\n".format(sorted(bad)))
            return 2
        sel = [c for c in allcells if cell_id(c) in want]
    cells = [c for i, c in enumerate(sel) if i % a.nshards == a.shard]
    print("  this job: {} cells".format(len(cells)))

    store = {}
    if a.resume_from:
        mine = dict((k, str(v)) for k, v in params)
        _p, rrows = read_folders([x for x in a.resume_from.split(",") if x], list(mine.keys()))
        if _p and dict((k, _p[0].get(k)) for k in mine) != mine:
            sys.stderr.write("resume: parameters differ from this run's (CLAUDE.md rule 17)\n")
            return 2
        for r in rrows:
            if r["end"] == "ok":
                store[r["tid"]] = r

    thr = load_throughput(a.throughput) if a.throughput else None
    miss, worst, big = [], 0.0, 0.0
    if thr is not None:
        best, worst, big, miss = estimates(cells, thr)
        cp.hdr("G-CAP -- ESTIMATE for this job (perfect scaling; barrier idle and tails ignored; NOT a bound)")
        if mode == "plan":
            for c in cells:
                if (c[0], c[1], c[2], c[3]) in thr:
                    b_, w_, g_ = cell_costs(c, thr)
                    print("  {:<48} best {:>7.0f} s  worst {:>7.0f} s  largest task {:>6.0f} s (worker-seconds)".format(
                        cell_id(c), b_, w_, g_))
        print("  best case (no cell adequate) {:.0f} s   worst-case estimate (every cell adequate) {:.0f} s   "
              "at {} workers   ceiling {:.0f} s".format(best / a.workers, worst / a.workers, a.workers, SHARD_CEIL_S))
        print("  largest single task, estimated {:.0f} s".format(big))
        if miss:
            print("  {} cells lack throughput: {}".format(len(miss), ", ".join(miss[:5])))
        else:
            tgt = a.shard_target * SHARD_CEIL_S
            kt, tt = shards_needed(sel, thr, a.workers, tgt)
            kc, tc = shards_needed(sel, thr, a.workers, SHARD_CEIL_S)
            for nm, lim, k, top in (("target", tgt, kt, tt), ("full ceiling", SHARD_CEIL_S, kc, tc)):
                if k is None:
                    print("  at the {} ({:.0f} s): no shard count fits; one cell alone is estimated at {:.0f} s".format(
                        nm, lim, top))
                else:
                    print("  at the {} ({:.0f} s): smallest --nshards {}   largest shard {:.0f} s = {:.1f}% of {:.0f} s, "
                          "at {} workers, over the {} selected cells".format(
                              nm, lim, k, top, 100.0 * top / SHARD_CEIL_S, SHARD_CEIL_S, a.workers, len(sel)))
            if kt is not None:
                print("  RECOMMENDED: --nshards {}, the count at the target. The estimate assumes perfect scaling, "
                      "ignores barrier idle and phase tails, and is not a bound. G-CAP refuses only above "
                      "{:.0f} s.".format(kt, SHARD_CEIL_S))
    if mode == "smoke":
        proj = (N_SMOKE_DRAW + 2 * N_SMOKE_REF) / REFSCALE_ACKLEY_RATE
        timeout_s = max(TIMEOUT_FLOOR_SMOKE, TIMEOUT_FACTOR * 2.0 * proj)
        src = "smoke: (4M + 2 x 1M) / 3.16e5, doubled for the solve and the 145-beta pass, floor 600 s"
    else:
        timeout_s = TIMEOUT_FACTOR * big
        src = "5 x the largest single task estimated from --throughput"
    if mode in ("smoke", "full"):
        cp.hdr("T1 -- PER-TASK TIMEOUT")
        print("  TIMEOUT_S = {:.0f} s   ({})".format(timeout_s, src))
    if mode == "plan":
        cp.hdr("ROWS SERVED BY EACH CELL (this job)")
        for c in cells:
            print("  {}   rows {}".format(cell_id(c), ",".join(serves[cell_id(c)])))
        print("\nPLAN MODE: no draws, nothing written.")
        return 0
    if mode == "full":
        if thr is None:
            sys.stderr.write("G-CAP: a full run needs --throughput <verified smoke folder>\n")
            return 2
        if miss or worst / a.workers > SHARD_CEIL_S or (cells and timeout_s <= 0):
            sys.stderr.write("G-CAP: worst-case estimate {:.0f} s exceeds {:.0f} s, or cells lack throughput; "
                             "select fewer --cells or add shards\n".format(worst / a.workers, SHARD_CEIL_S))
            return 2
        avail = mem_available_mb()
        need = MEM_GUARD_FACTOR * N25_HELD64_PEAK_MB
        cp.hdr("G-MEM -- MEMORY GUARD")
        print("  MemAvailable {}   required {:.1f} MB (2 x N25's held-64M peak {} MB)".format(
            "unreadable" if avail is None else "{:.0f} MB".format(avail), need, N25_HELD64_PEAK_MB))
        if avail is None or avail < need:
            sys.stderr.write("G-MEM: available memory {} is below {:.1f} MB. This job holds 64M arrays; it belongs on "
                             "Kaggle (notes/CALPREC2_RUNBOOK.md), not on this machine.\n".format(
                                 "unreadable" if avail is None else "{:.0f} MB".format(avail), need))
            return 2
        print("  G-MEM PASS")

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = "" if a.nshards == 1 else "-s{}of{}".format(a.shard, a.nshards)
    outdir = os.path.join(OUTROOT, "calprec2-{}-{}{}".format(mode, stamp, tag))
    os.makedirs(outdir)
    with open(os.path.join(outdir, "calprec2_params.csv"), "x", newline="") as fh:
        csv.writer(fh).writerows(params)
    with open(os.path.join(outdir, "calprec2_plan.csv"), "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cell", "shard", "rows"])
        for c in cells:
            w.writerow([cell_id(c), a.shard, ";".join(serves[cell_id(c)])])
    print("\n  run dir  {}".format(outdir))

    if mode == "smoke":
        units = sorted(set((c[0], c[1], c[2], c[3], 0.1) for c in cells), key=cell_id)
        out = Out(os.path.join(outdir, "calprec2_throughput.csv"), THR_COLS)
        runner = Runner(a.workers, timeout_s, out, {})
        try:
            runner.run([("smoke", {"tid": "SMOKE|" + cell_id(u), "phase": "SMOKE", "c": u}) for u in units], "smoke")
        finally:
            out.close()
        print("\nSMOKE: unit costs only; not results.")
        return 4 if runner.errors else 0

    out = Out(os.path.join(outdir, "calprec2_tasks.csv"), TASK_COLS)
    runner = Runner(a.workers, timeout_s, out, store)
    try:
        flags3 = job(cells, runner, store)
    finally:
        out.close()
    for f in flags3:
        print("  FAIL {}".format(f))
    print("\n" + "=" * 96)
    print("errored or timed-out tasks: {}".format(runner.errors))
    print("files  {}".format(outdir))
    print("=" * 96)
    if flags3:
        return 3
    return 4 if runner.errors else 0


if __name__ == "__main__":
    sys.exit(main())
