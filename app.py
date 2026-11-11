# -*- coding: utf-8 -*-
"""
Portal TI — demonstração pública.

Recorte navegável do portal interno de gestão de identidade descrito no README.
As integrações com Microsoft 365, diretório local e ERP são simuladas por
providers em memória; as travas de segurança são as mesmas do desenho original
e rodam de verdade neste código.

Roda de dois jeitos, com o mesmo código: como servidor Flask comum, ou dentro
do navegador do visitante (Pyodide), que é como a demonstração pública é
servida pelo GitHub Pages. Ver `web/` e `tools/build_site.py`.

Nenhum dado aqui vem de um ambiente real.
"""

import os
from datetime import datetime

from flask import Flask, abort, redirect, render_template, request, session, url_for

from portal_demo import busca, credenciais, dados
from portal_demo.auditoria import Auditoria
from portal_demo.fila import FilaRetentativa
from portal_demo.i18n import IDIOMAS, _, _h, em_ingles, idioma_atual, tr
from portal_demo.orquestracao import AlvoProtegido, NegadoPorEscopo, Orquestrador
from portal_demo.politicas import (
    exigir_operacao,
    exigir_sistemas,
    perfil_valido,
    sistemas_do_perfil,
    ve_auditoria_seguranca,
)
from portal_demo.providers import montar

app = Flask(__name__)
app.secret_key = "demonstracao-publica-sem-segredo"
app.jinja_env.globals.update(_=_, _h=_h, tr=tr, idioma_atual=idioma_atual)

PASTA_INSTANCIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance")
os.makedirs(PASTA_INSTANCIA, exist_ok=True)
CAMINHO_AUDITORIA = os.path.join(PASTA_INSTANCIA, "auditoria_demo.sqlite3")

PERFIL_PADRAO = "identidade"

# ---------------------------------------------------------------------------
# Estado da demonstração. No portal real isto mora nos três sistemas; aqui é um
# dicionário em memória, reiniciável pelo botão do rodapé.
# ---------------------------------------------------------------------------
ESTADO = {}
SIMULACOES = {}
PESSOAS = {}
FILA = FilaRetentativa()
# Perfil que tentou agir sobre um alvo protegido fica suspenso do portal até a
# auditoria liberar. No portal real a suspensão é por técnico; aqui o "técnico"
# da demonstração é o perfil escolhido na entrada.
SUSPENSOS = {}

SIMULACOES_VALIDAS = ("m365_sem_confirmacao", "diretorio_sem_confirmacao", "erp_sem_confirmacao", "email_falhando")


def reiniciar_demo():
    """Devolve a demonstração ao ponto de partida."""
    ESTADO.clear()
    SIMULACOES.clear()
    PESSOAS.clear()
    SUSPENSOS.clear()
    FILA.itens.clear()
    for pessoa in dados.PESSOAS:
        copia = dict(pessoa)
        PESSOAS[copia["login"]] = copia
        ESTADO[copia["login"]] = dict(copia["estado"])
    AUDITORIA.limpar()
    AUDITORIA.semear(HISTORICO_FICTICIO)


HISTORICO_FICTICIO = [
    (14, dict(ator_perfil="identidade", ator_rotulo="Analista de Identidade",
              operacao="Novo Usuário - Colaborador", alvo="Otávio Bittencourt", resultado="parcial",
              por_sistema={"m365": "ok", "diretorio": "ok", "erp": "sem conta"},
              detalhe="ERP fora do escopo do cargo informado.")),
    (52, dict(ator_perfil="suporte", ator_rotulo="Suporte N1",
              operacao="Alterar Senha", alvo="Rafael Antunes", resultado="ok",
              por_sistema={"m365": "ok", "diretorio": "ok", "erp": "ok"},
              detalhe="Senha única, troca obrigatória no primeiro acesso.")),
    (96, dict(ator_perfil="email", ator_rotulo="Operador de E-mail",
              operacao="Bloquear acesso", alvo="Marina Coelho", resultado="ok",
              por_sistema={"m365": "bloqueado"},
              detalhe="Perfil alcança apenas o Microsoft 365.")),
    (120, dict(ator_perfil="email", ator_rotulo="Operador de E-mail",
               operacao="Bloquear acesso", alvo="Marina Coelho", resultado="negado",
               categoria="seguranca", por_sistema={"diretorio": "negado"},
               detalhe="Pedido por URL direta a um sistema fora do escopo do perfil.")),
    (203, dict(ator_perfil="identidade", ator_rotulo="Analista de Identidade",
               operacao="Novo Usuário - Aluno", alvo="Lívia Ferraz", resultado="ok",
               por_sistema={"m365": "ok", "erp": "ok"},
               detalhe="Aluno não recebe conta no diretório.")),
    (330, dict(ator_perfil="identidade", ator_rotulo="Analista de Identidade",
               operacao="Bloquear acesso", alvo="Tiago Vasconcelos", resultado="recusado",
               categoria="seguranca", por_sistema={},
               detalhe="Alvo protegido. Sessão de quem pediu encerrada na hora.")),
]

