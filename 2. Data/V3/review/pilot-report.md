# Pilot-fill report

- Worksheet: `class2026/materials/2. Data/V3/pbl-data-types-student-worksheet.docx`
- Pilot copy: `class2026/materials/2. Data/V3/review/pbl-data-types-pilot-fill.docx`
- Date: 2026-09-25
- Persona / independence mode: fresh-agent independent pilot；中文生物医学初学者，会基本Excel/AI，不熟练编程。仅阅读学生工作单、参考R1–R4、data及学生可见助手；未读教师答案、design或build。
- Lint / design summary: 作者最终复跑确认：lint为0 errors、0 warnings；design为0 errors、0 warnings。独立试填没有读取教师design文件；结果由主作者提供。
- Fields: 129 · answered: 129 · unanswered: 0
- Blockers: **0 block** · 2 friction
- Estimated minutes (sum of field estimates): 119
- Gate: **PASS** (also requires lint and design with 0 errors and time within budget)

## Minutes by part

| Part | Minutes |
|---|---|
| 我的3W与数据起点 | 19 |
| 二 用实验检验理解 | 34 |
| 实验2 哪些分析有意义 | 12 |
| 实验2 标准化改变了什么 | 8 |
| 实验3 处理数据会改变结论吗 | 19 |
| 迁移 同一思路能用到新数据吗 | 12 |
| 三 向全班解释我的学习 | 14 |

## Blockers by pitfall

| Code | Pitfall | block | friction |
|---|---|---|---|
| P15 | scope or workload (beyond lesson, over budget, syllabus task missing) | 0 | 2 |

## Blocker list

| Field | Location | Prompt | Code | Severity | Note | Suggested fix |
|---|---|---|---|---|---|---|
| F015 | T6 r1 c2 · 实验1 数字一定代表数量吗 | 教学编号 (record_id) → 分析用途与条件（实验2后） | P15 | friction | 实验2连同B1方法判断约33分钟，超过25分钟分项导向；整体课后约92分钟，仍符合总预算20%容差。 | 按学习需要灵活使用各模块时间，同类字段只补不同条件。 |
| F079 | T15 r1 c2 · 实验3 处理数据会改变结论吗 | Cleveland → 胆固醇 缺失数 | P15 | friction | 92分钟估计采用计算助手和直接附自生成数值表；从零用Excel构建全部表格仍会明显超时。 | 对纯Excel路径另给公式模板或时间，不把工具安装调试计入本课90分钟。 |

## Decision check

能。初始根据A1四中心均有记录及R2字段定义，暂选A并等候缺失检查。最终选B，暂限定Cleveland作描述并承认代表性限制。C3完整记录299条中297来自Cleveland（中心占比32.93%→99.33%），以及C2 Switzerland胆固醇123条全为0，是改变范围建议的证据。Hungary-244胆固醇603 mg/dL只触发核实，不自动删除。建议包含年龄均值、胸痛类别编码、num仅作结局来源，并指出缺少随访信息不能作生存研究。

## Residual friction and risks

保留2条P15摩擦：实验2连同B1方法判断约33分钟，高于25分钟分项导向，但课后总量92分钟在90分钟预算20%容差内。时间以预配置Python环境、使用数值助手和直接附自生成结果为前提；从零用Excel构建全部表格仍会超时，环境安装调试也不在90分钟内。模块时间须灵活使用。时间为模拟估计，不是真实学生计时试验。

## 按实际学习阶段归属的耗时

自动“Minutes by part”按文档位置分类，不等于课时：B1方法格位于实验1版面却明确课后完成；阅读、工具启动、汇报熟悉也没有单独答格。因此以此表判断时间门槛。

|阶段|模拟分钟|预算|结果|
|---|---:|---:|---|
|启动：3W/身份/初选19＋类型角色16＋改名6＋引导5＋助手启动2|48|45|+6.7%，通过20%容差|
|课后阅读|15|15|符合|
|课后实验2及B1方法|33|25|分项摩擦|
|课后实验3含极端值/来源复核|21|30|符合|
|课后迁移|11.5|10|+15%|
|课后提纲/建议/自检|11.5|10|+15%|
|课后合计|92|90|+2.2%，通过20%容差|
|汇报课堂熟悉讲解与讨论修正|5＋3|计入45分钟汇报课|已明确时间归属|

数值表允许附上自己生成的输出，试填仍为全部129格写入具体数值供QA核查。每张表的阅读、核对及附入时间集中记首格，其余数值格0分钟，不代表没有读过。学生语义解释、手工复核、方法判断与决策时间均保留。

## 修订前后

|首轮问题|实质修订|复查状态|
|---|---|---|
|16×5个B1判断格使启动超时|改16类型格＋16课后方法格，同类可引用|已复试，48分钟|
|计算任务无工具脚手架|可选数值助手；允许附自生成结果，无需逐格转抄|助手运行成功，9张CSV全部与独立原始数据计算一致|
|实验1未引方法资料却要求判断方法|方法明确实验2/R3后完成|解决|
|标准化用途框和B1重复|删除框，只填B1|解决|
|实验2手核、本表等模糊引用|改为具体操作和表C1|解决|
|单细胞表示不确定|明确归一化表达值|解决|
|D1真实数据边界重复|集中最后边界框|解决|
|讨论时点及汇报准备不清|汇报课堂熟悉5分钟、讨论修正3分钟|解决|
|长篇建议工作量|120–180字或等量要点、引用数值|改善，总量门槛通过|

最终：129/129完成，0阻断、2摩擦。未发现内容错误、遗漏必需输出位置或未提供的证据。最新语句已冷读，所有原P03指代问题已修复。助手只提供数值，不代填类型、方法或建议。pilot副本为教师QA，未渲染，未修改学生DOCX。独立审计细节见independent-pilot-notes.md，数值输出见pilot-helper-output。
