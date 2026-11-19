"""Release checks for the two V3 documents and their linked inputs."""
from pathlib import Path
import subprocess
import sys
import json
import math
import re
from docx import Document
import pandas as pd
import numpy as np

root=Path(__file__).resolve().parents[1]
repo=root.parents[3]
qa=repo/'.codex/skills/pbl-ml-package/scripts/worksheet_check.py'
assert qa.exists(),qa
review=root/'review'
for args,dest in [(['lint',str(root/'pbl-data-types-student-worksheet.docx'),'-o',str(review/'worksheet-lint.md')],'lint-console.txt'),
                  (['design',str(review/'analysis-design.json'),'--homework-minutes','90'],'design-check.md')]:
    r=subprocess.run([sys.executable,str(qa),*args],capture_output=True,text=True,encoding='utf-8')
    (review/dest).write_text(r.stdout+r.stderr,encoding='utf-8')
    print(r.stdout+r.stderr)
    assert r.returncode==0,dest

source=root.parent/'assets/pbl-understanding-data/heart-disease-four-site.csv'
assert source.read_bytes()==(root/'data/heart-disease-four-site.csv').read_bytes()
for file in ['pbl-data-types-student-worksheet.docx','pbl-data-types-reference.docx']:
    d=Document(root/file)
    texts=[p.text for p in d.paragraphs]+[c.text for t in d.tables for r in t.rows for c in r.cells]
    assert not any('\ufffd' in t for t in texts),'Replacement glyph in '+file
    for t in texts:
        for rel in re.findall(r'(?:\.\./chap2_data\.pptx|(?:data|scripts)/[A-Za-z0-9_.-]+)',t):
            assert (root/rel).exists(),rel
    print(file,len(d.tables),'tables; text and links passed')
design=json.loads((review/'analysis-design.json').read_text(encoding='utf-8'))
for a in design['analyses']:
    for rel in a['artifacts']:assert (root/rel).exists(),rel
for e in design['evidence_items']:
    for rel in e['artifacts']:assert (root/rel).exists(),rel

# Validate the optional student calculation helper against separately computed truth.
r=subprocess.run([sys.executable,str(root/'scripts/experiment_helper.py'),'--output-dir',str(review/'helper-check')],capture_output=True,text=True,encoding='utf-8')
assert r.returncode==0,r.stderr
t=json.loads((review/'verified-results.json').read_text(encoding='utf-8'))
out=review/'helper-check'
rec=pd.read_csv(out/'B1-recoding.csv')
assert (rec['原类别频数']==rec['改名后同类频数']).all()
counts=pd.read_csv(out/'B2-counts.csv')
assert counts.iloc[:,1:].values.tolist()==t['contingency']
scale=pd.read_csv(out/'B3-scale.csv')
assert np.allclose(scale['原均值'],[v['mean'] for v in t['standardization']],atol=1e-5)
assert np.allclose(scale['z均值'],0,atol=1e-5) and np.allclose(scale['z标准差'],1)
ret=pd.read_csv(out/'C3-complete-cases.csv')
assert ret['完整记录数'].tolist()==[v['complete_n'] for v in t['retention']]
assert int(ret['完整记录数'].sum())==299
sens=pd.read_csv(out/'C2-zero-comparison.csv')
sw=sens[sens['中心'].eq('Switzerland')].iloc[0]
assert sw['排除零值记录数']==0 and pd.isna(sw['排除零值均值mg/dL'])
for i,row in sens.iterrows():
    v=t['quality'][i]
    assert np.isclose(row['保留零值均值mg/dL'],v['chol_mean_with_zero'],atol=1e-5)
    if v['chol_mean_without_zero'] is not None:assert np.isclose(row['排除零值均值mg/dL'],v['chol_mean_without_zero'],atol=1e-5)
sources=json.loads((review/'source-verification.json').read_text(encoding='utf-8'))
assert len(sources)==5 and all(r.get('status')==200 for r in sources)
print('Original data unchanged; all 5 public source links verified; helper results match.')
for folder,expected in [('worksheet-render',8),('reference-render',4)]:
    pages=json.loads((review/folder/'pages.json').read_text(encoding='utf-8'))
    assert len(pages)==expected,(folder,len(pages))
    assert min(x['characters'] for x in pages)>250,(folder,'near-empty page')
    for x in pages:assert (review/folder/f"page-{x['page']}.png").exists()
    print(folder,len(pages),'pages; no near-empty page')
print('PASS: release checks. Visual page inspection and independent pilot are separate gates.')
