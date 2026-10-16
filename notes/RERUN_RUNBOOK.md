# Rerun runbook: the fixed-beta rerun on Kaggle, shard by shard

Written 2026-10-16 for scripts/rerun.py, scripts/rerunlib.py and
scripts/rerun_analysis.py (notes/ANALYSIS_CRITERIA.md; review
notes/RERUN_REVIEW.md; ledger N35 to N37). Follow it in order. Every
command block starts from the repository root.

Rules this runbook enforces:
- **One Kaggle job at a time.** This counts calprec2's long shards too:
  a rerun job and a calprec2 job are never on Kaggle together.
- **Commit and push after every job.** Each job's output folder and its
  kgrun log are committed and pushed before the next job starts. kgrun's
  git guard refuses to start while runs/ has uncommitted paths or HEAD is
  unpushed.
- **Nothing fetched is lost.** A job that stops or dies is resumed from
  every earlier attempt folder of the same shard (CLAUDE.md rule 17).
- **No code edits while a shard set is in progress.** Do not edit
  rerun.py, rerunlib.py or costprobe2.py between the first shard and the
  last.
  - A resume compares rerun_sha256, rerunlib_sha256 and costprobe2_sha256
    with the earlier attempt's, and refuses on any difference.
  - The run mode refuses a plan built with a different rerunlib.py or
    costprobe2.py.
  - The shard set below runs at the commit that wrote this runbook:
    rerun.py sha256 756c4069...818e, rerunlib.py 5d55050e...9b06,
    costprobe2.py ea5cb2e1...f64b. These are the values the schedule log
    printed.

## Exit codes

| Script | Code | Meaning | What to do |
|---|---|---|---|
| rerun.py | 0 | complete | next job |
| rerun.py | 2 | setup refused: plan, P1, S1, a precheck criterion, unmeasured unit, a resume whose parameters differ | stop and paste; nothing to resume |
| rerun.py | 3 | F1 FAILED (finite-J audit identity) or D-SMOKE differ | stop and paste; do not resume |
| rerun.py | 4 | task errors, OVER BUDGET, or T1 STALL | relaunch the same shard as a resume; if the same tasks fail again, stop and paste |
| rerun.py | 5 | G-STOP: stopped after --stop-after (36000 s); not a failure | relaunch the same shard as a resume |
| rerun_analysis.py | 0 | complete | read the log |
| rerun_analysis.py | 2 | setup or A0: a folder fails its manifest, a realization disagrees with the plan, a task is complete twice | stop and paste |
| rerun_analysis.py | 6 | MARGIN REVISIT REQUIRED (5b): no gap computed | stop and paste; the margin goes back to Rahul |
| rerun_analysis.py | 7 | INCOMPLETE: analysis refused (D3) | finish the missing rows; no output was written |

When several rerun.py conditions apply, the code is the first of 5, 3,
4. The summary prints every condition.

"kgrun exit code 0" means only that kgrun finished. The job's own exit is
the line "kgrun runner: exit code N" in the kernel log (step 3).

## The rule that ties RMAP and ONSET together

RMAP owns the 24 cells it shares with ONSET: d 10 and 40, r 1.0 to 3.0,
tau0 0.1, all three objectives, both diffusions. REFSIZE owns the
ackley, sphere and rosenbrock cells it shares with NAMED and HORIZON, and
NAMED owns rastrigin's, which HORIZON shares. A shared cell is run once,
by the job whose --rows contain its owner. So:
- never launch ONSET without RMAP, or NAMED or HORIZON without REFSIZE.
  ONSET launched alone does not run the RMAP-owned cells, and reads as
  incomplete until RMAP's job has run;
- the archived-beta set below always runs all thirteen rows together,
  with one --rows list;
- every shard of a set uses the IDENTICAL --rows list and --nshards. The
  longest-processing-time split is a function of the plan, --rows and
  --nshards. A different list would reassign tasks between shards, and
  could run some twice and others never.

## Shard count for the archived-beta set (Rahul, 2026-10-16; ledger N37)

From logs/rerun-schedule-20261016-1945.log:
- 19068 tasks over the thirteen rows;
- 3 shards: 16795 s estimated each;
- 4 shards: 12596 s each.

Rahul chose 4. His reason: the estimate is a stated lower bound assuming
perfect scaling, and calprec2's shards have consistently run above their
estimates, so 3 shards leaves too little margin under the ceiling for the
saving of one launch.

## 0. Once, before the first job

0.1 The Kaggle image. The determinism gate passed on Kaggle with Python
3.13.15 and NumPy 2.1.3 (ENVIRONMENT.md). Every job's header must show
them (step 3). If the image has changed, stop: rule 16 requires detcheck
on the new image first.

0.2 The plan and the timing folders are shipped as data folders:

