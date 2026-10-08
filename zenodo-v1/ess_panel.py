"""
ess_panel.py  —  CBO-GAP Phase 1c: does the exponent survive scrutiny?

WHAT THIS SCRIPT IS FOR, IN PLAIN LANGUAGE
------------------------------------------
Phase 1b produced one clean result: for Ackley, the slope of log Ehat against
log J depends on the dimension and on essentially nothing else. Across three
decades of beta*spread the columns barely moved, and a single power law
|slope| = c * d^(-p) fitted with p near 0.57 and residuals under 0.2.

That result is not yet safe. Three things could destroy it, and this script
tests all three in one run.

  P1c.1 — THE KILL TEST: reference-run bias.
      Every number so far was measured against a 50000-particle reference run,
      not against the mean-field limit. GHV used a million. If the reference
      cloud is itself under-resolved at large d, then a "dimension-dependent
      exponent" and a "dimension-dependent proxy artefact" look identical.
      What we compute: the Ackley exponent curve at three reference sizes.
      What the result means: if the fitted p is stable across Jinf, the curve
      is real. If p drifts with Jinf, THE EXPONENT RESULT IS DEAD and the paper
      keeps only the d = 2 cliff. This is the one experiment whose outcome
      changes what may be claimed, so it runs first and is reported first.

  P1c.2 — THE OBJECTIVE PANEL.
      "The exponent depends on the objective" currently rests on two functions.
      That is an anecdote. Six objectives spanning the (s, ell, u) table turn
      the measured exponent into a COLUMN of that table rather than a separate
      claim, and let the ell question be answered with six points instead of
      two.
      Rosenbrock is the row that matters most: it is the only one with
      ell != u, it fails FKR's growth conditions (19) and (20), and GHV state
      their main results need ell = u. Whatever it does is informative, and if
      it misbehaves that is a finding rather than a bug.

  P1c.3 — BOOTSTRAP INTERVALS.
      Every slope so far was fitted to the MEAN over 20 realisations with no
      uncertainty attached. Calling a gap of 0.044 "collapse" and 0.156 "no
      collapse" had no basis. Resampling the realisations gives real intervals,
      and any verdict whose interval straddles the threshold must be reported
      as undecided rather than decided.

WHAT THIS SCRIPT STILL CANNOT DO
--------------------------------
It cannot reach the beta of FKR's own figures — past roughly 700 divided by the
objective's range every Boltzmann weight underflows and the weighted mean IS the
arg min. Rows in that regime are flagged SATURATED and their slope is not a rate.

It cannot prove a mechanism for p. Six dimensions and a power law is a
description. The earlier extreme-order-statistics guess of 2/d was tested twice
and failed both times; no mechanism is assumed here.

The initial law is centred exactly on the minimizer. That is the favourable case
and it is not swept — it is a stated limitation, not a hidden one.

HOW TO RUN
----------
    python ess_panel.py --workers 3 --quick    (smoke test, ~3 minutes)
    python ess_panel.py --workers 3            (the real sweep, ~2-3 hours)

NumPy only. No SciPy. Python 3.8 compatible.
Writes ess_panel_raw.csv and ess_panel_summary.csv.
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


# ----------------------------------------------------------------------
# objectives, with their (s, ell, u) classification from the audit table
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
    t3 = (wl - 1.0) ** 2 * (1.0 + np.sin(2.0 * np.pi * wl) ** 2)
    return t1 + t2 + t3


def f_rosenbrock(X):
    xi, xn = X[:, :-1], X[:, 1:]
    return np.sum(100.0 * (xn - xi ** 2) ** 2 + (1.0 - xi) ** 2, axis=1)


OBJECTIVES = {
    "ackley": f_ackley,
    "rastrigin": f_rastrigin,
    "sphere": f_sphere,
    "griewank": f_griewank,
    "levy": f_levy,
    "rosenbrock": f_rosenbrock,
}

# (s, ell, u) and the minimizer, from the audit table. The minimizer matters:
# Levy and Rosenbrock do NOT have theirs at the origin, and centring the initial
# law on the origin for them would be a different experiment from the others.
CLASS = {
    "ackley":     ("A(0,0,0)",   "bounded; ell=0"),
    "rastrigin":  ("A(1,2,2)",   "full coverage"),
    "sphere":     ("A(1,2,2)",   "full coverage"),
    "griewank":   ("A(1,2,2)",   "full coverage"),
    "levy":       ("A(2,2,2)",   "GHV ok; FAILS FKR (19)"),
    "rosenbrock": ("A(3,1,4)",   "ell!=u; FAILS FKR (19),(20)"),
}
MINIMIZER = {"ackley": 0.0, "rastrigin": 0.0, "sphere": 0.0,
             "griewank": 0.0, "levy": 1.0, "rosenbrock": 1.0}


def spread_of(objective, d, n=20000, seed=12345):
    rng = np.random.default_rng(seed + 1000 * d)
    X = rng.standard_normal((n, d)) + MINIMIZER[objective]
    return float(np.std(OBJECTIVES[objective](X)))


def weighted_mean_and_ess(X, fvals, beta):
    shift = fvals.min()
    w = np.exp(-beta * (fvals - shift))
    s = w.sum()
    m = (w[:, None] * X).sum(axis=0) / s
    return m, float((s * s) / (w * w).sum())


def one_realisation(objective, beta, d, sigma, dt, K, Jinf, J_list, seed):
    """Synchronous coupling, as in GHV Subsection 2.6: one reference system of
    Jinf particles; for each J a smaller system started at the same positions
    and driven by the same Brownian increments as the reference system's first
    J particles, each computing its own consensus point."""
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = rng.standard_normal((Jinf, d)) + MINIMIZER[objective]
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
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1),
                       out=runmax[J])

    return {J: float(np.mean(runmax[J])) for J in J_list}, ess_ref


def task(a):
    obj, B, beta, d, Jinf, sigma, dt, K, J_list, seed = a
    per_J, ess = one_realisation(obj, beta, d, sigma, dt, K, Jinf, J_list, seed)
    return obj, B, beta, d, Jinf, per_J, ess


def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def bootstrap_slope(per_realisation, J_list, n_boot=400, seed=7):
    """per_realisation[J] is a list over realisations. Resample realisations
    with replacement, refit the slope each time, return the 2.5/97.5 quantiles.
    This is the uncertainty that every earlier slope in this project lacked."""
    rng = np.random.default_rng(seed)
    R = len(per_realisation[J_list[0]])
    Jv = np.array(J_list, float)
    M = np.array([[per_realisation[J][r] for J in J_list] for r in range(R)])
    out = []
    for _ in range(n_boot):
        idx = rng.integers(0, R, R)
        out.append(fit_slope(Jv, M[idx].mean(axis=0)))
    out = np.array([o for o in out if np.isfinite(o)])
    if out.size < 20:
        return float("nan"), float("nan")
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def powerfit(pairs):
    dd = np.array([p[0] for p in pairs], float)
    ss = np.abs(np.array([p[1] for p in pairs], float))
    m = np.isfinite(ss) & (ss > 1e-6)
    if m.sum() < 3:
        return float("nan"), float("nan"), float("nan")
    A = np.vstack([np.log(dd[m]), np.ones(m.sum())]).T
    sol, _, _, _ = np.linalg.lstsq(A, np.log(ss[m]), rcond=None)
    resid = float(np.max(np.abs(np.log(ss[m]) - A @ sol)))
    return -float(sol[0]), math.exp(float(sol[1])), resid


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--sigma", type=float, default=0.2)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260819)
    args = p.parse_args()

    lam, K = 1.0, int(round(args.T / args.dt))
    B_panel = 30.0  # the least-saturated point of the Phase 1b grid

    if args.quick:
        dims = [2, 5, 10]
        Jinfs = [2000, 4000]
        J_of = {2000: [10, 40, 160], 4000: [10, 40, 160, 400]}
        M = 3
        panel = ["ackley", "rastrigin", "rosenbrock"]
    else:
        dims = [2, 3, 5, 10, 20, 40]
        Jinfs = [12500, 25000, 50000]
        J_of = {12500: [10, 20, 40, 80, 160, 320, 640, 1250],
                25000: [10, 20, 40, 80, 160, 320, 640, 1280, 2500],
                50000: [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]}
        M = 20
        panel = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]

    print("=" * 78)
    print("CBO-GAP Phase 1c — reference-run stability, objective panel, intervals")
    print("=" * 78)
    print("  sigma {}   dt {}   T {}   steps {}   realisations {}".format(
        args.sigma, args.dt, args.T, K, M))
    print("  every J is at most Jinf/10; larger J is refused, not reported")

    print("\n  FKR condition 2*lambda > d*sigma^2:")
    bad = set()
    for d in dims:
        ok = 2.0 * lam > d * args.sigma ** 2
        if not ok:
            bad.add(d)
        print("    d={:<4} 2*lambda={:.3f}  d*sigma^2={:.3f}  {}".format(
            d, 2.0 * lam, d * args.sigma ** 2, "ok" if ok else "VIOLATED — drop"))
    dims = [d for d in dims if d not in bad]

    print("\n  objective panel (class from the audit table, minimizer, spread at d=10):")
    print("    {:<12} {:<12} {:<30} {:>10}".format("objective", "class", "note", "spread"))
    for o in panel:
        print("    {:<12} {:<12} {:<30} {:>10.4f}".format(
            o, CLASS[o][0], CLASS[o][1], spread_of(o, 10)))
    print("\n  Levy and Rosenbrock have their minimizer at the all-ones point, so")
    print("  their initial law is centred there. Centring on the origin instead")
    print("  would be a different experiment and is not what the others do.")

    tasks, s = [], args.seed
    # P1c.1 — Ackley at every Jinf
    for Ji in Jinfs:
        for d in dims:
            beta = B_panel / spread_of("ackley", d)
            for _ in range(M):
                s += 1
                tasks.append(("ackley", B_panel, beta, d, Ji, args.sigma,
                              args.dt, K, J_of[Ji], s))
    # P1c.2 — the rest of the panel at the largest Jinf only
    Jmax = Jinfs[-1]
    for obj in panel:
        if obj == "ackley":
            continue
        for d in dims:
            beta = B_panel / spread_of(obj, d)
            for _ in range(M):
                s += 1
                tasks.append((obj, B_panel, beta, d, Jmax, args.sigma,
                              args.dt, K, J_of[Jmax], s))

    print("\n  {} realisations queued on {} workers\n".format(len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    agg = {}
    for obj, B, beta, d, Ji, per_J, ess in res:
        k = (obj, Ji, d)
        if k not in agg:
            agg[k] = {"beta": beta, "E": {J: [] for J in J_of[Ji]}, "ess": []}
        for J in J_of[Ji]:
            agg[k]["E"][J].append(per_J[J])
        agg[k]["ess"].append(ess)

    with open("ess_panel_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "Jinf", "d", "beta", "J", "Ehat", "stderr",
                    "min_ESS_ref", "realisations"])
        for (obj, Ji, d), r in sorted(agg.items()):
            for J in J_of[Ji]:
                v = np.array(r["E"][J])
                w.writerow([obj, Ji, d, "{:.6g}".format(r["beta"]), J,
                            "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.4f}".format(np.mean(r["ess"])), len(v)])

    slopes, summary = {}, []
    for (obj, Ji, d), r in sorted(agg.items()):
        Jl = J_of[Ji]
        sl = fit_slope(np.array(Jl, float),
                       np.array([np.mean(r["E"][J]) for J in Jl]))
        lo, hi = bootstrap_slope(r["E"], Jl)
        ess = float(np.mean(r["ess"]))
        v = "SATURATED" if ess < 1.01 else ("recovered" if hi <= -0.85 else
                                            ("NOT observed" if lo > -0.85 else "UNDECIDED"))
        slopes[(obj, Ji, d)] = (sl, lo, hi, ess, v)
        summary.append([obj, Ji, d, "{:.6f}".format(sl), "{:.6f}".format(lo),
                        "{:.6f}".format(hi), "{:.4f}".format(ess), v])

    with open("ess_panel_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "Jinf", "d", "slope", "ci_lo", "ci_hi",
                    "min_ESS_ref", "verdict"])
        w.writerows(summary)

    print("\n" + "-" * 78)
    print("P1c.1 — THE KILL TEST: is the Ackley exponent stable in Jinf?")
    print("-" * 78)
    print("  If the fitted p drifts with the reference size, the exponent curve is")
    print("  a proxy artefact and the paper keeps only the d = 2 cliff.\n")
    hdr = "  {:>6}" + "".join("{:>22}".format("Jinf=" + str(J)) for J in Jinfs)
    print(hdr)
    print("  {:>6}".format("d") + "".join("{:>22}".format("slope [95% CI]") for _ in Jinfs))
    for d in dims:
        line = "  {:>6}".format(d)
        for Ji in Jinfs:
            sl, lo, hi, _, _ = slopes[("ackley", Ji, d)]
            line += "{:>22}".format("{:+.3f} [{:+.3f},{:+.3f}]".format(sl, lo, hi))
        print(line)
    print()
    ps = []
    for Ji in Jinfs:
        pe, c, resid = powerfit([(d, slopes[("ackley", Ji, d)][0]) for d in dims])
        ps.append(pe)
        print("    Jinf={:<7} p = {:.4f}   c = {:.4f}   max resid = {:.4f}".format(
            Ji, pe, c, resid))
    drift = max(ps) - min(ps)
    print("\n    spread of p across reference sizes: {:.4f}".format(drift))
    print("    VERDICT: {}".format(
        "p is stable — the exponent curve SURVIVES" if drift < 0.10 else
        "p DRIFTS with Jinf — the exponent curve is NOT SAFE to claim"))

    print("\n" + "-" * 78)
    print("P1c.2 — the objective panel at Jinf={}, B={:g}".format(Jmax, B_panel))
    print("-" * 78)
    print("  This is the measured column of the (s, ell, u) table.\n")
    hdr2 = "  {:<12} {:<12}" + "".join("{:>10}".format("d=" + str(d)) for d in dims)
    print(hdr2.format("objective", "class"))
    for obj in panel:
        line = "  {:<12} {:<12}".format(obj, CLASS[obj][0])
        for d in dims:
            sl, lo, hi, ess, v = slopes[(obj, Jmax, d)]
            line += "{:>10}".format("{:+.3f}".format(sl) + ("*" if ess < 1.01 else ""))
        print(line)
    print("\n  * = ESS reached 1: hardmin regime, the number is not a rate.\n")
    print("  {:<12} {:>8} {:>8} {:>12} {:>28}".format(
        "objective", "p", "c", "max resid", "power law usable?"))
    for obj in panel:
        pe, c, resid = powerfit([(d, slopes[(obj, Jmax, d)][0]) for d in dims])
        usable = "yes" if resid < 0.25 else "NO — do not quote this fit"
        print("  {:<12} {:>8.4f} {:>8.4f} {:>12.4f} {:>28}".format(obj, pe, c, resid, usable))

    print("\n" + "-" * 78)
    print("P1c.3 — verdicts with intervals")
    print("-" * 78)
    print("  UNDECIDED means the interval straddles the -0.85 threshold. Those")
    print("  rows must be reported as undecided, not rounded to a verdict.\n")
    print("  {:<12} {:>4} {:>10} {:>20} {:>10} {:>14}".format(
        "objective", "d", "slope", "95% CI", "min ESS", "verdict"))
    for obj in panel:
        for d in dims:
            sl, lo, hi, ess, v = slopes[(obj, Jmax, d)]
            print("  {:<12} {:>4} {:>10.4f} {:>20} {:>10.3f} {:>14}".format(
                obj, d, sl, "[{:+.3f},{:+.3f}]".format(lo, hi), ess, v))

    print("\n" + "=" * 78)
    print("wrote ess_panel_raw.csv and ess_panel_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 78)


if __name__ == "__main__":
    main()
