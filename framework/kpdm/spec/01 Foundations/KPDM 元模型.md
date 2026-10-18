---
type: object-model
work_id: KPDM
status: candidate
version: 0.5.0-rc.2
baseline: 0.4.1
created: 2026-08-11
updated: 2026-09-14
authority: object-model
---

# KPDM 对象模型

> 文件名保留为“KPDM 元模型”，以免破坏既有引用与审计追溯（见 KPDM-D013）；其权威角色自 2026-08-25 起为**对象模型**。
>
> 第一性结构见 [KPDM 三层元模型](KPDM%20%E4%B8%89%E5%B1%82%E5%85%83%E6%A8%A1%E5%9E%8B.md)。本文件回答的是另一个问题：Core-6 所需的知识与生产要素，在系统中如何被命名、赋予字段、建立关系并流转状态。它是 Core-6 的实现词汇表，不是与 Core-6 并列的第二套分解。
>
> 27 个对象向 Core-6 的归位表见 [KPDM 三层元模型](KPDM%20%E4%B8%89%E5%B1%82%E5%85%83%E6%A8%A1%E5%9E%8B.md)「27 个元对象的归位」。
>
> 0.5.0-rc.2 变化：Claim 增加 `status` 子类型（KPDM-D025，待作者接受）；状态模型补入生产、质量与发布三组受控词。对象枚举仍为 27 个。

## 核心关系

~~~mermaid
flowchart LR
  Q["Problem / 问题"] --> A["Audience / 受众"]
  Q --> C["Claim / 主张"]
  C --> K["Concept / 概念"]
  C --> E["Evidence / 证据"]
  C --> B["Boundary / 边界"]
  C --> M["Method / 方法"]
  K --> AR["Architecture / 知识架构"]
  M --> T["Tool / 工具"]
  AR --> U["Publication Unit / 表达单元"]
  U --> P["Product / 知识产品"]
  P --> V["Validation / 校验"]
  V --> D["Decision / 裁决"]
  D --> R["Revision / 修订"]
  R --> AR
~~~

## 二十七个核心元对象

| 对象 | 定义 | 必需字段 |
|---|---|---|
| Project | 一次知识产品开发活动 | 目标、范围、所有者、版本、状态 |
| Problem | 要解决的问题或认知缺口 | 情境、受影响者、重要性、成功变化 |
| Audience | 目标读者或使用者 | 角色、已有认知、任务、阅读情境 |
| Concept | 稳定概念及边界 | 名称、定义、非例、关系、权威源 |
| Claim | 可被判断、引用或质疑的主张 | 类型、内容、强度、边界、状态；`status` 子类型另需对象、范围、判据、证据、验证者、版本、限制 |
| Evidence | 支撑或反驳主张的材料 | 来源、命题、直接性、覆盖、限制 |
| Source | 外部或内部来源 | 作者/机构、版本、日期、定位、引用 |
| Architecture | 概念、主张和方法的组织结构 | 层级、关系、权威矩阵、视图 |
| Method | 从输入到输出的可执行规则 | 输入、步骤、角色、输出、失败条件 |
| Tool | 承载方法的模板、清单或软件 | 使用者、字段、规则、版本、验证 |
| PublicationUnit | 可发布表达单元 | 论点、读者任务、证据、前后依赖 |
| Product | 知识体系、书、出版物或文章 | profile、受众、单元、发布状态 |
| Validation | 对成果的独立检查 | 方法、门槛、结果、证据、限制 |
| Decision | 对分支、冲突或版本的裁决 | 选项、理由、决定人、影响、日期 |
| QualityTarget | 实例预设的 Q0–Q4 品质高度 | 等级、用途、验收维度、批准人 |
| ProvenanceRecord | 材料、主张和表达的来源链 | source、usage、locator、changes |
| RightsRecord | 权利、许可、保密和发布状态 | owner、license、permission、status |
| DataReference | 数据集、变量和计算链 | dataset、version、ID、transform、uncertainty |
| AIContribution | AI 在成果中的作用和核验 | tool、purpose、risk、verification、decision |
| ContextPack | 一次工作可依赖的版本化权威上下文 | context_id、version、authority、constraints、staleness |
| WorkPacket | 可执行、可验收的最小工作合同 | mode、objective、inputs、outputs、SLO、tests、decisions |
| ClaimGraph | 主张、证据、反例和依赖组成的论证图 | claims、edges、support、conflict、boundary |
| QualitySLO | 将质量高度转成可测试门槛 | dimension、metric、threshold、method、evidence |
| UncertaintyItem | 影响成果的显式未知与处置 | question、risk、owner、method、status、disposition |
| RegressionTest | 防止变更破坏既有行为的测试 | input、expected、tolerance、result、evidence |
| GoldenCase | 人工确认的代表性可重复案例 | type、fixed_input、expected、decision、version |
| ReleaseCandidate | 等待批准的不可变发布候选包 | manifest、SLO、tests、limitations、approval |

## 主张类型

