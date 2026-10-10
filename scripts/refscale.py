"""
refscale.py  --  CBO-GAP round 2: is the population concentration estimable,
                 and at what reference size?

THE QUESTION, IN PLAIN LANGUAGE
-------------------------------
calprec.py measures the concentration a calibrated beta produces by evaluating
it on a large independent reference sample. Its reference-adequacy check C4
failed at ackley, d = 40, tau0 = 0.01: two independent reference halves of
2,000,000 values disagreed by 0.3455 relative against a 0.10 margin
(logs/calprec-refcheck-v2.log). The cause is the tail of the weight
distribution. At the beta that gives a 1 percent ESS fraction, E[w^2] is
carried by rare points near the minimum, so a finite reference that misses
them understates sum w^2 and overstates tau. The yardstick fails exactly where
the measurement matters most.

Because 0 < w = exp(-beta f) <= 1 for both objectives here (f >= 0), every
moment of w is finite and the central limit theorem guarantees that SOME
reference size suffices. Existence is therefore not in question. This script
asks how large that size is, and whether it can be reached.

WHAT IT DOES
------------
Cells: objective in {ackley, sphere}, d = 40, initial law "centred", and two
nominal targets tau0 in {0.01, 0.1}. That gives four cells. tau0 = 0.1 is the
positive control: C4 passed there in the refcheck run.

  1. CALIBRATION. For each cell, draw ONE calibration sample of
     N_CAL = 1,000,000 objective values with its own seed (kind 11), solve
     beta once with the archived exactcal.beta_on_ensemble, print it to full
     precision, and hold it fixed. The target is nominal. Every result is
     labelled "at beta = X", never "at tau0 = 0.01", until the reference has
     estimated tau(beta).
  2. REFERENCES. For each objective, each size n in the ladder
     4M, 16M, 64M, 256M (1G only by --ladder, after a timing smoke), and
     each of SIX replicates, draw a fully independent reference with its own
     seed (kind 12). Stream it in fixed chunks of --chunk values and evaluate
     BOTH of that objective's betas on the same stream. The realized
     concentration on a reference is tau_hat = ESS / n with
        log ESS = 2 lse(-beta f) - lse(-2 beta f),
     exactly as the archived log_ess_of computes it.
  3. STREAMING. The reference is never held in memory, except on the two
     lowest rungs, which are held only for the equivalence gate E1. For each
     chunk the archived exactcal._logsumexp is applied to a = -beta f and to
     2a. The per-chunk results are combined by applying exactcal._logsumexp to
     the vector of chunk results. Combining per-chunk logsumexps this way is
     mathematically exact. The only new code is that composition and the
     chunked draw, and E1 checks both against the archived function.

  Nothing reimplements dynamics; no trajectories are evolved. Nothing in the
  archive is written to.

PRE-SPECIFIED CRITERIA (fixed 2026-10-09, before first execution)
------------------------------------------------------------------
  E1  EQUIVALENCE GATE. On the two lowest rungs of the ladder in use, every
      replicate's reference is also held in memory, and the archived
      exactcal.log_ess_of is evaluated on the held array at each beta. The
      streamed and held log-ESS must agree to
            |logESS_streamed - logESS_held| / |logESS_held|  <=  1e-12.
      If any comparison fails, the run stops before the higher rungs start
      (exit code 3). The rows already written stay on disk.
      Worked example (illustrative values): streamed 10.596634733096073,
      held 10.596634733096080. The difference is 7e-15, the relative
      difference 6.6e-16, which is at most 1e-12: pass.

  C5  REPLICATE SPREAD (precision). For a cell and rung, take the six
      replicate values tau_hat_1..6 at the cell's fixed beta. median is the
      mean of the 3rd and 4th sorted values, range = max - min. The rung
      passes C5 when
            range / median  <=  0.025.
      Derivation, not choice: the reference exists to adjudicate calprec's
      C1, whose margin is 0.05. For that judgment to be sound, one
      reference's own relative standard error must be at most a fifth of
      that, 0.01. For six independent draws from an approximately normal
      estimator, the expected range is about 2.53 standard deviations, so
      range / median <= 2.53 x 0.01, taken as 0.025. The factor 2.53 assumes
      approximate normality of tau_hat across replicates. C5 measures
      precision only. Bias, where all six replicates miss the rare region in
      the same way, is NOT detected by C5; it is the job of the drift test D1.
      Worked example, pass: sorted values 0.00988 0.00994 0.00997 0.00999
      0.01003 0.01008. Median (0.00997 + 0.00999)/2 = 0.00998, range
      0.00020, ratio 0.0200, at most 0.025: passes C5.
      Worked example, fail: sorted values 0.00982 0.00990 0.00994 0.00996
      0.01001 0.01007. Median 0.00995, range 0.00025, ratio 0.02513, above
      0.025: fails C5, by a small margin.

  D1  DRIFT TEST (bias). A rung passes D1 when its median agrees with the
      median of the NEXT HIGHER rung:
            |median_n - median_next| / median_next  <=  0.025.
      A bias from under-sampling the rare region shows up as a trend in the
      median with size. The top rung has no higher rung, so it cannot pass
      D1 and is reported as "untested".
      Worked example: median 0.00995 at 64M and 0.01003 at 256M give
      |0.00995 - 0.01003| / 0.01003 = 0.0080, at most 0.025: 64M passes D1.

  ADEQUATE. A rung is adequate for a cell when it passes BOTH C5 and D1. The
      top rung is never adequate (D1 untested), whatever its C5 value. The
      smallest adequate rung is reported per cell; if there is none, the
      script prints "no adequate rung in the ladder" for that cell.

  S1  LARGEST-TERM SHARE (reported, no threshold). Per replicate and beta,
      the share of sum w^2 carried by the single largest term, in log space:
            share = exp( max(-2 beta f) - lse(-2 beta f) ).
      A share near 1 means one point dominates sum w^2, so the estimate is
      not converged, whatever C5 says.
      Worked example: max(-2 beta f) = -3.0 and lse(-2 beta f) = -1.0 give
      share = exp(-2.0) = 0.135.

  X1  EXACT VALUE FOR SPHERE (accuracy). For f = ||x||^2 with
      x ~ N(0, I_d) (sphere, centred law, XSTAR = 0), the Gaussian moment
      generating function gives E[w] = (1+2 beta)^(-d/2) and
      E[w^2] = (1+4 beta)^(-d/2). Therefore
            tau(beta) = (1 + 4 beta)^(d/2) / (1 + 2 beta)^d,
      computed in log space. It is printed beside every sphere replicate and
      beside each sphere rung's median, with the relative error of the
      median, (median - tau_exact) / tau_exact. This is the only place in the
      study where accuracy, not just precision, is directly observable. It
      tests whether "adequate" coincides with "accurate".
      Worked example (small d, by hand): d = 2, beta = 0.5 gives
      tau = (1 + 2)^1 / (1 + 1)^2 = 3/4 = 0.75. A median of 0.765 would have
      relative error +0.02.

  F1  EXTRAPOLATION GUARD. Per cell, fit log(range/median) against log(n)
      by least squares over all rungs (numpy.polyfit, degree 1). Print an
      extrapolated required size, the n at which the fitted line reaches
      0.025, ONLY when
        (i)  the fitted slope is negative, and
        (ii) the top two medians pass D1 (the second-highest rung passes D1).
      Otherwise print "not in the asymptotic regime; no extrapolation". If
      any rung has range/median = 0, no fit is attempted. The size is always
      labelled "extrapolation from a K-point fit, not a measurement", where K
      is the number of rungs.
      Worked example: ratios 0.40, 0.20, 0.10, 0.05 at 4M, 16M, 64M, 256M
      give slope log(0.5)/log(4) = -0.5. The line reaches 0.025 one factor
      of 4 above 256M, at 1.02e9. If the 64M and 256M medians pass D1, the
      script prints "extrapolated required size 1.02e+09 (extrapolation from
      a 4-point fit, not a measurement)".

OUTCOMES, FIXED IN ADVANCE (agreed 2026-10-09)
  O1  An adequate size is reached and is within reach of a real run: calprec's
      C4 is rerun at that reference size, and N_star becomes declarable.
  O2  No adequate size is reached, or only at an unrunnable size: the
      tau0 = 0.01 cells are redefined by a declared fixed beta, with tau(beta)
      reported together with its uncertainty. The manuscript states that the
      tightest target is not identifiable by direct Monte Carlo on this
      problem. That is an estimand change, decided now, not after the run.
  O3  Sphere is adequate where ackley is not: the limit is the objective's
      tail, not the method. The manuscript says so, with the exact-tau
      evidence of X1.
  Whether a size is "within reach of a real run" is judged from the measured
  wall times and peak RSS this script prints. It is not decided by the script.

SEEDS
  Every random stream is numpy.random.default_rng(SeedSequence(key)), where
  key is a tuple of integers:
      (ENTROPY, kind, objective code, d, nominal tau0 in millionths, n, rep)
  kind 11 = calibration sample, kind 12 = reference. calprec.py uses kinds 1
  and 2 with the same ENTROPY, so no stream here can coincide with one
  there. The full key is the seed, used at full SeedSequence width, not
  reduced to 32 bits, so distinct keys give distinct streams. Each key is
  written to the output CSVs. References are shared by both betas of an
  objective, so their key carries nominal tau0 = 0. Objective codes:
  ackley 0, sphere 1.

OUTPUT (new folder <outdir>/refscale-<timestamp>/, every file opened "x")
  refscale_calibration.csv  one row per cell: seed key, beta (repr), achieved
                            fraction on the calibration sample, sphere exact
                            tau(beta), wall, peak RSS
  refscale_real.csv         one row per (objective, beta, n, replicate):
                            seed key, streamed log-ESS, tau_hat, largest-term
                            share, sphere exact tau and relative error, E1
                            values where applicable, wall, peak RSS. Written
                            as each task finishes.
  refscale_rung.csv         one row per (cell, n): median, min, max, range,
                            ratio, C5, D1, adequate, sphere exact tau and
                            relative error of the median
  refscale_fit.csv          one row per cell: slope, intercept, F1 verdict,
                            extrapolated size or blank
  Each task runs in a fresh worker process (maxtasksperchild=1), so the peak
  RSS printed per task (resource.getrusage, Linux kilobytes / 1024) is that
  task's own.

ORDER OF WORK
  Phase A: the four calibrations. Phase B: the two lowest rungs (E1),
  largest first; if E1 fails anywhere, stop. Phase C: the remaining rungs,
  largest first. The gate runs before the expensive rungs so a failure costs
  minutes, not hours.

AMENDMENT (2026-10-10, after the first full execution; ledger N21)
  --objectives NAME[,NAME] restricts the run to a subset of the two objectives,
  for the follow-up 4G rung on sphere only. It selects objectives and nothing
  else: no criterion, threshold, seed rule, ladder rule or default changes.
  Seed keys depend on the objective's code, not on which objectives are run,
  so a selected objective's calibration and references at a given (n, rep)
  are the same streams as in a run of both. With the flag absent the run is
  identical to the version first executed (c6dc0cb).

SMOKE MODE (--smoke): ladder 4M, 16M, two replicates, every phase as above.
  It prints measured throughput per objective, and a PROJECTION (a lower
  bound from that throughput, not a measurement) of the full run's wall time
  for the ladder to 256M and for the ladder to 1G. C5, D1 and F1 are printed
  but are not results: the smoke uses two replicates, and C5's 2.53 factor
  is for six. Outside smoke mode, --reps must be 6.

HOW TO RUN (from the repository root, venv active)
    python scripts/refscale.py --workers 2 --smoke
    python scripts/refscale.py --workers 4
    python scripts/refscale.py --workers 4 --ladder 4000000,16000000,64000000,256000000,1024000000
  --archive PATH (else CBOGAP_ARCHIVE, else <repo>/zenodo-v1) and --outdir
  PATH (else CBOGAP_OUTDIR, else <repo>/runs) are resolved by
  scripts/cbopaths.py, with the same semantics as detcheck.py. On Kaggle the
  kgrun runner discovers the mount path (on 2026-10-09:
  /kaggle/input/datasets/ericsom/cbo-gap-archive) and passes both flags.
  Exit code 0 when the run completes (whatever the verdicts), 2 on a setup
  error, 3 when E1 fails and the run stops.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import argparse
import csv
import datetime
import math
import os
import platform
import resource
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.dont_write_bytecode = True

import cbopaths                                                # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The archive path must be known at import time, so --archive and --outdir
# are read from argv before argparse (scripts/cbopaths.py). argparse still
# declares both flags in main(), so --help lists them and an unknown flag is
# still an error.
ARCH = cbopaths.archive_path(ROOT)
OUTROOT = cbopaths.output_root(ROOT)
if not os.path.isdir(ARCH):
    sys.stderr.write("setup error: archive not found at {}\n".format(ARCH))
    sys.stderr.write("pass --archive <path> or set CBOGAP_ARCHIVE\n")
    sys.exit(2)
sys.path.insert(0, ARCH)

try:
    import exactcal as ec
except Exception as exc:                                        # pragma: no cover
    sys.stderr.write("setup error: cannot import exactcal: {}\n".format(exc))
    sys.exit(2)

OBJS = ["ackley", "sphere"]
OBJ_CODE = {"ackley": 0, "sphere": 1}
D = 40
LAW = "centred"
TAUS = [0.01, 0.1]
LADDER = [4000000, 16000000, 64000000, 256000000]
SMOKE_LADDER = [4000000, 16000000]
PROJ_LADDERS = [[4000000, 16000000, 64000000, 256000000],
                [4000000, 16000000, 64000000, 256000000, 1024000000]]
REPS = 6
SMOKE_REPS = 2
N_CAL = 1000000
CHUNK = 250000
ENTROPY = 20261009
KIND_CAL = 11
KIND_REF = 12
E1_TOL = 1e-12
C5_MARGIN = 0.025
D1_MARGIN = 0.025


def seed_key(kind, obj, tau, n, rep):
    return (ENTROPY, kind, OBJ_CODE[obj], D, int(round(tau * 1000000)), int(n), int(rep))


def key_str(key):
    return "-".join(str(k) for k in key)


def rng_for(key):
    return np.random.default_rng(np.random.SeedSequence(list(key)))


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def tau_from_log_ess(log_ess, n):
    """As calprec.tau_of and the archived beta_on_ensemble return it."""
    return math.exp(min(log_ess, 700.0)) / n


def exact_tau_sphere(beta, d):
    """X1: tau(beta) = (1+4 beta)^(d/2) / (1+2 beta)^d, in log space."""
    return math.exp(0.5 * d * math.log1p(4.0 * beta) - d * math.log1p(2.0 * beta))


def f_values(obj, n, rng, chunk):
    """Objective values of n iid points from the initial law, held; values only."""
    f = ec.OBJECTIVES[obj]
    out = np.empty(n, dtype=np.float64)
    done = 0
    while done < n:
        m = min(chunk, n - done)
        X = ec.draw_initial(rng, m, D, obj, LAW)
        out[done:done + m] = f(X)
        del X
        done += m
    return out


def calibrate(a):
    """Phase A task: one cell's calibration sample and its fixed beta."""
    obj, tau, n_cal, chunk = a
    t0 = time.time()
    key = seed_key(KIND_CAL, obj, tau, n_cal, 0)
    fv = f_values(obj, n_cal, rng_for(key), chunk)
    beta, achieved = ec.beta_on_ensemble(fv, tau, n_cal)
    del fv
    exact = exact_tau_sphere(beta, D) if obj == "sphere" else None
    return {"objective": obj, "tau0_nominal": tau, "n_cal": n_cal,
            "seed_key": key_str(key), "beta": float(beta),
            "achieved_on_cal": float(achieved), "exact_tau_sphere": exact,
            "wall_s": time.time() - t0, "peak_rss_mb": peak_rss_mb()}


