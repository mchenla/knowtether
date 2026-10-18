---
type: original-work
work_id: KPDM
work_type: framework
title: 知识产品开发元模型
english_title: Knowledge Product Development Meta-Model
status: candidate
version: 0.5.0-rc.2
accepted_baseline: 0.4.0 trial / conditional-pass
created: 2026-08-11
updated: 2026-09-14
authority: work-entry
---

# 知识产品开发元模型（KPDM）

KPDM 是一套由人主导、AI Agent 主动辅助的原创知识开发框架。它帮助创作者从问题、经验、材料和思想出发，发展可说明的知识贡献，形成框架、书籍、文章、报告或系列成果，并通过检查、实际使用和反馈持续修订。人的主导权贯穿问题选择、思想发展、价值取舍、核心主张和最终表达；Agent 在明确授权内研究、提议、质疑、起草和核验。对于还没有中心思想的任务，可以先探索再形成主张；研究概览本身可以是交付物。框架同时支持不使用 Agent 的创作。

## 从哪里开始

- 要做一件具体的事：[快速入门](00%20Start/%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8.md)，从一句话任务开始，用一张 [工作单](04%20Templates/%E8%BD%BB%E9%87%8F%E5%B7%A5%E4%BD%9C%E5%8D%95%E6%A8%A1%E6%9D%BF.md)。
- 要知道你的成果类型有什么要求：[知识产品类型适配](02%20Methods%20and%20Protocols/%E7%9F%A5%E8%AF%86%E4%BA%A7%E5%93%81%E7%B1%BB%E5%9E%8B%E9%80%82%E9%85%8D.md)。
- 要看规则本身：按下表三层阅读。

| 层 | 权威文件 | 回答的问题 |
|---|---|---|
| 创作内核与原则 | [KPDM 三层元模型](01%20Foundations/KPDM%20%E4%B8%89%E5%B1%82%E5%85%83%E6%A8%A1%E5%9E%8B.md) | 创作知识产品必须想清楚什么（Core-6）；所有实例继承哪些原则与红线 |
| 质量约束 | [KPDM 质量约束](01%20Foundations/KPDM%20%E8%B4%A8%E9%87%8F%E7%BA%A6%E6%9D%9F.md)、[质量高度与验收等级](03%20Quality%20and%20Governance/%E8%B4%A8%E9%87%8F%E9%AB%98%E5%BA%A6%E4%B8%8E%E9%AA%8C%E6%94%B6%E7%AD%89%E7%BA%A7.md) | 任何成果必须接受哪些检查；高度怎样变成门槛 |
| 协作与生产支持 | [KPDM 生产控制层](02%20Methods%20and%20Protocols/KPDM%20%E7%94%9F%E4%BA%A7%E6%8E%A7%E5%88%B6%E5%B1%82.md)、[人机协作协议](02%20Methods%20and%20Protocols/%E4%BA%BA%E6%9C%BA%E5%8D%8F%E4%BD%9C%E5%8D%8F%E8%AE%AE.md)、[上下文包与工作包协议](02%20Methods%20and%20Protocols/%E4%B8%8A%E4%B8%8B%E6%96%87%E5%8C%85%E4%B8%8E%E5%B7%A5%E4%BD%9C%E5%8C%85%E5%8D%8F%E8%AE%AE.md) | 人和 Agent 各管什么；什么时候一张工作单够，什么时候要展开 |

完整清单见 [KPDM 知识索引](KPDM%20%E7%9F%A5%E8%AF%86%E7%B4%A2%E5%BC%95.md)。产品需求见 [KPDM 产品需求文档](01%20Foundations/KPDM%20%E4%BA%A7%E5%93%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3.md)，需求到文件的对应见 [KPDM 0.5 需求映射与迁移](08%20Evolution/KPDM%200.5%20%E9%9C%80%E6%B1%82%E6%98%A0%E5%B0%84%E4%B8%8E%E8%BF%81%E7%A7%BB.md)。

## 当前边界

覆盖以提升认知、判断、学习、行动或创造能力为目的的知识创作。框架或知识体系、书籍、文章、报告、系列成果为平等的产品类型。知识型叙事属于适用范围；纯文学与纯艺术创作暂不纳入，只保留扩展接口。

## 版本与状态

| 项 | 值 |
|---|---|
| 最近接受基线 | 0.4.0 trial / conditional-pass（2026-08-11 起，含 0.4.1–0.4.4 的三层文档） |
| 当前正文 | 0.5.0-rc.2 candidate，2026-09-14 按 KPDM-PRODUCT-REQ-01 重构，待作者接受 |
| 机器模型 | `05 Machine Model/kpdm.v0.5.0-rc.2.json`（候选）；`kpdm.v0.4.json`（基线） |
| 已执行的检查 | 结构检查与规范一致性检查，见项目目录 `20260914/KPDM-v0.5.0-rc.2/validation_report.json` |
| 未执行的检查 | 作者体验、异质项目、真实读者任务、外部效度（O-04、O-09，PRD V01–V05） |

0.5.0-rc.2 把 0.4 的 20 份规范合并为 13 份；被合并文件的原路径保留为兼容指针，0.4.0 原文保存在 `99 Versions/0.4.0/`。作者接受本版前，0.4.0 仍是对外引用的基线；接受后登记为 0.5.0 基线并关闭对应决策。状态主张纪律见 [KPDM 质量约束](01%20Foundations/KPDM%20%E8%B4%A8%E9%87%8F%E7%BA%A6%E6%9D%9F.md)：不得以文件齐全、版本升级或作者自评替代验证。

## 相关原创作品

- 《知识产品工程》（未随公开包分发）：基于 KPDM 内核形成的书籍作品，拥有独立 work_id、版本和生命周期；本次重构不同步书稿。

## 项目治理

| 项目 | 状态 | 位置 |
|---|---|---|
| KPDM 0.4 基线建设 | conditional-closed | KPDM 项目索引（未随公开包分发） |
| KPDM 0.5 三层重构 | doing | KPDM 0.5 项目索引（未随公开包分发） |

长期维护责任归 README（未随公开包分发）。后续重大版本必须另行立项。

## 权威规则

作者规范源目录是 KPDM 框架作品的唯一权威源；本文件为其公开快照，只容纳规范正文、模板、机器模型和演进记录。项目文件可以链接本目录，但不得复制并修改规范正文；构建脚本、临时产物和其他作品的工作文件不得存放于此。
