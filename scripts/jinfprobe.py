"""
jinfprobe.py  --  CBO-GAP: what one coupled realization of CONC and TAU8
costs, in wall time and peak RSS, at reference sizes J_inf above 50000 and
with the J window extended to J_inf / 10  (ledger N45 window extension, C5;
N40 larger-reference rerun, C6; CLAUDE.md rule 6; Rahul's instruction
2026-10-31)

WHY THIS EXISTS
---------------
Rule 6: no trajectory design is proposed whose per-worker peak RSS has not
been measured. Two designs are pending and both need trajectories that have
never run:
  C5  the window extension: the same fixed-beta algorithm over a wider J
      window. The archived grids keep J <= J_inf / 10, so J up to 50000
      needs J_inf 500000 and J up to 400000 needs J_inf 4000000.
  C6  the larger-reference rerun: the affected d 40 cells of CONC and TAU8
      at J_inf = J_needed from sizetest E1 (200000, 1000000 or 4000000).
Measured so far: J_inf 50000 for every CONC and TAU8 unit (costprobe2), and
J_inf up to 100000 at d 10 only (REFSIZE). Nothing above 100000, and nothing
at d 40 above 50000.

WHAT IT RUNS (a measurement of cost; it decides nothing about the science)
  A UNIT is (module, objective, d): the 24 CONC units (mechanism; the six
  named objectives; d 2, 5, 10, 40) and the 18 TAU8 units (boundary; the
  six; d 5, 10, 40), 42 in all, every one with a committed costprobe2
  anchor at J_inf 50000. Each unit runs ONE coupled realization at every
  J_inf of the LADDER 50000, 200000, 500000, 1000000, 2000000, 4000000:
  252 tasks. A realization is the archived module's own one_realisation,
  imported and called unmodified (rule 4), exactly as rerunlib.realise
  calls it for CONC (mechanism) and TAU8 (boundary): law "centred", sigma
  rerunlib.SIGMA_ISO, dt rerunlib.DT, K = round(1.0 / DT), T 1.
  BETA: calprec2's fixed beta for (module, objective, d, centred, 0.01)
  from calprec2_beta.csv (runs/calprec2-finalize-20261023-112503), the
  tightest target, at which both designs would run. Wall time is assumed
  not to depend on beta (costprobe2's cost model, items A5 and A6 of its
  review); it is not tested here.
  J WINDOW: JEXT(N) = the J10 grid (10 ... 5000) cut at N / 10, then 10000,
  20000, 40000, ... while <= N / 10, then N / 10 itself if not yet in.
  Worked example: N 500000: J10 + 10000, 20000, 40000, 50000. N 50000:
  J10 exactly, the archived grid.
  SEEDS: SeedSequence(key), key = (20261031, KIND, module index, objective
  index, d, N), module and objective indices from costprobe2.MODULES and
  OBJ_NAMES; KIND 91 (run), 92 (smoke). Used by no other script.
  OUTPUT, per task: wall, peak RSS of its own process, every per-J coupled
  error E_J (rule 5), and the module's concentration extras.

PRE-SPECIFIED RULES (fixed 2026-10-31, before first execution)
  G-FORK  calprec2's scheduler finds the task only under the "fork" start
      method; any other is exit 2.
  G3  ARCHIVE IDENTITY: mechanism and boundary hash to
      costprobe2.ARCHIVE_SHA256; exit 2 otherwise.
  IN  INPUTS: the costprobe2 folders and the beta table verify against
      their sha256.txt; every unit has exactly one costprobe2 "main" row at
      J_inf 50000, J10, T 1, end ok, and a beta; exit 2 otherwise.
  M1  COST MODEL (for the schedule only). P(N) = N + sum JEXT(N), the
      particles evolved per step. est(unit, N) = wall50(unit) x P(N) /
      P(50000), wall50 from costprobe2 (Kaggle, 4 workers). Worked example:
      wall50 20.0 s; P(50000) = 60110, P(500000) = 630110: est 209.7 s.
      Linear in P is an assumption; the probe measures it.
  R1  RSS PREDICTION (for the concurrency guard only). For a task of unit u
      at N: if u has measured complete rows at two or more lower ladder
      sizes (this job or resumed), the line through the two largest of
      them, (P1, r1) and (P2, r2): r2 + (r2 - r1) (P - P2) / (P2 - P1), and
      at least r2; with one, r1 x P / P1; with none, the costprobe2 anchor
      x P / P(50000). Worked example: 300 MB at P 240110 and 600 MB at
      630110: at 1260110, 600 + 300 x 630000 / 390000 = 1084.6 MB.
  R2  CONCURRENCY GUARD. Tasks run in groups (N, d), N then d increasing.
      A group's workers = min(--workers, floor(--budget-mb / the largest R1
      prediction in it)). If that is 0 the group is NOT RUN, printed with
      its prediction; so is every group at a larger N of the same d. The
      default budget is 24000 MB of a Kaggle session's 30 GB. Worked
      example: prediction 9000 MB, budget 24000, --workers 4: 2 workers;
      prediction 26000 MB: not run.
  S1  SHARDS. All ladder sizes of a unit go to one shard, so R1 can use
      that unit's own smaller sizes. Units sorted by (-sum of est over the
      ladder, unit id) are assigned one by one to the shard with the
      smallest load so far (ties: lowest index). A task's load is est /
      its R2 workers under the anchor-scaled prediction (R1 with no
      measurement), so the load is the shard's elapsed estimate under
      perfect scaling. Plan mode prints the smallest K whose largest shard
      load is at most 0.5 x 21600 s, calprec2's target. The assignment is a
      function of the inputs and K only, so plan, every shard and every
      resume compute the same one.
  T1  PER-TASK TIMEOUT = max(600 s, 5 x the largest est among the job's
      tasks) (calprec2's factor and floor). A task over it is terminated
      and written as an error row.
  STOP --stop-after, default auto = min(36000, 43200 - TIMEOUT_S - 600):
      no new task starts after it; running tasks finish; exit 5; resume
      the same shard from the new folder. G-STOP: --stop-after + TIMEOUT_S
      > 43200 is exit 2. Worked example: TIMEOUT_S 10000: auto 32600.
  RS  RESUME (CLAUDE.md rule 17), --resume-from DIR[,DIR], mode run only:
      each folder is read only after its sha256.txt verifies and must hold
      one jinfprobe_params.csv and one jinfprobe_results.csv; its
      parameters other than the folder list (mode, shard, nshards,
      workers, the effective stop-after, ladder, kind, budget, the four
      script hashes, the input folder names, python, numpy) must equal
      this job's; a row
      counts as complete only with end "ok"; a complete tid found twice, or
      a tid not of this shard, is exit 2. The new folder holds new rows
      only.
  SMOKE  --mode smoke: every unit at 50000 and 200000 only (kind 92), one
      job. SMOKE PASS iff no task errored or timed out and no group was
      held back by R2; exit 0, else exit 4.
  NULL RATE (every rule above): none is a statistical criterion. G-FORK,
      G3, IN, RS and G-STOP are deterministic checks of inputs and
      settings; M1, R1, R2, S1, T1 and STOP schedule the work and decide no
      scientific question. Nothing here fires by chance.

WHAT THE RESULTS ARE FOR, AND WHAT THEY ARE NOT
  They are the measured wall and peak RSS that the C5 and C6 designs must
  be priced from. They are single realizations at one beta per unit: not
  a slope, not a rate, not a result about the algorithm. The per-J errors
  are written because rule 5 requires them, not to be analysed.

MODES
  plan    LAPTOP. Reads the inputs; prints the units, the M1 estimate per
          task, the R1 anchor prediction and R2 workers, the S1 schedule for
          K = 1 .. 16 and the K at the target. Writes nothing.
  smoke   KAGGLE. G-FORK, G3, IN, then the smoke tasks.
  run     KAGGLE. One shard: G-FORK, G3, IN, G-STOP, RS, then its groups.
  report  LAPTOP. Reads fetched folders (smoke or run, not mixed); prints
          per unit and N the measured wall, the M1 estimate and their
          ratio, and the peak RSS. Writes nothing.

EXIT CODES
  0  ran to the end (plan, report; smoke PASS; run with every task done).
  2  bad argument; folder, manifest, archive or input problem; G-FORK,
     G-STOP; a resume problem.
  4  errored or timed-out tasks; SMOKE FAIL.
  5  run stopped by --stop-after: resume this shard.
  6  run complete except groups held back by R2 (printed).
  Precedence: 4 over 5 over 6.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python -B scripts/jinfprobe.py --mode plan
  smoke and run go to Kaggle through kgrun.py (rule 13):
    --mode smoke --costprobe runs/A,runs/B --beta-table runs/C --workers 4
    --mode run --costprobe runs/A,runs/B --beta-table runs/C --shard S --nshards K --workers 4
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import hashlib                                                  # noqa: E402
import io                                                       # noqa: E402
import json                                                     # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import calprec2 as C2                                           # noqa: E402
import rerunlib as RL                                           # noqa: E402

cp = C2.cp
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = C2.OUTROOT
SEED0 = 20261031
K_RUN, K_SMOKE = 91, 92
LADDER = [50000, 200000, 500000, 1000000, 2000000, 4000000]
SMOKE_LADDER = [50000, 200000]
J10 = list(cp.J10)
OBJ6 = list(cp.OBJ6)
UNITS = ([("mechanism", o, d) for o in OBJ6 for d in (2, 5, 10, 40)] +
         [("boundary", o, d) for o in OBJ6 for d in (5, 10, 40)])
TAU_BETA = 0.01
LAW = "centred"
T_END = 1.0
BUDGET_MB = 24000.0
SHARD_TARGET_S = 0.5 * C2.CEILING_DEFAULT
TIMEOUT_FLOOR = 600.0
DEFAULT_COSTPROBE = [os.path.join(REPO, "runs", "costprobe2-s0-kaggle-20261010-103952"),
                     os.path.join(REPO, "runs", "costprobe2-s1-kaggle-20261011-101343")]
DEFAULT_BETA_TABLE = os.path.join(REPO, "runs", "calprec2-finalize-20261023-112503")
PARAMS_CSV = "jinfprobe_params.csv"
ROWS_CSV = "jinfprobe_results.csv"
COLS = ["tid", "phase", "cell", "n", "rep", "module", "objective", "d", "jinf", "jlist", "K", "beta", "seed_key",
        "pred_rss_mb", "workers_group", "E_json", "extras_json", "env", "wall_s", "rss_mb", "rss_flag", "error",
        "end"]
RESUME_KEYS = ("mode", "shard", "nshards", "workers", "stop_after", "ladder", "kind", "budget_mb", "script_sha256",
               "calprec2_sha256", "costprobe2_sha256", "rerunlib_sha256", "costprobe", "beta_table", "python",
               "numpy")
TASK_FN = "jinfprobe"


class Stop(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, code, msg)
        self.code = code
        self.msg = msg


def say(s=""):
    print(s)
    sys.stdout.flush()


def hdr(s):
    say("\n" + "=" * 100)
    say(s)
    say("=" * 100)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def verified(folder):
    try:
        return cp.verify_folder(folder)
    except SystemExit:
        raise Stop(2, "{} fails or lacks its sha256.txt".format(folder))


def unit_id(u):
    return "{}|{}|{}".format(u[0], u[1], u[2])


# ----------------------------------------------------------------------
# J window, cost model, RSS prediction
# ----------------------------------------------------------------------

def jext(n):
    top = n // 10
    out = [J for J in J10 if J <= top]
    j = 10000
    while j <= top:
        out.append(j)
        j *= 2
    if top not in out:
        out.append(top)
    return sorted(set(out))


def particles(n):
    return n + sum(jext(n))


P50 = particles(50000)


def est_of(wall50, n):
    return wall50 * particles(n) / float(P50)


def predict_rss(anchor, measured, n):
    """R1. measured: {N: rss} of the unit's complete rows below n."""
    pts = sorted((particles(m), r) for m, r in measured.items() if m < n)
    p = particles(n)
    if len(pts) >= 2:
        (p1, r1), (p2, r2) = pts[-2], pts[-1]
        return max(r2, r2 + (r2 - r1) * (p - p2) / float(p2 - p1))
    if len(pts) == 1:
        return pts[0][1] * p / float(pts[0][0])
    return anchor * p / float(P50)


