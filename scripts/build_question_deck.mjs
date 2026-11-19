import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const runtime='C:/Users/rongs/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=runtime+'/node/node_modules';
const {Presentation,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const build=path.resolve(base,'../../../.tmp/high-dimension/question-deck-v2');
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.join(base,'slides'),{recursive:true});
const ink='#163334', teal='#087F79', gray='#5B696A', orange='#AC561C', paper='#FAFBF8';
const font='Microsoft YaHei';
const deck=Presentation.create({slideSize:{width:1280,height:720}});
deck.theme.defaultFont=font;
const source='依据本课 student-worksheet.md、experiment-design.md、data/README.md。';
const slides=[
 {type:'cover',title:'高维数据与维度灾难',question:'特征越多，模型就一定越好吗？',body:'用白血病真实表达数据，向研究团队提出分析建议',note:'第3讲  PBL问题引导  zhang',notes:'开场只呈现待检验的问题，不表态。告诉学生：今天的任务是用自己获得的证据回应团队。让学生保留初始判断，最后再回看。'},
 {title:'研究团队面临的决定',question:'我们应纳入多少特征？',left:'你的角色\n研究助理',right:'团队希望根据表达数据区分 ALL 与 AML。\n\n同事主张：“测得的特征越多，预测就越好。”\n\n导师需要你说明：支持这个主张，究竟需要什么证据？',output:'最终产出：一份有证据、有理由、说明适用范围的建议。',notes:'0–7分钟，T1.1。先让每人写立场，再两人交换理由。不要评价哪种立场正确。'},
 {title:'今天要完成的判断',question:'怎样才算回答了团队的问题？',items:[['数据','明确样本、特征和研究单位。'],['距离','比较“近”和“远”，解释指标的变化。'],['泛化','比较训练与未参与拟合样本的表现。'],['建议','用证据修订判断，并提出下一步验证。']],output:'课堂45分钟：T1 13分钟 / T2 10分钟 / T3 7分钟 / T4 8分钟 / T5 7分钟',notes:'本页是学习目标和时间安排，不是实验结论。课后60分钟完成迁移与稳定性分析。'},
 {title:'数据背景',question:'这份数据测量了什么？',left:'72\n份表达样本\n\n7,129\n个实测探针特征',right:'Golub 白血病微阵列表达数据\nOpenML leukemia，ID 1104，版本1\n\nALL：急性淋巴细胞白血病\nAML：急性髓系白血病\n\n我们使用已有表达值和诊断标签。',output:'思考：这里的一行是什么？一列是什么？n与p分别代表什么？',notes:source+' 数据背景不是实验答案。来源：https://www.openml.org/d/1104；Golub et al. Science (1999), DOI:10.1126/science.286.5439.531。原始数据许可字段为Public，不扩写为CC BY。'},
 {title:'探针与数据表',question:'哪些列可以进入模型？',table:[['字段','含义'],['sample_id','按原行序建立的教学编号'],['original_split','已有的训练与测试划分标记'],['diagnosis','样本的ALL或AML诊断'],['7,129个探针列','微阵列对特定核酸序列表达的测量']],intro:'探针是微阵列中的测量单元，在本表中对应一个表达特征列。',output:'T1.2：计算p/n，核对类别数量，并说明每种列在分析中的角色。',notes:source+' T1.2，7–13分钟。让学生先判断输入列，不直接公布排除列表。追问：探针数、基因数和独立信息量为什么可能不同？'},
 {title:'纳入更多已有的探针特征',question:'比较中什么不变，什么改变？',left:'同一批样本\n同一份表达表',right:'先确定一次探针列顺序。\n\n分析前2列，再扩展到前3列、前10列，\n逐步使用更多已有列。\n\n每个较小子集，都包含在后续较大子集中。',output:'讨论：多纳入一列，是否必然多获得一份独立、有用的信息？',notes:'解释操作语义：没有新增患者或重新测量。随机种子只决定已有探针列的顺序。不要预先判定更多列会使性能上升或下降。'},
 {title:'T1 初始判断与迁移',question:'什么证据会让你改变看法？',left:'先独立写三句\n\n我的判断是……\n我的理由是……\n如果看到……\n我会修订判断。',right:'小组分担五类情境\n转录组、蛋白组、代谢组、医学影像、单细胞\n\n每类说明一行、一列、特征量级和一个风险。\n\n为什么细胞多，不一定意味着独立患者多？',output:'提交：初判＋数据概况表＋五类情境表。',notes:'T1.1–T1.3。初判不按猜对评分。课堂分担五类场景后汇总，避免每组重复做长报告。不要把72个教学编号称为已核验独立患者。'},
 {title:'T2 距离比较的操作范围',question:'纳入更多列后，样本间距离怎样变化？',table:[['保持相同','本次约定'],['样本','全部72份表达样本'],['尺度与距离','逐探针z-score；欧氏距离'],['探针顺序','随机种子42，不根据诊断选列'],['比较维度p','2、3、10、100、1,000、7,129']],output:'先分别预测平均距离、距离CV的变化，再运行notebook实验A。',notes:'T2，13–23分钟。标准化公式为每列减均值、除总体标准差（ddof=0）。此处是描述当前样本，不用该全样本变换评分模型。'},
 {title:'T2 如何读取距离证据',question:'你看到的是绝对距离，还是相对差异？',left:'平均距离\n样本对距离的平均值\n\n距离CV\n距离标准差 ÷ 平均距离',right:'先看二维和三维散点图。\n\n再看各维度的距离分布。\n图横轴为“距离 ÷ 该条件平均距离”。\n\n表中仍记录原始平均距离。',output:'记录p=2、3、100、7,129的均距、CV与R。解释两个指标是否表达同一件事。',notes:'T2.1–T2.3。对应A-scatter-2D-3D.png、A-distance-distributions.png、A-real-distances.csv。幻灯片不展示运行图和趋势。请学生在自己的输出中指出证据。'},
 {title:'T3 最近邻与最远邻',question:'“相对接近”应该怎样衡量？',left:'R = (d_max − d_min) / d_min',right:'对每个样本，排除它自己。\n\nd_min：到最近邻的距离\nd_max：到最远邻的距离\n\n逐个计算R，再汇总全体R的中位数。',output:'找到G001：在p=2和7,129时手算R，再与全体绝对差中位数比较。',notes:'T3.1，23–30分钟。文件A-neighbors-seed42.csv和A-real-distances.csv。若遇d_min=0要单独记录。请学生讨论相对差与绝对差，而非直接告诉变化方向。'},
 {title:'T3 结论对选列敏感吗',question:'换一批已有探针，判断还成立吗？',items:[['对照','保留72份样本，改用种子7和2026确定列序。'],['观察','比较同一p下的CV与R，记录不同与相同之处。'],['追问','是否每一步都单调？请指出一条具体记录。'],['边界','全部7,129列只改变顺序，距离应怎样变化？']],output:'提交：G001核算＋种子对照＋一句有条件的解释。',notes:'T3.2–T3.3。补充追问：尺度、特征相关性与距离度量如何影响解释？未实际运行的替代度量只能作为假设或建议。不要披露非单调发生的具体条件。'},
 {title:'T4 预测实验的操作范围',question:'怎样比较不同特征数量的预测表现？',table:[['项目','固定约定'],['训练 / 测试','原始划分：38份 / 34份'],['模型','训练部分标准化，再用1近邻分类'],['探针顺序','沿用种子42'],['比较维度p','2、10、100、1,000、7,129']],output:'先写训练与测试表现的预测，列出保持不变和发生变化的因素。',notes:'T4.1，30–38分钟。解释1近邻如何使用最近训练样本标签，不预告训练满分。标准化仅fit训练数据，测试应用同一变换。固定全部方案后统一查看测试结果。'},
 {title:'T4 两次判断',question:'只看训练表现，你能下什么结论？',left:'第一次\n只显示训练BA\n\n记录判断及理由。',right:'第二次\n再显示测试BA\n\n你的判断是否改变？\n哪项证据促使你修订？\n还缺什么才能谈新患者表现？',output:'提交：完整得分表＋一项机制解释＋一项证据缺口。',notes:'停在本页，先运行notebook仅显示训练BA的单元，让学生写判断后再运行下一单元。不要提前打开B-generalization.png。讨论时不把训练测试差距直接写成高维的因果效应。'},
 {title:'T4 评分指标与结果核查',question:'两类诊断怎样公平计分？',intro:'BA =（ALL召回率 ＋ AML召回率）÷ 2',table:[['核查项','请学生完成'],['ALL召回率','ALL预测正确数 ÷ 测试集中ALL总数'],['AML召回率','AML预测正确数 ÷ 测试集中AML总数'],['p=7,129','用两类正确数手算一次BA'],['比较基线','如果全部预测为ALL，BA是多少？']],output:'追问：本次结果是否足以支持“更多必然更好”或“更多必然更差”？',notes:'T4.2–T4.3。依据B-original-split.csv核对分母。不给BA基线答案，不给训练与测试数值。评价学生是否准确区分指标、当前队列和未来泛化。'},
 {title:'T5 大量检验与报告选择',question:'如果只报告最小p-value，会遗漏什么？',left:'理论条件\n\n7,129项检验\n所有原假设成立\n每项I类错误率0.05',right:'预期会出现多少个假阳性？\n\n这个期望数，能当作本数据实测的差异基因数吗？\n\nFDR控制想解决哪一种风险？',output:'写出计算式、解释其含义，并指出“只挑最显著”带来的问题。',notes:'T5.1，38–45分钟。本题只做理论计算，不运行差异检验。不给乘积答案。不要把探针数称作不同基因数。'},
 {title:'T5 分析流程审查',question:'这个流程哪里需要修改？',items:[['待审查①','在全部72份样本上，按诊断筛选20个探针。'],['待审查②','使用全部样本的均值与标准差做标准化。'],['待审查③','对分类器交叉验证，报告新患者预测能力。']],output:'重画流程：标出哪里fit，哪里只能应用已有变换。测试集上能重新选列吗？',notes:'T5.2。此页清楚标注为待审查流程，不展示修复答案。追问如果搜索多个k，选择k与评价性能各放在哪里。不要在学生作答前画出正确Pipeline。'},
 {title:'给研究团队的最终建议',question:'你的初始判断需要怎样修订？',items:[['主张','你现在怎样回应“特征越多模型一定越好”？'],['证据','引用一个距离结果和一个泛化结果。'],['推理','这些数值为什么支持你的判断？'],['边界','还不能推出什么？下一步需要什么验证？']],output:'T5.3：填写四句话退出卡，再与课前判断对照。',notes:'最后3分钟给两组短分享，再让全班写退出卡。不按是否选择同一主张评分，要求证据可追溯、机制合理、边界具体。'},
 {title:'H1 课后追问与提交',question:'预测表现与所选探针都稳定吗？',left:'原训练38份样本内\n3折 × 3次重复\n\n比较全部7,129探针\n与训练折内选20探针',right:'验证BA：均值、最小值、最大值。\n\n所选集合：Jaccard中位数与范围。\nJaccard = 交集数 ÷ 并集数\n\n筛选是否每折更好？这些折是否独立？',output:'课后60分钟：600–900字，补充两种策略及代价、元数据限制和一项更强验证。',notes:'H1。k=20预设，筛选在训练折内拟合。数据表B-training-only-cv.csv和B-selection-stability.csv。提交填写工作单及运行notebook，不另交重复报告。作业包含情境n/p、课堂两类数值证据、稳定性比较、策略和边界。'},
 {title:'实验入口与完成标准',question:'什么样的回答是清楚且可核查的？',left:'入口\nstudent-worksheet.md\n\nnotebook/\nhigh-dimension-lab.ipynb\n\ndata/README.md',right:'问题：明确自己回答哪一个问题。\n证据：给出数值、条件和所在表。\n解释：说明证据与判断的关系。\n边界：说明还未验证的部分。\n\n保留版本、种子、运行结果和参数改动。',output:'评分关注证据与推理。表格可粘贴输出，解释由你完成。',notes:source+' 教师可在开课前先打开本页帮助定位文件。课堂预先安装requirements.txt。原始数据含负值，按数据说明处理，不直接log或把非正值当缺失。遇计算故障用教师按阶段提供的表，课后补做操作。'}
];

