---
type: work-changelog
work_id: KPDM
updated: 2026-09-20
---

# KPDM 变更日志

## Punctuation fingerprint: em dash - 2026-09-20

- 《KPDM 质量约束》“模型语言指纹与文字温度”新增第 7 条：长破折号（“—”“——”）作为连接、区间与并列分隔是模型偏好的标点习惯，改写优先级表加入对应规则（改为 " - "、冒号、逗号或顿号，仅在真正的插入语或转折处保留）。
- 触发：HYRubber 销售资料 V2 审校（作者指出“1992 — 2026”“……——……”属 AI 偏好错误）。
- 不改变六项约束实质，不改版本号；rc.2 候选状态不变。

## 0.5.0-rc.2 — Restructuring per product requirements — 2026-09-14

按 [KPDM 产品需求文档](../01%20Foundations/KPDM%20%E4%BA%A7%E5%93%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3.md)（KPDM-PRODUCT-REQ-01，文档版本 1.1.0）重构权威源。本版为候选，待作者接受；最近接受基线仍为 0.4.0 trial / conditional-pass。

- 定位改为「由人主导、AI Agent 主动辅助的原创知识开发框架」；框架或知识体系、书籍、文章、报告、系列成果为平等 Profile，新增报告 Profile；
- 20 份规范合并为 13 份：总纲与普适原则并入三层元模型；开发生命周期并入生产控制层；人机协作知识生产系统并入人机协作协议；实例化初始化协议并入上下文包与工作包协议；版权引用协议并入权威主张证据治理；反馈学习与版本治理并入回归测试与发布候选；质量SLO 与 PDCA 校验并入质量高度与验收等级。被合并文件原路径改为兼容指针，0.4.0 原文存 `99 Versions/0.4.0/`；协议编号 INIT-01、PROD-01、PRD-01 保留；
- 新增 [快速入门](../00%20Start/%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8.md)（含两种起点与 §6.3 设计情境）、[轻量工作单模板](../04%20Templates/%E8%BD%BB%E9%87%8F%E5%B7%A5%E4%BD%9C%E5%8D%95%E6%A8%A1%E6%9D%BF.md)（八项，含研究任务填法）、[知识概览模板](../04%20Templates/%E7%9F%A5%E8%AF%86%E6%A6%82%E8%A7%88%E6%A8%A1%E6%9D%BF.md)（概览、材料记录七列、交接与恢复、设计情境示例）、字段映射表、增加控制的触发条件、必须返回人的情形、创作活动分工表、研究循环与停止条件、变更影响规则、读者任务验证、引用与论证反例检查、七条阻断条件、轻量入口的最少发布检查；
- 按 D024 把总纲「四层成果」改写为产物视图；按 D025 把状态主张表示为 Claim 的 status 子类型；生产状态增加 `author-accepted`；两项裁决仍为 proposed-author-review；
- 机器模型 `kpdm.v0.5.0-rc.2.json` 与 Schema 迁入 `05 Machine Model/`，增加 `documents`、`status_model`、`escalation_triggers`、`return_to_human`、`research_loop`、`blocking_conditions`、`material_record_fields`、`acceptance`，协议增加 `document` 字段；`examples/` 含 1 正例 11 负例；标准 Draft 2020-12 校验与规范一致性检查在项目目录执行并留报告；
- 所有模板标明 `applies_to: 0.5.0-rc.2`；项目章程模板增加报告 Profile；
- 本次不同步《知识产品工程》书稿，不执行 V01–V10，不关闭 O-04、O-09；R20、R22 保留为后续扩展；结构与一致性检查通过不构成外部效度提升。

## STORM-informed product requirements — 2026-09-14

