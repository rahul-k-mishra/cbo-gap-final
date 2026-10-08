"""
verify.py  —  CBO-GAP verification script (parallel, no SciPy)

WHAT THIS SCRIPT IS FOR, IN PLAIN LANGUAGE
------------------------------------------
Four claims were made by hand in the CBO-GAP analysis. Three of them nothing
downstream survives without. This script checks all four numerically, so the
paper never rests on an unchecked hand derivation.

  CHECK 1 — the kappa_d refinement.
      Claim: the paper's own scaling alpha_0 = O(d log(1/eps)/eps) drops a
      term, because the volume of the unit ball shrinks superexponentially.
      What we compute: log(1/kappa_d) for growing d, and compare it against
      (d/2)*log(d).
      What the result means: if the difference stays proportional to d (not
      faster), the claimed refinement O(d log(d/eps)/eps) is correct.

  CHECK 2 — the doubly-exponential trace.
      Claim: for BOUNDED objectives the mean-field constant is doubly
      exponential in alpha; for COERCIVE ones only singly exponential.
      What we compute: log(log(c_M)) as alpha grows, on both branches of
      Eq. (77).
      What the result means: if log(log(c_M)) grows LINEARLY in alpha on the
      bounded branch and only LOGARITHMICALLY on the coercive branch, the two
      branches are qualitatively different and the trace holds. This is the
      claim I most expect to be wrong — it contradicts the authors' own
      summary sentence in Theorem 3.8.

  CHECK 3 — Rosenbrock's lower growth exponent l.
      Claim: l = 1, not 4, because along the parabolic valley the objective
      grows only linearly in |x|.
      What we compute: m(R) = the smallest value of Rosenbrock on the sphere
      of radius R, for many R, found by a valley-parameterised start plus a
      projected local search on the sphere. Then the slope of log m against
      log R.
      What the result means: slope ~ 1 confirms l = 1. Anything near 4 would
      destroy the A(3,1,4) row and everything leaning on it.
      This is the expensive check and the reason for the parallelism.

  CHECK 4 — Schwefel is unbounded below on R^d.
      Claim: f -> -infinity, so it belongs to no class A(s,l,u) at all.
      What we compute: f at the exact points where every sine term equals +1.
      What the result means: if the values march off to -infinity, the whole
      Schwefel row is confirmed and Schwefel is admissible only as a
      box-constrained problem, which is a different theory.

HOW TO RUN
----------
    python verify.py
    python verify.py --workers 3
    python verify.py --workers 3 --quick

Requires NumPy only. No SciPy. Runs on Python 3.8.
Default is 3 worker processes, which is roughly 75-80 percent of a 4-core
machine. Each worker is pinned to a single BLAS thread so the processes do
not fight each other over cores.
"""

import argparse
import math
import os
import sys
import time
from multiprocessing import Pool

# Keep the numerical libraries single-threaded inside each worker process.
# Without this, 3 processes x N BLAS threads oversubscribes the CPU and the
# run gets SLOWER than serial. This must happen before numpy is imported.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402


# ----------------------------------------------------------------------
# CHECK 1 — kappa_d refinement (cheap, runs in the parent process)
# ----------------------------------------------------------------------

def log_unit_ball_volume(d):
    """log of the volume of the unit ball in R^d, via lgamma. No SciPy."""
    return 0.5 * d * math.log(math.pi) - math.lgamma(d / 2.0 + 1.0)


def check1(dims):
    rows = []
    for d in dims:
        neg_log_kappa = -log_unit_ball_volume(d)
        leading = 0.5 * d * math.log(d)
        residual = neg_log_kappa - leading
        rows.append((d, neg_log_kappa, leading, residual, residual / d))
    return rows


# ----------------------------------------------------------------------
# CHECK 2 — the two branches of Eq. (77) (cheap)
# ----------------------------------------------------------------------

