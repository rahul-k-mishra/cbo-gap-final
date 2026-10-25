"""
memprobe.py  --  CBO-GAP round 2: peak RSS of a held reference and the archived
                 beta_on_ensemble on it (calprec v2 review A4)

WHAT THIS MEASURES, IN PLAIN LANGUAGE
-------------------------------------
calprec v2 would hold a reference of up to 64M objective values in memory
and run the archived exactcal.beta_on_ensemble on it. beta_on_ensemble calls
log_ess_of, which allocates arrays the size of the reference (-beta f,
2a, a - max, exp(...)). How much memory that takes in one worker has never
been measured. Nothing about a held solve is designed until this number
exists (Rahul, 2026-10-11).

For each size n in 4000000, 16000000 and 64000000, in a fresh worker process:
  1. record the worker's peak RSS before anything is allocated (baseline);
  2. draw n objective values of ackley, d = 40, centred law, through the
     archived exactcal.draw_initial and exactcal.OBJECTIVES, in chunks of
     250000, into one held float64 array; record the peak RSS (held);
  3. run exactcal.beta_on_ensemble(values, 0.01, n); record the peak RSS
     (solve) and the wall times.
Peak RSS is resource.getrusage(RUSAGE_SELF).ru_maxrss / 1024 (Linux
kilobytes to MB). The objective and law affect only the values, not the
array sizes, so one cell is enough.

EXTENSION 2026-10-25 (ledger N42). --module, --objective, --d and --tau
select another cell. Without them the script does exactly what it did for
N25: exactcal, ackley, d = 40, centred, tau0 0.01. With --module set to a
costprobe2 module, step 2 draws through that module's own sampler and
objective (costprobe2.probe_sample and costprobe2.objective_of, the
functions calprec2 draws with), in the same chunks of 250000. Step 3 is
unchanged: exactcal.beta_on_ensemble, which calls exactcal.log_ess_of, the
function calprec2's E1 evaluates on its held 64M replicate.
  Why: the calprec2 smoke over RMAP, CLIFF and ONSET
  (runs/calprec2-smoke-ext-kaggle-20261025-065222) measured a 4M peak of
  679.4 MB for regimemap rastrigin d = 80 against 374.2 MB at d = 40, so
  d enters the peak beyond the chunk. N25's 64M peak (2472.8 MB) is a
  d = 40 measurement, and no 64M peak at d = 80 exists.
  Worked example: --module regimemap --objective rastrigin --d 80 --tau 0.1
  draws rng.standard_normal((m, 80)) chunks, evaluates regimemap.OBJ
  ["rastrigin"] on them, and solves at tau0 0.1.
The seed key gains no field: SeedSequence((ENTROPY, kind, n, chunk)) as
before. The values are used for nothing but this measurement.

SAFETY GATE (pre-specified; the laptop's free memory can be as low as
1.5 GB, CLAUDE.md rule 6)
  The sizes run one at a time, in order, never in parallel, whatever
  --workers is: parallel probes would confound each other's RSS and could
  exhaust memory. --workers sets only the pool size (rule 5).
  64M runs only if its extrapolated solve peak is at most 0.8 x MemAvailable
  (/proc/meminfo) read just before it starts. The extrapolation is linear
  in n from the 4M and 16M solve peaks:
      peak_64 ~ peak_16 + (peak_16 - peak_4) x (64 - 16) / (16 - 4)
  Otherwise the script stops before 64M, prints both numbers and says so.
  Worked example (illustrative values): peaks 400 and 1000 MB give
  1000 + 600 x 4 = 3400 MB; with MemAvailable 3000 MB the limit is 2400 MB,
  so 64M is not run.

REPORTED CRITERION (no decision is taken here)
  M-RSS  The solve peak at 64M against the 3072 MB per-worker budget
         (Rahul, 2026-10-10): "within budget" or "exceeds budget".
         Worked example (illustrative values): 2650 MB, within budget.

SEEDS
  default_rng(SeedSequence((ENTROPY 20261011, kind 61, n, chunk))), at full
  width. The values are not used for anything but this measurement.

OUTPUT (new folder <outdir>/memprobe-<timestamp>/, file opened "x")
  memprobe.csv   one row per size: n, baseline, held and solve peak RSS (MB),
                 draw and solve walls, beta, achieved, MemAvailable before,
                 and the gate's decision

HOW TO RUN (from the repository root, venv active)
    python scripts/memprobe.py --workers 1
    python scripts/memprobe.py --workers 1 --module regimemap --objective rastrigin --d 80 --tau 0.1
  The second form needs about 3 GB free and belongs on Kaggle (kgrun).
  --archive and --outdir are resolved by scripts/cbopaths.py. Exit code 0
  on completion, including when the gate stops before 64M; 2 on a setup
  error.

NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402
from multiprocessing import Pool                                # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True

import cbopaths                                                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = cbopaths.archive_path(ROOT)
OUTROOT = cbopaths.output_root(ROOT)
if not os.path.isdir(ARCH):
    sys.stderr.write("setup error: archive not found at {}\n".format(ARCH))
    sys.exit(2)
sys.path.insert(0, ARCH)
try:
    import exactcal as ec
except Exception as exc:                                        # pragma: no cover
    sys.stderr.write("setup error: cannot import exactcal: {}\n".format(exc))
    sys.exit(2)

SIZES = [4000000, 16000000, 64000000]
CHUNK = 250000
D, OBJ, LAW, TAU = 40, "ackley", "centred", 0.01
ENTROPY, KIND = 20261011, 61
BUDGET_MB = 3072.0
GATE_FRACTION = 0.8


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def file_sha(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def mem_available_mb():
    with open("/proc/meminfo") as fh:
        for ln in fh:
            if ln.startswith("MemAvailable:"):
                return float(ln.split()[1]) / 1024.0
    return float("nan")


def sampler(cell):
    """(draw(rng, m), f) for the cell: exactcal's as for N25, or a costprobe2
    module's own sampler and objective (calprec2's f_chunk)."""
    module, obj, d, law = cell["module"], cell["obj"], cell["d"], cell["law"]
    if module == "exactcal":
        return (lambda rng, m: ec.draw_initial(rng, m, d, obj, law)), ec.OBJECTIVES[obj]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import costprobe2 as cp
    mod = cp.MODS[module]
    return ((lambda rng, m: cp.probe_sample(module, mod, obj, d, law, rng, m)),
            cp.objective_of(module, mod, obj))


def probe(n, cell):
    base = rss_mb()
    draw, f = sampler(cell)
    t0 = time.time()
    vals = np.empty(n, dtype=np.float64)
    pos, ci = 0, 0
    while pos < n:
        m = min(CHUNK, n - pos)
        rng = np.random.default_rng(np.random.SeedSequence([ENTROPY, KIND, n, ci]))
        X = draw(rng, m)
        vals[pos:pos + m] = f(X)
        del X
        pos += m
        ci += 1
    t_draw = time.time() - t0
    held = rss_mb()
    t0 = time.time()
    beta, ach = ec.beta_on_ensemble(vals, cell["tau"], n)
    t_solve = time.time() - t0
    solve = rss_mb()
    return {"n": n, "baseline_mb": base, "held_mb": held, "solve_mb": solve,
            "draw_s": t_draw, "solve_s": t_solve, "beta": float(beta), "achieved": float(ach),
            "pid": os.getpid()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--archive", default=None)
    p.add_argument("--outdir", default=None)
    p.add_argument("--module", default="exactcal")
    p.add_argument("--objective", default=OBJ)
    p.add_argument("--d", type=int, default=D)
    p.add_argument("--tau", type=float, default=TAU)
    a = p.parse_args()
    if a.workers < 1:
        sys.stderr.write("setup error: --workers must be at least 1\n")
        return 2
    cell = {"module": a.module, "obj": a.objective, "d": a.d, "law": LAW, "tau": a.tau}
    try:
        sampler(cell)
    except Exception as exc:
        sys.stderr.write("setup error: cell {}: {}: {}\n".format(cell, type(exc).__name__, exc))
        return 2
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(OUTROOT, "memprobe-" + stamp)
    os.makedirs(outdir)

    print("=" * 88)
    print("CBO-GAP memprobe -- peak RSS of a held reference and the archived beta_on_ensemble")
    print("=" * 88)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {} (sizes run one at a time)".format(
        platform.platform(), platform.machine(), os.cpu_count(), a.workers))
    print("  archive  {}".format(ARCH))
    print("  cell     module {}  {} d={} {} tau0 {}   sizes {}   chunk {}".format(
        cell["module"], cell["obj"], cell["d"], cell["law"], cell["tau"], SIZES, CHUNK))
    print("  script   sha256 {}".format(file_sha(os.path.abspath(__file__))))
    print("  seeds    default_rng(SeedSequence((ENTROPY {}, kind {}, n, chunk))), full width".format(ENTROPY, KIND))
    print("  gate     64M only if extrapolated solve peak <= {} x MemAvailable".format(GATE_FRACTION))
    print("  budget   {:.0f} MB per worker (reported, M-RSS)".format(BUDGET_MB))
    print("  run dir  {}".format(outdir))
    sys.stdout.flush()

    fields = ["n", "baseline_mb", "held_mb", "solve_mb", "draw_s", "solve_s", "beta", "achieved",
              "mem_available_mb", "gate"]
    rows = []
    with open(os.path.join(outdir, "memprobe.csv"), "x", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        fh.flush()
        for n in SIZES:
            avail = mem_available_mb()
            gate = "run"
            if n == SIZES[-1]:
                p4, p16 = rows[0]["solve_mb"], rows[1]["solve_mb"]
                extrap = p16 + (p16 - p4) * (64.0 - 16.0) / (16.0 - 4.0)
                limit = GATE_FRACTION * avail
                print("\n  gate: extrapolated 64M solve peak {:.0f} MB, MemAvailable {:.0f} MB, limit {:.0f} MB".format(
                    extrap, avail, limit))
                if not (extrap <= limit):
                    gate = "not run: extrapolated {:.0f} MB > limit {:.0f} MB".format(extrap, limit)
                    w.writerow({"n": n, "mem_available_mb": "{:.0f}".format(avail), "gate": gate})
                    fh.flush()
                    print("  64M NOT RUN: {}".format(gate))
                    break
            with Pool(processes=a.workers, maxtasksperchild=1) as pool:
                r = pool.apply(probe, (n, cell))
            r["mem_available_mb"] = avail
            r["gate"] = gate
            rows.append(r)
            w.writerow({"n": n, "baseline_mb": "{:.1f}".format(r["baseline_mb"]),
                        "held_mb": "{:.1f}".format(r["held_mb"]), "solve_mb": "{:.1f}".format(r["solve_mb"]),
                        "draw_s": "{:.1f}".format(r["draw_s"]), "solve_s": "{:.1f}".format(r["solve_s"]),
                        "beta": repr(r["beta"]), "achieved": repr(r["achieved"]),
                        "mem_available_mb": "{:.0f}".format(avail), "gate": gate})
            fh.flush()
            os.fsync(fh.fileno())
            print("\n  n {:>9}   baseline {:7.1f} MB   held {:7.1f} MB   solve peak {:7.1f} MB   "
                  "draw {:6.1f} s   solve {:6.1f} s   MemAvailable before {:.0f} MB".format(
                      n, r["baseline_mb"], r["held_mb"], r["solve_mb"], r["draw_s"], r["solve_s"], avail))
            sys.stdout.flush()
    if len(rows) == len(SIZES):
        s = rows[-1]["solve_mb"]
        print("\n  M-RSS  64M solve peak {:.1f} MB: {}".format(s, "within budget" if s <= BUDGET_MB else "exceeds budget"))
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(main())
