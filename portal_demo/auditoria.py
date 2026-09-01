# -*- coding: utf-8 -*-
"""
Auditoria.

Uma linha por ação, com o resultado de cada sistema na mesma linha. Quem lê
não precisa cruzar três logs para saber o que aconteceu.

Eventos de categoria `seguranca` (tentativa contra alvo protegido, acesso
negado por escopo, sessão encerrada) só aparecem para o perfil de auditoria.
Quem pode ser objeto da investigação não vê a investigação.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

ESQUEMA = """
CREATE TABLE IF NOT EXISTS eventos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    quando        TEXT    NOT NULL,
    ator_perfil   TEXT    NOT NULL,
    ator_rotulo   TEXT    NOT NULL,
    operacao      TEXT    NOT NULL,
    alvo          TEXT    NOT NULL,
    categoria     TEXT    NOT NULL DEFAULT 'operacional',
    resultado     TEXT    NOT NULL,
    m365          TEXT,
    diretorio     TEXT,
    erp           TEXT,
    detalhe       TEXT
);
"""


class Auditoria:
    def __init__(self, caminho):
        self.caminho = caminho
        with self._conexao() as con:
            con.executescript(ESQUEMA)

    @contextmanager
    def _conexao(self):
        # `with sqlite3.connect(...)` faz commit, mas não fecha: no Windows a
        # conexão pendurada segura o arquivo e impede qualquer limpeza.
        con = sqlite3.connect(self.caminho)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def registrar(self, *, ator_perfil, ator_rotulo, operacao, alvo, resultado,
                  categoria="operacional", por_sistema=None, detalhe="", quando=None):
        por_sistema = por_sistema or {}
        with self._conexao() as con:
            con.execute(
                "INSERT INTO eventos (quando, ator_perfil, ator_rotulo, operacao, alvo,"
                " categoria, resultado, m365, diretorio, erp, detalhe)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    (quando or datetime.now()).strftime("%d/%m/%Y %H:%M"),
                    ator_perfil,
                    ator_rotulo,
                    operacao,
                    alvo,
                    categoria,
                    resultado,
                    por_sistema.get("m365"),
                    por_sistema.get("diretorio"),
                    por_sistema.get("erp"),
                    detalhe,
                ),
            )

    def listar(self, *, incluir_seguranca, limite=60):
        """
        O filtro de categoria é aplicado na consulta, não na tela.

        Uma linha que o perfil não pode ver nunca chega ao template, então não
        há como ela vazar por um `view-source` ou por um endpoint de dados.
        """
        consulta = "SELECT * FROM eventos"
        if not incluir_seguranca:
            consulta += " WHERE categoria <> 'seguranca'"
        consulta += " ORDER BY id DESC LIMIT ?"
        with self._conexao() as con:
            return [dict(linha) for linha in con.execute(consulta, (limite,))]

    def limpar(self):
        """Só a demonstração usa isto, para voltar ao ponto de partida."""
        with self._conexao() as con:
            con.execute("DELETE FROM eventos")

    def semear(self, entradas):
        """Histórico fictício, para a demonstração não abrir com a tabela vazia."""
        with self._conexao() as con:
            (total,) = con.execute("SELECT COUNT(*) FROM eventos").fetchone()
        if total:
            return
        agora = datetime.now()
        for minutos_atras, entrada in entradas:
            self.registrar(quando=agora - timedelta(minutes=minutos_atras), **entrada)
