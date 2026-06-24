class EntregaModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def obter_estatisticas(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM entregas WHERE status_entrega = 'Preparando'")
        preparando = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM entregas WHERE status_entrega = 'Em Rota'")
        em_rota = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM entregas WHERE status_entrega = 'Entregue' AND DATE(hora_entrega) = CURDATE()")
        entregues_hoje = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(AVG(TIMESTAMPDIFF(MINUTE, hora_saida, hora_entrega)), 0) FROM entregas WHERE hora_saida IS NOT NULL AND hora_entrega IS NOT NULL AND DATE(hora_entrega) = CURDATE()")
        tempo_medio = cursor.fetchone()[0] or 0
        cursor.close()
        return preparando, em_rota, entregues_hoje, int(tempo_medio)

    def listar_entregas(self):
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                e.*,
                p.valor_total,
                c.nome   AS nome_cliente,
                c.telefone AS telefone_cliente,
                c.endereco AS endereco_cliente
            FROM entregas e
            JOIN pedidos p  ON e.id_pedido = p.id_pedidos
            JOIN cliente c  ON p.id_cliente = c.id_cliente
            ORDER BY e.id_entrega DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        for r in rows:
            if r.get("hora_saida"):
                try:
                    r["hora_saida_fmt"] = r["hora_saida"].strftime("%H:%M")
                except Exception:
                    r["hora_saida_fmt"] = str(r["hora_saida"])
            else:
                r["hora_saida_fmt"] = "--"
        return rows

    def listar_pedidos_sem_entrega(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
            SELECT p.id_pedidos, c.nome
            FROM pedidos p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            ORDER BY p.id_pedidos DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def salvar(self, id_pedido, nome_entregador, telefone_entregador,
               veiculo, endereco_entrega, tempo_estimado, status_entrega,
               id_entrega=None):
        cursor = self.conexao.cursor()
        hora_saida = "NOW()" if status_entrega == "Em Rota" else "NULL"
        hora_entrega = "NOW()" if status_entrega == "Entregue" else "NULL"
        if id_entrega:
            cursor.execute(f"""
                UPDATE entregas SET
                    id_pedido           = %s,
                    nome_entregador     = %s,
                    telefone_entregador = %s,
                    veiculo             = %s,
                    endereco_entrega    = %s,
                    tempo_estimado      = %s,
                    status_entrega      = %s,
                    hora_saida          = CASE WHEN %s = 'Em Rota'  AND hora_saida   IS NULL THEN NOW() ELSE hora_saida   END,
                    hora_entrega        = CASE WHEN %s = 'Entregue' AND hora_entrega IS NULL THEN NOW() ELSE hora_entrega END
                WHERE id_entrega = %s
            """, (id_pedido, nome_entregador, telefone_entregador,
                  veiculo, endereco_entrega, tempo_estimado, status_entrega,
                  status_entrega, status_entrega, id_entrega))
        else:
            cursor.execute("""
                INSERT INTO entregas
                    (id_pedido, nome_entregador, telefone_entregador,
                     veiculo, endereco_entrega, tempo_estimado, status_entrega)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_pedido, nome_entregador, telefone_entregador,
                  veiculo, endereco_entrega, tempo_estimado, status_entrega))
        self.conexao.commit()
        cursor.close()

    def excluir(self, id_entrega):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM entregas WHERE id_entrega = %s", (id_entrega,))
        self.conexao.commit()
        cursor.close()
