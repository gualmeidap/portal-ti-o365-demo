# -*- coding: utf-8 -*-
"""
Microsoft 365. No portal real, `msal` para o token e Graph API para as escritas.

Nesta demonstração as chamadas de rede são substituídas por um estado em
memória. O que se mantém fiel é o formato: o mesmo contrato, o mesmo login
próprio do sistema e a mesma confirmação de base antes de escrever.
"""

from ..dados import DOMINIOS, DOMINIO_EMAIL
from .base import BaseNaoConfirmada, Provider, Resultado


class MicrosoftProvider(Provider):
    chave = "m365"
    rotulo = "Microsoft 365"
    protocolo = "Graph API"

    def __init__(self, estado, simulacoes):
        self.estado = estado
        self.simulacoes = simulacoes

    def login_de(self, pessoa):
        # Colaborador e aluno vivem em domínios distintos: o vínculo decide.
        dominio = pessoa.get("dominio") or DOMINIOS.get(pessoa.get("tipo"), DOMINIO_EMAIL)
        return "{}@{}".format(pessoa["login"], dominio)

    def confirmar_base(self):
        # No portal real: confirma que o token vale para o ambiente esperado
        # antes de qualquer escrita. Ambiente divergente, token sem escopo ou
        # consulta sem resposta são motivo de recusa, não de tentativa.
        if self.simulacoes.get("m365_sem_confirmacao"):
            raise BaseNaoConfirmada(
                self.chave,
                "O ambiente que respondeu não é o esperado para esta operação.",
            )
        return "ambiente de demonstração"

    def existe(self, pessoa):
        return self.estado.get(pessoa["login"], {}).get("m365") not in (None, "sem_conta")

    def criar(self, pessoa, senha):
        self.estado.setdefault(pessoa["login"], {})["m365"] = "ativo"
        return Resultado.sucesso(
            self.chave,
            "Caixa criada e licença atribuída.",
            login=self.login_de(pessoa),
        )

    def ativar(self, pessoa):
        self.estado.setdefault(pessoa["login"], {})["m365"] = "ativo"
        return Resultado.sucesso(
            self.chave,
            "Entrada liberada e licença devolvida.",
            login=self.login_de(pessoa),
        )

    def desativar(self, pessoa):
        self.estado.setdefault(pessoa["login"], {})["m365"] = "bloqueado"
        return Resultado.sucesso(
            self.chave,
            "Entrada bloqueada e sessões ativas revogadas.",
            login=self.login_de(pessoa),
        )

    def redefinir_senha(self, pessoa, senha):
        return Resultado.sucesso(
            self.chave,
            "Senha trocada, com troca obrigatória no primeiro acesso.",
            login=self.login_de(pessoa),
        )
