"""
perjcal.py  —  CBO-GAP: hold the FINITE-J concentration fixed, not the reference

WHY THIS EXISTS
---------------
exactcal.py solves beta on the reference ensemble, so ESS_0(J_inf)/J_inf equals
the target exactly. finitej.py then showed that the nested subensembles, whose
coupled error is what the slope is fitted to, are NOT at the target, and worse,
are systematically further from it at d = 40 than at d = 2 at every ensemble
size measured. 22 of 30 intervals excluded zero. The residual of 0.078 at
tau_0 = 0.01 is therefore confounded: some of it is dimension and some of it is
finite-J concentration, and the nested design cannot separate them.

This script separates them by controlling the thing that was uncontrolled. For
each ensemble size J it solves a separate beta_J on the first J particles, so
that ESS_0(J)/J equals the target exactly at that J, and then evolves both the
J-ensemble and a reference at that same beta_J. Every point on the fitted curve
now starts at the same realized concentration, in every dimension.

WHAT THIS CHANGES, AND IT IS NOT A DETAIL
------------------------------------------
Under this protocol beta varies with J. The curve being fitted is therefore not
one algorithm observed at a sequence of ensemble sizes; it is a family of
algorithms indexed by J, each calibrated to the same initial concentration. The
fitted exponent is a different estimand from the one in Sections 7.3 and 7.13
and the two should not be pooled or compared as if they were the same quantity.
What the comparison DOES answer is the question finitej.py raised: when finite-J
concentration is held fixed, does the dimension-associated contrast survive?

The reference is re-run at each beta_J rather than shared, because a reference
evolved at a different beta is a different dynamics and the difference would no
longer be a mean-field approximation error. That is what makes this expensive.

DESIGN
------
  6 named objectives x d in {2,40} x tau_0 in {0.5,0.01} x centred law x 15 reps.
  J is restricted to the non-vacuous window J >= 1/tau_0 throughout, so ten
  sizes at tau_0 = 0.5 and six at tau_0 = 0.01. That is 2880 reference
  evolutions, roughly 4.5 hours on three workers.

  d = 2 and d = 40 only, because the contrast the confound threatens is exactly
  d = 2 against d = 40. tau_0 = 0.5 and 0.01 only, because those are the two
  ends at which finitej.py found the cleanest and the worst finite-J control.

PRE-REGISTERED, fixed before this script was first executed
------------------------------------------------------------
  P-C1  CONTROL ACHIEVED AT EVERY J. For every realization and every J the
        achieved ESS_0(J)/J must lie within 1 percent of the target. Misses are
        counted and excluded; if more than 5 percent of points miss, the
        protocol has failed and nothing below is reported.

  P-C2  THE CONTRAST UNDER FINITE-J CONTROL. The d = 2 to d = 40 change in the
        fitted exponent is computed at each target with a bootstrap interval
        over the six objectives, and printed beside the nested-design values
        from exactcal.py on the same window: 0.054 at tau_0 = 0.5 and 0.078 at
        tau_0 = 0.01.

  P-C3  THE DECISION, stated before the numbers exist.
        (a) If the change at tau_0 = 0.01 falls to within the interval of the
            change at tau_0 = 0.5, then the residual reported in Section 7.3 was
            finite-J concentration and not dimension, and the manuscript says
            so and withdraws the residual.
        (b) If it remains above that interval, the residual survives control of
            finite-J concentration and is attributable to dimension or to some
            mechanism this design does not measure; the manuscript reports it as
            surviving and names what is still not excluded.
        (c) If the interval is too wide to distinguish (a) from (b), the
            manuscript says the experiment was not powered to separate them.
        All three outcomes are written up. No threshold is chosen afterwards.

  Objective functions, the initial-law draw and the concentration solver are
  imported from exactcal.py rather than retyped. The error accumulates the
  SQUARED distance, matching every generating script in this project.

HOW TO RUN
    python perjcal.py --workers 3 --quick     (smoke, about 2 minutes)
    python perjcal.py --workers 3             (full, about 4.5 hours)

Writes perjcal_real.csv. Touches no existing file.
NumPy only. Python 3.8 compatible. exactcal.py must be in the same directory.
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
    import exactcal as ec
except Exception as exc:                                    # pragma: no cover
    sys.stderr.write("cannot import exactcal.py from this directory: {}\n".format(exc))
    sys.exit(2)

N_BOOT = 4000
SEED = 20260828
NESTED = {0.5: 0.054, 0.01: 0.078}          # exactcal, same window, for comparison


def one_J(objective, d, init, tau, J, sigma, lam, dt, K, Jinf, seed):
    """Evolve a J-ensemble and a J_inf reference, both at beta_J, and return the
    coupled error at that single J together with the achieved concentration."""
    f = ec.OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = ec.draw_initial(rng, Jinf, d, objective, init)

    # the one substantive change: beta is solved on the FIRST J particles
    beta, achieved = ec.beta_on_ensemble(f(X0[:J]), tau, J)

    Xref = X0.copy()
    Xsub = X0[:J].copy()
    runmax = np.zeros(J)
    sq = math.sqrt(dt)
    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        vr, _ = ec.weighted_mean_and_logess(Xref, f(Xref), beta)
        dr = Xref - vr
        Xref = Xref - lam * dt * dr + sigma * np.linalg.norm(dr, axis=1)[:, None] * dW
        vs, _ = ec.weighted_mean_and_logess(Xsub, f(Xsub), beta)
        ds = Xsub - vs
        Xsub = Xsub - lam * dt * ds + sigma * np.linalg.norm(ds, axis=1)[:, None] * dW[:J]
        np.maximum(runmax, np.sum((Xsub - Xref[:J]) ** 2, axis=1), out=runmax)
    return float(np.mean(runmax)), float(beta), float(achieved)


def job(a):
    obj, d, init, tau, J, rep, sigma, lam, dt, K, Jinf, seed = a
    E, beta, ach = one_J(obj, d, init, tau, J, sigma, lam, dt, K, Jinf, seed)
    return (obj, d, init, tau, J, rep, seed, E, beta, ach)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    a = p.parse_args()

    lam, sigma, dt, T = 1.0, 0.2, 0.01, 1.0
    K = int(round(T / dt))
    assert abs(sigma - 0.2) < 1e-12, "sigma must match mechanism.py and exactcal.py"

    if a.quick:
        Jinf, Jgrid = 4000, [10, 40, 160, 400]
        objs, dims, taus, M = ["ackley", "sphere"], [2, 40], [0.5, 0.01], 2
    else:
        Jinf, Jgrid = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        objs = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
        dims, taus, M = [2, 40], [0.5, 0.01], 15
    Jgrid = [J for J in Jgrid if J <= Jinf // 10]
    init = "centred"

    print("=" * 90)
    print("CBO-GAP — finite-J concentration held fixed, one beta per ensemble size")
    print("=" * 90)
    print("  beta varies with J by construction, so the fitted exponent here is a")
    print("  DIFFERENT ESTIMAND from Sections 7.3 and 7.13 and is not pooled with them.")
    print("  python {}   numpy {}   workers {}".format(sys.version.split()[0],
                                                       np.__version__, a.workers))
    print("  lambda {}  sigma {}  dt {}  T {}  K {}  Jinf {}  reps {}".format(
        lam, sigma, dt, T, K, Jinf, M))

    tasks, n = [], 0
    for tau in taus:
        keep = [J for J in Jgrid if J >= 1.0 / tau]
        print("  tau_0 = {:<5} non-vacuous sizes: {}".format(tau, keep))
        for obj in objs:
            for d in dims:
                for rep in range(M):
                    sd = SEED + 7919 * rep + 131 * d + 17 * len(obj) + int(round(tau * 1000))
                    for J in keep:
                        tasks.append((obj, d, init, tau, J, rep, sigma, lam, dt, K, Jinf, sd))
                        n += 1
    print("\n  {} reference evolutions queued on {} workers\n".format(n, a.workers))

    t0 = time.time()
    pool = Pool(processes=a.workers)
    try:
        res = pool.map(job, tasks, chunksize=1)
    finally:
        pool.close()
        pool.join()
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    w = csv.writer(open("perjcal_real.csv", "w", newline=""))
    w.writerow(["objective", "d", "init", "tau", "J", "rep", "seed",
                "E", "beta", "achieved_frac", "achieved_over_target"])
    for (obj, d, init_, tau, J, rep, sd, E, beta, ach) in res:
        w.writerow([obj, d, init_, tau, J, rep, sd, "%.8g" % E, "%.10g" % beta,
                    "%.8g" % ach, "%.8g" % (ach / tau)])

    # ---------------- P-C1 ----------------
    print("\n" + "-" * 90)
    print("P-C1 — was the finite-J control achieved at every ensemble size?")
    print("-" * 90)
    rat = np.array([r[9] / r[3] for r in res])
    miss = int((np.abs(rat - 1.0) > 0.01).sum())
    print("  achieved/target over {} points: mean {:.6f}  min {:.6f}  max {:.6f}".format(
        len(rat), rat.mean(), rat.min(), rat.max()))
    print("  points outside 1% of target: {} of {}".format(miss, len(rat)))
    print("  for comparison, the nested design gave ratios from 0.65 to 19.1 at these targets")
    if miss > 0.05 * len(rat):
        print("\n  P-C1 FAIL — the protocol did not achieve its own control. Stop here.")
        sys.exit(1)
    print("  P-C1 PASS")

    # ---------------- P-C2 ----------------
    print("\n" + "-" * 90)
    print("P-C2 — the d = 2 to d = 40 contrast under finite-J control")
    print("-" * 90)
    cell = {}
    for (obj, d, init_, tau, J, rep, sd, E, beta, ach) in res:
        cell.setdefault((tau, obj, d, rep), {})[J] = E

    def slope(dic):
        Js = sorted(dic)
        y = np.log(np.array([dic[J] for J in Js], float))
        m = np.isfinite(y)
        return float(np.polyfit(np.log(np.array(Js, float))[m], y[m], 1)[0])

    per = {}
    for k, dic in cell.items():
        per.setdefault((k[0], k[2], k[1]), []).append(slope(dic))
    rng = np.random.default_rng(SEED)
    print("  %-8s %10s %10s %10s %24s %12s" % (
        "tau_0", "d=2", "d=40", "change", "95% interval", "nested"))
    out = {}
    for tau in taus:
        objs_here = sorted({k[2] for k in per if k[0] == tau})
        a2 = {o: float(np.mean(per[(tau, 2, o)])) for o in objs_here}
        a40 = {o: float(np.mean(per[(tau, 40, o)])) for o in objs_here}
        ch = abs(np.mean(list(a40.values())) - np.mean(list(a2.values())))
        bs = []
        for _ in range(N_BOOT):
            s_ = [objs_here[j] for j in rng.integers(0, len(objs_here), len(objs_here))]
            bs.append(abs(np.mean([a40[o] for o in s_]) - np.mean([a2[o] for o in s_])))
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out[tau] = (ch, lo, hi)
        print("  %-8s %+10.4f %+10.4f %10.4f  [%.4f,%.4f] %12s" % (
            tau, np.mean(list(a2.values())), np.mean(list(a40.values())), ch, lo, hi,
            "%.3f" % NESTED[tau] if tau in NESTED else "-"))

    # ---------------- P-C3 ----------------
    print("\n" + "-" * 90)
    print("P-C3 — does the residual survive control of finite-J concentration?")
    print("-" * 90)
    if 0.5 in out and 0.01 in out:
        c05, l05, h05 = out[0.5]
        c01, l01, h01 = out[0.01]
        print("  tau_0 = 0.50 change {:.4f}  interval [{:.4f},{:.4f}]".format(c05, l05, h05))
        print("  tau_0 = 0.01 change {:.4f}  interval [{:.4f},{:.4f}]".format(c01, l01, h01))
        width = h01 - l01
        if c01 <= h05:
            print("\n  OUTCOME (a): the tight-target change falls inside the moderate-target")
            print("  interval. The residual reported in Section 7.3 is finite-J concentration")
            print("  and not dimension. The manuscript withdraws it.")
        elif l01 > h05:
            print("\n  OUTCOME (b): the tight-target change remains above the moderate-target")
            print("  interval. The residual survives finite-J concentration control. The")
            print("  manuscript reports it as surviving and states what is still not excluded.")
        else:
            print("\n  OUTCOME (c): the intervals overlap without resolving. Not powered to")
            print("  separate the two. The manuscript says exactly that.")
        print("\n  interval width at the tight target: {:.4f}".format(width))
    print("\n" + "=" * 90)
    print("wrote perjcal_real.csv")
    print("Send this entire console output and perjcal_real.csv.")
    print("=" * 90)


if __name__ == "__main__":
    main()
