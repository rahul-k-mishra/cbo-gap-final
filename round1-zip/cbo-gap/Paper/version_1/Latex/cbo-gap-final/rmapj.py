"""
rmapj.py  —  CBO-GAP: repeat Phase 11 Part D and archive the per-J errors

WHY THIS EXISTS
---------------
The severity trend of +0.144 per doubling of dimension is the strongest
quantitative result in the manuscript. It is fitted over J = 10 ... 5000 at
tau_0 = 0.1. The attainability bound of Section 7.3 says a target tau_0 is
reachable only when J >= 1/tau_0, so at tau_0 = 0.1 the smallest size J = 10
sits exactly on the bound and is reachable only when the effective sample size
equals one. Every other experiment in the paper has been checked against that
bound by refitting on the restricted window. This one cannot be: regimemap.py
computed the per-J errors, fitted the slope inside the worker, and wrote only
the slope. The array E is returned by one_realisation and then discarded.

So the check needs the numbers, not a new experiment. This script reruns Part D
with identical seeds and writes E.

IT DOES NOT REIMPLEMENT ANYTHING
--------------------------------
It imports regimemap.py and calls its one_realisation, its sigma_of, its
solve_beta and its fit_slope. Not one line of dynamics is retyped. This matters:
an earlier attempt to reproduce a different script by hand used the norm where
the original used the squared norm, which halved every exponent and cost a full
run before it was caught. Importing removes that class of error entirely. If
regimemap.py is edited, this script changes with it, which is the correct
coupling.

The task list is rebuilt in the exact loop order regimemap.py uses when invoked
as --part D, starting from the same seed 20260829 and incrementing by one per
realization, so realization k here receives the seed realization k received
then. beta comes from the same probe with the same probe seed.

PRE-REGISTERED, fixed before this script was first executed
------------------------------------------------------------
  P-R1  EXACT REPRODUCTION. Every one of the 2160 fitted slopes must equal the
        value in regimemap_D_real.csv to six decimals. This is a deterministic
        rerun, not a replication: same seeds, same beta, same dynamics. If any
        slope differs, the import is not reproducing the archived run and the
        refit below means nothing. The script reports the largest discrepancy
        and stops if it exceeds 1e-6.

  P-R2  THE REFIT. Slopes are refitted on J >= 20, dropping only the size that
        sits on the attainability bound, and the severity contrasts and the
        dimension trends of Section 7.13 are recomputed. Both the full-grid and
        the restricted values are reported side by side with bootstrap
        intervals, whatever they show.

  P-R3  THE DECISION. The manuscript reports the restricted-window trend if the
        two differ by more than the bootstrap slope-SE reference scale of
        0.026; otherwise it reports the full-grid trend and states that the
        restriction changes nothing. In either case both numbers are printed
        and the caption says which window was used. No threshold is chosen
        after seeing the output.

COST
    2160 coupled realizations, about 6.4 hours on three workers. This buys one
    sensitivity check on one number. It is worth running only because that
    number is the paper's headline r-axis result.

HOW TO RUN
    python rmapj.py --workers 3 --quick     (smoke, about 1 minute)
    python rmapj.py --workers 3             (full, about 6.4 hours)

Writes rmapj_real.csv. Touches no existing file.
NumPy only. Python 3.8 compatible. regimemap.py must be in the same directory.
"""

import argparse
import csv
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

try:
    import regimemap as rm
except Exception as exc:                                    # pragma: no cover
    sys.stderr.write("cannot import regimemap.py from this directory: {}\n".format(exc))
    sys.exit(2)

