"""
c5run.py  --  CBO-GAP: the trajectories of C5, the window extension, rows
CONC-X and TAU8-X: every CONC and TAU8 cell at J_inf 4000000 with the J
window to 400000  (ledger N45, "C5 DESIGN"; CLAUDE.md rules 4 to 6, 17;
Rahul's instruction 2026-11-01)

WHAT THIS DOES, IN PLAIN LANGUAGE
---------------------------------
It evolves 4320 coupled realizations (288 cells x 15) with the archived
modules' own one_realisation, at the same fixed beta each cell's 50000 run
used, at a reference size of 4000000 particles, and writes every
realization's E_J at the 17 J of the extended window. It fits no slope and
decides nothing about the science: c5_analysis.py does that, under readings
fixed in N45 before this ran.

WHY A SEPARATE SCRIPT, NOT TWO ROWS OF rerun.py (decided 2026-11-01)
  rerun_analysis.py refuses to run unless rerunlib.ROWS equals its 21 rows,
  and refuses a plan built with another rerunlib.py hash. Adding rows to
  rerunlib would stop the confirmed 21-row analysis from being re-run at
  HEAD. So CONC-X and TAU8-X live here, and rerunlib, rerun.py and
  rerun_analysis.py are untouched. What is shared is imported: the cells'
  coordinates and key layout (rerunlib.coord_fields, rerunlib.ENTROPY), the
  finite-J audit (rerunlib.audit_one), the archived dynamics
  (costprobe2.MODS), the betas (calprec2_beta.csv), the scheduler
  (calprec2.Runner, as jinfprobe used it at 4000000), the J window
  (jinfprobe.jext) and the shard rule (c5price.cells, c5price.assign).

THE ROWS
  CONC-X  the 144 CONC cells (c5price.cells, row CONC): mechanism; six
          objectives; d 2, 5, 10, 40; laws centred, mix-0.1; tau_0 0.5,
          0.1, 0.01. Owner index 21.
  TAU8-X  the 144 TAU8 cells (row TAU8): boundary; six objectives; d 5,
          10, 40; tau_0 0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01.
          Owner index 22. Law centred.
  Every cell: J_inf 4000000, T 1, K = 100, DT 0.01, sigma 0.2
  (rerunlib.SIGMA_ISO), M 15, J window JLIST = jinfprobe.jext(4000000):
  10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000, 10000, 20000, 40000,
  80000, 160000, 320000, 400000.
  A realization is the archived one_realisation called unmodified, the
  same calls as rerunlib.realise makes for mechanism and boundary.

SEEDS
  key = (rerunlib.ENTROPY 20261016, KIND, owner index, rerunlib.coord_fields
  of the cell (module, objective, d, law, tau_0 e6, r e6, sigma_design e6,
  beta_design e6, J_inf, T e6, arm, sub-arm), rep). KIND 95 run, 97 smoke,
  98 drill; the bootstrap key is the same without rep, kind 96. Owner
  indices 21 and 22 are used by no rerunlib row (rerunlib.ROWS has 21
  rows, indices 0 to 20), J_inf 4000000 by no rerun cell, and kinds 95 to
  98 by no script (in use: 1, 2, 11, 12, 31 to 35, 41 to 43, 51, 61 to 67,
  71, 81, 83, 91, 92). Worked example: CONC-X mechanism ackley d 2
  centred tau_0 0.5 rep 0: 20261016-95-21-2-0-2-0-500000-0-0-0-4000000-
  1000000-0-0-0.

PRE-SPECIFIED RULES (fixed 2026-11-01, before first execution)
  G-FORK  calprec2's scheduler under the "fork" start method only; exit 2.
  G3  mechanism and boundary hash to costprobe2.ARCHIVE_SHA256; exit 2.
  IN  --timing: the three jinfprobe run folders, read by c5price.read_probe
      (verified manifests, 252 complete tasks, one script hash).
      --beta-table: a verified calprec2 finalize folder with
      calprec2_beta.csv. --rerun-plan: the verified rerun plan whose CONC
      and TAU8 cells the 50000 run used. Exit 2 on any failure.
  B1  SAME BETA AS THE 50000 CELL. For every cell, repr(float(calprec2
      beta)) must equal the beta string of the rerun plan's row (CONC or
      TAU8) with the same module, objective, d, law and tau_0, and that
      row must have J_inf 50000 and M 15. Any mismatch: exit 2, nothing
      run. This is what lets D-ref compare like with like.
      Worked example: CONC mechanism ackley d 2 centred 0.5: calprec2
      0.5401932690411878, plan "0.5401932690411878": pass.
  W   WORKERS PER d (c5price PR): min(--workers, floor(--budget-mb / (1.10
      x R_d))), R_d the largest 4000000 peak RSS jinfprobe measured at d.
      Tasks run in groups by d, d increasing, each group at its workers.
      A row whose RSS exceeds --budget-mb / workers is flagged "G-RSS
      FAIL" (printed and written; not an error: the budget leaves 6 GB of
      Kaggle's 30 GB); a worker killed for memory is an error row.
      Worked example: R_d 10000 MB: 24000 / 11000, 2 workers, flag above
      12000 MB.
  S2  SHARDS = c5price's rule exactly: load = the unit's measured 4000000
      wall / W; tasks in c5price's order (-load, c5price task id), each to
      the least-loaded shard (heap, ties to the lowest index), with
      c5price.assign. So shard S of K here holds exactly the tasks c5price
      priced as shard S of K. Plan mode prints the smallest K at the
      10800 s target and "S2 PASS" iff it equals --nshards.
  T1  per-task timeout = max(600 s, 5 x the largest measured wall among
      the shard's tasks).
  STOP --stop-after, default auto = min(36000, 43200 - T1 - 600): no task
      starts after it; running tasks finish; exit 5; resume the shard.
      G-STOP: --stop-after + T1 > 43200 is exit 2.
  RS  RESUME (CLAUDE.md rule 17), --resume-from DIR[,DIR], run and drill:
      each folder only after its sha256.txt verifies; one c5run_params.csv
      and one c5run_real.csv; its parameters other than the folder list
      (RESUME_KEYS) equal this job's; a row counts only with end "ok"; a
      complete tid twice, or a tid not of this job, is exit 2. Printed per
      folder: "  read <folder>: shard S of K, N rows, M complete".
  F1  the finite-J audit, rerunlib.audit_one: the redrawn reference's
      log-ESS equals the le0 one_realisation returned within 1e-12 x
      max(1, |le0|); a failure writes "F1 FAILED", the job continues and
      ends with exit 3.
  SMOKE  --mode smoke (kind 97): per row, the task of the unit with the
      smallest measured wall, run twice; SMOKE PASS iff both members end
      ok, their E_json strings are identical, and F1 holds in both.
      Exit 0 on PASS, 3 on FAIL.
  DRILL  --mode drill (kind 98): the 12 tasks of the CONC-X d 2 unit
      with the smallest measured 4000000 wall (ties: c5price order),
      tau_0 0.5, both laws, reps 0 to 5, at 4 workers, with the given
      --stop-after. It exists to exercise the stop and resume path on
      Kaggle (exit 5, then resumed attempts) before the shards; its rows
      are not data. Worked example: wall w = 130 s, --stop-after 150:
      four tasks start at 0 and four near 130 s; near 260 s four are
      pending and none starts: exit 5; the resumed attempt runs the four:
      exit 0. With w = 170 s: only the first four start (8 pending), exit
      5; attempt 2 runs four and stops with four pending, exit 5; attempt
      3 runs the last four, exit 0. For any w between 75 and 150 s attempt
      1 exits 5 and at most three attempts finish the drill.
  NULL RATE (every rule above): none is a statistical criterion. G-FORK,
      G3, IN, B1, RS, G-STOP and F1 are deterministic checks; W, S2, T1
      and STOP schedule work; SMOKE compares two runs of one key bitwise.
      Nothing here fires by chance.

OUTPUT (every file opened "x")
  <outdir>/c5run-<mode>-YYYYMMDD-HHMMSS[-s<S>of<K>]/
    c5run_params.csv  every parameter (checked on resume)
    c5run_real.csv    one row per realization: ids, keys, cell, beta and
                      calprec2 label, E_J at every J of JLIST (E_json), the
                      module's extras, le0, the audit, wall, peak RSS

MODES
  plan    LAPTOP, writes nothing: IN, B1, W, the S2 sweep and the shard
          detail for --nshards, the end-to-end estimate (E2E below).
  smoke   KAGGLE. G-FORK, G3, IN, B1, then SMOKE.
  drill   KAGGLE. G-FORK, G3, IN, B1, G-STOP, RS, then DRILL.
  run     KAGGLE. One shard: G-FORK, G3, IN, B1, G-STOP, RS, its groups.
  E2E (plan only; an estimate, not a measurement): per shard, its S2 load
      plus OVERHEAD_S = 1800 s (one 15-minute tick interval to launch after
      the previous fetch, one to notice the finish); serial = the sum over
      shards; with N kernels in flight, the shards in order on N slots,
      each to the slot that frees first. Printed for N = 1 to 5.

EXIT CODES
  0 done (plan; smoke PASS; run or drill with every task done); 2 bad
  argument, input, manifest, B1, G-FORK, G3, G-STOP or resume problem;
  3 F1 failure or SMOKE FAIL; 4 errored or timed-out tasks; 5 stopped by
  --stop-after (resume this shard). Precedence: 3 and 4 over 5.

HOW TO RUN (repository root; Python 3.8 to 3.13, NumPy only)
    python -B scripts/c5run.py --mode plan --nshards 116
  on Kaggle through the queue (rule 22), or kgrun by hand (rule 13):
    --mode smoke --timing A,B,C --beta-table D --rerun-plan E --workers 4
    --mode drill --timing ... --stop-after 300 --workers 4
    --mode run --timing ... --shard S --nshards K --workers 4
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import heapq                                                    # noqa: E402
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

import c5price as PR                                            # noqa: E402
import jinfprobe as JP                                          # noqa: E402

C2, RL, cp = JP.C2, JP.RL, JP.cp
rl = RL
Stop, say, hdr, sha256_of = JP.Stop, JP.say, JP.hdr, JP.sha256_of

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = C2.OUTROOT
J_INF = PR.J_INF
M = PR.M
JLIST = JP.jext(J_INF)
T_END = 1.0
OWNER = {"CONC": ("CONC-X", 21), "TAU8": ("TAU8-X", 22)}
KIND_RUN, KIND_BOOT, KIND_SMOKE, KIND_DRILL = 95, 96, 97, 98
BUDGET_MB = PR.BUDGET_MB
TARGET_S = PR.TARGET_S
OVERHEAD_S = 1800.0
TIMEOUT_FLOOR = 600.0
DRILL_N = 12
DEFAULT_TIMING = [os.path.join(REPO, "runs", x) for x in (
    "jinfprobe-s0of3-a1-kaggle-20261031-210629", "jinfprobe-s1of3-a1-kaggle-20261031-233459",
    "jinfprobe-s2of3-a1-kaggle-20261101-015818")]
DEFAULT_BETA = os.path.join(REPO, "runs", "calprec2-finalize-20261023-112503")
DEFAULT_PLAN = os.path.join(REPO, "runs", "rerun-plan-20261023-112643")
PARAMS_CSV = "c5run_params.csv"
ROWS_CSV = "c5run_real.csv"
COLS = ["tid", "phase", "cell", "n", "rep", "row", "module", "objective", "d", "law", "tau0", "jinf", "jlist",
        "K", "beta", "cal_label", "seed_key", "boot_key", "order_id", "pred_rss_mb", "workers_group", "E_json",
        "extras_json", "le0", "le_redraw", "F1", "audit_ref", "audit_ratios", "env", "wall_s", "rss_mb",
        "rss_flag", "error", "end"]
RESUME_KEYS = ("mode", "shard", "nshards", "workers", "stop_after", "budget_mb", "kind", "script_sha256",
               "jinfprobe_sha256", "c5price_sha256", "calprec2_sha256", "costprobe2_sha256", "rerunlib_sha256",
               "timing", "beta_table", "rerun_plan", "python", "numpy")
TASK_FN = "c5run"


# ----------------------------------------------------------------------
# cells, keys, inputs
# ----------------------------------------------------------------------

def key_str(k):
    return "-".join(str(x) for x in k)


def rl_cell(c):
    """rerunlib's cell dict for a c5price cell (row, module, objective, d, law, tau), at J_INF."""
    return rl._cell(c[0], c[1], c[2], c[3], law=c[4], tau=c[5], jinf=J_INF)