def workers_for(pred, workers, budget):
    return int(min(workers, math.floor(budget / pred))) if pred > 0 else workers


# ----------------------------------------------------------------------
# inputs
# ----------------------------------------------------------------------

def read_anchors(folders):
    """IN. {unit: (wall50, rss50)} from costprobe2's main rows."""
    found = {}
    for f in folders:
        for rel in verified(f):
            if os.path.basename(rel) != "costprobe2_results.csv":
                continue
            with io.open(os.path.join(f, rel), "r", newline="", encoding="utf-8") as fh:
                for x in csv.DictReader(fh):
                    if x.get("kind") != "main" or x.get("module") not in ("mechanism", "boundary"):
                        continue
                    if x["J_inf"] != "50000" or x["J_grid"] != "J10" or x["T"] != "1.0" or x["end"] != "ok":
                        continue
                    u = (x["module"], x["objective"], int(x["d"]))
                    found.setdefault(u, []).append((float(x["wall_s"]), float(x["peak_rss_mb"])))
    out = {}
    for u in UNITS:
        v = found.get(u, [])
        if len(v) != 1:
            raise Stop(2, "IN: unit {} has {} costprobe2 main rows at J_inf 50000, J10, T 1".format(unit_id(u), len(v)))
        out[u] = v[0]
    return out


