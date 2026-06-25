-- ============================================================
--  PizzaLoop — RBAC (Cargos/Permissões) + Auditoria
--  Execute estes comandos no MySQL Workbench, na ordem abaixo.
-- ============================================================

-- ── 0. LIMPEZA: remove a tabela 'cargos' de um exemplo genérico
--    anterior, que não é usada nesta implementação (o cargo fica
--    direto na coluna 'login.cargo', sem tabela relacional) ────
DROP TABLE IF EXISTS cargos;

-- Observação: se você também rodou o ALTER TABLE usuarios ADD COLUMN
-- cargo_id / ativo daquele exemplo genérico, a coluna cargo_id pode
-- ficar "presa" na tabela usuarios sem nenhuma tabela cargos pra
-- referenciar. Isso não quebra nada (a coluna simplesmente não é
-- usada), mas se quiser remover a sujeira, veja as instruções que te
-- passei na conversa (precisa achar o nome da FK antes de remover a
-- coluna). Não é obrigatório para o sistema funcionar.

-- ── 1. CARGO E DADOS DO USUÁRIO NA TABELA LOGIN ────────────
-- Cargos suportados: 'admin', 'socio', 'funcionario', 'entregador'

ALTER TABLE login
    ADD COLUMN IF NOT EXISTS nome   VARCHAR(100) NOT NULL DEFAULT '' AFTER email,
    ADD COLUMN IF NOT EXISTS cargo  VARCHAR(20)  NOT NULL DEFAULT 'funcionario' AFTER senha,
    ADD COLUMN IF NOT EXISTS ativo  TINYINT(1)   NOT NULL DEFAULT 1 AFTER cargo;

-- Se o comando acima der erro no seu MySQL, execute um de cada vez:
-- ALTER TABLE login ADD COLUMN IF NOT EXISTS nome  VARCHAR(100) NOT NULL DEFAULT '' AFTER email;
-- ALTER TABLE login ADD COLUMN IF NOT EXISTS cargo VARCHAR(20)  NOT NULL DEFAULT 'funcionario' AFTER senha;
-- ALTER TABLE login ADD COLUMN IF NOT EXISTS ativo TINYINT(1)   NOT NULL DEFAULT 1 AFTER cargo;

-- ── 2. IMPORTANTE: marque seu usuário atual como admin ─────
-- Já preenchido com o seu e-mail (adm1@gmail.com). Se quiser, troque
-- 'Admin PizzaLoop' pelo seu nome de verdade antes de executar.

UPDATE login SET nome = 'Admin PizzaLoop', cargo = 'admin' WHERE email = 'adm1@gmail.com';


-- ── 3. TABELA DE AUDITORIA (histórico de alterações) ───────
CREATE TABLE IF NOT EXISTS auditoria (
    id_auditoria  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_email VARCHAR(150) NOT NULL,
    usuario_nome  VARCHAR(100) NOT NULL,
    usuario_cargo VARCHAR(20)  NOT NULL,
    acao          VARCHAR(20)  NOT NULL,   -- 'criou', 'editou', 'excluiu'
    modulo        VARCHAR(30)  NOT NULL,   -- 'estoque', 'pedidos', 'produtos', etc.
    detalhe       TEXT         DEFAULT NULL,
    data_hora     DATETIME     NOT NULL DEFAULT NOW()
);
