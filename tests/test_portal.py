import app as portal
from portal_demo.fila import FilaRetentativa
from portal_demo.orquestracao import Orquestrador
from portal_demo.politicas import AlvoProtegido, NegadoPorEscopo
from portal_demo.providers import montar

from .conftest import entrar
import pytest


def estado(login):
    return portal.ESTADO[login]


# ── sessão e escopo ──────────────────────────────────────────────────────────
def test_sem_sessao_nenhuma_tela(client):
    r = client.get("/gestao-acesso")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_escopo_vale_no_servidor_mesmo_por_url(client):
    entrar(client, "email")
    r = client.get("/criar-aluno")
    assert r.status_code == 403
    eventos = portal.AUDITORIA.listar(incluir_seguranca=True)
    assert eventos[0]["operacao"] == "Acesso negado" and eventos[0]["categoria"] == "seguranca"


def test_formulario_adulterado_nao_alcanca_sistema_fora_do_escopo(client):
    entrar(client, "email")
    r = client.post("/gestao-acesso/joana.prado/desativar", data={"sistema": "diretorio"})
    assert r.status_code == 403
    assert estado("joana.prado")["diretorio"] == "ativo"


def test_registros_de_seguranca_filtrados_na_consulta(client):
    entrar(client, "identidade")
    html = client.get("/logs").get_data(as_text=True)
    assert "Tiago Vasconcelos" not in html  # o único registro dele é de segurança
    entrar(client, "auditoria")
    assert "Tiago Vasconcelos" in client.get("/logs").get_data(as_text=True)


# ── proteção de alvo e suspensão ─────────────────────────────────────────────
def test_alvo_protegido_encerra_sessao_e_suspende_perfil(client):
    entrar(client, "identidade")
    r = client.post("/gestao-acesso/tiago.vasconcelos/desativar", data={"sistema": "todos"})
    assert r.status_code == 403
    assert estado("tiago.vasconcelos")["m365"] == "ativo"
    assert "identidade" in portal.SUSPENSOS
    assert client.get("/").status_code == 302          # sessão acabou
    entrar(client, "identidade")
    assert client.get("/").status_code == 302          # e não volta só entrando de novo
    # Só a auditoria libera, e fica registrado.
    entrar(client, "auditoria")
    client.post("/suspensoes/identidade/liberar")
    assert "identidade" not in portal.SUSPENSOS
    assert portal.AUDITORIA.listar(incluir_seguranca=True)[0]["operacao"] == "Suspensão liberada"
    entrar(client, "identidade")
    assert client.get("/").status_code == 200


def test_quem_nao_audita_nao_libera_suspensao(client):
    portal.SUSPENSOS["email"] = {"quando": "-", "alvo": "x"}
    entrar(client, "identidade")
    assert client.post("/suspensoes/email/liberar").status_code == 403
    assert "email" in portal.SUSPENSOS


# ── falha fechada ────────────────────────────────────────────────────────────
def test_criacao_recusada_por_inteiro_se_uma_base_nao_confirma(client):
    entrar(client, "identidade")
    client.post("/demo/simular", data={"chave": "diretorio_sem_confirmacao"})
    html = client.post("/criar-usuario", data={"nome": "Camila Rezende", "unidade": "Biblioteca Central",
                                               "sistemas": ["m365", "diretorio", "erp"]}).get_data(as_text=True)
    assert "Nada foi escrito" in html
    assert "camila.rezende" not in portal.ESTADO


def test_bloqueio_nao_espera_sistema_que_nao_confirma_e_enfileira(client):
    entrar(client, "rh")
    client.post("/demo/simular", data={"chave": "erp_sem_confirmacao"})
    client.post("/gestao-acesso/joana.prado/desativar", data={"sistema": "todos"})
    assert estado("joana.prado") == {"m365": "bloqueado", "diretorio": "bloqueado", "erp": "ativo"}
    pendentes = portal.FILA.pendentes()
    assert [(i["login"], i["sistema"]) for i in pendentes] == [("joana.prado", "erp")]
    assert portal.AUDITORIA.listar(incluir_seguranca=False)[0]["erp"] == "na fila"


def test_fila_reconfere_base_e_conclui_quando_volta(client):
    entrar(client, "rh")
    client.post("/demo/simular", data={"chave": "erp_sem_confirmacao"})
    client.post("/gestao-acesso/joana.prado/desativar", data={"sistema": "todos"})
    entrar(client, "identidade")
    client.post("/fila/processar")                       # ERP ainda não confirma
    assert portal.FILA.itens[0]["estado"] == "pendente" and portal.FILA.itens[0]["tentativas"] == 1
    assert estado("joana.prado")["erp"] == "ativo"
    client.post("/demo/simular", data={"chave": "erp_sem_confirmacao"})  # desliga a simulação
    client.post("/fila/processar")
    assert portal.FILA.itens[0]["estado"] == "concluido"
    assert estado("joana.prado")["erp"] == "bloqueado"


