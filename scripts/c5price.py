"""
c5price.py  --  CBO-GAP: the price and shard count of the C5 design (the
window extension, with C6's second reading folded in), from the walls and
peak RSS that jinfprobe MEASURED at J_inf 4000000  (ledger N45, "C5
DESIGN"; CLAUDE.md rule 6; Rahul's instruction 2026-11-01)

LAPTOP. Reads three committed jinfprobe run folders; WRITES NOTHING. No
trajectory, no seed, no random number: it prices a design and prints a
schedule. It decides no scientific question.

THE DESIGN IT PRICES (fixed in ledger N45 before this script was written)
  Cells: every cell of CONC (costprobe2.GRID["CONC"]: six objectives x d 2,
  5, 10, 40 x laws centred, mix-0.1 x tau_0 0.5, 0.1, 0.01: 144) and of
  TAU8 (GRID["TAU8"]: six objectives x d 5, 10, 40 x eight tau_0: 144);
  288 cells. M = 15 realizations per cell (the rows' own M). One J_inf,
  4000000, for every cell; J window JEXT(4000000) = J10 then 10000, 20000,
  ..., 320000, then 400000 (jinfprobe.jext). A task is one coupled
  realization of one cell: 288 x 15 = 4320 tasks.

PRE-SPECIFIED RULES (fixed 2026-11-01, before first execution)
  IN  The three folders (--folder, repeated) each verify against their
      sha256.txt and hold one jinfprobe_params.csv with mode run, kind 91,
      the full ladder, and one script sha256 common to all three; their
      complete rows are 252 distinct tasks, every unit of jinfprobe.UNITS at
      every ladder size. Exit 2 otherwise.
  PW  TASK WALL = the measured wall of the task's unit (module, objective,
      d) at J_inf 4000000 in the probe. Not modelled: the probe ran the
      centred law at the tau_0 0.01 beta, one realization per unit; that
      wall does not depend on beta, law or seed is an assumption
      (costprobe2 A5, A6), not tested. STOP and resume cover a miss.
      Worked example: unit wall 1500.0 s: each of its 15 x (number of
      cells of that unit) tasks is priced at 1500.0 s.
  PR  WORKERS PER d = min(--workers, floor(--budget-mb / (1.10 x R_d))),
      R_d the largest measured 4000000 peak RSS over the probe's units at
      that d. The factor 1.10 covers the beta, law and seed the probe did
      not vary (the probe's own 4000000 rows came within a few percent of
      R1's prediction, in both directions). Worked example: R_d 10000 MB,
      budget 24000: 24000 / 11000 = 2.18, 2 workers; R_d 2500 MB: 8.7, 4
      (capped at --workers 4).
  FEAS EVERY TASK FITS A SESSION iff, for every unit, workers_d >= 1 and
      5 x wall (calprec2's T1 timeout) + 600 s <= 43200 s, the 12-hour cap.
      FEASIBLE or NOT FEASIBLE is printed, with every unit that fails. On
      NOT FEASIBLE the units that fit are priced alone and labelled "the
      largest runnable version".
  PS  SHARDS. Load of a task = wall / workers_d (elapsed under perfect
      scaling, as jinfprobe S1). Tasks sorted by (-load, task id) go one by
      one to the shard with the smallest load so far (ties: lowest index).
      Printed: the largest shard load for K on a grid from 1 to --kmax, and
      the smallest K whose largest load is at most --target (default
      10800 s, half of calprec2's 21600 s ceiling, the target jinfprobe
      used); for that K, per shard its task count, load, T1 = max(600, 5 x
      largest wall) and auto --stop-after = min(36000, 43200 - T1 - 600).
      Worked example: 10 tasks of load 1000 s and target 2500: K 4 gives
      loads 3000, 3000, 2000, 2000, K 5 gives 2000 each: K = 5.
  NULL RATE (every rule above): none is a statistical criterion. IN and
      FEAS are deterministic checks; PW, PR and PS schedule work. Nothing
      here fires by chance.

THE TOTALS PRINTED
  Tasks, the sum of task walls (task-seconds), the sum of loads (session-
  seconds under perfect scaling), per (row, d), and overall.

HOW TO RUN (repository root)
    python -B scripts/c5price.py --folder runs/A --folder runs/B --folder runs/C
Python 3.8 to 3.13, NumPy only. Exit 0 on a printed price (FEASIBLE or
not); 2 on an input problem.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import heapq                                                    # noqa: E402
import io                                                       # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jinfprobe as JP                                          # noqa: E402

cp = JP.cp
Stop = JP.Stop
say, hdr = JP.say, JP.hdr

J_INF = 4000000
M = 15
BUDGET_MB = 24000.0
RSS_FACTOR = 1.10
TARGET_S = 10800.0
CAP_S = 43200.0
T1_FACTOR = 5.0
T1_FLOOR = 600.0
STOP_DEFAULT = 36000.0


def cells():
    """(row, module, objective, d, law, tau) for every C5 cell."""
    out = []
    g = cp.GRID["CONC"]
    for o in g["objs"]:
        for d in g["dims"]:
            for law in g["laws"]:
                for t in g["taus"]:
                    out.append(("CONC", "mechanism", o, d, law, t))
    g = cp.GRID["TAU8"]
    for o in g["objs"]:
        for d in g["dims"]:
            for t in g["taus"]:
                out.append(("TAU8", "boundary", o, d, "centred", t))
    return out


def read_probe(folders):
    """IN. {unit: (wall, rss)} at J_INF, and the folders' params."""
    store, prms = {}, []
    for f in folders:
        rels = JP.verified(f)
        pp = [r for r in rels if os.path.basename(r) == JP.PARAMS_CSV]
        rr = [r for r in rels if os.path.basename(r) == JP.ROWS_CSV]
        if len(pp) != 1 or len(rr) != 1:
            raise Stop(2, "IN: {}: expected one {} and one {}".format(f, JP.PARAMS_CSV, JP.ROWS_CSV))
        pr = JP.read_kv(os.path.join(f, pp[0]))
        if pr.get("mode") != "run" or pr.get("kind") != str(JP.K_RUN) or \
                pr.get("ladder") != ",".join(str(n) for n in JP.LADDER):
            raise Stop(2, "IN: {}: not a jinfprobe run folder of the full ladder".format(f))
        prms.append(pr)
        with io.open(os.path.join(f, rr[0]), "r", newline="", encoding="utf-8") as fh:
            for x in csv.DictReader(fh):
                if x.get("end") != "ok":
                    continue
                if x["tid"] in store:
                    raise Stop(2, "IN: task {} complete in two folders".format(x["tid"]))
                store[x["tid"]] = x
        say("  read {}: shard {} of {}, script sha256 {}".format(
            os.path.basename(f.rstrip("/")), pr.get("shard"), pr.get("nshards"), pr.get("script_sha256")))
    if len(set(p.get("script_sha256") for p in prms)) != 1:
        raise Stop(2, "IN: the folders differ in script sha256")
    want = set("JP{}|{}|{}".format(JP.K_RUN, JP.unit_id(u), n) for u in JP.UNITS for n in JP.LADDER)
    if set(store) != want:
        raise Stop(2, "IN: complete tasks {} of {}; missing {}".format(
            len(set(store) & want), len(want), sorted(want - set(store))[:5]))
    say("  IN PASS  {} complete tasks, every unit at every ladder size".format(len(store)))
    out = {}
    for u in JP.UNITS:
        x = store["JP{}|{}|{}".format(JP.K_RUN, JP.unit_id(u), J_INF)]
        out[u] = (float(x["wall_s"]), float(x["rss_mb"]))
    return out, prms


