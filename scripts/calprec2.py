"""
calprec2.py  --  CBO-GAP round 2: calprec v2, one fixed beta per calibration
                 cell for the fixed-beta rerun, calibrated through each row's
                 own archived module

WHAT THIS PRODUCES, IN PLAIN LANGUAGE
-------------------------------------
The specification is notes/CALPREC_V2_SPEC.md (cited as "spec 5" and so
on). For every calibration cell

    (module, objective, d, initial law, tau0)

needed by a rerun row whose beta targets a concentration, this script finds
a fixed beta and measures the concentration tau(beta) that beta actually
produces, on large independent reference samples. The finalize step writes
the beta table (calprec2_beta.csv) that the rerun script reads. Each beta is
labelled "target" (tau(beta) is within 5% of tau0) or "beta" (it is not, or
cannot be shown to be; the cell is then labelled by its beta, never by a
target; spec 6, ledger N18 O2).

No trajectories are evolved. Nothing in the archive is written to.

REVISION 2026-10-11, before any execution (notes/CALPREC_V2_REVIEW.md,
second pass). D5a, the 200-step streamed bisection on the laptop, is
WITHDRAWN (ledger N24). Case (a) and case (b) solves are now a streamed GRID
solve run with the rest of the job (criterion E3). Phase A is written to its
own file and read by continuation jobs. Tasks run under costprobe2's
process-per-task scheduler with a timeout.

WHAT IS IMPORTED, AND WHAT IS NOT
  * Archive modules and grids come from scripts/costprobe2.py: MODS
    (hashed by V1), GRID and SOURCE (checked against the archived source by
    V0), objective_of and probe_sample. costprobe2.py's sha256 is printed
    and stored in the params file.
  * The objective of a cell is its own module's (spec 3, RERUN_PLAN F5).
  * The initial law is drawn with the module's own draw_initial
    (mechanism, control, regime). For the modules whose one_realisation
    draws X0 inline (boundary, law, sigma, crossed, cliff, regimemap), it is
    drawn as rng.standard_normal((n, d)) + x*, with x* from the module's own
    dict. V2 checks that line against the module source.
  * Phase A's bisection is exactcal.beta_on_ensemble.
  * The streamed log-ESS is the refscale composition: exactcal._logsumexp
    applied per chunk to -beta f and to -2 beta f, then applied to the
    vector of chunk results (E1).
  * The GRID SOLVE is not imported (see S below). E3 checks it against
    beta_on_ensemble.

CELLS (spec 2)
  The rows and their modules:
    CONC mechanism, ADAPT control, TAU8 boundary,
    REFSIZE / SYNTH / NAMED / HORIZON regime, GEOM law, SIGMA sigma,
    ANISO crossed, RMAP and ONSET regimemap, CLIFF cliff.
  BETA-ISO, BETA-ANI, LAWPANEL (F1), PROBEARM (D6) and PERJ (F4) are not
  calibrated here. Identical cells of one module are calibrated once. The
  plan prints the deduplicated count.

JOBS, AND HOW A CELL SPANS SEVERAL OF THEM (review A1, A2)
  A job evaluates, for each of its cells, the rungs from that cell's
  start up to --max-rung:
    - start = 0 if the cell has no climb rows in the --inputs folders;
    - otherwise start = (highest rung with six complete climb rows) + 1.
  The highest rung already evaluated is the continuation point. It is
  judged in this job, once the rung above it exists; its own rows come from
  the inputs and are not recomputed. Phase A of a cell is computed once, in
  the first job that touches the cell, and written to that job's
  calprec2_phaseA.csv. A later job reads it from --inputs; the folder is
  verified against its sha256.txt. A job given a cell with climb rows but
  no phase-A rows stops with exit 2. No task id is ever written twice, so
  finalize's rule needs no exception: a repeated id is accepted only over an
  earlier error row.
  --inputs is not a rule-17 resumption. The folders must agree with this
  job on script sha256, costprobe2 sha256, rows, Python and NumPy, but they
  may differ in --cells, --shard, --max-rung and --workers.
  --resume-from is rule 17 (CLAUDE.md, amended 2026-10-10): every
  parameter must be equal.

PROCEDURE PER CELL (barriers between phases; parallel over cells,
replicates and blocks)
  A   CALIBRATION. For each N in L_CAL = 4000, 16000, 64000, 256000,
      1000000, 4000000 and each of R = 24 draws: N values (kind 31),
      beta_hat = beta_on_ensemble(values, tau0, N). beta_adq = the median of
      the 24 beta_hat at N = 4000000.
  C   CLIMB. L_REF = 1M, 4M, 16M, 64M, 256M, 1G, six replicates per rung
      (kind 32), streamed in chunks of 250000, evaluated at beta_adq. Rung i
      is judged once rung i+1 exists: the first rung that passes C5m and D1
      is n*. If rung i+1 is 1G and rung i fails, the cell is case (a). If
      --max-rung is reached first, the cell is "unresolved, highest
      evaluated rung L_REF[i+1]", to be continued (A2 corrected).
  C1  SUFFICIENCY PASS at n*. The six replicates of n* are regenerated and
      evaluated at the 144 beta_hat and at beta_adq (R1). N_cell = the
      smallest N whose 24 beta_hat all pass C1, or none (case (b)).
  B   PRODUCTION. beta_prod = beta_on_ensemble on a size-N_cell sample
      (kind 33).
  C'  PRODUCTION CHECK. beta_prod is evaluated on six NEW replicates of size
      n* (kind 32, replicates 6 to 11): C6. On failure, case (b).
  S   GRID SOLVES for case (b), at n*, and case (a), at 1G.
      E3 first (below). Then the streamed grid solve on an independent
      kind-34 stream of the solve size, rep 0:
      - pass 1 evaluates K = 64 betas log-spaced over [1e-10, 1e10], the
        bracket of beta_on_ensemble, all on one streamed pass;
      - each later pass evaluates 64 betas log-spaced between the two grid
        neighbours that bracket the target;
      - passes stop when hi/lo - 1 <= 1e-6 (GRID_TOL). The width after
        each pass is printed.
      With 64 points over 20 decades, the width falls roughly as
      46 / 63^p after p passes, so the stop rule needs 5 passes. Two passes
      give about 1.2e-2, not below 1e-4.
      beta_s = sqrt(lo hi), as beta_on_ensemble returns. Each pass is split
      into blocks of 64 chunks, run as separate tasks and combined in chunk
      order.
      beta_s is then evaluated on the six kind-32 replicates of the solve
      size, together with beta_adq (for R1).
      Why an independent stream and all six replicates, rather than the
      spec's "solve on one replicate and evaluate on the other five":
      - the estimate tau_ref is then the same median-of-six estimator that
        C5m was calibrated for (c6 is for six; spec 11a);
      - none of the six evaluation replicates was used to choose beta_s, so
        tau_ref is not biased toward tau0 by reusing the solving sample.
      Under "the other five", the estimator would be a median of five,
      which C5m's constant does not cover, and one replicate would serve
      both to choose and to judge.

PRE-SPECIFIED CRITERIA (fixed 2026-10-11, before first execution)
------------------------------------------------------------------
  V0  PLAN IDENTITY.
      (a) costprobe2's P0(a): every grid factor equals the archived
          source's constant.
      (b) Per row, the calibration cells times the levels of the factors
          that do not enter beta equal Table 2's cell count.
      Otherwise exit 2.
      Worked example: SIGMA has 24 cells; 24 x (2 diffusions x 6 r) = 288,
      Table 2's count: pass. With five r values, 240: exit 2.
  V1  ARCHIVE IDENTITY. Every imported archive module's __file__ lies in the
      archive and hashes to its zenodo-v1.sha256 entry, or exit 2.
      Worked example: regimemap.py hashes to eb1d704f...14c8: ok.
  V2  SAMPLER IDENTITY. For every module used, the first line after
      "rng = np.random.default_rng(seed)" in one_realisation that mentions
      "rng" must equal SAMPLER_LINE, or exit 2.
      Worked example: sigma's line is "X0 = rng.standard_normal((Jinf, d))
      + xs": ok.
  E1  STREAMING EQUIVALENCE. Replicate 0 of the 1M rung is held whenever it
      is evaluated. For every beta, |logESS_streamed - logESS_held| /
      |logESS_held| <= 1e-12, against exactcal.log_ess_of. Every cell's
      first job starts at 1M, so E1 runs for every cell (review C2). In
      finalize, a cell without an E1 row is flagged "E1 not run", exit 4.
      A failure gives exit 3.
      Worked example (refscale): 10.596634733096073 against
      10.596634733096080 gives 6.6e-16: pass.
  E3  GRID-SOLVE EQUIVALENCE. On the cell's lowest held rung (1M, kind-34
      stream, rep 0), the grid solve and exactcal.beta_on_ensemble on the
      held values must agree:
          |beta_grid / beta_held - 1| <= 1e-6, printed.
      If E3 fails, no solve result of that cell is used: the cell is
      flagged, and exit 3.
      Worked example (illustrative values): 6.0285345 against 6.0285381
      gives 6.0e-7: pass.
  R1  REGENERATION IDENTITY. When a rung's six replicates are re-evaluated
      (the C1 pass, or a solve evaluation at a climbed rung), tau_hat at
      beta_adq must equal the climb's, compared as repr strings. It applies
      only when both rows were computed under the same Python and NumPy
      (the "env" column). Otherwise the comparison is reported as "R1 not
      applicable (env differs)" and is not a failure (review B4). A failure
      gives exit 3.
      Worked example: 0.0099834716023 against 0.0099834716023: pass.
  C5m range / tau_ref <= 0.054682, at beta_adq. tau_ref is the median of
      six; the threshold comes from ledger N23.
      Worked examples (spec 5):
      - 0.00970 0.00980 0.00985 0.00990 0.01000 0.01010: ratio 0.0405, pass;
      - 0.00940 0.00960 0.00975 0.00985 0.00995 0.01010: ratio 0.0714, fail.
  D1  |tau_ref(n) - tau_ref(4n)| / tau_ref(4n) <= 0.025, at beta_adq.
      Worked example: 0.00995 against 0.01003 gives 0.0080: pass.
  ADEQUATE  Passes C5m and D1. The top rung is never adequate.
  C1  At n*: max over a level's 24 draws of |tau_ref(beta_hat)/tau0 - 1|
      <= 0.05. N_cell = the smallest such level.
      Worked example: 0.0098 to 0.0104 at tau0 = 0.01 gives 0.04:
      sufficient.
  C6  |tau_ref(beta_prod)/tau0 - 1| <= 0.05 over the six C' replicates.
      Worked example: tau0 0.1, tau_ref 0.1042: 0.042, pass.
  CB  Case (b): "target" with beta_s if |tau_ref(beta_s)/tau0 - 1| <= 0.05;
      otherwise "beta".
  CA  Case (a): "beta", with beta_s solved at 1G, and tau(beta_s) as the
      median of six 1G replicates, with their range.
  INCOMPLETE  A cell whose rows for a phase are missing or errored is
      labelled "incomplete (<phase>)". It is never given a case label
      (review B2).
  S1  Largest-term share: reported, no threshold.
  X1/X2  Exact tau for the centred law with a diagonal quadratic objective
      (sphere; synthetic rho = 0):
          prod_i (1 + 4 beta a_i)^(1/2) / (1 + 2 beta a_i).
      Reported, no threshold.
      Worked example: d = 2, a = (1, 1), beta = 0.5 gives 0.75.
  G-RSS  Peak RSS of each task <= 3072 MB, else a FAIL line and a flagged
      row. The only held arrays are phase A (at most 4000000 values) and
      the 1M arrays of E1 and E3. No held solve exists above 1M, pending
      the memory probe (review A4).
  G-CAP  A full run needs --throughput (a verified smoke folder), and its
      WORST-CASE ESTIMATE must be at most 21600 s, or exit 2.
      The estimate is
          sum over cells of (A, unless it is in the inputs; climb from the
          cell's start to --max-rung; the C1 pass, C' and an n* solve at
          the rung below --max-rung, or a 1G solve if --max-rung is 1G)
          / workers,
      with each pass costing n x (t_draw + n_beta x t_beta).
      It assumes perfect scaling. It ignores barrier idle time and the tail
      of each phase. It is an estimate, NOT a bound (review B3). The best
      case assumes adequacy at the start rung.
      Worked example (illustrative values): 6 x 4M at one beta with t_draw
      3e-6 and t_beta 2e-8 costs 6 x 4e6 x 3.02e-6 = 72.5 s.
  T1  PER-TASK TIMEOUT (costprobe2's scheduler, adopted). Each task runs in
      its own process, at most --workers at once. A task still running
      after TIMEOUT_S is terminated and written as an error row
      ("timeout"). A process that exits without a result is written as an
      error row ("worker exited").
          TIMEOUT_S = 5 x the projected wall of the job's largest task,
      with the projection from the throughput table, printed at the head
      of the run.
      In smoke mode, where no table exists yet, the projection is
      (4000000 + 2 x 1000000) points / 3.16e5 points per second, plus the
      same again for the solve and the 145-beta pass, and the timeout is
      floored at 600 s. 3.16e5 is refscale's measured ackley throughput,
      the slowest it measured (runs/refscale-kaggle-20261010-094820).
      Worked example (illustrative values): largest task projected 700 s:
      TIMEOUT_S = 3500 s.

EXIT CODES
  0  completed, every task ok, and no flag;
  2  setup error (V0, V1, V2, G-CAP, inputs, resume, finalize merge);
  3  E1, E3 or R1 failed;
  4  a task errored or timed out, or (in finalize) a cell is incomplete
     or "E1 not run" (review C6).
  Exit 3 takes precedence over exit 4.

SEEDS (spec 7)
  Every stream is numpy.random.default_rng(SeedSequence(key + (chunk,)))
  at full width (ledger N16), with
      key = (ENTROPY 20261010, kind, module code, objective code, d,
             law code, tau0 x 1e6, n, rep)
  Kinds: 31 calibration, 32 reference, 33 production, 34 solve, 35 smoke.
  Reference keys (kind 32) carry tau0 = 0, as spec 7 says, so cells
  differing only in tau0 share reference streams. Their tau_ref values
  are therefore correlated, not independent (review B5). The chunk index
  is appended to the key so that any chunk can be regenerated alone; that
  is an addition to spec 7. Codes are indices in costprobe2's MODULES,
  OBJ_NAMES and LAWS.

MODES
  --plan            V0, V1, V2, the cells with their rung range for this
                    job and, with --throughput, the estimates. No draws;
                    nothing written.
  --smoke           Unit costs t_draw, t_solve and t_beta per (module,
                    objective, d, law), written to calprec2_throughput.csv.
                    Not results.
  (default)         The job.
  --finalize DIR[,DIR]
                    No draws. Merges the verified folders, recomputes every
                    verdict per cell and writes calprec2_beta.csv.
  Selection: --rows, --cells, --shard i --nshards k, --max-rung j
  (default 5), --inputs DIR[,DIR], --resume-from DIR[,DIR].

OUTPUT (new folder <outdir>/calprec2-<mode>-<timestamp>[-s<i>of<k>]/, every
        file opened "x", every row flushed and fsynced, a task's row
        written once the task completes)
  calprec2_params.csv      the parameters inputs, resume and finalize compare
  calprec2_plan.csv        the cells, their shard, start rung, max rung and
                           rows
  calprec2_phaseA.csv      phase-A rows (only in the job that computes them)
  calprec2_tasks.csv       all other task rows: tid, phase, cell, key, n,
                           rep, block, betas and the per-beta log-ESS, lse
                           terms, tau_hat, S1 share and E1 values
                           (";"-joined repr lists), beta solved, achieved,
                           env, wall, peak RSS, G-RSS flag, error, end
  calprec2_throughput.csv  smoke only
  calprec2_beta.csv        finalize only

HOW TO RUN (from the repository root, venv active)
    python scripts/calprec2.py --plan
    python scripts/calprec2.py --workers 4 --smoke
    python scripts/calprec2.py --workers 4 --throughput DIR --max-rung 3 --shard 0 --nshards K
    python scripts/calprec2.py --workers 4 --throughput DIR --inputs DIR --cells ID --max-rung 5
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
K_CAL, K_REF, K_PROD, K_SOLVE, K_SMOKE = 31, 32, 33, 34, 35
L_CAL = [4000, 16000, 64000, 256000, 1000000, 4000000]
R_CAL = 24
L_REF = [1000000, 4000000, 16000000, 64000000, 256000000, 1024000000]
REPS = 6
PRODCHECK_REPS = list(range(6, 12))
CHUNK = 250000
BLOCK_CHUNKS = 64
C5M_MAX = 0.054682
D1_MAX = 0.025
C1_MAX = 0.05
C6_MAX = 0.05
E1_TOL = 1e-12
E3_TOL = 1e-6
GRID_K = 64
GRID_TOL = 1e-6
GRID_MAX_PASSES = 8
BIS_LO, BIS_HI = 1e-10, 1e10
RSS_BUDGET_MB = 3072.0
SHARD_CEIL_S = 21600.0
TIMEOUT_FACTOR = 5.0
TIMEOUT_FLOOR_SMOKE = 600.0
REFSCALE_ACKLEY_RATE = 3.16e5     # points/s/worker, runs/refscale-kaggle-20261010-094820
N_SMOKE_DRAW, N_SMOKE_REF, SMOKE_NBETA = 4000000, 1000000, 145
NLEV = len(L_CAL) * R_CAL + 1

ROWMOD = {"CONC": "mechanism", "ADAPT": "control", "TAU8": "boundary",
          "REFSIZE": "regime", "SYNTH": "regime", "NAMED": "regime", "HORIZON": "regime",
          "GEOM": "law", "SIGMA": "sigma", "ANISO": "crossed", "RMAP": "regimemap",
          "CLIFF": "cliff", "ONSET": "regimemap"}
CALROWS = ["CONC", "ADAPT", "TAU8", "REFSIZE", "SYNTH", "NAMED", "HORIZON", "GEOM",
           "SIGMA", "ANISO", "RMAP", "CLIFF", "ONSET"]

SAMPLER_LINE = {
    "mechanism": "X0 = draw_initial(rng, Jinf, d, objective, init)",
    "control": "X0 = draw_initial(rng, Jinf, d, objective, init)",
    "regime": "X0 = draw_initial(rng, Jinf, d, xstar, init)",
    "boundary": "X0 = rng.standard_normal((Jinf, d)) + MINIMIZER[objective]",
    "law": "X0 = rng.standard_normal((Jinf, d)) + xs",
    "sigma": "X0 = rng.standard_normal((Jinf, d)) + xs",
    "crossed": "X0 = rng.standard_normal((Jinf, d)) + xs",
    "cliff": "X0 = rng.standard_normal((Jinf, d)) + xs",
    "regimemap": "X0 = rng.standard_normal((Jinf, d))",
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
    if row == "ADAPT":
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], len(g["arms"])
    if row in ("TAU8", "SYNTH", "NAMED", "GEOM"):
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], 1
    if row == "REFSIZE":
        return [(m, o, g["d"], "centred", 0.1) for o in g["objs"]], len(g["jinfs"])
    if row == "HORIZON":
        return [(m, o, 10, law, 0.1) for o in g["objs"] for law in g["laws"]], len(g["Ts"])
    if row == "SIGMA":
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], len(g["diffs"]) * len(g["rs"])
    if row == "ANISO":
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], len(g["diffs"]) * (len(g["sigmas"]) + len(g["rs"]))
    if row in ("RMAP", "CLIFF"):
        return [(m, o, d, "centred", t) for o in g["objs"] for d in g["dims"]
                for t in g["taus"]], len(g["diffs"]) * len(g["rs"])
    if row == "ONSET":
        return [(m, o, d, "centred", g["tau"]) for o in g["objs"] for d in g["dims"]], \
            len(g["diffs"]) * len(g["rs"])
    raise ValueError(row)


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


def tid_of(label, c, n, rep, extra=""):
    return "{}|{}|{}|{}{}".format(label, cell_id(c), n, rep, extra)


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


def blocks_of(n):
    ch = chunks_of(n)
    return [ch[i:i + BLOCK_CHUNKS] for i in range(0, len(ch), BLOCK_CHUNKS)]


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
    """per_chunk: list over chunks (or blocks) of [(l1, l2, mx) per beta]."""
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
    m, o, d, law, _t = c
    if law != "centred":
        return None
    if o == "sphere":
        a = np.ones(d)
    else:
        sp = getattr(cp.MODS[m], "SYNTH_PARAMS", {})
        if o not in sp or sp[o][1] != 0.0:
            return None
        a = sp[o][0] ** (np.arange(d, dtype=float) / max(d - 1, 1))
    return float(math.exp(float(np.sum(0.5 * np.log1p(4.0 * beta * a) - np.log1p(2.0 * beta * a)))))


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
            "n": t.get("n", ""), "rep": t.get("rep", ""), "block": t.get("block", ""), "env": ENV}


def task_cal(t):
    """Phase A, B, and the held E3 solve: beta_on_ensemble on a held sample."""
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
    """One whole replicate, streamed, at a list of betas; E1 on rep 0 of 1M."""
    row = base_row(t)
    t0 = time.time()
    try:
        c, n, rep, betas = t["c"], t["n"], t["rep"], t["betas"]
        key = key_of(t["kind"], c, n, rep)
        row["key"] = key_str(key)
        row["betas"] = jl(betas)
        hold = (t["kind"] == K_REF and n == L_REF[0] and rep == 0)
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
        row["exact_tau"] = ";".join("" if exact_tau(c, b) is None else repr(exact_tau(c, b)) for b in betas)
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


def task_block(t):
    """One block of one grid-solve pass: per-beta lse terms over its chunks."""
    row = base_row(t)
    t0 = time.time()
    try:
        c, betas = t["c"], t["betas"]
        key = key_of(K_SOLVE, c, t["n"], 0)
        row["key"] = key_str(key)
        row["betas"] = jl(betas)
        per = [chunk_terms(f_chunk(c, key, ci, m), betas) for ci, m in t["chunks"]]
        res = combine_terms(per, len(betas))
        row["l1"] = jl([r[0] for r in res])
        row["l2"] = jl([r[1] for r in res])
        row["mx"] = jl([r[2] for r in res])
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


TASKS = {"cal": task_cal, "ref": task_ref, "block": task_block, "smoke": task_smoke}

TASK_COLS = ["tid", "phase", "cell", "key", "n", "rep", "block", "betas", "log_ess", "l1", "l2", "mx",
             "tau_hat", "share", "exact_tau", "e1_reldiff", "e1", "beta_solved", "achieved",
             "status", "env", "wall_s", "rss_mb", "rss_flag", "error", "end"]
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


def error_row(t, msg, pid):
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
    def __init__(self, workers, timeout_s, outs, store):
        self.workers, self.timeout_s, self.outs, self.store = workers, timeout_s, outs, store
        self.errors = 0

    def run(self, items, label):
        """items: list of (fn_name, task dict, out key). Tasks already in the
        store are not run. Returns nothing; rows go to the store and files."""
        todo = [x for x in items if x[1]["tid"] not in self.store]
        print("  [{}] {} task(s) to run, {} already in the inputs".format(
            label, len(todo), len(items) - len(todo)))
        sys.stdout.flush()
        pending, running, nout, t0 = list(todo), [], 0, time.time()
        try:
            while pending or running:
                while pending and len(running) < self.workers:
                    fn, t, ok_ = pending.pop(0)
                    rc, sc = multiprocessing.Pipe(duplex=False)
                    pr = multiprocessing.Process(target=child_main, args=(fn, t, sc))
                    pr.start()
                    sc.close()
                    running.append([pr, rc, t, ok_, time.monotonic()])
                progressed = False
                for item in list(running):
                    pr, rc, t, ok_, ts = item
                    row = None
                    if rc.poll():
                        try:
                            row = rc.recv()
                        except EOFError:
                            pr.join()
                            row = error_row(t, "worker exited with code {} without a result".format(pr.exitcode), pr.pid)
                        pr.join()
                    elif not pr.is_alive():
                        pr.join()
                        row = error_row(t, "worker exited with code {} without a result".format(pr.exitcode), pr.pid)
                    elif time.monotonic() - ts > self.timeout_s:
                        pr.terminate()
                        pr.join()
                        row = error_row(t, "timeout after {:.0f} s (TIMEOUT_S {:.0f} s)".format(
                            time.monotonic() - ts, self.timeout_s), pr.pid)
                    if row is None:
                        continue
                    rc.close()
                    running.remove(item)
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
                    self.outs[ok_].write(row)
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
            for pr, rc, _t, _o, _ts in running:
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
            elif base in ("calprec2_tasks.csv", "calprec2_phaseA.csv"):
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
        print("  read {}: {} rows".format(f, len(rows)))
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


def grid_passes():
    """Passes the stop rule needs over the initial bracket: computed, printed."""
    w, p = BIS_HI / BIS_LO, 0
    while w - 1.0 > GRID_TOL and p < GRID_MAX_PASSES:
        w = w ** (1.0 / (GRID_K - 1))
        p += 1
    return p


def estimates(cells, starts, thr, mx, have_a):
    """(best-case s, worst-case s, largest single-task s, cells lacking throughput)."""
    best, worst, big, missing = 0.0, 0.0, 0.0, []
    P = grid_passes()
    for c in cells:
        u = (c[0], c[1], c[2], c[3])
        if u not in thr:
            missing.append(cell_id(c))
            continue
        td, tb, ts = thr[u]

        def pas(n, nb):
            return n * (td + nb * tb)
        a = 0.0 if cell_id(c) in have_a else R_CAL * sum(L_CAL) * (td + ts)
        big = max(big, L_CAL[-1] * (td + ts))
        s = starts[cell_id(c)]
        climb = sum(REPS * pas(L_REF[i], 1) for i in range(s, mx + 1))
        for i in range(s, mx + 1):
            big = max(big, pas(L_REF[i], 1))
        if mx == len(L_REF) - 1:
            ns = L_REF[-1]
            tail = 0.0
        else:
            ns = L_REF[max(s, mx - 1)]
            tail = REPS * pas(ns, NLEV) + REPS * pas(ns, 1)
            big = max(big, pas(ns, NLEV))
        solve = L_REF[0] * (td + ts) + P * pas(L_REF[0], GRID_K) + P * pas(ns, GRID_K) + REPS * pas(ns, 2)
        big = max(big, pas(min(ns, BLOCK_CHUNKS * CHUNK), GRID_K), pas(ns, 2))
        worst += a + climb + tail + solve
        s1 = min(s + 1, mx)
        best += a + REPS * pas(L_REF[s], 1) + REPS * pas(L_REF[s1], 1) + REPS * pas(L_REF[s], NLEV) \
            + REPS * pas(L_REF[s], 1)
    return best, worst, big, missing


# --------------------------------------------------------------------------
# the job
# --------------------------------------------------------------------------

def item(fn, t, out="tasks"):
    return (fn, t, out)


def rung_stats(store, label, c, n, idx=0, reps=None):
    vals = []
    for rep in (reps if reps is not None else range(REPS)):
        r = store.get(tid_of(label, c, n, rep))
        if r is None or r["end"] != "ok":
            return None
        vals.append(floats(r["tau_hat"])[idx])
    return median(vals), max(vals) - min(vals), vals


def highest_climbed(store, c):
    top = None
    for i, n in enumerate(L_REF):
        if rung_stats(store, "C", c, n) is not None:
            top = i
    return top


def r1_check(store, label, c, n, idx):
    """R1 between climb rows and re-evaluation rows at rung n; same env only."""
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


def grid_solve_round(runner, cells_n, store, label):
    """Run the grid passes for every (cell, n) in cells_n, all cells together,
    pass by pass. Returns {cid: (beta, lo, hi, widths) or error string}."""
    state = {}
    for cid, n in cells_n:
        state[cid] = {"n": n, "lo": BIS_LO, "hi": BIS_HI, "widths": [], "done": False, "err": None}
    for p in range(GRID_MAX_PASSES):
        live = [cid for cid in state if not state[cid]["done"] and state[cid]["err"] is None]
        if not live:
            break
        items = []
        for cid in live:
            s = state[cid]
            c = cell_from_id(cid)
            grid = list(np.geomspace(s["lo"], s["hi"], GRID_K))
            s["grid"] = grid
            for bi, blk in enumerate(blocks_of(s["n"])):
                items.append(item("block", {"tid": tid_of(label, c, s["n"], 0, "|p{}|b{}".format(p, bi)),
                                             "phase": label, "c": c, "n": s["n"], "rep": 0,
                                             "block": "p{}b{}".format(p, bi), "betas": grid, "chunks": blk}))
        runner.run(items, "{} pass {}".format(label, p + 1))
        for cid in live:
            s = state[cid]
            c = cell_from_id(cid)
            rows = [store.get(tid_of(label, c, s["n"], 0, "|p{}|b{}".format(p, bi)))
                    for bi in range(len(blocks_of(s["n"])))]
            if any(r is None or r["end"] != "ok" for r in rows):
                s["err"] = "incomplete (grid pass {})".format(p + 1)
                continue
            if floats(rows[0]["betas"]) != [float(repr(x)) for x in s["grid"]]:
                s["err"] = "grid of pass {} in the inputs differs from this job's".format(p + 1)
                continue
            per = [list(zip(floats(r["l1"]), floats(r["l2"]), floats(r["mx"]))) for r in rows]
            res = combine_terms(per, GRID_K)
            les = [log_ess_from(x) for x in res]
            goal = math.log(c[4] * s["n"])
            above = [i for i in range(GRID_K) if les[i] > goal]
            if not above or above[0] != 0:
                s["err"] = "target outside the grid bracket at pass {}".format(p + 1)
                continue
            i = max(above)
            if i >= GRID_K - 1:
                s["err"] = "target outside the grid bracket at pass {}".format(p + 1)
                continue
            s["lo"], s["hi"] = s["grid"][i], s["grid"][i + 1]
            s["widths"].append(s["hi"] / s["lo"] - 1.0)
            if s["widths"][-1] <= GRID_TOL:
                s["done"] = True
    out = {}
    for cid, s in state.items():
        if s["err"] is not None:
            out[cid] = s["err"]
        elif not s["done"]:
            out[cid] = "stop rule not met in {} passes".format(GRID_MAX_PASSES)
        else:
            out[cid] = (math.sqrt(s["lo"] * s["hi"]), s["lo"], s["hi"], s["widths"])
    return out


def job(a, cells, starts, runner, store):
    flags3 = []
    cmap = dict((cell_id(c), c) for c in cells)

    cp.hdr("PHASE A  calibration samples")
    items = [item("cal", {"tid": tid_of("A", c, N, rep), "phase": "A", "c": c, "n": N, "rep": rep,
                          "kind": K_CAL}, "phaseA")
             for c in cells for N in L_CAL for rep in range(R_CAL)]
    runner.run(items, "A")
    betas, badq = {}, {}
    for c in cells:
        rows = [store.get(tid_of("A", c, N, rep)) for N in L_CAL for rep in range(R_CAL)]
        if all(r is not None and r["end"] == "ok" for r in rows):
            bl = [float(r["beta_solved"]) for r in rows]
            betas[cell_id(c)] = bl
            badq[cell_id(c)] = median(bl[-R_CAL:])
    live = [cell_id(c) for c in cells if cell_id(c) in badq]
    print("  {} of {} cells have a complete phase A".format(len(live), len(cells)))

    cp.hdr("PHASE C  climb at beta_adq, up to rung {}".format(L_REF[a.max_rung]))
    status = {}
    pending = {}
    for cid in live:
        s = starts[cid]
        if s > a.max_rung:
            status[cid] = ("unresolved", s - 1)
            continue
        pending[cid] = [s] if s > 0 else [0, min(1, a.max_rung)]
    while pending:
        items = []
        for cid, rungs in pending.items():
            c = cmap[cid]
            for i in sorted(set(rungs)):
                for rep in range(REPS):
                    items.append(item("ref", {"tid": tid_of("C", c, L_REF[i], rep), "phase": "C", "c": c,
                                              "n": L_REF[i], "rep": rep, "kind": K_REF, "betas": [badq[cid]]}))
        runner.run(items, "C")
        nxt = {}
        for cid, rungs in pending.items():
            c = cmap[cid]
            hi = max(rungs)
            if hi == 0:
                status[cid] = ("unresolved", 0)
                continue
            s_lo = rung_stats(store, "C", c, L_REF[hi - 1])
            s_hi = rung_stats(store, "C", c, L_REF[hi])
            if s_lo is None or s_hi is None:
                status[cid] = ("incomplete (climb)", None)
                continue
            if s_lo[1] / s_lo[0] <= C5M_MAX and abs(s_lo[0] - s_hi[0]) / s_hi[0] <= D1_MAX:
                status[cid] = ("adequate", hi - 1)
            elif hi == len(L_REF) - 1:
                status[cid] = ("case_a", hi)
            elif hi >= a.max_rung:
                status[cid] = ("unresolved", hi)
            else:
                nxt[cid] = [hi + 1]
        pending = nxt
    for cid in sorted(status):
        st = status[cid]
        if st[0] == "unresolved":
            print("  {:<48} unresolved, highest evaluated rung {}".format(cid, L_REF[st[1]]))
        else:
            print("  {:<48} {}".format(cid, st))

    adq = sorted(cid for cid in status if status[cid][0] == "adequate")
    cp.hdr("PHASE C1  sufficiency pass at n*, {} cells".format(len(adq)))
    items = []
    for cid in adq:
        c, ns = cmap[cid], L_REF[status[cid][1]]
        for rep in range(REPS):
            items.append(item("ref", {"tid": tid_of("P", c, ns, rep), "phase": "P", "c": c, "n": ns,
                                      "rep": rep, "kind": K_REF, "betas": betas[cid] + [badq[cid]]}))
    runner.run(items, "C1")
    ncell, case_b = {}, []
    for cid in adq:
        c, ns = cmap[cid], L_REF[status[cid][1]]
        if r1_check(store, "P", c, ns, NLEV - 1) == "FAIL":
            flags3.append("R1 FAIL " + cid)
        rows = [store.get(tid_of("P", c, ns, rep)) for rep in range(REPS)]
        if any(r is None or r["end"] != "ok" for r in rows):
            continue
        taus = [floats(r["tau_hat"]) for r in rows]
        for li, N in enumerate(L_CAL):
            devs = [abs(median([t[li * R_CAL + j] for t in taus]) / c[4] - 1.0) for j in range(R_CAL)]
            if max(devs) <= C1_MAX:
                ncell[cid] = N
                break
        if cid not in ncell:
            case_b.append(cid)

    cp.hdr("PHASE B and C'  production beta and its check, {} cells".format(len(ncell)))
    runner.run([item("cal", {"tid": tid_of("B", cmap[cid], ncell[cid], 0), "phase": "B", "c": cmap[cid],
                             "n": ncell[cid], "rep": 0, "kind": K_PROD}) for cid in sorted(ncell)], "B")
    items = []
    for cid in sorted(ncell):
        r = store.get(tid_of("B", cmap[cid], ncell[cid], 0))
        if r is None or r["end"] != "ok":
            continue
        c, ns = cmap[cid], L_REF[status[cid][1]]
        for rep in PRODCHECK_REPS:
            items.append(item("ref", {"tid": tid_of("Q", c, ns, rep), "phase": "Q", "c": c, "n": ns,
                                      "rep": rep, "kind": K_REF, "betas": [float(r["beta_solved"])]}))
    runner.run(items, "C'")
    for cid in sorted(ncell):
        c, ns = cmap[cid], L_REF[status[cid][1]]
        s = rung_stats(store, "Q", c, ns, reps=PRODCHECK_REPS)
        if s is not None and abs(s[0] / c[4] - 1.0) > C6_MAX:
            case_b.append(cid)

    solves = [(cid, L_REF[status[cid][1]]) for cid in sorted(case_b)] + \
             [(cid, L_REF[-1]) for cid in sorted(status) if status[cid][0] == "case_a"]
    cp.hdr("PHASE S  E3, then grid solves, {} cells".format(len(solves)))
    runner.run([item("cal", {"tid": tid_of("H", cmap[cid], L_REF[0], 0), "phase": "H", "c": cmap[cid],
                             "n": L_REF[0], "rep": 0, "kind": K_SOLVE}) for cid, n in solves], "E3 held")
    g3 = grid_solve_round(runner, [(cid, L_REF[0]) for cid, n in solves], store, "G3")
    e3ok = {}
    for cid, n in solves:
        h = store.get(tid_of("H", cmap[cid], L_REF[0], 0))
        g = g3.get(cid)
        if h is None or h["end"] != "ok" or not isinstance(g, tuple):
            print("  E3 {}  not evaluated ({})".format(cid, g if not isinstance(g, tuple) else "held solve missing"))
            continue
        rel = abs(g[0] / float(h["beta_solved"]) - 1.0)
        e3ok[cid] = rel <= E3_TOL
        print("  E3 {}  held {}  grid {!r}  rel {:.2e}  {}".format(
            cid, h["beta_solved"], g[0], rel, "PASS" if e3ok[cid] else "FAIL"))
        if not e3ok[cid]:
            flags3.append("E3 FAIL " + cid)
    go = [(cid, n) for cid, n in solves if e3ok.get(cid)]
    gs = grid_solve_round(runner, go, store, "G")
    items = []
    for cid, n in go:
        g = gs.get(cid)
        if not isinstance(g, tuple):
            print("  solve {}: {}".format(cid, g))
            continue
        print("  solve {}  n {}  beta_s {!r}  widths {}".format(cid, n, g[0], ", ".join("{:.2e}".format(w) for w in g[3])))
        for rep in range(REPS):
            items.append(item("ref", {"tid": tid_of("E", cmap[cid], n, rep), "phase": "E", "c": cmap[cid],
                                      "n": n, "rep": rep, "kind": K_REF, "betas": [g[0], badq[cid]]}))
    runner.run(items, "S-eval")
    for cid, n in go:
        if r1_check(store, "E", cmap[cid], n, 1) == "FAIL":
            flags3.append("R1 FAIL " + cid)
    for r in list(store.values()):
        if r.get("e1") == "FAIL":
            flags3.append("E1 FAIL " + r["tid"])
    return sorted(set(flags3))


# --------------------------------------------------------------------------
# finalize
# --------------------------------------------------------------------------

def finalize(rows, cells, outdir):
    cp.hdr("FINALIZE  {} rows, {} cells".format(len(rows), len(cells)))
    st = dict((r["tid"], r) for r in rows)
    out, any3, any4 = [], False, False
    for c in cells:
        cid = cell_id(c)
        rec = {"cell": cid, "module": c[0], "objective": c[1], "d": c[2], "law": c[3], "tau0": repr(c[4])}
        flags = []
        arows = [st.get(tid_of("A", c, N, rep)) for N in L_CAL for rep in range(R_CAL)]
        if any(r is None or r["end"] != "ok" for r in arows):
            rec["label"] = "incomplete (phase A)"
            any4 = True
            out.append(rec)
            continue
        bl = [float(r["beta_solved"]) for r in arows]
        badq = median(bl[-R_CAL:])
        rec["beta_adq"] = repr(badq)
        e1 = st.get(tid_of("C", c, L_REF[0], 0))
        if e1 is None or e1.get("e1") not in ("PASS", "FAIL"):
            flags.append("E1 not run")
            any4 = True
        elif e1["e1"] == "FAIL":
            flags.append("E1 FAIL")
            any3 = True
        meds = {}
        for i, n in enumerate(L_REF):
            s = rung_stats(st, "C", c, n)
            if s is not None:
                meds[i] = s
        top = max(meds) if meds else None
        nstar = None
        for i in sorted(meds):
            if i + 1 in meds and meds[i][1] / meds[i][0] <= C5M_MAX and \
                    abs(meds[i][0] - meds[i + 1][0]) / meds[i + 1][0] <= D1_MAX:
                nstar = i
                break
        rec["rungs"] = ";".join(str(L_REF[i]) for i in sorted(meds))
        label, beta, prov, tref, rng, nsolve = None, None, "", None, None, None
        if nstar is not None:
            ns = L_REF[nstar]
            rec["n_star"] = ns
            rec["C5m"] = "{:.6f}".format(meds[nstar][1] / meds[nstar][0])
            rec["D1"] = "{:.6f}".format(abs(meds[nstar][0] - meds[nstar + 1][0]) / meds[nstar + 1][0])
            pr = [st.get(tid_of("P", c, ns, rep)) for rep in range(REPS)]
            if any(r is None or r["end"] != "ok" for r in pr):
                label = "incomplete (C1 pass)"
            else:
                r1 = r1_check(st, "P", c, ns, NLEV - 1)
                if r1 == "FAIL":
                    flags.append("R1 FAIL")
                    any3 = True
                elif r1.startswith("not applicable"):
                    flags.append("R1 not applicable (env differs)")
                taus = [floats(r["tau_hat"]) for r in pr]
                ncell = None
                for li, N in enumerate(L_CAL):
                    dev = max(abs(median([t[li * R_CAL + j] for t in taus]) / c[4] - 1.0) for j in range(R_CAL))
                    rec["C1_" + str(N)] = "{:.6f}".format(dev)
                    if ncell is None and dev <= C1_MAX:
                        ncell = N
                rec["N_cell"] = "" if ncell is None else ncell
                if ncell is not None:
                    b = st.get(tid_of("B", c, ncell, 0))
                    q = rung_stats(st, "Q", c, ns, reps=PRODCHECK_REPS)
                    if b is None or b["end"] != "ok" or q is None:
                        label = "incomplete (production or C')"
                    else:
                        dev = abs(q[0] / c[4] - 1.0)
                        rec["C6"] = "{:.6f}".format(dev)
                        if dev <= C6_MAX:
                            label, beta, prov = "target", float(b["beta_solved"]), "calibration N_cell {}".format(ncell)
                            tref, rng = q[0], q[1]
                if label is None:
                    nsolve, case = ns, "b"
        elif top is not None and top == len(L_REF) - 1:
            nsolve, case = L_REF[-1], "a"
        elif top is not None and meds:
            label = "unresolved, highest evaluated rung {}".format(L_REF[top])
        else:
            label = "incomplete (climb)"
        if label is None and nsolve is not None:
            h = st.get(tid_of("H", c, L_REF[0], 0))
            g3 = [st.get(t) for t in st if t.startswith("G3|" + cid + "|")]
            ev = rung_stats(st, "E", c, nsolve)
            gpasses = sorted(set(t.split("|p")[1].split("|")[0] for t in st if t.startswith("G|" + cid + "|")),
                             key=int) if any(t.startswith("G|" + cid + "|") for t in st) else []
            if h is None or h["end"] != "ok" or not g3:
                label = "incomplete (E3, case {})".format(case)
            elif ev is None:
                label = "incomplete (solve, case {})".format(case)
            else:
                beta = floats(st[tid_of("E", c, nsolve, 0)]["betas"])[0]
                tref, rng = ev[0], ev[1]
                dev = abs(tref / c[4] - 1.0)
                rec["case_dev"] = "{:.6f}".format(dev)
                rec["grid_passes"] = len(gpasses)
                prov = "grid solve at n {} (case {})".format(nsolve, case)
                label = "target" if (case == "b" and dev <= C6_MAX) else "beta"
                r1 = r1_check(st, "E", c, nsolve, 1)
                if r1 == "FAIL":
                    flags.append("R1 FAIL")
                    any3 = True
                elif r1.startswith("not applicable"):
                    flags.append("R1 not applicable (env differs)")
        if label.startswith("incomplete"):
            any4 = True
        rec.update({"label": label, "beta": "" if beta is None else repr(beta), "provenance": prov,
                    "tau_ref": "" if tref is None else repr(tref), "range": "" if rng is None else repr(rng),
                    "exact_tau": "" if beta is None or exact_tau(c, beta) is None else repr(exact_tau(c, beta)),
                    "flags": ";".join(flags)})
        out.append(rec)
    cols = ["cell", "module", "objective", "d", "law", "tau0", "label", "beta", "provenance", "tau_ref",
            "range", "exact_tau", "beta_adq", "rungs", "n_star", "C5m", "D1"] + \
        ["C1_" + str(N) for N in L_CAL] + ["N_cell", "C6", "case_dev", "grid_passes", "flags"]
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
    p.add_argument("--max-rung", type=int, default=len(L_REF) - 1)
    p.add_argument("--plan", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--throughput", default=None)
    p.add_argument("--inputs", default="")
    p.add_argument("--resume-from", default="")
    p.add_argument("--finalize", default="")
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    a = p.parse_args()
    rows = CALROWS if a.rows is None else [r for r in a.rows.split(",") if r]
    for r in rows:
        if r not in ROWMOD:
            sys.stderr.write("setup error: {} is not a calibrated row\n".format(r))
            return 2
    if not (0 <= a.max_rung < len(L_REF)) or not (0 <= a.shard < a.nshards) or a.workers < 1:
        sys.stderr.write("setup error: rung, shard or worker arguments out of range\n")
        return 2
    mode = "finalize" if a.finalize else "plan" if a.plan else "smoke" if a.smoke else "full"
    me = cp.sha256_file(os.path.abspath(__file__))
    cps = cp.sha256_file(os.path.abspath(cp.__file__))

    print("=" * 96)
    print("CBO-GAP calprec2 -- calprec v2: one fixed beta per calibration cell, through each row's module")
    print("=" * 96)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {}   start {}".format(
        platform.platform(), platform.machine(), os.cpu_count(), a.workers, multiprocessing.get_start_method()))
    print("  threads  " + "  ".join("{}={}".format(v, os.environ.get(v)) for v in cp.THREAD_VARS))
    print("  archive  {}".format(cp.ARCH))
    print("  script   sha256 {}".format(me))
    print("  costprobe2.py sha256 {}".format(cps))
    print("  mode     {}   rows {}   shard {} of {}   max rung {}".format(
        mode, ",".join(rows), a.shard, a.nshards, L_REF[a.max_rung]))
    print("  L_CAL {}  R {}   L_REF {}  reps {}   chunk {}  block {} chunks".format(
        L_CAL, R_CAL, L_REF, REPS, CHUNK, BLOCK_CHUNKS))
    print("  C5m <= {}  D1 <= {}  C1 <= {}  C6 <= {}  E1 <= {:g}  E3 <= {:g}  RSS <= {:.0f} MB".format(
        C5M_MAX, D1_MAX, C1_MAX, C6_MAX, E1_TOL, E3_TOL, RSS_BUDGET_MB))
    print("  grid     K {} per pass over [{:g}, {:g}], stop at relative width <= {:g}: {} passes by the rule".format(
        GRID_K, BIS_LO, BIS_HI, GRID_TOL, grid_passes()))
    print("  seeds    default_rng(SeedSequence(key + (chunk,))), full width; key = (ENTROPY {}, kind, module, "
          "objective, d, law, tau0e6 (0 for kind {}), n, rep); kinds A {} C {} B {} S {} smoke {}".format(
              ENTROPY, K_REF, K_CAL, K_REF, K_PROD, K_SOLVE, K_SMOKE))

    check_v(rows)

    allcells = sorted(set(c for r in rows for c in cal_cells(r)[0]), key=cell_id)
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
    if a.cells:
        want = set(x for x in a.cells.split(",") if x)
        bad = want - set(cell_id(c) for c in allcells)
        if bad:
            sys.stderr.write("setup error: unknown cell ids {}\n".format(sorted(bad)))
            return 2
        allcells = [c for c in allcells if cell_id(c) in want]
    cells = [c for i, c in enumerate(allcells) if i % a.nshards == a.shard]
    print("  this job: {} cells".format(len(cells)))

    params = [["script_sha256", me], ["costprobe2_sha256", cps], ["mode", mode], ["rows", ",".join(rows)],
              ["cells", a.cells or ""], ["shard", a.shard], ["nshards", a.nshards],
              ["max_rung", a.max_rung], ["workers", a.workers],
              ["python", platform.python_version()], ["numpy", np.__version__]]

    if mode == "finalize":
        _p, trows = read_folders([x for x in a.finalize.split(",") if x], ["script_sha256", "costprobe2_sha256", "rows"])
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir = os.path.join(OUTROOT, "calprec2-finalize-" + stamp)
        os.makedirs(outdir)
        fcells = sorted(set(r["cell"] for r in trows if r["phase"] == "A"))
        code = finalize(trows, [cell_from_id(x) for x in fcells], outdir)
        print("\nfiles  {}".format(outdir))
        return code

    store = {}
    if a.inputs:
        _p, irows = read_folders([x for x in a.inputs.split(",") if x],
                                 ["script_sha256", "costprobe2_sha256", "rows", "python", "numpy"])
        if _p and any(_p[0].get(k) != str(v) for k, v in params if k in ("script_sha256", "costprobe2_sha256",
                                                                          "rows", "python", "numpy")):
            sys.stderr.write("inputs: script, costprobe2, rows, Python or NumPy differ from this job's\n")
            return 2
        for r in irows:
            if r["end"] == "ok":
                store[r["tid"]] = r
    if a.resume_from:
        mine = dict((k, str(v)) for k, v in params)
        _p, rrows = read_folders([x for x in a.resume_from.split(",") if x], list(mine.keys()))
        if _p and dict((k, _p[0].get(k)) for k in mine) != mine:
            sys.stderr.write("resume: parameters differ from this run's (CLAUDE.md rule 17)\n")
            return 2
        for r in rrows:
            if r["end"] == "ok":
                if r["tid"] in store:
                    sys.stderr.write("resume: task {} also in the inputs\n".format(r["tid"]))
                    return 2
                store[r["tid"]] = r

    starts, have_a = {}, set()
    for c in cells:
        cid = cell_id(c)
        has_a = all(tid_of("A", c, N, rep) in store for N in L_CAL for rep in range(R_CAL))
        top = highest_climbed(store, c)
        if top is not None and not has_a:
            sys.stderr.write("inputs: cell {} has climb rows but no phase-A rows\n".format(cid))
            return 2
        if has_a:
            have_a.add(cid)
        starts[cid] = 0 if top is None else top + 1
    cp.hdr("RUNG RANGE PER CELL (this job)")
    for c in cells:
        cid = cell_id(c)
        s = starts[cid]
        print("  {:<48} phase A {}  rungs {} to {}{}".format(
            cid, "from inputs" if cid in have_a else "computed here",
            L_REF[s] if s < len(L_REF) else "-", L_REF[a.max_rung],
            "" if s == 0 else "  (judges {} first)".format(L_REF[s - 1])))

    thr = load_throughput(a.throughput) if a.throughput else None
    miss, worst, big = [], 0.0, 0.0
    if thr is not None:
        best, worst, big, miss = estimates(cells, starts, thr, a.max_rung, have_a)
        cp.hdr("G-CAP -- ESTIMATE for this job (perfect scaling; barrier idle and tails ignored; NOT a bound)")
        print("  best case {:.0f} s   worst-case estimate {:.0f} s   at {} workers   ceiling {:.0f} s".format(
            best / a.workers, worst / a.workers, a.workers, SHARD_CEIL_S))
        print("  largest single task, estimated {:.0f} s".format(big))
        if miss:
            print("  {} cells lack throughput: {}".format(len(miss), ", ".join(miss[:5])))
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
        for c in cells:
            print("  {}   rows {}".format(cell_id(c), ",".join(serves[cell_id(c)])))
        print("\nPLAN MODE: no draws, nothing written.")
        return 0
    if mode == "full":
        if thr is None:
            sys.stderr.write("G-CAP: a full run needs --throughput <verified smoke folder>\n")
            return 2
        if miss or worst / a.workers > SHARD_CEIL_S or timeout_s <= 0:
            sys.stderr.write("G-CAP: worst-case estimate {:.0f} s exceeds {:.0f} s, or cells lack "
                             "throughput; lower --max-rung or add shards\n".format(worst / a.workers, SHARD_CEIL_S))
            return 2

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tag = "" if a.nshards == 1 else "-s{}of{}".format(a.shard, a.nshards)
    outdir = os.path.join(OUTROOT, "calprec2-{}-{}{}".format(mode, stamp, tag))
    os.makedirs(outdir)
    with open(os.path.join(outdir, "calprec2_params.csv"), "x", newline="") as fh:
        csv.writer(fh).writerows(params)
    with open(os.path.join(outdir, "calprec2_plan.csv"), "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cell", "shard", "start_rung", "max_rung", "phase_a", "rows"])
        for c in cells:
            cid = cell_id(c)
            w.writerow([cid, a.shard, L_REF[starts[cid]] if starts[cid] < len(L_REF) else "", L_REF[a.max_rung],
                        "inputs" if cid in have_a else "here", ";".join(serves[cid])])
    print("\n  run dir  {}".format(outdir))

    if mode == "smoke":
        units = sorted(set((c[0], c[1], c[2], c[3], 0.1) for c in cells), key=cell_id)
        outs = {"thr": Out(os.path.join(outdir, "calprec2_throughput.csv"), THR_COLS)}
        runner = Runner(a.workers, timeout_s, outs, {})
        try:
            runner.run([item("smoke", {"tid": "SMOKE|" + cell_id(u), "phase": "SMOKE", "c": u}, "thr")
                        for u in units], "smoke")
        finally:
            outs["thr"].close()
        print("\nSMOKE: unit costs only; not results.")
        return 4 if runner.errors else 0

    outs = {"phaseA": Out(os.path.join(outdir, "calprec2_phaseA.csv"), TASK_COLS),
            "tasks": Out(os.path.join(outdir, "calprec2_tasks.csv"), TASK_COLS)}
    runner = Runner(a.workers, timeout_s, outs, store)
    try:
        flags3 = job(a, cells, starts, runner, store)
    finally:
        for o in outs.values():
            o.close()
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
