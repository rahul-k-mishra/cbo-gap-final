"""
sigma.py  —  CBO-GAP Phase 8: the parameter boundary, and the anisotropic claim

WHY THIS SCRIPT EXISTS
----------------------
A referee identified two gaps in the manuscript that are not matters of wording.

  GAP 1 — the condition 2*lambda > d*sigma^2 is derived and never tested.
      Section 4.2 of the manuscript shows that the constant c(theta,lambda,sigma)
      of FKR Eq. (56) vanishes as d*sigma^2 rises to 2*lambda, and that alpha_0
      is proportional to c^{-2}, so alpha_0 diverges like (2*lambda - d*sigma^2)^{-2}
      at the boundary. Every experiment so far held sigma = 1/5 and stopped at
      d = 40, where d*sigma^2 = 1.6 against 2*lambda = 2. The interesting region
      was never entered. This is the one analytic claim in the paper with no
      measurement behind it.

  GAP 2 — the anisotropic comparison rests on one data point.
      The manuscript reports isotropic -0.868 against anisotropic -0.877 at
      d = 10, beta = 3, and concludes there is no evidence the choice matters.
      That is one comparison. It matters more than it looks: for anisotropic
      diffusion the corresponding stability condition is dimension-free,
      2*lambda > sigma^2 rather than 2*lambda > d*sigma^2, which is why
      anisotropic noise is recommended for high-dimensional problems. If recent
      work reports a dimension-independent prefactor in the anisotropic case,
      a one-point comparison is not an adequate answer.

THE CONTROL VARIABLE
--------------------
Both gaps are the same experiment once the right variable is used. Define

    r = d*sigma^2 / (2*lambda)      for isotropic diffusion
    r =   sigma^2 / (2*lambda)      for anisotropic diffusion

so that r = 1 is the boundary of the parameter condition in each case, and
sigma is solved for at each (d, r). Sweeping r from 0.1 to 0.99 walks up to the
boundary from below, in both diffusion types, at matched distance from it.

This is the honest comparison. Comparing the two diffusion types at a common
sigma would confound the diffusion structure with how close each is to its own
stability limit — at sigma = 1/5 and d = 40 the isotropic system sits at r = 0.8
while the anisotropic system sits at r = 0.02, which is not a comparison of
diffusion structure at all.

Concentration is held fixed by bisection on beta, as in the earlier phases, so
that anything found here is not the concentration effect in disguise.

PRE-REGISTERED, fixed before this script was first run
-------------------------------------------------------
  delta = -1 - slope_hat. A cell is RATE-CONSISTENT AT TOLERANCE 0.15 when the
  upper end of the bootstrap 95 percent interval is at or below -0.85. The
  proven exponent is -1 and a slope of -0.85 is never described as that rate.

  BOOTSTRAP: the resampling unit is the independent coupled realisation. All J
  values within a realisation are kept together, the slope is refitted on each
  resample, 400 resamples, percentile interval, seed fixed at 7. This was left
  unspecified in the manuscript and the referee was right to ask.

  MULTIPLE TESTING: the criterion is applied per cell and no familywise error
  guarantee is claimed. Bonferroni-adjusted intervals are reported alongside as
  a sensitivity check, not as the headline.

  TOLERANCE SENSITIVITY: counts are reported at tolerances 0.10, 0.15 and 0.20.
  The 0.15 value is arbitrary and its consequences should be visible.

  PREDICTION, recorded before the run: if the parameter condition governs
  observability, isotropic rate-consistency should fall as r rises toward 1,
  and anisotropic should not degrade with dimension at matched r. If neither
  happens, the condition is a proof device rather than an operating limit, and
  that is a reportable result.

WHAT THIS SCRIPT DOES NOT DO
----------------------------
It does not measure the end-to-end optimization error; the estimator is the
coupled distance between a finite ensemble and a large reference ensemble. The
reference is a proxy at 50000, not the mean-field limit. The horizon is fixed
at T = 1. The initial law is centred at the minimizer.

HOW TO RUN
----------
    python sigma.py --workers 3 --quick        (smoke test, ~4 min)
    python sigma.py --workers 3                (full, budget 5-6 h)
    python sigma.py --workers 3 --part iso     (isotropic only, ~2.5-3 h)
    python sigma.py --workers 3 --part aniso   (anisotropic only)

NumPy only. No SciPy. Python 3.8 compatible.
Writes sigma_raw.csv and sigma_summary.csv.
"""

