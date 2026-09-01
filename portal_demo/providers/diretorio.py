# -*- coding: utf-8 -*-
"""
Diretório local. No portal real, `ldap3` sobre canal cifrado.

O login daqui não é o e-mail: é o formato de domínio do diretório. É por isso
que o e-mail de credenciais precisa dizer, sistema por sistema, com qual nome
a pessoa entra.
"""

from ..dados import DOMINIO_DIRETORIO
from .base import BaseNaoConfirmada, Provider, Resultado


class DiretorioProvider(Provider):
    chave = "diretorio"
    rotulo = "Diretório local"
    protocolo = "LDAP"

    def __init__(self, estado, simulacoes):
        self.estado = estado
        self.simulacoes = simulacoes

    def login_de(self, pessoa):
        return "{}\\{}".format(DOMINIO_DIRETORIO, pessoa["login"])

    def confirmar_base(self):
        # No portal real: lê a raiz do diretório na conexão já aberta e compara
        # com a raiz configurada. Sem essa confirmação não se escreve. Um
        # diretório parecido com o certo é exatamente o cenário que essa trava
        # existe para impedir.
        if self.simulacoes.get("diretorio_sem_confirmacao"):
            raise BaseNaoConfirmada(
                self.chave,
                "A raiz do diretório que respondeu não confere com a esperada.",
            )
        return "diretório de demonstração"

    def existe(self, pessoa):
        return self.estado.get(pessoa["login"], {}).get("diretorio") not in (None, "sem_conta")

    def criar(self, pessoa, senha):
        self.estado.setdefault(pessoa["login"], {})["diretorio"] = "ativo"
        return Resultado.sucesso(
            self.chave,
            "Conta criada na unidade organizacional do setor.",
            login=self.login_de(pessoa),
        )

    def ativar(self, pessoa):
        self.estado.setdefault(pessoa["login"], {})["diretorio"] = "ativo"
        return Resultado.sucesso(self.chave, "Conta reativada.", login=self.login_de(pessoa))

    def desativar(self, pessoa):
        self.estado.setdefault(pessoa["login"], {})["diretorio"] = "bloqueado"
        return Resultado.sucesso(
            self.chave,
            "Conta desabilitada e retirada dos grupos de acesso.",
            login=self.login_de(pessoa),
        )

    def redefinir_senha(self, pessoa, senha):
        return Resultado.sucesso(
            self.chave,
            "Senha trocada no diretório.",
            login=self.login_de(pessoa),
        )