def keys_of(c, rep, kind):
    own = OWNER[c[0]][1]
    cf = rl.coord_fields(rl_cell(c))
    return (rl.ENTROPY, kind, own) + tuple(cf) + (int(rep),), (rl.ENTROPY, KIND_BOOT, own) + tuple(cf)


def read_betas(folder):
    rels = JP.verified(folder)
    hits = [r for r in rels if os.path.basename(r) == "calprec2_beta.csv"]
    if len(hits) != 1:
        raise Stop(2, "IN: {}: expected one calprec2_beta.csv".format(folder))
    return rl.read_calprec2(os.path.join(folder, hits[0]))


def read_plan(folder):
    rels = JP.verified(folder)
    hits = [r for r in rels if os.path.basename(r) == "rerun_plan.csv"]
    if len(hits) != 1:
        raise Stop(2, "IN: {}: expected one rerun_plan.csv".format(folder))
    out = {}
    with io.open(os.path.join(folder, hits[0]), "r", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["row"] in ("CONC", "TAU8"):
                k = (r["row"], r["module"], r["objective"], int(r["d"]), r["law"], float(r["tau0"]))
                if k in out:
                    raise Stop(2, "IN: rerun plan has cell {} twice".format(k))
                out[k] = r
    return out


def check_b1(cal, plan):
    hdr("B1  same beta as the 50000 cell (calprec2 against the rerun plan)")
    betas, labels, bad = {}, {}, []
    for c in PR.cells():
        rec = cal.get((c[1], c[2], c[3], c[4], float(c[5])))
        pr = plan.get(c)
        if rec is None or not rec.get("beta"):
            bad.append("{}: no calprec2 beta".format(c))
            continue
        b = repr(float(rec["beta"]))
        if pr is None:
            bad.append("{}: not in the rerun plan".format(c))
        elif pr["beta"] != b or pr["J_inf"] != "50000" or pr["M"] != str(M):
            bad.append("{}: calprec2 {} plan {} (J_inf {}, M {})".format(c, b, pr["beta"], pr["J_inf"], pr["M"]))
        betas[c], labels[c] = b, rec.get("label", "")
    for x in bad[:20]:
        say("  B1 FAIL " + x)
    if bad:
        raise Stop(2, "B1: {} cell(s) whose beta differs from the 50000 cell's".format(len(bad)))
    say("  B1 PASS  {} cells, every beta equal to the rerun plan's".format(len(betas)))
    return betas, labels


def inputs(a):
    hdr("IN  inputs")
    probe, _p = PR.read_probe([os.path.abspath(x) for x in a.timing])
    cal = read_betas(os.path.abspath(a.beta_table))
    plan = read_plan(os.path.abspath(a.rerun_plan))
    say("  IN PASS  probe 42 units; calprec2 {} cells; rerun plan {} CONC and TAU8 cells".format(len(cal), len(plan)))
    betas, labels = check_b1(cal, plan)
    rd = {}
    for u in JP.UNITS:
        rd[u[2]] = max(rd.get(u[2], 0.0), probe[u][1])
    wd = dict((d, int(min(a.workers, math.floor(a.budget_mb / (PR.RSS_FACTOR * r))))) for d, r in rd.items())
    hdr("W  workers per d (c5price PR)")
    for d in sorted(rd):
        say("  d {:>2}: R_d {:.1f} MB, workers {}, G-RSS flag above {:.0f} MB".format(
            d, rd[d], wd[d], a.budget_mb / max(wd[d], 1)))
    if min(wd.values()) < 1:
        raise Stop(2, "W: a d with no worker inside the budget")
    return probe, betas, labels, wd


def order_id(c, rep):
    """c5price's task id, which S2 orders by."""
    return "{}|{}|{}|{}|{}|{}|{}".format(c[0], c[1], c[2], c[3], c[4], c[5], rep)


def make_tasks(probe, betas, labels, wd, kind):
    tasks = []
    for c in PR.cells():
        u = (c[1], c[2], c[3])
        for rep in range(M):
            k, bk = keys_of(c, rep, kind)
            tasks.append({"tid": "{}|{}".format(OWNER[c[0]][0], key_str(k)), "phase": OWNER[c[0]][0], "n": J_INF,
                          "rep": rep, "c": (c[1], c[2], c[3], c[4], c[5]), "cell5": c, "row": OWNER[c[0]][0],
                          "unit": u, "d": c[3], "key": k, "boot": bk, "beta_s": betas[c], "beta": float(betas[c]),
                          "label": labels[c], "wall": probe[u][0], "load": probe[u][0] / wd[c[3]],
                          "oid": order_id(c, rep)})
    return tasks


def assign(tasks, k):
    by = dict((t["oid"], t) for t in tasks)
    loads = sorted(((t["oid"], t["load"]) for t in tasks), key=lambda z: (-z[1], z[0]))
    sh = PR.assign(loads, k)
    out = {}
    for i, s in enumerate(sh):
        out[i] = [by[x] for x in s[2]]
    return out, [s[1] for s in sh]


# ----------------------------------------------------------------------
# the task (a forked child of calprec2's scheduler)
# ----------------------------------------------------------------------

def task_c5(t):
    row = C2.base_row(t)
    c = t["cell5"]
    row.update({"row": t["row"], "module": c[1], "objective": c[2], "d": c[3], "law": c[4], "tau0": repr(c[5]),
                "jinf": J_INF, "jlist": ";".join(str(J) for J in JLIST), "K": int(round(T_END / RL.DT)),
                "beta": t["beta_s"], "cal_label": t["label"], "seed_key": key_str(t["key"]),
                "boot_key": key_str(t["boot"]), "order_id": t["oid"],
                "pred_rss_mb": "{:.1f}".format(t.get("pred", 0.0)), "workers_group": t.get("wg", "")})
    t0 = time.time()
    try:
        mod = cp.MODS[c[1]]
        seed = np.random.SeedSequence(list(t["key"]))
        o, d, K = c[2], c[3], int(round(T_END / RL.DT))
        if c[1] == "mechanism":
            E, le0, lem = mod.one_realisation(o, t["beta"], d, c[4], RL.SIGMA_ISO, RL.DT, K, J_INF, JLIST, seed)
            ex = {"le0": le0, "le_min": lem}
        else:
            out = mod.one_realisation(o, d, c[5], t["beta"], RL.SIGMA_ISO, RL.DT, K, J_INF, JLIST, seed)
            E, le0 = out[0], out[1]
            ex = {"le0": out[1], "le_mean": out[2], "le_min": out[3]}
        E_json = json.dumps(dict((str(J), repr(float(E[J]))) for J in JLIST), sort_keys=True)
        del E
        ratios, ref, f1, le_rd = rl.audit_one(rl_cell(c), np.random.SeedSequence(list(t["key"])), t["beta"],
                                              float(le0))
        row.update({"E_json": E_json,
                    "extras_json": json.dumps(dict((k, repr(float(v))) for k, v in ex.items()), sort_keys=True),
                    "le0": repr(float(le0)), "le_redraw": repr(float(le_rd)), "F1": "ok" if f1 else "F1 FAILED",
                    "audit_ref": repr(float(ref)),
                    "audit_ratios": json.dumps(dict((str(J), repr(float(v))) for J, v in sorted(ratios.items()))),
                    "end": "ok", "error": ""})
    except Exception as e:                                       # noqa: BLE001 (written as an error row)
        row.update({"error": "{}: {}".format(type(e).__name__, e), "end": "err"})
    row["wall_s"] = "{:.3f}".format(time.time() - t0)
    row["rss_mb"] = "{:.1f}".format(C2.rss_mb())
    return row


C2.TASKS[TASK_FN] = task_c5


# ----------------------------------------------------------------------
# header, params, resume, execution
# ----------------------------------------------------------------------

def hashes():
    return [("script_sha256", "script  ", os.path.abspath(__file__)), ("jinfprobe_sha256", "jinfprobe.py", JP.__file__),
            ("c5price_sha256", "c5price.py", PR.__file__), ("calprec2_sha256", "calprec2.py", C2.__file__),
            ("costprobe2_sha256", "costprobe2.py", cp.__file__), ("rerunlib_sha256", "rerunlib.py", RL.__file__)]


def base(x):
    return os.path.basename(x.rstrip("/"))


def header(a, mode, shard, nshards):
    hdr("CBO-GAP c5run  (ledger N45, C5: rows CONC-X and TAU8-X)  mode {}".format(mode))
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {}".format(a.workers))
    for _k, label, path in hashes():
        say("  {} sha256 {}".format(label, sha256_of(path)))
    say("  mode     {}   shard {} of {}".format(mode, shard, nshards))
    say("  timing   {}".format(",".join(base(x) for x in a.timing)))
    say("  beta table {}".format(base(a.beta_table)))
    say("  rerun plan {}".format(base(a.rerun_plan)))
    say("  design   288 cells (CONC-X 144, TAU8-X 144), M {}, J_inf {}, J {}".format(
        M, J_INF, ",".join(str(J) for J in JLIST)))
    say("  dynamics archived one_realisation; sigma {}; dt {}; K {}; law per cell".format(
        RL.SIGMA_ISO, RL.DT, int(round(T_END / RL.DT))))
    say("  seeds    SeedSequence((ENTROPY {}, kind, owner 21 CONC-X / 22 TAU8-X, rerunlib.coord_fields, rep)); "
        "kind {} run, {} bootstrap, {} smoke, {} drill".format(rl.ENTROPY, KIND_RUN, KIND_BOOT, KIND_SMOKE, KIND_DRILL))
    say("  budget   {:.0f} MB for concurrent tasks".format(a.budget_mb))


def params_rows(a, mode, shard, nshards, kind, stop):
    rows = [["mode", mode], ["shard", str(shard)], ["nshards", str(nshards)], ["workers", str(a.workers)],
            ["stop_after", repr(float(stop))], ["budget_mb", repr(float(a.budget_mb))], ["kind", str(kind)]]
    rows += [[k, sha256_of(p)] for k, _l, p in hashes()]
    rows += [["timing", ",".join(base(x) for x in a.timing)], ["beta_table", base(a.beta_table)],
             ["rerun_plan", base(a.rerun_plan)], ["python", platform.python_version()], ["numpy", np.__version__],
             ["resume_from", a.resume_from or ""]]
    return rows


def read_resume(folders, want, mine):
    store = {}
    for f in folders:
        rels = JP.verified(f)
        pp = [r for r in rels if os.path.basename(r) == PARAMS_CSV]
        rr = [r for r in rels if os.path.basename(r) == ROWS_CSV]
        if len(pp) != 1 or len(rr) != 1:
            raise Stop(2, "RS: {}: expected one {} and one {}".format(f, PARAMS_CSV, ROWS_CSV))
        pr = JP.read_kv(os.path.join(f, pp[0]))
        bad = sorted(k for k in want if pr.get(k) != want[k])
        if bad:
            raise Stop(2, "RS: {}: parameters differ from this job's in {} (rule 17)".format(f, bad))
        rows, nok = 0, 0
        with io.open(os.path.join(f, rr[0]), "r", newline="", encoding="utf-8") as fh:
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
        say("  read {}: shard {} of {}, {} rows, {} complete".format(f, pr.get("shard"), pr.get("nshards"), rows, nok))
    return store


def new_outdir(mode, shard, nshards):
    tag = "" if nshards == 1 else "-s{}of{}".format(shard, nshards)
    out = os.path.join(OUTROOT, "c5run-{}-{}{}".format(mode, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), tag))
    os.makedirs(out)
    return out


