# Conclusion — PPT Agent Optimization

> Executive summary for plan phase handoff.
> Date: 2026-03-23 (revised: corrected Gemini role framing)

---

## Problem Statement

PPT Agent 的 7 阶段工作流和 4-agent 架构在结构上是健全的，但 production run（小米 SU7，12 张幻灯片）揭示了核心设计意图与实际执行之间的断层：**审美优化层完全失效**。

Gemini 在架构中的角色是**视觉审美优化师**——不是打分员，不是合规检查员，而是主动提出具体的布局改进和视觉增强建议，让 Claude 生成的幻灯片从"正确"变为"出色"。这是 dual-model 架构的核心价值：Claude 擅长内容结构和代码生成，Gemini 提供独立的审美视角和创意改进。

当前的问题：
1. **Gemini 不可用时，审美优化完全消失** — Claude self-review fallback 不是在做审美优化，而是在给自己打高分（12 张幻灯片全部 8.2-8.8，Notes 完全相同）。Claude 审自己的 SVG 天然缺乏独立审美视角，这不是提示词能解决的根本问题。
2. **预审技术检查无法执行** — review-core 缺少 Bash 工具，5 项自动化检查（xmllint、viewBox、字号、色彩合规、安全区域）全是死代码。
3. **优化建议从未流入 fix loop** — 即使 Gemini 可用，其优化建议的传递路径（structured fix JSON → slide-core patch）偏向属性微调，无法承载结构性的布局重组建议。
4. **资源预算失衡** — content-core 在大型 deck 上截断，slide-core 过度分配。

这些问题层层叠加：没有真正的审美优化 → fix loop 从不触发 → fix 策略形同虚设 → Phase 6 退化为单轮生成器。

---

## Top 5 Actionable Recommendations

### R1: 给 review-core 添加 Bash 工具 (Effort: S)

**What**: 在 review-core 的 frontmatter tools 数组中添加 `Bash`。
**Why**: 预审自动化检查（xmllint、viewBox、font-size、color compliance、safe area）全部需要 Bash 但当前无法执行。每张 SVG 都跳过技术预检直接进入昂贵的 LLM 审查。
**Risk**: 极低 — 单行修改。
**Files**: `agents/review-core.md`

### R2: 重建审美优化层 (Effort: L)

**What**: 三部分改造（a 和 c 是原子单元，必须同步交付）：
- **(a) 明确 Gemini 优化师角色**：重写 review-core 和 reviewer.md 的提示词，强调 Gemini 的任务是"主动提出让幻灯片视觉效果更出色的具体改进建议"，而不是"检查合规并打分"。输出格式应以优化建议为主体，分数只是附带判断。同步修正 `skills/gemini-cli/SKILL.md` 中的 `## Review Criteria` 为 `## Optimization Criteria`，以及 line 81 "optimization must still happen" 改为 "technical validation only"，消除源文件内部矛盾。
- **(b) 重新定义 self-review fallback 的边界**：承认 Claude 自审无法替代跨模型审美优化。Fallback 时只执行可编程的技术验证（hard constraints：字号、间距、色彩对比度、安全区域、XML 有效性、文本溢出估算、outline 内容覆盖检查），不伪装成审美优化。明确标记为 "technical validation only — aesthetic optimization skipped"。
- **(c) 丰富优化建议的传递格式**（与 a 同步交付）：除了当前的属性级 fix JSON，增加 `layout_suggestion` 字段用于承载结构性建议（"将 3 列改为 hero+grid"、"合并卡片 2 和 3"、"增加呼吸空间"）。建议类型分类法扩展为 5 类：`attribute_change`（属性微调）、`layout_restructure`（布局重组）、`full_rethink`（完全重新设计）、`content_reduction`（降低信息密度）、`deck_coordination`（跨幻灯片协调，来自整体评审）。slide-core 根据建议类型决定执行策略。

**Why**: 当前 self-review 是橡皮图章，根本原因不是提示词不够强，而是 Claude 审自己的 SVG 缺乏独立审美视角。加强提示词只会让 Claude 更详细地描述"为什么自己做得好"，而不是真正发现改进空间。正确的做法是：Gemini 可用时做真正的审美优化，不可用时诚实地只做技术检查、跳过审美优化。
**Risk**: 高 — 改变 Phase 6 的核心行为模型。Wave 2 完成后需要一次校准生产运行（8-10 页 deck）验证 Gemini 建议质量和分类法有效性，再进入 Wave 3。
**Files**: `agents/review-core.md`, `skills/gemini-cli/references/roles/reviewer.md`, `skills/gemini-cli/SKILL.md`（line 81 + prompt template），`commands/ppt.md`

### R3: 修复资源预算失衡 (Effort: S)

**What**: content-core maxTurns 25→35，slide-core maxTurns 30→20，review-core maxTurns 15→20。将 draft_slide_ready 信号从逐页改为每 3 页批量发送。
**Why**: content-core 在 12+ 页 deck 上截断（15 页需要 36 轮）。slide-core 为单张幻灯片分配了 30 轮但只需要 12-15 轮。review-core 整体评审模式需要读取所有 SVG，15 轮太紧。
**Risk**: 极低 — 数值调整。
**Files**: `agents/content-core.md`, `agents/slide-core.md`, `agents/review-core.md`, `commands/ppt.md`

