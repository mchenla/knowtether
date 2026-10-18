---
type: moc
work_id: KPDM
status: candidate
version: 0.5.0-rc.2
accepted_baseline: 0.4.0
created: 2026-08-11
updated: 2026-09-14
authority: knowledge-index
---

# KPDM 知识索引

阅读、引用与出版入口。开发与验证记录不在本页，见「开发治理」。当前正文为 0.5.0-rc.2 候选，待作者接受；最近接受基线为 0.4.0 trial。

## 使用入口

- [快速入门](00%20Start/%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8.md)：从一句话任务开始；接手与增量接入
- [轻量工作单模板](04%20Templates/%E8%BD%BB%E9%87%8F%E5%B7%A5%E4%BD%9C%E5%8D%95%E6%A8%A1%E6%9D%BF.md)：八项工作单
- [知识概览模板](04%20Templates/%E7%9F%A5%E8%AF%86%E6%A6%82%E8%A7%88%E6%A8%A1%E6%9D%BF.md)：研究任务的知识概览、材料记录与交接（含设计情境示例）
- [KPDM 产品需求文档](01%20Foundations/KPDM%20%E4%BA%A7%E5%93%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3.md)：面向 0.5.x 的产品定义、需求与验收提案（KPDM-PRODUCT-REQ-01，文档版本 1.1.0，含研究入口与 R17–R22）
- [KPDM 0.5 需求映射与迁移](08%20Evolution/KPDM%200.5%20%E9%9C%80%E6%B1%82%E6%98%A0%E5%B0%84%E4%B8%8E%E8%BF%81%E7%A7%BB.md)：需求到文件、字段与检查的对应；0.4 文件去向

## 第一层｜创作内核、原则与对象

- [KPDM 三层元模型](01%20Foundations/KPDM%20%E4%B8%89%E5%B1%82%E5%85%83%E6%A8%A1%E5%9E%8B.md)：唯一元模型宪法。定位与人的主导权、Core-6、产物视图、十二条普适原则、七条发布红线、完成定义
- [KPDM 元模型](01%20Foundations/KPDM%20%E5%85%83%E6%A8%A1%E5%9E%8B.md)：27 个对象的定义与字段、主张类型（含 status 子类型）、权威与视图规则、状态模型
- [命名空间与定位](01%20Foundations/%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4%E4%B8%8E%E5%AE%9A%E4%BD%8D.md)：正式身份、命名规则、旧命名空间迁移、0.5 文件合并

## 第二层｜质量约束与验收

- [KPDM 质量约束](01%20Foundations/KPDM%20%E8%B4%A8%E9%87%8F%E7%BA%A6%E6%9D%9F.md)：真实性、人类可理解性、概念克制、权利安全、认知诚实、可追溯性；新术语准入、反迎合、状态主张纪律、模型语言指纹、元话语隔离
- [质量高度与验收等级](03%20Quality%20and%20Governance/%E8%B4%A8%E9%87%8F%E9%AB%98%E5%BA%A6%E4%B8%8E%E9%AA%8C%E6%94%B6%E7%AD%89%E7%BA%A7.md)：Q0–Q4 与十维模型；读者任务验证；QualitySLO、置信向量、不确定性；验证合同与 PDCA 校验
- [发布前合规与完整性检查](03%20Quality%20and%20Governance/%E5%8F%91%E5%B8%83%E5%89%8D%E5%90%88%E8%A7%84%E4%B8%8E%E5%AE%8C%E6%95%B4%E6%80%A7%E6%A3%80%E6%9F%A5.md)：轻量入口的最少检查；Release Gate 清单

## 第三层｜协作与生产支持

- [KPDM 生产控制层](02%20Methods%20and%20Protocols/KPDM%20%E7%94%9F%E4%BA%A7%E6%8E%A7%E5%88%B6%E5%B1%82.md)：控制对象、裁剪原则、增加控制的触发条件、状态主张控制、G0–G7 与 PDCA
- [人机协作协议](02%20Methods%20and%20Protocols/%E4%BA%BA%E6%9C%BA%E5%8D%8F%E4%BD%9C%E5%8D%8F%E8%AE%AE.md)（KPDM-HAI-01、KPDM-PROD-01）：分工表、必须返回人的情形、授权与接受、四种模式、RACI、跨会话接手
- [上下文包与工作包协议](02%20Methods%20and%20Protocols/%E4%B8%8A%E4%B8%8B%E6%96%87%E5%8C%85%E4%B8%8E%E5%B7%A5%E4%BD%9C%E5%8C%85%E5%8D%8F%E8%AE%AE.md)（KPDM-WP-01、KPDM-INIT-01）：轻量入口、展开路径、字段映射、ContextPack、WorkPacket
- [权威、主张、证据与引用治理](02%20Methods%20and%20Protocols/%E6%9D%83%E5%A8%81%E3%80%81%E4%B8%BB%E5%BC%A0%E3%80%81%E8%AF%81%E6%8D%AE%E4%B8%8E%E5%BC%95%E7%94%A8%E6%B2%BB%E7%90%86.md)（KPDM-PRD-01）：主张—证据规则、来源质量、来源/署名/许可、数据引用、权利审查门
- [知识产品类型适配](02%20Methods%20and%20Protocols/%E7%9F%A5%E8%AF%86%E4%BA%A7%E5%93%81%E7%B1%BB%E5%9E%8B%E9%80%82%E9%85%8D.md)：框架或知识体系、书籍、文章、报告、系列成果五个平等 Profile；裁剪矩阵
- [回归测试、Golden Case与发布候选](02%20Methods%20and%20Protocols/%E5%9B%9E%E5%BD%92%E6%B5%8B%E8%AF%95%E3%80%81Golden%20Case%E4%B8%8E%E5%8F%91%E5%B8%83%E5%80%99%E9%80%89.md)（KPDM-RC-01）：回归、GoldenCase、ReleaseCandidate、变更影响、反馈学习、版本规则

