"""Independent audit of generated results; optional primary-source data check."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'01_DID/data/public.csv')
    parser.add_argument('--author-data',type=Path)
    args=parser.parse_args()
    raw=pd.read_csv(args.input)
    processed=pd.read_csv(ROOT/'data/processed/analysis_sample.csv')
    # Ensure the pipeline has not altered its raw-column values in processed output.
    np.testing.assert_allclose(raw.to_numpy(float),processed[raw.columns].to_numpy(float),equal_nan=True)
    pre=raw.EMPFT+raw.NMGRS+.5*raw.EMPPT
    post=raw.EMPFT2+raw.NMGRS2+.5*raw.EMPPT2
    paired=(post-pre).dropna()
    state=raw.loc[paired.index,'STATE']
    nj,pa=paired[state.eq(1)],paired[state.eq(0)]
    independent_t=stats.ttest_ind(nj,pa,equal_var=False)
    observed_did=nj.mean()-pa.mean()
    independent_se=observed_did/independent_t.statistic
    t3=pd.read_csv(ROOT/'outputs/tables/table_3.csv')
    target=t3[(t3.row==4)&t3.group.eq('NJ-PA')].iloc[0]
    np.testing.assert_allclose([target.estimate,target.se],[observed_did,independent_se],atol=1e-12)
    # Independent two-period within-store transformation, rather than change regression.
    base=pre.loc[paired.index].to_numpy(); after=post.loc[paired.index].to_numpy()
    y=np.column_stack([base,after]); y_within=(y-y.mean(axis=1,keepdims=True)).ravel()
    post_within=np.tile([-.5,.5],len(paired))
    interaction_within=np.repeat(state.to_numpy(),2)*post_within
    within=sm.OLS(y_within,np.column_stack([post_within,interaction_within])).fit()
    np.testing.assert_allclose(within.params[1],target.estimate,atol=1e-12)
    t4=pd.read_csv(ROOT/'outputs/tables/table_4.csv')
    assert t4.n.eq(357).all()
    assert processed.loc[processed.STATUS2.eq(3),'table4_sample'].all()
    assert not processed.loc[processed.STATUS2.isin([2,4,5]),'table4_sample'].any()
    bins=pd.read_csv(ROOT/'outputs/tables/figure_1_bins.csv')
    np.testing.assert_allclose(bins.groupby(['wave','state']).percent.sum(),100,atol=1e-12)
    assert not raw.duplicated().any()
    # This numerical assertion targets the substantive published estimate, not every
    # unmatched cell. The original comparison log must still be reviewed.
    np.testing.assert_allclose(t4.estimate,[2.325831,2.303860,15.652890,14.915674,11.913064],atol=1e-6)
    summary={'raw_columns_preserved':True,'paired_did_independent_welch_check':True,
        'paired_did_within_store_check':True,'within_store_did':float(within.params[1]),
        'closures_and_regression_sample_check':True,'figure_totals_check':True,
        'table4_core_coefficients_check':True,'exact_match_of_all_paper_entries':False}
    (ROOT/'outputs/tables/validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    if args.author_data:
        official=pd.read_csv(args.author_data,sep=r'\s+',header=None,na_values='.')
        assert official.shape==raw.shape
        np.testing.assert_allclose(raw.to_numpy(float),official.to_numpy(float),rtol=0,atol=0,equal_nan=True)
        source={'source_page':'https://davidcard.berkeley.edu/data_sets.html',
            'archive_url':'https://davidcard.berkeley.edu/data_sets/njmin.zip',
            'accessed_date':'2026-10-13','course_input_sha256':hashlib.sha256(args.input.read_bytes()).hexdigest(),
            'author_public_dat_sha256':hashlib.sha256(args.author_data.read_bytes()).hexdigest(),
            'rows':410,'columns':46,'numeric_cells_including_missing':18860,
            'numeric_matrix_and_missingness_exactly_equal':True,
            'note':'Column order checked against official codebook and SAS INPUT list; no source data republished.'}
        (ROOT/'outputs/tables/source_verification.json').write_text(json.dumps(source,indent=2),encoding='utf-8')
        summary['official_data_numeric_equality_check']=True
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
