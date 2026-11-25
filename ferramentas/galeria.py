"""Monta previas/galeria.html: os temas da Besco animados, lado a lado, num arquivo só."""

import base64
import html
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCA = 'export const cena: Cena = '
temas = [json.loads(l[len(MARCA):]) for f in sorted((RAIZ / 'hooks' / 'cenas').glob('t*.ts'))
         for l in f.read_text().splitlines() if l.startswith(MARCA)]
besco = [t for t in temas if t['tipo'] == 'besco']
cartoes = ''.join(
    f'<figure><img alt="{html.escape(t["alt"])}" src="data:image/svg+xml;base64,'
    f'{base64.b64encode(t["svg"].encode()).decode()}"><figcaption><b>{html.escape(t["titulo"])}</b>'
    f'<code>/pixel {t["id"]}</code><span>{"janela escura" if t["janela"] == "dark" else "janela clara"}</span>'
    f'</figcaption></figure>' for t in besco)
pagina = f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pack Besco</title><style>
:root{{--fundo:#0b0a1c;--texto:#ecebff;--fraco:#9a98c8;--cartao:#151432}}
body{{margin:0;background:var(--fundo);color:var(--texto);font:15px/1.4 system-ui,sans-serif}}
header{{padding:32px 16px 8px;max-width:1400px;margin:auto}}h1{{margin:0 0 6px;font-size:28px}}p{{margin:0;color:var(--fraco)}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;padding:16px;max-width:1400px;margin:auto}}
figure{{margin:0;background:var(--cartao);border-radius:12px;overflow:hidden}}
img{{display:block;width:100%;aspect-ratio:16/10;object-fit:cover}}
figcaption{{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;padding:10px 12px}}
code{{color:#b6b9ff}}span{{color:var(--fraco);font-size:13px;margin-left:auto}}
</style><header><h1>Pack Besco: {len(besco)} temas animados</h1>
<p>Para aplicar, digite o comando embaixo de cada tema numa sessão da aba Code do Claude Desktop.</p></header>
<main>{cartoes}</main></html>'''
(RAIZ / 'previas' / 'galeria.html').write_text(pagina)
print(len(besco), 'temas,', len(pagina) // 1024, 'KB')