def timing_of(a, mine):
    to = max(TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR * max(t["wall"] for t in mine))
    stop = a.stop_after if a.stop_after is not None else min(C2.STOP_AFTER_DEFAULT, C2.KAGGLE_CAP_S - to - 600.0)
    return to, stop


def execute(a, mode, shard, nshards, mine, wd, kind):
    to, stop = timing_of(a, mine)
    hdr("T1, STOP, G-STOP")
    say("  TIMEOUT_S = {:.0f} s  (max({:.0f}, {:.0f} x largest measured wall {:.1f} s))".format(
        to, TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR, max(t["wall"] for t in mine)))
    say("  --stop-after {:.0f} s{} + TIMEOUT_S {:.0f} s = {:.0f} s   cap {:.0f} s".format(
        stop, " (auto)" if a.stop_after is None else "", to, stop + to, C2.KAGGLE_CAP_S))
    if stop <= 0 or stop + to > C2.KAGGLE_CAP_S:
        raise Stop(2, "G-STOP: --stop-after + TIMEOUT_S exceeds the 12-hour cap")
    say("  G-STOP PASS")
    store = {}
    if a.resume_from:
        hdr("RS  resume (CLAUDE.md rule 17)")
        want = dict((k, v) for k, v in params_rows(a, mode, shard, nshards, kind, stop) if k in RESUME_KEYS)
        store = read_resume([os.path.abspath(x) for x in a.resume_from.split(",") if x], want,
                            set(t["tid"] for t in mine))
        say("  {} complete task(s) read; they are skipped".format(len(store)))
    out = new_outdir(mode, shard, nshards)
    with io.open(os.path.join(out, PARAMS_CSV), "x", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(params_rows(a, mode, shard, nshards, kind, stop))
    say("\n  run dir  {}".format(out))
    o = C2.Out(os.path.join(out, ROWS_CSV), COLS)
    runner = C2.Runner(a.workers, to, o, store, stop_after=stop)
    hdr("Tasks, in groups by d  (W)")
    try:
        for d in sorted(set(t["d"] for t in mine)):
            gts = sorted([t for t in mine if t["d"] == d], key=lambda t: (-t["load"], t["oid"]))
            w = min(a.workers, wd[d])
            for t in gts:
                t["wg"], t["pred"] = w, a.budget_mb / w
            C2.RSS_BUDGET_MB = a.budget_mb / w
            say("  group d {}: {} task(s), workers {}, G-RSS flag above {:.0f} MB".format(d, len(gts), w,
                                                                                    a.budget_mb / w))
            runner.workers = w
            runner.run([(TASK_FN, t) for t in gts], "d{}".format(d))
            if runner.stopped:
                break
    finally:
        o.close()
    done = [r for r in runner.store.values() if r.get("end") == "ok"]
    f1bad = sum(1 for r in runner.store.values() if r.get("F1") == "F1 FAILED")
    flags = sum(1 for r in runner.store.values() if r.get("rss_flag"))
    say("\n" + "=" * 96)
    say("tasks run by this job: {}   task execution {:.0f} s".format(runner.ran, runner.elapsed()))
    say("complete rows, this job and resumed: {} of {}".format(len(done), len(mine)))
    say("largest per-task peak RSS {:.1f} MB; G-RSS flags {}".format(
        max([float(r["rss_mb"]) for r in done] or [float("nan")]), flags))
    say("F1 failures: {}".format(f1bad))
    if runner.stopped:
        say("STOPPED by --stop-after {:.0f} s. Resume this shard from this folder.".format(stop))
    else:
        say("not stopped: every task ran")
    say("errored or timed-out tasks: {}".format(runner.errors))
    say("files  {}".format(out))
    say("=" * 96)
    code = 0
    if runner.stopped:
        code = 5
    if f1bad:
        code = 3
    if runner.errors:
        code = 4
    return code, runner.store


# ----------------------------------------------------------------------
# modes
# ----------------------------------------------------------------------

def mode_plan(a):
    header(a, "plan", 0, a.nshards)
    probe, betas, labels, wd = inputs(a)
    tasks = make_tasks(probe, betas, labels, wd, KIND_RUN)
    keys = set(t["key"] for t in tasks)
    say("\n  tasks {} ({} distinct keys, {} distinct bootstrap keys)".format(
        len(tasks), len(keys), len(set(t["boot"] for t in tasks))))
    if len(keys) != len(tasks):
        raise Stop(2, "K1: duplicate keys")
    hdr("S2  shards (c5price's rule; target {:.0f} s)".format(TARGET_S))
    pick = None
    for k in range(1, a.kmax + 1):
        mx = max(assign(tasks, k)[1])
        if mx <= TARGET_S:
            pick = k
            break
    say("  smallest K at the target: {}".format(pick))
    say("  S2 {}  (--nshards {})".format("PASS" if pick == a.nshards else "FAIL", a.nshards))
    shards, loads = assign(tasks, a.nshards)
    for i in range(a.nshards):
        to = max(TIMEOUT_FLOOR, C2.TIMEOUT_FACTOR * max(t["wall"] for t in shards[i]))
        say("    shard {:>3}: {:>3} tasks, load {:>7.0f} s, T1 {:>6.0f} s, auto --stop-after {:>6.0f} s".format(
            i, len(shards[i]), loads[i], to, min(C2.STOP_AFTER_DEFAULT, C2.KAGGLE_CAP_S - to - 600.0)))
    hdr("E2E  end-to-end estimate (S2 loads under perfect scaling + {:.0f} s per shard; not a measurement)".format(
        OVERHEAD_S))
    dur = [ld + OVERHEAD_S for ld in loads]
    for n in range(1, 6):
        slots = [0.0] * n
        heapq.heapify(slots)
        for x in dur:
            heapq.heappush(slots, heapq.heappop(slots) + x)
        mk = max(slots)
        say("  {} kernel(s) in flight: {:>9.0f} s = {:>6.1f} days".format(n, mk, mk / 86400.0))
    hdr("c5run.py plan done, exit {}  (nothing written)".format(0 if pick == a.nshards else 2))
    return 0 if pick == a.nshards else 2


def mode_smoke(a):
    header(a, "smoke", 0, 1)
    JP.gates()
    probe, betas, labels, wd = inputs(a)
    tasks = make_tasks(probe, betas, labels, wd, KIND_SMOKE)
    pick = []
    for row in ("CONC-X", "TAU8-X"):
        t = min((t for t in tasks if t["row"] == row and t["rep"] == 0), key=lambda t: (t["wall"], t["oid"]))
        for m in ("a", "b"):
            tt = dict(t)
            tt["tid"] = t["tid"] + "|" + m
            pick.append(tt)
    code, store = execute(a, "smoke", 0, 1, pick, wd, KIND_SMOKE)
    hdr("SMOKE  the two members of each key, bitwise")
    ok = code == 0
    by = {}
    for tid, r in store.items():
        by.setdefault(tid.rsplit("|", 1)[0], []).append(r)
    for b, rs in sorted(by.items()):
        same = (len(rs) == 2 and all(r.get("end") == "ok" and r.get("F1") == "ok" for r in rs)
                and rs[0]["E_json"] == rs[1]["E_json"])
        ok = ok and same
        say("  {}  {}".format(b, "identical, F1 ok" if same else "DIFFER, errored or F1 failed"))
    if len(by) != 2:
        ok = False
    say("SMOKE {}".format("PASS" if ok else "FAIL"))
    return 0 if ok else (4 if code == 4 else 3)


def mode_drill(a):
    header(a, "drill", 0, 1)
    JP.gates()
    probe, betas, labels, wd = inputs(a)
    tasks = make_tasks(probe, betas, labels, wd, KIND_DRILL)
    d2 = sorted(set(t["unit"] for t in tasks if t["row"] == "CONC-X" and t["d"] == 2),
                key=lambda u: (probe[u][0], u))
    pick = sorted([t for t in tasks if t["unit"] == d2[0] and t["cell5"][5] == 0.5 and t["rep"] < 6],
                  key=lambda t: t["oid"])
    say("  DRILL  unit {} (measured wall {:.1f} s), {} tasks".format(JP.unit_id(d2[0]), probe[d2[0]][0], len(pick)))
    if len(pick) != DRILL_N:
        raise Stop(2, "DRILL: {} tasks, expected {}".format(len(pick), DRILL_N))
    return execute(a, "drill", 0, 1, pick, wd, KIND_DRILL)[0]


def mode_run(a):
    header(a, "run", a.shard, a.nshards)
    JP.gates()
    probe, betas, labels, wd = inputs(a)
    tasks = make_tasks(probe, betas, labels, wd, KIND_RUN)
    shards, loads = assign(tasks, a.nshards)
    mine = shards[a.shard]
    say("  shard {} of {}: {} tasks, S2 load {:.0f} s".format(a.shard, a.nshards, len(mine), loads[a.shard]))
    return execute(a, "run", a.shard, a.nshards, mine, wd, KIND_RUN)[0]


def main():
    ap = argparse.ArgumentParser(description="C5 trajectories, rows CONC-X and TAU8-X (ledger N45)")
    ap.add_argument("--mode", choices=("plan", "smoke", "drill", "run"), required=True)
    ap.add_argument("--timing", default=",".join(DEFAULT_TIMING), help="comma-joined jinfprobe run folders")
    ap.add_argument("--beta-table", default=DEFAULT_BETA)
    ap.add_argument("--rerun-plan", default=DEFAULT_PLAN)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-mb", type=float, default=BUDGET_MB)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--kmax", type=int, default=400)
    ap.add_argument("--stop-after", type=float, default=None)
    ap.add_argument("--resume-from", default="")
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    a.timing = [x for x in a.timing.split(",") if x]
    if len(a.timing) != 3 or len(set(os.path.abspath(x) for x in a.timing)) != 3:
        raise Stop(2, "--timing takes the three jinfprobe run folders")
    if a.workers < 1 or a.budget_mb <= 0 or a.nshards < 1 or not (0 <= a.shard < a.nshards):
        raise Stop(2, "workers, budget-mb, shard or nshards out of range")
    if a.resume_from and a.mode not in ("run", "drill"):
        raise Stop(2, "--resume-from is for run and drill only")
    if a.mode in ("smoke", "drill") and a.nshards != 1:
        raise Stop(2, "{} is one job".format(a.mode))
    if a.mode == "drill" and a.stop_after is None:
        raise Stop(2, "drill needs --stop-after")
    if a.mode == "plan":
        return mode_plan(a)
    if a.mode == "smoke":
        return mode_smoke(a)
    if a.mode == "drill":
        return mode_drill(a)
    return mode_run(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
