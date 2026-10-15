"""
visibility.py  —  CBO-GAP Phase 2: the guarantee-visibility boundary

WHY THIS SCRIPT EXISTS
----------------------
Phase 1c produced a fitted exponent and, on inspection of its own diagnostics,
three problems that invalidate parts of it. This script fixes all three and
replaces the central measured object with one that has an obvious reason to
exist.

  PROBLEM 1 — the scale used to match objectives was wrong.
      Phase 1b and 1c matched objectives by the product of beta and the STANDARD
      DEVIATION of the objective over the initial law. For Rosenbrock, which is
      quartic, that standard deviation is dominated by the tail and not by the
      bulk the particles occupy: 6519 at d = 10, against 0.23 for Griewank. Five
      orders of magnitude. Matching on it drove Rosenbrock's beta down to 0.0046,
      where the weights are nearly uniform and the method is barely running. Its
      apparent recovery of the rate at every dimension was an artefact of that
      choice, and the objective column of the Phase 1c panel is not interpretable.
      FIX: match on a robust spread, the 5th-to-95th percentile range, which
      measures the bulk. Both scales are computed and printed side by side so the
      size of the earlier error is visible rather than quietly corrected.

  PROBLEM 2 — the initial law was centred exactly on the minimizer.
      This is the most attackable choice in the project. With the cloud already
      centred on the answer, what is measured is local consensus behaviour, not
      global optimization, and a referee is entitled to say so.
      FIX: four initializations, from the favourable case to one where only a
      small fraction of the initial mass is anywhere near the global basin.

  PROBLEM 3 — the measured object was a fitted exponent nobody needs.
      A slope of -0.57 invites the question "why should I care", and the honest
      answer was thin.
      FIX: measure instead the smallest ensemble size at which the PROVEN rate
      becomes observable. That is a quantity with an immediate operational
      meaning: below it the theorem tells a practitioner nothing they can see.

THE PRE-REGISTERED RULE — fixed here, before this script was ever run
---------------------------------------------------------------------
An earlier analysis rule in this project was changed after results were seen
(a two-sided slope test that should always have been one-sided). To prevent a
repeat, the rule below is fixed in advance and is not to be adjusted after
looking at the output.

  The proven rate for the squared coupled error is J^(-1), i.e. slope -1.
  The bound is ONE-SIDED, so decay faster than -1 is consistent with it.
  Tolerance delta = 0.15.
  A fit is RECOVERED iff the upper end of its 95 percent bootstrap interval
  is at most -0.85.
  N_vis is the smallest J0 on the grid such that fitting the slope on
  J >= J0 is RECOVERED. If no J0 qualifies, N_vis is reported as not in range
  and must not be extrapolated.

WHY THE SATURATION IS NOT A FLOATING-POINT ARTEFACT
---------------------------------------------------
An objection worth answering properly: at large beta the Boltzmann weights
underflow, so is the observed hardmin regime just numerics?

No, and this is provable rather than checkable. The weights are already computed
in shifted form, exp(-beta*(f - min f)), so the largest is exactly 1 and nothing
overflows. When the second-largest weight underflows, its ratio to the largest is
below exp(-745), which is roughly 1e-324. The true weighted mean differs from the
arg min by that same relative amount. Machine epsilon in double precision is
about 2e-16. So the computed weighted mean equals the true weighted mean to full
machine precision: the arg min IS the weighted mean, to sixteen digits. Higher
precision moves the beta at which this happens; it does not make the regime go
away, because the regime is a fact about the weights and not about the format.

Separately, this script computes the effective sample size EXACTLY in log space,
via log ESS = 2*logsumexp(logw) - logsumexp(2*logw), which is well defined even
when every individual weight has underflowed. Phase 1c computed ESS from the
weights directly and could not distinguish an ESS of exactly 1 from 1 + 1e-300.
Here both are reported.

WHAT THIS SCRIPT STILL DOES NOT DO
----------------------------------
It does not vary the time horizon, and the constants under discussion grow
exponentially in the horizon. It does not vary sigma toward the 2*lambda > d*sigma^2
boundary. It does not use controlled synthetic landscapes with independently
manipulated conditioning and modality, which is the right way to stop named
benchmarks from being the scientific unit. All three are the next phase, not
this one.

HOW TO RUN
----------
    python visibility.py --workers 3 --quick        (smoke test, ~3 min)
    python visibility.py --workers 3                (full, budget 4-5 hours)
    python visibility.py --workers 3 --realisations 12   (faster, wider CIs)

NumPy only. No SciPy. Python 3.8 compatible.
Writes visibility_raw.csv and visibility_summary.csv.
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

GAMMA_THEORY = -1.0
DELTA = 0.15
THRESH = GAMMA_THEORY + DELTA          # -0.85
N_BOOT = 400


# ----------------------------------------------------------------------
# objectives
# ----------------------------------------------------------------------

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

# Initializations, from the favourable case outward. OFFSET_SCALE is how far
# the misplaced component sits from the minimizer, in units of the initial
# standard deviation.
OFFSET_SCALE = 3.0
INITS = ["centred", "offset", "mix-0.1", "mix-0.01"]


def draw_initial(rng, n, d, objective, init):
    """Initial positions under one of four laws. 'centred' is the favourable
    case used throughout Phase 1 and is retained only for continuity."""
    xs = MINIMIZER[objective]
    if init == "centred":
        return rng.standard_normal((n, d)) + xs
    if init == "offset":
        return rng.standard_normal((n, d)) + xs + OFFSET_SCALE
    eps = 0.1 if init == "mix-0.1" else 0.01
    X = rng.standard_normal((n, d)) + xs + OFFSET_SCALE
    near = rng.random(n) < eps
    X[near] = rng.standard_normal((int(near.sum()), d)) + xs
    return X


# ----------------------------------------------------------------------
# scales, and the exact effective sample size
# ----------------------------------------------------------------------

def scales_of(objective, d, init, n=40000, seed=12345):
    """Both scales, so the size of the Phase 1c error stays visible.
    std      — standard deviation, what Phase 1b/1c matched on. Tail-driven.
    robust   — 5th-to-95th percentile range. Measures the bulk the particles
               actually occupy, which is what the Boltzmann weights see."""
    rng = np.random.default_rng(seed + 1000 * d + 7 * INITS.index(init))
    X = draw_initial(rng, n, d, objective, init)
    f = OBJECTIVES[objective](X)
    q = np.percentile(f, [5, 95])
    return float(np.std(f)), float(q[1] - q[0])


def _logsumexp(a):
    m = a.max()
    return m + math.log(float(np.exp(a - m).sum()))


def weighted_mean_and_logess(X, fvals, beta):
    """Weighted mean in shifted form, and the effective sample size computed
    EXACTLY in log space so it remains meaningful after every weight has
    underflowed. Phase 1c could not distinguish ESS = 1 from 1 + 1e-300."""
    logw = -beta * (fvals - fvals.min())
    w = np.exp(logw)
    m = (w[:, None] * X).sum(axis=0) / w.sum()
    log_ess = 2.0 * _logsumexp(logw) - _logsumexp(2.0 * logw)
    return m, log_ess


# ----------------------------------------------------------------------
# one coupled realisation
# ----------------------------------------------------------------------

def one_realisation(objective, beta, d, init, sigma, dt, K, Jinf, J_list, seed):
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = draw_initial(rng, Jinf, d, objective, init)
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    log_ess_min = float("inf")
    sq = math.sqrt(dt)

    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        m, le = weighted_mean_and_logess(Xref, f(Xref), beta)
        log_ess_min = min(log_ess_min, le)
        dref = Xref - m
        Xref = Xref - dt * dref + sigma * np.linalg.norm(dref, axis=1)[:, None] * dW
        for J in J_list:
            Xj = Xsub[J]
            mj, _ = weighted_mean_and_logess(Xj, f(Xj), beta)
            dj = Xj - mj
            Xsub[J] = Xj - dt * dj + sigma * np.linalg.norm(dj, axis=1)[:, None] * dW[:J]
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1), out=runmax[J])

    return {J: float(np.mean(runmax[J])) for J in J_list}, log_ess_min


def task(a):
    obj, B, beta, d, init, sigma, dt, K, Jinf, J_list, seed = a
    per_J, le = one_realisation(obj, beta, d, init, sigma, dt, K, Jinf, J_list, seed)
    return obj, B, beta, d, init, per_J, le


# ----------------------------------------------------------------------
# fitting, the pre-registered verdict, and N_vis
# ----------------------------------------------------------------------

def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def boot_ci(per_real, J_sel, seed=7, n_boot=N_BOOT):
    R = len(per_real[J_sel[0]])
    M = np.array([[per_real[J][r] for J in J_sel] for r in range(R)])
    Jv = np.array(J_sel, float)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_boot):
        out.append(fit_slope(Jv, M[rng.integers(0, R, R)].mean(axis=0)))
    out = np.array([o for o in out if np.isfinite(o)])
    if out.size < 20:
        return float("nan"), float("nan")
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def n_vis(per_real, J_list, seed=7):
    """Pre-registered: smallest J0 such that the fit on J >= J0 has its 95
    percent upper bound at or below -0.85. Never extrapolated past the grid."""
    for i, J0 in enumerate(J_list):
        sel = J_list[i:]
        if len(sel) < 4:
            break
        _, hi = boot_ci(per_real, sel, seed=seed)
        if np.isfinite(hi) and hi <= THRESH:
            return J0
    return None


def spearman(a, b):
    def rank(v):
        o = np.argsort(v)
        r = np.empty(len(v), float)
        r[o] = np.arange(len(v), dtype=float)
        return r
    ra, rb = rank(np.asarray(a, float)), rank(np.asarray(b, float))
    ra -= ra.mean()
    rb -= rb.mean()
    den = math.sqrt(float((ra ** 2).sum()) * float((rb ** 2).sum()))
    return float((ra * rb).sum() / den) if den > 0 else float("nan")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=0)
    p.add_argument("--sigma", type=float, default=0.2)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260820)
    args = p.parse_args()

    lam, K = 1.0, int(round(args.T / args.dt))
    B = 30.0

    if args.quick:
        Jinf = 4000
        J_list = [10, 20, 40, 80, 160, 320, 400]
        dims, objs, inits, M = [2, 5], ["ackley", "rosenbrock"], ["centred", "mix-0.1"], 3
    else:
        Jinf = 50000
        J_list = [10, 14, 20, 28, 40, 57, 80, 113, 160, 226, 320, 452, 640,
                  905, 1280, 1810, 2560, 3620, 5000]
        dims = [2, 3, 5, 10, 20, 40]
        objs = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
        inits, M = INITS, 20
    if args.realisations:
        M = args.realisations
    J_list = [J for J in J_list if J <= Jinf // 10]

    print("=" * 80)
    print("CBO-GAP Phase 2 — guarantee-visibility boundary")
    print("=" * 80)
    print("  PRE-REGISTERED RULE (fixed before this script was first run):")
    print("    proven slope {:+.1f}; one-sided; tolerance {:.2f}".format(GAMMA_THEORY, DELTA))
    print("    RECOVERED iff bootstrap 95% upper bound <= {:+.2f}".format(THRESH))
    print("    N_vis = smallest J0 with the fit on J >= J0 recovered; never extrapolated")
    print("  Jinf {}   J grid {} values   realisations {}   B {:g}".format(
        Jinf, len(J_list), M, B))
    print("  sigma {}  dt {}  T {}  steps {}".format(args.sigma, args.dt, args.T, K))

    print("\n  FKR condition 2*lambda > d*sigma^2:")
    dims = [d for d in dims if 2.0 * lam > d * args.sigma ** 2]
    print("    satisfied for d in {} (grid stops before failure at d=50)".format(dims))

    print("\n  SCALE COMPARISON — why Phase 1c's objective column was not interpretable")
    print("  std is what Phase 1b/1c matched on; robust is the 5-95 percentile range.")
    print("  {:<12} {:>4} {:>12} {:>12} {:>9} {:>14} {:>14}".format(
        "objective", "d", "std", "robust", "ratio", "beta(std)", "beta(robust)"))
    scale = {}
    for o in objs:
        for d in dims:
            s, r = scales_of(o, d, "centred")
            scale[(o, d, "centred")] = r
            print("  {:<12} {:>4} {:>12.4g} {:>12.4g} {:>9.1f} {:>14.5g} {:>14.5g}".format(
                o, d, s, r, s / r if r > 0 else float("nan"), B / s, B / r))
    for o in objs:
        for d in dims:
            for init in inits:
                if (o, d, init) not in scale:
                    scale[(o, d, init)] = scales_of(o, d, init)[1]

    tasks, s = [], args.seed
    for o in objs:
        for d in dims:
            for init in inits:
                beta = B / scale[(o, d, init)]
                for _ in range(M):
                    s += 1
                    tasks.append((o, B, beta, d, init, args.sigma, args.dt, K,
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
    for o, Bv, beta, d, init, per_J, le in res:
        k = (o, d, init)
        if k not in agg:
            agg[k] = {"beta": beta, "E": {J: [] for J in J_list}, "le": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        agg[k]["le"].append(le)

    with open("visibility_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "init", "beta", "robust_spread", "J",
                    "Ehat", "stderr", "log_ESS", "ESS", "realisations"])
        for (o, d, init), r in sorted(agg.items()):
            le = float(np.mean(r["le"]))
            for J in J_list:
                v = np.array(r["E"][J])
                w.writerow([o, d, init, "{:.6g}".format(r["beta"]),
                            "{:.6g}".format(scale[(o, d, init)]), J,
                            "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.6g}".format(le), "{:.6g}".format(math.exp(min(le, 700))),
                            len(v)])

    rec, summary = {}, []
    for (o, d, init), r in sorted(agg.items()):
        sl = fit_slope(np.array(J_list, float),
                       np.array([np.mean(r["E"][J]) for J in J_list]))
        lo, hi = boot_ci(r["E"], J_list)
        nv = n_vis(r["E"], J_list)
        le = float(np.mean(r["le"]))
        verdict = ("recovered" if hi <= THRESH else
                   ("NOT observed" if lo > THRESH else "UNDECIDED"))
        rec[(o, d, init)] = (sl, lo, hi, le, nv, verdict)
        summary.append([o, d, init, "{:.6g}".format(r["beta"]), "{:.6f}".format(sl),
                        "{:.6f}".format(lo), "{:.6f}".format(hi),
                        "{:.6g}".format(le), nv if nv else "not in range", verdict])

    with open("visibility_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "init", "beta", "slope", "ci_lo", "ci_hi",
                    "log_ESS", "N_vis", "verdict"])
        w.writerows(summary)

    print("\n" + "-" * 80)
    print("P2.1 — N_vis: smallest ensemble at which the PROVEN rate is observable")
    print("-" * 80)
    print("  '>grid' means no J0 on the grid qualifies. That is a floor, not an")
    print("  estimate, and must not be extrapolated.\n")
    print("  {:<12} {:<10}".format("objective", "init") +
          "".join("{:>9}".format("d=" + str(d)) for d in dims))
    for o in objs:
        for init in inits:
            line = "  {:<12} {:<10}".format(o, init)
            for d in dims:
                nv = rec[(o, d, init)][4]
                line += "{:>9}".format(str(nv) if nv else ">grid")
            print(line)

    print("\n" + "-" * 80)
    print("P2.2 — does the favourable initialization drive the result?")
    print("-" * 80)
    print("  Centred places the cloud on the answer. If N_vis worsens sharply as")
    print("  mass moves away, Phase 1 measured local consensus, not optimization.\n")
    print("  {:<12} {:>4}".format("objective", "d") +
          "".join("{:>12}".format(i) for i in inits))
    for o in objs:
        for d in dims:
            line = "  {:<12} {:>4}".format(o, d)
            for init in inits:
                sl = rec[(o, d, init)][0]
                line += "{:>12}".format("{:+.3f}".format(sl))
            print(line)

    print("\n" + "-" * 80)
    print("P2.3 — ESS within a fixed dimension (Phase 1c's null, re-examined)")
    print("-" * 80)
    print("  Pooled across regimes ESS had no predictive power. Within one")
    print("  dimension it appeared to order the objectives exactly. Spearman")
    print("  correlation of log ESS against slope, per dimension, centred init.")
    print("  Caveat that no correlation can remove: ESS and the slope are both")
    print("  downstream of the same weight concentration.\n")
    for init in inits:
        for d in dims:
            xs = [rec[(o, d, init)][3] for o in objs]
            ys = [rec[(o, d, init)][0] for o in objs]
            if len(objs) >= 3:
                print("    init {:<10} d={:<4} spearman(logESS, slope) = {:+.4f}".format(
                    init, d, spearman(xs, ys)))

    print("\n" + "-" * 80)
    print("P2.4 — slopes with intervals")
    print("-" * 80)
    print("  {:<12} {:>4} {:<10} {:>9} {:>19} {:>11} {:>14}".format(
        "objective", "d", "init", "slope", "95% CI", "log ESS", "verdict"))
    for o in objs:
        for d in dims:
            for init in inits:
                sl, lo, hi, le, nv, v = rec[(o, d, init)]
                print("  {:<12} {:>4} {:<10} {:>9.4f} {:>19} {:>11.4g} {:>14}".format(
                    o, d, init, sl, "[{:+.3f},{:+.3f}]".format(lo, hi), le, v))

    print("\n" + "=" * 80)
    print("wrote visibility_raw.csv and visibility_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 80)


if __name__ == "__main__":
    main()
