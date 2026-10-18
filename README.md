# 知据 KnowTether

**和 AI 一起，把资料与想法写成有依据、讲得清的文章和报告。**

[English](README.en.md) · [KPDM 方法](framework/kpdm/README.md) · [能力核对](docs/capabilities.md) · [下载](https://github.com/mchenla/knowtether/releases/latest)

## 一眼了解

| 问题 | 回答 |
| --- | --- |
| 是什么 · Ontology | 一个开源的人机知识协作助手，由 KPDM 方法与 KnowTether 插件组成。 |
| 为什么用 · Why | 把来源、判断和表达要求带进 AI 写作，方便核对与修改。 |
| 提供什么 · What | 方法规范、模板、写作提醒、工作记录和有限的自动检查。 |
| 在哪里用 · Where | Codex 插件；Claude Code 项目 Hook。规范也能单独阅读使用。 |
| 谁来用 · Who | 用 AI 写文章、报告、研究综述或发展框架的人。 |
| 什么时候用 · When | 明确任务、起草、审阅与交付知识成果时。 |
| 怎么用 · How | 安装并信任 Hook，照常用自然语言提任务；Agent 接收提醒，人核对并作决定。 |

**KPDM 全称：Knowledge Product Development Meta-Model，知识产品开发元模型。** 它说明人与 AI 如何把资料、想法做成可理解、可使用、可检查的知识成果；知据把其中部分要求带进 Agent 工作流。

## Codex：两条命令安装

需要支持插件命令的 Codex，以及非交互 PATH 中的 Python 3.10+：

```bash
codex plugin marketplace add mchenla/knowtether
codex plugin add knowtether@knowtether
```

进入 Codex 的 `/hooks`，审阅并信任三个知据 Hook，再开新会话；桌面端安装后重启。无需另行 pip 安装。

照常提任务，例如：“给研究生写一篇文章，解释为什么读了很多论文仍写不好文献综述，并给出练习方法。”无需提示标签。匹配知识请求后，Hook 会先读取并校验随包必要规范，将原文选段与协作要求交给 Agent。[读取机制与局限](docs/minimum-reading.md)

已有用户先运行 `codex plugin marketplace upgrade knowtether`，再执行上述 `codex plugin add` 命令。[完整插件说明](docs/codex-plugin.md) · [Python CLI 与 Claude Code](docs/cli.md)

## 实际能做到什么

Hook 在会话开始、知识请求提交和回答结束时提供提醒或检查。当前自动文本检查只覆盖引用占位、部分强断言、独立验证措辞、集中套语和数字区间长破折号；有工作单时还检查记录与版本一致性。

它不保证消除谄媚、抬杠、盲从、断章取义、事实错误、分类遗漏或 AI 文风，也不提供语法纠正、技术水印检测与移除。0.4.0 已补上写作前的最小原文阅读包和明确协作要求；启停对照的24份输出中，区间表达细则有所改善，其他已测语义任务两组表现相近；启用后的耗时和输入量增加。[对照结果与原文](docs/evaluation-0.4.1.md)没有告警不表示质量通过。[逐项支持与证据](docs/capabilities.md) · [验证记录](docs/validation.md)

## 开源与版本

- 当前软件：**0.4.1**。[插件、独立规范、源码及校验文件下载](https://github.com/mchenla/knowtether/releases/latest)
- [KPDM 正文、模板和机器模型](framework/kpdm/README.md)：**CC BY 4.0**；KnowTether 代码和适配说明：**MIT**。[许可范围](LICENSING.md)
- KPDM 正文：**0.5.0-rc.2 candidate**；最近接受基线：**0.4.0 trial / conditional-pass**。发布软件不改变框架状态。

[人机协作知识创作学：学科建设草案](framework/kpdm/extensions/人机协作知识创作学.md) · [贡献与问题反馈](CONTRIBUTING.md) · [安全说明](SECURITY.md)
