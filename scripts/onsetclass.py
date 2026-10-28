"""onsetclass.py -- what kind of bend each H3 onset is: the start of a rise,
its end, a steepening of a rise already under way, or no rise (ledger N43).
Read-only diagnostic.

WRITES NOTHING. It reads committed files, verifies their manifests, and
prints to the console. No file is opened for writing, no run folder is
created, nothing is random (no seed), and no trajectory is evolved.

WHAT IT READS
  --n39     runs/rerun-analysis-20261025-051314 (N39): analysis_cells.csv,
            analysis_onsets.csv, analysis_margin.csv. ONSET, probe beta.
  --twenty  runs/rerun-analysis-20261027-185918 (N42): analysis_cells.csv,
            analysis_onsets_calibrated.csv. ONSET-CAL, fixed beta.
  The archive (rerunlib.ARCH, zenodo-v1): regimemap_D_real.csv and
            sn-article.tex, each checked against zenodo-v1.sha256. Round 1.
  The readers are onsetdiag.py's (read_slopes, read_onsets), imported,
  so the file checks of the onsetdiag run that exited 0 apply unchanged.

THE CURVES AND THEIR ONSETS
  For each row (ONSET, ONSET-CAL), diffusion (isotropic, anisotropic), d
  (5, 10, 20, 40, 80): the W-full point S-slope y at r = 0.75, 1.0, 1.25,
  1.5, 2.0, 3.0 for each objective (ackley, rastrigin, sphere), and the
  mean curve over the three, computed as onset_block does
  (np.mean(np.array([ackley, rastrigin, sphere]), axis=0)). That is 30
  per-objective curves and 10 mean curves per row, 80 in all. The onset of
  each is rerunlib.onset_bp of the curve (H3). It is recomputed and must
  equal the committed onset (onsetdiag R1 already showed 80 of 80).
  Round 1: rerunlib.onset_control, imported (the O1 positive control). It
  builds the ten mean curves of the submitted tab:onset from
  regimemap_D_real.csv (part D: mean over rep of the archived slope per
  diffusion, objective, d, r; then the mean over the three objectives) and
  their onsets, and checks the ten against the table. It must pass.

  Sign convention. The S-slope is near -1 when the J^-1 rate is seen and
  moves toward 0 as it degrades. A RISE is an increase of y (toward 0).

THE CLASSIFICATION RULE (post hoc)
  Fixed by Claude on 2026-10-28 (ledger N43) AFTER the curves of the 25
  onsets at 2.00 had been seen, together with the isotropic d 80 mean
  curves (onsetdiag DETAIL) and the round-1 table's ten mean curves. The
  extension to bends below 2.0 (below) was written on 2026-10-28 before
  this script computed any of the other 55. The log prints this.
  For an onset at grid point c (c one of 0.75, 1.0, 1.25, 1.5, 2.0):
    before = y(c) - y(0.75)     the net rise from the first r up to the bend
    after  = y(3.0) - y(c)      the net rise from the bend to the last r
  against m, the 5b margin, read from N39's analysis_margin.csv (value
  "m", 0.07811313532738592), as the size of a change worth naming. m was
  fixed for slope differences between arms; using it here is a borrowed
  scale, not a criterion it was set for.
    start      after > m and before <= m   (flat, then a rise from the bend)
    end        before > m and after <= m   (a rise up to the bend, then none)
    continues  before > m and after > m    (rising on both sides: the bend
                                            is a change of steepness)
    no rise    before <= m and after <= m
    line       c = 0.75: a bend at the first point is a straight line in
               log r (onsetdiag F1), so there is no bend to classify;
               before is 0 by construction. Printed with "after".
  Worked examples (illustrative numbers):
    y = (-1.00, -0.98, -0.85, -0.70, -0.55, -0.56), onset 2.0: before
        +0.45 > m, after -0.01 <= m: end.
    y = (-1.0, -1.0, -1.0, -1.0, -1.0, -0.4), onset 2.0: before 0.00, after
        +0.60: start.
    y = (-1.0, -0.9, -0.8, -0.8, -0.8, -0.6), onset 1.25: before +0.20,
        after +0.20: continues.
    y = (-1.00, -1.01, -0.99, -1.02, -1.00, -0.98), onset 1.0: before
        -0.01, after +0.03: no rise.
  The rule uses net changes on point values: no interval, and a curve
  that rises and falls inside an interval can net to small values. It
  describes; it is not a test and gives no verdict.

NEAR THE THRESHOLD
  For each onset: dist = the smaller of |before - m| and |after - m|.
  A call can change if m moves by dist or more, and cannot change if m
  moves by less. Printed per onset, then counts with dist <= 0.005, 0.01,
  0.02 and 0.05 (fixed here, descriptive), then the ten smallest.
  Example: before +0.076, after +0.117: dist = min(0.0021, 0.0389) =
  0.0021; counted in every band.

WHAT IT PRINTS, IN ORDER
  V1  the two manifests; the two archive files against zenodo-v1.sha256.
  V2  cells and onset files through onsetdiag's readers (kinds 40/10/6).
  V3  ONSET slopes equal as strings in both folders.
  M   m as read.
  O1  round 1's control: ten onsets equal to tab:onset.
  R   recomputed onsets equal to the committed ones (80 of 80 expected).
  TABLE  one line per onset (80 rows, then 10 round-1): row, diffusion,
      d, objective or pooled, onset, its committed 95% interval, before,
      after, dist, class, and the curve. Round 1's lines give the
      tab:onset line number and the table's printed per-r means beside the
      recomputed ones; its interval is not parsed or shown.
  COUNTS  class by row and by level (objective, pooled); class by onset
      value; round 1 by class.
  NEAR   the threshold summary above.

EXIT CODES
  0  completed.
  2  setup: a manifest or archive hash fails, a reader stops (onsetdiag's
     named messages), m is missing, or O1 fails.
  3  a recomputed onset differs from the committed one: everything is
     printed, and the classification is of the recomputed onset.

HOW TO RUN (laptop, the CAL4 environment)
  python scripts/onsetclass.py --n39 runs/rerun-analysis-20261025-051314 \
      --twenty runs/rerun-analysis-20261027-185918 --workers 2

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import multiprocessing                                          # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import onsetdiag as od                                          # noqa: E402
import rerunlib as rl                                           # noqa: E402

say, hdr, sha, fail = od.say, od.hdr, od.sha, od.fail
RULE_DATE = "2026-10-28"
CLASSES = ["start", "end", "continues", "no rise", "line"]
BANDS = [0.005, 0.01, 0.02, 0.05]
ARCH_FILES = ["regimemap_D_real.csv", "sn-article.tex"]


def classify(rs, y, onset, m):
    """(k, before, after, dist, class) for a curve y over rs with onset."""
    k = min(range(len(rs) - 1), key=lambda i: abs(rs[i] - onset))
    before = y[k] - y[0]
    after = y[-1] - y[k]
    dist = min(abs(before - m), abs(after - m))
    if k == 0:
        cls = "line"
    elif after > m and before <= m:
        cls = "start"
    elif before > m and after <= m:
        cls = "end"
    elif before > m and after > m:
        cls = "continues"
    else:
        cls = "no rise"
    return k, before, after, dist, cls


def unit(args):
    """One (row, diffusion, d): every curve, its onset, its class."""
    row, df, d, rs, objs, curves, m = args
    out = []
    pts = []
    for o in objs:
        y = curves[o]
        pts.append(y)
        on = float(rl.onset_bp(rs, y))
        out.append((row, df, d, o, y, on) + classify(rs, y, on, m))
    mp = [float(v) for v in np.mean(np.array(pts), axis=0)]
    on = float(rl.onset_bp(rs, mp))
    out.append((row, df, d, "pooled", mp, on) + classify(rs, mp, on, m))
    return out


def read_intervals(path, g):
    """{(diffusion, objective, d): (lo95, hi95)} from the onset rows; the
    file has already passed od.read_onsets."""
    out = {}
    with open(path, newline="") as fh:
        for rec in csv.DictReader(fh):
            if od.onset_kind(rec, g) == "onset":
                out[(rec["diffusion"], rec["objective"], int(rec["d"]))] = (rec["lo95"], rec["hi95"])
    return out


def read_m(folder):
    p = os.path.join(folder, "analysis_margin.csv")
    with open(p, newline="") as fh:
        vals = dict((r["name"], r["value"]) for r in csv.DictReader(fh))
    if "m" not in vals:
        fail("{} has no row m".format(p))
    return float(vals["m"]), vals["m"], p


def check_archive():
    man = {}
    with open(os.path.join(os.path.dirname(HERE), "zenodo-v1.sha256")) as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if ln:
                h, rel = ln.split("  ", 1)
                man[rel] = h
    for f in ARCH_FILES:
        p = os.path.join(rl.ARCH, f)
        if f not in man:
            fail("{} is not in zenodo-v1.sha256".format(f))
        got = sha(p)
        if got != man[f]:
            fail("{} sha256 {} differs from zenodo-v1.sha256 {}".format(p, got, man[f]))
        say("  {}  sha256 {}  equals zenodo-v1.sha256".format(p, got))


def line(row, df, d, o, on, iv, before, after, dist, cls):
    say("  {:<9} {:<11} d={:<3} {:<9} onset {:.2f}  95% [{}, {}]  before {:+.4f}  after {:+.4f}  "
        "dist {:.4f}  {}".format(row, df, d, o, on, iv[0], iv[1], before, after, dist, cls))


def main():
    ap = argparse.ArgumentParser(description="classification of every H3 onset (N43), read-only")
    ap.add_argument("--n39", required=True)
    ap.add_argument("--twenty", required=True)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    folders = {"n39": a.n39, "twenty": a.twenty}

    say("=" * 100)
    say("CBO-GAP onsetclass -- what kind of bend each H3 onset is (N43), read-only")
    say("=" * 100)
    say("  onsetclass sha256 {}".format(sha(os.path.abspath(__file__))))
    say("  onsetdiag sha256  {}".format(sha(os.path.join(HERE, "onsetdiag.py"))))
    say("  rerunlib sha256   {}".format(sha(os.path.join(HERE, "rerunlib.py"))))
    say("  python {}   numpy {}   platform {}   workers {}".format(
        platform.python_version(), np.__version__, platform.platform(), a.workers))
    say("  --n39 {}   --twenty {}   archive {}".format(a.n39, a.twenty, rl.ARCH))
    say("  writes nothing; no seed (nothing random); point S-slopes only, no bootstrap")
    say("")
    say("  What this prints, in plain words. Each H3 onset is where one bend fits a curve of")
    say("  S-slope against log r best. A bend can sit where a rise starts, where it ends, or")
    say("  where a rise already under way gets steeper, and the onset number alone does not")
    say("  say which. For every onset of ONSET (probe beta) and ONSET-CAL (fixed beta), 80 in")
    say("  all, and for round 1's ten, this script measures the net rise of the curve up to")
    say("  the bend ('before') and from the bend to r = 3.0 ('after'), and names the bend by")
    say("  comparing both with the margin m. A rise is the slope moving from -1 toward 0.")
    say("")
    say("  THE RULE IS POST HOC. It was fixed by Claude on {} (ledger N43) after the".format(RULE_DATE))
    say("  curves of the 25 onsets at 2.00, the isotropic d 80 mean curves and round 1's ten")
    say("  mean curves had been seen. Its extension to bends below 2.0 was written on {}".format(RULE_DATE))
    say("  before any of the other 55 was computed. It describes the point curves; it is not")
    say("  a test. Rule: before = y(onset) - y(0.75); after = y(3.0) - y(onset);")
    say("    start      after > m, before <= m      end      before > m, after <= m")
    say("    continues  both > m                    no rise  both <= m")
    say("    line       onset 0.75: a bend at the first point is a straight line, no bend")
    say("  dist = the smaller of |before - m| and |after - m|: the call cannot change unless m")
    say("  moves by at least dist.")

    hdr("V1  manifests and archive")
    for k in ("n39", "twenty"):
        rels = rl.verify_folder(folders[k])
        say("  {} verified ({} files)".format(folders[k], len(rels)))
    check_archive()

    g = rl.GRID["ONSET"]
    rs, objs = list(g["rs"]), list(g["objs"])
    if rl.GRID["ONSET-CAL"]["rs"] != g["rs"] or list(rl.GRID["ONSET-CAL"]["objs"]) != objs:
        fail("ONSET-CAL grid differs from ONSET's")

    hdr("V2  cells and onset files (onsetdiag readers)")
    slopes, rec, ivs = {}, {}, {}
    for row, fk, onf in od.ROWS:
        p = os.path.join(folders[fk], "analysis_cells.csv")
        slopes[row], n = od.read_slopes(p, row, g)
        say("  {:<9} {}  sha256 {}  {} cells, each once".format(row, p, sha(p), n))
        q = os.path.join(folders[fk], onf)
        rec[row], kinds = od.read_onsets(q, g, od.HEADER_KIND[row])
        ivs[row] = read_intervals(q, g)
        say("  {:<9} {}  sha256 {}  rows: onset {}, heterogeneity {}, J4 count {}".format(
            row, q, sha(q), kinds["onset"], kinds["heterogeneity"], kinds["J4 count"]))

    hdr("V3  ONSET slopes equal in both folders")
    other, _ = od.read_slopes(os.path.join(a.twenty, "analysis_cells.csv"), "ONSET", g)
    diff = [k for k in slopes["ONSET"] if slopes["ONSET"][k] != other[k]]
    if diff:
        fail("ONSET slopes differ between folders at {} cells, first {}".format(len(diff), diff[0]))
    say("  ONSET: {} cells equal as strings".format(len(other)))

    hdr("M  the margin")
    m, m_s, m_p = read_m(a.n39)
    say("  m = {} ({}, row m)".format(m_s, m_p))

    hdr("O1  round 1: the ten mean curves of tab:onset from the archive (rerunlib.onset_control)")
    ok, rep, o1 = rl.onset_control(rl.ARCH, os.path.join(rl.ARCH, "sn-article.tex"))
    for ln in rep:
        say("  " + ln)
    if not ok:
        fail("O1 failed: the archive does not reproduce tab:onset")
    say("  O1 PASS: 10 of 10")

    jobs = []
    for row, _, _ in od.ROWS:
        for df in g["diffs"]:
            for d in g["dims"]:
                curves = dict((o, [float(slopes[row][(df, o, d, r)]) for r in rs]) for o in objs)
                jobs.append((row, df, d, rs, objs, curves, m))
    pool = multiprocessing.Pool(a.workers)
    res = [x for u in pool.map(unit, jobs) for x in u]
    pool.close()
    pool.join()

    hdr("R  recomputed onsets against the committed ones")
    bad = 0
    for row, _, onf in od.ROWS:
        n_eq = 0
        mine = [x for x in res if x[0] == row]
        for x in mine:
            if x[5] == rec[row][(x[1], x[3], x[2])]:
                n_eq += 1
            else:
                bad += 1
                say("  MISMATCH {} {} d={} {}: recomputed {} committed {}".format(
                    row, x[1], x[2], x[3], x[5], rec[row][(x[1], x[3], x[2])]))
        say("  R {:<9} {} of {} equal ({})".format(row, n_eq, len(mine), onf))

    hdr("TABLE  every onset: committed interval, before, after, dist, class")
    say("  curves: S-slope at r = {}".format(", ".join(str(r) for r in rs)))
    for row, _, _ in od.ROWS:
        for x in sorted([x for x in res if x[0] == row],
                        key=lambda z: (z[1], z[2], (objs + ["pooled"]).index(z[3]))):
            r_, df, d, o, y, on, k, before, after, dist, cls = x
            line(row, df, d, o, on, ivs[row][(df, o, d)], before, after, dist, cls)
            say("  {:>36} y {}".format("", " ".join("{:+.3f}".format(v) for v in y)))
    r1 = []
    tab = rl.tex_onset_table(os.path.join(rl.ARCH, "sn-article.tex"))[0]
    for e in o1:
        k, before, after, dist, cls = classify(rs, e["means"], e["computed"], m)
        r1.append((e, before, after, dist, cls))
        say("  {:<9} {:<11} d={:<3} {:<9} onset {:.2f}  tab:onset line {}  before {:+.4f}  after {:+.4f}  "
            "dist {:.4f}  {}".format("ROUND-1", e["diffusion"], e["d"], "pooled", e["computed"], e["tex_line"],
                                     before, after, dist, cls))
        say("  {:>36} y {}   (table prints {})".format(
            "", " ".join("{:+.3f}".format(v) for v in e["means"]), " ".join(tab[(e["diffusion"], e["d"])][0])))

    hdr("COUNTS  (descriptive; the rule is post hoc)")
    for row, _, _ in od.ROWS:
        for lvl in ("objective", "pooled"):
            xs = [x for x in res if x[0] == row and ((x[3] == "pooled") == (lvl == "pooled"))]
            say("  {:<9} {:<9} {}  of {}".format(
                row, lvl, "  ".join("{} {}".format(c, sum(1 for x in xs if x[10] == c)) for c in CLASSES),
                len(xs)))
    say("")
    vals = sorted(set(x[5] for x in res))
    for row, _, _ in od.ROWS:
        for v in vals:
            xs = [x for x in res if x[0] == row and x[5] == v]
            if xs:
                say("  {:<9} onset {:.2f}: {}  of {}".format(
                    row, v, "  ".join("{} {}".format(c, sum(1 for x in xs if x[10] == c)) for c in CLASSES),
                    len(xs)))
    say("")
    say("  ROUND-1   pooled    {}  of {}".format(
        "  ".join("{} {}".format(c, sum(1 for z in r1 if z[4] == c)) for c in CLASSES), len(r1)))
    say("  ROUND-1 by onset: " + "; ".join("{} d={} {:.2f} {}".format(
        z[0]["diffusion"], z[0]["d"], z[0]["computed"], z[4]) for z in r1))

    hdr("NEAR  how many calls sit near m")
    allx = [(x[0], x[1], x[2], x[3], x[5], x[9], x[10]) for x in res if x[10] != "line"]
    allx += [("ROUND-1", z[0]["diffusion"], z[0]["d"], "pooled", z[0]["computed"], z[3], z[4])
             for z in r1 if z[4] != "line"]
    for grp in ("ONSET", "ONSET-CAL", "ROUND-1"):
        xs = [x for x in allx if x[0] == grp]
        say("  {:<9} {}  of {} classified onsets".format(
            grp, "  ".join("dist <= {} : {}".format(b, sum(1 for x in xs if x[5] <= b)) for b in BANDS),
            len(xs)))
    say("  the ten smallest dist:")
    for x in sorted(allx, key=lambda z: z[5])[:10]:
        say("    {:<9} {:<11} d={:<3} {:<9} onset {:.2f}  dist {:.4f}  {}".format(*x))

    hdr("SUMMARY")
    say("  peak RSS (main process) {:.1f} MB".format(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0))
    if bad:
        say("  R FOUND {} mismatches (exit 3)".format(bad))
        sys.exit(3)
    say("  completed; nothing written")


if __name__ == "__main__":
    main()