slides[7].table[0][0]='项目';
slides[9].right='对每个样本，排除它自己。\n\nd_min：到最近邻的距离\nd_max：到最远邻的距离\n\n逐个计算R，\n再取全体R的中位数。';
slides[14].right='预期会出现多少个假阳性？\n\n这个期望数，能当作实测的\n差异基因数吗？\n\nFDR控制想解决哪一种风险？';

slides.splice(7,0,{
 title:'为什么这样设计距离实验？',
 question:'特征数量改变时，样本间的远近差别会怎样变化？',
 items:[
  ['逐步增加列','固定72份样本和计算方法，按同一列序取前p列。\n保留已选特征，观察纳入更多已有探针后的变化。'],
  ['比较距离CV','CV（变异系数）= 距离标准差 ÷ 平均距离。\n衡量距离的相对分散程度，便于比较不同维度。'],
  ['固定随机种子','种子是控制随机排列的整数，如42。\n相同代码与环境下，可复现同一探针列序。'],
  ['更换随机种子','再用7和2026排列已有列，重复取前p列。\n检查观察到的变化是否依赖某一次特征选择。']
 ],
 output:'先预测，再用数据判断：换一批特征后，你的解释还成立吗？',
 notes:'本页放在T2操作说明前，解释实验目的，不预告趋势。这里CV指变异系数，不是交叉验证。种子只控制已有列的排列，不生成模拟数据，不改变样本。每个种子内使用嵌套子集。特征数增加时，特征组成和相关性也在变化，所以不能把结果解释成维度本身的纯因果效应。更换种子检查选列敏感性，不等于获得独立的新队列。'
});

