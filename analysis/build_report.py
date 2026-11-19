from pathlib import Path
import json,math
import pandas as pd
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results';j=json.loads((R/'results.json').read_text());w=j['primary']
d=Document();sec=d.sections[0];sec.page_height=Cm(29.7);sec.page_width=Cm(21);sec.top_margin=Cm(2.3);sec.bottom_margin=Cm(2.2);sec.left_margin=Cm(2.5);sec.right_margin=Cm(2.5)
for name,size,cn in [('Normal',12,'宋体'),('Title',22,'黑体'),('Heading 1',15,'黑体'),('Heading 2',14,'黑体'),('Caption',10.5,'宋体')]:
 s=d.styles[name];s.font.name='Times New Roman';s.font.size=Pt(size);s.font.color.rgb=RGBColor(0,0,0);s.element.rPr.rFonts.set(qn('w:eastAsia'),cn);s.font.bold=False
 s.paragraph_format.space_after=Pt(6)
d.styles['Normal'].paragraph_format.first_line_indent=Pt(24);d.styles['Normal'].paragraph_format.line_spacing=1.4
for name in ['Heading 1','Heading 2']:d.styles[name].paragraph_format.first_line_indent=Pt(0);d.styles[name].paragraph_format.space_before=Pt(12)
for s in d.styles:
 for border in list(s.element.findall('.//' + qn('w:pBdr'))):border.getparent().remove(border)
def p(t):return d.add_paragraph(t)
def h(t):return d.add_paragraph(t,'Heading 1')
def hh(t):return d.add_paragraph(t,'Heading 2')
def cap(t):
 z=d.add_paragraph(t,'Caption');z.alignment=1;z.paragraph_format.first_line_indent=Pt(0);return z
def table(head,rows):
 t=d.add_table(rows=1,cols=len(head));t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for c,x in zip(t.rows[0].cells,head):c.text=str(x)
 for row in rows:
  for c,x in zip(t.add_row().cells,row):c.text=str(x)
 for ri,row in enumerate(t.rows):
  for c in row.cells:
   c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   for z in c.paragraphs:
    z.alignment=1;z.paragraph_format.first_line_indent=Pt(0);z.paragraph_format.line_spacing=1.15;z.paragraph_format.space_before=Pt(4);z.paragraph_format.space_after=Pt(4)
    if ri==0:z.paragraph_format.keep_with_next=True
    for run in z.runs:run.font.size=Pt(10.5)
   tcPr=c._tc.get_or_add_tcPr();bd=OxmlElement('w:tcBorders')
   for side in ['top','bottom','left','right']:
    e=OxmlElement('w:'+side);e.set(qn('w:val'),'single' if (side=='top' and ri==0) or (side=='bottom' and ri in [0,len(t.rows)-1]) else 'nil');e.set(qn('w:sz'),'10' if ri in [0,len(t.rows)-1] else '6');e.set(qn('w:color'),'000000');bd.append(e)
   tcPr.append(bd)
  pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
 t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
 return t
def fig(name,caption):
 z=d.add_paragraph();z.paragraph_format.first_line_indent=Pt(0);z.alignment=1;z.add_run().add_picture(str(R/name),width=Cm(15.6));z.paragraph_format.keep_with_next=True;cap(caption)
