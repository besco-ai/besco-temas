"""Pack de temas animados da Besco: cenas em vetor (não pixel), todas com o logo da Besco pulsando.

Cada função devolve um dicionário com id, título, janela, alt, svg e a tinta do vidro.
Regras do app que valem aqui: SVG puro, sem imagem nem fonte embutida, `url()` e `href` só para `#id`
local, id sempre com hífen, nada de barra invertida, até 131.072 caracteres, movimento lento.
"""

import json
import math
import random
from pathlib import Path

AQUI = Path(__file__).resolve().parent
W, H = 1600, 1000
LAV = '#b6b9ff'
_L = json.loads((AQUI / 'besco-logo.json').read_text())
CX0, CY0, LW, LH = 158, 197, 584, 168


def _logo_defs():
    caminhos = [_L['b'], _L['pontoDoMeio'], *_L['letras']]
    cheio = ''.join(f'<path d="{c}"/>' for c in caminhos) + ''.join(
        f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in _L['pontos'])
    linha = ''.join(f'<path pathLength="100" d="{c}"/>' for c in caminhos) + ''.join(
        f'<circle pathLength="100" cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in _L['pontos'])
    return cheio, linha


LOGO_CHEIO, LOGO_LINHA = _logo_defs()


def logo(x, y, largura, cor, classe='', extra='', linha=False, ref='l-besco'):
    """Logo com o canto de cima à esquerda em (x, y). `classe` anima o grupo em volta do próprio centro."""
    s = largura / LW
    alvo = 'l-linha' if linha else ref
    dentro = f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f}) translate(-{CX0} -{CY0})">' \
             f'<use href="#{alvo}" fill="{cor}" {extra}/></g>'
    return f'<g class="{classe}">{dentro}</g>' if classe else dentro


def altura(largura):
    return largura * LH / LW


def svg(corpo, css='', defs='', linha=False):
    logo_def = f'<g id="l-besco">{LOGO_CHEIO}</g>'
    if linha:
        logo_def += f'<g id="l-linha">{LOGO_LINHA}</g>'
    base_css = ('.gira,.pulsa,.flutua,.respira{transform-box:fill-box;transform-origin:center}'
                '.pulsa{animation:pulsa 3.4s ease-in-out infinite}'
                '@keyframes pulsa{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}'
                '.brilha{animation:brilha 3.4s ease-in-out infinite}'
                '@keyframes brilha{0%,100%{opacity:.35}50%{opacity:.95}}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
            f'<defs>{logo_def}<filter id="f-brilho" x="-40%" y="-80%" width="180%" height="260%">'
            f'<feGaussianBlur stdDeviation="22"/></filter>{defs}</defs>'
            f'<style>{base_css}{css}</style>{corpo}</svg>')


def logo_pulsando(x, y, largura, cor, brilho=None, extra_brilho=''):
    """O logo com um brilho borrado atrás, os dois pulsando juntos."""
    b = brilho or cor
    return (f'<g class="pulsa">{logo(x, y, largura, b, classe="brilha", extra=f"filter=\"url(#f-brilho)\" {extra_brilho}")}'
            f'{logo(x, y, largura, cor)}</g>')


def grad_linear(ident, cores, x2=0, y2=1):
    paradas = ''.join(f'<stop offset="{i / (len(cores) - 1):.3f}" stop-color="{c}"/>' for i, c in enumerate(cores))
    return f'<linearGradient id="{ident}" x1="0" y1="0" x2="{x2}" y2="{y2}">{paradas}</linearGradient>'


def grad_radial(ident, cores, opacidades=None):
    op = opacidades or [1] * len(cores)
    paradas = ''.join(f'<stop offset="{i / (len(cores) - 1):.3f}" stop-color="{c}" stop-opacity="{o}"/>'
                      for i, (c, o) in enumerate(zip(cores, op)))
    return f'<radialGradient id="{ident}">{paradas}</radialGradient>'


def estrelas(n, semente, y_max=H, classes=3, r=(0.8, 2.2), cores=('#ffffff', '#c9d4ff', '#ffe9b0')):
    rnd = random.Random(semente)
    grupos = [[] for _ in range(classes)]
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, y_max)
        grupos[rnd.randrange(classes)].append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(*r):.1f}" fill="{rnd.choice(cores)}"/>')
    corpo = ''.join(f'<g class="pisca{i}">{"".join(g)}</g>' for i, g in enumerate(grupos))
    css = ''.join(f'.pisca{i}{{animation:pisca 4s ease-in-out {-i * 1.3:.1f}s infinite}}' for i in range(classes))
    css += '@keyframes pisca{0%,100%{opacity:1}50%{opacity:.35}}'
    return corpo, css


def onda(y, amp, comp, fase=0, largura=W * 2, fundo=H):
    pts = [f'M0 {fundo}', f'L0 {y + amp * math.sin(fase):.0f}']
    passo = comp / 8
    x = 0
    while x <= largura:
        pts.append(f'L{x:.0f} {y + amp * math.sin(x / comp * 2 * math.pi + fase):.0f}')
        x += passo
    pts.append(f'L{largura} {fundo}Z')
    return ''.join(pts)


def anda_x(nome, dur, dist=-W, atraso=0):
    return (f'.{nome}{{animation:{nome} {dur}s linear {-atraso}s infinite}}'
            f'@keyframes {nome}{{0%{{transform:translateX(0)}}100%{{transform:translateX({dist}px)}}}}')


def vai_e_volta(nome, dur, dx=0, dy=0, atraso=0, extra=''):
    return (f'.{nome}{{animation:{nome} {dur}s ease-in-out {-atraso}s infinite alternate}}'
            f'@keyframes {nome}{{0%{{transform:translate(0px,0px){extra}}}100%{{transform:translate({dx}px,{dy}px)}}}}')


def tema(ident, titulo, janela, alt, conteudo, tinta):
    return {'id': ident, 'titulo': titulo, 'janela': janela, 'alt': alt, 'svg': conteudo, 'tinta': tinta}


# ---------------------------------------------------------------------- céu e espaço

