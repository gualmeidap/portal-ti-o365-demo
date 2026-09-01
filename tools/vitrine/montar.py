# -*- coding: utf-8 -*-
"""
Monta a página de vitrine a partir de `pagina.src.html`.

A vitrine é uma versão da história deste repositório em formato de página única,
para mandar a quem não vai abrir o GitHub. O fonte traz marcadores `__IMG_nome__`
que este roteiro troca pelas capturas de `docs/capturas/`, embutidas como data
URI — a página final não depende deste repositório nem de rede para carregar.

    python -m pip install pillow
    python tools/vitrine/montar.py

A saída (`pagina.html`, alguns megabytes) não é versionada: é reconstruível a
qualquer momento a partir do fonte mais as capturas, que essas sim são versionadas.

A página publicada fica na galeria de artifacts da conta. Para atualizar a MESMA
página a partir de outra conversa, é preciso passar a URL dela — publicar sem a
URL cria uma página nova em vez de atualizar a existente.
"""

import base64
import io
import os
import re

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
CAPTURAS = os.path.join(RAIZ, "docs", "capturas")
ORIGEM = os.path.join(AQUI, "pagina.src.html")
DESTINO = os.path.join(AQUI, "pagina.html")

# As capturas nascem em 2x para telas retina; 1700px é o suficiente para a
# largura em que a página as mostra, e corta o peso pela metade.
LARGURA_MAX = 1700


def data_uri(nome):
    """A imagem `nome`, pronta para ir embutida no atributo src."""
    gif = os.path.join(CAPTURAS, nome + ".gif")
    if os.path.exists(gif):
        with open(gif, "rb") as arquivo:
            bruto = arquivo.read()
        return "data:image/gif;base64," + base64.b64encode(bruto).decode(), len(bruto)

    imagem = Image.open(os.path.join(CAPTURAS, nome + ".png"))
    if imagem.width > LARGURA_MAX:
        altura = round(imagem.height * LARGURA_MAX / imagem.width)
        imagem = imagem.resize((LARGURA_MAX, altura), Image.LANCZOS)
    buffer = io.BytesIO()
    imagem.convert("RGB").save(buffer, format="PNG", optimize=True)
    bruto = buffer.getvalue()
    return "data:image/png;base64," + base64.b64encode(bruto).decode(), len(bruto)


def main():
    with io.open(ORIGEM, encoding="utf-8") as arquivo:
        html = arquivo.read()

    total = 0
    for nome in sorted(set(re.findall(r"__IMG_([a-z0-9-]+)__", html))):
        uri, tamanho = data_uri(nome)
        html = html.replace("__IMG_" + nome + "__", uri)
        total += tamanho
        print("  {:<34} {:>7.0f} KB".format(nome, tamanho / 1024))

    faltando = re.findall(r"__IMG_([a-z0-9-]+)__", html)
    if faltando:
        raise SystemExit("marcadores sem imagem correspondente: " + ", ".join(faltando))

    with io.open(DESTINO, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

    print("\n  imagens: {:.1f} MB | página: {:.1f} MB".format(
        total / 1048576, os.path.getsize(DESTINO) / 1048576))
    print("  ->", DESTINO)


if __name__ == "__main__":
    main()