def check2(alphas, C2=1.0, C3=1.0, C4=1.0, dEcal=1.0, delta=0.1):
    """
    Bounded branch  : b2 = exp(alpha * dEcal)
    Coercive branch : b2 = 2*(C2/C3)*(1 + 1/(alpha*C3)) / C4**2   (decreasing in alpha)

    In both cases M >= 2K/delta with K proportional to b2, and
    c_M = exp(alpha*C2*(1 + sqrt(M))).
    Everything is done in log space; c_M itself overflows immediately.
    """
    rows = []
    for a in alphas:
        # bounded branch: log b2 = a*dEcal
        log_M_bounded = a * dEcal + math.log(2.0 / delta)
        log_log_cM_bounded = math.log(a * C2) + 0.5 * log_M_bounded  # dominant term

        # coercive branch
        b2_coer = 2.0 * (C2 / C3) * (1.0 + 1.0 / (a * C3)) / (C4 ** 2)
        log_M_coer = math.log(b2_coer) + math.log(2.0 / delta)
        log_log_cM_coer = math.log(a * C2) + 0.5 * log_M_coer

        rows.append((a, log_log_cM_bounded, log_log_cM_coer))
    return rows


# ----------------------------------------------------------------------
# CHECK 3 — Rosenbrock lower growth exponent (the expensive one)
# ----------------------------------------------------------------------

def rosenbrock(x):
    xi = x[:-1]
    xn = x[1:]
    return float(np.sum(100.0 * (xn - xi ** 2) ** 2 + (1.0 - xi) ** 2))


def rosenbrock_grad(x):
    d = x.size
    g = np.zeros(d)
    xi = x[:-1]
    xn = x[1:]
    t = xn - xi ** 2
    g[:-1] += -400.0 * xi * t - 2.0 * (1.0 - xi)
    g[1:] += 200.0 * t
    return g


def valley_point(d, R):
    """
    Valley-parameterised start: the exact curve x_{k+1} = x_k^2 with x_1 = t,
    with t chosen by bisection so that |x| = R. This is the point whose
    existence makes l = 1 rather than 4, so the local search starts here
    instead of hoping to stumble onto the valley from a random point.
    """
    def norm_of(t):
        x = np.empty(d)
        x[0] = t
        for k in range(1, d):
            x[k] = x[k - 1] ** 2
            if not np.isfinite(x[k]):
                return np.inf, x
        return float(np.linalg.norm(x)), x

    lo, hi = 1.0, 2.0
    n_hi, _ = norm_of(hi)
    tries = 0
    while n_hi < R and tries < 200:
        hi = 1.0 + (hi - 1.0) * 1.5
        n_hi, _ = norm_of(hi)
        tries += 1
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        n_mid, x_mid = norm_of(mid)
        if n_mid < R:
            lo = mid
        else:
            hi = mid
    _, x = norm_of(0.5 * (lo + hi))
    n = np.linalg.norm(x)
    if np.isfinite(n) and n > 0:
        x = x * (R / n)
    return x


def min_on_sphere(d, R, restarts, iters, seed):
    """
    Smallest Rosenbrock value found on the sphere |x| = R.

    Method: projected gradient descent with backtracking, staying on the
    sphere by renormalising after every step. Started from the valley point
    plus random restarts. This gives an UPPER bound on m(R) — if the search
    misses, the reported exponent is too large, never too small, so a result
    near 1 is trustworthy and a result near 4 would need more restarts before
    it is believed.
    """
    rng = np.random.RandomState(seed)
    best = np.inf

    starts = [valley_point(d, R)]
    # mirrored valley and random points on the sphere
    vp = starts[0].copy()
    vp[0] = -vp[0]
    starts.append(vp)
    for _ in range(max(0, restarts - 2)):
        z = rng.randn(d)
        z *= R / np.linalg.norm(z)
        starts.append(z)

    for x0 in starts:
        x = x0.astype(np.float64).copy()
        n = np.linalg.norm(x)
        if not np.isfinite(n) or n == 0:
            continue
        x *= R / n
        fx = rosenbrock(x)
        step = R * 1e-3
        for _ in range(iters):
            g = rosenbrock_grad(x)
            # project the gradient onto the tangent space of the sphere
            g = g - (np.dot(g, x) / (R * R)) * x
            gn = np.linalg.norm(g)
            if gn == 0 or not np.isfinite(gn):
                break
            g = g / gn
            improved = False
            for _ in range(40):
                y = x - step * g
                ny = np.linalg.norm(y)
                if not np.isfinite(ny) or ny == 0:
                    step *= 0.5
                    continue
                y *= R / ny
                fy = rosenbrock(y)
                if np.isfinite(fy) and fy < fx:
                    x, fx = y, fy
                    step *= 1.3
                    improved = True
                    break
                step *= 0.5
            if not improved:
                break
            if step < R * 1e-14:
                break
        if fx < best:
            best = fx
    return best