AUDITORIA = Auditoria(CAMINHO_AUDITORIA)
reiniciar_demo()


# ---------------------------------------------------------------------------
# Contexto
# ---------------------------------------------------------------------------
def perfil_atual():
    perfil = session.get("perfil", PERFIL_PADRAO)
    return perfil if perfil_valido(perfil) else PERFIL_PADRAO


def orquestrador():
    return Orquestrador(montar(ESTADO, SIMULACOES), fila=FILA)


def pessoa_ou_404(login):
    pessoa = PESSOAS.get(login)
    if pessoa is None:
        abort(404)
    pessoa = dict(pessoa)
    pessoa["estado"] = ESTADO.get(login, {})
    return pessoa


def sistemas_pedidos(perfil):
    """Sistemas marcados no formulário, limitados ao escopo do perfil."""
    pedidos = request.form.getlist("sistemas")
    if not pedidos:
        pedidos = sistemas_do_perfil(perfil)
    return [s for s in dados.SISTEMAS if s in pedidos]


def registrar(perfil, **campos):
    AUDITORIA.registrar(ator_perfil=perfil, ator_rotulo=dados.PERFIS[perfil]["rotulo"], **campos)


@app.context_processor
def contexto():
    perfil = perfil_atual()
    agora = datetime.now()
    em_ingles_agora = idioma_atual() == "en"
    return {
        "dados": dados,
        "perfil": perfil,
        "perfil_info": dados.PERFIS[perfil],
        "perfis": dados.PERFIS,
        "sistemas_do_perfil": sistemas_do_perfil(perfil),
        "ve_seguranca": ve_auditoria_seguranca(perfil),
        "simulacoes": SIMULACOES,
        "suspensos": SUSPENSOS,
        "fila_pendentes": len(FILA.pendentes()),
        "idioma": idioma_atual(),
        "agora": agora.strftime("%m/%d/%Y %I:%M %p") if em_ingles_agora else agora.strftime("%d/%m/%Y às %H:%Mh"),
    }


# ---------------------------------------------------------------------------
# Recusas de política viram tela, não erro genérico.
# ---------------------------------------------------------------------------
@app.errorhandler(NegadoPorEscopo)
def tratar_escopo(erro):
    registrar(erro.perfil, operacao="Acesso negado", alvo=request.path, resultado="negado",
              categoria="seguranca", detalhe=erro.motivo, detalhe_en=erro.motivo_en)
    return render_template("erro_escopo.html", erro=erro, caminho=request.path), 403


@app.errorhandler(AlvoProtegido)
def tratar_alvo_protegido(erro):
    perfil = perfil_atual()
    motivo = erro.motivo.rstrip(".")
    registrar(perfil, operacao="Bloquear acesso", alvo=erro.pessoa["nome"], resultado="recusado",
              categoria="seguranca",
              detalhe="Alvo protegido: {}. Sessão encerrada e perfil suspenso do portal.".format(motivo),
              detalhe_en="Protected target: {}. Session ended and profile suspended from the portal.".format(
                  em_ingles(motivo)))
    # Quem tenta perde o acesso ao portal na mesma requisição, e não volta só
    # por entrar de novo: a suspensão fica até a auditoria liberar.
    SUSPENSOS[perfil] = {"quando": datetime.now().strftime("%d/%m/%Y %H:%M"), "alvo": erro.pessoa["nome"]}
    _limpar_sessao()
    return render_template("erro_alvo_protegido.html", erro=erro), 403


def _limpar_sessao():
    """Encerra a sessão, preservando só a escolha de idioma."""
    idioma_escolhido = session.get("idioma")
    session.clear()
    if idioma_escolhido:
        session["idioma"] = idioma_escolhido


