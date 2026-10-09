"""
detcheck.py  --  CBO-GAP round 2: determinism gate for this machine

WHAT THIS CHECKS, IN PLAIN LANGUAGE
-----------------------------------
The deposited archive (zenodo-v1) was produced on Windows 7, Python 3.8.10,
NumPy 1.24.4. Before any number produced on this machine is compared with an
archived number, we must know whether this machine reproduces the archived
dynamics exactly. This script reruns three archived realizations with their
archived seeds, through the archived code itself (imported from zenodo-v1,
not retyped), and compares every stored quantity with what this machine
produces. It also measures wall time and peak memory per realization, which
are the two numbers every round-2 design on this machine must be sized from.

PRE-REGISTERED CRITERIA (fixed 2026-10-08, before first execution)
--------------------------------------------------------------------
  D1  CALIBRATION. The solved inverse temperature beta, the achieved initial
      ESS fraction and the stored log-ESS values equal the archived values to
      within half a unit in the last digit the archive stored.
  D2  TRAJECTORY. Every per-J coupled error E_J equals the archived value to
      within half a unit in the last stored digit (the archive stores %.8g),
      and the fitted slope likewise (%.6g in exactcal_real.csv, %.6f in
      rmapj_real.csv).
  D3  WORKER INDEPENDENCE. Repeating the run with a single worker gives
      bitwise identical floating-point results for every quantity.
  PASS = D1 and D2 hold for every quantity of all three realizations and D3
  holds. Any FAIL means: no number from this machine is compared with an
  archived number; comparisons are within-platform only. The first three
  coordinates of the initial draw X0 are printed and stored so that a future
  cross-platform comparison can tell a random-stream mismatch from a
  floating-point one (the archive did not store X0, so X0 is recorded here
  for this machine and compared with nothing).

WORKED EXAMPLE OF THE TOLERANCE RULE
  archived "0.056786325"  -> 9 decimals          -> tolerance 0.5e-9
  archived "5.398521e-05" -> 6 decimals, exp -5  -> tolerance 0.5e-6 * 1e-5 = 5e-12
  archived "-1.22556"     -> 5 decimals          -> tolerance 5e-6
  archived "0.5397402043" -> 10 decimals         -> tolerance 5e-11
  A quantity passes when |computed - archived| <= tolerance. This is exactly
  "equal to the precision the archive kept", nothing looser.

THE THREE REALIZATIONS
  R1  exactcal_real.csv, first row: ackley, d = 2, centred, tau_0 = 0.5
  R2  exactcal_real.csv, first row with d = 40
  R3  rmapj_real.csv, first row with diffusion = isotropic and d = 80
  R1 is the cheapest cell in the archive; R3 is the heaviest memory path
  (J_inf = 50000, d = 80). Each is run in a fresh worker process so that the
  reported peak RSS is that realization's own.

WHAT IT DOES NOT DO
  It does not touch zenodo-v1. It writes one results file into a new run
  folder opened with mode "x" and refuses to run if that folder exists.
  It reimplements nothing: dynamics, calibration and slope fitting are the
  archived functions ec.one_realisation, ec.fit_slope, rm.one_realisation,
  rm.sigma_of, rj.probe_beta, rj.job.

HOW TO RUN (from the repository root, venv active)
    python scripts/detcheck.py --workers 2 > logs/detcheck-$(date +%Y%m%d-%H%M).log 2>&1
    python scripts/detcheck.py --workers 2 --tasks R1        (about a minute: smoke)
On Kaggle the archive is mounted read-only at a path the kgrun runner
discovers rather than assumes (on 2026-10-09: /kaggle/input/datasets/ericsom/cbo-gap-archive),
and output goes to /kaggle/working. The runner then calls, for example:
    python detcheck.py --archive /kaggle/input/datasets/ericsom/cbo-gap-archive --outdir /kaggle/working
The gate is PER PLATFORM. A pass on one machine says nothing about another,
so it runs first on every new machine before any number from that machine is
compared with an archived one.
Exit code 0 on PASS, 1 on FAIL, 2 on a setup error.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import argparse
import csv
import datetime
import hashlib
import math
import os
import platform
import resource
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.dont_write_bytecode = True

import cbopaths                                                # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The archive path must be known at import time, so --archive and --outdir
# are read from argv before argparse (scripts/cbopaths.py). argparse still
# declares both flags in main(), so --help lists them and an unknown flag is
# still an error.
ARCH = cbopaths.archive_path(ROOT)
OUTROOT = cbopaths.output_root(ROOT)
if not os.path.isdir(ARCH):
    sys.stderr.write("setup error: archive not found at {}\n".format(ARCH))
    sys.stderr.write("pass --archive <path> or set CBOGAP_ARCHIVE\n")
    sys.exit(2)
sys.path.insert(0, ARCH)

try:
    import exactcal as ec
    import regimemap as rm
    import rmapj as rj
except Exception as exc:                                       # pragma: no cover
    sys.stderr.write("setup error: cannot import archived scripts: {}\n".format(exc))
    sys.exit(2)

J_LIST = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
JINF = 50000
LAM, SIGMA_EC, DT, K, T = 1.0, 0.2, 0.01, 100, 1.0
TAU_RMAPJ = 0.1
FILES_USED = ["exactcal.py", "regimemap.py", "rmapj.py",
              "exactcal_real.csv", "rmapj_real.csv"]


# ----------------------------------------------------------------------------
# tolerance rule: half a unit in the last digit the archive stored
# ----------------------------------------------------------------------------
def half_ulp_of_string(s):
    s = s.strip()
    if "e" in s or "E" in s:
        mant, exp = s.replace("E", "e").split("e")
        exp = int(exp)
    else:
        mant, exp = s, 0
    dec = len(mant.split(".")[1]) if "." in mant else 0
    return 0.5 * (10.0 ** (-dec)) * (10.0 ** exp)


def compare(name, archived_str, computed):
    a = float(archived_str)
    tol = half_ulp_of_string(archived_str)
    diff = abs(computed - a)
    return (name, archived_str, repr(float(computed)), diff, tol, diff <= tol)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------
# the three tasks; each returns a dict of computed quantities plus timing/RSS
# ----------------------------------------------------------------------------
def run_exactcal_row(row):
    obj, d, init, tau = row["objective"], int(row["d"]), row["init"], float(row["tau"])
    seed = int(row["seed"])
    rng = np.random.default_rng(seed)
    x0 = ec.draw_initial(rng, JINF, d, obj, init)
    x0_first = [float(v) for v in x0[0, :3]]
    t0 = time.time()
    per_J, beta, ach, le0, lem = ec.one_realisation(
        obj, d, init, tau, SIGMA_EC, LAM, DT, K, JINF, J_LIST, seed)
    wall = time.time() - t0
    slope = ec.fit_slope(J_LIST, [per_J[J] for J in J_LIST])
    rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    out = {"beta": float(beta), "achieved_frac": float(ach),
           "log_ess_0": float(le0), "log_ess_min": float(lem), "slope": float(slope)}
    for J in J_LIST:
        out["E_%d" % J] = float(per_J[J])
    return {"vals": out, "x0_first": x0_first, "wall": wall, "rss_mb": rss_mb,
            "pid": os.getpid()}


def run_rmapj_row(row):
    name, d, diff = row["objective"], int(row["d"]), row["diffusion"]
    r, tau, rep, seed = float(row["r"]), float(row["tau"]), int(row["rep"]), int(row["seed"])
    rng = np.random.default_rng(seed)
    x0 = rng.standard_normal((JINF, d))          # regimemap.one_realisation's own first draw
    x0_first = [float(v) for v in x0[0, :3]]
    del x0
    beta = rj.probe_beta(name, d, tau)
    sigma = rm.sigma_of(diff, d, r, LAM)
    t0 = time.time()
    res = rj.job((name, d, diff, r, tau, rep, beta, sigma, LAM, DT, K, JINF, J_LIST, seed))
    wall = time.time() - t0
    slope, E = res[9], res[10]
    rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    out = {"beta": float(beta), "sigma": float(sigma), "slope": float(slope)}
    for J, v in zip(J_LIST, E):
        out["E_%d" % J] = float(v)
    return {"vals": out, "x0_first": x0_first, "wall": wall, "rss_mb": rss_mb,
            "pid": os.getpid()}


def task(a):
    label, kind, row = a
    if kind == "exactcal":
        return (label, run_exactcal_row(row))
    return (label, run_rmapj_row(row))


# ----------------------------------------------------------------------------
def pick_rows():
    ex = list(csv.DictReader(open(os.path.join(ARCH, "exactcal_real.csv"), newline="")))
    rj_rows = list(csv.DictReader(open(os.path.join(ARCH, "rmapj_real.csv"), newline="")))
    r1 = ex[0]
    r2 = next(x for x in ex if int(x["d"]) == 40)
    r3 = next(x for x in rj_rows if x["diffusion"] == "isotropic" and int(x["d"]) == 80)
    return {"R1": ("exactcal", r1, ex.index(r1) + 2),
            "R2": ("exactcal", r2, ex.index(r2) + 2),
            "R3": ("rmapj", r3, rj_rows.index(r3) + 2)}


def describe(label, kind, row, line):
    if kind == "exactcal":
        return "{}  exactcal_real.csv line {}: {} d={} {} tau0={} seed={}".format(
            label, line, row["objective"], row["d"], row["init"], row["tau"], row["seed"])
    return "{}  rmapj_real.csv line {}: {} {} d={} r={} tau0={} rep={} seed={}".format(
        label, line, row["diffusion"], row["objective"], row["d"], row["r"],
        row["tau"], row["rep"], row["seed"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--tasks", default="R1,R2,R3")
    p.add_argument("--archive", default=None,
                   help="path to the deposited archive; default <repo>/zenodo-v1, "
                        "or CBOGAP_ARCHIVE. On Kaggle: the path the kgrun runner finds "
                        "(2026-10-09: /kaggle/input/datasets/<user>/<dataset>)")
    p.add_argument("--outdir", default=None,
                   help="directory to create the run folder in; default <repo>/runs, "
                        "or CBOGAP_OUTDIR. On Kaggle: /kaggle/working")
    a = p.parse_args()

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(OUTROOT, "detcheck-" + stamp)
    os.makedirs(outdir)                        # refuses if it exists

    print("=" * 88)
    print("CBO-GAP detcheck -- determinism gate for this machine")
    print("=" * 88)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}".format(platform.platform(), platform.machine(),
                                                        os.cpu_count()))
    print("  workers  {}   tasks {}".format(a.workers, a.tasks))
    print("  archive  {}".format(ARCH))
    for f in FILES_USED:
        print("    sha256 {}  {}".format(sha256_of(os.path.join(ARCH, f)), f))
    print("  parameters: lam {}  sigma(exactcal) {}  dt {}  K {}  T {}  Jinf {}".format(
        LAM, SIGMA_EC, DT, K, T, JINF))
    print("  J grid    : {}".format(J_LIST))
    print("  tolerance : half a unit in the last archived digit, per quantity")
    print("  run folder: {}".format(outdir))
    print()

    rows = pick_rows()
    labels = [s.strip() for s in a.tasks.split(",") if s.strip()]
    for lab in labels:
        if lab not in rows:
            sys.stderr.write("unknown task {}\n".format(lab))
            sys.exit(2)
        kind, row, line = rows[lab]
        print("  " + describe(lab, kind, row, line))
    print()
    tasks = [(lab, rows[lab][0], rows[lab][1]) for lab in labels]

    def run_all(nworkers):
        t0 = time.time()
        pool = Pool(processes=nworkers, maxtasksperchild=1)
        try:
            res = dict(pool.map(task, tasks, chunksize=1))
        finally:
            pool.close()
            pool.join()
        return res, time.time() - t0

    print("-" * 88)
    print("pass 1: {} worker(s)".format(a.workers))
    print("-" * 88)
    res_a, wall_a = run_all(a.workers)
    print("  wall {:.1f} s".format(wall_a))

    # ---------------- D1 + D2 ----------------
    allrows, overall = [], True
    for lab in labels:
        kind, row, line = rows[lab]
        r = res_a[lab]
        print()
        print("  {}  wall {:.1f} s   peak RSS of its worker {:.0f} MB   X0[0,:3] = {}".format(
            lab, r["wall"], r["rss_mb"], ["%.17g" % v for v in r["x0_first"]]))
        print("  {:<14} {:>18} {:>24} {:>12} {:>10}  {}".format(
            "quantity", "archived", "computed", "absdiff", "tol", "ok"))
        for q, cval in r["vals"].items():
            if q not in row:
                continue
            name, arch_s, comp_s, diff, tol, ok = compare(q, row[q], cval)
            overall = overall and ok
            allrows.append([lab, kind, line, q, arch_s, comp_s, "%.3e" % diff, "%.3e" % tol,
                            "PASS" if ok else "FAIL"])
            print("  {:<14} {:>18} {:>24} {:>12.3e} {:>10.1e}  {}".format(
                q, arch_s, comp_s, diff, tol, "PASS" if ok else "FAIL"))
    d12 = "PASS" if overall else "FAIL"

    # ---------------- D3 ----------------
    print()
    print("-" * 88)
    print("pass 2: 1 worker, for D3 (bitwise identity of every quantity)")
    print("-" * 88)
    res_b, wall_b = run_all(1)
    print("  wall {:.1f} s".format(wall_b))
    d3_ok = True
    for lab in labels:
        for q, v in res_a[lab]["vals"].items():
            same = (v == res_b[lab]["vals"][q]) or (math.isnan(v) and math.isnan(res_b[lab]["vals"][q]))
            if not same:
                d3_ok = False
                print("  D3 mismatch {} {}: {!r} vs {!r}".format(lab, q, v, res_b[lab]["vals"][q]))
        if res_a[lab]["x0_first"] != res_b[lab]["x0_first"]:
            d3_ok = False
            print("  D3 mismatch {} X0".format(lab))
    d3 = "PASS" if d3_ok else "FAIL"

    # ---------------- results file ----------------
    out_csv = os.path.join(outdir, "detcheck_results.csv")
    with open(out_csv, "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["task", "source", "line", "quantity", "archived", "computed",
                    "absdiff", "tol", "verdict"])
        for rr in allrows:
            w.writerow(rr)
        for lab in labels:
            r = res_a[lab]
            w.writerow([lab, "timing", "", "wall_seconds", "", "%.3f" % r["wall"], "", "", ""])
            w.writerow([lab, "memory", "", "peak_rss_mb", "", "%.1f" % r["rss_mb"], "", "", ""])
            w.writerow([lab, "x0", "", "X0_first3", "", " ".join("%.17g" % v for v in r["x0_first"]),
                        "", "", ""])
        w.writerow(["ALL", "verdict", "", "D1_D2", "", d12, "", "", ""])
        w.writerow(["ALL", "verdict", "", "D3", "", d3, "", "", ""])

    print()
    print("=" * 88)
    print("VERDICT   D1+D2: {}   D3: {}   OVERALL: {}".format(
        d12, d3, "PASS" if (overall and d3_ok) else "FAIL"))
    print("results   {}".format(out_csv))
    if not (overall and d3_ok):
        print("FAIL means: no number from this machine is compared with an archived number.")
        print("Comparisons stay within platform until the cause is identified.")
    print("=" * 88)
    sys.exit(0 if (overall and d3_ok) else 1)


if __name__ == "__main__":
    main()
