# Arquitetura

Complemento ao [README](../README.md), para quem quiser olhar o código.

## O contrato

Todo sistema integrado implementa a mesma interface. São cinco verbos e duas
funções de apoio:

```python
class Provider:
    chave = ""       # "m365", "diretorio", "erp"
    rotulo = ""
    protocolo = ""

    def login_de(self, pessoa): ...      # como a pessoa se chama NESTE sistema
    def confirmar_base(self): ...        # contra qual base vou escrever?

    def existe(self, pessoa): ...
    def criar(self, pessoa, senha): ...
    def ativar(self, pessoa): ...
    def desativar(self, pessoa): ...
    def redefinir_senha(self, pessoa, senha): ...
```

`login_de` existe porque o nome de acesso é diferente em cada sistema, e a
tradução é responsabilidade de quem conhece o sistema — não da orquestração e
muito menos da tela.

`confirmar_base` é a única função que todo provider precisa implementar mesmo
que o sistema "não precise": é ela que sustenta a falha fechada.

## O caminho de uma operação

```
rota  ──►  exigir_operacao(perfil, operacao)         políticas, no servidor
      ──►  Orquestrador.executar(...)
             ├─ exigir_operacao / exigir_sistemas    de novo, aqui é a garantia
             ├─ exigir_alvo_permitido                proteção de alvo
             ├─ confirmar_base() em TODOS            falha fechada
             └─ verbo() em cada um                   só depois de tudo confirmado
      ──►  auditoria.registrar(...)                  uma linha, com cada sistema
      ──►  template do resultado
```

A verificação de escopo aparece duas vezes de propósito. Na rota, para responder
403 cedo e com uma tela decente. Na orquestração, porque ela é o **único**
caminho até os providers: enquanto a checagem estiver lá, nenhuma rota nova
criada com pressa consegue contornar a política por esquecimento.

## Por que a orquestração não conhece os sistemas

`orquestracao.py` não importa `msal`, `ldap3` nem nada de protocolo. Ele recebe
um dicionário de providers prontos e chama `getattr(provider, verbo)`. Três
consequências práticas:

- **Testar não exige rede.** Os providers desta demonstração são exatamente isso:
  implementações do mesmo contrato que guardam estado em memória. A orquestração
  não sabe a diferença — e é justamente por isso que a demo consegue exercitar as
  travas de verdade.
- **Acrescentar um sistema é um arquivo.** Escrever a classe, registrar em
  `providers/montar()`, acrescentar o rótulo em `dados.SISTEMAS`. Nem
  orquestração nem telas mudam.
- **Cada integração falha do seu jeito, e traduz isso para o mesmo `Resultado`.**
  Quem lê a auditoria não precisa saber o que é um código de erro de LDAP.

## Estado da demonstração

O portal real guarda estado nos três sistemas e usa o SQLite só para auditoria.
Esta demonstração guarda tudo em memória (`ESTADO`, em `app.py`) mais um SQLite
temporário em `instance/`, recriado a cada reinício. O botão **Reiniciar
demonstração**, no rodapé, devolve tudo ao ponto de partida.

Os controles de simulação no rodapé ligam e desligam a falha de confirmação de
base de cada sistema. Eles existem só na demo: no portal real, esse estado vem
da resposta das integrações, não de um botão.
