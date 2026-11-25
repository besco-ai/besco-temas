"""Gera todas as cenas do pixel-temas e escreve hooks/cenas.ts.

Uso:  python3 -I ferramentas/gerar.py          (de dentro da pasta do plugin)

- Cenas desenhadas aqui: estáticas e animadas, em pixel art de 192 x 108.
- Zoeira: cada foto listada em fotos/zoeira.json vira três temas (DVD, chuva de cara, funcionário do mês).
  Sem foto, os três saem com uma carinha de pixel no lugar.
- GIFs: cada arquivo em gifs/ vira um tema animado, reduzido até caber no limite do app.
- Prévias em PNG e GIF vão para previas/.
"""

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from pixel import (BAYER, Cena, Tela, checar_svg, foto_para_sprite, gif_para_quadros, largura_texto, mistura, rgb,  # noqa: E402
                   ruido)

RAIZ = AQUI.parent
CEU_NOITE = ('#060a1d', '#0c1432', '#16214a', '#243262')
W, H = 192, 108


def linha(t, x0, y0, x1, y1, cor):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    erro = dx + dy
    while True:
        t.ponto(x0, y0, cor)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * erro
        if e2 >= dy:
            erro += dy
            x0 += sx
        if e2 <= dx:
            erro += dx
            y0 += sy


def estrelas(t, n, y_max, semente, cores=('#ffffff', '#c9d4ff', '#ffe9b0')):
    rnd = random.Random(semente)
    pos = []
    for _ in range(n):
        x, y = rnd.randrange(W), rnd.randrange(y_max)
        t.ponto(x, y, rnd.choice(cores))
        pos.append((x, y))
    return pos


def nuvem(t, x, y, escala, cor, sombra):
    rnd = random.Random(x * 7 + y)
    bolhas = [(x + i * 4 * escala, y - rnd.randint(0, 3) * escala, rnd.randint(3, 5) * escala) for i in range(4)]
    for bx, by, r in bolhas:
        t.disco(bx, by + 1, r, sombra)
    for bx, by, r in bolhas:
        t.disco(bx, by, r, cor)
    t.ret(x - 2, y + 1, 4 * 4 * escala - 2, 3, cor)


def palmeira(t, bx, by, alt, curva, cor):
    x = bx
    for k in range(alt):
        f = k / alt
        x = bx + curva * f * f * alt * 0.3
        t.ret(round(x) - 1, by - k, 3 if f < 0.65 else 2, 1, cor)
    tx, ty = round(x), by - alt
    for ang, comp in ((-175, 20), (-145, 17), (-115, 11), (-65, 11), (-35, 17), (-5, 20), (-90, 7), (160, 12), (20, 12)):
        a = math.radians(ang)
        for s in range(comp):
            fx = tx + math.cos(a) * s
            fy = ty + math.sin(a) * s * 0.55 + (s / comp) ** 2 * comp * 0.5
            t.ret(round(fx), round(fy), 2, 2 if s < comp * 0.6 else 1, cor)
    t.disco(tx, ty + 2, 2.2, cor)


