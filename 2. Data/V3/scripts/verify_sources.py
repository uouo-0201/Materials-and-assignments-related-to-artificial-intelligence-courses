from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
import json
urls=['https://archive.ics.uci.edu/dataset/45/heart+disease',
'https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/heart-disease.names',
'https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html',
'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html',
'https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Logit.html']
def get(u):
    try:
        r=requests.get(u,timeout=30)
        return {'url':u,'status':r.status_code,'text':r.text}
    except Exception as e:return {'url':u,'error':str(e)}
results=list(ThreadPoolExecutor(5).map(get,urls))
p=Path(__file__).resolve().parents[1]/'review/source-verification.json'
p.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:print(r['url'],r.get('status',r.get('error')))