| 类型 | 说明 | 典型校验 |
|---|---|---|
| definition | 对概念的人为定义 | 清晰性、边界、一致性 |
| factual | 可核验事实 | 权威来源、时效性、准确性 |
| explanatory | 解释或因果主张 | 理论、数据、反例、替代解释 |
| normative | 应该如何的价值或规范选择 | 理由、价值、适用边界、权衡 |
| methodological | 方法步骤或判断规则 | 可执行性、复现、结果表现 |
| predictive | 对未来结果的预测 | 前提、模型、回测、误差 |
| original_construct | 原创模型或组合 | 新颖性、必要性、解释力、比较 |
| boundary | 适用与不适用声明 | 反例、场景测试、外推限制 |
| status | 对某成果「完成、有效、成熟、可用、权威」等状态的主张 | 评价对象、适用范围、通过判据、支持证据、验证主体、适用版本、已知限制齐全；验证主体独立于产出者 |

`status` 是 Claim 的子类型，不是第 28 个元对象。它把《KPDM 质量约束》的状态主张纪律落到字段上：缺任一必需字段的状态主张改写为事实描述，不得以状态词代替证据。

## 主张类型与依据

核心主张按上表分类后，必须能定位其依据：事实定位来源，解释定位理论、数据与替代解释，规范选择定位理由与权衡，原创构造定位与已有认识的比较。缺失的依据保留为未知项，不得由 Agent 或作者补写成事实。

## 权威与视图

知识内核是权威层；出版物是视图层。书可以重组叙事，但不得静默改变概念定义。文章可以简化，但必须保留关键边界。工具可以编码规则，但不能成为隐蔽的新规范源。

所有实例先继承 [KPDM 三层元模型](KPDM%20%E4%B8%89%E5%B1%82%E5%85%83%E6%A8%A1%E5%9E%8B.md) 的普适原则与发布红线，再按 [上下文包与工作包协议](../02%20Methods%20and%20Protocols/%E4%B8%8A%E4%B8%8B%E6%96%87%E5%8C%85%E4%B8%8E%E5%B7%A5%E4%BD%9C%E5%8C%85%E5%8D%8F%E8%AE%AE.md) 选择轻量入口或展开路径。QualityTarget 决定所需 Check 强度；ProvenanceRecord、RightsRecord、DataReference 和 AIContribution 共同形成发布证据链。ContextPack 冻结输入，WorkPacket 冻结变换合同，QualitySLO 与 RegressionTest 冻结验收，ReleaseCandidate 冻结待批准成果。

生产控制层见 [KPDM 生产控制层](../02%20Methods%20and%20Protocols/KPDM%20%E7%94%9F%E4%BA%A7%E6%8E%A7%E5%88%B6%E5%B1%82.md)、[人机协作协议](../02%20Methods%20and%20Protocols/%E4%BA%BA%E6%9C%BA%E5%8D%8F%E4%BD%9C%E5%8D%8F%E8%AE%AE.md)、[上下文包与工作包协议](../02%20Methods%20and%20Protocols/%E4%B8%8A%E4%B8%8B%E6%96%87%E5%8C%85%E4%B8%8E%E5%B7%A5%E4%BD%9C%E5%8C%85%E5%8D%8F%E8%AE%AE.md)、[质量高度与验收等级](../03%20Quality%20and%20Governance/%E8%B4%A8%E9%87%8F%E9%AB%98%E5%BA%A6%E4%B8%8E%E9%AA%8C%E6%94%B6%E7%AD%89%E7%BA%A7.md)、[回归测试、Golden Case与发布候选](../02%20Methods%20and%20Protocols/%E5%9B%9E%E5%BD%92%E6%B5%8B%E8%AF%95%E3%80%81Golden%20Case%E4%B8%8E%E5%8F%91%E5%B8%83%E5%80%99%E9%80%89.md)。

## 状态模型

- 对象：candidate → draft → review → validated → active → deprecated；
- 主张：hypothesis → supported / contested / rejected；
- 出版：outline → manuscript → review-copy → publication-candidate → published；
- 校验：planned → doing → checking → passed / conditional / failed → closed；
- 工作包：planned → ready → doing → verifying → passed / conditional / failed → closed；
- 发布候选：assembled → checking → approved / conditional / rejected → published / superseded。

成果的生产、质量与发布状态分开记录，受控词汇见 [KPDM 生产控制层](../02%20Methods%20and%20Protocols/KPDM%20%E7%94%9F%E4%BA%A7%E6%8E%A7%E5%88%B6%E5%B1%82.md)「状态主张控制」：

- 生产状态：registered → drafted → structurally-reviewed → author-accepted；
- 质量与验证状态：criterion-ready、calibrated、field-piloted、independently-validated；
- 发布状态：candidate → release-approved / withdrawn；
- 限制限定：self-assessed、provisional、unverified。

`author-accepted` 只表示作者接受了某个具体版本，不表示独立复核或发布批准。

## 反馈升级

项目经验先记为 candidate-pattern。至少在两个性质不同的项目中有效，且没有破坏已有原则，才能进入通用元模型。只在一个项目中成立的规则保留为项目 profile。