def read_betas(folder):
    rels = verified(folder)
    if "calprec2_beta.csv" not in [os.path.basename(r) for r in rels]:
        raise Stop(2, "{}: no calprec2_beta.csv".format(folder))
    path = os.path.join(folder, [r for r in rels if os.path.basename(r) == "calprec2_beta.csv"][0])
    tab = {}
    with io.open(path, "r", newline="", encoding="utf-8") as fh:
        for x in csv.DictReader(fh):
            tab[x["cell"]] = x["beta"]
    out = {}
    for u in UNITS:
        cid = C2.cell_id((u[0], u[1], u[2], LAW, TAU_BETA))
        if cid not in tab:
            raise Stop(2, "IN: calprec2_beta.csv has no {}".format(cid))
        out[u] = tab[cid]
    return out


def make_tasks(anchors, betas, ladder, kind):
    tasks = []
    for u in UNITS:
        for n in ladder:
            key = (SEED0, kind, cp.MODULES.index(u[0]), cp.OBJ_NAMES.index(u[1]), u[2], n)
            tasks.append({"tid": "JP{}|{}|{}".format(kind, unit_id(u), n), "phase": "JP", "n": n, "rep": 0,
                          "c": (u[0], u[1], u[2], LAW, TAU_BETA), "unit": u, "module": u[0], "objective": u[1],
                          "d": u[2], "jinf": n, "jlist": jext(n), "K": int(round(T_END / RL.DT)),
                          "beta": float(betas[u]), "beta_s": betas[u], "key": key,
                          "est": est_of(anchors[u][0], n), "anchor_rss": anchors[u][1]})
    return tasks


