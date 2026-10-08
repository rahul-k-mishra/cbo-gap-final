"""
mechanism.py  —  CBO-GAP Phase 3: is weight concentration the mechanism?

WHY THIS SCRIPT EXISTS
----------------------
Phase 2 ran 2880 realisations and produced three results, none of which was the
one it set out to measure.

  (a) There is no crossover. Across 144 cells the slope fitted on J <= 160 and
      the slope fitted on J >= 640 differ by a mean of -0.008 and a median of
      +0.014. The log-log curves are straight over three decades of ensemble
      size. Consequently the quantity Phase 2 was built to measure — the
      smallest ensemble at which the proven rate becomes observable — does not
      exist within reach: the error follows a power law with an exponent that
      is not -1 and stays on it. No ensemble size in range makes the guarantee
      visible.

  (b) The control variable was wrong. Matching the product of beta and the
      objective's spread does NOT match weight concentration. At the matched
      value used throughout Phases 1b, 1c and 2, the achieved effective sample
      size at d = 2 ranged from 181 for Ackley to 26340 for Rosenbrock — two
      orders of magnitude apart. Rosenbrock was running with near-uniform
      weights, which is why it appeared to keep the rate at every dimension.
      Every cross-objective comparison in this project so far is compromised by
      this, including the ones this project reported as findings.

  (c) Effective sample size orders but does not predict. Pooled Spearman
      correlation with the slope is -0.746 over 144 cells, and within a fixed
      dimension at d >= 10 it reaches -1.000. But log ESS alone explains only
      R^2 = 0.20 of the variance in the slope, dimension alone 0.17, and both
      together 0.28. Strong ordering, weak quantitative prediction.

The obvious confound in (c) is (b): ESS cannot be evaluated as a mechanism while
beta is set by a rule that does not control it. This script removes that
confound by controlling ESS directly.

WHAT THIS SCRIPT DOES
---------------------
For every cell — objective, dimension, initialization — beta is found by
bisection so that the effective sample size of a probe ensemble drawn from the
initial law equals a target FRACTION of the ensemble. ESS is monotone decreasing
in beta, from the full ensemble at beta = 0 down to 1, so the bisection is clean
and the target is always reachable.

Then the question is simple and decisive:

  With weight concentration held fixed, do the differences between objectives
  and between dimensions survive?

  IF THEY COLLAPSE — concentration is the mechanism, everything measured in
  Phases 1 and 2 was concentration in disguise, and guarantee visibility has a
  one-parameter description. That is the strong outcome and it makes the
  landscape-descriptor programme unnecessary.

  IF THEY PERSIST — geometry matters beyond concentration, ESS is a correlate
  rather than a cause, and measurable landscape descriptors become necessary
  rather than optional. That is the weaker outcome for this paper and the more
  interesting one for the field.

Either way the answer is worth the compute, which is the property a confirmatory
experiment should have and which no run in this project has had until now.

A SECOND MEASUREMENT, FOR FREE
------------------------------
The beta found by bisection is itself a result: it is the inverse temperature
required to maintain constant weight concentration as the dimension grows. That
curve has a counterpart in the theory — FKR's informal alpha_0 grows with d —
and it has never been measured.

THE PRE-REGISTERED RULES — fixed before this script was first run
-----------------------------------------------------------------
Written down in advance because an analysis rule in this project was already
changed once after results were seen.

  Proven slope for the squared coupled error is -1. The bound is ONE-SIDED, so
  decay faster than -1 is consistent with it. Tolerance 0.15. RECOVERED iff the
  upper end of the 95 percent bootstrap interval is at most -0.85.

  COLLAPSE at a given (dimension, target) iff the standard deviation of the
  slope across objectives is at most 0.10.

  CONCENTRATION IS THE MECHANISM iff, in the variance decomposition, adding
  objective identity to a model already containing target and dimension raises
  R^2 by less than 0.05.

WHAT THIS SCRIPT STILL DOES NOT DO
----------------------------------
It controls the INITIAL effective sample size, not its trajectory. The minimum
over the run is recorded so the reader can see how far the control propagates,
and if it does not propagate the collapse test is weakened accordingly — this is
stated rather than discovered later.

It does not vary the time horizon or sigma, and it uses named benchmarks rather
than controlled synthetic landscapes with independently manipulated conditioning
and modality. Both remain open.

HOW TO RUN
----------
    python mechanism.py --workers 3 --quick          (smoke test, ~3 min)
    python mechanism.py --workers 3                  (full, budget 3-4 hours)
    python mechanism.py --workers 3 --realisations 10    (faster, wider CIs)

NumPy only. No SciPy. Python 3.8 compatible.
Writes mechanism_raw.csv and mechanism_summary.csv.
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

GAMMA_THEORY, DELTA = -1.0, 0.15
THRESH = GAMMA_THEORY + DELTA
COLLAPSE_SD = 0.10
MECHANISM_DR2 = 0.05
N_BOOT = 400


def f_ackley(X):
    d = X.shape[1]
    s1 = np.sqrt(np.sum(X * X, axis=1) / d)
    s2 = np.sum(np.cos(2.0 * np.pi * X), axis=1) / d
    return -20.0 * np.exp(-0.2 * s1) - np.exp(s2) + 20.0 + math.e


def f_rastrigin(X):
    return np.sum(X * X + 10.0 * (1.0 - np.cos(2.0 * np.pi * X)), axis=1)


def f_sphere(X):
    return np.sum(X * X, axis=1)


def f_griewank(X):
    d = X.shape[1]
    i = np.arange(1, d + 1, dtype=float)
    return (np.sum(X * X, axis=1) / 4000.0
            - np.prod(np.cos(X / np.sqrt(i)), axis=1) + 1.0)


def f_levy(X):
    w = 1.0 + (X - 1.0) / 4.0
    t1 = np.sin(np.pi * w[:, 0]) ** 2
    wm = w[:, :-1]
    t2 = np.sum((wm - 1.0) ** 2 * (1.0 + 10.0 * np.sin(np.pi * wm + 1.0) ** 2), axis=1)
    wl = w[:, -1]
    return t1 + t2 + (wl - 1.0) ** 2 * (1.0 + np.sin(2.0 * np.pi * wl) ** 2)


def f_rosenbrock(X):
    xi, xn = X[:, :-1], X[:, 1:]
    return np.sum(100.0 * (xn - xi ** 2) ** 2 + (1.0 - xi) ** 2, axis=1)


OBJECTIVES = {"ackley": f_ackley, "rastrigin": f_rastrigin, "sphere": f_sphere,
              "griewank": f_griewank, "levy": f_levy, "rosenbrock": f_rosenbrock}
CLASS = {"ackley": "A(0,0,0)", "rastrigin": "A(1,2,2)", "sphere": "A(1,2,2)",
         "griewank": "A(1,2,2)", "levy": "A(2,2,2)", "rosenbrock": "A(3,1,4)"}
MINIMIZER = {"ackley": 0.0, "rastrigin": 0.0, "sphere": 0.0,
             "griewank": 0.0, "levy": 1.0, "rosenbrock": 1.0}
OFFSET_SCALE = 3.0


def draw_initial(rng, n, d, objective, init):
    xs = MINIMIZER[objective]
    if init == "centred":
        return rng.standard_normal((n, d)) + xs
    X = rng.standard_normal((n, d)) + xs + OFFSET_SCALE
    near = rng.random(n) < 0.1
    X[near] = rng.standard_normal((int(near.sum()), d)) + xs
    return X


def _logsumexp(a):
    m = a.max()
    return m + math.log(float(np.exp(a - m).sum()))


def log_ess_of(fvals, beta):
    """Exact log effective sample size, valid after every weight has underflowed."""
    logw = -beta * (fvals - fvals.min())
    return 2.0 * _logsumexp(logw) - _logsumexp(2.0 * logw)


def weighted_mean_and_logess(X, fvals, beta):
    logw = -beta * (fvals - fvals.min())
    w = np.exp(logw)
    m = (w[:, None] * X).sum(axis=0) / w.sum()
    return m, 2.0 * _logsumexp(logw) - _logsumexp(2.0 * logw)


def beta_for_target(objective, d, init, tau, n_probe=4000, seed=999):
    """Bisect beta so the probe ensemble's ESS fraction equals tau. ESS is
    monotone decreasing in beta — the full ensemble at beta = 0, one as beta
    grows — so the target is always bracketed."""
    rng = np.random.default_rng(seed + 131 * d + 7919 * len(objective))
    X = draw_initial(rng, n_probe, d, objective, init)
    f = OBJECTIVES[objective](X)
    goal = math.log(tau * n_probe)
    lo, hi = 1e-10, 1e10
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if log_ess_of(f, mid) > goal:
            lo = mid
        else:
            hi = mid
    beta = math.sqrt(lo * hi)
    return beta, math.exp(min(log_ess_of(f, beta), 700)) / n_probe


def one_realisation(objective, beta, d, init, sigma, dt, K, Jinf, J_list, seed):
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = draw_initial(rng, Jinf, d, objective, init)
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    le0, le_min = None, float("inf")
    sq = math.sqrt(dt)
    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        m, le = weighted_mean_and_logess(Xref, f(Xref), beta)
        if le0 is None:
            le0 = le
        le_min = min(le_min, le)
        dref = Xref - m
        Xref = Xref - dt * dref + sigma * np.linalg.norm(dref, axis=1)[:, None] * dW
        for J in J_list:
            Xj = Xsub[J]
            mj, _ = weighted_mean_and_logess(Xj, f(Xj), beta)
            dj = Xj - mj
            Xsub[J] = Xj - dt * dj + sigma * np.linalg.norm(dj, axis=1)[:, None] * dW[:J]
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1), out=runmax[J])
    return {J: float(np.mean(runmax[J])) for J in J_list}, le0, le_min


def task(a):
    obj, tau, beta, d, init, sigma, dt, K, Jinf, J_list, seed = a
    per_J, le0, lem = one_realisation(obj, beta, d, init, sigma, dt, K, Jinf, J_list, seed)
    return obj, tau, beta, d, init, per_J, le0, lem


def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def boot_ci(per_real, J_sel, seed=7):
    R = len(per_real[J_sel[0]])
    M = np.array([[per_real[J][r] for J in J_sel] for r in range(R)])
    Jv = np.array(J_sel, float)
    rng = np.random.default_rng(seed)
    out = [fit_slope(Jv, M[rng.integers(0, R, R)].mean(axis=0)) for _ in range(N_BOOT)]
    out = np.array([o for o in out if np.isfinite(o)])
    if out.size < 20:
        return float("nan"), float("nan")
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def r2_of(design, y):
    sol, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
    pred = design @ sol
    return 1.0 - float(((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=0)
    p.add_argument("--sigma", type=float, default=0.2)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260821)
    args = p.parse_args()

    lam, K = 1.0, int(round(args.T / args.dt))

    if args.quick:
        Jinf, J_list = 4000, [10, 40, 160, 400]
        dims, objs, inits, taus, M = [2, 10], ["ackley", "rosenbrock"], ["centred"], [0.5, 0.01], 3
    else:
        Jinf, J_list = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        dims = [2, 5, 10, 40]
        objs = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
        inits, taus, M = ["centred", "mix-0.1"], [0.5, 0.1, 0.01], 15
    if args.realisations:
        M = args.realisations
    J_list = [J for J in J_list if J <= Jinf // 10]

    print("=" * 80)
    print("CBO-GAP Phase 3 — is weight concentration the mechanism?")
    print("=" * 80)
    print("  PRE-REGISTERED (fixed before first run):")
    print("    RECOVERED iff bootstrap 95% upper bound <= {:+.2f}".format(THRESH))
    print("    COLLAPSE at a (d, tau) iff sd of slope across objectives <= {:.2f}".format(COLLAPSE_SD))
    print("    MECHANISM iff adding objective identity raises R^2 by < {:.2f}".format(MECHANISM_DR2))
    print("  Jinf {}   J grid {}   realisations {}".format(Jinf, len(J_list), M))
    print("  sigma {}  dt {}  T {}  steps {}".format(args.sigma, args.dt, args.T, K))
    dims = [d for d in dims if 2.0 * lam > d * args.sigma ** 2]
    print("  d in {} (2*lambda > d*sigma^2 holds throughout)".format(dims))

    print("\n" + "-" * 80)
    print("P3.0 — beta found by bisection, and the control it achieves")
    print("-" * 80)
    print("  Phase 2 matched beta*spread and got ESS from 181 to 26340 at d=2.")
    print("  Here ESS is the control, and beta is whatever delivers it.\n")
    print("  {:<12} {:<9} {:>5} {:>7} {:>14} {:>12}".format(
        "objective", "init", "d", "tau", "beta", "ESS frac"))
    betas = {}
    for o in objs:
        for init in inits:
            for d in dims:
                for tau in taus:
                    b, ach = beta_for_target(o, d, init, tau)
                    betas[(o, d, init, tau)] = b
                    print("  {:<12} {:<9} {:>5} {:>7.3g} {:>14.6g} {:>12.4f}".format(
                        o, init, d, tau, b, ach))

    print("\n  P3.1 — beta required to hold concentration as d grows (centred):")
    print("  This curve has a theoretical counterpart: FKR's informal alpha_0")
    print("  grows with d. It has not previously been measured.\n")
    print("  {:<12} {:>7}".format("objective", "tau") +
          "".join("{:>14}".format("d=" + str(d)) for d in dims))
    for o in objs:
        for tau in taus:
            print("  {:<12} {:>7.3g}".format(o, tau) +
                  "".join("{:>14.5g}".format(betas[(o, d, "centred", tau)]) for d in dims))

    tasks, s = [], args.seed
    for o in objs:
        for d in dims:
            for init in inits:
                for tau in taus:
                    for _ in range(M):
                        s += 1
                        tasks.append((o, tau, betas[(o, d, init, tau)], d, init,
                                      args.sigma, args.dt, K, Jinf, J_list, s))

    print("\n  {} realisations queued on {} workers\n".format(len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    agg = {}
    for o, tau, beta, d, init, per_J, le0, lem in res:
        k = (o, d, init, tau)
        if k not in agg:
            agg[k] = {"beta": beta, "E": {J: [] for J in J_list}, "le0": [], "lem": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        agg[k]["le0"].append(le0)
        agg[k]["lem"].append(lem)

    rec, rows = {}, []
    for (o, d, init, tau), r in sorted(agg.items()):
        sl = fit_slope(np.array(J_list, float),
                       np.array([np.mean(r["E"][J]) for J in J_list]))
        lo, hi = boot_ci(r["E"], J_list)
        le0, lem = float(np.mean(r["le0"])), float(np.mean(r["lem"]))
        v = "recovered" if hi <= THRESH else ("NOT observed" if lo > THRESH else "UNDECIDED")
        rec[(o, d, init, tau)] = (sl, lo, hi, le0, lem, v)
        rows.append([o, d, init, tau, "{:.6g}".format(r["beta"]), "{:.6f}".format(sl),
                     "{:.6f}".format(lo), "{:.6f}".format(hi),
                     "{:.6g}".format(le0), "{:.6g}".format(lem), v])

    with open("mechanism_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "init", "tau", "beta", "J", "Ehat", "stderr",
                    "log_ESS_initial", "log_ESS_min", "realisations"])
        for (o, d, init, tau), r in sorted(agg.items()):
            for J in J_list:
                v = np.array(r["E"][J])
                w.writerow([o, d, init, tau, "{:.6g}".format(r["beta"]), J,
                            "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.6g}".format(np.mean(r["le0"])),
                            "{:.6g}".format(np.mean(r["lem"])), len(v)])
    with open("mechanism_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "init", "tau", "beta", "slope", "ci_lo",
                    "ci_hi", "log_ESS_initial", "log_ESS_min", "verdict"])
        w.writerows(rows)

    print("\n" + "-" * 80)
    print("P3.2 — does the control propagate? initial vs minimum ESS during the run")
    print("-" * 80)
    print("  Only the INITIAL concentration is controlled. If the minimum drifts")
    print("  far apart across objectives, the collapse test below is weakened and")
    print("  that must be said rather than discovered by a referee.\n")
    print("  {:<12} {:>5} {:>7} {:>14} {:>14}".format(
        "objective", "d", "tau", "ESS frac init", "ESS frac min"))
    for o in objs:
        for d in dims:
            for tau in taus:
                _, _, _, le0, lem, _ = rec[(o, d, "centred", tau)]
                print("  {:<12} {:>5} {:>7.3g} {:>14.4g} {:>14.4g}".format(
                    o, d, tau, math.exp(min(le0, 700)) / Jinf,
                    math.exp(min(lem, 700)) / Jinf))

    print("\n" + "-" * 80)
    print("P3.3 — THE COLLAPSE TEST")
    print("-" * 80)
    print("  With concentration held fixed, do the objectives agree?\n")
    print("  {:<9} {:>5} {:>7}".format("init", "d", "tau") +
          "".join("{:>11}".format(o[:9]) for o in objs) + "{:>9}{:>14}".format("sd", "verdict"))
    for init in inits:
        for d in dims:
            for tau in taus:
                ss = [rec[(o, d, init, tau)][0] for o in objs]
                sd = float(np.std(ss, ddof=1))
                print("  {:<9} {:>5} {:>7.3g}".format(init, d, tau) +
                      "".join("{:>11.3f}".format(x) for x in ss) +
                      "{:>9.3f}{:>14}".format(sd, "COLLAPSE" if sd <= COLLAPSE_SD else "persists"))

    print("\n" + "-" * 80)
    print("P3.4 — variance decomposition")
    print("-" * 80)
    keys = sorted(rec)
    y = np.array([rec[k][0] for k in keys])
    ltau = np.log(np.array([k[3] for k in keys], float))
    ld = np.log(np.array([k[1] for k in keys], float))
    one = np.ones(len(y))
    obj_ix = {o: i for i, o in enumerate(objs)}
    Dobj = np.zeros((len(y), len(objs) - 1))
    for i, k in enumerate(keys):
        j = obj_ix[k[0]]
        if j > 0:
            Dobj[i, j - 1] = 1.0
    r_t = r2_of(np.vstack([ltau, one]).T, y)
    r_td = r2_of(np.vstack([ltau, ld, one]).T, y)
    r_tdo = r2_of(np.column_stack([ltau, ld, one, Dobj]), y)
    print("  target alone                : R^2 = {:.4f}".format(r_t))
    print("  target + dimension          : R^2 = {:.4f}".format(r_td))
    print("  target + dimension + object : R^2 = {:.4f}".format(r_tdo))
    print("  gain from objective identity: {:.4f}".format(r_tdo - r_td))
    print("\n  VERDICT: {}".format(
        "CONCENTRATION IS THE MECHANISM — objective identity adds little"
        if (r_tdo - r_td) < MECHANISM_DR2 else
        "GEOMETRY PERSISTS — concentration alone does not explain the surface"))

    print("\n" + "-" * 80)
    print("P3.5 — full table")
    print("-" * 80)
    print("  {:<12} {:>5} {:<9} {:>7} {:>9} {:>19} {:>14}".format(
        "objective", "d", "init", "tau", "slope", "95% CI", "verdict"))
    for k in keys:
        sl, lo, hi, le0, lem, v = rec[k]
        print("  {:<12} {:>5} {:<9} {:>7.3g} {:>9.4f} {:>19} {:>14}".format(
            k[0], k[1], k[2], k[3], sl, "[{:+.3f},{:+.3f}]".format(lo, hi), v))

    print("\n" + "=" * 80)
    print("wrote mechanism_raw.csv and mechanism_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 80)


if __name__ == "__main__":
    main()
