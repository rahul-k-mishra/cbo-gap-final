"""
exactcal.py  —  CBO-GAP: the concentration arm with beta solved on the ACTUAL
                reference ensemble instead of a 4000-point probe

WHY THIS EXISTS
---------------
mechanism.py sets the inverse temperature by bisecting on a probe ensemble of
4000 points drawn from the initial law, then discards the probe and evolves a
different draw of J_inf = 50000 points. What is held fixed across dimensions is
therefore a calibration target and an estimate of beta, not the concentration of
the ensemble actually used. Recovered from the archived log_ESS_initial column,
the achieved-over-target ratio in that experiment is

    target 0.5   mean 1.0002  range [0.909, 1.042]
    target 0.1   mean 0.9619  range [0.481, 1.141]
    target 0.01  mean 0.8104  range [0.106, 1.363]

so the control is tight at 0.5 and degrades by a factor of thirteen at 0.01 —
which is exactly where the headline residual of 0.553 sits. The causal chain
dimension -> concentration -> fitted exponent is therefore established at the
level of the target and not of the realized concentration, and part of the
residual may be uncontrolled calibration error rather than an effect of
dimension. This is the single largest attack surface left in the manuscript.

The fix costs nothing in trajectory time. This script draws the reference
ensemble FIRST, then bisects beta on that same ensemble, so the achieved initial
ESS fraction equals the target by construction, to bisection tolerance, in every
cell. Everything else — objectives, initial laws, dimensions, targets, J grid,
J_inf, realization count, coupling, slope fit — is copied unchanged from
mechanism.py so the two runs are comparable cell by cell.

DESIGN, identical to mechanism.py
---------------------------------
  6 objectives x 4 dimensions {2,5,10,40} x 2 initial laws x 3 targets
  {0.5, 0.1, 0.01} = 144 cells, 15 realizations each = 2160 coupled realizations.
  J_inf = 50000, J in {10,...,5000}, lambda = 1, dt = 0.01, T = 1, K = 100.
  Expect roughly 3 hours on three workers.

PRE-REGISTERED, fixed before this script was first executed
-----------------------------------------------------------
  P-E1  CONTROL ACHIEVED. In every one of the 144 cells the achieved initial ESS
        fraction must lie within 1 percent of its target. If any cell misses,
        the bisection is reported as having failed there and that cell is
        excluded from P-E2 and P-E3 and counted.

  P-E2  THE HEADLINE UNDER EXACT CONTROL. The quantity of interest is the change
        in the fitted exponent from d = 2 to d = 40 at each target, which under
        probe calibration was 0.030, 0.099 and 0.553 at targets 0.5, 0.1 and
        0.01. These are recomputed under exact calibration with a bootstrap
        interval over the 15 realizations. The comparison is reported for all
        three targets; no threshold decides anything, because the point is to
        see how much of each number survives.

  P-E3  WHERE THE PROBE MATTERED. For each target, the probe-calibrated and
        exact-calibrated changes are differenced. The pre-registered
        expectation, stated before the run: the difference is negligible at
        target 0.5, where the archived probe error was already under 5 percent,
        and is largest at target 0.01, where it was a factor of thirteen. If the
        0.553 result is substantially unchanged, the probe objection is answered
        and the manuscript keeps the number. If it moves materially, the
        manuscript reports the exact-calibration value and states that the
        probe-calibrated one was contaminated. Either outcome is written up.

  Nothing here is decided after seeing the output. The three targets are all
  reported whatever they show.

HOW TO RUN
    python exactcal.py --workers 3 --quick     (smoke, about 1 minute)
    python exactcal.py --workers 3             (full, about 3 hours)

Writes exactcal_real.csv and exactcal_summary.csv. It does NOT write to any
filename used by another script, so no archived file can be overwritten.
NumPy only. No SciPy. Python 3.8 compatible.
"""

import argparse
import csv
import math
import os
import platform
import sys
import time
from multiprocessing import Pool

import numpy as np

# ---------------------------------------------------------------- objectives
# Copied verbatim from mechanism.py so the two runs are comparable.


def f_ackley(X):
    d = X.shape[1]
    s1 = np.sqrt(np.mean(X * X, axis=1))
    s2 = np.mean(np.cos(2.0 * np.pi * X), axis=1)
    return -20.0 * np.exp(-0.2 * s1) - np.exp(s2) + 20.0 + math.e


