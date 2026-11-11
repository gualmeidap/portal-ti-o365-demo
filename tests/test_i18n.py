"""Every screen, rendered in English, must have no untranslated fixed text."""
import app as portal
from portal_demo import dados
from portal_demo.i18n import FALTANDO

from .conftest import entrar

# Values that pass through _() but are proper names or paths, not UI text.
NAO_TRADUZIVEIS = {p["nome"] for p in dados.PESSOAS} | {"Camila Rezende", "Diego Mattos"}


def faltando():
    return {t for t in FALTANDO if t not in NAO_TRADUZIVEIS and not t.startswith("/")}


def test_every_screen_in_english_is_fully_translated(client):
    FALTANDO.clear()
    client.get("/idioma/en")
    client.get("/login")
    for perfil in dados.PERFIS:
        entrar(client, perfil)
        for path in ("/", "/gestao-acesso", "/gestao-acesso?origem=m365&termo=ana", "/gestao-acesso?origem=m365&termo=meridiana",
                     "/gestao-acesso?origem=erp&termo=zzzz", "/alterar-senha", "/alterar-senha?origem=m365&termo=meridiana",
                     "/alterar-senha?login=sofia.menezes", "/gestao-acesso/paulo.matos", "/gestao-acesso/marina.coelho",
                     "/criar-usuario", "/criar-aluno", "/alterar-senha", "/fila", "/logs"):
            client.get(path)
    # Flows that produce results, refusals, queue items, receipts and e-mails.
    entrar(client, "identidade")
    client.post("/criar-usuario", data={"nome": "Camila Rezende", "unidade": "Biblioteca Central"})
    client.get("/credenciais")
    client.post("/demo/simular", data={"chave": "diretorio_sem_confirmacao"})
    client.post("/criar-aluno", data={"nome": "Diego Mattos", "unidade": "Direito"})
    client.post("/demo/simular", data={"chave": "diretorio_sem_confirmacao"})
    client.post("/demo/simular", data={"chave": "erp_sem_confirmacao"})
    entrar(client, "rh")
    client.post("/gestao-acesso/joana.prado/desativar", data={"sistema": "todos"})
    client.post("/gestao-acesso/paulo.matos/desativar", data={"sistema": "todos"})
    client.post("/demo/simular", data={"chave": "email_falhando"})
    client.post("/gestao-acesso/rafael.antunes/desativar", data={"sistema": "todos"})
    entrar(client, "identidade")
    client.post("/fila/processar")
    client.get("/fila")
    client.post("/alterar-senha", data={"login": "joana.prado", "sistemas": ["m365", "diretorio", "erp"]})
    client.get("/criar-aluno")
    entrar(client, "email")
    client.get("/criar-aluno")                                        # scope refusal screen
    client.post("/gestao-acesso/tiago.vasconcelos/desativar", data={"sistema": "m365"})  # protected
    client.post("/login", data={"perfil": "email"})                   # suspended notice
    entrar(client, "auditoria")
    client.get("/logs")
    client.get("/")
    assert faltando() == set()


def test_language_switch_translates_history_too(client):
    entrar(client, "auditoria")
    pt = client.get("/logs").get_data(as_text=True)
    client.get("/idioma/en")
    en = client.get("/logs").get_data(as_text=True)
    assert "Alvo protegido" in pt and "Protected target" in en
    assert "Analista de Identidade" in pt and "Identity Analyst" in en
