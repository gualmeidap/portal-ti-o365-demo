# -*- coding: utf-8 -*-
"""
Fila de retentativa.

Um bloqueio que não pôde ser escrito num sistema não é esquecido: vira um item
na fila, e um processo agendado (no portal real, um cron a cada 5 minutos)
tenta de novo.

Duas regras que a fila não pode quebrar:

* **Só bloqueio entra.** A fila existe para que um acesso que devia ser
  cortado não fique aberto. Reativação que falha deixa alguém sem acesso, o
  que é problema operacional e aparece na tela de quem pediu.
* **A política é reconferida a cada tentativa.** A fila transforma um pedido
  em intenção persistente; sem reconferir, ela poderia concluir, minutos
  depois, um bloqueio que não deveria acontecer. Base não confirmada
  continua não sendo escrita.
"""

from datetime import datetime

from .i18n import em_ingles
from .politicas import AlvoProtegido, exigir_alvo_permitido
from .providers import BaseNaoConfirmada

MAX_TENTATIVAS = 5
ATOR = "Sistema (retentativa automática)"


class FilaRetentativa:
    def __init__(self):
        self.itens = []

    def enfileirar(self, pessoa, sistema, motivo):
        # Um pedido repetido não duplica a intenção.
        for item in self.itens:
            if item["login"] == pessoa["login"] and item["sistema"] == sistema and item["estado"] == "pendente":
                return item
        item = {
            "id": len(self.itens) + 1,
            "quando": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "login": pessoa["login"],
            "nome": pessoa["nome"],
            "sistema": sistema,
            "verbo": "desativar",
            "tentativas": 0,
            "estado": "pendente",
            "ultimo_erro": motivo,
        }
        self.itens.insert(0, item)
        return item

    def pendentes(self):
        return [i for i in self.itens if i["estado"] == "pendente"]

    def processar(self, providers, pessoas, auditoria):
        """Uma passada do processo agendado. Devolve um resumo por estado."""
        resumo = {"concluido": 0, "pendente": 0, "cancelado": 0, "desistiu": 0}
        for item in self.pendentes():
            pessoa = pessoas.get(item["login"])
            provider = providers[item["sistema"]]
            por_sistema = {}
            try:
                if pessoa is None or item["verbo"] != "desativar":
                    raise AlvoProtegido({"motivo_protecao": "Item fora do escopo da fila."})
                exigir_alvo_permitido(pessoa, "desativar")
            except AlvoProtegido as recusa:
                item["estado"], item["ultimo_erro"] = "cancelado", recusa.motivo
                por_sistema[item["sistema"]] = "cancelado"
                resultado, detalhe = "recusado", "Retentativa cancelada: {}".format(recusa.motivo)
                detalhe_en = "Retry cancelled: {}".format(em_ingles(recusa.motivo))
            else:
                item["tentativas"] += 1
                try:
                    provider.confirmar_base()
                    escrita = provider.desativar(pessoa)
                    sucesso, erro = escrita.ok, ("" if escrita.ok else escrita.mensagem)
                except BaseNaoConfirmada as recusa:
                    sucesso, erro = False, recusa.motivo
                if sucesso:
                    item["estado"], item["ultimo_erro"] = "concluido", ""
                    por_sistema[item["sistema"]] = "bloqueado"
                    resultado = "ok"
                    detalhe = "Retentativa {}: bloqueio concluído.".format(item["tentativas"])
                    detalhe_en = "Retry {}: block completed.".format(item["tentativas"])
                else:
                    item["ultimo_erro"] = erro
                    if item["tentativas"] >= MAX_TENTATIVAS:
                        item["estado"] = "desistiu"
                    por_sistema[item["sistema"]] = "na fila" if item["estado"] == "pendente" else "falhou"
                    resultado = "parcial"
                    detalhe = "Retentativa {}: {}".format(item["tentativas"], erro)
                    detalhe_en = "Retry {}: {}".format(item["tentativas"], em_ingles(erro))
            resumo[item["estado"]] += 1
            auditoria.registrar(
                ator_perfil="sistema", ator_rotulo=ATOR, operacao="Retentativa de bloqueio",
                alvo=item["nome"], resultado=resultado, por_sistema=por_sistema,
                detalhe=detalhe, detalhe_en=detalhe_en,
            )
        return resumo