function text(slide,str,x,y,w,h,size=28,color=ink,bold=false){
 const shape=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=str;
 shape.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',insets:0,verticalAlignment:'top'};
 return shape;
}
function nativeTable(slide,rows,top=250){
 const tb=slide.tables.add({rows:rows.length,columns:2,left:72,top,width:1136,height:rows.length*57,values:rows,columnWidths:[290,846]});
 for(let r=0;r<rows.length;r++) for(let c=0;c<2;c++){
  const cell=tb.getCell(r,c);cell.fill=r===0?'#E5EFEB':(r%2?'#FFFFFF':'#F0F4F0');
  cell.text.style={typeface:font,fontSize:25,bold:r===0,color:r===0?teal:ink,insets:10};
 }
 return tb;
}
for(let i=0;i<slides.length;i++){
 const d=slides[i],s=deck.slides.add();s.background.fill=paper;
 if(d.type==='cover'){
  text(s,'生物医学数据科学  第3讲',76,78,1080,40,24,teal,true);
  text(s,d.title,76,194,1120,90,58,ink,true);
  text(s,d.question,76,329,1120,100,44,teal,true);
  text(s,d.body,76,478,1100,62,28,gray);
  text(s,d.note,76,628,1050,32,22,gray);
 }else{
  text(s,d.title,72,43,1136,58,42,ink,true);
  text(s,d.question,72,129,1136,76,34,teal,true);
  if(d.intro)text(s,d.intro,72,215,1136,52,27,gray);
  if(d.table)nativeTable(s,d.table,d.intro?281:247);
  else if(d.items){
   const gap=d.items.length===3?108:85;
   d.items.forEach(([label,body],j)=>{text(s,label,72,245+j*gap,215,60,28,teal,true);text(s,body,304,245+j*gap,900,70,29);});
  }else{
   text(s,d.left,72,244,d.left.startsWith('R =')?650:470,338,d.left.startsWith('R =')?32:30,ink,true);
   text(s,d.right,d.left.startsWith('R =')?770:600,244,d.left.startsWith('R =')?438:608,348,28,ink);
  }
  text(s,d.output,72,621,1090,66,23,orange);
 }
 text(s,String(i+1).padStart(2,'0'),1200,666,45,25,16,gray);
 s.speakerNotes.text=d.notes+'\n'+source;
}
await fs.writeFile(path.join(build,'slide-content.json'),JSON.stringify(slides,null,2));
await (await PresentationFile.exportPptx(deck)).save(path.join(build,'candidate.pptx'));
for(let i=0;i<deck.slides.items.length;i++){
 const png=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const skill='C:/Users/rongs/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const result=await finalizePresentation({workspaceDir:base,candidatePath:path.join(build,'candidate.pptx'),
 finalPath:path.join(base,'slides/high-dimension-pbl-questions-v2.pptx'),
 pythonExecutable:runtime+'/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...[5,9,13,15].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[5,9,13,15],fontPolicy:{basis:'design',families:[font]},
 verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify(result));
