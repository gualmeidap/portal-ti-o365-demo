# -*- coding: utf-8 -*-
"""
Gera as capturas de tela da demonstração, do zero.

Nenhuma imagem deste repositório saiu de um ambiente real: este roteiro sobe a
aplicação de demonstração com dados fictícios, percorre os fluxos e fotografa o
que aparece. Para regenerar tudo:

    python -m pip install playwright pillow
    python tools/capturas.py

Usa o Chrome já instalado na máquina (`channel="chrome"`), sem baixar navegador.
A aplicação precisa estar rodando em http://127.0.0.1:5057.
"""

import os

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5057"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURAS = os.path.join(RAIZ, "docs", "capturas")
VIEWPORT = {"width": 1360, "height": 860}

os.makedirs(CAPTURAS, exist_ok=True)
quadros_gif = []


def foto(pagina, nome, gif=False):
    caminho = os.path.join(CAPTURAS, nome + ".png")
    pagina.screenshot(path=caminho, full_page=True)
    if gif:
        quadro = os.path.join(CAPTURAS, "_gif_" + nome + ".png")
        pagina.screenshot(path=quadro, full_page=False)
        quadros_gif.append(quadro)
    print("  ->", nome + ".png")
    return caminho


def entrar(pagina, perfil="identidade"):
    """A demonstração exige sessão, como o portal. Entra e volta ao painel."""
    pagina.goto(BASE + "/login")
    pagina.check("input[name='perfil'][value='%s']" % perfil)
    pagina.click("button:has-text('Entrar no sistema')")
    pagina.wait_for_load_state("networkidle")


def montar_gif(destino, duracao=2600):
    if not quadros_gif:
        return
    imagens = [Image.open(q).convert("P", palette=Image.ADAPTIVE, colors=128) for q in quadros_gif]
    imagens[0].save(
        destino, save_all=True, append_images=imagens[1:],
        duration=duracao, loop=0, optimize=True,
    )
    for quadro in quadros_gif:
        os.remove(quadro)
    print("  ->", os.path.basename(destino))


def main():
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome", headless=True)
        contexto = navegador.new_context(viewport=VIEWPORT, device_scale_factor=2,
                                         locale="pt-BR")
        pagina = contexto.new_page()

        print("Entrada")
        pagina.goto(BASE + "/login")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "00-login")

        entrar(pagina)
        pagina.click("button:has-text('Reiniciar demonstração')")
        pagina.wait_for_load_state("networkidle")
        pagina.goto(BASE)
        pagina.wait_for_load_state("networkidle")

        print("Painel e criação")
        foto(pagina, "01-inicio")

        pagina.goto(BASE + "/criar-usuario")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "02-criar-colaborador", gif=True)

        pagina.click("button:has-text('Provisionar em')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "03-resultado-criacao", gif=True)

        pagina.click("a:has-text('Ver o e-mail de credenciais')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "04-email-credenciais", gif=True)

        print("Gestão de acesso")
        pagina.goto(BASE + "/gestao-acesso")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "05-gestao-acesso")

        pagina.goto(BASE + "/gestao-acesso/joana.prado")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "06-painel-da-pessoa")

        pagina.click("button:has-text('Bloquear em todos')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "07-bloqueio-em-todos")

        print("Travas")
        pagina.goto(BASE + "/gestao-acesso/tiago.vasconcelos")
        pagina.click("button:has-text('Bloquear em todos')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "08-alvo-protegido")

        # A tentativa contra alvo protegido derrubou a sessão de verdade.
        entrar(pagina)

        pagina.click("button:has-text('Diretório não confirma a base')")
        pagina.wait_for_load_state("networkidle")
        pagina.goto(BASE + "/criar-usuario")
        pagina.click("button:has-text('Provisionar em')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "09-falha-fechada")
        pagina.click("button:has-text('Diretório não confirma a base')")
        pagina.wait_for_load_state("networkidle")

        pagina.goto(BASE)
        pagina.select_option("select[name='perfil']", "email")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "10-escopo-no-menu")
        pagina.goto(BASE + "/criar-aluno")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "11-escopo-recusado-no-servidor")

        print("Auditoria")
        pagina.goto(BASE + "/logs")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "12-auditoria-operacional")

        pagina.select_option("select[name='perfil']", "auditoria")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "13-auditoria-seguranca")

        montar_gif(os.path.join(CAPTURAS, "fluxo-criacao.gif"))
        navegador.close()


if __name__ == "__main__":
    main()
