# calprec2 runbook: the 336-cell full run on Kaggle, shard by shard

Written 2026-10-11 for scripts/calprec2.py (CALPREC_V2_SPEC 11c, ledger N28)
and scripts/kgrun.py with resumption (ledger K5, closed). Follow it in
order. Every command block starts from the repository root.

Rules this runbook enforces:
- one Kaggle job at a time;
- after each job, its output folder and its kgrun log are committed and
  pushed before the next job starts. kgrun's git guard refuses to start
  while runs/ has uncommitted paths or HEAD is unpushed;
- nothing is lost that was fetched. A job that dies is resumed from every
  earlier attempt folder of the same shard.

## 0. Once, before the first shard

0.1 Get the shard count. Use the RECOMMENDED count, the one at the
50% target. The count at the full ceiling is printed too; do not use it.

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
set -o noclobber
python scripts/calprec2.py --plan --workers 4 --rows CONC,TAU8,SIGMA,ANISO --throughput runs/calprec2-smoke-kaggle-20261011-121225 > logs/calprec2-plan-target-thr.log 2>&1
echo "exit code $?"
grep -n "PASS\|FAIL\|total\|best case\|largest single\|at the target\|at the full ceiling\|RECOMMENDED\|no shard" logs/calprec2-plan-target-thr.log
```

Write down K, the number after "RECOMMENDED: --nshards". Commit the log:

```
cd /home/rahul/Research/cbo-gap-final
git add logs/calprec2-plan-target-thr.log
git commit -m "calprec2 plan at the shard target (N28): logs/calprec2-plan-target-thr.log"
git push
```

0.2 Check the Kaggle environment once. The determinism gate passed on
Kaggle with Python 3.13.15 and NumPy 2.1.3 (ENVIRONMENT.md). Every shard's
header must show those same versions (step 2). If Kaggle's image has
changed them, stop: rule 16 requires detcheck on the new image before any
number from it is used. A resumed attempt on a different version is
refused by calprec2 anyway (exit 2), because resume compares python and
numpy.

## 1. Launch one attempt of one shard

Set four values: K from 0.1, S the shard index (0 to K-1), A the attempt
number (1 for a fresh shard), and RESUME. RESUME is empty for attempt 1.
For later attempts it lists EVERY earlier attempt folder of THIS shard
that has calprec2 rows (section 4), comma-separated, with no spaces.

Fresh shard, attempt 1:

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
set -o noclobber
K=__K_FROM_STEP_0.1__
S=0
A=1
JOB=calprec2-s${S}of${K}-a${A}
THR=runs/calprec2-smoke-kaggle-20261011-121225
ARGS="--workers 4 --rows CONC,TAU8,SIGMA,ANISO --throughput ${THR} --shard ${S} --nshards ${K}"
git status --short runs
git status -sb | head -n 1
python scripts/kgrun.py run --job "${JOB}" --script calprec2.py --data-dirs "${THR}" --args "${ARGS}" > logs/kgrun-${JOB}.log 2>&1
echo "kgrun exit code $?"
tail -n 25 logs/kgrun-${JOB}.log
```

Resumed attempt, A = 2 or later. RESUME names the earlier attempts'
folders of the same shard:

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
set -o noclobber
K=__K_FROM_STEP_0.1__
S=__SAME_SHARD__
A=__NEXT_ATTEMPT__
RESUME=runs/__FOLDER_OF_ATTEMPT_1__,runs/__FOLDER_OF_ATTEMPT_2__
JOB=calprec2-s${S}of${K}-a${A}
THR=runs/calprec2-smoke-kaggle-20261011-121225
ARGS="--workers 4 --rows CONC,TAU8,SIGMA,ANISO --throughput ${THR} --shard ${S} --nshards ${K}"
python scripts/kgrun.py run --job "${JOB}" --script calprec2.py --data-dirs "${THR}" --resume-dirs "${RESUME}" --args "${ARGS}" > logs/kgrun-${JOB}.log 2>&1
echo "kgrun exit code $?"
tail -n 25 logs/kgrun-${JOB}.log
```

Notes:
- ARGS must be identical across the attempts of one shard: same workers,
  rows, shard and nshards. calprec2 refuses a resume whose parameters
  differ (rule 17).
- Never put --resume-from in ARGS. kgrun adds it on Kaggle, with the
  rebuilt paths.
- RESUME FOLDERS ARE NEVER ANOTHER SHARD'S. Do not pass shard 0's
  folders to shard 1.
  - Different shards have disjoint tasks, so there is nothing to skip.
  - Their parameters differ in "shard", so calprec2 refuses them (exit 2).
  Rahul's instruction of 2026-10-11 said to launch the next shard "with
  the previous folders as resume inputs". He has since said that was wrong
  (2026-10-11). Resume inputs come from earlier attempts of the SAME shard
  only. A new shard's attempt 1 has none.
- Do not pass --stop-after. The default, 32400 s (nine hours, three under
  the cap), is a margin choice, not a measurement. It is one of the
  parameters a resume must match, so every attempt of a shard must use
  the same value; leaving it at the default guarantees that.
- "kgrun exit code 0" means kgrun itself finished. It says nothing about
  the job. The job's own exit is the line "kgrun runner: exit code N" in
  the kernel log (step 2).
- If the laptop sleeps or kgrun is interrupted while polling, the Kaggle
  job keeps running. Do not relaunch. Check it, and fetch only after it
  reports complete or error:

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
python scripts/kgrun.py status --job "${JOB}"
```

