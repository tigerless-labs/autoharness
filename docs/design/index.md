# design —— 索引

autoharness 的设计：一个面向智能体技能层的结构化管理器。痛点与意图见 [`../DEFINITION.md`](../DEFINITION.md)。

- **[workflow.md](workflow.md)** —— 主线：原则、四层流水线（intake → manage → retrieve，外加一个预留的 eval 层）、暂定的工作假设，以及各层借用了什么。
- **[management.md](management.md)** —— 带类型的 DAG：关系、冲突、去重，以及新技能的准入闸门。
- **[eval.md](eval.md)** —— 预留的评估层：每条技能的理由账本，以及奠定未来演化层的使用遥测数据源。

工作方法（非产品架构）：

- **[research-loom.md](research-loom.md)** —— 本项目自身的"文献→设计"工作方法：五层结构（来源·方向·idea·设计·决策，非时序、按需跨层维护）、原子稳定/视图可弃/可溯源的不变量。操作指南见 `research-loom` skill，内容产物见 [`../research-loom/`](../research-loom/index.md)。
