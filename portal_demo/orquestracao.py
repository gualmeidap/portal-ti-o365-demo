# -*- coding: utf-8 -*-
"""
A orquestração.

Não sabe falar com nenhum sistema específico. Recebe os providers prontos,
percorre a mesma interface em todos e monta um resultado por sistema.

A ordem importa: **primeiro confirma todas as bases, depois escreve em
qualquer uma**. Confirmar sistema a sistema, escrevendo conforme avança,
deixaria a pessoa criada em um sistema e ausente nos outros quando o terceiro
falhasse. Se qualquer base não se confirma, nada é escrito.
"""

from dataclasses import dataclass, field

from .politicas import (
    AlvoProtegido,
    NegadoPorEscopo,
    exigir_alvo_permitido,
    exigir_operacao,
    exigir_sistemas,
)
from .providers import BaseNaoConfirmada


@dataclass
class Execucao:
    """O resultado completo de uma operação, sistema por sistema."""

    operacao: str
    verbo: str
    pessoa: dict
    resultados: list = field(default_factory=list)
    recusada: bool = False
    motivo_recusa: str = ""
    sistema_da_recusa: str = ""
    senha: str = ""

    @property
    def ok(self):
        return not self.recusada and all(r.ok for r in self.resultados)

    @property
    def por_sistema(self):
        return {r.sistema: r for r in self.resultados}


class Orquestrador:
    def __init__(self, providers):
        self.providers = providers

    def executar(self, *, operacao, verbo, pessoa, sistemas, perfil, senha=None):
        """
        Executa `verbo` nos `sistemas` pedidos, em nome de `perfil`.

        Levanta `NegadoPorEscopo` e `AlvoProtegido`: são recusas de política, e
        quem chama precisa tratá-las como tal, não como erro de integração.
        """
        # 1. Escopo. Verificado aqui também, e não só na rota: esta função é o
        #    único caminho até os providers, então é aqui que a garantia vale.
        exigir_operacao(perfil, operacao)
        exigir_sistemas(perfil, sistemas)

        # 2. Proteção de alvo, antes de qualquer contato com os sistemas.
        exigir_alvo_permitido(pessoa, verbo)

        execucao = Execucao(operacao=operacao, verbo=verbo, pessoa=pessoa, senha=senha or "")

        # 3. Falha fechada: confirmar todas as bases antes de escrever em uma.
        for chave in sistemas:
            try:
                self.providers[chave].confirmar_base()
            except BaseNaoConfirmada as recusa:
                execucao.recusada = True
                execucao.sistema_da_recusa = recusa.sistema
                execucao.motivo_recusa = recusa.motivo
                return execucao

        # 4. Só agora se escreve.
        for chave in sistemas:
            provider = self.providers[chave]
            acao = getattr(provider, verbo)
            if verbo in ("criar", "redefinir_senha"):
                execucao.resultados.append(acao(pessoa, senha))
            else:
                execucao.resultados.append(acao(pessoa))

        return execucao

    def situacao(self, pessoa, sistemas):
        """Onde a pessoa existe hoje, por sistema. Leitura, não escrita."""
        return {chave: self.providers[chave].existe(pessoa) for chave in sistemas}

    def logins_de(self, pessoa, sistemas):
        """O nome de acesso da pessoa em cada sistema. Quase nunca é o mesmo."""
        return {chave: self.providers[chave].login_de(pessoa) for chave in sistemas}


__all__ = ["Orquestrador", "Execucao", "AlvoProtegido", "NegadoPorEscopo"]
