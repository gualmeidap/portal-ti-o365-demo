# -*- coding: utf-8 -*-
"""
ERP acadêmico-financeiro. No portal real, SOAP sobre `requests` para escrita e
consultas diretas para o que o serviço não expõe.

Terceiro formato de login: nem e-mail, nem domínio de diretório, mas o usuário
curto que o ERP aceita.
"""

from .base import BaseNaoConfirmada, Provider, Resultado


class ErpProvider(Provider):
    chave = "erp"
    rotulo = "ERP acadêmico"
    protocolo = "SOAP + SQL"

    def __init__(self, estado, simulacoes):
        self.estado = estado
        self.simulacoes = simulacoes

    def login_de(self, pessoa):
        nome, _, sobrenome = pessoa["login"].partition(".")
        return (nome[0] + sobrenome)[:12] if sobrenome else nome[:12]

    def confirmar_base(self):
        # No portal real: a consulta de identificação da base precisa responder
        # e bater com o ambiente configurado. Homologação e produção têm o mesmo
        # desenho e a mesma cara; só a resposta dessa consulta as distingue.
        if self.simulacoes.get("erp_sem_confirmacao"):
            raise BaseNaoConfirmada(
                self.chave,
                "A base que respondeu não é a que esta operação deveria escrever.",
            )
        return "base de demonstração"

    def existe(self, pessoa):
        return self.estado.get(pessoa["login"], {}).get("erp") not in (None, "sem_conta")

    def criar(self, pessoa, senha):
        self.estado.setdefault(pessoa["login"], {})["erp"] = "ativo"
        return Resultado.sucesso(
            self.chave,
            "Usuário criado com o perfil de acesso do cargo.",
            login=self.login_de(pessoa),
        )

    def ativar(self, pessoa):
        self.estado.setdefault(pessoa["login"], {})["erp"] = "ativo"
        return Resultado.sucesso(self.chave, "Usuário reativado.", login=self.login_de(pessoa))

    def desativar(self, pessoa):
        self.estado.setdefault(pessoa["login"], {})["erp"] = "bloqueado"
        return Resultado.sucesso(self.chave, "Usuário inativado.", login=self.login_de(pessoa))

    def redefinir_senha(self, pessoa, senha):
        return Resultado.sucesso(self.chave, "Senha trocada no ERP.", login=self.login_de(pessoa))
