# -*- coding: utf-8 -*-
"""
Busca de pessoas nas três bases.

É a função principal da Gestão de Acesso e da redefinição de senha: o técnico
digita um pedaço do nome, do e-mail ou do login e encontra a pessoa na base que
ele escolher, sem precisar saber de antemão onde ela existe. Quem aparece na
busca de uma base pode nem existir nas outras, e o painel da pessoa mostra isso.

O mínimo de caracteres é regra do servidor, e não só da tela: a rota é chamável
direto, e um termo curto devolve gente arbitrária que não identifica ninguém.
"""

import unicodedata

from .dados import MIN_CARACTERES_BUSCA
from .providers import montar

LIMITE = 20


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().split())


def buscar(termo, origem, pessoas, estado, simulacoes):
    """
    Devolve {"curto": bool, "candidatos": [...]}.

    Cada candidato diz como a pessoa aparece NA BASE pesquisada (e-mail, login
    de rede, usuário do ERP), porque é esse nome que o técnico reconhece.
    """
    termo = (termo or "").strip()
    if len(termo) < MIN_CARACTERES_BUSCA:
        return {"curto": True, "candidatos": []}

    t = normalizar(termo)
    providers = montar(estado, simulacoes)
    achados = []
    for login, pessoa in pessoas.items():
        situacao = estado.get(login, {}).get(origem, "sem_conta")
        if situacao == "sem_conta":
            continue  # não existe nesta base: não aparece nela
        identificador = providers[origem].login_de(pessoa)
        campos = [identificador, pessoa["nome"]]
        if origem == "erp":
            campos.append(pessoa.get("registro", ""))
        if not any(t in normalizar(c) for c in campos):
            continue
        achados.append({
            "login": login,
            "nome": pessoa["nome"],
            "unidade": pessoa.get("unidade", ""),
            "tipo": pessoa.get("tipo", ""),
            "como": identificador,
            "cadastros": len(pessoa.get("erp_candidatos", [])) if origem == "erp" and not pessoa.get("erp_vinculo") else 0,
            "situacao": situacao,
        })
    achados.sort(key=lambda a: normalizar(a["nome"]))
    return {"curto": False, "candidatos": achados[:LIMITE]}
