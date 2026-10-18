# Claude Code 插件

## 准备

使用 Claude Code 2.1.275 或更新版本，并将 Python 3.10+ 放在 `PATH` 上。插件自带 Python 代码，无须 `pip install`，不需要账号令牌或 API key。Windows 上 Claude Code 通过 Git Bash 运行 Hook 命令。

## 安装

在 Claude Code 会话中：

```
/plugin install knowtether --marketplace mchenla/knowtether
```

或在终端里分两步：

```bash
claude plugin marketplace add mchenla/knowtether
claude plugin install knowtether@knowtether
```

这是仓库市场分发，不代表进入 Anthropic 官方目录。安装后开始新会话。想先试用而不安装，可在克隆的仓库目录外运行 `claude --plugin-dir <仓库路径>`。

## 自动提醒

与 Codex 插件共用同一组 Hook 和规则，见 [Codex 插件说明](codex-plugin.md)「使用」一节：`SessionStart` 给知识创作的简短规范，`UserPromptSubmit` 按任务复杂度提供轻量摘要或 KPDM 原文选段，`Stop` 给不阻断的告警。照常用自然语言提任务即可。

Claude Code 只设置 `CLAUDE_PLUGIN_ROOT`，不设置 Codex 的 `PLUGIN_ROOT`；Hook 命令按 `${PLUGIN_ROOT:-$CLAUDE_PLUGIN_ROOT}` 取插件目录，两个宿主共用 `hooks/hooks.json`。

## 命令

下列命令只在 Claude Code 中提供，放在 `claude/skills/`，Codex 不加载：

| 命令 | 做什么 |
| --- | --- |
| `/knowtether:start <一句话任务>` | 六个问题、成果类型与 Q 目标，在项目里写 `knowtether/worksheet.md`，含明确的委托范围 |
| `/knowtether:research <主题>` | 可随时转向与叫停的研究循环：多角度提问、每份材料七列记录（含定位与核对状态）、可编辑的知识概览 |
| `/knowtether:draft [章节]` | 在委托范围内起草或修订；候选保持候选；遇新核心主张、原意改变、范围扩大或未授权风险即返回人 |
| `/knowtether:check <文件>` | 由独立上下文的 `verifier` Agent 做六维检查、主张与证据匹配、状态词和模型语言检查；结论为 pass / conditional-pass / fail |
| `/knowtether:release <文件>` | 发布门：七条红线、权利、数据、隐私、编辑、成品表达隔离 |
| `/knowtether:handoff write\|read` | 交接记录；接手时不继承旧会话授权，上游变化的部分标为需重查 |
| `/knowtether:adopt <路径>` | 把已有草稿对照工作单八项，标「已有 / 缺失 / 需重构」，只为缺口生成修订任务 |
| `/knowtether:knowtether` | 与 Codex 共用的完整 KPDM 工作流 Skill |

Agent：`knowtether:verifier`（独立检查）、`knowtether:researcher`（研究循环）、`knowtether:reader-sim`（模拟读者，输出自标「模拟」，不得填入真实读者结果）。

命令写入的记录在项目的 `knowtether/` 目录：`worksheet.md`、`knowledge-overview.md`、`handoff.md`。它们与 Hook 读取的 `.kpdm/work.json` 是两种记录形式，互不替代；Hook 的工作单检查只读 `.kpdm/work.json`。

`claude/scripts/fingerprint_check.py` 列出长破折号、套语、「不是……而是……」句式、元话语和状态词所在行；`claude/scripts/worksheet_lint.py` 检查工作单八项。两者只报告候选位置，不判定质量。

## 按项目停用与兼容

停用方法与 Codex 相同：在项目 `.kpdm/config.json` 写入 `{"schema_version": 1, "enabled": false}`。

已用 `knowtether install --host claude` 在项目 `.claude/settings.local.json` 注册过 KnowTether Hook 的目录，插件让原入口处理同一事件，避免重复提醒。

## 限度

命令与 Agent 是操作指导，不能保证来源内容正确、权利已经清楚或读者能完成任务；这些仍由人核对与决定。模板改编自 KPDM 模板，沿用 CC BY 4.0，见 [claude/templates/README.md](../claude/templates/README.md)。Windows 上的 Claude Code 插件 Hook 尚未实际运行验证。