def aurora():
    est, css_e = estrelas(140, 1, 600)
    faixas = ''
    css = css_e
    for i, (y, cores, dur) in enumerate(((260, ('#3dffb0', '#7d7bff'), 22), (340, ('#7d7bff', '#ff7ad9'), 28),
                                         (220, ('#58f0ff', '#b6b9ff'), 34))):
        faixas += (f'<g class="au{i}"><path d="{onda(y, 60, 700 + i * 120, i, W * 2, y + 260)}" '
                   f'fill="url(#g-au{i})" opacity=".55" filter="url(#f-borra)"/></g>')
        css += vai_e_volta(f'au{i}', dur, dx=-500, dy=20 * (i - 1))
    defs = ''.join(grad_linear(f'g-au{i}', [c[0], c[1], '#0b1030'], 0, 1)
                   for i, c in enumerate((('#3dffb0', '#7d7bff'), ('#7d7bff', '#ff7ad9'), ('#58f0ff', '#b6b9ff'))))
    defs += grad_linear('g-ceu', ['#03040f', '#0a1030', '#1a1f4f']) + \
        '<filter id="f-borra" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>'
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-ceu)"/>{est}{faixas}'
             f'<path d="{onda(820, 40, 900, 1)}" fill="#1c2350"/><path d="{onda(880, 30, 600, 3)}" fill="#e8ecff"/>'
             f'<path d="{onda(920, 24, 500, 5)}" fill="#cdd3f5"/>'
             + logo_pulsando(960, 120, 520, '#eef0ff', '#7dffd0'))
    return tema('besco-aurora', 'Besco Aurora', 'dark', 'Aurora boreal sobre colinas de neve com o logo da Besco',
                svg(corpo, css, defs), '#0a1030')


def galaxia():
    rnd = random.Random(2)
    est, css_e = estrelas(200, 2)
    braco = []
    for k in range(700):
        a = k * 0.045
        r = 8 + a * 34
        for lado in (0, math.pi):
            x = 420 + math.cos(a + lado) * r + rnd.gauss(0, 10)
            y = 480 + math.sin(a + lado) * r * 0.45 + rnd.gauss(0, 6)
            braco.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(.6, 2):.1f}" '
                         f'fill="{rnd.choice(["#ffffff", "#c8c6ff", "#ff9ee6", "#9ed8ff"])}" opacity="{rnd.uniform(.4, 1):.2f}"/>')
    defs = grad_radial('g-nucleo', ['#ffffff', '#d7c8ff', '#6a4fd8', '#120a35'], [1, .9, .4, 0]) + \
        grad_linear('g-fundo', ['#05031a', '#0e0830', '#1c0f45'])
    css = css_e + '.gal{animation:gal 140s linear infinite;transform-box:fill-box;transform-origin:center}' \
                  '@keyframes gal{to{transform:rotate(360deg)}}'
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-fundo)"/>{est}'
             f'<g transform="translate(420 480) scale(1 .5) translate(-420 -480)"><g class="gal">'
             f'<circle cx="420" cy="480" r="430" fill="none"/>{"".join(braco)}</g></g>'
             f'<ellipse cx="420" cy="480" rx="160" ry="90" fill="url(#g-nucleo)"/>'
             + logo_pulsando(980, 150, 500, '#f2ecff', '#a98bff'))
    return tema('besco-galaxia', 'Besco Galáxia', 'dark', 'Galáxia em espiral girando devagar ao lado do logo da Besco',
                svg(corpo, css, defs), '#0e0830')


def orbita():
    est, css_e = estrelas(160, 3)
    cx, cy = 1180, 420
    orbitas = ''
    css = css_e
    for i, (r, dur, cor, tam) in enumerate(((330, 30, '#ff9ee6', 16), (420, 46, '#7dffd0', 11), (520, 70, '#ffd27a', 22),
                                            (250, 20, LAV, 8))):
        orbitas += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LAV}" stroke-opacity=".18" stroke-width="2"/>'
                    f'<g class="or{i}"><circle cx="{cx}" cy="{cy}" r="{r}" fill="none"/>'
                    f'<circle cx="{cx + r}" cy="{cy}" r="{tam}" fill="{cor}"/></g>')
        css += f'.or{i}{{transform-box:fill-box;transform-origin:center;animation:or {dur}s linear {-i * 7}s infinite}}'
    css += '@keyframes or{to{transform:rotate(360deg)}}'
    defs = grad_radial('g-sol', ['#3a2f8f', '#1a1450', '#0a0820'], [.9, .5, 0])
    corpo = (f'<rect width="{W}" height="{H}" fill="#070616"/>{est}'
             f'<circle cx="{cx}" cy="{cy}" r="320" fill="url(#g-sol)"/>{orbitas}'
             + logo_pulsando(cx - 210, cy - 60, 420, '#ffffff', LAV))
    return tema('besco-orbita', 'Besco Órbita', 'dark', 'Planetas girando em volta do logo da Besco',
                svg(corpo, css, defs), '#0a0820')


def foguete():
    est, css_e = estrelas(220, 4)
    cx, cy = 1180, 430
    foguete_svg = ('<g transform="rotate(90)"><path d="M0 -46 C18 -30 18 10 12 26 L-12 26 C-18 10 -18 -30 0 -46Z" fill="#f4f2ff"/>'
                   '<circle cx="0" cy="-10" r="8" fill="#7d7bff"/><path d="M-12 14 L-24 32 L-12 28Z" fill="#ff7ad9"/>'
                   '<path d="M12 14 L24 32 L12 28Z" fill="#ff7ad9"/><path class="fogo" d="M-8 28 Q0 60 8 28Z" fill="#ffb347"/></g>')
    css = css_e + ('.rota{transform-box:fill-box;transform-origin:center;animation:rota 24s linear infinite}'
                   '@keyframes rota{to{transform:rotate(360deg)}}'
                   '.fogo{transform-box:fill-box;transform-origin:top;animation:fogo .6s ease-in-out infinite alternate}'
                   '@keyframes fogo{to{transform:scaleY(.6)}}'
                   + anda_x('fundo1', 90, -W) + anda_x('fundo2', 150, -W))
    planetas = ('<circle cx="260" cy="760" r="120" fill="#5b3fd1"/><path d="M140 760 a120 40 0 0 0 240 0" fill="none" '
                'stroke="#ffd27a" stroke-width="10" opacity=".8"/><circle cx="520" cy="200" r="40" fill="#ff7ad9" opacity=".8"/>')
    corpo = (f'<rect width="{W}" height="{H}" fill="#06051a"/><g class="fundo1">{est}<g transform="translate({W} 0)">{est}</g></g>'
             f'{planetas}<circle cx="{cx}" cy="{cy}" r="250" fill="#141040"/>'
             f'<g class="rota"><circle cx="{cx}" cy="{cy}" r="330" fill="none"/>'
             f'<g transform="translate({cx + 330} {cy})">{foguete_svg}</g></g>'
             + logo_pulsando(cx - 200, cy - 58, 400, '#ffffff', '#7d7bff'))
    return tema('besco-foguete', 'Besco Foguete', 'dark', 'Um foguete dando voltas no planeta Besco',
                svg(corpo, css), '#0a0820')


