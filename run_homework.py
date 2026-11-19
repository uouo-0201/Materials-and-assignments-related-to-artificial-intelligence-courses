from pathlib import Path
import os,sys,json,contextlib,io,datetime
BASE=Path(__file__).resolve().parent/'7. Naive-Bayes'
OUT=BASE/'.tmp/naive-bayes/homework'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(BASE)
sys.path.insert(0,str(BASE/'scripts'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nbformat
from IPython.utils.capture import capture_output
nb=nbformat.read(BASE/'notebooks/naive-bayes-lab.ipynb',as_version=4)
scope={}
for cell in nb.cells:
 if cell.cell_type!='code': continue
 source=cell.source
 if 'FREEZE_CONFIRMED = False' in source:
  source=source.replace('FREEZE_CONFIRMED = False','FREEZE_CONFIRMED = True').replace('OPEN_LOCKED_TEST = False','OPEN_LOCKED_TEST = True').replace('OPEN_TRANSFER_TEST = False','OPEN_TRANSFER_TEST = True')
  cell.source=source
 with capture_output() as cap: exec(compile(source,'naive-bayes-lab.ipynb','exec'),scope)
 cell.execution_count=sum(c.cell_type=='code' and c.get('execution_count') is not None for c in nb.cells)+1
 cell.outputs=[nbformat.v4.new_output('stream',name='stdout',text=cap.stdout+cap.stderr)]
 plt.close('all')
nbformat.write(nb,BASE/'notebooks/naive-bayes-lab-作业第七讲已运行.ipynb')
import teacher_analysis
teacher_analysis.OUT=OUT
teacher_analysis.main()
import pandas as pd
from lab_utils import scores,FEATURES
tr=scope['train']; va=scope['val']; model=scope['model']
print('TRAIN',scores(tr.bladder_inflammation,model.predict_proba(tr[FEATURES])[:,1]))
print(pd.read_csv(OUT/'C-duplicate-5-probabilities.csv').assign(delta=lambda d:abs(d.original_probability-d.duplicate_probability)).sort_values('delta',ascending=False).head().to_string())
