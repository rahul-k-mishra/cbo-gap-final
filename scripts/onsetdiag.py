"""onsetdiag.py -- why three per-objective onsets of 2.00 pool to 1.00
(ledger N42, observation of 2026-10-28). Read-only diagnostic.

WRITES NOTHING. It reads two committed analysis folders, verifies their
sha256.txt manifests, and prints to the console. No file is opened for
writing, no run folder is created, nothing is random (no seed), and no
trajectory is evolved. Rerunning it prints the same numbers.

WHAT IT READS
  --n39     runs/rerun-analysis-20261025-051314 (N39): analysis_cells.csv
            and analysis_onsets.csv, for ONSET (probe beta).
  --twenty  runs/rerun-analysis-20261027-185918 (N42): analysis_cells.csv
            and analysis_onsets_calibrated.csv, for ONSET-CAL (fixed beta).
  From each analysis_cells.csv it takes the W-full point S-slope of every
  ONSET or ONSET-CAL cell: per diffusion (isotropic, anisotropic), per
  objective (ackley, rastrigin, sphere), per d (5, 10, 20, 40, 80), per r
  (0.75, 1.0, 1.25, 1.5, 2.0, 3.0), tau0 0.1. These are the point values
  H3 fed to the onset estimator in rerun_analysis.py (onset_block). The
  bootstrap intervals are not recomputed; that needs the realizations.

THE ESTIMATOR (H3, rerunlib.onset_bp, imported, not retyped)
  x = log r over the six r values; y = the six S-slopes. For each
  candidate c in x without its last value (r = 0.75, 1.0, 1.25, 1.5, 2.0),
  least squares y = a + b1 x + b2 max(x - c, 0); the onset is exp(c) for
  the c with the smallest residual sum of squares (RSS); ties go to the
  smaller c.
  - Per objective: y is that objective's curve.
  - Pooled: y is the mean over the three objectives at each r (the mean
    curve), computed exactly as onset_block does:
    np.mean(np.array([ackley, rastrigin, sphere]), axis=0). The pooled
    onset is the onset of the mean curve, not the mean of the onsets.

  Two facts about the candidate set that follow from the algebra, stated
  here so the printed RSS profiles can be read against them:
  F1. c at r = 0.75 (the first x): max(x - c, 0) = x - c at every point,
      which is a combination of x and 1. The design has rank 2 and the fit
      is one straight line in log r through all six points.
      Example: y = (-1.0, -0.9, -0.8, -0.7, -0.6, -0.5) against x is not
      exactly linear (the r spacing is not even in log r), so the RSS at
      c = log 0.75 is the RSS of a straight-line fit, nothing more.
  F2. c at r = 2.0 (the last candidate): max(x - c, 0) is zero at every
      point except r = 3.0. That column fits the r = 3.0 point exactly,
      so the RSS at c = log 2.0 is the RSS of a straight line through the
      first five points alone, whatever y(3.0) is.
      Example: y = (-1, -1, -1, -1, -1, -0.4). At c = log 2.0 the line
      through the first five is flat at -1 and the hinge column takes
      y(3.0): RSS 0, so the onset is 2.0. A curve that rises steadily from
      r = 1 to r = 2 and then stops rising also has its first five points
      close to a line, and can land at 2.0 for that reason.

WHAT IT PRINTS, IN ORDER
  V1  Both manifests verify (every file listed in sha256.txt hashes as
      listed). Failure: exit 2, nothing else printed.
  V2  Each of the 180 (diffusion, objective, d, r) cells of each row is
      present exactly once in W-full. Failure: exit 2.
  V3  The ONSET W-full S-slopes in the two folders are equal as strings
      (CAL4 already showed it; checked again because the two folders are
      read here). Failure: exit 2.
  R1  Recomputation of every recorded onset. For each row, diffusion and
      d, the three per-objective onsets and the pooled onset are
      recomputed from the S-slopes above with rerunlib.onset_bp and
      compared with the onset column of analysis_onsets.csv (ONSET) or
      analysis_onsets_calibrated.csv (ONSET-CAL). Criterion: equal as
      floats (the onset is a grid value; no tolerance). Printed: "R1
      ONSET 40 of 40 equal" and every mismatch with both values.
      Example: ONSET isotropic d 80 pooled is recorded as 1.0; if the
      recomputation gives 1.0 that onset is "equal".
  D   An independent check of onset_bp's choice: the RSS at each
      candidate is recomputed as |y - A pinv(A) y|^2 (projection, not
      lstsq), and its first minimum is compared with onset_bp's onset.
      Criterion: the same r. Printed "D 40 of 40 agree" per row, and each
      disagreement with the RSS gap between the two candidates.
      Example: RSS profile (0.010, 0.004, 0.006, 0.008, 0.004): the first
      minimum is the second candidate, r = 1.0; onset_bp must also return
      1.0 (ties go to the smaller c).
  DETAIL, isotropic d = 80, ONSET and ONSET-CAL: for each of the three
      objectives and the mean curve:
      - the six S-slopes;
      - the RSS at each of the five candidates, with the fitted a, b1, b2
        and the design's rank, the chosen candidate marked "<- onset";
      - at the chosen candidate, the fitted value and residual at each r;
      - the steps y(r_k+1) - y(r_k) between neighbouring r (rise per
        step), a description of the curve's shape, not a test.
      Then:
      - the mean of the three per-objective fitted curves, each at its own
        onset, and its RSS against the mean curve;
      - the mean curve's RSS at each per-objective onset beside its RSS at
        its own onset;
      - a text plot of the four curves against r (A ackley, R rastrigin,
        S sphere, M mean).
  SCOPE, every (row, diffusion, d): the three per-objective onsets, the
      pooled onset, whether the pooled onset equals any per-objective
      onset ("pooled among objectives: yes/no"), and for each curve
      whether its onset is the last candidate, 2.0 (the F2 case). A
      count, per row, of the (diffusion, d) whose pooled onset equals none
      of the three per-objective onsets. A description; no verdict is
      attached to any count.

EXIT CODES
  0  V1 to V3 passed, R1 all equal, D all agree.
  2  setup: a manifest fails, a cell is missing or duplicated, an onset
     file has an unexpected row, or V3 differs.
  3  everything printed, but R1 found a recorded onset that the recorded
     S-slopes do not reproduce, or D found onset_bp's choice differs from
     the independent RSS route. Either is a finding about the committed
     onsets (N39's or N42's), not about this script's inputs.

HOW TO RUN (laptop, the CAL4 environment)
  python scripts/onsetdiag.py --n39 runs/rerun-analysis-20261025-051314 \
      --twenty runs/rerun-analysis-20261027-185918 --workers 2

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import hashlib                                                  # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rerunlib as rl                                           # noqa: E402

ROWS = [("ONSET", "n39", "analysis_onsets.csv"),
        ("ONSET-CAL", "twenty", "analysis_onsets_calibrated.csv")]
DETAIL = ("isotropic", 80)
LETTER = {"ackley": "A", "rastrigin": "R", "sphere": "S", "mean": "M"}
PLOT_W = 61


def say(s=""):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()


def hdr(s):
    say("")
    say("-" * 100)
    say(s)
    say("-" * 100)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def fail(msg):
    say("SETUP FAILED: " + msg)
    sys.exit(2)


def read_slopes(path, row, g):
    """{(diffusion, objective, d, r): S_slope string} for W-full cells of row."""
    out = {}
    with open(path, newline="") as fh:
        for rec in csv.DictReader(fh):
            if rec["row"] != row or rec["window"] != "W-full":
                continue
            parts = rec["cell"].split("|")
            key = (rec["diffusion"], parts[2], int(parts[3][1:]), float(parts[6][2:]))
            if key in out:
                fail("{} {}: cell {} appears twice in W-full".format(path, row, key))
            out[key] = rec["S_slope"]
    want = [(df, o, d, r) for df in g["diffs"] for o in g["objs"] for d in g["dims"] for r in g["rs"]]
    miss = [k for k in want if k not in out]
    wset = set(want)
    extra = [k for k in out if k not in wset]
    if miss or extra:
        fail("{} {}: {} cells missing, {} unexpected (first missing {})".format(
            path, row, len(miss), len(extra), miss[:1]))
    return out, len(want)


def read_onsets(path, g):
    """{(diffusion, objective, d): onset float}, heterogeneity rows skipped."""
    out = {}
    with open(path, newline="") as fh:
        for rec in csv.DictReader(fh):
            if rec["objective"].startswith("heterogeneity"):
                continue
            key = (rec["diffusion"], rec["objective"], int(rec["d"]))
            if key in out:
                fail("{}: {} appears twice".format(path, key))
            out[key] = float(rec["onset"])
    want = [(df, o, d) for df in g["diffs"] for o in list(g["objs"]) + ["pooled"] for d in g["dims"]]
    if sorted(out) != sorted(want):
        fail("{}: expected {} onset rows, found {}".format(path, len(want), len(out)))
    return out


def profile(rs, y):
    """Per candidate c: (r, rank, a, b1, b2, rss_lstsq, rss_pinv, fitted)."""
    x = np.log(np.array(rs, dtype=float))
    yy = np.asarray(y, dtype=float)
    res = []
    for k in range(len(x) - 1):
        c = x[k]
        z = np.maximum(x - c, 0.0)
        A = np.vstack([x, z, np.ones(len(x))]).T
        sol, _, rank, _ = np.linalg.lstsq(A, yy, rcond=None)
        fit = A @ sol
        rss_l = float(((yy - fit) ** 2).sum())
        proj = A @ (np.linalg.pinv(A) @ yy)
        rss_p = float(((yy - proj) ** 2).sum())
        res.append({"r": rs[k], "rank": int(rank), "b1": float(sol[0]), "b2": float(sol[1]),
                    "a": float(sol[2]), "rss": rss_l, "rss_pinv": rss_p, "fit": [float(v) for v in fit]})
    return res


def unit(args):
    """One (row, diffusion, d): every curve, its onset, its profile."""
    row, df, d, rs, objs, curves = args
    out = {"row": row, "diffusion": df, "d": d, "curves": {}}
    pts = []
    for o in objs:
        y = curves[o]
        pts.append(y)
        out["curves"][o] = {"y": y, "onset": float(rl.onset_bp(rs, y)), "profile": profile(rs, y)}
    mp = list(np.mean(np.array(pts), axis=0))
    out["curves"]["pooled"] = {"y": [float(v) for v in mp], "onset": float(rl.onset_bp(rs, mp)),
                               "profile": profile(rs, mp)}
    return out


def at_onset(cv):
    """Index of the candidate the onset came from (onset_bp returns exp(log r),
    so the match is to the nearest grid value, not by float equality)."""
    return min(range(len(cv["profile"])), key=lambda i: abs(cv["profile"][i]["r"] - cv["onset"]))


def first_min(vals):
    best = 0
    for i, v in enumerate(vals):
        if v < vals[best]:
            best = i
    return best


def fmt(v):
    return "{:+.4f}".format(v)


def text_plot(rs, curves):
    allv = [v for y in curves.values() for v in y]
    lo, hi = min(allv), max(allv)
    span = hi - lo if hi > lo else 1.0
    say("  text plot: S-slope from {:+.3f} (left) to {:+.3f} (right); one line per r".format(lo, hi))
    for i, r in enumerate(rs):
        line = [" "] * PLOT_W
        for name, y in curves.items():
            pos = int(round((y[i] - lo) / span * (PLOT_W - 1)))
            ch = LETTER[name]
            line[pos] = ch if line[pos] == " " else "*"
        say("  r={:<5} |{}|".format(r, "".join(line)))
    say("  (A ackley, R rastrigin, S sphere, M mean curve; * two or more letters in one column)")


def detail(rs, objs, u):
    say("")
    say("  {}  {} d={}".format(u["row"], u["diffusion"], u["d"]))
    names = list(objs) + ["pooled"]
    for o in names:
        cv = u["curves"][o]
        lab = "mean curve (pooled)" if o == "pooled" else o
        say("")
        say("    {}: S-slope at r = {}".format(lab, ", ".join(str(r) for r in rs)))
        say("      y      " + "  ".join(fmt(v) for v in cv["y"]))
        say("      steps  " + "  ".join(fmt(cv["y"][k + 1] - cv["y"][k]) for k in range(len(rs) - 1))
            + "   (y at the next r minus y at this r)")
        say("      candidate   rank    a         b1        b2        RSS")
        for p in cv["profile"]:
            mark = "  <- onset" if p is cv["profile"][at_onset(cv)] else ""
            say("      c at r={:<5} {}     {}   {}   {}   {:.6e}{}".format(
                p["r"], p["rank"], fmt(p["a"]), fmt(p["b1"]), fmt(p["b2"]), p["rss"], mark))
        ch = cv["profile"][at_onset(cv)]
        say("      at the onset {:.2f}: fitted  ".format(cv["onset"]) + "  ".join(fmt(v) for v in ch["fit"]))
        say("                       residual "
            + "  ".join(fmt(a - b) for a, b in zip(cv["y"], ch["fit"])))
    pm = u["curves"]["pooled"]
    fits = []
    for o in objs:
        cv = u["curves"][o]
        fits.append(cv["profile"][at_onset(cv)]["fit"])
    mfit = list(np.mean(np.array(fits), axis=0))
    say("")
    say("    mean of the three per-objective fitted curves (each at its own onset):")
    say("      " + "  ".join(fmt(v) for v in mfit))
    say("      its RSS against the mean curve {:.6e}".format(
        float(sum((a - b) ** 2 for a, b in zip(pm["y"], mfit)))))
    say("    mean curve's RSS at each per-objective onset, against its own onset {:.2f}:".format(pm["onset"]))
    own = pm["profile"][at_onset(pm)]["rss"]
    for o in objs:
        r_o = u["curves"][o]["onset"]
        rss_o = pm["profile"][at_onset(u["curves"][o])]["rss"]
        say("      {:<10} onset {:.2f}  mean-curve RSS there {:.6e}   at {:.2f} {:.6e}".format(
            o, r_o, rss_o, pm["onset"], own))
    say("")
    pc = dict((o, u["curves"][o]["y"]) for o in objs)
    pc["mean"] = pm["y"]
    text_plot(rs, pc)


def main():
    ap = argparse.ArgumentParser(description="ONSET onset diagnostic (N42), read-only")
    ap.add_argument("--n39", required=True)
    ap.add_argument("--twenty", required=True)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    folders = {"n39": a.n39, "twenty": a.twenty}

    say("=" * 100)
    say("CBO-GAP onsetdiag -- why three per-objective onsets of 2.00 pool to 1.00 (N42), read-only")
    say("=" * 100)
    say("  onsetdiag sha256 {}".format(sha(os.path.abspath(__file__))))
    say("  rerunlib sha256  {}".format(sha(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                        "rerunlib.py"))))
    say("  python {}   numpy {}   platform {}   workers {}".format(
        platform.python_version(), np.__version__, platform.platform(), a.workers))
    say("  --n39 {}   --twenty {}".format(a.n39, a.twenty))
    say("  writes nothing; no seed (nothing random); point S-slopes only, no bootstrap")
    say("")
    say("  What this prints, in plain words. The onset of a curve is where a single bend (a")
    say("  hinge) fits the S-slope-against-log-r curve best, chosen among r = 0.75, 1.0, 1.25,")
    say("  1.5 and 2.0. The pooled onset is the bend of the AVERAGE curve over the three")
    say("  objectives, not the average of their bends. For isotropic d = 80 the script prints")
    say("  each curve, how badly a bend at each candidate fits it (RSS: smaller fits better),")
    say("  where the best bend lands, and a text plot, for ONSET (probe beta) and ONSET-CAL")
    say("  (fixed beta). Two facts about the candidates: a bend at 0.75 is just a straight")
    say("  line; a bend at 2.0 has only r = 3.0 to its right, so it always fits r = 3.0")
    say("  exactly and is judged on the first five points alone. R1 checks that the committed")
    say("  onsets follow from the committed slopes; D checks onset_bp's choice by a second")
    say("  route; SCOPE lists every dimension so the d = 80 case can be compared with the rest.")

    hdr("V1  manifests")
    for k in ("n39", "twenty"):
        rels = rl.verify_folder(folders[k])
        say("  {} verified ({} files)".format(folders[k], len(rels)))

    g = rl.GRID["ONSET"]
    rs, objs = list(g["rs"]), list(g["objs"])
    if rl.GRID["ONSET-CAL"]["rs"] != g["rs"] or list(rl.GRID["ONSET-CAL"]["objs"]) != objs:
        fail("ONSET-CAL grid differs from ONSET's")

    hdr("V2  cells (W-full point S-slopes)")
    slopes, rec = {}, {}
    for row, fk, onf in ROWS:
        p = os.path.join(folders[fk], "analysis_cells.csv")
        slopes[row], n = read_slopes(p, row, g)
        say("  {:<9} {}  sha256 {}  {} cells, each once".format(row, p, sha(p), n))
        q = os.path.join(folders[fk], onf)
        rec[row] = read_onsets(q, g)
        say("  {:<9} {}  sha256 {}  {} onsets".format(row, q, sha(q), len(rec[row])))

    hdr("V3  ONSET slopes equal in both folders")
    p2 = os.path.join(a.twenty, "analysis_cells.csv")
    other, _ = read_slopes(p2, "ONSET", g)
    diff = [k for k in slopes["ONSET"] if slopes["ONSET"][k] != other[k]]
    if diff:
        fail("ONSET slopes differ between folders at {} cells, first {}".format(len(diff), diff[0]))
    say("  ONSET: {} cells equal as strings in {} and {}".format(len(other), a.n39, a.twenty))

    jobs = []
    for row, _, _ in ROWS:
        for df in g["diffs"]:
            for d in g["dims"]:
                curves = dict((o, [float(slopes[row][(df, o, d, r)]) for r in rs]) for o in objs)
                jobs.append((row, df, d, rs, objs, curves))
    pool = multiprocessing.Pool(a.workers)
    units = pool.map(unit, jobs)
    pool.close()
    pool.join()

    bad = 0
    hdr("R1  every recorded onset recomputed from the recorded slopes")
    for row, _, onf in ROWS:
        n_eq, n_all = 0, 0
        for u in [x for x in units if x["row"] == row]:
            for o in objs + ["pooled"]:
                got = u["curves"][o]["onset"]
                want = rec[row][(u["diffusion"], o, u["d"])]
                n_all += 1
                if got == want:
                    n_eq += 1
                else:
                    bad += 1
                    say("  MISMATCH {} {} d={} {}: recomputed {} recorded {}".format(
                        row, u["diffusion"], u["d"], o, got, want))
        say("  R1 {:<9} {} of {} equal ({})".format(row, n_eq, n_all, onf))

    hdr("D  onset_bp's choice against an independent RSS route (pinv projection)")
    for row, _, _ in ROWS:
        n_ag, n_all = 0, 0
        for u in [x for x in units if x["row"] == row]:
            for o in objs + ["pooled"]:
                cv = u["curves"][o]
                rp = [p["rss_pinv"] for p in cv["profile"]]
                k = first_min(rp)
                n_all += 1
                j = at_onset(cv)
                if k == j:
                    n_ag += 1
                else:
                    bad += 1
                    say("  DISAGREE {} {} d={} {}: onset_bp {:.2f} (RSS {:.6e}), pinv route {} (RSS {:.6e})".format(
                        row, u["diffusion"], u["d"], o, cv["onset"], rp[j], cv["profile"][k]["r"], rp[k]))
        say("  D {:<9} {} of {} agree".format(row, n_ag, n_all))

    hdr("DETAIL  isotropic d = 80: the curves, the hinge fits, where each onset lands")
    for row, _, _ in ROWS:
        u = [x for x in units if x["row"] == row and x["diffusion"] == DETAIL[0] and x["d"] == DETAIL[1]][0]
        detail(rs, objs, u)

    hdr("SCOPE  every (row, diffusion, d): per-objective onsets, pooled onset")
    say("  'last' marks an onset at 2.0, the candidate with only r = 3.0 to its right (F2)")
    for row, _, _ in ROWS:
        n_none = 0
        n_u = 0
        for u in sorted([x for x in units if x["row"] == row], key=lambda z: (z["diffusion"], z["d"])):
            per = [u["curves"][o]["onset"] for o in objs]
            pooled = u["curves"]["pooled"]["onset"]
            among = pooled in per
            n_u += 1
            n_none += 0 if among else 1
            say("  {:<9} {:<11} d={:<3} {}   pooled {:.2f}{}  pooled among objectives: {}".format(
                row, u["diffusion"], u["d"],
                "  ".join("{} {:.2f}{}".format(o[:4], v, " last" if abs(v - 2.0) < 1e-9 else "     ")
                          for o, v in zip(objs, per)),
                pooled, " last" if abs(pooled - 2.0) < 1e-9 else "     ", "yes" if among else "no"))
        say("  {}: pooled onset equal to none of the three per-objective onsets in {} of {}".format(
            row, n_none, n_u))

    hdr("SUMMARY")
    say("  peak RSS (main process) {:.1f} MB".format(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0))
    if bad:
        say("  R1 or D FOUND {} discrepancies (exit 3); see the lines above".format(bad))
        sys.exit(3)
    say("  R1 all equal, D all agree; nothing written")


if __name__ == "__main__":
    main()
