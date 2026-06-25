# PizzaLoop — Cargos, Permissões e Auditoria (implementado)

Este pacote já vem com o sistema de cargos/permissões e o log de auditoria
que discutimos, plugado direto no seu projeto real (sem mudar a estrutura
MVC que vocês já usam).

## ⚠️ Passo obrigatório antes de rodar

1. Abra o **MySQL Workbench**, conecte no seu banco na nuvem e rode o
   arquivo `sql/rbac_auditoria.sql` (na ordem em que está escrito).
2. No final do script tem uma linha comentada:
   ```sql
   -- UPDATE login SET nome = 'Seu Nome', cargo = 'admin' WHERE email = 'seu-email-atual@exemplo.com';
   ```
   **Descomente e troque pelo seu e-mail atual de login.** Sem isso, seu
   usuário fica com cargo padrão `funcionario` e você não vê a tela de
   "Gerenciar Funcionários".
3. Todo usuário cadastrado por você mesmo na tela "Criar uma nova conta"
   (tela de login) entra automaticamente como `funcionario` — só o admin
   consegue promover alguém a `socio`, `admin` ou `entregador`, na nova
   tela **Gerenciar Funcionários**.

## O que foi adicionado

### Cargos (`services/permissao_service.py`)
Fonte única da regra: o que cada cargo pode **ver** e **editar**, por módulo.

| Módulo | Admin | Sócio | Funcionário | Entregador |
|---|---|---|---|---|
| Dashboard | ver/editar | ver/editar | ver | — |
| Pedidos | ver/editar | ver/editar | ver/editar | — |
| Clientes | ver/editar | ver/editar | ver/editar | — |
| Produtos | ver/editar | ver/editar | **ver apenas** | — |
| Entregadores | ver/editar | ver/editar | — | ver/editar |
| Relatórios | ver/editar | ver/editar | — | — |
| Estoque | ver/editar | ver/editar | — | — |
| Funcionários | ver/editar | — | — | — |
| Auditoria | **ver apenas** | **ver apenas** | — | — |

Quer mudar alguma regra? É só editar o dicionário `PERMISSOES` nesse arquivo
— nenhum outro lugar do código precisa mudar.

### Fluxo de login (`models/login_model.py`, `controllers/login_controller.py`, `views/tela_login.py`)
- A tabela `login` ganhou as colunas `nome`, `cargo` e `ativo`.
- `autenticar()` agora retorna também o usuário logado (nome, e-mail, cargo),
  que vira a "sessão" usada pelo resto do sistema.
- Login de conta **desativada** é bloqueado com uma mensagem clara.

### Sidebar e navegação (`views/tela_sistema.py`, `controllers/sistema_controller.py`)
- O menu lateral só mostra os módulos que o cargo logado pode ver
  (Camada 1 — interface).
- `mudar_tela()` **revalida a permissão antes de renderizar qualquer tela**
  (Camada 2 — segurança real), mesmo que alguém tente forçar a navegação.
- Nome e cargo reais aparecem no rodapé da sidebar.
- **Botão "Sair" agora faz logout de verdade** (volta pra tela de login, não
  fecha o programa) — importante porque vocês decidiram usar 1 computador
  só, compartilhado entre os cargos.

### Auditoria (`models/auditoria_model.py`, `controllers/auditoria_controller.py`, `views/tela_auditoria.py`)
- Toda ação registrada grava: quem fez, e-mail, cargo, ação (criou/editou/
  excluiu), módulo, detalhe e data/hora.
- Tela **"Auditoria"** (visível só pro admin) lista as últimas 200 ações.
- A auditoria nunca trava a ação principal: se o log falhar, a operação do
  usuário continua funcionando.

### Gerenciar Funcionários (`controllers/funcionario_controller.py`, `views/tela_funcionarios.py`)
- Tela nova, visível só pro admin, no menu lateral (🔐 Funcionários).
- Cadastra nome, e-mail, senha provisória e cargo.
- Permite trocar o cargo de qualquer pessoa e ativar/desativar contas
  (sem apagar o histórico de auditoria dela).
- Você não consegue desativar a própria conta de admin por acidente.

### Estoque — exemplo completo das duas camadas (`controllers/estoque_controller.py`, `views/tela_estoque.py`)
Implementei o padrão completo aqui como **exemplo de referência**:
- Botões de **Novo Item / Editar / Excluir / Movimentação** só aparecem
  para quem pode editar estoque (Camada 1).
- `EstoqueController` **revalida a permissão de novo** antes de salvar,
  excluir ou registrar movimentação (Camada 2) — e grava na auditoria
  quando a ação é bem-sucedida.

## Como replicar o mesmo padrão nas outras telas
Pedidos, Clientes, Produtos e Entregadores ainda não têm a auditoria/permissão
plugada (só o roteamento de menu e o bloqueio de navegação, que já valem para
todas as telas). Para deixá-las no mesmo nível do Estoque, em cada controller:

```python
from controllers.auditoria_controller import AuditoriaController
from services import permissao_service

class XController:
    def __init__(self, conexao_banco, usuario_logado=None):
        self.model = XModel(conexao_banco)
        self.auditoria = AuditoriaController(conexao_banco)
        self.usuario_logado = usuario_logado

    def salvar(self, ...):
        if not permissao_service.pode_editar(self.usuario_logado, "NOME_DO_MODULO"):
            return False, "Você não tem permissão para isso."
        # ... lógica existente ...
        self.auditoria.registrar(self.usuario_logado, "editou", "NOME_DO_MODULO", "detalhe")
        return True, "Salvo!"
```

E na view correspondente, troque a instanciação do controller:
```python
usuario_logado = getattr(janela_raiz, "usuario_logado", None)
controlador = XController(janela_raiz.conn, usuario_logado)
```

## Limpeza feita no zip
Havia uma cópia duplicada e não usada de `controllers/`, `models/`, `views/`
e `banco/` dentro da própria pasta `views/` (resíduo de algum merge/zip
anterior). Como o `main.py` nunca importava dessa cópia, ela foi removida
para não confundir durante a manutenção.
