# Audit Report — Design/UX Perspective

> Auditor: gemini-perspective
> Date: 2026-03-23
> Scope: Updated TPD Thinking artifacts after Gemini role framing correction

---

## 1. R2 Feasibility: Three-Part Optimization Layer Rebuild

**Assessment: Decomposition is sound, but part (a) has an internal contradiction that must be resolved.**

**(a) Rewrite Gemini role prompts** — 当前 `reviewer.md` 已经部分正确：第 3 行写着 "actively improve the visual quality"、第 16 行 "Think like a designer, not an auditor"。但 SKILL.md 的 prompt template（第 108 行）仍然使用 `## Review Criteria` 标题和 compliance-checking 语言（"Layout Balance: card arrangement, visual weight distribution, whitespace usage"），输出格式要求 `overall_score` + `pass: true/false`。这种格式框架本质上仍然是审计员模式。

**具体矛盾点**：reviewer.md 的 "Optimization Methodology" 第 1 步说 "what's the first thing that feels off?"（优化师思维），但紧接着第 2 步是 "Evaluate each criterion independently with a 1-10 score"（审计员思维）。真正的审美优化师应该先提出改进建议，分数只是对当前状态的快照，不是主要输出。

**Missing piece**: 没有定义优化建议的具体输出结构。当前 Fix Suggestion Format（reviewer.md 第 106-138 行）只有 `element/selector_hint/attribute/current/target` — 这是纯属性级 patch 格式，无法承载 "将三列改为 hero+grid" 类的结构性建议。R2(c) 提到了 `layout_suggestion` 字段，但在 R2(a) 的提示词重写中没有体现这个新格式应该如何融入 Gemini 的输出要求。

**(b) Self-review fallback 重定义** — 逻辑清晰。但 SKILL.md 第 81 行当前写着 "optimization must still happen, just without the cross-model perspective"，这与 R2(b) 的 "technical validation only" 直接矛盾。这行文字必须在 R2(b) 实施时显式修改。

**(c) 丰富优化建议格式** — 方向正确，但需要更具体的 schema 定义。`layout_suggestion` 作为一个字段太模糊。需要区分：对现有布局的结构性调整（"card-2 和 card-3 合并为一个 hero card"）vs. 整体布局切换建议（"从 three_column 改为 hero_grid"）。前者 slide-core 可以尝试 patch，后者必须 regenerate。

**Verdict**: 分解方向正确，但 (a)→(c) 之间的衔接缺失——提示词重写必须同时引入新的建议输出格式，否则 Gemini 还是会被旧格式框住。

---

## 2. Suggestion-Driven Fix Strategy: Taxonomy Sufficiency

**Assessment: 三类分类（attribute_change / layout_restructure / full_rethink）覆盖了主要场景，但有两个重要遗漏。**

**缺失类型 1: content_reduction** — handoff.json 的 UD-3 已经提到了这个类型但未纳入正式分类。当信息密度过高时，优化建议可能是"删除 bullet 4 和 5，保留前 3 条"或"将 6 个 metric card 精简为 4 个"。这不是布局变更，而是内容层面的减法。slide-core 需要回溯 outline.json 来决定哪些内容可以舍弃，与纯 SVG 层面的 patch/regenerate 是不同的执行路径。

**缺失类型 2: cross-slide coordination** — 当 Gemini 做 holistic review 时，可能提出 "slide-03 和 slide-07 都用了 hero_grid 布局，建议 slide-07 改为 dashboard_mosaic 增加视觉节奏"。这种建议跨越单张幻灯片的边界，当前的 per-slide fix loop 无法处理。需要一个 `deck_coordination` 建议类型，由 orchestrator 路由到对应的 slide-core。

**不需要的类型**: animation hints（SVG 是静态的，不涉及动画）。

**Verdict**: 建议将分类扩展为 5 类：`attribute_change` / `layout_restructure` / `content_reduction` / `full_rethink` / `deck_coordination`。前 4 类用于 per-slide review，第 5 类专用于 holistic review。

---

## 3. Technical Validation Fallback Coverage

**Assessment: 当前 5 项检查覆盖了基础结构完整性，但遗漏了几个高频实际问题。**

当前清单：
1. xmllint — XML 有效性 ✓
2. viewBox — 视口声明 ✓
3. font-size — 字号下限 ✓
4. color compliance — 色彩令牌合规 ✓
5. safe area — 安全区域 ✓

**遗漏项（按影响排序）**：

1. **文本溢出检测（Critical）** — reviewer.md 第 31 行将 text overflow 列为 Critical severity，但技术预检中没有。一个 `<text>` 元素的字符数 × 估算字宽如果超过其父 `<g>` 或 `<rect>` 的宽度，应该被标记。这是可编程检测的（CJK 字符宽度 × 1.8 / Latin × 0.6，与容器宽度比较），虽然不完美但能捕获明显溢出。

