"""
crossed.py  —  CBO-GAP Phase 9: is anisotropic worse, or just noisier?

THE CONFOUND THIS SCRIPT EXISTS TO REMOVE
------------------------------------------
Phase 8 compared isotropic and anisotropic diffusion at matched distance from
each one's own stability condition, r = d*sigma^2/(2*lambda) for isotropic and
r = sigma^2/(2*lambda) for anisotropic. Anisotropic came out flatter, and the
gap grew monotonically with dimension: +0.075 at d = 40 and tau = 0.1, +0.108 at
tau = 0.01, against roughly zero at d = 5.

That result cannot be reported as it stands. Because the anisotropic condition
is dimension-free, matching r forces

    sigma_aniso / sigma_iso  =  sqrt(d),

which is 2.2 at d = 5 and 6.3 at d = 40. Phase 8 did not compare two diffusion
structures. It compared a system carrying six times the noise against one that
was not. A referee needs one sentence to say so, and would be right.

Matched r is the correct control for a statement about the CONDITION. It is the
wrong control for a statement about the STRUCTURE. Neither arm alone answers the
question, so this script runs both and reports them side by side:

    ARM A, matched sigma      sigma in {0.1, 0.2, 0.4}, identical for both
                              diffusion types. Isolates diffusion structure at
                              equal noise magnitude. This is the arm that can
                              speak to whether componentwise noise helps in high
                              dimension.

    ARM B, matched r          r in {0.1, 0.5, 0.9}, sigma solved per type as in
                              Phase 8. Reproduces the Phase 8 comparison on the
                              same seeds and grid so the two arms are directly
                              comparable rather than being compared across runs.

Concentration is held fixed by bisection on beta throughout, so nothing here can
be the concentration effect in disguise.

A NOTE ON WHAT MATCHED SIGMA MEANS
-----------------------------------
At a common sigma the two systems are NOT at a common distance from their own
stability limits: at sigma = 0.4 and d = 40 the isotropic system has
d*sigma^2 = 6.4 against 2*lambda = 2, so it lies OUTSIDE the condition of
FKR Theorem 3.7 entirely, while the anisotropic system at sigma^2 = 0.16 is
comfortably inside. Those cells are flagged in the output. They are not dropped,
because whether the observable rate degrades outside the condition is exactly
what Phase 8 found it does not, and the flag lets a reader see which cells carry
that caveat.

This is the honest structure of the problem: the two diffusion types cannot be
compared at matched sigma AND matched r simultaneously. Reporting both and
naming the trade-off is the most that the design permits.

PRE-REGISTERED, fixed before the first run
-------------------------------------------
  delta = -1 - slope_hat. RATE-CONSISTENT AT TOLERANCE 0.15 iff the bootstrap
  95 percent upper bound is at or below -0.85. The proven exponent is -1 and a
  slope of -0.85 is never called that rate. Counts are also reported at
  tolerances 0.10 and 0.20 because 0.15 is arbitrary and Phase 8 showed the
  count moves from 71 to 115 of 144 across that range.

  Bootstrap unit: the independent coupled realisation, all J values kept
  together, slope refitted per resample, 400 resamples, percentile interval,
  seed 7. Criterion applied per cell; no familywise guarantee is claimed and
  Bonferroni-adjusted intervals are reported alongside.

  THE DECISION RULE, fixed in advance:
    If the anisotropic-minus-isotropic gap at matched sigma is below 0.05 at
    every dimension while the matched-r gap grows with dimension as in Phase 8,
    the Phase 8 result is a noise-magnitude effect and must be reported as such.
    If the gap persists at matched sigma and grows with dimension, it is a
    property of the diffusion structure.
    If the gap at matched sigma runs the OTHER way, anisotropic is better at
    equal noise and worse only because its condition permits more of it, which
    is a third outcome and the most interesting one.

WHAT THIS SCRIPT DOES NOT DO
----------------------------
It does not measure the end-to-end optimization error; the estimator is the
coupled distance between a finite ensemble and a reference ensemble of 50000,
which is a proxy and not the mean-field limit. Horizon fixed at T = 1. Initial
law centred at the minimizer. Four objectives.

HOW TO RUN
----------
    python crossed.py --workers 3 --quick      (smoke test, ~4 min)
    python crossed.py --workers 3              (full, budget 3-3.5 h)
    python crossed.py --workers 3 --arm A      (matched sigma only)
    python crossed.py --workers 3 --arm B      (matched r only)

NumPy only. No SciPy. Python 3.8 compatible.
Writes crossed_raw.csv and crossed_summary.csv.
"""

