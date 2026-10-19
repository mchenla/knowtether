# Python CLI 与 Claude Code 使用说明

[返回首页](../README.md)。仅使用 Codex 插件时，无须另装 Python CLI 或创建工作单。

## 按项目安装：兼容原 CLI 与 Claude Code

本节及后续 `knowtether` CLI 命令适用于单独安装 Python 发行包的用户。只使用上述 Codex 插件时无须执行这些步骤；可直接使用随插件安装的 `knowtether` Skill 和自动提醒。

需要 Python 3.10 或更新版本，以及支持相应 Hook 事件的主机。Claude Code 需要 2.1.139 或更新版本，以支持本安装器使用的 `args` 直接执行形式，见[官方更新记录](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#21139)。请在知识创作项目中操作，避免把工作文件放进 KPDM 规范源目录。

```bash
git clone https://github.com/mchenla/knowtether.git
cd knowtether
python -m pip install .
```

切换到要启用的项目目录，先预览配置变化，再安装。按使用的主机选择其中一项：

```bash
knowtether install --root . --host codex --dry-run
knowtether install --root . --host codex
```

```bash
knowtether install --root . --host claude --dry-run
knowtether install --root . --host claude
```

安装器合并项目配置，修改已有配置前建立备份；遇到无法安全处理的配置会报告错误。配置位置为：

| 主机 | 项目配置 | 主机要求 |
| --- | --- | --- |
| Codex | `.codex/hooks.json` | 安装后使用 `/hooks` 审阅并信任配置；运行环境还须允许项目 Hook。 |
| Claude Code | `.claude/settings.local.json` | 使用当前协议的 `command` + `args` 直接执行形式；旧版不支持时需要升级。 |

安装还会在缺少时建立 `.kpdm/config.json`，不会代替主机信任步骤或自动全局启用 Hook。启用后按主机要求重新开始或加载会话。本项目尚无覆盖全部主机版本的兼容承诺。官方协议见 [Codex Hooks](https://learn.chatgpt.com/docs/hooks) 和 [Claude Code Hooks](https://code.claude.com/docs/en/hooks)。

所有命令也可以写成 `python -m kpdm_hooks ...`。这对未将 Python 脚本目录加入 `PATH` 的环境尤其有用。

## Hook 什么时候工作

| 事件 | 用途 |
| --- | --- |
| `SessionStart` | 提供按任务启用 KPDM 的提示；发现其他会话的工作单时提醒核对本次委托。 |
| `UserPromptSubmit` | 根据知识任务的轻量匹配结果补充写作提醒。 |
| `Stop` | 对最后一条助手消息做文本启发式检查，并检查当前会话绑定的工作单。 |

短任务可以直接使用提醒，无须先填工作单。复杂成果或需要跨会话追踪的项目，可以启用 `.kpdm/work.json`。

Hook 不读取完整会话来还原授权，不会因提示内容产生新的授权。关键词可能误判；未触发提醒也不表示任务不属于知识创作。

## 为持续任务建立工作单

```bash
knowtether init --root .
```

`init` 依次尝试 `CODEX_THREAD_ID`、`CODEX_SESSION_ID`、`CLAUDE_SESSION_ID`。这些变量在某些运行方式下不存在，此时使用当前 Hook 输入中的 `session_id` 显式传入：

```bash
knowtether init --root . --session-id YOUR_CURRENT_SESSION_ID
```

补充 `.kpdm/work.json` 中的八项 `worksheet`。起草前把前六项写到够用；检查时再更新后两项。已有资料可以引用，未知项保持未知，填写“不适用”时说明原因。

| 字段 | 内容 |
| --- | --- |
| `intent` | 为谁解决什么问题、成果形式、用途和 Q 目标 |
| `central_idea` | 研究问题、暂定主张、拟议贡献或尚未决定的部分 |
| `expression_structure` | 读者如何阅读、理解或查询成果 |
| `evidence_and_scope` | 来源位置、推理、反例、限制、未知与使用权利 |
| `delegation` | 有效输入版本、Agent 可做的工作、停止条件与人的职责 |
| `acceptance` | 读者任务、通过条件、检查方式与责任人 |
| `results_and_revisions` | 实际检查、失败项、修订和仍未解决的问题 |
| `human_decision` | 人接受或退回的具体版本，以及单独的发布决定 |

同时核对 `input_version`、`artifact_version`、`allowed_write_roots` 和 `open_issues`。可选 `claims` 与 `sources` 用于记录主张和来源关系，参见 [示例工作单](../examples/work.json) 和 [规则映射](rules.md)。

接手已有工作单时，先核对当前委托，再绑定当前会话：

```bash
knowtether bind --root . --session-id YOUR_CURRENT_SESSION_ID
knowtether context --root .
```

`bind` 只更新工具绑定，不表示人的授权已续期。多个会话并行创作时使用各自的项目工作目录。停用当前工作单：

```bash
knowtether close --root .
```

## 检查一份成果

0.6.0的`inspect`可对[明确声明的项目资料](project-evidence.md)做配对计算，并核对汇报正文预算；`check`仍是原有记录与文本提示。两者都不作语义批准。

```bash
knowtether check --root . --artifact article.md
knowtether check --root . --artifact article.md --strict
```

不传 `--artifact` 时检查项目工作单。文本检查只提供可复核的提示：即使没有告警，也需要核对来源是否真实且支持主张，并让目标读者实际尝试预设任务。

| 方式 | 退出码 |
| --- | --- |
| 默认 `check` | 检查发现问题时仍返回 `0`，由人或上层流程审阅报告。 |
| `check --strict` | 发现 warning 或 error 时返回 `1`。 |
| CLI 无法完成检查 | 配置、输入或环境错误返回 `2`。 |
| 主机 Hook | 告警运行，返回 `0`，不发送阻断或批准决定。 |

`--strict` 便于在 CI 中发现已定义的机械问题；它不把语义质量判断变成自动发布许可。

对照 [较清楚的演示文本](../examples/good.md) 与 [有意保留问题的演示文本](../examples/problematic.md)，可以了解提醒的用途。这些都是设计示例，没有真实研究数据，也没有真实读者测试结果。[示例工作单](../examples/work.json) 故意保留开放问题和未人工核验记录，因此会出现 `OPEN_ISSUES`、`SOURCE_UNVERIFIED` 提醒；请勿为消除提示而虚填核验结果。

## 发布硬门

日常 Hook 和 `check` 只提醒。要对外发布时，明确运行发布硬门；任何一条不满足就返回 `1`，表示不能标为可发布：

```bash
knowtether release --root . --artifact final.md
```

未用 pip 安装时，用随插件分发的入口：`python3 -B <插件目录>/hooks/entry.py release --root . --artifact final.md`。

| 规则 | 拦下的情况 |
| --- | --- |
| `RELEASE_SOURCE` | 主张/来源行不是含非空ID的对象、ID重复或主张缺type；`fact`、`data`、`quote`、`cause` 类主张没有来源或 `support_note`；来源缺 `locator`，或 `verification` 不是 `human-verified`；没有事实类主张且 `publication.external_facts` 不是 `"none"` |
| `RELEASE_PLACEHOLDER` | 成品还有 `[citation needed]`、`TODO`、`TBD`、`[待补]`、`【待核实】` 等占位（代码块除外） |
| `RELEASE_RIGHTS` | 任一来源的 `rights_status` 为空、未知/待定、`pending`、`denied`、`prohibited` 或任何 `blocked-*` |
| `RELEASE_ACCEPTANCE` | 没有与 `artifact_version` 同版本、带 `evidence_ref` 的 `author_acceptance` 记录 |
| `RELEASE_WORKFLOW_LABEL` | 成品含「候选发布版」「内部草稿」「供某人审阅」、`DRAFT`、`WIP` 等工作流标签 |

| 结果 | 退出码 |
| --- | --- |
| 五条都满足 | `0`，`verdict` 为 `pass` |
| 任一条不满足 | `1`，`blocking` 给出问题；文本命中含行号，记录问题含ID或序号 |
| 路径越出项目、空白成品或输入错误 | `2` |

硬门检查记录和成品文本，不检查真假。它拦不住从未登记或错误分类的事实、填假的记录，或来源存在却不支持主张的情况；这些仍要人逐项核对。接受记录按版本字符串匹配，未绑定文件散列。谈论“DRAFT”等术语的正文也可能命中模式，应核对上下文，不能为通过删除真实限制。`human-verified`、`author_acceptance` 和 `external_facts: "none"` 只能由人确认后填写，Agent 不得为通过硬门而改写。Hook 从不运行硬门。

## 卸载

```bash
knowtether uninstall --root . --host codex --dry-run
knowtether uninstall --root . --host codex
```

Claude Code 使用 `--host claude`。卸载仅移除本项目安装的 handler，保留他人的 Hook 与配置。Python 包可另行使用 `python -m pip uninstall kpdm-hooks` 移除。