2. **outline.json 内容覆盖检查（Major）** — 技术验证应该检查 outline.json 中该页定义的 `key_points` 是否在 SVG 的 `<text>` 元素中出现（模糊匹配即可）。如果大纲要求 3 个要点但 SVG 只渲染了 1 个，这是内容丢失，不是审美问题。

3. **卡片重叠检测（Major）** — 解析 `<g transform="translate(x,y)">` 和内部 `<rect width height>`，检查任意两个卡片的 bounding box 是否重叠。这是纯几何计算，不需要 LLM。

**不需要的项**: card overlap 在实际 Bento Grid 生成中几乎不会发生（因为 svg-generator 的坐标系是确定性的），所以优先级低于前两项。

**Verdict**: 至少添加文本溢出估算和内容覆盖检查。这两项在 Gemini 不可用时是最有价值的自动化质量兜底。

---

## 4. Gemini Prompt Inconsistency

**Assessment: 存在显著的语言不一致，updated artifacts 没有充分识别这个问题。**

**具体矛盾清单**：

| 文件 | 行 | 语言 | 角色定位 |
|------|-----|------|----------|
| reviewer.md 第 1 行 | "Aesthetic Optimizer" | 优化师 ✓ |
| reviewer.md 第 16 行 | "Think like a designer, not an auditor" | 优化师 ✓ |
| SKILL.md 第 30 行 | "optimize layout and improve visual aesthetics" | 优化师 ✓ |
| SKILL.md 第 108 行 | `## Review Criteria` | **审计员** ✗ |
| SKILL.md 第 116-122 行 | "Structured review with: overall_score, pass: true/false, per-criterion scores" | **审计员** ✗ |
| SKILL.md 第 131-133 行 | Fallback Strategy: "Apply the same structured optimization process: 5 criteria, numeric scores, pass/fail gate" | **混合** — 用了 "optimization" 但紧接着强调 scores 和 gates |
| review-core.md 第 22 行 | "Gemini's role is to propose concrete visual improvements (not just check compliance)" | 优化师 ✓ |
| review-core.md 第 64-71 行 | Output sections: Score, Pass/Fail, per-criterion scores, Issues, Fix Suggestions | **审计员框架 + 优化师内容** |
| commands/ppt.md 第 182 行 | "Checks layout balance, color harmony, typography, readability, information density" | **审计员** ✗（"Checks" 而非 "Optimizes"） |

**核心问题**：updated artifacts（conclusion.md、synthesis.md）正确诊断了 "Gemini 是优化师不是打分员"，但没有产出一份需要修改的语言清单。R2(a) 只说 "重写提示词"，没有指出具体哪些措辞需要改、改成什么。上面这份矛盾清单应该是 R2(a) 的一部分。

**Verdict**: 需要在 R2(a) 中增加一份"术语统一清单"（terminology alignment checklist），列出所有需要从审计员语言改为优化师语言的具体位置。

---

## 5. Holistic Review Priority

**Assessment: 将 holistic review 放在 Wave 4 是一个值得质疑的决策。**

**论点**：Cross-slide aesthetic coherence（视觉节奏、色彩故事、排版一致性）恰恰是 Gemini 作为独立审美视角最不可替代的贡献。Per-slide 审美优化 Claude 还勉强能做一些（虽然不如 Gemini），但 cross-slide 的全局审美判断是 Claude 完全无法自行完成的——因为 orchestrator 不持有所有 SVG 的视觉感知，只有元数据。

**当前 Wave 安排的逻辑**：先修好 per-slide 优化（Wave 2-3），再做 holistic（Wave 4）。这个顺序表面上合理（先修单页再修全局），但忽略了一个事实：**如果 holistic review 的反馈需要改变个别幻灯片的布局类型（比如 "slide-07 应该从 dashboard 改为 quote 作为呼吸页"），这个建议只有在 per-slide fix loop 还能执行的时候才有价值。** 如果 holistic 在所有幻灯片都已 finalized 之后才运行，它的建议就只能是 advisory warnings，无法落地。

**建议**：将 holistic review 的**设计和协议定义**提前到 Wave 3（与 suggestion format 一起定义 `deck_coordination` 建议类型），将实际的 mid-flight checkpoint 实现放在 Wave 3 或早 Wave 4。这样 Wave 2 的 per-slide 优化层可以先跑起来，Wave 3 同时增加 cross-slide 的协调能力。

**Verdict**: 设计层面应前移到 Wave 3，实现可以留在 Wave 4 早期。当前安排低估了 holistic review 的独特价值。

---

## 6. Wave Ordering: Wave 2 vs Wave 3 Dependency

**Assessment: 存在循环依赖问题，当前排序需要调整。**

**问题描述**：
- Wave 2 = 重建审美优化层（R2a: 重写 Gemini 提示词，R2b: self-review fallback）
- Wave 3 = 优化传递机制（R2c: layout_suggestion 格式，R5b: 建议驱动 fix 策略）

