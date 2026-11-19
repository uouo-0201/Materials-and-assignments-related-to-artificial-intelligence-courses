"""Build the approved Lesson 2 worksheet and reference, plus reproducibility QA.

Only writes inside V3. The student data is a byte-for-byte copy of the course CSV.
Run from any directory: python build_v3.py
"""
from pathlib import Path
import hashlib
import json
import shutil
import pandas as pd
import numpy as np
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
REVIEW = ROOT / 'review'
SOURCE = ROOT.parent / 'assets/pbl-understanding-data/heart-disease-four-site.csv'
for p in (DATA, REVIEW): p.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SOURCE, DATA / SOURCE.name)
assert SOURCE.read_bytes() == (DATA / SOURCE.name).read_bytes()
DF = pd.read_csv(DATA / SOURCE.name)
FEATURES = [c for c in DF if c not in ['record_id', 'site', 'num']]
SITES = ['Cleveland', 'Hungary', 'Switzerland', 'VA Long Beach']
assert DF.shape == (920, 16) and len(FEATURES) == 13
assert DF['num'].notna().all() and DF['cp'].notna().all()
CN = {'record_id':'教学编号','site':'来源中心','age':'年龄','sex':'性别编码','cp':'胸痛类别',
      'trestbps':'静息血压','chol':'胆固醇','fbs':'血糖阈值','restecg':'静息心电图',
      'thalach':'最大心率','exang':'运动心绞痛','oldpeak':'ST下降','slope':'ST斜率',
      'ca':'显影血管数','thal':'灌注检查','num':'原始疾病标签'}

def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def csv(name, rows):
    pd.DataFrame(rows).to_csv(DATA/name, index=False, encoding='utf-8-sig')

csv('teaching-followup.csv', [dict(person='甲',months=12,event=1),dict(person='乙',months=12,event=0)])
csv('teaching-stage-count.csv',[dict(case='甲',stage='I',mutations=0),dict(case='乙',stage='II',mutations=1),dict(case='丙',stage='III',mutations=4)])
csv('teaching-instruments.csv',[dict(sample='同一标准样本',instrument=k,replicate=i+1,value=v) for k,vals in [('甲',[100,101,99]),('乙',[120,121,119])] for i,v in enumerate(vals)])
write_json(DATA/'teaching-matrix-scenarios.json', {
    'teaching_only':True,
    'single_cell':{'donors':3,'cells_per_donor':100,'genes_per_cell':20000,'values':'normalized continuous expression','retain':['donor_id','batch']},
    'imaging':{'subjects':20,'images_per_subject':2,'height':64,'width':64,'channels':1,'retain':['subject_id']}})

# Teacher-only numeric truth; no worked results are distributed as student answers.
y = (DF.num > 0).astype(int)
recode = DF.cp.map({1:10,2:20,3:40,4:80})
g = DF.groupby('site')
missing = g[FEATURES].apply(lambda x: x.isna().sum()).reindex(SITES)
missing.to_csv(REVIEW/'verified-missing-counts.csv',encoding='utf-8-sig')
quality=[]
for site in SITES:
    x=DF[DF.site.eq(site)]
    positive=int(x.num.gt(0).sum())
    valid=x.chol.dropna()
    nonzero=valid[valid.ne(0)]
    quality.append({'site':site,'n':len(x),'chol_missing':int(x.chol.isna().sum()),
        'ca_missing':int(x.ca.isna().sum()),'chol_zero':int(x.chol.eq(0).sum()),
        'positive':positive,'positive_pct':100*positive/len(x),
        'chol_n_with_zero':len(valid),'chol_mean_with_zero':float(valid.mean()),
        'chol_n_without_zero':len(nonzero),'chol_mean_without_zero':float(nonzero.mean()) if len(nonzero) else None})
complete=DF.dropna(subset=FEATURES)
retention=[{'site':s,'original_n':int(DF.site.eq(s).sum()),'complete_n':int(complete.site.eq(s).sum()),
            'original_mix_pct':100*DF.site.eq(s).mean(),'complete_mix_pct':100*complete.site.eq(s).mean()} for s in SITES]
c=DF[DF.site.eq('Cleveland')][['age','trestbps','chol']]
z=(c-c.mean())/c.std(ddof=0)
scale=[{'variable':v,'n':len(c),'mean':float(c[v].mean()),'sd_ddof0':float(c[v].std(ddof=0)),
        'z_mean':float(z[v].mean()),'z_sd_ddof0':float(z[v].std(ddof=0)),
        'first_raw':float(c[v].iloc[0]),'first_z':float(z[v].iloc[0])} for v in c]
