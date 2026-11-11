# -*- coding: utf-8 -*-
"""
A orquestração.

Não sabe falar com nenhum sistema específico. Recebe os providers prontos,
percorre a mesma interface em todos e monta um resultado por sistema.

A ordem importa: **primeiro confirma as bases, depois escreve**. Para criar e
redefinir senha, se qualquer base não se confirma, nada é escrito: meio
provisionamento é mais caro de desfazer do que uma recusa.

Para **bloquear**, a regra muda de sentido. Recusar o bloqueio inteiro porque
um sistema não confirmou deixaria o acesso aberto nos outros dois, que é
exatamente o risco que o bloqueio existe para fechar. Então cada sistema é
confirmado por si: os que confirmam são bloqueados na hora, e o que não
confirmou não é escrito (continua valendo a falha fechada) e vai para a fila
de retentativa, que tenta de novo e reconfere a base antes de escrever.
"""

from dataclasses import dataclass, field

from .politicas import (
    OPERACOES_DE_REVOGACAO,
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
    # Bloqueio: sistemas que não confirmaram a base e ficaram na fila.
    pendentes: list = field(default_factory=list)

    @property
    def ok(self):
        return not self.recusada and not self.pendentes and all(r.ok for r in self.resultados)

    @property
    def por_sistema(self):
        return {r.sistema: r for r in self.resultados}


class Orquestrador:
    def __init__(self, providers, fila=None):
        self.providers = providers
        self.fila = fila

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

        if verbo in OPERACOES_DE_REVOGACAO:
            return self._revogar(execucao, sistemas)

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
            acao = getattr(self.providers[chave], verbo)
            if verbo in ("criar", "redefinir_senha"):
                execucao.resultados.append(acao(pessoa, senha))
            else:
                execucao.resultados.append(acao(pessoa))
        return execucao

    def _revogar(self, execucao, sistemas):
        """Bloqueio: cada sistema por si. O que não confirma vai para a fila."""
        for chave in sistemas:
            provider = self.providers[chave]
            try:
                provider.confirmar_base()
            except BaseNaoConfirmada as recusa:
                execucao.pendentes.append({"sistema": chave, "motivo": recusa.motivo})
                if self.fila is not None:
                    self.fila.enfileirar(execucao.pessoa, chave, recusa.motivo)
                continue
            execucao.resultados.append(provider.desativar(execucao.pessoa))
        return execucao

    def situacao(self, pessoa, sistemas):
        """Onde a pessoa existe hoje, por sistema. Leitura, não escrita."""
        return {chave: self.providers[chave].existe(pessoa) for chave in sistemas}

    def logins_de(self, pessoa, sistemas):
        """O nome de acesso da pessoa em cada sistema. Quase nunca é o mesmo."""
        return {chave: self.providers[chave].login_de(pessoa) for chave in sistemas}


__all__ = ["Orquestrador", "Execucao", "AlvoProtegido", "NegadoPorEscopo"]
