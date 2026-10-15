"""
m4_slopese.py  --  CBO-GAP measurement M4: the realization-level standard
                   error of the per-cell slope, on archived data

WHY THIS EXISTS
---------------
notes/ANALYSIS_CRITERIA_DRAFT.md items 4 and 5; ledger N30. Several archived
tolerances are tied to a "noise floor":
  - 0.0219, the delta-method SE from per-J standard errors (audit.py A1),
    which tex 78 itself calls biased downward;
  - 0.0260, a realization-level bootstrap median over 420 cells (tex 78),
    for which no archived code exists (N30).
The rerun cannot measure its own SE before it runs, so any tolerance tied to
a noise scale is either carried over or set by a rule (draft 4A to 4C).
M4 measures the realization-level SE per cell on every archived file that
allows it, so that the carried-over values can be compared with what the
archive itself gives.

DATA (read-only; hashes checked against zenodo-v1.sha256 before use)
  exactcal_real.csv     144 cells x 15, per J, random beta.
  rmapj_real.csv        180 cells x 12, per J, probe beta, tau_0 0.1.
  regimemap_D_real.csv  180 cells x 12, per-realization slopes only (Part D;
                        the same realizations as rmapj, rmapj P-R1).
  regimemap_M_real.csv  240 cells x 12, per-realization slopes only (Part M,
                        tau_0 0.5 / 0.1 / 0.03 / 0.01), probe beta.
  420 = 180 (D) + 240 (M), the cell count tex 78 gives for 0.0260.

METHOD (per cell; full grid J = 10 ... 5000 where E_J is stored)
  se_boot_curve  bootstrap SD of S_curve (per-J files only): realizations
                 resampled, slope refitted on the resampled mean curve
                 (regimemap.fit_slope), B resamples. This is the construction
                 tex 78 describes ("all J values within a realization move
                 together and the slope is refitted on each resample").
  se_boot_slope  bootstrap SD of S_slope: per-realization slopes (refitted
                 for the per-J files, the stored ones for regimemap files)
                 resampled, B resamples.
  se_plain_slope SD of the per-realization slopes / sqrt(R), no bootstrap.
  Seed key [20261015, 64, source code, cell index, 0].
  Worked example (illustrative numbers): 12 per-realization slopes with
  sample SD 0.090 give se_plain_slope = 0.090 / sqrt(12) = 0.0260.

  Candidate reconstructions of tex 78's 0.0260 (median) and [0.0191, 0.0341]
  (IQR), printed side by side and NOT judged:
    C-a  median and IQR of se_boot_slope over the 420 regimemap cells;
    C-b  median and IQR of se_plain_slope over the same 420;
    C-c  median and IQR of se_boot_curve over the 180 rmapj cells (the only
         Part D or M file that allows the refit construction).
  The bootstrap of tex 78 is not archived, so its B and seed are unknown.
  Agreement of a candidate would identify the construction; disagreement
  would not show 0.0260 wrong.

PRE-SPECIFIED CHECK (fixed 2026-10-15, before first execution)
  P0  as in m1_estimands.py, on exactcal_real.csv and rmapj_real.csv: stored
      slopes reproduced by the archived fit to half a unit in the last
      stored digit plus 1e-7, or exit 3. Worked example there.
  There is NO verdict criterion. M4 is descriptive and sets no tolerance.
  B is the measurement's own setting.

WHAT THE RESULT CAN INFORM
  - The realization-level slope SE per cell, by construction, on the
    random-beta (exactcal) and probe-beta (rmapj, regimemap) designs, at 15
    and 12 realizations, on the full grid.
  - Whether one of three plausible constructions reproduces tex 78's 0.0260
    (N30), and how the three constructions differ.
  - The size of the per-cell SE against the archived tolerances (0.0219,
    0.0260, 2 x 0.0219, 0.05, 0.10, 0.15) that the rerun may or may not
    re-adopt.
WHAT IT CANNOT INFORM
  - The SE under calprec v2 betas. None of these files was produced at a
    fixed calibrated beta. The rerun's SE is unknown until the rerun exists.
  - The SE on windows other than the full grid (see M2 for window shifts).
  - What any tolerance should be. That is a choice (draft item 4).

OUTPUT (new folder <outdir>/m4-<timestamp>/, every file opened "x")
  m4_cells.csv  one row per cell: source, cell index, coordinates, R,
                S_curve (if available), S_slope, se_boot_curve,
                se_boot_slope, se_plain_slope, non-finite counts, seed key.

HOW TO RUN (from the repository root, venv active)
    python scripts/m4_slopese.py --workers 2
  Defaults: --boot 4000. Exit 0 when done, 2 on a setup error, 3 on P0
  FAIL.

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import argparse
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.dont_write_bytecode = True

import measlib as ml                                            # noqa: E402

KIND = 64
FILES = ["regimemap.py", "exactcal.py", "reboot.py", "rmapj.py",
         "exactcal_real.csv", "rmapj_real.csv",
         "regimemap_D_real.csv", "regimemap_M_real.csv"]


def task(a):
    source, idx, E, slopes, B = a
    Jv = np.array(ml.J_LIST, dtype=np.float64)
    rng = ml.rng_for(KIND, [ml.SOURCE_CODE[source], idx, 0])
    out = {"source": source, "idx": idx, "S_curve": float("nan"),
           "se_boot_curve": float("nan"), "nf_curve": 0}
    if E is not None:
        R = E.shape[0]
        se = ml.slopes_each(Jv, E)
        ii = rng.integers(0, R, size=(B, R))
        bc = ml.boot_curve(Jv, E, ii)
        out["S_curve"] = ml.slope_curve(Jv, E)
        out["se_boot_curve"] = float(np.nanstd(bc, ddof=1))
        out["nf_curve"] = ml.n_nonfinite(bc)
    else:
        se = np.asarray(slopes, dtype=np.float64)
        R = se.size
        ii = rng.integers(0, R, size=(B, R))
    bs = np.nanmean(se[ii], axis=1)
    fin = se[np.isfinite(se)]
    out.update({"R": R, "S_slope": float(np.nanmean(se)),
                "se_boot_slope": float(np.nanstd(bs, ddof=1)),
                "se_plain_slope": float(np.std(fin, ddof=1) / math.sqrt(fin.size)),
                "nf_slope": ml.n_nonfinite(se),
                "seed_key": ml.key_str(KIND, [ml.SOURCE_CODE[source], idx, 0]),
                "rss": ml.rss_mb()})
    return out


def summ(v):
    v = np.asarray(v, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return "n   0"
    return "n {:>3}  median {:.4f}  IQR [{:.4f},{:.4f}]  min {:.4f}  max {:.4f}".format(
        v.size, np.median(v), np.percentile(v, 25), np.percentile(v, 75), v.min(), v.max())


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

    outdir = ml.new_outdir("m4")
    ok = ml.print_header(
        "CBO-GAP M4 -- realization-level slope SE per cell (draft items 4, 5; N30)",
        KIND, a.workers,
        {"boot B": a.boot, "window": "full grid J = 10..5000 (per-J files)",
         "constructions": "se_boot_curve, se_boot_slope, se_plain_slope",
         "candidates": "C-a, C-b over 420 regimemap cells; C-c over 180 rmapj cells",
         "P0": "refit vs stored slope (per-J files), tol half-unit + 1e-7; exit 3 on fail",
         "verdict": "none; descriptive",
         "covers": "random-beta (exactcal) and probe-beta (rmapj, regimemap) designs "
                   "ONLY; not calprec betas"},
        FILES, outdir)
    if not ok:
        print("SETUP ERROR: archive hash mismatch; nothing measured")
        return 2

    Jv = np.array(ml.J_LIST, dtype=np.float64)
    ex = ml.load_exactcal()
    rj = ml.load_rmapj()
    rd = ml.load_regimemap("regimemap_D_real.csv")
    rmm = ml.load_regimemap("regimemap_M_real.csv")
    n1, b1, w1 = ml.p0_check(ex, Jv, "exactcal")
    n2, b2, w2 = ml.p0_check(rj, Jv, "rmapj")
    print("\n  P0 exactcal_real.csv: {} slopes, {} outside tolerance (worst excess {:.2e})".format(n1, b1, w1))
    print("  P0 rmapj_real.csv:    {} slopes, {} outside tolerance (worst excess {:.2e})".format(n2, b2, w2))
    if b1 or b2:
        print("  P0 FAIL: the stored slopes are not reproduced; nothing measured")
        return 3
    print("  P0 PASS")
    print("  cells: exactcal {}, rmapj {}, regimemap_D {}, regimemap_M {}".format(
        len(ex), len(rj), len(rd), len(rmm)))
    sys.stdout.flush()

    coords, tasks = {}, []
    for i, (k, c) in enumerate(ex.items()):
        coords[("exactcal", i)] = ["", k[0], k[1], k[2], k[3], ""]
        tasks.append(("exactcal", i, c["E"], None, a.boot))
    for i, (k, c) in enumerate(rj.items()):
        coords[("rmapj", i)] = [k[0], k[1], k[2], "centred", "0.1", k[3]]
        tasks.append(("rmapj", i, c["E"], None, a.boot))
    for src, cells in (("regimemap_D", rd), ("regimemap_M", rmm)):
        for i, (k, c) in enumerate(cells.items()):
            coords[(src, i)] = [k[0], k[1], k[2], "centred", k[4], k[3]]
            tasks.append((src, i, None, c["slope"], a.boot))
    t0 = time.time()
    with Pool(processes=a.workers) as pool:
        res = pool.map(task, tasks, chunksize=1)
    wall = time.time() - t0

    rows = []
    for r in res:
        rows.append([r["source"], r["idx"]] + coords[(r["source"], r["idx"])] + [
            r["R"], ml.fmt(r["S_curve"]), ml.fmt(r["S_slope"]), ml.fmt(r["se_boot_curve"]),
            ml.fmt(r["se_boot_slope"]), ml.fmt(r["se_plain_slope"]), r["nf_curve"],
            r["nf_slope"], r["seed_key"]])
    ml.write_csv(os.path.join(outdir, "m4_cells.csv"),
                 ["source", "cell_index", "diffusion", "objective", "d", "init", "tau", "r",
                  "R", "S_curve", "S_slope", "se_boot_curve", "se_boot_slope",
                  "se_plain_slope", "nonfinite_curve_resamples", "nonfinite_slopes",
                  "seed_key"], rows)

    print("\n  {} cells in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        len(res), wall, max(r["rss"] for r in res)))
    print()
    for src in ("exactcal", "rmapj", "regimemap_D", "regimemap_M"):
        sub = [r for r in res if r["source"] == src]
        for f in ("se_boot_curve", "se_boot_slope", "se_plain_slope"):
            v = [r[f] for r in sub]
            if not np.any(np.isfinite(v)):
                continue
            print("  {:<12} {:<15} {}".format(src, f, summ(v)))
    for t in ("0.5", "0.1", "0.01"):
        sub = [r for r in res if r["source"] == "exactcal" and coords[("exactcal", r["idx"])][4] == t]
        print("  exactcal tau {:<5} se_boot_curve  {}".format(t, summ([r["se_boot_curve"] for r in sub])))
    for t in ("0.5", "0.1", "0.03", "0.01"):
        sub = [r for r in res if r["source"] == "regimemap_M" and coords[("regimemap_M", r["idx"])][4] == t]
        print("  regimemap_M tau {:<5} se_boot_slope {}".format(t, summ([r["se_boot_slope"] for r in sub])))
    rm420 = [r for r in res if r["source"] in ("regimemap_D", "regimemap_M")]
    print("\n  candidate reconstructions of tex 78 (0.0260, IQR [0.0191,0.0341], 420 cells); not judged")
    print("  C-a se_boot_slope  over regimemap D+M  {}".format(summ([r["se_boot_slope"] for r in rm420])))
    print("  C-b se_plain_slope over regimemap D+M  {}".format(summ([r["se_plain_slope"] for r in rm420])))
    print("  C-c se_boot_curve  over rmapj          {}".format(
        summ([r["se_boot_curve"] for r in res if r["source"] == "rmapj"])))
    print("\n  COVERS random-beta and probe-beta designs only; says nothing about calprec betas.")
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
