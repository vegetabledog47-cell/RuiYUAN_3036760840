# Core replication methods and discrepancy record

This is the core replication phase only, prepared on 13 October 2026. No independent extension is included. It is not yet a complete final course submission.

## Sources inspected

1. The user-supplied original paper, `Minimum_wages_and_employment_.pdf`, scanned 22-page version. Journal page 775 (PDF page 4) defines FTE and closure treatment; page 776 (PDF page 5) is Table 2; page 777 (PDF page 6) is Figure 1; pages 778-781 (PDF pages 7-10) explain Tables 3-4 and print both tables on journal page 780 (PDF page 9).
2. The course `01_DID/data/public.csv`, its README and data dictionary, plus the individual-project brief (Draft v3).
3. [David Card's official data page](https://davidcard.berkeley.edu/data_sets.html), [official archive README](https://davidcard.berkeley.edu/readme/njmin-readme.txt), and the [author's public archive](https://davidcard.berkeley.edu/data_sets/njmin.zip), accessed 13 October 2026. `public.dat`, `codebook` and `check.sas` were inspected. This archive concerns the surveys also used in *Myth and Measurement*, chapter 2; it is a useful primary cross-check, not proof of the exact program that produced every AER table entry.

The complete 410-by-46 numeric matrix in the course CSV equals the official `public.dat`, including missing values. See `results/source_verification.json`. The official archive and original paper are not bundled or republished. All analysis uses the course CSV, not pasted coefficients from another replication.

## Sample construction and definitions

- Raw sample: 410 restaurants, NJ 331 and PA 79. No rows are deleted globally or winsorized.
- `SHEET` is not globally unique: 407 appears once in each state for different restaurants. The working identifier is `(STATE,SHEET)`. Deduplicating by SHEET would incorrectly drop a restaurant.
- FTE = full-time employees + managers + 0.5 × part-time employees. Missing components remain missing: a missing worker count is not zero.
- Wave-2 employment at the six permanent closures is zero. The four temporary closures (status 2, 4, 5) are missing in the baseline; Table 3 row 5 alone sets their employment to zero.
- Percentage full-time = 100 × EMPFT / FTE. This reproduces the published definition; it is not a headcount fraction, and managers are not included in the numerator.
- Full meal price = soda + fries + entree, with all three required. The supplied prices include tax; no further tax is added.
- Recruiting bonuses use BONUS at wave 1 and SPECIAL2 at wave 2.
- Descriptive means use the available observations for each variable. We retain reported wave-2 operating characteristics as supplied, consistent with `check.sas`. In particular, renovation-closed sheet 65 reports a $5.05 starting wage, and second-wave refuser sheet 136 reports hours and some prices. No ad hoc deletion is used to force a printed match.
- Wage-point percentages in Table 2 use all stores in each state as denominator, treating a missing wage as not satisfying that wage-point indicator, as SAS `(WAGE_ST=4.25)` and `(WAGE_ST2=5.05)` do. This differs from Figure 1, which excludes missing wages from its denominator. This detail matters: NJ's initial $4.25 count is 101; 101/331 = 30.5% in Table 2, whereas 101/314 = 32.2% among observed wages in Figure 1.
- NJ baseline wage groups are $4.25 (101), $4.26-$4.99 (140), and at least $5.00 (73); the remaining 17 have missing baseline wages. Employment means within each group use the available employment observations.

## Table 2

All rows, state means, mean standard errors, denominators and t statistics are generated. Standard errors are sample SD / sqrt(n). The NJ-minus-PA t statistic uses sqrt(SE_NJ² + SE_PA²), allowing unequal group variances. The published table does not show standard errors for store-type percentages; the CSV includes them for auditing.

Remaining differences include the NJ wave-2 $5.05 percentage: the archive contains 283 such wages, giving 85.4985%, whereas the paper prints 85.2%. Dropping the observed wage of temporary closure sheet 65 would give 282/331 = 85.1964%, but the author's public `check.sas` does not make that deletion. That is a plausible explanation, not an established fact about the AER implementation. The script retains the observation. Some t statistics also do not match printed precision; these are listed in `comparison.csv`.

## Table 3

Rows 1 and 2 are separate-wave employment means. Row 3 subtracts those means, allowing unequal observed samples. Row 4 averages store-level changes for stores with both employment observations. Row 5 does the same after setting temporary-closure employment to zero. Between-group differences are recomputed from unrounded means; their standard errors combine the independent group variances.

The main paired-sample DiD is 2.7500, SE 1.34234 (paper 2.75, 1.34); temporary closures set to zero give 2.50921, SE 1.34601 (paper 2.51, 1.35). The balanced sample is 384 stores: NJ 309 and PA 75. The alternative closure sample is 388 stores: NJ 313 and PA 75.

For row 3, the unbalanced difference of means needs a covariance-aware SE. This implementation uses a store-level influence-function estimator:

    z_i = observed_after_i * (after_i - mean_after)/n_after
          - observed_before_i * (before_i - mean_before)/n_before
    SE = sqrt[N/(N-1) * sum(z_i^2)]

Missing contributions are zero; N is the number of original stores in the group. This is a documented estimator for the observed-data estimand, not a claim to have recovered the original authors' unpublished variance algorithm. For NJ it gives 0.47215 versus the paper's 0.54; for PA 1.22199 versus 1.25. All eight row-3 SEs (including contrasts) remain outside the published rounding intervals. `check.sas` labels its summaries only 'PART OF TABLE 3' and does not establish the row-3 variance calculation. The difference must remain disclosed. Several small point-estimate discrepancies also remain, typically around 0.005-0.008 FTE; they cannot automatically be asserted to be simple rounding errors.

## Table 4

Outcome: wave-2 minus wave-1 FTE. Sample: observed employment in both waves and observed starting wages in both waves, **or a permanent closure with observed baseline wage**. This gives N=357 (NJ 290, PA 67), mean change -0.237535, sample SD 8.825485, matching the paper's sample description.

GAP = max((5.05 - initial wage)/initial wage, 0) for NJ; GAP = 0 for PA. Models use OLS with an intercept and conventional homoskedastic standard errors to match the historical table. Chain dummies omit one chain; regions omit North NJ.

| Model | Computed coefficient | Computed SE | Paper coefficient (SE) |
|---|---:|---:|---:|
| i: NJ | 2.325831 | 1.191596 | 2.33 (1.19) |
| ii: NJ + chain + ownership | 2.303860 | 1.195532 | 2.30 (1.20) |
| iii: GAP | 15.652890 | 6.080237 | 15.65 (6.08) |
| iv: GAP + chain + ownership | 14.915674 | 6.205335 | 14.92 (6.21) |
| v: GAP + chain + regions, author SAS implementation | 11.913064 | 7.394409 | 11.91 (7.39) |

**Model (v) has an important source inconsistency.** The printed Table 4 says chain/ownership controls are included. The author's public `check.sas` command for model (v) omits CO_OWNED. Following that command gives the printed GAP coefficient and SE, but residual SE = 8.740165 and joint-controls p = 0.307491, rather than printed 8.75 and 0.40. Adding ownership gives GAP = 11.979237 (SE 7.419121), residual SE = 8.752489 and joint-controls p = 0.404570. Thus neither coherent specification matches every printed entry. Both are preserved: the principal table follows the author's SAS, and `table_4_model_v_label_audit.csv` records the printed-label interpretation. This audit resolves an implementation ambiguity; it is not the independent extension.

Controls p is a joint F test of all added chain/ownership/region regressors, excluding the intercept and NJ/GAP. Its restriction matrix is constructed explicitly. Model (i)'s 95% interval includes zero slightly; the point estimate alone should not be described as decisive evidence of a positive causal effect.

## Figure 1

Both survey waves and both states are reproduced as grouped wage-distribution bars. Ten-cent half-open bins are [4.20,4.30), [4.30,4.40), ... [5.40,5.50), with the last bin pooling all wages at least $5.50. Wages are converted to integer cents before binning to avoid floating-point boundary errors. Every nonmissing wage is assigned to a bin, and percentages sum to 100 within each state/wave. Exact bin edges and tail handling are not given in the original figure, so bar-for-bar identity is not claimed. The large NJ mass around $5.05 after the increase is reproduced. `figure_1_bins.csv` provides the underlying counts and denominators.

## Validation and interpretation

- Input dimensions, state counts, state/sheet uniqueness, closure counts, and the 357-observation regression sample are checked at runtime.
- OLS coefficients are independently compared with NumPy least squares; all agree to numerical precision.
- Original Table 2-4 entries were manually transcribed from complete rendered pages, including footnotes. They are used only in the comparison routine, not as analysis outputs.
- The full workflow is rerun against the original external input and the copied local input; result equivalence and input integrity are checked separately.
- All 186 transcribed numeric entries have explicit published-precision comparisons. These include means, SEs, contrasts, t statistics and regression diagnostics. Counts are descriptive validation metrics, not a grade or a statement that unmatched entries are correct.
- The research comparison supports the paper's finding of no observed relative employment decline in NJ in this sample. Causal interpretation still requires suitable parallel trends and no confounding state-specific shocks. Only one pre-treatment survey is available, so this dataset cannot directly test pre-trends. Questionnaire measurement error, missing observations and the two-state design limit inference. No new robust-inference or extension claim is made.

## Deliverable status

All assigned core tables and the wage-distribution figure have been implemented and generated. Exact numerical identity is **not** achieved for every entry. Discrepancies and source ambiguities remain explicitly recorded. Independent extension, final submission report, student review of the AI-use statement, GitHub hosting and course submission remain later tasks.
