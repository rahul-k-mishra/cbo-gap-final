"""
dtref.py  --  CBO-GAP: DTREF, the time-step refinement check (ledger N46;
CLAUDE.md rules 4 to 6, 17; Rahul approved the design 2026-11-03).
Nothing launches until C5 is done (Rahul, 2026-11-03).

WHAT THIS DOES, IN PLAIN LANGUAGE
---------------------------------
Every slope in the paper is fitted to the coupled error of the explicit
Euler-Maruyama scheme at dt = 0.01 on [0, T]. The cited theorems are about
the continuous-time dynamics (ledger O3, R5). This script re-runs the same
realizations at dt = 0.005 and dt = 0.0025, on the SAME Brownian path and
the SAME initial ensemble, so that a later analysis (dtref_analysis.py,
criterion fixed below) can say whether each reported slope and contrast is
stable under refinement. It writes per-realization E_J at every level. It
fits no slope and decides nothing about the science.

HOW, WITHOUT RETYPING THE DYNAMICS (rule 4)
  A realization is rerunlib.realise -> the archived module's
  one_realisation, called unmodified, exactly as rerun.py calls it. Three
  things are changed for the duration of one call, in the forked child
  that runs it, and restored afterwards:
  (1) rerunlib.DT is set to the level's step, so realise passes dt and
      K = round(T / dt) (rerunlib.K_of) to one_realisation;
  (2) numpy.random.default_rng is replaced for its FIRST call only. That
      call is one_realisation's "rng = np.random.default_rng(seed)"; the
      replacement asserts that it receives this task's SeedSequence object
      and returns a BridgeRNG wrapping the real generator built from it.
      Every later default_rng call gets the real function;
  (3) for the four modules whose initial ensemble comes from draw_initial
      (mechanism, visibility, control, regime), that module's global
      draw_initial is wrapped so that its return ends the initial phase.
  BridgeRNG has two phases.
  - INITIAL: every call is passed to the real generator unchanged (the
    X0 draw, and for draw_initial also its rng.random and second normal
    draw). It ends after draw_initial returns, or for the seven inline
    modules after the first standard_normal call ("X0 =
    rng.standard_normal((Jinf, d)) [+ shift]"). G-SRC below checks that
    one_realisation has exactly this shape.
  - LOOP: the only call allowed is standard_normal((Jinf, d)), once per
    step (the archived "dW = rng.standard_normal((Jinf, d)) * sq"). Any
    other call or shape raises, so the task ends as an error row, never
    silently. At level L (q = 2^L fine steps per coarse step) the wrapper
    draws, every q calls, ONE coarse normal Z from the real generator,
    exactly the draw the dt 0.01 run made at that step, and refines it L
    times by the Brownian bridge:
        a -> (a + U) / sqrt(2), (a - U) / sqrt(2),
    U standard normal from a bridge stream for that level. Each refined
    value is N(0, 1); the q fine increments xi_i sqrt(dt / q) sum to
    Z sqrt(dt) (check C). Level L uses bridge streams 1..L, each keyed
    by the trajectory key and the level number, so the dt 0.005 path is
    exactly the dt 0.0025 path coarse-grained by two, and both are the
    dt 0.01 path refined. At L = 0 the wrapper returns Z itself: the
    same object the archived call would have drawn.
  Diffusion is not in any key (rerunlib 5a), so the two arms of a paired
  cell share X0, the coarse path and the bridge, as they share them at
  dt 0.01.

LEVELS
  L  q  dt      K at T = 1   (T 0.5 and 2.0 in HORIZON scale K the same way)
  0  1  0.01    100          committed rerun rows; gate only
  1  2  0.005   200
  2  4  0.0025  400
  Not 0.002: 0.01 / 0.002 = 5 and 0.005 / 0.002 = 2.5, so 0.002 cannot
  share a dyadic Brownian path with 0.005 (N46).

SEEDS
  Trajectory: SeedSequence(rerunlib.traj_key(cell, owner, rep)), kind 81,
  the committed rerun row's own key, unchanged at every level (that is
  what makes the coarse path the committed one).
  Bridge stream of level l (l = 1, 2): SeedSequence((ENTROPY 20261016,
  101, owner index, rerunlib.coord_fields(cell), rep, l)). Kind 101 is
  used by no other script (in use: 1, 2, 4, 11, 12, 31 to 35, 41 to 43,
  51, 61 to 67, 71, 81, 83, 91, 92, 95 to 98). Worked example, CONC
  mechanism ackley d 2 centred tau_0 0.5 rep 0, level 2: (20261016, 101,
  3, 2, 0, 2, 0, 500000, 0, 0, 0, 50000, 1000000, 0, 0, 0, 2).

THE GATE  (--mode gate; Kaggle; must PASS before any run; Rahul,
2026-11-03: "If a module cannot pass it, say which and do not quietly fall
back." There is no fallback: a module that fails is reported by name and
run mode refuses every row that uses it.)
  Gate tasks: for each row in --rows (default all 21), for each (module,
  law, diffusion, arm, sub-arm) group, the rep 0 task of the cell with the
  smallest measured unit wall (ties: tid). Each is run four times:
  P0 plain rerunlib.realise at dt 0.01, no wrapper at all; W0 wrapped at
  L 0; W1 at L 1; W2 at L 2.
  A  (the decisive check; the wrapper changes nothing)
     A1  W0's row equals P0's row, string for string, in every column of
         rerun.REAL_COLS except env, wall_s, peak_rss_mb and pid.
     A2  W0's row equals the COMMITTED rerun row with the same tid (from
         --committed, verified manifests), in the same columns.
     A3  (diagnostic, not a gate) P0 equals the committed row. If A2 fails
         and A3 fails too, the image or platform changed the numbers, not
         the wrapper ("IMAGE"); if A2 fails and A3 passes, the wrapper did
         ("WRAPPER"). Either way the group FAILS.
     Worked example: E_80 "0.0123456789012345" in P0 and W0 and committed:
     A1, A2 pass. W0 "0.0123456789012346": A1 FAIL, A2 FAIL, A3 pass ->
     WRAPPER.
  B  (same start, same coarse path) W0, W1, W2 have the same x0_sha
     (sha256 of the initial ensemble, or of its normal draw for the inline
     modules), the same coarse_sha (sha256 over every coarse Z drawn in
     the loop, in order), the same n_init (calls passed through before
     the loop) and, where the module returns it, the same le0 string.
  C  (the bridge is a refinement) at W1 and W2: n_coarse = round(T /
     0.01), n_fine = round(T / dt), no other call in the loop, and
     bridge_err <= 1e-12, where bridge_err is the largest, over coarse
     steps, of max |sum_i xi_i sqrt(dt/q) - Z sqrt(dt)| / max |Z sqrt(dt)|.
     Worked example: q 2, Z 1.0, U 0.3: xi = 0.919239..., 0.494974...;
     their sum times sqrt(0.005) is 0.1 = Z sqrt(0.01) up to rounding
     (about 1e-17): pass.
  RSS  for each module, the rep 0 task of its largest-wall unit in --rows
     at L 2 (the most memory: q + 2 extra (J_inf, d) arrays), wrapped,
     with C. Peak RSS printed and written (rule 6); above --budget-mb /
     workers it is "G-RSS FAIL" and the module FAILS.
  A group PASSES iff A1, A2, B and C pass and every member ended ok. A
  module PASSES iff every one of its groups and its RSS task pass. The
  gate PASSES iff every module in --rows passes. Printed: one line per
  group and per module ("MODULE regimemap PASS (60 groups)" or "MODULE
  control FAIL: ADAPT|control|...|adaptive: A2 WRAPPER E_640"), then
  "GATE PASS" or "GATE FAIL". Written: dtref_gate.csv (one row per
  group and RSS task) and dtref_gate_verdict.csv (module verdicts, the
  overall verdict, python, numpy, script sha256).
  NULL RATE (A, B, C, RSS): deterministic comparisons of strings, hashes,
  counts and a rounding bound; none fires by chance (probability 0). A
  fixture with a planted one-ulp change in W0 must FAIL A1; one with a
  wrapper that skips a bridge level must FAIL C (pre-run checks).

RUN  (--mode run; Kaggle; one shard)
  Refused (exit 2) unless --gate names a verified gate folder whose
  verdict is GATE PASS, run on the same python and numpy as this job, with
  this script's sha256, covering every module of --rows.
  --rows must be given explicitly in run mode (the scope is fixed in the
  queue definition before launch, N46: every row the abstract quotes;
  Table 1 quotes no slope). Plan and gate default to all 21 rows.
  Tasks: every cell of --rows (rerun.tasks_for: owner rows only, every
  diffusion, every rep 0 .. M-1, the archived M), at L 1 and L 2. L 0 is
  not rerun: the gate's A proves W0 = the committed row. Task tid =
  "<rerun tid>|L<l>".
  Shards: est = the unit's measured costprobe2 wall x q (wall is
  proportional to K: each step is the same work; draw_initial and beta
  are per task and do not depend on dt). Longest-processing-time first:
  tasks in order (-est, tid), each to the least-loaded shard, ties to the
  lowest index. Worked example: ests 8, 6, 4, 4, 2 on two shards: 8 -> 0,
  6 -> 1, 4 -> 1 (6 < 8), 4 -> 0 (8 < 10), 2 -> 1 (10 < 12); loads 12
  and 12.
  T1  per-task timeout max(600 s, 5 x the largest est in the shard).
  STOP --stop-after, default min(36000, 43200 - T1 - 600); no task starts
      after it; exit 5; resume the shard.
  C   every run row carries bridge ("ok" or the failure) and bridge_err;
      any failure: exit 3 at the end.
  RS  resume (rule 17), --resume-from DIR[,DIR]: each folder only after
      its sha256.txt verifies; one dtref_params.csv and one
      dtref_real.csv; parameters other than the folder list equal this
      job's; a row counts only with end "ok"; a tid twice, or a tid not
      of this job, is exit 2. Printed per folder.
  NULL RATE (run): none is a statistical criterion; all deterministic.

PLAN  (--mode plan; laptop; writes nothing)
  G-SRC, the plan, the walls, task counts and task-seconds per row and
  level, the shard loads for --nshards, and the smallest shard count
  whose largest load is at most --target (default 10800 s). Every figure
  is labelled a lower bound (perfect scaling, costprobe2 walls).

G-SRC  (every mode) for each archived module the rows use, the source of
  one_realisation (inspect) must have, after whitespace normalisation:
  exactly one line containing "rng" of each of the forms
      rng = np.random.default_rng(seed)
      X0 = draw_initial(rng, ...)      [mechanism, visibility, control, regime]
      X0 = rng.standard_normal((Jinf, d))...   [the other seven]
      dW = rng.standard_normal((Jinf, d)) * sq
  no other line containing "rng" or "np.random", "sq = math.sqrt(dt)"
  once, and the dW line inside a "for _ in range(K):" loop. Any
  deviation: exit 2, naming the module. Deterministic; NULL RATE 0.

PRE-REGISTERED ANALYSIS  (dtref_analysis.py; to be written and its null
fixture run before any DTREF shard; fixed here 2026-11-03, N46)
  Estimand, per realization i of a cell arm: Delta_i(l) = gamma_i(L l) -
  gamma_i(L 0), the slope fitted exactly as rerun_analysis.py fits that
  row's slope (same window, same function), L 0 from the committed row,
  for l = 1, 2. The same per-realization difference for every contrast
  the abstract quotes, computed on the paired realizations.
  STABLE    the 95% percentile bootstrap interval (realizations resampled
            within the cell, paired across levels) of mean Delta lies
            inside (-0.01, +0.01);
  SHIFTED   it lies entirely outside [-0.01, +0.01];
  UNRESOLVED otherwise.
  delta = 0.01: a third of the smallest resolved effect the abstract
  reports (+0.0305), N46. Worked example: [-0.004, +0.007] STABLE;
  [+0.013, +0.021] SHIFTED; [-0.002, +0.015] UNRESOLVED.
  B-RUN (before any Delta is used): for every trajectory, its L1 and L2
  rows have equal x0_sha, coarse_sha and n_init, and equal le0 strings,
  and where the module returns le0 it equals the committed row's. A
  trajectory that fails is excluded and listed; the count per row is
  reported. Deterministic; NULL RATE 0.
  NULL RATE: under any true |Delta| >= 0.01, STABLE fires with probability
  at most 0.025 per cell arm (one-sided coverage of a 95% interval at the
  nearer bound; by construction, asymptotically in M). Counts per row; no
  family-wise claim. Null fixtures: synthetic rows with no dt effect, and
  with a planted shift of 0.02, through the whole analysis script.

OUTPUT (every file opened "x")
  <outdir>/dtref-<mode>-YYYYMMDD-HHMMSS[-s<S>of<K>]/
    dtref_params.csv        every parameter (checked on resume)
    dtref_real.csv          one row per task: tid, level, dt, K, every
                            rerun.REAL_COLS column (traj_tid is rerun's
                            tid), x0_sha, coarse_sha, n_init, n_coarse,
                            n_fine, bridge_err, bridge, rss_mb, rss_flag
    dtref_gate.csv          gate only
    dtref_gate_verdict.csv  gate only

EXIT CODES
  0 done (plan; gate PASS; run with every task done); 2 bad argument,
  input, manifest, G-SRC, gate folder or resume problem; 3 gate FAIL, or
  a bridge check failure in run; 4 errored or timed-out tasks; 5 stopped
  by --stop-after (resume this shard). Precedence: 3 and 4 over 5.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python -B scripts/dtref.py --mode plan --rows CONC,TAU8 --nshards 20
  on Kaggle, after C5 (kgrun by hand, rule 13, or the queue once rerunq
  knows dtref):
    --mode gate --workers 4
    --mode run --rows ROWS --gate runs/<gate folder> --shard S --nshards K --workers 4
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import hashlib                                                  # noqa: E402
import inspect                                                  # noqa: E402
import io                                                       # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import re                                                       # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cbopaths                                                 # noqa: E402
import rerunlib as rl                                           # noqa: E402
import rerun as RR                                              # noqa: E402
import calprec2 as C2                                           # noqa: E402

cp = rl.cp
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = cbopaths.output_root(REPO)
ENV = "python {} numpy {}".format(platform.python_version(), np.__version__)

DT0 = 0.01
LEVELS = (0, 1, 2)
RUN_LEVELS = (1, 2)
KIND_BRIDGE = 101
BRIDGE_TOL = 1e-12
BUDGET_MB = 12000.0
TARGET_S = 10800.0
TIMEOUT_FLOOR = 600.0
SKIP_COLS = ("env", "wall_s", "peak_rss_mb", "pid")
DRAW_INITIAL_MODULES = ("mechanism", "visibility", "control", "regime")
R2 = math.sqrt(0.5)

DEFAULT_PLAN = os.path.join(REPO, "runs", "rerun-plan-20261028-212945")
DEFAULT_TIMING = [os.path.join(REPO, "runs", x) for x in (
    "costprobe2-s0-kaggle-20261010-103952", "costprobe2-s1-kaggle-20261011-101343")]
DEFAULT_COMMITTED = [os.path.join(REPO, "runs", x) for x in (
    "rerun-arch-s0of4-a1-kaggle-20261024-020220", "rerun-arch-s1of4-a1-kaggle-20261024-133226",
    "rerun-arch-s2of4-a1-kaggle-20261024-160215", "rerun-arch-s3of4-a1-kaggle-20261024-200233",
    "rerun-cal-s0of2-a1-kaggle-20261025-003238", "rerun-cal-s1of2-a1-kaggle-20261025-050238",
    "rerun-cal3-s0of2-a1-kaggle-20261027-011714", "rerun-cal3-s1of2-a1-kaggle-20261027-043215",
    "rerun-onsetr-s0of10-a1-kaggle-20261029-024727", "rerun-onsetr-s1of10-a1-kaggle-20261029-054727",
    "rerun-onsetr-s2of10-a1-kaggle-20261029-084728", "rerun-onsetr-s3of10-a1-kaggle-20261029-121727",
    "rerun-onsetr-s4of10-a1-kaggle-20261029-154728", "rerun-onsetr-s5of10-a1-kaggle-20261029-191727",
    "rerun-onsetr-s6of10-a1-kaggle-20261029-223227", "rerun-onsetr-s7of10-a1-kaggle-20261030-020149",
    "rerun-onsetr-s8of10-a1-kaggle-20261030-040227", "rerun-onsetr-s9of10-a1-kaggle-20261030-061727")]

PARAMS_CSV = "dtref_params.csv"
ROWS_CSV = "dtref_real.csv"
GATE_CSV = "dtref_gate.csv"
VERDICT_CSV = "dtref_gate_verdict.csv"
EXTRA_COLS = ["x0_sha", "coarse_sha", "n_init", "n_coarse", "n_fine", "bridge_err", "bridge", "rss_mb",
              "rss_flag"]
COLS = (["tid", "phase", "level", "dt", "K_level", "traj_tid"] + [c for c in RR.REAL_COLS if c != "tid"]
        + EXTRA_COLS)
GATE_COLS = ["group", "module", "kind", "traj_tid", "A1", "A2", "A3", "A_diag", "B", "C", "rss_mb", "rss_flag",
             "verdict", "detail"]
RESUME_KEYS = ("mode", "rows", "shard", "nshards", "workers", "stop_after", "budget_mb", "script_sha256",
               "rerun_sha256", "rerunlib_sha256", "costprobe2_sha256", "calprec2_sha256", "plan", "plan_sha256",
               "timing", "gate", "python", "numpy")
TASK_FN = "dtref"


class Stop(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, code, msg)
        self.code, self.msg = code, msg


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "=" * 100)
    say(s)
    say("=" * 100)


def sha256_of(path):
    return rl.file_sha(path)


def base(x):
    return os.path.basename(x.rstrip("/"))


def verified(folder):
    try:
        return rl.verify_folder(folder)
    except SystemExit:
        raise Stop(2, "{} fails or lacks its sha256.txt".format(folder))


def one_file(folder, rels, name):
    hits = [r for r in rels if os.path.basename(r) == name]
    if len(hits) != 1:
        raise Stop(2, "{}: expected one {}, found {}".format(folder, name, len(hits)))
    return os.path.join(folder, hits[0])


def read_kv(path):
    with io.open(path, "r", newline="", encoding="utf-8") as fh:
        return dict((r[0], r[1]) for r in csv.reader(fh) if r)


def dt_of(level):
    return DT0 / (2 ** level)


def k_of(T, level):
    return int(round(float(T) / dt_of(level)))


# ----------------------------------------------------------------------
# G-SRC: the archived one_realisation has the shape the wrapper assumes
# ----------------------------------------------------------------------

def norm(line):
    return re.sub(r"\s+", " ", line.strip())


def src_check(module):
    """[] if one_realisation has the expected rng shape, else a list of reasons."""
    mod = cp.MODS[module]
    lines = [norm(x) for x in inspect.getsource(mod.one_realisation).splitlines()]
    raw = inspect.getsource(mod.one_realisation).splitlines()
    bad = []
    rng_lines = [x for x in lines if re.search(r"\brng\b", x) or "np.random" in x]
    want_rng = "rng = np.random.default_rng(seed)"
    want_dw = "dW = rng.standard_normal((Jinf, d)) * sq"
    if module in DRAW_INITIAL_MODULES:
        x0 = [x for x in rng_lines if re.match(r"X0 = draw_initial\(rng, ", x)]
    else:
        x0 = [x for x in rng_lines if x.startswith("X0 = rng.standard_normal((Jinf, d))")]
    if rng_lines.count(want_rng) != 1:
        bad.append("default_rng line x{}".format(rng_lines.count(want_rng)))
    if rng_lines.count(want_dw) != 1:
        bad.append("dW line x{}".format(rng_lines.count(want_dw)))
    if len(x0) != 1:
        bad.append("X0 line x{}".format(len(x0)))
    other = [x for x in rng_lines if x not in (want_rng, want_dw) and x not in x0]
    if other:
        bad.append("other rng lines: {}".format(other))
    if sum(1 for x in lines if x == "sq = math.sqrt(dt)") != 1:
        bad.append("sq = math.sqrt(dt) not found exactly once")
    if sum(1 for x in lines if "draw_initial" in x) != (1 if module in DRAW_INITIAL_MODULES else 0):
        bad.append("draw_initial used other than once in the X0 line")
    # the dW line must sit inside "for _ in range(K):" (indentation deeper than the for)
    idx_for = [i for i, x in enumerate(raw) if norm(x) == "for _ in range(K):"]
    idx_dw = [i for i, x in enumerate(raw) if norm(x) == want_dw]
    if len(idx_for) != 1 or len(idx_dw) != 1 or idx_dw[0] <= idx_for[0]:
        bad.append("dW line not after a single 'for _ in range(K):'")
    else:
        ind = lambda s: len(s) - len(s.lstrip(" "))             # noqa: E731
        if ind(raw[idx_dw[0]]) <= ind(raw[idx_for[0]]) or any(
                raw[j].strip() and ind(raw[j]) <= ind(raw[idx_for[0]]) for j in range(idx_for[0] + 1, idx_dw[0])):
            bad.append("dW line not in the body of the K loop")
    i_rng = [i for i, x in enumerate(lines) if x == want_rng]
    i_x0 = [i for i, x in enumerate(lines) if x in x0]
    if i_rng and i_x0 and idx_for and not (i_rng[0] < i_x0[0] < idx_for[0]):
        bad.append("order is not default_rng, X0, loop")
    return bad


def g_src(modules):
    hdr("G-SRC  archived one_realisation shape (the wrapper's assumption)")
    fails = []
    for m in sorted(modules):
        bad = src_check(m)
        say("  {:<12} {}".format(m, "PASS" if not bad else "FAIL: " + "; ".join(bad)))
        if bad:
            fails.append(m)
    if fails:
        raise Stop(2, "G-SRC: {} do not have the shape the wrapper assumes".format(", ".join(fails)))
    say("  G-SRC PASS  {} module(s)".format(len(modules)))


# ----------------------------------------------------------------------
# the wrapped generator
# ----------------------------------------------------------------------

class BridgeRNG(object):
    """Passes the initial draws through; in the loop serves bridge-refined
    increments built from one real coarse draw every q calls."""

    def __init__(self, real, level, shape, inline, bridge_gens, dt_coarse):
        self._real, self._level, self._shape, self._inline = real, level, tuple(shape), inline
        self._q = 2 ** level
        self._gens = bridge_gens
        self._sqc = math.sqrt(dt_coarse)
        self._sqf = math.sqrt(dt_coarse / self._q)
        self._loop = False
        self._queue = []
        self.n_init, self.n_coarse, self.n_fine = 0, 0, 0
        self.bridge_err = 0.0
        self.x0_sha = ""
        self._csha = hashlib.sha256()
        self.violation = ""

    # -- phase control
    def end_initial(self, X0):
        if self._loop:
            self.violation = "end_initial called twice"
            raise RuntimeError(self.violation)
        self.x0_sha = hashlib.sha256(np.ascontiguousarray(X0).tobytes()).hexdigest()[:32]
        self._loop = True

    def coarse_sha(self):
        return self._csha.hexdigest()[:32]

    # -- the only method the loop may call
    def standard_normal(self, *args, **kw):
        if not self._loop:
            out = self._real.standard_normal(*args, **kw)
            self.n_init += 1
            if self._inline:
                self.end_initial(out)
            return out
        if kw or len(args) != 1 or tuple(args[0]) != self._shape:
            self.violation = "loop call standard_normal{} {}".format(args, kw)
            raise RuntimeError(self.violation)
        if not self._queue:
            Z = self._real.standard_normal(self._shape)
            self.n_coarse += 1
            self._csha.update(np.ascontiguousarray(Z).tobytes())
            if self._level == 0:
                self._queue = [Z]
            else:
                arrs = [Z]
                for lev in range(1, self._level + 1):
                    nxt = []
                    for a in arrs:
                        U = self._gens[lev].standard_normal(self._shape)
                        nxt.append((a + U) * R2)
                        nxt.append((a - U) * R2)
                    arrs = nxt
                tot = arrs[0] * self._sqf
                for a in arrs[1:]:
                    tot = tot + a * self._sqf
                ref = Z * self._sqc
                scale = float(np.max(np.abs(ref))) or 1.0
                err = float(np.max(np.abs(tot - ref))) / scale
                del tot, ref
                if err > self.bridge_err:
                    self.bridge_err = err
                self._queue = arrs
        self.n_fine += 1
        return self._queue.pop(0)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if self.__dict__.get("_loop"):
            self.__dict__["violation"] = "loop call {}".format(name)
            raise RuntimeError("BridgeRNG: {} called in the loop".format(name))
        self.__dict__["n_init"] += 1
        return getattr(self.__dict__["_real"], name)


def bridge_key(c, owner, rep, lev):
    return (rl.ENTROPY, KIND_BRIDGE, rl.ROWS.index(owner)) + tuple(rl.coord_fields(c)) + (int(rep), int(lev))


def realise_level(c, df, seed, level, rep, owner, wrapped=True):
    """rerunlib.realise at the level's dt; wrapped=False is P0 (dt 0.01, untouched)."""
    if not wrapped:
        return rl.realise(c, df, c["beta"], c["sigma"][df], seed), None
    module = c["module"]
    mod = cp.MODS[module]
    real_default_rng = np.random.default_rng
    gens = dict((lev, real_default_rng(np.random.SeedSequence(list(bridge_key(c, owner, rep, lev)))))
                for lev in range(1, level + 1))
    box = {}

    def factory(*a, **kw):
        np.random.default_rng = real_default_rng
        if len(a) != 1 or kw or a[0] is not seed:
            raise RuntimeError("first default_rng call is not one_realisation's (seed object differs)")
        box["rng"] = BridgeRNG(real_default_rng(a[0]), level, (c["jinf"], c["d"]),
                               module not in DRAW_INITIAL_MODULES, gens, DT0)
        return box["rng"]

    old_dt = rl.DT
    old_di = getattr(mod, "draw_initial", None)
    try:
        rl.DT = dt_of(level)
        if module in DRAW_INITIAL_MODULES:
            def di(rng, *a, **kw):
                X = old_di(rng, *a, **kw)
                rng.end_initial(X)
                return X
            mod.draw_initial = di
        np.random.default_rng = factory
        res = rl.realise(c, df, c["beta"], c["sigma"][df], seed)
    finally:
        np.random.default_rng = real_default_rng
        rl.DT = old_dt
        if old_di is not None:
            mod.draw_initial = old_di
    return res, box.get("rng")


