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

Além dos PNGs, produz dois GIFs:

  fluxo-criacao.gif   o caminho feliz, para o README do projeto
  portal-ti.gif       o caminho feliz E a recusa, para vitrine curta (perfil,
                      post, qualquer lugar onde só há uma imagem para contar
                      a história inteira)
"""

import os

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5057"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURAS = os.path.join(RAIZ, "docs", "capturas")
VIEWPORT = {"width": 1360, "height": 860}

os.makedirs(CAPTURAS, exist_ok=True)

# Quadros de GIF, separados por destino. Uma mesma tela pode alimentar os dois.
quadros = {"fluxo": [], "perfil": []}


def foto(pagina, nome, gifs=(), guardar=True):
    """
    Fotografa a tela atual.

    `guardar=False` produz só quadro de GIF, para telas que não precisam virar
    PNG solto no repositório.
    """
    if guardar:
        pagina.screenshot(path=os.path.join(CAPTURAS, nome + ".png"), full_page=True)
        print("  ->", nome + ".png")
    if gifs:
        quadro = os.path.join(CAPTURAS, "_quadro_" + nome + ".png")
        pagina.screenshot(path=quadro, full_page=False)
        for destino in gifs:
            quadros[destino].append(quadro)


def entrar(pagina, perfil="identidade"):
    """A demonstração exige sessão, como o portal. Entra e volta ao painel."""
    pagina.goto(BASE + "/login")
    pagina.check("input[name='perfil'][value='%s']" % perfil)
    pagina.click("button:has-text('Entrar no sistema')")
    pagina.wait_for_load_state("networkidle")


def montar_gif(nome_arquivo, destino, duracoes, largura=None):
    """
    Junta os quadros em um GIF.

    `duracoes` é um tempo por quadro: a tela que carrega a informação mais
    densa — a recusa — precisa de mais tempo que o formulário.
    """
    caminhos = quadros[destino]
    if not caminhos:
        return
    imagens = []
    for caminho in caminhos:
        imagem = Image.open(caminho)
        if largura and imagem.width > largura:
            altura = round(imagem.height * largura / imagem.width)
            imagem = imagem.resize((largura, altura), Image.LANCZOS)
        imagens.append(imagem.convert("P", palette=Image.ADAPTIVE, colors=128))

    saida = os.path.join(CAPTURAS, nome_arquivo)
    imagens[0].save(
        saida, save_all=True, append_images=imagens[1:],
        duration=duracoes, loop=0, optimize=True,
    )
    print("  -> {} ({} quadros, {:.0f} KB)".format(
        nome_arquivo, len(imagens), os.path.getsize(saida) / 1024))


def limpar_quadros():
    for caminhos in quadros.values():
        for caminho in caminhos:
            if os.path.exists(caminho):
                os.remove(caminho)


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
        foto(pagina, "02-criar-colaborador", gifs=("fluxo", "perfil"))

        pagina.click("button:has-text('Provisionar em')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "03-resultado-criacao", gifs=("fluxo", "perfil"))

        pagina.click("a:has-text('Ver o e-mail de credenciais')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "04-email-credenciais", gifs=("fluxo",))

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
        pagina.wait_for_load_state("networkidle")
        # Só quadro de GIF: mostra contra quem a tentativa vai, sem virar mais
        # um PNG quase igual ao painel da Joana.
        foto(pagina, "alvo-antes-da-tentativa", gifs=("perfil",), guardar=False)

        pagina.click("button:has-text('Bloquear em todos')")
        pagina.wait_for_load_state("networkidle")
        foto(pagina, "08-alvo-protegido", gifs=("perfil",))

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

        print("GIFs")
        # README do projeto: formulário, resultado, e-mail.
        montar_gif("fluxo-criacao.gif", "fluxo", duracoes=[2600, 2600, 2600])
        # Vitrine curta: acrescenta a tentativa e a recusa, que é o desfecho.
        # Reduzido a 1360px porque é exibido a ~760px e precisa ser leve.
        montar_gif("portal-ti.gif", "perfil",
                   duracoes=[2200, 2800, 2200, 3600], largura=1360)

        limpar_quadros()
        navegador.close()


if __name__ == "__main__":
    main()