- [KPDM 产品需求文档](../01%20Foundations/KPDM%20%E4%BA%A7%E5%93%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3.md) 文档版本更新为 1.1.0：基于 STORM／Co-STORM 官方仓库、两篇论文及接口／引擎实现，补充开放研究与聚焦任务入口、材料驱动追问、用户转向与停止、知识概览及中间成果恢复；
- 扩展 R01、R07，新增 R17–R22 和 V07–V10；加入引用不支持主张、同源转载、错误因果关联、搜索摘要与作者假设等反例检查；
- 将研究能力纳入原八项工作单及 M2／M3 交付，不要求新增元对象、多 Agent 调度或图形界面；
- 更新外部依据登记和索引；外部方法的实验结果不计为 KPDM 验证，新功能与门槛均为需求提案；
- 框架版本仍为 0.4.0 trial / conditional-pass；本次未运行 STORM、迁入候选规范或进行对外发布。

## Product requirements rewrite — 2026-09-14

- 新增 [KPDM 产品需求文档](../01%20Foundations/KPDM%20%E4%BA%A7%E5%93%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3.md)，根据当前权威规范及 0.5.0-rc.1 候选包，重写框架产品的定位、用户任务、范围、创作流程、人机分工和验收要求；
- 定义 16 项需求与 6 组验证计划，区分已有检查记录和新增试用门槛；
- 在 README 与知识索引增加产品需求入口；
- 本次仅形成产品需求提案，不迁入 0.5 候选规范，不关闭既有开放项，框架仍为 0.4.0 trial / conditional-pass。

## Structure and authority restructuring — 2026-08-25

- 裁决元模型权威关系：[KPDM 三层元模型](../01%20Foundations/KPDM%20%E4%B8%89%E5%B1%82%E5%85%83%E6%A8%A1%E5%9E%8B.md) 为唯一元模型宪法，[KPDM 元模型](../01%20Foundations/KPDM%20%E5%85%83%E6%A8%A1%E5%9E%8B.md) 降为其下位对象模型（KPDM-D018）；文件名按 KPDM-D013 保留不变；
- 权威源目录清理：EA 构建包、CBBOK 评分与修复脚本、书稿渲染证据、`__pycache__` 与临时文件迁出 `未随公开包分发的作者本地记录`，作品目录只保留规范正文、模板、机器模型与演进记录（KPDM-D019）；
- 已关闭项目迁入 `未随公开包分发的作者本地记录`，历史 PDCA 与校验记录中的原路径按 KPDM-D013 不回写（KPDM-D020）；
- 为 2026-08-12 与 2026-08-18 的既成演进补立项目容器 KPDM 0.5 项目索引（未随公开包分发） 与 `KPDM-PDCA-06`；
- 本次不改变 0.4.0 trial / conditional-pass 状态，也不改变任何规范正文的实质内容。

## Model-language fingerprint and prose warmth — 2026-08-18

- 新增大模型偏好词、机械句式、抽象词堆叠和自造概念的识别规则；
- 明确“锁、情境、边界、证据、循证、纪律、铁律”等词不是禁词，但不得成为万能表达支架；
- 建立从模型语言还原到具体对象、动作、来源和自然专业表达的改写规则；
- 将文字温度和独立编辑检查纳入 Q3–Q4 语言质量硬门。

## Status-claim discipline — 2026-08-12

- 将完成度、成熟度、有效性、可靠性、可用性和权威性明确为必须验证的状态主张；
- 新增“不得自证完成”规则，禁止用作者声明、文件齐全、版本升级、虚拟案例或 AI 自评替代质量与真实效度证据；
- 在生产控制层区分生产状态、质量与验证状态、发布状态及限制限定；
- 在 Release Gate 增加状态词、验证主体、派生视图继承和 Q3–Q4 独立复核检查。
## Vault object-model restructuring — 2026-08-11

- 将框架 KPDM 与书籍《知识产品工程》拆为 `50 Original Works` 下的并列作品；
- 将 KPDM 0.4 基线建设与《知识产品工程》第一稿开发拆为两个临时项目并完成条件关闭；
- 项目开发记录分别归档于 `未随公开包分发的作者本地记录` 与 `未随公开包分发的作者本地记录`；
- 建立 `未随公开包分发的作者本地记录` 承担无结束日期的长期维护责任；
- 建立 Vault 对象分类与项目准入规则，后续重大版本必须重新立项。

## Workspace authority migration — 2026-08-11