def constelacao():
    from PIL import Image
    import numpy as np
    im = Image.open(AQUI / 'besco-logo.png').convert('RGBA')
    largura = 64
    alt = round(im.height * largura / im.width)
    m = np.array(im.resize((largura, alt), Image.LANCZOS))[:, :, 3] > 120
    rnd = random.Random(5)
    escala, ox, oy = 10, 860, 110
    pts = [(ox + x * escala, oy + y * escala) for y, x in np.argwhere(m) if rnd.random() < 0.4]
    linhas = []
    for i, (x, y) in enumerate(pts):
        viz = sorted(pts, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)[1:3]
        for vx, vy in viz:
            if (vx - x) ** 2 + (vy - y) ** 2 < 32 ** 2:
                linhas.append(f'M{x} {y}L{vx} {vy}')
    est, css_e = estrelas(180, 6)
    nos = ''.join(f'<circle class="pisca{i % 3}" cx="{x}" cy="{y}" r="{rnd.uniform(2.5, 4.5):.1f}" fill="#ffffff"/>'
                  for i, (x, y) in enumerate(pts))
    css = css_e + '.traco{stroke-dasharray:6 10;animation:traco 6s linear infinite}@keyframes traco{to{stroke-dashoffset:-160}}'
    defs = grad_linear('g-noite', ['#020417', '#0b0f35', '#1b1650'])
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-noite)"/>{est}'
             f'<g class="pulsa">{logo(ox, oy, largura * escala, LAV, classe="brilha", extra="filter=\"url(#f-brilho)\" opacity=\".5\"")}'
             f'<path class="traco" d="{"".join(linhas)}" stroke="{LAV}" stroke-opacity=".6" stroke-width="1.5" fill="none"/>{nos}</g>'
             f'<path d="{onda(900, 30, 700, 2)}" fill="#090b26"/>')
    return tema('besco-constelacao', 'Besco Constelação', 'dark', 'O logo da Besco desenhado com estrelas ligadas',
                svg(corpo, css, defs), '#0b0f35')


# ---------------------------------------------------------------------- neon e retrô

def neon():
    defs = ('<pattern id="p-tijolo" width="120" height="60" patternUnits="userSpaceOnUse">'
            '<rect width="120" height="60" fill="#2a1622"/><path d="M0 0H120M0 30H120M0 0V30M60 30V60" '
            'stroke="#1a0c14" stroke-width="4"/></pattern>'
            + grad_radial('g-luz', ['#ff5fd2', '#2a1622'], [.35, 0]))
    css = ('.falha{animation:falha 7s steps(1) infinite}'
           '@keyframes falha{0%,91%,93%,95%,100%{opacity:1}92%,94%{opacity:.25}}')
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#p-tijolo)"/>'
             f'<ellipse cx="1220" cy="260" rx="520" ry="260" fill="url(#g-luz)" class="brilha"/>'
             f'<g class="falha">{logo_pulsando(960, 180, 520, "#ffe6fb", "#ff5fd2")}</g>'
             f'<rect x="0" y="880" width="{W}" height="120" fill="#120810"/>')
    return tema('besco-neon', 'Besco Neon', 'dark', 'Letreiro de neon rosa da Besco numa parede de tijolos',
                svg(corpo, css, defs), '#1a0c14')


def synthwave():
    defs = (grad_linear('g-ceu', ['#12002e', '#3c0a5e', '#a8235f', '#ff7b4a'])
            + grad_linear('g-sol', ['#ffe066', '#ff8a4a', '#ff3f8e'])
            + f'<clipPath id="c-chao"><rect x="0" y="620" width="{W}" height="380"/></clipPath>')
    sol = '<circle cx="1180" cy="470" r="230" fill="url(#g-sol)"/>' + ''.join(
        f'<rect x="900" y="{470 + k * 34}" width="560" height="{4 + k * 2.4:.0f}" fill="#7a1a62"/>' for k in range(1, 7))
    horiz = ''.join(f'<path d="M0 {620 + k * 40}H{W}" stroke="#ff2fa0" stroke-width="3"/>' for k in range(0, 11))
    vert = ''.join(f'<path d="M{800 + j * 6} 620L{800 + j * 120} 1000" stroke="#ff2fa0" stroke-width="3"/>'
                   for j in range(-14, 15))
    montanha = 'M0 620L180 470L330 560L470 430L640 620Z M980 620L1130 520L1270 590L1430 480L1600 600V620Z'
    css = '.grade{animation:grade 1.6s linear infinite}@keyframes grade{to{transform:translateY(40px)}}'
    corpo = (f'<rect width="{W}" height="620" fill="url(#g-ceu)"/>{estrelas(80, 7, 300)[0]}{sol}'
             f'<path d="{montanha}" fill="#24083f" stroke="#ff4fa3" stroke-width="3"/>'
             f'<rect y="620" width="{W}" height="380" fill="#0a0218"/>'
             f'<g clip-path="url(#c-chao)"><g class="grade">{horiz}</g>{vert}</g>'
             + logo_pulsando(930, 120, 500, '#ffffff', '#ff4fd8'))
    return tema('besco-synthwave', 'Besco Synthwave', 'dark', 'Pôr do sol neon com grade correndo e o logo da Besco',
                svg(corpo, css + estrelas(80, 7, 300)[1], defs), '#1a0830')


def vaporwave():
    defs = (grad_linear('g-ceu', ['#1b0f3a', '#5b1f6e', '#ff6ec7', '#ffb3e6'])
            + grad_linear('g-sol', ['#fff27a', '#ff9ee6', '#a45bff']))
    css = ('.rgb1{animation:rgb1 5s ease-in-out infinite}.rgb2{animation:rgb2 5s ease-in-out infinite}'
           '@keyframes rgb1{0%,100%{transform:translate(0,0)}50%{transform:translate(-8px,3px)}}'
           '@keyframes rgb2{0%,100%{transform:translate(0,0)}50%{transform:translate(8px,-3px)}}'
           + vai_e_volta('palma', 6, dx=0, dy=0, extra=' rotate(0deg)'))
    palma = ''.join(f'<path d="M{x} 1000 Q{x + 20} 820 {x + 10} 700" stroke="#2a0b3f" stroke-width="18" fill="none"/>'
                    + ''.join(f'<path d="M{x + 10} 700 q{dx} {dy} {dx * 2} {dy * 2.6}" stroke="#2a0b3f" stroke-width="14" '
                              f'fill="none" stroke-linecap="round"/>' for dx, dy in ((-60, -10), (60, -10), (-50, 20), (50, 20), (0, -40)))
                    for x in (90, 1460))
    grade = ''.join(f'<path d="M0 {640 + k * 36}H{W}" stroke="#4ff0ff" stroke-opacity=".7" stroke-width="2"/>' for k in range(11))
    grade += ''.join(f'<path d="M{800 + j * 8} 640L{800 + j * 110} 1000" stroke="#4ff0ff" stroke-opacity=".7" stroke-width="2"/>'
                     for j in range(-15, 16))
    x, y, lw = 920, 170, 520
    corpo = (f'<rect width="{W}" height="640" fill="url(#g-ceu)"/>'
             f'<circle cx="1180" cy="520" r="200" fill="url(#g-sol)"/>'
             + ''.join(f'<rect x="960" y="{540 + k * 26}" width="440" height="{5 + k * 3}" fill="#ff6ec7"/>' for k in range(5))
             + f'<rect y="640" width="{W}" height="360" fill="#1b0f3a"/>{grade}{palma}'
             f'<g class="pulsa"><g class="rgb1">{logo(x, y, lw, "#4ff0ff", extra="opacity=\".8\"")}</g>'
             f'<g class="rgb2">{logo(x, y, lw, "#ff4fd8", extra="opacity=\".8\"")}</g>{logo(x, y, lw, "#ffffff")}</g>')
    return tema('besco-vaporwave', 'Besco Vaporwave', 'dark', 'Estética vaporwave rosa e ciano com o logo da Besco tremendo em cores',
                svg(corpo, css, defs), '#2a0b3f')