def f(x):return f'{x:.2f}'
title=d.add_paragraph('作业第五讲','Title');title.alignment=1
z=d.add_paragraph('统计检验与假设设计\n心脏病证据与最大运动心率的四中心横断面分析');z.alignment=1;z.paragraph_format.first_line_indent=Pt(0)
h('摘要')
p(f'本作业以四中心心脏病教学数据为基础，依次完成假设设计、错误类型与检出能力、统计方法选择、主要结果报告和偏倚评估。920名受试者中，865名具有最大运动心率记录。疾病组与无疾病组的平均心率分别为128.26与148.80次/分钟，未调整均值差为{w["diff"]:.2f}次/分钟，95%置信区间为[{w["lo"]:.2f}, {w["hi"]:.2f}]，双侧Welch检验p={w["p"]:.3g}。结果支持统计关联；临床意义和因果关系仍需独立证据。')
h('一 基础术语与计算原理')
hh('1 研究对象与估计目标')
p('总体是希望推断的人群，样本是实际观察到的受试者；分析单位是一个独立受试者。结局变量是要解释或比较的测量值，本题为thalach，即最大运动心率，单位次/分钟。分组变量disease由num生成：num>0时为1，num=0时为0；“无疾病证据”不应扩展为保证健康。site表示数据来源中心，不是随机治疗分组。')
p('参数是总体特征，统计量是由样本算出的量。设μ₁、μ₀分别为疾病组与无疾病组总体平均心率，目标参数Δ=μ₁−μ₀。样本估计为两组样本均值之差。H0是待检验的约束，H1为对应的备择；本题分别为Δ=0与Δ≠0。')
hh('2 p值 显著性与置信区间')
p('显著性水平α是分析前规定的一类错误控制标准，本题取0.05。p值是在H0及模型条件成立时，获得当前或更极端统计量的概率；p值不是H0成立的概率，也不是结果“由偶然造成”的概率。若p<α则拒绝H0；否则只能未拒绝H0。')
p('效应量说明差异有多大。本题优先使用保留原始单位的均值差；置信区间进一步说明估计精度。95%置信区间的重复抽样解释是：按同一程序反复抽样并构造区间，约95%的区间覆盖真实参数，而不是固定总体参数有95%的随机概率落在已得到的区间内。')
hh('3 Welch检验的实际计算')
p('先分别计算均值x̄=Σxᵢ/n与样本方差s²=Σ(xᵢ−x̄)²/(n−1)。两独立组均值差的标准误为SE=√(s₁²/n₁+s₀²/n₀)，衡量均值差因抽样而波动的程度。Welch法不要求两组总体方差相等。')
p(f'代入本题：Δ̂=128.26−148.80={w["diff"]:.2f}；SE=√(24.02²/474+23.61²/391)≈{w["se"]:.3f}；t=Δ̂/SE≈{w["t"]:.3f}。自由度ν=(v₁+v₀)²/[v₁²/(n₁−1)+v₀²/(n₀−1)]，其中vᵢ=sᵢ²/nᵢ，得ν≈{w["df"]:.2f}。')
p('双侧p=2P(Tν≥|t|)，95% CI=Δ̂±t₀.₉₇₅,ν×SE。本题临界值约1.963，误差界约3.19次/分钟。计算脚本使用原始未四舍五入数值，正文显示值只用于讲解。')
hh('4 混杂 多重比较与预测')
p('混杂是分组与结局的关联受到其他共同相关因素影响，例如年龄可能同时关联疾病状态与最大运动心率。调整回归估计是在模型规定的协变量条件下比较组别，仍依赖模型和测量条件。OR是优势比，优势为p/(1−p)，OR不等于风险比。关联模型中的OR也不能直接代表预测模型能准确区分个体。')
h('二 任务一 把问题变成假设')
hh('1 研究问题与实验设计')
p('我关注四中心记录中，有疾病证据者与无疾病证据者的最大运动心率总体均值是否不同。这是对已有观察性横断面资料的二次分析，不实施干预。每名受试者为一个分析单位，两个组由不同受试者组成。希望解释类似来源人群的关联，不主张样本代表全部普通居民。')
table(['项目','预定分析内容'],[['研究对象','原始920人；主分析纳入disease和thalach完整者'],['比较对象','disease=1 对比 disease=0'],['主要终点','thalach 最大运动心率 次/分钟'],['目标参数','Δ=μ₁−μ₀'],['H0与H1','H0：Δ=0；H1：Δ≠0'],['α与方向','α=0.05；双侧检验'],['主方法','独立样本Welch t检验与均值差95% CI']])
p('选择双侧是因为研究问题问“是否不同”，两个方向均有解释价值。不能看到负向差异之后再改成单侧。这里将上述规则作为可复现的教学分析方案；已有材料包含结果参考，因此不将本次分析表述为真正的前瞻性注册。')
hh('2 变量类型与数据质量')
table(['变量','类型','角色'],[['thalach','连续型','主要结局'],['disease','二分类','主要分组'],['age','连续型','协变量'],['sex','二分类 0女性 1男性','协变量'],['site','四水平分类','中心固定效应'],['record_id','标识符','唯一性核对'],['trestbps chol oldpeak','连续型','未用于主检验的其他测量']])
p('代码核查record_id唯一，disease与num>0一致。缺失心率保留为空并排除于主分析，不填0。四中心资料可能存在中心内相似性；中心固定效应控制平均水平差异，但只有四个中心，不把常规聚类稳健推断当作已可靠解决全部相关性。')
h('三 任务二 错误类型与检出能力')
hh('1 两类错误与未显著的边界')
table(['真实情况','研究判断','含义'],[['两组均值相同','拒绝H0','Type I error 假阳性'],['两组均值不同','未拒绝H0','Type II error 假阴性'],['两组均值不同','拒绝H0','正确检出 概率为power'],['两组均值相同','未拒绝H0','正确不拒绝']])
p('假阳性例子：实际上类似来源人群两组最大心率均值相同，但抽到的样本使检验显著。假阴性例子：总体真实相差5次/分钟，却因样本少或测量波动大而未显著。β是特定备择效应下的二类错误概率，power=1−β；它随备择效应、样本量、噪声、α和设计变化。')
p('未拒绝H0后，需要检查区间是否仍包含有实际意义的差异、样本是否充足、测量是否可靠。若要主张“足够相近”，应事先规定等效界值并用等效检验；普通差异检验不显著不能证明等效。')
hh('2 检出能力实验设计与结果')
p('本实验不是额外患者数据模拟，而是基于两独立组、等样本量、共同标准差和双侧α=0.05的非中心t分布理论计算。每组n从20变化到500，分别设定真实差异5或10次/分钟、标准差24或36次/分钟，控制其他条件以比较power。5和10是教学假设值，未声称是临床阈值。')
fig('fig3_power.png','图1 样本量 真实效应与噪声对检出能力的影响')
p(f'曲线说明样本量和真实效应增加提高power，噪声增加则降低power。在真实差异5次/分钟、标准差24的教学条件下，80% power约需每组{math.ceil(j["power_n_per_group"])}人。近似公式n≈2×(1.96+0.84)²×24²/5²≈362，精确t方法略有修正；若预计10%缺失，应再除以0.90并向上取整。这里不使用观察到的巨大效应计算“事后power”来重复证明显著性。')
h('四 任务三 选择方法与补充实验')
hh('1 五类问题的方法选择')
table(['问题','首选方法','关键条件','备选方法'],[['两组thalach','Welch t','独立记录 无支配性离群值','Mann–Whitney U'],['同一患者前后','配对t','差值独立且近似正态','Wilcoxon符号秩'],['sex与disease','Pearson卡方','独立记录 期望频数足够','2×2 Fisher精确检验'],['age与thalach','Pearson相关','线性关系 无严重离群值','Spearman相关'],['三指标预测disease','Logistic回归','logit函数形式合理 无完全分离','正则化Logistic及验证']])
p('Mann–Whitney U针对秩或分布差异，只有附加分布形状条件下才能作位置差异解释，不自动检验均值或中位数相等。配对t检验对差值而不是两次测量分别判断正态性；Wilcoxon符号秩的位置解释也需要差值分布近似对称。当前数据无前后配对，因此不编造配对数值。')
hh('2 分类关联与连续相关实验')
c=j['chi2'];pr=j['pearson'];sp=j['spearman']
p(f'补充实验均为探索性，不能扩大为多个确认性主终点。sex与disease使用两字段完整记录构建2×2列联表，进行不含Yates校正的Pearson卡方检验。χ²=Σ(O−E)²/E，E=行和×列和/总数；最小期望频数为{c["min_expected"]:.2f}，适用大样本近似。')
table(['sex','无疾病证据','有疾病证据'],[['女性',*c['table'][0]],['男性',*c['table'][1]]])
p(f'结果χ²(1)={c["stat"]:.3f}，p={c["p"]:.3g}，提示样本中性别构成与疾病状态有关。age与thalach在865个完整记录中进行Pearson相关，r={pr["r"]:.3f}，p={pr["p"]:.3g}；Spearman敏感性分析ρ={sp["r"]:.3f}，p={sp["p"]:.3g}。相关系数无单位，负号表示年龄较大者往往最大心率较低，不代表年龄的因果效应已被识别。')
hh('3 二分类模型实验')
p('以disease为结局，age、sex和thalach为解释变量，拟合Logistic模型log[p/(1−p)]=β₀+β₁age+β₂sex+β₃thalach。OR=exp(β)，95%区间由回归系数区间取指数获得。当前仅展示模型拟合和条件关联，不将同一训练数据拟合视为预测验证。')
lr=pd.read_csv(R/'logistic_or.csv',index_col=0)
table(['变量','OR','95% CI','p值'],[[k,f(v.OR),f'[{v.lo:.3f}, {v.hi:.3f}]',f'{v.p:.3g}'] for k,v in lr.iterrows() if k!='Intercept'])
p('age和thalach的OR对应每增加1单位，sex对应男性相对女性。若要回答“能否预测”，还需划分训练与验证数据，检查非线性、分离和过拟合，报告验证集区分度、校准截距与斜率及Brier分数；跨中心外部验证尤为重要。因此本模型结果支持进一步验证的候选关联，尚不能确认临床预测价值。')
h('五 任务四 主要实验与结果报告')
hh('1 实验设计与纳入流程')
p('主实验固定thalach为唯一主要终点，以疾病组减无疾病组为差值方向。先核对组别和缺失，再画分布图，最后进行双侧Welch t检验并报告均值差与95% CI。主分析为未调整完整病例比较，年龄、性别与中心调整用于后续敏感性分析。')
table(['组别','原始人数','心率缺失','缺失率','分析人数'],[['疾病组',509,35,'6.88%',474],['无疾病组',411,20,'4.87%',391],['合计',920,55,'5.98%',865]])
p('各受试者仅贡献一行，两组不存在配对关系。Welch不要求方差齐性。直方图和箱线图用于检查分布、尾部和离群值；本次不根据正态性检验p值机械切换方法，也不为获得显著性而删除离群记录。大样本支持均值的近似推断，但不能纠正选择偏倚。')
fig('fig1_distribution.png','图2 两组最大运动心率分布与箱线图')
hh('2 描述统计与主要检验')
ds=pd.read_csv(R/'descriptive.csv',index_col=0)
table(['组别','n','均值±标准差','中位数','四分位区间'],[[('疾病组' if k==1 else '无疾病组'),int(v['count']),f'{v["mean"]:.2f} ± {v["std"]:.2f}',f(v['median']),f'[{v.q25:.2f}, {v.q75:.2f}]'] for k,v in ds.iterrows()])
p(f'疾病组相对无疾病组均值差为{w["diff"]:.2f}次/分钟，95% CI [{w["lo"]:.2f}, {w["hi"]:.2f}]；Welch t={w["t"]:.3f}，ν={w["df"]:.2f}，双侧p={w["p"]:.3g}。p小于0.05，拒绝H0，且区间完全位于0以下。上述差值就是原始单位效应量，不能只用“显著”替代它。')
u=j['mannwhitney'];p(f'作为分布稳健性补充，Mann–Whitney U={u["U"]:.1f}，双侧p={u["p"]:.3g}。该分析与均值比较指向相同的组间分布差异，但两者检验目标不同，不将U检验的p值解释为均值差区间。')
hh('3 统计意义 实际意义与因果边界')
p('统计意义：在检验条件成立时，本数据为两组总体均值差异提供强证据。实际意义：约20.5次/分钟的组间差异幅度值得进一步研究，但课程未提供临床最小重要差异，不能从小p值直接断言临床价值。组间分布仍有重叠，均值差不等于个体诊断准确率。因果边界：横断面观察资料缺少随机分配和明确时间先后，不能推断疾病导致心率降低、低心率导致疾病或治疗有效。')
h('六 任务五 混杂 敏感性与退出卡')
hh('1 调整模型与中心分层实验')
p('年龄可能同时关联疾病状态和运动心率；性别可能关联疾病构成与运动能力；中心可能代表不同转诊人群、流程与病例构成。实验依次拟合thalach~disease、thalach~disease+age+sex及thalach~disease+age+sex+C(site)，使用HC3异方差稳健标准误，再按中心计算Welch均值差。协变量依据研究问题选定，不依据单变量p值筛选。')
table(['模型','n','疾病组均值差','95% CI','p值'],[[{'unadjusted':'未调整OLS','age_sex':'调整年龄与性别','full':'再调整中心'}[k],v['n'],f(v['diff']),f'[{v["lo"]:.2f}, {v["hi"]:.2f}]',f'{v["p"]:.3g}'] for k,v in j['models'].items()])
fig('fig2_forest.png','图3 未调整 调整与中心分层的均值差及95%置信区间')
v=j['models']['full'];p(f'调整年龄、性别与中心后，均值差为{v["diff"]:.2f}次/分钟，95% CI [{v["lo"]:.2f}, {v["hi"]:.2f}]。调整前后差值幅度的变化说明病例构成可能解释部分未调整关联；不能将差值变化直接视为已证明混杂的因果比例。图中各中心区间宽度与样本组成有关，不能根据“一组显著、另一组不显著”判断中心间效应差异；需要预定的交互作用检验。')
hh('2 缺失机制与未测量因素')
mc=pd.read_csv(R/'missing_comparison.csv')
table(['心率记录','n','平均年龄','男性比例','疾病比例'],[[('缺失' if str(v['missing']).lower()=='true' else '完整'),int(v.n),f(v.age_mean),f'{v.male_pct:.1f}%',f'{v.disease_pct:.1f}%'] for _,v in mc.iterrows()])
p('缺失与完整者的已观测组成若不同，就需要警惕完整病例选择偏倚；即使这些变量相近，也不能证明完全随机缺失。分中心缺失计数保存在结果目录。当前未作插补，因为缺失机制和充分辅助信息尚未建立。后续可在合理的随机缺失假设下多重插补，再与完整病例估计比较，并对非随机缺失作偏移敏感性分析。')
p('用药尤其影响心率反应的药物、运动能力、疾病严重程度和检测方案可能影响估计，但并非均有字段可用，不能声称已控制。HC3处理异方差，中心固定效应控制中心平均水平，它们均不自动消除未测量混杂、复杂聚类或模型形式错误。未来需收集用药和运动负荷信息，并考虑年龄非线性。')
hh('3 多重比较的计算与控制')
p('如果20个H0全部为真、检验相互独立且各α=0.05，则完全不出现假阳性的概率为0.95²⁰，至少一次假阳性的概率为1−0.95²⁰≈64.15%。指标相关时此精确数值不成立，但选择性报告仍会高估效应。这个概率不是某一个显著发现为假的概率。')
p('确认性分析应事先确定主要终点并完整报告。若20项都属于同一确认性检验族，可用Holm法逐步控制家族错误率，或用Bonferroni阈值0.05/20=0.0025。大规模探索可说明假设后使用Benjamini–Hochberg控制FDR。本报告主检验唯一；其余相关、分类与回归检验均标为探索性，不因多个小p值而增加确认性主张。')
hh('4 主张 证据 推理 边界')
p('主张：在本数据心率记录完整的受试者中，疾病组最大运动心率平均较低，双侧Welch检验拒绝两组总体均值相同的H0。')
p(f'证据：疾病组n=474，无疾病组n=391；均值128.26与148.80次/分钟，均值差−20.54，95% CI [−23.73, −17.35]，p={w["p"]:.3g}。')
p('推理：差值为负、置信区间不含0，表明差异方向和幅度具有统计证据；调整后结果提示需要考虑年龄、性别和中心构成。')
p('边界：观察性完整病例关联不能排除未测量混杂与选择偏倚，不能单凭此结果断定临床重要性、个体预测表现或因果作用。')
h('七 课后作业 另一个完整假设检验设计')
hh('1 科学问题与前瞻性方案')
p('我另选“规律步行干预是否改变轻度高血压成年患者12周收缩压”作为设计题。拟纳入18—75岁、降压药方案稳定的轻度高血压成人，按1∶1随机分配到常规管理加步行指导组或常规管理组。两组均按统一仪器和流程测量基线及12周收缩压，以12周收缩压为唯一主要终点；每人为一个单位。该部分是尚未开展的方案，不报告虚构受试者或疗效数据。')
p('令Δ为按基线收缩压调整的12周组间平均差（干预减对照），H0：Δ=0，H1：Δ≠0。采用双侧α=0.05，因为获益与潜在反向变化均需识别。解释变量为随机组别（二分类），结局为12周收缩压（连续，mmHg），基线收缩压与年龄为连续协变量，性别和中心为分类协变量。')
hh('2 方法 假设与混杂控制')
p('首选ANCOVA：12周收缩压~随机组别+基线收缩压+年龄+性别+中心。关键条件为受试者间独立、条件均值模型合理以及无严重数据错误；可用稳健标准误。备选为分组自助法的调整均值差区间；若有多次随访，采用重复测量混合模型。不可用独立t检验比较同一人的前后值。')
p('年龄、基线收缩压和降压药调整都可能影响结局。随机分配降低基线混杂，按基线血压与中心分层随机；事先记录用药和方案变化，按意向治疗分析。依从性差和失访可能产生偏倚，应记录原因，采用适当插补并进行非随机缺失敏感性分析；遵从方案分析仅作补充。')
hh('3 报告计划 样本量与边界')
p('报告各组随机人数、完成随访人数、失访原因、基线及12周描述统计、调整均值差、95% CI和精确p值。以5 mmHg作为待临床论证的规划差异，假设标准差12 mmHg、power=80%、双侧α=0.05，保守独立均值近似n≈2×(1.96+0.84)²×12²/5²≈90.3，向上取91人/组；再考虑10%失访为102人/组，共204人。正式立项需据先导数据用精确方法修订，不能把此近似计划当作已完成研究。')
p('只设一个主要终点；次要终点和亚组预先登记，若作确认性检验采用Holm控制。结论区分统计差异、达到临床阈值的幅度与患者获益；随机试验若依从、失访和实施条件合理，可支持分配干预的因果效应，但不能无条件外推至所有人群或所有步行强度。')
h('八 复现步骤与要求覆盖')
p('本报告覆盖工作单任务1—5；补充幻灯片要求的纳入流程与缺失特征比较，并按教案完成另选生物医学问题的课后研究设计。课程材料中未提供可运行实验代码，analysis/run_analysis.py为本次新增分析脚本，analysis/build_report.py为文档生成脚本，原始工作单和数据保留。')
p('在VS Code中打开本作业目录，选择包含numpy、pandas、scipy、matplotlib、statsmodels和python-docx的Python解释器；先运行analysis/run_analysis.py，再运行analysis/build_report.py。脚本从自身路径定位数据，不依赖终端当前位置；本次安装的补充依赖位于.tmp/packages，分析脚本自动加载。结果目录保留JSON数值、CSV表及300 dpi黑白图。')
p('运行环境：Python 3.12；主要包版本为'+ '，'.join(f'{k} {v}' for k,v in j['versions'].items())+'。主检验和所有补充估计由CSV重新计算；power图为理论计算，无随机抽样种子需求。')
p('课程依据：Hypothesis.md第八至九节；V3/README.md；V3/data/README.md；V3/student-worksheet.md及同名Word工作单；V3/lesson-plan.md；V3/slides/hypothesis-test-pbl.pptx。教师参考只作为数值交叉核对，未替代原始数据计算。')
for z in d.paragraphs:
 for run in z.runs:run.font.color.rgb=RGBColor(0,0,0)
d.save(ROOT/'作业第五讲.docx')
print(ROOT/'作业第五讲.docx')
