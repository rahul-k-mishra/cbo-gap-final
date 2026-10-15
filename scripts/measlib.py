"""
measlib.py  --  CBO-GAP round 2: shared helpers for the measurements M1 to M7

WHY THIS EXISTS
---------------
M1 to M7 (scripts/m1_estimands.py ... scripts/m7_pairing.py; ledger N30 to
N33, notes/ANALYSIS_CRITERIA_DRAFT.md) all read the same archived
per-realization files, check them against the deposit manifest, seed their
bootstraps the same way and write run folders the same way. One copy of
that code lives here so that seven copies cannot drift apart. This module
contains no dynamics and no criterion. Every criterion is stated in the
docstring of the script that applies it.

WHAT IT PROVIDES
----------------
  Archive access. The archive path comes from scripts/cbopaths.py (--archive,
  else CBOGAP_ARCHIVE, else <repo>/zenodo-v1). The archived modules
  regimemap (rm), exactcal (ec) and reboot (rb) are imported from it, and
  so is the helper module scripts/detcheck.py (half_ulp_of_string,
  sha256_of). The slope fit is the archived one, rm.fit_slope or
  ec.fit_slope (CLAUDE.md rule 4); nothing is refitted by retyped code.
  sys.dont_write_bytecode is set before any import, so no __pycache__ is
  written into the read-only archive.

  verify_archive(names). Hashes each named archive file and compares it with
  <repo>/zenodo-v1.sha256, the manifest of the deposit. Returns the rows to
  print and a flag. A script stops with exit 2 on any mismatch.

  Loaders. They return the per-realization data of the archive in the file's
  row order:
    load_exactcal()  exactcal_real.csv, key (objective, d, init, tau_str)
    load_rmapj()     rmapj_real.csv,    key (diffusion, objective, d, r_str)
    load_regimemap(fname)  regimemap_D_real.csv or regimemap_M_real.csv,
                     key (diffusion, objective, d, r_str, tau_str),
                     realizations ordered by the rep column.
  Each value holds E (R x J float array, where the file stores per-J
  errors), the stored slope strings, the stored seeds or reps, and J.

  Seeds. rng_for(kind, key) = default_rng(SeedSequence([ENTROPY, kind] +
  key)), at full SeedSequence width, never reduced to 32 bits (ledger N16).
  key_str(kind, key) is the text written to the output CSVs. The bootstrap
  stream of a cell is keyed by the cell, never by the worker or by the
  order of tasks, so results do not depend on --workers.

  Bootstrap primitives:
    slope_curve(Jv, E)         rm.fit_slope on the realization-mean curve
    slopes_each(Jv, E)         rm.fit_slope within each realization
    boot_curve(Jv, E, idx)     slope_curve on every resample in idx (B x R)
    boot_mean(v, idx)          mean of v on every resample in idx
    pct(x, q)                  numpy.percentile (default linear rule, as in
                               the archive) of the finite entries of x

  Output. new_outdir(prefix) creates <outroot>/<prefix>-<timestamp>/ and
  fails if it exists; write_csv opens every file with mode "x".

Worked example of a seed key. M1 (kind 61) bootstrapping cell index 17 of
exactcal_real.csv (source code 1), repeat 0:
    key [20261015, 61, 1, 17, 0]
    rng = default_rng(SeedSequence([20261015, 61, 1, 17, 0]))
    key_str -> "20261015-61-1-17-0"

Importing this module imports the archive modules and detcheck, prints
nothing and creates nothing. A missing archive exits 2 with a message, as
in detcheck.py.

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402

sys.dont_write_bytecode = True

import numpy as np                                              # noqa: E402

import cbopaths                                                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = cbopaths.archive_path(ROOT)
OUTROOT = cbopaths.output_root(ROOT)
if not os.path.isdir(ARCH):
    sys.stderr.write("setup error: archive not found at {}\n".format(ARCH))
    sys.stderr.write("pass --archive <path> or set CBOGAP_ARCHIVE\n")
    sys.exit(2)
sys.path.insert(0, ARCH)

try:
    import regimemap as rm                                      # noqa: E402
    import exactcal as ec                                       # noqa: E402
    import reboot as rb                                         # noqa: E402
except Exception as exc:                                        # pragma: no cover
    sys.stderr.write("setup error: cannot import archived scripts: {}\n".format(exc))
    sys.exit(2)

import detcheck                                                 # noqa: E402

half_ulp_of_string = detcheck.half_ulp_of_string
sha256_of = detcheck.sha256_of

ENTROPY = 20261015
J_LIST = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5000]
SOURCE_CODE = {"exactcal": 1, "rmapj": 2, "regimemap_D": 3, "regimemap_M": 4}
MANIFEST = os.path.join(ROOT, "zenodo-v1.sha256")


# ----------------------------------------------------------------------------
# archive integrity
# ----------------------------------------------------------------------------
def verify_archive(names):
    """Return (rows, ok). Each row: (name, sha256 computed, status)."""
    want = {}
    with open(MANIFEST, newline="") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            h, n = line.split(None, 1)
            want[n.strip()] = h
    rows, ok = [], True
    for n in names:
        path = os.path.join(ARCH, n)
        if not os.path.isfile(path):
            rows.append((n, "-", "MISSING"))
            ok = False
            continue
        h = sha256_of(path)
        st = "ok" if want.get(n) == h else "MISMATCH against zenodo-v1.sha256"
        if st != "ok":
            ok = False
        rows.append((n, h, st))
    return rows, ok


# ----------------------------------------------------------------------------
# loaders
# ----------------------------------------------------------------------------
def _rows(fname):
    with open(os.path.join(ARCH, fname), newline="") as fh:
        return list(csv.DictReader(fh))


def load_exactcal():
    """Cells of exactcal_real.csv in first-appearance order."""
    cells = {}
    for x in _rows("exactcal_real.csv"):
        k = (x["objective"], int(x["d"]), x["init"], x["tau"])
        c = cells.setdefault(k, {"E": [], "slope_str": [], "seed": [], "J": J_LIST})
        c["E"].append([float(x["E_%d" % J]) for J in J_LIST])
        c["slope_str"].append(x["slope"])
        c["seed"].append(int(x["seed"]))
    for c in cells.values():
        c["E"] = np.array(c["E"], dtype=np.float64)
    return cells


def load_rmapj():
    """Cells of rmapj_real.csv in first-appearance order."""
    cells = {}
    for x in _rows("rmapj_real.csv"):
        k = (x["diffusion"], x["objective"], int(x["d"]), x["r"])
        c = cells.setdefault(k, {"E": [], "slope_str": [], "seed": [], "rep": [], "J": J_LIST})
        c["E"].append([float(x["E_%d" % J]) for J in J_LIST])
        c["slope_str"].append(x["slope"])
        c["seed"].append(int(x["seed"]))
        c["rep"].append(int(x["rep"]))
    for c in cells.values():
        order = np.argsort(np.array(c["rep"]), kind="stable")
        c["E"] = np.array(c["E"], dtype=np.float64)[order]
        c["slope_str"] = [c["slope_str"][i] for i in order]
        c["seed"] = [c["seed"][i] for i in order]
        c["rep"] = [c["rep"][i] for i in order]
    return cells


def load_regimemap(fname):
    """Cells of regimemap_D_real.csv or regimemap_M_real.csv; slopes only."""
    cells = {}
    for x in _rows(fname):
        k = (x["diffusion"], x["objective"], int(x["d"]), x["r"], x["tau"])
        c = cells.setdefault(k, {"slope_str": [], "rep": []})
        c["slope_str"].append(x["slope"])
        c["rep"].append(int(x["rep"]))
    for c in cells.values():
        order = np.argsort(np.array(c["rep"]), kind="stable")
        c["slope_str"] = [c["slope_str"][i] for i in order]
        c["rep"] = [c["rep"][i] for i in order]
        c["slope"] = np.array([float(s) for s in c["slope_str"]], dtype=np.float64)
    return cells


# ----------------------------------------------------------------------------
# seeds
# ----------------------------------------------------------------------------
def rng_for(kind, key):
    return np.random.default_rng(np.random.SeedSequence([ENTROPY, kind] + [int(v) for v in key]))


def key_str(kind, key):
    return "-".join(str(v) for v in [ENTROPY, kind] + [int(v) for v in key])


# ----------------------------------------------------------------------------
# bootstrap primitives (the slope fit is the archived rm.fit_slope)
# ----------------------------------------------------------------------------
def slope_curve(Jv, E):
    return float(rm.fit_slope(Jv, E.mean(axis=0)))


def slopes_each(Jv, E):
    return np.array([rm.fit_slope(Jv, row) for row in E], dtype=np.float64)


def boot_curve(Jv, E, idx):
    means = E[idx].mean(axis=1)
    return np.array([rm.fit_slope(Jv, m) for m in means], dtype=np.float64)


def boot_mean(v, idx):
    return v[idx].mean(axis=1)


def pct(x, q):
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return float("nan")
    return float(np.percentile(x, q))


def n_nonfinite(x):
    return int((~np.isfinite(np.asarray(x, dtype=np.float64))).sum())


# ----------------------------------------------------------------------------
# output and reporting
# ----------------------------------------------------------------------------
def new_outdir(prefix):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(OUTROOT, "{}-{}".format(prefix, stamp))
    os.makedirs(out)
    return out


def write_csv(path, header, rows):
    with open(path, "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def fmt(v):
    return repr(float(v))


def print_header(title, kind, workers, params, archive_files, outdir):
    print("=" * 88)
    print(title)
    print("=" * 88)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {}".format(
        platform.platform(), platform.machine(), os.cpu_count(), workers))
    print("  archive  {}".format(ARCH))
    print("  run dir  {}".format(outdir))
    print("  seeds    default_rng(SeedSequence([ENTROPY {}, kind {}, source code, cell index, "
          "statistic or repeat ...])), full width".format(ENTROPY, kind))
    print("  source codes {}".format(SOURCE_CODE))
    print("  slope fit: archived regimemap.fit_slope (exactcal.fit_slope only for the P0 check)")
    for k in sorted(params):
        print("  {:<14} {}".format(k, params[k]))
    rows, ok = verify_archive(archive_files)
    print("  archive files checked against zenodo-v1.sha256:")
    for n, h, st in rows:
        print("    {}  {}  {}".format(h, n, st))
    sys.stdout.flush()
    return ok


def p0_check(cells, Jv, which):
    """Refit every realization's slope with the archived function that wrote
    it and compare with the stored string. Tolerance: half a unit in the last
    stored digit plus 1e-7 (see the calling script's docstring). Returns
    (n compared, n failed, worst excess)."""
    n = bad = 0
    worst = 0.0
    for c in cells.values():
        for row, s in zip(c["E"], c["slope_str"]):
            if which == "exactcal":
                got = float(ec.fit_slope(list(Jv), list(row)))
            else:
                got = float(rm.fit_slope(Jv, row))
            tol = half_ulp_of_string(s) + 1e-7
            diff = abs(got - float(s))
            n += 1
            if not diff <= tol:
                bad += 1
                worst = max(worst, diff - tol)
    return n, bad, worst
