# -*- coding: utf-8 -*-
"""
Ponte para rodar o portal dentro do navegador (Pyodide), no GitHub Pages.

O mesmo `app.py` que roda como servidor é carregado aqui sem nenhuma mudança.
A página `web/index.html` intercepta cliques em links e envios de formulário e
chama `pedir()`, que entrega a requisição ao Flask pelo cliente de teste dele
(mesmo roteamento, mesmos `before_request`, mesma sessão por cookie). Não há
servidor: cada visitante tem o portal inteiro, sozinho, na própria aba.
"""

from werkzeug.datastructures import MultiDict

from app import app

_cliente = app.test_client()


def pedir(metodo, caminho, campos, idioma_navegador):
    """Devolve (status, caminho_final, html)."""
    resposta = _cliente.open(
        caminho,
        method=metodo,
        data=MultiDict([tuple(par) for par in (campos or [])]) if metodo == "POST" else None,
        headers={"Accept-Language": idioma_navegador or "pt-BR"},
        follow_redirects=True,
    )
    final = resposta.request.path
    if resposta.request.query_string:
        final += "?" + resposta.request.query_string.decode()
    return resposta.status_code, final, resposta.get_data(as_text=True)
