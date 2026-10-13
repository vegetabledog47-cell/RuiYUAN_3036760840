# AI-use record: core replication phase

This is a draft factual record of assistance in this chat. The student must review and supplement it before final submission. It does not claim the student has already independently checked every result.

## Assistance used

Codex read the local brief and data dictionary, rendered the scanned original paper to inspect Tables 2-4, Figure 1 and surrounding definitions, and wrote Python code and project documentation. It used a browser and downloaded David Card's official public archive to inspect the author's data and SAS cross-check program. It generated tables, figures, sample audits and comparison files, and maintained local Git commits.

## Checks performed by the assistant

- Compared the complete course CSV with the author's original public data; values and missingness match.
- Checked sample sizes, permanent versus temporary closures, missing employment components, wage-group membership, and the permanent-closure exception for the Table 4 wage requirement.
- Verified OLS coefficients independently with NumPy least squares, and checked figure-bin totals.
- Re-ran the pipeline from both local and external inputs, with explicit discrepancy reporting.
- Visually inspected the rendered source tables/footnotes and generated wage figure.

## Errors and assumptions corrected or rejected

1. An initial assertion treated SHEET as globally unique. Inspection found sheet 407 in different states for different restaurants; the assertion and identifier were corrected to use state plus sheet. No row was dropped.
2. Candidate headcount formulas did not reproduce the paper's full-time percentage. The code uses EMPFT/FTE, as confirmed by the author's SAS program.
3. Requiring both wage observations for every restaurant would exclude six permanent closures and produce only 351 regression observations. The closure exception restores N=357 and the published sample moments.
4. A trial excluded nonoperating stores' reported second-wave operating variables. After inspecting the author's code, this blanket rule was rejected; the source values are retained, and the resulting Table 2 wage-point discrepancy is disclosed.
5. The printed Table 4 model-v label suggests including ownership. The author's public SAS omits it. Both coherent specifications were computed, and the conflicting printed diagnostics were not mixed into a fabricated single model.
6. A store-cluster variance estimator for the unequal-sample Table 3 row 3 does not reproduce every published SE. This uncertainty remains disclosed rather than replacing computed SEs with copied values.
7. Original figure bin edges are not documented. Explicit bins and tail handling were chosen and documented; exact visual identity is not claimed.

## Student review still needed

The student should verify the economic interpretation, inspect the discrepancy log, run the workflow, understand the equations and sample choices, and add any other AI use before submitting. No independent extension or claim of student verification is included here.
