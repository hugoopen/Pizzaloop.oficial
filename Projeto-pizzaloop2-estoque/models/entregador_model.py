class EntregadorModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def buscar_todos_entregadores(self):
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM entregadores ORDER BY nome ASC")
        lista = cursor.fetchall()
        cursor.close()
        return lista

    def buscar_entregadores_ativos(self):
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM entregadores WHERE ativo = 1 ORDER BY nome ASC")
        lista = cursor.fetchall()
        cursor.close()
        return lista

    def salvar_dados_entregador(self, nome_entregador, telefone_entregador,
                                 cpf_entregador, veiculo_entregador,
                                 placa_veiculo, id_entregador=None):
        cursor = self.conexao.cursor()
        if id_entregador:
            cursor.execute(
                """UPDATE entregadores
                   SET nome = %s, telefone = %s, cpf = %s,
                       veiculo = %s, placa = %s
                   WHERE id_entregador = %s""",
                (nome_entregador, telefone_entregador, cpf_entregador,
                 veiculo_entregador, placa_veiculo, id_entregador)
            )
        else:
            cursor.execute(
                """INSERT INTO entregadores (nome, telefone, cpf, veiculo, placa, ativo)
                   VALUES (%s, %s, %s, %s, %s, 1)""",
                (nome_entregador, telefone_entregador, cpf_entregador,
                 veiculo_entregador, placa_veiculo)
            )
        self.conexao.commit()
        cursor.close()

    def alternar_status_ativo_entregador(self, id_entregador):
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE entregadores SET ativo = NOT ativo WHERE id_entregador = %s",
            (id_entregador,)
        )
        self.conexao.commit()
        cursor.close()

    def excluir_entregador(self, id_entregador):
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM entregadores WHERE id_entregador = %s",
            (id_entregador,)
        )
        self.conexao.commit()
        cursor.close()
