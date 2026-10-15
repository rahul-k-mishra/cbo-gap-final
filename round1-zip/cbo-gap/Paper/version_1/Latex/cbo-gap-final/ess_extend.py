"""
ess_extend.py  —  CBO-GAP Phase 1b: is the exponent a function of d alone?

WHAT THIS SCRIPT IS FOR, IN PLAIN LANGUAGE
------------------------------------------
The first sweep found two things. At d = 2 the Monte Carlo rate is recovered at
every beta tested, both objectives, both diffusion types. At d = 5 and d = 10 it
is not, and instead the error settles onto a slope that is remarkably stable in
beta but falls sharply with d — standard deviation 0.008 across three decades of
beta at d = 10. Ackley and Rastrigin settled onto DIFFERENT slopes at the same d.

That leaves exactly one question worth spending compute on:

    Is the observed exponent a function of the dimension alone, or of the
    dimension together with how far the objective spreads the Boltzmann weights?

This script answers it, and kills one confound while doing so.

  THE CONFOUND. Rastrigin is unbounded and its spread over the initial cloud
  grows with d; Ackley is bounded and its spread saturates. So at a common beta
  the two objectives are NOT being compared at a common weight concentration —
  they differ in the growth exponent ell AND in scale at the same time. Any
  claim about ell drawn from the first sweep is uninterpretable.

  THE FIX. Multiplying the objective by a constant is exactly the same thing as
  dividing beta by that constant — this is a reparameterisation, not a new
  experiment, and it is worth nothing on its own. Its value is that it supplies
  a common axis. We therefore control the product

      B := beta * spread(f, d)

  where spread is the standard deviation of f over the initial law, estimated
  once per (objective, d) from a fixed sample. Sweeping B and solving for beta
  puts both objectives at matched weight concentration at every d, so any
  remaining difference between them is not a scale artefact.

  WHAT WE THEN COMPUTE. The slope of log Ehat against log J for
  d in {2, 3, 5, 10, 20, 40}, and a fit of |slope| against d as a power law.
  If the exponent is a clean function of d, the two objectives collapse onto one
  curve. If they do not collapse, the exponent depends on the objective as well,
  and no single dimension formula can be claimed.

  WHY d STOPS AT 40. FKR require 2*lambda > d*sigma^2. With lambda = 1 and
  sigma = 0.2 that is d < 50. Running d = 50 or beyond would put the rows
  outside the hypothesis the whole paper is comparing against, so the grid
  stops short of it rather than producing numbers that have to be discarded.

WHAT THIS SCRIPT CANNOT DO
--------------------------
It cannot separate "the exponent is 2/d" from any other decaying function of d
on six points. It reports the fitted power and its residuals and leaves the
mechanism open. The earlier extreme-order-statistics guess of 2/d was checked
against the first sweep and did not fit — the ratio of measured slope to 2/d
drifted from 1.10 to 1.65 — so no mechanism is assumed here.

The reference run is a large-J proxy, not the mean-field limit, so every J above
Jinf/10 is refused. Rows whose effective sample size reaches 1 are in the
hardmin regime and their slope is not a rate; they are flagged.

HOW TO RUN
----------
    python ess_extend.py --workers 3 --quick     (smoke test, ~2 minutes)
    python ess_extend.py --workers 3             (the real sweep, ~1-2 hours)

NumPy only. No SciPy. Python 3.8 compatible.
Writes ess_extend_raw.csv and ess_extend_summary.csv.
"""

import argparse
import csv
import math
import os
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402


def f_ackley(X):
    d = X.shape[1]
    s1 = np.sqrt(np.sum(X * X, axis=1) / d)
    s2 = np.sum(np.cos(2.0 * np.pi * X), axis=1) / d
    return -20.0 * np.exp(-0.2 * s1) - np.exp(s2) + 20.0 + math.e


def f_rastrigin(X):
    return np.sum(X * X + 10.0 * (1.0 - np.cos(2.0 * np.pi * X)), axis=1)


OBJECTIVES = {"ackley": f_ackley, "rastrigin": f_rastrigin}


def spread_of(objective, d, n=20000, seed=12345):
    """Standard deviation of the objective over the initial law N(0, I_d).
    This is the scale that multiplies beta inside the Boltzmann weights."""
    rng = np.random.default_rng(seed + 1000 * d)
    X = rng.standard_normal((n, d))
    return float(np.std(OBJECTIVES[objective](X)))


