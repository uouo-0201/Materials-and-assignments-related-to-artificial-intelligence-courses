"""Teacher-only independent pilot; reads only student CSV and extracted fields."""
import json
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent
path = root / 'review/pilot-fields.json'
pilot = json.loads(path.read_text(encoding='utf-8'))
fields = {x['id']: x for x in pilot['fields']}
def put(n, answer, minutes):
    fields[f'F{n:03}']['answer'] = answer if isinstance(answer, list) else [answer]
    fields[f'F{n:03}']['minutes'] = minutes
def flag(n,code,severity,note,fix):
    fields[f'F{n:03}']['blockers'].append(dict(code=code,severity=severity,note=note,fix=fix))

early = [
 '一列常是一个指标，一行是一次记录；我以前会把所有数字都当数量。',
 '编号、疾病标签和特征有什么不同？年龄存整数是否就是计数？',
 '读R1/R2，打开真实表对比age、cp和record_id的含义。',
 '年龄可以求平均，血型应该数各类人数。',
 '想知道0/1的均值是什么，以及类别怎么进入Logistic。',
 '读R3，做胸痛改名和列联表，看看结果是否改变。',
 '病人资料可能有空白，也可能来自不同医院。',
 '不确定缺失能否填0，医院不同能否说明仪器不同。',
 '读R3质量部分，分中心数空白和0，比较删行前后的中心构成。',
 'Heart Disease；UCI Machine Learning Repository；Janosi等（1989）；DOI:10.24432/C52P4X（R4[1]）。',
 '920条，13个候选特征；另外num是原始标签，site是来源，record_id是教学编号。总共16列（R2及CSV）。',
 '一行是一个来源文件里的临床记录。record_id只由中心和行号组成，没有跨文件的真实患者链接，不能证明920个独立患者（R2）。',
 '暂选A，四中心都保留用于描述，待检查后再限定研究。A1显示各中心均有记录；未知事实是一些关键指标是否在某中心大量缺失，这会改变建议。'
]
for n,a in enumerate(early,1): put(n,a,[1,1,1,1,1,1,1,1,1,3,2,2,3][n-1])
rows = [
 ['标识类别；链接元数据（R2）','不宜：编号不是数量','不宜：每行独有，不能当有意义分组','不宜：仅定位记录','不宜：编号'],
 ['无序多分类；来源元数据（R2）','不宜：中心名','有条件：与y分组并检查独立性','类别编码；需说明研究与预测中心','不宜：先编码'],
 ['连续量、整年记录；候选特征（R1/R2）','可：平均年龄','不宜：连续原值','数值预测；预测前可知年龄','有条件：按方法考虑尺度'],
 ['二分类；候选特征（R2）','可：非缺失中编码1比例','有条件：独立记录与期望频数','类别编码0/1；沿用历史定义','一般不必；保留0/1较易解释'],
 ['无序多分类；候选特征（R2）','不宜：只是标签','有条件：与y列联表','类别编码；以一类作参照','不宜直接z化；先编码'],
 ['连续量；候选特征（R2）','有条件：先核对不合理值','不宜：连续原值','数值预测；入院测量须在预测前','有条件：尺度及数值方法需要'],
 ['连续量；候选特征（R2）','有条件：说明缺失、0和异常处理','不宜：连续原值','数值预测；检查时点和质量','有条件：先核对质量'],
 ['二分类；候选特征（R2）','可：已观测者中高于阈值比例','有条件：独立性与期望频数','类别编码0/1；预测前可得','一般不必；不可补空白为0'],
 ['无序多分类；候选特征（R2）','不宜：心电图编码不等距','有条件：分类列联表','类别编码；不把0/1/2当线性量','不宜：先编码'],
 ['连续测量、整值记录；候选特征（R2）','可：有记录者平均心率','不宜：连续原值','数值预测；须已完成运动检查','有条件：按方法考虑'],
 ['二分类；候选特征（R2）','可：已观测者阳性比例','有条件：分类列联表','类别编码0/1；预测时须可获得','一般不必：保留0/1'],
 ['连续量；候选特征，单位待核（R2）','有条件：先确认测量尺度','不宜：连续原值','数值预测；检查时点须合适','有条件：尺度可靠且标准差非0'],
 ['有方向次序的分类；候选特征（R2）','不宜：上斜到下斜不证明等距','有条件：按类别列联表','先类别编码；单数值需趋势假设','不宜直接z化类别编号'],
 ['计数；候选特征（R2）','有条件：均值有含义，须说分母','有条件：0–3类别且不稀疏','数值预测；也可分类，检查时点','有条件：按方法需要'],
 ['无序多分类；候选特征（R2）','不宜：3/6/7只是类别标签','有条件：分类列联表','类别编码；预测前须可获得','不宜直接z化'],
 ['原始疾病类别；结局来源（R2）','不宜：0–4不等于统一分期','有条件：先统一为0与>0','结局：派生y；不能又作输入','不宜：结局编码不用z化']
]
for r,answers in enumerate(rows):
 for c,a in enumerate(answers):
  put(14+r*5+c,a,1.0 if c==0 else .35)
