-- ============================================================
--  PizzaLoop — Integração Estoque ↔ Relatório
--  Execute estes comandos UMA VEZ no seu banco MySQL.
-- ============================================================

-- ── 1. TABELA: produto_ingredientes ──────────────────────────
--  Liga cada produto a um ou mais itens do estoque,
--  informando quanto de cada ingrediente é consumido
--  por unidade vendida do produto.
--
--  Exemplo: 1 Pizza usa 0.3 kg de Queijo + 0.2 kg de Farinha
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS produto_ingredientes (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    id_produto       INT            NOT NULL,
    id_item          INT            NOT NULL,
    quantidade_usada DECIMAL(10, 3) NOT NULL DEFAULT 1.000,
    CONSTRAINT fk_pi_produto FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto) ON DELETE CASCADE,
    CONSTRAINT fk_pi_item    FOREIGN KEY (id_item)
        REFERENCES estoque(id_item)    ON DELETE CASCADE,
    UNIQUE KEY uq_prod_item (id_produto, id_item)
);

-- ── 2. COMO USAR ──────────────────────────────────────────────
--  Após criar a tabela, vincule seus produtos aos ingredientes.
--  Substitua os IDs pelos reais do seu banco.
--
--  Exemplo:
--  INSERT INTO produto_ingredientes (id_produto, id_item, quantidade_usada)
--  VALUES
--      (1, 3, 0.300),   -- Produto 1 usa 300g do item 3 (Queijo)
--      (1, 5, 0.200),   -- Produto 1 usa 200g do item 5 (Farinha)
--      (2, 3, 0.250);   -- Produto 2 usa 250g do item 3 (Queijo)
--
--  Para descobrir os IDs:
--      SELECT id_produto, nome_produto FROM produtos;
--      SELECT id_item,    nome_item    FROM estoque;

-- ── 3. COLUNA preco_custo NO ESTOQUE (se ainda não existir) ──
ALTER TABLE estoque
    ADD COLUMN IF NOT EXISTS preco_custo DECIMAL(10, 2) DEFAULT 0.00;