```
cd /home/rahul/Research/cbo-gap-final
PLAN=runs/rerun-plan-20261016-193630
T0=runs/costprobe2-s0-kaggle-20261010-103952
T1=runs/costprobe2-s1-kaggle-20261011-101343
for d in ${PLAN} ${T0} ${T1}; do (cd $d && sha256sum -c sha256.txt) || echo "MANIFEST FAIL $d"; done
```

## 1. Smoke on Kaggle (D-SMOKE), once

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
set -o noclobber
PLAN=runs/rerun-plan-20261016-193630
ROWS=BETA-ISO,BETA-ANI,LAWPANEL,PROBEARM,ADAPT,REFSIZE,SYNTH,NAMED,HORIZON,GEOM,RMAP,CLIFF,ONSET
JOB=rerun-smoke-arch-a1
git status --short runs
git status -sb | head -n 1
python scripts/kgrun.py run --job "${JOB}" --script rerun.py --data-dirs "${PLAN}" --args "--smoke --plan-from ${PLAN} --rows ${ROWS} --workers 4" > logs/kgrun-${JOB}.log 2>&1
echo "kgrun exit code $?"
tail -n 25 logs/kgrun-${JOB}.log
```

Read the result (step 3), commit it (step 4), and paste it. The shards
start only after "D-SMOKE PASS" and "kgrun runner: exit code 0".

## 2. One attempt of one shard of the archived-beta set

K = 4 (above). S runs 0, 1, 2, 3, one job at a time. A is the attempt
number. RESUME is empty for attempt 1.

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
set -o noclobber
K=4
S=0
A=1
PLAN=runs/rerun-plan-20261016-193630
T0=runs/costprobe2-s0-kaggle-20261010-103952
T1=runs/costprobe2-s1-kaggle-20261011-101343
ROWS=BETA-ISO,BETA-ANI,LAWPANEL,PROBEARM,ADAPT,REFSIZE,SYNTH,NAMED,HORIZON,GEOM,RMAP,CLIFF,ONSET
JOB=rerun-arch-s${S}of${K}-a${A}
ARGS="--plan-from ${PLAN} --timing-from ${T0} --timing-from ${T1} --rows ${ROWS} --shard ${S} --nshards ${K} --workers 4"
git status --short runs
git status -sb | head -n 1
python scripts/kgrun.py run --job "${JOB}" --script rerun.py --data-dirs "${PLAN},${T0},${T1}" --args "${ARGS}" > logs/kgrun-${JOB}.log 2>&1
echo "kgrun exit code $?"
tail -n 25 logs/kgrun-${JOB}.log
```

A resumed attempt (A = 2 or later, after exit 4, exit 5 or a death with
rows) has the same ARGS and adds --resume-dirs "${RESUME}". RESUME lists
every earlier attempt folder of THIS shard that holds rerun rows. To list
them:

```
cd /home/rahul/Research/cbo-gap-final
for d in runs/rerun-arch-s${S}of${K}-a*-kaggle-*; do ls "$d"/rerun-*/rerun_real.csv >/dev/null 2>&1 && printf '%s,' "$d"; done; echo
```

Drop the trailing comma. Then:

```
python scripts/kgrun.py run --job "${JOB}" --script rerun.py --data-dirs "${PLAN},${T0},${T1}" --resume-dirs "${RESUME}" --args "${ARGS}" > logs/kgrun-${JOB}.log 2>&1
```

Notes:
- **ARGS** must be identical across the attempts of one shard, and,
  except for --shard, across the four shards.
- **Never** put --resume-from in ARGS; kgrun adds it. Never pass
  --stop-after: the default, 36000 s, is one of the parameters a resume
  must match.
- **Resume folders.** They are only ever the same shard's. Another
  shard's tasks are disjoint and its "shard" parameter differs, so
  rerun.py refuses it (exit 2).
- **If kgrun is interrupted while polling,** the Kaggle job keeps running.
  Do not relaunch. Check it with:

  ```
  python scripts/kgrun.py status --job "${JOB}"
  ```

  Fetch only once it reports complete or error.

## 3. Read the result (rule 18)

