CREATE TABLE IF NOT EXISTS entregas (
    id_entrega        INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido         INT NOT NULL,
    nome_entregador   VARCHAR(100) NOT NULL,
    telefone_entregador VARCHAR(20),
    veiculo           VARCHAR(60),
    endereco_entrega  VARCHAR(255),
    tempo_estimado    INT DEFAULT 30,
    status_entrega    VARCHAR(30) DEFAULT 'Preparando',
    hora_saida        DATETIME,
    hora_entrega      DATETIME,
    criado_em         DATETIME DEFAULT NOW(),
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedidos) ON DELETE CASCADE
);
