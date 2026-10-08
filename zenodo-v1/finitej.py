"""
finitej.py  —  CBO-GAP: is the finite-J subensemble concentrated at the target?

WHY THIS EXISTS
---------------
exactcal.py solves beta by bisection on the reference ensemble of J_inf = 50000
particles, so the reference achieves its target concentration exactly. But the
finite ensembles whose coupled error is measured are the FIRST J particles of
that reference, and

    ESS_0(J) / J   is not  ESS_0(J_inf) / J_inf

as a matter of arithmetic. The reference is exactly calibrated; the J = 10, 20,
... 5000 subensembles are not. If that ratio drifts systematically with J or
with dimension, then part of what the concentration arm attributes to dimension
could still be finite-J concentration, and the control is weaker than claimed.

This script measures it. It runs NO trajectories and burns no new simulation
time. For every one of the 2160 archived realizations it reuses the seed and the
beta already stored in exactcal_real.csv, redraws the same initial ensemble, and
computes the initial ESS fraction of each nested subensemble. Expect a few
minutes, not hours.

WHAT IS REPORTED
----------------
  For each target tau_0 and each J:

      ratio(J) = [ ESS_0(J) / J ] / tau_0

  with mean, standard deviation, and the 5th and 95th percentiles across
  realizations, plus the same broken out by dimension at the tightest target.

PRE-REGISTERED, fixed before this script was first executed
-----------------------------------------------------------
  P-F1  The reference reproduces. Recomputing ESS_0(J_inf)/tau_0 from the stored
        seed and beta must return 1.000 to three decimals in every realization.
        If it does not, the redraw does not reproduce the archived run and
        nothing below is trustworthy; the script says so and stops.

  P-F2  BIAS. The mean of ratio(J) is reported at every J. Sampling ESS from a
        subensemble is not unbiased for the parent fraction, so a departure from
        one at small J is expected and is not by itself a defect. What matters
        is the size of the departure and whether it varies with dimension.

  P-F3  THE THING THAT WOULD MATTER. The quantity that could contaminate the
        concentration arm is a systematic DIFFERENCE ACROSS DIMENSION in
        ratio(J) at fixed target, because the headline contrast is d = 2 against
        d = 40 at fixed tau_0. For each target and each J the script reports
        ratio at d = 2 minus ratio at d = 40 with a bootstrap interval. If those
        intervals contain zero at every J, the finite-J concentration is not
        differentially biased across the contrast that the paper draws, and the
        exact-calibration conclusion stands as stated. If they do not, the
        manuscript must report the finite-J drift as a competing explanation for
        the residual at tau_0 = 0.01.

  Both outcomes are written into the manuscript. Nothing is decided after
  seeing the numbers.

HOW TO RUN
    python finitej.py --workers 3

Reads exactcal_real.csv. Writes finitej_summary.csv. Prints everything needed.
NumPy only. No SciPy. Python 3.8 compatible.
"""

import argparse
import csv
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

J_LIST = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
JINF = 50000
SEED = 20260824
N_BOOT = 4000


def f_ackley(X):
    s1 = np.sqrt(np.mean(X * X, axis=1))
    s2 = np.mean(np.cos(2.0 * np.pi * X), axis=1)
    return -20.0 * np.exp(-0.2 * s1) - np.exp(s2) + 20.0 + math.e


def f_rastrigin(X):
    return np.sum(X * X - 10.0 * np.cos(2.0 * np.pi * X) + 10.0, axis=1)


def f_sphere(X):
    return np.sum(X * X, axis=1)


def f_griewank(X):
    i = np.arange(1, X.shape[1] + 1, dtype=float)
    return (np.sum(X * X, axis=1) / 4000.0
            - np.prod(np.cos(X / np.sqrt(i)), axis=1) + 1.0)


def f_levy(X):
    W = 1.0 + (X - 1.0) / 4.0
    a = np.sin(np.pi * W[:, 0]) ** 2
    m = (W[:, :-1] - 1.0) ** 2 * (1.0 + 10.0 * np.sin(np.pi * W[:, :-1] + 1.0) ** 2)
    c = (W[:, -1] - 1.0) ** 2 * (1.0 + np.sin(2.0 * np.pi * W[:, -1]) ** 2)
    return a + np.sum(m, axis=1) + c


def f_rosenbrock(X):
    return np.sum(100.0 * (X[:, 1:] - X[:, :-1] ** 2) ** 2
                  + (X[:, :-1] - 1.0) ** 2, axis=1)


OBJ = {"ackley": f_ackley, "rastrigin": f_rastrigin, "sphere": f_sphere,
       "griewank": f_griewank, "levy": f_levy, "rosenbrock": f_rosenbrock}
XSTAR = {"ackley": 0.0, "rastrigin": 0.0, "sphere": 0.0,
         "griewank": 0.0, "levy": 1.0, "rosenbrock": 1.0}


def draw_initial(rng, n, d, objective, init):
    c = XSTAR[objective]
    if init == "centred":
        return c + rng.standard_normal((n, d))
    if init == "offset":
        return c + 3.0 + rng.standard_normal((n, d))
    eps = 0.1 if init == "mix-0.1" else 0.01
    m = rng.random(n) < eps
    X = c + 3.0 + rng.standard_normal((n, d))
    X[m] = c + rng.standard_normal((int(m.sum()), d))
    return X


