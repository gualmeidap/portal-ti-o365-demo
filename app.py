# -*- coding: utf-8 -*-
"""
Portal TI — demonstração pública.

Recorte navegável do portal interno de gestão de identidade descrito no README.
As integrações com Microsoft 365, diretório local e ERP são simuladas por
providers em memória; as travas de segurança são as mesmas do desenho original
e rodam de verdade neste código.

Nenhum dado aqui vem de um ambiente real.
"""

import os
from datetime import datetime

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from portal_demo import credenciais, dados
from portal_demo.auditoria import Auditoria
from portal_demo.orquestracao import AlvoProtegido, NegadoPorEscopo, Orquestrador
from portal_demo.politicas import (
    exigir_operacao,
    perfil_valido,
    sistemas_do_perfil,
    ve_auditoria_seguranca,
)
from portal_demo.providers import montar

app = Flask(__name__)
app.secret_key = "demonstracao-publica-sem-segredo"

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


def reiniciar_demo():
    """Devolve a demonstração ao ponto de partida."""
    ESTADO.clear()
    SIMULACOES.clear()
    PESSOAS.clear()
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
    return Orquestrador(montar(ESTADO, SIMULACOES))


def pessoa_ou_404(login):
    pessoa = PESSOAS.get(login)
    if pessoa is None:
        from flask import abort

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


@app.context_processor
def contexto():
    perfil = perfil_atual()
    return {
        "dados": dados,
        "perfil": perfil,
        "perfil_info": dados.PERFIS[perfil],
        "perfis": dados.PERFIS,
        "sistemas_do_perfil": sistemas_do_perfil(perfil),
        "ve_seguranca": ve_auditoria_seguranca(perfil),
        "simulacoes": SIMULACOES,
        "agora": datetime.now().strftime("%d/%m/%Y às %H:%Mh"),
    }


# ---------------------------------------------------------------------------
# Recusas de política viram tela, não erro genérico.
# ---------------------------------------------------------------------------
@app.errorhandler(NegadoPorEscopo)
def tratar_escopo(erro):
    AUDITORIA.registrar(
        ator_perfil=erro.perfil,
        ator_rotulo=dados.PERFIS[erro.perfil]["rotulo"],
        operacao="Acesso negado",
        alvo=request.path,
        resultado="negado",
        categoria="seguranca",
        detalhe=erro.motivo,
    )
    return render_template("erro_escopo.html", erro=erro, caminho=request.path), 403


@app.errorhandler(AlvoProtegido)
def tratar_alvo_protegido(erro):
    perfil = perfil_atual()
    AUDITORIA.registrar(
        ator_perfil=perfil,
        ator_rotulo=dados.PERFIS[perfil]["rotulo"],
        operacao="Bloquear acesso",
        alvo=erro.pessoa["nome"],
        resultado="recusado",
        categoria="seguranca",
        detalhe="Alvo protegido: {}. Sessão encerrada.".format(erro.motivo.rstrip(".")),
    )
    # Quem tenta perde o acesso ao portal na mesma requisição.
    session.clear()
    return render_template("erro_alvo_protegido.html", erro=erro), 403


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
    bloqueadas = sum(
        1 for e in ESTADO.values() if any(v == "bloqueado" for v in e.values())
    )
    return render_template(
        "dashboard.html",
        contas=contas,
        bloqueadas=bloqueadas,
        total_pessoas=len(PESSOAS),
        eventos=AUDITORIA.listar(incluir_seguranca=ve_auditoria_seguranca(perfil), limite=4),
    )


@app.route("/perfil", methods=["POST"])
def trocar_perfil():
    escolhido = request.form.get("perfil", PERFIL_PADRAO)
    if perfil_valido(escolhido):
        session["perfil"] = escolhido
    return redirect(request.form.get("voltar") or url_for("dashboard"))


@app.route("/logout")
def logout():
    """Encerra a sessão e devolve à tela de entrada."""
    session.clear()
    return redirect(url_for("login"))


# Únicos endpoints alcançáveis sem sessão. Tudo o mais passa pelo guarda abaixo.
ENDPOINTS_LIVRES = {"login", "static"}


