"""
m5_gapwidth.py  --  CBO-GAP measurement M5: how wide is a 90% interval for an
                    anisotropic-minus-isotropic slope gap when the two arms
                    are independent, at 12 realizations per arm?

WHY THIS EXISTS
---------------
notes/ANALYSIS_CRITERIA_DRAFT.md item 5; ledger N31. An equivalence verdict at
margin m is possible only if the 90% interval for a gap can be narrower than
2m. Whether a margin is attainable at 12 realizations per arm therefore has
to be known before the margin is chosen. The archive's two arms are
independent (N31: they never shared seeds), so the archive measures the
independent-arm case directly. Whether the rerun shares seed keys across
diffusions is an open decision, and shared keys might narrow the interval.
M5 cannot measure that.

DATA (read-only; hashes checked against zenodo-v1.sha256 before use)
  rmapj_real.csv        Part D, 180 cells x 12, per J: 3 objectives x d {5,
                        10, 20, 40, 80} x r {0.75 ... 3.0} x 2 diffusions,
                        tau_0 0.1, probe beta.
  regimemap_M_real.csv  Part M, 240 cells x 12, slopes only: 3 objectives x
                        d {10, 40} x r {0.5 ... 3.0} x tau_0 {0.5, 0.1, 0.03,
                        0.01} x 2 diffusions, probe beta.

METHOD
  gap = S(anisotropic) - S(isotropic)  (positive: anisotropic flatter; the
  sign of tex 650). S is S_curve or S_slope as in M1; Part M allows S_slope
  only.
  Three levels, each with its own independent-arm bootstrap (B resamples,
  each arm resampled separately, never paired):
    L-cell    one objective: 12 against 12;
    L-pool-u  the three objectives pooled per arm, 36 against 36, resampled
              without regard to objective (the archive's pooling, made
              independent);
    L-pool-s  the three objectives pooled, resampled within each objective
              and each arm (stratified), gap = mean over the three objectives
              of the per-objective gap. For S_curve the per-objective gap is
              the S_curve difference.
  Interval: 5th and 95th percentiles (the 90% two-sided interval that TOST
  at 5% per side uses, as audit A3, regimemap and reboot). half-width =
  (p95 - p5) / 2.
  Seed key [20261015, 65, source code, group index, level code, arm], where
  the level codes are L-cell 1, L-pool-u 2 and L-pool-s 3, and arm is 0
  isotropic or 1 anisotropic. Group indices are positions in the sorted
  group list and are written to the output.
  Worked example (illustrative numbers): resampled gaps with p5 = +0.010 and
  p95 = +0.090 give half-width 0.040; an interval of that half-width can lie
  inside +-m only if m > 0.040.

PRE-SPECIFIED CHECK (fixed 2026-10-15, before first execution)
  P0  as in m1_estimands.py, on rmapj_real.csv: stored slopes reproduced by
      the archived fit to half a unit in the last stored digit plus 1e-7, or
      exit 3. Worked example there.
  There is NO verdict criterion. M5 reports half-widths. It does not compare
  them with any margin, and no margin in this script is a proposal for the
  rerun.

WHAT THE RESULT CAN INFORM
  - The distribution of 90% half-widths for an iso/aniso gap under the
    probe-beta design with independent arms, at 12 realizations per arm per
    objective, per objective and pooled over three objectives, at tau_0 0.1
    (Part D) and at tau_0 0.5, 0.1, 0.03, 0.01 (Part M, S_slope only).
  - Whether a given margin was attainable at all in the archived design.
WHAT IT CANNOT INFORM
  - Half-widths under calprec v2 betas. These files were produced at the
    4000-point probe beta. The rerun's half-widths are unknown until it
    exists.
  - Half-widths with shared seed keys across diffusions (common random
    numbers). The archive has no such pair; a pilot would be needed.
  - The ANISO row (crossed.py) design at matched sigma, whose files are cell
    means only (ARC2), or the SIGMA and CLIFF rows.
  - Which margin is right. That is a convention (draft item 5).

OUTPUT (new folder <outdir>/m5-<timestamp>/, every file opened "x")
  m5_gaps.csv  one row per (source, group, level, estimand): coordinates,
               R per arm, gap, p5, p95, half-width, non-finite count, seed
               keys.

HOW TO RUN (from the repository root, venv active)
    python scripts/m5_gapwidth.py --workers 2
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

KIND = 65
FILES = ["regimemap.py", "exactcal.py", "reboot.py", "rmapj.py",
         "rmapj_real.csv", "regimemap_M_real.csv"]
OBJS = ["ackley", "rastrigin", "sphere"]
LEVEL = {"L-cell": 1, "L-pool-u": 2, "L-pool-s": 3}


def resample_stat(rng, data, est, B):
    """data: per objective, a (R, J) array (S_curve) or (R,) slopes (S_slope).
    Returns B values of the statistic on one arm."""
    Jv = np.array(ml.J_LIST, dtype=np.float64)
    if est == "curve":
        out = []
        for E in data:
            ii = rng.integers(0, E.shape[0], size=(B, E.shape[0]))
            out.append(ml.boot_curve(Jv, E, ii))
        return out
    out = []
    for s in data:
        ii = rng.integers(0, s.size, size=(B, s.size))
        out.append(np.nanmean(s[ii], axis=1))
    return out


def task(a):
    source, gidx, coords, level, est, iso, ani, B = a
    lc = LEVEL[level]
    keys = [ml.key_str(KIND, [ml.SOURCE_CODE[source], gidx, lc, arm]) for arm in (0, 1)]
    rngs = [ml.rng_for(KIND, [ml.SOURCE_CODE[source], gidx, lc, arm]) for arm in (0, 1)]
    Jv = np.array(ml.J_LIST, dtype=np.float64)

    def point(data):
        if est == "curve":
            return [ml.slope_curve(Jv, E) for E in data]
        return [float(np.nanmean(s)) for s in data]

    if level == "L-pool-u":
        if est == "curve":
            iso_d, ani_d = [np.vstack(iso)], [np.vstack(ani)]
        else:
            iso_d, ani_d = [np.concatenate(iso)], [np.concatenate(ani)]
    else:
        iso_d, ani_d = iso, ani
    bi = resample_stat(rngs[0], iso_d, est, B)
    ba = resample_stat(rngs[1], ani_d, est, B)
    g = np.mean(np.vstack(ba), axis=0) - np.mean(np.vstack(bi), axis=0)
    gap = float(np.mean(point(ani_d)) - np.mean(point(iso_d)))
    lo, hi = ml.pct(g, 5.0), ml.pct(g, 95.0)
    R = [x.shape[0] for x in iso_d]
    return {"source": source, "gidx": gidx, "coords": coords, "level": level, "est": est,
            "R": "/".join(str(x) for x in R), "gap": gap, "lo": lo, "hi": hi,
            "hw": 0.5 * (hi - lo), "nonfinite": ml.n_nonfinite(g), "keys": " ".join(keys),
            "rss": ml.rss_mb()}


def summ(v):
    v = np.asarray(v, dtype=np.float64)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return "n   0"
    q = np.percentile(v, [0, 10, 25, 50, 75, 90, 100])
    return "n {:>3}  min {:.4f}  p10 {:.4f}  q25 {:.4f}  med {:.4f}  q75 {:.4f}  p90 {:.4f}  max {:.4f}".format(
        v.size, *q)


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

    outdir = ml.new_outdir("m5")
    ok = ml.print_header(
        "CBO-GAP M5 -- 90% half-width of iso/aniso gaps, independent arms (draft item 5; N31)",
        KIND, a.workers,
        {"boot B": a.boot, "gap": "S(anisotropic) - S(isotropic)",
         "interval": "5 / 95 percentiles; half-width = (p95 - p5) / 2",
         "levels": "L-cell (12 v 12), L-pool-u (36 v 36), L-pool-s (stratified by objective)",
         "estimands": "Part D: S_curve and S_slope; Part M: S_slope only",
         "P0": "refit vs stored slope (rmapj), tol half-unit + 1e-7; exit 3 on fail",
         "verdict": "none; no margin is compared",
         "covers": "probe-beta design, independent arms ONLY; not calprec betas, "
                   "not shared seed keys"},
        FILES, outdir)
    if not ok:
        print("SETUP ERROR: archive hash mismatch; nothing measured")
        return 2

    Jv = np.array(ml.J_LIST, dtype=np.float64)
    rj = ml.load_rmapj()
    rmm = ml.load_regimemap("regimemap_M_real.csv")
    n2, b2, w2 = ml.p0_check(rj, Jv, "rmapj")
    print("\n  P0 rmapj_real.csv: {} slopes, {} outside tolerance (worst excess {:.2e})".format(n2, b2, w2))
    if b2:
        print("  P0 FAIL: the stored slopes are not reproduced; nothing measured")
        return 3
    print("  P0 PASS")
    sys.stdout.flush()

    tasks = []
    # Part D groups: (d, r); cells per objective
    dgroups = sorted({(k[2], k[3]) for k in rj}, key=lambda x: (x[0], float(x[1])))
    for gi, (d, r) in enumerate(dgroups):
        for est in ("curve", "slope"):
            def arm(dif):
                if est == "curve":
                    return [rj[(dif, o, d, r)]["E"] for o in OBJS]
                return [ml.slopes_each(Jv, rj[(dif, o, d, r)]["E"]) for o in OBJS]
            iso, ani = arm("isotropic"), arm("anisotropic")
            for oi, o in enumerate(OBJS):
                tasks.append(("rmapj", gi * 10 + oi, ["D", o, d, r, "0.1"], "L-cell", est,
                              [iso[oi]], [ani[oi]], a.boot))
            for lev in ("L-pool-u", "L-pool-s"):
                tasks.append(("rmapj", gi * 10 + 9, ["D", "pooled", d, r, "0.1"], lev, est,
                              iso, ani, a.boot))
    mgroups = sorted({(k[2], k[3], k[4]) for k in rmm},
                     key=lambda x: (x[0], float(x[1]), -float(x[2])))
    for gi, (d, r, t) in enumerate(mgroups):
        iso = [rmm[("isotropic", o, d, r, t)]["slope"] for o in OBJS]
        ani = [rmm[("anisotropic", o, d, r, t)]["slope"] for o in OBJS]
        for oi, o in enumerate(OBJS):
            tasks.append(("regimemap_M", gi * 10 + oi, ["M", o, d, r, t], "L-cell", "slope",
                          [iso[oi]], [ani[oi]], a.boot))
        for lev in ("L-pool-u", "L-pool-s"):
            tasks.append(("regimemap_M", gi * 10 + 9, ["M", "pooled", d, r, t], lev, "slope",
                          iso, ani, a.boot))
    print("  groups: Part D {}, Part M {};  tasks {}".format(len(dgroups), len(mgroups), len(tasks)))
    print("  group index rule: 10 x (position in sorted group list) + objective position "
          "(ackley 0, rastrigin 1, sphere 2), or + 9 for the pooled levels")
    sys.stdout.flush()

    t0 = time.time()
    with Pool(processes=a.workers) as pool:
        res = pool.map(task, tasks, chunksize=1)
    wall = time.time() - t0

    rows = []
    for r in res:
        rows.append([r["source"], r["gidx"]] + list(r["coords"]) + [
            r["level"], r["est"], r["R"], ml.fmt(r["gap"]), ml.fmt(r["lo"]), ml.fmt(r["hi"]),
            ml.fmt(r["hw"]), r["nonfinite"], r["keys"]])
    ml.write_csv(os.path.join(outdir, "m5_gaps.csv"),
                 ["source", "group_index", "part", "objective", "d", "r", "tau", "level",
                  "estimand", "R_per_arm", "gap", "p5", "p95", "half_width",
                  "nonfinite_resamples", "seed_keys_iso_aniso"], rows)

    print("\n  {} tasks in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        len(res), wall, max(r["rss"] for r in res)))
    print("\n  90% half-width of the gap, independent arms")
    for src, part in (("rmapj", "D"), ("regimemap_M", "M")):
        for est in ("curve", "slope"):
            for lev in ("L-cell", "L-pool-u", "L-pool-s"):
                v = [r["hw"] for r in res if r["source"] == src and r["est"] == est and r["level"] == lev]
                if v:
                    print("  part {} S_{:<5} {:<9} {}".format(part, est, lev, summ(v)))
    for t in ("0.5", "0.1", "0.03", "0.01"):
        v = [r["hw"] for r in res if r["source"] == "regimemap_M" and r["level"] == "L-pool-u"
             and r["coords"][4] == t]
        print("  part M S_slope L-pool-u tau {:<5} {}".format(t, summ(v)))
    print("  non-finite resampled gaps, total: {}".format(sum(r["nonfinite"] for r in res)))
    print("\n  COVERS the probe-beta design with independent arms only; says nothing about")
    print("  calprec betas or shared seed keys.")
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