def assign(loads, k):
    """PS. loads: [(tid, load)] sorted. Returns the per-shard (count, load, tids)."""
    sh = [[0, 0.0, []] for _ in range(k)]
    heap = [(0.0, j) for j in range(k)]
    for tid, ld in loads:
        cur, i = heapq.heappop(heap)
        sh[i][0] += 1
        sh[i][1] += ld
        sh[i][2].append(tid)
        heapq.heappush(heap, (sh[i][1], i))
    return sh


def largest(args):
    loads, k = args
    return k, max(s[1] for s in assign(loads, k))


def price(tasks, probe, wd, a, label):
    hdr("PS  shards: {}".format(label))
    loads = sorted(((t["tid"], probe[t["unit"]][0] / wd[t["d"]]) for t in tasks), key=lambda z: (-z[1], z[0]))
    walls = dict((t["tid"], probe[t["unit"]][0]) for t in tasks)
    tot = {}
    for t in tasks:
        g = tot.setdefault((t["row"], t["d"]), [0, 0.0, 0.0])
        g[0] += 1
        g[1] += probe[t["unit"]][0]
        g[2] += probe[t["unit"]][0] / wd[t["d"]]
    say("  {:<6} {:>3} {:>7} {:>16} {:>18}".format("row", "d", "tasks", "task-seconds", "session-seconds"))
    for k in sorted(tot):
        say("  {:<6} {:>3} {:>7} {:>16.0f} {:>18.0f}".format(k[0], k[1], tot[k][0], tot[k][1], tot[k][2]))
    say("  {:<10} {:>7} {:>16.0f} {:>18.0f}".format("all", sum(v[0] for v in tot.values()),
                                                   sum(v[1] for v in tot.values()), sum(v[2] for v in tot.values())))
    ks = sorted(set([k for k in range(1, 21)] + list(range(20, a.kmax + 1, 5)) + [a.kmax]))
    pool = multiprocessing.Pool(a.workers)
    try:
        res = dict(pool.map(largest, [(loads, k) for k in ks]))
    finally:
        pool.close()
        pool.join()
    for k in ks:
        say("  K {:>4}: largest shard {:>9.0f} s = {:>5.1f}% of the 43200 s cap".format(k, res[k], 100.0 * res[k] / CAP_S))
    pick = None
    prev = 0
    for k in ks:
        if res[k] <= a.target:
            for j in range(prev + 1, k + 1):
                if (res[j] if j in res else largest((loads, j))[1]) <= a.target:
                    pick = j
                    break
            break
        prev = k
    if pick is None:
        say("  no K up to {} meets the target {:.0f} s".format(a.kmax, a.target))
        return
    sh = assign(loads, pick)
    say("  at the target {:.0f} s: K = {}".format(a.target, pick))
    for i, s in enumerate(sh):
        to = max(T1_FLOOR, T1_FACTOR * max(walls[x] for x in s[2]))
        say("    shard {:>3}: {:>4} tasks, load {:>7.0f} s, T1 {:>6.0f} s, auto --stop-after {:>6.0f} s".format(
            i, s[0], s[1], to, min(STOP_DEFAULT, CAP_S - to - 600.0)))


