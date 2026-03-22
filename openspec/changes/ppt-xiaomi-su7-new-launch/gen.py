#!/usr/bin/env python3
PRIMARY = "#1a365d"
ACCENT = "#e67e22"
WHITE = "#ffffff"
TEXT = "#1a202c"
LIGHT_BG = "#f0f4f8"
WIDTH = 1280
HEIGHT = 720

def g(n, content):
    path = f"openspec/changes/ppt-xiaomi-su7-new-launch/slides/slide-{n:02d}.svg"
    with open(path, 'w') as f: f.write(content)
    path2 = f"openspec/changes/ppt-xiaomi-su7-new-launch/drafts/slide-{n:02d}.svg"
    with open(path2, 'w') as f: f.write(content)

g(1, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"><defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:{PRIMARY}"/><stop offset="100%" style="stop-color:#2a4a7f"/></linearGradient></defs><rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg)"/><rect x="0" y="0" width="8" height="{HEIGHT}" fill="{ACCENT}"/><text x="80" y="150" font-family="system-ui" font-size="48" fill="rgba(255,255,255,0.8)">新一代</text><text x="80" y="240" font-family="system-ui" font-size="88" font-weight="800" fill="{WHITE}">小米SU7</text><rect x="80" y="270" width="350" height="6" fill="{ACCENT}" rx="3"/><text x="80" y="350" font-family="system-ui" font-size="36" fill="rgba(255,255,255,0.9)">新一代驾驶者之车</text><text x="80" y="420" font-family="system-ui" font-size="22" fill="rgba(255,255,255,0.7)">更好看 · 更好开 · 更智能 · 更安全</text><text x="80" y="600" font-family="system-ui" font-size="16" fill="rgba(255,255,255,0.5)">2026年3月19日 · 小米春季新品发布会</text></svg>')