truth={'shape':list(DF.shape),'features':FEATURES,'age_mean':float(DF.age.mean()),
       'cp_mean':float(DF.cp.mean()),'recoded_cp_mean':float(recode.mean()),
       'cp_counts':{str(int(k)):int(v) for k,v in DF.cp.value_counts().sort_index().items()},
       'positive_n':int(y.sum()),'positive_proportion':float(y.mean()),
       'contingency':pd.crosstab(DF.cp,y).values.tolist(),'quality':quality,'retention':retention,
       'complete_total':len(complete),'standardization':scale,
       'instrument_mean_difference':20,'cell_matrix':[300,20000],'image_matrix':[40,4096],
       'data_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
assert truth['complete_total']==299 and truth['positive_n']==509
assert np.allclose(z.mean(),0,atol=1e-12) and np.allclose(z.std(ddof=0),1)
assert recode.notna().all() and sorted(recode.value_counts())==sorted(DF.cp.value_counts())
write_json(REVIEW/'verified-results.json',truth)

NAVY='243E50'; TEAL='306B72'; PALE='EAF1F2'; LIGHT='F4F6F7'; GREY='59636B'

def font_run(run,size=None,bold=None,color=None):
    run.font.name='Arial'
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
    if size: run.font.size=Pt(size)
    if bold is not None: run.bold=bold
    if color: run.font.color.rgb=RGBColor.from_string(color)

def new_doc(kind):
    d=Document(); s=d.sections[0]
    for border in d.styles.element.xpath('.//w:pBdr'):
        border.getparent().remove(border)
    s.page_width=Cm(21);s.page_height=Cm(29.7)
    s.top_margin=s.bottom_margin=Cm(1.6);s.left_margin=s.right_margin=Cm(1.65)
    s.header_distance=Cm(.65);s.footer_distance=Cm(.65)
    for name,size,col in [('Normal',10.5,'20292F'),('Title',23,'000000'),('Subtitle',11,GREY),('Heading 1',16,NAVY),('Heading 2',12,TEAL),('Heading 3',10.5,TEAL)]:
        st=d.styles[name];st.font.name='Arial';st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string(col)
        st.font.italic=False
        st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
        st.paragraph_format.space_after=Pt(5)
        st.paragraph_format.line_spacing=Pt(15) if name=='Normal' else 1.08
        snap=OxmlElement('w:snapToGrid');snap.set(qn('w:val'),'0');st.element.get_or_add_pPr().append(snap)
        if name.startswith('Heading'):st.paragraph_format.keep_with_next=True
    d.styles['Normal'].paragraph_format.widow_control=True
    d.core_properties.title='理解数据 '+kind
    d.core_properties.subject='第2讲 变量类型与数据类型'
    d.core_properties.author='AI4BiomedicalDS'
    fp=s.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    rr=fp.add_run('第2讲 · '+kind+'   ');font_run(rr,8,color=GREY)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');fp._p.append(field)
    return d

def p(d,text='',style=None,bold=False,size=None,keep=False):
    par=d.add_paragraph(style=style)
    r=par.add_run(text);font_run(r,size,bold if bold else None)
    par.paragraph_format.keep_with_next=keep
    snap=OxmlElement('w:snapToGrid');snap.set(qn('w:val'),'0');par._p.get_or_add_pPr().append(snap)
    if not style:par.paragraph_format.keep_together=True
    return par

def title(d,txt,sub):
    p(d,txt,'Title');p(d,sub,'Subtitle')

def heading(d,txt,level=1,new=False):
    h=d.add_paragraph(txt,f'Heading {level}')
    if new:h.paragraph_format.page_break_before=True
    return h

def table(d,headers,rows,widths=None,height=None,size=9.5):
    t=d.add_table(rows=1,cols=len(headers));t.style='Table Grid';t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths:
        for c,w in zip(t.columns,widths):c.width=Cm(w)
    for i,h in enumerate(headers):t.rows[0].cells[i].text=h
    for row in rows:
        cells=t.add_row().cells
        for c,txt in zip(cells,row):c.text=str(txt)
    for ri,row in enumerate(t.rows):
        if widths:
            for cell,w in zip(row.cells,widths):cell.width=Cm(w)
        trPr=row._tr.get_or_add_trPr(); no=OxmlElement('w:cantSplit');trPr.append(no)
        if ri==0:
            repeat=OxmlElement('w:tblHeader');trPr.append(repeat)
        if ri and height:
            row.height=Cm(height);row.height_rule=WD_ROW_HEIGHT_RULE.AT_LEAST
        for ci,cell in enumerate(row.cells):
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcPr=cell._tc.get_or_add_tcPr()
            mar=OxmlElement('w:tcMar')
            for k,v in [('top','55'),('bottom','55'),('left','85'),('right','85')]:
                x=OxmlElement('w:'+k);x.set(qn('w:w'),v);x.set(qn('w:type'),'dxa');mar.append(x)
            tcPr.append(mar)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),PALE);tcPr.append(sh)
            for par in cell.paragraphs:
                par.paragraph_format.space_after=Pt(1);par.paragraph_format.space_before=Pt(0)
                par.paragraph_format.line_spacing=Pt(size+3)
                par.paragraph_format.keep_with_next=(ri==0)
                snap=OxmlElement('w:snapToGrid');snap.set(qn('w:val'),'0');par._p.get_or_add_pPr().append(snap)
                for r in par.runs:font_run(r,size,ri==0,NAVY if ri==0 else None)
    return t

def answer(d,prompt,label='我的解释与证据',height=1.5):
    p(d,prompt,keep=True)
    return table(d,[label],[['']],height=height,size=10)

def small(d,text):return p(d,text,size=9)

