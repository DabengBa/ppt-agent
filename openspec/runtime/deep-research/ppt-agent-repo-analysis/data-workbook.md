# PPT Agent 深度研究报告 — Task 2: 数据工作簿

## 1. 仓库总体统计

| 指标 | 数值 |
|------|------|
| 总文件数（不含 .git/runtime） | 23 |
| 源代码总行数 | 2,778 行 |
| 总字符数 | 105,476 字符 |
| Git 提交数 | 3 |
| 初始提交文件数 | 21 |
| 初始提交代码量 | 2,708 行 |
| 项目版本 | 1.0.0 |
| 创建日期 | 2026-03-21 |

## 2. 文件类型分布

| 扩展名 | 文件数 | 占比 | 主要用途 |
|--------|--------|------|---------|
| `.md` | 13 | 56.5% | 智能体定义、命令、提示词、文档 |
| `.yaml` | 4 | 17.4% | 风格令牌配置 |
| `.json` | 3 | 13.0% | 插件元数据、资源索引、包配置 |
| `.ts` | 1 | 4.3% | Gemini CLI 调用脚本 |
| `.html` | 1 | 4.3% | 交互式预览模板 |
| `.gitignore` | 1 | 4.3% | Git 忽略规则 |

**关键观察**：Markdown 占文件总数的 56.5%，说明这是一个"文档即代码"的项目——智能体行为通过结构化 Markdown 定义，而非传统编程语言。

## 3. 目录结构与代码分布

| 目录 | 文件数 | 行数 | 占比 | 职责 |
|------|--------|------|------|------|
| `skills/_shared/references/prompts/` | 4 | 698 | 25.1% | 核心设计系统提示词 |
| `skills/_shared/assets/` | 1 | 528 | 19.0% | HTML 预览模板 |
| `skills/gemini-cli/` (合计) | 3 | 510 | 18.4% | Gemini 审查技能 |
| `agents/` | 4 | 335 | 12.1% | 智能体定义 |
| `commands/` | 1 | 261 | 9.4% | 主编排命令 |
| `skills/_shared/references/styles/` | 4 | 206 | 7.4% | 风格令牌 |
| 根目录 (CLAUDE.md + README + configs) | 6 | 240 | 8.6% | 项目文档和配置 |

### 代码量分布图（文本表示）

```
提示词系统 ████████████████████████░░░ 698 行 (25.1%)
HTML 模板  ███████████████████░░░░░░░░ 528 行 (19.0%)
Gemini 技能 ██████████████████░░░░░░░░░ 510 行 (18.4%)
智能体定义  ████████████░░░░░░░░░░░░░░░ 335 行 (12.1%)
主命令     █████████░░░░░░░░░░░░░░░░░░ 261 行 ( 9.4%)
风格令牌   ███████░░░░░░░░░░░░░░░░░░░░ 206 行 ( 7.4%)
文档/配置  ████████░░░░░░░░░░░░░░░░░░░ 240 行 ( 8.6%)
```

## 4. 智能体详细参数

### 4.1 智能体配置矩阵

| 智能体 | 行数 | 模型 | 工具数 | Max Turns | Effort | 模式数 |
|--------|------|------|--------|-----------|--------|--------|
| research-core | 63 | Sonnet | 6 | 20 | Medium | 2 (research, collect) |
| content-core | 77 | Opus | 4 | 25 | High | 2 (outline, draft) |
| slide-core | 95 | Opus | 5 | 30 | High | 1 (design, +fixes) |
| review-core | 100 | Sonnet | 4 | 15 | Medium | 2 (review, holistic) |

### 4.2 信号协议统计

| 智能体 | 信号类型数 | 信号列表 |
|--------|-----------|---------|
| research-core | 4 | heartbeat, research_ready, collection_ready, error |
| content-core | 5 | heartbeat, outline_ready, draft_slide_ready, draft_complete, error |
| slide-core | 4 | heartbeat, slide_ready, slide_fixed, error |
| review-core | 4 | heartbeat, review_passed, review_failed, error |

**总信号类型**：17 个（含重复 heartbeat/error），去重后 10 个独立信号类型。

## 5. 设计系统数据

### 5.1 提示词参考规模