## 兼容指针（0.4 文件，已并入上列文件）

[KPDM 总纲](01%20Foundations/KPDM%20%E6%80%BB%E7%BA%B2.md)、[普适原则与不可妥协底线](01%20Foundations/%E6%99%AE%E9%80%82%E5%8E%9F%E5%88%99%E4%B8%8E%E4%B8%8D%E5%8F%AF%E5%A6%A5%E5%8D%8F%E5%BA%95%E7%BA%BF.md)、[开发生命周期与阶段门](02%20Methods%20and%20Protocols/%E5%BC%80%E5%8F%91%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F%E4%B8%8E%E9%98%B6%E6%AE%B5%E9%97%A8.md)、[人机协作知识生产系统](02%20Methods%20and%20Protocols/%E4%BA%BA%E6%9C%BA%E5%8D%8F%E4%BD%9C%E7%9F%A5%E8%AF%86%E7%94%9F%E4%BA%A7%E7%B3%BB%E7%BB%9F.md)、[实例化初始化协议](02%20Methods%20and%20Protocols/%E5%AE%9E%E4%BE%8B%E5%8C%96%E5%88%9D%E5%A7%8B%E5%8C%96%E5%8D%8F%E8%AE%AE.md)、[版权、引用、数据与来源协议](02%20Methods%20and%20Protocols/%E7%89%88%E6%9D%83%E3%80%81%E5%BC%95%E7%94%A8%E3%80%81%E6%95%B0%E6%8D%AE%E4%B8%8E%E6%9D%A5%E6%BA%90%E5%8D%8F%E8%AE%AE.md)、[反馈学习与版本治理](02%20Methods%20and%20Protocols/%E5%8F%8D%E9%A6%88%E5%AD%A6%E4%B9%A0%E4%B8%8E%E7%89%88%E6%9C%AC%E6%B2%BB%E7%90%86.md)、[质量SLO、置信向量与不确定性治理](02%20Methods%20and%20Protocols/%E8%B4%A8%E9%87%8FSLO%E3%80%81%E7%BD%AE%E4%BF%A1%E5%90%91%E9%87%8F%E4%B8%8E%E4%B8%8D%E7%A1%AE%E5%AE%9A%E6%80%A7%E6%B2%BB%E7%90%86.md)、[PDCA 成果校验与进度治理](03%20Quality%20and%20Governance/PDCA%20%E6%88%90%E6%9E%9C%E6%A0%A1%E9%AA%8C%E4%B8%8E%E8%BF%9B%E5%BA%A6%E6%B2%BB%E7%90%86.md)。0.4.0 原文见 `99 Versions/0.4.0/`。

## 模板

