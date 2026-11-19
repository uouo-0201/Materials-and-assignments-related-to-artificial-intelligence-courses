# 第3讲 高维数据与维度灾难

负责人zhang。独立45分钟课堂＋60分钟作业，使用第4讲Golub白血病真实表达数据：72份样本、7129个探针。

- [学生工作单](student-worksheet.md)：T1–T5、证据表与H1。
- [教师参考](teacher-reference.md)：逐题答案、实际数值、评分和边界。
- [实验设计](experiment-design.md)：目标、方法及时间安排。
- [数据说明](data/README.md)：来源、字段及使用规则。
- [课堂notebook](notebook/high-dimension-lab.ipynb)：距离、泛化与选择稳定性。

安装：`python -m pip install -r requirements.txt`。完整重算：`python scripts/experiments.py --output teacher-results`。更新文档和空白notebook：`python scripts/build_materials.py`；此步骤会覆盖生成文档和notebook，先保存个人修改。

学生发放工作单、data、notebook、scripts/experiments.py、requirements.txt；教师保留答案、teacher-results、review、build_materials.py。student-results是学生计算输出，不属于初始发放；先写预测再看证据。

High-dimension.md已同步为实测数据课纲。所有选列与验证使用原表达值及诊断；纳入更多已有的探针特征时，这些特征的信号属性未知，不能预设更多必然更差。
