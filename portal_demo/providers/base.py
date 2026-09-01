# -*- coding: utf-8 -*-
"""
A interface que todo sistema integrado implementa.

A orquestração conversa só com esta interface. Ela não sabe o que é Graph API,
o que é LDAP nem o que é SOAP: só sabe pedir `existe`, `criar`, `ativar`,
`desativar` e `redefinir_senha`, e ler o `Resultado` que volta.

Acrescentar um quarto sistema é escrever mais um arquivo nesta pasta.
"""

from dataclasses import dataclass, field


class BaseNaoConfirmada(Exception):
    """
    Levantada quando o provider não consegue confirmar contra qual base vai
    escrever. A orquestração trata isso como recusa, nunca como aviso.
    """

    def __init__(self, sistema, motivo):
        self.sistema = sistema
        self.motivo = motivo
        super().__init__(motivo)


@dataclass
class Resultado:
    """O que um provider devolve depois de uma operação."""

    sistema: str
    ok: bool
    mensagem: str
    detalhes: dict = field(default_factory=dict)

    @classmethod
    def sucesso(cls, sistema, mensagem, **detalhes):
        return cls(sistema=sistema, ok=True, mensagem=mensagem, detalhes=detalhes)

    @classmethod
    def falha(cls, sistema, mensagem, **detalhes):
        return cls(sistema=sistema, ok=False, mensagem=mensagem, detalhes=detalhes)


class Provider:
    """
    Contrato comum. Cada sistema traduz estes cinco verbos para o seu próprio
    protocolo, e monta o login do jeito que aquele sistema espera.
    """

    chave = ""
    rotulo = ""
    protocolo = ""

    # -- identidade -------------------------------------------------------
    def login_de(self, pessoa):
        """Como esta pessoa se chama NESTE sistema. Raramente é igual nos três."""
        raise NotImplementedError

    # -- trava de segurança -----------------------------------------------
    def confirmar_base(self):
        """
        Devolve uma descrição da base alvo, ou levanta `BaseNaoConfirmada`.

        Chamado antes de qualquer escrita. Se o provider não consegue dizer com
        certeza onde vai escrever, a operação não acontece.
        """
        raise NotImplementedError

    # -- operações --------------------------------------------------------
    def existe(self, pessoa):
        raise NotImplementedError

    def criar(self, pessoa, senha):
        raise NotImplementedError

    def ativar(self, pessoa):
        raise NotImplementedError

    def desativar(self, pessoa):
        raise NotImplementedError

    def redefinir_senha(self, pessoa, senha):
        raise NotImplementedError