put(94,['原cp均值3.25，重编号均值56.28（920条，CSV）。','四类前后计数分别46→46、174→174、204→204、496→496。无症状从4改80仍496条。','改的是编号均值，不是病人的胸痛类别；因此类别编号平均缺少稳定医学意义。'],12)
d=pd.read_csv(root/'data/heart-disease-four-site.csv')
d['y']=(d.num>0).astype(int)
put(95,'53.51年；920条非缺失年龄。',2)
put(96,'该文件记录的平均年龄，不代表目前普通人群。',1)
put(97,'3.25；920条胸痛编码，沿用实验1计算。',.5)
put(98,'无稳定医学量含义；改名实验已经说明。',.5)
put(99,'0.5533=509/920=55.33%。',2)
put(100,'该文件中num>0的比例，不能当当前人群患病率。',1)
ct=pd.crosstab(d.cp,d.y)
for row in range(4):
 for col in range(2):put(101+2*row+col,str(ct.loc[row+1,col]),1)
put(109,['比较胸痛类别与疾病状态的分布关系；卡方是候选方法，但须检查记录独立性和期望频数（R3）。','手工复核：cp=1有26+20=46；四行总计46+174+204+496=920。最小期望计数46×411/920=20.55，频数不稀疏；独立患者身份仍未核实。'],4)
put(110,'age，保留年数作数值预测；在计划预测时通常已知，仍需确认记录时点（R2/R3）。',1.5)
put(111,'cp，设2、3、4三列0/1指示，以1为参照；须在预测前记录症状，不用1–4当等距量。',2)
put(112,'num不能作为预测y的输入，因为y由num得到，会泄漏结局；预测前尚不知道造影标签。',1.5)
g=d[d.site=='Cleveland']
for row,col in enumerate(['age','trestbps','chol']):
 vals=[g[col].mean(),g[col].std(ddof=0),0.,1.]
 for c,v in enumerate(vals):put(113+4*row+c,f'{v:.2f}',1.25)
