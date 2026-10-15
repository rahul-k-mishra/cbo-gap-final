"""
m6_hetero.py  --  CBO-GAP measurement M6: within-unit sampling variance
                  against between-unit spread, across the chosen objectives

WHY THIS EXISTS
---------------
notes/ANALYSIS_CRITERIA_DRAFT.md item 6. Referee point 6 asks that variation
across the chosen objectives and initial laws be reported separately, as
heterogeneity over the test set. The draft lists five candidate statistics
(6A to 6E). Whether a between-unit component net of sampling noise (6C) is
estimable at all, and how far the raw SD across units (6B, the archived
COLLAPSE statistic) overstates the spread, both depend on the ratio of
within-unit to between-unit variance. M6 measures that ratio on the archived
per-realization files.

DATA (read-only; hashes checked against zenodo-v1.sha256 before use)
  exactcal_real.csv     per J, random beta. Units: the 12 (objective, init)
                        pairs at each (d, tau_0).
  rmapj_real.csv        per J, probe beta, tau_0 0.1. Units: the 3
                        objectives at each (diffusion, d, r).
  regimemap_M_real.csv  slopes only, probe beta. Units: the 3 objectives at
                        each (diffusion, d, r, tau_0).

QUANTITIES (per group of k units; full grid where E_J is stored)
  y_i       per-unit estimate: S_curve or S_slope (as M1), or, for exactcal,
            the per-unit change S(d = 40) - S(d = 2) at fixed (tau_0, unit)
            (the Table 3 contrast, unit by unit);
  v_i       within-unit sampling variance of y_i: the bootstrap variance over
            B resamples of the unit's realizations (for a change, the d = 2
            and d = 40 cells are resampled independently and their variances
            add, since their seeds differ);
  s2        sample variance of y_i across the k units (ddof 1);
  sd_units  sqrt(s2), the archived COLLAPSE statistic (6B);
  vbar      mean of v_i;
  tau2_mm   max(0, s2 - vbar), the unweighted moment estimate of the
            between-unit variance net of sampling noise (6C). E[s2] = tau2 +
            vbar when the y_i are independent;
  ratio     vbar / s2, the share of the raw spread that sampling noise alone
            would produce;
  Q         sum of (y_i - y_w)^2 / v_i, with y_w the 1/v_i-weighted mean,
            df = k - 1 (6D). No p-value is printed: that would need the
            chi-square distribution, and this project uses NumPy only;
  I2        max(0, (Q - (k - 1)) / Q).
  Seed key [20261015, 66, source code, cell index, 0] for each cell's
  bootstrap. A unit's cell is resampled once and reused by every group that
  contains it.
  Worked example (illustrative numbers): k = 3 units with y = -1.00, -0.95,
  -0.90 have s2 = 0.0025. With v_i = 0.0009 each, vbar = 0.0009, tau2_mm =
  0.0016, ratio = 0.36, y_w = -0.95, Q = (0.0025 + 0 + 0.0025)/0.0009 = 5.56
  and I2 = (5.56 - 2)/5.56 = 0.64.

KNOWN LIMITS STATED BEFORE THE RUN
  - In exactcal_real.csv Ackley and Sphere share every seed (ledger N6), so
    their unit estimates are not independent within a group. s2, tau2_mm, Q
    and I2 assume independence and are biased for exactcal groups by an
    unknown amount. M6 reports them anyway, labelled. The rmapj and
    regimemap files use distinct seeds for every realization (N31 specimen).
  - With k = 3 units (rmapj, regimemap) every between-unit statistic is
    very imprecise. M6 does not attach intervals to them.

PRE-SPECIFIED CHECK (fixed 2026-10-15, before first execution)
  P0  as in m1_estimands.py, on exactcal_real.csv and rmapj_real.csv: stored
      slopes reproduced by the archived fit to half a unit in the last
      stored digit plus 1e-7, or exit 3. Worked example there.
  There is NO verdict criterion. M6 sets no threshold and chooses no
  statistic. B is the measurement's own setting.

WHAT THE RESULT CAN INFORM
  - The ratio of within-unit to between-unit variance on the random-beta
    (exactcal) and probe-beta (rmapj, regimemap) designs, at 15 and 12
    realizations, for per-cell slopes and for the d = 2 to d = 40 change.
  - Whether 6C would mostly truncate at zero, and how far 6B is inflated by
    sampling noise, on those designs.
WHAT IT CANNOT INFORM
  - The same ratio under calprec v2 betas. None of these files was produced
    at a fixed calibrated beta. The rerun's ratio is unknown until it
    exists.
  - Population heterogeneity over objectives not in the test set. Referee
    point 6 rules that reading out, and nothing here supports it.
  - Which statistic to report. That is a choice (draft item 6).

OUTPUT (new folder <outdir>/m6-<timestamp>/, every file opened "x")
  m6_units.csv   one row per (group, unit, estimand): y_i, v_i, seed key(s).
  m6_groups.csv  one row per (group, estimand): k, mean, sd_units, vbar,
                 tau2_mm, ratio, Q, df, I2, an N6 flag.

HOW TO RUN (from the repository root, venv active)
    python scripts/m6_hetero.py --workers 2
  Defaults: --boot 4000. Exit 0 when done, 2 on a setup error, 3 on P0
  FAIL.

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import argparse
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.dont_write_bytecode = True

import measlib as ml                                            # noqa: E402

KIND = 66
FILES = ["regimemap.py", "exactcal.py", "reboot.py", "rmapj.py",
         "exactcal_real.csv", "rmapj_real.csv", "regimemap_M_real.csv"]


def cell_task(a):
    """Point and bootstrap values of S_curve and S_slope for one cell."""
    source, idx, E, slopes, B = a
    Jv = np.array(ml.J_LIST, dtype=np.float64)
    rng = ml.rng_for(KIND, [ml.SOURCE_CODE[source], idx, 0])
    out = {"source": source, "idx": idx,
           "seed_key": ml.key_str(KIND, [ml.SOURCE_CODE[source], idx, 0])}
    if E is not None:
        R = E.shape[0]
        se = ml.slopes_each(Jv, E)
        ii = rng.integers(0, R, size=(B, R))
        out["curve"] = (ml.slope_curve(Jv, E), ml.boot_curve(Jv, E, ii))
    else:
        se = np.asarray(slopes, dtype=np.float64)
        R = se.size
        ii = rng.integers(0, R, size=(B, R))
    out["slope"] = (float(np.nanmean(se)), np.nanmean(se[ii], axis=1))
    out["rss"] = ml.rss_mb()
    return out


def group_stats(y, v):
    y = np.asarray(y, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    k = y.size
    s2 = float(np.var(y, ddof=1))
    vbar = float(np.mean(v))
    w = 1.0 / v
    yw = float(np.sum(w * y) / np.sum(w))
    Q = float(np.sum((y - yw) ** 2 / v))
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    return {"k": k, "mean": float(np.mean(y)), "sd_units": s2 ** 0.5, "vbar": vbar,
            "tau2_mm": max(0.0, s2 - vbar), "ratio": vbar / s2 if s2 > 0 else float("nan"),
            "Q": Q, "df": k - 1, "I2": I2}


def summ(v):
    v = np.asarray(v, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return "n   0"
    return "n {:>3}  min {:.4f}  q25 {:.4f}  med {:.4f}  q75 {:.4f}  max {:.4f}".format(
        v.size, v.min(), np.percentile(v, 25), np.median(v), np.percentile(v, 75), v.max())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    a = p.parse_args()
    if a.workers < 1 or a.boot < 100:
        sys.stderr.write("setup error: --workers >= 1 and --boot >= 100 required\n")
        return 2

    outdir = ml.new_outdir("m6")
    ok = ml.print_header(
        "CBO-GAP M6 -- within-unit variance against between-unit spread (draft item 6)",
        KIND, a.workers,
        {"boot B": a.boot,
         "units": "exactcal: 12 (objective, init) per (d, tau0); rmapj: 3 objectives per "
                  "(diffusion, d, r); regimemap_M: 3 objectives per (diffusion, d, r, tau0)",
         "statistics": "sd_units, vbar, tau2_mm = max(0, s2 - vbar), ratio = vbar/s2, Q, I2",
         "N6": "exactcal ackley and sphere share seeds; exactcal groups flagged",
         "P0": "refit vs stored slope (per-J files), tol half-unit + 1e-7; exit 3 on fail",
         "verdict": "none; descriptive",
         "covers": "random-beta (exactcal) and probe-beta (rmapj, regimemap) designs "
                   "ONLY; not calprec betas; no population inference"},
        FILES, outdir)
    if not ok:
        print("SETUP ERROR: archive hash mismatch; nothing measured")
        return 2

    Jv = np.array(ml.J_LIST, dtype=np.float64)
    ex = ml.load_exactcal()
    rj = ml.load_rmapj()
    rmm = ml.load_regimemap("regimemap_M_real.csv")
    n1, b1, w1 = ml.p0_check(ex, Jv, "exactcal")
    n2, b2, w2 = ml.p0_check(rj, Jv, "rmapj")
    print("\n  P0 exactcal_real.csv: {} slopes, {} outside tolerance (worst excess {:.2e})".format(n1, b1, w1))
    print("  P0 rmapj_real.csv:    {} slopes, {} outside tolerance (worst excess {:.2e})".format(n2, b2, w2))
    if b1 or b2:
        print("  P0 FAIL: the stored slopes are not reproduced; nothing measured")
        return 3
    print("  P0 PASS")
    sys.stdout.flush()

    tasks, index = [], {}
    for i, (k, c) in enumerate(ex.items()):
        index[("exactcal", k)] = i
        tasks.append(("exactcal", i, c["E"], None, a.boot))
    for i, (k, c) in enumerate(rj.items()):
        index[("rmapj", k)] = i
        tasks.append(("rmapj", i, c["E"], None, a.boot))
    for i, (k, c) in enumerate(rmm.items()):
        index[("regimemap_M", k)] = i
        tasks.append(("regimemap_M", i, None, c["slope"], a.boot))
    t0 = time.time()
    with Pool(processes=a.workers) as pool:
        res = pool.map(cell_task, tasks, chunksize=1)
    wall = time.time() - t0
    by = {(r["source"], r["idx"]): r for r in res}

    def cell(src, k):
        return by[(src, index[(src, k)])]

    unit_rows, group_rows, summary = [], [], {}

    def add_group(label, src, gcoords, est, units, n6):
        ys, vs = [], []
        for uname, y, v, keyz in units:
            ys.append(y)
            vs.append(v)
            unit_rows.append([label, src] + gcoords + [uname, est, ml.fmt(y), ml.fmt(v), keyz])
        g = group_stats(ys, vs)
        group_rows.append([label, src] + gcoords + [est, g["k"], ml.fmt(g["mean"]), ml.fmt(g["sd_units"]),
                                                     ml.fmt(g["vbar"]), ml.fmt(g["tau2_mm"]),
                                                     ml.fmt(g["ratio"]), ml.fmt(g["Q"]), g["df"],
                                                     ml.fmt(g["I2"]), "N6 seeds shared" if n6 else ""])
        summary.setdefault((label, est), []).append(g)

    exu = sorted({(k[0], k[2]) for k in ex})
    for d in sorted({k[1] for k in ex}):
        for t in ("0.5", "0.1", "0.01"):
            for est in ("curve", "slope"):
                units = []
                for (o, ini) in exu:
                    c = cell("exactcal", (o, d, ini, t))
                    pt, bt = c[est]
                    units.append(("{}/{}".format(o, ini), pt, float(np.nanvar(bt, ddof=1)), c["seed_key"]))
                add_group("exactcal-slope", "exactcal", [d, t, "", ""], est, units, True)
    for t in ("0.5", "0.1", "0.01"):
        for est in ("curve", "slope"):
            units = []
            for (o, ini) in exu:
                c2 = cell("exactcal", (o, 2, ini, t))
                c40 = cell("exactcal", (o, 40, ini, t))
                y = c40[est][0] - c2[est][0]
                v = float(np.nanvar(c40[est][1], ddof=1) + np.nanvar(c2[est][1], ddof=1))
                units.append(("{}/{}".format(o, ini), y, v, c2["seed_key"] + " " + c40["seed_key"]))
            add_group("exactcal-change", "exactcal", ["2->40", t, "", ""], est, units, True)
    for dif in ("isotropic", "anisotropic"):
        for d in sorted({k[2] for k in rj}):
            for r in sorted({k[3] for k in rj}, key=float):
                for est in ("curve", "slope"):
                    units = []
                    for o in ("ackley", "rastrigin", "sphere"):
                        c = cell("rmapj", (dif, o, d, r))
                        pt, bt = c[est]
                        units.append((o, pt, float(np.nanvar(bt, ddof=1)), c["seed_key"]))
                    add_group("rmapj", "rmapj", [d, "0.1", dif, r], est, units, False)
    for dif in ("isotropic", "anisotropic"):
        for d in sorted({k[2] for k in rmm}):
            for r in sorted({k[3] for k in rmm}, key=float):
                for t in sorted({k[4] for k in rmm}, key=float):
                    units = []
                    for o in ("ackley", "rastrigin", "sphere"):
                        c = cell("regimemap_M", (dif, o, d, r, t))
                        pt, bt = c["slope"]
                        units.append((o, pt, float(np.nanvar(bt, ddof=1)), c["seed_key"]))
                    add_group("regimemap_M", "regimemap_M", [d, t, dif, r], "slope", units, False)

    ml.write_csv(os.path.join(outdir, "m6_units.csv"),
                 ["group", "source", "d", "tau", "diffusion", "r", "unit", "estimand", "y", "v",
                  "seed_keys"], unit_rows)
    ml.write_csv(os.path.join(outdir, "m6_groups.csv"),
                 ["group", "source", "d", "tau", "diffusion", "r", "estimand", "k", "mean",
                  "sd_units", "vbar", "tau2_mm", "ratio_vbar_over_s2", "Q", "df", "I2", "flag"],
                 group_rows)

    print("\n  {} cells in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        len(res), wall, max(r["rss"] for r in res)))
    print()
    for (label, est) in sorted(summary):
        gs = summary[(label, est)]
        print("  {:<16} S_{:<5} groups {:>3}  k {}".format(label, est, len(gs), gs[0]["k"]))
        print("      ratio vbar/s2   {}".format(summ([g["ratio"] for g in gs])))
        print("      sd_units        {}".format(summ([g["sd_units"] for g in gs])))
        print("      sqrt(tau2_mm)   {}".format(summ([g["tau2_mm"] ** 0.5 for g in gs])))
        print("      I2              {}".format(summ([g["I2"] for g in gs])))
        print("      tau2_mm truncated at 0: {} of {}".format(
            sum(1 for g in gs if g["tau2_mm"] == 0.0), len(gs)))
    print("\n  exactcal groups assume independent units; Ackley and Sphere share seeds (N6).")
    print("  COVERS random-beta and probe-beta designs only; says nothing about calprec betas")
    print("  and nothing about objectives outside the test set.")
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
