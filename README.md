# 知据 KnowTether

**和 AI 一起，把资料与想法写成有依据、能用的文章、汇报和书稿。**

[English](README.en.md) · [KPDM 方法](framework/kpdm/README.md) · [能力核对](docs/capabilities.md) · [下载](https://github.com/mchenla/knowtether/releases/latest)

## 一眼了解

| 问题 | 回答 |
| --- | --- |
| 是什么 · Ontology | 一个开源的人机知识协作助手，由 KPDM 方法与 KnowTether 插件组成。 |
| 为什么用 · Why | 把来源、判断和表达要求带进 AI 写作，方便核对与修改。 |
| 提供什么 · What | 方法规范、模板、写作提醒、工作记录和有限的自动检查。 |
| 在哪里用 · Where | Codex 插件；Claude Code 插件或项目 Hook。规范也能单独阅读使用。 |
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

## Before / After：从资料到工作汇报

任务：根据含缺行、附件缺失、版本冲突和错误结论的资料，写6页工作汇报，决定两个人日该投在哪里。固定展示本轮第1次启停稿。

| Before：停用 | After：启用0.7.0及核算 |
| --- | --- |
| “现有15条记录，仅7个完整配对，低于预期16条。” | “实际仅15条运行记录，少于清单预期16条；读者验证文件缺失。” |
| 68.334秒，7次工具调用，累计输入85965 token | 62.986秒，2次工具调用，累计输入47741 token |

**两稿都正确处理六类问题，没有新增找错优势。** 此对减少了工具往返，但启用稿仍有两页讲述提示超1 - 2字符，需编辑。

整组16稿中，配对耗时变化中位数约少2% - 11%；累计输入在汇报约少37% - 38%、完整章节约少19%，缺陷章节却约多8%。启用注入6310 - 6409字符；首次请求输入增加，累计输入不能当账单。每项仅两轮、开发AI评阅；启用章节还出现补测计划不封顶的问题，**没有证明复杂写作质量稳定提升**。[16稿、质量与全部开销](docs/evaluation-0.7.0.md)

0.7.0保留其他Agent的Claude插件和显式发布检查，补齐发行文件，并修复六个机械误放行反例；自动指导没有加码。Claude清单和Git Bash启动器已验证，完整Claude模型会话仍未验证；托管审阅Agent保留在原PR。[整合审查](docs/integration-review-0.7.0.md) · [此前24稿对照](docs/evaluation-0.6.0-source-quality.md)

## Codex：两条命令安装

需要支持插件命令的 Codex，以及非交互 PATH 中的 Python 3.10+：

```bash
codex plugin marketplace add mchenla/knowtether
codex plugin add knowtether@knowtether
```

进入 Codex 的 `/hooks`，审阅并信任三个知据 Hook，再开新会话；桌面端安装后重启。无需另行 pip 安装。

照常提任务，无需提示标签。**短任务只给简短指导；复杂写作才读相关KPDM选段**，如报告或书籍的专门要求。已有足够指导时不再重复打开Skill；需要完整流程可明确要求“按完整KPDM处理”。[分层读取与局限](docs/minimum-reading.md)

已有用户先运行 `codex plugin marketplace upgrade knowtether`，再执行上述 `codex plugin add` 命令。[完整插件说明](docs/codex-plugin.md) · [Python CLI 与 Claude Code](docs/cli.md)

## Claude Code：一条命令安装

需要 Claude Code 2.1.275+ 与 `PATH` 上的 Python 3.10+。在会话中运行：

```
/plugin install knowtether --marketplace mchenla/knowtether
```

同一组 Hook 照常提醒；另有 `/knowtether:start`、`research`、`draft`、`check`、`release`、`handoff`、`adopt` 七个命令，从一句话任务到发布前检查。[Claude Code 插件说明](docs/claude-plugin.md)

## 实际能做到什么

Hook 在会话开始、知识请求提交和回答结束时提供提醒或检查。有配对数据时，可用显式项目清单加入计算与来源回执；普通写作无需建表。[可选资料计算](docs/project-evidence.md)

明确运行发布检查时，硬门会拦下五类问题：未经人核对的事实来源、残留引用占位、权利未知的材料、没有对应版本的接受记录、成品里的工作流标签；它只检查记录与文本，不判定内容真假。[发布硬门](docs/cli.md#发布硬门)

当前文本提示覆盖引用占位、部分强断言、独立验证措辞、集中套语、数字区间长破折号、少数夸大赞美句及部分不可见字符；有工作单时还检查记录与版本一致性。

协作要求包括不迎合、不无故争辩、不盲从，分类适用时检查MECE；表达要求具体、自然、有人的动作，避免冷套语、机械标题和不合文体的格式。它们是指导，不能保证彻底消除语义或语言问题。不可见字符提示也不等于水印识别；不提供统计水印移除或绕过AI检测器的承诺。没有告警不表示质量通过。[逐项支持与证据](docs/capabilities.md) · [验证记录](docs/validation.md)

此前短任务的指导量已较0.4.1减少约93%；复杂写作仍需权衡等待和收益。去谄媚、自然文风和MECE等要求继续保留，但本轮没有证明这些语义能力进一步改善。[历史对照](docs/evaluation-0.5.0.md)

## 开源与版本

- 当前软件：**0.7.0**。[插件、独立规范、源码及校验文件下载](https://github.com/mchenla/knowtether/releases/latest)
- [KPDM 正文、模板和机器模型](framework/kpdm/README.md)：**CC BY 4.0**；KnowTether 代码和适配说明：**MIT**。[许可范围](LICENSING.md)
- KPDM 正文：**0.5.0-rc.2 candidate**；最近接受基线：**0.4.0 trial / conditional-pass**。发布软件不改变框架状态。

[人机协作知识创作学：学科建设草案](framework/kpdm/extensions/人机协作知识创作学.md) · [贡献与问题反馈](CONTRIBUTING.md) · [安全说明](SECURITY.md)