g(2, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"><rect width="{WIDTH}" height="{HEIGHT}" fill="{PRIMARY}"/><rect x="0" y="0" width="12" height="{HEIGHT}" fill="{ACCENT}"/><text x="100" y="200" font-family="system-ui" font-size="28" fill="{ACCENT}" letter-spacing="8">OVERVIEW</text><text x="100" y="300" font-family="system-ui" font-size="72" font-weight="700" fill="{WHITE}">车型概览</text><rect x="100" y="330" width="200" height="5" fill="{ACCENT}" rx="2"/><text x="100" y="400" font-family="system-ui" font-size="32" fill="rgba(255,255,255,0.8)">21.99万元起</text><text x="100" y="450" font-family="system-ui" font-size="20" fill="rgba(255,255,255,0.6)">重新定义性价比</text></svg>')

g(3, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">三款配置，任你选择</text>
<rect x="50" y="130" width="360" height="480" rx="16" fill="{LIGHT_BG}"/><rect x="50" y="130" width="360" height="60" fill="{PRIMARY}"/><text x="230" y="172" text-anchor="middle" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">标准版</text><text x="230" y="270" text-anchor="middle" font-family="system-ui" font-size="48" font-weight="800" fill="{PRIMARY}">21.99<tspan font-size="20">万</tspan></text><text x="230" y="310" text-anchor="middle" font-family="system-ui" font-size="18" fill="{ACCENT}">720km续航</text><text x="100" y="380" font-family="system-ui" font-size="14" fill="#666">✓ V6s Plus电机</text><text x="100" y="420" font-family="system-ui" font-size="14" fill="#666">✓ 752V高压平台</text><text x="100" y="460" font-family="system-ui" font-size="14" fill="#666">✓ 激光雷达标配</text><text x="100" y="500" font-family="system-ui" font-size="14" fill="#666">✓ Xiaomi HAD</text>
<rect x="430" y="130" width="360" height="480" rx="16" fill="{LIGHT_BG}"/><rect x="430" y="130" width="360" height="60" fill="{PRIMARY}"/><text x="610" y="172" text-anchor="middle" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">Pro版</text><text x="610" y="270" text-anchor="middle" font-family="system-ui" font-size="48" font-weight="800" fill="{PRIMARY}">24.99<tspan font-size="20">万</tspan></text><text x="610" y="310" text-anchor="middle" font-family="system-ui" font-size="18" fill="{ACCENT}">902km超长续航</text><text x="480" y="380" font-family="system-ui" font-size="14" fill="#666">✓ 100度内最长续航</text><text x="480" y="420" font-family="system-ui" font-size="14" fill="#666">✓ 空悬+CDC</text><text x="480" y="460" font-family="system-ui" font-size="14" fill="#666">✓ 豪华配置</text>
<rect x="810" y="130" width="420" height="480" rx="16" fill="{PRIMARY}"/><rect x="810" y="130" width="420" height="60" fill="{ACCENT}"/><text x="1020" y="172" text-anchor="middle" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">Max版</text><text x="1020" y="270" text-anchor="middle" font-family="system-ui" font-size="48" font-weight="800" fill="{WHITE}">30.39<tspan font-size="20">万</tspan></text><text x="1020" y="310" text-anchor="middle" font-family="system-ui" font-size="18" fill="{ACCENT}">690马力 · 零百3.08秒</text><text x="870" y="380" font-family="system-ui" font-size="14" fill="rgba(255,255,255,0.9)">✓ 897V超快充</text><text x="870" y="420" font-family="system-ui" font-size="14" fill="rgba(255,255,255,0.9)">✓ 508kW澎湃动力</text><text x="870" y="460" font-family="system-ui" font-size="14" fill="rgba(255,255,255,0.9)">✓ 城市NOA</text><text x="870" y="500" font-family="system-ui" font-size="14" fill="{ACCENT}">✓ 终极驾驶机器</text>
</svg>''')

g(4, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">设计美学</text><text x="280" y="58" font-family="system-ui" font-size="18" fill="rgba(255,255,255,0.7)">经得起时间考验</text>
<rect x="50" y="130" width="570" height="300" rx="16" fill="{LIGHT_BG}"/><rect x="50" y="130" width="570" height="60" fill="{PRIMARY}"/><text x="100" y="172" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">外观延续经典</text><text x="100" y="240" font-family="system-ui" font-size="40" font-weight="800" fill="{PRIMARY}">5米车长 · 2米车宽 · 3米轴距</text><text x="100" y="290" font-family="system-ui" font-size="18" fill="#666">✓ 标志性水滴大灯</text><text x="100" y="330" font-family="system-ui" font-size="18" fill="#666">✓ 家族式光环尾灯</text><text x="100" y="370" font-family="system-ui" font-size="18" fill="#666">✓ C级豪华轿车比例</text>
<rect x="650" y="130" width="580" height="300" rx="16" fill="{LIGHT_BG}"/><rect x="650" y="130" width="580" height="60" fill="{PRIMARY}"/><text x="700" y="172" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">细节焕新升级</text><text x="700" y="250" font-family="system-ui" font-size="16" fill="#666">✓ 全新进气格栅设计</text><text x="700" y="290" font-family="system-ui" font-size="16" fill="#666">✓ 内置4D毫米波雷达</text><text x="700" y="330" font-family="system-ui" font-size="16" fill="#666">✓ 远光照射提升至400米</text><text x="700" y="370" font-family="system-ui" font-size="16" fill="#666">✓ 前后摄像头高压清洗</text>
<rect x="50" y="460" width="1180" height="120" rx="12" fill="{PRIMARY}"/><text x="100" y="520" font-family="system-ui" font-size="28" font-weight="700" fill="{WHITE}">延续经典设计语言，细节打磨更精致</text><text x="100" y="555" font-family="system-ui" font-size="16" fill="rgba(255,255,255,0.8)">做经得起时间考验的设计</text>
</svg>''')

g(5, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">九色系列：个性之选</text>
<text x="60" y="140" font-family="system-ui" font-size="18" fill="{ACCENT}" font-weight="600">跑车色系</text>
<rect x="60" y="165" width="340" height="130" rx="12" fill="#4A90D9"/><rect x="60" y="305" width="340" height="55" rx="12" fill="{LIGHT_BG}"/><text x="90" y="345" font-family="system-ui" font-size="20" font-weight="700" fill="{PRIMARY}">卡布里蓝</text>
<rect x="420" y="165" width="200" height="130" rx="12" fill="#C73E3A"/><rect x="420" y="305" width="200" height="55" rx="12" fill="{LIGHT_BG}"/><text x="450" y="345" font-family="system-ui" font-size="20" font-weight="700" fill="{PRIMARY}">赤霞红</text>
<rect x="640" y="165" width="200" height="130" rx="12" fill="#9B59B6"/><rect x="640" y="305" width="200" height="55" rx="12" fill="{LIGHT_BG}"/><text x="670" y="345" font-family="system-ui" font-size="20" font-weight="700" fill="{PRIMARY}">璀璨洋红</text>
<text x="60" y="410" font-family="system-ui" font-size="18" fill="{ACCENT}" font-weight="600">时尚色系</text>
<rect x="60" y="435" width="180" height="100" rx="12" fill="#95A5A6"/><rect x="60" y="545" width="180" height="50" rx="12" fill="{LIGHT_BG}"/><text x="90" y="580" font-family="system-ui" font-size="16" font-weight="700" fill="{PRIMARY}">雅灰</text>
<rect x="260" y="435" width="180" height="100" rx="12" fill="#F5B7B1"/><rect x="260" y="545" width="180" height="50" rx="12" fill="{LIGHT_BG}"/><text x="290" y="580" font-family="system-ui" font-size="16" font-weight="700" fill="{PRIMARY}">流金粉</text>
<rect x="460" y="435" width="180" height="100" rx="12" fill="#BB8FCE"/><rect x="460" y="545" width="180" height="50" rx="12" fill="{LIGHT_BG}"/><text x="490" y="580" font-family="system-ui" font-size="16" font-weight="700" fill="{PRIMARY}">霞光紫</text>
<text x="660" y="410" font-family="system-ui" font-size="18" fill="{ACCENT}" font-weight="600">经典色系</text>
<rect x="660" y="435" width="180" height="100" rx="12" fill="#1D8348"/><rect x="660" y="545" width="180" height="50" rx="12" fill="{LIGHT_BG}"/><text x="690" y="580" font-family="system-ui" font-size="16" font-weight="700" fill="{PRIMARY}">靛石绿</text>
<rect x="860" y="435" width="120" height="100" rx="12" fill="#F5F5F5" stroke="#ddd"/><rect x="860" y="545" width="120" height="50" rx="12" fill="{LIGHT_BG}"/><text x="880" y="580" font-family="system-ui" font-size="16" font-weight="700" fill="{PRIMARY}">珍珠白</text>
<rect x="1000" y="435" width="120" height="100" rx="12" fill="#1C1C1C"/><rect x="1000" y="545" width="120" height="50" rx="12" fill="{LIGHT_BG}"/><text x="1020" y="580" font-family="system-ui" font-size="16" font-weight="700" fill="{PRIMARY}">曜石黑</text>
</svg>''')

g(6, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"><rect width="{WIDTH}" height="{HEIGHT}" fill="{PRIMARY}"/><rect x="0" y="0" width="12" height="{HEIGHT}" fill="{ACCENT}"/><text x="100" y="200" font-family="system-ui" font-size="28" fill="{ACCENT}" letter-spacing="8">INTERIOR</text><text x="100" y="300" font-family="system-ui" font-size="72" font-weight="700" fill="{WHITE}">内饰豪华</text><rect x="100" y="330" width="200" height="5" fill="{ACCENT}" rx="2"/><text x="100" y="400" font-family="system-ui" font-size="32" fill="rgba(255,255,255,0.9)">精致与豪华的全面提升</text></svg>')

g(7, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">内饰设计：重新定义豪华</text>
<rect x="50" y="130" width="560" height="200" rx="16" fill="{LIGHT_BG}"/><rect x="50" y="130" width="560" height="60" fill="{PRIMARY}"/><text x="100" y="172" font-family="system-ui" font-size="22" font-weight="700" fill="{WHITE}">三层环绕氛围灯</text><text x="100" y="240" font-family="system-ui" font-size="16" fill="#666">联动音乐节奏、驾驶模式变化</text><text x="100" y="280" font-family="system-ui" font-size="16" fill="#666">256色氛围灯，支持音乐律动</text>
<rect x="650" y="130" width="580" height="200" rx="16" fill="{LIGHT_BG}"/><rect x="650" y="130" width="580" height="60" fill="{PRIMARY}"/><text x="700" y="172" font-family="system-ui" font-size="22" font-weight="700" fill="{WHITE}">Nappa真皮方向盘</text><text x="700" y="240" font-family="system-ui" font-size="16" fill="#666">运动握圈真皮包覆</text><text x="700" y="280" font-family="system-ui" font-size="16" fill="#666">新增镀铬装饰点缀</text>
<rect x="50" y="360" width="560" height="200" rx="16" fill="{LIGHT_BG}"/><rect x="50" y="360" width="560" height="60" fill="{PRIMARY}"/><text x="100" y="402" font-family="system-ui" font-size="22" font-weight="700" fill="{WHITE}">100%软包覆</text><text x="100" y="470" font-family="system-ui" font-size="16" fill="#666">高频接触内饰面全面软包</text><text x="100" y="510" font-family="system-ui" font-size="16" fill="#666">精致度极大提升</text>
<rect x="650" y="360" width="580" height="200" rx="16" fill="{LIGHT_BG}"/><rect x="650" y="360" width="580" height="60" fill="{PRIMARY}"/><text x="700" y="402" font-family="system-ui" font-size="22" font-weight="700" fill="{WHITE}">电动前备箱</text><text x="700" y="470" font-family="system-ui" font-size="16" fill="#666">105L超大容量</text><text x="700" y="510" font-family="system-ui" font-size="16" fill="#666">支持8种开合方式</text>
</svg>''')

g(8, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"><rect width="{WIDTH}" height="{HEIGHT}" fill="{PRIMARY}"/><rect x="0" y="0" width="12" height="{HEIGHT}" fill="{ACCENT}"/><text x="100" y="200" font-family="system-ui" font-size="28" fill="{ACCENT}" letter-spacing="8">SAFETY</text><text x="100" y="300" font-family="system-ui" font-size="72" font-weight="700" fill="{WHITE}">安全升级</text><rect x="100" y="330" width="200" height="5" fill="{ACCENT}" rx="2"/><text x="100" y="400" font-family="system-ui" font-size="32" fill="rgba(255,255,255,0.9)">不计成本的安全投入</text><text x="100" y="450" font-family="system-ui" font-size="20" fill="rgba(255,255,255,0.6)">全系标配12项安全配置</text></svg>')

g(9, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">安全：全系标配12项</text>
<rect x="50" y="130" width="360" height="130" rx="12" fill="{LIGHT_BG}"/><rect x="50" y="130" width="360" height="50" fill="{PRIMARY}"/><text x="80" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">2200MPa超强钢防滚架</text><text x="80" y="220" font-family="system-ui" font-size="14" fill="#666">A柱至C柱全覆盖</text>
<rect x="430" y="130" width="360" height="130" rx="12" fill="{LIGHT_BG}"/><rect x="430" y="130" width="360" height="50" fill="{PRIMARY}"/><text x="460" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">9个安全气囊</text><text x="460" y="220" font-family="system-ui" font-size="14" fill="#666">新增后排侧气囊</text>
<rect x="810" y="130" width="420" height="130" rx="12" fill="{LIGHT_BG}"/><rect x="810" y="130" width="420" height="50" fill="{PRIMARY}"/><text x="840" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">三重冗余门把手</text><text x="840" y="220" font-family="system-ui" font-size="14" fill="#666">100%符合2027年新国标</text>
<rect x="50" y="290" width="360" height="130" rx="12" fill="{LIGHT_BG}"/><rect x="50" y="290" width="360" height="50" fill="{PRIMARY}"/><text x="80" y="325" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">1500MPa电池防护横梁</text><text x="80" y="380" font-family="system-ui" font-size="14" fill="#666">耐穿刺性能提升13倍</text>
<rect x="430" y="290" width="360" height="130" rx="12" fill="{LIGHT_BG}"/><rect x="430" y="290" width="360" height="50" fill="{PRIMARY}"/><text x="460" y="325" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">四门防撞梁</text><text x="460" y="380" font-family="system-ui" font-size="14" fill="#666">全方位被动保护</text>
<rect x="810" y="290" width="420" height="130" rx="12" fill="{LIGHT_BG}"/><rect x="810" y="290" width="420" height="50" fill="{PRIMARY}"/><text x="840" y="325" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">高强防护涂层</text><text x="840" y="380" font-family="system-ui" font-size="14" fill="#666">耐刮擦提升10倍</text>
<rect x="50" y="450" width="1180" height="120" rx="12" fill="{PRIMARY}"/><text x="100" y="505" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">安全是造车的底线</text><text x="100" y="540" font-family="system-ui" font-size="16" fill="rgba(255,255,255,0.8)">碰撞后车门仍可从车内或车外手动解锁</text>
</svg>''')

g(10, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"><rect width="{WIDTH}" height="{HEIGHT}" fill="{PRIMARY}"/><rect x="0" y="0" width="12" height="{HEIGHT}" fill="{ACCENT}"/><text x="100" y="200" font-family="system-ui" font-size="28" fill="{ACCENT}" letter-spacing="8">INTELLIGENCE</text><text x="100" y="300" font-family="system-ui" font-size="72" font-weight="700" fill="{WHITE}">智能科技</text><rect x="100" y="330" width="200" height="5" fill="{ACCENT}" rx="2"/><text x="100" y="400" font-family="system-ui" font-size="32" fill="rgba(255,255,255,0.9)">全系标配，入门即高配</text></svg>')

g(11, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">智能驾驶：全系标配激光雷达</text>
<rect x="50" y="130" width="500" height="300" rx="16" fill="{PRIMARY}"/><text x="300" y="240" text-anchor="middle" font-family="system-ui" font-size="100" font-weight="900" fill="{ACCENT}">700</text><text x="300" y="320" text-anchor="middle" font-family="system-ui" font-size="32" fill="{WHITE}">TOPS</text><text x="300" y="370" text-anchor="middle" font-family="system-ui" font-size="18" fill="rgba(255,255,255,0.7)">英伟达Drive Thor芯片</text>
<rect x="580" y="130" width="340" height="140" rx="12" fill="{LIGHT_BG}"/><text x="620" y="180" font-family="system-ui" font-size="16" fill="#666">✓ 全系激光雷达</text><text x="620" y="210" font-family="system-ui" font-size="16" fill="#666">✓ 全系4D毫米波雷达</text><text x="620" y="240" font-family="system-ui" font-size="16" fill="#666">✓ 全系11颗高清摄像头</text><text x="620" y="270" font-family="system-ui" font-size="16" fill="#666">✓ Xiaomi HAD端到端智驾</text>
<rect x="950" y="130" width="280" height="300" rx="12" fill="{LIGHT_BG}"/><text x="1090" y="200" text-anchor="middle" font-family="system-ui" font-size="18" fill="{PRIMARY}">Xiaomi XLA认知大模型</text><text x="1090" y="250" text-anchor="middle" font-family="system-ui" font-size="14" fill="#666">多模态空间感知</text><text x="1090" y="290" text-anchor="middle" font-family="system-ui" font-size="14" fill="#666">增强推理能力</text><text x="1090" y="350" text-anchor="middle" font-family="system-ui" font-size="16" fill="{ACCENT}">Max版城市NOA</text>
<rect x="580" y="300" width="650" height="130" rx="12" fill="{LIGHT_BG}"/><text x="620" y="350" font-family="system-ui" font-size="16" fill="#666">Xiaomi XLA认知大模型</text><text x="620" y="390" font-family="system-ui" font-size="14" fill="#666">融入多模态数据，提升通用理解能力</text><rect x="50" y="460" width="1180" height="120" rx="12" fill="{ACCENT}"/><text x="100" y="515" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">智能驾驶全系标配，不再是高配专属</text>
</svg>''')

g(12, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">三电升级：效率与性能</text>
<rect x="50" y="130" width="280" height="260" rx="12" fill="{LIGHT_BG}"/><rect x="50" y="130" width="280" height="50" fill="{PRIMARY}"/><text x="80" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">V6s Plus电机</text><text x="80" y="230" font-family="system-ui" font-size="14" fill="#666">最高转速22000rpm</text><text x="80" y="260" font-family="system-ui" font-size="14" fill="#666">标准版235kW</text><text x="80" y="290" font-family="system-ui" font-size="14" fill="#666">Max版508kW</text><text x="80" y="320" font-family="system-ui" font-size="14" fill="{ACCENT}">690马力</text>
<rect x="350" y="130" width="280" height="260" rx="12" fill="{LIGHT_BG}"/><rect x="350" y="130" width="280" height="50" fill="{PRIMARY}"/><text x="380" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">超快充平台</text><text x="380" y="230" font-family="system-ui" font-size="14" fill="#666">标准版/Pro: 752V</text><text x="380" y="260" font-family="system-ui" font-size="14" fill="#666">Max版: 897V</text><text x="380" y="290" font-family="system-ui" font-size="14" fill="{ACCENT}">15分钟补能670km</text>
<rect x="650" y="130" width="280" height="260" rx="12" fill="{LIGHT_BG}"/><rect x="650" y="130" width="280" height="50" fill="{PRIMARY}"/><text x="680" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">超长续航</text><text x="680" y="230" font-family="system-ui" font-size="14" fill="#666">标准版: 720km</text><text x="680" y="260" font-family="system-ui" font-size="14" fill="#666">Pro版: 902km</text><text x="680" y="290" font-family="system-ui" font-size="14" fill="#666">Max版: 835km</text><text x="680" y="320" font-family="system-ui" font-size="14" fill="{ACCENT}">100度内最长</text>
<rect x="950" y="130" width="280" height="260" rx="12" fill="{PRIMARY}"/><rect x="950" y="130" width="280" height="50" fill="{ACCENT}"/><text x="980" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">澎湃动力</text><text x="980" y="230" font-family="system-ui" font-size="14" fill="rgba(255,255,255,0.8)">Max版零百: 3.08秒</text><text x="980" y="260" font-family="system-ui" font-size="14" fill="rgba(255,255,255,0.8)">最高车速: 265km/h</text><text x="980" y="290" font-family="system-ui" font-size="14" fill="rgba(255,255,255,0.8)">碳化硅高压平台</text><text x="980" y="320" font-family="system-ui" font-size="14" fill="{ACCENT}">5.2C充电倍率</text>
<rect x="50" y="420" width="1180" height="120" rx="12" fill="{LIGHT_BG}" stroke="{PRIMARY}" stroke-width="2"/><text x="100" y="470" font-family="system-ui" font-size="22" font-weight="700" fill="{PRIMARY}">800V架构全系标配</text><text x="500" y="470" font-family="system-ui" font-size="22" fill="#666">|</text><text x="550" y="470" font-family="system-ui" font-size="22" font-weight="700" fill="{PRIMARY}">超长续航</text><text x="750" y="470" font-family="system-ui" font-size="22" fill="#666">|</text><text x="800" y="470" font-family="system-ui" font-size="22" font-weight="700" fill="{PRIMARY}">超快补能</text>
</svg>''')

g(13, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{WHITE}"/>
<rect x="0" y="0" width="{WIDTH}" height="90" fill="{PRIMARY}"/>
<rect x="0" y="0" width="6" height="90" fill="{ACCENT}"/>
<text x="40" y="58" font-family="system-ui" font-size="32" font-weight="700" fill="{WHITE}">底盘升级：蛟龙出击</text>
<rect x="50" y="130" width="360" height="140" rx="12" fill="{LIGHT_BG}"/><rect x="50" y="130" width="360" height="50" fill="{PRIMARY}"/><text x="80" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">前双叉臂+后五连杆</text><text x="80" y="220" font-family="system-ui" font-size="14" fill="#666">运动与舒适的完美平衡</text>
<rect x="430" y="130" width="360" height="140" rx="12" fill="{LIGHT_BG}"/><rect x="430" y="130" width="360" height="50" fill="{PRIMARY}"/><text x="460" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">闭式双腔空悬(Pro/Max)</text><text x="460" y="220" font-family="system-ui" font-size="14" fill="#666">软硬调节区间更大</text>
<rect x="810" y="130" width="420" height="140" rx="12" fill="{LIGHT_BG}"/><rect x="810" y="130" width="420" height="50" fill="{PRIMARY}"/><text x="840" y="165" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">CDC自适应减振(Pro/Max)</text><text x="840" y="220" font-family="system-ui" font-size="14" fill="#666">实时调节阻尼</text>
<rect x="50" y="300" width="560" height="140" rx="12" fill="{LIGHT_BG}"/><rect x="50" y="300" width="560" height="50" fill="{PRIMARY}"/><text x="80" y="335" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">前四活塞固定卡钳</text><text x="80" y="400" font-family="system-ui" font-size="14" fill="#666">全系标配 · 制动性能出色</text>
<rect x="630" y="300" width="600" height="140" rx="12" fill="{LIGHT_BG}"/><rect x="630" y="300" width="600" height="50" fill="{PRIMARY}"/><text x="660" y="335" font-family="system-ui" font-size="16" font-weight="700" fill="{WHITE}">前245/后265宽胎</text><text x="660" y="400" font-family="system-ui" font-size="14" fill="#666">全系标配 · 提升操控稳定性</text>
<rect x="50" y="480" width="1180" height="120" rx="12" fill="{PRIMARY}"/><text x="100" y="535" font-family="system-ui" font-size="24" font-weight="700" fill="{WHITE}">自研蛟龙底盘 · 兼顾舒适与运动</text><text x="100" y="570" font-family="system-ui" font-size="16" fill="rgba(255,255,255,0.8)">软硬深度融合的高性能智能底盘系统，专为驾驶者打造</text>
</svg>''')

g(14, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs><linearGradient id="ebg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:{PRIMARY}"/><stop offset="100%" style="stop-color:#2a4a7f"/></linearGradient></defs>
<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#ebg)"/>
<rect x="0" y="0" width="10" height="{HEIGHT}" fill="{ACCENT}"/>
<text x="80" y="150" font-family="system-ui" font-size="60" font-weight="700" fill="{WHITE}">新一代小米SU7</text>
<rect x="80" y="180" width="300" height="5" fill="{ACCENT}" rx="2"/>
<rect x="80" y="250" width="450" height="140" rx="16" fill="rgba(230,126,34,0.2)" stroke="{ACCENT}" stroke-width="3"/>
<text x="130" y="320" font-family="system-ui" font-size="18" fill="rgba(255,255,255,0.7)">官方指导价</text>
<text x="130" y="370" font-family="system-ui" font-size="64" font-weight="800" fill="{ACCENT}">21.99<tspan font-size="28">万</tspan></text>
<text x="80" y="450" font-family="system-ui" font-size="28" fill="{WHITE}">即刻下定，享首销权益</text>
<rect x="80" y="510" width="280" height="60" rx="30" fill="{ACCENT}"/>
<text x="220" y="548" text-anchor="middle" font-family="system-ui" font-size="22" font-weight="700" fill="{WHITE}">立即下定</text>
<rect x="400" y="510" width="420" height="60" rx="12" fill="rgba(255,255,255,0.1)"/>
<text x="430" y="545" font-family="system-ui" font-size="14" fill="rgba(255,255,255,0.8)">标准版/Pro版赠4.4万权益</text>
<text x="700" y="545" font-family="system-ui" font-size="14" fill="{ACCENT}">|</text>
<text x="730" y="545" font-family="system-ui" font-size="14" fill="{ACCENT}">Max版赠6.9万权益</text>
<text x="80" y="630" font-family="system-ui" font-size="18" fill="rgba(255,255,255,0.6)">小米SU7 · 新一代驾驶者之车</text>
</svg>''')

print("Generated 14 slides for New Generation Xiaomi SU7")
