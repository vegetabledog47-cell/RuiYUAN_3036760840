"""Reproduce the assigned Card-Krueger tables from the unmodified course CSV."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import platform
import sys

import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'outputs/tables'
COMPARISONS = []


def compare(table, row, column, actual, original, digits=2, note=''):
    # Paper entries are rounded; a half-unit tolerance allows either rounding convention.
    tol = .5 * 10 ** (-digits) + 1e-10
    COMPARISONS.append(dict(table=table, row=row, column=column, actual=float(actual),
        original=float(original), difference=float(actual-original), digits=digits,
        matches_published_precision=bool(abs(actual-original) <= tol), note=note))


def describe(s):
    s = s.dropna()
    return float(s.mean()), float(s.std(ddof=1)/np.sqrt(len(s))), len(s)


def indicator(s, value):
    return s.eq(value).astype(float).where(s.notna()) * 100


def prepare(path):
    d = pd.read_csv(path)
    assert d.shape == (410, 46), 'Unexpected input dimensions'
    # SHEET 407 occurs in both states: never deduplicate on SHEET alone.
    assert not d[['STATE','SHEET']].duplicated().any(), 'State/sheet keys must be unique'
    d['store_id'] = d.STATE.astype(str)+'_'+d.SHEET.astype(str)
    assert d.STATE.value_counts().to_dict() == {1: 331, 0: 79}
    for suffix in ['', '2']:
        d['fte'+suffix] = d['EMPFT'+suffix] + d['NMGRS'+suffix] + .5*d['EMPPT'+suffix]
        d['fulltime_pct'+suffix] = 100*d['EMPFT'+suffix]/d['fte'+suffix]
        d['meal'+suffix] = d['PSODA'+suffix]+d['PFRY'+suffix]+d['PENTREE'+suffix]
    d.loc[d.STATUS2.eq(3), 'fte2'] = 0
    d.loc[d.STATUS2.isin([2,4,5]), 'fte2'] = np.nan
    d['fte2_temp_zero'] = d.fte2.mask(d.STATUS2.isin([2,4,5]), 0)
    d['delta'] = d.fte2-d.fte
    d['delta_temp_zero'] = d.fte2_temp_zero-d.fte
    d['gap'] = ((5.05-d.WAGE_ST)/d.WAGE_ST).clip(lower=0).where(d.STATE.eq(1), 0)
    d['wage_group'] = np.select([d.WAGE_ST.eq(4.25), d.WAGE_ST.between(4.26,4.99),
                                d.WAGE_ST.ge(5)], ['low','mid','high'], default='missing')
    # Permanent closures have observed zero employment but no meaningful second-wave wage.
    d['table4_sample'] = (d[['fte','fte2','WAGE_ST']].notna().all(axis=1)
                          & (d.WAGE_ST2.notna() | d.STATUS2.eq(3)))
    d['balanced_sample'] = d[['fte','fte2']].notna().all(axis=1)
    assert d.STATUS2.eq(3).sum() == 6
    assert d.STATUS2.isin([2,4,5]).sum() == 4
    assert d.table4_sample.sum() == 357
    return d


def table2(d):
    specs = []
    for chain, name, orig in [(1,'Burger King',[41.1,44.3,-.5]),(2,'KFC',[20.5,15.2,1.2]),
                              (3,'Roy Rogers',[24.8,21.5,.6]),(4,"Wendy's",[13.6,19.0,-1.1])]:
        specs.append(('1',name,indicator(d.CHAIN,chain),orig,None,1))
    specs.append(('1','Company-owned',indicator(d.CO_OWNED,1),[34.1,35.4,-.2],None,1))
    wave1 = [
        ('FTE employment',d.fte,[20.4,23.3,-2.0],[.51,1.35],1),
        ('Percentage full-time employees',d.fulltime_pct,[32.8,35.0,-.7],[1.3,2.7],1),
        ('Starting wage',d.WAGE_ST,[4.61,4.63,-.4],[.02,.04],2),
        ('Wage = 4.25 (percentage)',100*d.WAGE_ST.eq(4.25).astype(float),[30.5,32.9,-.4],[2.5,5.3],1),
        ('Price of full meal',d.meal,[3.35,3.04,4.0],[.04,.07],2),
        ('Hours open (weekday)',d.HRSOPEN,[14.4,14.5,-.3],[.2,.3],1),
        ('Recruiting bonus',indicator(d.BONUS,1),[23.6,29.1,-1.0],[2.3,5.1],1)]
    wave2 = [
        ('FTE employment',d.fte2,[21.0,21.2,-.2],[.52,.94],1),
        ('Percentage full-time employees',d.fulltime_pct2,[35.9,30.4,1.8],[1.4,2.8],1),
        ('Starting wage',d.WAGE_ST2,[5.08,4.62,10.8],[.01,.04],2),
        ('Wage = 4.25 (percentage)',100*d.WAGE_ST2.eq(4.25).astype(float),[.0,25.3,None],[None,4.9],1),
        ('Wage = 5.05 (percentage)',100*d.WAGE_ST2.eq(5.05).astype(float),[85.2,1.3,36.1],[2.0,1.3],1),
        ('Price of full meal',d.meal2,[3.41,3.03,5.0],[.04,.07],2),
        ('Hours open (weekday)',d.HRSOPEN2,[14.4,14.7,-.8],[.2,.3],1),
        ('Recruiting bonus',indicator(d.SPECIAL2,1),[20.3,23.4,-.6],[2.3,4.9],1)]
    specs += [('2',*x) for x in wave1] + [('3',*x) for x in wave2]
    rows = []
    for section,label,s,orig,original_se,digits in specs:
        nj,njse,njn = describe(s[d.STATE.eq(1)])
        pa,pase,pan = describe(s[d.STATE.eq(0)])
        # The published Table 2 uses the unequal-variance mean-difference statistic.
        t = (nj-pa)/np.sqrt(njse**2+pase**2)
        key = section+'. '+label
        rows.append(dict(section=section,variable=label,NJ=nj,NJ_se=njse,NJ_n=njn,
                         PA=pa,PA_se=pase,PA_n=pan,t=t,mean_digits=digits))
        for col,a,o,nd in [('NJ',nj,orig[0],digits),('PA',pa,orig[1],digits),('t',t,orig[2],1)]:
            if o is not None: compare('Table 2',key,col,a,o,nd)
        if original_se:
            se_digits=2 if label in ['FTE employment','Starting wage','Price of full meal'] else 1
            for col,a,o in [('NJ_se',njse,original_se[0]),('PA_se',pase,original_se[1])]:
                if o is not None: compare('Table 2',key,col,a,o,se_digits)
    return pd.DataFrame(rows)


def table3(d):
    groups = {'PA':d.STATE.eq(0),'NJ':d.STATE.eq(1)}
    groups.update({x:d.STATE.eq(1)&d.wage_group.eq(x) for x in ['low','mid','high']})
    orig = np.array([
        [23.33,20.44,-2.89,19.56,20.08,22.25,-2.69,-2.17],
        [21.17,21.03,-.14,20.88,20.96,20.21,.67,.75],
        [-2.16,.59,2.76,1.32,.87,-2.04,3.36,2.91],
        [-2.28,.47,2.75,1.21,.71,-2.16,3.36,2.87],
        [-2.28,.23,2.51,.90,.49,-2.39,3.29,2.88]])
    orig_se=np.array([
        [1.35,.51,1.44,.77,.84,1.14,1.37,1.41],
        [.94,.52,1.07,1.01,.76,1.03,1.44,1.27],
        [1.25,.54,1.36,.95,.84,1.14,1.48,1.41],
        [1.25,.48,1.34,.82,.69,1.01,1.30,1.22],
        [1.25,.49,1.35,.87,.69,1.02,1.34,1.23]])
    rows=[]
    # Row 3: separate-wave means. For its SE, use store-cluster influence functions
    # for the difference of two means, allowing different observed samples.
    for r in range(5):
        values={}
        for g,mask in groups.items():
            a=d.loc[mask]
            if r in [0,1]:
                mean,se,n=describe(a['fte' if r==0 else 'fte2'])
            elif r==2:
                y1,y2=a.fte,a.fte2
                mean=y2.mean()-y1.mean()
                influence=(y2-y2.mean()).fillna(0)/y2.count()-(y1-y1.mean()).fillna(0)/y1.count()
                n=len(a)
                se=float(np.sqrt(np.sum(influence**2)*n/(n-1)))
            else:
                mean,se,n=describe(a['delta' if r==3 else 'delta_temp_zero'])
            values[g]=(mean,se,n)
        for name,left,right in [('NJ-PA','NJ','PA'),('low-high','low','high'),('mid-high','mid','high')]:
            m1,s1,_=values[left]; m0,s0,_=values[right]
            values[name]=(m1-m0,np.sqrt(s1*s1+s0*s0),None)
        for j,g in enumerate(['PA','NJ','NJ-PA','low','mid','high','low-high','mid-high']):
            mean,se,n=values[g]
            rows.append(dict(row=r+1,group=g,estimate=mean,se=se,n=n))
            compare('Table 3',str(r+1),g,mean,orig[r,j])
            compare('Table 3',str(r+1),g+'_se',se,orig_se[r,j],note=(
                'Unequal-sample store-cluster influence SE; original algorithm not reported.' if r==2 else ''))
    return pd.DataFrame(rows)


def table4(d):
    a=d.loc[d.table4_sample].copy()
    for c in [2,3,4]: a['chain'+str(c)]=a.CHAIN.eq(c).astype(float)
    controls=['chain2','chain3','chain4','CO_OWNED']
    regions=['SOUTHJ','CENTRALJ','PA1','PA2'] # North NJ is the reference region.
    # Author check.sas omits ownership in (v), despite the printed table saying
    # chain/ownership controls are included. Following that code reproduces (v).
    specifications=[['STATE'],['STATE']+controls,['gap'],['gap']+controls,
                    ['gap']+controls[:3]+regions]
    original_b=[2.33,2.30,15.65,14.92,11.91]
    original_se=[1.19,1.20,6.08,6.21,7.39]
    original_ser=[8.79,8.78,8.76,8.76,8.75]
    original_p=[None,.34,None,.44,.40]
    rows=[]; coefficients=[]
    for i,cols in enumerate(specifications):
        model=sm.OLS(a.delta,sm.add_constant(a[cols].astype(float))).fit()
        # Check OLS independently against NumPy's least-squares implementation.
        np.testing.assert_allclose(model.params,np.linalg.lstsq(model.model.exog,a.delta,rcond=None)[0],atol=1e-10)
        key=cols[0]; p=np.nan
        if len(cols)>1:
            restriction=np.eye(len(model.params))[2:]
            p=float(model.f_test(restriction).pvalue)
        b=float(model.params[key]); se=float(model.bse[key]); ser=float(np.sqrt(model.mse_resid))
        rows.append(dict(model=i+1,regressor=key,estimate=b,se=se,n=int(model.nobs),
            residual_se=ser,controls_p=p,chain_controls=i in [1,3,4],ownership_control=i in [1,3],region_controls=i==4,
            ci95_lower=float(model.conf_int().loc[key,0]),ci95_upper=float(model.conf_int().loc[key,1])))
        for term in model.params.index:
            coefficients.append(dict(model=i+1,term=term,estimate=float(model.params[term]),
                                     se=float(model.bse[term]),p=float(model.pvalues[term])))
        for col,actual,original in [('estimate',b,original_b[i]),('se',se,original_se[i]),
                                    ('residual_se',ser,original_ser[i]),('controls_p',p,original_p[i])]:
            if original is not None: compare('Table 4',str(i+1),col,actual,original)
    pd.DataFrame(coefficients).to_csv(RESULTS/'table_4_all_coefficients.csv',index=False)
    # Audit the discrepancy between the printed label and the author's code.
    alternative=sm.OLS(a.delta,sm.add_constant(a[['gap']+controls+regions].astype(float))).fit()
    pd.DataFrame([dict(specification='Printed-label interpretation: add ownership to model v',
        estimate=float(alternative.params['gap']),se=float(alternative.bse['gap']),
        n=int(alternative.nobs),residual_se=float(np.sqrt(alternative.mse_resid)))]).to_csv(
        RESULTS/'table_4_model_v_label_audit.csv',index=False)
    return pd.DataFrame(rows)


def figure1(d):
    # Paper does not document exact bin edges/tail handling. Use explicit 10-cent
    # half-open intervals, with the last bin pooling all wages >= $5.50.
    labels=[f'{x/100:.2f}' for x in range(425,556,10)]
    fig,axes=plt.subplots(2,1,figsize=(10,9),layout='constrained')
    rows=[]
    for wave,(ax,col,title) in enumerate(zip(axes,['WAGE_ST','WAGE_ST2'],['February-March 1992','November-December 1992']),1):
        for state,name,offset,color,hatch in [(1,'New Jersey',-.19,'#243b53',None),(0,'Pennsylvania',.19,'white','///')]:
            wages=d.loc[d.STATE.eq(state),col].dropna()
            cents=np.rint(wages*100).astype(int)
            counts=np.histogram(cents,bins=np.r_[np.arange(420,551,10),np.inf])[0]
            pct=100*counts/len(wages)
            assert counts.sum()==len(wages)
            assert abs(pct.sum()-100)<1e-10
            ax.bar(np.arange(len(labels))+offset,pct,width=.36,label=name,color=color,hatch=hatch,
                   edgecolor='#243b53',linewidth=.8)
            rows += [dict(wave=wave,state=name,wage_bin=label,count=int(n),percent=float(p),denominator=len(wages))
                     for label,n,p in zip(labels,counts,pct)]
        ax.set(title=title,ylabel='Percent of stores',ylim=(0,40 if wave==1 else 95))
        ax.set_xticks(np.arange(len(labels)),labels,rotation=45)
        ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
        ax.legend(frameon=False)
    axes[-1].set_xlabel(r'Starting wage bin midpoint (\$); last bin: \$5.50 and above')
    fig.suptitle('Figure 1. Distribution of starting wage rates',fontsize=16)
    fig.savefig(ROOT/'outputs/figures/figure_1.png',dpi=180)
    plt.close(fig)
    pd.DataFrame(rows).to_csv(RESULTS/'figure_1_bins.csv',index=False)


def audit(d,path):
    rows=[]
    for state in [0,1]:
        a=d[d.STATE.eq(state)]
        for label,mask in [('all',pd.Series(True,index=a.index)),('wave1_fte',a.fte.notna()),
                           ('wave2_fte',a.fte2.notna()),('balanced',a.balanced_sample),
                           ('temporary_zero_balanced',a.delta_temp_zero.notna()),('table4',a.table4_sample),
                           ('permanent_closure',a.STATUS2.eq(3)),('temporary_closure',a.STATUS2.isin([2,4,5]))]:
            rows.append(dict(state='NJ' if state else 'PA',sample=label,n=int(mask.sum())))
    pd.DataFrame(rows).to_csv(RESULTS/'sample_audit.csv',index=False)
    manifest={'input_filename':path.name,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'rows':len(d),'columns_raw':46,'python':platform.python_version(),
        'libraries':{x.__name__:x.__version__ for x in [np,pd,scipy,statsmodels,matplotlib]},
        'scope':'Tables 2-4 and Figure 1 only; no independent extension',
        'table4_n':int(d.table4_sample.sum()),'table4_delta_mean':float(d.loc[d.table4_sample,'delta'].mean()),
        'table4_delta_sd':float(d.loc[d.table4_sample,'delta'].std())}
    (RESULTS/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')


def viewer(t2,t3,t4,comparison):
    styles='body{font:16px/1.6 system-ui;max-width:1150px;margin:40px auto;padding:0 24px;color:#243b53}table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}th,td{padding:8px;border-bottom:1px solid #d9e2ec;text-align:right}th:first-child,td:first-child{text-align:left}h1,h2{color:#102a43}img{max-width:100%}.note{background:#f0f4f8;padding:18px}a{color:#1261a0}'
    def tab(x): return x.to_html(index=False,float_format=lambda n:f'{n:.4f}',border=0)
    display2=t2[['section','variable','NJ','NJ_se','NJ_n','PA','PA_se','PA_n','t']]
    display3=t3.pivot(index='row',columns='group',values='estimate').reindex(columns=['PA','NJ','NJ-PA','low','mid','high','low-high','mid-high']).reset_index()
    se3=t3.pivot(index='row',columns='group',values='se').reindex(columns=['PA','NJ','NJ-PA','low','mid','high','low-high','mid-high']).reset_index()
    discrepancies=comparison[~comparison.matches_published_precision]
    content=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Card-Krueger core replication</title><style>{styles}</style>
    <h1>Card &amp; Krueger (1994): core replication</h1>
    <p>Tables 2-4 and Figure 1. Original input: 410 restaurants; regression sample: 357.</p>
    <div class="note">This page displays the core replication. The ownership extension and complete discussion are in
    <a href="../../report.pdf">the final report</a> and <a href="extension_primary.csv">the extension table</a>.
    All displayed results are computed from the supplied CSV.
    Published values are used only for comparison, never to replace computed results.
    See <a href="../../report.md">the report source</a> for definitions and discrepancies.</div>
    <h2>Table 2. Means of key variables</h2>{tab(display2)}
    <p>Section 1: store types; section 2: wave 1; section 3: wave 2. Percentages are in percentage points.</p>
    <h2>Table 3. Employment levels and changes</h2>{tab(display3)}
    <p>Rows: 1 before; 2 after; 3 separate-wave difference; 4 paired-store difference; 5 temporary closures set to zero.
    Low/mid/high: NJ baseline wage $4.25 / $4.26-$4.99 / at least $5.00.</p>
    <h3>Table 3 standard errors</h3>{tab(se3)}
    <h2>Table 4. Change in FTE employment</h2>{tab(t4)}
    <p>Conventional OLS standard errors, as in the original table. Controls p: joint F test excluding all added controls.
    Model (v) follows the author's public SAS code and omits ownership, despite the published combined controls label.</p>
    <h2>Figure 1. Starting wages</h2><img src="../figures/figure_1.png" alt="Wage distributions by state and survey wave">
    <p>Explicit ten-cent bins and top-coded tail; the original publication does not specify exact bin edges.
    The broad distribution is reproduced; pixel-level/bar-level identity is not claimed.</p>
    <h2>Comparison with the published tables</h2>
    <p>{int(comparison.matches_published_precision.sum())} / {len(comparison)} entries fall within the original displayed rounding interval.
    Differences outside that interval appear below; all comparisons are in <a href="comparison.csv">comparison.csv</a>.</p>
    {tab(discrepancies)}<h2>Audit</h2>{tab(pd.read_csv(RESULTS/'sample_audit.csv'))}
    <p>Source: Card and Krueger (1994), American Economic Review 84(4), pp. 772-793; course Package 01.</p></html>'''
    (RESULTS/'replication_results.html').write_text(content,encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'01_DID'/'data'/'public.csv')
    args=parser.parse_args()
    if not args.input.is_file():
        parser.error('Place the course CSV at 01_DID/data/public.csv, or pass --input PATH.')
    RESULTS.mkdir(parents=True,exist_ok=True)
    (ROOT/'outputs/figures').mkdir(parents=True,exist_ok=True)
    d=prepare(args.input)
    processed=ROOT/'data'/'processed'; processed.mkdir(parents=True,exist_ok=True)
    d.to_csv(processed/'analysis_sample.csv',index=False)
    t2,t3,t4=table2(d),table3(d),table4(d)
    for name,t in [('table_2',t2),('table_3',t3),('table_4',t4)]: t.to_csv(RESULTS/(name+'.csv'),index=False)
    figure1(d); audit(d,args.input)
    comparison=pd.DataFrame(COMPARISONS)
    comparison.to_csv(RESULTS/'comparison.csv',index=False)
    viewer(t2,t3,t4,comparison)
    print(t4.to_string(index=False))
    print('\nPublished precision matches:',int(comparison.matches_published_precision.sum()),'/',len(comparison))
    print('\nDiscrepancies:\n',comparison[~comparison.matches_published_precision].to_string(index=False))
    print('\nResults:',RESULTS)


if __name__=='__main__': main()
