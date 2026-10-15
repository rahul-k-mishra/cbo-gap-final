"""
m1_estimands.py  --  CBO-GAP measurement M1: how far apart are the two
                     per-cell slope estimands on archived data?

WHY THIS EXISTS
---------------
Ledger N33. The archive reports two different per-cell slopes without saying
which is which:
  S-curve  average E_J over the cell's realizations at each J, then fit one
           slope to the averaged curve (mechanism, control, boundary, sigma,
           crossed, cliff, regime, law, visibility);
  S-slope  fit a slope within each realization, then average the slopes
           (regimemap, and so partm, reboot and rmapj; exactcal P-E2;
           perjcal P-C2).
The rerun must choose one before its first number exists
(notes/ANALYSIS_CRITERIA_DRAFT.md, "A choice that comes before items 1 to
6"). M1 measures how large the difference is on the archived files that
store E_J per realization, so the choice is made knowing the size of what
it changes.

DATA (read-only; hashes checked against zenodo-v1.sha256 before use)
  exactcal_real.csv  144 cells x 15 realizations, E_J at J = 10 ... 5000.
                     beta solved per realization (random-beta design).
  rmapj_real.csv     180 cells x 12 realizations, same J grid. Probe beta,
                     tau_0 = 0.1 nominal, both diffusions, r 0.75 to 3.

METHOD (per cell)
  Window: the full grid, J = 10 ... 5000, the window every archived
  trajectory script used. Window effects are M2's question, not M1's.
  S_curve = regimemap.fit_slope(J, mean over realizations of E_J)
  S_slope = mean over realizations of regimemap.fit_slope(J, E_J of that
            realization)
  gap     = S_slope - S_curve   (positive: the mean of slopes is flatter)
  Bootstrap: realizations of the cell resampled with replacement, B
  resamples, BOTH estimands computed on the SAME resample, so the gap is
  paired within the resample. Seed key [20261015, 61, source code, cell
  index, 0] (scripts/measlib.py). The cell index is the cell's position in
  the file's first-appearance order and is written to the output.
  Interval for the gap: 2.5th and 97.5th percentiles of the B resampled
  gaps (numpy default linear rule, as the archive). Non-finite resampled
  values are dropped and counted.

  Sign convention, worked example (illustrative numbers, not data): three
  realizations with per-realization slopes -1.10, -0.90, -1.00 give
  S_slope = -1.000; if the averaged curve fits to -1.020, the gap is
  -1.000 - (-1.020) = +0.020, the mean of slopes being flatter.

PRE-SPECIFIED CHECK (fixed 2026-10-15, before first execution)
  P0  REPRODUCTION OF THE STORED SLOPES. Every realization's slope is
      refitted with the archived function that wrote it (exactcal.fit_slope
      for exactcal_real.csv, regimemap.fit_slope for rmapj_real.csv, which
      rmapj imports) and compared with the stored string. Tolerance: half a
      unit in the last stored digit (the detcheck rule) plus 1e-7. The
      1e-7 allows for the stored E_J being rounded to 8 significant digits.
      That moves each log E_J by at most about 5e-8, and the slope by less
      than that times the sum of the absolute least-squares weights. This is
      reasoning, not a measurement, and is why the allowance is an order of
      magnitude above it.
      Worked example: stored "-1.22556" has half-unit 5e-6, so the
      tolerance is 5.1e-6; a refit of -1.2255620 differs by 2.0e-6: pass.
      If any realization fails, the script prints P0 FAIL and exits 3
      before measuring anything: the data are not being read as written.
  There is NO verdict criterion. M1 is descriptive. It reports the gap per
  cell and its distribution, and decides nothing. No threshold in this
  script is a proposal for the rerun. B and the 2.5/97.5 levels are the
  measurement's own settings, not proposals for the rerun's criteria.

WHAT THE RESULT CAN INFORM
  - The size and sign of the S-curve against S-slope difference on the
    random-beta (exactcal) and probe-beta (rmapj) designs, per cell, on the
    full grid, at 15 and 12 realizations.
  - Whether the archived numbers that mix the two estimands (ledger N33)
    could differ by an amount comparable to the effects reported.
WHAT IT CANNOT INFORM
  - The gap under calprec v2 betas. Neither file was produced at a fixed
    calibrated beta; exactcal's beta is random, rmapj's is the 4000-point
    probe beta. The rerun's gap is unknown until the rerun exists.
  - The gap on any window other than the full grid (M2), or at a realization
    count other than 15 or 12.
  - Which estimand is right. That is a choice about what the paper claims,
    not a measurement.

OUTPUT (new folder <outdir>/m1-<timestamp>/, every file opened "x")
  m1_cells.csv  one row per cell: source, cell index, cell coordinates, R,
                S_curve, S_slope, gap, gap 2.5 and 97.5 percentiles,
                bootstrap SD of the gap, non-finite resamples, seed key.
  The console prints the gap's distribution (min, quartiles, max) by
  source, by tau_0 for exactcal and by diffusion and d for rmapj, and the
  number of cells whose gap interval excludes zero.

HOW TO RUN (from the repository root, venv active)
    python scripts/m1_estimands.py --workers 2
  Defaults: --boot 4000. Exit 0 when done, 2 on a setup error (archive
  missing or hash mismatch), 3 on P0 FAIL.

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

KIND = 61
FILES = ["regimemap.py", "exactcal.py", "reboot.py", "rmapj.py",
         "exactcal_real.csv", "rmapj_real.csv"]


def task(a):
    source, idx, key, E, B = a
    Jv = np.array(ml.J_LIST, dtype=np.float64)
    R = E.shape[0]
    sc = ml.slope_curve(Jv, E)
    se = ml.slopes_each(Jv, E)
    ss = float(np.nanmean(se))
    rng = ml.rng_for(KIND, [ml.SOURCE_CODE[source], idx, 0])
    ii = rng.integers(0, R, size=(B, R))
    bc = ml.boot_curve(Jv, E, ii)
    bs = np.nanmean(se[ii], axis=1)
    g = bs - bc
    return {"source": source, "idx": idx, "key": key, "R": R, "S_curve": sc,
            "S_slope": ss, "gap": ss - sc, "lo": ml.pct(g, 2.5), "hi": ml.pct(g, 97.5),
            "sd": float(np.nanstd(g, ddof=1)), "nonfinite": ml.n_nonfinite(g),
            "seed_key": ml.key_str(KIND, [ml.SOURCE_CODE[source], idx, 0]),
            "rss": ml.rss_mb()}


def quart(v):
    v = np.asarray(v, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return "n 0"
    return "n {:>3}  min {:+.4f}  q25 {:+.4f}  median {:+.4f}  q75 {:+.4f}  max {:+.4f}".format(
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

    outdir = ml.new_outdir("m1")
    ok = ml.print_header(
        "CBO-GAP M1 -- S-curve against S-slope on archived per-J files (ledger N33)",
        KIND, a.workers,
        {"boot B": a.boot, "window": "full grid J = 10..5000",
         "gap": "S_slope - S_curve (positive = mean of slopes flatter)",
         "interval": "2.5 / 97.5 percentiles of the paired resampled gap",
         "P0": "refit vs stored slope, tol half-unit + 1e-7; exit 3 on fail",
         "verdict": "none; descriptive",
         "covers": "random-beta (exactcal) and probe-beta (rmapj) designs ONLY; "
                   "not calprec betas"},
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

    tasks = []
    for i, (k, c) in enumerate(ex.items()):
        tasks.append(("exactcal", i, k, c["E"], a.boot))
    for i, (k, c) in enumerate(rj.items()):
        tasks.append(("rmapj", i, k, c["E"], a.boot))
    t0 = time.time()
    with Pool(processes=a.workers) as pool:
        res = pool.map(task, tasks, chunksize=1)
    wall = time.time() - t0

    rows = []
    for r in res:
        k = r["key"]
        if r["source"] == "exactcal":
            coords = ["", k[0], k[1], k[2], k[3], ""]
        else:
            coords = [k[0], k[1], k[2], "centred", "0.1", k[3]]
        rows.append([r["source"], r["idx"]] + coords + [
            r["R"], ml.fmt(r["S_curve"]), ml.fmt(r["S_slope"]), ml.fmt(r["gap"]),
            ml.fmt(r["lo"]), ml.fmt(r["hi"]), ml.fmt(r["sd"]), r["nonfinite"], r["seed_key"]])
    ml.write_csv(os.path.join(outdir, "m1_cells.csv"),
                 ["source", "cell_index", "diffusion", "objective", "d", "init", "tau", "r",
                  "R", "S_curve", "S_slope", "gap", "gap_p2_5", "gap_p97_5", "gap_boot_sd",
                  "nonfinite_resamples", "seed_key"], rows)

    print("\n  {} cells in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        len(res), wall, max(r["rss"] for r in res)))
    print("\n  gap = S_slope - S_curve, full grid")
    for src in ("exactcal", "rmapj"):
        sub = [r for r in res if r["source"] == src]
        excl = sum(1 for r in sub if r["lo"] > 0 or r["hi"] < 0)
        print("  {:<9} all           {}".format(src, quart([r["gap"] for r in sub])))
        print("  {:<9} intervals excluding 0: {} of {}".format(src, excl, len(sub)))
    for t in ("0.5", "0.1", "0.01"):
        sub = [r for r in res if r["source"] == "exactcal" and r["key"][3] == t]
        print("  exactcal  tau {:<5}     {}".format(t, quart([r["gap"] for r in sub])))
    for dif in ("isotropic", "anisotropic"):
        for d in (5, 10, 20, 40, 80):
            sub = [r for r in res if r["source"] == "rmapj" and r["key"][0] == dif and r["key"][2] == d]
            print("  rmapj     {:<11} d {:<3} {}".format(dif, d, quart([r["gap"] for r in sub])))
    print("  bootstrap SD of the gap, all cells: {}".format(quart([r["sd"] for r in res])))
    print("  non-finite resampled gaps, total: {}".format(sum(r["nonfinite"] for r in res)))
    print("\n  COVERS random-beta and probe-beta designs only; says nothing about calprec betas.")
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
