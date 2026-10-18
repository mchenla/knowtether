# Codex 插件：两条命令安装

## 准备

使用支持 `codex plugin marketplace add` 和 `codex plugin add` 的 Codex CLI，并将 Python 3.10+ 放在 Codex 非交互运行环境的 `PATH` 上。插件自带 Python 代码，无须先 `pip install`，无须启动服务器或配置账号令牌。Windows 支持 `python`、`python3` 或 `py -3`；macOS/Linux 支持 `python3` 或 `python`。

## 安装

```bash
codex plugin marketplace add mchenla/knowtether
codex plugin add knowtether@knowtether
```

第一条命令添加这个 GitHub 仓库中的市场清单，第二条安装 `knowtether` 市场中的同名插件。这是仓库市场分发，不代表进入官方公共插件目录。

运行 `codex`，进入 `/hooks` 审阅并信任三个 KnowTether Hooks，再开始新会话。桌面端请在安装后重启，以便载入插件。安装不自动授予 Hook 信任，不跳过宿主的确认步骤。若 CLI 不识别上述子命令，先更新到支持这些命令的版本。

## 使用

开始新的知识创作任务即可获得条件性提醒。请求开头使用 `[kpdm]` 可明确触发知识任务提醒；也可以调用插件中的 `knowtether` Skill，例如 `$knowtether:knowtether`，或直接要求按知据规范起草或审阅。

- `SessionStart`：提供仅适用于知识创作的简短规范；发现旧会话工作单时提示核对当前委托。
- `UserPromptSubmit`：对匹配的知识请求，先读取校验三份随包规范并提供原文选段和协作要求，见 [最小阅读](minimum-reading.md)。
- `Stop`：对最后一条消息和当前会话绑定的工作单提供告警；不阻断、不批准、不要求自动续跑。

短任务无须创建工作单或项目配置。复杂任务可在会话 `cwd` 对应的创作目录维护 `.kpdm/work.json`，字段见 [规则映射](rules.md)。插件只读取这个目录下的记录，不搜索父目录，不从完整会话推定授权。工作单记录不会写入插件缓存。

## 按项目停用

在项目 `.kpdm/config.json` 中写入：

```json
{"schema_version": 1, "enabled": false}
```

这会停用该目录的插件 Hooks。删除这个配置或改为 `enabled: true` 后，在新会话中恢复。`close` 只停用工作单检查，不等于停用插件的知识任务提醒。

## 兼容旧版安装

原有 `knowtether` / `kpdm-hooks` Python 命令和按项目安装方法仍然可用。在同一会话目录检测到旧版 `.codex/hooks.json` 注册的 KnowTether 事件时，插件让原入口处理该事件，避免重复提醒。

准备改用插件时，可在旧项目目录运行已安装的 CLI：`knowtether uninstall --root . --host codex`。它只移除本工具的项目注册，保留工作单和其他 Hooks。不要同时保留多个全局 KnowTether 注册；插件只检查当前目录中的旧版注册，不扫描个人全局配置。

## 更新与卸载

```bash
codex plugin marketplace upgrade knowtether
codex plugin add knowtether@knowtether
```

卸载插件：`codex plugin remove knowtether@knowtether`。不再需要市场源时运行 `codex plugin marketplace remove knowtether`。具体选项以已安装 CLI 的 `--help` 为准；卸载不会删除创作项目中的 `.kpdm` 工作记录。

## 包结构与检查边界

仓库使用 `.codex-plugin/plugin.json` 描述插件，以兼容已实测的 Codex 0.163 alpha。该版本遇到根 `plugin.json` 会漏载 Hook，因此暂不同时提供根清单，市场清单为 `.agents/plugins/marketplace.json`。Skill 位于 `skills/knowtether/`，Hooks 位于 `hooks/hooks.json`，代码直接从安装后的插件包导入。

POSIX 启动脚本为 `hooks/run-posix.sh`。Windows 入口使用显式 PowerShell 启动器，避免依赖 Codex 当前选用 cmd 还是 PowerShell；编码的命令只加载可审阅的 `hooks/run-windows.ps1`。Windows 的 `ExecutionPolicy Bypass` 仅作用于这个子进程，不修改持久策略，也不替代 Codex 的 Hook 信任。重新生成配置：`python scripts/build_plugin_hooks.py`；只校验：增加 `--check`。

安装流程、打包检查和事件 fixture 不证明事实可靠、读者理解、独立核验或真实知识质量改善。完整评估范围见 [验证记录](validation.md)。

参考：[OpenAI 插件打包与市场说明](https://developers.openai.com/plugins/build/plugins)、[Codex Hooks](https://learn.chatgpt.com/docs/hooks)。分发结构参考 [Ponytail](https://github.com/DietrichGebert/ponytail)；知据的规则、脚本和图标为本项目实现。

## 随包规范

从 0.3.0 起，插件同时包含 `framework/kpdm/` 的 CC BY 4.0 规范快照；代码与适配 Skill 继续为 MIT。Skill 按需链接到快速入门、模板和相关规范，普通短任务保持轻量。框架与软件版本分别管理，见 [KPDM](../framework/kpdm/README.md) 和 [许可范围](../LICENSING.md)。0.4.0 增加最小原文阅读包；三个入口命令与提示型 Stop 边界保留。
