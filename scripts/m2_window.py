"""
m2_window.py  --  CBO-GAP measurement M2: how much does the fit window move
                  the slope, at tau_0 = 0.5, 0.1 and 0.01, on archived data?

WHY THIS EXISTS
---------------
notes/ANALYSIS_CRITERIA_DRAFT.md item 2. The rerun needs a fit window per
row, fixed before its first number. The only archived window check is
audit.py A5: tau_0 = 0.1 only, on probe-calibrated cell means (tex 352: "This
was not tested at tighter targets"). M2 measures window sensitivity per cell
on the two archived files that store E_J per realization. It also
reconstructs the point estimates of Table 3's d = 2 to d = 40 change on two
windows, because no archived script computes them (ledger N30).

DATA (read-only; hashes checked against zenodo-v1.sha256 before use)
  exactcal_real.csv  144 cells x 15, tau_0 in {0.5, 0.1, 0.01}, random beta.
  rmapj_real.csv     180 cells x 12, tau_0 = 0.1, probe beta.

WINDOWS (the options of the draft's item 2; tau_0 read EXACTLY from the
CSV string as a fraction, so 1/tau_0 has no floating-point error)
  W-full   every J in 10 ... 5000                           (option 2A)
  W-ge     J >= 1/tau_0                                     (option 2B)
  W-gt     J >  1/tau_0                                     (option 2C)
  W-4      J >  4 (1/tau_0 - 1)                             (option 2D)
  W-100    J >= 100 at every tau_0 (exactcal only; 100 = 1/0.01, the
           tightest tau_0 in that file)                     (option 2G)
  Worked example, tau_0 = 0.1: W-ge keeps 10 ... 5000 (10 sizes), W-gt keeps
  20 ... 5000 (9), W-4 keeps J > 36, so 40 ... 5000 (8). At tau_0 = 0.01:
  W-ge and W-gt keep 160 ... 5000 (6), W-4 keeps J > 396, so 640 ... 5000
  (4). A window with fewer than 3 sizes is skipped and reported.
  Windows that coincide with W-full for a cell are still computed and
  marked "same as W-full", so no comparison is silently dropped.

METHOD (per cell and window)
  S_curve and S_slope exactly as in M1 (regimemap.fit_slope, imported).
  shift(W) = S(W) - S(W-full) for each estimand (positive: flatter on W).
  Bootstrap: realizations resampled with replacement, B resamples, ONE set
  of resample indices per cell shared by every window and both estimands,
  so window differences are paired. Seed key [20261015, 62, source code,
  cell index, 0]. Reported per window: point S, bootstrap SD of S, shift,
  bootstrap SD of the shift, 2.5 and 97.5 percentiles of the shift.

  Table 3 reconstruction (exactcal only; reported, no verdict). For each
  tau_0, window in {W-full, W-ge} and estimand: change = mean over the
  twelve (objective, init) of S at d = 40 minus the same mean at d = 2.
  Sign, worked example (illustrative numbers): mean slopes -1.06 at d = 2
  and -1.01 at d = 40 give change = -1.01 - (-1.06) = +0.05, flatter at
  d = 40, the sign Table 3 prints in "change 2 -> 40". The manuscript's
  values are at tex 369-375 (Table 3), tex 34 and tex 563. The script
  prints its values and does not compare them; a reader compares. A match
  would identify the estimand and window Table 3 used. A mismatch would
  not show which number is wrong.

PRE-SPECIFIED CHECK (fixed 2026-10-15, before first execution)
  P0  as in m1_estimands.py: every stored slope is reproduced by the
      archived fit to half a unit in the last stored digit plus 1e-7, or the
      script exits 3 before measuring. Worked example there.
  There is NO verdict criterion. M2 is descriptive. No window, threshold or
  level in this script is a proposal for the rerun. B and the 2.5/97.5
  levels are the measurement's own settings.

WHAT THE RESULT CAN INFORM
  - How far each candidate window moves the per-cell slope, and how that
    compares with the per-cell bootstrap SD, on the random-beta design at
    tau_0 = 0.5, 0.1 and 0.01 and on the probe-beta design at tau_0 = 0.1.
  - Whether the archived Table 3 change values follow from exactcal_real.csv
    on the full grid or on J >= 1/tau_0, and under which estimand (N30).
WHAT IT CANNOT INFORM
  - Window sensitivity under calprec v2 betas. Neither file was produced at
    a fixed calibrated beta, and tau(beta) for a calprec cell can differ from
    nominal (ledger N19), which moves 1/tau. The rerun's sensitivity is
    unknown until the rerun exists.
  - Windows at tau_0 values other than 0.5, 0.1 and 0.01 (TAU8, GEOM, RMAP
    use others), or for rows with no tau_0 (BETA-ISO, BETA-ANI, LAWPANEL).
  - Which window is right. That depends on what the paper claims.
  - Anything about the twelve-unit intervals of Table 3 (withdrawn; R6).

OUTPUT (new folder <outdir>/m2-<timestamp>/, every file opened "x")
  m2_windows.csv  one row per (cell, window, estimand): sizes kept, S, SD,
                  shift from W-full, shift SD, shift 2.5 and 97.5
                  percentiles, non-finite count, seed key.
  m2_table3.csv   one row per (tau_0, window, estimand): mean at d = 2,
                  mean at d = 40, change.

HOW TO RUN (from the repository root, venv active)
    python scripts/m2_window.py --workers 2
  Defaults: --boot 4000. Exit 0 when done, 2 on a setup error, 3 on P0
  FAIL.

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import argparse
import os
import sys
import time
from fractions import Fraction
from multiprocessing import Pool

import numpy as np

sys.dont_write_bytecode = True

import measlib as ml                                            # noqa: E402

KIND = 62
FILES = ["regimemap.py", "exactcal.py", "reboot.py", "rmapj.py",
         "exactcal_real.csv", "rmapj_real.csv"]
WINDOWS = ["W-full", "W-ge", "W-gt", "W-4", "W-100"]


def window_sizes(name, tau_str, source):
    t = Fraction(tau_str)
    inv = 1 / t
    if name == "W-full":
        return list(ml.J_LIST)
    if name == "W-ge":
        return [J for J in ml.J_LIST if J >= inv]
    if name == "W-gt":
        return [J for J in ml.J_LIST if J > inv]
    if name == "W-4":
        return [J for J in ml.J_LIST if J > 4 * (inv - 1)]
    if name == "W-100":
        return [J for J in ml.J_LIST if J >= 100] if source == "exactcal" else None
    raise ValueError(name)


def task(a):
    source, idx, key, tau_str, E, B = a
    R = E.shape[0]
    rng = ml.rng_for(KIND, [ml.SOURCE_CODE[source], idx, 0])
    ii = rng.integers(0, R, size=(B, R))
    full_cols = list(range(len(ml.J_LIST)))
    out = []
    base = {}
    for w in WINDOWS:
        Js = window_sizes(w, tau_str, source)
        if Js is None:
            continue
        if len(Js) < 3:
            out.append({"w": w, "Js": Js, "skip": True})
            continue
        cols = [ml.J_LIST.index(J) for J in Js]
        Jv = np.array(Js, dtype=np.float64)
        Ew = E[:, cols]
        sc = ml.slope_curve(Jv, Ew)
        se = ml.slopes_each(Jv, Ew)
        ss = float(np.nanmean(se))
        bc = ml.boot_curve(Jv, Ew, ii)
        bs = np.nanmean(se[ii], axis=1)
        rec = {"w": w, "Js": Js, "skip": False, "same": cols == full_cols,
               "curve": (sc, bc), "slope": (ss, bs)}
        if w == "W-full":
            base = rec
        out.append(rec)
    rows = []
    for rec in out:
        if rec["skip"]:
            rows.append({"w": rec["w"], "n": len(rec["Js"]), "skip": True})
            continue
        for est in ("curve", "slope"):
            pt, bt = rec[est]
            p0, b0 = base[est]
            sh = bt - b0
            rows.append({"w": rec["w"], "n": len(rec["Js"]), "skip": False, "same": rec["same"],
                         "est": est, "S": pt, "S_sd": float(np.nanstd(bt, ddof=1)),
                         "shift": pt - p0, "shift_sd": float(np.nanstd(sh, ddof=1)),
                         "lo": ml.pct(sh, 2.5), "hi": ml.pct(sh, 97.5),
                         "nonfinite": ml.n_nonfinite(bt)})
    return {"source": source, "idx": idx, "key": key, "tau": tau_str, "rows": rows,
            "seed_key": ml.key_str(KIND, [ml.SOURCE_CODE[source], idx, 0]), "rss": ml.rss_mb()}


def quart(v):
    v = np.asarray(v, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return "n   0"
    return "n {:>3}  min {:+.4f}  q25 {:+.4f}  med {:+.4f}  q75 {:+.4f}  max {:+.4f}".format(
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

    outdir = ml.new_outdir("m2")
    ok = ml.print_header(
        "CBO-GAP M2 -- fit-window sensitivity on archived per-J files (draft item 2; N30)",
        KIND, a.workers,
        {"boot B": a.boot, "windows": "W-full, W-ge (J>=1/tau0), W-gt (J>1/tau0), "
                                      "W-4 (J>4(1/tau0-1)), W-100 (exactcal, J>=100)",
         "tau_0": "read exactly as a fraction from the CSV string",
         "shift": "S(W) - S(W-full), paired on shared resample indices",
         "estimands": "S_curve and S_slope (as M1)",
         "P0": "refit vs stored slope, tol half-unit + 1e-7; exit 3 on fail",
         "verdict": "none; descriptive",
         "covers": "random-beta (exactcal) and probe-beta (rmapj) designs ONLY; "
                   "not calprec betas"},
        FILES, outdir)
    if not ok:
        print("SETUP ERROR: archive hash mismatch; nothing measured")
        return 2
    print("  window sizes by tau_0:")
    for t in ("0.5", "0.1", "0.01"):
        for w in WINDOWS:
            print("    tau {:<5} {:<7} {}".format(t, w, window_sizes(w, t, "exactcal")))

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
        tasks.append(("exactcal", i, k, k[3], c["E"], a.boot))
    for i, (k, c) in enumerate(rj.items()):
        tasks.append(("rmapj", i, k, "0.1", c["E"], a.boot))
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
        for x in r["rows"]:
            if x["skip"]:
                rows.append([r["source"], r["idx"]] + coords + [x["w"], x["n"], "skipped (<3 sizes)",
                                                                "", "", "", "", "", "", "", "", r["seed_key"]])
                continue
            rows.append([r["source"], r["idx"]] + coords + [
                x["w"], x["n"], "same as W-full" if x["same"] else "differs", x["est"],
                ml.fmt(x["S"]), ml.fmt(x["S_sd"]), ml.fmt(x["shift"]), ml.fmt(x["shift_sd"]),
                ml.fmt(x["lo"]), ml.fmt(x["hi"]), x["nonfinite"], r["seed_key"]])
    ml.write_csv(os.path.join(outdir, "m2_windows.csv"),
                 ["source", "cell_index", "diffusion", "objective", "d", "init", "tau", "r",
                  "window", "n_sizes", "relation", "estimand", "S", "S_boot_sd", "shift",
                  "shift_boot_sd", "shift_p2_5", "shift_p97_5", "nonfinite_resamples",
                  "seed_key"], rows)

    print("\n  {} cells in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        len(res), wall, max(r["rss"] for r in res)))

    print("\n  shift = S(window) - S(W-full); |shift| / shift SD in the second line")
    for src, taus in (("exactcal", ("0.5", "0.1", "0.01")), ("rmapj", ("0.1",))):
        for t in taus:
            for w in WINDOWS[1:]:
                for est in ("curve", "slope"):
                    xs = [x for r in res if r["source"] == src and r["tau"] == t
                          for x in r["rows"] if x["w"] == w and not x["skip"] and x["est"] == est]
                    if not xs:
                        continue
                    same = all(x["same"] for x in xs)
                    excl = sum(1 for x in xs if x["lo"] > 0 or x["hi"] < 0)
                    print("  {:<8} tau {:<5} {:<6} S_{:<5} {}{}".format(
                        src, t, w, est, quart([x["shift"] for x in xs]),
                        "   (same as W-full)" if same else ""))
                    z = [abs(x["shift"]) / x["shift_sd"] for x in xs if x["shift_sd"] > 0]
                    print("  {:<8} {:<9} {:<6} {:<7} |shift|/SD {}   intervals excluding 0: {} of {}".format(
                        "", "", "", "", quart(z), excl, len(xs)))
            for est in ("curve", "slope"):
                xs = [x for r in res if r["source"] == src and r["tau"] == t
                      for x in r["rows"] if x["w"] == "W-full" and x["est"] == est]
                print("  {:<8} tau {:<5} W-full S_{:<5} bootstrap SD of S: {}".format(
                    src, t, est, quart([x["S_sd"] for x in xs])))

    t3 = []
    print("\n  Table 3 reconstruction (exactcal; mean over 12 objective-init units; "
          "change = d40 - d2; no verdict)")
    for t in ("0.5", "0.1", "0.01"):
        for w in ("W-full", "W-ge"):
            for est in ("curve", "slope"):
                m = {}
                for dd in (2, 40):
                    vals = [x["S"] for r in res if r["source"] == "exactcal" and r["tau"] == t
                            and r["key"][1] == dd for x in r["rows"]
                            if x["w"] == w and not x["skip"] and x["est"] == est]
                    m[dd] = (float(np.mean(vals)), len(vals))
                ch = m[40][0] - m[2][0]
                t3.append([t, w, est, ml.fmt(m[2][0]), ml.fmt(m[40][0]), ml.fmt(ch), m[2][1], m[40][1]])
                print("  tau {:<5} {:<7} S_{:<5}  d=2 {:+.4f}  d=40 {:+.4f}  change {:+.4f}  (units {} / {})".format(
                    t, w, est, m[2][0], m[40][0], ch, m[2][1], m[40][1]))
    ml.write_csv(os.path.join(outdir, "m2_table3.csv"),
                 ["tau", "window", "estimand", "mean_d2", "mean_d40", "change_d40_minus_d2",
                  "units_d2", "units_d40"], t3)
    print("\n  COVERS random-beta and probe-beta designs only; says nothing about calprec betas.")
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