- 将总纲、元模型、原则、协议、质量规则、模板和机器模型移入 `未随公开包分发的作者本地记录`；
- 将《知识产品工程》正文和成品 PDF 移入原创作品区（其后进一步拆为独立书籍作品）；
- 当时 PDCA、决策、案例、出版开发包、构建脚本和 QA 保留在 `未随公开包分发的作者本地记录`；最终按交付物拆入两个已关闭项目；
- 建立 `KPDM 知识索引` 与 `KPDM 项目索引`；
- 更新 CBBOK 跨项目链接和 PDF 构建路径；
- 模型语义版本保持 0.4.0，本次只改变权威位置和项目结构。


## 0.4.0 — 2026-08-11

- 正式名称改为“知识产品开发元模型”，英文 Knowledge Product Development Meta-Model；
- 建立 `KPDM` 项目、协议、PDCA、决策、出版实例和机器文件命名空间；
- 新增 [命名空间与定位](../01%20Foundations/%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4%E4%B8%8E%E5%AE%9A%E4%BD%8D.md)、`kpdm.v0.4.json` 和 `kpdm.schema.v0.4.json`；
- 主动协议由 `MF-*` 迁移为 `KPDM-*`；
- v0.1–v0.3 机器模型、历史 PDCA、案例和决策编号保持不可变；
- 建立旧名称、旧文件名和旧目录兼容入口；
- 出版视图升级为 KPDM Publication 0.2.0，并重建 PDF 品牌与元数据。

## KPDM Publication 0.2.0 — 2026-08-11

- 将出版视图中的 Meta-Framework 品牌更新为知识产品开发元模型（KPDM）；
- 出版实例 ID 由 `MF-PUB-*` 迁移为 `KPDM-PUB-*`；
- 书名《知识产品工程》保持不变。

## Publication 0.1.0 — 2026-08-11

- 以 book-publication Profile 实例化 Meta-Framework；
- 建立《知识产品工程：AI时代的人机协作创作元模型》项目章程、ContextPack、ClaimGraph 和 WorkPackets；
- 完成五部分十二章、约 1.25 万字符的完整第一稿；
- 建立 MF-PUB-PDCA-01、第一稿置信向量、不确定性负荷和第二稿触发条件；
- 生成 38 页 A5 书稿 PDF，完成逐页渲染、字体嵌入、目录、书签和视觉 QA；
- 当前仅为 Q1 Working Manuscript，不通过公开 Release Gate。

## 0.3.0 — 2026-08-11

- 新增人机协作知识生产系统与 Explore、Architect、Produce、Verify 四模式；
- 新增 ContextPack、WorkPacket、ClaimGraph、QualitySLO、UncertaintyItem、RegressionTest、GoldenCase、ReleaseCandidate；
- 元对象由十九个扩展为二十七个；
- 新增七维置信向量、风险加权不确定性燃尽和历史周期校准规则；
- 新增 MF-PROD-01、MF-WP-01、MF-RC-01 及四个执行模板；
- 新增 v0.3 机器模型、Schema、自举 GoldenCase 与 MF-PDCA-03；
- 保持 trial 状态，自举不计作跨项目验证。

## 0.2.0 — 2026-08-11

- 新增十二条普适原则和七条发布红线；
- 新增 Q0–Q4 质量高度与十维质量模型；
- 新增 MF-INIT-01 实例化初始化协议；
- 新增 MF-HAI-01 人机协作协议和风险分层核验；
- 新增 MF-PRD-01 版权、引用、数据和来源协议；
- 元对象由十四个扩展为十九个；
- 新增发布前合规检查和正式外部依据登记。

## 0.1.0 — 2026-08-11

- 从 CBBOK 开发实践提取首版个人知识产品开发元模型；
- 建立十四个核心元对象、八阶段生命周期和阶段门；
- 建立成果校验 PDCA、加权进度、主张—证据和权威治理；
- 建立知识体系、著作或出版物、文章和系列内容 profile；
- 建立反馈回灌与跨项目升级规则；
- CBBOK 登记为首个反向验证案例。