def sheet():
    d=new_doc('学生工作单')
    # Page 1: concepts before student paperwork.
    title(d,'理解数据','第2讲学生工作单 · V3 · 先学习，再实验，最后解释')
    p(d,'完成本工作单后，你应能用数据回答：什么是变量？变量类型如何影响分析方法？生物医学数据为什么需要特别检查？',bold=True)
    heading(d,'一 我要学会什么')
    p(d,'先用学习地图确定目标，再填写3W。右侧能力是你在汇报时应当展示的表现；不要求背诵整份参考资料。')
    table(d,['关键概念与技能','学会后的表现'],[
        ['观察单位、变量与研究角色','说明一行代表谁、一列测量什么；区分候选特征、结局、编号和来源。'],
        ['连续、计数、二分类、多分类、有序、时间','依据测量含义判断类型，解释哪些运算有意义；理解随访时间还需要事件状态。'],
        ['数据矩阵与高维结构','解释患者×指标、细胞×基因、图像×像素；区分记录数、独立对象数和特征数。'],
        ['均值、列联表、Logistic、标准化','给出合适的用途和条件；识别类别编码、结局泄漏及尺度变化。'],
        ['缺失、异常、批次、类别不平衡、测量误差','用实际结果指出质量风险，区分观察到的现象与尚待核实的原因。']], [5.1,12.6],size=10)
    heading(d,'先分清三个容易混淆的地方',2)
    p(d,'变量类型看“测量了什么”，不只看是否存成数字。研究角色看“准备回答什么问题”，同一变量的角色可能改变。高维说的是整张矩阵的结构，并不是与连续、分类互斥的一种单列类型。')
    heading(d,'贯穿全课的问题',2)
    p(d,'心血管研究团队得到四个中心的历史记录，希望描述患者特征，并为后续区分疾病状态的研究准备数据。你会如何界定研究对象、选择分析、处理质量疑问？哪些发现会使团队暂缓某项分析？')
    p(d,'最终建议可选：A 保留四中心及全部候选字段，说明处理条件；B 限定有依据的中心或字段，说明取舍；C 证据不足，暂缓拟议分析，说明需补充什么。')
    small(d,'学习安排：课堂启动45分钟（学习目标、3W、实验1）；课后90分钟（学习15、实验2为25、实验3为30、迁移10、汇报准备10）；汇报课堂45分钟。每人独立完成，可以讨论和使用AI。')
    small(d,'只为教学与研究准备提出建议；本表不能直接证明因果关系、当前人群患病率或临床使用效果。')

    # Page 2.
    heading(d,'我的3W与数据起点',new=True)
    p(d,'3W指“我已经知道什么、还需要学会什么、将怎样学习和检验”。围绕三个课程问题各写短句；第三项写一个参考章节和一个实际行动，作为自己的学习计划。',keep=True)
    table(d,['课程问题','我已经知道什么？','我还需要学会什么？','我将阅读什么、检查什么或做什么实验？'],[
        ['什么是变量？','','',''],['类型如何影响方法？','','',''],['生物医学数据有何特殊性？','','','']], [2.8,4.0,4.5,6.4],height=1.45,size=10)
    small(d,'格式示例（另一情境）：已知血型是类别；不确定编号能否求均值；阅读参考R1，用改变血型编号的办法检验。')
    heading(d,'数据获取',2)
    p(d,'真实数据：data/heart-disease-four-site.csv。路径相对于V3文件夹；用Excel或Python打开均可。保留原文件，在副本上计算；CSV空单元表示缺失，0保留为原记录值。',size=9.5)
    p(d,'配套阅读：pbl-data-types-reference.docx；R1是概念，R2是字段字典，R3是方法和质量，R4是资源。教学示例也在data中。',size=9.5)
    p(d,'可选计算助手：在V3文件夹运行 python scripts/experiment_helper.py（使用课程已配置的pandas、numpy）。它生成数值表，不替你解释；也可用Excel自行计算。学习时间按工具已可用估计，读懂比较和核对结果是必做任务。',size=9.5)
    small(d,'数值表可直接用自己运行得到的对应结果替换，无需抄录数值；解释和判断须自己写。')
    p(d,'表 A1 四中心数据概况。每行一个来源中心；人数列为文件记录数，未核实跨中心身份。来源：课程本地数据。',keep=True,size=9)
    table(d,['来源中心','Cleveland','Hungary','Switzerland','VA Long Beach'],[['记录数',303,294,123,200]], [3.3,3.4,3.4,3.4,4.2],size=9)
    p(d,'数据身份：查看表 A1、数据文件与参考R2/R4，在下面写出来源、记录数、候选特征数及另外三列的用途。说明为何“记录数”不自动等于“独立患者数”。',keep=True)
    table(d,['必须说明的项目','我的核对'],[
        ['来源名称、发布者、DOI或网址',''],['记录数、候选特征数、其他列',''],['一行的含义与身份核实限制','']], [5.2,12.5],height=.85,size=10)
    answer(d,'初步建议：根据表 A1及参考R2，在“贯穿全课的问题”的A、B、C中选一项，写一句理由及一项最可能改变建议的未知事实。','初步建议与待查事实',1.2)
    small(d,'AI可以解释概念或帮助写公式，但你须亲自运行或检查结果。至少手工核对一个计数或标准化值，并在实验2保留核对痕迹。')

    # Page 3.
    heading(d,'二 用实验检验理解',new=True)
    heading(d,'实验1 数字一定代表数量吗',2)
    p(d,'先学：变量类型、研究角色、类别编码（参考R1/R2）。在真实数据中观察各列取值，以“描述患者、准备疾病状态研究”为目的完成下表；这是全课唯一的逐列判断表。')
    p(d,'表 B1 逐列判断表。课堂先为每列填写类型与角色；课后读参考R3、做实验2，再在“分析用途与条件”中判断均值、卡方、Logistic及标准化的适用性。同类字段可引用一个已判断字段，只补不同的条件，避免重复写四遍。',keep=True)
    table(d,['字段','类型与角色（课堂）','分析用途与条件（实验2后）'],[
        [CN[c]+' ('+c+')','',''] for c in DF.columns], [4.2,5.0,8.5],height=.57,size=9.3)
    small(d,'方法判断针对“描述患者、准备疾病状态研究”。均值指平均原值；卡方指与另一个适当分类变量组成列联表；Logistic须区分结局和输入。可按“均值／卡方／Logistic／标准化”的顺序写短语。')
    p(d,'改名实验：复制胸痛类别，把1、2、3、4分别改为10、20、40、80。比较改名前后的均值，以及同一语义类别的频数；把两列频数并排保存在自己的实验结果中。',bold=True,size=10)
    answer(d,'用胸痛改名实验的两个均值和一类胸痛的前后计数作证据，写出哪些量改变、哪些没有改变，以及这对“类别编号可以平均”的说法意味着什么。','改名实验的数值与解释',1.6)

    # Page 4.
    heading(d,'实验2 哪些分析有意义',new=True)
    p(d,'先学：均值与比例、列联表、二分类Logistic（参考R3）。使用全部920条记录；本课定义疾病状态y：原始标签num=0时y=0，num>0时y=1。这里只讨论分组与表示，不计算p值、不拟合模型。')
    heading(d,'比较三个均值',2)
    p(d,'计算年龄均值、原始胸痛编码均值及y的均值。把实验1已经算出的胸痛均值直接用于比较，写明每个结果代表什么；若没有合适的研究含义，请说明理由。',keep=True)
    table(d,['计算对象','数值与单位或分母','在研究中能解释为什么？'],[
        ['年龄','',''],['胸痛原编号','',''],['疾病状态y（0/1）','','']], [4.2,5.0,8.5],height=.85,size=10)
    heading(d,'从频数到方法',2)
    p(d,'表 B2 胸痛类别×疾病状态。用真实数据填写频数，每行是一类胸痛，合计须覆盖920条记录。比较这两个变量的分布时，卡方是否为候选方法？把一个仍需检查的条件写在表后。',keep=True)
    table(d,['胸痛原编号','y=0记录数','y=1记录数'],[[k,'',''] for k in [1,2,3,4]], [5.9,5.9,5.9],height=.57,size=10)
    answer(d,'根据表 B2写出卡方比较的对象及一项使用条件。再手工核对一行频数或合计，注明核对方式；把适用条件补入表 B1。','方法判断与手工核对',1.2)
    heading(d,'为后续Logistic研究定义输入与输出',2)
    p(d,'利用参考R2的含义，为区分y=0与y=1写一个数值预测变量、一个分类预测变量及其表示方式，并指出一个不能直接用来预测y的字段及理由。用数据中的具体字段回答，同时说明预测时该信息是否可获得。',keep=True)
    table(d,['研究角色','字段、表示方式与必要条件'],[
        ['数值预测变量',''],['分类预测变量',''],['不能直接作为输入的字段','']], [5.0,12.7],height=.85,size=10)

    # Page 5.
    heading(d,'实验2 标准化改变了什么',new=True)
    p(d,'先学：标准化改变数值尺度，是否需要它取决于分析方法（参考R3）。只取Cleveland的303条记录，对年龄、静息血压、胆固醇分别计算z=(x−均值)/标准差。标准差统一使用分母n，即Excel的STDEV.P或Python的ddof=0。')
    p(d,'表 B3 尺度比较。每行一个变量；均值和标准差都由同一批Cleveland记录计算。填转换前后的统计量，原单位见参考R2，z无单位；结果保留两位小数。',keep=True)
    table(d,['变量','原均值','原标准差','z均值','z标准差'],[
        ['年龄','','','',''],['静息血压','','','',''],['胆固醇','','','','']], [4.1,3.4,3.4,3.4,3.4],height=1.1,size=10)
    answer(d,'核对计算：找到Cleveland-001的年龄，代入你计算的年龄均值与标准差，写出代入式和结果，并与软件结果比较。','一个可复核的标准化值',1.7)
    answer(d,'解释变化：结合表 B3，说明三个变量的尺度发生了什么变化，原来的测量含义是否改变。再判断标准化能否处理真实四中心数据中的空缺或中心差异，并解释理由。','尺度、含义与标准化的边界',2.8)
    p(d,'把方法判断留在一个地方：现在完成表 B1的“分析用途与条件”。至少用一个数值字段和一个类别字段说明标准化或编码的用途；同类字段引用即可，不再另写解释。')
    heading(d,'实验结果怎样保存',2)
    p(d,'保留能复核实验1至3的Excel表或Python结果，标出数据范围、单位和缺失处理。工作单中的表就是汇报材料；较大的频数表、缺失表或图可以另附，不需要把同一解释再写成报告。')
    small(d,'本次是描述与尺度实验，不估计模型泛化性能，因此不划分训练集与测试集。将来若评估预测模型，均值、标准差等参数应只从训练数据估计，再应用到验证或测试数据。')

    # Page 6.
    heading(d,'实验3 处理数据会改变结论吗',new=True)
    p(d,'先学：缺失、异常、类别构成、来源差异和测量误差（参考R3）。始终区分“看到了什么”“可能是什么原因”和“还需要什么证据”。所有比较使用原数据的副本。')
    p(d,'表 C1 分中心检查。先生成13个候选特征的缺失计数表，再把胆固醇与血管数的计数填入本表；计算各中心y=1的比例。每行一个中心，阳性比例以该中心记录数为分母；缺失只填计数。',keep=True)
    table(d,['中心','记录数','胆固醇\n缺失数','血管数\n缺失数','胆固醇\n零值数','y=1\n比例%'],[
        [s,int(DF.site.eq(s).sum()),'','','',''] for s in SITES], [3.9,2.1,2.7,2.7,2.7,3.6],height=.65,size=9)
    p(d,'表 C2 胆固醇敏感性比较。分别保留零值、临时排除零值后算均值；两种情况都排除空单元，其他字段不参与筛选。每格填“参与均值的记录数；均值mg/dL”；无有效记录时写“0；不可计算”。排除零值只是检验影响，并不证明零值的成因。',keep=True)
    table(d,['中心','保留零值：记录数；均值','排除零值：记录数；均值'],[[s,'',''] for s in SITES],[4.3,6.7,6.7],height=.65,size=9.5)
    p(d,'表 C3 完整记录筛选的代价。仅删除13个候选特征中存在空单元的记录，零值仍保留；填写各中心剩余数与筛选后的中心占比（分母为全部剩余记录数）。与表 A1的原始构成比较。',keep=True)
    table(d,['中心','完整记录数','筛选后中心占比%'],[[s,'',''] for s in SITES],[5.9,5.9,5.9],height=.65,size=9.5)
    answer(d,'解释后果：引用表 C1至C3的数字，写出两项发现及各自影响。其中须比较Cleveland筛选前后的占比，并说明表 C1的中心阳性比例差异是否足以证明技术批次效应。','两项发现、分析后果与待查原因',2.2)
    small(d,'再检查一个真实极端值（例如胆固醇的最大值），把它及是否应删除的理由用于最终建议。没有复测、校准或原始记录核查时，不能把“异常”自动判定为“错误”。')

    # Page 7.
    heading(d,'迁移 同一思路能用到新数据吗',new=True)
    p(d,'先学：有序与计数、随访时间与事件状态、矩阵与独立对象、测量误差（参考R1/R3）。表 D1是完整的教学示例输入，不属于920条真实记录，也不用于疾病推断。')
    p(d,'表 D1 五个教学情境。按每行输入完成对应判断，每格写关键词、短句或矩阵维度；不需要额外寻找数据。',keep=True)
    table(d,['情境与已给输入','你要解决的问题','我的判断及依据'],[
        ['病期与计数：甲、乙、丙的分期为I、II、III；突变数为0、1、4。','哪一列是有序、哪一列是计数？“III与II之差”等同于“II与I之差”需要什么依据？',''],
        ['随访：甲12个月发生事件；乙观察到12个月仍未发生事件。','相同的12个月能否当作相同结局？需要同时保留哪两列？',''],
        ['单细胞：3位供者，每人100个细胞，每细胞20000个基因的归一化表达值；有供者号与批次。','细胞×基因矩阵多大？有多少供者？单列连续测量与高维结构有什么区别？',''],
        ['影像：20位受试者，每人2张64×64灰度图；有受试者号。','按图像展开为像素矩阵时有多少行、多少列？为何图像数不等于独立受试者数？',''],
        ['仪器：同一标准样本，甲测得100、101、99；乙测得120、121、119（任意单位）。','计算两仪器均值差。这比中心阳性比例差多了什么证据？没有标准真值时能否判断哪台准确？','']], [6.1,5.8,5.8],height=3.0,size=10)
    answer(d,'把边界说清楚：从表 D1选择一项研究需求，指出真实心脏病表缺少的具体字段或链接信息。写出团队取得什么资料后才能开始回答这项问题。','真实数据的能力边界',2.1)

    # Page 8.
    heading(d,'三 向全班解释我的学习',new=True)
    p(d,'每人准备5–8分钟，用完成的工作单和实验结果讲解；不另做幻灯片。课后只写提纲与建议，汇报课开始用5分钟熟悉讲解，再随机邀请1至2位同学，其他同学依据证据提问。讲解顺序可以自定，但必须回答三个课程问题。')
    p(d,'汇报提纲：为每个课程问题选一项自己完成的实验或迁移结果，写关键词提示即可。指出要展示的表或计算、它支持的解释，以及一个适用限制；不抄写实验全文。',keep=True)
    table(d,['课程问题','我要展示的结果','我会怎样解释及限定结论'],[
        ['什么是变量？','',''],['变量类型如何影响方法？','',''],['生物医学数据有何特殊性？','','']], [4.2,5.1,8.4],height=1.3,size=10)
    answer(d,'最终建议：回到“贯穿全课的问题”的A、B、C，选择保留全部、限制范围或暂缓分析。用约120–180字或等量要点说明对象范围、变量与方法选择、两项质量证据（含极端值判断）、优先核实的资料及一项本表不能回答的新问题；引用实验数值即可，不重抄计算。','给研究团队的数据使用建议',3.5)
    heading(d,'汇报前自检',2)
    p(d,'逐项自查，能做到的打勾；暂不能解释的先回到相应实验修正。')
    p(d,'☐ 我能用具体字段说明类型与角色，并解释胸痛改名实验。',size=9.5)
    p(d,'☐ 我能讲清均值、卡方、Logistic输入和标准化的适用条件。',size=9.5)
    p(d,'☐ 我能复核一个计算，区分质量现象、成因推测与使用边界。',size=9.5)
    p(d,'☐ 我能指出哪项证据会改变建议，并回答同学的追问。',size=9.5)
    answer(d,'汇报课堂讨论后（3分钟，计入汇报课）：记录一个具体质疑及证据，说明自己修改了哪项解释；若保持原判断，也要说明理由。','讨论后修正记录',1.5)
    small(d,'提交：完成的工作单＋可复核的实验结果。数据来源、记录数、特征数见“数据身份”，变量类型见表 B1，质量问题见实验3与最终建议，已覆盖课程作业五项要求。')
    d.save(ROOT/'pbl-data-types-student-worksheet.docx')

