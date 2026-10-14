# AI use disclosure

**Author:** Rui YUAN, 3036760840
**Course:** ECON 6067
**Updated:** 14 October 2026

## Project direction and AI assistance

I supplied the assignment brief, original paper and course data package, and requested a staged workflow: complete the assigned core replication before undertaking an extension. I also requested explanations of the methods, results and development history, and a review of the AI disclosure against the assignment requirements. I specified the local delivery arrangements and repository visibility.

Codex provided substantial assistance throughout the project. This included interpreting the brief and data dictionary, inspecting the scanned paper, retrieving the author's public data and SAS program, writing the analysis and validation code, and generating tables and figures. Codex proposed the ownership heterogeneity question and implemented the interaction model and sensitivity checks. It also drafted and formatted the report, prepared documentation and maintained Git records. At my request, Codex checked the final Moodle notice and example repository, aligned the submission layout, documented a reusable skill, reran the workflow and prepared the GitHub submission settings. The report layout was inspected page by page. Restricted course data and derived store-level data were excluded from the GitHub repository.

## Validation of AI generated outputs

Codex performed source comparisons and implemented numerical checks within the workflow:

- The course CSV was compared with the author's public data; all numeric values and missing entries matched.
- Sample counts, wage groups, missing employment components and permanent versus temporary closures were checked against the paper and source documentation.
- OLS coefficients were checked using NumPy least squares. The paired DiD was independently recomputed using Welch inference and a two-period within-store regression.
- The extension's HC3 covariance matrix was checked against its sandwich formula, and the unadjusted ownership interaction against the four-cell difference.
- Wage-bin counts and percentage totals were checked. A clean-copy rerun regenerated 22 table, figure and report files identically.

These are assistant-performed and automated validation checks. They are distinguished here from personal verification by the student and do not establish the research design's causal assumptions.

## Corrections and unresolved differences

Several initial coding assumptions were corrected during the AI-assisted workflow. SHEET was initially treated as a globally unique identifier; because sheet 407 appears in both states, the identifier was changed to state plus sheet without deleting a restaurant. The full-time percentage was corrected to EMPFT/FTE, consistent with the author's SAS program. The Table 4 wage screen was also corrected to retain six permanent closures, restoring the published 357-store sample rather than excluding them to obtain 351 observations.

A trial rule excluding nonoperating stores' reported follow-up characteristics was rejected after checking the author's program. Reported source values were retained, and the remaining Table 2 differences were disclosed. For Table 4 model v, the printed ownership-control label conflicts with the author's public SAS specification. Both coherent specifications were computed and documented; statistics from different models were not combined to force agreement with the printed column.

The Table 3 row-3 standard errors remain different from those published. The implemented variance estimator is documented, and computed values were not replaced with the paper's figures. Figure 1 uses explicit wage bins and tail treatment because the original figure does not specify these details; exact bar-for-bar reproduction is not claimed.

## Interpretation and responsibility

All six ownership specifications are reported, including wide intervals and the sign change after controlling for baseline employment. The nonsignificant interaction is interpreted as limited evidence, not proof of equal effects. The report also explains the two-state inference limitation, the absence of a pre-trend test and the remaining replication discrepancies.

I remain responsible for understanding and defending the data choices, empirical methods and conclusions in the submitted project. AI assistance and its associated checks do not transfer that responsibility. This disclosure should be updated if further assistance or personal verification is undertaken before submission.