## 2. Read the result (rule 18)

If kgrun printed "FETCH OUTPUT into runs/<folder>", that is the folder.
Do NOT fetch again. A second fetch of the same kernel makes a second folder
with the same rows, and finalize stops (exit 2) on a task that is complete
in two folders. If it printed "Run did not complete", fetch it now, once:

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
set -o noclobber
python scripts/kgrun.py fetch --job "${JOB}" > logs/kgrun-${JOB}-fetch.log 2>&1
echo "exit code $?"
cat logs/kgrun-${JOB}-fetch.log
```

Then read the header and the end of the job. The kernel log is Kaggle's
JSON stream, so grep for fixed phrases:

```
cd /home/rahul/Research/cbo-gap-final
F=$(ls -d runs/${JOB}-kaggle-* | tail -n 1)
echo "${F}"
ls -R "${F}"
(cd "${F}" && sha256sum -c sha256.txt)
sha256sum scripts/calprec2.py
grep -o "script   sha256 [0-9a-f]*" "${F}"/*.log
grep -o "numpy    [0-9.]*" "${F}"/*.log
grep -o "python   3[0-9.]*" "${F}"/*.log
grep -o "mode     [^\"]*" "${F}"/*.log
grep -o "shipped folders[^\"]*\|resume  [^\"]*\|data  [^\"]*\|rows, [0-9]* with end ok" "${F}"/*.log
grep -o "read /tmp/kgrun-ship[^\"]*" "${F}"/*.log
grep -o "G-MEM [A-Z]*\|G-RSS FAIL[^\"]*\|FAIL [^\"]*\|ERROR [^\"]*" "${F}"/*.log | head -n 40
grep -o "errored or timed-out tasks: [0-9]*" "${F}"/*.log
grep -o "kgrun runner: exit code [0-9]*" "${F}"/*.log
```

Check, before anything else:
- the script sha256 equals the local sha256sum of scripts/calprec2.py at
  the commit you launched from;
- python 3.13.15 and numpy 2.1.3 (0.2);
- mode full, the shard and nshards you set;
- for a resumed attempt, every RESUME folder appears with "manifest
  PASS", and calprec2's "read /tmp/kgrun-ship/..." lines show the rows
  it found.

## 3. Commit and push, every time, whatever the outcome

```
cd /home/rahul/Research/cbo-gap-final
git add "${F}" logs/kgrun-${JOB}.log
git add logs/kgrun-${JOB}-fetch.log 2>/dev/null
git status --short
git commit -m "calprec2 shard ${S} of ${K}, attempt ${A}: runner exit code __N__, ${F} (N28)"
git push
git status -sb | head -n 1
```

If fetch brought back nothing, the folder is empty and git cannot track it.
Commit the logs alone, and say "nothing fetched" in the message. Do not
delete the empty folder; it is harmless, and deleting under runs/ is denied.

Then paste into the conversation:
- the tail of the kgrun log;
- the grep output of step 2.

## 4. Decide the next launch from the runner's exit code

- exit code 0: the shard is done. Go to step 1 with S = S + 1, A = 1 and
  RESUME empty.
- exit code 4 (errored or timed-out tasks; the folder holds every
  completed row):
  - relaunch the SAME shard with A = A + 1;
  - RESUME = every earlier attempt folder of this shard, this one
    included;
  - errored rows are not complete, so only they, and the tasks not yet
    run, are redone;
  - if the same tasks fail again, stop and paste.
- exit code 5 (stopped early by --stop-after; NOT a failure). The folder
  is complete as far as it goes. The run's last lines say which phase it
  stopped in, how many tasks of that phase were not started, and that
  later phases were not built.
  - Do steps 2 and 3 as for any attempt: fetch if kgrun did not, verify
    the manifest, commit and push.
  - Relaunch the SAME shard with A = A + 1. RESUME = every earlier attempt
    folder of this shard, this one included.
  - The resumed job recomputes nothing already complete. It continues from
    the first incomplete task: the not-started tasks of the stopping
    phase, then the later phases.
  - A shard may need several exit-5 attempts. Each one is a complete
    record; none is lost.
- exit code 3 (E1 or R1 failed): stop. Do not resume. Paste the FAIL
  lines. E1's 1e-12 is not loosened in advance (Rahul, 2026-10-11).
- exit code 2 (setup: V0, V1, V2, G-CAP, G-MEM, G-STOP, or a resume refused
  because parameters, Python or NumPy differ): stop and paste. There is
  no calprec2 output to resume from.
- NO "kgrun runner: exit code" line: the job died, by the 12-hour cap,
  pre-emption or cancellation. With --stop-after this should not happen
  through the cap: G-STOP refuses any job whose stop plus per-task timeout
  exceeds 12 hours. It can still happen through pre-emption, or through
  time Kaggle spends before phase A. Look in the fetched folder:
  - it holds a calprec2-full-*/calprec2_tasks.csv. Each row was flushed and
    fsynced when its task finished, so every row with end "ok" is complete,
    and a row cut off mid-write is not counted as complete. It is a
    partial folder: committed in step 3, it goes into RESUME. Relaunch the
    same shard with A = A + 1;
  - it holds no calprec2 rows (Kaggle kept nothing of /kaggle/working).
    That attempt's work is lost. Relaunch the same shard with A = A + 1
    and the SAME RESUME as the attempt that died, which is empty if it was
    attempt 1. The loss is bounded by one attempt.
  Whether /kaggle/working survives the cap is still not known (ledger K5).
  The first death will tell. Paste its fetch log.