If kgrun printed "FETCH OUTPUT into runs/<folder>", that is the folder; do
not fetch again (a second fetch makes a second folder with the same rows,
and the analysis stops on a task complete in two folders). If it printed
"Run did not complete", fetch once:

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
set -o noclobber
python scripts/kgrun.py fetch --job "${JOB}" > logs/kgrun-${JOB}-fetch.log 2>&1
echo "exit code $?"
cat logs/kgrun-${JOB}-fetch.log
```

Then:

```
cd /home/rahul/Research/cbo-gap-final
F=$(ls -d runs/${JOB}-kaggle-* | tail -n 1)
echo "${F}"
ls -R "${F}"
(cd "${F}" && sha256sum -c sha256.txt)
sha256sum scripts/rerun.py scripts/rerunlib.py scripts/costprobe2.py
grep -o "rerun_sha256 *[0-9a-f]*\|rerunlib_sha256 *[0-9a-f]*\|costprobe2_sha256 *[0-9a-f]*" "${F}"/*.log | sort -u
grep -o "python   3[0-9.]*\|numpy [0-9.]*\|mode [a-z]*)\|this shard: [^\"]*\|T1 stall guard [0-9]* s" "${F}"/*.log | sort -u
grep -o "resume: read [^\"]*" "${F}"/*.log
grep -o "ERROR [^\"]*\|OVER BUDGET\|F1 FAILED\|T1 STALL[^\"]*\|G-STOP[^\"]*\|D-SMOKE [A-Z]*" "${F}"/*.log | sort | uniq -c | head -n 40
grep -o "completed [0-9]*  errors [0-9]*  not started [0-9]*\|peak RSS max [^\"]*\|F1: [^\"]*" "${F}"/*.log
grep -o "kgrun runner: exit code [0-9]*" "${F}"/*.log
```

Check, before anything else:
- the three script hashes equal the local ones and the values at the top
  of this runbook;
- python 3.13.15 and numpy 2.1.3;
- mode run (or smoke), and "this shard:" with the shard you set;
- for a resume, a "resume: read" line for every RESUME folder.

## 4. Commit and push, every time, whatever the outcome

```
cd /home/rahul/Research/cbo-gap-final
git add "${F}" logs/kgrun-${JOB}.log
git add logs/kgrun-${JOB}-fetch.log 2>/dev/null
git status --short
git commit -m "rerun ${JOB}: runner exit code __N__, ${F} (N37)"
git push
git status -sb | head -n 1
```

If fetch brought back nothing, commit the logs alone and say so. Do not
delete the empty folder. Paste the tail of the kgrun log and the step 3
output.

## 5. Next launch, from the runner's exit code

- 0: the shard is done. Next shard, A = 1, RESUME empty.
- 5 (G-STOP): relaunch the same shard, A + 1, RESUME = every earlier
  attempt folder of this shard, this one included. Nothing complete is
  redone.
- 4 (errors, OVER BUDGET, T1 STALL): as for 5. Errored rows are not
  complete, so only they and the unstarted tasks run. If the same tasks
  fail again, stop and paste.
- 3 (F1 FAILED, D-SMOKE differ): stop and paste. Do not resume.
- 2 (setup, or a resume refused): stop and paste.
- No "kgrun runner: exit code" line (the job died: cap, pre-emption,
  cancellation). If the fetched folder holds a rerun-*/rerun_real.csv,
  every row ending "ok" is complete (each was flushed and fsynced); commit
  it and resume with it. If it holds no rows, relaunch with the same
  RESUME as the attempt that died.
- kgrun refused with "git guard": commit and push (step 4), then
  relaunch the same command.

## 6. The calibrated rows (CONC, TAU8, SIGMA, ANISO), after calprec2

After calprec2's finalize has written calprec2_beta.csv
(notes/CALPREC2_RUNBOOK.md section 6.3) and been committed:
1. A second precheck, on the laptop, with --calprec2
   runs/<calprec2 finalize folder>. It writes a new plan folder, and
   manifest.py writes its sha256.txt. Its keys and its archived-beta rows
   are identical to the first plan's: owners are computed over all
   seventeen rows in every plan.
2. A schedule for --rows CONC,TAU8,SIGMA,ANISO against the NEW plan.
   Rahul chooses the shard count from its output.
3. A Kaggle smoke and the shards of that set, as in sections 1 to 5, with
   the new plan and job names rerun-cal-s${S}of${K}-a${A}.
No step of this section starts before calprec2's table exists.

## 7. The analysis, after all seventeen rows are complete

It runs on the laptop, against the second (final) plan and every attempt
folder of every shard of both sets. It refuses with exit 7 if any row is
incomplete (D3) and with exit 2 if a task is complete in two folders.

```
cd /home/rahul/Research/cbo-gap-final
. .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
set -o noclobber
PLAN=runs/__FINAL_PLAN__
RUNS=$(for d in runs/rerun-arch-s*of4-a*-kaggle-* runs/rerun-cal-s*-a*-kaggle-*; do ls "$d"/rerun-*/rerun_real.csv >/dev/null 2>&1 && printf -- '--runs %s ' "$d"; done)
python scripts/rerun_analysis.py --plan-from ${PLAN} ${RUNS} --workers 2 > logs/rerun-analysis-$(date +%Y%m%d-%H%M).log 2>&1
echo "exit code $?"
python scripts/manifest.py
```

Smoke folders never go into --runs; their task ids are kind 83 and A0
rejects them.
