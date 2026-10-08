"""
control.py  —  CBO-GAP Phase 4: closing the residual, and one thing it cannot close

WHY THIS SCRIPT EXISTS
----------------------
Phase 3 controlled the INITIAL effective sample size by bisecting beta, and the
result overturned the project's headline. With concentration held at half the
ensemble, the slope across dimension ran -1.040, -1.031, -1.022, -1.010 from
d = 2 to d = 40, a drop of 0.030. Phase 1c had reported a drop of 0.96 across the
same span and fitted a power law to it. The dimension-dependent exponent was an
artefact of a control variable that let concentration collapse as d grew.

What survived was a residual. At the tightest target the objectives still
separated: standard deviation across objectives of 0.115 at d = 10 and 0.136 at
d = 40, and the pre-registered decomposition printed GEOMETRY PERSISTS.

That verdict is not to be believed, for two reasons, and this script exists to
settle both.

  REASON 1 — the criterion was badly chosen, by me.
      The pre-registered mechanism test used the gain in R^2 from adding
      objective identity, with a threshold of 0.05. It printed 0.0508. But the
      total R^2 of the full model was 0.146: the treatment had crushed the
      variance, so there was almost nothing left to explain and R^2 became a
      ratio of noise to noise. R^2 is the wrong statistic when the treatment
      works. This script reports ABSOLUTE spread instead, and reports the R^2
      alongside only to show why it must not be used.

  REASON 2 — the residual tracks control failure, not geometry.
      Only the initial concentration was held; it decays during the run. The
      correlation between that decay and the slope is +0.077 at the loosest
      target, +0.290 in the middle, and +0.577 at the tightest. Restricting to
      well-controlled cells gives a mean slope of -1.062 with spread 0.142;
      poorly controlled cells give -0.840 with spread 0.250. Every cell that
      "persisted" is a cell where the control lapsed.

So: hold the concentration for the WHOLE run, and see whether the residual
survives. If it vanishes, concentration is the mechanism and the objective-
dependence reported in every earlier phase of this project was an artefact of
how beta was chosen. If it survives under genuine control, geometry is real and
the landscape-descriptor programme becomes necessary.

THE DESIGN CHOICE THAT MATTERS, AND THE TRAP IT AVOIDS
------------------------------------------------------
The obvious implementation is to re-solve beta separately for every ensemble so
each one sits at the target. That is WRONG and would invalidate the whole
measurement: the J-particle system and the reference system would then be
solving different equations, and the quantity being measured is precisely the
distance between a J-particle system and its own mean-field limit. Coupling
requires one dynamics.

Therefore beta is re-solved on the REFERENCE ensemble only, and the resulting
schedule beta(t) is applied to every sub-ensemble. All systems solve the same
time-inhomogeneous SDE, the coupling stays valid, and the controlled quantity is
the concentration of the reference ensemble — which is exactly the quantity whose
decay Phase 3 identified as the problem.

WHAT THIS EXPERIMENT CANNOT DO, AND MUST NOT BE READ AS
--------------------------------------------------------
A time-varying beta is NOT the algorithm the theory analyses. FKR and GHV both
fix the inverse temperature. Annealed variants exist in the CBO literature, but
the guarantee being audited is for fixed beta.

This is a DIAGNOSTIC arm, not a proposal. Its only job is to answer whether the
residual objective-dependence is caused by concentration decay. A critic who says
"you changed the algorithm until it worked" would be right if this arm were
presented as a result about CBO. It is presented as a result about the
experiment. The fixed-beta arm runs in the same script, on the same cells, with
the same seeds, and remains the object of every claim about the theory.

THE PRE-REGISTERED RULES — fixed before this script was first run
-----------------------------------------------------------------
  RECOVERED iff the bootstrap 95 percent upper bound is at most -0.85.

  THE RESIDUAL IS A CONTROL ARTEFACT iff, in the adaptive arm:
    (i)  every cell has concentration drift below 0.05 in log units, AND
    (ii) the standard deviation of the slope across objectives is at most 0.10
         at every dimension and target, AND
    (iii) the mean slope lies within 0.15 of -1.

  GEOMETRY IS REAL iff (i) holds and (ii) fails.

  R^2 is reported but is NOT a criterion. It was one in Phase 3 and it should
  not have been.

HOW TO RUN
----------
    python control.py --workers 3 --quick        (smoke test, ~3 min)
    python control.py --workers 3                (full, budget 2-3 hours)

NumPy only. No SciPy. Python 3.8 compatible.
Writes control_raw.csv and control_summary.csv.
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
DRIFT_OK = 0.05
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


def _lse(a):
    m = a.max()
    return m + math.log(float(np.exp(a - m).sum()))


def log_ess(fc, beta):
    """Exact log effective sample size. fc is f minus its minimum, so the
    largest weight is 1 and nothing overflows; the identity remains valid after
    every individual weight has underflowed."""
    lw = -beta * fc
    return 2.0 * _lse(lw) - _lse(2.0 * lw)


def solve_beta(fc, goal_log, lo=1e-12, hi=1e12, iters=90):
    """Bisect in log beta for the target log ESS. ESS is monotone decreasing in
    beta — the full ensemble at beta = 0, one as beta grows — so the target is
    always bracketed and no failure branch is needed."""
    for _ in range(iters):
        mid = math.sqrt(lo * hi)
        if log_ess(fc, mid) > goal_log:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def solve_beta_warm(fc, goal_log, prev, iters=40):
    """Same, warm-started from the previous step's beta. The concentration moves
    slowly between steps, so a bracket of a factor of eight either side is ample
    and costs a fraction of a cold solve."""
    lo, hi = prev / 8.0, prev * 8.0
    if log_ess(fc, lo) < goal_log:
        lo = 1e-12
    if log_ess(fc, hi) > goal_log:
        hi = 1e12
    return solve_beta(fc, goal_log, lo, hi, iters)


def wmean(X, fc, beta):
    w = np.exp(-beta * fc)
    return (w[:, None] * X).sum(axis=0) / w.sum()


def one_realisation(objective, d, init, tau, arm, beta0, sigma, dt, K,
                    Jinf, J_list, seed):
    """Both arms share seeds, so the two arms of a cell see identical initial
    positions and identical Brownian paths. The only difference is the schedule."""
    f = OBJECTIVES[objective]
    rng = np.random.default_rng(seed)
    X0 = draw_initial(rng, Jinf, d, objective, init)
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    goal = math.log(tau * Jinf)
    beta, le0, le_min, le_max = beta0, None, float("inf"), -float("inf")
    b_first, b_last = None, None
    sq = math.sqrt(dt)

    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        fv = f(Xref)
        fc = fv - fv.min()
        if arm == "adaptive":
            beta = solve_beta_warm(fc, goal, beta)
        le = log_ess(fc, beta)
        if le0 is None:
            le0, b_first = le, beta
        b_last = beta
        le_min, le_max = min(le_min, le), max(le_max, le)

        dref = Xref - wmean(Xref, fc, beta)
        Xref = Xref - dt * dref + sigma * np.linalg.norm(dref, axis=1)[:, None] * dW

        # the SAME beta drives every sub-ensemble: one dynamics, valid coupling
        for J in J_list:
            Xj = Xsub[J]
            fj = f(Xj)
            dj = Xj - wmean(Xj, fj - fj.min(), beta)
            Xsub[J] = Xj - dt * dj + sigma * np.linalg.norm(dj, axis=1)[:, None] * dW[:J]
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1), out=runmax[J])

    return ({J: float(np.mean(runmax[J])) for J in J_list},
            le0, le_min, le_max, b_first, b_last)


def task(a):
    (obj, d, init, tau, arm, beta0, sigma, dt, K, Jinf, J_list, seed) = a
    per_J, le0, lem, lex, b0, b1 = one_realisation(
        obj, d, init, tau, arm, beta0, sigma, dt, K, Jinf, J_list, seed)
    return obj, d, init, tau, arm, per_J, le0, lem, lex, b0, b1


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
    p.add_argument("--seed", type=int, default=20260822)
    args = p.parse_args()

    lam, K = 1.0, int(round(args.T / args.dt))

    if args.quick:
        Jinf, J_list = 4000, [10, 40, 160, 400]
        dims, objs, taus, M = [10], ["ackley", "rastrigin"], [0.01], 3
    else:
        Jinf, J_list = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        dims = [5, 10, 40]
        objs = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
        taus, M = [0.1, 0.01], 15
    if args.realisations:
        M = args.realisations
    J_list = [J for J in J_list if J <= Jinf // 10]
    init = "centred"
    arms = ["fixed", "adaptive"]

    print("=" * 82)
    print("CBO-GAP Phase 4 — holding concentration for the whole run")
    print("=" * 82)
    print("  PRE-REGISTERED (fixed before first run):")
    print("    RECOVERED iff bootstrap 95% upper bound <= {:+.2f}".format(THRESH))
    print("    RESIDUAL IS A CONTROL ARTEFACT iff, in the adaptive arm, drift < {:.2f}".format(DRIFT_OK))
    print("      AND sd across objectives <= {:.2f} everywhere AND mean slope within 0.15 of -1".format(COLLAPSE_SD))
    print("    GEOMETRY IS REAL iff drift is controlled and the sd criterion fails")
    print("    R^2 is reported but is NOT a criterion. It was one in Phase 3 and")
    print("    should not have been: the treatment crushes the variance, so R^2")
    print("    becomes a ratio of noise to noise.")
    print("\n  The adaptive arm is DIAGNOSTIC. A time-varying inverse temperature is")
    print("  not the algorithm FKR and GHV analyse. Every claim about the theory")
    print("  rests on the fixed arm, which runs here on the same cells and seeds.")
    print("\n  Jinf {}   J grid {}   realisations {}   init {}".format(
        Jinf, len(J_list), M, init))
    print("  sigma {}  dt {}  T {}  steps {}".format(args.sigma, args.dt, args.T, K))
    dims = [d for d in dims if 2.0 * lam > d * args.sigma ** 2]
    print("  d in {} (2*lambda > d*sigma^2 holds throughout)".format(dims))

    print("\n  initial beta by bisection (both arms start here):")
    beta0 = {}
    print("  {:<12} {:>5} {:>7} {:>16}".format("objective", "d", "tau", "beta(0)"))
    for o in objs:
        for d in dims:
            for tau in taus:
                rng = np.random.default_rng(999 + 131 * d)
                Xp = draw_initial(rng, 4000, d, o, init)
                fv = OBJECTIVES[o](Xp)
                b = solve_beta(fv - fv.min(), math.log(tau * 4000))
                beta0[(o, d, tau)] = b
                print("  {:<12} {:>5} {:>7.3g} {:>16.6g}".format(o, d, tau, b))

    tasks, s = [], args.seed
    for o in objs:
        for d in dims:
            for tau in taus:
                for r in range(M):
                    s += 1
                    for arm in arms:      # same seed s in both arms
                        tasks.append((o, d, init, tau, arm, beta0[(o, d, tau)],
                                      args.sigma, args.dt, K, Jinf, J_list, s))

    print("\n  {} realisations queued on {} workers ({} cells x {} arms x {})\n".format(
        len(tasks), args.workers, len(objs) * len(dims) * len(taus), len(arms), M))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    agg = {}
    for o, d, ini, tau, arm, per_J, le0, lem, lex, b0, b1 in res:
        k = (o, d, tau, arm)
        if k not in agg:
            agg[k] = {"E": {J: [] for J in J_list}, "le0": [], "lem": [],
                      "lex": [], "b0": [], "b1": []}
        for J in J_list:
            agg[k]["E"][J].append(per_J[J])
        for key, val in (("le0", le0), ("lem", lem), ("lex", lex), ("b0", b0), ("b1", b1)):
            agg[k][key].append(val)

    rec, rows = {}, []
    for (o, d, tau, arm), r in sorted(agg.items()):
        sl = fit_slope(np.array(J_list, float),
                       np.array([np.mean(r["E"][J]) for J in J_list]))
        lo, hi = boot_ci(r["E"], J_list)
        le0, lem, lex = (float(np.mean(r[k])) for k in ("le0", "lem", "lex"))
        drift = max(le0 - lem, lex - le0)
        v = "recovered" if hi <= THRESH else ("NOT observed" if lo > THRESH else "UNDECIDED")
        rec[(o, d, tau, arm)] = (sl, lo, hi, drift, float(np.mean(r["b0"])),
                                 float(np.mean(r["b1"])), v)
        rows.append([o, d, tau, arm, "{:.6f}".format(sl), "{:.6f}".format(lo),
                     "{:.6f}".format(hi), "{:.6g}".format(drift),
                     "{:.6g}".format(np.mean(r["b0"])), "{:.6g}".format(np.mean(r["b1"])), v])

    with open("control_raw.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "tau", "arm", "J", "Ehat", "stderr",
                    "log_ESS_init", "log_ESS_min", "beta_first", "beta_last", "realisations"])
        for (o, d, tau, arm), r in sorted(agg.items()):
            for J in J_list:
                v = np.array(r["E"][J])
                w.writerow([o, d, tau, arm, J, "{:.8g}".format(v.mean()),
                            "{:.8g}".format(v.std(ddof=1) / math.sqrt(len(v))),
                            "{:.6g}".format(np.mean(r["le0"])),
                            "{:.6g}".format(np.mean(r["lem"])),
                            "{:.6g}".format(np.mean(r["b0"])),
                            "{:.6g}".format(np.mean(r["b1"])), len(v)])
    with open("control_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["objective", "d", "tau", "arm", "slope", "ci_lo", "ci_hi",
                    "drift", "beta_first", "beta_last", "verdict"])
        w.writerows(rows)

    print("\n" + "-" * 82)
    print("P4.1 — did the control hold? concentration drift, in log units")
    print("-" * 82)
    print("  Phase 3 held only the initial value and drift reached 0.31 at the")
    print("  tightest target. Adaptive should be near zero by construction; if it")
    print("  is not, the schedule is failing and nothing below can be trusted.\n")
    print("  {:<12} {:>5} {:>7} {:>12} {:>12}".format("objective", "d", "tau", "fixed", "adaptive"))
    worst = 0.0
    for o in objs:
        for d in dims:
            for tau in taus:
                a, b = rec[(o, d, tau, "fixed")][3], rec[(o, d, tau, "adaptive")][3]
                worst = max(worst, b)
                print("  {:<12} {:>5} {:>7.3g} {:>12.4f} {:>12.4f}".format(o, d, tau, a, b))
    print("\n  worst adaptive drift = {:.4f}  ({})".format(
        worst, "control holds" if worst < DRIFT_OK else "CONTROL FAILED — read no further"))

    print("\n" + "-" * 82)
    print("P4.2 — THE TEST: spread across objectives, fixed arm versus adaptive")
    print("-" * 82)
    print("  Absolute spread, not R^2. Phase 3's residual was sd 0.115 at d=10")
    print("  and 0.136 at d=40 at the tightest target.\n")
    print("  {:>5} {:>7} {:>10} {:>10} {:>10} {:>10} {:>16}".format(
        "d", "tau", "sd fixed", "sd adapt", "mean fix", "mean adp", "adaptive verdict"))
    ok_sd = True
    for d in dims:
        for tau in taus:
            sf = [rec[(o, d, tau, "fixed")][0] for o in objs]
            sa = [rec[(o, d, tau, "adaptive")][0] for o in objs]
            sdf, sda = float(np.std(sf, ddof=1)), float(np.std(sa, ddof=1))
            if sda > COLLAPSE_SD:
                ok_sd = False
            print("  {:>5} {:>7.3g} {:>10.4f} {:>10.4f} {:>10.4f} {:>10.4f} {:>16}".format(
                d, tau, sdf, sda, float(np.mean(sf)), float(np.mean(sa)),
                "COLLAPSE" if sda <= COLLAPSE_SD else "persists"))

    mean_ad = float(np.mean([rec[(o, d, tau, "adaptive")][0]
                             for o in objs for d in dims for tau in taus]))
    print("\n  overall mean adaptive slope = {:+.4f} (theory {:+.1f})".format(mean_ad, GAMMA_THEORY))
    if worst >= DRIFT_OK:
        verdict = "INCONCLUSIVE — the adaptive control itself failed"
    elif ok_sd and abs(mean_ad - GAMMA_THEORY) <= DELTA:
        verdict = ("RESIDUAL IS A CONTROL ARTEFACT — objective-dependence in every "
                   "earlier phase was concentration decay")
    elif ok_sd:
        verdict = "spread collapses but the mean is off -1: report both, claim neither"
    else:
        verdict = "GEOMETRY IS REAL — concentration alone does not explain the surface"
    print("  VERDICT: {}".format(verdict))

    print("\n" + "-" * 82)
    print("P4.3 — the schedule: how beta must move to hold concentration")
    print("-" * 82)
    print("  A measured object with a theoretical counterpart — FKR's informal")
    print("  alpha_0 grows with d, and nothing in the literature says what")
    print("  schedule maintains the operating regime.\n")
    print("  {:<12} {:>5} {:>7} {:>14} {:>14} {:>10}".format(
        "objective", "d", "tau", "beta start", "beta end", "ratio"))
    for o in objs:
        for d in dims:
            for tau in taus:
                _, _, _, _, b0v, b1v, _ = rec[(o, d, tau, "adaptive")]
                print("  {:<12} {:>5} {:>7.3g} {:>14.5g} {:>14.5g} {:>10.3f}".format(
                    o, d, tau, b0v, b1v, b1v / b0v if b0v > 0 else float("nan")))

    print("\n" + "-" * 82)
    print("P4.4 — R^2, reported and disqualified")
    print("-" * 82)
    for arm in arms:
        keys = [(o, d, tau) for o in objs for d in dims for tau in taus]
        y = np.array([rec[(o, d, tau, arm)][0] for (o, d, tau) in keys])
        ltau = np.log(np.array([k[2] for k in keys], float))
        ld = np.log(np.array([k[1] for k in keys], float))
        one = np.ones(len(y))
        ix = {o: i for i, o in enumerate(objs)}
        Do = np.zeros((len(y), len(objs) - 1))
        for i, k in enumerate(keys):
            j = ix[k[0]]
            if j > 0:
                Do[i, j - 1] = 1.0

        def r2(D):
            sol, _, _, _ = np.linalg.lstsq(D, y, rcond=None)
            return 1.0 - float(((y - D @ sol) ** 2).sum() / ((y - y.mean()) ** 2).sum())
        a = r2(np.vstack([ltau, ld, one]).T)
        b = r2(np.column_stack([ltau, ld, one, Do]))
        print("  {:<9} total slope sd = {:.4f}   R^2(tau,d) = {:.4f}   +objective = {:.4f}   gain {:.4f}".format(
            arm, float(np.std(y, ddof=1)), a, b, b - a))
    print("\n  If the spreads above are small, these gains are noise ratios and")
    print("  carry no information. That is why R^2 is not a criterion here.")

    print("\n" + "-" * 82)
    print("P4.5 — full table")
    print("-" * 82)
    print("  {:<12} {:>5} {:>7} {:<9} {:>9} {:>19} {:>14}".format(
        "objective", "d", "tau", "arm", "slope", "95% CI", "verdict"))
    for o in objs:
        for d in dims:
            for tau in taus:
                for arm in arms:
                    sl, lo, hi, dr, b0v, b1v, v = rec[(o, d, tau, arm)]
                    print("  {:<12} {:>5} {:>7.3g} {:<9} {:>9.4f} {:>19} {:>14}".format(
                        o, d, tau, arm, sl, "[{:+.3f},{:+.3f}]".format(lo, hi), v))

    print("\n" + "=" * 82)
    print("wrote control_raw.csv and control_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 82)


if __name__ == "__main__":
    main()