# ----------------------------------------------------------------------
# the task (a forked child of calprec2's Runner)
# ----------------------------------------------------------------------

def bridge_verdict(b, T, level):
    if b is None:
        return "no wrapper"
    if b.violation:
        return "FAIL " + b.violation
    probs = []
    if not b._loop:
        probs.append("initial phase never ended")
    if b.n_coarse != k_of(T, 0):
        probs.append("n_coarse {} != {}".format(b.n_coarse, k_of(T, 0)))
    if b.n_fine != k_of(T, level):
        probs.append("n_fine {} != {}".format(b.n_fine, k_of(T, level)))
    if b.bridge_err > BRIDGE_TOL:
        probs.append("bridge_err {!r} > {!r}".format(b.bridge_err, BRIDGE_TOL))
    return "ok" if not probs else "FAIL " + "; ".join(probs)


def task_dtref(t):
    tt = t["rt"]
    c, df, level = tt["cell"], tt["diff"], t["level"]
    o = {"tid": tt["tid"], "error": "", "end": "err", "E": {}, "extras": {}, "audit": None, "le0": None,
         "le_redraw": None, "F1": "", "wall": float("nan")}
    b = None
    try:
        seed = np.random.SeedSequence(list(tt["key"]))
        t0 = time.time()
        (E, extras, le0), b = realise_level(c, df, seed, level, tt["rep"], c["owner"], wrapped=t["wrapped"])
        o["wall"] = time.time() - t0
        o["E"], o["extras"], o["le0"] = E, extras, le0
        if c["row"] in rl.AUDIT_ROWS:
            ratios, ref, f1, le_rd = rl.audit_one(c, np.random.SeedSequence(list(tt["key"])), c["beta"], le0)
            o["audit"] = (ratios, ref)
            o["le_redraw"] = le_rd
            o["F1"] = "ok" if f1 else "F1 FAILED"
        o["end"] = "ok"
    except Exception as exc:                                     # noqa: BLE001 (an error row)
        o["error"] = "{}: {}".format(type(exc).__name__, exc)
    o["rss"] = C2.rss_mb()
    o["pid"] = os.getpid()
    vals = RR.real_row(tt, o)
    row = dict(zip(RR.REAL_COLS, [str(x) for x in vals]))
    row["traj_tid"] = row.pop("tid")
    row.update({"tid": t["tid"], "phase": t["phase"], "level": str(level), "dt": repr(dt_of(level)),
                "K_level": str(k_of(c["T"], level)), "rss_mb": "{:.1f}".format(o["rss"])})
    if b is not None:
        bv = bridge_verdict(b, c["T"], level)
        row.update({"x0_sha": b.x0_sha, "coarse_sha": b.coarse_sha(), "n_init": str(b.n_init),
                    "n_coarse": str(b.n_coarse), "n_fine": str(b.n_fine), "bridge_err": repr(b.bridge_err),
                    "bridge": bv})
    else:
        row["bridge"] = "plain (P0)"
    if o["end"] != "ok":
        row["end"] = "err"
    return row


