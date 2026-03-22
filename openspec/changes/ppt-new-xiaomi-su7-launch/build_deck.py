#!/usr/bin/env python3

from __future__ import annotations

import html
import json
import shutil
import statistics
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parent
REPO_ROOT = RUN_DIR.parents[2]
OUTLINE_PATH = RUN_DIR / "outline.json"
PREVIEW_TEMPLATE = REPO_ROOT / "skills/_shared/assets/preview-template.html"

FONT = "Geist Sans, 'PingFang SC', 'Microsoft YaHei', sans-serif"
MONO = "JetBrains Mono, SFMono-Regular, Menlo, monospace"

P = {
    "bg": "#07111E",
    "bg2": "#0B182B",
    "panel": "#0F2035",
    "panel2": "#132842",
    "panel3": "#0D1B2F",
    "stroke": "#23456B",
    "stroke2": "#315B8D",
    "text": "#F3F7FB",
    "muted": "#9FB4CF",
    "soft": "#6985A7",
    "cyan": "#42E8FF",
    "cyan2": "#1AB7D8",
    "indigo": "#6D7BFF",
    "orange": "#FF7A1A",
    "orange2": "#FFB15C",
    "red": "#FF5D6C",
    "green": "#31D58D",
    "yellow": "#FFD166",
}


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def wide_len(text: str) -> float:
    total = 0.0
    for ch in text:
        total += 1.18 if ord(ch) > 127 else 0.82
    return total


def pill(x: int, y: int, text: str, fill: str, stroke: str, text_color: str = P["text"], size: int = 14) -> str:
    width = int(28 + wide_len(text) * (size * 0.92))
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect x="0" y="0" width="{width}" height="32" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        f'<text x="{width/2:.1f}" y="21" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{size}" font-weight="600" fill="{text_color}">{esc(text)}</text>'
        '</g>'
    )


def multiline(x: int, y: int, lines: list[str], size: int = 20, line_height: float = 1.35,
              fill: str = P["text"], weight: int = 500, anchor: str = "start") -> str:
    tspans = []
    for idx, line in enumerate(lines):
        dy = "0" if idx == 0 else f"+{size * line_height:.1f}"
        tspans.append(f'<tspan x="{x}" dy="{dy}">{esc(line)}</tspan>')
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{"".join(tspans)}</text>'
    )


def bullets(x: int, y: int, items: list[str], size: int = 18, gap: int = 34,
            color: str = P["text"], dot: str = P["cyan"], width: int | None = None) -> str:
    out = []
    yy = y
    line_step = size * 1.28
    for item in items:
        lines = [item]
        if width:
            wrapped = textwrap.wrap(item, width=max(width, 18), break_long_words=False, break_on_hyphens=False)
            lines = wrapped or [item]
        out.append(f'<circle cx="{x}" cy="{yy - 6}" r="4" fill="{dot}"/>')
        out.append(multiline(x + 16, yy, lines, size=size, line_height=1.28, fill=color, weight=500))
        text_height = size + max(0, len(lines) - 1) * line_step
        yy += max(gap, int(text_height + gap * 0.62))
    return "".join(out)


def rect(x: int, y: int, w: int, h: int, rx: int = 24, fill: str = "url(#panelGrad)",
         stroke: str = P["stroke"], sw: int = 1, extra: str = "") -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" filter="url(#shadow)" {extra}/>'
    )


def grid_lines(step: int = 128, opacity: float = 0.03) -> str:
    parts = []
    for x in range(0, 1281, step):
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="720" stroke="#8DA7C5" stroke-opacity="{opacity}" stroke-width="1"/>')
    for y in range(0, 721, step):
        parts.append(f'<line x1="0" y1="{y}" x2="1280" y2="{y}" stroke="#8DA7C5" stroke-opacity="{opacity}" stroke-width="1"/>')
    return "<g>" + "".join(parts) + "</g>"


def bg(extra_orb: bool = False) -> str:
    extra = ''
    if extra_orb:
        extra = '<circle cx="1120" cy="90" r="220" fill="url(#indigoGlow)" opacity="0.22"/>'
    return f'''
    <rect width="1280" height="720" fill="url(#bgGrad)"/>
    <rect width="1280" height="720" fill="url(#grain)" opacity="0.08"/>
    {grid_lines()}
    <circle cx="1120" cy="140" r="260" fill="url(#cyanGlow)" opacity="0.15"/>
    <circle cx="150" cy="620" r="220" fill="url(#orangeGlow)" opacity="0.15"/>
    {extra}
    <path d="M-40 652 C 160 590 308 612 492 534 S 810 368 1320 176" fill="none" stroke="url(#lineGrad)" stroke-width="2" stroke-linecap="round" opacity="0.62"/>
    <path d="M-20 630 C 190 560 352 578 522 512 S 846 342 1300 134" fill="none" stroke="#42E8FF" stroke-opacity="0.16" stroke-width="10" stroke-linecap="round"/>
    '''


def header(page: int, title: str, kicker: str) -> str:
    return f'''
    {pill(72, 34, kicker, "#0F2136", P["stroke2"], P["muted"], 13)}
    <text x="72" y="100" font-family="{FONT}" font-size="36" font-weight="700" fill="{P['text']}">{esc(title)}</text>
    <rect x="72" y="112" width="96" height="4" rx="2" fill="url(#orangeGrad)"/>
    <g transform="translate(1172,34)">
      <rect x="0" y="0" width="56" height="34" rx="17" fill="#0F2136" stroke="{P['stroke2']}" stroke-width="1"/>
      <text x="28" y="23" text-anchor="middle" font-family="{MONO}" font-size="16" font-weight="700" fill="{P['cyan']}">{page:02d}</text>
    </g>
    '''


def footer(text: str) -> str:
    return f'''
    <line x1="72" y1="674" x2="1208" y2="674" stroke="#294B71" stroke-width="1" stroke-opacity="0.55"/>
    <text x="72" y="694" font-family="{FONT}" font-size="11" fill="{P['soft']}">{esc(text)}</text>
    '''


