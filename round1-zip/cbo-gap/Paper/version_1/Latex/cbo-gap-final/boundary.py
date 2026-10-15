"""
boundary.py  —  CBO-GAP Phase 5: where exactly is the visibility boundary?

WHY THIS SCRIPT EXISTS
----------------------
Phase 4 ran 1080 realisations across two arms and produced one result that
survives everything this project has thrown at it.

At a concentration target of one tenth of the ensemble, across six objectives,
three dimensions and both arms — 36 cells — the mean slope was -0.9999 with a
standard deviation of 0.065, and 35 of 36 cells recovered the proven rate. At one
hundredth, the mean was -0.823 and half the cells failed.

Dimension did not matter. Objective did not matter. Growth class did not matter.
In the arm where concentration was genuinely held for the whole run, the
concentration target alone explains R^2 = 0.63 of the slope and adding dimension
raises it only to 0.66.

Four phases of this project chased beta, dimension, the objective's assumption
class, effective sample size as a diagnostic, a dimension-dependent exponent and
a crossover ensemble size. All of those are dead. What separates the regime where
the guarantee is visible from the regime where it is not appears to be a single
dimensionless quantity, and it is bracketed between 0.1 and 0.01 and resolved
nowhere.

This script resolves it.

WHAT IS MEASURED, AND IN WHICH CURRENCY
---------------------------------------
The boundary is only useful if it is stated in a quantity a practitioner can
measure during a run. Three candidates are recorded for every cell:

  initial       — the effective sample size fraction at t = 0. This is what the
                  bisection controls, but concentration decays afterwards, so
                  the initial value overstates what the run actually experienced.
  time-averaged — the mean over the trajectory. Closest to "what the run was
                  actually like".
  minimum       — the worst point of the trajectory. The most conservative.

Phase 4's fixed arm had drift up to 3.4 in log units, which is a factor of 30, so
these three will NOT agree and the choice between them matters.

PRE-REGISTERED, and stated before the first run
------------------------------------------------
  RECOVERED, per cell, iff the bootstrap 95 percent upper bound is at most -0.85.

  PER CELL ONLY. No verdict in this script is computed from a mean across cells.
  In Phase 4 the criterion averaged a target that recovers with one that does not
  and returned a pass that neither target earned. That error is not repeated:
  aggregates are printed for description and are barred from every verdict.

  The boundary for a cell is reported as a BRACKET — the largest target that
  fails and the smallest that recovers — never as an interpolated point, unless
  the slope is monotone in the target for that cell. Monotonicity is tested and
  reported per cell, and non-monotone cells are excluded from any interpolation
  rather than quietly averaged in.

  THE CRITERION IS UNIVERSAL iff there exists a single target value recovered in
  every cell and a single target value failing in every cell. If the brackets do
  not overlap, there is no universal criterion and the boundary depends on
  something else, which must then be said plainly.

  The three currencies above are all reported with their spreads. The criterion
  will be stated in whichever gives the smallest spread of the boundary across
  cells. Naming the three in advance and the selection rule in advance is what
  keeps that from being a choice made after seeing which looks best.

WHY ONLY THE FIXED ARM
----------------------
A time-varying inverse temperature is not the algorithm FKR and GHV analyse. The
adaptive arm in Phase 4 was diagnostic and it did its job: it showed that holding
concentration removes the between-objective spread without moving the level. Every
claim about the theory rests on fixed beta, so that is what runs here.

WHAT THIS STILL CANNOT SETTLE
-----------------------------
Why the level is what it is. At the tight target the objectives agree on a slope
that is not -1, in both arms. Concentration explains the variation between
objectives, not the level, and nothing in this script addresses the level.

The horizon is still fixed at 1, sigma is still fixed, the benchmarks are still
named functions rather than controlled synthetic landscapes, and the reference
ensemble is still a proxy at one twentieth of GHV's.

HOW TO RUN
----------
    python boundary.py --workers 3 --quick     (smoke test, ~3 min)
    python boundary.py --workers 3             (full, budget 2-3 hours)

NumPy only. No SciPy. Python 3.8 compatible.
Writes boundary_raw.csv and boundary_summary.csv.
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

THRESH = -0.85
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


def _lse(a):
    m = a.max()
    return m + math.log(float(np.exp(a - m).sum()))


def log_ess(fc, beta):
    lw = -beta * fc
    return 2.0 * _lse(lw) - _lse(2.0 * lw)


def solve_beta(fc, goal_log, iters=90):
    """ESS is monotone decreasing in beta, from the full ensemble at 0 down to
    one, so the target is always bracketed."""
    lo, hi = 1e-12, 1e12
    for _ in range(iters):
        mid = math.sqrt(lo * hi)
        if log_ess(fc, mid) > goal_log:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def one_realisation(objective, d, tau, beta, sigma, dt, K, Jinf, J_list, seed):
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = rng.standard_normal((Jinf, d)) + MINIMIZER[objective]
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    les = []
    sq = math.sqrt(dt)
    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        fv = f(Xref)
        fc = fv - fv.min()
        les.append(log_ess(fc, beta))
        w = np.exp(-beta * fc)
        dref = Xref - (w[:, None] * Xref).sum(axis=0) / w.sum()
        Xref = Xref - dt * dref + sigma * np.linalg.norm(dref, axis=1)[:, None] * dW
        for J in J_list:
            Xj = Xsub[J]
            fj = f(Xj)
            wj = np.exp(-beta * (fj - fj.min()))
            dj = Xj - (wj[:, None] * Xj).sum(axis=0) / wj.sum()
            Xsub[J] = Xj - dt * dj + sigma * np.linalg.norm(dj, axis=1)[:, None] * dW[:J]
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1), out=runmax[J])
    les = np.array(les)
    return ({J: float(np.mean(runmax[J])) for J in J_list},
            float(les[0]), float(les.mean()), float(les.min()))


def task(a):
    obj, d, tau, beta, sigma, dt, K, Jinf, J_list, seed = a
    per_J, l0, lm, lmin = one_realisation(obj, d, tau, beta, sigma, dt, K,
                                          Jinf, J_list, seed)
    return obj, d, tau, per_J, l0, lm, lmin


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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=0)
    p.add_argument("--sigma", type=float, default=0.2)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260823)
    args = p.parse_args()

    lam, K = 1.0, int(round(args.T / args.dt))

    if args.quick:
        Jinf, J_list = 4000, [10, 40, 160, 400]
        dims, objs = [10], ["ackley", "rosenbrock"]
        taus, M = [0.3, 0.1, 0.03, 0.01], 3
    else:
        Jinf, J_list = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        dims = [5, 10, 40]
        objs = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
        taus = [0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01]
        M = 15
    if args.realisations:
        M = args.realisations
    J_list = [J for J in J_list if J <= Jinf // 10]

    print("=" * 84)
    print("CBO-GAP Phase 5 — resolving the visibility boundary")
    print("=" * 84)
    print("  PRE-REGISTERED, fixed before the first run:")
    print("    RECOVERED per cell iff bootstrap 95% upper bound <= {:+.2f}".format(THRESH))
    print("    PER CELL ONLY — no verdict is computed from a mean across cells.")
    print("    Boundary reported as a BRACKET; interpolation only where the slope")
    print("    is monotone in the target, tested per cell.")
    print("    UNIVERSAL iff one target recovers everywhere and one fails everywhere.")
    print("    Three currencies reported: initial, time-averaged, minimum ESS")
    print("    fraction; the criterion is stated in whichever has the smallest")
    print("    spread of the boundary across cells.")
    print("\n  Fixed beta only — the algorithm the theory analyses.")
    print("  Jinf {}   J grid {}   realisations {}   targets {}".format(
        Jinf, len(J_list), M, taus))
    print("  sigma {}  dt {}  T {}  steps {}".format(args.sigma, args.dt, args.T, K))
    dims = [d for d in dims if 2.0 * lam > d * args.sigma ** 2]
    print("  d in {} (2*lambda > d*sigma^2 holds throughout)".format(dims))

    print("\n  beta by bisection on a probe ensemble:")
    beta = {}
    for o in objs:
        for d in dims:
            rng = np.random.default_rng(999 + 131 * d)
            Xp = rng.standard_normal((4000, d)) + MINIMIZER[o]
            fv = OBJECTIVES[o](Xp)
            fc = fv - fv.min()
            for tau in taus:
                beta[(o, d, tau)] = solve_beta(fc, math.log(tau * 4000))
    print("  {:<12} {:>5}".format("objective", "d") +
          "".join("{:>12}".format("t=" + str(t)) for t in taus))
    for o in objs:
        for d in dims:
            print("  {:<12} {:>5}".format(o, d) +
                  "".join("{:>12.4g}".format(beta[(o, d, t)]) for t in taus))

    tasks, s = [], args.seed
    for o in objs:
        for d in dims:
            for tau in taus:
                for _ in range(M):
                    s += 1
                    tasks.append((o, d, tau, beta[(o, d, tau)], args.sigma,
                                  args.dt, K, Jinf, J_list, s))

    print("\n  {} realisations queued on {} workers\n".format(len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    agg = {}
    for o, d, tau, per_J, l0, lm, lmin in res:
        k = (o, d, tau)
        if k not in agg:
            agg[k] = {"E": {J: [] for J in J_list}, "l0": [], "lm": [], "lmin": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        agg[k]["l0"].append(l0)
        agg[k]["lm"].append(lm)
        agg[k]["lmin"].append(lmin)

    rec, rows = {}, []
    for (o, d, tau), r in sorted(agg.items()):
        sl = fit_slope(np.array(J_list, float),
                       np.array([np.mean(r["E"][J]) for J in J_list]))
        lo, hi = boot_ci(r["E"], J_list)
        f0 = math.exp(min(float(np.mean(r["l0"])), 700)) / Jinf
        fm = math.exp(min(float(np.mean(r["lm"])), 700)) / Jinf
        fmin = math.exp(min(float(np.mean(r["lmin"])), 700)) / Jinf
        v = "recovered" if hi <= THRESH else ("NOT observed" if lo > THRESH else "UNDECIDED")
        rec[(o, d, tau)] = (sl, lo, hi, f0, fm, fmin, v)
        rows.append([o, CLASS[o], d, tau, "{:.6g}".format(beta[(o, d, tau)]),
                     "{:.6f}".format(sl), "{:.6f}".format(lo), "{:.6f}".format(hi),
                     "{:.6g}".format(f0), "{:.6g}".format(fm), "{:.6g}".format(fmin), v])

    with open("boundary_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "tau", "beta", "J", "Ehat", "stderr",
                    "ess_frac_initial", "ess_frac_timeavg", "ess_frac_min", "realisations"])
        for (o, d, tau), r in sorted(agg.items()):
            f0 = math.exp(min(float(np.mean(r["l0"])), 700)) / Jinf
            fm = math.exp(min(float(np.mean(r["lm"])), 700)) / Jinf
            fmin = math.exp(min(float(np.mean(r["lmin"])), 700)) / Jinf
            for J in J_list:
                v = np.array(r["E"][J])
                w.writerow([o, d, tau, "{:.6g}".format(beta[(o, d, tau)]), J,
                            "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.6g}".format(f0), "{:.6g}".format(fm),
                            "{:.6g}".format(fmin), len(v)])
    with open("boundary_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "class", "d", "tau", "beta", "slope", "ci_lo",
                    "ci_hi", "ess_frac_initial", "ess_frac_timeavg",
                    "ess_frac_min", "verdict"])
        w.writerows(rows)

    print("\n" + "-" * 84)
    print("P5.1 — slope against target, per cell")
    print("-" * 84)
    print("  r = recovered, u = undecided, n = not observed\n")
    print("  {:<12} {:<10} {:>4}".format("objective", "class", "d") +
          "".join("{:>13}".format("t=" + str(t)) for t in taus) + "{:>7}".format("mono"))
    monotone = {}
    for o in objs:
        for d in dims:
            ss = [rec[(o, d, t)][0] for t in taus]
            diffs = np.diff(ss)      # taus descending: slope should rise (flatten)
            mono = bool(np.all(diffs >= -0.02))
            monotone[(o, d)] = mono
            line = "  {:<12} {:<10} {:>4}".format(o, CLASS[o], d)
            for t in taus:
                sl, _, _, _, _, _, v = rec[(o, d, t)]
                line += "{:>13}".format("{:+.3f}{}".format(sl, v[0]))
            print(line + "{:>7}".format("yes" if mono else "NO"))
    print("\n  Non-monotone cells are excluded from interpolation below rather")
    print("  than averaged in.")

    print("\n" + "-" * 84)
    print("P5.2 — THE BOUNDARY, as a bracket per cell")
    print("-" * 84)
    print("  largest target that FAILS  /  smallest target that RECOVERS\n")
    print("  {:<12} {:<10} {:>4} {:>10} {:>10} {:>14} {:>14} {:>12}".format(
        "objective", "class", "d", "fails at", "recovers", "ESS init", "ESS timeavg", "ESS min"))
    fails, oks = [], []
    b_init, b_tavg, b_min = [], [], []
    for o in objs:
        for d in dims:
            fail = max([t for t in taus if rec[(o, d, t)][6] != "recovered"], default=None)
            ok = min([t for t in taus if rec[(o, d, t)][6] == "recovered"
                      and (fail is None or t > fail)], default=None)
            if fail is not None:
                fails.append(fail)
            if ok is not None:
                oks.append(ok)
                _, _, _, f0, fm, fmin = rec[(o, d, ok)][:6]
                b_init.append(f0)
                b_tavg.append(fm)
                b_min.append(fmin)
            print("  {:<12} {:<10} {:>4} {:>10} {:>10} {:>14} {:>14} {:>12}".format(
                o, CLASS[o], d,
                "{:g}".format(fail) if fail is not None else "none",
                "{:g}".format(ok) if ok is not None else "none in grid",
                "{:.4g}".format(rec[(o, d, ok)][3]) if ok else "-",
                "{:.4g}".format(rec[(o, d, ok)][4]) if ok else "-",
                "{:.4g}".format(rec[(o, d, ok)][5]) if ok else "-"))

    print("\n" + "-" * 84)
    print("P5.3 — is the criterion universal?")
    print("-" * 84)
    univ_ok = [t for t in taus
               if all(rec[(o, d, t)][6] == "recovered" for o in objs for d in dims)]
    univ_no = [t for t in taus
               if all(rec[(o, d, t)][6] != "recovered" for o in objs for d in dims)]
    print("  targets recovered in EVERY cell : {}".format(univ_ok if univ_ok else "none"))
    print("  targets failing in EVERY cell   : {}".format(univ_no if univ_no else "none"))
    if univ_ok and univ_no:
        print("\n  UNIVERSAL: the boundary lies between {:g} and {:g} for all {} cells,".format(
            max(univ_no), min(univ_ok), len(objs) * len(dims)))
        print("  spanning {} objectives, {} dimensions and {} assumption classes.".format(
            len(objs), len(dims), len(set(CLASS[o] for o in objs))))
    else:
        print("\n  NOT UNIVERSAL: no single target separates every cell. The boundary")
        print("  depends on something beyond concentration, and that must be said.")

    def spread(v, name):
        if len(v) < 2:
            return
        v = np.array(v)
        print("    {:<14} n={:<3} median={:.4g}  min={:.4g}  max={:.4g}  "
              "log10 spread={:.3f}".format(
                  name, len(v), float(np.median(v)), float(v.min()), float(v.max()),
                  float(np.log10(v.max() / v.min())) if v.min() > 0 else float("inf")))
    print("\n  Boundary expressed in each currency, at the smallest recovering target:")
    spread(b_init, "initial")
    spread(b_tavg, "time-averaged")
    spread(b_min, "minimum")
    cands = [(np.log10(max(v) / min(v)) if v and min(v) > 0 else float("inf"), n)
             for v, n in ((b_init, "initial"), (b_tavg, "time-averaged"), (b_min, "minimum"))]
    print("\n  Smallest spread — the currency the criterion should be stated in: {}".format(
        min(cands)[1]))

    print("\n" + "-" * 84)
    print("P5.4 — description only (barred from every verdict above)")
    print("-" * 84)
    for t in taus:
        ss = [rec[(o, d, t)][0] for o in objs for d in dims]
        n_r = sum(1 for o in objs for d in dims if rec[(o, d, t)][6] == "recovered")
        print("    tau={:<6g} mean slope {:+.4f}  sd {:.4f}   recovered {}/{}".format(
            t, float(np.mean(ss)), float(np.std(ss, ddof=1)), n_r, len(objs) * len(dims)))

    print("\n" + "=" * 84)
    print("wrote boundary_raw.csv and boundary_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 84)


if __name__ == "__main__":
    main()