def reference(a):
    """Phase B/C task: one streamed reference, evaluated at every beta of its
    objective. hold=True also keeps the values and applies E1."""
    obj, betas, n, rep, chunk, hold = a
    t0 = time.time()
    key = seed_key(KIND_REF, obj, 0.0, n, rep)
    rng = rng_for(key)
    f = ec.OBJECTIVES[obj]
    nb = len(betas)
    l1 = [[] for _ in range(nb)]
    l2 = [[] for _ in range(nb)]
    mx2 = [-math.inf] * nb
    held = np.empty(n, dtype=np.float64) if hold else None
    done = 0
    nchunks = 0
    while done < n:
        m = min(chunk, n - done)
        X = ec.draw_initial(rng, m, D, obj, LAW)
        fv = f(X)
        del X
        if hold:
            held[done:done + m] = fv
        for i in range(nb):
            av = -betas[i] * fv
            l1[i].append(ec._logsumexp(av))
            a2 = 2.0 * av
            l2[i].append(ec._logsumexp(a2))
            mx2[i] = max(mx2[i], float(np.max(a2)))
            del av, a2
        del fv
        done += m
        nchunks += 1
    out = []
    for i in range(nb):
        lse1 = ec._logsumexp(np.asarray(l1[i]))
        lse2 = ec._logsumexp(np.asarray(l2[i]))
        log_ess = 2.0 * lse1 - lse2
        row = {"log_ess_streamed": log_ess,
               "tau_hat": tau_from_log_ess(log_ess, n),
               "largest_share": math.exp(mx2[i] - lse2),
               "log_ess_held": None, "e1_reldiff": None, "e1": "not applied"}
        if hold:
            lh = float(ec.log_ess_of(held, betas[i]))
            rd = abs(log_ess - lh) / abs(lh) if lh != 0.0 else math.inf
            row["log_ess_held"] = lh
            row["e1_reldiff"] = rd
            row["e1"] = "PASS" if rd <= E1_TOL else "FAIL"
        out.append(row)
    del held
    return {"objective": obj, "n": n, "rep": rep, "seed_key": key_str(key),
            "chunks": nchunks, "rows": out, "wall_s": time.time() - t0,
            "peak_rss_mb": peak_rss_mb()}