def main():
    ap = argparse.ArgumentParser(description="price of the C5 design from jinfprobe's measured walls (writes nothing)")
    ap.add_argument("--folder", action="append", default=[], help="a jinfprobe run folder; repeat for each")
    ap.add_argument("--workers", type=int, default=4, help="Kaggle workers per session and the local pool size")
    ap.add_argument("--budget-mb", type=float, default=BUDGET_MB)
    ap.add_argument("--target", type=float, default=TARGET_S)
    ap.add_argument("--kmax", type=int, default=400)
    a = ap.parse_args()
    if a.workers < 1 or a.budget_mb <= 0 or a.target <= 0 or a.kmax < 1:
        raise Stop(2, "workers, budget-mb, target or kmax out of range")
    if not a.folder:
        raise Stop(2, "--folder is required, once per jinfprobe run folder")
    folders = [os.path.abspath(x) for x in a.folder]
    if len(set(folders)) != len(folders):
        raise Stop(2, "a folder is given twice")
    hdr("CBO-GAP c5price  (ledger N45, C5 design; rule 6)  --  writes nothing, draws no random number")
    say("  python   {}".format(platform.python_version()))
    say("  numpy    {}".format(np.__version__))
    say("  platform {}".format(platform.platform()))
    say("  workers  {} (per Kaggle session in PR; local pool for the K sweep)".format(a.workers))
    say("  script   sha256 {}".format(JP.sha256_of(os.path.abspath(__file__))))
    say("  jinfprobe.py sha256 {}".format(JP.sha256_of(JP.__file__)))
    say("  design   CONC + TAU8, {} cells, M {}, J_inf {}, J window {}".format(
        len(cells()), M, J_INF, ",".join(str(J) for J in JP.jext(J_INF))))
    say("  budget   {:.0f} MB, RSS factor {:.2f}, target {:.0f} s, kmax {}".format(a.budget_mb, RSS_FACTOR, a.target,
                                                                              a.kmax))
    say("  seeds    none (no random number is drawn)")
    hdr("IN  the probe")
    probe, _p = read_probe(folders)
    hdr("PW, PR  per unit at J_inf {} (measured)".format(J_INF))
    rd = {}
    for u in JP.UNITS:
        rd[u[2]] = max(rd.get(u[2], 0.0), probe[u][1])
    wd = dict((d, int(min(a.workers, math.floor(a.budget_mb / (RSS_FACTOR * r))))) for d, r in rd.items())
    say("  {:<26} {:>10} {:>10}".format("unit", "wall s", "RSS MB"))
    for u in JP.UNITS:
        say("  {:<26} {:>10.3f} {:>10.1f}".format(JP.unit_id(u), probe[u][0], probe[u][1]))
    for d in sorted(rd):
        say("  d {:>2}: R_d {:.1f} MB, x {:.2f} = {:.1f} MB, workers {}".format(d, rd[d], RSS_FACTOR, RSS_FACTOR * rd[d],
                                                                             wd[d]))
    hdr("FEAS  does every task fit one session")
    bad = []
    for u in JP.UNITS:
        if wd[u[2]] < 1:
            bad.append((u, "RSS x {:.2f} above the budget at one worker".format(RSS_FACTOR)))
        elif T1_FACTOR * probe[u][0] + 600.0 > CAP_S:
            bad.append((u, "5 x wall + 600 s above the 43200 s cap"))
    for u, why in bad:
        say("  NOT FITTING  {}: {}".format(JP.unit_id(u), why))
    tasks = []
    for c in cells():
        u = (c[1], c[2], c[3])
        for rep in range(M):
            tasks.append({"tid": "{}|{}|{}|{}|{}|{}|{}".format(c[0], c[1], c[2], c[3], c[4], c[5], rep),
                          "row": c[0], "unit": u, "d": c[3]})
    say("  tasks {} ({} cells x M {})".format(len(tasks), len(cells()), M))
    if not bad:
        say("  FEASIBLE: every task fits one session")
        price(tasks, probe, wd, a, "the full design")
    else:
        bu = set(u for u, _w in bad)
        keep = [t for t in tasks if t["unit"] not in bu]
        say("  NOT FEASIBLE: {} of {} tasks do not fit; the largest runnable version keeps {}".format(
            len(tasks) - len(keep), len(tasks), len(keep)))
        if keep:
            price(keep, probe, wd, a, "the largest runnable version")
    hdr("c5price.py done, exit 0  (nothing written)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as e:
        say("\nSTOP (exit {}): {}".format(e.code, e.msg))
        sys.exit(e.code)