import argparse
import csv
import math
import os
import platform
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

TOLS = [0.10, 0.15, 0.20]
TOL = 0.15
THRESH = -1.0 + TOL
N_BOOT = 400
BOOT_SEED = 7
GAP_RULE = 0.05


def f_ackley(X):
    d = X.shape[1]
    s1 = np.sqrt(np.sum(X * X, axis=1) / d)
    s2 = np.sum(np.cos(2.0 * np.pi * X), axis=1) / d
    return -20.0 * np.exp(-0.2 * s1) - np.exp(s2) + 20.0 + math.e


def f_rastrigin(X):
    return np.sum(X * X + 10.0 * (1.0 - np.cos(2.0 * np.pi * X)), axis=1)


def f_sphere(X):
    return np.sum(X * X, axis=1)


def f_rosenbrock(X):
    xi, xn = X[:, :-1], X[:, 1:]
    return np.sum(100.0 * (xn - xi ** 2) ** 2 + (1.0 - xi) ** 2, axis=1)


OBJ = {"ackley": f_ackley, "rastrigin": f_rastrigin,
       "sphere": f_sphere, "rosenbrock": f_rosenbrock}
XSTAR = {"ackley": 0.0, "rastrigin": 0.0, "sphere": 0.0, "rosenbrock": 1.0}


def _lse(a):
    m = a.max()
    return m + math.log(float(np.exp(a - m).sum()))


def log_ess(fc, beta):
    lw = -beta * fc
    return 2.0 * _lse(lw) - _lse(2.0 * lw)


def solve_beta(fc, goal_log, iters=90):
    lo, hi = 1e-14, 1e14
    for _ in range(iters):
        mid = math.sqrt(lo * hi)
        if log_ess(fc, mid) > goal_log:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def r_of(diff, d, sigma, lam=1.0):
    return (d * sigma ** 2 if diff == "isotropic" else sigma ** 2) / (2.0 * lam)


def sigma_of(diff, d, r, lam=1.0):
    return math.sqrt(2.0 * lam * r / (d if diff == "isotropic" else 1.0))


def one_realisation(name, d, diff, beta, sigma, lam, dt, K, Jinf, J_list, seed):
    f = OBJ[name]
    xs = XSTAR[name]
    rng = np.random.default_rng(seed)
    X0 = rng.standard_normal((Jinf, d)) + xs
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    les = []
    sq = math.sqrt(dt)

    def step(X, dW):
        fv = f(X)
        fc = fv - fv.min()
        w = np.exp(-beta * fc)
        m = (w[:, None] * X).sum(axis=0) / w.sum()
        dv = X - m
        noise = (sigma * np.linalg.norm(dv, axis=1)[:, None] * dW
                 if diff == "isotropic" else sigma * dv * dW)
        return X - lam * dt * dv + noise, fc

    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        Xref, fc = step(Xref, dW)
        les.append(log_ess(fc, beta))
        for J in J_list:
            Xsub[J], _ = step(Xsub[J], dW[:J])
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1),
                       out=runmax[J])

    les = np.array(les)
    return ({J: float(np.mean(runmax[J])) for J in J_list},
            float(les[0]), float(les.mean()), float(les.min()))