| 提示词文件 | 行数 | 核心内容 |
|-----------|------|---------|
| svg-generator.md | 300 | SVG 画布规范、设计令牌、CJK 处理 |
| bento-grid-layout.md | 208 | 10 种布局、卡片约束、构成指南 |
| outline-architect.md | 130 | 金字塔原理、4 种框架、JSON schema |
| cognitive-design-principles.md | 60 | Miller 定律、Mayer 原理、Gestalt |

**总提示词行数**：698 行——占整个项目的 25.1%，这是项目知识密度最高的部分。

### 5.2 布局系统参数

| 布局类型 | 适用场景 | 最大信息单元 |
|---------|---------|-------------|
| single_focus | 封面、引言 | 2-3 |
| 2-column symmetric | 对比 | 4-6 |
| 2-column asymmetric | 图文混排 | 3-5 |
| 3-column | 多特性并列 | 4-6 |
| hero+grid | 主视觉+细节 | 4-7 |
| mixed | 灵活内容 | 3-5 |
| timeline | 时间线/流程 | 3-6 |
| dashboard | 数据仪表盘 | 4-7 |
| horizontal split | 上下分区 | 3-5 |
| full-bleed | 全出血背景 | 1-2 |

### 5.3 风格系统参数

| 风格 | 主色 | 辅色 | 强调色 | 标题字体 | 正文字体 | CJK 字体 |
|------|------|------|--------|---------|---------|---------|
| business | #1a365d | #2d3748 | #e67e22 | Inter | Inter | Noto Sans SC |
| tech | #0f172a | #1e293b | #6366f1 | JetBrains Mono | Inter | Noto Sans SC |
| creative | #1a1a2e | #2d1b69 | #7c3aed | Poppins | Inter | Noto Sans SC |
| minimal | #18181b | #27272a | #3b82f6 | Inter | Inter | Noto Sans SC |

**关键约束参数**：
- 卡片宽高比范围：1:2 ～ 4:1
- 安全区域内边距：60px
- 最小正文字体：14px
- 最小标签字体：12px
- 卡片标题字体：24-32px
- 卡片间距：16px

## 6. 质量门控参数

### 6.1 评分模型

| 评分维度 | 权重 | 硬门控阈值 | 说明 |
|---------|------|-----------|------|
| Layout Balance | 25% | >= 6 | 空间分配均衡性 |
| Readability | 25% | >= 6 | 文字可读性 |
| Typography | 20% | — | 排版规范性 |
| Information Density | 20% | — | 信息密度合理性 |
| Color Harmony | 10% | — | 色彩搭配和谐度 |

**通过条件**：加权总分 >= 7.0 且 Layout Balance >= 6 且 Readability >= 6

### 6.2 自适应修复预算

| 初始分数区间 | 修复策略 | 最大修复轮数 |
|-------------|---------|-------------|
| >= 7.0 | 直接通过 | 0 |
| 5.0 - 6.9 | 迭代修复 | 2 |
| 3.0 - 4.9 | 有限修复 | 1 |
| < 3.0 | 从头重新生成 | 0（重生成） |

### 6.3 自动化预检项

| 检查项 | 严重级别 | 工具 | 失败行为 |
|--------|---------|------|---------|
| XML 有效性 | Critical | xmllint | 自动失败，不进入 LLM 审查 |
| ViewBox 存在 | Critical | grep | 自动失败 |
| 字体大小 >= 12px | Major/Info | grep | 扣分 |
| 颜色令牌合规性 | Warning | grep | 提示 |
| 安全区域边界 | Major | 坐标计算 | 扣分 |

## 7. 工作流参数

### 7.1 七阶段工作流