def assign(tasks, k, workers, budget):
    """S1. {shard: [tasks]} and {shard: load}."""
    by_unit = {}
    for t in tasks:
        by_unit.setdefault(t["unit"], []).append(t)

    def load_of(ts):
        s = 0.0
        for t in ts:
            w = workers_for(predict_rss(t["anchor_rss"], {}, t["n"]), workers, budget)
            s += t["est"] / max(w, 1)
        return s

    order = sorted(by_unit, key=lambda u: (-sum(t["est"] for t in by_unit[u]), unit_id(u)))
    shards = dict((i, []) for i in range(k))
    loads = dict((i, 0.0) for i in range(k))
    for u in order:
        i = min(range(k), key=lambda j: (loads[j], j))
        shards[i].extend(by_unit[u])
        loads[i] += load_of(by_unit[u])
    return shards, loads


# ----------------------------------------------------------------------
# the task (in a forked child of calprec2's scheduler)
# ----------------------------------------------------------------------

def task_probe(t):
    row = C2.base_row(t)
    row.update({"module": t["module"], "objective": t["objective"], "d": t["d"], "jinf": t["jinf"],
                "jlist": ";".join(str(J) for J in t["jlist"]), "K": t["K"], "beta": t["beta_s"],
                "seed_key": "-".join(str(x) for x in t["key"]), "pred_rss_mb": "{:.1f}".format(t.get("pred", 0.0)),
                "workers_group": t.get("wg", "")})
    t0 = time.time()
    try:
        mod = cp.MODS[t["module"]]
        seed = np.random.SeedSequence(list(t["key"]))
        jl, n, o, d, K = t["jlist"], t["jinf"], t["objective"], t["d"], t["K"]
        if t["module"] == "mechanism":
            E, le0, lem = mod.one_realisation(o, t["beta"], d, LAW, RL.SIGMA_ISO, RL.DT, K, n, jl, seed)
            ex = {"le0": le0, "le_min": lem}
        else:
            out = mod.one_realisation(o, d, TAU_BETA, t["beta"], RL.SIGMA_ISO, RL.DT, K, n, jl, seed)
            E = out[0]
            ex = {"le0": out[1], "le_mean": out[2], "le_min": out[3]}
        row.update({"E_json": json.dumps(dict((str(J), repr(float(E[J]))) for J in jl), sort_keys=True),
                    "extras_json": json.dumps(dict((k, repr(float(v))) for k, v in ex.items()), sort_keys=True),
                    "end": "ok", "error": ""})
    except Exception as e:                                       # noqa: BLE001 (written as an error row)
        row.update({"error": "{}: {}".format(type(e).__name__, e), "end": "err"})
    row["wall_s"] = "{:.3f}".format(time.time() - t0)
    row["rss_mb"] = "{:.1f}".format(C2.rss_mb())
    return row


