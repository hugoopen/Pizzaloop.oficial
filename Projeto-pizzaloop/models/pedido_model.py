class PedidoModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def listar_pedidos_completos(self):
        cursor = self.conexao.cursor(dictionary=True)
        consulta_pedidos = """
            SELECT
                p.*,
                c.nome         AS nome_cliente,
                pr.nome_produto,
                i.quantidade,
                p.data_hora,
                e.nome         AS nome_entregador
            FROM pedidos p
            JOIN cliente       c  ON p.id_cliente = c.id_cliente
            JOIN itens_pedidos i  ON p.id_pedidos = i.id_pedido
            JOIN produtos      pr ON i.id_produto = pr.id_produto
            LEFT JOIN entregadores e ON p.id_entregador = e.id_entregador
            ORDER BY p.id_pedidos DESC
        """
        cursor.execute(consulta_pedidos)
        lista_pedidos = cursor.fetchall()
        cursor.close()
        for pedido in lista_pedidos:
            data_hora = pedido.get("data_hora")
            if data_hora:
                try:
                    pedido["data_formatada"] = data_hora.strftime("%d/%m %H:%M")
                except Exception:
                    pedido["data_formatada"] = str(data_hora)
            else:
                pedido["data_formatada"] = "--"
            if "pago" not in pedido:
                pedido["pago"] = 0
        return lista_pedidos

    def salvar_pedido_completo(self, id_cliente, id_produto, quantidade,
                               preco_unitario, status_pedido, metodo_pagamento,
                               id_entregador=None, id_pedido=None, tempo_preparo="20 min", pago=0):
        cursor = self.conexao.cursor()
        valor_total_pedido = float(preco_unitario) * int(quantidade)
        if id_pedido:
            cursor.execute(
                """UPDATE pedidos
                   SET id_cliente       = %s,
                       valor_total      = %s,
                       status_pedido    = %s,
                       metodo_pagamento = %s,
                       id_entregador    = %s,
                       tempo_preparo    = %s,
                       pago             = %s
                   WHERE id_pedidos = %s""",
                (id_cliente, valor_total_pedido, status_pedido,
                 metodo_pagamento, id_entregador, tempo_preparo, pago, id_pedido)
            )
            cursor.execute(
                "UPDATE itens_pedidos SET id_produto = %s, quantidade = %s WHERE id_pedido = %s",
                (id_produto, quantidade, id_pedido)
            )
        else:
            cursor.execute(
                """INSERT INTO pedidos
                       (id_cliente, valor_total, status_pedido, metodo_pagamento,
                        id_entregador, tempo_preparo, pago, data_hora)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
                (id_cliente, valor_total_pedido, status_pedido,
                 metodo_pagamento, id_entregador, tempo_preparo, pago)
            )
            novo_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO itens_pedidos (id_pedido, id_produto, quantidade) VALUES (%s, %s, %s)",
                (novo_id, id_produto, quantidade)
            )
        self.conexao.commit()
        cursor.close()

    def alternar_pago(self, id_pedido, pago):
        cursor = self.conexao.cursor()
        cursor.execute("UPDATE pedidos SET pago = %s WHERE id_pedidos = %s", (pago, id_pedido))
        self.conexao.commit()
        cursor.close()

    def excluir(self, id_pedido):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM itens_pedidos WHERE id_pedido = %s", (id_pedido,))
        cursor.execute("DELETE FROM pedidos WHERE id_pedidos = %s", (id_pedido,))
        self.conexao.commit()
        cursor.close()
