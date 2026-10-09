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

Determinism gate (scripts/detcheck.py v2, D1-D3), archive /home/rahul/Research/cbo-gap-final/zenodo-v1, tasks R1,R2,R3: VERDICT   D1+D2: PASS   D3: PASS   OVERALL: PASS -- see logs/detcheck-v2-full-repo.log
Determinism gate (scripts/detcheck.py v2, D1-D3), archive /home/rahul/cbo-archive-test, tasks R1,R2,R3: VERDICT   D1+D2: PASS   D3: PASS   OVERALL: PASS -- see logs/detcheck-v2-full-separate.log

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
