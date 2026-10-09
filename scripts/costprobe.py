"""
costprobe.py  --  CBO-GAP round 2, stage C0: what the fixed-beta reruns cost
                  on THIS machine

WHAT THIS MEASURES, IN PLAIN LANGUAGE
-------------------------------------
Two experiments have to be repeated under a fixed inverse temperature
(referee points 3, 4 and 5): the concentration arm EXP-CAL and the
operating-level sweep EXP-TAU8. Before either is designed in detail we need
the per-realization wall time and peak memory of the archived dynamics on
this machine, for every (objective, dimension) that appears in those grids.
This script times exactly one realization of each, in its own worker process,
and then PROJECTS the total cost of both reruns from what it measured. The
projection is arithmetic on measured times, printed by the script; nothing is
assumed.

It does not calibrate anything, does not decide anything, and writes nothing
except its own results file. It calls the archived function
exactcal.one_realisation unmodified, so the timings are the real cost of the
round-2 dynamics (the fixed-beta variant differs only by skipping one
bisection, which is two logsumexp passes over 50 000 values per realization).

THE GRIDS, READ FROM THE ARCHIVED SCRIPTS, NOT ASSUMED
  EXP-CAL   (zenodo-v1/exactcal.py, lines 263-265)
            6 objectives x d in {2, 5, 10, 40} x 2 initial laws
            x tau0 in {0.5, 0.1, 0.01} x 15 realizations
            = 144 cells, 2160 realizations
  EXP-TAU8  (zenodo-v1/boundary.py, lines 253-256)
            6 objectives x d in {5, 10, 40}
            x tau0 in {0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01}
            x 15 realizations, centred law
            = 144 cells, 2160 realizations

WHAT IS PROBED
  One realization for each (objective, d) in the union of the two grids:
  6 objectives x {2, 5, 10, 40} = 24 realizations, centred law, tau0 = 0.1,
  probe seeds that collide with no archived seed (base 90000000).
  Wall time is assumed to depend on (objective, d) and not on tau0 or on the
  initial law; that assumption is stated here and is the one soft spot in the
  projection. It is checked cheaply with --repeat 2, which probes each
  combination at tau0 = 0.5 as well and prints both.

PROJECTION RULE
  projected wall for a grid = sum over its cells of
      15 x (measured per-realization time for that cell's objective and d)
  divided by the number of workers, since realizations are independent and
  the pool is saturated. Perfect scaling across workers is assumed; the
  measured ratio between a 2-worker and a 1-worker pass of detcheck on this
  machine was 77.0 against 89.3 seconds, so on two cores the real figure will
  be worse than the projection. The projection is therefore a lower bound and
  is labelled as one in the output.

HOW TO RUN (from the repository root, venv active)
    python scripts/costprobe.py --workers 2
    python scripts/costprobe.py --workers 2 --quick      (4 combinations)
--archive PATH (else CBOGAP_ARCHIVE, else <repo>/zenodo-v1) names the
archive the dynamics are imported from; --outdir PATH (else CBOGAP_OUTDIR,
else <repo>/runs) names the directory the run folder is created in. Both
are resolved by scripts/cbopaths.py, with the same semantics as detcheck.py;
a missing archive is a setup error (exit code 2). On Kaggle the kgrun
runner discovers the mount path rather than assuming it (on 2026-10-09:
/kaggle/input/datasets/ericsom/cbo-gap-archive) and calls, for example:
    python costprobe.py --archive /kaggle/input/datasets/ericsom/cbo-gap-archive --outdir /kaggle/working
Writes <outdir>/costprobe-<timestamp>/costprobe_results.csv (default under
runs/), opened with mode "x".
Exit code 0 always unless setup fails (2); this script has no pass criterion.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import argparse
import csv
import datetime
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
except Exception as exc:                                        # pragma: no cover
    sys.stderr.write("setup error: cannot import exactcal: {}\n".format(exc))
    sys.exit(2)

J_LIST = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
JINF = 50000
LAM, SIGMA, DT, K = 1.0, 0.2, 0.01, 100
OBJS = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
DIMS = [2, 5, 10, 40]
SEED_BASE = 90000000

EXPCAL = {"name": "EXP-CAL-FIX (concentration arm, referee 3 and 4)",
          "objs": OBJS, "dims": DIMS, "laws": 2, "taus": 3, "reps": 15}
EXPTAU8 = {"name": "EXP-TAU8-FIX (operating level, referee 5)",
           "objs": OBJS, "dims": [5, 10, 40], "laws": 1, "taus": 8, "reps": 15}


def probe(a):
    obj, d, tau, seed = a
    t0 = time.time()
    per_J, beta, ach, le0, lem = ec.one_realisation(
        obj, d, "centred", tau, SIGMA, LAM, DT, K, JINF, J_LIST, seed)
    wall = time.time() - t0
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    slope = ec.fit_slope(J_LIST, [per_J[J] for J in J_LIST])
    return (obj, d, tau, seed, wall, rss, float(beta), float(ach), float(slope),
            os.getpid())


def hms(sec):
    sec = int(round(sec))
    return "{:d}h {:02d}m {:02d}s".format(sec // 3600, (sec % 3600) // 60, sec % 60)


def project(grid, tmap, workers):
    total = 0.0
    missing = []
    for o in grid["objs"]:
        for d in grid["dims"]:
            if (o, d) not in tmap:
                missing.append((o, d))
                continue
            total += tmap[(o, d)] * grid["laws"] * grid["taus"] * grid["reps"]
    cells = len(grid["objs"]) * len(grid["dims"]) * grid["laws"] * grid["taus"]
    reals = cells * grid["reps"]
    return total, total / max(workers, 1), cells, reals, missing


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--quick", action="store_true",
                   help="probe only ackley and rosenbrock at d = 2 and 40")
    p.add_argument("--repeat", type=int, default=1, choices=[1, 2],
                   help="2 also probes every combination at tau0 = 0.5")
    p.add_argument("--archive", default=None,
                   help="path to the deposited archive; default <repo>/zenodo-v1, "
                        "or CBOGAP_ARCHIVE. On Kaggle: the path the kgrun runner finds "
                        "(2026-10-09: /kaggle/input/datasets/<user>/<dataset>)")
    p.add_argument("--outdir", default=None,
                   help="directory to create the run folder in; default <repo>/runs, "
                        "or CBOGAP_OUTDIR. On Kaggle: /kaggle/working")
    a = p.parse_args()

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(OUTROOT, "costprobe-" + stamp)
    os.makedirs(outdir)

    objs = ["ackley", "rosenbrock"] if a.quick else OBJS
    dims = [2, 40] if a.quick else DIMS
    taus = [0.1, 0.5][:a.repeat]

    print("=" * 86)
    print("CBO-GAP costprobe -- per-realization cost of the fixed-beta reruns")
    print("=" * 86)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   cpus {}   workers {}".format(platform.platform(),
                                                        os.cpu_count(), a.workers))
    print("  archive  {}".format(ARCH))
    print("  fixed    lam {}  sigma {}  dt {}  K {}  Jinf {}  law centred".format(
        LAM, SIGMA, DT, K, JINF))
    print("  J grid   {}".format(J_LIST))
    print("  probing  {} objectives x {} dims x tau0 {}  seeds from {}".format(
        len(objs), len(dims), taus, SEED_BASE))
    print("  run dir  {}".format(outdir))
    print()

    tasks = []
    i = 0
    for t in taus:
        for o in objs:
            for d in dims:
                tasks.append((o, d, t, SEED_BASE + i))
                i += 1

    t0 = time.time()
    pool = Pool(processes=a.workers, maxtasksperchild=1)
    try:
        res = pool.map(probe, tasks, chunksize=1)
    finally:
        pool.close()
        pool.join()
    wall_all = time.time() - t0

    print("-" * 86)
    print("  {:<11} {:>3} {:>6} {:>10} {:>9} {:>12} {:>10}".format(
        "objective", "d", "tau0", "wall s", "RSS MB", "beta", "slope"))
    tmap = {}
    rows = []
    for (o, d, t, seed, wall, rss, beta, ach, slope, pid) in res:
        print("  {:<11} {:>3d} {:>6} {:>10.1f} {:>9.0f} {:>12.6g} {:>10.4f}".format(
            o, d, t, wall, rss, beta, slope))
        rows.append([o, d, t, seed, "%.3f" % wall, "%.1f" % rss, "%.10g" % beta,
                     "%.8g" % ach, "%.6g" % slope])
        if t == 0.1 or (o, d) not in tmap:
            tmap[(o, d)] = wall
    print("-" * 86)
    print("  probe wall {}   peak RSS over workers {:.0f} MB".format(
        hms(wall_all), max(r[5] for r in res)))
    print()

    print("PROJECTIONS (lower bounds: perfect worker scaling assumed)")
    summary = []
    for grid in (EXPCAL, EXPTAU8):
        tot, perw, cells, reals, missing = project(grid, tmap, a.workers)
        print("  {}".format(grid["name"]))
        print("    {} cells, {} realizations".format(cells, reals))
        if missing:
            print("    NOT PROJECTED: no probe for {}; rerun without --quick".format(missing))
            continue
        print("    core-time {}   at {} workers {}".format(hms(tot), a.workers, hms(perw)))
        summary.append([grid["name"], cells, reals, "%.0f" % tot, a.workers, "%.0f" % perw])
    if not EXPCAL["objs"] or tmap:
        pass
    tot_both = sum(float(s[3]) for s in summary) if summary else 0.0
    if len(summary) == 2:
        print("  BOTH RERUNS: core-time {}   at {} workers {}".format(
            hms(tot_both), a.workers, hms(tot_both / a.workers)))
    print()

    out = os.path.join(outdir, "costprobe_results.csv")
    with open(out, "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "tau0", "seed", "wall_s", "peak_rss_mb",
                    "beta", "achieved_frac", "slope"])
        for r in rows:
            w.writerow(r)
        w.writerow([])
        w.writerow(["grid", "cells", "realizations", "core_seconds", "workers",
                    "projected_seconds"])
        for s in summary:
            w.writerow(s)
    print("results {}".format(out))
    print("=" * 86)


if __name__ == "__main__":
    main()
