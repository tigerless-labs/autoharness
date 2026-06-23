# design —— 索引

autoharness 的设计：一个面向智能体技能层的结构化管理器。痛点与意图见 [`../DEFINITION.md`](../DEFINITION.md)。

- **[workflow.md](workflow.md)** —— 主线：原则、四层流水线（intake → manage → retrieve，外加一个预留的 eval 层）、暂定的工作假设，以及各层借用了什么。
- **[management.md](management.md)** —— 带类型的 DAG：关系、冲突、去重，以及新技能的准入闸门。
- **[eval.md](eval.md)** —— 预留的评估层：每条技能的理由账本，以及奠定未来演化层的使用遥测数据源。