def task(a):
    (arm, name, d, diff, lvl, tau, beta, sigma, lam, dt, K, Jinf, J_list, seed) = a
    per_J, l0, lm, lmin = one_realisation(name, d, diff, beta, sigma, lam,
                                          dt, K, Jinf, J_list, seed)
    return arm, name, d, diff, lvl, tau, beta, sigma, per_J, l0, lm, lmin


def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def boot_ci(per_real, J_list, level=95.0):
    R = len(per_real[J_list[0]])
    M = np.array([[per_real[J][k] for J in J_list] for k in range(R)])
    Jv = np.array(J_list, float)
    rng = np.random.default_rng(BOOT_SEED)
    out = [fit_slope(Jv, M[rng.integers(0, R, R)].mean(axis=0)) for _ in range(N_BOOT)]
    out = np.array([o for o in out if np.isfinite(o)])
    if out.size < 20:
        return float("nan"), float("nan")
    lo = (100.0 - level) / 2.0
    return float(np.percentile(out, lo)), float(np.percentile(out, 100.0 - lo))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--arm", default="both", help="A, B, or both")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=12)
    p.add_argument("--lam", type=float, default=1.0)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260827)
    args = p.parse_args()

    K = int(round(args.T / args.dt))
    M = 3 if args.quick else args.realisations
    diffs = ["isotropic", "anisotropic"]

    if args.quick:
        Jinf, Jgrid = 4000, [10, 40, 160, 400]
        objs, dims = ["ackley", "rosenbrock"], [10]
        sigmas, rs, taus = [0.2], [0.5], [0.1]
    else:
        Jinf, Jgrid = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        objs = ["ackley", "rastrigin", "sphere", "rosenbrock"]
        dims = [5, 10, 40]
        sigmas, rs, taus = [0.1, 0.2, 0.4], [0.1, 0.5, 0.9], [0.1, 0.01]
    J_list = [J for J in Jgrid if J <= Jinf // 10]
    arms = {"A": ["A"], "B": ["B"], "both": ["A", "B"]}[args.arm.upper()
                                                       if args.arm.upper() in ("A", "B")
                                                       else "both"]

    print("=" * 88)
    print("CBO-GAP Phase 9 — diffusion structure separated from noise magnitude")
    print("=" * 88)
    print("  PRE-REGISTERED (fixed before the first run):")
    print("    RATE-CONSISTENT AT TOLERANCE {:.2f} iff bootstrap 95% upper bound <= {:+.2f}.".format(TOL, THRESH))
    print("    Counts also at tolerances {}; Phase 8 moved 71->115 of 144 across that range.".format(TOLS))
    print("    Bootstrap unit: independent coupled realisation, all J together,")
    print("    slope refitted per resample, {} resamples, percentile, seed {}.".format(N_BOOT, BOOT_SEED))
    print("    DECISION RULE: if the matched-sigma gap is below {:.2f} at every".format(GAP_RULE))
    print("    dimension while the matched-r gap grows with d, the Phase 8 result")
    print("    is a noise-magnitude effect and is reported as such.")
    print("\n  REPRODUCIBILITY")
    print("    python {}   numpy {}".format(platform.python_version(), np.__version__))
    print("    platform {}   workers {}".format(platform.platform(), args.workers))
    print("    base seed {}   J grid {}".format(args.seed, J_list))
    print("    Jinf {}   realisations/cell {}   lambda {}   dt {}   T {}   steps {}".format(
        Jinf, M, args.lam, args.dt, args.T, K))

    cells = 0
    if "A" in arms:
        cells += len(diffs) * len(objs) * len(dims) * len(sigmas) * len(taus)
    if "B" in arms:
        cells += len(diffs) * len(objs) * len(dims) * len(rs) * len(taus)
    print("\n  EXPERIMENT MATRIX")
    if "A" in arms:
        print("    arm A  2 diffusions x {} objectives x {} dims x {} sigmas x {} taus = {}".format(
            len(objs), len(dims), len(sigmas), len(taus),
            len(diffs) * len(objs) * len(dims) * len(sigmas) * len(taus)))
    if "B" in arms:
        print("    arm B  2 diffusions x {} objectives x {} dims x {} r x {} taus = {}".format(
            len(objs), len(dims), len(rs), len(taus),
            len(diffs) * len(objs) * len(dims) * len(rs) * len(taus)))
    print("    total {} cells x {} realisations = {} coupled realisations".format(
        cells, M, cells * M))

    print("\n  ARM A, matched sigma: implied r, and whether the FKR condition holds")
    print("  {:<12} {:>4}".format("diffusion", "d") +
          "".join("{:>16}".format("sigma=" + str(s)) for s in sigmas))
    for diff in diffs:
        for d in dims:
            line = "  {:<12} {:>4}".format(diff, d)
            for s in sigmas:
                rr = r_of(diff, d, s, args.lam)
                line += "{:>16}".format("r={:.2f}{}".format(rr, "  OUT" if rr >= 1 else ""))
            print(line)
    print("  OUT marks cells outside 2*lambda > d*sigma^2 (isotropic) or 2*lambda > sigma^2")
    print("  (anisotropic). They are kept and flagged: Phase 8 found the observable")
    print("  rate insensitive to r, and whether that survives outside the condition")
    print("  is part of what this arm measures.")

    beta = {}
    for name in objs:
        for d in dims:
            rng = np.random.default_rng(4242 + 131 * d + 7 * len(name))
            Xp = rng.standard_normal((4000, d)) + XSTAR[name]
            fv = OBJ[name](Xp)
            fc = fv - fv.min()
            for t in taus:
                beta[(name, d, t)] = solve_beta(fc, math.log(t * 4000))

    tasks, s = [], args.seed
    for arm in arms:
        levels = sigmas if arm == "A" else rs
        for diff in diffs:
            for name in objs:
                for d in dims:
                    for lvl in levels:
                        sg = lvl if arm == "A" else sigma_of(diff, d, lvl, args.lam)
                        for t in taus:
                            for _ in range(M):
                                s += 1
                                tasks.append((arm, name, d, diff, lvl, t,
                                              beta[(name, d, t)], sg, args.lam,
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
    for arm, name, d, diff, lvl, t, b, sg, per_J, l0, lm, lmin in res:
        k = (arm, diff, name, d, lvl, t)
        if k not in agg:
            agg[k] = {"beta": b, "sigma": sg, "E": {J: [] for J in J_list},
                      "l0": [], "lm": [], "lmin": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        agg[k]["l0"].append(l0); agg[k]["lm"].append(lm); agg[k]["lmin"].append(lmin)

    nb = len(agg)
    bonf = 100.0 * (1.0 - 0.05 / nb)
    rec, rows = {}, []
    for k in sorted(agg):
        rr = agg[k]
        sl = fit_slope(np.array(J_list, float),
                       np.array([np.mean(rr["E"][J]) for J in J_list]))
        lo, hi = boot_ci(rr["E"], J_list, 95.0)
        blo, bhi = boot_ci(rr["E"], J_list, bonf)
        f0 = math.exp(min(float(np.mean(rr["l0"])), 700)) / Jinf
        fm = math.exp(min(float(np.mean(rr["lm"])), 700)) / Jinf
        fmn = math.exp(min(float(np.mean(rr["lmin"])), 700)) / Jinf
        rec[k] = dict(slope=sl, lo=lo, hi=hi, blo=blo, bhi=bhi,
                      sigma=rr["sigma"], beta=rr["beta"],
                      tau0=f0, taubar=fm, taumin=fmn)
        rows.append([k[0], k[1], k[2], k[3], k[4], k[5], "{:.6g}".format(rr["sigma"]),
                     "{:.6g}".format(r_of(k[1], k[3], rr["sigma"], args.lam)),
                     "{:.6g}".format(rr["beta"]), "{:.6f}".format(sl),
                     "{:.6f}".format(-1.0 - sl), "{:.6f}".format(lo), "{:.6f}".format(hi),
                     "{:.6f}".format(blo), "{:.6f}".format(bhi),
                     "{:.6g}".format(f0), "{:.6g}".format(fm), "{:.6g}".format(fmn),
                     "rate-consistent" if hi <= THRESH else "not rate-consistent"])

    with open("crossed_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "diffusion", "objective", "d", "level", "tau", "sigma",
                    "r", "beta", "J", "Ehat", "stderr", "tau0", "taubar", "taumin",
                    "realisations"])
        for k in sorted(agg):
            rr = agg[k]
            f0 = math.exp(min(float(np.mean(rr["l0"])), 700)) / Jinf
            fm = math.exp(min(float(np.mean(rr["lm"])), 700)) / Jinf
            fmn = math.exp(min(float(np.mean(rr["lmin"])), 700)) / Jinf
            for J in J_list:
                v = np.array(rr["E"][J])
                w.writerow([k[0], k[1], k[2], k[3], k[4], k[5],
                            "{:.6g}".format(rr["sigma"]),
                            "{:.6g}".format(r_of(k[1], k[3], rr["sigma"], args.lam)),
                            "{:.6g}".format(rr["beta"]), J, "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.6g}".format(f0), "{:.6g}".format(fm),
                            "{:.6g}".format(fmn), len(v)])
    with open("crossed_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "diffusion", "objective", "d", "level", "tau", "sigma",
                    "r", "beta", "slope", "delta", "ci_lo", "ci_hi", "bonf_lo",
                    "bonf_hi", "tau0", "taubar", "taumin", "verdict"])
        w.writerows(rows)

    def gap(arm, d, lvl, t):
        a = np.mean([rec[(arm, "isotropic", o, d, lvl, t)]["slope"] for o in objs])
        b = np.mean([rec[(arm, "anisotropic", o, d, lvl, t)]["slope"] for o in objs])
        return a, b, b - a

    if "A" in arms:
        print("\n" + "-" * 88)
        print("P9.1 — ARM A: matched sigma. Diffusion structure at equal noise.")
        print("-" * 88)
        print("  Positive gap means anisotropic is FLATTER, i.e. worse.\n")
        print("  {:>7} {:>5} {:>7} {:>12} {:>13} {:>10} {:>8}".format(
            "sigma", "d", "tau", "isotropic", "anisotropic", "gap", "iso r"))
        for sg in sigmas:
            for d in dims:
                for t in taus:
                    a, b, g = gap("A", d, sg, t)
                    rr = r_of("isotropic", d, sg, args.lam)
                    print("  {:>7g} {:>5} {:>7g} {:>12.4f} {:>13.4f} {:>10.4f} {:>8}".format(
                        sg, d, t, a, b, g, "{:.2f}{}".format(rr, "*" if rr >= 1 else "")))
        print("\n  * = isotropic cell outside the FKR parameter condition.")

    if "B" in arms:
        print("\n" + "-" * 88)
        print("P9.2 — ARM B: matched r. Reproduces Phase 8 on these seeds.")
        print("-" * 88)
        print("  {:>7} {:>5} {:>7} {:>12} {:>13} {:>10} {:>16}".format(
            "r", "d", "tau", "isotropic", "anisotropic", "gap", "sigma ratio"))
        for r in rs:
            for d in dims:
                for t in taus:
                    a, b, g = gap("B", d, r, t)
                    si = sigma_of("isotropic", d, r, args.lam)
                    sa = sigma_of("anisotropic", d, r, args.lam)
                    print("  {:>7g} {:>5} {:>7g} {:>12.4f} {:>13.4f} {:>10.4f} {:>16}".format(
                        r, d, t, a, b, g, "{:.1f}x".format(sa / si)))

    if len(arms) == 2:
        print("\n" + "-" * 88)
        print("P9.3 — THE TEST: does the gap survive at equal noise?")
        print("-" * 88)
        print("  {:>5} {:>7} {:>18} {:>18} {:>14}".format(
            "d", "tau", "gap, matched sigma", "gap, matched r", "difference"))
        gA, gB = {}, {}
        for d in dims:
            for t in taus:
                ga = np.mean([gap("A", d, sg, t)[2] for sg in sigmas])
                gb = np.mean([gap("B", d, r, t)[2] for r in rs])
                gA[(d, t)] = ga; gB[(d, t)] = gb
                print("  {:>5} {:>7g} {:>18.4f} {:>18.4f} {:>14.4f}".format(
                    d, t, ga, gb, gb - ga))
        small_A = all(abs(gA[(d, t)]) < GAP_RULE for d in dims for t in taus)
        grows_B = all(gB[(dims[-1], t)] > gB[(dims[0], t)] for t in taus)
        print("\n  matched-sigma gap below {:.2f} everywhere : {}".format(GAP_RULE, small_A))
        print("  matched-r gap grows with dimension        : {}".format(grows_B))
        if small_A and grows_B:
            v = ("NOISE MAGNITUDE — the Phase 8 anisotropic result is an artefact of "
                 "matched r handing anisotropic sqrt(d) times the noise")
        elif not small_A and gA[(dims[-1], taus[0])] > gA[(dims[0], taus[0])]:
            v = ("DIFFUSION STRUCTURE — the gap persists at equal noise and grows "
                 "with dimension")
        elif not small_A and gA[(dims[-1], taus[0])] < 0:
            v = ("REVERSED — anisotropic is better at equal noise and worse only "
                 "because its condition permits more of it")
        else:
            v = "MIXED — report both arms and claim neither mechanism"
        print("  VERDICT: {}".format(v))

    print("\n" + "-" * 88)
    print("P9.4 — tolerance and multiplicity sensitivity")
    print("-" * 88)
    print("  {:<6} {:<14} {:>14} {:>14} {:>14} {:>18}".format(
        "arm", "diffusion", "tol 0.10", "tol 0.15", "tol 0.20", "tol 0.15 Bonferroni"))
    for arm in arms:
        for diff in diffs:
            ks = [k for k in rec if k[0] == arm and k[1] == diff]
            c = [sum(1 for k in ks if rec[k]["hi"] <= -1.0 + tol) for tol in TOLS]
            nbf = sum(1 for k in ks if rec[k]["bhi"] <= THRESH)
            print("  {:<6} {:<14} {:>14} {:>14} {:>14} {:>18}".format(
                arm, diff, "{}/{}".format(c[0], len(ks)), "{}/{}".format(c[1], len(ks)),
                "{}/{}".format(c[2], len(ks)), "{}/{}".format(nbf, len(ks))))

    print("\n" + "-" * 88)
    print("P9.5 — concentration trajectory, the three ESS quantities")
    print("-" * 88)
    print("  Phase 8 found taubar/tau0 falling from 3.24 to 0.97 as isotropic r rose")
    print("  to 0.99 at d = 40: the condition governs the concentration dynamics even")
    print("  though it does not move the observable rate. Repeated here.\n")
    print("  {:<6} {:<14} {:>5} {:>9} {:>10} {:>12} {:>12}".format(
        "arm", "diffusion", "d", "level", "tau_0", "tau_bar", "ratio"))
    for arm in arms:
        levels = sigmas if arm == "A" else rs
        for diff in diffs:
            for d in dims:
                for lvl in (levels[0], levels[-1]):
                    ks = [(arm, diff, o, d, lvl, 0.1) for o in objs
                          if (arm, diff, o, d, lvl, 0.1) in rec]
                    if not ks:
                        continue
                    t0v = np.mean([rec[k]["tau0"] for k in ks])
                    tbv = np.mean([rec[k]["taubar"] for k in ks])
                    print("  {:<6} {:<14} {:>5} {:>9g} {:>10.4f} {:>12.4f} {:>12.2f}".format(
                        arm, diff, d, lvl, t0v, tbv, tbv / t0v if t0v > 0 else float("nan")))

    print("\n" + "=" * 88)
    print("wrote crossed_raw.csv and crossed_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 88)


if __name__ == "__main__":
    main()
