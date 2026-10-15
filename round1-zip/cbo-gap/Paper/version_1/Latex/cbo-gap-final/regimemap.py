"""
regimemap.py  —  CBO-GAP Phase 11: the regime map, the onset curve, and the
                 diffusion-energy question answered properly

WHY THIS EXISTS
---------------
A referee raised seventy points on v0.3. The statistical ones were closed by
audit.py without new simulation, and three of them damaged the manuscript:

  * the noise floor is 0.0219 (median delta-method SE of the fitted slope over
    1344 cells, IQR [0.016, 0.029]), not the 0.055 the manuscript quoted, so
    every effect previously dismissed as "inside the noise floor" must be
    re-judged against a yardstick 2.5 times smaller;
  * with intervals attached, the claim that r does not move the exponent inside
    the condition FAILS at d = 10, where the coefficients are -0.047
    [-0.102,-0.002] and -0.058 [-0.121,-0.015];
  * the free-breakpoint intervals for the degradation onset are [1.00,1.50],
    [1.25,3.00], [1.00,1.50] and [2.00,3.00]. Three of four contain the
    theoretical boundary r = 1, so "onset near r = 1.5" is not established.

Two things then need new simulation, and one needs a definition.

THE DEFINITION, WHICH CHANGES THE INTERPRETATION OF PHASE 9
------------------------------------------------------------
The referee asked what "equal noise" means for two different diffusion
operators. Writing them out settles it. With v the consensus point,

    isotropic     dX = -lambda (X - v) dt + sigma |X - v| dB,
    anisotropic   dX = -lambda (X - v) dt + sigma diag(X - v) dB,

the instantaneous diffusion covariance and its trace are

    isotropic     sigma^2 |X-v|^2 I_d,        trace = d sigma^2 |X-v|^2,
    anisotropic   sigma^2 diag((X-v)^2),      trace =   sigma^2 |X-v|^2.

So at a COMMON sigma the isotropic system injects d times the total quadratic
variation. Matching the trace requires sigma_aniso = sqrt(d) sigma_iso, which is
EXACTLY the matched-r condition of Phase 9, since r_iso = d sigma^2/(2 lambda)
and r_aniso = sigma^2/(2 lambda).

That is not a coincidence and it inverts the reading given in v0.3. Phase 9
described matched-r as an unfair comparison that handed anisotropic sqrt(d)
times the noise, and matched-sigma as the clean one. The algebra says the
opposite: matched r IS matched diffusion energy, and matched sigma is matched
per-coordinate scale while the total injected noise differs by a factor of d.
Both comparisons are legitimate and they answer different questions. Neither is
"the" equal-noise comparison, and the manuscript must say which metric each
table uses. This script measures the realised trace in both arms so the claim
rests on a measurement and not only on the algebra.

WHAT IS MEASURED
----------------
  PART M — THE REGIME MAP.
      tau_0 x r x diffusion at two dimensions. This is the figure the referee
      identified as the paper's best available summary: concentration on one
      axis, distance from the parameter condition on the other, the fitted
      exponent as the value, with the theoretical boundary r = 1 drawn on it.
      It also tests directly whether the two axes interact, which Table 3 of
      the manuscript suggests (the dimension effect is 0.030 at tau_0 = 0.5 and
      0.553 at tau_0 = 0.01) but which has never been measured jointly with r.

  PART D — THE ONSET CURVE.
      r_onset(d) across d in {5,10,20,40,80} on a grid refined near the
      boundary. Phase 10 used two dimensions and could not say whether the
      onset moves with d. If r_onset is constant, the sufficient condition is
      the right normalisation and its boundary is merely conservative. If
      r_onset falls with d, the condition is the wrong normalisation and the
      manuscript can say so with a curve rather than an anecdote.

PER-REALIZATION STORAGE
-----------------------
Every previous script stored cell means and standard errors only. That made a
paired analysis of the two diffusion arms impossible even though they shared
seeds, and audit.py had to fall back on an unpaired, conservative interval.
This script writes one row per realization per cell, with the slope fitted
within that realization. Paired differences, equivalence tests and change-point
intervals can then be computed exactly.

PRE-REGISTERED, fixed before the first run
-------------------------------------------
  delta = -1 - slope_hat. RATE-CONSISTENT AT TOLERANCE 0.15 iff the bootstrap
  95 percent upper bound is at or below -0.85; counts also at 0.10 and 0.20,
  and with Bonferroni adjustment. The proven exponent is -1 and a slope of
  -0.85 is never called that rate.

  Bootstrap unit: the independent coupled realization. 400 resamples,
  percentile interval, seed 7. For the two-arm comparison the resample is
  PAIRED on the shared realization index.

  EQUIVALENCE, not absence of significance: two one-sided tests at margin 0.05.
  A cell is declared equivalent only if the whole interval for the paired
  difference lies inside the margin.

  ONSET: free-breakpoint profile least squares in log r, bootstrap interval
  over objectives and realizations. The onset is declared to differ from the
  theoretical boundary only if the interval excludes r = 1.

  THE MAP IS INFORMATIVE iff the fitted exponent varies by more than 0.10
  across the tau_0 axis at fixed r AND more than 0.10 across the r axis at
  fixed tau_0. If it varies on only one axis, the other is not part of the
  story and the manuscript should stop claiming it is.

WHAT THIS STILL DOES NOT DO
---------------------------
It does not measure the end-to-end optimization error; the estimator is the
coupled distance to a reference ensemble of 50000, a proxy and not the
mean-field limit. Horizon fixed at T = 1, centred initial law, three objectives.
Outside the condition FKR Theorem 3.7 says nothing, so anything measured there
is not evidence about that theorem.

HOW TO RUN
    python regimemap.py --workers 3 --quick     (smoke test, ~5 min)
    python regimemap.py --workers 3 --part M    (regime map, ~7 h)
    python regimemap.py --workers 3 --part D    (onset curve, ~7 h)
    python regimemap.py --workers 3             (both, ~14 h)

NumPy only. No SciPy. Python 3.8 compatible.
Writes regimemap_real.csv (one row per realization), regimemap_summary.csv.
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
EQUIV = 0.05
N_BOOT = 400
BOOT_SEED = 7
SIGMA_FLOOR = 0.0219      # measured, see audit.py


def f_ackley(X):
    d = X.shape[1]
    s1 = np.sqrt(np.sum(X * X, axis=1) / d)
    s2 = np.sum(np.cos(2.0 * np.pi * X), axis=1) / d
    return -20.0 * np.exp(-0.2 * s1) - np.exp(s2) + 20.0 + math.e


def f_rastrigin(X):
    return np.sum(X * X + 10.0 * (1.0 - np.cos(2.0 * np.pi * X)), axis=1)


def f_sphere(X):
    return np.sum(X * X, axis=1)


OBJ = {"ackley": f_ackley, "rastrigin": f_rastrigin, "sphere": f_sphere}


def sigma_of(diff, d, r, lam=1.0):
    """r = 1 is the boundary of the parameter condition for each diffusion
    type: 2 lambda > d sigma^2 isotropic, 2 lambda > sigma^2 anisotropic.
    By the trace calculation in the header, matching r also matches the total
    injected quadratic variation."""
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


def fit_slope(J, E):
    m = np.isfinite(E) & (E > 0)
    if m.sum() < 3:
        return float("nan")
    A = np.vstack([np.log(J[m]), np.ones(m.sum())]).T
    return float(np.linalg.lstsq(A, np.log(E[m]), rcond=None)[0][0])


def one_realisation(name, d, diff, beta, sigma, lam, dt, K, Jinf, J_list, seed):
    f = OBJ[name]
    rng = np.random.default_rng(seed)
    X0 = rng.standard_normal((Jinf, d))
    Xref = X0.copy()
    Xsub = {J: X0[:J].copy() for J in J_list}
    runmax = {J: np.zeros(J) for J in J_list}
    les, qv = [], []
    sq = math.sqrt(dt)

    def step(X, dW, track=False):
        fv = f(X)
        fc = fv - fv.min()
        w = np.exp(-beta * fc)
        m = (w[:, None] * X).sum(axis=0) / w.sum()
        dv = X - m
        if diff == "isotropic":
            noise = sigma * np.linalg.norm(dv, axis=1)[:, None] * dW
            # trace of the diffusion covariance, d sigma^2 |x-v|^2
            tr = float(np.mean(d * sigma ** 2 * np.sum(dv * dv, axis=1)))
        else:
            noise = sigma * dv * dW
            # trace of the diffusion covariance, sigma^2 |x-v|^2
            tr = float(np.mean(sigma ** 2 * np.sum(dv * dv, axis=1)))
        if track:
            qv.append(tr)
        return X - lam * dt * dv + noise, fc

    for _ in range(K):
        dW = rng.standard_normal((Jinf, d)) * sq
        Xref, fc = step(Xref, dW, track=True)
        les.append(log_ess(fc, beta))
        for J in J_list:
            Xsub[J], _ = step(Xsub[J], dW[:J])
            np.maximum(runmax[J], np.sum((Xsub[J] - Xref[:J]) ** 2, axis=1),
                       out=runmax[J])

    les = np.array(les)
    E = np.array([float(np.mean(runmax[J])) for J in J_list])
    sl = fit_slope(np.array(J_list, float), E)
    return dict(slope=sl, E=E, le0=float(les[0]), lebar=float(les.mean()),
                lemin=float(les.min()), qv=float(np.mean(qv)),
                spread=float(np.mean(np.linalg.norm(Xref - Xref.mean(axis=0), axis=1))))


def task(a):
    (part, name, d, diff, r, tau, rep, beta, sigma, lam, dt, K, Jinf, J_list, seed) = a
    out = one_realisation(name, d, diff, beta, sigma, lam, dt, K, Jinf, J_list, seed)
    return part, name, d, diff, r, tau, rep, beta, sigma, out


def boot_ci(slopes, level=95.0, seed=BOOT_SEED):
    s = np.array([x for x in slopes if np.isfinite(x)])
    if s.size < 3:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    bs = [float(np.mean(rng.choice(s, s.size, replace=True))) for _ in range(N_BOOT)]
    lo = (100.0 - level) / 2.0
    return float(np.percentile(bs, lo)), float(np.percentile(bs, 100.0 - lo))


def paired_ci(a, b, level=90.0, seed=BOOT_SEED):
    """Paired on the shared realization index. This is what could not be done
    from the earlier files, which stored cell means only."""
    n = min(len(a), len(b))
    dif = np.array(b[:n]) - np.array(a[:n])
    dif = dif[np.isfinite(dif)]
    if dif.size < 3:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    bs = [float(np.mean(rng.choice(dif, dif.size, replace=True))) for _ in range(1000)]
    lo = (100.0 - level) / 2.0
    return float(dif.mean()), float(np.percentile(bs, lo)), float(np.percentile(bs, 100.0 - lo))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--part", default="both", help="M, D or both")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--realisations", type=int, default=12)
    p.add_argument("--lam", type=float, default=1.0)
    p.add_argument("--dt", type=float, default=0.01)
    p.add_argument("--T", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=20260829)
    args = p.parse_args()

    K = int(round(args.T / args.dt))
    M = 3 if args.quick else args.realisations
    diffs = ["isotropic", "anisotropic"]
    objs = ["ackley", "rastrigin", "sphere"]
    parts = {"M": ["M"], "D": ["D"], "BOTH": ["M", "D"]}[args.part.upper()
                                                         if args.part.upper() in ("M", "D")
                                                         else "BOTH"]

    if args.quick:
        Jinf, Jgrid = 4000, [10, 40, 160, 400]
        objs = ["ackley", "sphere"]
        dimsM, rsM, tausM = [10], [0.5, 2.0], [0.5, 0.01]
        dimsD, rsD = [10, 40], [1.0, 2.0]
    else:
        Jinf, Jgrid = 50000, [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
        dimsM, rsM, tausM = [10, 40], [0.5, 1.0, 1.5, 2.0, 3.0], [0.5, 0.1, 0.03, 0.01]
        dimsD, rsD = [5, 10, 20, 40, 80], [0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
    J_list = [J for J in Jgrid if J <= Jinf // 10]
    tauD = 0.1

    print("=" * 88)
    print("CBO-GAP Phase 11 — regime map, onset curve, diffusion energy")
    print("=" * 88)
    print("  PRE-REGISTERED (fixed before the first run):")
    print("    RATE-CONSISTENT AT TOLERANCE {:.2f} iff bootstrap 95% upper bound <= {:+.2f};".format(TOL, THRESH))
    print("    counts also at {} and with Bonferroni adjustment.".format(TOLS))
    print("    Bootstrap unit: the independent coupled realization; the two-arm")
    print("    comparison resamples PAIRED on the shared realization index.")
    print("    EQUIVALENCE by two one-sided tests at margin {:.2f}, not by absence".format(EQUIV))
    print("    of significance. ONSET by free-breakpoint profile least squares;")
    print("    it differs from r = 1 only if the interval excludes 1.")
    print("    Measured noise floor from audit.py: {:.4f}.".format(SIGMA_FLOOR))
    print("\n  DIFFUSION ENERGY, the referee's question answered:")
    print("    isotropic   trace of covariance = d sigma^2 |x-v|^2")
    print("    anisotropic trace of covariance =   sigma^2 |x-v|^2")
    print("    so matched sigma means the isotropic system injects d times the")
    print("    total quadratic variation, and matching the trace requires")
    print("    sigma_aniso = sqrt(d) sigma_iso, which is exactly matched r.")
    print("    Phase 9 called matched r the unfair comparison. The algebra says")
    print("    matched r is the matched-energy comparison. Both arms are")
    print("    legitimate; the realised trace is measured below either way.")
    print("\n  REPRODUCIBILITY")
    print("    python {}   numpy {}".format(platform.python_version(), np.__version__))
    print("    platform {}   workers {}".format(platform.platform(), args.workers))
    print("    seed {}   J grid {}   Jinf {}   reps/cell {}".format(
        args.seed, J_list, Jinf, M))
    print("    lambda {}   dt {}   T {}   steps {}".format(args.lam, args.dt, args.T, K))

    tasks, s = [], args.seed
    beta = {}

    def getbeta(name, d, tau):
        k = (name, d, tau)
        if k not in beta:
            rng = np.random.default_rng(4242 + 131 * d + 7 * len(name))
            Xp = rng.standard_normal((4000, d))
            fv = OBJ[name](Xp)
            beta[k] = solve_beta(fv - fv.min(), math.log(tau * 4000))
        return beta[k]

    ncell = 0
    if "M" in parts:
        ncell += len(diffs) * len(objs) * len(dimsM) * len(rsM) * len(tausM)
    if "D" in parts:
        ncell += len(diffs) * len(objs) * len(dimsD) * len(rsD)
    print("\n  EXPERIMENT MATRIX")
    if "M" in parts:
        print("    part M  2 diff x {} obj x {} d x {} r x {} tau = {}".format(
            len(objs), len(dimsM), len(rsM), len(tausM),
            len(diffs) * len(objs) * len(dimsM) * len(rsM) * len(tausM)))
    if "D" in parts:
        print("    part D  2 diff x {} obj x {} d x {} r x 1 tau = {}".format(
            len(objs), len(dimsD), len(rsD),
            len(diffs) * len(objs) * len(dimsD) * len(rsD)))
    print("    {} cells x {} realizations = {} coupled realizations".format(
        ncell, M, ncell * M))

    for part in parts:
        dims = dimsM if part == "M" else dimsD
        rs = rsM if part == "M" else rsD
        taus = tausM if part == "M" else [tauD]
        for diff in diffs:
            for name in objs:
                for d in dims:
                    for r in rs:
                        sg = sigma_of(diff, d, r, args.lam)
                        for t in taus:
                            b = getbeta(name, d, t)
                            for rep in range(M):
                                s += 1
                                tasks.append((part, name, d, diff, r, t, rep, b, sg,
                                              args.lam, args.dt, K, Jinf, J_list, s))

    print("\n  {} realizations queued on {} workers\n".format(len(tasks), args.workers))
    t0 = time.time()
    if args.workers > 1:
        with Pool(processes=args.workers) as pool:
            res = pool.map(task, tasks, chunksize=1)
    else:
        res = [task(t) for t in tasks]
    print("  sweep finished in {:.1f} s".format(time.time() - t0))

    # ---- per-realization output, so pairing is possible downstream ----
    with open("regimemap_real.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["part", "diffusion", "objective", "d", "r", "tau", "rep",
                    "sigma", "beta", "slope", "delta", "log_ess_0", "log_ess_bar",
                    "log_ess_min", "diff_trace", "final_spread"])
        for part, name, d, diff, r, t, rep, b, sg, o in res:
            w.writerow([part, diff, name, d, r, t, rep, "{:.6g}".format(sg),
                        "{:.6g}".format(b), "{:.6f}".format(o["slope"]),
                        "{:.6f}".format(-1.0 - o["slope"]),
                        "{:.6g}".format(o["le0"]), "{:.6g}".format(o["lebar"]),
                        "{:.6g}".format(o["lemin"]), "{:.6g}".format(o["qv"]),
                        "{:.6g}".format(o["spread"])])

    cell = {}
    for part, name, d, diff, r, t, rep, b, sg, o in res:
        cell.setdefault((part, diff, name, d, r, t), []).append(o)

    rec, rows = {}, []
    nb = len(cell)
    bonf = 100.0 * (1.0 - 0.05 / nb)
    for k, v in sorted(cell.items()):
        sl = [x["slope"] for x in v]
        lo, hi = boot_ci(sl, 95.0)
        blo, bhi = boot_ci(sl, bonf)
        rec[k] = dict(slopes=sl, mean=float(np.nanmean(sl)), lo=lo, hi=hi,
                      blo=blo, bhi=bhi,
                      tau0=float(np.mean([math.exp(min(x["le0"], 700)) for x in v])) / Jinf,
                      taubar=float(np.mean([math.exp(min(x["lebar"], 700)) for x in v])) / Jinf,
                      qv=float(np.mean([x["qv"] for x in v])),
                      spread=float(np.mean([x["spread"] for x in v])))
        rows.append([k[0], k[1], k[2], k[3], k[4], k[5],
                     "{:.6f}".format(rec[k]["mean"]),
                     "{:.6f}".format(-1.0 - rec[k]["mean"]),
                     "{:.6f}".format(lo), "{:.6f}".format(hi),
                     "{:.6f}".format(blo), "{:.6f}".format(bhi),
                     "{:.6g}".format(rec[k]["tau0"]), "{:.6g}".format(rec[k]["taubar"]),
                     "{:.6g}".format(rec[k]["qv"]), "{:.6g}".format(rec[k]["spread"]),
                     "in" if k[4] < 1 else "out",
                     "rate-consistent" if hi <= THRESH else "not rate-consistent"])

    with open("regimemap_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["part", "diffusion", "objective", "d", "r", "tau", "slope",
                    "delta", "ci_lo", "ci_hi", "bonf_lo", "bonf_hi", "tau0",
                    "taubar", "diff_trace", "final_spread", "region", "verdict"])
        w.writerows(rows)

    def ms(part, diff, d, r, t):
        v = [rec[(part, diff, o, d, r, t)]["mean"] for o in objs
             if (part, diff, o, d, r, t) in rec]
        return float(np.mean(v)) if v else float("nan")

    # ---------------- PART M ----------------
    if "M" in parts:
        print("\n" + "-" * 88)
        print("P11.1 — THE REGIME MAP: fitted exponent over tau_0 and r")
        print("-" * 88)
        print("  r = 1 is the boundary of the parameter condition. Values are means")
        print("  over {} objectives; * marks cells not rate-consistent.\n".format(len(objs)))
        for diff in diffs:
            for d in dimsM:
                print("  {} , d = {}".format(diff, d))
                print("    {:>8}".format("tau_0") +
                      "".join("{:>11}".format("r=" + str(r)) for r in rsM))
                for t in tausM:
                    line = "    {:>8g}".format(t)
                    for r in rsM:
                        bad = sum(1 for o in objs
                                  if ("M", diff, o, d, r, t) in rec
                                  and rec[("M", diff, o, d, r, t)]["hi"] > THRESH)
                        line += "{:>11}".format("{:+.3f}{}".format(
                            ms("M", diff, d, r, t), "*" if bad else ""))
                    print(line)
                print("    {:>8}".format("") +
                      "".join("{:>11}".format("in" if r < 1 else "OUT") for r in rsM))
                print()

        print("  variation along each axis, to test whether both matter:")
        print("  {:<13} {:>4} {:>26} {:>26}".format(
            "diffusion", "d", "range over tau_0 (fixed r)", "range over r (fixed tau_0)"))
        okt = okr = True
        for diff in diffs:
            for d in dimsM:
                vt = max(max(ms("M", diff, d, r, t) for t in tausM) -
                         min(ms("M", diff, d, r, t) for t in tausM) for r in rsM)
                vr = max(max(ms("M", diff, d, r, t) for r in rsM) -
                         min(ms("M", diff, d, r, t) for r in rsM) for t in tausM)
                okt &= vt > 0.10
                okr &= vr > 0.10
                print("  {:<13} {:>4} {:>26.4f} {:>26.4f}".format(diff, d, vt, vr))
        print("\n  MAP VERDICT: {}".format(
            "both axes matter" if (okt and okr) else
            ("only the concentration axis matters" if okt else
             ("only the r axis matters" if okr else "neither axis moves the exponent"))))

    # ---------------- PART D ----------------
    if "D" in parts:
        print("\n" + "-" * 88)
        print("P11.2 — THE ONSET CURVE: does the degradation onset move with d?")
        print("-" * 88)
        print("  Mean exponent at tau_0 = {:g}; free-breakpoint estimate with a".format(tauD))
        print("  bootstrap interval over objectives and realizations.\n")
        for diff in diffs:
            print("  {}".format(diff))
            print("    {:>5}".format("d") + "".join("{:>10}".format("r=" + str(r)) for r in rsD)
                  + "{:>12}{:>20}".format("r_onset", "95% CI"))
            for d in dimsD:
                x = np.log(np.array(rsD))
                y = np.array([ms("D", diff, d, r, tauD) for r in rsD])

                def bp(yy):
                    def rss(b):
                        z = np.maximum(x - b, 0.0)
                        A = np.vstack([x, z, np.ones(len(x))]).T
                        sol, _, _, _ = np.linalg.lstsq(A, yy, rcond=None)
                        return float(((yy - A @ sol) ** 2).sum())
                    return math.exp(min(x[:-1], key=rss))
                base = bp(y)
                rng = np.random.default_rng(BOOT_SEED)
                bs = []
                for _ in range(300):
                    yy = []
                    for r in rsD:
                        pool = [sl for o in objs
                                for sl in rec.get(("D", diff, o, d, r, tauD),
                                                  {"slopes": []})["slopes"]]
                        yy.append(float(np.mean(rng.choice(pool, len(pool), replace=True)))
                                  if pool else np.nan)
                    yy = np.array(yy)
                    if np.all(np.isfinite(yy)):
                        bs.append(bp(yy))
                lo, hi = (np.percentile(bs, [2.5, 97.5]) if len(bs) > 20 else (np.nan, np.nan))
                print("    {:>5}".format(d) +
                      "".join("{:>10}".format("{:+.3f}".format(ms("D", diff, d, r, tauD)))
                              for r in rsD) +
                      "{:>12.3f}{:>20}".format(base, "[{:.2f},{:.2f}]".format(lo, hi)))
            print()
        print("  If r_onset is constant in d, the sufficient condition is the right")
        print("  normalisation and its boundary is merely conservative. If it falls")
        print("  with d, the condition is the wrong normalisation.")

    # ---------------- paired comparison ----------------
    print("\n" + "-" * 88)
    print("P11.3 — PAIRED isotropic versus anisotropic, and the realised energy")
    print("-" * 88)
    print("  Paired on the shared realization index, which the earlier files could")
    print("  not support. Equivalence at margin {:.2f} by two one-sided tests.\n".format(EQUIV))
    print("  {:<5} {:>4} {:>6} {:>7} {:>9} {:>19} {:>22} {:>14}".format(
        "part", "d", "r", "tau", "gap", "90% CI", "verdict", "trace ratio"))
    for part in parts:
        dims = dimsM if part == "M" else dimsD
        rs = rsM if part == "M" else rsD
        taus = tausM if part == "M" else [tauD]
        for d in dims:
            for r in rs:
                for t in taus:
                    A = [sl for o in objs
                         for sl in rec.get((part, "isotropic", o, d, r, t),
                                           {"slopes": []})["slopes"]]
                    B = [sl for o in objs
                         for sl in rec.get((part, "anisotropic", o, d, r, t),
                                           {"slopes": []})["slopes"]]
                    if len(A) < 3 or len(B) < 3:
                        continue
                    g, lo, hi = paired_ci(A, B)
                    v = ("EQUIVALENT" if (lo > -EQUIV and hi < EQUIV) else
                         ("DIFFERENT" if (lo > EQUIV or hi < -EQUIV) else "inconclusive"))
                    qi = np.mean([rec[(part, "isotropic", o, d, r, t)]["qv"] for o in objs
                                  if (part, "isotropic", o, d, r, t) in rec])
                    qa = np.mean([rec[(part, "anisotropic", o, d, r, t)]["qv"] for o in objs
                                  if (part, "anisotropic", o, d, r, t) in rec])
                    print("  {:<5} {:>4} {:>6g} {:>7g} {:>9.4f} {:>19} {:>22} {:>14.3f}".format(
                        part, d, r, t, g, "[{:+.3f},{:+.3f}]".format(lo, hi), v,
                        qi / qa if qa > 0 else float("nan")))
    print("\n  The trace ratio is the realised isotropic-to-anisotropic diffusion")
    print("  energy. At matched r it should be near 1, confirming that matched r is")
    print("  the matched-energy comparison and matched sigma is not.")

    # ---------------- tolerance and multiplicity ----------------
    print("\n" + "-" * 88)
    print("P11.4 — tolerance and multiplicity, split by region")
    print("-" * 88)
    print("  {:<6} {:<13} {:>6} {:>12} {:>12} {:>12} {:>16}".format(
        "part", "diffusion", "region", "tol 0.10", "tol 0.15", "tol 0.20", "Bonferroni"))
    for part in parts:
        for diff in diffs:
            for reg in ("in", "out"):
                ks = [k for k in rec if k[0] == part and k[1] == diff
                      and ((k[4] < 1) == (reg == "in"))]
                if not ks:
                    continue
                c = [sum(1 for k in ks if rec[k]["hi"] <= -1.0 + tol) for tol in TOLS]
                nbf = sum(1 for k in ks if rec[k]["bhi"] <= THRESH)
                print("  {:<6} {:<13} {:>6} {:>12} {:>12} {:>12} {:>16}".format(
                    part, diff, reg, "{}/{}".format(c[0], len(ks)),
                    "{}/{}".format(c[1], len(ks)), "{}/{}".format(c[2], len(ks)),
                    "{}/{}".format(nbf, len(ks))))

    print("\n" + "=" * 88)
    print("wrote regimemap_real.csv (per realization) and regimemap_summary.csv")
    print("total wall {:.1f} s".format(time.time() - t0))
    print("=" * 88)


if __name__ == "__main__":
    main()