C2.TASKS[TASK_FN] = task_dtref


# ----------------------------------------------------------------------
# inputs, tasks, shards
# ----------------------------------------------------------------------

def parse_rows(s):
    rows = [r for r in s.split(",") if r]
    bad = [r for r in rows if r not in rl.ROWS]
    if bad or not rows:
        raise Stop(2, "--rows: unknown or empty {}".format(bad))
    return sorted(set(rows), key=rl.ROWS.index)


def inputs(a):
    hdr("IN  plan, walls")
    try:
        params, cells, psha = RR.load_plan(os.path.abspath(a.plan))
        walls = RR.load_walls([os.path.abspath(x) for x in a.timing])
    except SystemExit:
        raise Stop(2, "IN: the plan or a timing folder was refused (message above)")
    say("  plan {} ({} cells, rerun_plan.csv sha256 {})".format(base(a.plan), len(cells), psha))
    say("  walls {} units from {}".format(len(walls), ",".join(base(x) for x in a.timing)))
    return cells, walls, psha


def traj_tasks(cells, rows):
    rts = RR.tasks_for(cells, rows)
    if len(set(t["tid"] for t in rts)) != len(rts):
        raise Stop(2, "K1: duplicate trajectory tids")
    return rts


def wall_of(walls, rt):
    u = RR.unit_of(rt)
    if u not in walls:
        raise Stop(2, "no measured wall for unit {}".format(u))
    return walls[u]