def median6(v):
    return float(np.median(np.asarray(v, dtype=np.float64)))


def fmt_num(x, spec):
    return "" if x is None else format(x, spec)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--smoke", action="store_true",
                   help="ladder 4M,16M with 2 replicates; prints a run-time projection")
    p.add_argument("--ladder", default=None,
                   help="comma-separated reference sizes; default 4M,16M,64M,256M")
    p.add_argument("--reps", type=int, default=None, help="must be 6 outside --smoke")
    p.add_argument("--ncal", type=int, default=N_CAL)
    p.add_argument("--chunk", type=int, default=CHUNK)
    p.add_argument("--objectives", default=None,
                   help="comma-separated subset of {}; default all, in that order. "
                        "Selects objectives only (amendment 2026-10-10)".format(",".join(OBJS)))
    p.add_argument("--archive", default=None,
                   help="path to the deposited archive; default <repo>/zenodo-v1, "
                        "or CBOGAP_ARCHIVE. On Kaggle: the path the kgrun runner finds "
                        "(2026-10-09: /kaggle/input/datasets/<user>/<dataset>)")
    p.add_argument("--outdir", default=None,
                   help="directory to create the run folder in; default <repo>/runs, "
                        "or CBOGAP_OUTDIR. On Kaggle: /kaggle/working")
    a = p.parse_args()

    if a.smoke:
        ladder = [int(s) for s in a.ladder.split(",")] if a.ladder else list(SMOKE_LADDER)
        reps = a.reps if a.reps is not None else SMOKE_REPS
    else:
        ladder = [int(s) for s in a.ladder.split(",")] if a.ladder else list(LADDER)
        reps = a.reps if a.reps is not None else REPS
        if reps != REPS:
            sys.stderr.write("setup error: --reps must be {} outside --smoke; C5's 2.53 "
                             "factor is for six replicates\n".format(REPS))
            return 2
    ladder = sorted(set(ladder))
    if len(ladder) < 2:
        sys.stderr.write("setup error: the ladder needs at least two rungs (E1 uses the "
                         "two lowest)\n")
        return 2
    gate_rungs = ladder[:2]
    # Amendment 2026-10-10 (ledger N21): --objectives selects a subset of OBJS
    # and nothing else. Absent, objs is OBJS in its original order, so every
    # task, seed key, print and file is as before the amendment.
    if a.objectives is None:
        objs = list(OBJS)
    else:
        want = [o for o in a.objectives.split(",") if o]
        bad = [o for o in want if o not in OBJS]
        if bad or not want or len(set(want)) != len(want):
            sys.stderr.write("setup error: --objectives must be distinct names from {}; "
                             "got {}\n".format(OBJS, a.objectives))
            return 2
        objs = [o for o in OBJS if o in want]
    chunk, n_cal = a.chunk, a.ncal

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(OUTROOT, ("refscale-smoke-" if a.smoke else "refscale-") + stamp)
    os.makedirs(outdir)                        # refuses if it exists

    print("=" * 96)
    print("CBO-GAP refscale -- reference size at which the population concentration is estimable")
    print("=" * 96)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {}".format(
        platform.platform(), platform.machine(), os.cpu_count(), a.workers))
    print("  archive  {}".format(ARCH))
    print("  mode     {}".format("SMOKE (timing; verdicts are not results)" if a.smoke else "FULL"))
    print("  cells    objectives {}  d {}  law {}  nominal tau0 {}".format(objs, D, LAW, TAUS))
    print("  calib.   N_CAL {}  seed kind {}".format(n_cal, KIND_CAL))
    print("  ladder   {}   replicates {}   chunk {}   seed kind {}".format(
        ladder, reps, chunk, KIND_REF))
    print("  seeds    default_rng(SeedSequence(key)), key = (ENTROPY {}, kind, obj code, d, "
          "tau0 in millionths, n, rep); obj codes {}".format(ENTROPY, OBJ_CODE))
    print("  E1       streamed vs archived log_ess_of on held arrays at rungs {}: "
          "relative diff <= {:g}, else stop".format(gate_rungs, E1_TOL))
    print("  C5       range/median over replicates <= {}".format(C5_MARGIN))
    print("  D1       |median_n - median_next| / median_next <= {}; top rung untested".format(
        D1_MARGIN))
    print("  F1       extrapolate only if slope < 0 and the second-highest rung passes D1")
    print("  X1       sphere exact tau(beta) = (1+4b)^(d/2) / (1+2b)^d")
    print("  run dir  {}".format(outdir))
    print()
    sys.stdout.flush()

    pool = Pool(processes=a.workers, maxtasksperchild=1)

    # Phase A: calibration ------------------------------------------------
    print("PHASE A  calibration, {} cells".format(len(objs) * len(TAUS)))
    cal_tasks = [(obj, tau, n_cal, chunk) for obj in objs for tau in TAUS]
    cals = pool.map(calibrate, cal_tasks)
    beta_of = {}
    with open(os.path.join(outdir, "refscale_calibration.csv"), "x", newline="") as fh:
        fields = ["objective", "d", "law", "tau0_nominal", "n_cal", "seed_key", "beta",
                  "achieved_on_cal", "exact_tau_sphere", "wall_s", "peak_rss_mb"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for c in cals:
            beta_of[(c["objective"], c["tau0_nominal"])] = c["beta"]
            w.writerow({"objective": c["objective"], "d": D, "law": LAW,
                        "tau0_nominal": c["tau0_nominal"], "n_cal": c["n_cal"],
                        "seed_key": c["seed_key"], "beta": repr(c["beta"]),
                        "achieved_on_cal": repr(c["achieved_on_cal"]),
                        "exact_tau_sphere": ("" if c["exact_tau_sphere"] is None
                                             else repr(c["exact_tau_sphere"])),
                        "wall_s": "{:.3f}".format(c["wall_s"]),
                        "peak_rss_mb": "{:.1f}".format(c["peak_rss_mb"])})
            ex = c["exact_tau_sphere"]
            print("  {:<7} nominal tau0 {:<5}  beta = {!r}   achieved on calibration sample "
                  "{:.6f}{}   wall {:.1f} s   peak RSS {:.0f} MB".format(
                      c["objective"], c["tau0_nominal"], c["beta"], c["achieved_on_cal"],
                      "" if ex is None else "   exact tau(beta) {:.6g}".format(ex),
                      c["wall_s"], c["peak_rss_mb"]))
    print()
    sys.stdout.flush()

    # Phases B and C: references -------------------------------------------
    betas = {obj: [beta_of[(obj, tau)] for tau in TAUS] for obj in objs}

    def tasks_for(rungs, hold):
        t = [(obj, betas[obj], n, rep, chunk, hold)
             for n in rungs for obj in objs for rep in range(reps)]
        t.sort(key=lambda x: -x[2])            # largest first
        return t

    real_fields = ["objective", "d", "law", "tau0_nominal", "beta", "n", "rep", "seed_key",
                   "chunks", "log_ess_streamed", "tau_hat", "largest_share",
                   "exact_tau_sphere", "rel_err_vs_exact", "log_ess_held", "e1_reldiff",
                   "e1", "wall_s", "peak_rss_mb"]
    real_fh = open(os.path.join(outdir, "refscale_real.csv"), "x", newline="")
    real_w = csv.DictWriter(real_fh, fieldnames=real_fields)
    real_w.writeheader()
    real_fh.flush()

    tau_hats = {}                               # (obj, tau, n) -> list of tau_hat
    e1_failures = []
    throughput = {obj: [0, 0.0] for obj in objs}  # points, wall seconds

    def run_phase(label, tasks):
        n_done = 0
        t_phase = time.time()
        for res in pool.imap_unordered(reference, tasks):
            n_done += 1
            obj = res["objective"]
            throughput[obj][0] += res["n"]
            throughput[obj][1] += res["wall_s"]
            for i, tau in enumerate(TAUS):
                r = res["rows"][i]
                beta = betas[obj][i]
                exact = exact_tau_sphere(beta, D) if obj == "sphere" else None
                relerr = (r["tau_hat"] - exact) / exact if exact else None
                tau_hats.setdefault((obj, tau, res["n"]), []).append(r["tau_hat"])
                if r["e1"] == "FAIL":
                    e1_failures.append((obj, tau, res["n"], res["rep"], r["e1_reldiff"]))
                real_w.writerow({
                    "objective": obj, "d": D, "law": LAW, "tau0_nominal": tau,
                    "beta": repr(beta), "n": res["n"], "rep": res["rep"],
                    "seed_key": res["seed_key"], "chunks": res["chunks"],
                    "log_ess_streamed": repr(r["log_ess_streamed"]),
                    "tau_hat": repr(r["tau_hat"]),
                    "largest_share": repr(r["largest_share"]),
                    "exact_tau_sphere": "" if exact is None else repr(exact),
                    "rel_err_vs_exact": "" if relerr is None else repr(relerr),
                    "log_ess_held": "" if r["log_ess_held"] is None else repr(r["log_ess_held"]),
                    "e1_reldiff": "" if r["e1_reldiff"] is None else repr(r["e1_reldiff"]),
                    "e1": r["e1"], "wall_s": "{:.3f}".format(res["wall_s"]),
                    "peak_rss_mb": "{:.1f}".format(res["peak_rss_mb"])})
            real_fh.flush()
            parts = []
            for i, tau in enumerate(TAUS):
                r = res["rows"][i]
                s = "beta={:.6g} tau_hat={:.6g} share={:.3g}".format(
                    betas[obj][i], r["tau_hat"], r["largest_share"])
                if obj == "sphere":
                    ex = exact_tau_sphere(betas[obj][i], D)
                    s += " exact={:.6g} relerr={:+.4f}".format(ex, (r["tau_hat"] - ex) / ex)
                if r["e1"] != "not applied":
                    s += " E1 {} ({:.2e})".format(r["e1"], r["e1_reldiff"])
                parts.append(s)
            print("  [{} {:>3}/{:>3}] {:<6} n={:<11d} rep {}  wall {:8.1f} s  RSS {:6.0f} MB  "
                  "elapsed {:8.1f} s".format(label, n_done, len(tasks), obj, res["n"],
                                             res["rep"], res["wall_s"], res["peak_rss_mb"],
                                             time.time() - t_phase))
            for s in parts:
                print("        " + s)
            sys.stdout.flush()
            nonlocal_peak[0] = max(nonlocal_peak[0], res["peak_rss_mb"])

    nonlocal_peak = [0.0]
    print("PHASE B  equivalence gate E1 on rungs {}, {} tasks, largest first".format(
        gate_rungs, len(objs) * len(gate_rungs) * reps))
    run_phase("B", tasks_for(gate_rungs, True))
    print()
    if e1_failures:
        real_fh.close()
        pool.close()
        pool.join()
        print("=" * 96)
        print("E1 FAILED: streamed and archived log-ESS disagree beyond {:g}:".format(E1_TOL))
        for f in e1_failures:
            print("  {} nominal tau0 {} n {} rep {}  relative diff {:.3e}".format(*f))
        print("The run stops here; the higher rungs were not started. Exit code 3.")
        print("=" * 96)
        return 3
    print("E1 PASSED on every replicate and beta at rungs {}.".format(gate_rungs))
    print()
    rest = [n for n in ladder if n not in gate_rungs]
    if rest:
        print("PHASE C  rungs {}, {} tasks, largest first".format(
            rest, len(objs) * len(rest) * reps))
        run_phase("C", tasks_for(rest, False))
        print()
    real_fh.close()
    pool.close()
    pool.join()
    peak_task_rss = nonlocal_peak[0]

    # Rung table: C5, D1, adequacy, X1 ---------------------------------------
    rung_rows = []
    fit_rows = []
    print("=" * 96)
    print("RUNG TABLE  (every value at the cell's fixed beta; tau0 is nominal)")
    print("=" * 96)
    for obj in objs:
        for i, tau in enumerate(TAUS):
            beta = betas[obj][i]
            exact = exact_tau_sphere(beta, D) if obj == "sphere" else None
            print("{} at beta = {!r}  (nominal tau0 {}){}".format(
                obj, beta, tau, "" if exact is None else
                "   exact tau(beta) = {:.8g}".format(exact)))
            print("  {:>11} {:>12} {:>12} {:>12} {:>9} {:>5} {:>9} {:>8} {:>9}{}".format(
                "n", "median", "min", "max", "ratio", "C5", "drift", "D1", "adequate",
                "" if exact is None else "  relerr(median)"))
            meds = [median6(tau_hats[(obj, tau, n)]) for n in ladder]
            ratios = []
            smallest_adequate = None
            for k, n in enumerate(ladder):
                v = tau_hats[(obj, tau, n)]
                med = meds[k]
                lo, hi = float(min(v)), float(max(v))
                ratio = (hi - lo) / med if med > 0.0 else math.inf
                ratios.append(ratio)
                c5 = "pass" if ratio <= C5_MARGIN else "fail"
                if k + 1 < len(ladder):
                    drift = abs(med - meds[k + 1]) / meds[k + 1]
                    d1 = "pass" if drift <= D1_MARGIN else "fail"
                else:
                    drift, d1 = None, "untested"
                adequate = "yes" if (c5 == "pass" and d1 == "pass") else "no"
                if adequate == "yes" and smallest_adequate is None:
                    smallest_adequate = n
                relerr = (med - exact) / exact if exact else None
                print("  {:>11d} {:>12.6g} {:>12.6g} {:>12.6g} {:>9.4f} {:>5} {:>9} {:>8} {:>9}{}".format(
                    n, med, lo, hi, ratio, c5, fmt_num(drift, ".4f") or "-", d1, adequate,
                    "" if relerr is None else "  {:+.4f}".format(relerr)))
                rung_rows.append({
                    "objective": obj, "tau0_nominal": tau, "beta": repr(beta), "n": n,
                    "reps": len(v), "median": repr(med), "min": repr(lo), "max": repr(hi),
                    "range": repr(hi - lo), "ratio": repr(ratio), "C5": c5,
                    "drift_vs_next": "" if drift is None else repr(drift), "D1": d1,
                    "adequate": adequate,
                    "exact_tau_sphere": "" if exact is None else repr(exact),
                    "rel_err_median_vs_exact": "" if relerr is None else repr(relerr)})
            if smallest_adequate is None:
                print("  smallest adequate rung: none -- no adequate rung in the ladder")
            else:
                print("  smallest adequate rung: {}".format(smallest_adequate))

            # F1 -------------------------------------------------------------
            slope = intercept = req = None
            if all(r > 0.0 and math.isfinite(r) for r in ratios):
                x = np.log(np.asarray(ladder, dtype=np.float64))
                y = np.log(np.asarray(ratios, dtype=np.float64))
                slope, intercept = (float(c) for c in np.polyfit(x, y, 1))
                top2_d1 = abs(meds[-2] - meds[-1]) / meds[-1] <= D1_MARGIN
                if slope < 0.0 and top2_d1:
                    req = math.exp((math.log(C5_MARGIN) - intercept) / slope)
                    verdict = "extrapolated"
                    print("  F1: slope {:.4f}; extrapolated required size {:.3g} (extrapolation "
                          "from a {}-point fit, not a measurement)".format(slope, req, len(ladder)))
                else:
                    verdict = "not in the asymptotic regime"
                    print("  F1: slope {:.4f}; not in the asymptotic regime; no "
                          "extrapolation".format(slope))
            else:
                verdict = "no fit (a ratio is zero or not finite)"
                print("  F1: no fit (a ratio is zero or not finite)")
            fit_rows.append({"objective": obj, "tau0_nominal": tau, "beta": repr(beta),
                             "points": len(ladder),
                             "slope": "" if slope is None else repr(slope),
                             "intercept": "" if intercept is None else repr(intercept),
                             "F1": verdict,
                             "extrapolated_size": "" if req is None else repr(req),
                             "smallest_adequate_rung": ("" if smallest_adequate is None
                                                        else smallest_adequate)})
            print()

    with open(os.path.join(outdir, "refscale_rung.csv"), "x", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rung_rows[0].keys()))
        w.writeheader()
        w.writerows(rung_rows)
    with open(os.path.join(outdir, "refscale_fit.csv"), "x", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fit_rows[0].keys()))
        w.writeheader()
        w.writerows(fit_rows)

    # Throughput and, in smoke mode, the projection ---------------------------
    print("=" * 96)
    print("MEASURED  peak RSS of any reference task {:.0f} MB".format(peak_task_rss))
    for obj in objs:
        pts, sec = throughput[obj]
        print("MEASURED  {} throughput {:.3g} points per second per worker "
              "({} points in {:.1f} worker-seconds)".format(obj, pts / sec, pts, sec))
    if a.smoke:
        print()
        print("PROJECTION (from the smoke throughput above; a lower bound, not a measurement;")
        print("           ignores the E1 held-array overhead and scheduling gaps)")
        for lad in PROJ_LADDERS:
            work = 0.0
            longest = 0.0
            for obj in objs:
                rate = throughput[obj][0] / throughput[obj][1]
                work += REPS * sum(lad) / rate
                longest = max(longest, max(lad) / rate)
            proj = max(work / a.workers, longest)
            print("  ladder {}  x {} reps  with {} workers: at least {:.2f} h".format(
                lad, REPS, a.workers, proj / 3600.0))
    print("=" * 96)
    print("files     {}".format(outdir))
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
