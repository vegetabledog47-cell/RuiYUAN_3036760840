"""Create the submission report and its editable Markdown from computed results."""
from pathlib import Path
import json
import re
from xml.sax.saxutils import escape
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'outputs/tables'
WIDTH=A4[0]-108
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle',fontName='Times-Bold',fontSize=21,leading=25,spaceAfter=14,textColor=colors.black))
styles.add(ParagraphStyle(name='ReportBody',fontName='Times-Roman',fontSize=10.5,leading=14,spaceAfter=8,textColor=colors.black))
styles.add(ParagraphStyle(name='ReportHeading',fontName='Times-Bold',fontSize=14,leading=18,spaceAfter=11,textColor=colors.black))
styles.add(ParagraphStyle(name='ReportSub',fontName='Times-Bold',fontSize=11,leading=14,spaceBefore=7,spaceAfter=6,textColor=colors.black))
styles.add(ParagraphStyle(name='ReportNote',fontName='Times-Roman',fontSize=9,leading=12,spaceAfter=7,textColor=colors.black))
styles.add(ParagraphStyle(name='ReportCell',fontName='Helvetica',fontSize=8.1,leading=10.6,textColor=colors.black))
styles.add(ParagraphStyle(name='ReportCellSmall',fontName='Helvetica',fontSize=7.2,leading=9.2,textColor=colors.black))
styles.add(ParagraphStyle(name='ReportCenter',fontName='Times-Roman',fontSize=11,leading=15,alignment=TA_CENTER,spaceAfter=12,textColor=colors.black))


def fmt(x, digits=2):
    return f'{x:.{digits}f}'


