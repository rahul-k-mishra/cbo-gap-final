"""
cliff.py  —  CBO-GAP Phase 10: is the parameter condition a cliff, and where?

WHAT THIS IS FIXING
-------------------
Phase 8 walked r = d*sigma^2/(2*lambda) from 0.1 to 0.99 and found the fitted
exponent essentially unmoved: regression coefficients of slope on r ranged from
-0.057 to +0.052 across every diffusion type, dimension and concentration
target, all inside the measured noise floor of 0.055. The conclusion drawn from
that run was that the condition 2*lambda > d*sigma^2 is a proof device rather
than an operating limit.

Phase 9 then produced, incidentally and in only two cells, this:

    d = 40, sigma = 0.4, isotropic, r = 3.20  ->  slope -0.507 (tau = 0.1)
                                                 slope -0.348 (tau = 0.01)

against roughly -0.97 to -1.06 in every cell with r < 1. The concentration
diagnostic in the same cells gives a time-averaged to initial ESS ratio of 0.03,
against 1.1 to 3.5 everywhere inside the condition: the ensemble never
concentrates because the noise overwhelms the drift.

So the Phase 8 conclusion was wrong, and wrong in an instructive way. The
condition is not a gradient that Phase 8 failed to detect. It appears to be a
cliff, and Phase 8 stopped at r = 0.99, just short of the edge.

That is currently supported by two cells at one value of r, one dimension and
one sigma. This script turns it into a curve or kills it.

WHAT IS MEASURED
----------------
r is swept from well inside the condition to well outside:

    r in {0.5, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0}

with sigma solved per (diffusion, d) so that each system sits at the prescribed
multiple of its OWN limit: r = d*sigma^2/(2*lambda) for isotropic and
r = sigma^2/(2*lambda) for anisotropic. Both diffusion types are run, because
the anisotropic condition is dimension-free and if the cliff is a property of
the condition rather than of the dimension then anisotropic should fall off the
same edge at the same r regardless of d. That is a sharp, falsifiable prediction
and it is the reason both types are here.

r = 1.0 is included exactly. If the cliff is real and sharp, the interesting
question is whether the collapse begins at r = 1 or somewhat past it, and no
grid that omits the boundary itself can answer that.

PRE-REGISTERED, fixed before the first run
-------------------------------------------
  delta = -1 - slope_hat. RATE-CONSISTENT AT TOLERANCE 0.15 iff the bootstrap
  95 percent upper bound is at or below -0.85. The proven exponent is -1 and a
  slope of -0.85 is never called that rate. Counts are reported at tolerances
  0.10, 0.15 and 0.20, and with Bonferroni-adjusted intervals, because Phase 9
  showed the count moving from 30 to 52 of 72 across that range and losing nine
  more cells to multiplicity.

  Bootstrap unit: the independent coupled realisation, all J values kept
  together, slope refitted per resample, 400 resamples, percentile, seed 7.

  A CLIFF IS ESTABLISHED iff, for each diffusion type, the mean slope over
  objectives satisfies all three of:
    (i)  it is within 0.10 of its r = 0.5 value at every r <= 1.0;
    (ii) it is flatter than that value by at least 0.30 at r = 5.0;
    (iii) the transition is monotone in r over the grid, to within the noise
          floor measured from this run's own replicates.
  If (i) holds and (ii) does not, there is no cliff on this grid and the
  Phase 8 reading stands. If (i) fails, the degradation begins inside the
  condition and both earlier readings are wrong.

  THE MECHANISM CLAIM is separate and is tested separately: the collapse, if
  present, should be accompanied by the time-averaged to initial ESS ratio
  falling below 1. Slope and concentration are reported side by side so that
  the mechanism is not asserted from the slope alone.

  NO OUT-OF-CONDITION CELL ENTERS ANY AGGREGATE VERDICT unless the verdict is
  explicitly about out-of-condition behaviour. Phase 9's automated verdict fired
  REVERSED because two cells at r = 3.2, kept deliberately, were allowed into a
  mean that was supposed to describe in-condition behaviour. Every table below
  marks in and out explicitly and no statistic mixes them silently.

WHAT THIS CANNOT SETTLE
-----------------------
Outside the condition, FKR Theorem 3.7 says nothing, so a collapse there is not
evidence against any theorem. It would show only that the condition tracks
something the run does, which is a statement about the sharpness of a sufficient
condition and not about its necessity. Necessity would require showing the rate
holds wherever the condition holds, which no finite grid can do.

The estimator remains the coupled distance to a reference ensemble of 50000,
not the mean-field limit. Horizon fixed at T = 1. Initial law centred.

HOW TO RUN
----------
    python cliff.py --workers 3 --quick     (smoke test, ~4 min)
    python cliff.py --workers 3             (full, budget 1.5-2 h)

NumPy only. No SciPy. Python 3.8 compatible.
Writes cliff_raw.csv and cliff_summary.csv.
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
FLAT_TOL = 0.10      # criterion (i)
DROP_MIN = 0.30      # criterion (ii)


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
    return math.sqrt(2.0 * lam * r / (d if diff == "isotropic" else 1.0))


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
    # spread of the reference cloud at the final time: a direct check on
    # whether the ensemble concentrated at all
    spread = float(np.mean(np.linalg.norm(Xref - Xref.mean(axis=0), axis=1)))
    return ({J: float(np.mean(runmax[J])) for J in J_list},
            float(les[0]), float(les.mean()), float(les.min()), spread)


def task(a):
    (name, d, diff, r, tau, beta, sigma, lam, dt, K, Jinf, J_list, seed) = a
    per_J, l0, lm, lmin, sp = one_realisation(name, d, diff, beta, sigma, lam,
                                              dt, K, Jinf, J_list, seed)
    return name, d, diff, r, tau, beta, sigma, per_J, l0, lm, lmin, sp


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
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=12)
    p.add_argument("--lam", type=float, default=1.0)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260828)
    args = p.parse_args()

    K = int(round(args.T / args.dt))
    M = 3 if args.quick else args.realisations
    diffs = ["isotropic", "anisotropic"]

    if args.quick:
        Jinf, Jgrid = 4000, [10, 40, 160, 400]
        objs, dims = ["ackley", "rosenbrock"], [10]
        rs, taus = [0.5, 1.0, 3.0], [0.1]
    else:
        Jinf, Jgrid = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        objs = ["ackley", "rastrigin", "sphere", "rosenbrock"]
        dims = [10, 40]
        rs = [0.5, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0]
        taus = [0.1]
    J_list = [J for J in Jgrid if J <= Jinf // 10]

    print("=" * 88)
    print("CBO-GAP Phase 10 — is the parameter condition a cliff?")
    print("=" * 88)
    print("  PRE-REGISTERED (fixed before the first run):")
    print("    RATE-CONSISTENT AT TOLERANCE {:.2f} iff bootstrap 95% upper bound <= {:+.2f}.".format(TOL, THRESH))
    print("    CLIFF ESTABLISHED iff, per diffusion type: (i) mean slope within")
    print("    {:.2f} of its r=0.5 value at every r <= 1.0; (ii) flatter by at least".format(FLAT_TOL))
    print("    {:.2f} at r = 5.0; (iii) monotone in r to within the measured noise floor.".format(DROP_MIN))
    print("    Mechanism tested separately: collapse should coincide with the")
    print("    time-averaged to initial ESS ratio falling below 1.")
    print("    No out-of-condition cell enters any in-condition aggregate. Phase 9's")
    print("    automated verdict fired on exactly that mistake.")
    print("\n  REPRODUCIBILITY")
    print("    python {}   numpy {}".format(platform.python_version(), np.__version__))
    print("    platform {}   workers {}".format(platform.platform(), args.workers))
    print("    base seed {}   J grid {}".format(args.seed, J_list))
    print("    Jinf {}   realisations/cell {}   lambda {}   dt {}   T {}   steps {}".format(
        Jinf, M, args.lam, args.dt, args.T, K))

    ncell = len(diffs) * len(objs) * len(dims) * len(rs) * len(taus)
    print("\n  EXPERIMENT MATRIX")
    print("    2 diffusions x {} objectives x {} dims x {} r x {} tau = {} cells".format(
        len(objs), len(dims), len(rs), len(taus), ncell))
    print("    {} cells x {} realisations = {} coupled realisations".format(
        ncell, M, ncell * M))

    print("\n  sigma at each (diffusion, d, r); r > 1 is outside the condition")
    print("  {:<12} {:>4}".format("diffusion", "d") +
          "".join("{:>9}".format("r=" + str(r)) for r in rs))
    for diff in diffs:
        for d in dims:
            print("  {:<12} {:>4}".format(diff, d) +
                  "".join("{:>9.3f}".format(sigma_of(diff, d, r, args.lam)) for r in rs))
    print("\n  Note that the anisotropic sigma does not depend on d: if the cliff is")
    print("  a property of the condition, anisotropic should fall off it at the same")
    print("  r at both dimensions. That is the falsifiable part of this run.")

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
    for name, d, diff, r, t, b, sg, per_J, l0, lm, lmin, sp in res:
        k = (diff, name, d, r, t)
        if k not in agg:
            agg[k] = {"beta": b, "sigma": sg, "E": {J: [] for J in J_list},
                      "l0": [], "lm": [], "lmin": [], "sp": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        for key, val in (("l0", l0), ("lm", lm), ("lmin", lmin), ("sp", sp)):
            agg[k][key].append(val)

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
        rec[k] = dict(slope=sl, lo=lo, hi=hi, blo=blo, bhi=bhi, sigma=rr["sigma"],
                      tau0=f0, taubar=fm, taumin=fmn, spread=float(np.mean(rr["sp"])))
        rows.append([k[0], k[1], k[2], k[3], k[4], "{:.6g}".format(rr["sigma"]),
                     "{:.6g}".format(rr["beta"]), "in" if k[3] < 1 else "out",
                     "{:.6f}".format(sl), "{:.6f}".format(-1.0 - sl),
                     "{:.6f}".format(lo), "{:.6f}".format(hi),
                     "{:.6f}".format(blo), "{:.6f}".format(bhi),
                     "{:.6g}".format(f0), "{:.6g}".format(fm), "{:.6g}".format(fmn),
                     "{:.6g}".format(np.mean(rr["sp"])),
                     "rate-consistent" if hi <= THRESH else "not rate-consistent"])

    with open("cliff_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["diffusion", "objective", "d", "r", "tau", "sigma", "beta",
                    "region", "J", "Ehat", "stderr", "tau0", "taubar", "taumin",
                    "final_spread", "realisations"])
        for k in sorted(agg):
            rr = agg[k]
            f0 = math.exp(min(float(np.mean(rr["l0"])), 700)) / Jinf
            fm = math.exp(min(float(np.mean(rr["lm"])), 700)) / Jinf
            fmn = math.exp(min(float(np.mean(rr["lmin"])), 700)) / Jinf
            for J in J_list:
                v = np.array(rr["E"][J])
                w.writerow([k[0], k[1], k[2], k[3], k[4], "{:.6g}".format(rr["sigma"]),
                            "{:.6g}".format(rr["beta"]), "in" if k[3] < 1 else "out",
                            J, "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.6g}".format(f0), "{:.6g}".format(fm),
                            "{:.6g}".format(fmn),
                            "{:.6g}".format(np.mean(rr["sp"])), len(v)])
    with open("cliff_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["diffusion", "objective", "d", "r", "tau", "sigma", "beta",
                    "region", "slope", "delta", "ci_lo", "ci_hi", "bonf_lo",
                    "bonf_hi", "tau0", "taubar", "taumin", "final_spread", "verdict"])
        w.writerows(rows)

    def ms(diff, d, r, t=taus[0]):
        return float(np.mean([rec[(diff, o, d, r, t)]["slope"] for o in objs]))

    # noise floor from this run: spread of slope over the three smallest r,
    # where the earlier phases found it flat
    floors = [max(ms(diff, d, r) for r in rs[:3]) - min(ms(diff, d, r) for r in rs[:3])
              for diff in diffs for d in dims]
    floor = float(np.median(floors))

    print("\n" + "-" * 88)
    print("P10.1 — the slope across and beyond the condition")
    print("-" * 88)
    print("  measured noise floor from this run (spread over r = {}): {:.4f}\n".format(
        rs[:3], floor))
    for diff in diffs:
        print("  {}".format(diff))
        print("    {:>4}".format("d") + "".join("{:>9}".format(r) for r in rs))
        for d in dims:
            print("    {:>4}".format(d) + "".join(
                "{:>9}".format("{:+.3f}".format(ms(diff, d, r))) for r in rs))
        print("    {:>4}".format("") + "".join(
            "{:>9}".format("in" if r < 1 else "OUT") for r in rs))
        print()

    print("-" * 88)
    print("P10.2 — the pre-registered cliff test")
    print("-" * 88)
    for diff in diffs:
        for d in dims:
            base = ms(diff, d, rs[0])
            inside = [r for r in rs if r <= 1.0]
            i_ok = all(abs(ms(diff, d, r) - base) <= FLAT_TOL for r in inside)
            drop = ms(diff, d, rs[-1]) - base
            ii_ok = drop >= DROP_MIN
            seq = [ms(diff, d, r) for r in rs]
            iii_ok = all(seq[i + 1] >= seq[i] - floor for i in range(len(seq) - 1))
            v = ("CLIFF" if (i_ok and ii_ok and iii_ok) else
                 ("no cliff on this grid" if i_ok and not ii_ok else
                  "degradation begins INSIDE the condition" if not i_ok else
                  "collapse present but not monotone"))
            print("  {:<12} d={:<4} flat inside {:<6} drop at r=5 {:+.3f} {:<6} monotone {:<6} -> {}".format(
                diff, d, str(i_ok), drop, str(ii_ok), str(iii_ok), v))

    print("\n" + "-" * 88)
    print("P10.3 — mechanism: concentration and cloud spread alongside the slope")
    print("-" * 88)
    print("  A collapse driven by the noise overwhelming the drift should show the")
    print("  ESS ratio falling below 1 and the final cloud spread growing.\n")
    print("  {:<12} {:>4} {:>7} {:>6} {:>10} {:>12} {:>14}".format(
        "diffusion", "d", "r", "reg", "slope", "taubar/tau0", "final spread"))
    for diff in diffs:
        for d in dims:
            for r in rs:
                ks = [(diff, o, d, r, taus[0]) for o in objs]
                t0v = np.mean([rec[k]["tau0"] for k in ks])
                tbv = np.mean([rec[k]["taubar"] for k in ks])
                spv = np.mean([rec[k]["spread"] for k in ks])
                print("  {:<12} {:>4} {:>7g} {:>6} {:>10.4f} {:>12.3f} {:>14.4g}".format(
                    diff, d, r, "in" if r < 1 else "OUT", ms(diff, d, r),
                    tbv / t0v if t0v > 0 else float("nan"), spv))

    print("\n" + "-" * 88)
    print("P10.4 — tolerance and multiplicity, split by region")
    print("-" * 88)
    print("  {:<12} {:>6} {:>12} {:>12} {:>12} {:>18}".format(
        "diffusion", "region", "tol 0.10", "tol 0.15", "tol 0.20", "tol 0.15 Bonferroni"))
    for diff in diffs:
        for reg in ("in", "out"):
            ks = [k for k in rec if k[0] == diff and
                  ((k[3] < 1) == (reg == "in"))]
            if not ks:
                continue
            c = [sum(1 for k in ks if rec[k]["hi"] <= -1.0 + tol) for tol in TOLS]
            nbf = sum(1 for k in ks if rec[k]["bhi"] <= THRESH)
            print("  {:<12} {:>6} {:>12} {:>12} {:>12} {:>18}".format(
                diff, reg, "{}/{}".format(c[0], len(ks)),
                "{}/{}".format(c[1], len(ks)), "{}/{}".format(c[2], len(ks)),
                "{}/{}".format(nbf, len(ks))))

    print("\n  Outside the condition FKR Theorem 3.7 says nothing, so failures there")
    print("  are not evidence against any theorem. They show only that the")
    print("  sufficient condition tracks something the run does.")

    print("\n" + "=" * 88)
    print("wrote cliff_raw.csv and cliff_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 88)


if __name__ == "__main__":
    main()