| 阶段 | 名称 | 硬停止 | 并行度 | 主要产出 |
|------|------|--------|--------|---------|
| 1 | Init | — | 串行 | run_dir, proposal.md, tasks.md |
| 2 | Requirement Research | ✅ | 串行 | research-context.md, requirements.md |
| 3 | Material Collection | — | 并行 N | materials-{topic}.md → materials.md |
| 4 | Outline Planning | ✅ | 串行 | outline.json, outline-preview.md |
| 5 | Planning Draft | — | 串行(逐张) | drafts/slide-{nn}.svg, draft-manifest.json |
| 6 | Design + Review | — | 管道化(窗口3) | slides/slide-{nn}.svg, reviews/review-{nn}.md |
| 7 | Delivery | ✅ | 串行 | output/*.svg, index.html, speaker-notes.md |

### 7.2 产出文件矩阵

| 产出文件 | 生成阶段 | 生成者 | 消费者 |
|---------|---------|--------|--------|
| input.md | Phase 1 | Lead | — |
| proposal.md | Phase 1 | Lead | — |
| tasks.md | Phase 1 | Lead | Lead |
| research-context.md | Phase 2 | research-core | Lead → content-core |
| requirements.md | Phase 2 | Lead | content-core |
| materials-{topic}.md | Phase 3 | research-core | Lead |
| materials.md | Phase 3 | Lead | content-core |
| outline.json | Phase 4 | content-core | content-core, slide-core, Lead |
| outline-preview.md | Phase 4 | content-core | 用户（审批） |
| drafts/slide-{nn}.svg | Phase 5 | content-core | slide-core |
| draft-manifest.json | Phase 5 | content-core | Lead |
| slides/slide-{nn}.svg | Phase 6 | slide-core | review-core |
| reviews/review-{nn}.md | Phase 6 | review-core | Lead, slide-core |
| output/slide-{nn}.svg | Phase 7 | Lead | 用户 |
| output/index.html | Phase 7 | Lead | 用户（浏览器） |
| speaker-notes.md | Phase 7 | Lead | 用户 |

## 8. HTML 预览模板数据

| 参数 | 值 |
|------|-----|
| 模板行数 | 528 行 |
| 查看模式 | 3（Gallery, Scroll, Present） |
| 模板占位符 | 4（TITLE, LOGO, ACCENT_COLOR, SLIDES_JSON） |
| 键盘快捷键 | 7（P, G, S, F, N, ←→, Esc） |
| 主题 | 深色 |
| CJK 支持 | 是 |

## 9. 技术栈汇总

### 9.1 运行时依赖

| 依赖 | 类型 | 必需性 | 用途 |
|------|------|--------|------|
| Claude Code | 平台 | 必需 | 插件宿主 |
| Claude Opus | API | 必需 | 内容和设计生成 |
| Claude Sonnet | API | 必需 | 研究和审查协调 |
| Gemini CLI | 工具 | 推荐（有回退） | SVG 质量审查 |
| Node.js + tsx | 运行时 | Gemini 审查时需要 | TypeScript 脚本执行 |
| xmllint | 系统工具 | 推荐 | SVG 格式验证 |
| 浏览器 | 工具 | 推荐 | 预览查看 |

### 9.2 Gemini 模型回退链

```
默认模型 → gemini-2.5-pro → gemini-2.5-flash → Claude 自审（exit code 2）
```

### 9.3 npm 包配置

```json
{
  "name": "ppt-agent",
  "version": "1.0.0",
  "description": "PPT slide generation workflow..."
}
```

**注意**：无 `dependencies`、无 `devDependencies`、无 `scripts`——这是一个纯插件项目，运行时通过 `npx tsx` 直接执行 TypeScript。

## 10. 页面类型与内容密度目标

| 页面类型 | 目标信息单元 | 最大关键点 | 首选布局 |
|---------|-----------|----------|---------|
| cover | 2-3 | 0 | single_focus |
| quote | 1-2 | 0 | single_focus |
| image | 1-2 | 0 | single_focus |
| content | 3-5 | 3 | two_column, mixed |
| data | 4-7 | 2 (+2-5 数据) | hero_grid, dashboard |
| comparison | 4-6 | 2-3/column | two_column, three_column |
| process | 3-5 | 3-5 steps | timeline, hero_grid |
| timeline | 3-6 | 3-6 nodes | timeline |

## 11. 关键数字摘要

| 指标 | 数值 |
|------|------|
| 智能体数量 | 4 |
| 工作流阶段数 | 7 |
| 硬停止点 | 3 |
| 布局类型 | 10 |
| 风格预设 | 4 |
| 提示词总行数 | 698 |
| 评分维度 | 5 |
| 通过阈值 | 7.0/10 |
| 最大修复轮数 | 2 |
| SVG 画布尺寸 | 1280×720 |
| 安全区域边距 | 60px |
| 信号类型（去重） | 10 |
| HTML 预览模式 | 3 |
| 键盘快捷键 | 7 |
| Gemini 回退层级 | 3 |