def ess_frac(fv, beta):
    a = -beta * fv
    a = a - a.max()
    w = np.exp(a)
    s = w.sum()
    return float(s * s / (w * w).sum()) / len(fv)


def job(row):
    obj, d, init, tau, seed, beta = row
    rng = np.random.default_rng(seed)
    X0 = draw_initial(rng, JINF, d, obj, init)
    fv = OBJ[obj](X0)
    out = [ess_frac(fv[:J], beta) / tau for J in J_LIST]
    return (obj, d, init, tau, ess_frac(fv, beta) / tau, out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--src", default="exactcal_real.csv")
    a = p.parse_args()
    if not os.path.exists(a.src):
        sys.stderr.write("MISSING FILE: {}\n".format(a.src))
        sys.exit(2)
    rows = []
    for x in csv.DictReader(open(a.src)):
        rows.append((x["objective"], int(x["d"]), x["init"], float(x["tau"]),
                     int(x["seed"]), float(x["beta"])))
    print("=" * 90)
    print("CBO-GAP — finite-J initial concentration under exact reference calibration")
    print("=" * 90)
    print("  no trajectories are run; seeds and beta come from {}".format(a.src))
    print("  python {}   numpy {}   workers {}".format(
        sys.version.split()[0], np.__version__, a.workers))
    print("  {} realizations, J grid {}\n".format(len(rows), J_LIST))

    pool = Pool(processes=a.workers)
    try:
        res = pool.map(job, rows, chunksize=4)
    finally:
        pool.close()
        pool.join()

    # ---------------- P-F1 ----------------
    ref = np.array([r[4] for r in res])
    print("-" * 90)
    print("P-F1 — does the redraw reproduce the archived reference calibration?")
    print("-" * 90)
    print("  ESS_0(J_inf)/tau over {} realizations: mean {:.6f}  min {:.6f}  max {:.6f}"
          .format(len(ref), ref.mean(), ref.min(), ref.max()))
    if abs(ref.mean() - 1.0) > 1e-3 or abs(ref.min() - 1.0) > 1e-3:
        print("\n  P-F1 FAIL — the redraw does not reproduce the archived run.")
        print("  Nothing below is trustworthy. Send this output and stop.")
        sys.exit(1)
    print("  P-F1 PASS\n")

    # ---------------- P-F2 ----------------
    print("-" * 90)
    print("P-F2 — finite-J concentration relative to target, [ESS_0(J)/J]/tau_0")
    print("-" * 90)
    w = csv.writer(open("finitej_summary.csv", "w", newline=""))
    w.writerow(["tau", "d", "J", "mean", "sd", "p5", "p95", "n"])
    for tau in (0.5, 0.1, 0.01):
        print("\n  target tau_0 = {}".format(tau))
        print("  %-8s %9s %9s %9s %9s" % ("J", "mean", "sd", "p5", "p95"))
        for j, J in enumerate(J_LIST):
            v = np.array([r[5][j] for r in res if abs(r[3] - tau) < 1e-12])
            print("  %-8d %9.4f %9.4f %9.4f %9.4f" %
                  (J, v.mean(), v.std(ddof=1), np.percentile(v, 5), np.percentile(v, 95)))
            for d in (2, 5, 10, 40):
                vd = np.array([r[5][j] for r in res
                               if abs(r[3] - tau) < 1e-12 and r[1] == d])
                w.writerow([tau, d, J, "%.6g" % vd.mean(), "%.6g" % vd.std(ddof=1),
                            "%.6g" % np.percentile(vd, 5), "%.6g" % np.percentile(vd, 95),
                            len(vd)])

    # ---------------- P-F3 ----------------
    print("\n" + "-" * 90)
    print("P-F3 — is the finite-J bias DIFFERENT between d = 2 and d = 40?")
    print("-" * 90)
    print("  this is the contrast the paper draws; a difference here would contaminate it\n")
    rng = np.random.default_rng(SEED)
    bad = 0
    for tau in (0.5, 0.1, 0.01):
        print("  target tau_0 = {}".format(tau))
        print("  %-8s %11s %26s %s" % ("J", "d2 - d40", "95% interval", "excludes 0"))
        for j, J in enumerate(J_LIST):
            a2 = np.array([r[5][j] for r in res if abs(r[3] - tau) < 1e-12 and r[1] == 2])
            a40 = np.array([r[5][j] for r in res if abs(r[3] - tau) < 1e-12 and r[1] == 40])
            diff = a2.mean() - a40.mean()
            bs = np.array([a2[rng.integers(0, len(a2), len(a2))].mean()
                           - a40[rng.integers(0, len(a40), len(a40))].mean()
                           for _ in range(N_BOOT)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            ex = (lo > 0) or (hi < 0)
            bad += 1 if ex else 0
            print("  %-8d %+11.4f      [%+0.4f,%+0.4f]        %s" %
                  (J, diff, lo, hi, "YES" if ex else "no"))
        print("")
    print("  intervals excluding zero: {} of {}".format(bad, 3 * len(J_LIST)))
    if bad == 0:
        print("  P-F3 PASS — no differential finite-J bias across the contrast the paper draws.")
    else:
        print("  P-F3 FAIL — finite-J concentration differs across dimension at some J.")
        print("  The manuscript must report this as a competing explanation for the residual.")
    print("\n" + "=" * 90)
    print("wrote finitej_summary.csv")
    print("Send this entire console output and the CSV.")
    print("=" * 90)


if __name__ == "__main__":
    main()