**矛盾**：如果 Wave 2 重写了 Gemini 提示词要求 Gemini "主动提出结构性布局建议"，但 Wave 3 的 `layout_suggestion` 格式还没定义，那 Gemini 的结构性建议将没有标准化的传递通道。Gemini 会输出自由文本的布局建议，slide-core 无法解析和执行。Wave 2 的优化层在 Wave 3 完成前只能产出属性级建议——这和改造前几乎没有区别。

**建议调整**：

**Wave 2 应该同时包含**：
- R2a: 重写 Gemini 提示词（含新输出格式规范）
- R2c: 定义 layout_suggestion 格式 schema（这是 R2a 的必要组件，不是独立的后续步骤）
- R2b: self-review fallback 重定义

**Wave 3 缩减为**：
- R5b: 建议驱动的 fix 策略（slide-core 侧的消费逻辑）
- U-07: Style token guided-freedom enforcement

这样 Wave 2 在产出端（Gemini）和格式端（schema）同步就位，Wave 3 在消费端（slide-core fix loop）落地。

**Verdict**: 当前排序有 producer/consumer 错配。R2c 应从 Wave 3 前移到 Wave 2，与 R2a 作为一个原子单元实施。

---

## 7. Missing Recommendation: Calibration Production Run

**Assessment: 强烈建议在 Wave 2 完成后增加一次校准生产跑。**

**理由**：
1. Wave 2 改变了 Phase 6 的核心行为模型（conclusion.md 自己评估为 "High Risk"）。没有实际跑通就进入 Wave 3 是盲飞。
2. Gemini 的实际优化建议质量未知。重写提示词后 Gemini 可能产出：(a) 高质量的结构性建议（期望情况），(b) 仍然是属性级微调换了一种说法，(c) 过于激进的建议导致 slide-core 频繁 regenerate。只有实际运行才能知道。
3. Wave 3 的 fix 策略分类（attribute_change / layout_restructure / full_rethink）需要真实的 Gemini 输出样本来验证分类是否充分、边界是否清晰。handoff.json UD-3 也承认这一点。
4. Self-review fallback 的 "technical validation only" 路径需要验证：纯技术检查是否足以通过大部分幻灯片？还是会大量误报需要调整阈值？

**建议**：在 Wave 2 完成后、Wave 3 开始前，运行一个 8-10 页的 production deck（可以复用小米 SU7 或选择新主题），收集：
- Gemini 的实际优化建议样本（验证建议类型分类）
- Self-review fallback 的技术检查通过率（验证阈值合理性）
- fix loop 是否首次被触发（验证优化层是否真正产出了有区分度的信号）

这个校准跑应作为 **Wave 2→3 之间的 Gate**，而不是可选步骤。

**Verdict**: 必须增加。这是 Wave 2 "High Risk" 评级的直接对应措施。没有校准跑，Wave 3 的设计决策缺乏实证基础。

---

## Scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Design Coherence** | **7/10** | 核心方向正确（优化师 vs 审计员的重新定位），但 SKILL.md 和 reviewer.md 中的审计员语言残留未被系统化识别；Wave 2/3 之间的 producer/consumer 依赖未理清；holistic review 的独特价值被低估 |
| **Practical Feasibility** | **6/10** | Wave 1 可直接执行；Wave 2 可行但缺少术语统一清单和校准跑计划使得实际效果不可预测；suggestion taxonomy 不够完整（缺 content_reduction 和 deck_coordination）；技术验证清单遗漏了高频问题（text overflow、content coverage） |

---

## Recommended Adjustments

1. **R2(a) 增加术语统一清单**：列出 SKILL.md、review-core.md、commands/ppt.md 中所有需要从审计员语言改为优化师语言的具体位置和建议措辞。
2. **R2(c) 前移到 Wave 2**：layout_suggestion 格式是 R2(a) 提示词重写的必要组件，不能推迟到 Wave 3。
3. **Suggestion taxonomy 扩展为 5 类**：增加 `content_reduction` 和 `deck_coordination`。
4. **技术验证清单扩展**：至少增加文本溢出估算和 outline 内容覆盖检查。
5. **Holistic review 设计前移到 Wave 3**：定义 `deck_coordination` 建议类型和 mid-flight checkpoint 协议。
6. **增加 Wave 2→3 校准跑 Gate**：8-10 页 production deck，验证 Gemini 建议质量和技术检查阈值。
7. **SKILL.md 第 81 行显式标记为修改项**：当前 "optimization must still happen" 与 R2(b) "technical validation only" 矛盾。

---

## Overall Verdict

**需要小幅修订后进入 plan phase。**

核心诊断和建议方向正确——Gemini 作为审美优化师的重新定位、self-review 的诚实降级、建议驱动替代分数驱动——这些都是对的。但执行细节上有几处 gap：Wave 2/3 的边界划分需要调整（R2c 前移），suggestion taxonomy 需要扩展，技术验证清单需要补全，以及最关键的——**缺少 Wave 2 之后的校准跑验证步骤**。

这些修订不改变整体架构方向，只是让执行计划更完整、风险更可控。修订量约半天工作，之后可以进入 plan phase。
