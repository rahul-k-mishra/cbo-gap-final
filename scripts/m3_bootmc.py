"""
m3_bootmc.py  --  CBO-GAP measurement M3: Monte Carlo error of bootstrap
                  percentile endpoints against the number of resamples B

WHY THIS EXISTS
---------------
notes/ANALYSIS_CRITERIA_DRAFT.md item 3; ledger N8. The archive used 400
resamples in every simulation script, 1000, 2000 and 4000 elsewhere, and the
manuscript claimed 4000 throughout. The rerun must fix B, or a rule for B,
before its first number. M3 measures how much a percentile endpoint moves
between independent bootstrap runs of the same cell at a given B. That is
the Monte Carlo error a verdict near a threshold is exposed to.

DATA (read-only; hashes checked against zenodo-v1.sha256 before use)
  exactcal_real.csv  144 cells x 15, random beta, tau_0 0.5 / 0.1 / 0.01.
  rmapj_real.csv     180 cells x 12, probe beta, tau_0 0.1.
  Full grid J = 10 ... 5000 throughout.

METHOD
  For each cell, each statistic (S_curve and S_slope, defined as in M1),
  each B in --blist, and each repeat k = 0 ... K-1: one bootstrap of B
  resamples of the cell's realizations, seeded by the key [20261015, 63,
  source code, cell index, B, k]. Every (B, k) therefore has its own
  independent stream. Endpoints recorded at the percentiles 2.5, 5, 95 and
  97.5 (numpy default linear rule, as the archive), with the bootstrap SD.
  Per (cell, statistic, B, percentile):
    mc_sd    = SD over the K repeats of the endpoint;
    boot_sd  = mean over the K repeats of the bootstrap SD;
    ratio    = mc_sd / boot_sd   (dimensionless).
  Worked example (illustrative numbers): K = 20 repeats of the 97.5th
  percentile at B = 400 with SD 0.0040 over repeats, and a bootstrap SD of
  0.0300, give mc_sd 0.0040 and ratio 0.133.

PRE-SPECIFIED CHECK (fixed 2026-10-15, before first execution)
  P0  as in m1_estimands.py: stored slopes reproduced by the archived fit to
      half a unit in the last stored digit plus 1e-7, or exit 3. Worked
      example there.
  There is NO verdict criterion. M3 is descriptive. It does not choose B.
  The B values, K and the percentiles are the measurement's own settings,
  not proposals for the rerun.

WHAT THE RESULT CAN INFORM
  - The size of the Monte Carlo error of a percentile endpoint at B = 400,
    1000, 2000, 4000 and 10000, in slope units and relative to the
    bootstrap SD, for cells of 15 and 12 realizations, on the random-beta
    and probe-beta designs.
  - How much of the round-1 400-against-4000 difference (N8) is Monte Carlo
    noise.
WHAT IT CANNOT INFORM
  - The Monte Carlo error under calprec v2 betas. The ratio mc_sd/boot_sd is
    expected to depend mostly on B and on the shape of the bootstrap
    distribution, but that is reasoning, and the shape under calprec betas
    is not measured. The rerun's own value is unknown until the rerun
    exists.
  - Coverage. M3 measures the stability of an endpoint, not whether the
    interval covers the true slope at its nominal level. Coverage needs a
    simulation with a known slope (draft items 1 and 3).
  - Interval methods other than the percentile method.

OUTPUT (new folder <outdir>/m3-<timestamp>/, every file opened "x")
  m3_cells.csv  one row per (cell, statistic, B, percentile): mean endpoint,
                mc_sd, boot_sd, ratio, non-finite resamples, seed key rule.
  The console prints, per source, statistic, B and percentile, the median
  and the maximum over cells of mc_sd and of the ratio.

HOW TO RUN (from the repository root, venv active)
    python scripts/m3_bootmc.py --workers 2
  Defaults: --blist 400,1000,2000,4000,10000  --repeats 20. This is the
  longest of M1 to M7: 324 cells x 20 repeats x 17400 resamples, about 113
  million calls of the archived slope fit. No wall time is claimed; the
  log prints the measured one. Exit 0 when done, 2 on a setup error, 3 on
  P0 FAIL.

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

KIND = 63
FILES = ["regimemap.py", "exactcal.py", "reboot.py", "rmapj.py",
         "exactcal_real.csv", "rmapj_real.csv"]
QS = [2.5, 5.0, 95.0, 97.5]


def task(a):
    source, idx, E, blist, K = a
    Jv = np.array(ml.J_LIST, dtype=np.float64)
    R = E.shape[0]
    se = ml.slopes_each(Jv, E)
    out = []
    for B in blist:
        ends = {"curve": [], "slope": []}
        sds = {"curve": [], "slope": []}
        nf = {"curve": 0, "slope": 0}
        for k in range(K):
            rng = ml.rng_for(KIND, [ml.SOURCE_CODE[source], idx, B, k])
            ii = rng.integers(0, R, size=(B, R))
            vals = {"curve": ml.boot_curve(Jv, E, ii),
                    "slope": np.nanmean(se[ii], axis=1)}
            for st in ("curve", "slope"):
                v = vals[st]
                ends[st].append([ml.pct(v, q) for q in QS])
                sds[st].append(float(np.nanstd(v, ddof=1)))
                nf[st] += ml.n_nonfinite(v)
        for st in ("curve", "slope"):
            e = np.array(ends[st])
            bsd = float(np.mean(sds[st]))
            for j, q in enumerate(QS):
                mc = float(np.std(e[:, j], ddof=1))
                out.append({"stat": st, "B": B, "q": q, "mean_end": float(np.mean(e[:, j])),
                            "mc_sd": mc, "boot_sd": bsd,
                            "ratio": mc / bsd if bsd > 0 else float("nan"), "nonfinite": nf[st]})
    return {"source": source, "idx": idx, "rows": out, "rss": ml.rss_mb()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--blist", default="400,1000,2000,4000,10000")
    p.add_argument("--repeats", type=int, default=20)
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    a = p.parse_args()
    try:
        blist = [int(x) for x in a.blist.split(",")]
    except ValueError:
        sys.stderr.write("setup error: --blist must be comma-separated integers\n")
        return 2
    if a.workers < 1 or a.repeats < 5 or min(blist) < 100:
        sys.stderr.write("setup error: --workers >= 1, --repeats >= 5, every B >= 100\n")
        return 2

    outdir = ml.new_outdir("m3")
    ok = ml.print_header(
        "CBO-GAP M3 -- Monte Carlo error of percentile endpoints against B (draft item 3; N8)",
        KIND, a.workers,
        {"B list": blist, "repeats K": a.repeats, "percentiles": QS,
         "statistics": "S_curve and S_slope (as M1), full grid",
         "seed key": "[20261015, 63, source, cell index, B, repeat]",
         "P0": "refit vs stored slope, tol half-unit + 1e-7; exit 3 on fail",
         "verdict": "none; descriptive",
         "covers": "random-beta (exactcal) and probe-beta (rmapj) designs ONLY; "
                   "not calprec betas; not coverage"},
        FILES, outdir)
    if not ok:
        print("SETUP ERROR: archive hash mismatch; nothing measured")
        return 2

    Jv = np.array(ml.J_LIST, dtype=np.float64)
    ex = ml.load_exactcal()
    rj = ml.load_rmapj()
    n1, b1, w1 = ml.p0_check(ex, Jv, "exactcal")
    n2, b2, w2 = ml.p0_check(rj, Jv, "rmapj")
    print("\n  P0 exactcal_real.csv: {} slopes, {} outside tolerance (worst excess {:.2e})".format(n1, b1, w1))
    print("  P0 rmapj_real.csv:    {} slopes, {} outside tolerance (worst excess {:.2e})".format(n2, b2, w2))
    if b1 or b2:
        print("  P0 FAIL: the stored slopes are not reproduced; nothing measured")
        return 3
    print("  P0 PASS")
    sys.stdout.flush()

    keys = {}
    tasks = []
    for i, (k, c) in enumerate(ex.items()):
        keys[("exactcal", i)] = ["", k[0], k[1], k[2], k[3], ""]
        tasks.append(("exactcal", i, c["E"], blist, a.repeats))
    for i, (k, c) in enumerate(rj.items()):
        keys[("rmapj", i)] = [k[0], k[1], k[2], "centred", "0.1", k[3]]
        tasks.append(("rmapj", i, c["E"], blist, a.repeats))
    t0 = time.time()
    with Pool(processes=a.workers) as pool:
        res = pool.map(task, tasks, chunksize=1)
    wall = time.time() - t0

    rows = []
    for r in res:
        for x in r["rows"]:
            rows.append([r["source"], r["idx"]] + keys[(r["source"], r["idx"])] + [
                x["stat"], x["B"], x["q"], ml.fmt(x["mean_end"]), ml.fmt(x["mc_sd"]),
                ml.fmt(x["boot_sd"]), ml.fmt(x["ratio"]), x["nonfinite"],
                "20261015-63-{}-{}-{}-k".format(ml.SOURCE_CODE[r["source"]], r["idx"], x["B"])])
    ml.write_csv(os.path.join(outdir, "m3_cells.csv"),
                 ["source", "cell_index", "diffusion", "objective", "d", "init", "tau", "r",
                  "statistic", "B", "percentile", "mean_endpoint", "mc_sd", "boot_sd",
                  "mc_sd_over_boot_sd", "nonfinite_resamples", "seed_key_rule"], rows)

    print("\n  {} cells in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        len(res), wall, max(r["rss"] for r in res)))
    print("\n  {:<8} {:<6} {:>6} {:>5}  {:>12} {:>12}  {:>10} {:>10}".format(
        "source", "stat", "B", "pct", "mc_sd med", "mc_sd max", "ratio med", "ratio max"))
    for src in ("exactcal", "rmapj"):
        for st in ("curve", "slope"):
            for B in blist:
                for q in QS:
                    xs = [x for r in res if r["source"] == src for x in r["rows"]
                          if x["stat"] == st and x["B"] == B and x["q"] == q]
                    mc = np.array([x["mc_sd"] for x in xs])
                    ra = np.array([x["ratio"] for x in xs])
                    mc, ra = mc[np.isfinite(mc)], ra[np.isfinite(ra)]
                    print("  {:<8} {:<6} {:>6} {:>5}  {:>12.6f} {:>12.6f}  {:>10.4f} {:>10.4f}".format(
                        src, st, B, q, np.median(mc), mc.max(), np.median(ra), ra.max()))
    print("  non-finite resampled values, total: {}".format(
        sum(x["nonfinite"] for r in res for x in r["rows"])))
    print("\n  COVERS random-beta and probe-beta designs only; says nothing about calprec betas")
    print("  and nothing about coverage.")
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
