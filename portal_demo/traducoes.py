# -*- coding: utf-8 -*-
"""
Português -> inglês.

As chaves são o texto-fonte em português, com espaços colapsados. Um teste
(`tests/test_i18n.py`) percorre todas as telas em inglês e falha se algum
texto ficar sem tradução.
"""

EN = {
    # --- moldura -----------------------------------------------------------
    "Demonstração": "Demo",
    "Demonstração pública · pessoas, unidades e domínios são fictícios · nenhum sistema real é contatado":
        "Public demo · people, units and domains are fictional · no real system is contacted",
    "Fora do escopo do perfil": "Outside this profile's scope",
    "Dashboard Inicial": "Dashboard",
    "Módulos": "Modules",
    "Registro": "Records",
    "Novo Usuário - Colaborador": "New User - Staff",
    "Novo Usuário - Aluno": "New User - Student",
    "Alterar Senha": "Reset Password",
    "Gestão de Acesso": "Access Management",
    "Fila de Retentativa": "Retry Queue",
    "Logs e Auditoria": "Logs & Audit",
    "Perfil de Teste": "Test profile",
    "suspenso": "suspended",
    "Sair do sistema": "Sign out",
    "Técnico Ativo": "Signed in as",
    "Sessão Atualizada": "Session updated",
    "Controles da demo": "Demo controls",
    "Diretório não confirma a base": "Directory does not confirm its database",
    "ERP não confirma a base": "ERP does not confirm its database",
    "Envio de e-mail falhando": "E-mail delivery failing",
    "Reiniciar demonstração": "Reset demo",
    "Portal TI · Demonstração pública": "IT Portal · Public demo",

    # --- entrada -----------------------------------------------------------
    "Entrar": "Sign in",
    "Gestão de identidade em três sistemas": "Identity management across three systems",
    "perfil suspenso do portal depois de tentar bloquear um alvo protegido. Só o perfil Auditoria e Segurança libera, pela tela de auditoria.":
        "profile suspended from the portal after trying to block a protected target. Only the Audit & Security profile can lift it, from the audit screen.",
    "Entrar como": "Sign in as",
    "No portal real, aqui vão usuário e senha. Nesta demonstração você escolhe o perfil técnico — porque é o escopo do perfil que muda o que a próxima tela deixa fazer.":
        "In the real portal this is a username and password. In this demo you pick a technical profile, because the profile's scope is what changes what the next screen lets you do.",
    "não opera nenhum sistema": "operates no system",
    "vê registros de segurança": "sees security records",
    "recebe comprovante por e-mail": "gets an e-mailed receipt",
    "Entrar no sistema": "Sign in",
    "Você pode trocar de perfil a qualquer momento pela barra lateral, sem sair. O escopo é verificado no servidor a cada requisição, não no menu.":
        "You can switch profiles at any time from the sidebar without signing out. Scope is checked on the server on every request, not in the menu.",

    # --- perfis, sistemas, unidades ---------------------------------------
    "Analista de Identidade": "Identity Analyst",
    "Provisiona e revoga acesso nos três sistemas.": "Provisions and revokes access in all three systems.",
    "Recursos Humanos": "Human Resources",
    "Desliga pessoas: bloqueia nos três sistemas e recebe o comprovante por e-mail.":
        "Offboards people: blocks them in all three systems and gets a receipt by e-mail.",
    "Operador de E-mail": "E-mail Operator",
    "Cuida apenas das caixas do Microsoft 365.": "Handles Microsoft 365 mailboxes only.",
    "Suporte N1": "Service Desk (L1)",
    "Só redefine senha. Não cria nem bloqueia ninguém.": "Only resets passwords. Creates or blocks no one.",
    "Auditoria e Segurança": "Audit & Security",
    "Não opera nada. Lê tudo, inclusive os registros de segurança.": "Operates nothing. Reads everything, security records included.",
    "Sistema (retentativa automática)": "System (automatic retry)",
    "Microsoft 365": "Microsoft 365",
    "Diretório local": "Local directory",
    "ERP acadêmico": "Academic ERP",
    "Coordenação de Ensino": "Academic Coordination",
    "Secretaria Acadêmica": "Registrar's Office",
    "Biblioteca Central": "Central Library",
    "Laboratório de Redes": "Networking Lab",
    "Comunicação Institucional": "Communications Office",
    "Engenharia de Computação": "Computer Engineering",
    "Direito": "Law",
    "Enfermagem": "Nursing",
    "Arquitetura e Urbanismo": "Architecture and Urban Planning",
    "colaborador": "staff",
    "aluno": "student",
    "Ativo": "Active",
    "Bloqueado": "Blocked",
    "Sem conta": "No account",
    "Escolher cadastro": "Choose record",

    # --- painel ------------------------------------------------------------
    "Início": "Home",
    "Bem-vindo ao Portal de Automação": "Welcome to the Automation Portal",
    "Selecione um módulo abaixo para gerenciar identidades nos três sistemas.": "Pick a module below to manage identities across the three systems.",
    "desligamento(s) incompleto(s)": "incomplete offboarding(s)",
    "pessoas bloqueadas em um sistema e ainda ativas em outro. Sem uma visão dos três lado a lado, isso passa despercebido.":
        "people blocked in one system and still active in another. Without the three side by side, this goes unnoticed.",
    "Conta nos três sistemas, uma senha só, e-mail de credenciais pronto.": "An account in all three systems, one password, credentials e-mail ready.",
    "Mesmo caminho, com o conjunto de sistemas que o vínculo pede.": "Same path, with the set of systems the enrollment calls for.",
    "Uma senha nova, aplicada em todos os sistemas onde a pessoa existe.": "One new password, applied in every system where the person exists.",
    "Bloquear e reativar, por sistema ou em todos de uma vez.": "Block and restore, per system or in all of them at once.",
    "Bloqueios que um sistema não pôde receber na hora, tentados de novo.": "Blocks a system could not take at the time, tried again.",
    "Logs de Auditoria": "Audit Logs",
    "Histórico e rastreabilidade de ações executadas.": "History and traceability of every action.",
    "Acessar Módulo": "Open module",
    "Fora do escopo de": "Outside the scope of",
    "Sistemas Integrados": "Integrated Systems",
    "Sem escopo": "No scope",
    "contas geridas": "managed accounts",
    "Log Recente": "Recent Log",
    "Nenhuma ação registrada": "No actions recorded",
    "Histórico completo →": "Full history →",

    # --- gestão de acesso --------------------------------------------------
    "Gestão de acesso": "Access management",
    "Situação de cada pessoa nos três sistemas, em uma linha.": "Each person's status in the three systems, on one line.",
    "Contas geridas": "Managed accounts",
    "pessoas": "people",
    "Pessoa": "Person",
    "Vínculo": "Type",
    "Desligamento incompleto": "Incomplete offboarding",
    "Gerenciar": "Manage",
    "Sugestão de percurso": "Suggested walkthrough",
    "Abra <strong>Tiago Vasconcelos</strong>, do Laboratório de Redes, e tente bloquear o acesso dele. A tela não vai impedir: quem impede é o servidor. Depois troque o perfil para <strong>Auditoria e Segurança</strong> e veja o que ficou registrado.":
        "Open <strong>Tiago Vasconcelos</strong>, from the Networking Lab, and try to block his access. The screen will not stop you: the server will. Then switch the profile to <strong>Audit &amp; Security</strong> and see what was recorded.",
    "<strong>Marina Coelho</strong> está bloqueada só no Microsoft 365: o desligamento ficou pela metade. Com o perfil <strong>Recursos Humanos</strong>, bloqueie em todos e veja o comprovante.":
        "<strong>Marina Coelho</strong> is blocked in Microsoft 365 only: her offboarding stopped halfway. With the <strong>Human Resources</strong> profile, block her everywhere and check the receipt.",
    "<strong>Paulo Henrique Matos</strong> tem dois cadastros parecidos no ERP. O portal não escolhe por você.":
        "<strong>Paulo Henrique Matos</strong> has two similar records in the ERP. The portal does not pick one for you.",
    "Ligue <strong>ERP não confirma a base</strong> no rodapé e bloqueie alguém em todos: os outros sistemas são bloqueados na hora, e o ERP vai para a fila de retentativa.":
        "Turn on <strong>ERP does not confirm its database</strong> in the footer and block someone everywhere: the other systems are blocked at once and the ERP goes to the retry queue.",
    "registro": "record",
    "Desligamento incompleto: bloqueada em um sistema e ainda ativa em outro.": "Incomplete offboarding: blocked in one system and still active in another.",
    "Bloqueio aguardando na fila de retentativa:": "Block waiting in the retry queue:",
    "Ver a fila": "See the queue",
    "Cadastro vinculado:": "Linked record:",
    "Mais de um cadastro do ERP bate com este nome. Escolha o certo: a escolha é reconferida no servidor.":
        "More than one ERP record matches this name. Pick the right one: the choice is re-checked on the server.",
    "Vincular este cadastro": "Link this record",
    "Fora do escopo deste perfil": "Outside this profile's scope",
    "Bloquear": "Block",
    "Reativar": "Restore",
    "Escolha o cadastro antes de agir no ERP.": "Choose the record before acting in the ERP.",
    "Sem conta neste sistema.": "No account in this system.",
    "Em todos de uma vez": "All at once",
    "O caso do desligamento: uma ação, os sistemas do escopo do perfil, uma linha de auditoria.":
        "The offboarding case: one action, every system in the profile's scope, one audit line.",
    "Reativar em todos": "Restore everywhere",
    "Bloquear em todos": "Block everywhere",
    "Voltar à lista": "Back to the list",

    # --- criação -----------------------------------------------------------
    "Um formulário, três sistemas, uma senha.": "One form, three systems, one password.",
    "Dados do colaborador": "Staff member details",
    "Dados do aluno": "Student details",
    "Todos os campos são fictícios nesta demonstração.": "Every field is fictional in this demo.",
    "Nome completo": "Full name",
    "O nome de acesso é derivado daqui, e traduzido para o formato de cada sistema.": "The username comes from here and is translated into each system's format.",
    "Unidade": "Unit",
    "Curso": "Program",
    "Domínio": "Domain",
    "Colaborador e aluno não dividem espaço de nomes: é o que impede um aluno homônimo de colidir com quem já trabalha aqui.":
        "Staff and students do not share a namespace: that is what stops a student with the same name from colliding with someone who already works here.",
    "Sistemas de destino": "Target systems",
    "fora do escopo": "out of scope",
    "Nada é escrito antes de todos os sistemas confirmarem a base.": "Nothing is written before every system confirms its database.",
    "O que acontece ao confirmar": "What happens when you confirm",
    "O servidor confere o escopo do perfil, ignorando o que o formulário mandou.": "The server checks the profile's scope, ignoring what the form sent.",
    "Cada sistema confirma contra qual base vai escrever. <strong class=\"font-semibold text-gray-800\">Todos</strong> precisam confirmar antes que qualquer um escreva.":
        "Each system confirms which database it will write to. <strong class=\"font-semibold text-gray-800\">All</strong> of them must confirm before any one writes.",
    "Uma senha é gerada e aplicada nos três, com troca obrigatória no primeiro acesso.": "One password is generated and applied to all three, with a mandatory change at first sign-in.",
    "Sai uma linha de auditoria com o resultado de cada sistema, e o e-mail de credenciais fica pronto.": "One audit line is written with each system's result, and the credentials e-mail is ready.",
    "Use os controles no rodapé para simular um sistema que não confirma a base e ver a recusa acontecer.":
        "Use the footer controls to simulate a system that does not confirm its database and watch the refusal happen.",

    # --- resultado ---------------------------------------------------------
    "Resultado sistema por sistema.": "Result, system by system.",
    "Operação recusada. Nada foi escrito.": "Operation refused. Nothing was written.",
    "não confirmou contra qual base escreveria.": "did not confirm which database it would write to.",
    "Motivo": "Reason",
    "Por que recusar em vez de seguir": "Why refuse instead of carrying on",
    "A confirmação acontece nos três sistemas <em>antes</em> de qualquer escrita. Como um deles não respondeu o esperado, nenhum foi tocado: a alternativa seria criar a pessoa em dois sistemas e deixá-la ausente no terceiro, ou pior, escrever no ambiente errado. Meio provisionamento é mais caro de descobrir e de desfazer do que uma recusa explícita.":
        "Confirmation happens in all three systems <em>before</em> any write. Since one of them did not answer as expected, none was touched: the alternative would be creating the person in two systems and leaving them missing in the third, or worse, writing to the wrong environment. Half-done provisioning costs more to find and undo than an explicit refusal.",
    "Voltar": "Back",
    "Ver o registro desta recusa": "See the record of this refusal",
    "Concluído": "Done",
    "Parcial": "Partial",
    "entra como": "signs in as",
    "falhou": "failed",
    "Base não confirmada: nada foi escrito aqui. O bloqueio foi para a fila de retentativa, que tenta de novo e reconfere a base antes de escrever.":
        "Database not confirmed: nothing was written here. The block went to the retry queue, which tries again and re-confirms the database before writing.",
    "na fila": "queued",
    "No bloqueio, esperar o sistema mais lento deixaria o acesso aberto nos outros. Por isso cada sistema é bloqueado assim que confirma a base, e o que não confirmou é tentado de novo pela fila.":
        "When blocking, waiting for the slowest system would leave access open in the others. So each system is blocked as soon as it confirms its database, and the one that did not is retried by the queue.",
    "Três sistemas, três formatos de login diferentes, uma senha só. É por isso que o e-mail de credenciais precisa dizer com qual nome se entra em cada lugar.":
        "Three systems, three username formats, one password. That is why the credentials e-mail has to say which name to use where.",
    "O e-mail de credenciais não foi entregue.": "The credentials e-mail was not delivered.",
    "A senha foi aplicada, mas a pessoa não sabe qual é: não consegue entrar. Por isso a operação fica como parcial, e não como sucesso.":
        "The password was applied, but the person does not know it and cannot sign in. That is why the operation is partial, not a success.",
    "Comprovante enviado para": "Receipt sent to",
    "O RH responde pelo desligamento fora do portal; sem o comprovante na caixa, a única prova estaria numa tela.":
        "HR answers for the offboarding outside the portal; without the receipt in its mailbox, the only proof would be on a screen.",
    "O acesso foi alterado, mas o comprovante não chegou à caixa do RH. A falha ficou registrada na auditoria.":
        "Access was changed, but the receipt did not reach HR's mailbox. The failure was recorded in the audit log.",
    "Ver o e-mail de credenciais": "See the credentials e-mail",
    "Ver na auditoria": "See it in the audit log",
    "Bloquear acesso": "Block access",
    "Reativar acesso": "Restore access",
    "Redefinir senha": "Reset password",

    # --- mensagens dos providers --------------------------------------------
    "Caixa criada e licença atribuída.": "Mailbox created and license assigned.",
    "Entrada liberada e licença devolvida.": "Sign-in allowed and license restored.",
    "Entrada bloqueada e sessões ativas revogadas.": "Sign-in blocked and active sessions revoked.",
    "Senha trocada, com troca obrigatória no primeiro acesso.": "Password changed, with a mandatory change at first sign-in.",
    "Conta criada na unidade organizacional do setor.": "Account created in the department's organizational unit.",
    "Conta reativada.": "Account restored.",
    "Conta desabilitada e retirada dos grupos de acesso.": "Account disabled and removed from access groups.",
    "Senha trocada no diretório.": "Password changed in the directory.",
    "Usuário criado com o perfil de acesso do cargo.": "User created with the job's access profile.",
    "Usuário reativado.": "User restored.",
    "Usuário inativado.": "User deactivated.",
    "Senha trocada no ERP.": "Password changed in the ERP.",
    "Cadastro do ERP não resolvido: há mais de um com este nome. Escolha o cadastro na tela da pessoa.":
        "ERP record not resolved: more than one has this name. Choose the record on the person's screen.",
    "O ambiente que respondeu não é o esperado para esta operação.": "The environment that answered is not the one expected for this operation.",
    "A raiz do diretório que respondeu não confere com a esperada.": "The directory root that answered does not match the expected one.",
    "A base que respondeu não é a que esta operação deveria escrever.": "The database that answered is not the one this operation should write to.",

    # --- auditoria ---------------------------------------------------------
    "Logs e auditoria": "Logs and audit",
    "Uma linha por ação, com o resultado de cada sistema.": "One line per action, with each system's result.",
    "Este perfil vê o registro operacional. Os registros de segurança são filtrados na consulta ao banco, não na tela: quem pode ser objeto de uma apuração não recebe as linhas dela nem pelo código-fonte da página.":
        "This profile sees the operational log. Security records are filtered in the database query, not on screen: someone who may be the subject of an investigation does not receive its rows, not even in the page source.",
    "Troque o perfil para Auditoria e Segurança para ver a tabela completa.": "Switch the profile to Audit & Security to see the full table.",
    "Perfis suspensos do portal": "Profiles suspended from the portal",
    "Tentou bloquear": "Tried to block",
    "Liberar": "Lift suspension",
    "Histórico de execuções": "Execution history",
    "registros": "records",
    "Quando": "When",
    "Quem": "Who",
    "Ação": "Action",
    "Alvo": "Target",
    "Resultado": "Result",
    "segurança": "security",
    "A auditoria é o produto, não um subproduto. Cada linha responde de uma vez quem pediu, o que pediu, contra quem, e como cada sistema respondeu — inclusive quando a resposta foi recusa.":
        "The audit log is the product, not a by-product. Each line answers at once who asked, what they asked for, against whom, and how each system answered, including when the answer was a refusal.",
    "ok": "ok",
    "parcial": "partial",
    "negado": "denied",
    "recusado": "refused",
    "bloqueado": "blocked",
    "sem conta": "no account",
    "cancelado": "cancelled",
    "Acesso negado": "Access denied",
    "Vincular cadastro do ERP": "Link ERP record",
    "Suspensão liberada": "Suspension lifted",
    "Comprovante ao RH não entregue": "Receipt to HR not delivered",
    "Retentativa de bloqueio": "Block retry",
    "ERP fora do escopo do cargo informado.": "ERP outside the scope of the given job.",
    "Senha única, troca obrigatória no primeiro acesso.": "Single password, mandatory change at first sign-in.",
    "Perfil alcança apenas o Microsoft 365.": "Profile reaches Microsoft 365 only.",
    "Pedido por URL direta a um sistema fora do escopo do perfil.": "Request by direct URL to a system outside the profile's scope.",
    "Aluno não recebe conta no diretório.": "Students get no directory account.",
    "Alvo protegido. Sessão de quem pediu encerrada na hora.": "Protected target. The requester's session ended immediately.",
    "Bloqueado onde a base confirmou; o restante foi para a fila de retentativa.": "Blocked where the database confirmed; the rest went to the retry queue.",
    "Senha aplicada, mas o e-mail de credenciais não foi entregue: a pessoa não consegue entrar.":
        "Password applied, but the credentials e-mail was not delivered: the person cannot sign in.",

    # --- e-mail de credenciais ---------------------------------------------
    "E-mail de credenciais": "Credentials e-mail",
    "E-mail de Credenciais": "Credentials E-mail",
    "Pré-visualização do que a pessoa recebe.": "Preview of what the person receives.",
    "Para": "To",
    "Assunto": "Subject",
    "Seus acessos estão prontos": "Your access is ready",
    "Olá,": "Hello,",
    "Seus acessos já estão prontos. A senha abaixo é a mesma nos sistemas listados, mas <strong class=\"font-semibold text-gray-800\">o nome de acesso muda em cada um</strong>. Confira na tabela com qual deles entrar.":
        "Your access is ready. The password below is the same in every system listed, but <strong class=\"font-semibold text-gray-800\">the username changes in each one</strong>. Check the table for which one to use.",
    "Sua senha": "Your password",
    "A senha é a mesma nos três sistemas e precisa ser trocada no primeiro acesso.": "The password is the same in all three systems and must be changed at first sign-in.",
    "Sistema": "System",
    "Você entra como": "You sign in as",
    "Para quê": "What for",
    "E-mail, arquivos e reuniões.": "E-mail, files and meetings.",
    "Entrar nos computadores da instituição e na rede sem fio.": "Signing in to campus computers and Wi-Fi.",
    "Sistema acadêmico e financeiro.": "Academic and financial system.",
    "Qualquer dúvida, é só responder este e-mail.": "Questions? Just reply to this e-mail.",
    "Por que este e-mail existe": "Why this e-mail exists",
    "Antes, cada sistema entregava a credencial do seu jeito, e por caminhos diferentes. A pessoa recebia um nome de acesso, tentava o mesmo nome no segundo, não entrava, e abria chamado no primeiro dia.":
        "Before, each system delivered its credential its own way, through different channels. People got one username, tried it in the second system, could not get in, and opened a ticket on day one.",
    "Uma senha só para os três é decisão deliberada: três senhas distintas viravam três bilhetes colados no monitor. A troca no primeiro acesso é obrigatória, e a senha nasce temporária.":
        "One password for all three is a deliberate choice: three different passwords became three sticky notes on the monitor. The change at first sign-in is mandatory, and the password starts out temporary.",
    "Senha e destinatário desta tela são gerados para a demonstração.": "The password and recipient on this screen are generated for the demo.",

    # --- recusas -----------------------------------------------------------
    "Acesso encerrado": "Session ended",
    "Operação recusada": "Operation refused",
    "Proteção de alvo.": "Target protection.",
    "Sessão": "Session",
    "Encerrada": "Ended",
    "Alvo protegido. Nada foi alterado.": "Protected target. Nothing was changed.",
    "Integrante da equipe técnica": "Member of the technical team",
    "Mantém este portal": "Maintains this portal",
    "Seu acesso ao portal foi encerrado e o perfil foi suspenso.": "Your portal session was ended and the profile was suspended.",
    "A sessão caiu na mesma requisição, antes da resposta chegar até aqui. Entrar de novo com o mesmo perfil não adianta: a suspensão fica até a auditoria liberar.":
        "The session was dropped in the same request, before this response reached you. Signing in again with the same profile does not help: the suspension stays until Audit lifts it.",
    "A regra": "The rule",
    "Nenhum técnico revoga o acesso de outro técnico, nem o da equipe que mantém este portal. Vale para todos os perfis, inclusive os que bloqueiam qualquer outra pessoa da instituição. Um portal que corta acesso nos três sistemas de uma vez é uma boa ferramenta para quem administra e uma boa arma para quem foi comprometido: a proteção existe para que ele não sirva à segunda coisa.":
        "No technician revokes another technician's access, nor that of the team that maintains this portal. This holds for every profile, including those that can block anyone else in the institution. A portal that cuts access in three systems at once is a good tool for administrators and a good weapon for a compromised account: the protection exists so it cannot serve the second purpose.",
    "O que ficou registrado": "What was recorded",
    "Quem pediu, contra quem, quando, e que a sessão foi encerrada. O registro é de segurança: aparece para a auditoria e não para quem opera — nem para quem acabou de tentar.":
        "Who asked, against whom, when, and that the session was ended. It is a security record: Audit sees it, operators do not, including the one who just tried.",
    "Entrar com outro perfil": "Sign in with another profile",
    "Na demonstração, entre como Auditoria e Segurança para ver o registro e liberar a suspensão.":
        "In the demo, sign in as Audit & Security to see the record and lift the suspension.",
    "Recusado": "Refused",
    "Pedido recusado": "Request refused",
    "Escopo do perfil, verificado no servidor.": "Profile scope, checked on the server.",
    "403 — fora do escopo do perfil": "403: outside this profile's scope",
    "Caminho pedido": "Requested path",
    "Por que a tela não bastava": "Why the screen was not enough",
    "Esconder o botão resolve o engano, não a tentativa. O escopo é verificado na rota e de novo na orquestração, que é o único caminho até as integrações. Chegar aqui pela URL, por um formulário adulterado ou por uma aba antiga dá no mesmo resultado.":
        "Hiding the button prevents mistakes, not attempts. Scope is checked in the route and again in the orchestration, the only path to the integrations. A typed URL, a tampered form or an old tab all end here.",
    "A recusa foi registrada. Este perfil não vê esse registro.": "The refusal was recorded. This profile cannot see that record.",
    "Voltar ao início": "Back to home",

    # --- senha ---------------------------------------------------------------
    "Alterar senha": "Reset password",
    "Uma senha nova, aplicada onde a pessoa existe.": "One new password, applied wherever the person exists.",
    "Redefinição de credencial": "Credential reset",
    "A mesma senha vale nos sistemas marcados.": "The same password applies to the selected systems.",
    "O e-mail que sai depois diz, para cada sistema, com qual nome de acesso entrar — porque o login não é o mesmo nos três.":
        "The e-mail sent afterwards says which username to use in each system, because the login is not the same in all three.",
    "Gerar e aplicar senha": "Generate and apply password",

    # --- fila ----------------------------------------------------------------
    "Fila de retentativa": "Retry queue",
    "Bloqueios que um sistema não pôde receber na hora.": "Blocks a system could not take at the time.",
    "Última passada:": "Last run:",
    "concluído(s)": "done",
    "ainda pendente(s)": "still pending",
    "cancelado(s)": "cancelled",
    "sem mais tentativas": "gave up",
    "Itens": "Items",
    "Rodar a retentativa agora": "Run the retry job now",
    "Tentativas": "Attempts",
    "Situação": "Status",
    "pendente": "pending",
    "concluido": "done",
    "desistiu": "gave up",
    "Fila vazia. Ligue \"ERP não confirma a base\" no rodapé e bloqueie alguém em todos os sistemas.":
        "The queue is empty. Turn on \"ERP does not confirm its database\" in the footer and block someone in all systems.",
    "Como a fila funciona": "How the queue works",
    "No portal real, um processo agendado roda a cada 5 minutos. Aqui, o botão faz a mesma passada.":
        "In the real portal a scheduled job runs every 5 minutes. Here, the button runs the same pass.",
    "<strong>Só bloqueio entra.</strong> A fila existe para que um acesso que devia ser cortado não fique aberto. Reativação que falha aparece na tela de quem pediu.":
        "<strong>Only blocks are queued.</strong> The queue exists so that access that should be cut does not stay open. A failed restore shows up on the requester's screen.",
    "<strong>A política é reconferida a cada tentativa.</strong> Alvo que passou a ser protegido é cancelado, e base que não confirma continua sem ser escrita.":
        "<strong>Policy is re-checked on every attempt.</strong> A target that became protected is cancelled, and a database that does not confirm is still not written.",
    "Depois de 5 tentativas o item para e fica visível para alguém olhar.": "After 5 attempts the item stops and stays visible for someone to look at.",
    "Item fora do escopo da fila.": "Item outside the queue's scope.",
}