def chuva_de_codigo():
    rnd = random.Random(8)
    colunas = ''
    css = ''
    for i in range(46):
        x = i * 35 + rnd.uniform(-6, 6)
        blocos = ''.join(f'<rect x="{x:.0f}" y="{j * 26}" width="14" height="{rnd.choice([10, 14, 18])}" rx="3" '
                         f'fill="{LAV}" opacity="{max(.08, 1 - j / 22):.2f}"/>' for j in range(22))
        dur = rnd.uniform(9, 18)
        colunas += f'<g class="cc{i}"><g transform="translate(0 -600)">{blocos}</g></g>'
        css += (f'.cc{i}{{animation:cc {dur:.1f}s linear {-rnd.uniform(0, dur):.1f}s infinite}}')
    css += '@keyframes cc{0%{transform:translateY(-200px)}100%{transform:translateY(1400px)}}'
    corpo = (f'<rect width="{W}" height="{H}" fill="#06061a"/><g opacity=".55">{colunas}</g>'
             f'<rect x="880" y="90" width="640" height="300" rx="30" fill="#06061a" opacity=".8"/>'
             + logo_pulsando(940, 160, 520, '#ffffff', LAV))
    return tema('besco-codigo', 'Besco Código', 'dark', 'Chuva de blocos de código caindo atrás do logo da Besco',
                svg(corpo, css), '#06061a')


def terminal():
    rnd = random.Random(9)
    linhas = ''
    css = ''
    cores = [LAV, '#7dffd0', '#ff9ee6', '#ffd27a', '#9ed8ff']
    for k in range(16):
        y = 240 + k * 38
        rec = rnd.choice([0, 0, 40, 80])
        segs = ''
        xx = 960 + rec
        for _ in range(rnd.randint(1, 4)):
            w = rnd.randint(40, 160)
            segs += f'<rect x="{xx}" y="{y}" width="{w}" height="16" rx="4" fill="{rnd.choice(cores)}"/>'
            xx += w + 14
        linhas += f'<g class="ln{k}">{segs}</g>'
        ini = k / 16 * 70
        css += (f'.ln{k}{{transform-box:fill-box;transform-origin:left;animation:ln{k} 16s steps(6) -12s infinite}}'
                f'@keyframes ln{k}{{0%,{ini:.1f}%{{transform:scaleX(0)}}{ini + 4:.1f}%,92%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}')
    css += '.cursor{animation:cursor 1s steps(1) infinite}@keyframes cursor{50%{opacity:0}}'
    janela = ('<rect x="920" y="150" width="620" height="720" rx="22" fill="#11102a" stroke="#2c2a5e" stroke-width="3"/>'
              '<rect x="920" y="150" width="620" height="54" rx="22" fill="#1c1a44"/>'
              '<circle cx="960" cy="177" r="9" fill="#ff6b6b"/><circle cx="990" cy="177" r="9" fill="#ffd27a"/>'
              '<circle cx="1020" cy="177" r="9" fill="#7dffd0"/>')
    corpo = (f'<rect width="{W}" height="{H}" fill="#0a0920"/>'
             f'{logo(60, 330, 820, "#1a1842")}{janela}{linhas}'
             f'<rect class="cursor" x="960" y="850" width="14" height="4" fill="#ffffff"/>'
             + logo_pulsando(1250, 168, 150, '#ffffff', LAV))
    return tema('besco-terminal', 'Besco Terminal', 'dark', 'Janela de terminal com código sendo digitado e o logo da Besco',
                svg(corpo, css), '#11102a')


def holograma():
    defs = (grad_linear('g-cone', ['#7df9ff', '#7df9ff'], 0, 1).replace('stop-color="#7df9ff"/></linear',
                                                                       'stop-color="#7df9ff" stop-opacity="0"/></linear')
            + '<pattern id="p-scan" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="3" fill="#000" opacity=".35"/></pattern>')
    css = ('.scan{animation:scan 3s linear infinite}@keyframes scan{to{transform:translateY(8px)}}'
           '.tremula{animation:tremula 5s steps(1) infinite}@keyframes tremula{0%,96%,98%,100%{opacity:.92}97%{opacity:.5}}'
           + vai_e_volta('sobe', 4, dy=-14))
    corpo = (f'<rect width="{W}" height="{H}" fill="#050b18"/>'
             + ''.join(f'<path d="M0 {y}H{W}" stroke="#0d2236" stroke-width="2"/>' for y in range(0, H, 50))
             + f'<path d="M1210 820 L940 260 L1480 260Z" fill="url(#g-cone)" opacity=".22"/>'
             f'<ellipse cx="1210" cy="830" rx="150" ry="34" fill="#0e3a52" stroke="#7df9ff" stroke-width="3"/>'
             f'<ellipse cx="1210" cy="820" rx="90" ry="18" fill="#7df9ff" opacity=".5" class="brilha"/>'
             f'<g class="sobe"><g class="tremula">{logo_pulsando(960, 190, 500, "#bff9ff", "#7df9ff")}'
             f'<g class="scan"><rect x="940" y="160" width="540" height="200" fill="url(#p-scan)"/></g></g></g>')
    return tema('besco-holograma', 'Besco Holograma', 'dark', 'Holograma ciano do logo da Besco saindo de um projetor',
                svg(corpo, css, defs), '#071624')


