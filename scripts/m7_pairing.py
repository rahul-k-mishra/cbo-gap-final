"""
m7_pairing.py  --  CBO-GAP measurement M7: do the archived "paired"
                   anisotropic-minus-isotropic intervals stand once the
                   pairing that never existed is removed?

WHY THIS EXISTS
---------------
Ledger N31. The isotropic and anisotropic arms of regimemap Part D never
shared seeds: realization k of one arm and realization k of the other were
independent runs (rmapj_real.csv: ackley, d = 5, r = 0.75, rep 0 has seed
20260830 isotropic and 20261910 anisotropic). The archived intervals
nevertheless difference the arms by realization index and bootstrap the
differences (reboot.py paired_gaps; regimemap.py paired_ci). N31 states, by
reasoning only, that this "does not make the intervals wrong ... only the
pairing claim". M7 tests that statement numerically on the comparison the
manuscript reports (tex 650; Table 9).

DATA (read-only; hashes checked against zenodo-v1.sha256 before use)
  regimemap_D_real.csv  Part D: 3 objectives x d {5, 10, 20, 40, 80} x r
  {0.75, 1.0, 1.25, 1.5, 2.0, 3.0} x 2 diffusions x 12 realizations,
  per-realization slopes, probe beta, tau_0 0.1. 30 (d, r) cells, each with
  36 slopes per arm.

THE CONSTRUCTIONS (per (d, r) cell; gap = mean anisotropic minus mean
isotropic slope over the 36 (objective, rep) keys; positive = anisotropic
flatter, the sign of tex 650)
  C-ARCH     the archived computation, exactly. reboot.cell and
             reboot.boot_mean are imported from the archive. As in
             paired_gaps: keys sorted, v = aniso - iso per key, B =
             reboot.B_NEW (4000) resampled means of v with seed
             reboot.SEED + 100 d + int(100 r), 5th and 95th percentiles.
             This is the construction the manuscript says it reports (tex
             309).
  C-ARCH-RM  regimemap.paired_ci, imported, on the slopes listed in
             regimemap's order (ackley, rastrigin, sphere; reps 0 to 11):
             1000 resamples, seed 7, 90%. The original Phase 11 print.
             Reported, not used in a criterion.
  C-IND      the same construction with the false within-objective
             alignment removed and everything else held fixed. Each resample
             draws 36 keys with replacement as C-ARCH does. For each drawn
             key it takes the isotropic slope of that key and the
             anisotropic slope of an INDEPENDENTLY drawn rep of the SAME
             objective. The objective structure of C-ARCH, in which both
             members of a pair share their objective, is kept. Only the rep
             alignment, which carries no shared seed, is broken. B = 4000,
             5th and 95th percentiles, repeated K times with seed keys
             [20261015, 67, 3, cell index, 1, k].
  C-PAIR-MC  C-ARCH's algorithm with fresh seeds, K repeats, keys [20261015,
             67, 3, cell index, 2, k], to measure C-ARCH's own Monte Carlo
             noise.
  C-IND-U    context only: each arm's 36 slopes resampled independently,
             ignoring objectives (key [..., 3, 0]).
  C-IND-S    context only: each arm resampled within each objective
             independently, gap = mean over objectives (key [..., 4, 0]).
  ALIGN      context only: P random within-objective permutations of the
             anisotropic rep labels (keys [..., 5, p]), each run through
             C-ARCH's algorithm with C-ARCH's own seed. This gives the spread
             of widths that the arbitrary rep alignment alone produces, and
             C-ARCH's rank in it.
  Cell index: the position of (d, r) in reboot's loop order (d outer, r
  inner, over reboot.DIMS_D and reboot.RS_D), 0 to 29.

PRE-SPECIFIED CRITERIA (fixed 2026-10-15, before first execution)
  M7-0  REPRODUCTION. The C-ARCH gaps at r = 0.75 and r = 3.0 must equal the
        values printed in tex 650 to their three printed decimals:
        |gap - printed| <= 0.0005. Printed values: r = 0.75: +0.016, +0.077,
        +0.116, +0.088, +0.161; r = 3.0: +0.148, +0.157, +0.058, -0.166,
        -0.212 (d = 5, 10, 20, 40, 80). If any fails, the script prints
        M7-0 FAIL and exits 3: it is not reading the comparison the paper
        reports.
        Worked example: a computed gap of +0.0163 against +0.016 differs by
        0.0003, which is at most 0.0005: pass.
  M7-A  WIDTH. Per cell: w_arch = p95 - p5 of C-ARCH; w_ind = the mean over
        the K repeats of the C-IND width; rho = w_arch / w_ind; sd_mc = the
        SD over k of (C-PAIR-MC width_k / C-IND width_k). The cell DIFFERS
        MATERIALLY in width iff |rho - 1| > 0.10 AND |rho - 1| > 3 sd_mc.
        The second condition stops Monte Carlo noise alone from triggering
        the first.
        Worked example (illustrative numbers): w_arch 0.090, w_ind 0.080
        gives rho 1.125. With sd_mc 0.020, 0.125 > 0.10 and 0.125 > 0.060:
        material. With sd_mc 0.050, 0.125 < 0.150: not material.
  M7-B  VERDICT. The archived rule (reboot.EQUIV, margin 0.05) applied to
        the C-ARCH interval and to the C-IND interval (endpoints averaged
        over the K repeats): EQUIV if p5 > -0.05 and p95 < +0.05; DIFF if
        p5 > +0.05 or p95 < -0.05; otherwise "incon". The cell DIFFERS
        MATERIALLY in verdict iff the two verdicts differ.
        Worked example: C-ARCH [+0.061, +0.150] is DIFF; C-IND [+0.045,
        +0.166] is incon: material.
  DECISION, printed as one line:
    "N31 STANDS" iff no cell is material under M7-A and none under M7-B.
    Otherwise "N31 MUST BE CORRECTED", listing every material cell with its
    rho, sd_mc and both verdicts. In that case the ledger sentence "the
    intervals themselves are not invalidated" is wrong for those cells and
    is corrected from this log.
  The 0.10 in M7-A is a threshold fixed by Claude for this measurement on
  2026-10-15 and confirmed by Rahul before execution. It is not a proposal
  for any rerun criterion.

WHAT THE RESULT CAN INFORM
  - Whether the archived Part D "paired" intervals and their equivalence
    verdicts (tex 650; Table 9; reboot.py) change when the false rep
    alignment is removed: that is, whether N31's "intervals stand" holds.
  - How much of an archived interval's width the arbitrary alignment
    produces (ALIGN).
WHAT IT CANNOT INFORM
  - The other index pairings N31 names: across r and d within one diffusion
    (the severity trend of tex 648, the onset intervals, b3 of tex 545, the
    rmapj trend). They use the same kind of pairing on a different statistic
    and are not tested here.
  - The 7.11 "3 of 18" result (audit.py A3), which is unpaired over four
    objectives and built from cell means, not per-realization slopes.
  - Anything under calprec v2 betas, or with shared seed keys across
    diffusions. These are probe-beta runs with independent arms.
  - Whether pairing on a SHARED seed would narrow the intervals in a rerun.
    The archive has no shared-seed pair to measure it on.

OUTPUT (new folder <outdir>/m7-<timestamp>/, every file opened "x")
  m7_cells.csv  one row per (d, r) cell: gap, every construction's p5, p95
                and width, rho, sd_mc, both verdicts, the material flags,
                the ALIGN width range and C-ARCH's rank, the within-objective
                index correlation of iso and aniso slopes, and the seed keys.

HOW TO RUN (from the repository root, venv active)
    python scripts/m7_pairing.py --workers 2
  Defaults: --repeats 20  --perms 200. Exit 0 when the decision line is
  printed (whichever way it goes), 2 on a setup error, 3 on M7-0 FAIL.

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

rb = ml.rb
rm = ml.rm

KIND = 67
FILES = ["regimemap.py", "reboot.py", "regimemap_D_real.csv"]
OBJS = ["ackley", "rastrigin", "sphere"]
WIDTH_TOL = 0.10
MC_MULT = 3.0
PRINTED = {(0.75, 5): 0.016, (0.75, 10): 0.077, (0.75, 20): 0.116, (0.75, 40): 0.088,
           (0.75, 80): 0.161, (3.0, 5): 0.148, (3.0, 10): 0.157, (3.0, 20): 0.058,
           (3.0, 40): -0.166, (3.0, 80): -0.212}
SRC = ml.SOURCE_CODE["regimemap_D"]


def verdict(lo, hi):
    if lo > -rb.EQUIV and hi < rb.EQUIV:
        return "EQUIV"
    if lo > rb.EQUIV or hi < -rb.EQUIV:
        return "DIFF"
    return "incon"


def task(a):
    ci, d, r, iso, ani, K, P = a
    keys = sorted(set(iso) & set(ani))
    n = len(keys)
    iv = np.array([iso[k] for k in keys])
    av = np.array([ani[k] for k in keys])
    v = av - iv
    gap = float(v.mean())
    B = rb.B_NEW

    # C-ARCH: reboot's own lines, with reboot's own functions and seed rule
    s = rb.SEED + d * 100 + int(r * 100)
    arch = np.percentile(rb.boot_mean(v, B, s), [5, 95])

    # C-ARCH-RM: regimemap.paired_ci on regimemap's ordering
    A = [iso[(o, k)] for o in OBJS for k in range(12)]
    Bv = [ani[(o, k)] for o in OBJS for k in range(12)]
    _g_rm, lo_rm, hi_rm = rm.paired_ci(A, Bv)

    obj_of = np.array([OBJS.index(k[0]) for k in keys])
    ani_mat = np.array([[ani[(o, k)] for k in range(12)] for o in OBJS])
    iso_mat = np.array([[iso[(o, k)] for k in range(12)] for o in OBJS])

    w_ind, w_pair, lo_ind, hi_ind = [], [], [], []
    for k in range(K):
        rng = ml.rng_for(KIND, [SRC, ci, 1, k])
        J = rng.integers(0, n, size=(B, n))
        U = rng.integers(0, 12, size=(B, n))
        g = ani_mat[obj_of[J], U].mean(axis=1) - iv[J].mean(axis=1)
        p5, p95 = np.percentile(g, [5, 95])
        lo_ind.append(p5)
        hi_ind.append(p95)
        w_ind.append(p95 - p5)
        rng2 = ml.rng_for(KIND, [SRC, ci, 2, k])
        J2 = rng2.integers(0, n, size=(B, n))
        q5, q95 = np.percentile(v[J2].mean(axis=1), [5, 95])
        w_pair.append(q95 - q5)
    w_ind = np.array(w_ind)
    w_pair = np.array(w_pair)
    w_arch = float(arch[1] - arch[0])
    rho = w_arch / float(w_ind.mean())
    sd_mc = float(np.std(w_pair / w_ind, ddof=1))
    lo_i, hi_i = float(np.mean(lo_ind)), float(np.mean(hi_ind))
    va, vi = verdict(arch[0], arch[1]), verdict(lo_i, hi_i)
    mat_a = abs(rho - 1.0) > WIDTH_TOL and abs(rho - 1.0) > MC_MULT * sd_mc
    mat_b = va != vi

    rng3 = ml.rng_for(KIND, [SRC, ci, 3, 0])
    gu = (av[rng3.integers(0, n, size=(B, n))].mean(axis=1)
          - iv[rng3.integers(0, n, size=(B, n))].mean(axis=1))
    u5, u95 = np.percentile(gu, [5, 95])
    rng4 = ml.rng_for(KIND, [SRC, ci, 4, 0])
    gs = np.zeros(B)
    for oi in range(len(OBJS)):
        gs += (ani_mat[oi][rng4.integers(0, 12, size=(B, 12))].mean(axis=1)
               - iso_mat[oi][rng4.integers(0, 12, size=(B, 12))].mean(axis=1))
    gs /= len(OBJS)
    s5, s95 = np.percentile(gs, [5, 95])

    widths = []
    for p in range(P):
        rng5 = ml.rng_for(KIND, [SRC, ci, 5, p])
        perm = np.vstack([rng5.permutation(12) for _ in OBJS])
        ap = np.array([ani_mat[OBJS.index(k[0]), perm[OBJS.index(k[0]), k[1]]] for k in keys])
        q = np.percentile(rb.boot_mean(ap - iv, B, s), [5, 95])
        widths.append(q[1] - q[0])
    widths = np.array(widths)
    rank = float(np.mean(widths <= w_arch))

    ic = iso_mat - iso_mat.mean(axis=1, keepdims=True)
    ac = ani_mat - ani_mat.mean(axis=1, keepdims=True)
    corr = float((ic * ac).sum() / np.sqrt((ic * ic).sum() * (ac * ac).sum()))

    return {"ci": ci, "d": d, "r": r, "n": n, "gap": gap, "arch": (float(arch[0]), float(arch[1])),
            "rm": (float(lo_rm), float(hi_rm)), "ind": (lo_i, hi_i), "w_ind": float(w_ind.mean()),
            "w_arch": w_arch, "rho": rho, "sd_mc": sd_mc, "va": va, "vi": vi,
            "mat_a": mat_a, "mat_b": mat_b, "u": (float(u5), float(u95)), "s": (float(s5), float(s95)),
            "align_lo": float(np.percentile(widths, 2.5)), "align_hi": float(np.percentile(widths, 97.5)),
            "rank": rank, "corr": corr, "seed_arch": s, "rss": ml.rss_mb()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--repeats", type=int, default=20)
    p.add_argument("--perms", type=int, default=200)
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    a = p.parse_args()
    if a.workers < 1 or a.repeats < 5 or a.perms < 20:
        sys.stderr.write("setup error: --workers >= 1, --repeats >= 5, --perms >= 20 required\n")
        return 2

    outdir = ml.new_outdir("m7")
    ok = ml.print_header(
        "CBO-GAP M7 -- archived 'paired' iso/aniso intervals against independent-arm intervals (N31)",
        KIND, a.workers,
        {"comparison": "regimemap Part D, 30 (d, r) cells, 36 keys per arm, tau_0 0.1",
         "C-ARCH": "reboot.cell + reboot.boot_mean, B {}, seed {} + 100 d + int(100 r), 5/95".format(
             rb.B_NEW, rb.SEED),
         "C-ARCH-RM": "regimemap.paired_ci (1000, seed 7, 90%), reported only",
         "C-IND": "keys drawn as C-ARCH, aniso rep drawn independently within objective; "
                  "B {}, K {} repeats".format(rb.B_NEW, a.repeats),
         "context": "C-IND-U, C-IND-S, ALIGN with {} permutations".format(a.perms),
         "M7-0": "C-ARCH gaps vs tex 650 printed values, |diff| <= 0.0005; exit 3 on fail",
         "M7-A": "material iff |rho - 1| > {} and > {} x sd_mc".format(WIDTH_TOL, MC_MULT),
         "M7-B": "material iff equivalence verdicts (margin {}) differ".format(rb.EQUIV),
         "decision": "N31 STANDS iff no cell material under M7-A or M7-B",
         "covers": "probe-beta Part D diffusion gaps ONLY; not the r/d pairings, "
                   "not calprec betas, not shared seed keys"},
        FILES, outdir)
    if not ok:
        print("SETUP ERROR: archive hash mismatch; nothing measured")
        return 2

    D = rb.load(os.path.join(ml.ARCH, "regimemap_D_real.csv"))
    tasks, ci = [], 0
    for d in rb.DIMS_D:
        for r in rb.RS_D:
            iso = rb.cell(D, "isotropic", d, r)
            ani = rb.cell(D, "anisotropic", d, r)
            tasks.append((ci, d, r, iso, ani, a.repeats, a.perms))
            ci += 1
    t0 = time.time()
    with Pool(processes=a.workers) as pool:
        res = pool.map(task, tasks, chunksize=1)
    wall = time.time() - t0
    res.sort(key=lambda x: x["ci"])

    print("\n  M7-0 reproduction of tex 650")
    bad0 = 0
    for x in res:
        ref = PRINTED.get((x["r"], x["d"]))
        if ref is None:
            continue
        okc = abs(x["gap"] - ref) <= 0.0005
        bad0 += 0 if okc else 1
        print("    d {:<3} r {:<5} gap {:+.4f}  printed {:+.3f}  {}".format(
            x["d"], x["r"], x["gap"], ref, "ok" if okc else "FAIL"))
    if bad0:
        print("  M7-0 FAIL: {} of 10 printed gaps not reproduced; nothing judged".format(bad0))
        return 3
    print("  M7-0 PASS")

    rows = []
    for x in res:
        rows.append([x["ci"], x["d"], x["r"], x["n"], ml.fmt(x["gap"]),
                     ml.fmt(x["arch"][0]), ml.fmt(x["arch"][1]), ml.fmt(x["w_arch"]),
                     ml.fmt(x["rm"][0]), ml.fmt(x["rm"][1]),
                     ml.fmt(x["ind"][0]), ml.fmt(x["ind"][1]), ml.fmt(x["w_ind"]),
                     ml.fmt(x["rho"]), ml.fmt(x["sd_mc"]), x["va"], x["vi"],
                     "yes" if x["mat_a"] else "no", "yes" if x["mat_b"] else "no",
                     ml.fmt(x["u"][0]), ml.fmt(x["u"][1]), ml.fmt(x["s"][0]), ml.fmt(x["s"][1]),
                     ml.fmt(x["align_lo"]), ml.fmt(x["align_hi"]), ml.fmt(x["rank"]),
                     ml.fmt(x["corr"]), x["seed_arch"],
                     "20261015-67-{}-{}-<construction>-<repeat>".format(SRC, x["ci"])])
    ml.write_csv(os.path.join(outdir, "m7_cells.csv"),
                 ["cell_index", "d", "r", "keys", "gap", "arch_p5", "arch_p95", "arch_width",
                  "rm_p5", "rm_p95", "ind_p5", "ind_p95", "ind_width_mean", "rho", "sd_mc",
                  "verdict_arch", "verdict_ind", "material_width", "material_verdict",
                  "indU_p5", "indU_p95", "indS_p5", "indS_p95", "align_width_p2_5",
                  "align_width_p97_5", "arch_width_rank_in_align", "index_corr_within_obj",
                  "reboot_seed", "seed_key_rule"], rows)

    print("\n  {} cells in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        len(res), wall, max(x["rss"] for x in res)))
    print("\n  {:<3} {:<5} {:>8} {:>19} {:>19} {:>19} {:>7} {:>6} {:>6} {:>6} {:>4} {:>4} {:>6}".format(
        "d", "r", "gap", "C-ARCH 90%", "C-IND 90%", "C-ARCH-RM 90%", "rho", "sd_mc",
        "V-arch", "V-ind", "A", "B", "corr"))
    for x in res:
        print("  {:<3} {:<5} {:>+8.4f} [{:+.4f},{:+.4f}] [{:+.4f},{:+.4f}] [{:+.4f},{:+.4f}] "
              "{:>7.3f} {:>6.3f} {:>6} {:>6} {:>4} {:>4} {:>+6.2f}".format(
                  x["d"], x["r"], x["gap"], x["arch"][0], x["arch"][1], x["ind"][0], x["ind"][1],
                  x["rm"][0], x["rm"][1], x["rho"], x["sd_mc"], x["va"], x["vi"],
                  "MAT" if x["mat_a"] else "-", "MAT" if x["mat_b"] else "-", x["corr"]))
    print("\n  context: ALIGN width range and C-ARCH rank; C-IND-U and C-IND-S intervals")
    for x in res:
        print("  d {:<3} r {:<5} ALIGN [{:.4f},{:.4f}] arch {:.4f} rank {:.2f}   "
              "U [{:+.4f},{:+.4f}]   S [{:+.4f},{:+.4f}]".format(
                  x["d"], x["r"], x["align_lo"], x["align_hi"], x["w_arch"], x["rank"],
                  x["u"][0], x["u"][1], x["s"][0], x["s"][1]))

    ma = [x for x in res if x["mat_a"]]
    mb = [x for x in res if x["mat_b"]]
    print("\n  M7-A cells material in width:   {} of {}".format(len(ma), len(res)))
    print("  M7-B cells material in verdict: {} of {}".format(len(mb), len(res)))
    rhos = np.array([x["rho"] for x in res])
    print("  rho over cells: min {:.3f}  median {:.3f}  max {:.3f}".format(
        rhos.min(), np.median(rhos), rhos.max()))
    if not ma and not mb:
        print("\n  DECISION: N31 STANDS -- removing the false rep alignment changes no width")
        print("  materially and no equivalence verdict.")
    else:
        print("\n  DECISION: N31 MUST BE CORRECTED -- material cells:")
        for x in sorted(set([y["ci"] for y in ma + mb])):
            y = res[x]
            print("    d {:<3} r {:<5} rho {:.3f}  sd_mc {:.3f}  verdict {} -> {}".format(
                y["d"], y["r"], y["rho"], y["sd_mc"], y["va"], y["vi"]))
    print("\n  COVERS the probe-beta Part D diffusion gaps only.")
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