def weighted_mean_and_ess(X, fvals, beta):
    shift = fvals.min()
    w = np.exp(-beta * (fvals - shift))
    s = w.sum()
    m = (w[:, None] * X).sum(axis=0) / s
    return m, float((s * s) / (w * w).sum())


def one_realisation(objective, beta, d, sigma, dt, K, Jinf, J_list, seed):
    """Synchronous coupling: one reference system of Jinf particles, and a
    J-particle system for each J started from the same positions and driven by
    the same Brownian increments as the reference system's first J particles.
    Each sub-system computes its own consensus point from its own particles."""
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = rng.standard_normal((Jinf, d))
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    ess_ref = float(Jinf)
    sq = math.sqrt(dt)

    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        m, e = weighted_mean_and_ess(Xref, f(Xref), beta)
        ess_ref = min(ess_ref, e)
        dref = Xref - m
        Xref = Xref - dt * dref + sigma * np.linalg.norm(dref, axis=1)[:, None] * dW
        for J in J_list:
            Xj = Xsub[J]
            mj, _ = weighted_mean_and_ess(Xj, f(Xj), beta)
            dj = Xj - mj
            Xsub[J] = Xj - dt * dj + sigma * np.linalg.norm(dj, axis=1)[:, None] * dW[:J]
            diff = np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1)
            np.maximum(runmax[J], diff, out=runmax[J])

    return {J: float(np.mean(runmax[J])) for J in J_list}, ess_ref


def task(a):
    obj, B, beta, d, sigma, dt, K, Jinf, J_list, seed = a
    per_J, ess = one_realisation(obj, beta, d, sigma, dt, K, Jinf, J_list, seed)
    return obj, B, beta, d, per_J, ess