def equalizador():
    rnd = random.Random(10)
    barras = ''
    css = ''
    n = 48
    for i in range(n):
        x = 20 + i * 33
        h = rnd.randint(120, 420)
        dur = rnd.uniform(.9, 1.8)
        cor = ['#7d7bff', LAV, '#ff9ee6', '#7dffd0'][i % 4]
        barras += f'<rect class="eq{i}" x="{x}" y="{1000 - h}" width="22" height="{h}" rx="6" fill="{cor}" opacity=".85"/>'
        css += (f'.eq{i}{{transform-box:fill-box;transform-origin:bottom;'
                f'animation:eq {dur:.2f}s ease-in-out {-rnd.uniform(0, dur):.2f}s infinite alternate}}')
    css += '@keyframes eq{from{transform:scaleY(.25)}to{transform:scaleY(1)}}'
    defs = grad_linear('g-fundo', ['#0c0a24', '#17123f', '#241a5a'])
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-fundo)"/>{barras}'
             + logo_pulsando(940, 140, 520, '#ffffff', '#7d7bff'))
    return tema('besco-som', 'Besco Som', 'dark', 'Equalizador de música pulsando com o logo da Besco',
                svg(corpo, css, defs), '#17123f')


def radar():
    cx, cy = 1200, 480
    aneis = ''.join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#3dffb0" stroke-opacity=".3" stroke-width="2"/>'
                    for r in (110, 220, 330, 440))
    cruz = f'<path d="M{cx - 460} {cy}H{cx + 460}M{cx} {cy - 460}V{cy + 460}" stroke="#3dffb0" stroke-opacity=".25" stroke-width="2"/>'
    defs = ('<linearGradient id="g-varre" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3dffb0" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#3dffb0" stop-opacity=".55"/></linearGradient>')
    a = math.radians(40)
    varre = (f'<g class="varre"><circle cx="{cx}" cy="{cy}" r="440" fill="none"/>'
             f'<path d="M{cx} {cy}L{cx + 440} {cy}A440 440 0 0 0 {cx + 440 * math.cos(a):.0f} {cy - 440 * math.sin(a):.0f}Z" '
             f'fill="url(#g-varre)"/></g>')
    rnd = random.Random(11)
    pontos = ''
    css = '.varre{transform-box:fill-box;transform-origin:center;animation:varre 6s linear infinite}@keyframes varre{to{transform:rotate(-360deg)}}'
    for i in range(7):
        r, ang = rnd.uniform(140, 420), rnd.uniform(0, 360)
        px, py = cx + r * math.cos(math.radians(ang)), cy - r * math.sin(math.radians(ang))
        pontos += f'<circle class="bl{i}" cx="{px:.0f}" cy="{py:.0f}" r="9" fill="#7dffd0"/>'
        atraso = (ang / 360) * 6
        css += f'.bl{i}{{animation:bl 6s linear {-6 + atraso:.2f}s infinite}}'
    css += '@keyframes bl{0%{opacity:1}60%{opacity:.1}100%{opacity:.1}}'
    corpo = (f'<rect width="{W}" height="{H}" fill="#04110f"/>{aneis}{cruz}{varre}{pontos}'
             + logo_pulsando(cx - 170, cy - 48, 340, '#e6fff6', '#3dffb0'))
    return tema('besco-radar', 'Besco Radar', 'dark', 'Radar verde girando com o logo da Besco no centro',
                svg(corpo, css, defs), '#04110f')


def blueprint():
    defs = ('<pattern id="p-grade" width="40" height="40" patternUnits="userSpaceOnUse">'
            '<path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".08" stroke-width="2"/></pattern>'
            '<pattern id="p-grade2" width="200" height="200" patternUnits="userSpaceOnUse">'
            '<path d="M200 0H0V200" fill="none" stroke="#ffffff" stroke-opacity=".16" stroke-width="2"/></pattern>')
    css = ('.risca{stroke-dasharray:100;animation:risca 9s ease-in-out -5s infinite}'
           '@keyframes risca{0%{stroke-dashoffset:100}45%,80%{stroke-dashoffset:0}100%{stroke-dashoffset:-100}}'
           '.enche{animation:enche 9s ease-in-out -5s infinite}@keyframes enche{0%,40%{opacity:0}55%,78%{opacity:.25}90%,100%{opacity:0}}')
    x, y, lw = 920, 200, 560
    cota = (f'<path d="M{x} {y - 40}H{x + lw}M{x} {y - 52}V{y - 28}M{x + lw} {y - 52}V{y - 28}" stroke="#ffffff" stroke-opacity=".6" stroke-width="2"/>'
            f'<path d="M{x - 40} {y}V{y + altura(lw):.0f}M{x - 52} {y}H{x - 28}M{x - 52} {y + altura(lw):.0f}H{x - 28}" stroke="#ffffff" stroke-opacity=".6" stroke-width="2"/>'
            f'<circle cx="{x + lw + 90}" cy="{y + 300}" r="60" fill="none" stroke="#ffffff" stroke-opacity=".4" stroke-width="2"/>'
            f'<path d="M{x + lw + 90} {y + 230}V{y + 370}M{x + lw + 20} {y + 300}H{x + lw + 160}" stroke="#ffffff" stroke-opacity=".4" stroke-width="2"/>')
    corpo = (f'<rect width="{W}" height="{H}" fill="#0d2a5c"/><rect width="{W}" height="{H}" fill="url(#p-grade)"/>'
             f'<rect width="{W}" height="{H}" fill="url(#p-grade2)"/>{cota}'
             f'<g class="pulsa">{logo(x, y, lw, "#ffffff", classe="enche")}'
             f'{logo(x, y, lw, "none", extra="class=\"risca\" stroke=\"#ffffff\" stroke-width=\"2\"", linha=True)}</g>')
    return tema('besco-planta', 'Besco Planta', 'dark', 'Planta técnica azul com o logo da Besco sendo desenhado à mão',
                svg(corpo, css, defs, linha=True), '#0d2a5c')


def contorno_neon():
    defs = grad_linear('g-traco', ['#7d7bff', '#ff5fd2', '#7dffd0'], 1, 0)
    css = ('.risca{stroke-dasharray:100;animation:risca 8s ease-in-out -5s infinite}'
           '@keyframes risca{0%{stroke-dashoffset:100}50%,75%{stroke-dashoffset:0}100%{stroke-dashoffset:-100}}'
           '.enche{animation:enche 8s ease-in-out -5s infinite}@keyframes enche{0%,45%{opacity:0}60%,72%{opacity:1}88%,100%{opacity:0}}')
    x, y, lw = 900, 170, 580
    corpo = (f'<rect width="{W}" height="{H}" fill="#07061a"/>'
             f'<g class="pulsa">{logo(x, y, lw, "#ff5fd2", classe="enche", extra="filter=\"url(#f-brilho)\" opacity=\".7\"")}'
             f'{logo(x, y, lw, "#ffffff", classe="enche")}'
             f'{logo(x, y, lw, "none", extra="class=\"risca\" stroke=\"url(#g-traco)\" stroke-width=\"3\"", linha=True)}</g>')
    return tema('besco-contorno', 'Besco Contorno', 'dark', 'O logo da Besco se desenhando em linha neon e acendendo',
                svg(corpo, css, defs, linha=True), '#07061a')