C2.TASKS[TASK_FN] = task_probe


# ----------------------------------------------------------------------
# gates, resume, run
# ----------------------------------------------------------------------

def gates():
    hdr("G-FORK, G3")
    sm = multiprocessing.get_start_method(allow_none=False)
    if sm != "fork":
        raise Stop(2, "G-FORK: start method {}, not fork".format(sm))
    say("  G-FORK PASS  start method fork")
    for m in ("mechanism", "boundary"):
        if sha256_of(cp.MODS[m].__file__) != cp.ARCHIVE_SHA256.get(m):
            raise Stop(2, "G3: archived {} does not match costprobe2.ARCHIVE_SHA256".format(m))
    say("  G3 PASS  mechanism, boundary match costprobe2.ARCHIVE_SHA256")


def header(a, mode):
    hdr("CBO-GAP jinfprobe  (ledger N45 C5, N40 C6; rule 6)  mode {}".format(mode))
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    say("  script   sha256 {}".format(sha256_of(os.path.abspath(__file__))))
    say("  calprec2.py sha256 {}".format(sha256_of(C2.__file__)))
    say("  costprobe2.py sha256 {}".format(sha256_of(cp.__file__)))
    say("  rerunlib.py sha256 {}".format(sha256_of(RL.__file__)))
    say("  costprobe {}".format(",".join(os.path.basename(x.rstrip("/")) for x in a.costprobe)))
    say("  beta table {}".format(os.path.basename(a.beta_table.rstrip("/"))))
    say("  units    {} (CONC mechanism d 2, 5, 10, 40; TAU8 boundary d 5, 10, 40; six objectives)".format(len(UNITS)))
    say("  beta     calprec2 fixed beta at ({}, {}); law {}; sigma {}; dt {}; T {}".format(
        LAW, TAU_BETA, LAW, RL.SIGMA_ISO, RL.DT, T_END))
    say("  seeds    SeedSequence(({}, kind, module index, objective index, d, J_inf)); kind {} run, {} smoke".format(
        SEED0, K_RUN, K_SMOKE))
    say("  budget   {:.0f} MB for concurrent tasks (R2)".format(a.budget_mb))


def timing(a, tasks):
    """T1 and STOP: (TIMEOUT_S, effective --stop-after)."""
    to = max(TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR * max(t["est"] for t in tasks))
    stop = a.stop_after if a.stop_after is not None else min(C2.STOP_AFTER_DEFAULT, C2.KAGGLE_CAP_S - to - 600.0)
    return to, stop


def params_rows(a, mode, ladder, kind, stop):
    return [["mode", mode], ["shard", str(a.shard)], ["nshards", str(a.nshards)], ["workers", str(a.workers)],
            ["stop_after", repr(float(stop))],
            ["ladder", ",".join(str(n) for n in ladder)], ["kind", str(kind)], ["budget_mb", repr(float(a.budget_mb))],
            ["script_sha256", sha256_of(os.path.abspath(__file__))], ["calprec2_sha256", sha256_of(C2.__file__)],
            ["costprobe2_sha256", sha256_of(cp.__file__)], ["rerunlib_sha256", sha256_of(RL.__file__)],
            ["costprobe", ",".join(os.path.basename(x.rstrip("/")) for x in a.costprobe)],
            ["beta_table", os.path.basename(a.beta_table.rstrip("/"))],
            ["python", platform.python_version()], ["numpy", np.__version__],
            ["resume_from", a.resume_from or ""]]


def read_kv(path):
    with io.open(path, "r", newline="", encoding="utf-8") as fh:
        return dict((r[0], r[1]) for r in csv.reader(fh) if r)