- [轻量工作单模板](04%20Templates/%E8%BD%BB%E9%87%8F%E5%B7%A5%E4%BD%9C%E5%8D%95%E6%A8%A1%E6%9D%BF.md)（默认入口）
- [知识概览模板](04%20Templates/%E7%9F%A5%E8%AF%86%E6%A6%82%E8%A7%88%E6%A8%A1%E6%9D%BF.md)（研究任务）
- [实例化初始化清单](04%20Templates/%E5%AE%9E%E4%BE%8B%E5%8C%96%E5%88%9D%E5%A7%8B%E5%8C%96%E6%B8%85%E5%8D%95.md)（展开初始化清单）
- [项目章程模板](04%20Templates/%E9%A1%B9%E7%9B%AE%E7%AB%A0%E7%A8%8B%E6%A8%A1%E6%9D%BF.md)
- [架构与权威矩阵模板](04%20Templates/%E6%9E%B6%E6%9E%84%E4%B8%8E%E6%9D%83%E5%A8%81%E7%9F%A9%E9%98%B5%E6%A8%A1%E6%9D%BF.md)
- [主张—证据台账模板](04%20Templates/%E4%B8%BB%E5%BC%A0%E2%80%94%E8%AF%81%E6%8D%AE%E5%8F%B0%E8%B4%A6%E6%A8%A1%E6%9D%BF.md)
- [执行进度看板模板](04%20Templates/%E6%89%A7%E8%A1%8C%E8%BF%9B%E5%BA%A6%E7%9C%8B%E6%9D%BF%E6%A8%A1%E6%9D%BF.md)
- [PDCA 循环记录模板](04%20Templates/PDCA%20%E5%BE%AA%E7%8E%AF%E8%AE%B0%E5%BD%95%E6%A8%A1%E6%9D%BF.md)
- [出版单元模板](04%20Templates/%E5%87%BA%E7%89%88%E5%8D%95%E5%85%83%E6%A8%A1%E6%9D%BF.md)
- [来源与权利台账模板](04%20Templates/%E6%9D%A5%E6%BA%90%E4%B8%8E%E6%9D%83%E5%88%A9%E5%8F%B0%E8%B4%A6%E6%A8%A1%E6%9D%BF.md)
- [数据引用记录模板](04%20Templates/%E6%95%B0%E6%8D%AE%E5%BC%95%E7%94%A8%E8%AE%B0%E5%BD%95%E6%A8%A1%E6%9D%BF.md)
- [人机协作记录模板](04%20Templates/%E4%BA%BA%E6%9C%BA%E5%8D%8F%E4%BD%9C%E8%AE%B0%E5%BD%95%E6%A8%A1%E6%9D%BF.md)
- [上下文包模板](04%20Templates/%E4%B8%8A%E4%B8%8B%E6%96%87%E5%8C%85%E6%A8%A1%E6%9D%BF.md)
- [工作包模板](04%20Templates/%E5%B7%A5%E4%BD%9C%E5%8C%85%E6%A8%A1%E6%9D%BF.md)
- [不确定性登记模板](04%20Templates/%E4%B8%8D%E7%A1%AE%E5%AE%9A%E6%80%A7%E7%99%BB%E8%AE%B0%E6%A8%A1%E6%9D%BF.md)
- [回归测试与发布候选模板](04%20Templates/%E5%9B%9E%E5%BD%92%E6%B5%8B%E8%AF%95%E4%B8%8E%E5%8F%91%E5%B8%83%E5%80%99%E9%80%89%E6%A8%A1%E6%9D%BF.md)

模板 frontmatter 标明 `applies_to` 版本。

## 机器模型

- `05 Machine Model/kpdm.v0.5.0-rc.2.json`、`05 Machine Model/kpdm.schema.v0.5.0-rc.2.json`：候选；含三层语义、人主导配置、状态模型、触发条件、研究循环、阻断条件、材料记录字段、文档映射
- `05 Machine Model/examples/`：1 个正例与 11 个负例
- `05 Machine Model/kpdm.v0.4.json`、`05 Machine Model/kpdm.schema.v0.4.json`：最近接受基线，不改

机器检查只覆盖结构与规范一致性；事实判断、可理解性和有效性由来源核验与真人验证承担。检查脚本与报告在项目目录 `未随公开包分发的作者本地记录`。

## 出版视图

`06 Publications` 当前为空：KPDM 的书籍表达已按 VAULT-D016 拆为独立作品 《知识产品工程》（未随公开包分发）。

## 外部依据

- [外部依据与接口登记](07%20References/%E5%A4%96%E9%83%A8%E4%BE%9D%E6%8D%AE%E4%B8%8E%E6%8E%A5%E5%8F%A3%E7%99%BB%E8%AE%B0.md)

## 历史版本

`99 Versions` 保存 v0.1–v0.3 机器快照、旧名称兼容文件，以及 `0.4.0/` 下被合并文件的 0.4.0 原文。均不是当前规范源。

## 演进

- [KPDM 变更日志](08%20Evolution/KPDM%20%E5%8F%98%E6%9B%B4%E6%97%A5%E5%BF%97.md)
- [KPDM 演进路线图](08%20Evolution/KPDM%20%E6%BC%94%E8%BF%9B%E8%B7%AF%E7%BA%BF%E5%9B%BE.md)
- [KPDM 三层表达重构记录](08%20Evolution/KPDM%20%E4%B8%89%E5%B1%82%E8%A1%A8%E8%BE%BE%E9%87%8D%E6%9E%84%E8%AE%B0%E5%BD%95.md)
- [KPDM 0.5 需求映射与迁移](08%20Evolution/KPDM%200.5%20%E9%9C%80%E6%B1%82%E6%98%A0%E5%B0%84%E4%B8%8E%E8%BF%81%E7%A7%BB.md)

## 开发治理

- KPDM 项目索引（未随公开包分发）（conditional-closed）
- KPDM 0.5 项目索引（未随公开包分发）（doing）
