class DashboardModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def obter_estatisticas(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM cliente")
        total_clientes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(valor_total) FROM pedidos")
        faturamento_total = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE DATE(data_hora) = CURDATE()")
        pedidos_realizados_hoje = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(AVG(valor_total), 0) FROM pedidos")
        valor_medio_pedido = cursor.fetchone()[0] or 0.0
        cursor.close()
        return total_clientes, total_pedidos, faturamento_total, pedidos_realizados_hoje, valor_medio_pedido

    def obter_ultimos_pedidos(self, limite=8):
        cursor = self.conexao.cursor(dictionary=True)
        consulta = """
            SELECT
                p.id_pedidos,
                c.nome           AS nome_cliente,
                pr.nome_produto,
                p.valor_total,
                p.status_pedido,
                p.metodo_pagamento,
                p.data_hora
            FROM pedidos p
            JOIN cliente       c  ON p.id_cliente = c.id_cliente
            JOIN itens_pedidos i  ON p.id_pedidos = i.id_pedido
            JOIN produtos      pr ON i.id_produto = pr.id_produto
            ORDER BY p.id_pedidos DESC
            LIMIT %s
        """
        cursor.execute(consulta, (limite,))
        pedidos = cursor.fetchall()
        cursor.close()
        for p in pedidos:
            dh = p.get("data_hora")
            if dh:
                try:
                    p["data_formatada"] = dh.strftime("%d/%m %H:%M")
                except Exception:
                    p["data_formatada"] = str(dh)
            else:
                p["data_formatada"] = "--"
        return pedidos

    def obter_vendas_semana(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT DATE(data_hora), COALESCE(SUM(valor_total), 0)
            FROM pedidos
            WHERE data_hora >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(data_hora)
            ORDER BY DATE(data_hora) ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
        dias_semana = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
        resultado = []
        for data, total in rows:
            resultado.append((dias_semana.get(data.weekday(), "?"), float(total)))
        return resultado

    def obter_pedidos_abertos_por_status(self):
        """Retorna dicionário {status: [lista de pedidos]} para os status em aberto."""
        cursor = self.conexao.cursor(dictionary=True)
        consulta = """
            SELECT
                p.id_pedidos,
                c.nome      AS nome_cliente,
                pr.nome_produto,
                p.valor_total,
                p.status_pedido,
                p.metodo_pagamento,
                p.data_hora
            FROM pedidos p
            JOIN cliente       c  ON p.id_cliente = c.id_cliente
            JOIN itens_pedidos i  ON p.id_pedidos = i.id_pedido
            JOIN produtos      pr ON i.id_produto = pr.id_produto
            WHERE p.status_pedido NOT IN ('Entregue', 'Cancelado')
            ORDER BY p.id_pedidos ASC
        """
        cursor.execute(consulta)
        pedidos = cursor.fetchall()
        cursor.close()

        grupos = {"Aguardando": [], "Em preparo": [], "A caminho": []}
        mapa_status = {
            "aguardando": "Aguardando",
            "em preparo": "Em preparo",
            "a caminho":  "A caminho",
        }
        for ped in pedidos:
            status_lower = (ped.get("status_pedido") or "").lower().strip()
            chave = mapa_status.get(status_lower)
            if chave:
                grupos[chave].append(ped)
        return grupos