def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--sigma", type=float, default=0.2)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260818)
    args = p.parse_args()

    lam = 1.0
    K = int(round(args.T / args.dt))

    if args.quick:
        Jinf, J_list = 4000, [10, 40, 160, 320]
        dims, Bs, M = [2, 5, 10], [30.0, 300.0], 3
    else:
        Jinf, J_list = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        dims, Bs, M = [2, 3, 5, 10, 20, 40], [30.0, 300.0, 3000.0], 20
    J_list = [J for J in J_list if J <= Jinf // 10]

    print("=" * 76)
    print("CBO-GAP Phase 1b — exponent versus dimension at matched beta*spread")
    print("=" * 76)
    print("  Jinf {}   J {}   realisations {}".format(Jinf, J_list, M))
    print("  sigma {}   dt {}   T {}   steps {}".format(args.sigma, args.dt, args.T, K))

    print("\n  FKR condition 2*lambda > d*sigma^2 (grid stops before it fails):")
    bad = set()
    for d in dims:
        ok = 2.0 * lam > d * args.sigma ** 2
        if not ok:
            bad.add(d)
        print("    d={:<4} 2*lambda={:.3f}  d*sigma^2={:.3f}   {}".format(
            d, 2.0 * lam, d * args.sigma ** 2, "ok" if ok else "VIOLATED — drop"))

    print("\n  spread of each objective over N(0, I_d), and the beta each B implies:")
    spread = {}
    print("    {:<10} {:>4} {:>12}".format("objective", "d", "spread") +
          "".join("{:>14}".format("beta@B=" + "{:g}".format(B)) for B in Bs))
    for obj in ("ackley", "rastrigin"):
        for d in dims:
            sp = spread_of(obj, d)
            spread[(obj, d)] = sp
            print("    {:<10} {:>4} {:>12.4f}".format(obj, d, sp) +
                  "".join("{:>14.5g}".format(B / sp) for B in Bs))
    print("\n  READ THIS: matching B is a reparameterisation, not a new physics.")
    print("  Its only job is to put the two objectives on a common weight-")
    print("  concentration axis so a difference between them cannot be scale.")

    tasks, s = [], args.seed
    for obj in ("ackley", "rastrigin"):
        for B in Bs:
            for d in dims:
                if d in bad:
                    continue
                beta = B / spread[(obj, d)]
                for _ in range(M):
                    s += 1
                    tasks.append((obj, B, beta, d, args.sigma, args.dt, K,
                                  Jinf, J_list, s))

    print("\n  {} realisations queued on {} workers\n".format(len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    agg = {}
    for obj, B, beta, d, per_J, ess in res:
        k = (obj, B, d)
        if k not in agg:
            agg[k] = {"beta": beta, "E": {J: [] for J in J_list}, "ess": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        agg[k]["ess"].append(ess)

    with open("ess_extend_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "B", "beta", "spread", "d", "J", "Ehat",
                    "stderr", "min_ESS_ref", "realisations"])
        for (obj, B, d), r in sorted(agg.items()):
            for J in J_list:
                v = np.array(r["E"][J])
                w.writerow([obj, B, "{:.6g}".format(r["beta"]),
                            "{:.6g}".format(spread[(obj, d)]), d, J,
                            "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.4f}".format(np.mean(r["ess"])), len(v)])

    print("\n" + "-" * 76)
    print("slope versus dimension, at matched B = beta * spread")
    print("-" * 76)
    print("  Recovered means slope <= -0.85: the bound GHV prove is one-sided,")
    print("  so decay FASTER than J^-1 is consistent with it and only flatter")
    print("  slopes fail. -2/d is printed for reference only; it did not fit the")
    print("  first sweep and is not a hypothesis here.\n")

    hdr = "  {:<10} {:>8} {:>4} {:>10} {:>10} {:>9} {:>16}"
    print(hdr.format("objective", "B", "d", "slope", "min ESS", "-2/d", "verdict"))
    summary, curves = [], {}
    for (obj, B, d), r in sorted(agg.items()):
        E = np.array([np.mean(r["E"][J]) for J in J_list])
        sl = fit_slope(np.array(J_list, float), E)
        ess = float(np.mean(r["ess"]))
        verdict = ("SATURATED" if ess < 1.01 else
                   ("recovered" if sl <= -0.85 else "NOT observed"))
        print(hdr.format(obj, "{:g}".format(B), d, "{:.4f}".format(sl),
                         "{:.3f}".format(ess), "{:.4f}".format(-2.0 / d), verdict))
        summary.append([obj, B, r["beta"], d, "{:.6f}".format(sl),
                        "{:.4f}".format(ess), verdict])
        curves.setdefault((obj, B), []).append((d, sl))

    with open("ess_extend_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "B", "beta", "d", "slope", "min_ESS_ref", "verdict"])
        w.writerows(summary)

    print("\n" + "-" * 76)
    print("power-law fit  |slope| = c * d^(-p)")
    print("-" * 76)
    print("  p near 1 would mean the exponent behaves like a constant over d.")
    print("  What matters more than p is the residual: a large residual means no")
    print("  power law describes it, and none should then be claimed.\n")
    print("  {:<10} {:>8} {:>8} {:>10} {:>12}".format("objective", "B", "p", "c", "max resid"))
    for (obj, B), pts in sorted(curves.items()):
        pts = sorted(pts)
        dd = np.array([q[0] for q in pts], float)
        ss = np.abs(np.array([q[1] for q in pts], float))
        m = np.isfinite(ss) & (ss > 0)
        if m.sum() < 3:
            continue
        A = np.vstack([np.log(dd[m]), np.ones(m.sum())]).T
        sol, _, _, _ = np.linalg.lstsq(A, np.log(ss[m]), rcond=None)
        pexp, c = -float(sol[0]), math.exp(float(sol[1]))
        resid = np.max(np.abs(np.log(ss[m]) - (A @ sol)))
        print("  {:<10} {:>8g} {:>8.4f} {:>10.4f} {:>12.4f}".format(obj, B, pexp, c, resid))

    print("\n" + "-" * 76)
    print("do the two objectives collapse at matched B?")
    print("-" * 76)
    for B in Bs:
        for d in dims:
            if d in bad:
                continue
            a = curves.get(("ackley", B), [])
            r = curves.get(("rastrigin", B), [])
            av = dict(a).get(d)
            rv = dict(r).get(d)
            if av is None or rv is None:
                continue
            gap = abs(av - rv)
            tag = "collapse" if gap < 0.10 else "NO collapse — objective matters"
            print("    B={:<8g} d={:<4} ackley {:+.4f}   rastrigin {:+.4f}   gap {:.4f}  {}".format(
                B, d, av, rv, gap, tag))
    print("\n  READ THIS: collapse at every d would license a statement about the")
    print("  dimension alone. A persistent gap means the exponent depends on the")
    print("  objective too, and the dimension formula must not be written.")

    print("\n" + "=" * 76)
    print("wrote ess_extend_raw.csv and ess_extend_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 76)


if __name__ == "__main__":
    main()
