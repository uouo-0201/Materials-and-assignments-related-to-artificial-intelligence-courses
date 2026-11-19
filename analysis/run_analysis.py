from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tmp/packages'))
import numpy as np,pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.power import TTestIndPower
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Times New Roman','font.size':11,'text.color':'black','axes.labelcolor':'black','axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':300})
d=pd.read_csv(ROOT/'V3/data/heart-disease-hypothesis.csv')
assert d.record_id.is_unique and (d.disease==(d.num>0).astype(int)).all()
a=d.dropna(subset=['disease','thalach']).copy()
x=a.loc[a.disease==1,'thalach'];y=a.loc[a.disease==0,'thalach']
def welch(x,y):
 n,m=len(x),len(y);v=x.var()/n;w=y.var()/m;se=np.sqrt(v+w);df=(v+w)**2/(v*v/(n-1)+w*w/(m-1));diff=x.mean()-y.mean();t,p=stats.ttest_ind(x,y,equal_var=False);lo,hi=diff+np.array([-1,1])*stats.t.ppf(.975,df)*se
 return dict(n1=n,n0=m,diff=diff,se=se,df=df,t=t,p=p,lo=lo,hi=hi)
r=welch(x,y)
desc=a.groupby('disease').thalach.agg(['count','mean','std','median','min','max']);desc['q25']=a.groupby('disease').thalach.quantile(.25);desc['q75']=a.groupby('disease').thalach.quantile(.75);desc.to_csv(OUT/'descriptive.csv')
miss=d.assign(missing=d.thalach.isna()).groupby(['site','disease']).agg(total=('record_id','size'),missing=('missing','sum'));miss.to_csv(OUT/'missing_by_site.csv')
missing=d.assign(missing=d.thalach.isna()).groupby('missing').agg(n=('record_id','size'),age_mean=('age','mean'),male_pct=('sex',lambda z:100*z.mean()),disease_pct=('disease',lambda z:100*z.mean()));missing.to_csv(OUT/'missing_comparison.csv')
fits={}
for name,formula in [('unadjusted','thalach ~ disease'),('age_sex','thalach ~ disease + age + sex'),('full','thalach ~ disease + age + sex + C(site)')]:
 f=smf.ols(formula,a).fit(cov_type='HC3');ci=f.conf_int().loc['disease'];fits[name]=dict(n=int(f.nobs),diff=f.params['disease'],lo=ci.iloc[0],hi=ci.iloc[1],p=f.pvalues['disease'])
sites=[]
for site,g in a.groupby('site'):
 z=welch(g.loc[g.disease==1,'thalach'],g.loc[g.disease==0,'thalach']);z['site']=site;sites.append(z)
pd.DataFrame(sites).to_csv(OUT/'site_results.csv',index=False)
ct=pd.crosstab(d.sex,d.disease);chi,pchi,dfchi,expected=stats.chi2_contingency(ct,correction=False)
pear=stats.pearsonr(a.age,a.thalach);spear=stats.spearmanr(a.age,a.thalach);mw=stats.mannwhitneyu(x,y,alternative='two-sided')
log=smf.logit('disease ~ age + sex + thalach',a).fit(disp=False);orr=pd.DataFrame({'OR':np.exp(log.params),'lo':np.exp(log.conf_int()[0]),'hi':np.exp(log.conf_int()[1]),'p':log.pvalues});orr.to_csv(OUT/'logistic_or.csv')
power=TTestIndPower();req=power.solve_power(effect_size=5/24,alpha=.05,power=.8,ratio=1)
res=dict(primary=r,models=fits,chi2=dict(stat=chi,p=pchi,min_expected=expected.min(),table=ct.values.tolist()),pearson=dict(r=pear.statistic,p=pear.pvalue),spearman=dict(r=spear.statistic,p=spear.pvalue),mannwhitney=dict(U=mw.statistic,p=mw.pvalue),power_n_per_group=req,versions={k:__import__(k).__version__ for k in ['numpy','pandas','scipy','statsmodels','matplotlib']})
(OUT/'results.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
fig,axs=plt.subplots(1,2,figsize=(9,3.2));axs[0].hist(y,bins=np.arange(60,211,10),histtype='step',color='black',label='No disease',linewidth=1.5);axs[0].hist(x,bins=np.arange(60,211,10),histtype='step',color='black',linestyle='--',label='Disease',linewidth=1.5);axs[0].set(xlabel='Maximum heart rate (beats/min)',ylabel='Count');axs[0].legend(frameon=False)
axs[1].boxplot([y,x],tick_labels=['No disease','Disease'],patch_artist=False,medianprops={'color':'black'},flierprops={'markeredgecolor':'black'});axs[1].set(ylabel='Maximum heart rate (beats/min)');fig.tight_layout();fig.savefig(OUT/'fig1_distribution.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,3.2));items=[('Welch unadjusted',r),('Adjusted age + sex',fits['age_sex']),('Adjusted age + sex + site',fits['full'])]+[(z['site'],z) for z in sites]
for i,(label,z) in enumerate(items):ax.errorbar(z['diff'],i,xerr=[[z['diff']-z['lo']],[z['hi']-z['diff']]],fmt='o',color='black',capsize=3)
ax.axvline(0,color='black',ls=':');ax.set_yticks(range(len(items)),[k for k,z in items]);ax.invert_yaxis();ax.set_xlabel('Disease minus no disease (beats/min), 95% CI');fig.tight_layout();fig.savefig(OUT/'fig2_forest.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,3));ns=np.arange(20,501,5)
for diff,sd,ls in [(5,24,'-'),(10,24,'--'),(5,36,':')]:ax.plot(ns,power.power(diff/sd,ns,alpha=.05,ratio=1),color='black',ls=ls,label=f'Difference={diff}, SD={sd}')
ax.axhline(.8,color='black',ls='-.',lw=.6);ax.set(xlabel='Sample size per group',ylabel='Power',ylim=(0,1));ax.legend(frameon=False);fig.tight_layout();fig.savefig(OUT/'fig3_power.png');plt.close(fig)
print(json.dumps(res,indent=2))
