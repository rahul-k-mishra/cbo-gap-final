"""
ess_surface.py  —  CBO-GAP Phase 1: the (beta, d, J) mean-field surface

WHAT THIS SCRIPT IS FOR, IN PLAIN LANGUAGE
------------------------------------------
Gerber, Hoffmann and Vaes prove that the CBO particle system converges to its
mean-field limit at rate J^(-1/2) in the norm, i.e. J^(-1) for the squared
error. They verify it numerically at exactly ONE parameter point: d = 2,
beta = 3, T = 1, with a reference run of a million particles. They then state
that the roles of the dimension and the other problem parameters in the
constant prefactor are left for future work.

Nobody has mapped the surface. This script maps it.

  P1.1 — THE SURFACE.
      What we compute: for each (objective, diffusion, beta, d), the error
      Ehat(J) between a J-particle run and a large-Jinf reference run that
      shares its initial positions and its Brownian paths. Then the slope of
      log Ehat against log J.
      What the result means: slope near -1 means the Monte Carlo rate is
      actually observed there. A flatter slope means the rate the theory
      promises is not visible at that parameter point.

  P1.2 — THE BETA THRESHOLD.
      What we compute: the largest beta, per dimension, at which the slope is
      still recovered.
      What the result means: this is the honest end of the measurable range.
      Above it the weighted mean is the arg min, the effective sample size is
      one, and no amount of extra particles produces Monte Carlo behaviour.
      FKR's own figures run at alpha = 1e15. GHV verify the rate at beta = 3.
      This number is what sits between them.

  P1.3 — ESS AS PREDICTOR.
      What we compute: the smallest effective sample size reached during each
      run, alongside the slope.
      What the result means: if low ESS predicts slope breakdown better than
      beta or d alone, ESS is a usable diagnostic and that is a constructive
      contribution rather than a complaint. If it adds nothing, we report the
      null and drop the claim.

  P1.4 — ANISOTROPIC CONFIRMATION.
      Same sweep on fewer points with componentwise noise. This is the version
      practitioners actually run in high dimension, and running only isotropic
      invites the referee objection that we tested a variant nobody uses.

THREE LIMITS YOU MUST READ BEFORE TRUSTING ANY NUMBER
-----------------------------------------------------
1. The reference run is NOT the mean-field limit. It is a large-J proxy, so
   every Ehat(J) carries a bias that does not show up in its own error bars.
   The only defence is to never quote a J close to Jinf. This script refuses
   any J above Jinf/10 and says so.

2. Large beta cannot be reached in floating point. Once beta times the range
   of the objective exceeds roughly 700, every Boltzmann weight except the
   smallest underflows to zero, the weighted mean becomes exactly the arg min,
   and ESS is exactly 1. That is not a bug and not a rate result — it is the
   hardmin regime, and rows that hit it are flagged SATURATED. They must be
   reported as "no Monte Carlo regime exists here", never as a measured slope.

3. The theory this is being compared against requires 2*lambda > d*sigma^2.
   Any row that violates it is outside FKR's own hypothesis and must be
   dropped from the paper, not explained away. The script checks and flags it.

HOW TO RUN
----------
    python ess_surface.py --workers 3 --quick     (smoke test, ~2 minutes)
    python ess_surface.py --workers 3             (the real sweep)

NumPy only. No SciPy. Python 3.8 compatible.
Writes ess_surface_raw.csv and ess_surface_summary.csv in the working folder.
"""

import argparse
import csv
import math
import os
import sys
import time
from multiprocessing import Pool

# Single-threaded BLAS inside each worker. Without this, 3 processes each
# spawning their own BLAS threads oversubscribe the cores and the whole sweep
# runs slower than serial. Must precede the numpy import.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402


# ----------------------------------------------------------------------
# objectives — both have their global minimum at the origin
# ----------------------------------------------------------------------