def reference():
    d=new_doc('学习参考')
    title(d,'理解数据','第2讲学习参考 · 与V3学生工作单配套')
    p(d,'本资料用于解决3W中发现的知识缺口。先读与当前实验有关的部分，再用真实数据检验自己的理解。字段字典解释测量含义，不代替你的类型判断。')
    heading(d,'R1 变量与数据矩阵')
    p(d,'变量是对象之间可能变化的属性，例如某次检查测得的浓度；变量值是某个对象的具体记录。观察单位说明一行代表患者、一次就诊、一个细胞还是一幅图。重复记录可能属于同一人，因此表格行数不自动等于独立样本数。')
    table(d,['概念','如何理解与识别'],[
        ['连续量与计数','连续量反映测量的大小，即使按整数记录仍可能来自连续测量；计数是次数或个数，通常取非负整数。不要仅凭小数点判断。'],
        ['二分类与多分类','两个类别是二分类；更多无自然次序的类别是无序多分类。数字可以只作标签，换编号不应改变类别本身。'],
        ['有序类别','等级有先后，但相邻等级差距未必相等。只有额外的测量依据才能支持等距运算，不能从编号推导。'],
        ['时间与删失','时间变量要说明起点、终点和单位。随访结束仍未发生事件时，知道的是事件时间超过观察时长；必须保留事件状态。'],
        ['特征、结局、元数据','这些是研究角色。特征是输入；结局是希望解释或预测的对象；编号、中心等元数据用于链接或描述来源，是否参与分析取决于问题。'],
        ['高维结构','指变量很多的矩阵，常需同时考虑样本数n与特征数p。基因表达等单列可为连续量，而整张矩阵是高维数据。']], [4.0,13.7],size=10)
    heading(d,'先定义矩阵的行与列',2)
    table(d,['数据表示','一行与一列','必须保留的链接'],[
        ['患者×临床指标','行是患者或就诊记录；列是指标','患者、就诊、测量时点'],
        ['细胞×基因','行是细胞；列是基因测量','供者、样本、测序批次'],
        ['图像×像素或特征','行是图像；列是像素值或提取特征','受试者、采集时点、设备']], [4.3,7.0,6.4],size=10)
    p(d,'解释矩阵大小时，把来源编号等元数据与测量特征分开计数。某些组学文件采用基因×样本方向，不能只凭文件行数认定样本数。')
    small(d,'相关阅读：课程课件第3–14页（变量与取值）、第15–18页（维度与矩阵）；具体文件路径及官方来源见R4。')

    heading(d,'R2 真实数据字段字典',new=True)
    p(d,'本地表含920条记录、16列：13个候选特征＋原始标签num＋来源中心site＋教学编号record_id。下表每行解释一个字段；“类型与角色”的判断由学生完成。')
    rows=[
        ['教学编号\nrecord_id','中心名与文件内行号组合；如Cleveland-001。不是可跨文件核实身份的患者ID。','教学添加'],
        ['来源中心\nsite','Cleveland、Hungary、Switzerland、VA Long Beach；按原处理文件添加。','来源名称'],
        ['年龄 age','年龄，按整数年记录。','年'],
        ['性别编码 sex','0=女；1=男，仅表示这份历史资料的记录方式。','0、1'],
        ['胸痛类别 cp','1=典型心绞痛；2=非典型心绞痛；3=非心绞痛性疼痛；4=无症状。','1、2、3、4'],
        ['静息血压 trestbps','入院时静息血压。','mmHg'],
        ['胆固醇 chol','血清胆固醇。','mg/dL'],
        ['血糖阈值 fbs','空腹血糖是否大于120 mg/dL；0=否，1=是。','0、1'],
        ['静息心电图 restecg','0=正常；1=ST-T波异常；2=符合所述左室肥厚标准。','0、1、2'],
        ['最大心率 thalach','运动检查中达到的最大心率。','次/分钟'],
        ['运动心绞痛 exang','是否运动诱发心绞痛；0=否，1=是。','0、1'],
        ['ST下降 oldpeak','运动相对静息的ST段下降；已查字典未明确给出可靠单位，不补猜。','单位未明确'],
        ['ST斜率 slope','运动峰值ST段斜率：1=上斜，2=平坦，3=下斜；不据编号推断等距风险。','1、2、3'],
        ['显影血管数 ca','荧光检查显影的主要血管数；字典范围0–3。','条'],
        ['灌注检查 thal','3=正常；6=固定缺损；7=可逆缺损。','3、6、7'],
        ['原始疾病标签 num','造影疾病状态。总说明给出0–4；本课按0与大于0派生二分类y。不能据这些编码认定统一疾病分期。','本地范围0–4']]
    table(d,['字段与文件列名','测量含义或编码说明','单位或范围'],rows,[4.2,10.8,2.7],size=9.3)
    small(d,'来源：UCI Heart Disease页面及原始heart-disease.names，结合本地文件。不同中心的实际取值与缺失状况须检查数据；在线摘要不是本地四中心文件的完整审计。')

    heading(d,'R3 方法选择与质量判断',new=True)
    heading(d,'均值与比例',2)
    p(d,'均值概括具有数量意义的取值；极端值可能使它偏移，必要时结合中位数及分布。若变量仅取0和1，均值等于取值1的比例。无序类别的编号均值通常不表达稳定的研究属性。')
    heading(d,'列联表与卡方',2)
    p(d,'列联表记录两个分类变量组合的频数。卡方独立性检验是判断关联的一种候选方法，需要合适的观察独立性、互斥类别及足够的期望频数；稀疏表可能需精确方法或有依据的合并。连续原值不能直接当成分类列联表，任意分箱还会损失信息。本课只判断适用性，不计算p值。[3]')
    heading(d,'二分类Logistic的输入与输出',2)
    p(d,'本课Logistic指二分类结局的模型。输入可以包含连续量、计数或分类变量；无序类别通常需指示变量表示。把有序等级作为单个数值输入会增加趋势或间距假设。输入必须在计划预测的时点可获得，不能包含结局本身或由结局直接推导的信息。本课不评估预测表现。[4]')
    heading(d,'标准化的用途和限制',2)
    p(d,'z=(x−均值)/标准差。以同一批数据、同一种标准差定义计算时，非恒定变量转换后均值约为0、标准差约为1。它改变量纲和数值尺度，不改变测量对象，不自动修复缺失、错误或来源偏差。是否需要标准化取决于方法、数值优化与正则化；不是所有Logistic分析都在数学上必须标准化。[2]')
    small(d,'实验统一用总体形式标准差（分母n；Excel STDEV.P；Python ddof=0）。若标准差为0，不用该公式。将来评估预测模型时，先分训练/验证/测试，再只用训练数据估计处理参数。')
    heading(d,'五类质量问题要分别判断',2)
    table(d,['问题','可观察到什么与还需核实什么'],[
        ['缺失','统计空单元、比例及来源分布；空缺不等于零。缺失原因和机制需要采集流程资料。'],
        ['异常','极端值或不合常识的值需要核对；可能是错误、真实极端或特殊亚组，不能默认删除。'],
        ['批次效应','技术来源造成系统差异。中心差异也可能来自患者构成；需要采集流程、共同标准样本等证据区分。'],
        ['类别不平衡','需说清标签定义、总体或亚组、各类人数与分母；不同分组口径可能得到不同判断。'],
        ['测量误差','复测反映重复性，共同标准样本可帮助比较仪器；没有标准真值或校准资料时，不能仅凭均值判断准确性。']], [3.1,14.6],size=9.5)

    heading(d,'R4 数据获取与阅读路径',new=True)
    p(d,'文件路径均相对于V3文件夹。真实数据与教学示例分开使用；核心计算不需要联网。')
    table(d,['材料','文件与用途'],[
        ['真实数据','data/heart-disease-four-site.csv；与上一级课程数据逐字节一致。'],
        ['分期与计数示例','data/teaching-stage-count.csv；3个教学对象。'],
        ['随访示例','data/teaching-followup.csv；event=1表示发生，0表示观察结束未发生。'],
        ['仪器重复测量','data/teaching-instruments.csv；同一标准样本、2台仪器各3次、任意单位。'],
        ['矩阵情境参数','data/teaching-matrix-scenarios.json；只提供人数、图像或细胞数、维度，不含真实组学或影像。'],
        ['可选计算助手','scripts/experiment_helper.py；运行后在experiment-results生成数值表，空均值须结合有效记录数解释。'],
        ['课程课件','../chap2_data.pptx；页码指文件中的幻灯片顺序。']], [4.1,13.6],size=9.5)
    heading(d,'怎样选读',2)
    table(d,['要解决的疑问','对应资源与阅读重点'],[
        ['类型与数据角色','R1/R2；课件3–14页，比较属性含义与存储值；UCI的Additional Variable Information。[1]'],
        ['矩阵与高维','R1；课件15–18页，先定义行列。PCA及维度灾难不是本课必做实验。'],
        ['方法与标准化','R3；StandardScaler说明中的公式、异常值敏感性及标准差定义；SciPy列联表说明；Logit的输入输出定义。[2–4]'],
        ['质量与来源差异','R3；课件25–30页，区分异常、缺失和重复；用实验3的实际证据检验解释。']], [4.1,13.6],size=9.5)
    heading(d,'来源与使用约定',2)
    small(d,'[1] Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease. UCI Machine Learning Repository. DOI: 10.24432/C52P4X. CC BY 4.0。\nhttps://archive.ics.uci.edu/dataset/45/heart+disease')
    small(d,'字段原始说明：https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/heart-disease.names')
    small(d,'[2] scikit-learn，StandardScaler（公式及Notes）。\nhttps://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html')
    small(d,'[3] SciPy，chi2_contingency（输入频数与Notes）。\nhttps://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html')
    small(d,'[4] statsmodels，Logit（endog与exog说明）。\nhttps://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Logit.html')
    small(d,'来源核查日期：2026-09-25。四个processed文件按行合并；本地预处理将?转为空单元，添加site和record_id，其余值保留。旧总说明另提及−9缺失标记，不能直接套用于当前CSV；当前CSV以空单元为缺失。')
    small(d,'网页摘要的303对应Cleveland；本课本地文件合计920。旧说明中的Hungarian标签频数与当前处理文件不完全一致，当前文件实际标签只有0、1，不能据旧说明还原疾病分期。零值、可疑值及来源差异留给实验核查。')
    d.save(ROOT/'pbl-data-types-reference.docx')

