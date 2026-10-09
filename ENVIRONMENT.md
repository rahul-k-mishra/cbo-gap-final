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
