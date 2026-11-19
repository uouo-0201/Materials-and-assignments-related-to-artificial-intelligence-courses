"""Map first cold-read answers into revised student worksheet, then re-answer changed prompts."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
old=json.loads((p/'pilot-fields-before-revision.json').read_text('utf-8'))
new=json.loads((p/'pilot-fields.json').read_text('utf-8'))
oldf={x['id']:x for x in old['fields']}
by_prompt={x['prompt']:x for x in old['fields']}
def f(n):return new['fields'][n-1]
def put(n,a,m):
 f(n)['answer']=a if isinstance(a,list) else [a]
 f(n)['minutes']=m
 f(n)['blockers']=[]
for item in new['fields']:
 if item['prompt'] in by_prompt:
  src=by_prompt[item['prompt']]
  item['answer']=src['answer'];item['minutes']=src['minutes'];item['blockers']=[]
methods=[
 '均值、卡方、Logistic输入、标准化均不宜：教学编号只用于定位记录（R2）。',
 '均值不宜；卡方可候选但检查独立性/频数；Logistic需中心类别编码并明确用途；不直接标准化中心名。',
 '均值可；连续原值不宜卡方；可作数值预测；尺度敏感方法或正则化时考虑z化，非所有方法必须。',
 '0/1均值为编码1比例；卡方看条件；Logistic可0/1输入；通常无需z化，沿用历史性别编码定义。',
 '原编号均值不宜；卡方看独立性/期望频数；Logistic用指示变量；不直接z化编号（R3）。',
 '同年龄；先核对血压0等异常，确认入院值在预测前可得。',
 '同年龄；先核对缺失、0及极端值，不由z化解决这些问题。',
 '同sex的二分类用法；分母为非缺失者，空白不补为0。',
 '同cp的无序类别用法，不把0/1/2当等距。',
 '同年龄；须确认预测时已完成运动检查。',
 '同sex的0/1用法；运动检查发生在预测前。',
 '同年龄；R2单位未明确，须核实测量尺度与时点。',
 '均值不宜；卡方可候选；Logistic先类别编码，单数值须额外趋势假设；不直接标准化编号。',
 '均值可解释但说分母；卡方须按0–3列联并查稀疏性；可数值预测，确认时点；标准化取决于方法。',
 '同cp；3/6/7是标签，预测前须已有灌注检查。',
 '原均值不宜；卡方先按0与>0统一状态；派生y作结局不可又作输入；不z化结局。'
]
full_times={0:1,1:1,2:1.5,3:1.5,4:1.5,12:1,13:1,15:1}
for row in range(16):
 put(14+2*row,oldf[f'F{14+5*row:03}']['answer'],1)
 put(15+2*row,methods[row],full_times.get(row,.375))
put(46,oldf['F094']['answer'],6)
for n in [47,49,51]:f(n)['minutes']=.5
for n in [48,50,52]:f(n)['minutes']=.75
for n in range(53,61):f(n)['minutes']=.25
f(61)['minutes']=3
for n in [62,63,64]:f(n)['minutes']=1.25
for n in range(65,77):f(n)['minutes']=.35
f(77)['minutes']=3
f(78)['minutes']=2.5
for n in range(79,111):f(n)['minutes']=.5
f(111)['minutes']=6
put(112,oldf['F161']['answer'],2)
put(113,'不能：甲发生事件，乙到12个月尚未发生。必须同时保留观察时长及事件状态（D1、R1）。',1.5)
put(114,'300×20000，3位供者；每一基因为连续的归一化表达测量，高维描述整张矩阵有许多变量，而不是另一种单列类型（D1、R1）。',2)
f(115)['minutes']=1.5
f(116)['minutes']=2.5
f(117)['minutes']=2
for n in range(118,124):f(n)['minutes']=.75
put(124,'建议B：先限定Cleveland作描述，不推广四中心。年龄可求均值，胸痛分类编码，num只派生结局。C3剩余299条中297来自Cleveland；Switzerland胆固醇123条全0，需核查采集和缺失编码。Hungary-244胆固醇603 mg/dL应复核，不自动删除。优先核实流程和患者链接；缺少随访时长及事件状态，不能回答生存问题。',5)
for n in range(125,129):f(n)['minutes']=.5
put(129,oldf['F178']['answer'],3)
def flag(n,code,note,fix):
 f(n)['blockers'].append(dict(code=code,severity='friction',note=note,fix=fix))
flag(15,'P15','B1虽可同类引用，初学者还要完成16种方法判断。计入实验2后，该部分约35分钟，超过分配的25；总课后在108分钟容差内，但很紧。','课堂提醒同类引用；将分项时间作为可调整导向，不要求25分钟内全体做完。')
flag(79,'P15','本轮预计课后约102分钟，以计算助手顺利运行、学生自行解释为前提；基本Excel学生从零构建全部计算仍会超时。','明确90分钟路径使用现成计算助手；纯Excel从零操作应给予额外时间或公式模板。')
flag(124,'P15','10分钟汇报准备较紧，短提纲/建议/自检约11.5分钟，若另试讲约6分钟，总课后仍在20%容差内。','允许用等量要点，汇报课堂提供短暂整理时间。')
new['pilot_metadata']={
 'date':'2026-09-25','independence':'fresh-agent, only student-visible worksheet/reference/data and optional helper',
 'persona':'中文生物医学初学者，基本Excel/AI，不熟练编程；已配置课程Python环境',
 'revision':'178 fields reduced to129; helper run and all numerical outputs inspected; all changed/dependent fields re-piloted',
 'block_count':0,'helper_command':'python scripts/experiment_helper.py --output-dir review/pilot-helper-output',
 'timing_basis':'Field minutes include reading and interpreting rows. Additional overhead: launch goals/R1/R2 orientation5 and helper launch2; homework R3 reading15, C3/extreme/source verification2, rehearsal6; discussion response3 in reporting class.'}
assert len(new['fields'])==129
assert all(x['answer'] and x['minutes'] is not None for x in new['fields'])
(p/'pilot-fields.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
launch=sum(f(n)['minutes'] for n in list(range(1,14))+list(range(14,45,2))+[46])+7
exp2=sum(f(n)['minutes'] for n in list(range(15,46,2))+list(range(47,79)))
exp3=sum(f(n)['minutes'] for n in range(79,112))+2
transfer=sum(f(n)['minutes'] for n in range(112,118))
prep=sum(f(n)['minutes'] for n in range(118,129))+6
totals={'launch':launch,'homework_reading':15,'experiment2':exp2,'experiment3':exp3,'transfer':transfer,'preparation':prep,'homework_total':15+exp2+exp3+transfer+prep,'reporting_class_reflection':3}
(p/'pilot-time-summary.json').write_text(json.dumps(totals,ensure_ascii=False,indent=2),encoding='utf-8')
print(totals)