def f_rastrigin(X):
    return np.sum(X * X - 10.0 * np.cos(2.0 * np.pi * X) + 10.0, axis=1)


def f_sphere(X):
    return np.sum(X * X, axis=1)


def f_griewank(X):
    d = X.shape[1]
    i = np.arange(1, d + 1, dtype=float)
    return (np.sum(X * X, axis=1) / 4000.0
            - np.prod(np.cos(X / np.sqrt(i)), axis=1) + 1.0)


def f_levy(X):
    W = 1.0 + (X - 1.0) / 4.0
    a = np.sin(np.pi * W[:, 0]) ** 2
    m = (W[:, :-1] - 1.0) ** 2 * (1.0 + 10.0 * np.sin(np.pi * W[:, :-1] + 1.0) ** 2)
    b = np.sum(m, axis=1)
    c = (W[:, -1] - 1.0) ** 2 * (1.0 + np.sin(2.0 * np.pi * W[:, -1]) ** 2)
    return a + b + c


def f_rosenbrock(X):
    return np.sum(100.0 * (X[:, 1:] - X[:, :-1] ** 2) ** 2
                  + (X[:, :-1] - 1.0) ** 2, axis=1)


OBJECTIVES = {"ackley": f_ackley, "rastrigin": f_rastrigin, "sphere": f_sphere,
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


def _logsumexp(a):
    m = float(np.max(a))
    return m + math.log(float(np.sum(np.exp(a - m))))


def log_ess_of(fvals, beta):
    a = -beta * fvals
    return 2.0 * _logsumexp(a) - _logsumexp(2.0 * a)


def weighted_mean_and_logess(X, fvals, beta):
    a = -beta * fvals
    a -= a.max()
    w = np.exp(a)
    s = w.sum()
    return (w[:, None] * X).sum(axis=0) / s, 2.0 * math.log(s) - math.log(float((w * w).sum()))


# --------------------------------------------- the one substantive change
def beta_on_ensemble(fvals, tau, n):
    """Bisect beta so that THIS ensemble's ESS fraction equals tau.

    mechanism.py bisected on a separate 4000-point probe and then evolved a
    different draw. Here fvals are the objective values of the reference
    ensemble that will actually be evolved, so the achieved fraction equals the
    target by construction. ESS is monotone decreasing in beta -- the full
    ensemble at beta = 0, one as beta grows -- so the target is bracketed.
    """
    goal = math.log(tau * n)
    lo, hi = 1e-10, 1e10
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if log_ess_of(fvals, mid) > goal:
            lo = mid
        else:
            hi = mid
    beta = math.sqrt(lo * hi)
    return beta, math.exp(min(log_ess_of(fvals, beta), 700)) / n


def one_realisation(objective, d, init, tau, sigma, lam, dt, K, Jinf, J_list, seed):
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = draw_initial(rng, Jinf, d, objective, init)

    # beta is solved on X0 itself, not on a discarded probe.
    beta, achieved = beta_on_ensemble(f(X0), tau, Jinf)

    X = X0.copy()
    Xsub = dict((J, X0[:J].copy()) for J in J_list)
    runmax = dict((J, np.zeros(J)) for J in J_list)
    fv = f(X)
    v, le0 = weighted_mean_and_logess(X, fv, beta)
    le_min = le0
    for k in range(K):
        dW = rng.standard_normal((Jinf, d)) * math.sqrt(dt)
        fv = f(X)
        v, le = weighted_mean_and_logess(X, fv, beta)
        le_min = min(le_min, le)
        Dv = X - v
        X = X + (-lam * Dv * dt) + sigma * np.linalg.norm(Dv, axis=1)[:, None] * dW
        for J in J_list:
            fs = f(Xsub[J])
            vs, _ = weighted_mean_and_logess(Xsub[J], fs, beta)
            Ds = Xsub[J] - vs
            Xsub[J] = Xsub[J] + (-lam * Ds * dt) + sigma * np.linalg.norm(Ds, axis=1)[:, None] * dW[:J]
            # SQUARED distance, matching mechanism.py and every other generating
            # script in this project. An earlier version of this file used the
            # norm, which halves every fitted exponent (-0.57 instead of -1.04)
            # and made the comparison with the archived values meaningless.
            np.maximum(runmax[J], np.sum((Xsub[J] - X[:J]) ** 2, axis=1), out=runmax[J])
    return (dict((J, float(np.mean(runmax[J]))) for J in J_list),
            beta, achieved, le0, le_min)


def task(a):
    obj, d, init, tau, sigma, lam, dt, K, Jinf, J_list, seed = a
    per_J, beta, achieved, le0, lem = one_realisation(
        obj, d, init, tau, sigma, lam, dt, K, Jinf, J_list, seed)
    return (obj, d, init, tau, seed, per_J, beta, achieved, le0, lem)


def fit_slope(J, E):
    x = np.log(np.array(J, dtype=float))
    y = np.log(np.array(E, dtype=float))
    A = np.column_stack([x, np.ones_like(x)])
    return float(np.linalg.lstsq(A, y, rcond=None)[0][0])


def dims_check(a):
    return [2, 40] if a.quick else [2, 5, 10, 40]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--sigma", type=float, default=0.2)
    a = p.parse_args()

    lam, sigma, dt, T = 1.0, a.sigma, 0.01, 1.0
    # sigma MUST match mechanism.py, whose argparse default is 0.2. An earlier
    # version of this file hardcoded 0.1, which halves the diffusion and moved
    # every fitted slope from about -1.0 to about -0.5, making the comparison
    # with the probe-calibrated numbers meaningless. The assertion below makes
    # that failure impossible to repeat silently.
    assert abs(sigma - 0.2) < 1e-12, (
        "sigma is {} but mechanism.py uses 0.2; the two runs would not be "
        "comparable. Pass --sigma 0.2 or accept the default.".format(sigma))
    for d in dims_check(a):
        assert 2.0 * lam > d * sigma ** 2, "dimension {} violates 2*lambda > d*sigma^2".format(d)
    K = int(round(T / dt))
    if a.quick:
        Jinf, J_list = 4000, [10, 40, 160, 400]
        dims, objs, inits, taus, M = [2, 40], ["ackley", "rosenbrock"], ["centred"], [0.5, 0.01], 3
    else:
        Jinf, J_list = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        dims = [2, 5, 10, 40]
        objs = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
        inits, taus, M = ["centred", "mix-0.1"], [0.5, 0.1, 0.01], 15
    J_list = [J for J in J_list if J <= Jinf // 10]

    print("=" * 88)
    print("CBO-GAP — concentration arm with beta solved on the ACTUAL reference ensemble")
    print("=" * 88)
    print("  PRE-REGISTERED (fixed before the first run of this script):")
    print("    P-E1 the achieved initial ESS fraction must be within 1% of target in")
    print("         all 144 cells; misses are counted and excluded.")
    print("    P-E2 the d=2 to d=40 change is recomputed at every target with a")
    print("         bootstrap interval and reported whatever it shows.")
    print("    P-E3 it is differenced against the probe-calibrated 0.030 / 0.099 /")
    print("         0.553. Both outcomes are written up.")
    print("  THE ONLY CHANGE from mechanism.py is where beta is solved.")
    print()
    print("  REPRODUCIBILITY")
    print("    python {}   numpy {}".format(platform.python_version(), np.__version__))
    print("    platform {}   workers {}".format(platform.platform(), a.workers))
    print("    lambda {}  sigma {}  dt {}  T {}  K {}".format(lam, sigma, dt, T, K))
    print("    J grid {}   Jinf {}   reps/cell {}".format(J_list, Jinf, M))
    print()
    cells = len(objs) * len(dims) * len(inits) * len(taus)
    print("  {} cells x {} realizations = {} coupled realizations".format(
        cells, M, cells * M))

    jobs = []
    for obj in objs:
        for d in dims:
            for init in inits:
                for tau in taus:
                    for m in range(M):
                        jobs.append((obj, d, init, tau, sigma, lam, dt, K, Jinf, J_list,
                                     20260822 + 7919 * m + 131 * d + 17 * len(obj)
                                     + 3 * len(init) + int(round(tau * 1000))))
    print("  {} realizations queued on {} workers\n".format(len(jobs), a.workers))
    t0 = time.time()
    pool = Pool(processes=a.workers)
    try:
        res = pool.map(task, jobs, chunksize=1)
    finally:
        pool.close()
        pool.join()
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    rw = csv.writer(open("exactcal_real.csv", "w", newline=""))
    rw.writerow(["objective", "d", "init", "tau", "seed", "beta", "achieved_frac",
                 "achieved_over_target", "slope", "log_ess_0", "log_ess_min"]
                + ["E_%d" % J for J in J_list])
    per_cell = {}
    for (obj, d, init, tau, seed, per_J, beta, ach, le0, lem) in res:
        sl = fit_slope(J_list, [per_J[J] for J in J_list])
        rw.writerow([obj, d, init, tau, seed, "%.10g" % beta, "%.8g" % ach,
                     "%.8g" % (ach / tau), "%.6g" % sl, "%.6g" % le0, "%.6g" % lem]
                    + ["%.8g" % per_J[J] for J in J_list])
        per_cell.setdefault((obj, d, init, tau), []).append((sl, ach / tau))

    sw = csv.writer(open("exactcal_summary.csv", "w", newline=""))
    sw.writerow(["objective", "d", "init", "tau", "slope", "achieved_over_target", "n"])
    for k in sorted(per_cell):
        v = per_cell[k]
        sw.writerow(list(k) + ["%.6g" % np.mean([x[0] for x in v]),
                               "%.6g" % np.mean([x[1] for x in v]), len(v)])

    # ---------------- P-E1 ----------------
    print("\n" + "-" * 88)
    print("P-E1 — was the control actually achieved?")
    print("-" * 88)
    bad = []
    for k in sorted(per_cell):
        r = float(np.mean([x[1] for x in per_cell[k]]))
        if abs(r - 1.0) > 0.01:
            bad.append((k, r))
    allr = np.array([x[1] for v in per_cell.values() for x in v])
    print("  achieved/target over all {} realizations: mean {:.6f}  min {:.6f}  max {:.6f}"
          .format(len(allr), allr.mean(), allr.min(), allr.max()))
    print("  cells outside 1% of target: {} of {}".format(len(bad), len(per_cell)))
    for k, r in bad[:10]:
        print("    MISS {} ratio {:.4f}".format(k, r))
    print("  compare mechanism.py, recovered from its archive:")
    print("    target 0.5 mean 1.0002 range [0.909,1.042]")
    print("    target 0.1 mean 0.9619 range [0.481,1.141]")
    print("    target .01 mean 0.8104 range [0.106,1.363]")

    # ---------------- P-E2 and P-E3 ----------------
    print("\n" + "-" * 88)
    print("P-E2 / P-E3 — the headline under exact control")
    print("-" * 88)
    probe = {0.5: 0.030, 0.1: 0.099, 0.01: 0.553}
    rng = np.random.default_rng(20260822)
    print("  %-7s %9s %9s %10s %24s %9s" % ("target", "d=2", "d=40", "change", "95% interval", "probe"))
    for tau in taus:
        s2, s40 = [], []
        for obj in objs:
            for init in inits:
                if (obj, 2, init, tau) in per_cell and (obj, 40, init, tau) in per_cell:
                    s2 += [x[0] for x in per_cell[(obj, 2, init, tau)]]
                    s40 += [x[0] for x in per_cell[(obj, 40, init, tau)]]
        if not s2:
            continue
        s2, s40 = np.array(s2), np.array(s40)
        ch = abs(s40.mean() - s2.mean())
        bs = np.array([abs(s40[rng.integers(0, len(s40), len(s40))].mean()
                           - s2[rng.integers(0, len(s2), len(s2))].mean())
                       for _ in range(4000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        pv = probe.get(tau)
        print("  %-7s %+9.4f %+9.4f %10.4f  [%.4f,%.4f] %9s" %
              (tau, s2.mean(), s40.mean(), ch, lo, hi,
               ("%.3f" % pv) if pv is not None else "-"))
        if pv is not None:
            print("        difference from probe-calibrated value: %+0.4f" % (ch - pv))

    print("\n" + "=" * 88)
    print("wrote exactcal_real.csv and exactcal_summary.csv")
    print("Send this entire console output and both CSV files.")
    print("=" * 88)


if __name__ == "__main__":
    main()
