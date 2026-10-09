"""
calprec.py  --  CBO-GAP round 2, stage C1: how large must the independent
                calibration sample be for a FIXED inverse temperature?

THE QUESTION, IN PLAIN LANGUAGE
-------------------------------
The referee's points 3, 4 and 5 all come down to one thing: the inverse
temperature beta must be a fixed property of the cell (objective, dimension,
initial law, target concentration), not a quantity re-solved on whatever
ensemble happens to be evolved. The referee offers two routes to such a beta:
solve it on an independent and sufficiently large calibration sample, or
estimate the population quantity tau = (E w)^2 / E[w^2] accurately. These are
the same route at two sample sizes.

The archived experiments took the first route at N = 4000. At a target of
tau0 = 0.01 that probe has an effective sample size of 40, which is why the
manuscript's Section 7.13 found achieved/target ratios spanning a factor of
forty. This script measures, rather than argues, how large N has to be.

Note on the shift: the ESS fraction is invariant under adding a constant to
f, so the archived use of f - min(f) is numerical stabilisation only and does
not by itself make the target sample-dependent. The sample dependence the
referee objects to comes from solving beta on the ensemble that is then
evolved.

WHAT IT DOES
  For each (objective, d, initial law):
    1. Build TWO independent reference half-vectors of N_REF/2 objective
       values each, from the initial law, drawn in chunks with separate
       dedicated seeds, keeping the values only (never the points), so memory
       stays at N_REF doubles. Their concatenation is the reference.
    2. For each target tau0 and each calibration size N in the sweep:
         draw R independent calibration samples, each with its own seed;
         solve beta on each with the archived bisection
         exactcal.beta_on_ensemble (nothing is reimplemented);
         evaluate the concentration that beta actually produces, on the
         INDEPENDENT reference and on each of its two halves separately,
         with the archived log_ess_of.
    3. Report, per (cell, N): the spread of beta, the spread of the realized
       concentration, and the largest relative deviation of the realized
       concentration from the target.
  It also solves beta on the reference vector itself, giving the near-
  population value beta_star that a calibration of size N_REF would produce,
  and reports how far each beta-hat sits from it.

  No trajectories are evolved. Nothing in zenodo-v1 is written to.

PRE-SPECIFIED CRITERIA (fixed 2026-10-08, before first execution)
  C1  SUFFICIENCY. A calibration size N is sufficient for a cell when, over
      all R draws,
            max_r | tau_ref(beta_hat_r) / tau0 - 1 |  <=  0.05.
      Worked example: tau0 = 0.01 and the R realized values run from 0.0098
      to 0.0104. The deviations are 0.02 and 0.04, the maximum is 0.04, which
      is at most 0.05, so N is sufficient for that cell.
  C2  THE ARCHIVED PROBE. The same statistic is reported at N = 4000, which
      is what every probe-calibrated experiment in the archive used. This
      quantifies the defect behind referee point 5; it is a measurement, not
      a gate.
  C3  DISTANCE TO THE NEAR-POPULATION VALUE. max_r |beta_hat_r / beta_star - 1|
      is reported per (cell, N). Reported only; no decision rests on it.
  C4  REFERENCE ADEQUACY. The reference is built as TWO independent halves of
      N_REF/2 points with separate seeds. For every solved beta the realized
      concentration is evaluated on each half. The reference is adequate for a
      cell and target when
            max_r | tau_A(beta_hat_r) - tau_B(beta_hat_r) |
                   / max(tau_A, tau_B)   <=  0.10.
      Where it is not, the C1 verdict for that cell and target is marked
      UNRELIABLE and no N_star may be declared from it: the reference must
      grow first. This criterion exists because the same heavy-tailed weights
      that bias a small calibration sample can also bias a finite reference,
      and a yardstick that has not been shown to be stable cannot measure a
      bias. Worked example: halves give 0.00102 and 0.00097; the relative
      disagreement is 0.00005/0.00102 = 0.049, at most 0.10, so adequate.
  PRODUCTION RULE. N_star, the calibration size the fixed-beta reruns will
      use, is the SMALLEST level in the sweep that satisfies C1 in EVERY
      cell, and it may be declared only if C4 holds in every cell and at
      every target. If no level satisfies C1 everywhere, the sweep is
      extended upward; the criterion is not relaxed and no cell is dropped.
  The criteria are not applied by this script to anything beyond printing the
  verdict per cell and the resulting N_star; no experiment is launched here.

GRIDS, READ FROM THE ARCHIVED SCRIPTS, NOT ASSUMED
  objectives  ackley rastrigin sphere griewank levy rosenbrock
              (zenodo-v1/exactcal.py line 264)
  dimensions  2 5 10 40            (exactcal.py line 263; EXP-TAU8 uses 5 10 40,
                                    a subset, from boundary.py line 253)
  laws        centred, mix-0.1     (exactcal.py line 265)
  targets     0.5 0.1 0.01         (EXP-CAL, exactcal.py line 265). The eight
                                    EXP-TAU8 targets are covered in a second
                                    invocation at the selected N, with --taus.

SEEDS
  Every seed here is derived from numpy.random.SeedSequence keyed by a tuple
  of integers, never by an arithmetic formula over name lengths. The archived
  exactcal.py formula is not injective: ackley and sphere have the same name
  length and therefore share a seed in every cell (ledger item N6). Seeds in
  this study start from entropy 20261009 and cannot collide with archived
  seeds, which are plain integers near 2.026e7 produced by that formula.

COST
  Dominated by the bisection: each solve does 200 iterations, each with two
  passes of exp over N values. The script prints a progress line per finished
  task with elapsed and projected total, so the real cost is known within the
  first few minutes rather than guessed here.

HOW TO RUN (from the repository root, venv active)
    python scripts/calprec.py --workers 2 --quick        smoke, about a minute
    python scripts/calprec.py --workers 2                full stage C1
    nohup python scripts/calprec.py --workers 2 > logs/calprec-full.log 2>&1 &
Writes runs/calprec-<timestamp>/ with two CSVs, opened with mode "x".
Exit code 0 if an N_star exists under C1, 1 if no level in the sweep
satisfies C1 everywhere (meaning: extend the sweep), 2 on a setup error.

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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(ROOT, "zenodo-v1")
if not os.path.isdir(ARCH):
    sys.stderr.write("setup error: {} not found\n".format(ARCH))
    sys.exit(2)
sys.path.insert(0, ARCH)

try:
    import exactcal as ec
except Exception as exc:                                        # pragma: no cover
    sys.stderr.write("setup error: cannot import exactcal: {}\n".format(exc))
    sys.exit(2)

OBJS = ["ackley", "rastrigin", "sphere", "griewank", "levy", "rosenbrock"]
DIMS = [2, 5, 10, 40]
LAWS = ["centred", "mix-0.1"]
TAUS = [0.5, 0.1, 0.01]
LEVELS = [4000, 16000, 64000, 256000, 1000000]
REPS = 24
N_REF = 4000000
CHUNK = 100000
ENTROPY = 20261009
C1_MARGIN = 0.05
C4_MARGIN = 0.10


def seed_for(kind, obj, d, law, tau, n, rep):
    """Injective by construction: SeedSequence over a tuple of small integers."""
    key = (ENTROPY, kind, OBJS.index(obj), d, LAWS.index(law),
           int(round(tau * 1000000)), int(n), int(rep))
    return int(np.random.SeedSequence(list(key)).generate_state(1, dtype=np.uint32)[0])


def f_values(obj, d, law, n, seed, chunk=CHUNK):
    """Objective values of n iid points from the initial law; values only."""
    f = ec.OBJECTIVES[obj]
    rng = np.random.default_rng(seed)
    out = np.empty(n, dtype=np.float64)
    done = 0
    while done < n:
        m = min(chunk, n - done)
        X = ec.draw_initial(rng, m, d, obj, law)
        out[done:done + m] = f(X)
        done += m
        del X
    return out


def tau_of(fvals, beta, n):
    return math.exp(min(ec.log_ess_of(fvals, beta), 700.0)) / n


def task(a):
    obj, d, law, taus, levels, reps, n_ref = a
    t0 = time.time()
    half = n_ref // 2
    ref_a = f_values(obj, d, law, half, seed_for(1, obj, d, law, 0.0, n_ref, 0))
    ref_b = f_values(obj, d, law, half, seed_for(1, obj, d, law, 0.0, n_ref, 1))
    ref = np.concatenate([ref_a, ref_b])
    rows = []
    for tau in taus:
        beta_star, _ = ec.beta_on_ensemble(ref, tau, len(ref))
        for n in levels:
            betas, taus_ach, split = [], [], []
            for rep in range(reps):
                fv = f_values(obj, d, law, n, seed_for(2, obj, d, law, tau, n, rep))
                b, _ = ec.beta_on_ensemble(fv, tau, n)
                betas.append(float(b))
                taus_ach.append(tau_of(ref, b, len(ref)))
                ta_a = tau_of(ref_a, b, half)
                ta_b = tau_of(ref_b, b, half)
                denom = max(ta_a, ta_b)
                split.append(abs(ta_a - ta_b) / denom if denom > 0.0 else float("inf"))
                del fv
            betas = np.asarray(betas)
            ta = np.asarray(taus_ach)
            sp = np.asarray(split)
            dev = np.abs(ta / tau - 1.0)
            rows.append({
                "objective": obj, "d": d, "law": law, "tau0": tau, "N": n,
                "reps": reps,
                "beta_star": float(beta_star),
                "beta_mean": float(betas.mean()),
                "beta_sd": float(betas.std(ddof=1)),
                "beta_min": float(betas.min()),
                "beta_max": float(betas.max()),
                "tau_mean": float(ta.mean()),
                "tau_sd": float(ta.std(ddof=1)),
                "tau_min": float(ta.min()),
                "tau_max": float(ta.max()),
                "max_rel_dev": float(dev.max()),
                "max_rel_beta_gap": float(np.abs(betas / beta_star - 1.0).max()),
                "max_ref_split": float(sp.max()),
                "C1": "sufficient" if dev.max() <= C1_MARGIN else "insufficient",
                "C4": "adequate" if sp.max() <= C4_MARGIN else "UNRELIABLE",
            })
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    return (obj, d, law, rows, time.time() - t0, rss)


def hms(sec):
    sec = int(round(sec))
    return "{:d}h {:02d}m {:02d}s".format(sec // 3600, (sec % 3600) // 60, sec % 60)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--reps", type=int, default=REPS)
    p.add_argument("--nref", type=int, default=N_REF)
    p.add_argument("--levels", default=",".join(str(x) for x in LEVELS))
    p.add_argument("--taus", default=",".join(repr(x) for x in TAUS))
    p.add_argument("--objs", default=",".join(OBJS))
    p.add_argument("--dims", default=",".join(str(x) for x in DIMS))
    p.add_argument("--laws", default=",".join(LAWS))
    a = p.parse_args()

    objs = [s.strip() for s in a.objs.split(",") if s.strip()]
    dims = [int(s) for s in a.dims.split(",") if s.strip()]
    laws = [s.strip() for s in a.laws.split(",") if s.strip()]
    levels = [int(s) for s in a.levels.split(",") if s.strip()]
    taus = [float(s) for s in a.taus.split(",") if s.strip()]
    reps, n_ref = a.reps, a.nref
    if a.quick:
        objs, dims, laws = ["ackley", "rosenbrock"], [2, 40], ["centred"]
        levels, taus, reps, n_ref = [4000, 16000], [0.5, 0.01], 6, 200000

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(ROOT, "runs", "calprec-" + stamp)
    os.makedirs(outdir)

    print("=" * 94)
    print("CBO-GAP calprec -- stage C1: calibration sample size for a fixed beta")
    print("=" * 94)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   cpus {}   workers {}".format(platform.platform(),
                                                        os.cpu_count(), a.workers))
    print("  archive  {}".format(ARCH))
    print("  mode     {}".format("QUICK SMOKE (not a result)" if a.quick else "FULL"))
    print("  objs     {}".format(objs))
    print("  dims     {}   laws {}".format(dims, laws))
    print("  taus     {}".format(taus))
    print("  levels   {}".format(levels))
    print("  reps     {}   reference vector {}   chunk {}".format(reps, n_ref, CHUNK))
    print("  seeds    SeedSequence, entropy {}, keyed by (kind, obj, d, law, tau, N, rep)".format(ENTROPY))
    print("  C1       sufficient when max over reps of |tau_realized/tau0 - 1| <= {}".format(C1_MARGIN))
    print("  C4       reference adequate when its two independent halves agree"
          " to within {} relative".format(C4_MARGIN))
    print("  N_star   smallest level sufficient in EVERY cell; no relaxation")
    print("  run dir  {}".format(outdir))
    print()

    tasks = [(o, d, law, taus, levels, reps, n_ref)
             for o in objs for d in dims for law in laws]
    print("  {} tasks, each = one reference vector plus {} solves".format(
        len(tasks), len(taus) * len(levels) * reps))
    print()

    allrows = []
    t0 = time.time()
    pool = Pool(processes=a.workers, maxtasksperchild=1)
    try:
        done = 0
        for (obj, d, law, rows, wall, rss) in pool.imap_unordered(task, tasks, chunksize=1):
            done += 1
            allrows.extend(rows)
            el = time.time() - t0
            proj = el / done * len(tasks)
            print("  [{:>3}/{:>3}] {:<11} d={:<3} {:<8} task {:>7.1f}s  RSS {:>5.0f}MB"
                  "  elapsed {}  projected {}".format(
                      done, len(tasks), obj, d, law, wall, rss, hms(el), hms(proj)))
            sys.stdout.flush()
    finally:
        pool.close()
        pool.join()
    print("  total wall {}".format(hms(time.time() - t0)))
    print()

    allrows.sort(key=lambda r: (r["objective"], r["d"], r["law"], -r["tau0"], r["N"]))
    detail = os.path.join(outdir, "calprec_detail.csv")
    cols = ["objective", "d", "law", "tau0", "N", "reps", "beta_star", "beta_mean",
            "beta_sd", "beta_min", "beta_max", "tau_mean", "tau_sd", "tau_min",
            "tau_max", "max_rel_dev", "max_rel_beta_gap", "max_ref_split",
            "C1", "C4"]
    with open(detail, "x", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in allrows:
            w.writerow(r)

    print("WORST CELL AT EACH CALIBRATION SIZE (C1 statistic: max |tau_realized/tau0 - 1|)")
    print("  {:>9} {:>6} {:>14}  {:<30} {:>10} {:>12}".format(
        "N", "tau0", "worst dev", "worst cell", "C1 ok", "C4 failures"))
    nstar = None
    per_level = {}
    any_unreliable = False
    for n in levels:
        okall = True
        for tau in taus:
            sub = [r for r in allrows if r["N"] == n and r["tau0"] == tau]
            if not sub:
                continue
            worst = max(sub, key=lambda r: r["max_rel_dev"])
            nok = sum(1 for r in sub if r["C1"] == "sufficient")
            nbad = sum(1 for r in sub if r["C4"] == "UNRELIABLE")
            any_unreliable = any_unreliable or (nbad > 0)
            okall = okall and (nok == len(sub)) and (nbad == 0)
            print("  {:>9} {:>6} {:>14.4f}  {:<30} {:>10} {:>12}".format(
                n, tau, worst["max_rel_dev"],
                "{} d={} {}".format(worst["objective"], worst["d"], worst["law"]),
                "{}/{}".format(nok, len(sub)),
                "C4 bad {}".format(nbad)))
            per_level.setdefault(n, []).append((tau, worst["max_rel_dev"], nok,
                                                len(sub), nbad))
        if okall and nstar is None:
            nstar = n
        print()

    print("C2  THE ARCHIVED 4000-POINT PROBE, for comparison with the above:")
    sub = [r for r in allrows if r["N"] == 4000]
    if sub:
        for tau in taus:
            s2 = [r for r in sub if r["tau0"] == tau]
            if not s2:
                continue
            w2 = max(s2, key=lambda r: r["max_rel_dev"])
            print("    tau0 {:<6} worst realized/target spread [{:.4g}, {:.4g}] at {} d={} {}".format(
                tau, w2["tau_min"] / tau, w2["tau_max"] / tau,
                w2["objective"], w2["d"], w2["law"]))
    else:
        print("    N = 4000 not in this sweep")
    print()

    summary = os.path.join(outdir, "calprec_summary.csv")
    with open(summary, "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["N", "tau0", "worst_max_rel_dev", "cells_sufficient", "cells",
                    "cells_C4_unreliable"])
        for n in levels:
            for (tau, dev, nok, tot, nbad) in per_level.get(n, []):
                w.writerow([n, tau, "%.6g" % dev, nok, tot, nbad])
        w.writerow([])
        w.writerow(["N_star", nstar if nstar else "NONE IN SWEEP"])

    print("C4  REFERENCE ADEQUACY (two independent halves of {} points each)".format(n_ref // 2))
    worstc4 = max(allrows, key=lambda r: r["max_ref_split"])
    print("    worst half-to-half disagreement {:.4f} at {} d={} {} tau0={} N={}".format(
        worstc4["max_ref_split"], worstc4["objective"], worstc4["d"],
        worstc4["law"], worstc4["tau0"], worstc4["N"]))
    nbad_all = sum(1 for r in allrows if r["C4"] == "UNRELIABLE")
    print("    rows marked UNRELIABLE: {} of {}".format(nbad_all, len(allrows)))
    print()

    print("=" * 94)
    if any_unreliable and nstar is None:
        print("The reference is not adequate everywhere (C4). Where C4 fails, the")
        print("measured deviation understates the truth and no N_star is declared.")
    if nstar is None:
        print("N_star: NO level in {} satisfies C1 in every cell.".format(levels))
        print("Under the production rule the sweep is extended upward; C1 is not relaxed.")
    else:
        print("N_star = {}  (smallest level satisfying C1 in every cell)".format(nstar))
    if a.quick:
        print("QUICK MODE: this is a smoke run on a reduced grid and is not a result.")
    print("detail  {}".format(detail))
    print("summary {}".format(summary))
    print("=" * 94)
    sys.exit(0 if nstar is not None else 1)


if __name__ == "__main__":
    main()
