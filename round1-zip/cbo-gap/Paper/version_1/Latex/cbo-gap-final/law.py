"""
law.py  —  CBO-GAP Phase 7: is the visibility boundary predictable from
                            measurable landscape properties?

WHERE THIS SITS
---------------
Phase 6 established two things and broke one.

  ESTABLISHED. At a concentration target of one tenth, 54 of 54 cells were
  rate-consistent at tolerance 0.15 — 12 synthetic landscapes with condition
  number, modality amplitude and ruggedness frequency varied independently,
  plus 6 named benchmarks, each at d = 5, 10, 40. At one hundredth, 16 of 36
  synthetic and 9 of 18 named cells were rate-consistent.

  ESTABLISHED. At the tight target the landscape properties separate, and not
  in the way one would guess. At d = 40, tau = 0.01, the main effect on the
  fitted slope of the condition number over two orders of magnitude is 0.009 —
  nothing. Modality amplitude gives 0.129 and is monotone (-0.746, -0.695,
  -0.617 for rho = 0, 5, 20); ruggedness frequency gives 0.078. Both effects
  grow with dimension. At tau = 0.1 every effect is below 0.07 and none is
  monotone: geometry only bites once concentration is tight.

  BROKEN. The predictive model failed out of sample: R^2 of 0.354 for dimension
  and target alone, 0.342 adding ESS trajectory features, and -92.6 adding
  geometry features. The diagnosis is covariate shift, and it is specific: 22 of
  36 named-benchmark cells have an objective-variance feature outside the range
  spanned by the synthetic training set, Rosenbrock reaching 10^7 against a
  synthetic maximum of 1.6 x 10^5. A linear model extrapolating two orders of
  magnitude beyond its support produces exactly that number. The features were
  not log-transformed and support was not checked before fitting. That is an
  analysis-design error of the same shape as the four already on record.

WHAT THIS SCRIPT ASKS
---------------------
Only two values of tau were run in Phase 6, so where each landscape's boundary
actually sits is unknown. With eight targets the boundary can be located per
landscape, and then the question becomes:

    Is tau_crit predictable from properties that can be MEASURED on an
    objective, without knowing which objective it is?

That question is answerable only if the descriptors are estimated from samples
rather than read off the generating formula, because a named benchmark has no
kappa, rho or omega to read off. So this script measures three descriptors on
every objective by the same procedure:

  cond    — fit a separable quadratic to f over the initial cloud by least
            squares; the descriptor is the ratio of the largest to the smallest
            fitted curvature coefficient. On the synthetic family this should
            recover kappa.
  nonquad — one minus the R^2 of that quadratic fit: the fraction of the
            objective's variation the quadratic cannot explain. On the synthetic
            family this should track rho.
  rugged  — the mean number of local minima per unit arclength along random
            lines through the minimizer. On the synthetic family this should
            track omega.

BUILT-IN FALSIFICATION, BEFORE ANY SIMULATION RUNS
--------------------------------------------------
Part 0 checks whether the measured descriptors recover the known generating
parameters on the synthetic family. It costs no simulation. If cond does not
track kappa, nonquad does not track rho, and rugged does not track omega, then
the descriptors are not measuring what they are named for and everything
downstream is void — the script says so and the expensive part should not be
run. This check exists because the previous phase discovered its modelling
problem only after 3.4 hours of compute.

THE PRE-REGISTERED RULES — fixed before this script was first run
-----------------------------------------------------------------
  delta = -1 - slope_hat. A cell is RATE-CONSISTENT AT TOLERANCE 0.15 when the
  bootstrap 95 percent interval excludes slopes flatter than -0.85. The proven
  exponent is -1; a slope of -0.85 is not that rate and is never described as it.

  tau_crit for a cell is obtained by interpolating delta against log tau to the
  crossing at 0.15, using only cells where delta is monotone in log tau to
  within the measured noise floor. The noise floor is estimated from this run's
  own replicates rather than assumed; the previous phase set a monotonicity
  tolerance of 0.02 against a measured floor of 0.055 and the test could not
  have passed.

  Cells whose boundary lies outside the grid are CENSORED, counted, and
  excluded from the regression. They are never extrapolated.

  Every scale-like feature is log-transformed before fitting. Before any
  prediction, each test point is checked against the convex range of the
  training features; points outside support are reported separately and their
  predictions are not counted toward the headline score.

  THE LAW IS USEFUL iff leave-one-landscape-out cross-validated R^2 on the
  synthetic family exceeds 0.5 AND the held-out prediction on the named
  benchmarks, restricted to points inside support, has R^2 above 0.
  Anything less is reported as a failure to find a law.

HOW TO RUN
----------
    python law.py --part 0                       (descriptor check, ~1 min, no CBO)
    python law.py --workers 3 --quick            (smoke test, ~5 min)
    python law.py --workers 3 --part 1           (the sweep, budget 4-4.5 h)
    python law.py --part 2                       (fit the law from the CSV on disk)

Part 2 also reads boundary_summary.csv from Phase 5 if it is present, which
already contains the six named benchmarks on the same eight-target grid, and
uses it as the held-out test set. No new simulation is needed for the named
benchmarks.

NumPy only. No SciPy. Python 3.8 compatible.
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

TOL = -0.15          # delta at the failure threshold: slope -0.85 gives delta -0.15
THRESH = -0.85       # bootstrap upper bound must be at or below this
N_BOOT = 400
TAUS = [0.3, 0.2, 0.1, 0.07, 0.05, 0.03, 0.02, 0.01]
DIMS = [5, 10, 40]


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


NAMED = {"ackley": f_ackley, "rastrigin": f_rastrigin, "sphere": f_sphere,
         "griewank": f_griewank, "levy": f_levy, "rosenbrock": f_rosenbrock}
NAMED_MIN = {"ackley": 0.0, "rastrigin": 0.0, "sphere": 0.0,
             "griewank": 0.0, "levy": 1.0, "rosenbrock": 1.0}

# Synthetic family, revised after the Phase 7 descriptor check.
#
# Two changes, both forced by measurement rather than taste.
#
#   The rho = 0 landscapes were duplicated across omega. With no oscillation
#   term, omega has no effect on the function, so syn_k1_r0_w1 and syn_k1_r0_w3
#   were literally the same function computed twice. Two of the twelve
#   landscapes were redundant, which is 6 of 36 cells and about 17 percent of
#   the Phase 6 Part B compute. Only one omega level is kept at rho = 0.
#
#   omega = 7 is added. The measured ruggedness descriptor is exactly
#   (2*omega + 1)/8 on this family, so omega in {1, 3} spans only 0.375 to
#   0.875. Ackley and Rastrigin both measure 1.875, because they oscillate with
#   period 1 and so have an effective omega near 2*pi. Without omega = 7 those
#   two benchmarks fall outside the training range and their held-out
#   predictions would be discarded as extrapolations before the model is fitted
#   — losing the only two hard cases in the test set.
SYNTH = []
for _k in (1.0, 100.0):
    SYNTH.append(("syn_k{:g}_r0_w1".format(_k), _k, 0.0, 1.0))
    for _r in (5.0, 20.0):
        for _w in (1.0, 3.0, 7.0):
            SYNTH.append(("syn_k{:g}_r{:g}_w{:g}".format(_k, _r, _w), _k, _r, _w))
SYNTH_PARAMS = {n: (k, r, w) for n, k, r, w in SYNTH}


def make_synth(kappa, rho, omega):
    def f(X):
        d = X.shape[1]
        a = kappa ** (np.arange(d, dtype=float) / max(d - 1, 1))
        return (X * X * a).sum(axis=1) + rho * (1.0 - np.cos(omega * X)).sum(axis=1)
    return f


def objective(name):
    if name in NAMED:
        return NAMED[name], NAMED_MIN[name]
    k, r, w = SYNTH_PARAMS[name]
    return make_synth(k, r, w), 0.0


def _avg_rank(v):
    """Average ranks, so ties get the same rank. Without this, ranks depend on
    the sort's arbitrary ordering of tied values, and a descriptor with many
    ties returns a different correlation on different machines. That happened:
    the ruggedness column had 23 of 36 values identical and its correlation
    came out +0.62 on one machine and +0.34 on another."""
    v = np.asarray(v, float)
    o = np.argsort(v, kind="mergesort")
    r = np.empty(len(v), float)
    r[o] = np.arange(len(v), dtype=float)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        if j > i:
            r[o[i:j + 1]] = np.mean(r[o[i:j + 1]])
        i = j + 1
    return r


def spearman(a, b):
    x, y = _avg_rank(a), _avg_rank(b)
    x = x - x.mean(); y = y - y.mean()
    den = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / den) if den > 0 else float("nan")


def tie_fraction(v):
    v = np.asarray(v, float)
    _, c = np.unique(v, return_counts=True)
    return float((c[c > 1].sum()) / len(v)) if len(v) else 0.0


# ----------------------------------------------------------------------
# descriptors, measured from samples only
# ----------------------------------------------------------------------

def descriptors(name, d, n=8000, npts=4001, seed=31337):
    """Three descriptors, computed by the same procedure for every objective.
    Nothing uses the generating formula, so a named benchmark is treated exactly
    as a synthetic one.

    The first version of this function was broken in two ways that the part 0
    check caught before any simulation was run, which is why the check exists.

      Modality was measured as the residual fraction of a global quadratic fit.
      That is a variance RATIO, so anisotropic scaling swamps it: at kappa = 100
      a landscape with rho = 20 returned 0.0012 while the same rho at kappa = 1
      returned 0.0635, a factor of fifty driven entirely by conditioning.
      Now each coordinate is detrended against its OWN fitted curvature and the
      modality amplitude is normalised per coordinate, so the scale of the bowl
      divides out.

      Ruggedness was counted along RANDOM directions. In d dimensions a random
      unit vector moves each coordinate by about t/sqrt(d), so the oscillation
      is diluted away and the count collapses onto its floor as d grows: 23 of
      36 synthetic cells returned exactly 1/8. Now the count is taken along the
      COORDINATE AXES, where the oscillation is not diluted, and after removing
      the quadratic trend, so the bowl cannot mask the wiggles.
    """
    f, xs = objective(name)
    rng = np.random.default_rng(seed + 97 * d + 7 * len(name))

    # ---- axis-aligned profiles through the minimizer -------------------
    t = np.linspace(-4.0, 4.0, npts)
    curv, amp, cross = [], [], []
    base = np.zeros((npts, d)) + xs
    for i in range(d):
        P = base.copy()
        P[:, i] = xs + t
        v = f(P)
        # fit v ~ a t^2 + b t + c on this axis, then detrend
        A = np.vstack([t * t, t, np.ones(npts)]).T
        sol, _, _, _ = np.linalg.lstsq(A, v, rcond=None)
        r = v - A @ sol
        a_i = abs(float(sol[0]))
        curv.append(a_i)
        # modality amplitude, normalised by this coordinate's own curvature
        # scale so that conditioning divides out
        scale = a_i * (t[-1] ** 2) if a_i > 1e-12 else (np.std(v) + 1e-12)
        # modality = mean depth of the local wells, normalised by this
        # coordinate's own curvature scale. Depth is used rather than the
        # residual standard deviation because a quadratic fit absorbs more of a
        # low-frequency oscillation than a high-frequency one, which made the
        # residual-based version confound modality amplitude with frequency
        # (correlation with omega of +0.59 against +0.42 with rho, the quantity
        # it was supposed to measure).
        dv = np.diff(v)
        lo_i = np.where((dv[:-1] < 0) & (dv[1:] > 0))[0] + 1
        hi_i = np.where((dv[:-1] > 0) & (dv[1:] < 0))[0] + 1
        if lo_i.size and hi_i.size:
            depths = []
            for li in lo_i:
                nb = hi_i[np.argmin(np.abs(hi_i - li))]
                depths.append(float(v[nb] - v[li]))
            amp.append(float(np.mean(depths)) / scale)
        else:
            amp.append(0.0)
        # ruggedness: sign changes of the detrended derivative per unit length,
        # GATED on the residual being real signal rather than round-off. Without
        # the gate a purely quadratic coordinate (rho = 0) has a residual at the
        # level of machine epsilon, whose sign flips thousands of times, and the
        # descriptor reports maximal ruggedness for the smoothest landscape in
        # the family. That is what kept the first two versions of this function
        # from separating ruggedness from conditioning.
        if float(np.std(r)) <= 1e-6 * (float(np.std(v)) + 1e-300):
            cross.append(0.0)
        else:
            dr = np.diff(r)
            cross.append(int(np.sum(dr[:-1] * dr[1:] < 0)) / (t[-1] - t[0]))

    curv = np.array(curv)
    pos = curv[curv > 1e-12]
    cond = float(pos.max() / pos.min()) if pos.size >= 2 else 1.0
    modality = float(np.mean(amp))
    rugged = float(np.mean(cross))

    X = rng.standard_normal((n, d)) + xs
    y = f(X)
    return dict(cond=cond, nonquad=modality, rugged=rugged,
                fvar=float(np.var(y)), fscale=float(np.std(y)))


def part0(quiet=False):
    if not quiet:
        print("=" * 84)
        print("P7.0 — do the measured descriptors recover the known parameters?")
        print("=" * 84)
        print("  No simulation is run here. If this check fails, the expensive part")
        print("  should not be started: the descriptors would not be measuring what")
        print("  they are named for and every downstream fit would be void.\n")
        print("  {} landscapes x {} dimensions = {} cells\n".format(
            len(SYNTH), len(DIMS), len(SYNTH) * len(DIMS)))
        print("  {:<20} {:>4} {:>8} {:>6} {:>6} {:>12} {:>10} {:>10}".format(
            "landscape", "d", "kappa", "rho", "omega", "cond", "nonquad", "rugged"))
    rows = []
    for nm, k, r, w in SYNTH:
        for d in DIMS:
            D = descriptors(nm, d)
            rows.append((k, r, w, d, D))
            if not quiet:
                print("  {:<20} {:>4} {:>8g} {:>6g} {:>6g} {:>12.4g} {:>10.4f} {:>10.4f}".format(
                    nm, d, k, r, w, D["cond"], D["nonquad"], D["rugged"]))


    K = [r[0] for r in rows]; R = [r[1] for r in rows]; W = [r[2] for r in rows]
    DD = [r[3] for r in rows]
    C = [r[4]["cond"] for r in rows]; NQ = [r[4]["nonquad"] for r in rows]
    RG = [r[4]["rugged"] for r in rows]
    if not quiet:
        print("\n  Tie fractions (a high value means the descriptor is saturating):")
        print("    cond {:.2f}   nonquad {:.2f}   rugged {:.2f}".format(
            tie_fraction(C), tie_fraction(NQ), tie_fraction(RG)))
    if not quiet:
        print("\n  Spearman correlations (tie-corrected), {} synthetic cells:".format(len(rows)))
        print("    cond    vs kappa : {:+.4f}   (should be strongly positive)".format(spearman(C, K)))
        print("    nonquad vs rho   : {:+.4f}   (should be strongly positive)".format(spearman(NQ, R)))
        print("    rugged  vs omega : {:+.4f}   (should be strongly positive)".format(spearman(RG, W)))
        print("\n  Cross-terms, which should be weak if the descriptors separate:")
        print("    cond    vs rho   : {:+.4f}".format(spearman(C, R)))
        print("    nonquad vs omega : {:+.4f}".format(spearman(NQ, W)))
        print("    rugged  vs kappa : {:+.4f}".format(spearman(RG, K)))
        print("    cond    vs d     : {:+.4f}".format(spearman(C, DD)))
        print("    nonquad vs d     : {:+.4f}".format(spearman(NQ, DD)))
        print("    rugged  vs d     : {:+.4f}".format(spearman(RG, DD)))

    sub = [i for i in range(len(R)) if R[i] > 0]

    def s2(a, b):
        return spearman([a[i] for i in sub], [b[i] for i in sub])

    print("\n  Restricted to the {} cells with rho > 0, where omega is".format(len(sub)))
    print("  IDENTIFIABLE. When rho = 0 the oscillation term vanishes and omega")
    print("  has no effect on the function at all, so those cells carry no")
    print("  information about omega and depress any correlation with it. The")
    print("  family now keeps only one omega level at rho = 0 for that reason.")
    print("    cond    vs kappa : {:+.4f}".format(s2(C, K)))
    print("    modality vs rho  : {:+.4f}".format(s2(NQ, R)))
    print("    rugged  vs omega : {:+.4f}".format(s2(RG, W)))
    print("    cross: cond-rho {:+.4f}  modality-omega {:+.4f}  modality-kappa {:+.4f}  rugged-kappa {:+.4f}".format(
        s2(C, R), s2(NQ, W), s2(NQ, K), s2(RG, K)))
    diag = (s2(C, K), s2(NQ, R), s2(RG, W))
    cross = (abs(s2(C, R)), abs(s2(NQ, W)), abs(s2(NQ, K)), abs(s2(RG, K)),
             abs(spearman(C, DD)), abs(spearman(NQ, DD)), abs(spearman(RG, DD)))
    ok = min(diag) > 0.6 and max(cross) < 0.5
    print("\n  worst diagonal {:+.4f} (needs > 0.60)   worst cross {:.4f} (needs < 0.50)".format(
        min(diag), max(cross)))
    print("\n  VERDICT: {}".format(
        "descriptors recover the generating parameters — proceed to --part 1"
        if ok else
        "DESCRIPTORS FAIL — do not run part 1; they are not measuring what they claim"))

    if quiet:
        return ok
    print("\n  Named benchmarks, same procedure:")
    print("  {:<14} {:>4} {:>12} {:>10} {:>10} {:>14}".format(
        "objective", "d", "cond", "nonquad", "rugged", "f variance"))
    for nm in NAMED:
        for d in DIMS:
            D = descriptors(nm, d)
            print("  {:<14} {:>4} {:>12.4g} {:>10.4f} {:>10.4f} {:>14.4g}".format(
                nm, d, D["cond"], D["nonquad"], D["rugged"], D["fvar"]))
    print("\n  Compare these ranges against the synthetic table above. Any named")
    print("  value outside the synthetic range is an extrapolation and its")
    print("  prediction will be excluded from the headline score in part 2.")
    return ok


# ----------------------------------------------------------------------
# simulation
# ----------------------------------------------------------------------

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


def one_realisation(name, d, beta, sigma, dt, K, Jinf, J_list, seed):
    f, xs = objective(name)
    rng = np.random.default_rng(seed)
    X0 = rng.standard_normal((Jinf, d)) + xs
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
            float(les[0]), float(les.mean()), float(les[0] - les.min()))


def task(a):
    name, d, tau, beta, sigma, dt, K, Jinf, J_list, seed = a
    per_J, l0, lm, dec = one_realisation(name, d, beta, sigma, dt, K,
                                         Jinf, J_list, seed)
    return name, d, tau, beta, per_J, l0, lm, dec


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


def part1(args):
    print("=" * 84)
    print("P7.1 — locating the boundary on the synthetic family")
    print("=" * 84)
    if not args.force:
        print("  GATE: running the descriptor check first. Part 1 costs several")
        print("  hours; if the descriptors do not recover the parameters they are")
        print("  named for, every fit downstream is void and the compute is wasted.")
        print("  Override with --force only if you know why.\n")
        if not part0(quiet=True):
            print("\n  ABORTING part 1: the descriptor check FAILED.")
            print("  Run 'python law.py --part 0' for the full table, fix the")
            print("  descriptors or the landscape family, and try again.")
            return
        print("\n  gate passed — starting the sweep\n")

    names = [n for n, _, _, _ in SYNTH]
    dims, taus = DIMS, TAUS
    Jinf, Jgrid = 50000, [10, 20, 40, 80, 160, 320, 640, 1250, 2500, 5000]
    if args.quick:
        names, dims, taus = names[:3], [5, 10], [0.3, 0.1, 0.03, 0.01]
        Jinf, Jgrid = 4000, [10, 40, 160, 400]
    J_list = [J for J in Jgrid if J <= Jinf // 10]
    K = int(round(args.T / args.dt))

    beta = {}
    for nm in names:
        f, xs = objective(nm)
        for d in dims:
            rng = np.random.default_rng(4242 + 131 * d)
            Xp = rng.standard_normal((4000, d)) + xs
            fv = f(Xp)
            fc = fv - fv.min()
            for t in taus:
                beta[(nm, d, t)] = solve_beta(fc, math.log(t * 4000))

    tasks, s = [], args.seed
    for nm in names:
        for d in dims:
            for t in taus:
                for _ in range(args.M):
                    s += 1
                    tasks.append((nm, d, t, beta[(nm, d, t)], args.sigma,
                                  args.dt, K, Jinf, J_list, s))
    print("  {} realisations on {} workers\n".format(len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    agg = {}
    for nm, d, t, b, per_J, l0, lm, dec in res:
        k = (nm, d, t)
        if k not in agg:
            agg[k] = {"beta": b, "E": {J: [] for J in J_list},
                      "l0": [], "lm": [], "dec": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        agg[k]["l0"].append(l0); agg[k]["lm"].append(lm); agg[k]["dec"].append(dec)

    rows = {}
    with open("law_synth.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "kappa", "rho", "omega", "d", "tau", "beta", "slope",
                    "delta", "ci_lo", "ci_hi", "log_ess_init", "log_ess_mean",
                    "log_ess_decay", "verdict"])
        for (nm, d, t) in sorted(agg):
            r = agg[(nm, d, t)]
            sl = fit_slope(np.array(J_list, float),
                           np.array([np.mean(r["E"][J]) for J in J_list]))
            lo, hi = boot_ci(r["E"], J_list)
            k_, r_, w_ = SYNTH_PARAMS[nm]
            v = "rate-consistent" if hi <= THRESH else "not rate-consistent"
            rows[(nm, d, t)] = (sl, lo, hi)
            w.writerow([nm, k_, r_, w_, d, t, "{:.6g}".format(r["beta"]),
                        "{:.6f}".format(sl), "{:.6f}".format(-1.0 - sl),
                        "{:.6f}".format(lo), "{:.6f}".format(hi),
                        "{:.6g}".format(np.mean(r["l0"])),
                        "{:.6g}".format(np.mean(r["lm"])),
                        "{:.6g}".format(np.mean(r["dec"])), v])

    # noise floor from this run's own replicates, not assumed
    floors = []
    for nm in names:
        for d in dims:
            v = [rows[(nm, d, t)][0] for t in taus[:3]]
            floors.append(max(v) - min(v))
    floor = float(np.median(floors))
    print("\n  measured noise floor (spread of slope over the three loosest")
    print("  targets, where it should be flat): median {:.4f}".format(floor))
    print("  Monotonicity below is tested against this measured value, not an")
    print("  assumed one — the previous phase assumed 0.02 against a floor of 0.055.")

    print("\n  {:<20} {:>4}".format("landscape", "d") +
          "".join("{:>10}".format("t=" + str(t)) for t in taus) +
          "{:>12}{:>8}".format("tau_crit", "status"))
    for nm in names:
        for d in dims:
            ds = [-1.0 - rows[(nm, d, t)][0] for t in taus]
            line = "  {:<20} {:>4}".format(nm, d) + \
                   "".join("{:>10.3f}".format(x) for x in ds)
            lt = np.log(taus)
            tc, status = None, ""
            tc, mono = taucrit_from_rows(
                {t: -1.0 - rows[(nm, d, t)][0] for t in taus}, taus, floor)
            if tc is None:
                status = ("never fails" if ds[-1] > TOL else "already failed")
            elif not mono:
                status = "non-mono"
            line += "{:>12}{:>8}".format("{:.4f}".format(tc) if tc else "-",
                                         status if status else "ok")
            print(line)
    print("\n  Censored and non-monotone cells are excluded from the regression in")
    print("  part 2 and are never extrapolated.")


# ----------------------------------------------------------------------
# part 2 — fit the law
# ----------------------------------------------------------------------

def taucrit_from_rows(rows, taus, floor):
    """Locate the concentration target at which a cell stops being
    rate-consistent.

    SIGN CONVENTION, which an earlier version of this function got backwards
    and which cost an eight-hour sweep. delta = -1 - slope. A FLAT slope of
    -0.85, the failure case, gives delta = -0.15; a STEEP slope of -1.15 gives
    delta = +0.15. Degradation therefore drives delta DOWNWARD, and the
    crossing to find is delta falling through -0.15 as tau tightens. The
    earlier version searched for delta rising through +0.15, which is the
    steep side, so the crossing almost never occurred: 30 of 42 cells were
    reported censored and the 5 that were not were spurious.

    taus is passed in DESCENDING order, so the sequence should be
    non-increasing apart from noise. Monotonicity is tested against the
    measured noise floor, not an assumed tolerance.
    """
    lt = np.log(taus)
    ds = [rows[t] for t in taus]
    mono = all(ds[i + 1] <= ds[i] + floor for i in range(len(ds) - 1))
    for i in range(len(taus) - 1):
        if ds[i] > TOL >= ds[i + 1]:
            x0, x1, y0, y1 = lt[i], lt[i + 1], ds[i], ds[i + 1]
            return math.exp(x0 + (TOL - y0) * (x1 - x0) / (y1 - y0)), mono
    # no crossing: either the cell never degrades within the grid (boundary
    # below the smallest target) or it was already degraded at the loosest.
    return None, mono


def part2():
    print("=" * 84)
    print("P7.2 — fitting the law, and testing it on the named benchmarks")
    print("=" * 84)
    if not os.path.exists("law_synth.csv"):
        print("  law_synth.csv not found — run --part 1 first")
        return
    S = collections_defaultdict()
    for r in csv.DictReader(open("law_synth.csv")):
        S[(r["name"], int(r["d"]))][float(r["tau"])] = float(r["delta"])
    floors = []
    for k in S:
        v = [S[k][t] for t in sorted(S[k], reverse=True)[:3]]
        floors.append(max(v) - min(v))
    floor = float(np.median(floors))

    X, y, keys = [], [], []
    cens = 0
    for (nm, d) in sorted(S):
        taus = sorted(S[(nm, d)], reverse=True)
        tc, mono = taucrit_from_rows(S[(nm, d)], taus, floor)
        if tc is None or not mono:
            cens += 1
            continue
        D = descriptors(nm, d)
        # cond spans decades and is logged; modality and ruggedness are already
        # dimensionless and bounded (0-2.5 and 0-2.1), so they are used raw.
        # An earlier version logged ruggedness, which sent the three landscapes
        # with rugged = 0 exactly to log(1e-9) = -20.7 against -0.98 for the
        # next smallest value: three points twenty units from everything else,
        # dominating a four-feature fit on roughly twenty-five cells.
        X.append([math.log(D["cond"]), D["nonquad"], D["rugged"], math.log(d)])
        y.append(math.log(tc))
        keys.append((nm, d))
    X, y = np.array(X), np.array(y)
    print("  usable cells {} of {}   censored or non-monotone {}".format(
        len(y), len(S), cens))
    if len(y) < 8:
        print("  too few usable cells to fit a law. That is itself the result.")
        return

    names_f = ["log cond", "modality", "rugged", "log d"]
    A = np.column_stack([X, np.ones(len(y))])
    sol, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    r2 = 1 - ((y - A @ sol) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    print("\n  log tau_crit = " + " + ".join(
        "{:+.4f}*{}".format(sol[i], names_f[i]) for i in range(4)) +
        " {:+.4f}".format(sol[4]))
    print("  in-sample R^2 = {:.4f}".format(r2))

    # leave-one-landscape-out
    uniq = sorted({k[0] for k in keys})
    preds, acts = [], []
    for held in uniq:
        tr = [i for i, k in enumerate(keys) if k[0] != held]
        te = [i for i, k in enumerate(keys) if k[0] == held]
        if not te or len(tr) < 6:
            continue
        s2, _, _, _ = np.linalg.lstsq(A[tr], y[tr], rcond=None)
        preds.extend(A[te] @ s2); acts.extend(y[te])
    preds, acts = np.array(preds), np.array(acts)
    cv = 1 - ((acts - preds) ** 2).sum() / ((acts - acts.mean()) ** 2).sum()
    print("  leave-one-landscape-out R^2 = {:.4f}  ({} predictions)".format(cv, len(acts)))

    if not os.path.exists("boundary_summary.csv"):
        print("\n  boundary_summary.csv (Phase 5) not found — cannot run the")
        print("  held-out test on the named benchmarks.")
        return
    N = collections_defaultdict()
    for r in csv.DictReader(open("boundary_summary.csv")):
        N[(r["objective"], int(r["d"]))][float(r["tau"])] = -1.0 - float(r["slope"])
    lo, hi = X.min(axis=0), X.max(axis=0)
    print("\n  {:<14} {:>4} {:>12} {:>12} {:>10} {:>12}".format(
        "objective", "d", "tau_crit obs", "predicted", "in support", "log error"))
    ins_p, ins_a = [], []
    for (nm, d) in sorted(N):
        taus = sorted(N[(nm, d)], reverse=True)
        tc, mono = taucrit_from_rows(N[(nm, d)], taus, floor)
        if tc is None or not mono:
            continue
        D = descriptors(nm, d)
        x = np.array([math.log(D["cond"]), D["nonquad"], D["rugged"], math.log(d)])
        inside = bool(np.all(x >= lo) and np.all(x <= hi))
        pred = math.exp(float(np.append(x, 1.0) @ sol))
        if inside:
            ins_p.append(math.log(pred)); ins_a.append(math.log(tc))
        print("  {:<14} {:>4} {:>12.4f} {:>12.4f} {:>10} {:>12.4f}".format(
            nm, d, tc, pred, "yes" if inside else "NO",
            math.log(pred) - math.log(tc)))
    if len(ins_a) >= 3:
        ip, ia = np.array(ins_p), np.array(ins_a)
        r2o = 1 - ((ia - ip) ** 2).sum() / ((ia - ia.mean()) ** 2).sum()
        print("\n  held-out R^2 on in-support named cells ({}): {:.4f}".format(len(ia), r2o))
        good = cv > 0.5 and r2o > 0.0
        print("  VERDICT: {}".format(
            "a usable law: cross-validated and it transfers to unseen objectives"
            if good else
            "NO usable law — report the descriptor effects and the failure to predict"))
    else:
        print("\n  too few in-support named cells for a held-out score.")


class collections_defaultdict(dict):
    def __missing__(self, k):
        self[k] = {}
        return self[k]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--part", default="0")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=12)
    p.add_argument("--sigma", type=float, default=0.2)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260825)
    p.add_argument("--force", action="store_true",
                   help="run part 1 even if the descriptor gate fails")
    args = p.parse_args()
    args.M = 3 if args.quick else args.realisations

    if args.quick:
        part0()
        part1(args)
        return
    if args.part == "0":
        part0()
    elif args.part == "1":
        part1(args)
    elif args.part == "2":
        part2()
    else:
        part0(); part1(args); part2()


if __name__ == "__main__":
    main()