def design():
    objectives=[
      ('LO1','什么是变量？','解释观察单位、变量、值、角色与记录/患者的差别','实验1','A1','表 B1与数据身份'),
      ('LO2','连续变量；离散变量；二分类变量；多分类变量；有序变量；时间变量；高维变量','分类全体字段并在迁移中判断有序、时间、高维结构','实验1、迁移','A1,A4','表 B1、表 D1'),
      ('LO3','样本 × 特征；患者 × 临床指标；细胞 × 基因；图像 × 像素/特征','写出矩阵维度、独立对象数及链接需求','迁移','A4','数据身份、表 D1'),
      ('LO4','哪些变量可以求均值？哪些变量适合做卡方检验？哪些变量适合进入 logistic regression？哪些变量需要标准化？','解释均值含义、构造列联表、定义输入输出与说明尺度用途','实验2','A2','表 B1、B2、B3与解释'),
      ('LO5','缺失值；异常值；批次效应；类别不平衡；测量误差','量化质量现象与筛选影响，区分成因推测和证据','实验3、迁移','A3,A4','表 C1–C3、表 D1与建议'),
      ('LO6','作业选择一个公开生物医学数据集，写出：数据来源；样本数；特征数；主要变量类型；可能的数据质量问题','提交能复核的五项数据审查内容','数据身份、实验1、实验3','A1,A3','数据身份、表 B1、实验3及最终建议')]
    qspec=[('Q1','实验1：数字一定代表数量吗',['LO1','LO2','LO6'],['数据表','字典','表 A1'],'S1',25,'表 B1及改名实验','A1'),
      ('Q2','实验2：哪些分析有意义',['LO4'],['数据表','字典'],'B',25,'表 B2、B3和方法解释','A2'),
      ('Q3','实验3：处理数据会改变结论吗',['LO5','LO6'],['数据表','字典'],'C',30,'表 C1–C3和后果解释','A3'),
      ('Q4','迁移：同一思路能用到新数据吗',['LO2','LO3','LO5'],['表 D1'],'D',10,'表 D1和使用边界','A4')]
    ev=[{'id':eid,'packet':'S1','artifacts':paths,'context':context} for eid,paths,context in [
        ('数据表',['data/heart-disease-four-site.csv'],'920 records; 16 columns; four-source historical clinical data'),
        ('字典',['pbl-data-types-reference.docx'],'R2; each row is a field, with definition and units'),
        ('表 A1',['pbl-data-types-student-worksheet.docx'],'Four source counts, each row of input is a record, not verified unique patients'),
        ('表 D1',['data/teaching-followup.csv','data/teaching-stage-count.csv','data/teaching-instruments.csv','data/teaching-matrix-scenarios.json'],'Five fully specified synthetic examples; never merged into real data')]]
    qs=[]
    for id,question,los,eids,release,minutes,output,aid in qspec:
        qs.append(dict(id=id,question=question,objective_ids=los,concept_ids=los,required_learning=[o[2] for o in objectives if o[0] in los],
            student_action=output,evidence_ids=eids,release_after=release,minutes=minutes,student_output=output,
            contribution_to_synthesis='汇报三个课程问题；最终建议引用该项结果',
            tracker_row='Not applicable: user approved direct response areas; '+output))
    d={'study_goal':'用实验回答课程计划第2讲的三个核心问题','source_priority':'plan.docx Lesson 2; approved V3 plan overrides broader data.md and packet workflow',
       'learning_objectives':[dict(id=id,source_excerpt=src,observable_outcome=out) for id,src,out,*_ in objectives],
       'problem_architecture':{'overarching_problem':'怎样描述四中心记录中的患者并为疾病状态研究准备数据？',
       'downstream_use':'研究团队描述患者特征并为后续二分类研究准备数据',
       'decision_options':['A 保留四中心及全部候选字段，说明处理条件','B 限定有依据的中心或字段','C 证据不足，暂缓拟议分析'],
       'inquiry_questions':qs},'evidence_items':ev,'course_coverage':[],
       'split_plan':{'required':False,'rationale':'只做描述和尺度实验，不估计泛化性能'},
       'workflow_override':{'approved':True,'reason':'User explicitly replaces extensive tracking/packet management',
          'student_packets':False,'student_tracker':False,'release_codes':'QA stage mapping only; all inputs provided from launch; B=experiment2, C=experiment3, D=transfer'},
       'time_budget':{'launch':45,'self_study':90,'report_class':45,'self_study_breakdown':{'reading':15,'experiment2':25,'experiment3':30,'transfer':10,'report_prep':10}},
       'analyses':[],'syllabus_tasks':[], 'boundaries':['No clinical or causal claims','No cross-source identity verification','Zero exclusions are sensitivity analysis, not established correction']}
    for id,src,out,location,aids,output in objectives:
        qids=[q['id'] for q in qs if id in q['objective_ids']]
        d['course_coverage'].append(dict(objective_id=id,concept_cluster_ids=[id],inquiry_question_ids=qids,analysis_ids=aids.split(','),
            required_learning=[out],student_output=output,worksheet_location=location,
            synthesis_use='汇报对应课程问题，综合进入最终数据使用建议',assessment_evidence=out))
    for id,method,domain,artifacts in [
        ('A1','逐列语义、角色判断与类别重编码对照','variable_semantics',['data/heart-disease-four-site.csv','review/verified-results.json']),
        ('A2','均值、列联频数、输入输出表示、ddof=0标准化','transformation_preprocessing',['review/verified-results.json']),
        ('A3','分中心缺失、比例、零值敏感性与完整记录构成','data_quality',['review/verified-results.json','review/verified-missing-counts.csv']),
        ('A4','明确输入的时间、矩阵与仪器教学对照','data_structure',['data/teaching-followup.csv','data/teaching-stage-count.csv','data/teaching-instruments.csv','data/teaching-matrix-scenarios.json'])]:
        related=[q for q in qs if q['id']=={'A1':'Q1','A2':'Q2','A3':'Q3','A4':'Q4'}[id]]
        d['analyses'].append(dict(id=id,method=method,domain=domain,artifacts=artifacts,objective_ids=related[0]['objective_ids'],inquiry_question_ids=[related[0]['id']],packet=related[0]['release_after'],interpretation_boundary='教学审查；不能得出因果或临床有效性结论'))
    for task,loc in [('判断每一列的变量类型','表 B1'),('哪些变量可以求均值？','表 B1与实验2'),('哪些变量适合做卡方检验？','表 B1、B2'),('哪些变量适合进入 logistic regression？','表 B1及输入输出判断'),('哪些变量需要标准化？','表 B1、B3及尺度解释'),('数据来源、样本数、特征数','数据身份'),('主要变量类型','表 B1'),('可能的数据质量问题','实验3及最终建议')]:
        d['syllabus_tasks'].append(dict(source_excerpt=task,worksheet_location=loc))
    write_json(REVIEW/'analysis-design.json',d)
    (REVIEW/'course-coverage.md').write_text('# V3课程覆盖\n\n|课程目标|可观察的学习成果|学生作答位置|\n|---|---|---|\n'+'\n'.join(f'|{src}|{out}|{output}|' for _,src,out,_,_,output in objectives)+'\n\n源：plan.docx第2讲。较宽泛data.md的距离、抽样、PCA等不作为本次核心任务。\n\n用户批准的结构替换：无需Packet A–D、总答案追踪表、证据卡、逐阶段退出条。QA的release代码只标识实验顺序，所有输入在启动时均可用。\n',encoding='utf-8')

if __name__=='__main__':
    sheet();reference();design()
    print('Created worksheet and reference in',ROOT)
    print('Data SHA256',truth['data_sha256'])
