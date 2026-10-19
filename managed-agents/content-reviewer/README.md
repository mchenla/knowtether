# 知识产品内容审核 Agent（Managed Agents 草案）

在 Claude Platform 的工作区里运行的托管 Agent。它读取成稿和 `.kpdm/work.json`，先运行知据发布硬门，再按 KPDM 规则逐条核对主张与来源、状态词和语言，把审核报告写到 `review.md`。

报告是 **AI 预审**：不改稿，不改记录，不批准发布，也不算人工复核或真实读者测试。

## 文件

| 文件 | 内容 |
| --- | --- |
| `agent.md` | Agent 配置（模型 Claude Opus 5.5，effort 为 high；工具集开启，网页工具关闭）与系统提示 |
| `environment.yaml` | 云端沙箱，`limited` 网络，不允许任何外部主机 |
| `rubric.md` | 评分器用的起始标准，评的是审核报告，不是成稿 |
| `run_review.py` | 发起一次审核会话：上传成稿、记录和来源，挂载知据仓库，设花费上限，下载报告 |

## 准备

1. Console 账户已开通 API 计费并有余额。
2. 安装 `ant` 1.30.0 以上，并用 `ant auth login` 登录。
3. 一个只读、只对 `mchenla/knowtether` 有权限的 GitHub fine-grained token，用于挂载仓库。
4. 发布硬门（PR #2）合并到 `main` 之后再运行；否则仓库里没有 `release` 命令。

## 创建 Agent 和环境（一次）

在本目录运行。先看计划，确认后再创建：

```bash
ant apply --dry-run -v agent.md environment.yaml
ant apply agent.md environment.yaml
```

ID 写进同目录的 `claude-lock.json`，要和这些文件一起提交。改了 `agent.md` 后再运行 `ant apply`，会生成新版本，而不是新 Agent。

## 发起一次审核

待审项目目录里需要有成稿、`.kpdm/work.json`，以及可选的 `sources/` 文件夹：

```bash
export AGENT_ID=$(jq -r '.resources["./agent.md"].id' claude-lock.json)
export ENV_ID=$(jq -r '.resources["./environment.yaml"].id' claude-lock.json)
export GITHUB_TOKEN=...   # 只读 token；不要写进文件
python run_review.py ~/projects/某篇文章 --artifact final.md --budget-cents 300
```

报告保存到项目目录下的 `review/review.md`。终端会打印 Console 链接，可以在网页上看实时过程。

## 设计取舍

- **网页工具关闭。** 成稿可能保密，也可能夹带给 Agent 的指令；不开外网就没有外传的通道。来源请放进 `sources/` 一起上传；没上传的来源，报告会标为「not opened」，不会判为支持。
- **不挂自定义技能。** 插件里的命令用了只有 Claude Code 才认的字段和变量，Skills API 会拒收；审核规则直接写在系统提示里，KPDM 原文从挂载的仓库读取。
- **用结果评分（outcome）启动。** 独立上下文的评分器按 `rubric.md` 检查报告，不达标就让 Agent 修改报告，最多 3 轮。
- **每次会话设花费上限**，默认 3 美元，到达上限会暂停而不是继续花钱。
- **工具调用由服务端自动判断。** 无法判断的调用，脚本一律拒绝，因为运行时无人值守。

## 尚未验证

这些文件只做了语法检查。没有在真实工作区创建过 Agent，也没有跑过会话，所以沙箱里是否预装 `python3`、`limited` 网络且不放行任何主机时仓库挂载是否正常、单次审核花费多少，都还不知道。第一次运行请设较低的上限，在 Console 里看过程。
