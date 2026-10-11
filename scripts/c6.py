"""
c6.py  --  CBO-GAP round 2: the constant c6 of calprec v2's criterion C5m

WHAT THIS COMPUTES, IN PLAIN LANGUAGE
-------------------------------------
calprec v2 estimates a reference concentration as the MEDIAN of six
independent replicates (notes/CALPREC_V2_SPEC.md, section 11a). Its
precision criterion C5m (section 5 of that spec) is

        range / median  <=  0.01 x d6 / c6

where, for six independent standard normals,
    c6 = the standard deviation of their median (mean of the 3rd and 4th
         sorted values), and
    d6 = the expected value of their range (largest minus smallest).

The spec takes d6 = 2.534 from refscale's derivation (refscale.py
docstring, C5: "the expected range is about 2.53 standard deviations"; the
spec writes 2.534). c6 was deliberately not stated from memory. This script
estimates c6 by Monte Carlo. It also re-estimates d6 in the same run, as a
check on the 2.534 the spec uses, and prints both.

The value printed here is used in calprec v2's C5m and nowhere else. It is
copied by hand from this script's console log into calprec v2's docstring
before calprec v2's first execution. No dynamics, no archive, no objective.

METHOD
  N draws, each a vector of six independent N(0, 1) values, generated in
  chunks of --chunk vectors. Each chunk has its own random stream:
      numpy.random.default_rng(SeedSequence(key)),
      key = (ENTROPY 20261011, kind 51, chunk index, chunk size)
  at full SeedSequence width, never reduced to 32 bits (ledger N16). The
  stream is keyed by the chunk, not by the worker, so the result is the
  same for any --workers. For each vector: median = (s3 + s4) / 2 and
  range = s6 - s1, where s1 <= ... <= s6 are the sorted values. Per chunk
  the script records n, the mean and the sum of squared deviations (M2) of
  the median, and the same for the range. Chunks are combined exactly with
  the parallel-variance formula (Chan, Golub and LeVeque), so the pooled
  values do not depend on the order in which chunks finish.

  Estimates:
      c6_hat = sqrt(pooled M2 of the median / (N - 1))
      d6_hat = pooled mean of the range
  Monte Carlo standard errors, by batch means over the K chunks:
      se(c6_hat) = sd over chunks of the per-chunk c6 / sqrt(K)
      se(d6_hat) = sd over chunks of the per-chunk mean range / sqrt(K)
  Thresholds:
      T_spec = 0.01 x 2.534  / c6_hat      (the spec's formula)
      T_mc   = 0.01 x d6_hat / c6_hat      (d6 from this run; reported)
  The standard errors of the thresholds:
      se(T_spec) = T_spec x se(c6_hat) / c6_hat   (delta method)
      se(T_mc)   = sd over chunks of the per-chunk T_mc / sqrt(K)
                   (batch means)

PRE-SPECIFIED CRITERIA (fixed 2026-10-11, before first execution)
  M1  PRECISION OF c6. se(c6_hat) / c6_hat <= 1e-3, or the script prints
      "M1 FAIL: increase --n" and the value must not be used.
      Worked example (illustrative values): c6_hat 0.46, se 0.0002 gives
      4.3e-4, at most 1e-3: pass.
  M2  CONSISTENCY OF d6 WITH 2.534. |d6_hat - 2.534| <= 0.0005 +
      3 se(d6_hat). The 0.0005 allows for 2.534 being a value rounded to
      three decimals. M2 is reported. On FAIL the script says that the
      spec's d6 is not supported by this run, and the choice between T_spec
      and T_mc goes to Rahul; this script does not choose.
      Worked example (illustrative values): d6_hat 2.5344, se 0.0002 gives
      |0.0004| <= 0.0011: pass.
  N must be at least 10,000,000 (Rahul, 2026-10-11), or the script exits 2.
  The number of chunks K must be at least 20, so that the batch-means
  standard errors rest on at least 20 batches, or the script exits 2.

OUTPUT (new folder <outdir>/c6-<timestamp>/, every file opened "x")
  c6_chunks.csv    one row per chunk: index, seed key, n, mean and M2 of
                   the median, mean and M2 of the range
  c6_summary.csv   c6_hat, se, d6_hat, se, T_spec, se, T_mc, se, M1, M2
  --outdir PATH (else CBOGAP_OUTDIR, else <repo>/runs) is resolved by
  scripts/cbopaths.py, as in every round-2 script. This script does not use
  the archive.

HOW TO RUN (from the repository root, venv active)
    python scripts/c6.py --workers 2
  Defaults: --n 10000000 --chunk 250000 (K = 40). Exit code 0 when M1
  passes, 1 when M1 fails, 2 on a setup error.

Standard library and NumPy only. Python 3.8 to 3.11 syntax.
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse                                                 # noqa: E402
import csv                                                      # noqa: E402
import datetime                                                 # noqa: E402
import math                                                     # noqa: E402
import platform                                                 # noqa: E402
import resource                                                 # noqa: E402
import sys                                                      # noqa: E402
import time                                                     # noqa: E402
from multiprocessing import Pool                                # noqa: E402

import numpy as np                                              # noqa: E402

sys.dont_write_bytecode = True

import cbopaths                                                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTROOT = cbopaths.output_root(ROOT)

ENTROPY = 20261011
KIND = 51
D6_SPEC = 2.534
M1_MAX = 1e-3
M2_ROUND = 0.0005
N_MIN = 10000000
K_MIN = 20


def chunk_task(a):
    idx, size = a
    key = (ENTROPY, KIND, idx, size)
    rng = np.random.default_rng(np.random.SeedSequence(list(key)))
    s = np.sort(rng.standard_normal((size, 6)), axis=1)
    med = 0.5 * (s[:, 2] + s[:, 3])
    rng_ = s[:, 5] - s[:, 0]
    out = {"idx": idx, "key": "-".join(str(k) for k in key), "n": size,
           "med_mean": float(med.mean()), "med_m2": float(((med - med.mean()) ** 2).sum()),
           "rng_mean": float(rng_.mean()), "rng_m2": float(((rng_ - rng_.mean()) ** 2).sum()),
           "rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
           "pid": os.getpid()}
    return out


def combine(parts, mk, vk):
    """Exact parallel combination of (n, mean, M2) over chunks."""
    n, mean, m2 = 0, 0.0, 0.0
    for p in parts:
        nb, mb, m2b = p["n"], p[mk], p[vk]
        if n == 0:
            n, mean, m2 = nb, mb, m2b
            continue
        delta = mb - mean
        tot = n + nb
        mean = mean + delta * nb / tot
        m2 = m2 + m2b + delta * delta * n * nb / tot
        n = tot
    return n, mean, m2


def batch_se(vals):
    v = np.asarray(vals, dtype=np.float64)
    return float(v.std(ddof=1) / math.sqrt(len(v)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--n", type=int, default=N_MIN)
    p.add_argument("--chunk", type=int, default=250000)
    p.add_argument("--outdir", default=None,
                   help="output root; default <repo>/runs or CBOGAP_OUTDIR")
    a = p.parse_args()
    if a.n < N_MIN:
        sys.stderr.write("setup error: --n must be at least {}\n".format(N_MIN))
        return 2
    if a.chunk < 1 or a.n % a.chunk != 0:
        sys.stderr.write("setup error: --n must be a multiple of --chunk\n")
        return 2
    K = a.n // a.chunk
    if K < K_MIN:
        sys.stderr.write("setup error: need at least {} chunks; got {}\n".format(K_MIN, K))
        return 2
    if a.workers < 1:
        sys.stderr.write("setup error: --workers must be at least 1\n")
        return 2

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(OUTROOT, "c6-" + stamp)
    os.makedirs(outdir)

    print("=" * 88)
    print("CBO-GAP c6 -- standard deviation of the median of six standard normals (calprec v2 C5m)")
    print("=" * 88)
    print("  python   {}".format(sys.version.replace("\n", " ")))
    print("  numpy    {}".format(np.__version__))
    print("  platform {}   machine {}   cpus {}   workers {}".format(
        platform.platform(), platform.machine(), os.cpu_count(), a.workers))
    print("  N {}   chunk {}   K {} chunks".format(a.n, a.chunk, K))
    print("  seeds    default_rng(SeedSequence(key)), full width; key = (ENTROPY {}, kind {}, "
          "chunk index, chunk size)".format(ENTROPY, KIND))
    print("  median   (s3 + s4) / 2 of six sorted N(0,1);  range s6 - s1")
    print("  M1       se(c6_hat) / c6_hat <= {:g}".format(M1_MAX))
    print("  M2       |d6_hat - {}| <= {} + 3 se(d6_hat)  (reported)".format(D6_SPEC, M2_ROUND))
    print("  use      calprec v2 C5m only:  threshold = 0.01 x d6 / c6")
    print("  run dir  {}".format(outdir))
    sys.stdout.flush()

    t0 = time.time()
    tasks = [(i, a.chunk) for i in range(K)]
    with Pool(processes=a.workers) as pool:
        parts = pool.map(chunk_task, tasks, chunksize=1)
    parts.sort(key=lambda x: x["idx"])
    wall = time.time() - t0

    with open(os.path.join(outdir, "c6_chunks.csv"), "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["idx", "seed_key", "n", "median_mean", "median_M2", "range_mean", "range_M2"])
        for q in parts:
            w.writerow([q["idx"], q["key"], q["n"], repr(q["med_mean"]), repr(q["med_m2"]),
                        repr(q["rng_mean"]), repr(q["rng_m2"])])

    n, _mm, m2 = combine(parts, "med_mean", "med_m2")
    c6 = math.sqrt(m2 / (n - 1))
    _n2, d6, _r2 = combine(parts, "rng_mean", "rng_m2")
    c6_chunks = [math.sqrt(q["med_m2"] / (q["n"] - 1)) for q in parts]
    se_c6 = batch_se(c6_chunks)
    se_d6 = batch_se([q["rng_mean"] for q in parts])
    t_spec = 0.01 * D6_SPEC / c6
    se_t_spec = t_spec * se_c6 / c6
    t_mc = 0.01 * d6 / c6
    se_t_mc = batch_se([0.01 * q["rng_mean"] / cc for q, cc in zip(parts, c6_chunks)])
    m1 = (se_c6 / c6) <= M1_MAX
    m2_ok = abs(d6 - D6_SPEC) <= M2_ROUND + 3.0 * se_d6

    with open(os.path.join(outdir, "c6_summary.csv"), "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["N", "K", "c6_hat", "se_c6", "d6_hat", "se_d6", "T_spec", "se_T_spec",
                    "T_mc", "se_T_mc", "M1", "M2"])
        w.writerow([n, K, repr(c6), repr(se_c6), repr(d6), repr(se_d6), repr(t_spec),
                    repr(se_t_spec), repr(t_mc), repr(se_t_mc), "PASS" if m1 else "FAIL",
                    "PASS" if m2_ok else "FAIL"])

    print()
    print("  {} draws in {:.1f} s;  per-worker peak RSS max {:.1f} MB".format(
        n, wall, max(q["rss_mb"] for q in parts)))
    print()
    print("  c6_hat  = {:.6f}   se {:.6f}   (relative {:.2e})".format(c6, se_c6, se_c6 / c6))
    print("  d6_hat  = {:.6f}   se {:.6f}   (spec uses {})".format(d6, se_d6, D6_SPEC))
    print("  T_spec  = 0.01 x {} / c6_hat     = {:.6f}   se {:.6f}".format(D6_SPEC, t_spec, se_t_spec))
    print("  T_mc    = 0.01 x d6_hat / c6_hat = {:.6f}   se {:.6f}".format(t_mc, se_t_mc))
    print()
    print("  M1  {}".format("PASS" if m1 else "FAIL: increase --n; do not use this value"))
    print("  M2  {}".format(
        "PASS: d6_hat is consistent with {}".format(D6_SPEC) if m2_ok else
        "FAIL: this run does not support d6 = {}; T_spec against T_mc is Rahul's choice".format(D6_SPEC)))
    print("=" * 88)
    print("files  {}".format(outdir))
    print("=" * 88)
    return 0 if m1 else 1


if __name__ == "__main__":
    sys.exit(main())