# ---------------------------------------------------------------------- natureza

def oceano():
    defs = (grad_linear('g-ceu', ['#ffd6c2', '#f7c6e8', '#d9d4ff', '#b9c6ff'])
            + grad_radial('g-sol', ['#fff7e0', '#ffe2b8', '#ffd0c8'], [1, .9, 0]))
    camadas = ''
    css = ''
    for i, (y, amp, comp, cor, dur) in enumerate(((640, 18, 520, '#9aa7f0', 40), (700, 22, 640, '#7d86e0', 30),
                                                  (780, 26, 760, '#5e64c8', 22), (870, 30, 900, '#3f43a8', 16))):
        camadas += f'<g class="mar{i}"><path d="{onda(y, amp, comp, i, W * 2)}" fill="{cor}"/></g>'
        css += anda_x(f'mar{i}', dur, -comp * 2)
    gaivotas = ''.join(f'<g class="gv{i}"><path d="M{x} {y}q14 -14 28 0q14 -14 28 0" stroke="#4a3f7a" stroke-width="4" fill="none"/></g>'
                       for i, (x, y) in enumerate(((-80, 260), (-200, 320))))
    css += vai_e_volta('gv0', 26, dx=1800, dy=-40) + vai_e_volta('gv1', 34, dx=1900, dy=20)
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-ceu)"/><circle cx="1210" cy="330" r="320" fill="url(#g-sol)"/>'
             + logo_pulsando(960, 250, 500, '#4b3fb0', '#ffffff') + gaivotas + camadas)
    return tema('besco-oceano', 'Besco Oceano', 'light', 'Mar em camadas ao amanhecer com o logo da Besco nascendo como o sol',
                svg(corpo, css, defs), '#f3e8ff')


def por_do_sol():
    defs = grad_linear('g-ceu', ['#2b1d5c', '#7a3d8c', '#ff7a8a', '#ffc38a'])
    montes = ''
    for i, (y, cor) in enumerate(((560, '#5a3a8c'), (660, '#432c74'), (760, '#2f1f5c'), (860, '#1e1440'))):
        rnd = random.Random(20 + i)
        pts = [f'M0 {H}']
        x = 0
        while x <= W + 200:
            pts.append(f'L{x} {y + rnd.randint(-110, 30)}')
            x += rnd.randint(120, 260)
        pts.append(f'L{W} {H}Z')
        montes += f'<path d="{"".join(pts)}" fill="{cor}"/>'
    nuvens = ''.join(f'<g class="nv{i}"><ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * .22:.0f}" fill="#ffd6e0" opacity=".55"/></g>'
                     for i, (x, y, rx) in enumerate(((200, 200, 180), (700, 140, 140), (1400, 240, 200))))
    css = ''.join(vai_e_volta(f'nv{i}', 30 + i * 8, dx=160 * (1 if i % 2 else -1)) for i in range(3))
    passaros = ''.join(f'<path d="M{x} {y}q10 -10 20 0q10 -10 20 0" stroke="#2b1d5c" stroke-width="3" fill="none"/>'
                       for x, y in ((300, 330), (340, 310), (380, 336)))
    css += vai_e_volta('bando', 20, dx=500, dy=-60)
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-ceu)"/>{nuvens}'
             f'<circle cx="1210" cy="420" r="260" fill="#ffd27a" opacity=".9"/>'
             + logo_pulsando(990, 360, 440, '#7a2f5c', '#ffffff') + f'<g class="bando">{passaros}</g>{montes}')
    return tema('besco-por-do-sol', 'Besco Pôr do Sol', 'dark', 'Montanhas em camadas no pôr do sol com o logo da Besco no sol',
                svg(corpo, css, defs), '#2b1d5c')


def chuva_neon():
    rnd = random.Random(12)
    gotas = ''.join(f'<path d="M{rnd.uniform(0, W):.0f} {rnd.uniform(-1000, 0):.0f}l-6 34" stroke="#9ea8ff" stroke-opacity=".5" stroke-width="2"/>'
                    for _ in range(160))
    predios = ''
    x = 0
    while x < W:
        w, h = rnd.randint(80, 160), rnd.randint(200, 520)
        predios += f'<rect x="{x}" y="{780 - h}" width="{w}" height="{h}" fill="#141033"/>'
        for jy in range(780 - h + 20, 770, 40):
            for jx in range(x + 14, x + w - 14, 30):
                if rnd.random() < .3:
                    predios += f'<rect x="{jx}" y="{jy}" width="12" height="16" fill="{rnd.choice(["#ffd27a", LAV, "#ff9ee6"])}" opacity=".8"/>'
        x += w + rnd.randint(4, 20)
    css = ('.chuva{animation:chuva 1.4s linear infinite}@keyframes chuva{to{transform:translate(-40px,1000px)}}'
           '.reflexo{animation:reflexo 2s ease-in-out infinite alternate}@keyframes reflexo{to{transform:translateX(10px) scaleY(.96)}}')
    corpo = (f'<rect width="{W}" height="{H}" fill="#0a0820"/>{predios}'
             f'<rect y="780" width="{W}" height="220" fill="#0d0b26"/>'
             + logo_pulsando(960, 160, 500, '#ffffff', '#ff5fd2')
             + f'<g class="reflexo" opacity=".3"><g transform="translate(0 1600) scale(1 -1)">'
               f'{logo(960, 680, 500, "#ff5fd2", extra="filter=\"url(#f-brilho)\"")}</g></g>'
             + f'<g class="chuva">{gotas}<g transform="translate(0 1000)">{gotas}</g></g>')
    return tema('besco-chuva-neon', 'Besco Chuva Neon', 'dark', 'Cidade na chuva com o logo neon da Besco refletido no chão molhado',
                svg(corpo, css), '#141033')


