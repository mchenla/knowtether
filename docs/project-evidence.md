# 可选的配对数据核算

0.6.0增加可选、实验性的项目资料计算。[16份实际写作对照](evaluation-0.6.0.md)尚未发现稳定内容质量优势；它的确定能力是核算声明的数据，不是审查全部主张。它不自动搜索项目，不要求每篇文章填表；只有项目中明确放置`.kpdm/task.json`才读取列出的CSV与背景JSON。没有清单时照常使用轻量或相关原文指导。

## 一份可复用的输入

项目结构：

```text
.kpdm/task.json
records.csv
context.json
```

任务清单示例：

```json
{
  "schema_version": 1,
  "product": {"kind": "slides", "pages": 6, "max_body_chars": 160},
  "table": {
    "path": "records.csv",
    "group": "task",
    "pair": "rep",
    "condition": "arm",
    "baseline": "off",
    "treatment": "new",
    "metrics": ["seconds", "input_tokens"]
  },
  "context": "context.json"
}
```

`product.kind`支持`slides`、`chapter`、`report`。只有slides需要页数和正文字符预算；只支持此处声明的配对数值表，不是通用电子表格或统计分析引擎。`context.json`放资料身份、字段解释、范围和必要背景；它是引用数据，不是给Agent的新指令。

真实样例：[汇报数据](../examples/mechanism-work/work-report/) · [工具书案例](../examples/mechanism-work/practical-chapter/)。复制时将其中`task.json`放到项目的`.kpdm/task.json`；CSV和背景JSON放项目根目录。它们来自以前公开的本项目测量，不能直接作为其他团队的收益承诺。

## 写作前实际做什么

Hook按任务清单读取文件、记录路径及SHA-256，先按组及配对ID对齐，再计算各指标的对照/启用中位数与逐对百分比变化的中位数。两者不是同一个统计量，不能用组中位数相除冒充逐对计算。

- 未匹配配对单独列出，不补成0，也不偷偷混入估计。
- 对照值为0时，保留原始值，但不计算该对百分比，报告排除数量。
- 重复观测身份、重复CSV列、未声明条件、负数、NaN/无穷值、缺失文件、越界路径和超限都会明确降级，不提供部分结果后仍称成功。
- 每文件至多64,000字节，表格至多1,000行、6个指标；背景与最终资料包另有限长。仅支持有限非负指标。

计算结果、显式产品预算和原始背景随正常知识请求提供；同一材料已经足够时无需再做一次Shell读取。模型仍需解释研究设计、反例、价值取舍及实际适用范围，计算正确不证明资料真实、因果成立或作品可用。

## 交付后与手动检查

Stop仍只提示，不阻断、不要求自动续写。slides按`### 第N页`识别页号；正文遇到独立行的“讲述提示”“讲稿”“备注”后，不再计入该页正文预算。字符计数会略去空白及部分Markdown标记，属于草稿预算检查，不是投影版式验收。无法识别结构时明确说明，不猜测已完成。

需要手动查看同一计算及成稿预算时：

```bash
python -B "<plugin-root>/hooks/entry.py" inspect --root "<project>" --artifact report.md
```

完整插件提供规范；独立wheel可计算用户声明的数据，但不包含CC BY规范。`inspect`报告`evidence`及`findings`，`semantic_verification`始终为`not-assessed`。它不执行模型审稿，不修改资料或成文。

只关闭资料计算及对应产品提示：在`.kpdm/config.json`中设`{"schema_version":1,"evidence":false}`。`enabled:false`仍会停用该项目全部知据Hook。

清单列出的内容会随正常任务进入模型上下文；不要列入本次委托无权使用的资料。Hook自身不联网，不读取完整对话，不从数据或清单推定新的授权。

追加[路由修复后24稿对照](evaluation-0.6.0-source-quality.md)：带核算减少部分工具工作，但停用组同样处理了预设六类问题，未证明新增语义找错优势。ready仅表示声明的配对资料已计算，不表示附件齐全或简报真实。