def ctuple(rt):
    c = rt["cell"]
    return (c["module"], c["obj"], c["d"], c["law"], float(c["tau"] or 0.0))


def mk(rt, level, phase, walls, wrapped=True, suffix=None):
    return {"tid": "{}|{}".format(rt["tid"], suffix or "L{}".format(level)), "phase": phase, "level": level,
            "wrapped": wrapped, "rt": rt, "c": ctuple(rt), "n": rt["cell"]["jinf"], "rep": rt["rep"],
            "est": wall_of(walls, rt) * (2 ** level), "row": rt["cell"]["row"], "module": rt["cell"]["module"]}


def run_tasks(rts, walls):
    return [mk(rt, lv, "L{}".format(lv), walls) for rt in rts for lv in RUN_LEVELS]


def assign(tasks, k):
    load = [0.0] * k
    out = [[] for _ in range(k)]
    for t in sorted(tasks, key=lambda t: (-t["est"], t["tid"])):
        s = min(range(k), key=lambda i: (load[i], i))
        out[s].append(t)
        load[s] += t["est"]
    return out, load


def group_of(rt):
    c = rt["cell"]
    return "{}|{}|{}|{}|{}|{}".format(c["row"], c["module"], c["law"], rt["diff"], c["arm"] or "-", c["subarm"])


