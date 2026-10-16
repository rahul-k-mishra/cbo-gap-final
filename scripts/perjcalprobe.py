"""
perjcalprobe.py  --  CBO-GAP round 2: what the per-J-beta experiment
                     (perjcal) costs, measured with its own archived dynamics

WHAT THIS MEASURES, IN PLAIN LANGUAGE
-------------------------------------
perjcal.py (zenodo-v1) is the experiment behind the abstract's second
result: for each ensemble size J it solves a separate beta_J on the first
J particles, so that ESS_0(J)/J equals the target at that J, and evolves
both the J-ensemble and a J_inf reference at beta_J. Every (realization,
J) pair is therefore one full reference evolution. Rahul put it in scope
on 2026-10-16 (notes/ANALYSIS_CRITERIA.md, K2) and approves its rows only
after seeing this projection.

This script times ONE call of the archived perjcal.one_J for every unit
of perjcal's archived full design, measures each call's peak RSS, and
projects the cost of running the design at its archived M. It decides
nothing about the science. It runs nothing that enters the paper: its
E values are timing by-products, not results.

perjcal is a different estimand from every fixed-beta quantity of the
rerun: beta varies with J along the fitted curve (perjcal.py docstring,
"WHAT THIS CHANGES"). Nothing here is pooled or compared with the
fixed-beta rows.

NOTHING IS REIMPLEMENTED (CLAUDE.md rule 4)
  Every probe is perjcal.one_J, imported from the archive and called
  unmodified. one_J itself imports the objectives, draw_initial,
  beta_on_ensemble and weighted_mean_and_logess from exactcal.py. This
  script writes nothing into the archive and reads it only by import and
  by hashing.

THE DESIGN PROJECTED (read from perjcal.py, checked by P0)
  6 named objectives x d in {2, 40} x tau_0 in {0.5, 0.01} x centred law
  x M = 15 realizations; J_inf 50000; J grid J10 capped at J_inf / 10;
  at each tau_0 only J >= 1 / tau_0 (perjcal.py: ten sizes at 0.5, six at
  0.01); sigma 0.2, lambda 1, dt 0.01, T 1, K 100.
  A probe UNIT is (objective, d, tau_0, J): exactly one call of one_J.
  The plan prints the number of units. Every unit is probed once.

THE COST MODEL, AND WHAT IT DOES NOT TEST
  The wall time of one_J is assumed to depend on the unit only, not on the
  seed. Check A1 gives evidence on that assumption for one unit only.
  Projection for the archived design (P5):
      core_s = M x sum over units of wall(unit) x scale
      wall_s = core_s / W
      shards = ceil(wall_s / 21600)
  W is this run's --workers. Walls are measured with up to W probes
  running at once, so they include the load of a saturated pool. Division
  by W assumes perfect scaling; scheduling gaps and the run's tail are
  ignored. 21600 s is the per-shard ceiling of costprobe2 (Rahul,
  2026-10-10).

PRE-SPECIFIED CRITERIA (fixed 2026-10-16, before first execution)
------------------------------------------------------------------
  P0  PLAN IDENTITY. The constants this script uses (objs, dims, taus, M,
      Jinf, Jgrid, lam, sigma, dt, T, init) are compared with the literal
      assignments in perjcal.py's main(): the top level of main() and the
      else branch of "if a.quick:". The source is parsed with ast; the
      quick branch is skipped. Each name must have exactly one literal
      assignment there, equal to this script's value. Two filters are
      expressions in the source and are printed as "not checked against
      source": the cap J <= Jinf // 10 and the window J >= 1.0 / tau.
      They are applied here with the same expressions.
      Worked example: perjcal.py's else branch assigns dims, taus, M =
      [2, 40], [0.5, 0.01], 15. Here DIMS = [2, 40]: ok. Had this script
      used [2, 10, 40], P0 prints "MISMATCH dims: archive [2, 40], here
      [2, 10, 40]" and exits 2.
  P1  ARCHIVE IDENTITY. perjcal.__file__ and exactcal.__file__ must lie in
      the archive directory, and each must hash to its zenodo-v1.sha256
      entry, embedded below. Otherwise exit 2.
      Worked example: perjcal.py hashing to f0b30430...574d: pass. A copy
      found elsewhere on sys.path, or one byte edited: exit 2.
  P2  SEED PASS-THROUGH AND DETERMINISM. numpy.random.SeedSequence(key) is
      passed unchanged as one_J's seed argument (one_J calls
      default_rng(seed) on it). The smallest unit is run twice with the same
      key, in two separate processes. E, beta_J and the achieved fraction
      must be bitwise identical, compared as %.17g strings. A member that
      errored or is missing is a FAIL. A P2 FAIL gives exit 3, after every
      row has been written.
      Worked example: E = 0.0012345678901234567 in both members, beta and
      achieved equal: pass. One member "err": FAIL.
  P4  MEMORY BUDGET. Each probe runs in its own fresh process. Its peak
      RSS (resource.getrusage, Linux kilobytes / 1024) must be at most
      3072 MB (costprobe2's budget, Rahul 2026-10-10). The design passes P4
      when every unit does.
      Worked example: 60, 140 and 310 MB: pass. One unit at 3100 MB:
      "EXCEEDS BUDGET", and the projection says so.
  A1  SEED DEPENDENCE OF WALL TIME (evidence, not a measurement). The unit
      with the largest proxy is run twice with two different keys
      (variants 1 and 2), queued adjacently. Neighbour load is
      uncontrolled. ratio = max(wall) / min(wall). PASS when ratio <= 1.25
      (costprobe2's A1 threshold). On FAIL, the projection is multiplied
      by the ratio and labelled "SCALED, not a bound".
      Worked example: 30.0 s and 36.0 s give 1.20: pass. 30.0 s and
      40.0 s give 1.333: fail, scale 1.333.
  A3  TIMING NOISE. The P2 pair's wall ratio is printed. Above 1.25 the A1
      verdict is labelled "noise-limited".
  A-ERR  An A1 member that errored, timed out or is missing makes A1 a
      FAIL with its error text; the projection is labelled "check
      errored" and is not scaled. Exit 4 unless P2 set 3.
  C1  ACHIEVED CONCENTRATION (reported; no decision). Each probe's
      achieved fraction over tau_0 is printed and written, as perjcal's
      own P-C1 measures it. It is a diagnostic of one call, not perjcal's
      criterion over a run.
  P5  PROJECTION, as above. Labels:
        - unscaled: "lower bound (perfect scaling; seed dependence tested
          on one unit only)";
        - scaled: "SCALED, not a bound".
      Worked example (illustrative numbers): units with a summed wall of
      2000 s, M = 15, W = 4, scale 1: core_s = 30000, wall_s = 7500,
      shards = 1. With W = 2 the same walls give wall_s = 15000, shards =
      1. With a summed wall of 10000 s and W = 2: core_s = 150000, wall_s
      = 75000, shards = 4.
      The design is NOT PROJECTED when any unit has no completed probe;
      the missing units are listed.
  T1  PER-PROBE TIMEOUT. A probe still running after --timeout seconds
      (default 7200) is terminated and written as an error row. A process
      that exits without a result is written as an error row. The default
      is a guard against a hung process, not a criterion on cost; a probe
      hitting it leaves the design NOT PROJECTED.

SEEDS
  Every stream is numpy.random.default_rng(SeedSequence(key)) at full
  width (ledger N16). The key is
      (ENTROPY 20261016, kind 91, objective code, d, tau_0 x 1e6, J,
       variant)
  objective code = the index in OBJ6 below; variant 0 for main probes, 99
  for both members of the P2 pair (their duplication is the test), 1 and
  2 for the A1 pair. Kind 91 is used by no other script (kinds in use: 1,
  2, 11, 12, 31 to 35, 41 to 43, 51, 61 to 67; 71 and 81 are reserved for
  the rerun under ENTROPY 20261016). The plan refuses duplicate keys
  outside the P2 pair. Every key is written in full in the results CSV.

MODES
  --plan    P1, P0, the unit list, its size and the queue. No dynamics,
            nothing written.
  --smoke   The P2 pair only. Tests imports, P1, P2 and the plumbing.
            Projects nothing.
  (default) The P2 pair, the A1 pair and every unit; then P4, A1, A3 and
            P5.

OUTPUT (new folder <outdir>/perjcalprobe-<timestamp>[-smoke]/, every file
        opened "x", every row flushed and fsynced)
  perjcalprobe_params.csv      the parameters of the run
  perjcalprobe_results.csv     one row per probe: task id, check, member,
                               unit, key, beta_J (repr), achieved fraction
                               (repr), achieved / tau_0, E (%.17g), wall,
                               peak RSS, pid, error, end marker
  perjcalprobe_projection.csv  (default mode) P2, P4, A1, A3 and P5

HOW TO RUN (from the repository root, venv active)
    python scripts/perjcalprobe.py --plan
    python scripts/perjcalprobe.py --workers 2 --smoke
    python scripts/perjcalprobe.py --workers 2
  --archive PATH and --outdir PATH are resolved by scripts/cbopaths.py.
  Exit codes: 0 completed, whatever the verdicts; 2 setup error (P0, P1,
  an import); 3 P2 failed; 4 A1 errored (A-ERR).

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

# The archived modules pin BLAS to one thread before importing numpy; here
# numpy may be imported first, so the same variables are set here, before
# numpy, and printed in the header (as costprobe2.py does).
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import ast                                                      # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import hashlib                                                  # noqa: E402
import math                                                     # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True

import cbopaths                                                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = cbopaths.archive_path(ROOT)
OUTROOT = cbopaths.output_root(ROOT)
if not os.path.isdir(ARCH):
    sys.stderr.write("setup error: archive not found at {}\n".format(ARCH))
    sys.stderr.write("pass --archive <path> or set CBOGAP_ARCHIVE\n")
    sys.exit(2)
sys.path.insert(0, ARCH)

try:
    import exactcal                                             # noqa: E402
    import perjcal                                              # noqa: E402
except Exception as exc:                                        # pragma: no cover
    sys.stderr.write("setup error: cannot import from the archive: {}\n".format(exc))
    sys.exit(2)

# Copied from zenodo-v1.sha256 (lines 19 and 40). P1.
ARCHIVE_SHA256 = {
    "exactcal": "b17e1be3c024ec4de0d88a6a50dfde557ea6552d50bd0cb5ed9521ab4012a813",
    "perjcal": "f0b304306d3afc877647167f30bb77287d57e39fdf009b08b0858a91993a574d",
}
MODS = {"exactcal": exactcal, "perjcal": perjcal}

# perjcal.py main(), non-quick branch; checked by P0.
OBJ6 = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
CONST = {
    "objs": OBJ6,
    "dims": [2, 40],
    "taus": [0.5, 0.01],
    "M": 15,
    "Jinf": 50000,
    "Jgrid": [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000],
    "lam": 1.0,
    "sigma": 0.2,
    "dt": 0.01,
    "T": 1.0,
    "init": "centred",
}
K = int(round(CONST["T"] / CONST["dt"]))
JLIST = [J for J in CONST["Jgrid"] if J <= CONST["Jinf"] // 10]

ENTROPY = 20261016
KIND = 91
RSS_BUDGET_MB = 3072.0
RATIO_MAX = 1.25
SHARD_CEIL_S = 21600.0
LB_LABEL = "lower bound (perfect scaling; seed dependence tested on one unit only)"
SCALED_LABEL = "SCALED, not a bound"
CAVEAT = "neighbour load uncontrolled; evidence, not a measurement"

RES_COLS = ["task_id", "check", "member", "objective", "d", "tau0", "J", "seed_key",
            "beta_J", "achieved_frac", "achieved_over_tau0", "E", "wall_s",
            "peak_rss_mb", "pid", "error", "end"]


def hdr(s):
    print("\n" + "-" * 96)
    print(s)
    print("-" * 96)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# P1, P0
# --------------------------------------------------------------------------

def p1():
    ok = True
    for name, mod in sorted(MODS.items()):
        f = os.path.abspath(mod.__file__)
        inside = os.path.dirname(f) == os.path.abspath(ARCH) and f.endswith(".py")
        h = sha256_file(f) if os.path.isfile(f) else "missing"
        good = inside and h == ARCHIVE_SHA256[name]
        ok = ok and good
        print("  P1 {:<9} {}  {}  {}".format(name, f, h[:16] + "...", "ok" if good else "FAIL"))
    return ok


def _literal_assigns(stmts, out):
    """Collect name -> [values] for literal assignments in a statement list
    (not descending into nested blocks)."""
    for st in stmts:
        if not isinstance(st, ast.Assign) or len(st.targets) != 1:
            continue
        tg, val = st.targets[0], st.value
        if isinstance(tg, ast.Name):
            pairs = [(tg.id, val)]
        elif isinstance(tg, ast.Tuple) and isinstance(val, ast.Tuple) and len(tg.elts) == len(val.elts):
            pairs = [(e.id, v) for e, v in zip(tg.elts, val.elts) if isinstance(e, ast.Name)]
        else:
            continue
        for n, v in pairs:
            try:
                out.setdefault(n, []).append(ast.literal_eval(v))
            except ValueError:
                pass


def p0():
    src = open(perjcal.__file__).read()
    tree = ast.parse(src)
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
    if len(mains) != 1:
        print("  P0 FAIL: perjcal.py has {} main() functions".format(len(mains)))
        return False
    found = {}
    _literal_assigns(mains[0].body, found)
    for st in mains[0].body:
        if isinstance(st, ast.If) and "quick" in ast.dump(st.test):
            _literal_assigns(st.orelse, found)
    ok = True
    for name in sorted(CONST):
        vals = found.get(name, [])
        here = CONST[name]
        if len(vals) != 1:
            print("  P0 FAIL {:<6} {} literal assignment(s) in main()".format(name, len(vals)))
            ok = False
        elif vals[0] != here:
            print("  P0 MISMATCH {}: archive {}, here {}".format(name, vals[0], here))
            ok = False
        else:
            print("  P0 ok   {:<6} {}".format(name, here))
    print("  not checked against source (expressions): J <= Jinf // 10; J >= 1.0 / tau")
    return ok


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------

def units():
    out = []
    for tau in CONST["taus"]:
        keep = [J for J in JLIST if J >= 1.0 / tau]
        for obj in CONST["objs"]:
            for d in CONST["dims"]:
                for J in keep:
                    out.append((obj, d, tau, J))
    return out


def key_of(obj, d, tau, J, variant):
    return (ENTROPY, KIND, OBJ6.index(obj), d, int(round(tau * 1e6)), J, variant)


def proxy(u):
    obj, d, tau, J = u
    return d * (CONST["Jinf"] + J)


def build_plan(mode):
    us = units()
    smallest = min(us, key=lambda u: (proxy(u), u[3], OBJ6.index(u[0]), u[2]))
    largest = max(us, key=lambda u: (proxy(u), u[3], -OBJ6.index(u[0]), u[2]))
    tasks = []
    for m in ("a", "b"):
        tasks.append({"check": "P2", "member": m, "unit": smallest,
                      "key": key_of(*smallest, variant=99)})
    if mode == "full":
        for v, m in ((1, "a"), (2, "b")):
            tasks.append({"check": "A1", "member": m, "unit": largest,
                          "key": key_of(*largest, variant=v)})
        for u in sorted(us, key=lambda x: -proxy(x)):
            tasks.append({"check": "", "member": "", "unit": u, "key": key_of(*u, variant=0)})
    for i, t in enumerate(tasks):
        t["tid"] = i
    keys = [t["key"] for t in tasks if t["check"] != "P2"]
    if len(set(keys)) != len(keys):
        sys.stderr.write("setup error: duplicate seed keys in the plan\n")
        sys.exit(2)
    return us, tasks, smallest, largest


# --------------------------------------------------------------------------
# one probe, in its own process
# --------------------------------------------------------------------------

def run_task(t):
    obj, d, tau, J = t["unit"]
    out = dict(t)
    out.update({"beta": float("nan"), "ach": float("nan"), "E": float("nan"),
                "wall": float("nan"), "error": "", "end": "err"})
    try:
        seed = np.random.SeedSequence(list(t["key"]))
        t1 = time.time()
        E, beta, ach = perjcal.one_J(obj, d, CONST["init"], tau, J, CONST["sigma"],
                                     CONST["lam"], CONST["dt"], K, CONST["Jinf"], seed)
        out["wall"] = time.time() - t1
        out["E"], out["beta"], out["ach"] = float(E), float(beta), float(ach)
        out["end"] = "ok"
    except Exception as exc:
        out["error"] = "{}: {}".format(type(exc).__name__, exc)
    out["rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    out["pid"] = os.getpid()
    return out


def child_main(t, conn):
    try:
        conn.send(run_task(t))
    finally:
        conn.close()


def error_row(t, msg, pid):
    o = dict(t)
    o.update({"beta": float("nan"), "ach": float("nan"), "E": float("nan"),
              "wall": float("nan"), "rss": float("nan"), "pid": pid,
              "error": msg, "end": "err"})
    return o


def res_row(o):
    obj, d, tau, J = o["unit"]
    return [o["tid"], o["check"], o["member"], obj, d, repr(tau), J,
            "-".join(str(x) for x in o["key"]), repr(o["beta"]), repr(o["ach"]),
            "%.10g" % (o["ach"] / tau), "%.17g" % o["E"], "%.3f" % o["wall"],
            "%.1f" % o["rss"], o["pid"], o["error"].replace("\n", " "), o["end"]]


# --------------------------------------------------------------------------
# verdicts and projection
# --------------------------------------------------------------------------

def analyse(done, us, outdir, workers, smoke):
    code = 0
    hdr("P2  seed pass-through and determinism")
    p2 = [o for o in done if o["check"] == "P2"]
    p2_ok = (len(p2) == 2 and all(o["end"] == "ok" for o in p2) and
             len(set(("%.17g" % o["E"], "%.17g" % o["beta"], "%.17g" % o["ach"]) for o in p2)) == 1)
    for o in p2:
        print("  member {}  E {:.17g}  beta {:.17g}  ach {:.17g}  wall {:.1f} s  {}{}".format(
            o["member"], o["E"], o["beta"], o["ach"], o["wall"], o["end"],
            ("  " + o["error"]) if o["error"] else ""))
    print("  P2 {}".format("PASS" if p2_ok else "FAIL"))
    if not p2_ok:
        code = 3
    a3 = float("nan")
    if len(p2) == 2 and all(o["end"] == "ok" for o in p2):
        w = [o["wall"] for o in p2]
        a3 = max(w) / min(w)
    print("  A3 timing noise: P2 wall ratio {:.3f}{}".format(
        a3, "  (above {}: A1 noise-limited)".format(RATIO_MAX) if a3 > RATIO_MAX else ""))
    if smoke:
        return code, None

    hdr("A1  seed dependence of wall time  ({})".format(CAVEAT))
    a1 = [o for o in done if o["check"] == "A1"]
    scale, a1_verdict = 1.0, ""
    if len(a1) != 2 or any(o["end"] != "ok" for o in a1):
        errs = "; ".join("member {}: {}".format(o["member"], o["error"] or o["end"]) for o in a1)
        a1_verdict = "FAIL (errored or missing: {})".format(errs or "no members")
        if code == 0:
            code = 4
    else:
        w = [o["wall"] for o in a1]
        ratio = max(w) / min(w)
        if ratio <= RATIO_MAX:
            a1_verdict = "PASS ratio {:.3f}".format(ratio)
        else:
            a1_verdict = "FAIL ratio {:.3f}".format(ratio)
            scale = ratio
        if a3 > RATIO_MAX:
            a1_verdict += " (noise-limited)"
        for o in a1:
            print("  member {}  key {}  wall {:.1f} s".format(
                o["member"], "-".join(str(x) for x in o["key"]), o["wall"]))
    print("  A1 {}".format(a1_verdict))

    hdr("P4  memory budget ({:.0f} MB per probe)".format(RSS_BUDGET_MB))
    main_ok = dict((o["unit"], o) for o in done if o["check"] == "" and o["end"] == "ok")
    rss_all = [o["rss"] for o in done if o["end"] == "ok"]
    over = [o for o in done if o["end"] == "ok" and o["rss"] > RSS_BUDGET_MB]
    if rss_all:
        print("  peak RSS over {} completed probes: max {:.1f} MB".format(len(rss_all), max(rss_all)))
    for o in over:
        print("  EXCEEDS BUDGET {} d={} tau={} J={}: {:.1f} MB".format(
            o["unit"][0], o["unit"][1], o["unit"][2], o["unit"][3], o["rss"]))
    p4 = "pass" if not over else "EXCEEDS BUDGET"
    print("  P4 {}".format(p4))

    hdr("C1  achieved fraction / tau_0 per probe (diagnostic, no decision)")
    rat = [o["ach"] / o["unit"][2] for o in done if o["end"] == "ok"]
    if rat:
        print("  over {} probes: min {:.6f}  max {:.6f}".format(len(rat), min(rat), max(rat)))

    hdr("P5  projection of perjcal's archived design")
    miss = [u for u in us if u not in main_ok]
    M = CONST["M"]
    rows = []
    if miss:
        label = "NOT PROJECTED: missing " + ";".join("/".join(str(x) for x in u) for u in miss)
        print("  " + label)
        rows.append(["perjcal-archived", len(us), M, "", "", "", "", workers, p4, a1_verdict, label])
    else:
        sum_wall = sum(main_ok[u]["wall"] for u in us)
        core_s = M * sum_wall * scale
        wall_s = core_s / workers
        shards = int(math.ceil(wall_s / SHARD_CEIL_S))
        label = SCALED_LABEL if scale > 1.0 else LB_LABEL
        if a1_verdict.startswith("FAIL (errored"):
            label += "; check errored"
        print("  units {}  M {}  summed unit wall {:.1f} s  scale {:.3f}".format(len(us), M, sum_wall, scale))
        print("  core_s {:.0f}  wall_s {:.0f} at {} workers  shards at {:.0f} s: {}".format(
            core_s, wall_s, workers, SHARD_CEIL_S, shards))
        print("  label: {}".format(label))
        for tau in CONST["taus"]:
            for d in CONST["dims"]:
                s = sum(main_ok[u]["wall"] for u in us if u[1] == d and u[2] == tau)
                print("    tau_0 {:<5} d {:<3} summed unit wall {:>9.1f} s".format(tau, d, s))
        rows.append(["perjcal-archived", len(us), M, "%.3f" % sum_wall, "%.3f" % scale,
                     "%.1f" % core_s, "%.1f" % wall_s, workers, p4, a1_verdict,
                     "{}; shards {}".format(label, shards)])
    with open(os.path.join(outdir, "perjcalprobe_projection.csv"), "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["design", "units", "M", "sum_unit_wall_s", "scale", "core_s", "wall_s",
                    "workers", "P4", "A1", "label"])
        w.writerow(["P2", "", "", "", "", "", "", workers, "", "", "PASS" if p2_ok else "FAIL"])
        w.writerow(["A3", "", "", "", "", "", "", workers, "", "", "%.3f" % a3])
        w.writerows(rows)
    return code, rows


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=7200.0)
    ap.add_argument("--archive", default=None)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    mode = "plan" if a.plan else ("smoke" if a.smoke else "full")
    me = sha256_file(os.path.abspath(__file__))

    print("=" * 96)
    print("CBO-GAP perjcalprobe -- cost of the per-J-beta experiment (perjcal.one_J)")
    print("=" * 96)
    print("  script   {}  sha256 {}".format(os.path.abspath(__file__), me))
    print("  python   {}   numpy {}".format(platform.python_version(), np.__version__))
    print("  platform {}".format(platform.platform()))
    print("  workers  {}   mode {}   timeout {:.0f} s".format(a.workers, mode, a.timeout))
    print("  threads  " + "  ".join("{}={}".format(v, os.environ.get(v)) for v in THREAD_VARS))
    print("  archive  {}".format(ARCH))
    print("  outroot  {}".format(OUTROOT))
    for k_ in sorted(CONST):
        print("  {:<6} {}".format(k_, CONST[k_]))
    print("  K {}   J list after cap {}".format(K, JLIST))
    print("  seeds    default_rng(SeedSequence(key)), key = (ENTROPY {}, kind {}, objective code,"
          " d, tau0 x 1e6, J, variant)".format(ENTROPY, KIND))
    print("  budget   {:.0f} MB per probe   ratio threshold {}   shard ceiling {:.0f} s".format(
        RSS_BUDGET_MB, RATIO_MAX, SHARD_CEIL_S))
    print("  perjcal is a DIFFERENT ESTIMAND (beta varies with J); nothing here is pooled")
    print("  with or compared to the fixed-beta rerun.")

    hdr("P1  archive identity")
    if not p1():
        sys.stderr.write("P1 failed\n")
        sys.exit(2)
    hdr("P0  plan identity against perjcal.py main()")
    if not p0():
        sys.stderr.write("P0 failed\n")
        sys.exit(2)

    us, tasks, smallest, largest = build_plan("smoke" if mode == "smoke" else "full")
    hdr("PLAN")
    for tau in CONST["taus"]:
        print("  tau_0 {:<5} sizes {}".format(tau, [J for J in JLIST if J >= 1.0 / tau]))
    print("  units {}   tasks this mode {}".format(len(us), len(tasks)))
    print("  P2 unit {}   A1 unit {}".format(smallest, largest))
    if mode == "plan":
        print("\n  --plan: nothing run, nothing written.")
        sys.exit(0)

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(OUTROOT, "perjcalprobe-{}{}".format(stamp, "-smoke" if mode == "smoke" else ""))
    os.makedirs(outdir)
    params = [["script_sha256", me], ["mode", mode], ["workers", a.workers],
              ["timeout_s", a.timeout], ["python", platform.python_version()],
              ["numpy", np.__version__], ["platform", platform.platform()],
              ["entropy", ENTROPY], ["kind", KIND], ["K", K], ["jlist", JLIST]]
    params += [[k_, CONST[k_]] for k_ in sorted(CONST)]
    with open(os.path.join(outdir, "perjcalprobe_params.csv"), "x", newline="") as fh:
        csv.writer(fh).writerows(params)
    print("\n  run dir  {}".format(outdir))

    hdr("PROBES  {} task(s), at most {} at once, one fresh process each".format(len(tasks), a.workers))
    fh = open(os.path.join(outdir, "perjcalprobe_results.csv"), "x", newline="")
    w = csv.writer(fh)
    w.writerow(RES_COLS)
    fh.flush()
    os.fsync(fh.fileno())
    pending, running, done = list(tasks), [], []
    t0 = time.time()
    try:
        while pending or running:
            while pending and len(running) < a.workers:
                t = pending.pop(0)
                rc, sc = multiprocessing.Pipe(duplex=False)
                pr_ = multiprocessing.Process(target=child_main, args=(t, sc))
                pr_.start()
                sc.close()
                running.append([pr_, rc, t, time.monotonic()])
            progressed = False
            for item in list(running):
                pr_, rc, t, ts = item
                o = None
                if rc.poll():
                    try:
                        o = rc.recv()
                    except EOFError:
                        pr_.join()
                        o = error_row(t, "worker exited with code {} without a result".format(pr_.exitcode), pr_.pid)
                    pr_.join()
                elif not pr_.is_alive():
                    pr_.join()
                    o = error_row(t, "worker exited with code {} without a result".format(pr_.exitcode), pr_.pid)
                elif time.monotonic() - ts > a.timeout:
                    pr_.terminate()
                    pr_.join()
                    o = error_row(t, "timeout after {:.0f} s".format(time.monotonic() - ts), pr_.pid)
                if o is None:
                    continue
                rc.close()
                running.remove(item)
                progressed = True
                done.append(o)
                w.writerow(res_row(o))
                fh.flush()
                os.fsync(fh.fileno())
                obj, d, tau, J = o["unit"]
                if o["end"] == "ok":
                    print("  [{:>4}/{:<4}] {:<3}{:<2} {:<11} d={:<3} tau={:<5} J={:<5} wall {:>8.1f} s  "
                          "RSS {:>7.1f} MB  ach/tau {:.6f}{}  elapsed {:>7.0f} s".format(
                              len(done), len(tasks), o["check"] or "-", o["member"], obj, d, tau, J,
                              o["wall"], o["rss"], o["ach"] / tau,
                              "  OVER BUDGET" if o["rss"] > RSS_BUDGET_MB else "", time.time() - t0))
                else:
                    print("  [{:>4}/{:<4}] ERROR {} d={} tau={} J={}: {}".format(
                        len(done), len(tasks), obj, d, tau, J, o["error"]))
                sys.stdout.flush()
            if not progressed:
                time.sleep(0.2)
    finally:
        for pr_, rc, _t, _ts in running:
            pr_.terminate()
            pr_.join()
        fh.close()
    print("  probes finished in {:.1f} s".format(time.time() - t0))

    code, _ = analyse(done, us, outdir, a.workers, mode == "smoke")
    print("\n" + "=" * 96)
    print("files  {}   exit {}".format(outdir, code))
    print("=" * 96)
    sys.exit(code)


if __name__ == "__main__":
    main()