def f_ackley(X):
    """Ackley. Bounded above and below on R^d, so it sits in A(0,0,0):
    the ell = 0 branch, which is the branch carrying exp(alpha * range)
    in FKR Eq. (77)."""
    d = X.shape[1]
    s1 = np.sqrt(np.sum(X * X, axis=1) / d)
    s2 = np.sum(np.cos(2.0 * np.pi * X), axis=1) / d
    return -20.0 * np.exp(-0.2 * s1) - np.exp(s2) + 20.0 + math.e


def f_rastrigin(X):
    """Rastrigin. Minorised by a quadratic, so A(1,2,2): the ell > 0 branch,
    where Eq. (77) gives a b2 that DECREASES in alpha. Included precisely so
    the two branches can be compared under one estimator."""
    return np.sum(X * X + 10.0 * (1.0 - np.cos(2.0 * np.pi * X)), axis=1)


OBJECTIVES = {"ackley": f_ackley, "rastrigin": f_rastrigin}


# ----------------------------------------------------------------------
# weighted mean and effective sample size
# ----------------------------------------------------------------------

def weighted_mean_and_ess(X, fvals, beta):
    """
    Boltzmann-weighted mean, computed in shifted form so the largest weight is
    always exactly 1 and the denominator can never be 0/0.

    ESS = (sum w)^2 / sum(w^2), the standard effective sample size. It equals J
    when all particles contribute equally and 1 when a single particle carries
    all the weight. GHV attribute their own small-J rate breakdown to ESS near 1.
    """
    shift = fvals.min()
    w = np.exp(-beta * (fvals - shift))
    s = w.sum()
    m = (w[:, None] * X).sum(axis=0) / s
    ess = (s * s) / (w * w).sum()
    return m, float(ess)


# ----------------------------------------------------------------------
# one coupled realisation
# ----------------------------------------------------------------------

def one_realisation(objective, diffusion, beta, d, sigma, dt, K,
                    Jinf, J_list, seed):
    """
    Synchronous coupling, exactly as in GHV Subsection 2.6.

    A reference system of Jinf particles is evolved. For every J in J_list a
    smaller system of J particles is evolved alongside it, started from the
    SAME initial positions and driven by the SAME Brownian increments as the
    first J particles of the reference system. Each small system computes its
    own consensus point from its own J particles — that difference is the whole
    quantity being measured.

    Returns, per J, the mean over particles of the running-supremum squared
    distance between the two trajectories, plus the smallest ESS seen.
    """
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)

    X0 = rng.standard_normal((Jinf, d))
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}

    ess_min_ref = float(Jinf)
    ess_min_sub = {J: float(J) for J in J_list}
    sq = math.sqrt(dt)

    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq

        mref, e = weighted_mean_and_ess(Xref, f(Xref), beta)
        ess_min_ref = min(ess_min_ref, e)
        dref = Xref - mref
        if diffusion == "isotropic":
            noise = sigma * np.linalg.norm(dref, axis=1)[:, None] * dW
        else:
            noise = sigma * dref * dW
        Xref = Xref - dt * dref + noise

        for J in J_list:
            Xj = Xsub[J]
            mj, ej = weighted_mean_and_ess(Xj, f(Xj), beta)
            ess_min_sub[J] = min(ess_min_sub[J], ej)
            dj = Xj - mj
            if diffusion == "isotropic":
                nj = sigma * np.linalg.norm(dj, axis=1)[:, None] * dW[:J]
            else:
                nj = sigma * dj * dW[:J]
            Xsub[J] = Xj - dt * dj + nj

            diff = np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1)
            np.maximum(runmax[J], diff, out=runmax[J])

    out = {}
    for J in J_list:
        out[J] = (float(np.mean(runmax[J])), ess_min_sub[J])
    return out, ess_min_ref


def task(args):
    (objective, diffusion, beta, d, sigma, dt, K, Jinf, J_list, seed) = args
    t0 = time.time()
    per_J, ess_ref = one_realisation(objective, diffusion, beta, d, sigma,
                                     dt, K, Jinf, J_list, seed)
    return (objective, diffusion, beta, d, per_J, ess_ref, time.time() - t0)


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------