def test_fila_cancela_alvo_protegido():
    fila = FilaRetentativa()
    pessoas = {"tiago.vasconcelos": {"nome": "Tiago", "login": "tiago.vasconcelos", "protegido": True,
                                     "motivo_protecao": "Integrante da equipe técnica"}}
    fila.enfileirar(pessoas["tiago.vasconcelos"], "erp", "timeout")

    class AuditoriaFalsa:
        def __init__(self):
            self.linhas = []

        def registrar(self, **kw):
            self.linhas.append(kw)

    aud = AuditoriaFalsa()
    resumo = fila.processar(montar({}, {}), pessoas, aud)
    assert resumo["cancelado"] == 1 and aud.linhas[0]["resultado"] == "recusado"


def test_criacao_continua_tudo_ou_nada_no_orquestrador():
    estado_ = {}
    orq = Orquestrador(montar(estado_, {"erp_sem_confirmacao": True}), fila=FilaRetentativa())
    pessoa = {"nome": "X Y", "login": "x.y", "tipo": "colaborador", "protegido": False}
    execucao = orq.executar(operacao="criar_colaborador", verbo="criar", pessoa=pessoa,
                            sistemas=["m365", "diretorio", "erp"], perfil="identidade", senha="s")
    assert execucao.recusada and estado_ == {}
    assert not orq.fila.itens  # criação nunca vai para a fila


def test_orquestrador_aplica_politica_mesmo_chamado_direto():
    orq = Orquestrador(montar({}, {}))
    with pytest.raises(NegadoPorEscopo):
        orq.executar(operacao="acesso", verbo="desativar", pessoa={"login": "a", "nome": "A"},
                     sistemas=["diretorio"], perfil="email")
    with pytest.raises(AlvoProtegido):
        orq.executar(operacao="acesso", verbo="desativar", pessoa={"login": "a", "nome": "A", "protegido": True},
                     sistemas=["m365"], perfil="identidade")


# ── homônimos no ERP ─────────────────────────────────────────────────────────
def test_erp_nao_adivinha_homonimo(client):
    entrar(client, "identidade")
    client.post("/gestao-acesso/paulo.matos/desativar", data={"sistema": "todos"})
    assert estado("paulo.matos")["erp"] == "a_vincular"           # não chutou
    assert estado("paulo.matos")["m365"] == "bloqueado"
    assert portal.AUDITORIA.listar(incluir_seguranca=False)[0]["erp"] == "falhou"


def test_vinculo_do_erp_reconferido_no_servidor(client):
    entrar(client, "identidade")
    assert client.post("/gestao-acesso/paulo.matos/vincular-erp", data={"registro": "DEMO-0000"}).status_code == 400
    assert portal.PESSOAS["paulo.matos"]["erp_vinculo"] is None
    client.post("/gestao-acesso/paulo.matos/vincular-erp", data={"registro": "DEMO-7310"})
    assert portal.PESSOAS["paulo.matos"]["erp_vinculo"] == "DEMO-7310"
    client.post("/gestao-acesso/paulo.matos/desativar", data={"sistema": "erp"})
    assert estado("paulo.matos")["erp"] == "bloqueado"


def test_email_so_alcanca_m365_nao_vincula_erp(client):
    entrar(client, "email")
    assert client.post("/gestao-acesso/paulo.matos/vincular-erp", data={"registro": "DEMO-7310"}).status_code == 403


# ── entrega de e-mail e comprovante ──────────────────────────────────────────
def test_senha_sem_email_entregue_e_parcial(client):
    entrar(client, "suporte")
    client.post("/demo/simular", data={"chave": "email_falhando"})
    html = client.post("/alterar-senha", data={"login": "joana.prado"}).get_data(as_text=True)
    assert "não foi entregue" in html
    assert portal.AUDITORIA.listar(incluir_seguranca=False)[0]["resultado"] == "parcial"


def test_rh_recebe_comprovante(client):
    entrar(client, "rh")
    html = client.post("/gestao-acesso/marina.coelho/desativar", data={"sistema": "todos"}).get_data(as_text=True)
    assert "rh@meridiana.example" in html
    assert estado("marina.coelho") == {"m365": "bloqueado", "diretorio": "bloqueado", "erp": "bloqueado"}


def test_rh_so_alcanca_gestao_de_acesso(client):
    entrar(client, "rh")
    assert client.get("/criar-usuario").status_code == 403
    assert client.get("/alterar-senha").status_code == 403


def test_desligamento_incompleto_aparece(client):
    entrar(client, "identidade")
    html = client.get("/gestao-acesso").get_data(as_text=True)
    assert "Desligamento incompleto" in html  # Marina: bloqueada só no Microsoft 365


def test_reiniciar_volta_ao_inicio(client):
    entrar(client, "rh")
    client.post("/gestao-acesso/joana.prado/desativar", data={"sistema": "todos"})
    client.post("/demo/reiniciar")
    assert estado("joana.prado")["m365"] == "ativo" and not portal.FILA.itens