put(125,'Cleveland-001年龄63：z=(63−54.438944)/9.023735=0.948726，约0.95；与用未四舍五入参数的软件结果一致。',3)
put(126,'B3三个变量都变为均值约0、总体标准差1的无单位分数，仍测量年龄、血压、胆固醇。空白仍无测量值；中心构成或采集流程差异也不会因z化消失（R3）。',3)
put(127,'age在需要尺度可比或带正则化的后续方法中可考虑z化；cp应先按类别编码，z化原编号不会纠正无序编码问题。我已据此修订B1这两行。',3)
features=[c for c in d if c not in ['record_id','site','num','y']]
cc=d.dropna(subset=features)
sites=['Cleveland','Hungary','Switzerland','VA Long Beach']
missing=d.groupby('site')[features].apply(lambda x:x.isna().sum())
missing.to_csv(root/'review/pilot-missing-counts.csv',encoding='utf-8-sig')
for row,site in enumerate(sites):
 h=d[d.site==site]
 vals=[str(h.chol.isna().sum()),str(h.ca.isna().sum()),str((h.chol==0).sum()),f'{h.y.sum()}/{len(h)}={h.y.mean()*100:.2f}%']
 for c,v in enumerate(vals):put(128+4*row+c,v,2 if c==0 else 1)
 for c,h2 in enumerate([h,h[h.chol!=0]]):
  value=f'{h2.chol.count()}；{h2.chol.mean():.2f} mg/dL' if h2.chol.count() else '0；不可计算'
  put(144+2*row+c,value,1.5)
 n=int((cc.site==site).sum())
 put(152+2*row,str(n),1.5)
 put(153+2*row,f'{n}/{len(cc)}={n/len(cc)*100:.2f}%',1)
put(160,['C1/C2：Switzerland胆固醇123条全0，保留均值0，去0后没有可算记录。不能把0解释成健康水平，也不能无证据认定错误原因。','C3：完整记录仅299条，其中Cleveland297条。Cleveland从303/920=32.93%升为297/299=99.33%，删空白几乎把四中心研究变成单中心。','C1至C3都不足以证明技术批次效应；还可能是患者构成或采集规则，需流程、共同样本或校准资料（R3）。'],6)
put(161,'分期有序，突变数为计数。分期相邻间距相等需可靠量表或测量依据，不能只由I、II、III推出（D1、R1）。',2)
put(162,'不能；甲发生事件，乙在12个月时仍未发生。保留观察时长和事件状态。真实心脏病表没有随访起止和事件列，不能直接作生存研究。',2.5)
put(163,'300×20000，3位供者。高维描述矩阵结构，不是单基因类型；若原始分子数是计数，若标准化表达量可能连续。题中没给具体表示，不能唯一判断。',3)
put(164,'40行×4096列；每人两图，所以独立受试者仅20，保留受试者链接。',2)
put(165,'甲均值100、乙120，乙−甲=20。同一标准样本使生物对象相同，比各中心患者阳性比例多了可比对象的控制；没有真值不能说哪台准确。',2.5)
put(166,'选择随访研究：需患者链接、统一起点、随访时长、事件发生日期或状态，以及失访/观察结束日期。获得这些并核对结局定义后再开始（D1随访行、R1）。',2)
for n,a in {
167:'展示B1胸痛行与改名实验的3.25→56.28。',168:'类型由含义决定；无症状496条不变。并非所有数字都不能平均，年龄可以。',
169:'展示B2频数、B3年龄z=0.95。',170:'卡方针对分类频数，标准化改尺度；记录独立性未确认，不能仅凭表格说检验一定有效。',
171:'展示C2 Switzerland及C3删行构成。',172:'质量处理改变样本范围；中心差异本身不能确定技术批次原因。'
}.items():put(n,a,1)
put(173,'建议B：暂以Cleveland及有明确含义的字段开展描述研究，不把结果推广为四中心人群结论。年龄可求均值，胸痛需类别编码；num仅用于派生结局。C3完整记录中297/299来自Cleveland，而原占比仅32.93%，直接删行会改变研究对象。C2显示Switzerland胆固醇123条全为0，须核实采集及缺失编码。极端值Hungary-244胆固醇603 mg/dL应查原始记录或复测，不能只因最大就删除。优先核实来源流程、真实患者链接及预测时点。表中缺少随访时间和事件状态，暂不能回答生存问题。',8)
for n,a in {174:'已勾选；可用胸痛改名数值解释。',175:'已勾选；需拿R3辅助解释期望频数及编码。',176:'已勾选；已核对46条及z=0.95。',177:'已勾选；若0有可靠编码解释、缺失可追补，可能扩大研究范围。'}.items():put(n,a,.5)
put(178,'模拟同学质疑：“只选Cleveland会不会牺牲代表性？”我补充：会，因此B只是受限研究，不宣称代表四中心。C3的99.33%说明完整记录分析也几乎如此，应明确范围并争取追补其他中心资料。此处为模拟质疑，并非真实课堂发言。',3)

