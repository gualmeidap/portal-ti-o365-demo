# -*- coding: utf-8 -*-
"""
Universo fictício da demonstração.

Nada aqui vem de um ambiente real: instituição, domínios, pessoas, unidades e
identificadores foram inventados para esta vitrine. O domínio `.example` é
reservado pela RFC 2606 justamente para exemplos e nunca resolve na internet.
"""

INSTITUICAO = "Universidade Meridiana"
INSTITUICAO_CURTA = "Meridiana"
DOMINIO_EMAIL = "meridiana.example"
DOMINIO_DIRETORIO = "MERIDIANA"

# ---------------------------------------------------------------------------
# Perfis: o escopo é uma propriedade do perfil, não do menu.
# `operacoes` e `sistemas` são verificados no servidor a cada requisição.
# ---------------------------------------------------------------------------
PERFIS = {
    "identidade": {
        "rotulo": "Analista de Identidade",
        "descricao": "Provisiona e revoga acesso nos três sistemas.",
        "operacoes": {"criar_colaborador", "criar_aluno", "redefinir_senha", "acesso"},
        "sistemas": {"m365", "diretorio", "erp"},
        "ve_auditoria_operacional": True,
        "ve_auditoria_seguranca": False,
    },
    "email": {
        "rotulo": "Operador de E-mail",
        "descricao": "Cuida apenas das caixas do Microsoft 365.",
        "operacoes": {"criar_colaborador", "redefinir_senha", "acesso"},
        "sistemas": {"m365"},
        "ve_auditoria_operacional": True,
        "ve_auditoria_seguranca": False,
    },
    "suporte": {
        "rotulo": "Suporte N1",
        "descricao": "Só redefine senha. Não cria nem bloqueia ninguém.",
        "operacoes": {"redefinir_senha"},
        "sistemas": {"m365", "diretorio", "erp"},
        "ve_auditoria_operacional": True,
        "ve_auditoria_seguranca": False,
    },
    "auditoria": {
        "rotulo": "Auditoria e Segurança",
        "descricao": "Não opera nada. Lê tudo, inclusive os registros de segurança.",
        "operacoes": set(),
        "sistemas": set(),
        "ve_auditoria_operacional": True,
        "ve_auditoria_seguranca": True,
    },
}

# Fonte única dos rótulos: menu, título de página e linha de auditoria usam estes
# mesmos nomes. Antes havia dois conjuntos concorrentes e a tela se contradizia.
OPERACOES = {
    "criar_colaborador": "Novo Usuário - Colaborador",
    "criar_aluno": "Novo Usuário - Aluno",
    "redefinir_senha": "Alterar Senha",
    "acesso": "Gestão de Acesso",
}

# Domínios de e-mail por tipo de vínculo. Colaborador e aluno não compartilham
# espaço de nomes: é o que evita um aluno homônimo colidir com um servidor.
DOMINIOS = {
    "colaborador": DOMINIO_EMAIL,
    "aluno": "alunos." + DOMINIO_EMAIL,
}

SISTEMAS = {
    "m365": {"rotulo": "Microsoft 365", "detalhe": "Graph API", "cor": "sky"},
    "diretorio": {"rotulo": "Diretório local", "detalhe": "LDAP", "cor": "violet"},
    "erp": {"rotulo": "ERP acadêmico", "detalhe": "SOAP + SQL", "cor": "amber"},
}

UNIDADES = [
    "Coordenação de Ensino",
    "Secretaria Acadêmica",
    "Biblioteca Central",
    "Laboratório de Redes",
    "Comunicação Institucional",
]

CURSOS = [
    "Engenharia de Computação",
    "Direito",
    "Enfermagem",
    "Arquitetura e Urbanismo",
]

# ---------------------------------------------------------------------------
# Pessoas fictícias já existentes na base de demonstração.
#
# `protegido` marca quem a política de proteção de alvo cobre: o pessoal
# técnico e a equipe que mantém o portal. Ninguém bloqueia essas contas
# pelo portal — nem quem tem perfil para bloquear todo o resto.
# ---------------------------------------------------------------------------
def registro_de(login):
    """
    Identificador estável a partir do login.

    `hash()` de string é aleatorizado a cada processo no Python 3, então usá-lo
    aqui fazia o registro da mesma pessoa mudar a cada reinício — e a cada
    captura de tela.
    """
    soma = sum((i + 1) * ord(c) for i, c in enumerate(login))
    return "DEMO-{:04d}".format(soma % 9000 + 1000)


def _pessoa(nome, login, tipo, unidade, estado, protegido=False, motivo_protecao=None, registro=None):
    return {
        "nome": nome,
        "login": login,
        "tipo": tipo,
        "unidade": unidade,
        "registro": registro or registro_de(login),
        "estado": estado,
        "protegido": protegido,
        "motivo_protecao": motivo_protecao,
    }


PESSOAS = [
    _pessoa("Joana Prado", "joana.prado", "colaborador", "Coordenação de Ensino",
            {"m365": "ativo", "diretorio": "ativo", "erp": "ativo"}),
    _pessoa("Rafael Antunes", "rafael.antunes", "colaborador", "Secretaria Acadêmica",
            {"m365": "ativo", "diretorio": "ativo", "erp": "ativo"}),
    _pessoa("Marina Coelho", "marina.coelho", "colaborador", "Biblioteca Central",
            {"m365": "bloqueado", "diretorio": "ativo", "erp": "ativo"}),
    _pessoa("Otávio Bittencourt", "otavio.bittencourt", "colaborador", "Comunicação Institucional",
            {"m365": "ativo", "diretorio": "ativo", "erp": "sem_conta"}),
    _pessoa("Tiago Vasconcelos", "tiago.vasconcelos", "colaborador", "Laboratório de Redes",
            {"m365": "ativo", "diretorio": "ativo", "erp": "ativo"},
            protegido=True, motivo_protecao="Integrante da equipe técnica"),
    _pessoa("Helena Duarte", "helena.duarte", "colaborador", "Laboratório de Redes",
            {"m365": "ativo", "diretorio": "ativo", "erp": "ativo"},
            protegido=True, motivo_protecao="Mantém este portal"),
    _pessoa("Bruno Salgado", "bruno.salgado", "aluno", "Engenharia de Computação",
            {"m365": "ativo", "diretorio": "ativo", "erp": "ativo"}),
    _pessoa("Lívia Ferraz", "livia.ferraz", "aluno", "Direito",
            {"m365": "ativo", "diretorio": "sem_conta", "erp": "ativo"}),
]

ESTADOS = {
    "ativo": {"rotulo": "Ativo", "classe": "bg-emerald-50 text-emerald-700 ring-emerald-600/20"},
    "bloqueado": {"rotulo": "Bloqueado", "classe": "bg-red-50 text-red-700 ring-red-600/20"},
    "sem_conta": {"rotulo": "Sem conta", "classe": "bg-gray-100 text-gray-600 ring-gray-500/20"},
}
