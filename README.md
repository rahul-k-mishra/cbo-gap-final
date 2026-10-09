# cbo-gap-final

Revision workspace for "Finite-ensemble observability of the mean-field
convergence rate in consensus-based optimization" (JOGO-D-26-00563, rejected
with invitation to resubmit). Author: Rahul Kumar Mishra.

Read CLAUDE.md first. It is binding for every human and every Claude session.
Then read notes/DEFECT_LEDGER.md.

## What is where

- zenodo-v1/ is the deposited archive, DOI 10.5281/zenodo.22068685, 68 files,
  read-only. Nothing is ever written there. Verify it with
  zenodo-v1-manifest-claude.sha256 after every clone.
- referee/ holds the referee report and the submitted PDF.
- manuscript/ is the round-2 LaTeX source.
- scripts/ holds round-2 scripts; they import dynamics from zenodo-v1.
- runs/<run-id>/ holds one executed run each; logs/ holds analysis-only logs.
- ENVIRONMENT.md records every machine this ran on; requirements.lock pins the
  Linux environment.

## After a fresh clone

    cd cbo-gap-final
    chmod -R a-w zenodo-v1
    cd zenodo-v1 && sha256sum * | LC_ALL=C sort -k2 | diff - ../zenodo-v1-manifest-claude.sha256 && echo "ARCHIVE INTACT"; cd ..
    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install -r requirements.lock

## Running a round-2 script

Every script prints its parameters, seeds, Python and NumPy versions and
platform at the head of the run, takes --workers, and refuses to overwrite an
existing output. Run from the repository root with the venv active, for example:

    cd /home/rahul/Research/cbo-gap-final
    . .venv/bin/activate
    export PYTHONDONTWRITEBYTECODE=1
    set -o noclobber
    python scripts/detcheck.py --workers 2 > logs/detcheck-$(date +%Y%m%d-%H%M).log 2>&1
    python scripts/manifest.py --dry-run
    python scripts/manifest.py

set -o noclobber makes the shell refuse to redirect onto a log that already
exists, so a console log is never overwritten.

detcheck.py takes --archive (default zenodo-v1 in this repository) and
--outdir (default runs/), so the same file runs unchanged with the archive
somewhere else, for example on Kaggle (calprec.py and costprobe.py do not
take these flags yet; CLAUDE.md rule 15 requires them before a Kaggle run):

    python scripts/detcheck.py --workers 4 --archive /kaggle/input/cbo-gap-archive --outdir /kaggle/working

After every run, scripts/manifest.py writes sha256.txt into each run folder
under runs/ that does not have one yet. It never touches a folder that
already has one. Commit the console log, the run folder and its sha256.txt
together.
