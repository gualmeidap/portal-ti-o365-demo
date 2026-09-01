# -*- coding: utf-8 -*-
"""
As travas. Tudo aqui é verificado no servidor, a cada requisição.

O menu esconder um botão é conveniência de interface. O que impede a operação
é esta camada, que roda antes de qualquer provider ser tocado e não depende de
o pedido ter vindo da tela ou de alguém ter digitado a URL na mão.
"""

from .dados import OPERACOES, PERFIS, SISTEMAS


class NegadoPorEscopo(Exception):
    """O perfil do ator não alcança esta operação ou este sistema."""

    def __init__(self, perfil, operacao=None, sistema=None):
        self.perfil = perfil
        self.operacao = operacao
        self.sistema = sistema
        if sistema:
            motivo = "O perfil {} não alcança {}.".format(
                PERFIS[perfil]["rotulo"], SISTEMAS[sistema]["rotulo"]
            )
        else:
            motivo = "O perfil {} não executa a operação {}.".format(
                PERFIS[perfil]["rotulo"], OPERACOES.get(operacao, operacao)
            )
        self.motivo = motivo
        super().__init__(motivo)


class AlvoProtegido(Exception):
    """
    Tentativa de revogar acesso de alguém que a política protege.

    Não é um aviso que se possa confirmar e seguir. A operação é recusada, o
    episódio vira registro de segurança e quem tentou perde o acesso ao portal
    na mesma requisição.
    """

    def __init__(self, pessoa):
        self.pessoa = pessoa
        self.motivo = pessoa.get("motivo_protecao") or "Alvo protegido pela política."
        super().__init__(self.motivo)


# Operações que retiram acesso. São as que passam pela proteção de alvo.
OPERACOES_DE_REVOGACAO = {"desativar"}


def perfil_valido(perfil):
    return perfil in PERFIS


def pode_operar(perfil, operacao):
    return operacao in PERFIS[perfil]["operacoes"]


def sistemas_do_perfil(perfil):
    """Os sistemas que este perfil alcança, na ordem canônica."""
    permitidos = PERFIS[perfil]["sistemas"]
    return [chave for chave in SISTEMAS if chave in permitidos]


def exigir_operacao(perfil, operacao):
    if not pode_operar(perfil, operacao):
        raise NegadoPorEscopo(perfil, operacao=operacao)


def exigir_sistemas(perfil, sistemas):
    permitidos = PERFIS[perfil]["sistemas"]
    for sistema in sistemas:
        if sistema not in permitidos:
            raise NegadoPorEscopo(perfil, sistema=sistema)


def exigir_alvo_permitido(pessoa, verbo):
    """
    Proteção de alvo.

    Nenhum técnico revoga o acesso de outro técnico, nem o da equipe que mantém
    o portal, independentemente do perfil de quem pede.
    """
    if verbo in OPERACOES_DE_REVOGACAO and pessoa.get("protegido"):
        raise AlvoProtegido(pessoa)


def ve_auditoria_seguranca(perfil):
    return PERFIS[perfil]["ve_auditoria_seguranca"]
