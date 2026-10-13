# Card and Krueger (1994): core replication

Scope: Table 2, Table 3, Table 4 and Figure 1. No independent extension is included.

## Inputs and execution

Python 3.11+ is recommended. Extract the course Package 01 into this directory, preserving `01_DID/data/public.csv`. Read the course README and data dictionary. Do not redistribute the course data or download links. The original paper is not redistributed.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python src\replicate.py
```

An external input can also be supplied:

```powershell
python src\replicate.py --input "PATH_TO_PUBLIC_CSV"
```

The script creates all tables, Figure 1, comparison files, a sample audit, processed store-level data, provenance, and a self-contained HTML results viewer. No manual data/code changes are required. See `REPLICATION_NOTES.md` for methods, unresolved differences and validation, and `AI_USE.md` for the AI-use record.

On this computer, the optional isolated workspace dependencies are detected by `powershell -ExecutionPolicy Bypass -File .\run.ps1`. On another computer use the virtual-environment instructions above. A Chinese guide is in `复现说明.md`. Start with `results/replication_results.html` to review the outputs. The HTML file uses the accompanying local PNG, so keep the results folder together.

After replication, run `python src/validate.py` for independent Welch and within-store DiD checks, closure/sample checks and raw-column integrity checks. Optionally pass `--author-data PATH_TO_OFFICIAL_PUBLIC_DAT` to repeat the numeric equality check against the official archive; this optional archive is not required to reproduce the main results.

The supplied raw data and processed store-level data are ignored by Git. They remain available locally; reviewers obtain the restricted raw input through the course and regenerate the processed data. Keep access to any shared processed data consistent with its license. Git history records development stages. Repository creation/publication and submission are not performed by this workflow.
