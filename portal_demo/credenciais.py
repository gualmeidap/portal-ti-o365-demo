# -*- coding: utf-8 -*-
"""
Uma senha, três sistemas, um e-mail que explica onde ela vale.

O problema que isto resolve: o login não é o mesmo nos três sistemas. A pessoa
recebia um e-mail com um nome de acesso, chegava no segundo sistema, tentava o
mesmo nome e abria chamado. O e-mail de credenciais passou a dizer, para cada
sistema, com qual nome se entra e para que serve aquele acesso.
"""

import secrets

# Palavras neutras e fáceis de ditar por telefone: metade dos primeiros acessos
# acontece com alguém lendo a senha em voz alta para outra pessoa.
_PALAVRAS = (
    "Vela", "Cedro", "Aurora", "Duna", "Farol", "Pedra", "Bruma", "Trilha",
    "Ilha", "Norte", "Rumo", "Serra",
)

PARA_QUE_SERVE = {
    "m365": "E-mail, arquivos e reuniões.",
    "diretorio": "Entrar nos computadores da instituição e na rede sem fio.",
    "erp": "Sistema acadêmico e financeiro.",
}


def gerar_senha():
    """
    Senha única, usada nos três sistemas.

    Uma senha só por pessoa é decisão deliberada: três senhas diferentes viram
    três bilhetes no monitor. Ela nasce temporária e a troca é obrigatória no
    primeiro acesso.
    """
    return "{}-{}-{}".format(
        secrets.choice(_PALAVRAS),
        secrets.choice(_PALAVRAS),
        secrets.randbelow(9000) + 1000,
    )


def montar_email(pessoa, logins, senha, sistemas, providers):
    """
    O conteúdo do e-mail de credenciais, pronto para pré-visualização.

    Devolve estrutura, não texto formatado: quem renderiza decide o formato.
    """
    linhas = []
    for chave in sistemas:
        linhas.append(
            {
                "sistema": providers[chave].rotulo,
                "login": logins[chave],
                "para_que_serve": PARA_QUE_SERVE.get(chave, ""),
            }
        )
    return {
        "para": pessoa["nome"],
        "assunto": "Seus acessos estão prontos",
        "senha": senha,
        "acessos": linhas,
        "aviso": "A senha é a mesma nos três sistemas e precisa ser trocada no primeiro acesso.",
    }
