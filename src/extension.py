"""Ownership heterogeneity extension, specified before examining robustness results."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'


def fit_model(a, controls, outcome='delta'):
    a=a.dropna(subset=[outcome,'STATE','CO_OWNED']+controls).copy()
    x=a[['STATE','CO_OWNED']].astype(float).copy()
    x['NJ_owned']=x.STATE*x.CO_OWNED
    if 'CHAIN' in controls:
        x=pd.concat([x,pd.get_dummies(a.CHAIN,prefix='chain',drop_first=True,dtype=float)],axis=1)
    for control in controls:
        if control!='CHAIN': x[control]=a[control].astype(float)
    x=sm.add_constant(x)
    ols=sm.OLS(a[outcome],x).fit()
    robust=ols.get_robustcov_results(cov_type='HC3',use_t=True)
    # Independently compute HC3 from its sandwich formula.
    design=np.asarray(x)
    inv=np.linalg.inv(design.T@design)
    leverage=np.einsum('ij,jk,ik->i',design,inv,design)
    adjusted=np.asarray(ols.resid)/(1-leverage)
    sandwich=inv@(design.T@(design*adjusted[:,None]**2))@inv
    np.testing.assert_allclose(sandwich,robust.cov_params(),rtol=1e-10,atol=1e-10)
    rows=[]
    for contrast, terms in [('Franchise DiD',{'STATE':1}),('Company owned DiD',{'STATE':1,'NJ_owned':1}),
                             ('Ownership difference',{'NJ_owned':1})]:
        weights=np.array([terms.get(name,0) for name in x.columns])
        test=robust.t_test(weights)
        ci=np.asarray(test.conf_int())[0]
        rows.append(dict(contrast=contrast,estimate=float(np.asarray(test.effect).item()),
            se=float(np.asarray(test.sd).item()),p=float(np.asarray(test.pvalue).item()),
            ci95_lower=float(ci[0]),ci95_upper=float(ci[1]),n=len(a),df_resid=int(robust.df_resid)))
    coefficients=pd.DataFrame(dict(term=x.columns,estimate=robust.params,se=robust.bse,p=robust.pvalues,
        conventional_se=ols.bse.to_numpy(),conventional_p=ols.pvalues.to_numpy()))
    return rows,coefficients,a


def main():
    d=pd.read_csv(ROOT/'data/processed/analysis_sample.csv')
    a=d.loc[d.balanced_sample].copy()
    cells=a.groupby(['STATE','CO_OWNED']).agg(n=('delta','size'),fte_before=('fte','mean'),
        fte_after=('fte2','mean'),delta=('delta','mean'),delta_sd=('delta','std'),
        baseline_wage=('WAGE_ST','mean'),baseline_wage_n=('WAGE_ST','count'),gap=('gap','mean')).reset_index()
    cells['state']=cells.STATE.map({0:'PA',1:'NJ'})
    cells['ownership']=cells.CO_OWNED.map({0:'Franchise',1:'Company owned'})
    cells.to_csv(RESULTS/'extension_cells.csv',index=False)
    # Baseline characteristics and observation rates expose group composition.
    composition=d.groupby(['STATE','CO_OWNED']).agg(raw_n=('SHEET','size'),
        paired_n=('balanced_sample','sum'),baseline_fte=('fte','mean'),baseline_wage=('WAGE_ST','mean'),
        permanent_closed=('STATUS2',lambda s:s.eq(3).sum())).reset_index()
    composition['paired_rate']=composition.paired_n/composition.raw_n
    composition.to_csv(RESULTS/'extension_composition.csv',index=False)
    specs=[('Unadjusted',a,[],'delta'),
        ('Primary chain controls',a,['CHAIN'],'delta'),
        ('Add baseline employment',a,['CHAIN','fte'],'delta'),
        ('Add baseline employment and wage',a,['CHAIN','fte','WAGE_ST'],'delta'),
        ('Exclude permanent closures',a.loc[a.STATUS2.ne(3)],['CHAIN'],'delta'),
        ('Temporary closures employment zero',d.loc[d.delta_temp_zero.notna()],['CHAIN'],'delta_temp_zero')]
    allrows=[]
    for label,sample,controls,outcome in specs:
        rows,coefs,used=fit_model(sample,controls,outcome)
        for row in rows: row['specification']=label
        allrows.extend(rows)
        if label=='Primary chain controls':
            coefs.to_csv(RESULTS/'extension_coefficients.csv',index=False)
            primary=pd.DataFrame(rows)
        if label=='Unadjusted':
            cell=cells.set_index(['STATE','CO_OWNED']).delta
            raw_interaction=(cell[1,1]-cell[0,1])-(cell[1,0]-cell[0,0])
            np.testing.assert_allclose(rows[2]['estimate'],raw_interaction,atol=1e-12)
    full=pd.DataFrame(allrows)
    full.to_csv(RESULTS/'extension_models.csv',index=False)
    primary.to_csv(RESULTS/'extension_primary.csv',index=False)
    sensitivity=full[full.contrast.eq('Ownership difference')].copy()
    sensitivity.to_csv(RESULTS/'extension_sensitivity.csv',index=False)
    # Each dot and interval is a prespecified regression contrast, not separate fits.
    fig,ax=plt.subplots(figsize=(9.4,4.0),layout='constrained')
    ypos=np.arange(len(primary))[::-1]
    ax.errorbar(primary.estimate,ypos,xerr=np.vstack([primary.estimate-primary.ci95_lower,
        primary.ci95_upper-primary.estimate]),fmt='o',capsize=5,color='#243b53')
    ax.set_yticks(ypos,['Franchise DiD','Company owned DiD','Company owned minus franchise'])
    ax.axvline(0,color='#7b8794',linestyle='--',linewidth=1)
    ax.set_xlabel('Change in FTE employees relative to PA (95% HC3 intervals)')
    ax.set_title('Ownership heterogeneity after the minimum wage increase',loc='left',fontsize=13)
    ax.grid(axis='x',alpha=.2)
    fig.savefig(RESULTS/'extension_ownership.png',dpi=180)
    plt.close(fig)
    summary={'question':'Does the NJ-versus-PA employment change differ between company-owned and franchise restaurants?',
        'primary_sample_n':len(a),'covariance':'HC3, t reference with residual degrees of freedom',
        'primary_controls':['chain dummies'],'within_state_shock_clustering':False,
        'warning':'Only two states; HC3 does not allow arbitrary correlated state-level policy shocks.',
        'independent_HC3_matrix_check':True,'unadjusted_DDD_identity_check':True,
        'multiple_testing':'One primary ownership-interaction test; five alternative specifications are sensitivity checks, not independent discoveries.',
        'primary':primary.to_dict(orient='records'),
        'interaction_sensitivity_range':[float(sensitivity.estimate.min()),float(sensitivity.estimate.max())],
        'all_sensitivity_interaction_intervals_include_zero':bool(((sensitivity.ci95_lower<0)&(sensitivity.ci95_upper>0)).all())}
    (RESULTS/'extension_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(full[['specification','contrast','estimate','se','p','n']].to_string(index=False))


if __name__=='__main__': main()
