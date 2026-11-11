# -*- coding: utf-8 -*-
"""
Português é o texto-fonte; o inglês vem de um dicionário.

`_()` traduz um texto fixo pelo dicionário (espaços colapsados, então o texto
pode quebrar linha no template). Para texto montado em tempo de execução, use
`tr(pt, en)`, que já carrega as duas versões. O idioma vem da sessão e só é
lido na hora de renderizar: trocar o idioma traduz também o que já aconteceu.
"""

from flask import g, has_request_context, request, session
from markupsafe import Markup

from .traducoes import EN

IDIOMAS = ("pt", "en")

# Textos pedidos em inglês e sem tradução. Os testes leem isto para garantir
# que nenhuma tela fique pela metade em inglês.
FALTANDO = set()


def _normalizar(texto):
    return " ".join(str(texto).split())


def idioma_atual():
    if has_request_context():
        if "idioma" not in g:
            escolhido = session.get("idioma")
            if escolhido not in IDIOMAS:
                escolhido = request.accept_languages.best_match(["pt", "pt-BR", "en"], default="pt")[:2]
            g.idioma = escolhido if escolhido in IDIOMAS else "pt"
        return g.idioma
    return "pt"


def _(texto):
    if texto is None:
        return ""
    if idioma_atual() == "en":
        chave = _normalizar(texto)
        if chave in EN:
            return EN[chave]
        FALTANDO.add(chave)
    return texto


def _h(texto):
    """Como `_`, para trechos com marcação vinda deste próprio código."""
    return Markup(_(texto))


def em_ingles(texto):
    """Versão em inglês de um texto fixo, fora do contexto de requisição."""
    return EN.get(_normalizar(texto), texto) if texto else texto


def tr(pt, en):
    return en if idioma_atual() == "en" else pt