def gate_tasks(rts, walls):
    groups = {}
    for rt in rts:
        if rt["rep"] != 0:
            continue
        g = group_of(rt)
        cand = (wall_of(walls, rt), rt["tid"])
        if g not in groups or cand < groups[g][0]:
            groups[g] = (cand, rt)
    tasks = []
    for g in sorted(groups):
        rt = groups[g][1]
        for lv, wr, sfx in ((0, False, "P0"), (0, True, "W0"), (1, True, "W1"), (2, True, "W2")):
            t = mk(rt, lv, "gate", walls, wrapped=wr, suffix=sfx)
            t["group"] = g
            tasks.append(t)
    big = {}
    for rt in rts:
        if rt["rep"] != 0:
            continue
        m = rt["cell"]["module"]
        cand = (-wall_of(walls, rt), rt["tid"])
        if m not in big or cand < big[m][0]:
            big[m] = (cand, rt)
    for m in sorted(big):
        t = mk(big[m][1], 2, "rss", walls, suffix="RSS")
        t["group"] = "RSS|" + m
        tasks.append(t)
    return tasks, sorted(groups)


# ----------------------------------------------------------------------
# committed rows (gate A2)
# ----------------------------------------------------------------------

def read_committed(folders, want):
    """{rerun tid: row dict} for the tids in want, from verified folders."""
    hdr("COMMITTED rerun rows (gate A2)")
    out = {}
    for f in folders:
        rels = verified(f)
        p = one_file(f, rels, "rerun_real.csv")
        n = 0
        with io.open(p, "r", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("end") != "ok" or r["tid"] not in want:
                    continue
                if r["tid"] in out:
                    raise Stop(2, "COMMITTED: tid {} complete in two folders".format(r["tid"]))
                out[r["tid"]] = r
                n += 1
        say("  {}: {} gate row(s)".format(base(f), n))
    say("  {} of {} gate trajectories found".format(len(out), len(want)))
    return out


def diff_cols(x, y):
    return [k for k in RR.REAL_COLS if k not in SKIP_COLS and k != "tid" and x.get(k, "") != y.get(k, "")]


def as_rerun(row):
    r = dict((k, row.get(k, "")) for k in RR.REAL_COLS)
    r["tid"] = row.get("traj_tid", "")
    return r


# ----------------------------------------------------------------------
# header, params, resume, execution
# ----------------------------------------------------------------------

def hashes():
    return [("script_sha256", "dtref.py", os.path.abspath(__file__)), ("rerun_sha256", "rerun.py", RR.__file__),
            ("rerunlib_sha256", "rerunlib.py", rl.__file__), ("costprobe2_sha256", "costprobe2.py", cp.__file__),
            ("calprec2_sha256", "calprec2.py", C2.__file__)]


def header(a, mode, rows):
    hdr("CBO-GAP dtref  (ledger N46: time-step refinement, DTREF)  mode {}".format(mode))
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    for _k, label, path in hashes():
        say("  {:<13} sha256 {}".format(label, sha256_of(path)))
    say("  mode     {}   shard {} of {}".format(mode, a.shard, a.nshards))
    say("  rows     {}".format(",".join(rows)))
    say("  plan     {}".format(base(a.plan)))
    say("  timing   {}".format(",".join(base(x) for x in a.timing)))
    say("  levels   " + "; ".join("L{} dt {!r} q {}".format(lv, dt_of(lv), 2 ** lv) for lv in LEVELS)
        + "   (run: L1, L2; gate: P0, W0, W1, W2)")
    say("  dynamics rerunlib.realise -> archived one_realisation, unmodified; rerunlib.DT set per level; "
        "generator wrapped (BridgeRNG)")
    say("  seeds    trajectory SeedSequence(rerunlib.traj_key), kind 81, unchanged at every level; bridge "
        "SeedSequence(({}, {}, owner, coord_fields, rep, level))".format(rl.ENTROPY, KIND_BRIDGE))
    say("  checks   gate A1 A2 (A3 diagnostic) B C RSS; run C; bridge tolerance {!r}".format(BRIDGE_TOL))
    say("  budget   {:.0f} MB for concurrent tasks".format(a.budget_mb))
    if a.gate:
        say("  gate     {}".format(base(a.gate)))


def params_rows(a, mode, rows, psha, stop):
    out = [["mode", mode], ["rows", ",".join(rows)], ["shard", str(a.shard)], ["nshards", str(a.nshards)],
           ["workers", str(a.workers)], ["stop_after", repr(float(stop))], ["budget_mb", repr(float(a.budget_mb))]]
    out += [[k, sha256_of(p)] for k, _l, p in hashes()]
    out += [["plan", base(a.plan)], ["plan_sha256", psha], ["timing", ",".join(base(x) for x in a.timing)],
            ["gate", base(a.gate) if a.gate else ""], ["committed", ",".join(base(x) for x in a.committed)],
            ["python", platform.python_version()], ["numpy", np.__version__],
            ["resume_from", a.resume_from or ""]]
    return out


def read_resume(folders, want, mine):
    hdr("RS  resume (CLAUDE.md rule 17)")
    store = {}
    for f in folders:
        rels = verified(f)
        pr = read_kv(one_file(f, rels, PARAMS_CSV))
        bad = sorted(k for k in want if pr.get(k) != want[k])
        if bad:
            raise Stop(2, "RS: {}: parameters differ from this job's in {} (rule 17)".format(f, bad))
        rows, nok = 0, 0
        with io.open(one_file(f, rels, ROWS_CSV), "r", newline="", encoding="utf-8") as fh:
            for x in csv.DictReader(fh):
                rows += 1
                if x["tid"] not in mine:
                    raise Stop(2, "RS: {}: task {} is not one of this job's".format(f, x["tid"]))
                if x.get("end") != "ok":
                    continue
                if x["tid"] in store:
                    raise Stop(2, "RS: task {} is complete in two folders (second: {})".format(x["tid"], f))
                store[x["tid"]] = x
                nok += 1
        say("  read {}: shard {} of {}, {} rows, {} complete".format(f, pr.get("shard"), pr.get("nshards"), rows,
                                                                       nok))
    say("  {} complete task(s) read; they are skipped".format(len(store)))
    return store


def new_outdir(mode, a):
    tag = "" if a.nshards == 1 else "-s{}of{}".format(a.shard, a.nshards)
    out = os.path.join(OUTROOT, "dtref-{}-{}{}".format(mode, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), tag))
    os.makedirs(out)
    return out


