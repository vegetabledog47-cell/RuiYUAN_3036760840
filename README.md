# Minimum wage replication and ownership extension

**Author:** Rui YUAN, 3036760840. **Course:** ECON 6067.

**Repository:** https://github.com/vegetabledog47-cell/RuiYUAN_3036760840

The project reproduces Card and Krueger (1994), Tables 2-4 and Figure 1, and tests whether the NJ-versus-PA employment change differs between company-owned and franchise restaurants. See **[report.pdf](report.pdf)** for the complete empirical report and **[AI_USE_DISCLOSURE.md](AI_USE_DISCLOSURE.md)** for AI disclosure. The report includes remaining numerical discrepancies and a source inconsistency in Table 4 model v. Do not describe every paper entry as exactly reproduced.

## Inputs and access

Obtain course Package 01 through the course's authorized channel. Extract it here without changing folder names:

```text
01_DID/
  README.md
  DATA_DICTIONARY.md
  data/
    public.csv
```

The expected CSV has 410 rows and 46 columns. SHA-256:

```text
45e6f4ac4928f7c9fcc2585a45e0467ecaa039f0b241f4c5a26cd290fd8e772b
```

Do not publish the course data, course download links or derived store-level data. These inputs are ignored by Git. They are present in the local delivery folder; reviewers with authorized access regenerate the processed dataset at `data/processed/analysis_sample.csv`.

Source verification: [David Card's official data page](https://davidcard.berkeley.edu/data_sets.html) provides a public archive and codebook. Its `public.dat` has the same numeric matrix and missingness as the course CSV; the archived SAS also documents the model-v ambiguity discussed in the report. The analysis does not require this additional download. To repeat that optional check, obtain the archive from the author's page and run `code/validate.py --author-data PATH_TO_PUBLIC_DAT` after the pipeline.

## Reproduce all results

Python 3.11+; tested on Python 3.14 on Windows. No Stata, Excel or paid application is required.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python code\run_all.py
```

`requirements-lock.txt` records the versions used for this delivery. For the closest environment match, install that file instead of `requirements.txt` on a compatible Python version.

On the delivery computer, an optional ignored `.runtime/python_packages/` folder supplements the existing Python installation. This launcher detects it automatically:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

The execution-policy flag applies only to that PowerShell process. The launcher does not change the computer's global execution policy. A different input location can be specified without code changes:

```powershell
python code\run_all.py --input "PATH_TO_PUBLIC_CSV"
```

The single command performs core replication, the ownership extension, independent validation and PDF/Markdown report generation. Inputs are not modified. No manual editing of data or result tables is required.

## Files

| Path | Purpose |
|---|---|
| `report.pdf` | Final empirical report, including all assigned tables, both figures, extension and discrepancy appendix |
| `report.md` | Editable text generated alongside the PDF |
| `AI_USE_DISCLOSURE.md` | Detailed AI-use and correction record |
| `project.json` | Author, course and repository metadata |
| `code/run_all.py` | Complete workflow entry point |
| `code/replicate.py` | Core sample construction, Tables 2-4, Figure 1 and published-entry comparisons |
| `code/extension.py` | Ownership interaction, HC3 intervals and six sensitivity specifications |
| `code/validate.py` | Independent DiD, closure, input-integrity and optional source-data checks |
| `code/build_report.py` | Report generation from computed results |
| `outputs/tables/` | Aggregate tables and audit outputs |
| `outputs/figures/` | Wage distribution and ownership figures |
| `skills/SKILL.md` | Reusable instructions for running and checking the workflow |
| `data/raw/README.md` | Restricted input access and original package structure |
| `data/processed/analysis_sample.csv` | Regenerated store-level analysis data; ignored by Git |
| `.git/` | Meaningful project development history |

`outputs/tables/extension_summary.json` records extension checks. `outputs/tables/reproducibility_check.json` records the final clean-input rerun. Runtime tests do not establish parallel trends or resolve common state shocks; the report discusses these limitations. Report regeneration requires ReportLab, already in the dependency files.

## 中文使用说明

先阅读 `report.pdf`。这是英文正式报告，已包含核心复现、独立拓展、稳健性检验、局限与 AI 使用说明。`report.md` 是可编辑文本，不需要与 PDF 分别提交两份报告。当前电脑运行 `run.ps1` 可重建全部结果。

课程要求向教学团队分享可访问的 GitHub 仓库链接。仓库必须允许老师下载或克隆；私有仓库需要给教学团队访问权限。仅把文件放在本地或建立私有仓库，并不能保证老师可访问。不要上传受限原始数据；按上文说明输入目录及获取方式。报告中的未完全一致数字已有解释，不能在提交时删去这些披露。

## Submission arrangement

This repository follows the teaching team's example structure. The original numbered course-package folder is retained unchanged, as required by the brief; `data/raw/README.md` documents its location. Store-level raw and processed data are excluded from the public repository under the course restriction and regenerated by the workflow. The required input is small and all other code and aggregate outputs are included.

Submission is by emailing this repository URL to both teaching-team addresses in the Moodle notice after inviting `xiongyan2224` and `Jeff7c` as collaborators. The deadline is 18 October 2026, 23:59 Hong Kong time.