def read_folders(folders, want, mine):
    """RS (run) and report: complete rows by tid from verified folders."""
    store, prms = {}, []
    for f in folders:
        rels = verified(f)
        pp = [r for r in rels if os.path.basename(r) == PARAMS_CSV]
        rr = [r for r in rels if os.path.basename(r) == ROWS_CSV]
        if len(pp) != 1 or len(rr) != 1:
            raise Stop(2, "{}: expected one {} and one {}".format(f, PARAMS_CSV, ROWS_CSV))
        pr = read_kv(os.path.join(f, pp[0]))
        if want is not None:
            bad = sorted(k for k in want if pr.get(k) != want[k])
            if bad:
                raise Stop(2, "{}: parameters differ from this job's in {} (rule 17)".format(f, bad))
        prms.append(pr)
        rows, nok = 0, 0
        with io.open(os.path.join(f, rr[0]), "r", newline="", encoding="utf-8") as fh:
            for x in csv.DictReader(fh):
                rows += 1
                if mine is not None and x["tid"] not in mine:
                    raise Stop(2, "{}: task {} is not one of this job's".format(f, x["tid"]))
                if x.get("end") != "ok":
                    continue
                nok += 1
                if x["tid"] in store:
                    raise Stop(2, "task {} is complete in two folders (second: {})".format(x["tid"], f))
                store[x["tid"]] = x
        say("  read {}: mode {}, shard {} of {}, {} rows, {} complete".format(
            f, pr.get("mode"), pr.get("shard"), pr.get("nshards"), rows, nok))
    return store, prms


def new_outdir(mode, shard, nshards):
    tag = "" if nshards == 1 else "-s{}of{}".format(shard, nshards)
    out = os.path.join(OUTROOT, "jinfprobe-{}-{}{}".format(mode, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
                                                          tag))
    os.makedirs(out)
    return out