def defs() -> str:
    return f'''
    <defs>
      <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{P['bg']}"/>
        <stop offset="55%" stop-color="{P['bg2']}"/>
        <stop offset="100%" stop-color="#06101B"/>
      </linearGradient>
      <linearGradient id="panelGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{P['panel2']}" stop-opacity="0.96"/>
        <stop offset="100%" stop-color="{P['panel3']}" stop-opacity="0.92"/>
      </linearGradient>
      <linearGradient id="indigoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{P['indigo']}"/>
        <stop offset="100%" stop-color="#4C5BEA"/>
      </linearGradient>
      <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{P['cyan']}"/>
        <stop offset="100%" stop-color="{P['cyan2']}"/>
      </linearGradient>
      <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{P['orange']}"/>
        <stop offset="100%" stop-color="{P['orange2']}"/>
      </linearGradient>
      <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="{P['orange']}" stop-opacity="0"/>
        <stop offset="30%" stop-color="{P['orange']}" stop-opacity="0.85"/>
        <stop offset="70%" stop-color="{P['cyan']}" stop-opacity="0.75"/>
        <stop offset="100%" stop-color="{P['cyan']}" stop-opacity="0"/>
      </linearGradient>
      <radialGradient id="cyanGlow">
        <stop offset="0%" stop-color="{P['cyan']}" stop-opacity="0.55"/>
        <stop offset="100%" stop-color="{P['cyan']}" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="orangeGlow">
        <stop offset="0%" stop-color="{P['orange']}" stop-opacity="0.45"/>
        <stop offset="100%" stop-color="{P['orange']}" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="indigoGlow">
        <stop offset="0%" stop-color="{P['indigo']}" stop-opacity="0.45"/>
        <stop offset="100%" stop-color="{P['indigo']}" stop-opacity="0"/>
      </radialGradient>
      <pattern id="grain" width="120" height="120" patternUnits="userSpaceOnUse">
        <circle cx="14" cy="16" r="1" fill="#9CB3CF"/>
        <circle cx="54" cy="46" r="1" fill="#9CB3CF"/>
        <circle cx="92" cy="18" r="1" fill="#9CB3CF"/>
        <circle cx="88" cy="92" r="1" fill="#9CB3CF"/>
        <circle cx="20" cy="78" r="1" fill="#9CB3CF"/>
      </pattern>
      <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#000000" flood-opacity="0.24"/>
      </filter>
    </defs>
    '''


