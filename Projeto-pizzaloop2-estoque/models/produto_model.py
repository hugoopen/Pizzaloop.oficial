class ProdutoModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def buscar_todos(self):
        with self.conexao.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM produtos")
            produtos = cursor.fetchall()
        return produtos

    def salvar_dados(
        self,
        nome_produto,
        preco_produto,
        id_produto=None,
        descricao_produto="",
        categoria_produto="Salgada",
        custo_produto=0.0
    ):
        cursor = self.conexao.cursor()
        try:
            if id_produto:
                cursor.execute(
                    """
                    UPDATE produtos
                    SET
                        nome_produto=%s,
                        preco=%s,
                        descricao=%s,
                        categoria=%s,
                        custo=%s
                    WHERE id_produto=%s
                    """,
                    (
                        nome_produto,
                        preco_produto,
                        descricao_produto,
                        categoria_produto,
                        custo_produto,
                        id_produto
                    )
                )
                id_retorno = id_produto
            else:
                cursor.execute(
                    """
                    INSERT INTO produtos
                    (
                        nome_produto,
                        preco,
                        descricao,
                        categoria,
                        custo
                    )
                    VALUES
                    (%s, %s, %s, %s, %s)
                    """,
                    (
                        nome_produto,
                        preco_produto,
                        descricao_produto,
                        categoria_produto,
                        custo_produto
                    )
                )
                id_retorno = cursor.lastrowid

            self.conexao.commit()
            return id_retorno

        except Exception as e:
            self.conexao.rollback()
            print(f"[ProdutoModel] Erro ao salvar dados do produto: {e}")
            raise e
        finally:
            cursor.close()

    # ========================================================
    # NOVO: PERSISTÊNCIA DE MÚLTIPLOS TAMANHOS POR PIZZA
    # ========================================================

    def salvar_tamanhos_do_produto(self, id_produto, dados_tamanhos):
        """
        Limpa as configurações antigas de tamanhos do produto e insere 
        o novo conjunto de dados estruturado (Tamanho, Fatias, Preço).
        """
        cursor = self.conexao.cursor()
        try:
            # 1. Limpa os registros antigos caso seja uma edição de produto
            cursor.execute("DELETE FROM tamanhos_produto WHERE id_produto = %s", (id_produto,))
            
            # 2. Insere as variações atualizadas vinda do dicionário mapeado
            sql_inserir = """
                INSERT INTO tamanhos_produto (id_produto, tamanho, fatias, preco) 
                VALUES (%s, %s, %s, %s)
            """
            for nome_tamanho, info in dados_tamanhos.items():
                cursor.execute(sql_inserir, (id_produto, nome_tamanho, info["fatias"], info["preco"]))
                
            # Nota: O commit final é gerenciado na Controller que engloba a operação
            print(f"[ProdutoModel] Tamanhos vinculados com sucesso ao produto ID {id_produto}.")
        except Exception as e:
            print(f"[ProdutoModel] Erro ao salvar tamanhos do produto id={id_produto}: {e}")
            raise e
        finally:
            cursor.close()

    def buscar_tamanhos_do_produto(self, id_produto):
        """
        Retorna as variações de tamanhos salvas de um produto formatadas como dicionário
        para popular os componentes dinâmicos na View.
        """
        with self.conexao.cursor(dictionary=True) as cursor:
            try:
                cursor.execute(
                    "SELECT tamanho, fatias, preco FROM tamanhos_produto WHERE id_produto = %s", 
                    (id_produto,)
                )
                resultados = cursor.fetchall()
                
                mapa_tamanhos = {}
                for linha in resultados:
                    mapa_tamanhos[linha["tamanho"]] = {
                        "fatias": linha["fatias"],
                        "preco": float(linha["preco"])
                    }
                return mapa_tamanhos
            except Exception as e:
                print(f"[ProdutoModel] Erro ao buscar tamanhos do produto id={id_produto}: {e}")
                return {}

    # ========================================================
    # MANUTENÇÃO DOS MÉTODOS ANTERIORES
    # ========================================================

    def salvar_itens_do_combo(self, id_combo, ids_produtos_associados):
        cursor = self.conexao.cursor()
        try:
            cursor.execute("DELETE FROM combo_produtos WHERE id_combo = %s", (id_combo,))
            sql_inserir = "INSERT INTO combo_produtos (id_combo, id_produto) VALUES (%s, %s)"
            for id_prod in ids_produtos_associados:
                cursor.execute(sql_inserir, (id_combo, id_prod))
            self.conexao.commit()
            print(f"[ProdutoModel] Itens do combo {id_combo} vinculados com sucesso.")
        except Exception as e:
            self.conexao.rollback()
            print(f"[ProdutoModel] Erro ao salvar itens associados do combo: {e}")
            raise e
        finally:
            cursor.close()

    def buscar_produtos_do_combo(self, id_combo):
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT id_produto FROM combo_produtos WHERE id_combo = %s", (id_combo,))
            resultados = cursor.fetchall()
            return [linha[0] for linha in resultados]

    def excluir(self, id_produto):
        cursor = self.conexao.cursor()
        try:
            cursor.execute("DELETE FROM produtos WHERE id_produto=%s", (id_produto,))
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            print(f"[ProdutoModel] Erro ao excluir produto id={id_produto}: {e}")
            raise e
        finally:
            cursor.close()

    def atualizar_imagem_banco(self, id_produto, novo_caminho_imagem):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                """
                UPDATE produtos
                SET
                    imagem=%s
                WHERE id_produto=%s
                """,
                (
                    novo_caminho_imagem,
                    id_produto
                )
            )
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            print(f"[ProdutoModel] Erro ao atualizar imagem do produto id={id_produto}: {e}")
            raise e
        finally:
            cursor.close()