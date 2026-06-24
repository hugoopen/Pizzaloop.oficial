from datetime import date, timedelta


class RelatorioModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def _intervalo_periodo(self, periodo: str):
        hoje = date.today()
        if periodo == "hoje":
            return hoje, hoje
        elif periodo == "7dias":
            return hoje - timedelta(days=6), hoje
        elif periodo == "30dias":
            return hoje - timedelta(days=29), hoje
        elif periodo == "mes":
            return hoje.replace(day=1), hoje
        elif periodo == "ano":
            return hoje.replace(month=1, day=1), hoje
        else:
            return hoje - timedelta(days=6), hoje

    def obter_resumo(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(valor_total), 0), COUNT(*), COALESCE(AVG(valor_total), 0)
            FROM pedidos
            WHERE DATE(data_hora) BETWEEN %s AND %s
        """, (data_ini, data_fim))
        linha = cursor.fetchone()
        cursor.close()
        return float(linha[0]), int(linha[1]), float(linha[2])

    def obter_resumo_pagamentos(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN pago = 1 THEN valor_total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN pago = 0 THEN valor_total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN pago = 1 THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN pago = 0 THEN 1 ELSE 0 END), 0)
            FROM pedidos
            WHERE DATE(data_hora) BETWEEN %s AND %s
        """, (data_ini, data_fim))
        linha = cursor.fetchone()
        cursor.close()
        return float(linha[0]), float(linha[1]), int(linha[2]), int(linha[3])

    def obter_lucro(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(valor_total), 0)
            FROM pedidos
            WHERE DATE(data_hora) BETWEEN %s AND %s
        """, (data_ini, data_fim))
        receita = float(cursor.fetchone()[0])
        cursor.execute("""
            SELECT COALESCE(SUM(i.quantidade * pr.custo), 0)
            FROM pedidos p
            JOIN itens_pedidos i  ON p.id_pedidos = i.id_pedido
            JOIN produtos      pr ON i.id_produto  = pr.id_produto
            WHERE DATE(p.data_hora) BETWEEN %s AND %s
        """, (data_ini, data_fim))
        custo = float(cursor.fetchone()[0])
        cursor.close()
        lucro  = receita - custo
        margem = (lucro / receita * 100) if receita > 0 else 0.0
        return receita, custo, lucro, margem

    def obter_lucro_por_produto(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT
                pr.nome_produto,
                SUM(p.valor_total)            AS receita_total,
                SUM(i.quantidade * pr.custo)  AS custo_total
            FROM pedidos p
            JOIN itens_pedidos i  ON p.id_pedidos = i.id_pedido
            JOIN produtos      pr ON i.id_produto  = pr.id_produto
            WHERE DATE(p.data_hora) BETWEEN %s AND %s
            GROUP BY pr.id_produto, pr.nome_produto
            ORDER BY (SUM(p.valor_total) - SUM(i.quantidade * pr.custo)) DESC
            LIMIT 10
        """, (data_ini, data_fim))
        linhas = cursor.fetchall()
        cursor.close()
        resultado = []
        for nome, receita, custo in linhas:
            r = float(receita)
            c = float(custo)
            resultado.append((nome, r, c, r - c))
        return resultado

    def obter_vendas_por_dia(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT DATE(data_hora), COUNT(*), COALESCE(SUM(valor_total), 0)
            FROM pedidos
            WHERE DATE(data_hora) BETWEEN %s AND %s
            GROUP BY DATE(data_hora)
            ORDER BY DATE(data_hora) ASC
        """, (data_ini, data_fim))
        linhas = cursor.fetchall()
        cursor.close()
        nomes_dias = {0: "Segunda", 1: "Terca", 2: "Quarta", 3: "Quinta",
                      4: "Sexta", 5: "Sabado", 6: "Domingo"}
        resultado = []
        for dia, qtd, total in linhas:
            nome_dia = nomes_dias.get(dia.weekday(), "")
            resultado.append((f"{nome_dia}, {dia.strftime('%d/%m')}", int(qtd), float(total)))
        return resultado

    def obter_performance_produtos(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT pr.nome_produto, SUM(i.quantidade) AS total_vendas, SUM(p.valor_total) AS receita_total
            FROM pedidos p
            JOIN itens_pedidos i ON p.id_pedidos = i.id_pedido
            JOIN produtos pr ON i.id_produto = pr.id_produto
            WHERE DATE(p.data_hora) BETWEEN %s AND %s
            GROUP BY pr.id_produto, pr.nome_produto
            ORDER BY total_vendas DESC
            LIMIT 10
        """, (data_ini, data_fim))
        linhas = cursor.fetchall()
        cursor.close()
        return [(nome, int(v), float(r)) for nome, v, r in linhas]

    def obter_horarios_movimento(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT HOUR(data_hora), COUNT(*), COALESCE(SUM(valor_total), 0)
            FROM pedidos
            WHERE DATE(data_hora) BETWEEN %s AND %s
            GROUP BY HOUR(data_hora)
            ORDER BY HOUR(data_hora) ASC
        """, (data_ini, data_fim))
        linhas = cursor.fetchall()
        cursor.close()
        return [(f"{h:02d}h", int(qtd), float(total)) for h, qtd, total in linhas]

    def obter_metodos_pagamento(self, periodo: str):
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT
                metodo_pagamento,
                COUNT(*),
                COALESCE(SUM(valor_total), 0),
                COALESCE(SUM(CASE WHEN pago = 1 THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN pago = 0 THEN 1 ELSE 0 END), 0)
            FROM pedidos
            WHERE DATE(data_hora) BETWEEN %s AND %s
            GROUP BY metodo_pagamento
        """, (data_ini, data_fim))
        linhas = cursor.fetchall()
        cursor.close()
        return [(m or "Nao informado", int(q), float(t), int(pg), int(npg))
                for m, q, t, pg, npg in linhas]

    # ── ESTOQUE ────────────────────────────────────────────────────────

    def obter_resumo_estoque(self):
        """Retorna (total_itens, itens_criticos, valor_total_estoque)."""
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT
                COUNT(*),
                SUM(CASE WHEN quantidade_atual < quantidade_minima THEN 1 ELSE 0 END),
                COALESCE(SUM(quantidade_atual * preco_custo), 0)
            FROM estoque
        """)
        linha = cursor.fetchone()
        cursor.close()
        total   = int(linha[0]) if linha[0] else 0
        criticos = int(linha[1]) if linha[1] else 0
        valor   = float(linha[2]) if linha[2] else 0.0
        return total, criticos, valor

    def obter_itens_criticos_estoque(self):
        """Retorna itens abaixo do mínimo ordenados pelo mais crítico."""
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT nome_item, categoria,
                   quantidade_atual, quantidade_minima, unidade_medida,
                   COALESCE(preco_custo, 0)
            FROM estoque
            WHERE quantidade_atual < quantidade_minima
            ORDER BY (quantidade_minima - quantidade_atual) DESC
            LIMIT 15
        """)
        linhas = cursor.fetchall()
        cursor.close()
        return [(str(nome), str(cat), float(atual), float(minimo), str(und), float(preco))
                for nome, cat, atual, minimo, und, preco in linhas]

    def obter_movimentacoes_estoque(self, periodo: str):
        """Retorna movimentações de estoque no período."""
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT
                e.nome_item,
                me.tipo,
                me.quantidade,
                e.unidade_medida,
                me.observacao,
                DATE(me.data_hora) AS dia
            FROM movimentacoes_estoque me
            JOIN estoque e ON me.id_item = e.id_item
            WHERE DATE(me.data_hora) BETWEEN %s AND %s
            ORDER BY me.data_hora DESC
            LIMIT 20
        """, (data_ini, data_fim))
        linhas = cursor.fetchall()
        cursor.close()
        return [(str(nome), str(tipo), float(qtd), str(und), str(obs or ""), str(dia))
                for nome, tipo, qtd, und, obs, dia in linhas]

    def obter_consumo_por_produto(self, periodo: str):
        """
        Retorna quanto de estoque foi consumido por produto no período,
        usando a tabela produto_ingredientes (criada pelo SQL fornecido).
        Retorna lista vazia se a tabela ainda não existir.
        """
        data_ini, data_fim = self._intervalo_periodo(periodo)
        cursor = self.conexao.cursor()
        try:
            cursor.execute("""
                SELECT
                    pr.nome_produto,
                    SUM(i.quantidade)                          AS qtd_vendida,
                    SUM(i.quantidade * pi.quantidade_usada)    AS total_consumido,
                    e.nome_item,
                    e.unidade_medida
                FROM pedidos p
                JOIN itens_pedidos     i   ON p.id_pedidos   = i.id_pedido
                JOIN produtos          pr  ON i.id_produto   = pr.id_produto
                JOIN produto_ingredientes pi ON pr.id_produto = pi.id_produto
                JOIN estoque           e   ON pi.id_item     = e.id_item
                WHERE DATE(p.data_hora) BETWEEN %s AND %s
                GROUP BY pr.id_produto, pr.nome_produto, e.id_item, e.nome_item, e.unidade_medida
                ORDER BY total_consumido DESC
                LIMIT 15
            """, (data_ini, data_fim))
            linhas = cursor.fetchall()
            cursor.close()
            return [(str(prod), int(qtd_v), float(cons), str(item), str(und))
                    for prod, qtd_v, cons, item, und in linhas]
        except Exception:
            cursor.close()
            return []