flag(14,'P15','block','启动课已有80个B1判断单元，另有3W、数据身份、学习和改名实验。按初学者读字典、查取值及写短句估计，启动约78分钟，超45分钟及20%容差。','保留逐列类型/角色；方法判断选代表字段。提供可执行Excel/AI操作起步材料，重新独立试填；不得仅把时间估计改小。')
flag(17,'P03','friction','实验1先学仅指R1/R2，但已要求Logistic、卡方和标准化判断；我必须自行推断应提前读R3。','先学明确引用R3方法小节，或把方法列移到实验2。')
flag(125,'P03','friction','“若实验2已手工核对频数”需要推断为前面的“方法判断与手工核对”，同名实验2也包含本节。','写“若已在‘方法判断与手工核对’核对频数”。')
flag(127,'P12','friction','要求在本框解释标准化用途，再直接修订B1同样的判断，形成重复写答。','取消本框；把例子、条件只写B1选定两行，提示汇报引用。')
flag(113,'P15','block','实验2除三种均值、B2、角色与手核，还有三列标准化、12统计格和三段解释；本次初学者估算约56分钟，超25分钟。','给出可操作模板/表格公式起步并减少重复；保留一列亲手标准化、另两列独立核验。')
flag(128,'P15','block','实验3含52个缺失计数的另附表、C1/C2/C3及文字推论和极端值查找；缺乏操作脚手架，估算至少约51分钟，超30分钟。','提供包含原数据引用、分中心计数与筛选步骤的空白Excel实验模板或短操作卡，保留学生计算与解释。')
flag(160,'P03','friction','“并说明本表是否足以”可指最近C3或C1至C3；我推断为三张表。','明确“说明表C1至C3是否足以”。')
flag(163,'P08','friction','D1问基因测量类型却仅给矩阵维度；原始计数或标准化表达量均合理，我只能条件作答。','在输入注明原始计数/标准化表达量，或明确允许条件答案并要求说明缺少的信息。')
flag(166,'P12','friction','D1总指令已要求说明真实数据缺哪项信息，随访行又问真实表能否做生存研究，边界框第三次写同一判断。','D1只作情境判别；真实数据缺字段的完整答案仅保留边界框，可引用D1。')
flag(173,'P15','block','汇报准备10分钟要写六格提纲、180–250字最终建议、核对极端值、四条自检及试讲5–8分钟；本次约24分钟。','合并提纲与建议，改为引用表格的简短口头提示并给准备时间；或调整实际课时须有授权。')
flag(178,'P18','friction','“课后修正记录”由“讨论后修正”推断在汇报课堂之后，工作单两次课堂容易混淆。','明确“汇报课堂讨论后（3分钟，计入汇报课）”。')
pilot['pilot_metadata']={'date':'2026-09-25','independence':'fresh-agent: student-visible materials only','persona':'中文生物医学初学者；基本Excel/AI操作，不熟练编程','timing_note':'field minutes include task setup/AI assistance and verification; reading and rehearsal overhead separately listed in notes; no teacher answers consulted','status':'revision required; blocking workload findings unresolved'}
assert all(x['answer'] and x['minutes'] is not None for x in pilot['fields'])
path.write_text(json.dumps(pilot,ensure_ascii=False,indent=2),encoding='utf-8')
print('filled',len(fields),'fields')
print('launch field minutes',sum(fields[f'F{n:03}']['minutes'] for n in range(1,95)))
print('exp2',sum(fields[f'F{n:03}']['minutes'] for n in range(95,128)))
print('exp3',sum(fields[f'F{n:03}']['minutes'] for n in range(128,161)))
print('transfer',sum(fields[f'F{n:03}']['minutes'] for n in range(161,167)))
print('prep',sum(fields[f'F{n:03}']['minutes'] for n in range(167,178)))
