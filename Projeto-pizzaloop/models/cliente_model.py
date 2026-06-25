class ClienteModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def buscar_todos(self):
        """Retorna lista simples de clientes (sem estatísticas)."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cliente ORDER BY nome ASC")
        lista = cursor.fetchall()
        cursor.close()
        return lista

    def buscar_todos_com_estatisticas(self):
        """Retorna clientes com total de pedidos, total gasto e data do último pedido."""
        cursor = self.conexao.cursor(dictionary=True)
        consulta = """
            SELECT
                c.*,
                COUNT(p.id_pedidos)            AS total_pedidos,
                COALESCE(SUM(p.valor_total), 0) AS total_gasto,
                MAX(DATE(p.data_hora))          AS ultimo_pedido
            FROM cliente c
            LEFT JOIN pedidos p ON c.id_cliente = p.id_cliente
            GROUP BY c.id_cliente
            ORDER BY c.nome ASC
        """
        cursor.execute(consulta)
        lista = cursor.fetchall()
        cursor.close()
        return lista

    def salvar_dados(self, nome_cliente, telefone_cliente, cpf_cliente,
                     email_cliente="",
                     cep_cliente="", endereco_cliente="",
                     numero_cliente="", bairro_cliente="", cidade_cliente="",
                     id_cliente=None):
        cursor = self.conexao.cursor()
        if id_cliente:
            cursor.execute(
                """UPDATE cliente
                   SET nome = %s, telefone = %s, cpf = %s,
                       email = %s,
                       cep = %s, endereco = %s, numero = %s,
                       bairro = %s, cidade = %s
                   WHERE id_cliente = %s""",
                (nome_cliente, telefone_cliente, cpf_cliente,
                 email_cliente,
                 cep_cliente, endereco_cliente, numero_cliente,
                 bairro_cliente, cidade_cliente, id_cliente)
            )
        else:
            cursor.execute(
                """INSERT INTO cliente
                       (nome, telefone, cpf, email, cep, endereco, numero, bairro, cidade)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (nome_cliente, telefone_cliente, cpf_cliente,
                 email_cliente,
                 cep_cliente, endereco_cliente, numero_cliente,
                 bairro_cliente, cidade_cliente)
            )
        self.conexao.commit()
        cursor.close()

    def excluir(self, id_cliente):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
        self.conexao.commit()
        cursor.close()