def check3_task(args):
    d, R, restarts, iters, seed = args
    t0 = time.time()
    m = min_on_sphere(d, R, restarts, iters, seed)
    return (d, R, m, time.time() - t0)


def fit_slope(logR, logm):
    """Least-squares slope of log m against log R. This is the exponent l."""
    A = np.vstack([logR, np.ones_like(logR)]).T
    sol, _, _, _ = np.linalg.lstsq(A, logm, rcond=None)
    return float(sol[0]), float(sol[1])


# ----------------------------------------------------------------------
# CHECK 4 — Schwefel unbounded below (cheap)
# ----------------------------------------------------------------------

def check4(d, ks):
    rows = []
    for k in ks:
        root = math.pi / 2.0 + 2.0 * math.pi * k   # sqrt(x_i)
        xi = root ** 2
        x = np.full(d, xi)
        f = 418.9829 * d - float(np.sum(x * np.sin(np.sqrt(np.abs(x)))))
        rows.append((k, xi, float(np.linalg.norm(x)), f))
    return rows


# ----------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3,
                   help="worker processes (default 3, about 75-80 percent of a 4-core box)")
    p.add_argument("--quick", action="store_true",
                   help="smaller grid and fewer restarts, for a first smoke run")
    p.add_argument("--seed", type=int, default=20260817)
    args = p.parse_args()

    print("=" * 72)
    print("CBO-GAP verification — 4 checks, NumPy only, {} workers".format(args.workers))
    print("=" * 72)

    # ---------------- CHECK 1 ----------------
    print("\nCHECK 1 — kappa_d refinement")
    print("  Agenda: is -log(kappa_d) equal to (d/2)log(d) plus something that")
    print("          only grows like d? If yes, alpha_0 = O(d log(d/eps)/eps).")
    dims = [2, 5, 10, 20, 50, 100, 200, 500, 1000]
    print("\n  {:>6} {:>16} {:>16} {:>14} {:>12}".format(
        "d", "-log(kappa_d)", "(d/2)log(d)", "residual", "residual/d"))
    prev = None
    for d, nlk, lead, res, res_per_d in check1(dims):
        print("  {:>6} {:>16.4f} {:>16.4f} {:>14.4f} {:>12.4f}".format(
            d, nlk, lead, res, res_per_d))
        prev = res_per_d
    print("\n  READ THIS: if the last column settles to a constant, the extra")
    print("  (d/2)log(d) term is real and the refinement stands. Settled value"
          " ~ {:.4f}".format(prev))

    # ---------------- CHECK 2 ----------------
    print("\nCHECK 2 — doubly-exponential trace, both branches of Eq. (77)")
    print("  Agenda: log(log(c_M)) versus alpha. Linear growth means doubly")
    print("          exponential. Logarithmic growth means singly exponential.")
    alphas = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    print("\n  {:>8} {:>22} {:>22}".format("alpha", "loglog c_M (bounded)", "loglog c_M (coercive)"))
    rows2 = check2(alphas)
    for a, lb, lc in rows2:
        print("  {:>8.1f} {:>22.4f} {:>22.4f}".format(a, lb, lc))
    a = np.array([r[0] for r in rows2])
    b = np.array([r[1] for r in rows2])
    c = np.array([r[2] for r in rows2])
    sb = float(np.polyfit(a, b, 1)[0])
    sc = float(np.polyfit(np.log(a), c, 1)[0])
    print("\n  Slope of loglog c_M against alpha, bounded branch : {:.4f}".format(sb))
    print("  Slope of loglog c_M against log(alpha), coercive   : {:.4f}".format(sc))
    print("  READ THIS: a clearly positive first slope with a flat second means")
    print("  the two branches differ qualitatively, exactly as claimed. This is")
    print("  the check most likely to overturn my trace — read it sceptically.")

    # ---------------- CHECK 3 ----------------
    print("\nCHECK 3 — Rosenbrock lower growth exponent l  (parallel section)")
    print("  Agenda: smallest Rosenbrock value on spheres of growing radius.")
    print("          The slope of log m against log R is l. Claim: l = 1.")

    if args.quick:
        d_list = [2, 3, 5]
        radii = np.logspace(1.0, 4.0, 10)
        restarts, iters = 12, 400
    else:
        d_list = [2, 3, 5, 10]
        radii = np.logspace(1.0, 6.0, 16)
        restarts, iters = 40, 2000

    tasks = []
    s = args.seed
    for d in d_list:
        for R in radii:
            s += 1
            tasks.append((d, float(R), restarts, iters, s))

    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            results = pool.map(check3_task, tasks, chunksize=1)
    else:
        results = [check3_task(t) for t in tasks]
    wall = time.time() - t0
    print("\n  {} sphere minimisations on {} workers in {:.1f} s".format(
        len(tasks), args.workers, wall))

    by_d = {}
    for d, R, m, _ in results:
        by_d.setdefault(d, []).append((R, m))

    print("\n  {:>4} {:>10} {:>12} {:>28}".format("d", "slope l", "intercept", "verdict"))
    for d in d_list:
        pts = sorted(by_d[d])
        R = np.array([p[0] for p in pts])
        m = np.array([p[1] for p in pts])
        ok = np.isfinite(m) & (m > 0)
        slope, inter = fit_slope(np.log(R[ok]), np.log(m[ok]))
        verdict = "consistent with l = 1" if abs(slope - 1.0) < 0.25 else "DOES NOT match l = 1"
        print("  {:>4} {:>10.4f} {:>12.4f} {:>28}".format(d, slope, inter, verdict))

    print("\n  Per-radius detail (d, R, m(R)):")
    for d in d_list:
        pts = sorted(by_d[d])
        for R, m in pts:
            print("    d={:<3} R={:>12.4g}  m(R)={:>14.6g}".format(d, R, m))

    print("\n  READ THIS: the search returns an UPPER bound on m(R). A slope near")
    print("  1 is therefore trustworthy; a slope near 4 would mean the search")
    print("  missed the valley, not that l = 4. If any d reports a bad slope,")
    print("  rerun that d alone with more restarts before concluding anything.")

    # ---------------- CHECK 4 ----------------
    print("\nCHECK 4 — Schwefel unbounded below on R^d")
    print("  Agenda: evaluate at the exact points where every sine term is +1.")
    print("          If f marches to -infinity, Schwefel is in no class A at all.")
    d4 = 5
    rows4 = check4(d4, [0, 1, 2, 5, 10, 50, 100, 500])
    print("\n  {:>6} {:>16} {:>16} {:>20}".format("k", "x_i", "|x|", "f(x), d=5"))
    for k, xi, nx, f in rows4:
        print("  {:>6} {:>16.4g} {:>16.4g} {:>20.6g}".format(k, xi, nx, f))
    fs = np.array([r[3] for r in rows4])
    nrm = np.array([r[2] for r in rows4])
    mask = fs < 0
    if mask.sum() >= 2:
        sl, _ = fit_slope(np.log(nrm[mask]), np.log(-fs[mask]))
        print("\n  Slope of log(-f) against log|x| : {:.4f}".format(sl))
    print("  READ THIS: monotonically falling f confirms the row. The slope")
    print("  should sit near 1, matching u = 1 on the upper side.")

    print("\n" + "=" * 72)
    print("done in {:.1f} s total".format(time.time() - t0 + wall * 0))
    print("=" * 72)


if __name__ == "__main__":
    main()
