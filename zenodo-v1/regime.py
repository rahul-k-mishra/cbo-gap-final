"""
regime.py  —  CBO-GAP Phase 6: the four things the referee said were missing

WHAT THIS SCRIPT IS FOR
-----------------------
A referee read the v0.2 manuscript and found one real mathematical error and
four claims stated more strongly than the evidence supports. The error is
recorded below because it changes nothing in this script but must not be lost.
The four experimental gaps are what this script closes.

  THE ERROR, for the record. Lemma 5.1 of v0.2 asserted ESS <= 1/max_i w_i.
  That is backwards. From sum_i w_i^2 <= (max_i w_i) sum_i w_i = max_i w_i one
  gets ESS = 1/sum w^2 >= 1/max_i w_i. The valid pair is
        1/w_max  <=  ESS  <=  1/w_max^2,
  and the saturation statement does not need either: with normalized weights,
  sum_i w_i^2 <= sum_i w_i = 1 with equality iff every weight is 0 or 1, so
  ESS = 1 exactly when one weight is 1. Corollary 5.2 survives on that argument.

  PART A — THE REFERENCE ENSEMBLE IS NOT THE MEAN-FIELD LIMIT.
      The d = 2 slope moved 1.313 -> 1.205 -> 1.179 as the reference grew from
      12500 to 50000. That is a material bias in the direction of the theory,
      which means every absolute exponent reported so far is contaminated.
      Fix: measure at 12500, 25000, 50000 and 100000 and extrapolate
      gamma(Jinf) = gamma_inf + a/Jinf, reporting the extrapolated limit with a
      bootstrap interval instead of a 50000-particle proxy value.
      All four are fitted on a COMMON J grid capped at 1250 = 12500/10, so the
      comparison is not contaminated by different fitting ranges.

  PART B — NAMED BENCHMARKS ARE NOT A SCIENTIFIC UNIT.
      Six named functions cannot separate "which function" from "which landscape
      property". Fix: twelve synthetic landscapes with condition number,
      modality amplitude and ruggedness frequency varied independently, on a
      common family
          f(x) = sum_i a_i x_i^2 + rho * sum_i (1 - cos(omega x_i)),
          a_i = kappa^((i-1)/(d-1)),
      so kappa is the condition number, rho the modality amplitude and omega the
      ruggedness frequency, and each can be moved without moving the others.

  PART C — THE MISSING 72 PERCENT, AND WHETHER IT IS PREDICTABLE.
      Concentration plus dimension explained R^2 = 0.28 of the slope. A model
      fitted on the synthetics and tested on the six named benchmarks answers
      whether the remainder is structure or noise. Eleven per-cell features are
      recorded: initial, minimum, mean and integrated log ESS, ESS decay,
      weighted covariance trace, consensus displacement, objective variance,
      initial distance to the minimizer, beta and the target.
      Three nested models are fitted and scored OUT OF SAMPLE:
          M1: dimension and target only
          M2: + the ESS trajectory features
          M3: + the geometry features
      If M3 does not beat M2 out of sample, the remainder is not explained by
      these features and the paper says so.

  PART D — ONE HORIZON AND ONE INITIALIZATION IS NOT A STUDY.
      T in {0.5, 1, 2} and two initializations, since the constants under audit
      grow exponentially in T and the principal result so far sits entirely in
      the favourable centred case.

TERMINOLOGY, CORRECTED
----------------------
The proven exponent for the squared coupled error is -1. A fitted slope of -0.85
is NOT that rate; it is 15 percent flatter in the exponent. This script therefore
reports
      delta = -1 - slope_hat
and calls a cell RATE-CONSISTENT AT TOLERANCE 0.15 when the bootstrap interval
excludes slopes flatter than -0.85. It never calls this "recovering the proven
rate". The v0.2 wording was wrong and is not reused.

CURVATURE, PROPERLY TESTED
--------------------------
v0.2 claimed the log-log curves are straight by comparing two half-range slopes.
That is an eyeball test. Here a quadratic term is fitted,
      log E = a + b log J + c (log J)^2,
with a bootstrap interval on c. Straightness is claimed only if that interval
contains zero, and only for the measured range of J — never for all J.

WHAT THIS SCRIPT STILL DOES NOT DO
----------------------------------
It does not measure the end-to-end optimization error. The estimator is the
coupled distance between a finite ensemble and a large reference ensemble, which
audits the mean-field approximation component and not the global convergence
statement. Conflating the two was a framing error in v0.2 and the title is being
changed accordingly.

It does not sweep sigma toward the 2*lambda > d*sigma^2 boundary.

HOW TO RUN
----------
    python regime.py --workers 3 --quick                 (smoke test, ~4 min)
    python regime.py --workers 3 --part A                (~20 min)
    python regime.py --workers 3 --part B                (~1.7 h)
    python regime.py --workers 3 --part C                (~50 min)
    python regime.py --workers 3 --part D                (~50 min)
    python regime.py --workers 3 --part BC               (B and C, then the model)
    python regime.py --workers 3 --part ALL              (~4 h)

Parts B and C must both have been run before the predictive model can be fitted;
running --part BC does both and fits it. Each part writes its own CSV, and
--part model refits from the CSVs already on disk without recomputing.

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

TOL = 0.15
THRESH = -1.0 + TOL          # -0.85
N_BOOT = 400


# ----------------------------------------------------------------------
# objectives: six named, twelve synthetic
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

# synthetic family: condition number kappa, modality amplitude rho, frequency omega
SYNTH = []
for _k in (1.0, 100.0):
    for _r in (0.0, 5.0, 20.0):
        for _w in (1.0, 3.0):
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


# ----------------------------------------------------------------------
# effective sample size, exactly in log space
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


def draw_initial(rng, n, d, xstar, init):
    if init == "centred":
        return rng.standard_normal((n, d)) + xstar
    X = rng.standard_normal((n, d)) + xstar + 3.0
    near = rng.random(n) < 0.1
    X[near] = rng.standard_normal((int(near.sum()), d)) + xstar
    return X


# ----------------------------------------------------------------------
# one coupled realisation, with feature extraction
# ----------------------------------------------------------------------

def one_realisation(name, d, init, beta, sigma, dt, K, Jinf, J_list, seed):
    f, xstar = objective(name)
    rng = np.random.default_rng(seed)
    X0 = draw_initial(rng, Jinf, d, xstar, init)
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    les, ctr, disp, fvar = [], [], [], []
    dist0 = float(np.mean(np.linalg.norm(X0 - xstar, axis=1)))
    sq = math.sqrt(dt)

    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        fv = f(Xref)
        fc = fv - fv.min()
        les.append(log_ess(fc, beta))
        fvar.append(float(np.var(fv)))
        w = np.exp(-beta * fc)
        w = w / w.sum()
        va = (w[:, None] * Xref).sum(axis=0)
        # weighted covariance trace, and the gap between weighted and plain mean
        ctr.append(float((w * np.sum((Xref - va) ** 2, axis=1)).sum()))
        disp.append(float(np.linalg.norm(va - Xref.mean(axis=0))))
        dref = Xref - va
        Xref = Xref - dt * dref + sigma * np.linalg.norm(dref, axis=1)[:, None] * dW
        for J in J_list:
            Xj = Xsub[J]
            fj = f(Xj)
            wj = np.exp(-beta * (fj - fj.min()))
            dj = Xj - (wj[:, None] * Xj).sum(axis=0) / wj.sum()
            Xsub[J] = Xj - dt * dj + sigma * np.linalg.norm(dj, axis=1)[:, None] * dW[:J]
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1), out=runmax[J])

    les = np.array(les)
    feats = {
        "le0": float(les[0]), "lemin": float(les.min()),
        "lemean": float(les.mean()), "leint": float(les.sum() * dt),
        "ledecay": float(les[0] - les.min()),
        "covtr": float(np.mean(ctr)), "disp": float(np.mean(disp)),
        "fvar": float(np.mean(fvar)), "dist0": dist0,
    }
    return {J: float(np.mean(runmax[J])) for J in J_list}, feats


def task(a):
    (name, d, init, tau, beta, sigma, dt, K, Jinf, J_list, T, seed) = a
    per_J, feats = one_realisation(name, d, init, beta, sigma, dt, K,
                                   Jinf, J_list, seed)
    return name, d, init, tau, beta, Jinf, T, per_J, feats


# ----------------------------------------------------------------------
# fitting
# ----------------------------------------------------------------------

def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def fit_curv(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 4:
        return float("nan")
    x = np.log(J[m])
    A = np.vstack([x * x, x, np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def boot(per_real, J_sel, fn, seed=7):
    R = len(per_real[J_sel[0]])
    M = np.array([[per_real[J][r] for J in J_sel] for r in range(R)])
    Jv = np.array(J_sel, float)
    rng = np.random.default_rng(seed)
    out = [fn(Jv, M[rng.integers(0, R, R)].mean(axis=0)) for _ in range(N_BOOT)]
    out = np.array([o for o in out if np.isfinite(o)])
    if out.size < 20:
        return float("nan"), float("nan")
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


FEATNAMES = ["le0", "lemin", "lemean", "leint", "ledecay",
             "covtr", "disp", "fvar", "dist0"]


def run_cells(cells, args, tag):
    """cells: list of (name, d, init, tau, Jinf, T). Returns per-cell records."""
    tasks, s = [], args.seed
    beta_of = {}
    for (name, d, init, tau, Jinf, T) in cells:
        f, xstar = objective(name)
        rng = np.random.default_rng(4242 + 131 * d + 17 * len(name))
        Xp = draw_initial(rng, 4000, d, xstar, init)
        fv = f(Xp)
        b = solve_beta(fv - fv.min(), math.log(tau * 4000))
        beta_of[(name, d, init, tau)] = b
    for (name, d, init, tau, Jinf, T) in cells:
        K = int(round(T / args.dt))
        J_list = [J for J in args.Jgrid if J <= Jinf // 10]
        for _ in range(args.M):
            s += 1
            tasks.append((name, d, init, tau, beta_of[(name, d, init, tau)],
                          args.sigma, args.dt, K, Jinf, J_list, T, s))
    print("  [{}] {} realisations on {} workers".format(tag, len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  [{}] done in {:.1f} s".format(tag, time.time() - t0))

    agg = {}
    for name, d, init, tau, beta, Jinf, T, per_J, feats in res:
        k = (name, d, init, tau, Jinf, T)
        if k not in agg:
            agg[k] = {"beta": beta, "E": {}, "F": {f: [] for f in FEATNAMES}}
        for J, v in per_J.items():
            agg[k]["E"].setdefault(J, []).append(v)
        for f in FEATNAMES:
            agg[k]["F"][f].append(feats[f])
    return agg


def cell_summary(agg, J_fit=None):
    rows = {}
    for k, r in agg.items():
        Js = sorted(r["E"]) if J_fit is None else [J for J in sorted(r["E"]) if J <= J_fit]
        E = np.array([np.mean(r["E"][J]) for J in Js])
        sl = fit_slope(np.array(Js, float), E)
        lo, hi = boot(r["E"], Js, fit_slope)
        c = fit_curv(np.array(Js, float), E)
        clo, chi = boot(r["E"], Js, fit_curv)
        F = {f: float(np.mean(r["F"][f])) for f in FEATNAMES}
        rows[k] = dict(slope=sl, lo=lo, hi=hi, curv=c, clo=clo, chi=chi,
                       beta=r["beta"], **F)
    return rows


def verdict(hi):
    return "rate-consistent" if hi <= THRESH else "not rate-consistent"


def write_csv(path, rows, extra_cols=()):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "d", "init", "tau", "Jinf", "T", "beta", "slope",
                    "delta", "ci_lo", "ci_hi", "curv", "curv_lo", "curv_hi",
                    "verdict"] + FEATNAMES)
        for k in sorted(rows):
            r = rows[k]
            w.writerow(list(k[:1]) + [k[1], k[2], k[3], k[4], k[5],
                       "{:.6g}".format(r["beta"]), "{:.6f}".format(r["slope"]),
                       "{:.6f}".format(-1.0 - r["slope"]),
                       "{:.6f}".format(r["lo"]), "{:.6f}".format(r["hi"]),
                       "{:.6g}".format(r["curv"]), "{:.6g}".format(r["clo"]),
                       "{:.6g}".format(r["chi"]), verdict(r["hi"])] +
                      ["{:.6g}".format(r[f]) for f in FEATNAMES])


# ----------------------------------------------------------------------
# the predictive model
# ----------------------------------------------------------------------

def design(rows, keys, feats):
    cols = []
    for f in feats:
        if f == "logd":
            cols.append(np.log([k[1] for k in keys]))
        elif f == "logtau":
            cols.append(np.log([k[3] for k in keys]))
        else:
            v = np.array([rows[k][f] for k in keys], float)
            cols.append(v)
    A = np.column_stack(cols + [np.ones(len(keys))])
    return A


def fit_predict(rows_tr, keys_tr, rows_te, keys_te, feats):
    A = design(rows_tr, keys_tr, feats)
    y = np.array([rows_tr[k]["slope"] for k in keys_tr])
    mu, sd = A[:, :-1].mean(axis=0), A[:, :-1].std(axis=0)
    sd[sd == 0] = 1.0
    As = np.column_stack([(A[:, :-1] - mu) / sd, np.ones(len(keys_tr))])
    sol, _, _, _ = np.linalg.lstsq(As, y, rcond=None)
    r2_in = 1 - ((y - As @ sol) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    B = design(rows_te, keys_te, feats)
    Bs = np.column_stack([(B[:, :-1] - mu) / sd, np.ones(len(keys_te))])
    yt = np.array([rows_te[k]["slope"] for k in keys_te])
    r2_out = 1 - ((yt - Bs @ sol) ** 2).sum() / ((yt - yt.mean()) ** 2).sum()
    rmse = float(np.sqrt(((yt - Bs @ sol) ** 2).mean()))
    return float(r2_in), float(r2_out), rmse


def load_rows(path):
    rows, keys = {}, []
    if not os.path.exists(path):
        return rows, keys
    for r in csv.DictReader(open(path)):
        k = (r["name"], int(r["d"]), r["init"], float(r["tau"]),
             int(r["Jinf"]), float(r["T"]))
        d = {f: float(r[f]) for f in FEATNAMES}
        d["slope"] = float(r["slope"])
        rows[k] = d
        keys.append(k)
    return rows, keys


def run_model():
    print("\n" + "-" * 82)
    print("P6.3 — the missing variance: nested models, scored OUT OF SAMPLE")
    print("-" * 82)
    rb, kb = load_rows("regime_B_synth.csv")
    rc, kc = load_rows("regime_C_named.csv")
    if not kb or not kc:
        print("  need both regime_B_synth.csv and regime_C_named.csv; run --part BC")
        return
    print("  train: {} synthetic cells   test: {} named-benchmark cells".format(len(kb), len(kc)))
    print("  Out-of-sample R^2 is the number that matters. In-sample R^2 always")
    print("  rises when features are added and is reported only for contrast.\n")
    M1 = ["logd", "logtau"]
    M2 = M1 + ["le0", "lemin", "lemean", "leint", "ledecay"]
    M3 = M2 + ["covtr", "disp", "fvar", "dist0"]
    print("  {:<34} {:>10} {:>12} {:>10}".format("model", "R2 in", "R2 out", "RMSE out"))
    prev = None
    for nm, fs in (("M1  dimension + target", M1),
                   ("M2  + ESS trajectory", M2),
                   ("M3  + geometry", M3)):
        a, b, c = fit_predict(rb, kb, rc, kc, fs)
        gain = "" if prev is None else "   (out-of-sample gain {:+.4f})".format(b - prev)
        prev = b
        print("  {:<34} {:>10.4f} {:>12.4f} {:>10.4f}{}".format(nm, a, b, c, gain))
    print("\n  A negative out-of-sample R^2 means the model predicts worse than")
    print("  the test-set mean: the features do not transfer from synthetic")
    print("  landscapes to named benchmarks, and the paper must say so.")


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--part", default="ALL",
                   help="A, B, C, D, BC, model, or ALL")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=0)
    p.add_argument("--sigma", type=float, default=0.2)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--seed", type=int, default=20260824)
    args = p.parse_args()
    args.M = 12
    args.Jgrid = [10, 20, 40, 80, 160, 320, 640, 1250, 2500, 5000]

    if args.quick:
        args.M = 3
        args.Jgrid = [10, 40, 160, 400]
    if args.realisations:
        args.M = args.realisations

    print("=" * 82)
    print("CBO-GAP Phase 6 — reference limit, synthetic landscapes, prediction, horizon")
    print("=" * 82)
    print("  TERMINOLOGY: the proven exponent is -1. A slope of -0.85 is NOT that")
    print("  rate. Cells are called RATE-CONSISTENT AT TOLERANCE {:.2f} when the".format(TOL))
    print("  bootstrap interval excludes slopes flatter than {:+.2f}. delta = -1 - slope.".format(THRESH))
    print("  Straightness on log-log axes is tested with a quadratic term and is")
    print("  claimed only for the measured range of J.")
    print("  sigma {}  dt {}  realisations/cell {}".format(args.sigma, args.dt, args.M))
    part = args.part.upper()

    # ---------------- PART A ----------------
    if part in ("A", "ALL"):
        print("\n" + "-" * 82)
        print("P6.1 — reference-ensemble extrapolation")
        print("-" * 82)
        Jinfs = [12500, 25000, 50000] if args.quick else [12500, 25000, 50000, 100000]
        if args.quick:
            Jinfs = [2000, 4000]
        objsA = ["ackley", "sphere", "rosenbrock"]
        dA = 10
        cells = [(o, dA, "centred", 0.1, Ji, 1.0) for o in objsA for Ji in Jinfs]
        agg = run_cells(cells, args, "A")
        Jcap = min(Jinfs) // 10
        rows = cell_summary(agg, J_fit=Jcap)
        write_csv("regime_A_reference.csv", rows)
        print("\n  All slopes fitted on the COMMON grid J <= {}, so the comparison".format(Jcap))
        print("  is not contaminated by different fitting ranges.\n")
        print("  {:<12}".format("objective") +
              "".join("{:>22}".format("Jinf=" + str(J)) for J in Jinfs) +
              "{:>26}".format("extrapolated Jinf->inf"))
        for o in objsA:
            line = "  {:<12}".format(o)
            xs, ys = [], []
            for Ji in Jinfs:
                r = rows[(o, dA, "centred", 0.1, Ji, 1.0)]
                line += "{:>22}".format("{:+.3f} [{:+.3f},{:+.3f}]".format(
                    r["slope"], r["lo"], r["hi"]))
                xs.append(1.0 / Ji)
                ys.append(r["slope"])
            A = np.vstack([np.array(xs), np.ones(len(xs))]).T
            sol, _, _, _ = np.linalg.lstsq(A, np.array(ys), rcond=None)
            line += "{:>26}".format("{:+.4f}".format(sol[1]))
            print(line)
        print("\n  The extrapolation fits slope(Jinf) = gamma_inf + a/Jinf. If the")
        print("  extrapolated value differs materially from the Jinf=50000 column,")
        print("  every absolute exponent in the earlier phases is biased and must")
        print("  be reported as a proxy value, not as a mean-field quantity.")

    # ---------------- PART B ----------------
    if part in ("B", "BC", "ALL"):
        print("\n" + "-" * 82)
        print("P6.2 — synthetic landscapes with independently varied properties")
        print("-" * 82)
        print("  f(x) = sum_i a_i x_i^2 + rho sum_i (1 - cos(omega x_i)),  a_i = kappa^(i/(d-1))")
        print("  kappa = condition number, rho = modality amplitude, omega = ruggedness\n")
        names = [n for n, _, _, _ in SYNTH]
        dims = [5, 10] if args.quick else [5, 10, 40]
        taus = [0.1] if args.quick else [0.1, 0.01]
        if args.quick:
            names = names[:3]
        cells = [(n, d, "centred", t, 50000 if not args.quick else 4000, 1.0)
                 for n in names for d in dims for t in taus]
        agg = run_cells(cells, args, "B")
        rows = cell_summary(agg)
        write_csv("regime_B_synth.csv", rows)
        print("  {:<20} {:>5} {:>7} {:>9} {:>9} {:>19} {:>18}".format(
            "landscape", "d", "tau", "slope", "delta", "95% CI", "verdict"))
        for k in sorted(rows):
            r = rows[k]
            print("  {:<20} {:>5} {:>7.3g} {:>9.4f} {:>9.4f} {:>19} {:>18}".format(
                k[0], k[1], k[3], r["slope"], -1.0 - r["slope"],
                "[{:+.3f},{:+.3f}]".format(r["lo"], r["hi"]), verdict(r["hi"])))
        cs = [rows[k]["curv"] for k in rows]
        zero_in = sum(1 for k in rows if rows[k]["clo"] <= 0 <= rows[k]["chi"])
        print("\n  curvature term: median {:+.4g}, interval contains zero in {}/{} cells".format(
            float(np.median(cs)), zero_in, len(rows)))

    # ---------------- PART C ----------------
    if part in ("C", "BC", "ALL"):
        print("\n" + "-" * 82)
        print("P6.2b — the six named benchmarks, held out as a TEST set")
        print("-" * 82)
        names = list(NAMED) if not args.quick else ["ackley", "rosenbrock"]
        dims = [5, 10] if args.quick else [5, 10, 40]
        taus = [0.1] if args.quick else [0.1, 0.01]
        cells = [(n, d, "centred", t, 50000 if not args.quick else 4000, 1.0)
                 for n in names for d in dims for t in taus]
        agg = run_cells(cells, args, "C")
        rows = cell_summary(agg)
        write_csv("regime_C_named.csv", rows)
        print("  {:<14} {:>5} {:>7} {:>9} {:>9} {:>19} {:>18}".format(
            "objective", "d", "tau", "slope", "delta", "95% CI", "verdict"))
        for k in sorted(rows):
            r = rows[k]
            print("  {:<14} {:>5} {:>7.3g} {:>9.4f} {:>9.4f} {:>19} {:>18}".format(
                k[0], k[1], k[3], r["slope"], -1.0 - r["slope"],
                "[{:+.3f},{:+.3f}]".format(r["lo"], r["hi"]), verdict(r["hi"])))

    # ---------------- PART D ----------------
    if part in ("D", "ALL"):
        print("\n" + "-" * 82)
        print("P6.4 — horizon and initialization sensitivity")
        print("-" * 82)
        names = ["ackley", "rastrigin", "sphere", "rosenbrock"]
        if args.quick:
            names = ["ackley"]
        Ts = [0.5, 1.0, 2.0] if not args.quick else [0.5, 1.0]
        inits = ["centred", "mix-0.1"]
        cells = [(n, 10, ini, 0.1, 50000 if not args.quick else 4000, T)
                 for n in names for ini in inits for T in Ts]
        agg = run_cells(cells, args, "D")
        rows = cell_summary(agg)
        write_csv("regime_D_horizon.csv", rows)
        print("  {:<14} {:<10}".format("objective", "init") +
              "".join("{:>16}".format("T=" + str(T)) for T in Ts))
        for n in names:
            for ini in inits:
                line = "  {:<14} {:<10}".format(n, ini)
                for T in Ts:
                    r = rows[(n, 10, ini, 0.1, 50000 if not args.quick else 4000, T)]
                    line += "{:>16}".format("{:+.3f}{}".format(
                        r["slope"], "*" if r["hi"] > THRESH else ""))
                print(line)
        print("\n  * = not rate-consistent at tolerance {:.2f}.".format(TOL))
        print("  The constants under audit grow exponentially in T, so any trend")
        print("  here bears directly on Section 4 of the manuscript.")

    if part in ("BC", "ALL", "MODEL"):
        run_model()

    print("\n" + "=" * 82)
    print("done")
    print("=" * 82)


if __name__ == "__main__":
    main()