@app.before_request
def exigir_sessao():
    """
    Sem sessão, nenhuma tela.

    O portal real autentica antes de qualquer coisa; a demonstração faz o mesmo,
    trocando a senha por uma escolha de perfil. Vale para todas as rotas de uma
    vez: rota nova nasce protegida por omissão, e não por lembrança de quem a
    escreveu.
    """
    if request.endpoint in ENDPOINTS_LIVRES or request.endpoint is None:
        return None
    if not perfil_valido(session.get("perfil", "")):
        return redirect(url_for("login", proximo=request.full_path.rstrip("?")))
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    """Entrada da demonstração: escolher com qual perfil técnico navegar."""
    if request.method == "POST":
        escolhido = request.form.get("perfil", "")
        if perfil_valido(escolhido):
            session["perfil"] = escolhido
            destino = request.form.get("proximo") or ""
            return redirect(destino if destino.startswith("/") else url_for("dashboard"))
    return render_template("login.html", proximo=request.args.get("proximo", ""))


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
    }

    sistemas = sistemas_pedidos(perfil)
    senha = credenciais.gerar_senha()
    orq = orquestrador()
    execucao = orq.executar(
        operacao=operacao, verbo="criar", pessoa=pessoa,
        sistemas=sistemas, perfil=perfil, senha=senha,
    )

    if execucao.ok:
        PESSOAS[login] = pessoa
        email = credenciais.montar_email(
            pessoa, orq.logins_de(pessoa, sistemas), senha, sistemas, orq.providers
        )
        session["ultimo_email"] = email
    else:
        session.pop("ultimo_email", None)

    _auditar(execucao, dados.OPERACOES[operacao], perfil, sistemas)
    return render_template("resultado.html", execucao=execucao, sistemas=sistemas,
                           titulo=dados.OPERACOES[operacao])


@app.route("/alterar-senha", methods=["GET", "POST"])
def redefinir_senha():
    perfil = perfil_atual()
    exigir_operacao(perfil, "redefinir_senha")

    if request.method == "GET":
        return render_template("senha.html", pessoas=_pessoas_visiveis())

    pessoa = pessoa_ou_404(request.form.get("login", ""))
    sistemas = sistemas_pedidos(perfil)
    senha = credenciais.gerar_senha()
    orq = orquestrador()
    execucao = orq.executar(
        operacao="redefinir_senha", verbo="redefinir_senha", pessoa=pessoa,
        sistemas=sistemas, perfil=perfil, senha=senha,
    )
    if execucao.ok:
        session["ultimo_email"] = credenciais.montar_email(
            pessoa, orq.logins_de(pessoa, sistemas), senha, sistemas, orq.providers
        )
    _auditar(execucao, "Redefinir senha", perfil, sistemas)
    return render_template("resultado.html", execucao=execucao, sistemas=sistemas,
                           titulo="Redefinir senha")


@app.route("/gestao-acesso")
def acesso():
    exigir_operacao(perfil_atual(), "acesso")
    return render_template("acesso.html", pessoas=_pessoas_visiveis())


@app.route("/gestao-acesso/<login>")
def acesso_pessoa(login):
    perfil = perfil_atual()
    exigir_operacao(perfil, "acesso")
    pessoa = pessoa_ou_404(login)
    return render_template("acesso_pessoa.html", pessoa=pessoa)


@app.route("/gestao-acesso/<login>/<verbo>", methods=["POST"])
def alterar_acesso(login, verbo):
    perfil = perfil_atual()
    exigir_operacao(perfil, "acesso")
    if verbo not in ("ativar", "desativar"):
        from flask import abort

        abort(404)

    pessoa = pessoa_ou_404(login)
    alvo = request.form.get("sistema", "todos")
    sistemas = sistemas_do_perfil(perfil) if alvo == "todos" else [alvo]

    execucao = orquestrador().executar(
        operacao="acesso", verbo=verbo, pessoa=pessoa,
        sistemas=sistemas, perfil=perfil,
    )
    titulo = "Bloquear acesso" if verbo == "desativar" else "Reativar acesso"
    _auditar(execucao, titulo, perfil, sistemas)
    return render_template("resultado.html", execucao=execucao, sistemas=sistemas,
                           titulo=titulo, voltar=url_for("acesso_pessoa", login=login))


@app.route("/logs")
def auditoria():
    # Nem a contagem de registros de segurança sai daqui para um perfil que não
    # pode vê-los: um número já diria que houve o que apurar, e quando.
    incluir = ve_auditoria_seguranca(perfil_atual())
    return render_template(
        "auditoria.html",
        eventos=AUDITORIA.listar(incluir_seguranca=incluir),
    )


@app.route("/credenciais")
def email_credenciais():
    email = session.get("ultimo_email")
    if not email:
        return redirect(url_for("dashboard"))
    return render_template("email.html", email=email)


@app.route("/demo/simular", methods=["POST"])
def simular():
    chave = request.form.get("chave", "")
    if chave in ("m365_sem_confirmacao", "diretorio_sem_confirmacao", "erp_sem_confirmacao"):
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


def _auditar(execucao, titulo, perfil, sistemas):
    if execucao.recusada:
        resultado, por_sistema = "recusado", {execucao.sistema_da_recusa: "recusado"}
        detalhe = "Falha fechada: {}".format(execucao.motivo_recusa)
    else:
        resultado = "ok" if execucao.ok else "parcial"
        por_sistema = {r.sistema: ("ok" if r.ok else "falhou") for r in execucao.resultados}
        detalhe = execucao.pessoa.get("unidade") or ""
    AUDITORIA.registrar(
        ator_perfil=perfil,
        ator_rotulo=dados.PERFIS[perfil]["rotulo"],
        operacao=titulo,
        alvo=execucao.pessoa["nome"],
        resultado=resultado,
        por_sistema=por_sistema,
        detalhe=detalhe,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5057, debug=False)