import argparse
import csv
import math
import os
import platform
import sys
import time
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

TOLS = [0.10, 0.15, 0.20]
TOL = 0.15
THRESH = -1.0 + TOL          # -0.85
N_BOOT = 400
BOOT_SEED = 7


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


def sigma_of(diff, d, r, lam=1.0):
    """Solve for sigma at a prescribed distance r from the parameter boundary.
    Isotropic: 2*lambda > d*sigma^2, so r = d*sigma^2/(2*lambda).
    Anisotropic: the corresponding condition is dimension-free, r = sigma^2/(2*lambda)."""
    if diff == "isotropic":
        return math.sqrt(2.0 * lam * r / d)
    return math.sqrt(2.0 * lam * r)


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
        if diff == "isotropic":
            noise = sigma * np.linalg.norm(dv, axis=1)[:, None] * dW
        else:
            noise = sigma * dv * dW
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
    (name, d, diff, r, tau, beta, sigma, lam, dt, K, Jinf, J_list, seed) = a
    per_J, l0, lm, lmin = one_realisation(name, d, diff, beta, sigma, lam,
                                          dt, K, Jinf, J_list, seed)
    return name, d, diff, r, tau, beta, sigma, per_J, l0, lm, lmin


def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def boot_ci(per_real, J_list, level=95.0):
    """Resampling unit is the independent coupled realisation; all J values
    within a realisation move together, and the slope is refitted per resample."""
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
    p.add_argument("--part", default="both", help="iso, aniso, or both")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=12)
    p.add_argument("--lam", type=float, default=1.0)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260826)
    args = p.parse_args()

    K = int(round(args.T / args.dt))
    M = 3 if args.quick else args.realisations

    if args.quick:
        Jinf, Jgrid = 4000, [10, 40, 160, 400]
        objs, dims = ["ackley", "rosenbrock"], [10]
        rs, taus = [0.1, 0.9], [0.1]
    else:
        Jinf, Jgrid = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        objs = ["ackley", "rastrigin", "sphere", "rosenbrock"]
        dims = [5, 10, 40]
        rs = [0.1, 0.25, 0.5, 0.75, 0.9, 0.99]
        taus = [0.1, 0.01]
    J_list = [J for J in Jgrid if J <= Jinf // 10]
    diffs = {"iso": ["isotropic"], "aniso": ["anisotropic"],
             "both": ["isotropic", "anisotropic"]}[args.part]

    print("=" * 86)
    print("CBO-GAP Phase 8 — the parameter boundary and the anisotropic comparison")
    print("=" * 86)
    print("  PRE-REGISTERED (fixed before the first run):")
    print("    delta = -1 - slope. RATE-CONSISTENT AT TOLERANCE {:.2f} iff the".format(TOL))
    print("    bootstrap 95% upper bound is at or below {:+.2f}.".format(THRESH))
    print("    Bootstrap unit: the independent coupled realisation, all J kept")
    print("    together, slope refitted per resample, {} resamples, percentile".format(N_BOOT))
    print("    interval, seed {}.".format(BOOT_SEED))
    print("    Criterion applied PER CELL. No familywise guarantee is claimed;")
    print("    Bonferroni-adjusted intervals are reported as a sensitivity check.")
    print("    Counts also reported at tolerances {}.".format(TOLS))
    print("\n  REPRODUCIBILITY")
    print("    python {}   numpy {}".format(platform.python_version(), np.__version__))
    print("    platform {}   workers {}".format(platform.platform(), args.workers))
    print("    base seed {}   J grid {}".format(args.seed, J_list))
    print("    Jinf {}   realisations/cell {}   lambda {}   dt {}   T {}   steps {}".format(
        Jinf, M, args.lam, args.dt, args.T, K))

    print("\n  EXPERIMENT MATRIX")
    ncell = len(diffs) * len(objs) * len(dims) * len(rs) * len(taus)
    print("    diffusion {} x objectives {} x dimensions {} x r {} x tau {} = {} cells".format(
        len(diffs), len(objs), len(dims), len(rs), len(taus), ncell))
    print("    {} cells x {} realisations = {} coupled realisations".format(
        ncell, M, ncell * M))

    print("\n  sigma solved at each (diffusion, d, r); r = 1 is the boundary")
    print("  {:<12} {:>4}".format("diffusion", "d") +
          "".join("{:>12}".format("r=" + str(r)) for r in rs))
    for diff in diffs:
        for d in dims:
            print("  {:<12} {:>4}".format(diff, d) +
                  "".join("{:>12.4f}".format(sigma_of(diff, d, r, args.lam)) for r in rs))
    print("\n  Note the contrast: at sigma = 1/5 and d = 40 the isotropic system sits")
    print("  at r = 0.80 while the anisotropic sits at r = 0.02. Comparing the two")
    print("  at a common sigma compares systems at very different distances from")
    print("  their own stability limits, which is why r is the control here.")

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
    for diff in diffs:
        for name in objs:
            for d in dims:
                for r in rs:
                    sg = sigma_of(diff, d, r, args.lam)
                    for t in taus:
                        for _ in range(M):
                            s += 1
                            tasks.append((name, d, diff, r, t, beta[(name, d, t)],
                                          sg, args.lam, args.dt, K, Jinf, J_list, s))

    print("\n  {} realisations queued on {} workers\n".format(len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    agg = {}
    for name, d, diff, r, t, b, sg, per_J, l0, lm, lmin in res:
        k = (diff, name, d, r, t)
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
        fmin = math.exp(min(float(np.mean(rr["lmin"])), 700)) / Jinf
        rec[k] = dict(slope=sl, lo=lo, hi=hi, blo=blo, bhi=bhi,
                      tau0=f0, taubar=fm, taumin=fmin,
                      beta=rr["beta"], sigma=rr["sigma"])
        rows.append([k[0], k[1], k[2], k[3], k[4], "{:.6g}".format(rr["sigma"]),
                     "{:.6g}".format(rr["beta"]), "{:.6f}".format(sl),
                     "{:.6f}".format(-1.0 - sl), "{:.6f}".format(lo),
                     "{:.6f}".format(hi), "{:.6f}".format(blo), "{:.6f}".format(bhi),
                     "{:.6g}".format(f0), "{:.6g}".format(fm), "{:.6g}".format(fmin),
                     "rate-consistent" if hi <= THRESH else "not rate-consistent"])

    with open("sigma_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["diffusion", "objective", "d", "r", "tau", "sigma", "beta",
                    "J", "Ehat", "stderr", "tau0", "taubar", "taumin", "realisations"])
        for k in sorted(agg):
            rr = agg[k]
            f0 = math.exp(min(float(np.mean(rr["l0"])), 700)) / Jinf
            fm = math.exp(min(float(np.mean(rr["lm"])), 700)) / Jinf
            fmin = math.exp(min(float(np.mean(rr["lmin"])), 700)) / Jinf
            for J in J_list:
                v = np.array(rr["E"][J])
                w.writerow([k[0], k[1], k[2], k[3], k[4], "{:.6g}".format(rr["sigma"]),
                            "{:.6g}".format(rr["beta"]), J, "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.6g}".format(f0), "{:.6g}".format(fm),
                            "{:.6g}".format(fmin), len(v)])
    with open("sigma_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["diffusion", "objective", "d", "r", "tau", "sigma", "beta",
                    "slope", "delta", "ci_lo", "ci_hi", "bonf_lo", "bonf_hi",
                    "tau0", "taubar", "taumin", "verdict"])
        w.writerows(rows)

    print("\n" + "-" * 86)
    print("P8.1 — walking up to the parameter boundary")
    print("-" * 86)
    print("  Mean fitted slope over the {} objectives, by r. r = 1 is the".format(len(objs)))
    print("  boundary of the condition in each diffusion type.\n")
    for diff in diffs:
        for t in taus:
            print("  {} , tau = {:g}".format(diff, t))
            print("    {:>5}".format("d") + "".join("{:>12}".format("r=" + str(r)) for r in rs))
            for d in dims:
                line = "    {:>5}".format(d)
                for r in rs:
                    v = [rec[(diff, o, d, r, t)]["slope"] for o in objs]
                    bad = sum(1 for o in objs if rec[(diff, o, d, r, t)]["hi"] > THRESH)
                    line += "{:>12}".format("{:+.3f}{}".format(np.mean(v), "*" * min(bad, 3)))
                print(line)
            print()
    print("  * marks objectives in that cell that are not rate-consistent.")
    print("  If the condition is an operating limit, the isotropic rows should")
    print("  degrade from left to right. If they do not, it is a proof device.")

    print("\n" + "-" * 86)
    print("P8.2 — isotropic against anisotropic at matched distance from the boundary")
    print("-" * 86)
    if len(diffs) == 2:
        print("  {:>5} {:>7} {:>7} {:>12} {:>12} {:>10}".format(
            "d", "r", "tau", "isotropic", "anisotropic", "gap"))
        for d in dims:
            for r in rs:
                for t in taus:
                    a = np.mean([rec[("isotropic", o, d, r, t)]["slope"] for o in objs])
                    b = np.mean([rec[("anisotropic", o, d, r, t)]["slope"] for o in objs])
                    print("  {:>5} {:>7g} {:>7g} {:>12.4f} {:>12.4f} {:>10.4f}".format(
                        d, r, t, a, b, abs(a - b)))
        print("\n  The manuscript currently rests this comparison on one data point.")
        print("  A dimension-dependent gap here would bear directly on the claim")
        print("  that anisotropic noise carries a dimension-free prefactor.")
    else:
        print("  run with --part both for this comparison")

    print("\n" + "-" * 86)
    print("P8.3 — sensitivity of the verdict to the tolerance, and to multiplicity")
    print("-" * 86)
    print("  The tolerance 0.15 is arbitrary. Counts at three tolerances, and")
    print("  with Bonferroni-adjusted intervals over all {} cells:\n".format(nb))
    print("  {:<14} {:>16} {:>16} {:>16} {:>20}".format(
        "diffusion", "tol 0.10", "tol 0.15", "tol 0.20", "tol 0.15 Bonferroni"))
    for diff in diffs:
        ks = [k for k in rec if k[0] == diff]
        cells = []
        for tol in TOLS:
            th = -1.0 + tol
            cells.append(sum(1 for k in ks if rec[k]["hi"] <= th))
        nbf = sum(1 for k in ks if rec[k]["bhi"] <= THRESH)
        print("  {:<14} {:>16} {:>16} {:>16} {:>20}".format(
            diff, "{}/{}".format(cells[0], len(ks)), "{}/{}".format(cells[1], len(ks)),
            "{}/{}".format(cells[2], len(ks)), "{}/{}".format(nbf, len(ks))))

    print("\n" + "-" * 86)
    print("P8.4 — the three ESS quantities, kept separate")
    print("-" * 86)
    print("  The manuscript used one symbol for three things. Initial, time-averaged")
    print("  and minimum ESS fraction, averaged over objectives, at tau target 0.1:\n")
    print("  {:<14} {:>5} {:>7} {:>12} {:>14} {:>12}".format(
        "diffusion", "d", "r", "tau_0", "tau_bar", "tau_min"))
    for diff in diffs:
        for d in dims:
            for r in (rs[0], rs[-1]):
                ks = [(diff, o, d, r, 0.1) for o in objs if (diff, o, d, r, 0.1) in rec]
                if not ks:
                    continue
                print("  {:<14} {:>5} {:>7g} {:>12.4f} {:>14.4f} {:>12.4f}".format(
                    diff, d, r,
                    np.mean([rec[k]["tau0"] for k in ks]),
                    np.mean([rec[k]["taubar"] for k in ks]),
                    np.mean([rec[k]["taumin"] for k in ks])))

    print("\n" + "=" * 86)
    print("wrote sigma_raw.csv and sigma_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 86)


if __name__ == "__main__":
    main()
