"""Biblioteca de pixel art: uma tela de pixels, desenho, conversão de foto e GIF, e exportação para SVG.

O fundo da janela do Claude Desktop só aceita vetor puro. Aqui cada pixel vira um traço de 1 unidade,
agrupado por cor em linhas corridas, e cada quadro de animação guarda só o que muda em relação ao quadro base.
"""

import math
import random

import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageSequence

LIMITE_SVG = 131_072
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16


def hexa(rgb):
    return '#%02x%02x%02x' % tuple(int(v) for v in rgb[:3])


def rgb(cor):
    cor = cor.lstrip('#')
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))


def mistura(a, b, t):
    ra, rb = rgb(a), rgb(b)
    return hexa([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def ruido(n, passo, amplitude, semente):
    """Ruído 1D suave: pontos aleatórios a cada `passo`, ligados por cosseno."""
    rnd = random.Random(semente)
    pontos = [rnd.uniform(-1, 1) for _ in range(n // passo + 3)]
    saida = []
    for x in range(n):
        i, f = divmod(x / passo, 1)
        i = int(i)
        t = (1 - math.cos(f * math.pi)) / 2
        saida.append((pontos[i] * (1 - t) + pontos[i + 1] * t) * amplitude)
    return np.array(saida)


class Tela:
    def __init__(self, w=192, h=108, cor='#000000'):
        self.w, self.h = w, h
        self.px = np.full((h, w), cor, dtype='<U9')

    def copia(self):
        t = Tela(self.w, self.h)
        t.px = self.px.copy()
        return t

    def ponto(self, x, y, cor):
        x, y = int(x), int(y)
        if cor and 0 <= x < self.w and 0 <= y < self.h:
            self.px[y, x] = cor

    def ret(self, x, y, w, h, cor):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        if x1 > x0 and y1 > y0:
            self.px[y0:y1, x0:x1] = cor

    def degrade(self, y0, y1, cores, x0=0, x1=None):
        """Degradê vertical pontilhado (Bayer 4x4) entre as cores, linha y0 até y1 - 1."""
        x1 = self.w if x1 is None else x1
        n = len(cores) - 1
        for y in range(max(0, y0), min(self.h, y1)):
            t = (y - y0) / max(1, y1 - y0 - 1) * n
            i = min(int(t), n - 1)
            f = t - i
            for x in range(max(0, x0), min(self.w, x1)):
                self.px[y, x] = cores[i + 1] if f > BAYER[y % 4, x % 4] else cores[i]

    def pontilhado(self, x, y, f, a, b):
        """Escolhe entre a e b no pixel (x, y) com a fração f de b, no padrão Bayer."""
        self.ponto(x, y, b if f > BAYER[int(y) % 4, int(x) % 4] else a)

    def disco(self, cx, cy, r, cor, filtro=None):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r and (filtro is None or filtro(x, y)):
                    self.ponto(x, y, cor)

    def sprite(self, x, y, linhas, legenda):
        for j, linha in enumerate(linhas):
            for i, ch in enumerate(linha):
                cor = legenda.get(ch)
                if cor:
                    self.ponto(x + i, y + j, cor)

    def colar(self, x, y, arr):
        """Cola um array de cores; '' é transparente."""
        for j in range(arr.shape[0]):
            for i in range(arr.shape[1]):
                if arr[j, i]:
                    self.ponto(x + i, y + j, arr[j, i])

    def silhueta(self, topos, cor, ate=None):
        for x in range(self.w):
            topo = int(round(topos[x]))
            self.ret(x, topo, 1, (self.h if ate is None else ate) - topo, cor)

    def texto(self, x, y, txt, cor, sombra=None):
        cx = x
        for ch in txt:
            glifo = FONTE.get(ch.upper(), FONTE[' '])
            for j, linha in enumerate(glifo):
                for i, c in enumerate(linha):
                    if c == '#':
                        if sombra:
                            self.ponto(cx + i + 1, y + j + 1, sombra)
                        self.ponto(cx + i, y + j, cor)
            cx += len(glifo[0]) + 1
        return cx - x - 1

    def png(self, caminho, escala=6):
        img = Image.new('RGB', (self.w, self.h))
        img.putdata([rgb(c) for c in self.px.flatten()])
        img.resize((self.w * escala, self.h * escala), Image.NEAREST).save(caminho)


def largura_texto(txt):
    return sum(len(FONTE.get(ch.upper(), FONTE[' '])[0]) + 1 for ch in txt) - 1


# Fonte de 3x5 com duas linhas no alto para acento: 7 linhas de altura.
_F = {
    'A': '.#.|#.#|###|#.#|#.#', 'B': '##.|#.#|##.|#.#|##.', 'C': '.##|#..|#..|#..|.##', 'D': '##.|#.#|#.#|#.#|##.',
    'E': '###|#..|##.|#..|###', 'F': '###|#..|##.|#..|#..', 'G': '.##|#..|#.#|#.#|.##', 'H': '#.#|#.#|###|#.#|#.#',
    'I': '###|.#.|.#.|.#.|###', 'J': '..#|..#|..#|#.#|.#.', 'K': '#.#|#.#|##.|#.#|#.#', 'L': '#..|#..|#..|#..|###',
    'M': '#.#|###|###|#.#|#.#', 'N': '##.|#.#|#.#|#.#|#.#', 'O': '.#.|#.#|#.#|#.#|.#.', 'P': '##.|#.#|##.|#..|#..',
    'Q': '.#.|#.#|#.#|##.|.##', 'R': '##.|#.#|##.|#.#|#.#', 'S': '.##|#..|.#.|..#|##.', 'T': '###|.#.|.#.|.#.|.#.',
    'U': '#.#|#.#|#.#|#.#|###', 'V': '#.#|#.#|#.#|#.#|.#.', 'W': '#.#|#.#|###|###|#.#', 'X': '#.#|#.#|.#.|#.#|#.#',
    'Y': '#.#|#.#|.#.|.#.|.#.', 'Z': '###|..#|.#.|#..|###', '0': '###|#.#|#.#|#.#|###', '1': '.#.|##.|.#.|.#.|###',
    '2': '##.|..#|.#.|#..|###', '3': '##.|..#|.#.|..#|##.', '4': '#.#|#.#|###|..#|..#', '5': '###|#..|##.|..#|##.',
    '6': '.##|#..|###|#.#|###', '7': '###|..#|.#.|.#.|.#.', '8': '###|#.#|###|#.#|###', '9': '###|#.#|###|..#|##.',
    '!': '.#.|.#.|.#.|...|.#.', '?': '##.|..#|.#.|...|.#.', '.': '...|...|...|...|.#.', ',': '...|...|...|.#.|#..',
    '-': '...|...|###|...|...', ':': '...|.#.|...|.#.|...', ' ': '...|...|...|...|...', '/': '..#|..#|.#.|#..|#..',
}
_ACENTO = {'agudo': ['..#', '.#.'], 'til': ['.##', '##.'], 'circ': ['.#.', '#.#'], 'grave': ['#..', '.#.']}
FONTE = {k: ['...', '...'] + v.split('|') for k, v in _F.items()}
for base, letras in {'A': 'ÁÃÂÀ', 'E': 'ÉÊ', 'I': 'Í', 'O': 'ÓÕÔ', 'U': 'Ú'}.items():
    for letra, acento in zip(letras, ['agudo', 'til', 'circ', 'grave'] if base == 'A' else
                             (['agudo', 'circ'] if base == 'E' else (['agudo', 'til', 'circ'] if base == 'O' else ['agudo']))):
        FONTE[letra] = _ACENTO[acento] + _F[base].split('|')
FONTE['Ç'] = ['...', '...'] + _F['C'].split('|')[:4] + ['.#.']


# ---------- foto e GIF ----------

def foto_para_sprite(caminho, lado=32, cores=20, recorte=None, redondo=True, contorno='#111111', vivo=1.25):
    """Foto vira sprite quadrado de pixel art. `recorte` = (x, y, lado) em frações da imagem, para centrar o rosto."""
    img = ImageOps.exif_transpose(Image.open(caminho)).convert('RGB')
    w, h = img.size
    if recorte:
        fx, fy, fl = recorte
        l = int(min(w, h) * fl)
        x0, y0 = int(w * fx), int(h * fy)
    else:
        l = min(w, h)
        x0, y0 = (w - l) // 2, (h - l) // 2
    img = img.crop((x0, y0, x0 + l, y0 + l))
    img = ImageEnhance.Color(img).enhance(vivo)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = img.resize((lado, lado), Image.LANCZOS)
    img = img.quantize(colors=cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    arr = np.array(img)
    saida = np.full((lado + 2, lado + 2), '', dtype='<U9')
    c = lado / 2
    dentro = np.zeros((lado + 2, lado + 2), dtype=bool)
    for y in range(lado):
        for x in range(lado):
            if not redondo or (x + 0.5 - c) ** 2 + (y + 0.5 - c) ** 2 <= c * c:
                saida[y + 1, x + 1] = hexa(arr[y, x])
                dentro[y + 1, x + 1] = True
    if contorno:
        for y in range(lado + 2):
            for x in range(lado + 2):
                if not dentro[y, x] and any(
                        0 <= y + dy < lado + 2 and 0 <= x + dx < lado + 2 and dentro[y + dy, x + dx]
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    saida[y, x] = contorno
    return saida


def gif_para_quadros(caminho, w, h, cores=32):
    """Lê um GIF, corta para preencher w x h, reduz para uma paleta comum. Devolve (telas, durações em segundos)."""
    img = Image.open(caminho)
    quadros, duracoes = [], []
    for q in ImageSequence.Iterator(img):
        duracoes.append(max(0.1, q.info.get('duration', 100) / 1000))
        q = q.convert('RGB')
        quadros.append(ImageOps.fit(q, (w, h), Image.NEAREST if max(q.size) <= 2 * max(w, h) else Image.LANCZOS))
    mosaico = Image.new('RGB', (w, h * len(quadros)))
    for i, q in enumerate(quadros):
        mosaico.paste(q, (0, i * h))
    paleta = mosaico.quantize(colors=cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    telas = []
    for q in quadros:
        arr = np.array(q.quantize(palette=paleta, dither=Image.Dither.NONE).convert('RGB'))
        t = Tela(w, h)
        t.px = np.array([[hexa(arr[y, x]) for x in range(w)] for y in range(h)], dtype='<U9')
        telas.append(t)
    return telas, duracoes


# ---------- exportação ----------

def _corridas(px, ignora=None, mascara=None, dx=0, dy=0):
    por_cor = {}
    altura, largura = px.shape
    for y in range(altura):
        x = 0
        while x < largura:
            c = px[y, x]
            if not c or c == ignora or (mascara is not None and not mascara[y, x]):
                x += 1
                continue
            x2 = x + 1
            while x2 < largura and px[y, x2] == c and (mascara is None or mascara[y, x2]):
                x2 += 1
            por_cor.setdefault(c, []).append(f'M{x + dx} {y + dy}.5h{x2 - x}')
            x = x2
    return por_cor


def caminhos(px, ignora=None, mascara=None, dx=0, dy=0):
    return ''.join(f'<path stroke="{c}" d="{"".join(d)}"/>' for c, d in _corridas(px, ignora, mascara, dx, dy).items())


def mais_comum(px):
    valores, contagem = np.unique(px[px != ''], return_counts=True)
    return valores[contagem.argmax()]


def _quadros_keyframes(nome, inicio, fim, total):
    a, b = inicio / total * 100, fim / total * 100
    passos = ['0%{opacity:0}'] if a > 0 else []
    passos.append(f'{a:.2f}%{{opacity:1}}')
    passos.append(f'{b:.2f}%{{opacity:0}}')
    if b < 100:
        passos.append('100%{opacity:0}')
    return f'@keyframes {nome}{{{"".join(passos)}}}'


class Cena:
    """Uma cena: tela base, animações por quadros (só a diferença) e camadas livres (sprites que andam)."""

    def __init__(self, base):
        self.base = base
        self.animacoes = []  # (telas, durações, atraso)
        self.defs = []
        self.camadas = []
        self.css = []

    def animar(self, telas, duracoes, atraso=0.0):
        """telas[0] pode ser a própria base; cada quadro aparece pela sua duração, em ciclo."""
        if isinstance(duracoes, (int, float)):
            duracoes = [duracoes] * len(telas)
        self.animacoes.append((telas, duracoes, atraso))

    def definir(self, ident, arr):
        """Guarda um sprite em <defs> com o id dado (com hífen), para reusar com <use>."""
        self.defs.append(f'<g id="{ident}">{caminhos(arr)}</g>')

    def svg(self):
        base = self.base
        fundo = mais_comum(base.px)
        partes = [f'<rect width="{base.w}" height="{base.h}" fill="{fundo}"/>',
                  f'<g fill="none" stroke-width="1">{caminhos(base.px, ignora=fundo)}']
        css = list(self.css)
        for k, (telas, duracoes, atraso) in enumerate(self.animacoes):
            total = sum(duracoes)
            t = 0.0
            for i, (tela, d) in enumerate(zip(telas, duracoes)):
                mascara = tela.px != base.px
                if mascara.any():
                    nome = f'k{k}q{i}'
                    partes.append(f'<g class="{nome}" opacity="0">{caminhos(tela.px, mascara=mascara)}</g>')
                    css.append(f'.{nome}{{animation:{nome} {total:.2f}s step-end {-atraso:.2f}s infinite}}')
                    css.append(_quadros_keyframes(nome, t, t + d, total))
                t += d
        partes.append('</g>')
        defs = f'<defs><g fill="none" stroke-width="1">{"".join(self.defs)}</g></defs>' if self.defs else ''
        estilo = f'<style>{"".join(css)}</style>' if css else ''
        corpo = ''.join(partes) + ''.join(self.camadas)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {base.w} {base.h}" '
                f'preserveAspectRatio="xMidYMid slice" shape-rendering="crispEdges">{estilo}{defs}{corpo}</svg>')


def checar_svg(svg, nome):
    proibidos = ['<image', 'data:', 'base64', 'foreignObject', '@import', '@font-face', '\\', 'url(']
    achados = [p for p in proibidos if p in svg]
    if achados:
        raise ValueError(f'{nome}: o SVG tem {achados}, que o app recusa')
    if len(svg) > LIMITE_SVG:
        raise ValueError(f'{nome}: o SVG tem {len(svg)} caracteres, acima do limite de {LIMITE_SVG}')
    return len(svg)
