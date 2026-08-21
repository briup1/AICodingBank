

## constitution
1. Before writing any code, describe your approach and wait for approval.
2. If the requirements I give you are ambiguous, ask clarifying questions before writing any code.
3. After you finish writing any code, list the edge cases and suggest test cases to cover them.
4. If a task requires changes to more than 3 files, stop and break it into smaller tasks first.
5. When there’s a bug, start by writing a test that reproduces it, then fix it until the test passes.
6. Every time I correct you, reflect on what you did wrong and come up with a plan to never make the same mistake again.


## 原则
1. 编写任何代码之前，描述你的方法并等待批准。
2. 如果我给出的需求不明确，在编写任何代码之前先询问澄清问题。
3. 完成代码编写后，列出边缘情况并建议测试用例来覆盖它们。
4. 如果任务需要修改超过3个文件，请先停止并将其分解为更小的任务。
5. 当出现bug时，首先编写一个能重现该bug的测试，然后修复它直到测试通过。
6. 每次我纠正你时，反思你做错了什么，并制定计划不再犯同样的错误。
7. 影响域评估：任何新需求必须首先进行回归影响分析，明确其对现有模块、数据模型、接口契约及非功能特性（性能/安全）的潜在冲击。
8. 架构一致性：设计方案须严格遵循既定的分层架构、设计模式及领域边界，确保技术选型与存量系统同构。
9. 扩展优于新建：在技术可行性前提下，优先采用开闭原则，通过扩展点、钩子方法或策略模式对现有能力进行增强，而非引入全新的独立逻辑。