def fit_slope(logJ, logE):
    A = np.vstack([logJ, np.ones_like(logJ)]).T
    sol, _, _, _ = np.linalg.lstsq(A, logE, rcond=None)
    return float(sol[0])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3,
                   help="worker processes (default 3, ~75-80 percent of a 4-core box)")
    p.add_argument("--quick", action="store_true",
                   help="tiny grid for a smoke test; the numbers mean nothing")
    p.add_argument("--sigma", type=float, default=0.2,
                   help="diffusion coefficient (GHV use 1/5)")
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260817)
    args = p.parse_args()

    lam = 1.0  # drift coefficient, absorbed into the time scale as in GHV
    K = int(round(args.T / args.dt))

    if args.quick:
        Jinf = 4000
        J_list = [10, 20, 40, 80, 160, 320]
        betas = [1.0, 10.0, 100.0]
        dims = [2, 5]
        M = 3
        aniso_betas, aniso_dims = [10.0], [2]
    else:
        Jinf = 50000
        J_list = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        betas = [1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
        dims = [2, 5, 10]
        M = 20
        aniso_betas, aniso_dims = [3.0, 30.0, 300.0], [2, 10]

    J_list = [J for J in J_list if J <= Jinf // 10]

    print("=" * 74)
    print("CBO-GAP Phase 1 — the (beta, d, J) mean-field surface")
    print("=" * 74)
    print("  reference particles Jinf : {}".format(Jinf))
    print("  J values quoted          : {}".format(J_list))
    print("  (every J is at most Jinf/10; larger J is refused, not reported)")
    print("  realisations per point   : {}".format(M))
    print("  sigma {}   dt {}   T {}   steps {}".format(args.sigma, args.dt, args.T, K))

    print("\n  FKR parameter condition 2*lambda > d*sigma^2:")
    bad_dims = set()
    for d in dims:
        lhs, rhs = 2.0 * lam, d * args.sigma ** 2
        ok = lhs > rhs
        if not ok:
            bad_dims.add(d)
        print("    d={:<4} 2*lambda={:.4f}  d*sigma^2={:.4f}   {}".format(
            d, lhs, rhs, "ok" if ok else "VIOLATED — drop this row"))
    if bad_dims:
        print("    Rows for d in {} lie outside FKR's own hypothesis.".format(sorted(bad_dims)))

    tasks = []
    s = args.seed
    for obj in ("ackley", "rastrigin"):
        for beta in betas:
            for d in dims:
                for _ in range(M):
                    s += 1
                    tasks.append((obj, "isotropic", beta, d, args.sigma,
                                  args.dt, K, Jinf, J_list, s))
    for obj in ("ackley", "rastrigin"):
        for beta in aniso_betas:
            for d in aniso_dims:
                for _ in range(M):
                    s += 1
                    tasks.append((obj, "anisotropic", beta, d, args.sigma,
                                  args.dt, K, Jinf, J_list, s))

    print("\n  {} realisations queued on {} workers".format(len(tasks), args.workers))
    print("  (progress prints as parameter points complete)\n")

    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            results = pool.map(task, tasks, chunksize=1)
    else:
        results = [task(t) for t in tasks]
    wall = time.time() - t0
    print("  sweep finished in {:.1f} s".format(wall))

    # aggregate
    agg = {}
    for obj, diff, beta, d, per_J, ess_ref, _ in results:
        key = (obj, diff, beta, d)
        if key not in agg:
            agg[key] = {"E": {J: [] for J in J_list},
                        "ess": {J: [] for J in J_list},
                        "ess_ref": []}
        for J in J_list:
            e, es = per_J[J]
            agg[key]["E"][J].append(e)
            agg[key]["ess"][J].append(es)
        agg[key]["ess_ref"].append(ess_ref)

    with open("ess_surface_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "diffusion", "beta", "d", "J",
                    "Ehat", "stderr", "min_ESS_sub", "min_ESS_ref", "realisations"])
        for (obj, diff, beta, d), rec in sorted(agg.items()):
            for J in J_list:
                v = np.array(rec["E"][J])
                w.writerow([obj, diff, beta, d, J,
                            "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v)) if len(v) > 1 else 0.0),
                            "{:.4f}".format(np.mean(rec["ess"][J])),
                            "{:.4f}".format(np.mean(rec["ess_ref"])),
                            len(v)])

    print("\n" + "-" * 74)
    print("P1.1 / P1.3 — slopes and ESS")
    print("-" * 74)
    print("  slope of log Ehat against log J. -1 is the rate GHV prove.")
    print("  min ESS is the smallest effective sample size seen in the reference run.\n")
    hdr = "  {:<10} {:<12} {:>7} {:>4} {:>9} {:>11} {:>22}"
    print(hdr.format("objective", "diffusion", "beta", "d", "slope", "min ESS", "verdict"))

    summary_rows = []
    for (obj, diff, beta, d), rec in sorted(agg.items()):
        E = np.array([np.mean(rec["E"][J]) for J in J_list])
        Jv = np.array(J_list, dtype=float)
        ok = np.isfinite(E) & (E > 0)
        slope = fit_slope(np.log(Jv[ok]), np.log(E[ok])) if ok.sum() >= 3 else float("nan")
        ess_ref = float(np.mean(rec["ess_ref"]))

        if ess_ref < 1.01:
            verdict = "SATURATED (hardmin)"
        elif d in bad_dims:
            verdict = "outside FKR hypothesis"
        elif abs(slope + 1.0) < 0.15:
            verdict = "J^-1 recovered"
        else:
            verdict = "rate NOT observed"

        print(hdr.format(obj, diff, "{:g}".format(beta), d,
                         "{:.4f}".format(slope), "{:.3f}".format(ess_ref), verdict))
        summary_rows.append([obj, diff, beta, d, "{:.6f}".format(slope),
                             "{:.4f}".format(ess_ref), verdict])

    with open("ess_surface_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "diffusion", "beta", "d", "slope", "min_ESS_ref", "verdict"])
        w.writerows(summary_rows)

    print("\n" + "-" * 74)
    print("P1.2 — the beta threshold")
    print("-" * 74)
    print("  Largest beta at which the J^-1 slope is still recovered, per case.")
    print("  Above it, no amount of extra particles produces Monte Carlo behaviour.\n")
    for obj in sorted(set(k[0] for k in agg)):
        for diff in sorted(set(k[1] for k in agg if k[0] == obj)):
            for d in sorted(set(k[3] for k in agg if k[0] == obj and k[1] == diff)):
                if d in bad_dims:
                    continue
                good = [b for b in sorted(betas + aniso_betas)
                        if (obj, diff, b, d) in agg
                        and abs(fit_slope(
                            np.log(np.array(J_list, dtype=float)),
                            np.log(np.array([np.mean(agg[(obj, diff, b, d)]["E"][J])
                                             for J in J_list]))) + 1.0) < 0.15
                        and np.mean(agg[(obj, diff, b, d)]["ess_ref"]) >= 1.01]
                thr = "{:g}".format(max(good)) if good else "none in range"
                print("    {:<10} {:<12} d={:<4} threshold beta = {}".format(obj, diff, d, thr))

    print("\n  READ THIS: the threshold is an upper bound set by this grid, not")
    print("  a measured boundary. Quote it as 'the rate is still observed at")
    print("  beta = X and no longer at the next grid point', never as a")
    print("  continuous crossing point.")

    print("\n" + "=" * 74)
    print("wrote ess_surface_raw.csv and ess_surface_summary.csv")
    print("total wall time {:.1f} s".format(time.time() - t0))
    print("=" * 74)


if __name__ == "__main__":
    main()
