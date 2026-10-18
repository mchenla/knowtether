# 知据 KnowTether

**和 AI 一起，把资料与想法写成有依据、能用的文章、汇报和书稿。**

[English](README.en.md) · [KPDM 方法](framework/kpdm/README.md) · [能力核对](docs/capabilities.md) · [下载](https://github.com/mchenla/knowtether/releases/latest)

## 一眼了解

| 问题 | 回答 |
| --- | --- |
| 是什么 · Ontology | 一个开源的人机知识协作助手，由 KPDM 方法与 KnowTether 插件组成。 |
| 为什么用 · Why | 把来源、判断和表达要求带进 AI 写作，方便核对与修改。 |
| 提供什么 · What | 方法规范、模板、写作提醒、工作记录和有限的自动检查。 |
| 在哪里用 · Where | Codex 插件；Claude Code 项目 Hook。规范也能单独阅读使用。 |
| 谁来用 · Who | 用 AI 写工作文档、汇报、学术报告、知识文章或书籍的人。 |
| 什么时候用 · When | 明确任务、起草、审阅与交付知识成果时。 |
| 怎么用 · How | 安装并信任 Hook，照常用自然语言提任务；Agent 接收提醒，人核对并作决定。 |

**KPDM 全称：Knowledge Product Development Meta-Model，知识产品开发元模型。** 它说明人与 AI 如何把资料、想法做成可理解、可使用、可检查的知识成果；知据把其中部分要求带进 Agent 工作流。

## 可以拿它做什么

| 场景 | 直接这样提任务 | 知据提醒Agent关注什么 |
| --- | --- | --- |
| 工作汇报PPT | 根据这些资料，写8页下季度AI试点汇报，最后给待决事项。 | 每页一个判断；证据、方案、成本与决定相连。 |
| 工作文档 | 把访谈和数据写成项目复盘，给下一步建议。 | 分清事实、解释和建议；不虚构成果。 |
| 学术报告、研究综述 | 比较这些研究，解释结论为什么不同。 | 比较研究设计、指标与适用范围，处理反例，保留出处。 |
| 知识文章 | 给新同事解释这个概念，并给一个可练习的例子。 | 用熟悉的词和具体例子，避免空泛断言。 |
| 工具书、教材 | 写一章让团队负责人能照着做的小型试验方法。 | 有可执行步骤、练习与检查办法，不只列目录。 |
| 出版物 | 审阅这一章的主张、引用和读者任务。 | 区分草稿与核验；保留署名、权利、编辑及真实读者检查。 |

插件提供指导和有限检查；PPTX、Word等文件生成取决于宿主工具，知据本身不负责排版导出。

## Before / After：工具书章节的一处实际差异

任务：写一章教团队负责人判断AI是否真的提效。下列是同一任务第二轮启停对照的原文选段，不是同一份稿子的前后编辑。

| Before：停用 | After：启用0.5.0 |
| --- | --- |
| “下一轮可以检查核验负担来自哪里，调整后重新比较。” | “达到预设条件，就限于该范围扩大试用；收益被复核抵消，就调整后重试；出现严重错误，立即暂停该用途。” |

这次差别在于**把调整建议补成了继续、重试和暂停的判断条件**。停用版同样有可用方法与计算练习；另一轮没有这项差别。六对复杂任务中，仅此一对观察到步骤完整性改善，其余预定内容标准持平，不能据此宣称普遍提升质量。[任务、判断与限制](docs/evaluation-0.5.0.md)

## Codex：两条命令安装

需要支持插件命令的 Codex，以及非交互 PATH 中的 Python 3.10+：

```bash
codex plugin marketplace add mchenla/knowtether
codex plugin add knowtether@knowtether
```

进入 Codex 的 `/hooks`，审阅并信任三个知据 Hook，再开新会话；桌面端安装后重启。无需另行 pip 安装。

照常提任务，无需提示标签。**短任务只给简短指导；复杂写作才读相关KPDM选段**，如报告或书籍的专门要求。已有足够指导时不再重复打开Skill；需要完整流程可明确要求“按完整KPDM处理”。[分层读取与局限](docs/minimum-reading.md)

已有用户先运行 `codex plugin marketplace upgrade knowtether`，再执行上述 `codex plugin add` 命令。[完整插件说明](docs/codex-plugin.md) · [Python CLI 与 Claude Code](docs/cli.md)

## 实际能做到什么

Hook 在会话开始、知识请求提交和回答结束时提供提醒或检查。当前文本提示覆盖引用占位、部分强断言、独立验证措辞、集中套语、数字区间长破折号、少数夸大赞美句及部分不可见字符；有工作单时还检查记录与版本一致性。

协作要求包括不迎合、不无故争辩、不盲从，分类适用时检查MECE；表达要求具体、自然、有人的动作，避免冷套语、机械标题和不合文体的格式。它们是指导，不能保证彻底消除语义或语言问题。不可见字符提示也不等于水印识别；不提供统计水印移除或绕过AI检测器的承诺。没有告警不表示质量通过。[逐项支持与证据](docs/capabilities.md) · [验证记录](docs/validation.md)

本轮短任务的指导量较0.4.1减少约93%，耗时中位数约25.3秒降到17.5秒；停用约8.2秒。复杂任务相对停用仍更慢。每类仅两轮，数字是本机小样本观察。[完整对照](docs/evaluation-0.5.0.md) · [0.4.1历史对照](docs/evaluation-0.4.1.md)

## 开源与版本

- 当前软件：**0.5.0**。[插件、独立规范、源码及校验文件下载](https://github.com/mchenla/knowtether/releases/latest)
- [KPDM 正文、模板和机器模型](framework/kpdm/README.md)：**CC BY 4.0**；KnowTether 代码和适配说明：**MIT**。[许可范围](LICENSING.md)
- KPDM 正文：**0.5.0-rc.2 candidate**；最近接受基线：**0.4.0 trial / conditional-pass**。发布软件不改变框架状态。

[人机协作知识创作学：学科建设草案](framework/kpdm/extensions/人机协作知识创作学.md) · [贡献与问题反馈](CONTRIBUTING.md) · [安全说明](SECURITY.md)