def main():
    info=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
    t2=pd.read_csv(RES/'table_2.csv'); t3=pd.read_csv(RES/'table_3.csv'); t4=pd.read_csv(RES/'table_4.csv')
    cells=pd.read_csv(RES/'extension_cells.csv'); ext=pd.read_csv(RES/'extension_primary.csv')
    sens=pd.read_csv(RES/'extension_sensitivity.csv'); comp=pd.read_csv(RES/'extension_composition.csv')
    comparisons=pd.read_csv(RES/'comparison.csv'); audit=pd.read_csv(RES/'sample_audit.csv')
    story=[]; md=[]
    def p(text,note=False):
        story.append(Paragraph(escape(text),styles['ReportNote' if note else 'ReportBody']))
        md.append(text+'\n')
    def h(text,sub=False):
        story.append(Paragraph(escape(text),styles['ReportSub' if sub else 'ReportHeading']))
        md.append(('### ' if sub else '## ')+text+'\n')
    def page():
        story.append(PageBreak()); md.append('\n---\n')
    def table(title,headers,rows,widths,small=False):
        story.append(Paragraph(escape(title),styles['ReportSub']))
        md.append('### '+title+'\n')
        st=styles['ReportCellSmall' if small else 'ReportCell']
        centered=ParagraphStyle('CenteredCell',parent=st,alignment=TA_CENTER)
        def cell(value,j):
            text=str(value)
            numeric=(j>0 and (re.match(r'^[\d\-\[\(]',text) or text in ['Yes','No']))
            return Paragraph(escape(text).replace('\n','<br/>'),centered if numeric else st)
        data=[[Paragraph(escape(str(x)).replace('\n','<br/>'),st) for x in headers]]
        data += [[cell(x,j) for j,x in enumerate(row)] for row in rows]
        tab=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        tab.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dbe5ef')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f6f7')]),
            ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d9d9d9')),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.extend([tab,Spacer(1,9)])
        md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |')
        md.extend('| '+' | '.join(str(x).replace('\n',' ') for x in row)+' |' for row in rows)
        md.append('')
    def picture(name,width):
        from PIL import Image as PILImage
        with PILImage.open(ROOT/'outputs/figures'/name) as im: w,ht=im.size
        story.append(Image(str(ROOT/'outputs/figures'/name),width=width,height=width*ht/w))
        story.append(Spacer(1,8)); md.append(f'![{name}](outputs/figures/{name})\n')

    title='Minimum Wage and Employment in Fast Food Restaurants'
    story.append(Paragraph(title,styles['ReportTitle']))
    md.append('# '+title+'\n')
    p('Replication of Card and Krueger 1994 and an ownership heterogeneity extension')
    p(f"{info['author']} | Student ID {info['student_id']} | {info['course']} | {info['date']}")
    h('Abstract')
    p('This project reproduces the assigned descriptive statistics, employment comparisons, reduced-form regressions and starting-wage distributions from Card and Krueger (1994). The input contains 410 fast-food restaurants in New Jersey and Pennsylvania surveyed around New Jersey\'s 1992 minimum-wage increase. In the 384-store paired employment sample, the difference-in-differences estimate is 2.75 full-time-equivalent employees, with a standard error of 1.34. The 357-store wage-screened regressions reproduce all five published treatment coefficients and their standard errors to displayed precision under the documented author-code interpretation. Some other printed entries remain unmatched, including unbalanced-sample standard errors and internally inconsistent model-v diagnostics. An independent extension tests whether the employment comparison differs by ownership. With chain controls, the company-owned-minus-franchise difference is -1.14 FTE, with a 95% HC3 interval of [-5.90, 3.62] and p = 0.637. Its sign changes when baseline employment is controlled. The sample does not provide precise evidence of ownership heterogeneity; this is not evidence of equivalence. A documented pipeline regenerates the results and this report from the input CSV.')
    h('1 Research question and motivation')
    p('Card and Krueger (1994) ask whether a higher minimum wage reduces employment in fast-food restaurants. On April 1, 1992, New Jersey increased its minimum wage from $4.25 to $5.05, while Pennsylvania retained $4.25. In a competitive labor-demand framework, a binding wage floor can reduce demand for labor. The paper uses the policy difference across neighboring areas to evaluate this prediction empirically, rather than assuming the sign of the response.')
    p('The original comparison is valuable because employment can change during a recession even without a policy change. A before-and-after comparison in New Jersey alone would mix policy effects with these changes. Comparing its employment change with eastern Pennsylvania attempts to remove common changes. This project first reconstructs the assigned results, then asks whether organizational form is associated with a different response. Ownership is recorded before the follow-up survey and is already available in the original data.')
    h('1 1 Data provenance and sample',sub=True)
    p('The main input is the course Package 01 public.csv, with 410 observations and 46 original fields. I also obtained David Card\'s public archive independently for source verification: every numeric value and missing entry in its public.dat equals the course CSV. The original paper and public codebook were inspected. The primary input remains the documented course CSV; independent source verification is not presented as a different dataset or as WRDS data collection.')

    page(); h('2 Data construction and empirical design')
    p('The sample covers Burger King, KFC, Roy Rogers and Wendy\'s. The baseline survey took place in February-March 1992 and follow-up in November-December 1992. New Jersey has 331 sampled restaurants and Pennsylvania 79. Variable-specific missing observations are retained in the master file and excluded only from the statistic that requires them. SHEET 407 occurs in both states for different restaurants, so the working identifier combines STATE and SHEET.')
    p('FTE = EMPFT + NMGRS + 0.5 x EMPPT. Managers receive full weight, and a missing component is not treated as zero. Six permanently closed restaurants have zero follow-up employment. Four temporary closures have missing baseline-specification follow-up employment; only the designated alternative in Table 3 sets them to zero. Full-time percentage is 100 x EMPFT/FTE, as in the author\'s SAS program. Meal price sums soda, fries and entree only when all three are observed. Prices already include tax.')
    rows=[]
    labels={'all':'Original stores','wave1_fte':'Observed baseline FTE','wave2_fte':'Observed follow-up FTE',
        'balanced':'Paired employment sample','temporary_zero_balanced':'Paired sample with temporary closures zero','table4':'Table 4 wage-screened sample',
        'permanent_closure':'Permanent closures','temporary_closure':'Temporary closures'}
    for key,label in labels.items():
        vals=audit[audit['sample'].eq(key)].set_index('state').n
        rows.append([label,str(vals['NJ']),str(vals['PA']),str(vals.sum())])
    table('Sample accounting',['Sample','NJ','PA','Total'],rows,[WIDTH-150,50,50,50])
    p('Table 4 requires employment in both waves and starting wages in both waves, with a permanent-closure exception for the follow-up wage. It retains 357 stores, including all six permanent closures. Mean employment change is -0.237535 and its sample SD is 8.825485, matching the published sample description. The ownership extension instead uses all 384 paired employment observations and does not screen on follow-up wages.')
    h('Identification and estimands',sub=True)
    p('DiD = (mean FTE after - mean FTE before in NJ) - (mean FTE after - mean FTE before in PA). For a causal interpretation, untreated employment changes must be comparable across the two states, with no confounding differential shock, relevant spillover or selection change. The sample has one pre-policy survey, so a pre-trend test is not available. Results concern initially sampled restaurants, not employment created through new restaurant entry.')
    p('The regression outcome is store-level change in FTE. GAP equals max[(5.05 - baseline wage)/baseline wage, 0] in NJ and zero in PA. NJ/GAP models have an intercept; additional specifications include chain indicators, ownership and regions. Historical table replication uses conventional OLS errors. The extension uses HC3 errors with residual-degree-of-freedom t intervals. These errors address restaurant-level heteroskedasticity, not arbitrary state-level policy shocks.')

    page(); h('3 Core replication results')
    h('3 1 Means of key variables',sub=True)
    rows=[]
    for _,r in t2.iterrows():
        digits=int(r.mean_digits); label=r.variable
        if r.section==1: nj=fmt(r.NJ,digits); pa=fmt(r.PA,digits)
        else:
            sed=2 if label in ['FTE employment','Starting wage','Price of full meal'] else 1
            nj=fmt(r.NJ,digits)+'\n('+fmt(r.NJ_se,sed)+')'
            pa=fmt(r.PA,digits)+'\n('+fmt(r.PA_se,sed)+')'
        rows.append([str(int(r.section)),label,nj,pa,fmt(r.t,1)])
    table('Table 2  Means of key variables',['Part','Variable','NJ','PA','t NJ minus PA'],rows,
        [30,WIDTH-234,74,74,56],small=True)
    p('Part 1: store type percentages; part 2: baseline; part 3: follow-up. Parentheses contain sample mean standard errors. Employment is FTE, wages and meal prices are dollars, and bonus/wage-point indicators are percentages. NJ-minus-PA t uses separate group variances. The script also computes t where the original displays a dash. Variable-specific denominators are in table_2.csv.',note=True)
    p('Wage-point percentages use all sampled stores in each state as the denominator, consistent with the author\'s equality indicators, while wage means use observed wages. NJ\'s baseline $4.25 count is 101: 101/331 = 30.5%, compared with 101/314 = 32.2% among nonmissing wages. The follow-up $5.05 count is 283 in the supplied and author data, giving 85.5%, versus 85.2% printed. Excluding a reported wage at one renovation closure would explain this count difference, but is not an established original rule and is not imposed here.',note=True)

    page(); h('3 2 Employment levels and changes')
    rows=[]
    for r in range(1,6):
        sub=t3[t3.row.eq(r)].set_index('group')
        labels3=['Before','After','Separate means change','Paired change','Temporary closures zero']
        rows.append([str(r)+' '+labels3[r-1]]+[fmt(sub.loc[g,'estimate'])+'\n('+fmt(sub.loc[g,'se'])+')'
            for g in ['PA','NJ','NJ-PA','low','mid','high','low-high','mid-high']])
    table('Table 3  Average employment before and after',['Row','PA','NJ','NJ minus PA','NJ low','NJ mid','NJ high','Low minus high','Mid minus high'],
        rows,[103]+[(WIDTH-103)/8]*8,small=True)
    p('Parentheses contain standard errors. Low/mid/high NJ groups have baseline wages of $4.25 / $4.26-$4.99 / at least $5.00. Group membership counts are 101 / 140 / 73, but each employment mean has its own observed count. All contrasts are computed from unrounded inputs.',note=True)
    p('The paired comparison reproduces 2.75 FTE (SE 1.34). PA paired stores lose 2.28 FTE on average while NJ paired stores gain 0.47. Setting temporary-closure employment to zero lowers the DiD to 2.51 (SE 1.35). This accounting choice is economically meaningful because a closed store still belongs to the original cohort. It does not overturn the relative employment pattern in these data.')
    p('The initial low-wage versus high-wage NJ comparison also reproduces the paper\'s qualitative pattern: the low-wage group has a larger employment increase. This is part of the assigned replication, not the independent extension. High baseline wages can reflect different restaurant characteristics, so the contrast is not automatically an experiment within NJ.')
    h('Unbalanced change standard errors',sub=True)
    p('Row 3 subtracts separate-wave means, rather than averaging only paired changes. Its sampling variance depends on within-store covariance and which observations are present in each wave. The publication does not specify enough detail to recover all its row-3 errors, and the public SAS summarizes only part of Table 3. I use a store-level influence-function estimator, allowing the two observed samples to differ:')
    p('z_i = I(after observed) x (after_i - mean_after)/n_after - I(before observed) x (before_i - mean_before)/n_before; SE = sqrt{N/(N-1) x sum_i z_i squared}. Missing contributions are zero; N is the original store count in the group.')
    p('This gives row-3 NJ SE = 0.47215 versus printed 0.54, and PA SE = 1.22199 versus 1.25. The row-3 between-state SE is 1.31003 versus 1.36. These are disclosed alternative variance estimates, not exact reproduction. Several other point estimates differ by roughly 0.005-0.008 FTE at the final displayed digit. No computed result is replaced with a copied paper value. Appendix A lists every comparison outside the published rounding interval.')

    page(); h('3 3 Reduced form employment regressions')
    headers=['Independent variable or statistic','i','ii','iii','iv','v']
    rows=[['NJ indicator']+[fmt(t4.iloc[i].estimate)+'\n('+fmt(t4.iloc[i].se)+')' if i<2 else '-' for i in range(5)],
          ['Initial wage GAP']+['-' if i<2 else fmt(t4.iloc[i].estimate)+'\n('+fmt(t4.iloc[i].se)+')' for i in range(5)],
          ['Chain controls','No','Yes','No','Yes','Yes'],
          ['Ownership control','No','Yes','No','Yes','No'],
          ['Region controls','No','No','No','No','Yes'],
          ['Residual standard error']+[fmt(x) for x in t4.residual_se],
          ['Joint controls F test p']+['-' if pd.isna(x) else fmt(x) for x in t4.controls_p],
          ['Observations']+[str(int(x)) for x in t4.n]]
    table('Table 4  Change in FTE employment',headers,rows,[WIDTH-275]+[55]*5)
    p('All models include an intercept. Standard errors in parentheses are conventional OLS errors. Model v follows the author\'s public SAS implementation; its ownership setting differs from the combined control label in the printed paper. Chain and region reference categories do not affect fitted treatment coefficients. The joint test excludes NJ/GAP and the intercept.',note=True)
    p('Models i-iv reproduce the displayed treatment coefficients, standard errors and reported controls diagnostics. The simple state coefficient is 2.3258 with SE 1.1916. Its 95% interval is [-0.0176, 4.6693], so the positive estimate should not be described as conclusive evidence of an employment increase at the two-sided 5% level. GAP is positively associated with employment change in models iii and iv. Because GAP is a proportion, its coefficient is not an effect per dollar of wages.')
    h('Source inconsistency in model v',sub=True)
    p('The printed table says chain and ownership controls are included. The public author command for the level-change model contains GAP, three chain indicators, CENTRALJ, SOUTHJ, PA1 and PA2, omitting CO_OWNED. That command gives GAP = 11.9131 and SE = 7.3944, matching printed 11.91 (7.39), but residual SE = 8.7402 and joint-controls p = 0.3075, rather than printed 8.75 and 0.40.')
    p('Adding ownership instead gives GAP = 11.9792 (SE 7.4191), residual SE = 8.7525 and joint-controls p = 0.4046. Thus two coherent specifications align with different parts of the printed column. The principal replication follows the author command and preserves the alternative in table_4_model_v_label_audit.csv. It does not combine a coefficient from one regression with diagnostics from another. The archive accompanies the survey data used in Myth and Measurement and is a primary implementation cross-check, not proof of the exact AER production program.')
    p(f"Across Tables 2-4, {int(comparisons.matches_published_precision.sum())} of {len(comparisons)} transcribed numeric entries fall in their printed rounding intervals. This count includes coefficients, means, errors, contrasts and diagnostics; it is an audit measure, not an estimate of scientific validity. Remaining differences are not all attributed to rounding.")

    page(); h('3 4 Starting wage distributions')
    picture('figure_1.png',WIDTH)
    p('Figure 1  Distribution of starting wages by state and survey wave. Each state-wave denominator is its number of observed wages. Bars use half-open ten-cent bins from [4.20, 4.30) through [5.40, 5.50), with wages at least $5.50 pooled in the last bar. Integer cents avoid floating-point boundary errors.',note=True)
    p('The broad original pattern is reproduced: before the policy, both states have substantial mass near $4.25 and other wage points; after the policy, NJ wages concentrate near $5.05 while PA retains a wider distribution including the old minimum. The original figure does not document exact bin edges or tail treatment, so bar-for-bar identity is not claimed. All nonmissing wages are included, and percentages sum to 100 within every state-wave group. Underlying counts are supplied in figure_1_bins.csv.')

    page(); h('4 Independent extension on restaurant ownership')
    h('4 1 Economic question and design',sub=True)
    p('Does the NJ-versus-PA employment change differ between company-owned restaurants and franchise restaurants? Ownership could matter if corporate stores can share resources across outlets or implement common staffing policies, while franchise operators make more local decisions. Conversely, centralized cost control could produce larger corporate staffing reductions. These are competing hypotheses, not mechanisms established by these data. A two-sided ownership interaction is therefore the primary test.')
    p('The extension goes beyond including ownership as a common control in the original regressions. It allows the NJ employment comparison itself to differ by ownership. Let O_i denote company ownership. The primary model is:')
    p('Change in FTE_i = a + b x NJ_i + c x O_i + d x (NJ_i x O_i) + chain controls + error_i.')
    p('Here b is the franchise NJ-minus-PA change, b+d is the company-owned change, and d is the difference between those two comparisons. In an equivalent two-period level model, d corresponds to the NJ x post x ownership interaction, with the required lower-order terms. Ownership is held at its recorded store characteristic. The model uses 384 paired employment stores and three chain indicators; no follow-up wage filter or outcome-driven subgroup threshold is introduced.')
    rows=[[r.state,r.ownership,str(int(r.n)),fmt(r.fte_before),fmt(r.fte_after),fmt(r.delta),fmt(r.baseline_wage)] for _,r in cells.iterrows()]
    table('Table 5  Paired sample by state and ownership',['State','Ownership','N','Before FTE','After FTE','Change FTE','Baseline wage'],
        rows,[38,113,35,64,64,69,WIDTH-383])
    p('The PA company-owned comparison group has only 26 stores. Baseline composition differs: PA franchises average 26.01 FTE and $4.51 in wages, while PA corporate stores average 18.43 FTE and $4.86 among observed wages. These differences motivate sensitivity checks with baseline employment and wages, rather than interpreting ownership as randomly assigned. The paired observation rates also range from 92.2% to 96.1% across groups; detailed counts are in extension_composition.csv.')
    h('Inference and identifying assumptions',sub=True)
    p('The primary ownership-difference test uses HC3 heteroskedasticity-consistent covariance and residual-df t inference. HC3 adjusts squared residual contributions for observation leverage (MacKinnon and White, 1985; statsmodels documentation). The company-owned contrast uses the full covariance of b and d, not the sum of their SEs. The unadjusted interaction is independently checked against the four-cell difference, and the HC3 matrix is checked against a direct sandwich calculation.')
    p('A causal ownership contrast requires comparable untreated NJ-minus-PA trends across ownership types, and no ownership-specific confounding shock. With two states and one pre-period these assumptions cannot be verified. State-cluster inference with only two clusters would not solve this problem. The reported HC3 intervals are conditional restaurant-level uncertainty and may understate uncertainty from common state shocks.')

    page(); h('4 2 Extension estimates')
    rows=[[r.contrast,fmt(r.estimate),fmt(r.se),f'[{r.ci95_lower:.2f}, {r.ci95_upper:.2f}]',fmt(r.p,3)] for _,r in ext.iterrows()]
    table('Table 6  Primary ownership contrasts',['Contrast','Estimate','HC3 SE','95 percent interval','p value'],rows,[WIDTH-265,58,58,94,55])
    p('Sample N = 384; residual degrees of freedom = 377. All contrasts come from the same chain-controlled regression. The ownership difference is company-owned DiD minus franchise DiD. Full coefficients and conventional-OLS inference are in extension_coefficients.csv.',note=True)
    picture('extension_ownership.png',WIDTH)
    p('Figure 2  Estimated employment contrasts with 95% HC3 intervals. Zero is included in all three intervals.',note=True)
    p('The estimated franchise DiD is 3.18 FTE and the company-owned DiD 2.04. The difference is -1.14 FTE, SE 2.42, with p = 0.637 and interval [-5.90, 3.62]. The data therefore do not reject equal ownership-specific comparisons. They also allow economically meaningful differences in either direction. Failure to reject is not evidence that the effects are equal or that ownership is irrelevant.')
    p('The descriptive four-cell ownership difference without chain controls is -1.10 FTE. Its proximity to the primary estimate suggests that the chain controls alone do not explain the initial point estimate. However, ownership groups differ in initial employment and wages, and the next section shows that conditioning on those initial characteristics changes the direction of the estimated difference.')

    page(); h('4 3 Sensitivity and limitations')
    short={'Unadjusted':'No chain controls','Primary chain controls':'Primary chain controls',
        'Add baseline employment':'Add baseline FTE','Add baseline employment and wage':'Add baseline FTE and wage',
        'Exclude permanent closures':'Exclude permanent closures','Temporary closures employment zero':'Temporary closures set to zero'}
    rows=[[short[r.specification],str(int(r.n)),fmt(r.estimate),fmt(r.se),f'[{r.ci95_lower:.2f}, {r.ci95_upper:.2f}]',fmt(r.p,3)] for _,r in sens.iterrows()]
    table('Table 7  Sensitivity of the ownership difference',['Specification','N','Difference','HC3 SE','95 percent interval','p'],rows,[WIDTH-278,32,58,58,93,37])
    p('All rows estimate the same company-owned-minus-franchise contrast but differ in adjustment or sample. The baseline-wage specification uses 365 complete observations. Removing permanent closures leaves 378; adding temporary closures with zero employment gives 388. Results are sensitivity checks around one primary hypothesis, not separate discoveries.',note=True)
    p('Ownership differences range from -1.14 to +1.78 FTE across the six specifications, and every interval includes zero. Adding baseline employment changes the sign to +1.51; adding baseline employment and wages gives +1.78. These controls change the conditional comparison and can be sensitive to regression to the mean or measurement error, so they are not automatically superior causal estimates. The sign reversal does show that a claim that corporate stores responded less favorably is not stable to plausible adjustment.')
    p('Closure alternatives keep the difference negative but imprecise. No alternative establishes a statistically precise ownership gap. A positive company-owned contrast in one adjusted model is not evidence of a significant difference from franchises: the relevant interaction test remains nonsignificant. I therefore report the interaction directly instead of comparing separate subgroup significance stars.')
    h('5 Limitations and conclusion',sub=True)
    p('Survey-based employment and wage reports can contain measurement error. Missingness can depend on store characteristics; paired comparisons exclude stores without observed changes, and different variable screens target different samples. Restaurants are not randomly assigned to ownership, baseline wage exposure differs, and the data do not observe corporate financial support, labor-demand shocks or staffing decisions. The proposed organizational channels cannot be distinguished directly. Only the sampled fast-food cohort in these areas is studied, so extrapolation to other industries, later periods or restaurant entry is not warranted.')
    p('The assigned core results broadly reproduce the original finding of no observed relative employment decline in NJ, while retaining transparent differences in printed statistics and one ambiguous model specification. The extension contributes a direct, economically motivated ownership comparison rather than more controls alone. Its main lesson is limited precision and sensitivity to baseline composition: this sample does not support a firm conclusion about ownership-specific responses. More pre-policy observations, additional policy comparisons and richer restaurant characteristics would be needed to strengthen that inference.')

    page(); h('6 Reproducibility and AI disclosure')
    p('The repository contains an end-to-end Python workflow, dependency requirements, generated aggregate results, sample audits and the report source. With the documented public.csv input in 01_DID/data/, run.ps1 or code/run_all.py regenerates the core replication, ownership extension, validation outputs and report without editing data or code. Restricted course raw data, processed store-level data and local dependency files are ignored by Git; processed data are regenerated locally. Original papers and course download links are not redistributed. Git commits record meaningful stages rather than one final upload.')
    p('Validation checks dimensions and state counts, state/sheet keys, closure treatment and the regression sample. The paired DiD is independently recomputed with Welch inference and a two-period within-store regression. OLS coefficients are compared with NumPy least squares. Extension HC3 covariance is checked against its matrix formula, and the unadjusted ownership interaction against the four-cell identity. Every wage observation enters a bin and every state-wave percentage total is 100. Repeated pipeline outputs are checked for deterministic equality. These checks establish implementation consistency, not the causal assumptions.')
    p('Codex assisted with reading the brief and data dictionary, visually inspecting the scanned paper, locating the official archive, coding, calculations, documentation and report drafting. AI outputs were checked using the tests above and source comparisons. Corrected or rejected suggestions included using SHEET as a global identifier, a headcount-based full-time percentage, dropping permanent closures because follow-up wages are missing, and deleting reported operating variables solely to improve a match. The model-v source conflict and unmatched row-3 SEs were retained explicitly. The full disclosure in AI_USE_DISCLOSURE.md separates assistant-performed checks from the student\'s responsibility for the final submission.')
    h('References')
    refs=[
        'Card, David, and Alan B. Krueger. 1994. Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania. American Economic Review 84(4): 772-793.',
        'Card, David. Available data sets, NJ-PA survey archive, codebook and check.sas. https://davidcard.berkeley.edu/data_sets.html. Accessed 13 October 2026. The archive README identifies its use in Myth and Measurement, chapter 2.',
        'MacKinnon, James G., and Halbert White. 1985. Some Heteroskedasticity-Consistent Covariance Matrix Estimators with Improved Finite Sample Properties. Journal of Econometrics 29(3): 305-325. https://doi.org/10.1016/0304-4076(85)90158-7.',
        'statsmodels. OLSResults.HC3_se documentation. https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.HC3_se.html. Accessed 13 October 2026.',
        'ECO6067. Individual Project: AI-Assisted Empirical Paper Replication and Extension. Draft v3, 2026. Course Package 01 README, data dictionary and public.csv.']
    for ref in refs: p(ref,note=True)

    page(); h('Appendix A Published entry discrepancies')
    bad=comparisons[~comparisons.matches_published_precision]
    rows=[]
    for _,r in bad.iterrows():
        label=r['row'].replace('3. Wage = 5.05 (percentage)','Wave 2 wage 5.05').replace('3. FTE employment','Wave 2 FTE').replace('3. Price of full meal','Wave 2 meal').replace('3. Hours open (weekday)','Wave 2 hours')
        rows.append([r['table'].replace('Table ','T'),label,r['column'],fmt(r.actual,4),fmt(r.original,2),fmt(r.difference,4)])
    table('Entries outside the printed rounding interval',['Table','Row or variable','Column','Computed','Printed','Difference'],rows,
        [34,WIDTH-268,83,53,45,53],small=True)
    p('Comparison tolerance is half a unit in the last displayed decimal, with a numerical epsilon. The complete comparison.csv includes matches as well. Table 2 wage-point differences involve denominator and closure-reporting conventions; Table 3 row-3 errors use the disclosed influence estimator; model-v diagnostics involve the documented source conflict. Other small differences are retained without claiming a known cause.',note=True)
    p('Complete observed counts, all model coefficients, official-source verification hashes, validation checks and both model-v interpretations are available in outputs/tables/. No published entry is substituted into the computed result tables.',note=True)

    def footer(canvas,doc):
        canvas.setFont('Times-Roman',8)
        canvas.drawString(54,32,'Rui YUAN | ECON 6067 | Replication and extension')
        canvas.drawRightString(A4[0]-54,32,str(doc.page))
    document=SimpleDocTemplate(str(ROOT/'report.pdf'),pagesize=A4,rightMargin=54,leftMargin=54,
        topMargin=45,bottomMargin=47,title=title,author=info['author'],invariant=1)
    document.build(story,onFirstPage=footer,onLaterPages=footer)
    (ROOT/'report.md').write_text('\n'.join(md),encoding='utf-8')
    print('Report created:',ROOT/'report.pdf')


if __name__=='__main__': main()