def execute(a, mode, tasks, ladder, kind, store):
    to, stop = timing(a, tasks)
    hdr("T1, STOP, G-STOP")
    say("  TIMEOUT_S = {:.0f} s  (max({:.0f}, {:.0f} x largest est {:.1f} s))".format(
        to, TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR, max(t["est"] for t in tasks)))
    say("  --stop-after {:.0f} s{} + TIMEOUT_S {:.0f} s = {:.0f} s   cap {:.0f} s".format(
        stop, " (auto)" if a.stop_after is None else "", to, stop + to, C2.KAGGLE_CAP_S))
    if stop <= 0 or stop + to > C2.KAGGLE_CAP_S:
        raise Stop(2, "G-STOP: --stop-after + TIMEOUT_S exceeds the 12-hour cap")
    say("  G-STOP PASS")
    out = new_outdir(mode, a.shard, a.nshards)
    with io.open(os.path.join(out, PARAMS_CSV), "x", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(params_rows(a, mode, ladder, kind, stop))
    say("\n  run dir  {}".format(out))
    C2.RSS_BUDGET_MB = a.budget_mb          # the per-task flag of calprec2's scheduler, at this probe's budget
    o = C2.Out(os.path.join(out, ROWS_CSV), COLS)
    runner = C2.Runner(a.workers, to, o, store, stop_after=stop)
    held = []
    blocked_d = set()
    hdr("Tasks, in groups (J_inf, d)  (R1, R2)")
    try:
        groups = sorted(set((t["jinf"], t["d"]) for t in tasks))
        for n, d in groups:
            gts = [t for t in tasks if t["jinf"] == n and t["d"] == d]
            if d in blocked_d:
                held.extend(gts)
                say("  group J_inf {} d {}: NOT RUN (a smaller J_inf at d {} was held back)".format(n, d, d))
                continue
            for t in gts:
                meas = {}
                for x in runner.store.values():
                    if x.get("end") == "ok" and x.get("module") == t["module"] and x.get("objective") == t["objective"] \
                            and str(x.get("d")) == str(d):
                        meas[int(x["jinf"])] = float(x["rss_mb"])
                t["pred"] = predict_rss(t["anchor_rss"], meas, n)
            pred = max(t["pred"] for t in gts)
            w = workers_for(pred, a.workers, a.budget_mb)
            if w < 1:
                held.extend(gts)
                blocked_d.add(d)
                say("  group J_inf {} d {}: NOT RUN, largest predicted RSS {:.1f} MB > budget {:.0f} MB (R2)".format(
                    n, d, pred, a.budget_mb))
                continue
            for t in gts:
                t["wg"] = w
            say("  group J_inf {} d {}: {} task(s), largest predicted RSS {:.1f} MB, workers {}".format(
                n, d, len(gts), pred, w))
            runner.workers = w
            runner.run([(TASK_FN, t) for t in gts], "J{} d{}".format(n, d))
            if runner.stopped:
                break
    finally:
        o.close()
    done = [r for r in runner.store.values() if r.get("end") == "ok"]
    say("\n" + "=" * 96)
    say("tasks run by this job: {}   task execution {:.0f} s".format(runner.ran, runner.elapsed()))
    say("largest per-task peak RSS {:.1f} MB".format(max([float(r["rss_mb"]) for r in done] or [float("nan")])))
    if runner.stopped:
        say("STOPPED by --stop-after {:.0f} s. Resume this shard from this folder.".format(stop))
    else:
        say("not stopped")
    say("errored or timed-out tasks: {}".format(runner.errors))
    say("held back by R2: {}".format(len(held)))
    say("files  {}".format(out))
    say("=" * 96)
    return runner, held


# ----------------------------------------------------------------------
# modes
# ----------------------------------------------------------------------

def inputs(a):
    hdr("IN  inputs")
    anchors = read_anchors([os.path.abspath(x) for x in a.costprobe])
    betas = read_betas(os.path.abspath(a.beta_table))
    say("  IN PASS  {} units, each with one costprobe2 anchor at J_inf 50000 and a calprec2 beta".format(len(anchors)))
    return anchors, betas


def mode_plan(a):
    header(a, "plan")
    anchors, betas = inputs(a)
    tasks = make_tasks(anchors, betas, LADDER, K_RUN)
    hdr("M1, R1 (anchor-scaled), R2 per task  (a schedule, not a measurement)")
    say("  J window per J_inf (JEXT) and particles per step P:")
    for n in LADDER:
        say("    J_inf {:>8}: P {:>9}  J {}".format(n, particles(n), ",".join(str(J) for J in jext(n))))
    say("  {:<26} {:>8} {:>9} {:>10} {:>12} {:>8}".format("unit", "J_inf", "wall50 s", "est s", "pred RSS MB",
                                                          "workers"))
    for t in tasks:
        p = predict_rss(t["anchor_rss"], {}, t["n"])
        say("  {:<26} {:>8} {:>9.2f} {:>10.1f} {:>12.1f} {:>8}".format(
            unit_id(t["unit"]), t["n"], anchors[t["unit"]][0], t["est"], p, workers_for(p, a.workers, a.budget_mb)))
    held = [t for t in tasks if workers_for(predict_rss(t["anchor_rss"], {}, t["n"]), a.workers, a.budget_mb) < 1]
    say("  tasks whose anchor-scaled prediction exceeds the budget: {} (R1 refines this from the unit's own"
        " smaller sizes during the run)".format(len(held)))
    hdr("S1  shard schedule (elapsed estimate under perfect scaling; overruns of up to 30% have been measured)")
    pick = None
    for k in range(1, 17):
        _s, loads = assign(tasks, k, a.workers, a.budget_mb)
        mx = max(loads.values())
        say("  K {:>2}: largest shard {:>9.0f} s = {:>5.1f}% of {:.0f} s".format(k, mx, 100.0 * mx / C2.CEILING_DEFAULT,
                                                                            C2.CEILING_DEFAULT))
        if pick is None and mx <= SHARD_TARGET_S:
            pick = k
    if pick is None:
        say("  no K up to 16 meets the target {:.0f} s".format(SHARD_TARGET_S))
    else:
        shards, loads = assign(tasks, pick, a.workers, a.budget_mb)
        say("  at the target {:.0f} s: K = {}".format(SHARD_TARGET_S, pick))
        for i in range(pick):
            to = max(TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR * max(t["est"] for t in shards[i]))
            say("    shard {}: {} tasks, {} units, load {:.0f} s, TIMEOUT_S {:.0f} s, auto --stop-after {:.0f} s".format(
                i, len(shards[i]), len(shards[i]) // len(LADDER), loads[i], to,
                min(C2.STOP_AFTER_DEFAULT, C2.KAGGLE_CAP_S - to - 600.0)))
    hdr("jinfprobe.py plan done, exit 0  (nothing written)")
    return 0


def mode_smoke(a):
    header(a, "smoke")
    gates()
    anchors, betas = inputs(a)
    tasks = make_tasks(anchors, betas, SMOKE_LADDER, K_SMOKE)
    runner, held = execute(a, "smoke", tasks, SMOKE_LADDER, K_SMOKE, {})
    ok = runner.errors == 0 and not held and not runner.stopped
    say("SMOKE {}".format("PASS" if ok else "FAIL"))
    return 0 if ok else 4


def mode_run(a):
    header(a, "run")
    gates()
    anchors, betas = inputs(a)
    tasks = make_tasks(anchors, betas, LADDER, K_RUN)
    shards, _loads = assign(tasks, a.nshards, a.workers, a.budget_mb)
    mine = shards[a.shard]
    say("  shard {} of {}: {} tasks, units {}".format(a.shard, a.nshards, len(mine),
                                                    ", ".join(sorted(set(unit_id(t["unit"]) for t in mine)))))
    store = {}
    if a.resume_from:
        hdr("RS  resume (CLAUDE.md rule 17)")
        want = dict((k, v) for k, v in params_rows(a, "run", LADDER, K_RUN, timing(a, mine)[1]) if k in RESUME_KEYS)
        store, _ = read_folders([os.path.abspath(x) for x in a.resume_from.split(",") if x], want,
                                set(t["tid"] for t in mine))
        say("  {} complete task(s) read; they are skipped".format(len(store)))
    runner, held = execute(a, "run", mine, LADDER, K_RUN, store)
    if runner.errors:
        return 4
    if runner.stopped:
        return 5
    return 6 if held else 0


def mode_report(a):
    hdr("jinfprobe.py  mode report  --  writes nothing")
    if not a.folder:
        raise Stop(2, "--folder is required, repeat it for each fetched folder")
    folders = [os.path.abspath(x) for x in a.folder]
    if len(set(folders)) != len(folders):
        raise Stop(2, "a folder is given twice")
    store, prms = read_folders(folders, None, None)
    modes = set(p.get("mode") for p in prms)
    if len(modes) != 1:
        raise Stop(2, "smoke and run folders mixed: {}".format(sorted(modes)))
    for k in ("python", "numpy", "costprobe", "beta_table", "script_sha256"):
        if len(set(p.get(k) for p in prms)) != 1:
            raise Stop(2, "folders differ in {}".format(k))
    anchors = read_anchors(DEFAULT_COSTPROBE if not a.costprobe_given else [os.path.abspath(x) for x in a.costprobe])
    say("  platform python {} numpy {}".format(prms[0].get("python"), prms[0].get("numpy")))
    say("  {:<26} {:>8} {:>10} {:>10} {:>7} {:>10} {:>10}".format("unit", "J_inf", "wall s", "est s", "ratio",
                                                               "RSS MB", "pred MB"))
    for u in UNITS:
        for x in sorted((r for r in store.values() if r["module"] == u[0] and r["objective"] == u[1]
                         and int(r["d"]) == u[2]), key=lambda r: int(r["jinf"])):
            n = int(x["jinf"])
            e = est_of(anchors[u][0], n)
            w = float(x["wall_s"])
            say("  {:<26} {:>8} {:>10.1f} {:>10.1f} {:>7.2f} {:>10} {:>10}".format(
                unit_id(u), n, w, e, w / e, x["rss_mb"], x["pred_rss_mb"]))
    say("  complete rows {}; largest peak RSS {:.1f} MB".format(
        len(store), max([float(r["rss_mb"]) for r in store.values()] or [float("nan")])))
    hdr("jinfprobe.py report done, exit 0")
    return 0


def main():
    ap = argparse.ArgumentParser(description="J_inf cost probe for C5 and C6 (rule 6)")
    ap.add_argument("--mode", choices=("plan", "smoke", "run", "report"), required=True)
    ap.add_argument("--costprobe", default=None, help="comma-joined costprobe2 folders")
    ap.add_argument("--beta-table", default=DEFAULT_BETA_TABLE)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-mb", type=float, default=BUDGET_MB)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--stop-after", type=float, default=None)
    ap.add_argument("--resume-from", default="")
    ap.add_argument("--folder", action="append", default=[], help="report: fetched folder; repeat")
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    a.costprobe_given = a.costprobe is not None
    a.costprobe = [x for x in a.costprobe.split(",") if x] if a.costprobe else list(DEFAULT_COSTPROBE)
    if a.workers < 1 or a.budget_mb <= 0 or a.nshards < 1 or not (0 <= a.shard < a.nshards):
        raise Stop(2, "workers, budget-mb, shard or nshards out of range")
    if a.resume_from and a.mode != "run":
        raise Stop(2, "--resume-from is for mode run only")
    if a.mode == "smoke" and a.nshards != 1:
        raise Stop(2, "smoke is one job")
    if a.mode == "plan":
        return mode_plan(a)
    if a.mode == "smoke":
        return mode_smoke(a)
    if a.mode == "run":
        return mode_run(a)
    return mode_report(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
