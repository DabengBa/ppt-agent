# PPT Agent

多智能体 PPT 幻灯片生成工作流，支持跨平台运行。

LLM 生成 + Gemini 审查，输出 SVG 1280×720 Bento Grid 布局的演示幻灯片。

## 效果展示

同一提示词、同一工作流，不同模型 × 不同宿主的对比效果：

> `/ppt-agent:ppt 帮我收集一下新一代小米su7的发布会资料然后做一套PPT`

### Claude Opus · Claude Code

| | | |
|:---:|:---:|:---:|
| ![封面](docs/images/slide-01.png) | ![产品定位](docs/images/slide-02.png) | ![外观设计](docs/images/slide-03.png) |
| ![性能参数](docs/images/slide-04.png) | ![标配亮点](docs/images/slide-05.png) | ![智能座舱](docs/images/slide-06.png) |
| ![智能驾驶](docs/images/slide-07.png) | ![安全体系](docs/images/slide-08.png) | ![续航充电](docs/images/slide-09.png) |
| ![产品矩阵](docs/images/slide-10.png) | ![生态布局](docs/images/slide-11.png) | ![结尾](docs/images/slide-12.png) |

### MiMo V2 Pro · OpenCode

| | | |
|:---:|:---:|:---:|
| ![封面](docs/images/mimo/slide-01.png) | ![市场势能](docs/images/mimo/slide-02.png) | ![更好看](docs/images/mimo/slide-03.png) |
| ![设计详情](docs/images/mimo/slide-04.png) | ![更好开](docs/images/mimo/slide-05.png) | ![配置对比](docs/images/mimo/slide-06.png) |
| ![蛟龙底盘](docs/images/mimo/slide-07.png) | ![更智能](docs/images/mimo/slide-08.png) | ![智能科技](docs/images/mimo/slide-09.png) |
| ![更安全](docs/images/mimo/slide-10.png) | ![安全守护](docs/images/mimo/slide-11.png) | ![竞品对决](docs/images/mimo/slide-12.png) |
| ![结尾](docs/images/mimo/slide-13.png) | | |

## 安装

```bash
claude plugin marketplace add zengwenliang416/ppt-agent
claude plugin install ppt-agent
```

## 使用

```
/ppt-agent:ppt <主题或需求描述>
```

## 工作流程

1. **初始化** — 解析参数，创建运行目录
2. **需求调研** — 背景搜索 + 用户确认需求
3. **素材收集** — 按章节并行深度搜索
4. **大纲规划** — 金字塔原理结构化大纲 + 用户审批
5. **规划草稿** — 每页生成简版 SVG 草稿
6. **设计稿 + 审查** — Bento Grid SVG 生成 + Gemini 质量审查循环
7. **交付** — 最终 SVG 文件 + 交互式 HTML 预览页

## 智能体

| 智能体 | 职责 |
|--------|------|
| `research-core` | 需求调研 + 素材收集 |
| `content-core` | 大纲规划 + 规划草稿 |
| `slide-core` | 设计 SVG 生成（Bento Grid 布局） |
| `review-core` | Gemini 驱动的 SVG 质量审查 |

## 输出目录

```
openspec/changes/<run_id>/
├── research-context.md      # 调研上下文
├── requirements.md          # 需求文档
├── materials.md             # 素材汇总
├── outline.json             # 结构化大纲
├── drafts/slide-{nn}.svg    # 规划草稿
├── slides/slide-{nn}.svg    # 设计稿
├── slide-status.json        # 逐页进度（支持中断恢复）
├── reviews/review-{nn}.md   # 审查报告
├── review-manifest.json     # 审查汇总（Phase 6→7 质量门控）
└── output/
    ├── slide-{nn}.svg       # 最终 SVG
    └── index.html           # 交互式预览页
```

## 跨平台适配路线图

PPT Agent 当前运行在 Claude Code 上，计划适配以下平台：

| 平台 | 难度 | 状态 | 说明 |
|------|------|------|------|
| [Droid (Factory)](https://factory.ai) | ⭐ | 🔜 待验证 | 官方兼容 Claude Code 插件格式，预计开箱即用 |
| [Codex (OpenAI)](https://developers.openai.com/codex) | ⭐⭐ | 📋 计划中 | SKILL.md 同构，agents 需 MD→TOML 转换 |
| [OpenClaw](https://openclaw.ai) | ⭐⭐⭐ | 📋 计划中 | SKILL.md 同构，需适配 plugin manifest 和 ClawHub |
| [OpenCode](https://opencode.ai) | ⭐⭐⭐⭐ | ✅ 已验证 | MiMo V2 Pro 已跑通完整工作流（见上方效果对比） |

### 长期方向

- **MCP Server 化**：将核心工作流封装为 MCP Server，暴露 `ppt/generate`、`ppt/outline`、`ppt/review` 等标准 tools。所有支持 MCP 的宿主（Claude Code / Codex / OpenCode / Droid / Cursor / Zed 等）均可直接接入，一次开发全平台通用。
- **核心解耦**：将 7 阶段工作流逻辑与宿主特有协议（Task / SendMessage / AskUserQuestion）分离为平台无关的 `core/` 层，新增平台只需编写轻量 adapter。
- **Headless 模式**：支持无交互批量生成，适用于 CI/CD pipeline 和 API 调用场景。

## 许可证

MIT