# ---------------------------------------------------------------------------
# Sessão, idioma e entrada
# ---------------------------------------------------------------------------
# Únicos endpoints alcançáveis sem sessão. Tudo o mais passa pelo guarda abaixo.
ENDPOINTS_LIVRES = {"login", "static", "idioma"}


@app.before_request
def exigir_sessao():
    """
    Sem sessão, nenhuma tela.

    O portal real autentica antes de qualquer coisa; a demonstração faz o mesmo,
    trocando a senha por uma escolha de perfil. Vale para todas as rotas de uma
    vez: rota nova nasce protegida por omissão, e não por lembrança de quem a
    escreveu. Perfil suspenso também não passa.
    """
    if request.endpoint in ENDPOINTS_LIVRES or request.endpoint is None:
        return None
    perfil = session.get("perfil", "")
    if not perfil_valido(perfil) or perfil in SUSPENSOS:
        session.pop("perfil", None)
        return redirect(url_for("login", proximo=request.full_path.rstrip("?")))
    return None


@app.route("/idioma/<codigo>")
def idioma(codigo):
    if codigo in IDIOMAS:
        session["idioma"] = codigo
    voltar = request.args.get("voltar") or ""
    return redirect(voltar if voltar.startswith("/") else url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Entrada da demonstração: escolher com qual perfil técnico navegar."""
    aviso = None
    if request.method == "POST":
        escolhido = request.form.get("perfil", "")
        if escolhido in SUSPENSOS:
            aviso = escolhido
        elif perfil_valido(escolhido):
            session["perfil"] = escolhido
            destino = request.form.get("proximo") or ""
            return redirect(destino if destino.startswith("/") else url_for("dashboard"))
    return render_template("login.html", proximo=request.args.get("proximo", ""), aviso=aviso)


@app.route("/perfil", methods=["POST"])
def trocar_perfil():
    escolhido = request.form.get("perfil", PERFIL_PADRAO)
    if perfil_valido(escolhido) and escolhido not in SUSPENSOS:
        session["perfil"] = escolhido
    return redirect(request.form.get("voltar") or url_for("dashboard"))


@app.route("/logout")
def logout():
    """Encerra a sessão e devolve à tela de entrada."""
    _limpar_sessao()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Telas
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    perfil = perfil_atual()
    contas = {
        chave: sum(1 for e in ESTADO.values() if e.get(chave) == "ativo")
        for chave in dados.SISTEMAS
    }
    return render_template(
        "dashboard.html",
        contas=contas,
        incompletos=sum(1 for e in ESTADO.values() if dados.desligamento_incompleto(e)),
        total_pessoas=len(PESSOAS),
        eventos=AUDITORIA.listar(incluir_seguranca=ve_auditoria_seguranca(perfil), limite=4),
    )


@app.route("/criar-usuario", methods=["GET", "POST"])
def criar_colaborador():
    return _tela_de_criacao("criar_colaborador", "colaborador")


@app.route("/criar-aluno", methods=["GET", "POST"])
def criar_aluno():
    return _tela_de_criacao("criar_aluno", "aluno")


def _tela_de_criacao(operacao, tipo):
    perfil = perfil_atual()
    exigir_operacao(perfil, operacao)

    if request.method == "GET":
        return render_template("criar.html", operacao=operacao, tipo=tipo)

    nome = (request.form.get("nome") or "").strip()
    login = _login_de(nome)
    pessoa = {
        "nome": nome,
        "login": login,
        "tipo": tipo,
        "unidade": request.form.get("unidade") or "",
        "dominio": request.form.get("dominio") or dados.DOMINIOS.get(tipo),
        "registro": dados.registro_de(login),
        "estado": {},
        "protegido": False,
        "erp_candidatos": [],
        "erp_vinculo": None,
    }

    sistemas = sistemas_pedidos(perfil)
    senha = credenciais.gerar_senha()
    orq = orquestrador()
    execucao = orq.executar(
        operacao=operacao, verbo="criar", pessoa=pessoa,
        sistemas=sistemas, perfil=perfil, senha=senha,
    )

    entrega = None
    if execucao.ok:
        PESSOAS[login] = pessoa
        entrega = _entregar_credenciais(pessoa, orq, senha, sistemas)
    else:
        session.pop("ultimo_email", None)

    _auditar(execucao, dados.OPERACOES[operacao], perfil, entrega=entrega)
    return render_template("resultado.html", execucao=execucao, sistemas=sistemas,
                           titulo=dados.OPERACOES[operacao], entrega=entrega)


@app.route("/alterar-senha", methods=["GET", "POST"])
def redefinir_senha():
    perfil = perfil_atual()
    exigir_operacao(perfil, "redefinir_senha")

    if request.method == "GET":
        login = request.args.get("login")
        if login:
            return _form_de_senha(perfil, pessoa_ou_404(login))
        ctx, redirecionar = _busca(perfil, "redefinir_senha")
        if redirecionar:
            return redirecionar
        return render_template("senha.html", pessoa=None, **ctx)

    pessoa = pessoa_ou_404(request.form.get("login", ""))
    # Só entram os sistemas onde a pessoa tem conta e que o perfil alcança: o que
    # vem marcado no formulário é pedido, não permissão.
    sistemas = [s_ for s_ in dados.SISTEMAS
                if s_ in request.form.getlist("sistemas") and s_ in sistemas_do_perfil(perfil)
                and pessoa["estado"].get(s_) in ("ativo", "bloqueado")]
    if not sistemas:
        return _form_de_senha(perfil, pessoa, erro=True)
    senha = credenciais.gerar_senha()
    orq = orquestrador()
    execucao = orq.executar(
        operacao="redefinir_senha", verbo="redefinir_senha", pessoa=pessoa,
        sistemas=sistemas, perfil=perfil, senha=senha,
    )
    entrega = _entregar_credenciais(pessoa, orq, senha, sistemas) if execucao.ok else None
    _auditar(execucao, "Redefinir senha", perfil, entrega=entrega)
    return render_template("resultado.html", execucao=execucao, sistemas=sistemas,
                           titulo="Redefinir senha", entrega=entrega)


def _form_de_senha(perfil, pessoa, erro=False):
    return render_template("senha.html", pessoa=pessoa, erro=erro,
                           pessoa_logins=orquestrador().logins_de(pessoa, list(dados.SISTEMAS)),
                           email_destino=dados.email_pessoal_mascarado(pessoa["login"]))


def _busca(perfil, endpoint):
    """
    Busca de pessoas, comum à Gestão de Acesso e à redefinição de senha.

    A origem pedida é conferida contra o escopo do perfil NO SERVIDOR: um
    perfil que só alcança o Microsoft 365 não consegue olhar o diretório nem o
    ERP, nem forjando a URL. Com um único resultado, vai direto para a pessoa.
    """
    permitidas = [o for o in dados.ORIGENS if o in sistemas_do_perfil(perfil)]
    origem = request.args.get("origem") or (permitidas[0] if permitidas else "m365")
    termo = (request.args.get("termo") or "").strip()
    ctx = {"origens": permitidas, "origem": origem, "termo": termo, "resultado": None, "acao": url_for(endpoint)}
    if not termo:
        return ctx, None
    if origem not in dados.ORIGENS:
        abort(400)
    exigir_sistemas(perfil, [origem])
    resultado = busca.buscar(termo, origem, PESSOAS, ESTADO, SIMULACOES)
    for c in resultado["candidatos"]:
        c["url"] = (url_for("acesso_pessoa", login=c["login"], origem=origem, termo=termo)
                    if endpoint == "acesso" else url_for("redefinir_senha", login=c["login"]))
    if len(resultado["candidatos"]) == 1:
        return ctx, redirect(resultado["candidatos"][0]["url"])
    ctx["resultado"] = resultado
    return ctx, None


@app.route("/gestao-acesso")
def acesso():
    perfil = perfil_atual()
    exigir_operacao(perfil, "acesso")
    ctx, redirecionar = _busca(perfil, "acesso")
    if redirecionar:
        return redirecionar
    pendencias = [p for p in _pessoas_visiveis() if dados.desligamento_incompleto(p["estado"])]
    return render_template("acesso.html", pendencias=pendencias, **ctx)


@app.route("/gestao-acesso/<login>")
def acesso_pessoa(login):
    perfil = perfil_atual()
    exigir_operacao(perfil, "acesso")
    pessoa = pessoa_ou_404(login)
    return render_template("acesso_pessoa.html", pessoa=pessoa,
                           na_fila=[i for i in FILA.pendentes() if i["login"] == login])


@app.route("/gestao-acesso/<login>/vincular-erp", methods=["POST"])
def vincular_erp(login):
    """
    O técnico escolhe qual cadastro do ERP é desta pessoa. A escolha vem do
    navegador, então é reconferida aqui contra a lista de candidatos: um
    formulário adulterado não vincula a pessoa a um cadastro qualquer.
    """
    perfil = perfil_atual()
    exigir_operacao(perfil, "acesso")
    exigir_sistemas(perfil, ["erp"])
    pessoa = PESSOAS.get(login)
    if pessoa is None:
        abort(404)
    escolhido = request.form.get("registro", "")
    candidato = next((c for c in pessoa.get("erp_candidatos", []) if c["registro"] == escolhido), None)
    if candidato is None:
        registrar(perfil, operacao="Vincular cadastro do ERP", alvo=pessoa["nome"], resultado="negado",
                  categoria="seguranca", por_sistema={"erp": "negado"},
                  detalhe="Cadastro {} não está entre os candidatos desta pessoa.".format(escolhido or "vazio"),
                  detalhe_en="Record {} is not among this person's candidates.".format(escolhido or "(empty)"))
        abort(400)
    pessoa["erp_vinculo"] = candidato["registro"]
    ESTADO[login]["erp"] = "ativo"
    registrar(perfil, operacao="Vincular cadastro do ERP", alvo=pessoa["nome"], resultado="ok",
              por_sistema={"erp": "ok"},
              detalhe="Vinculado a {} ({}).".format(candidato["registro"], candidato["nome"]),
              detalhe_en="Linked to {} ({}).".format(candidato["registro"], candidato["nome"]))
    return redirect(url_for("acesso_pessoa", login=login))


@app.route("/gestao-acesso/<login>/<verbo>", methods=["POST"])
def alterar_acesso(login, verbo):
    perfil = perfil_atual()
    exigir_operacao(perfil, "acesso")
    if verbo not in ("ativar", "desativar"):
        abort(404)

    pessoa = pessoa_ou_404(login)
    alvo = request.form.get("sistema", "todos")
    sistemas = sistemas_do_perfil(perfil) if alvo == "todos" else [alvo]

    execucao = orquestrador().executar(
        operacao="acesso", verbo=verbo, pessoa=pessoa,
        sistemas=sistemas, perfil=perfil,
    )
    titulo = "Bloquear acesso" if verbo == "desativar" else "Reativar acesso"
    comprovante = _comprovante_rh(perfil, execucao, titulo)
    _auditar(execucao, titulo, perfil)
    return render_template("resultado.html", execucao=execucao, sistemas=sistemas, titulo=titulo,
                           comprovante=comprovante, entrega=None,
                           voltar=url_for("acesso_pessoa", login=login))


@app.route("/fila")
def fila():
    perfil = perfil_atual()
    # Quem opera a fila e quem audita enxergam; os demais recebem o 403 de escopo.
    if not ve_auditoria_seguranca(perfil):
        exigir_operacao(perfil, "fila")
    return render_template("fila.html", itens=FILA.itens, resumo=session.pop("resumo_fila", None))


@app.route("/fila/processar", methods=["POST"])
def processar_fila():
    exigir_operacao(perfil_atual(), "fila")
    session["resumo_fila"] = FILA.processar(montar(ESTADO, SIMULACOES), PESSOAS, AUDITORIA)
    return redirect(url_for("fila"))


@app.route("/logs")
def auditoria():
    # Nem a contagem de registros de segurança sai daqui para um perfil que não
    # pode vê-los: um número já diria que houve o que apurar, e quando.
    incluir = ve_auditoria_seguranca(perfil_atual())
    return render_template("auditoria.html", eventos=AUDITORIA.listar(incluir_seguranca=incluir))


@app.route("/suspensoes/<perfil_suspenso>/liberar", methods=["POST"])
def liberar_suspensao(perfil_suspenso):
    """Só a auditoria libera, e a liberação fica registrada com quem liberou."""
    perfil = perfil_atual()
    if not ve_auditoria_seguranca(perfil):
        abort(403)
    info = SUSPENSOS.pop(perfil_suspenso, None)
    if info:
        registrar(perfil, operacao="Suspensão liberada", alvo=dados.PERFIS[perfil_suspenso]["rotulo"],
                  resultado="ok", categoria="seguranca",
                  detalhe="Suspenso desde {} por tentar bloquear {}.".format(info["quando"], info["alvo"]),
                  detalhe_en="Suspended since {} for trying to block {}.".format(info["quando"], info["alvo"]))
    return redirect(url_for("auditoria"))


@app.route("/credenciais")
def email_credenciais():
    email = session.get("ultimo_email")
    if not email:
        return redirect(url_for("dashboard"))
    return render_template("email.html", email=email)


@app.route("/demo/simular", methods=["POST"])
def simular():
    chave = request.form.get("chave", "")
    if chave in SIMULACOES_VALIDAS:
        SIMULACOES[chave] = not SIMULACOES.get(chave)
    return redirect(request.form.get("voltar") or url_for("dashboard"))


@app.route("/demo/reiniciar", methods=["POST"])
def reiniciar():
    reiniciar_demo()
    session.pop("ultimo_email", None)
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Apoio
# ---------------------------------------------------------------------------
def _login_de(nome):
    partes = [p for p in nome.lower().split() if len(p) > 2]
    sem_acento = str.maketrans("áàâãéêíóôõúüç", "aaaaeeiooouuc")
    if len(partes) >= 2:
        bruto = "{}.{}".format(partes[0], partes[-1])
    else:
        bruto = partes[0] if partes else "novo.usuario"
    return bruto.translate(sem_acento)


def _pessoas_visiveis():
    lista = []
    for login, pessoa in PESSOAS.items():
        copia = dict(pessoa)
        copia["estado"] = ESTADO.get(login, {})
        lista.append(copia)
    return sorted(lista, key=lambda p: p["nome"])


def _entregar_credenciais(pessoa, orq, senha, sistemas):
    """
    Monta e "envia" o e-mail de credenciais.

    Senha trocada sem o aviso chegar não é sucesso: a pessoa fica sem entrar e
    sem saber por quê. Por isso a entrega volta como resultado próprio, e a
    operação só fica verde quando ela também deu certo.
    """
    session["ultimo_email"] = credenciais.montar_email(
        pessoa, orq.logins_de(pessoa, sistemas), senha, sistemas, orq.providers
    )
    return {"ok": not SIMULACOES.get("email_falhando")}


def _comprovante_rh(perfil, execucao, titulo):
    """O RH responde pelo desligamento fora do portal: recebe o comprovante na caixa."""
    if not dados.PERFIS[perfil].get("recebe_comprovante") or execucao.recusada:
        return None
    entregue = not SIMULACOES.get("email_falhando")
    if not entregue:
        registrar(perfil, operacao="Comprovante ao RH não entregue", alvo=execucao.pessoa["nome"],
                  resultado="parcial", detalhe=titulo)
    return {"para": dados.CAIXA_RH, "ok": entregue}


def _auditar(execucao, titulo, perfil, entrega=None):
    detalhe_en = None
    if execucao.recusada:
        resultado, por_sistema = "recusado", {execucao.sistema_da_recusa: "recusado"}
        detalhe = "Falha fechada: {}".format(execucao.motivo_recusa)
        detalhe_en = "Fail closed: {}".format(em_ingles(execucao.motivo_recusa))
    else:
        por_sistema = {r.sistema: ("ok" if r.ok else "falhou") for r in execucao.resultados}
        por_sistema.update({p["sistema"]: "na fila" for p in execucao.pendentes})
        detalhe = execucao.pessoa.get("unidade") or ""
        if execucao.pendentes:
            detalhe = "Bloqueado onde a base confirmou; o restante foi para a fila de retentativa."
        falhas = [r for r in execucao.resultados if not r.ok]
        if falhas:
            detalhe = falhas[0].mensagem
        if entrega and not entrega["ok"]:
            detalhe = "Senha aplicada, mas o e-mail de credenciais não foi entregue: a pessoa não consegue entrar."
        ok = execucao.ok and (entrega is None or entrega["ok"])
        resultado = "ok" if ok else "parcial"
    registrar(perfil, operacao=titulo, alvo=execucao.pessoa["nome"], resultado=resultado,
              por_sistema=por_sistema, detalhe=detalhe, detalhe_en=detalhe_en)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5057)
    app.run(host="127.0.0.1", port=parser.parse_args().port, debug=False)