- kgrun refused with "git guard": commit and push (step 3), then relaunch
  the same command. Nothing went to Kaggle.

RESUME lists only folders whose sha256.txt verifies and that hold
calprec2 rows. An empty folder, or one with only a log, does not go in it.
To list this shard's usable attempt folders:

```
cd /home/rahul/Research/cbo-gap-final
for d in runs/calprec2-s${S}of${K}-a*-kaggle-*; do ls "$d"/calprec2-full-*/calprec2_params.csv >/dev/null 2>&1 && printf '%s,' "$d"; done; echo
```

Drop the trailing comma when setting RESUME.

## 5. After every shard has exited 0: finalize on the laptop

Finalize does no draws. It reads every attempt folder of every shard,
concatenates the rows (a repeated task is accepted only over an earlier
error row), and expects all 336 cells. A missing shard gives "incomplete
(phase A)" cells and exit 4.

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
set -o noclobber
K=__K_FROM_STEP_0.1__
ALL=$(for d in runs/calprec2-s*of${K}-a*-kaggle-*; do ls "$d"/calprec2-full-*/calprec2_params.csv >/dev/null 2>&1 && printf '%s,' "$d"; done)
ALL=${ALL%,}
echo "${ALL}" | tr ',' '\n' | wc -l
python scripts/calprec2.py --finalize "${ALL}" > logs/calprec2-finalize.log 2>&1
echo "exit code $?"
tail -n 40 logs/calprec2-finalize.log
python scripts/manifest.py > logs/calprec2-finalize-manifest.log 2>&1
cat logs/calprec2-finalize-manifest.log
git add runs/calprec2-finalize-* logs/calprec2-finalize.log logs/calprec2-finalize-manifest.log
git commit -m "calprec2 finalize (N28): calprec2_beta.csv for 336 cells"
git push
```

Paste the finalize log. The label counts, the adequacy counts and every
FLAG line go into the ledger only from that log.
