class EstoqueModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def buscar_todos(self):
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estoque ORDER BY categoria ASC, nome_item ASC")
        lista = cursor.fetchall()
        cursor.close()
        return lista

    def buscar_por_id(self, id_item):
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estoque WHERE id_item = %s", (id_item,))
        item = cursor.fetchone()
        cursor.close()
        return item

    def salvar(self, nome_item, categoria, quantidade_atual,
               unidade_medida, quantidade_minima, id_item=None, preco_custo=0.0):
        cursor = self.conexao.cursor()
        try:
            if id_item:
                cursor.execute(
                    """UPDATE estoque
                       SET nome_item = %s, categoria = %s,
                           quantidade_atual = %s, unidade_medida = %s,
                           quantidade_minima = %s, preco_custo = %s
                       WHERE id_item = %s""",
                    (nome_item, categoria, quantidade_atual,
                     unidade_medida, quantidade_minima, preco_custo, id_item)
                )
            else:
                cursor.execute(
                    """INSERT INTO estoque
                           (nome_item, categoria, quantidade_atual,
                            unidade_medida, quantidade_minima, preco_custo)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (nome_item, categoria, quantidade_atual,
                     unidade_medida, quantidade_minima, preco_custo)
                )
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            raise e
        finally:
            cursor.close()

    def excluir(self, id_item):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "DELETE FROM movimentacoes_estoque WHERE id_item = %s", (id_item,)
            )
            cursor.execute(
                "DELETE FROM estoque WHERE id_item = %s", (id_item,)
            )
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            raise e
        finally:
            cursor.close()

    def registrar_movimentacao(self, id_item, tipo, quantidade, observacao=""):
        cursor = self.conexao.cursor()
        try:
            if tipo == "Entrada":
                cursor.execute(
                    "UPDATE estoque SET quantidade_atual = quantidade_atual + %s WHERE id_item = %s",
                    (quantidade, id_item)
                )
            elif tipo == "Saída":
                cursor.execute(
                    "UPDATE estoque SET quantidade_atual = GREATEST(0, quantidade_atual - %s) WHERE id_item = %s",
                    (quantidade, id_item)
                )
            elif tipo == "Ajuste":
                cursor.execute(
                    "UPDATE estoque SET quantidade_atual = %s WHERE id_item = %s",
                    (quantidade, id_item)
                )

            cursor.execute(
                """INSERT INTO movimentacoes_estoque
                       (id_item, tipo, quantidade, observacao)
                   VALUES (%s, %s, %s, %s)""",
                (id_item, tipo, quantidade, observacao)
            )
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            raise e
        finally:
            cursor.close()

    def buscar_movimentacoes(self, id_item, limite=30):
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """SELECT * FROM movimentacoes_estoque
               WHERE id_item = %s
               ORDER BY data_hora DESC
               LIMIT %s""",
            (id_item, limite)
        )
        lista = cursor.fetchall()
        cursor.close()
        return lista

    def contar_itens_abaixo_minimo(self):
        cursor = self.conexao.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM estoque WHERE quantidade_atual < quantidade_minima"
        )
        resultado = cursor.fetchone()[0]
        cursor.close()
        return resultado