def nuvens():
    defs = grad_linear('g-ceu', ['#8fb0ff', '#b9c8ff', '#e6e2ff', '#fff2f8'])
    rnd = random.Random(13)
    camada = ''
    css = ''
    for i in range(7):
        x, y, r = rnd.uniform(0, W), rnd.uniform(500, 900), rnd.uniform(60, 130)
        bolas = ''.join(f'<circle cx="{x + k * r * .7:.0f}" cy="{y - (k % 2) * r * .4:.0f}" r="{r * (1 - abs(k - 1.5) * .15):.0f}" fill="#ffffff"/>'
                        for k in range(4))
        camada += f'<g class="nu{i}" opacity=".9">{bolas}</g>'
        css += vai_e_volta(f'nu{i}', rnd.uniform(25, 45), dx=rnd.choice([-1, 1]) * rnd.uniform(80, 200))
    baloes = ''
    for i, (x, cor) in enumerate(((300, '#7d7bff'), (520, '#ff9ee6'), (1500, '#7dffd0'))):
        baloes += (f'<g class="bl{i}"><ellipse cx="{x}" cy="{700 + i * 30}" rx="46" ry="56" fill="{cor}"/>'
                   f'<path d="M{x - 30} {740 + i * 30}L{x - 10} {790 + i * 30}M{x + 30} {740 + i * 30}L{x + 10} {790 + i * 30}" stroke="#5a4f8a" stroke-width="3"/>'
                   f'<rect x="{x - 12}" y="{790 + i * 30}" width="24" height="18" rx="4" fill="#8a5a3a"/></g>')
        css += (f'.bl{i}{{animation:bl{i} {50 + i * 12}s linear {-i * 15}s infinite}}'
                f'@keyframes bl{i}{{0%{{transform:translate(0,200px)}}100%{{transform:translate({60 - i * 40}px,-1000px)}}}}')
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-ceu)"/>' + logo_pulsando(960, 170, 520, '#4b47b8', '#ffffff')
             + baloes + camada)
    return tema('besco-nuvens', 'Besco Nuvens', 'light', 'Céu claro com nuvens, balões subindo e o logo da Besco',
                svg(corpo, css, defs), '#eef0ff')


def ondulacao():
    cx, cy = 1210, 760
    css = ('.ri{transform-box:fill-box;transform-origin:center;animation:ri 6s ease-out infinite}'
           '@keyframes ri{0%{transform:scale(.2);opacity:.9}100%{transform:scale(1.6);opacity:0}}')
    aneis = ''.join(f'<ellipse class="ri" style="animation-delay:{-k * 2}s" cx="{cx}" cy="{cy}" rx="300" ry="70" fill="none" '
                    f'stroke="{LAV}" stroke-width="4"/>' for k in range(3))
    defs = grad_linear('g-agua', ['#0d0b2b', '#090722'])
    corpo = (f'<rect width="{W}" height="620" fill="#100d33"/>{estrelas(90, 14, 600)[0]}'
             f'<rect y="620" width="{W}" height="380" fill="url(#g-agua)"/>'
             + logo_pulsando(960, 200, 500, '#f2f0ff', LAV)
             + f'<g opacity=".25"><g transform="translate(0 1240) scale(1 -1)">{logo(960, 520, 500, LAV)}</g></g>{aneis}')
    return tema('besco-ondulacao', 'Besco Ondulação', 'dark', 'Ondas circulares se abrindo num lago escuro sob o logo da Besco',
                svg(corpo, css + estrelas(90, 14, 600)[1], defs), '#100d33')


# ---------------------------------------------------------------------- formas e cores

def bolhas(escuro=False):
    rnd = random.Random(15 if escuro else 16)
    cores = ['#5b4fd8', '#8a3fd1', '#1f9ea8', '#d14f9a'] if escuro else ['#c9c6ff', '#ffc6ec', '#c6fff0', '#ffe6c2']
    blobs = ''
    css = ''
    for i in range(7):
        x, y, r = rnd.uniform(100, 1500), rnd.uniform(100, 900), rnd.uniform(180, 340)
        blobs += f'<g class="bo{i}"><circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{cores[i % 4]}" opacity="{.55 if escuro else .8}"/></g>'
        css += vai_e_volta(f'bo{i}', rnd.uniform(14, 24), dx=rnd.uniform(-260, 260), dy=rnd.uniform(-180, 180))
    defs = '<filter id="f-nevoa" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="70"/></filter>'
    fundo = '#0a0a1e' if escuro else '#f5f3ff'
    cor_logo = '#ffffff' if escuro else '#3d3a8f'
    corpo = (f'<rect width="{W}" height="{H}" fill="{fundo}"/><g filter="url(#f-nevoa)">{blobs}</g>'
             + logo_pulsando(960, 180, 520, cor_logo, LAV if escuro else '#ffffff'))
    if escuro:
        return tema('besco-gradiente', 'Besco Gradiente', 'dark', 'Manchas de cor escura se movendo devagar atrás do logo da Besco',
                    svg(corpo, css, defs), '#0a0a1e')
    return tema('besco-bolhas', 'Besco Bolhas', 'light', 'Manchas pastel se movendo devagar atrás do logo da Besco',
                svg(corpo, css, defs), '#f5f3ff')


def lava():
    rnd = random.Random(17)
    blobs = ''
    css = ''
    for i in range(9):
        x, r = rnd.uniform(100, 1500), rnd.uniform(70, 150)
        blobs += f'<g class="lv{i}"><circle cx="{x:.0f}" cy="1100" r="{r:.0f}" fill="#ff6a3d"/></g>'
        dur = rnd.uniform(18, 30)
        css += (f'.lv{i}{{animation:lv {dur:.1f}s ease-in-out {-rnd.uniform(0, dur):.1f}s infinite alternate}}')
    css += '@keyframes lv{0%{transform:translateY(0)}100%{transform:translateY(-1150px)}}'
    defs = ('<filter id="f-gosma" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="30"/>'
            '<feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 26 -12"/></filter>'
            + grad_linear('g-fundo', ['#2a0a4a', '#4a0f5a', '#7a1a4a']))
    corpo = (f'<rect width="{W}" height="{H}" fill="url(#g-fundo)"/><g filter="url(#f-gosma)">{blobs}'
             f'<rect y="960" width="{W}" height="60" fill="#ff6a3d"/></g>'
             + logo_pulsando(960, 160, 520, '#fff0e6', '#ffb347'))
    return tema('besco-lava', 'Besco Lava', 'dark', 'Lâmpada de lava com bolhas laranja subindo atrás do logo da Besco',
                svg(corpo, css, defs), '#2a0a4a')


