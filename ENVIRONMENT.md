# Environments

## Linux box, recorded 2026-10-08

```
Linux rahul-HP-245-G6-Notebook-PC 7.0.0-38-generic #38~24.04.4-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 14 16:37:11 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
Python 3.12.3
3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]
numpy 2.5.3
Linux-7.0.0-38-generic-x86_64-with-glibc2.39
nproc 2
Model name:                              AMD A6-9220 RADEON R4, 5 COMPUTE CORES 2C+3G
avx avx2 
               total        used        free      shared  buff/cache   available
Mem:           11409        3743        2745         100        4863        7666
Swap:           3789           0        3789
/dev/sda2       457G   35G  400G   8% /
```

Determinism gate (scripts/detcheck.py v3, D1-D3), archive /home/rahul/Research/cbo-gap-final/zenodo-v1, tasks R1,R2,R3: VERDICT   D1+D2: PASS   D3: PASS   OVERALL: PASS -- see logs/detcheck-v3-full-repo.log
Determinism gate (scripts/detcheck.py v3, D1-D3), archive /home/rahul/cbo-archive-test, tasks R1,R2,R3: VERDICT   D1+D2: PASS   D3: PASS   OVERALL: PASS -- see logs/detcheck-v3-full-separate.log
v3 is the current detcheck.py (after the cbopaths refactor). The v2 logs
(logs/detcheck-v2-full-repo.log, logs/detcheck-v2-full-separate.log) are
identical to the v3 logs in every compared quantity, every computed value,
every verdict, X0 and the five archive hashes. By diff, they differ only
in the run-folder path, the wall times and, in the repository-layout pair,
R2's printed peak RSS (167 MB in v2, 166 MB in v3). The v2 pass is
therefore not lost by the change.

## Kaggle CPU session, recorded 2026-10-09

From runs/detcheck-kaggle-20261009-094955/cbo-detcheck.log, the third launch
(kernel version 3), copied from the runner and detcheck headers:

```
  python   3.13.15 (main, Aug  6 2026, 11:06:22) [GCC 13.3.0]
  numpy    2.1.3
  platform Linux-6.18.48+-x86_64-with-glibc2.39   machine x86_64   cpus 4
  workers  4   tasks R1,R2,R3
  archive  /kaggle/input/datasets/ericsom/cbo-gap-archive
  found by candidate 2, /kaggle/input/datasets/<user>/<dataset>
```

The mount path was discovered by the runner, not assumed (ledger K3). The
two earlier launches failed before any script ran (ledger K1, K3).

Determinism gate (scripts/detcheck.py, D1-D3), archive /kaggle/input/datasets/ericsom/cbo-gap-archive, tasks R1,R2,R3: VERDICT   D1+D2: PASS   D3: PASS   OVERALL: PASS -- see runs/detcheck-kaggle-20261009-094955/cbo-detcheck.log

Measured in that run (4-worker pass, each realization in its own worker):

```
  pass 1: 4 worker(s)   wall 29.9 s
  R1  wall 2.7 s    peak RSS of its worker 42 MB
  R2  wall 16.3 s   peak RSS of its worker 180 MB
  R3  wall 29.7 s   peak RSS of its worker 330 MB
  pass 2: 1 worker, for D3   wall 46.4 s
```

## Round-1 Windows 7 machine, as recorded in round1-zip (2026-10-15)

round1-zip/ is a second read-only source beside zenodo-v1/. It is a round-1
working directory from Rahul's earlier laptop, extracted by Rahul and made
read-only. It is never written to. Its manifest is round1-zip.sha256 at the
repository root (143 files, paths relative to round1-zip/), verified with:

```
cd /home/rahul/Research/cbo-gap-final/round1-zip
sha256sum -c --quiet ../round1-zip.sha256 && echo "ROUND1 INTACT"
```

Platform of the round-1 runs, copied from the headers of its console logs
(for example round1-zip/cbo-gap/logs_M_full.log):

```
    python 3.8.10   numpy 1.24.4
    platform Windows-7-6.1.7601-SP1   workers 3
```

No determinism gate was ever run on that machine (ledger K4). Its contents
are recorded in ledger N34.
