---
type: quality-control
work_id: KPDM
status: draft-active
version: 0.4.0
created: 2026-08-11
updated: 2026-08-11
authority: quality-control
---

# 质量 SLO、置信向量与不确定性治理

## QualitySLO

QualityTarget 规定产品最终高度；QualitySLO 把高度转换为某个 WorkPacket 或 ReleaseCandidate 的可测试门槛。每个 SLO 包含维度、指标、阈值、检查方法、证据、责任人和红线。

示例：核心事实可追溯率 100%；高风险数据二次核验率 100%；术语冲突 0；关键任务读者测试成功率达到预设阈值。阈值必须在 Do 前冻结。

不以平均分掩盖红线。Truth、Rights 或安全红线失败时，ReleaseCandidate 直接失败。

## 置信向量

复杂知识产品不得只给一个貌似精确的总分。使用七维置信向量记录判断基础：

| 代码 | 维度 | 核心问题 |
|---|---|---|
| C | Claim | 主张是否清晰、有限定且无冲突 |
| E | Evidence | 证据是否直接、充分、时效适当 |
| A | Architecture | 对象、依赖和定义是否一致 |
| R | Rights | 权利、隐私与许可是否可发布 |
| U | Usefulness | 目标受众能否完成预期任务 |
| P | Process | 过程、版本和裁决是否可追踪 |
| X | External | 是否获得独立或现实验证 |

每维只使用 `low / medium / high / not-tested`，并链接依据。向量表达的是证据状态，不是事实概率。任一关键维 `not-tested` 时，不得声称总体高置信。

## UncertaintyItem

所有可能影响主张、架构、权利、数据、使用或发布的未知项必须对象化，字段包括：问题、类型、影响、概率区间、风险等级、负责人、解决方法、截止点、状态和处置。

状态：`open → investigating → resolved / accepted / invalidated`。

accepted 不是已解决，必须说明接受理由、残余风险和允许用途。高风险未知不得 accepted 后直接进入 Q3/Q4 发布。

## 不确定性燃尽

按风险加权，不按数量美化：高风险=8，中风险=3，低风险=1。

`Uncertainty Load = Σ(开放项 × 风险权重)`

每轮记录起始负荷、关闭负荷、新增负荷和期末负荷。新增合理未知可能使曲线上升，这通常说明 Check 有效，不应被视为进度倒退。

## 预测指标

- 周期区间：同 profile、同复杂度历史包的 P50–P80；
- 返工率：发生至少一次返工的关闭包比例；
- 缺陷逃逸率：发布后发现缺陷 / 发布前后全部缺陷；
- SLO 达成率：通过指标 / 应检查指标，红线另计；
- 不确定性清除率：本轮关闭负荷 /（期初负荷 + 新增负荷）。

没有足够历史样本时，明确标注“不可校准”，不得制造确定日期或成功概率。