def pinheiro(t, cx, base, altura, cor, luz=None, tronco='#4a3424'):
    t.ret(cx - 1, base - 3, 2, 3, tronco)
    topo = base - 3 - altura
    for r in range(altura):
        meia = int(1 + (r // 5) * 1.3 + (r % 5) * 0.8)
        for x in range(cx - meia, cx + meia + 1):
            t.ponto(x, topo + r, luz if (luz and x <= cx - meia + 1) else cor)


# ---------------------------------------------------------------- estáticas

def cena_synthwave():
    t = Tela(W, H)
    t.degrade(0, 66, ['#0b0420', '#1d0838', '#3a0d52', '#6a1466', '#a8235f', '#e0435a', '#ff7b4a'])
    estrelas(t, 70, 38, 3)
    cx, cy, r = 146, 48, 22
    for y in range(int(cy - r), int(cy + r) + 1):
        cor = mistura('#ffe066', '#ff3f8e', (y - (cy - r)) / (2 * r))
        dy = y - (cy - 6)
        if dy > 0 and (dy % 6) < 1 + dy // 7:
            continue
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                t.ponto(x, y, cor)
    fundo = 58 + ruido(W, 22, 7, 11) - np.exp(-((np.arange(W) - 40) / 18) ** 2) * 14
    frente = 62 + ruido(W, 14, 4, 12) - np.exp(-((np.arange(W) - 178) / 12) ** 2) * 9
    t.silhueta(fundo, '#2a0b45', ate=67)
    t.silhueta(frente, '#170529', ate=67)
    for x in range(W):
        t.ponto(x, int(round(fundo[x])), '#7a2a8a')
        t.ponto(x, int(round(frente[x])), '#ff4fa3')
    t.ret(0, 66, W, H - 66, '#0a0218')
    for y in (67, 68, 70, 73, 77, 82, 88, 95, 103):
        t.ret(0, y, W, 1, mistura('#5a1466', '#ff2fa0', (y - 66) / 42))
    for j in range(-14, 15):
        linha(t, 96 + int(j * 1.6), 66, 96 + j * 15, 107, '#c42a9a')
    t.ret(0, 66, W, 1, '#ff7bd0')
    # palmeiras em silhueta nos cantos
    for bx, alt, curva in ((174, 50, -1.0), (186, 40, 0.8), (12, 44, 1.0)):
        palmeira(t, bx, 107, alt, curva, '#050110')
    return Cena(t)


def cena_floresta():
    t = Tela(W, H)
    t.degrade(0, 72, ['#6fbdeb', '#94d0f0', '#bde3f3', '#e6f4f1'])
    t.disco(160, 16, 7, '#fff7d1')
    t.disco(160, 16, 5, '#ffffff')
    for x, y, e in ((20, 14, 1), (118, 22, 1), (64, 8, 1)):
        nuvem(t, x, y, e, '#ffffff', '#d6e7f2')
    montanha = 50 + ruido(W, 26, 9, 21) - np.exp(-((np.arange(W) - 150) / 20) ** 2) * 16
    t.silhueta(montanha, '#93b6cf', ate=80)
    rnd = random.Random(4)
    pico = montanha.min()
    for x in range(W):
        topo = int(round(montanha[x]))
        if topo < pico + 6:
            neve = max(1, int(pico + 6 - topo) // 2 + rnd.randint(0, 1))
            t.ret(x, topo, 1, neve, '#f4f8fb')
    camadas = [(68, '#7fa79a', None, 14, 7, 31), (80, '#4d8566', None, 18, 6, 32), (98, '#24573c', '#3b7a52', 26, 9, 33)]
    for base, cor, luz, alt, espaco, sem in camadas:
        rnd = random.Random(sem)
        x = rnd.randint(-4, espaco)
        while x < W + 6:
            pinheiro(t, x, base + rnd.randint(-2, 2), alt + rnd.randint(-5, 5), cor, luz,
                     tronco='#4a3424' if base >= 98 else cor)
            x += espaco + rnd.randint(-2, 3)
        t.ret(0, base - 1, W, H - base + 1, cor) if base < 98 else None
    t.degrade(96, H, ['#5aa35a', '#3f8a46', '#2f7239'])
    rnd = random.Random(5)
    for _ in range(70):
        t.ponto(rnd.randrange(W), rnd.randrange(98, H), rnd.choice(['#ffd84d', '#ff8fb4', '#ffffff', '#9fe08a']))
    return Cena(t)


# ---------------------------------------------------------------- animadas

def cena_cidade():
    t = Tela(W, H)
    t.degrade(0, 84, ['#060a1d', '#0c1432', '#16214a', '#243262', '#3a4a7a'])
    pos = estrelas(t, 90, 50, 7)
    t.disco(164, 18, 11, '#2b3760')
    t.disco(164, 18, 9, '#f2efd2')
    for cx, cy, r in ((161, 15, 2), (167, 21, 1.5), (166, 13, 1)):
        t.disco(cx, cy, r, '#d6d0a8')
    rnd = random.Random(41)
    janelas = []
    x = -3
    while x < W:  # prédios de trás
        w, h = rnd.randint(8, 16), rnd.randint(18, 44)
        t.ret(x, 96 - h, w, h, '#1a2347')
        x += w + rnd.randint(-2, 1)
    x = -2
    antena = None
    while x < W:  # prédios da frente, com janelas
        w, h = rnd.randint(10, 20), rnd.randint(14, 38)
        if 124 < x < 150 and antena is None:
            h = 52
            antena = (x + w // 2, 96 - h)
        t.ret(x, 96 - h, w, h, '#0d1330')
        t.ret(x, 96 - h, w, 1, '#222c52')
        for jy in range(96 - h + 3, 94, 3):
            for jx in range(x + 2, x + w - 1, 3):
                acesa = rnd.random() < 0.33
                janelas.append((jx, jy, acesa))
                t.ponto(jx, jy, rnd.choice(['#ffd36b', '#ffb347', '#fff1b8']) if acesa else '#1c2445')
        x += w + rnd.randint(1, 3)
    ax, ay = antena
    t.ret(ax, ay - 8, 1, 8, '#3a4470')
    # rio com reflexos
    t.ret(0, 96, W, H - 96, '#0a1028')
    t.ret(0, 96, W, 1, '#1c2a55')
    base = t
    cena = Cena(base)
    # estrelas piscando
    for semente in (1, 2):
        sel = random.Random(semente).sample(pos, 10)
        f = base.copia()
        for sx, sy in sel:
            f.ponto(sx, sy, '#ffffff')
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= sx + dx < W and 0 <= sy + dy < H and base.px[sy + dy, sx + dx] in CEU_NOITE:
                    f.ponto(sx + dx, sy + dy, '#8fa2e0')
        cena.animar([base, f], [3.0 + semente, 0.9], atraso=semente * 1.7)
    # janelas que acendem e apagam
    for semente in (3, 4, 5):
        sel = random.Random(semente).sample(janelas, 14)
        f = base.copia()
        for jx, jy, acesa in sel:
            f.ponto(jx, jy, '#1c2445' if acesa else '#ffd36b')
        cena.animar([base, f], [5.0 + semente, 4.0], atraso=semente * 2.3)
    # luz vermelha da antena
    f = base.copia()
    f.ponto(ax, ay - 9, '#ff3b3b')
    f.ponto(ax - 1, ay - 9, '#7a1a2a')
    f.ponto(ax + 1, ay - 9, '#7a1a2a')
    cena.animar([base, f], [1.4, 1.0])
    # reflexo no rio, dois quadros
    q = []
    for k in range(2):
        f = base.copia()
        r2 = random.Random(60 + k)
        for _ in range(60):
            rx, ry = r2.randrange(W), r2.randrange(98, H)
            f.ret(rx, ry, r2.randint(2, 4), 1, r2.choice(['#2b3a70', '#5a5a7a', '#8a7a4a']))
        q.append(f)
    cena.animar(q, [1.1, 1.1])
    # trem atravessando a ponte
    trem = np.full((5, 44), '', dtype='<U9')
    trem[0:4, :] = '#1b2550'
    trem[0, :] = '#33406e'
    for i in range(2, 42, 4):
        trem[1:3, i:i + 2] = '#ffe08a'
    trem[4, 3:41:6] = '#05070f'
    for i in range(0, 44, 11):
        trem[:, i] = '#05070f'
    trem[1:3, 42:44] = '#fff6cc'
    cena.definir('s-trem', trem)
    cena.camadas.append('<g class="trem"><use href="#s-trem" x="-46" y="91"/></g>')
    cena.css.append('.trem{animation:trem 26s steps(119) infinite}'
                    '@keyframes trem{0%{transform:translate(0px,0px)}92%{transform:translate(238px,0px)}'
                    '100%{transform:translate(238px,0px)}}')
    t.ret(0, 96, W, 1, '#2a3566')
    return cena


def cena_praia():
    def desenha(barco_dy=0, onda=0, espuma=0):
        t = Tela(W, H)
        t.degrade(0, 60, ['#58aee6', '#86c6ec', '#b7def0', '#f1e4c6'])
        t.degrade(60, 87, ['#1f7fb8', '#2f98c9', '#46b1d6', '#62c7dd'])
        t.ret(0, 60, W, 1, '#1a6ea3')
        rnd = random.Random(9)
        for _ in range(55):
            x, y = rnd.randrange(W), rnd.randrange(62, 85)
            x = (x + onda * (1 + (y - 60) // 8)) % W
            t.ret(x, y, rnd.randint(2, 4), 1, '#bfeaf5')
        t.degrade(87, H, ['#f2d9a0', '#ecce90', '#e3c07e'])
        for x in range(W):
            alt = int(1.5 + 1.5 * math.sin(x / 9 + espuma * 1.6))
            t.ret(x, 86, 1, alt, '#ffffff')
            t.ponto(x, 86 + alt, '#d9f2f5')
        # barco a vela
        bx, by = 148, 50 + barco_dy
        for k in range(12):
            t.ret(bx + 1, by - 12 + k, k // 2 + 1, 1, '#fdfbf5')
            t.ret(bx - k // 3, by - 12 + k, k // 3, 1, '#f0e8d8')
        t.ret(bx, by - 14, 1, 15, '#5a3d2e')
        t.ret(bx - 6, by + 1, 14, 2, '#c0453a')
        t.ret(bx - 5, by + 3, 12, 1, '#8a2f28')
        # guarda-sol e toalha na areia
        ux, uy = 170, 80
        for k in range(10):
            t.ret(ux - k, uy + k // 2, 2 * k + 1, 1, '#e84a5f' if (k // 2) % 2 == 0 else '#fff4e0')
        t.ret(ux, uy + 5, 1, 18, '#6b4a33')
        t.ret(150, 98, 18, 6, '#3fa7a0')
        t.ret(150, 99, 18, 1, '#f5f0e0')
        t.ret(150, 102, 18, 1, '#f5f0e0')
        for x, y in ((30, 100), (60, 95), (120, 104), (184, 104)):
            t.ponto(x, y, '#f7a6b8')
            t.ponto(x + 1, y, '#ffd5df')
        return t

    base = desenha()
    cena = Cena(base)
    cena.animar([base, desenha(barco_dy=1)], [1.6, 1.6])
    cena.animar([desenha(onda=k) for k in range(4)], 0.7)
    cena.animar([desenha(espuma=k) for k in range(3)], 1.2, atraso=0.4)
    nuvens = Tela(W * 2, 30, '')
    nuvens.px[:] = ''
    for x, y in ((10, 12), (70, 6), (130, 14), (202, 12), (262, 6), (322, 14)):
        nuvem(nuvens, x, y, 1, '#ffffff', '#dceaf3')
    cena.definir('s-nuvens', nuvens.px)
    cena.camadas.append('<g class="ceu"><use href="#s-nuvens" x="0" y="4"/></g>')
    cena.css.append('.ceu{animation:ceu 150s steps(192) infinite}'
                    '@keyframes ceu{0%{transform:translate(0px,0px)}100%{transform:translate(-192px,0px)}}')
    gaivota = np.array([list('#.....#'), list('.#...#.'), list('..#.#..')], dtype='<U9')
    gaivota[gaivota == '#'] = '#3a3a48'
    gaivota[gaivota == '.'] = ''
    cena.definir('s-gaivota', gaivota)
    for i, (y, d, a) in enumerate(((24, 40, 0), (30, 52, 18))):
        cena.camadas.append(f'<g class="g{i}"><use href="#s-gaivota" x="-10" y="{y}"/></g>')
        cena.css.append(f'.g{i}{{animation:g{i} {d}s steps(101) {-a}s infinite}}'
                        f'@keyframes g{i}{{0%{{transform:translate(0px,0px)}}50%{{transform:translate(202px,-6px)}}'
                        f'100%{{transform:translate(202px,-6px)}}}}')
    return cena


def cena_chuva():
    jx0, jy0, jx1, jy1 = 108, 12, 176, 60

    def desenha(gato=0, vapor=None, chuva=None):
        t = Tela(W, H)
        t.degrade(0, 96, ['#191628', '#201c34', '#262140', '#2a2446'])
        t.ret(0, 93, W, 3, '#1a1626')
        # luz quente do abajur na parede
        for y in range(20, 84):
            for x in range(60, 150):
                d = math.hypot((x - 96) / 1.2, y - 62)
                if d < 30:
                    t.pontilhado(x, y, (30 - d) / 30 * 0.55, t.px[y, x], '#3a2a3a')
        # janela
        t.ret(jx0 - 3, jy0 - 3, jx1 - jx0 + 6, jy1 - jy0 + 6, '#3d3456')
        t.degrade(jy0, jy1, ['#0d1730', '#15234a', '#1f3060'], jx0, jx1)
        rnd = random.Random(77)
        x = jx0
        while x < jx1:
            w, h = rnd.randint(5, 10), rnd.randint(8, 22)
            t.ret(x, jy1 - h, min(w, jx1 - x), h, '#0a1124')
            for wy in range(jy1 - h + 2, jy1 - 1, 3):
                for wx in range(x + 1, min(x + w, jx1) - 1, 2):
                    if rnd.random() < 0.3:
                        t.ponto(wx, wy, '#e8b860')
            x += w + 1
        if chuva is not None:
            r2 = random.Random(5)
            for _ in range(46):
                dx, dy = r2.randrange(jx0, jx1), r2.randrange(jy1 - jy0)
                y = jy0 + (dy + chuva * 6) % (jy1 - jy0)
                t.ret(dx, y, 1, 2, '#7d95c4')
        t.ret(jx0 + (jx1 - jx0) // 2, jy0, 2, jy1 - jy0, '#3d3456')
        t.ret(jx0, jy0 + (jy1 - jy0) // 2, jx1 - jx0, 2, '#3d3456')
        t.ret(jx0 - 5, jy1 + 3, jx1 - jx0 + 10, 3, '#4b4068')
        # planta no peitoril
        t.ret(166, jy1 - 3, 7, 6, '#b5653f')
        t.ret(166, jy1 - 3, 7, 1, '#d07b52')
        for k, (fx, fy) in enumerate(((-2, -6), (1, -9), (4, -7), (7, -5), (3, -11))):
            linha(t, 169, jy1 - 3, 169 + fx, jy1 - 3 + fy, '#4f9a5a' if k % 2 else '#3c7d48')
        # chão e mesa
        t.ret(0, 96, W, H - 96, '#2b2235')
        for x in range(0, W, 24):
            t.ret(x, 97, 1, H - 97, '#231b2c')
        t.ret(0, 96, W, 1, '#3a2e47')
        t.ret(86, 78, 106, 3, '#7a543f')
        t.ret(86, 81, 106, 2, '#5a3d2e')
        t.ret(90, 83, 3, 13, '#4a3224')
        t.ret(186, 83, 3, 13, '#4a3224')
        # abajur
        t.ret(94, 76, 8, 2, '#3a3046')
        t.ret(97, 62, 2, 14, '#3a3046')
        for k in range(7):
            t.ret(93 - k // 2, 56 + k, 10 + k, 1, '#f2b45a' if k < 6 else '#c98a3a')
        for y in range(63, 78):
            for x in range(86, 112):
                d = math.hypot(x - 98, (y - 63) * 0.8)
                if d < 14 and abs(x - 98) < (y - 61) * 0.9:
                    t.pontilhado(x, y, (14 - d) / 14 * 0.6, t.px[y, x], '#5a4450')
        # caneca
        t.ret(112, 72, 6, 6, '#e9e4f2')
        t.ret(112, 72, 6, 1, '#8a6a4a')
        t.ret(118, 73, 2, 1, '#e9e4f2')
        t.ret(119, 74, 1, 2, '#e9e4f2')
        t.ret(118, 76, 2, 1, '#e9e4f2')
        if vapor is not None:
            for k in range(7):
                vx = 114 + round(math.sin((k + vapor * 2) * 0.9) * 1.5)
                t.ponto(vx, 70 - k, '#6e6a8a' if k < 4 else '#4a4566')
        # livros
        for i, (c, h) in enumerate((('#5a7bc0', 9), ('#c05a6a', 11), ('#e0b850', 8), ('#5aa08a', 10))):
            t.ret(170 + i * 3, 78 - h, 3, h, c)
            t.ret(170 + i * 3, 78 - h + 2, 3, 1, mistura(c, '#ffffff', 0.35))
        # gato dormindo
        gx, gy = 140, 74
        ry = 3.5 + gato * 0.6
        for y in range(int(gy - ry - 1), gy + 4):
            for x in range(gx - 9, gx + 10):
                if ((x + 0.5 - gx) / 9) ** 2 + ((y + 0.5 - (gy + 0.5)) / ry) ** 2 <= 1 and y <= gy + 3:
                    listra = (x - gx) % 4 == 0 and y < gy
                    t.ponto(x, y, '#b8662a' if listra else '#e08a3c')
        t.disco(gx + 8, gy - 1 - gato * 0.3, 3.3, '#e08a3c')
        hy = int(round(gy - 1 - gato * 0.3))
        t.ponto(gx + 6, hy - 4, '#e08a3c')
        t.ponto(gx + 6, hy - 3, '#e08a3c')
        t.ponto(gx + 10, hy - 4, '#e08a3c')
        t.ponto(gx + 10, hy - 3, '#e08a3c')
        t.ponto(gx + 7, hy, '#2a1a12')
        t.ponto(gx + 9, hy, '#2a1a12')
        t.ponto(gx + 8, hy + 1, '#f2a0a0')
        for x in range(gx - 9, gx + 6):
            t.ponto(x, gy + 3, '#f3d2a6' if x > gx - 7 else '#b8662a')
        t.ret(gx - 10, gy + 1, 2, 2, '#b8662a')
        # quadro na parede, à esquerda
        t.ret(20, 22, 30, 22, '#4b4068')
        t.degrade(24, 42, ['#e86a5a', '#f2a65a', '#f7d27a'], 22, 48)
        t.disco(35, 36, 5, '#fff2c0', filtro=lambda x, y: y < 38)
        t.ret(22, 38, 26, 4, '#3a6a8a')
        return t

    base = desenha(chuva=0, vapor=0)
    cena = Cena(base)
    cena.animar([desenha(chuva=k, vapor=0) for k in range(4)], 0.3)
    cena.animar([base, desenha(gato=1, chuva=0, vapor=0)], [1.8, 1.8])
    cena.animar([desenha(chuva=0, vapor=k) for k in range(3)], 0.6)
    return cena


LAVANDA = '#b6b9ff'


def mascara_logo(largura=68):
    im = Image.open(AQUI / 'besco-logo.png').convert('RGBA')
    altura = round(im.height * largura / im.width)
    return np.array(im.resize((largura, altura), Image.LANCZOS))[:, :, 3] > 110


def cena_besco():
    """Lago à noite entre montanhas, com o logo da Besco pulsando no céu e refletido na água."""
    logo = mascara_logo(68)
    lh, lw = logo.shape
    lx, ly = 106, 13
    horizonte = 66
    pontos = np.argwhere(logo) + [ly, lx]
    distancia = {}
    for y in range(max(0, ly - 12), ly + lh + 12):
        for x in range(max(0, lx - 12), min(W, lx + lw + 12)):
            d = np.sqrt(((pontos - [y, x]) ** 2).sum(axis=1)).min()
            if d <= 11:
                distancia[(x, y)] = d
    cheio = np.zeros((lh + 2, lw + 2), dtype=bool)
    cheio[1:-1, 1:-1] = logo
    aneis = ['#3d3888', '#2d2970', '#221f58']
    rnd_ceu = random.Random(21)
    estrelas_pos = [(rnd_ceu.randrange(W), rnd_ceu.randrange(52), rnd_ceu.choice(['#ffffff', '#c9d4ff', '#ffe9b0']))
                    for _ in range(80)]
    longe = 46 + ruido(W, 20, 8, 31) - np.exp(-((np.arange(W) - 34) / 20) ** 2) * 16 - np.exp(-((np.arange(W) - 96) / 14) ** 2) * 6
    perto = 57 + ruido(W, 12, 4, 32) - np.exp(-((np.arange(W) - 182) / 14) ** 2) * 12 - np.exp(-((np.arange(W) - 70) / 12) ** 2) * 5

    def ceu(pulso=0, estrela=0, cometa=-1):
        t = Tela(W, H)
        t.degrade(0, horizonte, ['#0b0920', '#120e33', '#1a1545', '#261d58', '#382a6c'])
        for k, (x, y, c) in enumerate(estrelas_pos):
            if (x, y) in distancia and distancia[(x, y)] < 9:
                continue
            t.ponto(x, y, '#ffffff' if (estrela and k % 7 == estrela) else c)
            if estrela and k % 7 == estrela:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    t.ponto(x + dx, y + dy, '#7d86d8')
        if cometa >= 0:
            for s in range(6):
                t.ponto(20 + cometa * 8 + s, 8 + cometa * 2 + s // 2, mistura('#120e33', '#ffffff', (s + 1) / 6))
        # halo em anéis, que cresce com o pulso
        raios = [2 + pulso * 1.0, 4 + pulso * 1.6, 6 + pulso * 1.8]
        for (x, y), d in distancia.items():
            for raio, cor in zip(raios, aneis):
                if d <= raio:
                    t.ponto(x, y, cor)
                    break
        # o logo
        for j in range(lh):
            for i in range(lw):
                if logo[j, i]:
                    miolo = cheio[j, i + 1] and cheio[j + 2, i + 1] and cheio[j + 1, i] and cheio[j + 1, i + 2]
                    base = mistura(LAVANDA, '#ffffff', 0.15 * pulso)
                    t.ponto(lx + i, ly + j, mistura(base, '#ffffff', 0.45) if miolo else base)
        # montanhas com a borda acesa pela luz do logo
        t.silhueta(longe, '#221a4c', ate=horizonte)
        t.silhueta(perto, '#150f34', ate=horizonte)
        for x in range(W):
            perto_do_logo = max(0.0, 1 - abs(x - (lx + lw / 2)) / 90)
            t.ponto(x, int(round(longe[x])), mistura('#3a2f74', LAVANDA, perto_do_logo * 0.4))
            if perto_do_logo > 0.3:
                t.ponto(x, int(round(perto[x])), mistura('#261d58', LAVANDA, perto_do_logo * 0.4))
        # cabana na margem direita
        cx, cy = 160, int(round(perto[160])) + 2
        t.ret(cx, cy - 6, 10, 7, '#2a1e3e')
        for k in range(5):
            t.ret(cx - 1 + k, cy - 7 - k, 12 - 2 * k, 1, '#3a2a52')
        t.ret(cx + 6, cy - 4, 2, 2, '#ffc46b')
        t.ret(cx + 2, cy - 4, 2, 2, '#ffc46b')
        t.ret(cx + 8, cy - 13, 2, 4, '#2a1e3e')
        return t

    def cena(pulso=0, fase=0, estrela=0, cometa=-1):
        t = ceu(pulso, estrela, cometa)
        alto = t.px.copy()
        # lago: reflexo espremido e ondulado do que está acima do horizonte
        reflexo = {'#3d3888': '#262363', '#2d2970': '#1c1a4e', '#ffc46b': '#7a5a46'}
        for y in range(horizonte, H):
            faixa = '#100d2c' if y < 80 else ('#0c0a24' if y < 94 else '#08071b')
            proxima = '#0c0a24' if y < 80 else '#08071b'
            limite = 80 if y < 80 else 94
            src = int(round(horizonte - 1 - (y - horizonte) * 1.45))
            onda = round(math.sin(y * 0.85 + fase * math.pi / 2) * (1 + (y - horizonte) / 20))
            for x in range(W):
                fundo = proxima if (limite - y <= 2 and y < 94 and (limite - y) / 3 < BAYER[y % 4, x % 4] * 0.9) else faixa
                c = alto[src, (x + onda) % W] if src >= 0 else ''
                if c in reflexo:
                    t.px[y, x] = reflexo[c]
                elif c and sum(rgb(c)) > 3 * 165:
                    t.px[y, x] = '#7173bd'
                else:
                    t.px[y, x] = fundo
        t.ret(0, horizonte, W, 1, '#2e2766')
        # brilhos soltos na água
        r2 = random.Random(90 + fase)
        for _ in range(26):
            x, y = r2.randrange(W), r2.randrange(horizonte + 2, H)
            t.ret(x, y, r2.randint(1, 3), 1, '#3a3478')
        # pinheiros escuros na margem de baixo, nos cantos
        for bx, alt in ((6, 30), (14, 22), (184, 32), (176, 24), (190, 20)):
            pinheiro(t, bx, H + 2, alt, '#07051a', tronco='#07051a')
        # canoa parada
        t.ret(128, 96, 16, 2, '#3a2618')
        t.ret(130, 98, 12, 1, '#2a1a10')
        t.ret(127, 95, 2, 1, '#3a2618')
        t.ret(143, 95, 2, 1, '#3a2618')
        return t

    sequencia = [0, 1, 2, 3, 2, 1]
    base = cena(pulso=0, fase=0)
    c = Cena(base)
    c.animar([cena(pulso=p, fase=k % 2) for k, p in enumerate(sequencia)], [0.6, 0.45, 0.45, 0.7, 0.45, 0.45])
    c.animar([base, cena(estrela=3), base, cena(estrela=5)], [2.6, 0.8, 2.2, 0.8], atraso=1)
    c.animar([base, cena(cometa=0), cena(cometa=1), cena(cometa=2)], [15, 0.1, 0.1, 0.1], atraso=6)
    # vaga-lumes
    vaga = np.array([['', '#d8ff8a', ''], ['#d8ff8a', '#fbffd0', '#d8ff8a'], ['', '#d8ff8a', '']], dtype='<U9')
    c.definir('s-vaga', vaga)
    rnd = random.Random(55)
    for i in range(7):
        x, y = rnd.choice([rnd.randint(2, 40), rnd.randint(150, 186)]), rnd.randint(70, 96)
        dx, dy = rnd.randint(-10, 10), rnd.randint(-12, -4)
        dur = rnd.uniform(6, 10)
        c.camadas.append(f'<g class="v{i}" opacity="0"><use href="#s-vaga" x="{x}" y="{y}"/></g>')
        c.css.append(f'.v{i}{{animation:v{i} {dur:.1f}s linear {-rnd.uniform(0, dur):.1f}s infinite}}'
                     f'@keyframes v{i}{{0%{{transform:translate(0px,0px);opacity:0}}30%{{opacity:0.9}}'
                     f'60%{{opacity:0.25}}80%{{opacity:0.85}}'
                     f'100%{{transform:translate({dx}px,{dy}px);opacity:0}}}}')
    return c


# ---------------------------------------------------------------- zoeira

def carinha(lado=32):
    """Carinha de óculos escuros: entra no lugar da foto enquanto não há foto."""
    s = np.full((lado + 2, lado + 2), '', dtype='<U9')
    c = (lado + 2) / 2
    for y in range(lado + 2):
        for x in range(lado + 2):
            d = math.hypot(x + 0.5 - c, y + 0.5 - c)
            if d <= lado / 2:
                s[y, x] = '#ffd23f' if d < lado / 2 - 3 or y < c else '#f2b20f'
            elif d <= lado / 2 + 1:
                s[y, x] = '#111111'
    k = lado / 32
    for y in range(int(11 * k), int(16 * k)):
        for x in range(int(6 * k), int(28 * k)):
            if not (int(15 * k) <= x <= int(18 * k) and y > 12 * k):
                s[y, x] = '#111111'
    s[int(12 * k), int(9 * k):int(12 * k)] = '#6a6a7a'
    s[int(12 * k), int(21 * k):int(24 * k)] = '#6a6a7a'
    for x in range(int(10 * k), int(25 * k)):
        y = int(22 * k + 3 * k * math.sin((x - 10 * k) / (15 * k) * math.pi))
        s[y, x] = '#7a3a12'
    return s


def zoeira_dvd(rosto, nome):
    t = Tela(W, H, '#000000')
    cena = Cena(t)
    cena.definir('f-rosto', rosto)
    lado = rosto.shape[0]
    vx, vy = W - lado, H - lado
    cena.camadas.append('<g class="dx"><g class="dy"><use href="#f-rosto" x="0" y="0"/></g></g>')
    cena.css.append(f'.dx{{animation:dx {vx / 9:.2f}s steps({vx}) infinite alternate}}'
                    f'.dy{{animation:dy {vy / 9:.2f}s steps({vy}) infinite alternate}}'
                    f'@keyframes dx{{0%{{transform:translate(0px,0px)}}100%{{transform:translate({vx}px,0px)}}}}'
                    f'@keyframes dy{{0%{{transform:translate(0px,0px)}}100%{{transform:translate(0px,{vy}px)}}}}')
    return cena


def zoeira_chuva(rosto, nome):
    t = Tela(W, H)
    t.degrade(0, H, ['#3a1c71', '#d76d77', '#ffaf7b'])
    cena = Cena(t)
    cena.definir('f-rosto', rosto)
    lado = rosto.shape[0]
    rnd = random.Random(8)
    colunas = list(range(-6, W - lado + 6, 20))
    for i, x in enumerate(colunas):
        y = rnd.randint(0, H - lado)
        dur = rnd.uniform(9, 16)
        queda = H + lado + 4
        cena.camadas.append(f'<g class="c{i}"><use href="#f-rosto" x="{x}" y="{y}"/></g>')
        cena.css.append(f'.c{i}{{animation:c{i} {dur:.1f}s steps({queda}) {-rnd.uniform(0, dur):.1f}s infinite}}'
                        f'@keyframes c{i}{{0%{{transform:translate(0px,{-y - lado - 2}px)}}'
                        f'100%{{transform:translate(0px,{queda - y - lado - 2}px)}}}}')
    return cena


def zoeira_quadro(rosto_grande, nome):
    t = Tela(W, H)
    # papel de parede verde com losangos
    for y in range(H):
        for x in range(W):
            t.px[y, x] = '#1f3b2d' if (x + y) % 12 and (x - y) % 12 else '#2c5240'
    t.ret(0, 92, W, H - 92, '#3b2618')
    t.ret(0, 92, W, 2, '#5a3a24')
    lado = rosto_grande.shape[0]
    fx, fy = 112, 8
    t.ret(fx - 6, fy - 6, lado + 12, lado + 12, '#8a5a12')
    t.ret(fx - 5, fy - 5, lado + 10, lado + 10, '#f2c24a')
    t.ret(fx - 3, fy - 3, lado + 6, lado + 6, '#b07a1a')
    t.ret(fx - 2, fy - 2, lado + 4, lado + 4, '#2a1a0a')
    t.colar(fx, fy, rosto_grande)
    for (cx, cy) in ((fx - 5, fy - 5), (fx + lado + 4, fy - 5), (fx - 5, fy + lado + 4), (fx + lado + 4, fy + lado + 4)):
        t.ret(cx - 1, cy - 1, 3, 3, '#fff0a0')
    texto1, texto2 = 'FUNCIONÁRIO', 'DO MÊS'
    py = fy + lado + 9
    largura = max(largura_texto(texto1), largura_texto(texto2)) + 8
    px0 = fx + lado // 2 - largura // 2
    t.ret(px0, py, largura, 20, '#8a5a12')
    t.ret(px0 + 1, py + 1, largura - 2, 18, '#e8b440')
    t.texto(fx + lado // 2 - largura_texto(texto1) // 2, py + 1, texto1, '#3a2200')
    t.texto(fx + lado // 2 - largura_texto(texto2) // 2, py + 9, texto2, '#3a2200')
    cena = Cena(t)
    # brilhos piscando em volta do quadro
    rnd = random.Random(3)
    quadros = []
    for k in range(3):
        f = t.copia()
        for _ in range(5):
            sx = rnd.choice([rnd.randint(fx - 16, fx - 9), rnd.randint(fx + lado + 9, fx + lado + 16)])
            sy = rnd.randint(fy, fy + lado)
            f.ponto(sx, sy, '#ffffff')
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                f.ponto(sx + dx, sy + dy, '#ffe680')
        quadros.append(f)
    cena.animar([t] + quadros, [0.6, 0.7, 0.7, 0.7])
    return cena


# ---------------------------------------------------------------- GIF

def cena_gif(caminho):
    for w, h, cores in ((192, 108, 32), (160, 90, 28), (128, 72, 24), (96, 54, 20), (64, 36, 16)):
        telas, duracoes = gif_para_quadros(caminho, w, h, cores)
        while True:
            cena = Cena(telas[0])
            cena.animar(telas, duracoes)
            svg = cena.svg()
            if len(svg) < 128_000 or len(telas) <= 2:
                break
            telas = telas[::2]
            duracoes = [a + b for a, b in zip(duracoes[::2], duracoes[1::2] + [0])]
        if len(svg) < 128_000:
            return cena, f'{w}x{h}, {len(telas)} quadros'
    raise ValueError(f'{caminho.name}: não coube no limite nem reduzido')


# ---------------------------------------------------------------- prévia e saída

def previa(cena, nome, segundos=6.0, passo=0.2):
    pasta = RAIZ / 'previas'
    pasta.mkdir(exist_ok=True)
    cena.base.png(pasta / f'{nome}.png')
    if not cena.animacoes:
        return
    imgs = []
    for n in range(int(segundos / passo)):
        tempo = n * passo
        px = cena.base.px.copy()
        for telas, duracoes, atraso in cena.animacoes:
            total = sum(duracoes)
            r = (tempo + atraso) % total
            acc = 0
            for tela, d in zip(telas, duracoes):
                if acc <= r < acc + d:
                    m = tela.px != cena.base.px
                    px[m] = tela.px[m]
                    break
                acc += d
        img = Image.new('RGB', (cena.base.w, cena.base.h))
        img.putdata([rgb(c) for c in px.flatten()])
        imgs.append(img.resize((cena.base.w * 4, cena.base.h * 4), Image.NEAREST))
    imgs[0].save(pasta / f'{nome}.gif', save_all=True, append_images=imgs[1:], duration=int(passo * 1000), loop=0)


def main():
    temas = []

    def add(ident, titulo, janela, tipo, alt, cena, vidro):
        svg = cena.svg()
        tamanho = checar_svg(svg, ident)
        previa(cena, ident)
        temas.append({'id': ident, 'titulo': titulo, 'janela': janela, 'tipo': tipo, 'alt': alt, 'svg': svg,
                      'vidro': vidro})
        print(f'  {ident:28s} {tamanho:7d} caracteres')

    escuro = lambda tinta: {'blur': 12, 'tint': tinta, 'opacity': 0.62}  # noqa: E731
    claro = lambda tinta: {'blur': 12, 'tint': tinta, 'opacity': 0.6}  # noqa: E731

    print('Cenas:')
    add('synthwave', 'Synthwave', 'dark', 'estatico', 'Pôr do sol retrô em pixel art com grade neon',
        cena_synthwave(), escuro('#1a0830'))
    add('floresta', 'Floresta', 'light', 'estatico', 'Floresta de pinheiros em pixel art com montanhas nevadas',
        cena_floresta(), claro('#eef6f2'))
    add('cidade', 'Cidade à Noite', 'dark', 'animado', 'Cidade em pixel art à noite, com janelas acendendo e um trem',
        cena_cidade(), escuro('#0c1330'))
    add('praia', 'Praia', 'light', 'animado', 'Praia em pixel art com ondas, barco e gaivotas',
        cena_praia(), claro('#f4ead2'))
    add('chuva', 'Chuva Lo-fi', 'dark', 'animado', 'Quarto em pixel art com chuva na janela e um gato dormindo',
        cena_chuva(), escuro('#1c1830'))
    add('besco', 'Besco no Lago', 'dark', 'animado',
        'Lago à noite em pixel art com o logo da Besco pulsando no céu e refletido na água',
        cena_besco(), escuro('#120e30'))

    config = RAIZ / 'fotos' / 'zoeira.json'
    pessoas = json.loads(config.read_text()) if config.exists() else []
    if not pessoas:
        pessoas = [{'nome': 'Carinha', 'id': '', 'foto': None}]
    print('Zoeira:')
    for p in pessoas:
        sufixo = f'-{p["id"]}' if p.get('id') else ''
        if p.get('foto'):
            arq = RAIZ / 'fotos' / p['foto']
            rec = p.get('recorte')
            rosto = foto_para_sprite(arq, 28, recorte=rec)
            grande = foto_para_sprite(arq, 54, cores=28, recorte=rec, redondo=False, contorno=None)
        else:
            rosto, grande = carinha(28), carinha(54)[1:-1, 1:-1]
        nome = p['nome']
        add(f'dvd{sufixo}', f'DVD: {nome}', 'dark', 'zoeira', f'{nome} quicando pela tela', zoeira_dvd(rosto, nome),
            False)
        add(f'chuva-de-cara{sufixo}', f'Chuva de {nome}', 'dark', 'zoeira', f'Chovendo {nome}',
            zoeira_chuva(rosto, nome), escuro('#2a1640'))
        add(f'funcionario-do-mes{sufixo}', f'Funcionário do Mês: {nome}', 'dark', 'zoeira',
            f'{nome} emoldurado como funcionário do mês', zoeira_quadro(grande, nome), escuro('#16281f'))

    gifs = sorted((RAIZ / 'gifs').glob('*.gif'))
    if gifs:
        print('GIFs:')
    for g in gifs:
        cena, info = cena_gif(g)
        ident = 'gif-' + ''.join(ch if ch.isalnum() else '-' for ch in g.stem.lower()).strip('-')[:56]
        add(ident, g.stem, 'dark', 'gif', f'GIF {g.stem} em pixel art', cena, escuro('#111111'))
        print(f'    ({info})')

    linhas = ['// Gerado por ferramentas/gerar.py. Não edite à mão: rode o gerador de novo.', '',
              "export type Vidro = { blur: number; tint: string; opacity: number } | false",
              "export type Cena = { id: string; titulo: string; janela: 'light' | 'dark'; "
              "tipo: 'estatico' | 'animado' | 'zoeira' | 'gif'; alt: string; svg: string; vidro: Vidro }", '',
              'export const CENAS: Cena[] = [']
    for tm in temas:
        linhas.append('  ' + json.dumps(tm, ensure_ascii=False) + ',')
    linhas.append(']')
    (RAIZ / 'hooks' / 'cenas.ts').write_text('\n'.join(linhas) + '\n')
    print(f'{len(temas)} temas em hooks/cenas.ts')


if __name__ == '__main__':
    main()