def confete():
    rnd = random.Random(18)
    pecas = ''
    css = ''
    cores = ['#7d7bff', '#ff9ee6', '#7dffd0', '#ffd27a', '#ff6b6b', LAV]
    for i in range(110):
        x = rnd.uniform(0, W)
        w, h = rnd.choice([(22, 12), (16, 16), (28, 9)])
        dur = rnd.uniform(10, 20)
        pecas += f'<g class="cf{i % 12}" style="animation-duration:{dur:.1f}s;animation-delay:{-rnd.uniform(0, dur):.1f}s">' \
                 f'<rect x="{x:.0f}" y="{rnd.uniform(0, 1000):.0f}" width="{w}" height="{h}" rx="2" fill="{rnd.choice(cores)}"/></g>'
    for k in range(12):
        css += (f'.cf{k}{{animation-name:cf{k};animation-timing-function:linear;animation-iteration-count:infinite}}'
                f'@keyframes cf{k}{{0%{{transform:translate(0,-1100px) rotate(0deg)}}100%{{transform:translate({(k - 6) * 20}px,120px) rotate({180 + k * 40}deg)}}}}')
    css += vai_e_volta('quica', 1.6, dy=-16)
    corpo = (f'<rect width="{W}" height="{H}" fill="#fbf9ff"/><g class="quica">'
             + logo_pulsando(960, 200, 520, '#3d3a8f', '#c9c6ff') + f'</g>{pecas}')
    return tema('besco-confete', 'Besco Confete', 'light', 'Confete caindo devagar em volta do logo da Besco',
                svg(corpo, css), '#fbf9ff')


def papel():
    camadas = ''
    css = ''
    cores = ['#e9e4ff', '#d6ceff', '#bfb4f5', '#a497e6', '#8778d1']
    for i, cor in enumerate(cores):
        y = 520 + i * 90
        camadas += (f'<g class="pp{i}"><path d="{onda(y + 10, 40, 900 - i * 80, i * 1.3, W * 2)}" fill="#000" opacity=".12" filter="url(#f-sombra)"/>'
                    f'<path d="{onda(y, 40, 900 - i * 80, i * 1.3, W * 2)}" fill="{cor}"/></g>')
        css += vai_e_volta(f'pp{i}', 18 + i * 4, dx=-120 + i * 20)
    defs = '<filter id="f-sombra" x="-10%" y="-20%" width="120%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>'
    css += vai_e_volta('flutua2', 3.4, dy=-18)
    corpo = (f'<rect width="{W}" height="{H}" fill="#f7f5ff"/>'
             f'<circle cx="1210" cy="330" r="230" fill="#ffffff"/>'
             f'<g class="flutua2">{logo_pulsando(980, 270, 460, "#5b4fb8", "#ffffff")}</g>{camadas}')
    return tema('besco-papel', 'Besco Papel', 'light', 'Camadas de papel recortado em lavanda com o logo da Besco flutuando',
                svg(corpo, css, defs), '#f7f5ff')


def isometrico():
    rnd = random.Random(19)
    cubos = ''
    css = ''

    def cubo(x, y, s, cores):
        topo = f'M{x} {y}l{s} {s / 2}l{-s} {s / 2}l{-s} {-s / 2}Z'
        esq = f'M{x - s} {y + s / 2}l{s} {s / 2}v{s}l{-s} {-s / 2}Z'
        dir_ = f'M{x} {y + s}l{s} {-s / 2}v{s}l{-s} {s / 2}Z'
        return f'<path d="{topo}" fill="{cores[0]}"/><path d="{esq}" fill="{cores[1]}"/><path d="{dir_}" fill="{cores[2]}"/>'

    paletas = [('#e6e4ff', '#b6b9ff', '#8f8ce8'), ('#ffe6f6', '#ffb6e0', '#e88cc4'), ('#e0fff6', '#a6f0d8', '#7cd0b8')]
    for i in range(14):
        x, y, s = rnd.uniform(60, 1540), rnd.uniform(80, 880), rnd.uniform(30, 70)
        cubos += f'<g class="cb{i}">{cubo(x, y, s, paletas[i % 3])}</g>'
        css += vai_e_volta(f'cb{i}', rnd.uniform(3, 6), dy=-rnd.uniform(14, 30), atraso=rnd.uniform(0, 5))
    base = cubo(1210, 420, 260, ('#f2f0ff', '#cfcaff', '#a9a3f0'))
    corpo = (f'<rect width="{W}" height="{H}" fill="#fafaff"/>{cubos}{base}'
             f'<g transform="translate(1210 550) scale(1 .58) rotate(-45) translate(-1210 -550)">'
             + logo_pulsando(1070, 515, 280, '#3d3a8f', '#ffffff') + '</g>')
    return tema('besco-isometrico', 'Besco Isométrico', 'light', 'Cubos isométricos flutuando e o logo da Besco no topo de um bloco',
                svg(corpo, css), '#fafaff')


def minimal_claro():
    rnd = random.Random(21)
    linhas = ''.join(f'<path d="M{x:.0f} -100L{x - 500:.0f} 1100" stroke="#3d3a8f" stroke-opacity=".06" stroke-width="2"/>'
                     for x in [rnd.uniform(0, 2200) for _ in range(30)])
    pontos = ''.join(f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" r="3" fill="#7d7bff" opacity=".3"/>'
                     for _ in range(40))
    css = anda_x('desliza', 60, -400) + vai_e_volta('pontos', 20, dy=-40)
    corpo = (f'<rect width="{W}" height="{H}" fill="#fbfaf7"/><g class="desliza">{linhas}</g><g class="pontos">{pontos}</g>'
             + logo_pulsando(980, 220, 480, '#2d2a6e', '#b6b9ff'))
    return tema('besco-minimal-claro', 'Besco Minimal Claro', 'light', 'Fundo claro minimalista com linhas finas e o logo da Besco respirando',
                svg(corpo, css), '#fbfaf7')


def minimal_escuro():
    cx, cy = 1215, 285
    css = ('.anel{transform-box:fill-box;transform-origin:center;animation:anel 4.5s ease-out infinite}'
           '@keyframes anel{0%{transform:scale(.6);opacity:.7}100%{transform:scale(2.2);opacity:0}}')
    aneis = ''.join(f'<circle class="anel" style="animation-delay:{-k * 1.5}s" cx="{cx}" cy="{cy}" r="200" fill="none" '
                    f'stroke="{LAV}" stroke-width="2"/>' for k in range(3))
    corpo = (f'<rect width="{W}" height="{H}" fill="#050508"/>{aneis}' + logo_pulsando(cx - 230, cy - 66, 460, LAV, '#7d7bff'))
    return tema('besco-minimal-escuro', 'Besco Minimal Escuro', 'dark', 'Fundo preto com anéis saindo do logo da Besco',
                svg(corpo, css), '#050508')


def todos():
    return [aurora(), galaxia(), orbita(), foguete(), constelacao(), neon(), synthwave(), vaporwave(), chuva_de_codigo(),
            terminal(), holograma(), equalizador(), radar(), blueprint(), contorno_neon(), oceano(), por_do_sol(),
            chuva_neon(), nuvens(), ondulacao(), bolhas(), bolhas(escuro=True), lava(), confete(), papel(), isometrico(),
            minimal_claro(), minimal_escuro()]
