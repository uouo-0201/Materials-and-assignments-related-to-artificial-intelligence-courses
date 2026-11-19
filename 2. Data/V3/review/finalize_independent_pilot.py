import json
from pathlib import Path
p=Path(__file__).resolve().parent
new=json.loads((p/'pilot-fields.json').read_text('utf-8'))
old=json.loads((p/'pilot-fields-intermediate.json').read_text('utf-8'))
by_prompt={x['prompt']:x for x in old['fields']}
for x in new['fields']:
 src=by_prompt[x['prompt']]
 x['answer']=src['answer'];x['minutes']=src['minutes'];x['blockers']=[]
def f(n):return new['fields'][n-1]
# Student attaches own generated results; table inspection time is assigned once,
# to its first cell. Other zero-minute cells belong to the same inspected table.
for first,last,minutes in [(53,60,1.5),(65,76,3),(79,94,5),(95,102,4),(103,110,4)]:
 for n in range(first,last+1):f(n)['minutes']=0
 f(first)['minutes']=minutes
def friction(n,note,fix):
 f(n)['blockers']=[dict(code='P15',severity='friction',note=note,fix=fix)]
friction(15,'实验2连同B1方法判断约33分钟，超过25分钟分项导向；整体课后约92分钟，仍符合总预算20%容差。','按学习需要灵活使用各模块时间，同类字段只补不同条件。')
friction(79,'92分钟估计采用计算助手和直接附自生成数值表；从零用Excel构建全部表格仍会明显超时。','对纯Excel路径另给公式模板或时间，不把工具安装调试计入本课90分钟。')
new['pilot_metadata']=old['pilot_metadata']
new['pilot_metadata'].update(revision='Final129 fields re-extracted; latest paragraphs checked; numeric tables may be attached without transcription; rehearsal5min moved into reporting class.',block_count=0,timing_basis='Launch48; homework92=reading15+experiment2 including B1 methods33+experiment3 including extreme/source verification21+transfer11.5+preparation11.5. Reporting class: familiarization5 plus reflection3. Zero-minute numeric cells share the first-cell table inspection/attachment estimate; all have substantive numeric answers for QA.')
(p/'pilot-fields.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'pilot-time-summary.json').write_text(json.dumps(dict(launch=48,homework_reading=15,experiment2=33,experiment3=21,transfer=11.5,preparation=11.5,homework_total=92,reporting_class_familiarization=5,reporting_class_reflection=3),ensure_ascii=False,indent=2),encoding='utf-8')
# Remove encoding-damaged intermediate append; the original narrative above it is intact.
notes=(p/'independent-pilot-notes.md').read_text('utf-8').split('\n\n\n## ?')[0]
notes+='''

## 最终复试结论

最新版本重新extract得到129字段，129全部回答。首轮问题保留作修订历史：目前0阻断、2条P15时间摩擦。新的逐列表将课堂类型判断与课后方法判断分开，允许同类引用；数值结果可直接附上，解释必须自行完成；汇报熟悉5分钟移至汇报课堂。这些是实际任务削减，而不是虚减估时。

最终估计启动48分钟（预算45，+6.7%）；课后92分钟（预算90，+2.2%）：阅读15、实验2连同B1方法33、实验3连同极端值21、迁移11.5、汇报提纲/建议/自检11.5。汇报课堂另用5分钟熟悉讲解、3分钟讨论修正。92分钟以预配置课程Python环境、使用助手、直接附数值表为前提，不涵盖安装调试或从零Excel编表。模块25/30/10/10可以灵活分配；总量在20%容差内。

助手实际运行并逐张检查9张CSV，包含52项缺失矩阵、胸痛前后频数、C2的有效n=0空均值、Cleveland-001的z=0.948726。全部符合首轮从原始学生CSV独立计算结果。工具不写类型、方法、原因解释或最终建议。仍亲手核对26+20=46及四类总和920，并保留z代入式。QA字段仍填具体数值，但实际学生可直接附结果；数值表阅读核对和附入时间仅记在首格，其余同表格0分钟，避免重复计时。

所有已报指代已解决：标准化明确真实四中心数据；C1明确缺失只填计数；C后果明确表C1阳性比例；D1明确归一化表达值；真实数据边界只在最后一格；讨论后修正明确是哪次课堂。无尚未解决的歧义阻断。B1方法列标题中的“实验2后”明确安排，不按页面位置算入启动。

最终决策有证据驱动：初始A，检查后B。完整记录299中297来自Cleveland和Switzerland的123个胆固醇零值使我限制范围；603 mg/dL仅要求核实。三个课程问题都可用已完成的表解释。最终结果见pilot-report.md和pilot-fields.json；生成pilot副本仅用于教师QA，不渲染、不交给学生。
'''
(p/'independent-pilot-notes.md').write_text(notes,encoding='utf-8')
print('Final129 field answers migrated;0 blockers;2 friction;48/92 minute estimate')