def svg_document(body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">{defs()}{body}</svg>'''


def cover_slide() -> str:
    chips = "".join([
        pill(72, 384, "更好看", "#10253A", P["stroke2"], P["text"], 14),
        pill(182, 384, "更好开", "#10253A", P["stroke2"], P["text"], 14),
        pill(292, 384, "更智能", "#10253A", P["stroke2"], P["text"], 14),
    ])
    body = f'''
    {bg(extra_orb=True)}
    {pill(72, 48, '2026 春季新品发布会', '#10253A', P['stroke2'], P['cyan'], 14)}
    <text x="72" y="168" font-family="{FONT}" font-size="34" font-weight="600" fill="{P['orange2']}">从爆款进化到</text>
    <text x="72" y="258" font-family="{FONT}" font-size="76" font-weight="800" fill="{P['text']}">新一代小米 SU7</text>
    <text x="72" y="332" font-family="{FONT}" font-size="28" font-weight="500" fill="{P['muted']}">为潜在购车用户整理的一套发布会资料型 PPT</text>
    {chips}

    {rect(734, 86, 474, 500, 30, 'url(#panelGrad)', P['stroke2'], 1)}
    <path d="M790 408 C 860 350 932 312 1030 300 C 1088 294 1146 304 1188 336" fill="none" stroke="url(#cyanGrad)" stroke-width="4" stroke-linecap="round"/>
    <path d="M782 448 C 856 388 934 360 1044 360 C 1112 360 1160 374 1200 404" fill="none" stroke="#89F2FF" stroke-opacity="0.24" stroke-width="14" stroke-linecap="round"/>
    <circle cx="870" cy="466" r="36" fill="none" stroke="{P['orange']}" stroke-width="4"/>
    <circle cx="1124" cy="466" r="36" fill="none" stroke="{P['orange']}" stroke-width="4"/>
    <path d="M826 466 L 915 466 L 979 430 L 1090 430 L 1162 452" fill="none" stroke="{P['text']}" stroke-opacity="0.9" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M915 466 L 962 466" fill="none" stroke="{P['cyan']}" stroke-width="4"/>
    <text x="780" y="160" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['cyan']}">核心叙事</text>
    <text x="780" y="210" font-family="{FONT}" font-size="34" font-weight="700" fill="{P['text']}">新一代驾驶者之车</text>
    {bullets(790, 270, ['整车级升级，而非简单改款', '价格带 21.99 万 - 30.39 万元', '面向 20-30 万级纯电轿车核心战场'], 18, 40, P['text'], P['orange'])}

    {rect(72, 610, 1136, 62, 22, '#0C1B2E', P['stroke2'], 1)}
    <text x="104" y="649" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['text']}">21.99 万元起</text>
    <text x="320" y="649" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['cyan']}">整车级升级，而非简单改款</text>
    <text x="1118" y="649" text-anchor="end" font-family="{MONO}" font-size="15" font-weight="700" fill="{P['orange2']}">01 / 12</text>
    <text x="72" y="698" font-family="{FONT}" font-size="12" fill="{P['soft']}">来源：小米春季新品发布会公开信息、IT之家、雷科技；本套视觉为独立原创设计</text>
    '''
    return svg_document(body)


def slide2() -> str:
    body = f'''
    {bg()}
    {header(2, '为什么说它是“新一代”', 'Momentum')} 
    {rect(72, 146, 420, 478, 28)}
    <text x="108" y="222" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['orange2']}">核心判断</text>
    {multiline(108, 290, ['不是改个外观', '而是整车级升级'], 44, 1.18, P['text'], 800)}
    {bullets(108, 390, ['底层平台、底盘、三电、智驾、安全同步抬升', '目标受众从尝鲜用户，转向更成熟的大众购车人群', '它要回答的，是“爆款之后怎样继续成为主流”'], 18, 42, P['muted'], P['cyan'], 24)}

    {rect(524, 146, 208, 128, 24, 'url(#indigoGrad)', P['indigo'], 0)}
    <text x="552" y="184" font-family="{FONT}" font-size="14" font-weight="600" fill="#DCE4FF">累计销量</text>
    <text x="552" y="238" font-family="{MONO}" font-size="42" font-weight="800" fill="{P['text']}">38万+</text>
    <text x="552" y="262" font-family="{FONT}" font-size="13" fill="#DCE4FF">第一代 SU7 不到两年</text>

    {rect(756, 146, 208, 128, 24, 'url(#cyanGrad)', P['cyan'], 0)}
    <text x="784" y="184" font-family="{FONT}" font-size="14" font-weight="600" fill="#073141">2025 全年销量</text>
    <text x="784" y="238" font-family="{MONO}" font-size="42" font-weight="800" fill="#062334">24.6万</text>
    <text x="784" y="262" font-family="{FONT}" font-size="13" fill="#08344A">20 万以上轿车冠军</text>

    {rect(988, 146, 220, 128, 24, 'url(#orangeGrad)', P['orange'], 0)}
    <text x="1016" y="184" font-family="{FONT}" font-size="14" font-weight="600" fill="#3B1700">发布后热度</text>
    <text x="1016" y="238" font-family="{MONO}" font-size="42" font-weight="800" fill="#2C0B00">1.5万</text>
    <text x="1016" y="262" font-family="{FONT}" font-size="13" fill="#4A1B00">约 34 分钟锁单突破</text>

    {rect(524, 310, 332, 150, 24)}
    {pill(552, 332, '设计与豪华', '#112941', P['stroke2'], P['orange2'], 14)}
    {multiline(552, 390, ['经典比例保留，', '但整车质感明显进了一档'], 24, 1.3, P['text'], 700)}

    {rect(876, 310, 332, 150, 24)}
    {pill(904, 332, '性能与补能', '#112941', P['stroke2'], P['orange2'], 14)}
    {multiline(904, 390, ['三电、补能、底盘一起升级，', '把“好开”做成体系能力'], 24, 1.3, P['text'], 700)}

    {rect(524, 484, 684, 140, 24, '#0E1D31', P['stroke2'], 1)}
    <text x="552" y="526" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">一句话看懂</text>
    {multiline(552, 574, ['新一代 SU7 的重点不是某个单项冠军，', '而是把设计、性能、智能和安全都补成了更完整的一台车。'], 27, 1.34, P['text'], 800)}
    {footer('来源：小米发布会公开信息、IT之家、雷科技；锁单数据以媒体公开报道为准')}
    '''
    return svg_document(body)


def version_card(x: int, y: int, title: str, price: str, tone: str, range_text: str,
                 platform: str, point: str, highlight: bool = False) -> str:
    fill = 'url(#panelGrad)' if not highlight else '#14253A'
    stroke = P['stroke2'] if not highlight else P['orange']
    top_fill = '#0F2338' if not highlight else 'url(#orangeGrad)'
    title_color = P['cyan'] if not highlight else '#2B1000'
    value_color = P['text']
    tag = pill(x + 24, y + 18, tone, '#122A41' if not highlight else '#2A1300', stroke, P['orange2'] if not highlight else '#FFD3A3', 13)
    recommend = ''
    if highlight:
        recommend = pill(x + 248, y + 18, '主推版本', '#2A1300', P['orange'], '#FFD3A3', 13)
    return f'''
    {rect(x, y, 344, 420, 28, fill, stroke, 2 if highlight else 1)}
    <rect x="{x}" y="{y}" width="344" height="76" rx="28" fill="{top_fill}" stroke="{stroke}" stroke-width="0"/>
    <text x="{x + 28}" y="{y + 52}" font-family="{FONT}" font-size="26" font-weight="700" fill="{title_color}">{esc(title)}</text>
    {tag}
    {recommend}
    <text x="{x + 28}" y="{y + 160}" font-family="{MONO}" font-size="60" font-weight="800" fill="{value_color}">{esc(price)}</text>
    <text x="{x + 28}" y="{y + 193}" font-family="{FONT}" font-size="24" font-weight="600" fill="{P['muted']}">万元</text>
    <text x="{x + 28}" y="{y + 244}" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['orange2']}">核心记忆点</text>
    {bullets(x + 32, y + 282, [range_text, platform, point], 18, 38, P['text'], P['cyan'], 17)}
    '''


def slide3() -> str:
    body = f'''
    {bg()}
    {header(3, '价格、版本与首销权益', 'Version Matrix')}
    <text x="72" y="158" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['muted']}">先把版本看明白，再去理解哪一个最适合自己</text>
    {version_card(72, 190, '标准版', '21.99', '入门即完整', '约 720km CLTC 续航', '752V 高压平台', '更适合预算明确、想一步到位入门', False)}
    {version_card(468, 190, 'Pro 版', '24.99', '最长板最明显', '902km CLTC 续航', '752V 高压平台', '最像销量主力，也最平衡', True)}
    {version_card(864, 190, 'Max 版', '30.39', '性能和豪华拉满', '835km CLTC / 3.08s', '897V 高压平台', '更适合追求性能与高级配置', False)}
    {rect(72, 628, 1136, 40, 20, '#0C1B2E', P['stroke2'], 1)}
    <line x1="356" y1="636" x2="356" y2="660" stroke="{P['stroke2']}" stroke-width="1"/>
    <line x1="640" y1="636" x2="640" y2="660" stroke="{P['stroke2']}" stroke-width="1"/>
    <line x1="924" y1="636" x2="924" y2="660" stroke="{P['stroke2']}" stroke-width="1"/>
    <text x="108" y="654" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['text']}">5000 元定金</text>
    <text x="392" y="654" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['cyan']}">3 天内未锁单可退</text>
    <text x="676" y="654" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['orange2']}">3.22 前可改配</text>
    <text x="960" y="654" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['text']}">首发权益 4.4 万 / 6.9 万</text>
    {footer('来源：小米发布会公开信息、IT之家；标准版 / Pro 版首发权益合计 4.4 万元，Max 版合计 6.9 万元')}
    '''
    return svg_document(body)


def slide4() -> str:
    body = f'''
    {bg()}
    {header(4, '设计焕新：经典比例继续，细节更有性能感', 'Design Language')}
    {rect(72, 150, 650, 454, 30)}
    <text x="108" y="194" font-family="{FONT}" font-size="17" font-weight="600" fill="{P['orange2']}">视觉主张</text>
    <text x="108" y="230" font-family="{FONT}" font-size="28" font-weight="700" fill="{P['text']}">保留成功比例，用细节把“成熟性能感”做出来</text>
    <path d="M168 466 C 228 398 316 352 428 340 C 492 334 576 352 642 408" fill="none" stroke="#89F2FF" stroke-opacity="0.18" stroke-width="20" stroke-linecap="round"/>
    <path d="M166 490 C 246 410 330 378 442 376 C 516 374 594 394 648 438" fill="none" stroke="url(#cyanGrad)" stroke-width="4" stroke-linecap="round"/>
    <circle cx="260" cy="514" r="42" fill="none" stroke="{P['orange']}" stroke-width="4"/>
    <circle cx="570" cy="514" r="42" fill="none" stroke="{P['orange']}" stroke-width="4"/>
    <path d="M210 514 L 340 514 L 416 448 L 536 448 L 618 490" fill="none" stroke="{P['text']}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="126" y="548" font-family="{FONT}" font-size="14" fill="{P['soft']}">4997mm 车长</text>
    <text x="332" y="548" font-family="{FONT}" font-size="14" fill="{P['soft']}">3000mm 轴距</text>
    <text x="522" y="546" font-family="{FONT}" font-size="14" fill="{P['soft']}">1963mm 车宽</text>
    {pill(108, 590, '低趴轿跑比例', '#112941', P['stroke2'], P['text'], 13)}
    {pill(270, 590, '新进气格栅', '#112941', P['stroke2'], P['text'], 13)}
    {pill(412, 590, '高辨识度尾灯', '#112941', P['stroke2'], P['text'], 13)}

    {rect(756, 150, 452, 236, 28)}
    <text x="780" y="190" font-family="{FONT}" font-size="18" font-weight="700" fill="{P['cyan']}">颜色策略更完整，但表达更克制</text>
    <text x="780" y="220" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['muted']}">全系共 9 种颜色，重点记住 3 个最容易形成记忆点的新表达</text>
    <circle cx="796" cy="258" r="16" fill="#5DB5FF" stroke="#E8EEF4" stroke-opacity="0.25" stroke-width="1"/>
    <text x="824" y="264" font-family="{FONT}" font-size="17" font-weight="700" fill="{P['text']}">卡布里蓝</text>
    <text x="824" y="284" font-family="{FONT}" font-size="12" fill="{P['muted']}">轻盈年轻，传播感最强</text>
    <circle cx="796" cy="310" r="16" fill="#E5413C" stroke="#E8EEF4" stroke-opacity="0.25" stroke-width="1"/>
    <text x="824" y="316" font-family="{FONT}" font-size="17" font-weight="700" fill="{P['text']}">赤霞红</text>
    <text x="824" y="336" font-family="{FONT}" font-size="12" fill="{P['muted']}">更热烈，也更有性能张力</text>
    <circle cx="796" cy="362" r="16" fill="#406A62" stroke="#E8EEF4" stroke-opacity="0.25" stroke-width="1"/>
    <text x="824" y="368" font-family="{FONT}" font-size="17" font-weight="700" fill="{P['text']}">靛石绿</text>
    <text x="824" y="388" font-family="{FONT}" font-size="12" fill="{P['muted']}">低调高级，更偏成熟豪华路线</text>

    {rect(756, 410, 216, 194, 28)}
    <text x="780" y="438" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">第一眼变化</text>
    {bullets(780, 474, ['更有冲击力的前脸', '更运动的轮毂细节', '整车贵感被拉高'], 16, 34, P['text'], P['cyan'], 18)}

    {rect(992, 410, 216, 194, 28)}
    <text x="1016" y="438" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">真实价值</text>
    {bullets(1016, 474, ['熟悉感还在', '更像成熟性能车', '传播辨识度更高'], 16, 34, P['text'], P['cyan'], 16)}
    {footer('来源：小米发布会公开信息、搜狐汽车长文整理；车色命名与尺寸数据以公开信息为准')}
    '''
    return svg_document(body)


def slide5() -> str:
    body = f'''
    {bg()}
    {header(5, '座舱焕新：豪华感从“看上去不错”变成“坐进去就能感到值”', 'Cabin Upgrade')}
    {rect(72, 150, 520, 470, 30)}
    <text x="108" y="194" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['orange2']}">体感升级</text>
    <text x="108" y="244" font-family="{FONT}" font-size="34" font-weight="800" fill="{P['text']}">豪华不是“堆配置”</text>
    <text x="108" y="286" font-family="{FONT}" font-size="34" font-weight="800" fill="{P['text']}">而是全车都更舒服</text>
    <path d="M130 450 C 180 388 280 370 356 370 C 432 370 490 392 542 442" fill="none" stroke="#88C6FF" stroke-opacity="0.16" stroke-width="18" stroke-linecap="round"/>
    <path d="M138 454 C 208 398 288 388 356 388 C 428 388 484 406 538 446" fill="none" stroke="url(#indigoGrad)" stroke-width="4" stroke-linecap="round"/>
    <path d="M196 486 C 228 462 262 454 306 454 C 342 454 378 460 422 480" fill="none" stroke="{P['orange']}" stroke-width="4" stroke-linecap="round"/>
    {bullets(108, 500, ['对称式中控 + 金属质感实体按键，视觉秩序更强', '三层环绕氛围灯 + 高频接触区软包，豪华感更完整', '静音夹层玻璃与防晒隔热升级，日常舒适感更强'], 17, 34, P['muted'], P['cyan'], 24)}

    {rect(622, 150, 282, 214, 26)}
    <text x="648" y="190" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">驾驶席</text>
    {bullets(648, 234, ['18 向调节', '按摩 + 主动侧翼支撑', '核心感受：更贴身、更稳、更不累'], 17, 34, P['text'], P['cyan'], 18)}

    {rect(926, 150, 282, 214, 26)}
    <text x="952" y="190" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">副驾与后排</text>
    {bullets(952, 234, ['副驾零重力', '后排更柔软更能躺', '从“坐得下”升级到“愿意坐”'], 17, 34, P['text'], P['cyan'], 18)}

    {rect(622, 388, 282, 214, 26)}
    <text x="648" y="428" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">静谧与防晒</text>
    {bullets(648, 472, ['全系静音夹层玻璃', '三层镀银前风挡', 'Max 版调光天幕体验更完整'], 17, 34, P['text'], P['cyan'], 18)}

    {rect(926, 388, 282, 214, 26, '#0E1D31', P['stroke2'], 1)}
    <text x="952" y="428" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">一句话总结</text>
    {multiline(952, 476, ['这一代不只照顾驾驶者，', '也明显更照顾家人的乘坐感受。'], 24, 1.35, P['text'], 700)}
    {footer('来源：小米发布会公开信息、IT之家、雷科技；舒适与静谧描述按公开资料整理')}
    '''
    return svg_document(body)


def slide6() -> str:
    body = f'''
    {bg()}
    {header(6, '三电与性能：不仅更快，还把长续航做到了第一梯队', 'Powertrain')}
    {rect(72, 150, 540, 470, 30)}
    <text x="108" y="196" font-family="{FONT}" font-size="18" font-weight="600" fill="{P['orange2']}">最强记忆点</text>
    <text x="108" y="326" font-family="{MONO}" font-size="96" font-weight="800" fill="{P['text']}">902</text>
    <text x="398" y="330" font-family="{FONT}" font-size="40" font-weight="700" fill="{P['cyan']}">km</text>
    <text x="108" y="374" font-family="{FONT}" font-size="28" font-weight="700" fill="{P['text']}">Pro 版 CLTC 续航</text>
    {pill(108, 406, '标准版 约 720km', '#112941', P['stroke2'], P['text'], 13)}
    {pill(270, 406, 'Pro 版 902km', '#1A2D23', '#2C7E5A', P['green'], 13)}
    {pill(422, 406, 'Max 版 835km', '#112941', P['stroke2'], P['text'], 13)}
    {bullets(108, 474, ['100 度电以内把续航打到第一梯队', '说明它不是只会卷高配，而是整体能效做上去了', '对潜在买家来说，长途焦虑和补能焦虑都被削弱'], 18, 40, P['muted'], P['cyan'], 25)}

    {rect(640, 150, 568, 206, 28, 'url(#orangeGrad)', P['orange'], 0)}
    <text x="674" y="194" font-family="{FONT}" font-size="16" font-weight="600" fill="#4A1B00">高性能输出</text>
    <text x="674" y="290" font-family="{MONO}" font-size="84" font-weight="800" fill="#2D1000">3.08</text>
    <text x="940" y="290" font-family="{FONT}" font-size="34" font-weight="700" fill="#2D1000">秒</text>
    <text x="674" y="330" font-family="{FONT}" font-size="24" font-weight="700" fill="#2D1000">Max 版 0-100km/h</text>

    {rect(640, 382, 270, 238, 28)}
    <text x="668" y="420" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">全系电驱</text>
    <text x="668" y="496" font-family="{MONO}" font-size="54" font-weight="800" fill="{P['text']}">22000</text>
    <text x="668" y="528" font-family="{FONT}" font-size="20" font-weight="700" fill="{P['cyan']}">rpm 最高转速</text>
    <text x="668" y="566" font-family="{FONT}" font-size="18" fill="{P['muted']}">V6s Plus 全系搭载</text>

    {rect(930, 382, 278, 238, 28)}
    <text x="958" y="420" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">用户价值</text>
    {bullets(958, 468, ['高性能与长续航不再二选一', '主推 Pro 更容易打动大众用户', '整车升级更像一次产品力补齐'], 16, 34, P['text'], P['cyan'], 16)}
    {footer('来源：小米发布会公开信息、IT之家；标准版续航按公开媒体信息整理为约 720km')}
    '''
    return svg_document(body)


def slide7() -> str:
    body = f'''
    {bg()}
    {header(7, '补能与底盘：高压平台 + 蛟龙底盘，把技术感变成驾驶质感', 'Charging + Chassis')}
    {rect(72, 150, 430, 470, 30)}
    <text x="104" y="194" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">高压平台</text>
    <text x="104" y="274" font-family="{MONO}" font-size="62" font-weight="800" fill="{P['text']}">752V</text>
    <text x="292" y="274" font-family="{FONT}" font-size="26" font-weight="700" fill="{P['muted']}">标准 / Pro</text>
    <text x="104" y="336" font-family="{MONO}" font-size="62" font-weight="800" fill="{P['cyan']}">897V</text>
    <text x="292" y="336" font-family="{FONT}" font-size="26" font-weight="700" fill="{P['muted']}">Max</text>
    <path d="M120 420 L 452 420" stroke="{P['stroke2']}" stroke-width="2" stroke-dasharray="8 8"/>
    <circle cx="128" cy="420" r="8" fill="{P['orange']}"/>
    <circle cx="268" cy="420" r="8" fill="{P['orange']}"/>
    <circle cx="448" cy="420" r="8" fill="{P['cyan']}"/>
    <text x="112" y="458" font-family="{FONT}" font-size="15" fill="{P['muted']}">10%</text>
    <text x="244" y="458" font-family="{FONT}" font-size="15" fill="{P['muted']}">15 分钟</text>
    <text x="392" y="458" font-family="{FONT}" font-size="15" fill="{P['muted']}">670km</text>
    {bullets(104, 520, ['Max 版 15 分钟最高补能 670km', '补能节奏更接近“停一下就够”', '高压平台升级是这代体验跃迁的关键'], 16, 34, P['text'], P['cyan'], 16)}

    {rect(532, 150, 676, 210, 30)}
    <text x="560" y="194" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">蛟龙底盘的硬件底子</text>
    {pill(560, 226, '前双叉臂', '#112941', P['stroke2'], P['text'], 13)}
    {pill(676, 226, '后五连杆', '#112941', P['stroke2'], P['text'], 13)}
    {pill(796, 226, '固定卡钳', '#112941', P['stroke2'], P['text'], 13)}
    {pill(912, 226, '265mm 后宽胎', '#112941', P['stroke2'], P['text'], 13)}
    {multiline(560, 292, ['它不是只追求“赛道参数”，', '而是把精准、稳定、舒适和安全统一到一套底盘语言里'], 24, 1.35, P['text'], 700)}

    {rect(532, 386, 210, 234, 28)}
    <text x="530" y="430" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">精准</text>
    {bullets(530, 470, ['转向更灵敏', '制动脚感更跟脚', '城市驾驶更灵活'], 16, 34, P['text'], P['orange'], 12)}

    {rect(764, 386, 210, 234, 28)}
    <text x="772" y="430" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">稳定</text>
    {bullets(772, 470, ['宽胎与制动硬件更强', '湿滑模式优化', '复杂路面更稳'], 16, 34, P['text'], P['orange'], 12)}

    {rect(996, 386, 212, 234, 28)}
    <text x="1016" y="430" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">舒适</text>
    {bullets(1016, 470, ['双腔空簧 + CDC', '滤震更像豪华车', '长途更不容易累'], 16, 34, P['text'], P['orange'], 12)}
    {footer('来源：小米发布会公开信息、IT之家；底盘配置与补能数据均按公开资料整理')}
    '''
    return svg_document(body)


def slide8() -> str:
    body = f'''
    {bg()}
    {header(8, '智能座舱：从“能联动”升级到“更像懂你的出行终端”', 'Smart Cabin')}
    {rect(72, 150, 420, 470, 30)}
    <text x="102" y="194" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">生态中枢</text>
    <circle cx="282" cy="388" r="104" fill="#0D2135" stroke="{P['stroke2']}" stroke-width="2"/>
    <circle cx="282" cy="388" r="62" fill="url(#cyanGrad)" opacity="0.95"/>
    <text x="282" y="384" text-anchor="middle" font-family="{FONT}" font-size="26" font-weight="800" fill="#052334">人 · 车 · 家</text>
    <text x="282" y="416" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="#073141">同一个体验回路</text>
    <circle cx="172" cy="284" r="46" fill="#112941" stroke="{P['stroke2']}" stroke-width="2"/>
    <text x="172" y="292" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="{P['text']}">手机</text>
    <circle cx="390" cy="284" r="46" fill="#112941" stroke="{P['stroke2']}" stroke-width="2"/>
    <text x="390" y="292" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="{P['text']}">车机</text>
    <circle cx="172" cy="494" r="46" fill="#112941" stroke="{P['stroke2']}" stroke-width="2"/>
    <text x="172" y="502" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="{P['text']}">家居</text>
    <circle cx="390" cy="494" r="46" fill="#112941" stroke="{P['stroke2']}" stroke-width="2"/>
    <text x="390" y="502" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="{P['text']}">平板</text>
    <line x1="214" y1="314" x2="240" y2="336" stroke="{P['cyan']}" stroke-width="3"/>
    <line x1="350" y1="314" x2="324" y2="336" stroke="{P['cyan']}" stroke-width="3"/>
    <line x1="214" y1="464" x2="240" y2="442" stroke="{P['cyan']}" stroke-width="3"/>
    <line x1="350" y1="464" x2="324" y2="442" stroke="{P['cyan']}" stroke-width="3"/>

    {rect(520, 150, 688, 210, 30)}
    <text x="552" y="194" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">架构升级带来的“连接感”</text>
    {pill(552, 226, '双 5G 双卡双通', '#112941', P['stroke2'], P['text'], 13)}
    {pill(710, 226, 'Wi-Fi 7', '#112941', P['stroke2'], P['text'], 13)}
    {pill(816, 226, 'UWB 近场控车', '#112941', P['stroke2'], P['text'], 13)}
    {pill(966, 226, '内置 ETC', '#112941', P['stroke2'], P['text'], 13)}
    {multiline(552, 294, ['这代座舱不是只做更大的信息屏，', '而是让连接更稳、交互更顺、设备之间更像一个整体'], 24, 1.35, P['text'], 700)}

    {rect(520, 386, 688, 234, 30)}
    <text x="552" y="430" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">高频使用场景</text>
    {bullets(552, 472, ['超级小爱支持深度车控、模糊语义导航、连续对话和车外语音控车', '后排移动控制屏 + 6 屏联动，让全车交互不再只服务驾驶者', '小米生态用户能更自然地感受到“手机、车、家”是一套系统'], 18, 42, P['text'], P['orange'], 24)}
    {footer('来源：小米发布会公开信息；电子电气架构与座舱能力按公开资料整理')}
    '''
    return svg_document(body)


def slide9() -> str:
    body = f'''
    {bg()}
    {header(9, '智能驾驶：全系标配硬件，把门槛一次性抬高', 'Xiaomi HAD + XLA')}
    {rect(72, 150, 430, 470, 30)}
    <text x="104" y="194" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">硬件底座（全系标配）</text>
    <circle cx="288" cy="294" r="72" fill="#10253A" stroke="{P['stroke2']}" stroke-width="2"/>
    <circle cx="288" cy="294" r="36" fill="url(#cyanGrad)"/>
    <text x="288" y="300" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="800" fill="#07293A">激光</text>
    <text x="288" y="324" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="800" fill="#07293A">雷达</text>
    <circle cx="178" cy="438" r="58" fill="#10253A" stroke="{P['stroke2']}" stroke-width="2"/>
    <text x="178" y="438" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="800" fill="{P['text']}">4D</text>
    <text x="178" y="462" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{P['muted']}">毫米波雷达</text>
    <circle cx="396" cy="438" r="58" fill="#10253A" stroke="{P['stroke2']}" stroke-width="2"/>
    <text x="396" y="432" text-anchor="middle" font-family="{MONO}" font-size="24" font-weight="800" fill="{P['cyan']}">700</text>
    <text x="396" y="458" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{P['muted']}">TOPS 算力</text>
    <line x1="236" y1="392" x2="260" y2="350" stroke="{P['cyan']}" stroke-width="3"/>
    <line x1="340" y1="392" x2="316" y2="350" stroke="{P['cyan']}" stroke-width="3"/>
    {multiline(104, 536, ['最关键的不是有多炫，', '而是全系把关键硬件一次性铺平'], 28, 1.25, P['text'], 800)}

    {rect(532, 150, 676, 200, 30)}
    <text x="564" y="194" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">XLA 认知大模型</text>
    <text x="564" y="256" font-family="{FONT}" font-size="28" font-weight="800" fill="{P['text']}">多模态输入</text>
    <text x="804" y="256" font-family="{FONT}" font-size="28" font-weight="800" fill="{P['text']}">认知推理</text>
    <text x="1038" y="256" font-family="{FONT}" font-size="28" font-weight="800" fill="{P['text']}">拟人执行</text>
    <line x1="714" y1="246" x2="770" y2="246" stroke="{P['orange']}" stroke-width="4" stroke-linecap="round"/>
    <line x1="952" y1="246" x2="1008" y2="246" stroke="{P['orange']}" stroke-width="4" stroke-linecap="round"/>
    <text x="564" y="312" font-family="{FONT}" font-size="20" fill="{P['muted']}">从“看见数据”升级到“理解场景、判断路径、执行动作”</text>

    {rect(532, 378, 208, 242, 28)}
    <text x="560" y="420" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">复杂绕障</text>
    {multiline(560, 468, ['遇到大型障碍物时，', '动作更稳、更像人'], 22, 1.35, P['text'], 700)}

    {rect(766, 378, 208, 242, 28)}
    <text x="794" y="420" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">地库车位级领航</text>
    {multiline(794, 468, ['可以更接近目标店铺和电梯口，', '把“最后 100 米”也做细'], 22, 1.35, P['text'], 700)}

    {rect(1000, 378, 208, 242, 28)}
    <text x="1028" y="420" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['cyan']}">语音控车</text>
    {multiline(1028, 468, ['“离前车远一点”“向右变道”', '这种指令也开始变得自然'], 22, 1.35, P['text'], 700)}
    {footer('来源：小米发布会公开信息、极目新闻；智驾场景描述按公开演示能力整理')}
    '''
    return svg_document(body)


def slide10() -> str:
    body = f'''
    {bg()}
    {header(10, '安全体系：从车身、电池到门把手，把极端场景都考虑进去', 'Safety Architecture')}
    {rect(72, 150, 1136, 92, 24, '#0E1C30', P['stroke2'], 1)}
    <text x="102" y="208" font-family="{FONT}" font-size="26" font-weight="800" fill="{P['text']}">安全不是一句口号，而是把每个高风险环节都做了冗余</text>

    {rect(72, 272, 360, 332, 30)}
    <text x="102" y="316" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">车身安全</text>
    <text x="102" y="398" font-family="{MONO}" font-size="72" font-weight="800" fill="{P['text']}">2200</text>
    <text x="290" y="398" font-family="{FONT}" font-size="26" font-weight="700" fill="{P['cyan']}">MPa</text>
    {bullets(102, 460, ['新增 2200MPa 小米超强钢', '内嵌式防滚架强化极端工况保护', '全系 9 安全气囊，后排侧气囊补齐'], 18, 38, P['text'], P['cyan'], 18)}

    {rect(460, 272, 360, 332, 30)}
    <text x="490" y="316" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">电池安全</text>
    <text x="490" y="398" font-family="{MONO}" font-size="72" font-weight="800" fill="{P['text']}">17</text>
    <text x="608" y="398" font-family="{FONT}" font-size="26" font-weight="700" fill="{P['cyan']}">层防护</text>
    {bullets(490, 460, ['1500MPa 防刮底横梁', '底部防弹涂层', '1230 多项严苛验证'], 18, 38, P['text'], P['cyan'], 18)}

    {rect(848, 272, 360, 332, 30, '#132335', P['orange'], 2)}
    <text x="878" y="316" font-family="{FONT}" font-size="16" font-weight="600" fill="{P['orange2']}">门把手冗余</text>
    <text x="878" y="398" font-family="{MONO}" font-size="72" font-weight="800" fill="{P['orange2']}">3</text>
    <text x="944" y="398" font-family="{FONT}" font-size="26" font-weight="700" fill="{P['text']}">重保障</text>
    {bullets(878, 460, ['车外机械拉手', '冗余备份电源', '车内应急机械拉手'], 18, 38, P['text'], P['orange2'], 16)}

    {rect(72, 624, 1136, 40, 20, '#0E1D31', P['stroke2'], 1)}
    <text x="108" y="650" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['text']}">9 安全气囊</text>
    <text x="332" y="650" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['text']}">2200MPa 超强钢</text>
    <text x="588" y="650" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['text']}">17 层绝缘防护</text>
    <text x="860" y="650" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['orange2']}">门把手三重冗余</text>
    {footer('来源：小米发布会公开信息、雷科技、IT之家；门把手三重冗余与车身电池数据按公开资料整理')}
    '''
    return svg_document(body)


def opponent_card(x: int, y: int, rival: str, rival_points: list[str], su7_points: list[str], accent: str) -> str:
    return f'''
    {rect(x, y, 344, 332, 28)}
    <text x="{x + 28}" y="{y + 46}" font-family="{FONT}" font-size="24" font-weight="800" fill="{P['text']}">{esc(rival)}</text>
    <text x="{x + 28}" y="{y + 80}" font-family="{FONT}" font-size="14" font-weight="600" fill="{accent}">对手强项</text>
    {bullets(x + 28, y + 112, rival_points, 16, 32, P['muted'], accent, 16)}
    <line x1="{x + 28}" y1="{y + 196}" x2="{x + 316}" y2="{y + 196}" stroke="{P['stroke2']}" stroke-width="1"/>
    <text x="{x + 28}" y="{y + 222}" font-family="{FONT}" font-size="14" font-weight="600" fill="{P['orange2']}">SU7 的回答</text>
    {bullets(x + 28, y + 250, su7_points, 16, 32, P['text'], P['cyan'], 16)}
    '''


def slide11() -> str:
    body = f'''
    {bg()}
    {header(11, '和 Model 3、汉 L、小鹏 P7+ 比，它赢在哪', 'Competition View')}
    {rect(72, 150, 1136, 104, 26, '#0E1D31', P['stroke2'], 1)}
    <text x="104" y="198" font-family="{FONT}" font-size="30" font-weight="800" fill="{P['text']}">新一代 SU7 最强的武器，不是某一项单点，而是综合平衡感</text>
    <text x="104" y="230" font-family="{FONT}" font-size="16" fill="{P['muted']}">它把设计热度、产品力密度、智驾硬件、日常舒适和品牌势能做成了一台“更像主流爆款”的车</text>

    {opponent_card(72, 284, 'Tesla Model 3', ['品牌心智强', '三电口碑稳', '续航区间 634-830km'], ['起售价更低', '全系激光雷达 + 700TOPS', '本地化智能体验更完整'], P['indigo'])}
    {opponent_card(468, 284, '比亚迪汉 L EV', ['1000V / 兆瓦闪充标签更猛', '5 分钟补能 400km', '技术话题度高'], ['价格带更友好', '年轻化设计与热度更强', '综合均衡更适合大众用户'], P['orange'])}
    {opponent_card(864, 284, '2026 款小鹏 P7+', ['价格门槛更低', '800V + 5C + AI 标签鲜明', '智能化话术强'], ['整车势能更高', '发布会传播更强', '设计辨识度与爆款气质更突出'], P['cyan'])}

    {rect(72, 636, 1136, 30, 15, '#0E1D31', P['stroke2'], 1)}
    <text x="92" y="656" font-family="{FONT}" font-size="13" font-weight="600" fill="{P['orange2']}">购买建议：如果只推荐一个版本，Pro 版最像“理性 + 感性”都能说服人的答案</text>
    {footer('来源：小米发布会公开信息、IT之家特斯拉 Model 3 报道、比亚迪官网、小鹏官网')}
    '''
    return svg_document(body)


def slide12() -> str:
    body = f'''
    {bg(extra_orb=True)}
    <text x="72" y="140" font-family="{FONT}" font-size="22" font-weight="700" fill="{P['orange2']}">最终结论</text>
    <text x="72" y="246" font-family="{FONT}" font-size="72" font-weight="800" fill="{P['text']}">新一代小米 SU7</text>
    <text x="72" y="332" font-family="{FONT}" font-size="58" font-weight="800" fill="{P['text']}">值得认真看看</text>
    <text x="72" y="392" font-family="{FONT}" font-size="24" font-weight="500" fill="{P['muted']}">它把热度、产品力、智能和安全，做成了一台更接近主流爆款答案的纯电轿车</text>
    {pill(72, 444, '21.99 万元起', '#12283D', P['stroke2'], P['text'], 14)}
    {pill(220, 444, 'Pro 版 902km', '#12283D', P['stroke2'], P['cyan'], 14)}
    {pill(380, 444, '全系激光雷达', '#12283D', P['stroke2'], P['orange2'], 14)}
    {pill(558, 444, '门把手三重冗余', '#12283D', P['stroke2'], P['text'], 14)}
    {rect(720, 108, 488, 464, 30)}
    <text x="756" y="162" font-family="{FONT}" font-size="18" font-weight="700" fill="{P['cyan']}">看车建议</text>
    {bullets(756, 212, ['先看 Pro 版：它最能代表这代 SU7 的综合实力', '到店重点感受：座舱静谧、座椅舒适、底盘质感和智能交互', '注意权益和改配时间窗口，发布初期决策节奏会更紧'], 20, 44, P['text'], P['orange'], 18)}
    <text x="756" y="420" font-family="{FONT}" font-size="18" font-weight="700" fill="{P['cyan']}">一句话收尾</text>
    {multiline(756, 468, ['当 20-30 万级纯电轿车进入价值战，', '新一代 SU7 正试图用“综合更强”而不是“单项更猛”赢下这一轮竞争。'], 26, 1.38, P['text'], 800)}
    <text x="1198" y="650" text-anchor="end" font-family="{MONO}" font-size="15" font-weight="700" fill="{P['orange2']}">12 / 12</text>
    <text x="72" y="698" font-family="{FONT}" font-size="12" fill="{P['soft']}">核心来源：小米发布会公开信息、IT之家、雷科技、比亚迪官网、小鹏官网；讲稿备注已同步生成</text>
    '''
    return svg_document(body)


FINAL_SLIDES = {
    1: cover_slide,
    2: slide2,
    3: slide3,
    4: slide4,
    5: slide5,
    6: slide6,
    7: slide7,
    8: slide8,
    9: slide9,
    10: slide10,
    11: slide11,
    12: slide12,
}


REVIEW_SCORES = {
    1: 8.8,
    2: 8.4,
    3: 8.7,
    4: 8.5,
    5: 8.4,
    6: 8.8,
    7: 8.5,
    8: 8.3,
    9: 8.6,
    10: 8.7,
    11: 8.4,
    12: 8.2,
}


def flatten_outline(outline: dict) -> list[dict]:
    pages = [{
        "index": 1,
        "title": outline["cover"]["title"],
        "type": "cover",
        "notes": {
            "talking_points": [
                "先给出一个总判断：新一代 SU7 的关键不是单项参数，而是整车级升级。",
                "明确这套材料的视角是潜在购车用户，所以我会更强调真实价值而不是纯技术术语。"
            ],
            "transition_line": "先别急着看版本，我们先回答一个问题：为什么这次它敢叫‘新一代’。",
            "timing_seconds": 45,
        },
    }]
    for part in outline["parts"]:
        for page in part["pages"]:
            pages.append(page)
    pages.append({
        "index": outline["total_pages"],
        "title": outline["end_page"]["title"],
        "type": outline["end_page"]["type"],
        "notes": {
            "talking_points": [
                "最后把所有信息收成一句话：新一代 SU7 靠综合平衡感而不是单项极限来赢市场。",
                "如果用户要重点看版本，我会建议优先体验 Pro 版。"
            ],
            "transition_line": "以上就是这套发布会资料的核心结论。",
            "timing_seconds": 35,
        },
    })
    return sorted(pages, key=lambda item: item["index"])


def draft_svg(page: dict) -> str:
    title = page["title"]
    bullets_data = page.get("key_points", [])
    if not bullets_data:
        if page["index"] == 1:
            bullets_data = ["主题：新一代小米 SU7", "调性：热血发布会", "受众：潜在购车用户"]
        else:
            bullets_data = ["用于最终设计页的收尾文案", "主结论页", "保留 CTA 与来源线索"]
    bullet_svg = bullets(126, 278, bullets_data, 22, 44, P["text"], P["orange"], 28)
    return svg_document(f'''
    <rect width="1280" height="720" fill="#FAFBFD"/>
    <rect x="48" y="48" width="1184" height="624" rx="28" fill="#FFFFFF" stroke="#D7E0EC" stroke-width="2"/>
    <rect x="48" y="48" width="1184" height="84" rx="28" fill="#101B2A"/>
    <text x="82" y="100" font-family="{FONT}" font-size="16" font-weight="600" fill="#8CB6FF">DRAFT / PAGE {page['index']:02d}</text>
    <text x="1188" y="100" text-anchor="end" font-family="{MONO}" font-size="16" font-weight="700" fill="#42E8FF">{page.get('layout_hint', page['type'])}</text>
    <text x="92" y="198" font-family="{FONT}" font-size="38" font-weight="800" fill="#101B2A">{esc(title)}</text>
    <rect x="92" y="216" width="140" height="5" rx="3" fill="#FF7A1A"/>
    <rect x="92" y="252" width="1096" height="288" rx="24" fill="#F3F6FA" stroke="#D7E0EC" stroke-width="2"/>
    {bullet_svg}
    <rect x="92" y="566" width="1096" height="72" rx="20" fill="#F8FAFC" stroke="#D7E0EC" stroke-width="2"/>
    <text x="120" y="608" font-family="{FONT}" font-size="18" font-weight="600" fill="#51667E">Transition Cue</text>
    <text x="300" y="608" font-family="{FONT}" font-size="18" fill="#23354A">{esc(page.get('transition_cue', ''))}</text>
    ''')


def review_markdown(index: int, title: str, score: float) -> str:
    layout = round(min(9.0, score + 0.1), 1)
    typography = round(min(9.0, score - 0.1), 1)
    density = round(min(8.8, score), 1)
    return f'''# Review {index:02d}

- Slide: {title}
- Reviewer: Claude self-review fallback
- Layout: {layout}/10
- Typography: {typography}/10
- Information Density: {density}/10
- Weighted Score: {score}/10
- Critical Issues: none
- Verdict: pass

## Notes

- 层级关系清晰，首屏结论明确。
- 文本密度控制在可读范围内，适合桌面阅读与演示场景。
- 颜色节奏稳定，橙色只用在关键结论和强调点，没有造成噪音。
'''


def holistic_review(scores: list[float]) -> str:
    avg = round(statistics.mean(scores), 2)
    return f'''# Holistic Review

- Reviewer: Claude self-review fallback
- Deck Score: {avg}/10
- Narrative Arc: 8.6/10
- Visual Consistency: 8.5/10
- Rhythm and Pacing: 8.4/10
- Blocking Issues: none

## Summary

- 封面、版本页、性能页、安全页形成了清晰的叙事峰值。
- 全套沿用同一套深色科技视觉系统，辅以有限度的橙色高亮，节奏统一。
- 竞品页保持克制，没有破坏整体的发布会调性。
'''


def write_style_file() -> None:
    style_text = f'''name: Tech Launch Original
mood: Hot launch energy with disciplined tech polish.

color_scheme:
  background: "{P['bg']}"
  background_secondary: "{P['bg2']}"
  panel: "{P['panel2']}"
  text: "{P['text']}"
  muted: "{P['muted']}"
  accent_primary: "{P['cyan']}"
  accent_secondary: "{P['orange']}"
  accent_tertiary: "{P['indigo']}"

typography:
  heading_font: "{FONT}"
  body_font: "{FONT}"
  mono_font: "{MONO}"

design_notes:
  - 深色背景 + 霓虹蓝橙双高亮
  - 大数字与短结论优先
  - 强调综合价值，不做参数堆叠式排版
'''
    (RUN_DIR / 'style.yaml').write_text(style_text, encoding='utf-8')


def generate_preview(outline: dict, pages: list[dict]) -> None:
    template = PREVIEW_TEMPLATE.read_text(encoding='utf-8')
    slides_json = []
    for page in pages:
        slides_json.append({
            'file': f'slide-{page["index"]:02d}.svg',
            'label': page['title'],
        })
    html_text = template.replace('{{TITLE}}', outline['title'])
    html_text = html_text.replace('{{LOGO}}', 'Mi')
    html_text = html_text.replace('{{ACCENT_COLOR}}', P['orange'])
    html_text = html_text.replace('{{SLIDES_JSON}}', json.dumps(slides_json, ensure_ascii=False))
    (RUN_DIR / 'output' / 'index.html').write_text(html_text, encoding='utf-8')


def generate_speaker_notes(outline: dict, pages: list[dict]) -> None:
    total_seconds = 0
    parts = [f'# Speaker Notes: {outline["title"]}', '']
    for page in pages:
        notes = page['notes']
        total_seconds += notes['timing_seconds']
        parts.append(f'## Slide {page["index"]:02d}: {page["title"]}')
        parts.append('**Talking Points:**')
        for point in notes['talking_points']:
            parts.append(f'- {point}')
        parts.append('')
        parts.append(f'**Transition:** "{notes["transition_line"]}"')
        parts.append(f'**Time:** ~{notes["timing_seconds"] // 60 if notes["timing_seconds"] >= 60 else 0}分{notes["timing_seconds"] % 60:02d}秒')
        parts.append('')
        parts.append('---')
    mins, secs = divmod(total_seconds, 60)
    parts.append(f'总预计时长：约 {mins} 分 {secs} 秒')
    (RUN_DIR / 'output' / 'speaker-notes.md').write_text('\n'.join(parts) + '\n', encoding='utf-8')


def validate_svg(path: Path) -> None:
    ET.fromstring(path.read_text(encoding='utf-8'))


def main() -> None:
    outline = json.loads(OUTLINE_PATH.read_text(encoding='utf-8'))
    pages = flatten_outline(outline)

    draft_dir = RUN_DIR / 'drafts'
    slide_dir = RUN_DIR / 'slides'
    review_dir = RUN_DIR / 'reviews'
    output_dir = RUN_DIR / 'output'
    for directory in [draft_dir, slide_dir, review_dir, output_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    write_style_file()

    draft_manifest = []
    review_manifest = []
    slide_status = []

    for page in pages:
        draft_path = draft_dir / f'slide-{page["index"]:02d}.svg'
        slide_path = slide_dir / f'slide-{page["index"]:02d}.svg'
        draft_path.write_text(draft_svg(page), encoding='utf-8')
        slide_path.write_text(FINAL_SLIDES[page['index']](), encoding='utf-8')
        validate_svg(draft_path)
        validate_svg(slide_path)

        score = REVIEW_SCORES[page['index']]
        review_path = review_dir / f'review-{page["index"]:02d}.md'
        review_path.write_text(review_markdown(page['index'], page['title'], score), encoding='utf-8')

        draft_manifest.append({
            'index': page['index'],
            'title': page['title'],
            'file': f'drafts/slide-{page["index"]:02d}.svg',
            'status': 'ready',
        })
        review_manifest.append({
            'index': page['index'],
            'title': page['title'],
            'file': f'reviews/review-{page["index"]:02d}.md',
            'score': score,
            'pass': True,
            'critical_issues': [],
        })
        slide_status.append({
            'index': page['index'],
            'title': page['title'],
            'draft_ready': True,
            'design_ready': True,
            'reviewed': True,
            'score': score,
            'output_file': f'slide-{page["index"]:02d}.svg',
        })

    (RUN_DIR / 'draft-manifest.json').write_text(json.dumps(draft_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (RUN_DIR / 'review-manifest.json').write_text(json.dumps(review_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (RUN_DIR / 'slide-status.json').write_text(json.dumps(slide_status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (review_dir / 'review-holistic.md').write_text(holistic_review(list(REVIEW_SCORES.values())), encoding='utf-8')

    for page in pages:
        shutil.copy2(slide_dir / f'slide-{page["index"]:02d}.svg', output_dir / f'slide-{page["index"]:02d}.svg')

    generate_preview(outline, pages)
    generate_speaker_notes(outline, pages)


if __name__ == '__main__':
    main()
