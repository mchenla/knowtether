# KPDM + 知据 KnowTether

[English](README.en.md)

让 Agent 在撰写文章、报告、研究概览等知识成果时，记得说明读者与用途，区分事实、推断和建议，保留来源、适用范围、未知项与人的决定。

**知据（KnowTether）** 是一个 Python 标准库实现的本地 Hook 适配器，支持 Codex 和 Claude Code。名字取“知识有据”之意：让知识输出连接回资料、推理和人的判断。它把 KPDM 的部分要求转成会话提示、工作单检查和文本告警。默认告警模式不阻断 Agent，也不替人批准主张或发布。

当前软件版本：`0.3.0`。适配参考为 **KPDM 0.5.0-rc.2 candidate**，最近接受基线仍为 **0.4.0 trial / conditional-pass**。本项目的安装、测试或发布不会提升 KPDM 框架状态。

## 方法规范与 Agent 实现

本仓库同时开源两部分：[KPDM 规范、模板与机器模型](framework/kpdm/README.md)采用 **CC BY 4.0**；KnowTether 的代码、Hook、Skill 与适配说明采用 **MIT**。完整许可范围见 [LICENSING.md](LICENSING.md)。

KPDM 规定知识产品如何形成、表达与核验；知据把其中部分要求带入 Agent 工作流。既可以只使用规范，也可以安装插件。插件 ZIP 和市场安装已包含规范，无须访问作者的 Obsidian 库；Python wheel 保持软件部分轻量分发。

## Codex：两条命令安装

准备支持插件命令的 Codex CLI，并将 Python 3.10+ 放在非交互环境的 `PATH` 上，然后运行：

```bash
codex plugin marketplace add mchenla/knowtether
codex plugin add knowtether@knowtether
```

之后运行 Codex，进入 `/hooks` 审阅并信任三个 KnowTether Hooks，再开始新会话。桌面端安装后重启以载入插件。插件自带代码，无须另行 `pip install`，也无须先创建工作单或配置文件。

这是与 Ponytail 相同的 GitHub 仓库市场分发方式。完整使用、按项目停用、升级和旧版兼容见 [Codex 插件说明](docs/codex-plugin.md)。

## 公开下载

仓库和安装包公开可访问，下载不需要 GitHub 账户。

- [下载独立 Codex 插件 ZIP（v0.3.0）](https://github.com/mchenla/knowtether/releases/download/v0.3.0/knowtether-0.3.0-plugin.zip)
- [下载独立 KPDM 规范包](https://github.com/mchenla/knowtether/releases/download/v0.3.0/kpdm-0.5.0-rc.2-public-snapshot.zip)
- [下载 Python 安装包（v0.3.0）](https://github.com/mchenla/knowtether/releases/download/v0.3.0/kpdm_hooks-0.3.0-py3-none-any.whl)
- [下载源代码 ZIP（v0.3.0）](https://github.com/mchenla/knowtether/releases/download/v0.3.0/knowtether-0.3.0-source.zip)
- [下载 SHA-256 校验文件](https://github.com/mchenla/knowtether/releases/download/v0.3.0/SHA256SUMS)
- [查看版本说明及所有下载项](https://github.com/mchenla/knowtether/releases/latest)

有 Python 3.10 或更新版本时，可以直接安装公开下载地址：

```bash
python -m pip install "https://github.com/mchenla/knowtether/releases/download/v0.3.0/kpdm_hooks-0.3.0-py3-none-any.whl"
knowtether --version
```

主命令为 `knowtether`。为兼容早期版本，Python 发行包仍为 `kpdm-hooks`，旧命令 `kpdm-hooks`、模块 `kpdm_hooks` 和已有 Hook 配置继续可用。升级可在上面的安装命令中增加 `--upgrade`。

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

同时核对 `input_version`、`artifact_version`、`allowed_write_roots` 和 `open_issues`。可选 `claims` 与 `sources` 用于记录主张和来源关系，参见 [示例工作单](examples/work.json) 和 [规则映射](docs/rules.md)。

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

对照 [较清楚的演示文本](examples/good.md) 与 [有意保留问题的演示文本](examples/problematic.md)，可以了解提醒的用途。这些都是设计示例，没有真实研究数据，也没有真实读者测试结果。[示例工作单](examples/work.json) 故意保留开放问题和未人工核验记录，因此会出现 `OPEN_ISSUES`、`SOURCE_UNVERIFIED` 提醒；请勿为消除提示而虚填核验结果。

## 卸载

```bash
knowtether uninstall --root . --host codex --dry-run
knowtether uninstall --root . --host codex
```

Claude Code 使用 `--host claude`。卸载仅移除本项目安装的 handler，保留他人的 Hook 与配置。Python 包可另行使用 `python -m pip uninstall kpdm-hooks` 移除。

## 能力范围

Core-6 表示目的、知识内核、依据、可用化、表达、验证与演进六种功能；文章可以自然组织，无须照搬六个标题或固定步骤。研究概览也可以是交付物，不强迫先编造中心主张。

自动检查能提示记录缺失、明显状态表述和部分文本信号；无法判断事实真假、引用是否支持主张、版权是否允许使用、文字是否被真实读者理解。公开知识成果按原规范至少采用 Q3，另行完成独立事实与引用检查、独立编辑或真实目标读者任务，以及人的发布决定。

当前验证包含自动测试、真实 Codex CLI 的隔离安装、宿主发现检查、信任界面和三个 Hook 的真实生命周期执行。一次不带显式标签的知识写作任务也触发了三 Hook 并产出有来源和限制的草稿；没有对照组或真实读者验证，尚未证明知识质量提升。机械检查不代表内容真实或通过 KPDM 验收，见 [验证记录](docs/validation.md)。

详见 [规则与人工责任](docs/rules.md)、[设计与优化方向](docs/design.md)、[安全说明](SECURITY.md)。欢迎按 [贡献说明](CONTRIBUTING.md) 报告误报、漏报与主机兼容问题。

## 许可与来源

KnowTether 原创代码和适配说明采用 [MIT](LICENSE)；`framework/kpdm/` 中的 KPDM 原创规范、模板、机器模型与公开快照采用 [CC BY 4.0](framework/kpdm/LICENSE)。版权声明为 `2026 MC (mchenla)`。外部作品仍按其各自条件使用；范围与署名见 [LICENSING.md](LICENSING.md) 和 [NOTICE](NOTICE)。