def gates_fork():
    sm = multiprocessing.get_start_method(allow_none=False)
    if sm != "fork":
        raise Stop(2, "G-FORK: start method {}, not fork".format(sm))
    say("  G-FORK PASS  start method fork")


def execute(a, mode, rows, psha, tasks, store_in=None):
    to = max(TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR * max(t["est"] for t in tasks))
    stop = a.stop_after if a.stop_after is not None else min(C2.STOP_AFTER_DEFAULT, C2.KAGGLE_CAP_S - to - 600.0)
    hdr("T1, STOP, G-STOP")
    say("  TIMEOUT_S {:.0f} s; --stop-after {:.0f} s{}; cap {:.0f} s".format(
        to, stop, " (auto)" if a.stop_after is None else "", C2.KAGGLE_CAP_S))
    if stop <= 0 or stop + to > C2.KAGGLE_CAP_S:
        raise Stop(2, "G-STOP: --stop-after + TIMEOUT_S exceeds the 12-hour cap")
    store = {}
    if a.resume_from:
        want = dict((k, v) for k, v in params_rows(a, mode, rows, psha, stop) if k in RESUME_KEYS)
        store = read_resume([os.path.abspath(x) for x in a.resume_from.split(",") if x], want,
                            set(t["tid"] for t in tasks))
    out = new_outdir(mode, a)
    with io.open(os.path.join(out, PARAMS_CSV), "x", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(params_rows(a, mode, rows, psha, stop))
    say("\n  run dir  {}".format(out))
    o = C2.Out(os.path.join(out, ROWS_CSV), COLS)
    C2.RSS_BUDGET_MB = a.budget_mb / a.workers
    runner = C2.Runner(a.workers, to, o, store, stop_after=stop)
    try:
        runner.run([(TASK_FN, t) for t in sorted(tasks, key=lambda t: (-t["est"], t["tid"]))], mode)
    finally:
        o.close()
    return out, runner


# ----------------------------------------------------------------------
# modes
# ----------------------------------------------------------------------

def mode_plan(a, rows):
    header(a, "plan", rows)
    g_src(set(c["module"] for c in rl_cells_of(rows)))
    cells, walls, _psha = inputs(a)
    rts = traj_tasks(cells, rows)
    tasks = run_tasks(rts, walls)
    hdr("TASKS per row and level (task-seconds: costprobe2 unit wall x q; a lower bound, perfect scaling)")
    tot = 0.0
    for r in rows:
        for lv in RUN_LEVELS:
            ts = [t for t in tasks if t["row"] == r and t["level"] == lv]
            s = sum(t["est"] for t in ts)
            tot += s
            say("  {:<10} L{}  tasks {:>6}  task-seconds {:>12.0f}".format(r, lv, len(ts), s))
    say("  total     tasks {:>6}  task-seconds {:>12.0f}  ({} worker(s): {:.0f} s under perfect scaling)".format(
        len(tasks), tot, a.workers, tot / a.workers))
    gts, groups = gate_tasks(rts, walls)
    say("\n  gate: {} groups, {} tasks, task-seconds {:.0f}".format(len(groups), len(gts),
                                                                   sum(t["est"] for t in gts)))
    hdr("SHARDS  (load = task-seconds / workers; target {:.0f} s)".format(a.target))
    pick = None
    for k in range(1, a.kmax + 1):
        if max(assign(tasks, k)[1]) / a.workers <= a.target:
            pick = k
            break
    say("  smallest shard count at the target: {}".format(pick))
    sh, loads = assign(tasks, a.nshards)
    for i in range(a.nshards):
        say("    shard {:>3}: {:>5} tasks, load {:>8.0f} s".format(i, len(sh[i]), loads[i] / a.workers))
    hdr("dtref.py plan done, exit 0  (nothing written)")
    return 0


def rl_cells_of(rows):
    out = []
    for r in rows:
        out.extend(rl.cells_of(r))
    return out


def judge_gate(rows_by_tid, gts, committed, budget):
    by_group = {}
    for t in gts:
        by_group.setdefault(t["group"], []).append(t)
    lines, verdicts = [], {}
    for g in sorted(by_group):
        ts = by_group[g]
        m = ts[0]["module"]
        got = dict((t["tid"].rsplit("|", 1)[1], rows_by_tid.get(t["tid"])) for t in ts)
        ttid = ts[0]["rt"]["tid"]
        res = {"group": g, "module": m, "traj_tid": ttid, "A1": "", "A2": "", "A3": "", "A_diag": "", "B": "",
               "C": "", "rss_mb": "", "rss_flag": "", "detail": ""}
        det = []
        if any(v is None or v.get("end") != "ok" for v in got.values()):
            det.append("member missing or errored: " + ",".join(sorted(k for k, v in got.items()
                                                                      if v is None or v.get("end") != "ok")))
        if g.startswith("RSS|"):
            res["kind"] = "rss"
            r = got.get("RSS")
            if r is not None and r.get("end") == "ok":
                res["rss_mb"] = r.get("rss_mb", "")
                res["C"] = "PASS" if r.get("bridge") == "ok" else "FAIL"
                if res["C"] != "PASS":
                    det.append("C: " + r.get("bridge", ""))
                try:
                    over = float(r.get("rss_mb") or "nan") > budget
                except ValueError:
                    over = True
                res["rss_flag"] = "G-RSS FAIL" if over else ""
                if over:
                    det.append("G-RSS FAIL")
        else:
            res["kind"] = "group"
            P0, W0, W1, W2 = got.get("P0"), got.get("W0"), got.get("W1"), got.get("W2")
            com = committed.get(ttid)
            if P0 and W0:
                d1 = diff_cols(as_rerun(W0), as_rerun(P0))
                res["A1"] = "PASS" if not d1 else "FAIL"
                if d1:
                    det.append("A1 W0 != P0 in " + ",".join(d1[:8]))
            if W0:
                if com is None:
                    res["A2"] = "FAIL"
                    det.append("A2 no committed row")
                else:
                    d2 = diff_cols(as_rerun(W0), com)
                    res["A2"] = "PASS" if not d2 else "FAIL"
                    if d2:
                        det.append("A2 W0 != committed in " + ",".join(d2[:8]))
            if P0 and com is not None:
                d3 = diff_cols(as_rerun(P0), com)
                res["A3"] = "PASS" if not d3 else "FAIL"
            if res["A2"] == "FAIL":
                res["A_diag"] = "IMAGE" if res["A3"] == "FAIL" else ("WRAPPER" if res["A3"] == "PASS" else "?")
            ws = [x for x in (W0, W1, W2) if x is not None]
            if len(ws) == 3:
                bprob = []
                for f in ("x0_sha", "coarse_sha", "n_init", "le0"):
                    vals = set(x.get(f, "") for x in ws)
                    if len(vals) != 1 or (f != "le0" and vals == {""}):
                        bprob.append(f)
                res["B"] = "PASS" if not bprob else "FAIL"
                if bprob:
                    det.append("B differs in " + ",".join(bprob))
                cprob = [x.get("bridge", "") for x in ws if x.get("bridge") != "ok"]
                res["C"] = "PASS" if not cprob else "FAIL"
                if cprob:
                    det.append("C " + " | ".join(cprob))
        ok = not det and all(res[k] in ("", "PASS") for k in ("A1", "A2", "B", "C"))
        if res["kind"] == "group" and not all(res[k] == "PASS" for k in ("A1", "A2", "B", "C")):
            ok = False
        if res["kind"] == "rss" and res["C"] != "PASS":
            ok = False
        res["verdict"] = "PASS" if ok else "FAIL"
        res["detail"] = "; ".join(det)
        lines.append(res)
        verdicts.setdefault(m, []).append((g, res))
    return lines, verdicts


def mode_gate(a, rows):
    header(a, "gate", rows)
    hdr("G-FORK, G-SRC")
    gates_fork()
    g_src(set(c["module"] for c in rl_cells_of(rows)))
    cells, walls, psha = inputs(a)
    rts = traj_tasks(cells, rows)
    gts, groups = gate_tasks(rts, walls)
    say("  gate: {} groups x (P0, W0, W1, W2) + {} RSS task(s) = {} tasks".format(
        len(groups), len(gts) - 4 * len(groups), len(gts)))
    committed = read_committed([os.path.abspath(x) for x in a.committed],
                               set(t["rt"]["tid"] for t in gts if t["phase"] == "gate"))
    out, runner = execute(a, "gate", rows, psha, gts)
    lines, verdicts = judge_gate(runner.store, gts, committed, a.budget_mb / a.workers)
    hdr("GATE  per group (A1 W0=P0, A2 W0=committed, A3 P0=committed [diagnostic], B, C) and per module")
    for r in lines:
        say("  {:<4} {:<70} A1 {:<4} A2 {:<4} A3 {:<4} {:<7} B {:<4} C {:<4} {}".format(
            r["verdict"], r["group"][:70], r["A1"], r["A2"], r["A3"], r["A_diag"], r["B"], r["C"],
            (r["rss_mb"] + " MB " + r["rss_flag"]) if r["kind"] == "rss" else r["detail"]))
    mods = []
    for m in sorted(verdicts):
        fails = [(g, r) for g, r in verdicts[m] if r["verdict"] != "PASS"]
        if fails:
            g, r = fails[0]
            say("MODULE {} FAIL: {} of {} group(s); first {}: {}".format(m, len(fails), len(verdicts[m]), g,
                                                                       r["detail"] or r["A_diag"]))
        else:
            say("MODULE {} PASS ({} group(s) incl. RSS)".format(m, len(verdicts[m])))
        mods.append([m, "FAIL" if fails else "PASS", str(len(verdicts[m])), str(len(fails))])
    allmods = set(c["module"] for c in rl_cells_of(rows))
    missing = sorted(allmods - set(verdicts))
    if missing:
        say("MODULES WITHOUT A GATE RESULT: {}".format(", ".join(missing)))
    passed = not missing and all(x[1] == "PASS" for x in mods) and runner.stopped is None
    with io.open(os.path.join(out, GATE_CSV), "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=GATE_COLS, extrasaction="ignore")
        w.writeheader()
        for r in lines:
            w.writerow(r)
    with io.open(os.path.join(out, VERDICT_CSV), "x", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["module", "verdict", "groups", "failed"])
        w.writerows(mods)
        w.writerow(["GATE", "PASS" if passed else "FAIL", "", ""])
        w.writerow(["rows", ",".join(rows), "", ""])
        w.writerow(["python", platform.python_version(), "", ""])
        w.writerow(["numpy", np.__version__, "", ""])
        w.writerow(["script_sha256", sha256_of(os.path.abspath(__file__)), "", ""])
    say("\nGATE {}".format("PASS" if passed else "FAIL"))
    say("files  {}".format(out))
    if runner.stopped is not None:
        say("the gate was stopped by --stop-after; rerun it whole")
    return 0 if passed else 3


def check_gate_folder(a, rows):
    hdr("GATE FOLDER (run is refused without a passing gate)")
    if not a.gate:
        raise Stop(2, "run needs --gate <gate folder>")
    rels = verified(os.path.abspath(a.gate))
    vt = {}
    with io.open(one_file(a.gate, rels, VERDICT_CSV), "r", newline="", encoding="utf-8") as fh:
        for r in csv.reader(fh):
            if r and r[0] != "module":
                vt[r[0]] = r[1]
    probs = []
    if vt.get("GATE") != "PASS":
        probs.append("GATE is {!r}".format(vt.get("GATE")))
    for k, v in (("python", platform.python_version()), ("numpy", np.__version__),
                 ("script_sha256", sha256_of(os.path.abspath(__file__)))):
        if vt.get(k) != v:
            probs.append("{}: gate {!r}, this job {!r}".format(k, vt.get(k), v))
    for m in sorted(set(c["module"] for c in rl_cells_of(rows))):
        if vt.get(m) != "PASS":
            probs.append("module {} is {!r} in the gate".format(m, vt.get(m)))
    if probs:
        for p in probs:
            say("  " + p)
        raise Stop(2, "the gate folder does not cover this run")
    say("  gate {} PASS for every module of {}".format(base(a.gate), ",".join(rows)))


def mode_run(a, rows):
    header(a, "run", rows)
    hdr("G-FORK, G-SRC")
    gates_fork()
    g_src(set(c["module"] for c in rl_cells_of(rows)))
    check_gate_folder(a, rows)
    cells, walls, psha = inputs(a)
    rts = traj_tasks(cells, rows)
    sh, loads = assign(run_tasks(rts, walls), a.nshards)
    mine = sh[a.shard]
    say("  shard {} of {}: {} tasks, load {:.0f} s at {} workers (lower bound)".format(
        a.shard, a.nshards, len(mine), loads[a.shard] / a.workers, a.workers))
    out, runner = execute(a, "run", rows, psha, mine)
    done = [r for r in runner.store.values() if r.get("end") == "ok"]
    cbad = sum(1 for r in done if r.get("bridge") != "ok")
    say("\n" + "=" * 100)
    say("tasks run by this job: {}   complete, this job and resumed: {} of {}".format(runner.ran, len(done),
                                                                                    len(mine)))
    say("largest per-task peak RSS {:.1f} MB".format(max([float(r["rss_mb"]) for r in done] or [float("nan")])))
    say("bridge check failures (C): {}".format(cbad))
    say("errored or timed-out tasks: {}".format(runner.errors))
    say("STOPPED by --stop-after; resume this shard" if runner.stopped else "not stopped: every task ran")
    say("files  {}".format(out))
    code = 5 if runner.stopped else 0
    if cbad:
        code = 3
    if runner.errors:
        code = 4
    return code


def main():
    ap = argparse.ArgumentParser(description="DTREF: time-step refinement check (ledger N46)")
    ap.add_argument("--mode", choices=("plan", "gate", "run"), required=True)
    ap.add_argument("--rows", default="")
    ap.add_argument("--plan", default=DEFAULT_PLAN)
    ap.add_argument("--timing", default=",".join(DEFAULT_TIMING))
    ap.add_argument("--committed", default=",".join(DEFAULT_COMMITTED))
    ap.add_argument("--gate", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-mb", type=float, default=BUDGET_MB)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--target", type=float, default=TARGET_S)
    ap.add_argument("--kmax", type=int, default=400)
    ap.add_argument("--stop-after", type=float, default=None)
    ap.add_argument("--resume-from", default="")
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    a.timing = [x for x in a.timing.split(",") if x]
    a.committed = [x for x in a.committed.split(",") if x]
    if not a.rows:
        if a.mode == "run":
            raise Stop(2, "run needs an explicit --rows (the scope, N46)")
        a.rows = ",".join(rl.ROWS)
    rows = parse_rows(a.rows)
    if a.workers < 1 or a.budget_mb <= 0 or a.nshards < 1 or not (0 <= a.shard < a.nshards):
        raise Stop(2, "workers, budget-mb, shard or nshards out of range")
    if a.resume_from and a.mode != "run":
        raise Stop(2, "--resume-from is for run only")
    if a.mode == "gate" and a.nshards != 1:
        raise Stop(2, "the gate is one job")
    if a.mode == "plan":
        return mode_plan(a, rows)
    if a.mode == "gate":
        return mode_gate(a, rows)
    return mode_run(a, rows)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
