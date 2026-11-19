"""Optional numerical helper for the V3 experiments, not an answer key.
From V3: python scripts/experiment_helper.py
Requires the course Python environment with pandas and numpy.
Writes UTF-8 CSV tables with Chinese headers; no cleaning or input overwrites.
Students may change the recoding map or selected variables to test their ideas.
"""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np

ROOT=Path("E:/人工智能课应用/课件/2. Data/V3/data/heart-disease-forur-site.csv").resolve().parents[1]
import argparse
parser = argparse.ArgumentParser() # 新增这一行，定义parser
parser.add_argument('--output-dir',default=str(ROOT/'experiment-results'))
args=parser.parse_args()
out=Path(args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(ROOT/'data/heart-disease-four-site.csv')
features=[c for c in df if c not in ['record_id','site','num']]
sites=['Cleveland','Hungary','Switzerland','VA Long Beach']
names={'age':'年龄','sex':'性别编码','cp':'胸痛类别','trestbps':'静息血压','chol':'胆固醇','fbs':'血糖阈值','restecg':'静息心电图','thalach':'最大心率','exang':'运动心绞痛','oldpeak':'ST下降','slope':'ST斜率','ca':'显影血管数','thal':'灌注检查'}
def save(name,frame):
    frame.to_csv(out/name,index=False,encoding='utf-8-sig',float_format='%.6f')

# Experiment 1: changing the label while keeping category membership fixed.
RECODE={1:10,2:20,3:40,4:80}
renamed=df.cp.map(RECODE)
save('B1-recoding.csv',pd.DataFrame([{'原编号':k,'新编号':v,'原类别频数':int(df.cp.eq(k).sum()),'改名后同类频数':int(renamed.eq(v).sum())} for k,v in RECODE.items()]))

# Experiment 2: these are summaries, not fitted prediction models or tests.
y=df.num.gt(0).astype(int)
save('B2-means.csv',pd.DataFrame([
    {'变量':'年龄','非空数':df.age.count(),'均值':df.age.mean(),'单位':'年'},
    {'变量':'原胸痛编号','非空数':df.cp.count(),'均值':df.cp.mean(),'单位':'编号'},
    {'变量':'改名后胸痛编号','非空数':renamed.count(),'均值':renamed.mean(),'单位':'编号'},
    {'变量':'疾病状态y','非空数':y.count(),'均值':y.mean(),'单位':'比例'}]))
ct=pd.crosstab(df.cp,y).reset_index();ct.columns=['胸痛原编号','y=0记录数','y=1记录数'];save('B2-counts.csv',ct)
c=df[df.site.eq('Cleveland')][['age','trestbps','chol']]
z=(c-c.mean())/c.std(ddof=0)
save('B3-scale.csv',pd.DataFrame([{'变量':names[v],'记录数':len(c),'原均值':c[v].mean(),'原标准差':c[v].std(ddof=0),'z均值':z[v].mean(),'z标准差':z[v].std(ddof=0),'Cleveland-001原值':c[v].iloc[0],'Cleveland-001转换值':z[v].iloc[0]} for v in c]))

# Experiment 3: two explicit sensitivity comparisons, neither saved as cleaned data.
miss=df.groupby('site')[features].apply(lambda x:x.isna().sum()).reindex(sites).rename(columns=names).reset_index().rename(columns={'site':'中心'})
save('C1-all-missing.csv',miss)
quality=[];sensitivity=[];retention=[]
complete=df.dropna(subset=features)
for site in sites:
    g=df[df.site.eq(site)];valid=g.chol.dropna();nonzero=valid[valid.ne(0)]
    quality.append({'中心':site,'记录数':len(g),'胆固醇缺失数':g.chol.isna().sum(),'血管数缺失数':g.ca.isna().sum(),'胆固醇零值数':g.chol.eq(0).sum(),'y=1记录数':g.num.gt(0).sum(),'y=1比例%':100*g.num.gt(0).mean()})
    sensitivity.append({'中心':site,'保留零值记录数':len(valid),'保留零值均值mg/dL':valid.mean(),'排除零值记录数':len(nonzero),'排除零值均值mg/dL':nonzero.mean()})
    retention.append({'中心':site,'原记录数':len(g),'原中心占比%':100*len(g)/len(df),'完整记录数':complete.site.eq(site).sum(),'筛选后中心占比%':100*complete.site.eq(site).mean()})
save('C1-quality.csv',pd.DataFrame(quality));save('C2-zero-comparison.csv',pd.DataFrame(sensitivity));save('C3-complete-cases.csv',pd.DataFrame(retention))
save('C-extreme-values.csv',df.nlargest(3,'chol')[['record_id','site','chol']].rename(columns={'record_id':'教学编号','site':'中心','chol':'胆固醇mg/dL'}))
print('Numerical tables saved to:',out)
print('Blank mean with n=0 means no valid observations; it is not zero.')
print('Use the worksheet to interpret and verify these results. No source data was changed.')