### R4: 加固恢复逻辑 (Effort: S)

**What**: (a) 在 outline.json 中添加 `approved: true` 字段，仅在用户确认后设置。恢复时检查该字段。(b) slide-status.json 使用原子写入模式（先写 .tmp，验证，再 rename）。
**Why**: 当前恢复逻辑可能跳过 Phase 4 的 Hard Stop（大纲未获批准就进入生产），且崩溃时可能损坏所有已完成的进度。
**Risk**: 极低 — 向后兼容（缺失 approved 字段视为 false）。
**Files**: `commands/ppt.md`, `skills/_shared/references/prompts/outline-architect.md`

### R5: 补充 chart_colors 令牌 + 优化建议驱动的 fix 策略 (Effort: M)

**What**: (a) 在 4 个 style YAML 中添加 `chart_colors`（有序 6-8 色 hex 数组），更新 svg-generator.md 的图表模式。(b) 基于校准运行数据，将 fix loop 从"分数驱动"改为"优化建议驱动"：Gemini 提出具体建议 → 每条建议自带类型（attribute_change / layout_restructure / full_rethink / content_reduction / deck_coordination）→ slide-core 根据建议类型选择执行策略。无 Gemini 时只做技术修复。
**Why**: 单色图表阻塞多系列数据可视化。当前 fix loop 基于分数阈值机械地选择 patch/regenerate，但正确的决策因素应该是"优化建议需要什么级别的改动"。
**前提**: R2 的校准运行完成，建议分类法经过验证。
**Risk**: chart_colors 低风险。fix 策略改动中风险 — 改变 Phase 6 行为模型，但有校准数据支撑。
**Files**: 4 个 style YAML, `svg-generator.md`, `commands/ppt.md`, `agents/slide-core.md`

---

## Recommended Implementation Sequence

### Wave 1 — 解锁基础能力（不改行为模型）
1. **R1**: review-core 添加 Bash（R2 的前提）
2. **R3**: 修复 maxTurns（content-core 25→35, slide-core 30→20, review-core 15→20）
3. **R4a**: outline.json 添加 approved 字段 + 恢复检查

### Wave 2 — 重建审美优化层（R2a + R2c 是原子单元）
4. **R2a+c**: 重写 Gemini 优化师角色提示词 + 同步定义优化建议传递格式（5 类建议分类法 + layout_suggestion 字段）。修正 SKILL.md 内部矛盾（line 81, prompt template）。
5. **R2b**: 重新定义 self-review fallback 为 "technical validation only"（含文本溢出估算 + outline 内容覆盖检查）
6. **R5a**: 添加 chart_colors 令牌

### 校准门控 — Wave 2 完成后必须执行一次生产运行（8-10 页 deck）
验证：Gemini 是否产出有价值的审美优化建议、建议分类法是否覆盖实际产出、技术检查阈值是否合理。根据校准结果调整 Wave 3 方案。

### Wave 3 — fix 策略 + 状态加固
7. **R5b**: 优化建议驱动的 fix 策略（基于校准数据）
8. **R4b**: slide-status.json 原子写入
9. Style token guided-freedom enforcement model
10. Holistic deck 审美一致性评审设计（Gemini 整体评审协议 — 跨幻灯片视觉节奏、色彩叙事、节奏感，这是 Gemini 最不可替代的贡献）

### Wave 4 — 视觉丰富度 + 管线优化
11. Missing SVG patterns (table, metric grid, grouped bar)
12. Holistic 审美评审实施 + deck_coordination 建议类型落地
13. Sonnet for attribute-level optimization patches
14. Heartbeat reduction, memory scope optimization, adaptive window

---

## Risk Assessment

| Recommendation | Implementation Risk | Regression Risk | Rollback Ease |
|---------------|-------------------|-----------------|---------------|
| R1 (Bash tool) | Very Low | None | Trivial (remove one word) |
| R2 (审美优化层重建) | High — 改变 Phase 6 核心行为 | Gemini 不可用时审美优化消失（但这是诚实的 tradeoff，好于假装有审美优化） | Medium（恢复旧提示词） |
| R3 (maxTurns) | Very Low | None | Trivial |
| R4 (Resume) | Low | 可能对 stale outline 要求重新审批 | Easy |
| R5 (chart_colors + fix 策略) | Medium | fix 策略改动影响 Phase 6 | Medium |

---

## What NOT to Change

以下架构决策经证据验证为正确选择：

1. **4-agent 架构** (research / content / slide / review) — 评估了 4 种拆分方案均被否决
2. **星形通信拓扑** — agents 只与 orchestrator 通信
3. **基于文件的状态机** — artifact 存在性作为持久真相层
4. **模型分配**: research-core (sonnet) / content-core (opus) — 正确匹配任务复杂度
5. **优雅降级模式** — agent-reach 和 gemini-cli 的降级策略一致且执行良好
6. **Gemini 作为独立审美视角的 dual-model 架构** — 核心设计意图正确，问题在于 fallback 路径伪装成了它不是的东西
7. **Style registry (index.json)** — 发现驱动的扩展性设计
8. **Phase 5→6 pipeline overlap** — 架构上正确，简化信号批量即可
