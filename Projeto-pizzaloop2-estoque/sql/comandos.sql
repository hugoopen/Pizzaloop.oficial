-- ============================================================
--  PizzaLoop — Comandos SQL para atualização do banco de dados
--  Execute estes comandos no seu banco MySQL na ordem abaixo.
-- ============================================================


-- ── 1. TABELA DE ENTREGADORES ─────────────────────────────
CREATE TABLE IF NOT EXISTS entregadores (
    id_entregador  INT AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(100)  NOT NULL,
    telefone       VARCHAR(20)   DEFAULT '',
    cpf            VARCHAR(14)   DEFAULT '',
    veiculo        VARCHAR(50)   DEFAULT '',
    placa          VARCHAR(10)   DEFAULT '',
    ativo          TINYINT(1)    NOT NULL DEFAULT 1,
    criado_em      DATETIME      DEFAULT NOW()
);


-- ── 2. ADICIONAR COLUNAS DE ENDEREÇO NA TABELA CLIENTE ────
--  (execute cada linha separada se o seu cliente MySQL não
--   suportar múltiplos ADD COLUMN em uma só instrução)

ALTER TABLE cliente
    ADD COLUMN IF NOT EXISTS numero   VARCHAR(10)   DEFAULT '' AFTER endereco,
    ADD COLUMN IF NOT EXISTS bairro   VARCHAR(100)  DEFAULT '' AFTER numero,
    ADD COLUMN IF NOT EXISTS cidade   VARCHAR(100)  DEFAULT '' AFTER bairro;

-- Se o comando acima der erro, execute um de cada vez:
-- ALTER TABLE cliente ADD COLUMN IF NOT EXISTS numero  VARCHAR(10)  DEFAULT '' AFTER endereco;
-- ALTER TABLE cliente ADD COLUMN IF NOT EXISTS bairro  VARCHAR(100) DEFAULT '' AFTER numero;
-- ALTER TABLE cliente ADD COLUMN IF NOT EXISTS cidade  VARCHAR(100) DEFAULT '' AFTER bairro;


-- ── 3. ADICIONAR CAMPO DE E-MAIL NA TABELA CLIENTE ────────
ALTER TABLE cliente
    ADD COLUMN IF NOT EXISTS email VARCHAR(150) DEFAULT '' AFTER nome;

-- Se der erro:
-- ALTER TABLE cliente ADD COLUMN IF NOT EXISTS email VARCHAR(150) DEFAULT '' AFTER nome;


-- ── 4. ADICIONAR ENTREGADOR AOS PEDIDOS ───────────────────
ALTER TABLE pedidos
    ADD COLUMN IF NOT EXISTS id_entregador INT NULL AFTER metodo_pagamento;

-- Chave estrangeira opcional (só execute se quiser integridade referencial):
-- ALTER TABLE pedidos
--     ADD CONSTRAINT fk_pedido_entregador
--     FOREIGN KEY (id_entregador)
--     REFERENCES entregadores(id_entregador)
--     ON DELETE SET NULL;

-- ==== MODIFICAÇÃO: status de pagamento ====
-- Execute UMA VEZ antes de abrir o sistema:
ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS pago TINYINT(1) NOT NULL DEFAULT 0;