SEED0 = 20260829
DIFFS = ["isotropic", "anisotropic"]
OBJS = ["ackley", "rastrigin", "sphere"]
DIMS_D = [5, 10, 20, 40, 80]
RS_D = [0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
TAU_D = 0.1
N_BOOT = 4000


def probe_beta(name, d, tau):
    """Identical to regimemap.py's getbeta: same probe size, same probe seed."""
    rng = np.random.default_rng(4242 + 131 * d + 7 * len(name))
    Xp = rng.standard_normal((4000, d))
    fv = rm.OBJ[name](Xp)
    return rm.solve_beta(fv - fv.min(), math.log(tau * 4000))


def job(a):
    name, d, diff, r, tau, rep, beta, sigma, lam, dt, K, Jinf, J_list, seed = a
    out = rm.one_realisation(name, d, diff, beta, sigma, lam, dt, K, Jinf, J_list, seed)
    return (name, d, diff, r, tau, rep, beta, sigma, seed,
            float(out["slope"]), [float(v) for v in out["E"]])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--reps", type=int, default=12)
    a = p.parse_args()

    lam, dt, T = 1.0, 0.01, 1.0
    K = int(round(T / dt))
    if a.quick:
        Jinf, Jgrid = 4000, [10, 40, 160, 400]
        objs, dims, rs, M = ["ackley", "sphere"], [10, 40], [1.0, 3.0], 3
    else:
        Jinf, Jgrid = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        objs, dims, rs, M = OBJS, DIMS_D, RS_D, a.reps
    J_list = [J for J in Jgrid if J <= Jinf // 10]

    print("=" * 90)
    print("CBO-GAP — Phase 11 Part D rerun with per-J errors archived")
    print("=" * 90)
    print("  dynamics, beta and slope fitting are imported from regimemap.py; nothing is retyped")
    print("  python {}   numpy {}   workers {}".format(sys.version.split()[0],
                                                       np.__version__, a.workers))
    print("  J grid {}   Jinf {}   reps/cell {}".format(J_list, Jinf, M))
    print("  seeds start at {} and increment by one, matching --part D\n".format(SEED0))

    tasks, s = [], SEED0
    for diff in DIFFS:
        for name in objs:
            for d in dims:
                for r in rs:
                    sg = rm.sigma_of(diff, d, r, lam)
                    b = probe_beta(name, d, TAU_D)
                    for rep in range(M):
                        s += 1
                        tasks.append((name, d, diff, r, TAU_D, rep, b, sg,
                                      lam, dt, K, Jinf, J_list, s))
    print("  {} realizations queued\n".format(len(tasks)))
    t0 = time.time()
    pool = Pool(processes=a.workers)
    try:
        res = pool.map(job, tasks, chunksize=1)
    finally:
        pool.close()
        pool.join()
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    w = csv.writer(open("rmapj_real.csv", "w", newline=""))
    w.writerow(["diffusion", "objective", "d", "r", "tau", "rep", "sigma", "beta",
                "seed", "slope"] + ["E_%d" % J for J in J_list])
    for (name, d, diff, r, tau, rep, beta, sigma, seed, sl, E) in res:
        w.writerow([diff, name, d, r, tau, rep, "%.6g" % sigma, "%.6g" % beta,
                    seed, "%.6f" % sl] + ["%.8g" % v for v in E])

    # ---------------- P-R1 ----------------
    print("\n" + "-" * 90)
    print("P-R1 — does this rerun reproduce the archived Part D slopes exactly?")
    print("-" * 90)
    if a.quick or not os.path.exists("regimemap_D_real.csv"):
        print("  skipped (quick mode, or regimemap_D_real.csv not present)")
    else:
        old = {}
        for x in csv.DictReader(open("regimemap_D_real.csv")):
            old[(x["diffusion"], x["objective"], int(x["d"]),
                 float(x["r"]), int(x["rep"]))] = float(x["slope"])
        worst, miss = 0.0, 0
        for (name, d, diff, r, tau, rep, beta, sigma, seed, sl, E) in res:
            k = (diff, name, d, r, rep)
            if k not in old:
                miss += 1
                continue
            worst = max(worst, abs(sl - old[k]))
        print("  cells compared: {}   not found in archive: {}".format(len(res) - miss, miss))
        print("  largest absolute slope discrepancy: {:.3e}".format(worst))
        if worst > 1e-6 or miss:
            print("\n  P-R1 FAIL — this is not a deterministic reproduction of the archived run.")
            print("  The refit below is not comparable to the manuscript. Send this and stop.")
            sys.exit(1)
        print("  P-R1 PASS")

    # ---------------- P-R2 ----------------
    print("\n" + "-" * 90)
    print("P-R2 — refit on J >= 20, the window in which tau_0 = 0.1 is not on the bound")
    print("-" * 90)
    keep = [J for J in J_list if J >= 20]
    idx = [J_list.index(J) for J in keep]
    lg_all = np.log(np.array(J_list, float))
    lg_res = np.log(np.array(keep, float))

    def fit(E, x):
        y = np.log(np.array(E, float))
        m = np.isfinite(y)
        return float(np.polyfit(x[m], y[m], 1)[0])

    cell_all, cell_res = {}, {}
    for (name, d, diff, r, tau, rep, beta, sigma, seed, sl, E) in res:
        cell_all.setdefault((diff, name, d, r), []).append(fit(E, lg_all))
        cell_res.setdefault((diff, name, d, r), []).append(fit([E[i] for i in idx], lg_res))

    rng = np.random.default_rng(20260827)

    def contrast(C, dif, d, lo, hi):
        A = [v for k, v in C.items() if k[0] == dif and k[2] == d and abs(k[3] - lo) < 1e-9]
        B = [v for k, v in C.items() if k[0] == dif and k[2] == d and abs(k[3] - hi) < 1e-9]
        a_ = np.array([np.mean(v) for v in A])
        b_ = np.array([np.mean(v) for v in B])
        return float(a_.mean() - b_.mean())

    print("  non-admissible severity, gamma(r=1) - gamma(r=3)\n")
    print("  %-12s %-5s %11s %11s %9s" % ("diffusion", "d", "full grid", "J >= 20", "shift"))
    for dif in DIFFS:
        for d in dims:
            u = contrast(cell_all, dif, d, 1.0, 3.0)
            v = contrast(cell_res, dif, d, 1.0, 3.0)
            print("  %-12s %-5d %+11.4f %+11.4f %+9.4f" % (dif, d, u, v, v - u))

    print("\n  dimension trend of that severity, per doubling of d\n")
    print("  %-12s %-11s %+11s %26s" % ("diffusion", "window", "trend", "95% interval"))
    trends = {}
    for dif in DIFFS:
        for lab, C in (("full grid", cell_all), ("J >= 20", cell_res)):
            keys = sorted({(k[1], i) for k in C for i in range(len(C[k]))})
            x = np.log2(np.array(dims, float))

            def one(sample):
                y = []
                for d in dims:
                    lo = [C[(dif, o, d, 1.0)][i] for o, i in sample if (dif, o, d, 1.0) in C]
                    hi = [C[(dif, o, d, 3.0)][i] for o, i in sample if (dif, o, d, 3.0) in C]
                    y.append(np.mean(lo) - np.mean(hi))
                return float(np.polyfit(x, np.array(y), 1)[0])
            base = one(keys)
            bs = [one([keys[j] for j in rng.integers(0, len(keys), len(keys))])
                  for _ in range(N_BOOT)]
            lo_, hi_ = np.percentile(bs, [2.5, 97.5])
            trends[(dif, lab)] = (base, lo_, hi_)
            print("  %-12s %-11s %+11.4f      [%+0.4f,%+0.4f]" % (dif, lab, base, lo_, hi_))

    # ---------------- P-R3 ----------------
    print("\n" + "-" * 90)
    print("P-R3 — which window does the manuscript report?")
    print("-" * 90)
    for dif in DIFFS:
        u = trends[(dif, "full grid")][0]
        v = trends[(dif, "J >= 20")][0]
        big = abs(u - v) > 0.026
        print("  %-12s full %+0.4f   restricted %+0.4f   shift %+0.4f   %s" %
              (dif, u, v, v - u,
               "REPORT RESTRICTED" if big else "restriction changes nothing, report full grid"))
    print("\n" + "=" * 90)
    print("wrote rmapj_real.csv")
    print("Send this entire console output and rmapj_real.csv.")
    print("=" * 90)


if __name__ == "__main__":
    main()
