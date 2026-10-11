"""
calprec2.py  --  CBO-GAP round 2: calprec v2, one fixed beta per calibration
                 cell for the fixed-beta rerun, calibrated through each row's
                 own archived module

WHAT THIS PRODUCES, IN PLAIN LANGUAGE
-------------------------------------
The specification is notes/CALPREC_V2_SPEC.md (sections cited as "spec 5"
and so on). For every calibration cell

    (module, objective, d, initial law, tau0)

needed by a rerun row whose beta targets a concentration, this script finds
a fixed beta and measures the concentration tau(beta) that beta actually
produces, on large independent reference samples. The finalize step writes
the beta table (calprec2_beta.csv) that the rerun script reads. Each beta in
it is labelled "target" (tau(beta) is within 5% of tau0) or "beta" (it is
not, or cannot be shown to be; the cell is then labelled by its beta, never
by a target; spec 6, ledger N18 O2).

No trajectories are evolved. Nothing in the archive is written to.

WHAT IS IMPORTED, AND THE ONE THING THAT IS NOT
  * The archive modules and the grid of every rerun row come from
    scripts/costprobe2.py: its MODS (imported from the archive, hashed by
    V1 below), its GRID and SOURCE (checked against the archived source by
    V0 below), its objective_of and probe_sample. calprec2 therefore
    calibrates exactly the grid costprobe2 measured. A change to
    costprobe2.py changes this script, so costprobe2.py's sha256 is printed
    and stored in the params file.
  * The objective of a cell is its own module's (spec 3, RERUN_PLAN F5):
    OBJECTIVES[name] (mechanism, control, boundary), OBJ[name] (sigma,
    crossed, cliff, regimemap) or objective(name)[0] (regime, law).
  * The initial law is drawn with the module's own draw_initial (mechanism,
    control, regime). For the modules whose one_realisation draws X0
    inline (boundary, law, sigma, crossed, cliff, regimemap), it is drawn as
    rng.standard_normal((n, d)) + x*, with x* from the module's own dict.
    That one line is the only sampling code not imported; V2 checks it
    against the module source.
  * The bisection is exactcal.beta_on_ensemble (bracket 1e-10 to 1e10, 200
    geometric steps), as in calprec v1 and refscale.
  * The streamed log-ESS is the refscale composition: exactcal._logsumexp
    applied per chunk to -beta f and to -2 beta f, then applied to the
    vector of chunk results. E1 checks it against exactcal.log_ess_of.
  * The streamed bisection (laptop mode, spec D5 and D5a) is NOT imported:
    it repeats beta_on_ensemble's bracket, step count and comparison, with
    the streamed log-ESS in place of log_ess_of. E2 checks it against
    beta_on_ensemble.

CELLS (spec 2)
  The rows and their modules:
    CONC mechanism, ADAPT control, TAU8 boundary,
    REFSIZE / SYNTH / NAMED / HORIZON regime, GEOM law, SIGMA sigma,
    ANISO crossed, RMAP and ONSET regimemap, CLIFF cliff.
  BETA-ISO, BETA-ANI and LAWPANEL are excluded (their beta is a design
  value or the B rule, F1). PROBEARM is excluded: its beta is
  mechanism.beta_for_target (D6). PERJ is dropped (F4). Identical cells of
  one module are calibrated once. The plan prints the deduplicated count
  per module; no count is stated here.

PROCEDURE PER CELL (spec 4; the phases run with a barrier between them,
in parallel over cells and replicates)
  A   CALIBRATION. For each N in L_CAL = 4000, 16000, 64000, 256000,
      1000000, 4000000 and each of R = 24 draws: N values from the cell's
      law and objective (kind 31), beta_hat = beta_on_ensemble(values,
      tau0, N).
      beta_adq = the median of the 24 beta_hat at N = 4000000 (the mean of
      the 12th and 13th sorted).
  C   CLIMB. The reference ladder is L_REF = 1M, 4M, 16M, 64M, 256M, 1G,
      with six replicates per rung (kind 32), each streamed in chunks of
      250000 and evaluated at beta_adq.
      - Rungs are evaluated in ascending order from --start-rung. Rung i is
        judged once rung i+1 has been evaluated.
      - The first rung that passes C5m and D1 is the adequate rung n*.
      - If rung i+1 is the top rung (1G) and rung i is not adequate, the
        cell is case (a): 1G cannot be adequate, because its D1 is
        untested (as in refscale).
      - If --max-rung stops the climb first, the cell is "unresolved,
        continue at rung <next>". A later job continues it with --cells and
        --start-rung (ledger K5: Kaggle cannot resume from earlier output,
        so the continuation recomputes phase A, whose seeds make it
        identical).
  C1  SUFFICIENCY PASS, at n*. The six replicates of rung n* are
      regenerated from their keys and evaluated at all 144 beta_hat and at
      beta_adq. R1 requires beta_adq to reproduce the climb's values.
      N_cell = the smallest N whose 24 beta_hat all pass C1.
  B   PRODUCTION. One further sample of size N_cell (kind 33), beta_prod =
      beta_on_ensemble(values, tau0, N_cell).
  C'  PRODUCTION CHECK. beta_prod is evaluated on six NEW replicates of size
      n* (kind 32, replicates 6 to 11): C6.
  S   SOLVES, for cases (a) and (b) (spec 6).
      - Case (b): an adequate rung, but no N is sufficient, or C6 fails.
      - Case (a): no adequate rung below 1G.
      The solve size is n* for case (b) and 1G for case (a). beta_s =
      beta_on_ensemble on an independent stream of that size (kind 34, rep
      0), evaluated on the six kind-32 replicates of that size. That
      evaluation also includes beta_adq, for R1.
      If the solve size exceeds the held cap (1024 MB of values, that is
      134217728 values), the solve is not done here. The cell is written
      as "streamed solve pending, laptop" (D5a), for --streamed-solve.

PRE-SPECIFIED CRITERIA (fixed 2026-10-11, before first execution)
------------------------------------------------------------------
  V0  PLAN IDENTITY.
      (a) costprobe2's P0(a): every grid factor of every row equals the
          constant the archived script assigns, read from its source.
      (b) For every row, the number of calibration cells times the levels
          of the factors that do not enter beta equals Table 2's cell
          count.
      Otherwise exit 2.
      Worked example (spec 5): SIGMA has 4 objectives x 3 d x 2 tau0 = 24
      cells. Times 2 diffusions x 6 r = 12, that gives 288, Table 2's
      count: pass. With an r list of five values, 24 x 10 = 240: exit 2.
  V1  ARCHIVE IDENTITY. Every imported archive module's __file__ lies in the
      archive and hashes to its zenodo-v1.sha256 entry, or exit 2.
      Worked example: regimemap.py hashes to eb1d704f...14c8: ok.
  V2  SAMPLER IDENTITY. For every module used, the first line after
      "rng = np.random.default_rng(seed)" in one_realisation that mentions
      "rng" must be exactly the X0 line that this script's sampler
      reproduces or calls (SAMPLER_LINE below), or exit 2.
      Worked example: sigma.one_realisation's first such line is
      "X0 = rng.standard_normal((Jinf, d)) + xs": ok.
  E1  STREAMING EQUIVALENCE. Whenever replicate 0 of the lowest rung (1M)
      is evaluated, it is also held. For every beta,
          |logESS_streamed - logESS_held| / |logESS_held| <= 1e-12,
      where logESS_held is exactcal.log_ess_of on the held array. A failure
      writes all rows, then exits 3.
      Worked example (refscale): 10.596634733096073 against
      10.596634733096080 gives 6.6e-16: pass.
  R1  REGENERATION IDENTITY. When a rung's six replicates are regenerated
      (in the C1 pass, or in an S evaluation at a climbed rung), tau_hat at
      beta_adq must equal the climb's value, compared as repr strings. A
      failure writes all rows, then exits 3. This catches a stream that is
      not a pure function of its key.
      Worked example: climb 0.0099834716023, regenerated 0.0099834716023:
      pass. A difference in the last digit: exit 3.
  C5m PRECISION OF THE MEDIAN-OF-SIX ESTIMATE (spec 5 and 11a; ledger N23).
      tau_ref = the median of the six tau_hat (the mean of the 3rd and
      4th sorted). A rung passes when
          range / tau_ref <= 0.054682
      at beta_adq.
      Worked examples (spec 5):
      - 0.00970 0.00980 0.00985 0.00990 0.01000 0.01010: tau_ref 0.009875,
        range 0.00040, ratio 0.0405: pass.
      - 0.00940 0.00960 0.00975 0.00985 0.00995 0.01010: ratio 0.0714: fail.
      - tau_ref 0.010000 with range 0.000545: ratio 0.0545, pass; with range
        0.000550: ratio 0.0550, fail.
  D1  DRIFT. |tau_ref(n) - tau_ref(4n)| / tau_ref(4n) <= 0.025, at
      beta_adq.
      Worked example: 0.00995 at 64M and 0.01003 at 256M give 0.0080: pass.
  ADEQUATE. A rung is adequate when it passes C5m and D1. The top rung is
      never adequate.
  C1  SUFFICIENCY, on the adequate rung n*. A level N is sufficient when
          max over its 24 draws of |tau_ref(beta_hat_r) / tau0 - 1| <= 0.05.
      Worked example: realized values 0.0098 to 0.0104 at tau0 = 0.01 give
      a maximum of 0.04: sufficient.
  N_cell  The smallest sufficient N in L_CAL, or none (case (b)).
  C6  PRODUCTION CHECK. |tau_ref(beta_prod) / tau0 - 1| <= 0.05, over the
      six C' replicates. On failure, case (b).
      Worked example: tau0 0.1, tau_ref 0.1042: deviation 0.042, pass.
  CB  CASE (b) RELABEL. If |tau_ref(beta_s) / tau0 - 1| <= 0.05 over the six
      evaluation replicates, the cell is labelled "target" with beta_s;
      otherwise "beta". (Spec 6 says "solve on one replicate and evaluate on
      the other five". This script solves on an independent kind-34 stream
      and evaluates on all six. See notes/CALPREC_V2_REVIEW.md, which lists
      this as an interpretation for Rahul.)
  CA  CASE (a). The cell is labelled "beta", with beta_s solved at 1G, and
      tau(beta_s) is the median of six 1G replicates, with their range.
  E2  STREAMED-SOLVE EQUIVALENCE (laptop mode only). On a 1M kind-34 stream
      of the cell, the streamed bisection and beta_on_ensemble on the held
      values must agree:
          |beta_streamed / beta_held - 1| <= 1e-9.
      Otherwise that cell's streamed solve is not used and is reported.
      Worked example (illustrative values): 6.028534528294139 against
      6.028534528294161: 3.6e-15, pass.
  S1  LARGEST-TERM SHARE. Reported per replicate and beta, no threshold.
  X1/X2  EXACT TAU. Reported, no threshold. These apply only to the
      centred law at x* = 0 with a diagonal quadratic objective: sphere
      (all a_i = 1) and the synthetic rho = 0 landscapes (a_i =
      kappa^((i-1)/(d-1))):
          tau(beta) = prod_i (1 + 4 beta a_i)^(1/2) / (1 + 2 beta a_i).
      Worked example: d = 2, a = (1, 1), beta = 0.5 gives 0.75.
  G-RSS  Peak RSS of every task <= 3072 MB. Beyond that, a FAIL line is
      printed and the row is flagged. Plan mode refuses to hold more than
      1024 MB of values (134217728 doubles).
  G-CAP  A full run is refused (exit 2) unless --throughput names a verified
      smoke folder, and the projected UPPER bound for this job is at most
      21600 s.
      upper bound = (sum over the job's cells of A + climb from --start-rung
                    to --max-rung + C1 pass, C' and S at the rung below
                    --max-rung) / workers
      Each cost is n x (t_draw + n_beta x t_beta) per pass, plus n x
      t_solve per solve, with the unit costs taken from the smoke's
      throughput table for the cell's (module, objective, d, law).
      Worked example (illustrative values): t_draw 3e-6 s, t_beta 2e-8 s,
      one rung of 6 x 4M at one beta gives 6 x 4e6 x (3.02e-6) = 72.5 s.

SEEDS (spec 7)
  Every stream is numpy.random.default_rng(SeedSequence(key + (chunk,)))
  at full width (ledger N16), with
      key = (ENTROPY 20261010, kind, module code, objective code, d,
             law code, tau0 x 1e6, n, rep)
  and kinds 31 (calibration), 32 (reference), 33 (production), 34 (solve),
  35 (smoke). Reference keys (kind 32) carry tau0 = 0, as the spec states,
  so the cells of one (module, objective, d, law) share their reference
  streams. The chunk index is appended to the key, so that any chunk can
  be regenerated alone. That addition to spec 7 makes a pass parallel over
  chunks (laptop mode) and lets R1 regenerate streams. Codes are the
  indices in costprobe2's MODULES, OBJ_NAMES and LAWS. Every key is written
  out in full.

MODES
  --plan            V0, V1, V2, the cell list, its sharding and, with
                    --throughput, the projections. No draws; nothing
                    written.
  --smoke           For every (module, objective, d, law) in the plan,
                    measures t_draw and t_solve (one 4M draw and its solve)
                    and t_beta (a 1M reference at 1 beta and at 145 betas).
                    It writes calprec2_throughput.csv. These are not
                    results.
  (default)         The procedure above for the selected cells, as one job.
  --rows R,R        The rows to calibrate (default: all thirteen).
  --cells ID,ID     Restrict to these cell ids (as printed by --plan).
  --shard i --nshards k
                    Cells sorted by id, cell j goes to shard j mod k.
  --start-rung i --max-rung j
                    Climb from L_REF[i]; evaluate no rung above L_REF[j]
                    (defaults 0 and 5).
  --resume-from DIR[,DIR]
                    CLAUDE.md rule 17. Verified folders whose params equal
                    this run's (other than the folder list) prefill the
                    task store; tasks found there are not recomputed;
                    output goes to a new folder; a completed task found
                    twice stops the run.
  --streamed-solve DIR[,DIR]
                    Laptop mode (D5a). For every "streamed solve pending"
                    cell in the verified folders: E2, then the streamed
                    bisection (one row per step, so --resume-from continues
                    it), then the six-replicate evaluation.
  --finalize DIR[,DIR]
                    No draws. Merges the verified folders: a repeated task
                    id is accepted only over an earlier error row. It
                    recomputes every verdict per cell from the rows and
                    writes calprec2_beta.csv.

OUTPUT (new folder <outdir>/calprec2-<mode>-<timestamp>[-s<i>of<k>]/, every
        file opened "x", every row flushed and fsynced; a task's row is
        written only when the task is complete, with end "ok")
  calprec2_params.csv      the parameters resumption and finalize compare
  calprec2_plan.csv        the cells, their shard, the rows they serve
  calprec2_tasks.csv       one row per task: tid, phase, cell, key, n, rep,
                           the betas and the per-beta log-ESS, tau_hat, S1
                           share and E1 values (";"-joined repr lists),
                           beta_hat or beta_s with the achieved fraction,
                           wall, peak RSS, G-RSS flag, error, end
  calprec2_steps.csv       laptop mode: one row per bisection step
  calprec2_throughput.csv  smoke only
  calprec2_beta.csv        finalize only: one row per cell, with label,
                           beta (repr), provenance, tau_ref, range, n*,
                           N_cell and every verdict

HOW TO RUN (from the repository root, venv active)
    python scripts/calprec2.py --plan
    python scripts/calprec2.py --workers 4 --smoke
    python scripts/calprec2.py --workers 4 --throughput DIR --max-rung 3 --shard 0 --nshards K
    python scripts/calprec2.py --workers 2 --streamed-solve DIR[,DIR]
    python scripts/calprec2.py --finalize DIR[,DIR]
  --archive and --outdir are resolved by scripts/cbopaths.py.
  Exit codes: 0 completed; 2 setup error (V0, V1, V2, G-CAP, a resume or
  finalize check); 3 E1 or R1 failed.

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
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402
from multiprocessing import Pool                                # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cbopaths                                                 # noqa: E402
import costprobe2 as cp                                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = cbopaths.output_root(ROOT)
EC = cp.MODS["exactcal"]

ENTROPY = 20261010
K_CAL, K_REF, K_PROD, K_SOLVE, K_SMOKE = 31, 32, 33, 34, 35
L_CAL = [4000, 16000, 64000, 256000, 1000000, 4000000]
R_CAL = 24
L_REF = [1000000, 4000000, 16000000, 64000000, 256000000, 1024000000]
REPS = 6
PRODCHECK_REPS = list(range(6, 12))
CHUNK = 250000
C5M_MAX = 0.054682
D1_MAX = 0.025
C1_MAX = 0.05
C6_MAX = 0.05
E1_TOL = 1e-12
E2_TOL = 1e-9
RSS_BUDGET_MB = 3072.0
HELD_CAP_VALUES = (1024 * 1024 * 1024) // 8
SHARD_CEIL_S = 21600.0
BIS_LO, BIS_HI, BIS_STEPS = 1e-10, 1e10, 200
N_SMOKE_DRAW, N_SMOKE_REF, SMOKE_NBETA = 4000000, 1000000, 145

ROWMOD = {"CONC": "mechanism", "ADAPT": "control", "TAU8": "boundary",
          "REFSIZE": "regime", "SYNTH": "regime", "NAMED": "regime", "HORIZON": "regime",
          "GEOM": "law", "SIGMA": "sigma", "ANISO": "crossed", "RMAP": "regimemap",
          "CLIFF": "cliff", "ONSET": "regimemap"}
CALROWS = ["CONC", "ADAPT", "TAU8", "REFSIZE", "SYNTH", "NAMED", "HORIZON", "GEOM",
           "SIGMA", "ANISO", "RMAP", "CLIFF", "ONSET"]

# V2: the first rng line of each module's one_realisation, which the sampler
# (costprobe2.probe_sample) reproduces or calls.
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
# cells
# --------------------------------------------------------------------------

def cal_cells(row):
    """(calibration cells of a row, product of the levels that do not enter beta)."""
    g = cp.GRID[row]
    m = ROWMOD[row]
    if row == "CONC":
        c = [(m, o, d, law, t) for o in g["objs"] for d in g["dims"]
             for law in g["laws"] for t in g["taus"]]
        return c, 1
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
    if n > HELD_CAP_VALUES:
        raise ValueError("held size {} exceeds the cap {}".format(n, HELD_CAP_VALUES))
    out = np.empty(n, dtype=np.float64)
    pos = 0
    for ci, m in chunks_of(n):
        out[pos:pos + m] = f_chunk(c, key, ci, m)
        pos += m
    return out


def chunk_terms(fv, betas):
    """Per beta: (lse(-b f), lse(-2 b f), max(-2 b f)) for one chunk."""
    out = []
    for b in betas:
        a = -b * fv
        a2 = 2.0 * a
        out.append((EC._logsumexp(a), EC._logsumexp(a2), float(np.max(a2))))
    return out


def combine_terms(per_chunk, nb):
    res = []
    for i in range(nb):
        l1 = EC._logsumexp(np.asarray([t[i][0] for t in per_chunk]))
        l2 = EC._logsumexp(np.asarray([t[i][1] for t in per_chunk]))
        mx = max(t[i][2] for t in per_chunk)
        res.append((2.0 * l1 - l2, math.exp(mx - l2)))
    return res


def tau_of(log_ess, n):
    return math.exp(min(log_ess, 700.0)) / n


def exact_tau(c, beta):
    """X1/X2: centred law, x* = 0, diagonal quadratic objective; else None."""
    m, o, d, law, _t = c
    if law != "centred":
        return None
    if o == "sphere":
        a = np.ones(d)
    else:
        mod = cp.MODS[m]
        sp = getattr(mod, "SYNTH_PARAMS", {})
        if o not in sp or sp[o][1] != 0.0:
            return None
        a = sp[o][0] ** (np.arange(d, dtype=float) / max(d - 1, 1))
    return float(math.exp(float(np.sum(0.5 * np.log1p(4.0 * beta * a) - np.log1p(2.0 * beta * a)))))


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


# --------------------------------------------------------------------------
# tasks (each returns one row dict)
# --------------------------------------------------------------------------

def jl(xs):
    return ";".join(repr(float(x)) for x in xs)


def task_cal(a):
    phase, c, N, rep, kind = a
    t0 = time.time()
    key = key_of(kind, c, N, rep)
    row = {"tid": "{}|{}|{}|{}".format(phase, cell_id(c), N, rep), "phase": phase,
           "cell": cell_id(c), "key": key_str(key), "n": N, "rep": rep}
    try:
        fv = values_held(c, key, N)
        beta, ach = EC.beta_on_ensemble(fv, c[4], N)
        row.update({"beta_solved": repr(float(beta)), "achieved": repr(float(ach)), "end": "ok"})
    except Exception as exc:
        row.update({"error": "{}: {}".format(type(exc).__name__, exc), "end": "err"})
    row["wall_s"] = "{:.3f}".format(time.time() - t0)
    row["rss_mb"] = "{:.1f}".format(rss_mb())
    return row


def task_ref(a):
    """One replicate, streamed, at a list of betas. Replicate 0 of rung L_REF[0]
    is also held (E1)."""
    label, c, n, rep, betas = a
    t0 = time.time()
    key = key_of(K_REF if label != "SE" else K_SOLVE, c, n, rep)
    row = {"tid": "{}|{}|{}|{}".format(label, cell_id(c), n, rep), "phase": label,
           "cell": cell_id(c), "key": key_str(key), "n": n, "rep": rep, "betas": jl(betas)}
    try:
        hold = (n == L_REF[0] and rep == 0)
        held = np.empty(n, dtype=np.float64) if hold else None
        per, pos = [], 0
        for ci, m in chunks_of(n):
            fv = f_chunk(c, key, ci, m)
            if hold:
                held[pos:pos + m] = fv
            pos += m
            per.append(chunk_terms(fv, betas))
        res = combine_terms(per, len(betas))
        les = [r[0] for r in res]
        row["log_ess"] = jl(les)
        row["tau_hat"] = jl([tau_of(x, n) for x in les])
        row["share"] = jl([r[1] for r in res])
        ex = [exact_tau(c, b) for b in betas]
        row["exact_tau"] = ";".join("" if e is None else repr(e) for e in ex)
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


def task_smoke(a):
    c = a
    row = {"tid": "SMOKE|{}|{}|{}|{}".format(c[0], c[1], c[2], c[3]), "phase": "SMOKE",
           "cell": cell_id(c)}
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
            per = []
            for ci, m in chunks_of(N_SMOKE_REF):
                per.append(chunk_terms(f_chunk(c, k2, ci, m), betas))
            combine_terms(per, len(betas))
            walls.append(time.time() - t0)
        t_beta = (walls[1] - walls[0]) / ((SMOKE_NBETA - 1) * N_SMOKE_REF)
        row.update({"t_draw": repr(t_draw), "t_solve": repr(t_solve), "t_beta": repr(t_beta),
                    "beta": repr(float(beta)), "end": "ok"})
    except Exception as exc:
        row.update({"error": "{}: {}".format(type(exc).__name__, exc), "end": "err"})
    row["rss_mb"] = "{:.1f}".format(rss_mb())
    return row


TASK_COLS = ["tid", "phase", "cell", "key", "n", "rep", "betas", "log_ess", "tau_hat", "share",
             "exact_tau", "e1_reldiff", "e1", "beta_solved", "achieved", "status", "wall_s",
             "rss_mb", "rss_flag", "error", "end"]
STEP_COLS = ["tid", "cell", "n", "step", "lo", "hi", "mid", "log_ess", "goal", "end"]
THR_COLS = ["tid", "phase", "cell", "t_draw", "t_solve", "t_beta", "beta", "rss_mb", "error", "end"]


# --------------------------------------------------------------------------
# files, folders, the task store
# --------------------------------------------------------------------------

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


def read_folders(folders, compare_keys):
    """Verified rows from folders: (params list, task rows, step rows). A repeated
    tid is accepted only over an earlier error row (as costprobe2's D1)."""
    params, tasks, steps = [], {}, {}
    order_t, order_s = [], []
    ref = None
    for f in folders:
        rels = cp.verify_folder(f)
        pr, tr, sr = None, [], []
        for rel in rels:
            base = os.path.basename(rel)
            p = os.path.join(f, rel)
            if base == "calprec2_params.csv":
                pr = dict((r[0], r[1]) for r in csv.reader(open(p, newline="")) if r)
            elif base == "calprec2_tasks.csv":
                tr.extend(csv.DictReader(open(p, newline="")))
            elif base == "calprec2_steps.csv":
                sr.extend(csv.DictReader(open(p, newline="")))
        if pr is None:
            sys.stderr.write("{} has no calprec2_params.csv\n".format(f))
            sys.exit(2)
        cmp_ = dict((k, pr.get(k)) for k in compare_keys)
        if ref is None:
            ref = cmp_
        elif cmp_ != ref:
            sys.stderr.write("{} differs in {} from the first folder: {} vs {}\n".format(
                f, compare_keys, cmp_, ref))
            sys.exit(2)
        params.append(pr)
        for store, order, rows in ((tasks, order_t, tr), (steps, order_s, sr)):
            for r in rows:
                t = r["tid"]
                if t in store:
                    if store[t]["end"] == "ok":
                        sys.stderr.write("task {} is complete in an earlier folder and repeated in {}\n".format(t, f))
                        sys.exit(2)
                else:
                    order.append(t)
                store[t] = r
        print("  read {}: {} task rows, {} step rows".format(f, len(tr), len(sr)))
    return params, [tasks[t] for t in order_t], [steps[t] for t in order_s]


def floats(s):
    return [float(x) for x in s.split(";")] if s else []


def median(v):
    return float(np.median(np.asarray(v, dtype=np.float64)))


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
        src = inspect.getsource(cp.MODS[m].one_realisation).splitlines()
        lines = [s.strip() for s in src]
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
# projection (G-CAP)
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


def project(cells, thr, start, mx):
    lo_tot, hi_tot, missing = 0.0, 0.0, []
    nlev = len(L_CAL) * R_CAL + 1
    for c in cells:
        u = (c[0], c[1], c[2], c[3])
        if u not in thr:
            missing.append(cell_id(c))
            continue
        td, tb, ts = thr[u]
        a = R_CAL * sum(L_CAL) * (td + ts)

        def ref(n, nb, reps=REPS):
            return reps * n * (td + nb * tb)
        climb_hi = sum(ref(L_REF[i], 1) for i in range(start, mx + 1))
        top = L_REF[max(start, mx - 1)]
        tail_hi = ref(top, nlev) + ref(top, 1) + (top * (td + ts) if top <= HELD_CAP_VALUES else 0.0) \
            + ref(top, 2)
        s0 = L_REF[start]
        lo = a + ref(s0, 1) + ref(L_REF[min(start + 1, mx)], 1) + ref(s0, nlev) + ref(s0, 1)
        lo_tot += lo
        hi_tot += a + climb_hi + tail_hi
    return lo_tot, hi_tot, missing


# --------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------

def run_pool(pool, fn, args, out, store, label):
    """Run tasks not already in the store; write each row on completion."""
    todo = [x for x in args if x[0] not in store]
    done = [store[x[0]] for x in args if x[0] in store]
    print("  [{}] {} task(s), {} taken from earlier folders".format(label, len(todo), len(done)))
    sys.stdout.flush()
    t0 = time.time()
    res = []
    for i, row in enumerate(pool.imap_unordered(fn, [x[1] for x in todo], chunksize=1)):
        rss = float(row.get("rss_mb") or 0.0)
        if rss > RSS_BUDGET_MB:
            row["rss_flag"] = "G-RSS FAIL"
            print("  G-RSS FAIL {} {:.1f} MB".format(row["tid"], rss))
        out.write(row)
        store[row["tid"]] = row
        res.append(row)
        if row["end"] != "ok":
            print("  ERROR {}: {}".format(row["tid"], row.get("error", "")))
        if (i + 1) % 50 == 0 or i + 1 == len(todo):
            print("    {}/{} done, {:.0f} s".format(i + 1, len(todo), time.time() - t0))
            sys.stdout.flush()
    return done + res


def tid_ref(label, c, n, rep):
    return "{}|{}|{}|{}".format(label, cell_id(c), n, rep)


def rung_stats(store, label, c, n, idx=0):
    vals = []
    for rep in range(REPS):
        r = store.get(tid_ref(label, c, n, rep))
        if r is None or r["end"] != "ok":
            return None
        vals.append(floats(r["tau_hat"])[idx])
    med = median(vals)
    return med, max(vals) - min(vals), vals


def full_run(a, cells, out, store, outdir):
    fail3 = []
    pool = Pool(processes=a.workers, maxtasksperchild=1)
    try:
        # A
        cp.hdr("PHASE A  calibration samples, {} cells x {} levels x {} draws".format(
            len(cells), len(L_CAL), R_CAL))
        args = []
        for c in cells:
            for N in L_CAL:
                for rep in range(R_CAL):
                    args.append(("A|{}|{}|{}".format(cell_id(c), N, rep), ("A", c, N, rep, K_CAL)))
        run_pool(pool, task_cal, args, out, store, "A")
        betas, badq = {}, {}
        for c in cells:
            bl = {}
            for N in L_CAL:
                rows = [store.get("A|{}|{}|{}".format(cell_id(c), N, rep)) for rep in range(R_CAL)]
                if any(r is None or r["end"] != "ok" for r in rows):
                    bl = None
                    break
                bl[N] = [float(r["beta_solved"]) for r in rows]
            if bl is not None:
                betas[cell_id(c)] = bl
                badq[cell_id(c)] = median(bl[L_CAL[-1]])
        live = [c for c in cells if cell_id(c) in badq]
        print("  {} of {} cells have a complete phase A".format(len(live), len(cells)))

        # C, the climb
        cp.hdr("PHASE C  climb at beta_adq, rungs {} to {}".format(L_REF[a.start_rung], L_REF[a.max_rung]))
        status = {}
        pending = dict((cell_id(c), [a.start_rung, min(a.start_rung + 1, a.max_rung)]) for c in live)
        cmap = dict((cell_id(c), c) for c in live)
        while pending:
            args = []
            for cid, rungs in pending.items():
                c = cmap[cid]
                for i in sorted(set(rungs)):
                    for rep in range(REPS):
                        args.append((tid_ref("C", c, L_REF[i], rep), ("C", c, L_REF[i], rep, [badq[cid]])))
            run_pool(pool, task_ref, args, out, store, "C")
            nxt = {}
            for cid, rungs in pending.items():
                c = cmap[cid]
                hi = max(rungs)
                if hi == a.start_rung:          # start == max: nothing to compare
                    status[cid] = ("unresolved", hi + 1)
                    continue
                s_lo = rung_stats(store, "C", c, L_REF[hi - 1])
                s_hi = rung_stats(store, "C", c, L_REF[hi])
                if s_lo is None or s_hi is None:
                    status[cid] = ("incomplete", None)
                    continue
                c5 = s_lo[1] / s_lo[0] <= C5M_MAX
                d1 = abs(s_lo[0] - s_hi[0]) / s_hi[0] <= D1_MAX
                if c5 and d1:
                    status[cid] = ("adequate", hi - 1)
                elif hi == len(L_REF) - 1:
                    status[cid] = ("case_a", hi)
                elif hi >= a.max_rung:
                    status[cid] = ("unresolved", hi)
                else:
                    nxt[cid] = [hi + 1]
            pending = nxt
        for cid in sorted(status):
            print("  {:<48} {}".format(cid, status[cid]))

        # C1 pass, B, C'
        adq = [cid for cid in status if status[cid][0] == "adequate"]
        cp.hdr("PHASE C1  sufficiency pass at n*, {} cells".format(len(adq)))
        args = []
        for cid in adq:
            c, ns = cmap[cid], L_REF[status[cid][1]]
            bl = [b for N in L_CAL for b in betas[cid][N]] + [badq[cid]]
            for rep in range(REPS):
                args.append((tid_ref("P", c, ns, rep), ("P", c, ns, rep, bl)))
        run_pool(pool, task_ref, args, out, store, "C1")
        ncell, case_b = {}, []
        for cid in adq:
            c, ns = cmap[cid], L_REF[status[cid][1]]
            rows = [store.get(tid_ref("P", c, ns, rep)) for rep in range(REPS)]
            if any(r is None or r["end"] != "ok" for r in rows):
                continue
            taus = [floats(r["tau_hat"]) for r in rows]
            climb = [store[tid_ref("C", c, ns, rep)]["tau_hat"].split(";")[0] for rep in range(REPS)]
            regen = [r["tau_hat"].split(";")[-1] for r in rows]
            if climb != regen:
                fail3.append("R1 " + cid)
            nc = None
            for li, N in enumerate(L_CAL):
                devs = []
                for j in range(R_CAL):
                    k = li * R_CAL + j
                    devs.append(abs(median([t[k] for t in taus]) / c[4] - 1.0))
                if max(devs) <= C1_MAX:
                    nc = N
                    break
            if nc is None:
                case_b.append(cid)
            else:
                ncell[cid] = nc
        cp.hdr("PHASE B and C'  production beta and its check, {} cells".format(len(ncell)))
        args = [("B|{}|{}|0".format(cid, ncell[cid]), ("B", cmap[cid], ncell[cid], 0, K_PROD))
                for cid in sorted(ncell)]
        run_pool(pool, task_cal, args, out, store, "B")
        args = []
        for cid in sorted(ncell):
            r = store.get("B|{}|{}|0".format(cid, ncell[cid]))
            if r is None or r["end"] != "ok":
                continue
            c, ns = cmap[cid], L_REF[status[cid][1]]
            for rep in PRODCHECK_REPS:
                args.append((tid_ref("Q", c, ns, rep), ("Q", c, ns, rep, [float(r["beta_solved"])])))
        run_pool(pool, task_ref, args, out, store, "C'")
        for cid in sorted(ncell):
            c, ns = cmap[cid], L_REF[status[cid][1]]
            vals = []
            for rep in PRODCHECK_REPS:
                r = store.get(tid_ref("Q", c, ns, rep))
                if r is not None and r["end"] == "ok":
                    vals.append(floats(r["tau_hat"])[0])
            if len(vals) == REPS and abs(median(vals) / c[4] - 1.0) > C6_MAX:
                case_b.append(cid)

        # S, the solves
        solves = [(cid, L_REF[status[cid][1]], "b") for cid in case_b] + \
                 [(cid, L_REF[-1], "a") for cid in status if status[cid][0] == "case_a"]
        cp.hdr("PHASE S  case (a) and (b) solves, {} cells".format(len(solves)))
        held = [(cid, n, k) for cid, n, k in solves if n <= HELD_CAP_VALUES]
        for cid, n, k in solves:
            if n > HELD_CAP_VALUES:
                row = {"tid": "W|{}|{}".format(cid, n), "phase": "W", "cell": cid, "n": n,
                       "status": "streamed solve pending, laptop (case {})".format(k), "end": "ok"}
                if row["tid"] not in store:
                    out.write(row)
                    store[row["tid"]] = row
                print("  {:<48} case ({}) at n {}: streamed solve pending, laptop".format(cid, k, n))
        args = [("S|{}|{}|0".format(cid, n), ("S", cmap[cid], n, 0, K_SOLVE)) for cid, n, k in held]
        run_pool(pool, task_cal, args, out, store, "S")
        args = []
        for cid, n, k in held:
            r = store.get("S|{}|{}|0".format(cid, n))
            if r is None or r["end"] != "ok":
                continue
            for rep in range(REPS):
                args.append((tid_ref("E", cmap[cid], n, rep),
                             ("E", cmap[cid], n, rep, [float(r["beta_solved"]), badq[cid]])))
        run_pool(pool, task_ref, args, out, store, "S-eval")
        for cid, n, k in held:
            c = cmap[cid]
            for rep in range(REPS):
                e = store.get(tid_ref("E", c, n, rep))
                cl = store.get(tid_ref("C", c, n, rep))
                if e is not None and cl is not None and e["end"] == "ok" and cl["end"] == "ok":
                    if e["tau_hat"].split(";")[-1] != cl["tau_hat"].split(";")[0]:
                        fail3.append("R1 " + cid)
        for r in store.values():
            if r.get("e1") == "FAIL":
                fail3.append("E1 " + r["tid"])
    finally:
        pool.close()
        pool.join()
    return sorted(set(fail3))


# --------------------------------------------------------------------------
# laptop mode: the streamed bisection (D5, D5a, E2)
# --------------------------------------------------------------------------

def chunk_task(a):
    c, key, ci, m, betas = a
    return chunk_terms(f_chunk(c, key, ci, m), betas)


def streamed_log_ess(pool, c, key, n, betas):
    per = pool.map(chunk_task, [(c, key, ci, m, betas) for ci, m in chunks_of(n)], chunksize=1)
    return [r[0] for r in combine_terms(per, len(betas))]


def streamed_bisect(pool, c, key, n, tau, steps_out, store_steps, label):
    """beta_on_ensemble's bracket, step count and comparison, with the streamed
    log-ESS. Each step is written as a row; earlier rows resume it."""
    goal = math.log(tau * n)
    lo, hi = BIS_LO, BIS_HI
    for s in range(BIS_STEPS):
        tid = "{}|{}|{}|{}".format(label, cell_id(c), n, s)
        r = store_steps.get(tid)
        if r is not None and r["end"] == "ok":
            lo, hi = float(r["lo"]), float(r["hi"])
            continue
        mid = math.sqrt(lo * hi)
        le = streamed_log_ess(pool, c, key, n, [mid])[0]
        if le > goal:
            lo = mid
        else:
            hi = mid
        row = {"tid": tid, "cell": cell_id(c), "n": n, "step": s, "lo": repr(lo), "hi": repr(hi),
               "mid": repr(mid), "log_ess": repr(le), "goal": repr(goal), "end": "ok"}
        steps_out.write(row)
        store_steps[tid] = row
    return math.sqrt(lo * hi)


def streamed_run(a, pending, out, steps_out, store, store_steps):
    pool = Pool(processes=a.workers)
    try:
        for cid, n in pending:
            c = cell_from_id(cid)
            cp.hdr("STREAMED SOLVE  {}  n {}".format(cid, n))
            k1 = key_of(K_SOLVE, c, L_REF[0], 0)
            heldv = values_held(c, k1, L_REF[0])
            b_held, _ = EC.beta_on_ensemble(heldv, c[4], L_REF[0])
            del heldv
            b_str = streamed_bisect(pool, c, k1, L_REF[0], c[4], steps_out, store_steps, "T2")
            rel = abs(b_str / b_held - 1.0)
            e2 = rel <= E2_TOL
            row = {"tid": "E2|{}".format(cid), "phase": "E2", "cell": cid, "n": L_REF[0],
                   "betas": jl([b_held, b_str]), "status": "E2 {} ({:.2e})".format("PASS" if e2 else "FAIL", rel),
                   "end": "ok"}
            if row["tid"] not in store:
                out.write(row)
                store[row["tid"]] = row
            print("  E2 {}  held {!r}  streamed {!r}  rel {:.2e}".format("PASS" if e2 else "FAIL", b_held, b_str, rel))
            if not e2:
                continue
            kn = key_of(K_SOLVE, c, n, 0)
            bs = streamed_bisect(pool, c, kn, n, c[4], steps_out, store_steps, "T")
            row = {"tid": "S|{}|{}|0".format(cid, n), "phase": "S", "cell": cid, "key": key_str(kn),
                   "n": n, "rep": 0, "beta_solved": repr(bs), "status": "streamed", "end": "ok"}
            if row["tid"] not in store:
                out.write(row)
                store[row["tid"]] = row
            # evaluate on the six kind-32 replicates of size n, with beta_adq for R1
            badq = None
            for r in store.values():
                if r["phase"] == "C" and r["cell"] == cid and r["end"] == "ok":
                    badq = floats(r["betas"])[0]
                    break
            bl = [bs] + ([badq] if badq is not None else [])
            for rep in range(REPS):
                tid = tid_ref("E", c, n, rep)
                if tid in store and store[tid]["end"] == "ok":
                    continue
                t0 = time.time()
                kr = key_of(K_REF, c, n, rep)
                les = streamed_log_ess(pool, c, kr, n, bl)
                er = {"tid": tid, "phase": "E", "cell": cid, "key": key_str(kr), "n": n, "rep": rep,
                      "betas": jl(bl), "log_ess": jl(les), "tau_hat": jl([tau_of(x, n) for x in les]),
                      "e1": "not applied", "wall_s": "{:.3f}".format(time.time() - t0), "end": "ok"}
                out.write(er)
                store[tid] = er
                print("  eval rep {}  tau_hat {}".format(rep, er["tau_hat"]))
    finally:
        pool.close()
        pool.join()


# --------------------------------------------------------------------------
# finalize
# --------------------------------------------------------------------------

def finalize(rows, cells, outdir):
    cp.hdr("FINALIZE  {} task rows, {} cells".format(len(rows), len(cells)))
    st = dict((r["tid"], r) for r in rows)

    def ok(t):
        r = st.get(t)
        return r if (r is not None and r["end"] == "ok") else None

    out = []
    for c in cells:
        cid = cell_id(c)
        rec = {"cell": cid, "module": c[0], "objective": c[1], "d": c[2], "law": c[3], "tau0": repr(c[4])}
        bl = {}
        for N in L_CAL:
            rr = [ok("A|{}|{}|{}".format(cid, N, rep)) for rep in range(R_CAL)]
            if any(r is None for r in rr):
                bl = None
                break
            bl[N] = [float(r["beta_solved"]) for r in rr]
        if bl is None:
            rec["label"] = "incomplete (phase A)"
            out.append(rec)
            continue
        badq = median(bl[L_CAL[-1]])
        rec["beta_adq"] = repr(badq)
        flags = []
        meds, nstar, top = {}, None, None
        for i, n in enumerate(L_REF):
            s = rung_stats(st, "C", c, n)
            if s is None:
                continue
            meds[i] = s
            top = i
        for i in sorted(meds):
            if i + 1 in meds:
                c5 = meds[i][1] / meds[i][0] <= C5M_MAX
                d1 = abs(meds[i][0] - meds[i + 1][0]) / meds[i + 1][0] <= D1_MAX
                if c5 and d1:
                    nstar = i
                    break
        rec["rungs"] = ";".join(str(L_REF[i]) for i in sorted(meds))
        if any(r.get("e1") == "FAIL" for r in rows if r["cell"] == cid):
            flags.append("E1 FAIL")
        label, beta, prov, tref, rng = None, None, "", None, None
        if nstar is not None:
            ns = L_REF[nstar]
            rec["n_star"] = ns
            rec["C5m"] = "{:.6f}".format(meds[nstar][1] / meds[nstar][0])
            rec["D1"] = "{:.6f}".format(abs(meds[nstar][0] - meds[nstar + 1][0]) / meds[nstar + 1][0])
            pr = [ok(tid_ref("P", c, ns, rep)) for rep in range(REPS)]
            ncell = None
            if all(r is not None for r in pr):
                taus = [floats(r["tau_hat"]) for r in pr]
                if [r["tau_hat"].split(";")[-1] for r in pr] != [st[tid_ref("C", c, ns, rep)]["tau_hat"].split(";")[0] for rep in range(REPS)]:
                    flags.append("R1 FAIL")
                for li, N in enumerate(L_CAL):
                    devs = [abs(median([t[li * R_CAL + j] for t in taus]) / c[4] - 1.0) for j in range(R_CAL)]
                    rec["C1_" + str(N)] = "{:.6f}".format(max(devs))
                    if ncell is None and max(devs) <= C1_MAX:
                        ncell = N
            else:
                flags.append("C1 pass incomplete")
            rec["N_cell"] = ncell if ncell is not None else ""
            if ncell is not None:
                b = ok("B|{}|{}|0".format(cid, ncell))
                q = [ok(tid_ref("Q", c, ns, rep)) for rep in PRODCHECK_REPS]
                if b is not None and all(r is not None for r in q):
                    vals = [floats(r["tau_hat"])[0] for r in q]
                    dev = abs(median(vals) / c[4] - 1.0)
                    rec["C6"] = "{:.6f}".format(dev)
                    if dev <= C6_MAX:
                        label, beta, prov = "target", float(b["beta_solved"]), "calibration N_cell {}".format(ncell)
                        tref, rng = median(vals), max(vals) - min(vals)
                else:
                    flags.append("B or C' incomplete")
            nsolve, case = ns, "b"
        elif top is not None and top == len(L_REF) - 1:
            nsolve, case = L_REF[-1], "a"
        else:
            rec["label"] = "unresolved, continue at rung {}".format(L_REF[top + 1] if top is not None and top + 1 < len(L_REF) else "?")
            rec["flags"] = ";".join(flags)
            out.append(rec)
            continue
        if label is None:
            s = ok("S|{}|{}|0".format(cid, nsolve))
            ev = [ok(tid_ref("E", c, nsolve, rep)) for rep in range(REPS)]
            if s is None or any(r is None for r in ev):
                label = "pending (case {}, solve at n {})".format(case, nsolve)
            else:
                vals = [floats(r["tau_hat"])[0] for r in ev]
                tref, rng = median(vals), max(vals) - min(vals)
                beta = float(s["beta_solved"])
                dev = abs(tref / c[4] - 1.0)
                rec["case_dev"] = "{:.6f}".format(dev)
                prov = "reference-solved n {} (case {}{})".format(nsolve, case,
                                                                 ", streamed" if s.get("status") == "streamed" else "")
                label = "target" if (case == "b" and dev <= C6_MAX) else "beta"
                cl = [ok(tid_ref("C", c, nsolve, rep)) for rep in range(REPS)]
                if all(r is not None for r in cl) and len(floats(ev[0]["betas"])) > 1:
                    if [r["tau_hat"].split(";")[-1] for r in ev] != [r["tau_hat"].split(";")[0] for r in cl]:
                        flags.append("R1 FAIL")
        rec.update({"label": label, "beta": "" if beta is None else repr(beta), "provenance": prov,
                    "tau_ref": "" if tref is None else repr(tref),
                    "range": "" if rng is None else repr(rng),
                    "exact_tau": "" if beta is None or exact_tau(c, beta) is None else repr(exact_tau(c, beta)),
                    "flags": ";".join(flags)})
        out.append(rec)
    cols = ["cell", "module", "objective", "d", "law", "tau0", "label", "beta", "provenance", "tau_ref",
            "range", "exact_tau", "beta_adq", "rungs", "n_star", "C5m", "D1"] + \
        ["C1_" + str(N) for N in L_CAL] + ["N_cell", "C6", "case_dev", "flags"]
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
    flagged = [rec for rec in out if rec.get("flags")]
    for rec in flagged:
        print("  FLAG {}: {}".format(rec["cell"], rec["flags"]))
    return 3 if any("E1" in r.get("flags", "") or "R1" in r.get("flags", "") for r in flagged) else 0


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
    p.add_argument("--start-rung", type=int, default=0)
    p.add_argument("--max-rung", type=int, default=len(L_REF) - 1)
    p.add_argument("--plan", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--throughput", default=None)
    p.add_argument("--resume-from", default="")
    p.add_argument("--streamed-solve", default="")
    p.add_argument("--finalize", default="")
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    a = p.parse_args()
    rows = CALROWS if a.rows is None else [r for r in a.rows.split(",") if r]
    for r in rows:
        if r not in ROWMOD:
            sys.stderr.write("setup error: {} is not a calibrated row\n".format(r))
            return 2
    if not (0 <= a.start_rung <= a.max_rung < len(L_REF)) or not (0 <= a.shard < a.nshards) or a.workers < 1:
        sys.stderr.write("setup error: rung, shard or worker arguments out of range\n")
        return 2
    mode = ("finalize" if a.finalize else "streamed" if a.streamed_solve else
            "plan" if a.plan else "smoke" if a.smoke else "full")
    me = cp.sha256_file(os.path.abspath(__file__))
    cps = cp.sha256_file(os.path.abspath(cp.__file__))

    print("=" * 96)
    print("CBO-GAP calprec2 -- calprec v2: one fixed beta per calibration cell, through each row's module")
    print("=" * 96)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {}".format(
        platform.platform(), platform.machine(), os.cpu_count(), a.workers))
    print("  threads  " + "  ".join("{}={}".format(v, os.environ.get(v)) for v in cp.THREAD_VARS))
    print("  archive  {}".format(cp.ARCH))
    print("  script   sha256 {}".format(me))
    print("  costprobe2.py sha256 {}".format(cps))
    print("  mode     {}   rows {}   shard {} of {}   rungs {} to {}".format(
        mode, ",".join(rows), a.shard, a.nshards, L_REF[a.start_rung], L_REF[a.max_rung]))
    print("  L_CAL {}  R {}   L_REF {}  reps {}   chunk {}".format(L_CAL, R_CAL, L_REF, REPS, CHUNK))
    print("  C5m <= {}  D1 <= {}  C1 <= {}  C6 <= {}  E1 <= {:g}  E2 <= {:g}  RSS <= {:.0f} MB  held cap {} values".format(
        C5M_MAX, D1_MAX, C1_MAX, C6_MAX, E1_TOL, E2_TOL, RSS_BUDGET_MB, HELD_CAP_VALUES))
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
              ["start_rung", a.start_rung], ["max_rung", a.max_rung], ["workers", a.workers],
              ["python", platform.python_version()], ["numpy", np.__version__]]

    if mode == "finalize":
        _p, trows, _s = read_folders([x for x in a.finalize.split(",") if x], ["script_sha256", "rows"])
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        outdir = os.path.join(OUTROOT, "calprec2-finalize-" + stamp)
        os.makedirs(outdir)
        fcells = sorted(set(r["cell"] for r in trows if r["phase"] == "A"))
        code = finalize(trows, [cell_from_id(x) for x in fcells], outdir)
        print("\nfiles  {}".format(outdir))
        return code

    thr = load_throughput(a.throughput) if a.throughput else None
    if thr is not None:
        lo, hi, miss = project(cells, thr, a.start_rung, a.max_rung)
        cp.hdr("G-CAP -- projection for this job")
        print("  lower bound {:.0f} s   upper bound {:.0f} s   at {} workers   ceiling {:.0f} s".format(
            lo / a.workers, hi / a.workers, a.workers, SHARD_CEIL_S))
        if miss:
            print("  {} cells have no throughput entry: {}".format(len(miss), ", ".join(miss[:5])))
    if mode == "plan":
        for c in cells:
            print("  {}   rows {}".format(cell_id(c), ",".join(serves[cell_id(c)])))
        print("\nPLAN MODE: no draws, nothing written.")
        return 0
    if mode == "full":
        if thr is None:
            sys.stderr.write("G-CAP: a full run needs --throughput <verified smoke folder>\n")
            return 2
        if miss or hi / a.workers > SHARD_CEIL_S:
            sys.stderr.write("G-CAP: projected upper bound {:.0f} s exceeds {:.0f} s, or cells lack "
                             "throughput; lower --max-rung or add shards\n".format(hi / a.workers, SHARD_CEIL_S))
            return 2

    store, store_steps = {}, {}
    if a.resume_from:
        mine = dict((k, str(v)) for k, v in params)
        _p, trows, srows = read_folders([x for x in a.resume_from.split(",") if x], list(mine.keys()))
        if _p and dict((k, _p[0].get(k)) for k in mine) != mine:
            sys.stderr.write("resume: parameters differ from this run's\n")
            return 2
        for r in trows:
            if r["end"] == "ok":
                store[r["tid"]] = r
        for r in srows:
            if r["end"] == "ok":
                store_steps[r["tid"]] = r
        print("  resume: {} completed tasks and {} steps taken from earlier folders".format(len(store), len(store_steps)))

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
        pool = Pool(processes=a.workers, maxtasksperchild=1)
        try:
            for i, row in enumerate(pool.imap_unordered(task_smoke, units, chunksize=1)):
                out.write(row)
                print("  [{}/{}] {}  {}".format(i + 1, len(units), row["cell"],
                                              row.get("error") or "t_draw {} t_beta {} t_solve {}".format(
                                                  row["t_draw"], row["t_beta"], row["t_solve"])))
                sys.stdout.flush()
        finally:
            pool.close()
            pool.join()
            out.close()
        print("\nSMOKE: unit costs only; not results.")
        return 0

    out = Out(os.path.join(outdir, "calprec2_tasks.csv"), TASK_COLS)
    if mode == "streamed":
        _p, trows, srows = read_folders([x for x in a.streamed_solve.split(",") if x], ["script_sha256"])
        for r in trows:
            if r["end"] == "ok":
                store.setdefault(r["tid"], r)
        pending = sorted(set((r["cell"], int(r["n"])) for r in trows if r["phase"] == "W"))
        steps_out = Out(os.path.join(outdir, "calprec2_steps.csv"), STEP_COLS)
        try:
            streamed_run(a, pending, out, steps_out, store, store_steps)
        finally:
            steps_out.close()
            out.close()
        print("\nfiles  {}".format(outdir))
        return 0

    try:
        fails = full_run(a, cells, out, store, outdir)
    finally:
        out.close()
    if fails:
        for f in fails:
            print("  FAIL {}".format(f))
        print("\nE1 or R1 FAILED; every row is written; exit 3")
        return 3
    print("\n" + "=" * 96)
    print("files  {}".format(outdir))
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
