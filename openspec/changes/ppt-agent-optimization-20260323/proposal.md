# Change: PPT Agent Optimization

> Revised: corrected Gemini role framing — aesthetic optimizer, not quality scorer

## Why

Production run 分析（小米 SU7，12 张幻灯片）揭示了核心设计意图与实际执行之间的断层：

**根本问题：审美优化层完全失效。**

Gemini 在架构中的角色是**视觉审美优化师**——主动提出具体的布局改进和视觉增强建议，让 Claude 生成的幻灯片从"正确"变为"出色"。这是 dual-model 架构的核心价值。当前：

1. **Gemini 不可用时，审美优化消失而非降级**: Claude self-review fallback 不是在做审美优化，而是在给自己打高分（12 张幻灯片全部 8.2-8.8，Notes 完全相同）。Claude 审自己的 SVG 天然缺乏独立审美视角——这不是提示词能解决的根本问题。
2. **预审技术检查是死代码**: review-core 缺少 Bash 工具，5 项自动化检查无法执行。
3. **优化建议的传递管道过窄**: fix JSON 只支持属性级微调，无法承载 Gemini 最有价值的结构性布局建议。
4. **资源预算失衡**: content-core 在大型 deck 上截断，slide-core 过度分配。
5. **恢复逻辑有安全漏洞**: 可能跳过大纲审批，且崩溃时丢失进度。
6. **单色图表渲染**: 所有数据可视化只用一个 accent 色，阻塞多系列图表。

## What Changes

**Wave 1（立即修复 — 解锁基础能力）:**
- review-core 添加 Bash 工具
- 修复 maxTurns: content-core 25→35, slide-core 30→20, review-core 15→20
- outline.json 添加 `approved` 字段保障恢复安全
- draft 信号批量化（每 3 页）

**Wave 2（重建审美优化层）:**
- 重写 Gemini 角色提示词：从"检查合规打分"改为"主动提出视觉优化建议"
- 重定义 self-review fallback 为 "technical validation only"——诚实承认无法替代跨模型审美优化
- 添加 chart_colors 令牌到所有 style YAML
- slide-status.json 原子写入

**Wave 3（优化传递机制）:**
- 丰富优化建议格式：增加 layout_suggestion 字段承载结构性建议
- 建议驱动的 fix 策略（替代分数驱动）：由优化建议类型决定 patch / restructure / regenerate
- Style token guided-freedom enforcement model

**Wave 4（视觉丰富度 + 管线优化）:**
- 补充缺失的 SVG 模式（table, metric grid, grouped bar）
- Gemini 整体审美一致性评审（cross-slide visual rhythm, color story）
- Sonnet for attribute-level optimization patches
- Heartbeat reduction, memory scope optimization, adaptive window

## Impact

- **Scope**: 10-12 files across agents, commands, skills, and style definitions
- **Risk Level**: Low for Wave 1 (config), High for Wave 2 (changes Phase 6 core behavior model), Medium for Wave 3 (new suggestion format), Low for Wave 4 (optimizations)
- **Architecture**: 不改变 4-agent 架构和星形拓扑。核心改变是 Gemini 的角色定位从 "scorer" 回归 "optimizer"，以及 self-review fallback 从"伪装审美优化"降级为"诚实的技术验证"
- **Key Tradeoff**: Gemini 不可用时，幻灯片只有技术验证没有审美优化。这是诚实的 tradeoff——好于当前的虚假信心
- **Backward Compatibility**: 所有改动向后兼容现有 run 目录
- **Not Changed**: 4-agent 架构, 星形拓扑, 文件状态机, 模型分配, 优雅降级模式, style registry, Phase 5→6 pipeline overlap
