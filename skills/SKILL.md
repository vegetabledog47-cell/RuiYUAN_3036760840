---
name: card-krueger-replication
description: Reproduce this repository's Card and Krueger 1994 Tables 2-4 and Figure 1, ownership heterogeneity extension, validation outputs and final report from the authorized restaurant survey CSV.
---

# Card and Krueger replication workflow

Use the repository root containing `project.json`, `code/` and `requirements.txt`. This skill documents the existing analysis; it does not authorize changing its research design or publishing restricted data.

## Execute

1. Obtain authorized course Package 01 as described in `../data/raw/README.md`. Keep its numbered folder structure. Check that `01_DID/data/public.csv` has 410 rows and 46 columns and the documented hash. Do not edit the input to improve a match.
2. Create a Python environment (Python 3.11 or newer), then install `requirements.txt`; `requirements-lock.txt` records the tested Python 3.14 environment.
3. From the root run `python code/run_all.py`. Use `--input PATH_TO_PUBLIC_CSV` for an alternative authorized input path. On the delivery computer `powershell -ExecutionPolicy Bypass -File .\run.ps1` also discovers the local dependency folder.
4. The command builds `data/processed/analysis_sample.csv`, all aggregate tables in `outputs/tables/`, figures in `outputs/figures/`, and `report.pdf` and `report.md`. No manual data or table edits are needed.

## Check and interpret

The workflow checks independent Welch and within-store DiD calculations, raw-column preservation, closure treatment, Table 4 coefficients, wage-bin totals, manual HC3 covariance and the four-cell ownership contrast. Inspect `outputs/tables/validation.json`, `extension_summary.json`, `sample_audit.csv` and `comparison.csv` after execution.

Expected landmarks are 384 paired stores, 357 Table 4 observations, paired DiD 2.75 FTE, and the chain-controlled company-owned-minus-franchise interaction about -1.1417 FTE (HC3 p about 0.637). All six extension specifications must be retained. These checks do not establish parallel trends or remove common state shocks.

Keep the 22 unmatched published numeric entries disclosed, and distinguish the author's Table 4 model-v specification from the printed ownership-control label. Do not substitute printed values for computed outputs or interpret a nonsignificant ownership contrast as equivalence. See the final report for the detailed methods and limitations.

Optional source validation: obtain `public.dat` from David Card's official archive, then run `python code/validate.py --author-data PATH_TO_PUBLIC_DAT`; `source_verification.json` records the numeric equality check. This is not a new independent sample.

Keep raw and processed store-level data outside public Git history. Update `AI_USE_DISCLOSURE.md` honestly when further assistance or student verification occurs. Repository invites, emails and submission require the user's applicable authorization; running this skill alone does not send them.
