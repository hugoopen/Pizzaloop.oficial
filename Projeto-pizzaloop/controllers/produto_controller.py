from models.produto_model import ProdutoModel


class ProdutoController:

    def __init__(self, conexao_banco):
        self.conexao_banco = conexao_banco
        self.model_produto = ProdutoModel(conexao_banco)

    def listar_para_view(self):
        return self.model_produto.buscar_todos()

    def validar_e_salvar(
        self,
        nome_produto,
        texto_preco,
        id_produto=None,
        descricao_produto="",
        categoria_produto="Salgada",
        texto_custo="0"
    ):
        try:
            nome_produto = nome_produto.strip()

            if not nome_produto:
                return False, "Nome do produto é obrigatório."

            if not texto_preco.strip():
                return False, "Preço é obrigatório."

            preco_convertido = float(texto_preco.replace(",", ".").strip())

            if preco_convertido <= 0:
                return False, "Preço deve ser maior que zero."

            custo_convertido = 0.0
            if texto_custo and str(texto_custo).strip():
                custo_convertido = float(str(texto_custo).replace(",", ".").strip())
                if custo_convertido < 0:
                    return False, "Custo não pode ser negativo."

            self.model_produto.salvar_dados(
                nome_produto,
                preco_convertido,
                id_produto,
                descricao_produto,
                categoria_produto,
                custo_convertido
            )

            if self.conexao_banco:
                try:
                    self.conexao_banco.commit()
                except AttributeError:
                    pass

            return True, "Produto salvo com sucesso!"

        except ValueError:
            return False, "Preço ou custo inválido. Use números (ex: 29.90)."
        except Exception as erro:
            return False, f"Erro ao salvar no banco: {erro}"

    # ========================================================
    # NOVO: GESTÃO DE MÚLTIPLOS TAMANHOS POR PRODUTO
    # ========================================================

    def validar_e_salvar_com_tamanhos(self, nome_produto, categoria_produto, descricao_produto, dados_tamanhos, id_produto=None):
        """
        Valida e envia para o Model o produto base e o dicionário contendo
        as fatias e os preços correspondentes de cada tamanho (P, M, G, Família).
        """
        try:
            nome_produto = nome_produto.strip()
            if not nome_produto:
                return False, "Nome do produto é obrigatório."
            
            if not dados_tamanhos:
                return False, "É necessário definir os preços dos tamanhos para a pizza."

            # Define um preço padrão para a tabela geral de produtos (usando o tamanho Grande como base)
            preco_padrao = dados_tamanhos.get("Grande", {}).get("preco", 0.00)
            try:
                preco_convertido = float(str(preco_padrao).replace(",", ".").strip())
            except ValueError:
                preco_convertido = 0.00

            # 1. Salva os dados básicos na tabela 'produtos' através do Model
            id_prod_final = self.model_produto.salvar_dados(
                nome_produto=nome_produto,
                preco_produto=preco_convertido,
                id_produto=id_produto,
                descricao_produto=descricao_produto,
                categoria_produto=categoria_produto,
                custo_produto=0.0  # O custo pode ser atrelado aos tamanhos ou deixado como zero
            )

            if not id_prod_final and id_produto:
                id_prod_final = id_produto

            if not id_prod_final:
                return False, "Erro ao gerar identificador do produto principal."

            # 2. Processa as strings de preço do dicionário e salva os tamanhos associados
            dados_processados = {}
            for nome_tamanho, info in dados_tamanhos.items():
                try:
                    preco_float = float(str(info["preco"]).replace(",", ".").strip())
                except ValueError:
                    return False, f"O preço do tamanho {nome_tamanho} é inválido."
                
                dados_processados[nome_tamanho] = {
                    "fatias": info["fatias"],
                    "preco": preco_float
                }

            # Envia para a nova função correspondente no seu model_produto
            self.model_produto.salvar_tamanhos_do_produto(id_prod_final, dados_processados)

            if self.conexao_banco:
                try:
                    self.conexao_banco.commit()
                except AttributeError:
                    pass

            return True, f"Pizza '{nome_produto}' e seus tamanhos salvos com sucesso!"

        except Exception as erro:
            return False, f"Erro ao salvar tamanhos do produto: {erro}"

    def obter_tamanhos_do_produto(self, id_produto):
        """
        Busca os tamanhos cadastrados para um produto específico para carregar na View.
        """
        try:
            if not id_produto:
                return {}
            # Delega para o Model buscar da tabela 'tamanhos_produto'
            return self.model_produto.buscar_tamanhos_do_produto(id_produto)
        except Exception as e:
            print(f"Erro ao obter tamanhos para o produto {id_produto}: {e}")
            return {}

    # ========================================================
    # MANUTENÇÃO DOS MÉTODOS ANTERIORES
    # ========================================================

    def validar_e_salvar_combo(
        self,
        nome_combo,
        texto_preco,
        ids_produtos_associados,
        id_produto=None,
        descricao_combo="",
        texto_custo="0"
    ):
        try:
            nome_combo = nome_combo.strip()

            if not nome_combo:
                return False, "Nome do combo é obrigatório."

            if not id_produto:
                if not ids_produtos_associados or len(ids_produtos_associados) < 2:
                    return False, "Deve conter pelo menos 2 produtos selecionados na composição."

            texto_preco_limpo = str(texto_preco).strip()

            if not texto_preco_limpo or texto_preco_limpo == "0.00":
                precos_sabores = []
                todos_produtos = self.model_produto.buscar_todos()
                for prod in todos_produtos:
                    if str(prod["id_produto"]) in [str(x) for x in ids_produtos_associados]:
                        precos_sabores.append(prod["preco"])

                if precos_sabores:
                    preco_convertido = float(max(precos_sabores))
                else:
                    return False, "Preço do combo é obrigatório ou não pôde ser calculado."
            else:
                preco_convertido = float(texto_preco_limpo.replace(",", "."))

            if preco_convertido <= 0:
                return False, "Preço calculated ou inserido deve ser maior que zero."

            custo_convertido = 0.0
            if texto_custo and str(texto_custo).strip():
                try:
                    custo_convertido = float(str(texto_custo).replace(",", ".").strip())
                except ValueError:
                    custo_convertido = 0.0

            id_combo_final = self.model_produto.salvar_dados(
                nome_produto=nome_combo,
                preco_produto=preco_convertido,
                id_produto=id_produto,
                descricao_produto=descricao_combo,
                categoria_produto="Combo",
                custo_produto=custo_convertido
            )

            if not id_combo_final and id_produto:
                id_combo_final = id_produto

            if id_combo_final:
                if ids_produtos_associados:
                    self.model_produto.salvar_itens_do_combo(id_combo_final, ids_produtos_associados)
                else:
                    print("[Info] Mantendo os sabores atuais do combo. Atualizado apenas dados básicos.")
            else:
                return False, "Falha ao registrar referências identificadoras do item no sistema."

            if self.conexao_banco:
                try:
                    self.conexao_banco.commit()
                except AttributeError:
                    pass

            return True, "Combo salvo com sucesso!"

        except ValueError:
            return False, "Preço inválido enviado para o sistema. Verifique a formatação do valor."
        except Exception as erro:
            return False, f"Erro ao salvar combo no sistema: {erro}"

    def excluir(self, id_produto):
        try:
            self.model_produto.excluir(id_produto)
            if self.conexao_banco:
                try:
                    self.conexao_banco.commit()
                except AttributeError:
                    pass
            return True, "Produto excluído com sucesso."
        except Exception as erro:
            return False, f"Não foi possível excluir: {erro}"

    def atualizar_caminho_imagem(self, id_produto, novo_caminho):
        try:
            if hasattr(self.model_produto, "atualizar_imagem_banco"):
                self.model_produto.atualizar_imagem_banco(id_produto, novo_caminho)

                if self.conexao_banco:
                    try:
                        self.conexao_banco.commit()
                    except AttributeError:
                        pass

                return True, "Imagem salva com sucesso no banco de dados!"
            else:
                msg_erro = "O método 'atualizar_imagem_banco' não foi implementado no ProdutoModel."
                print(f"[Erro] {msg_erro}")
                return False, msg_erro

        except Exception as erro:
            print(f"Erro no Controller ao tentar atualizar imagem: {erro}")
            return False, f"Erro ao atualizar imagem no banco de dados: {erro}"

    def obter_produtos_do_combo(self, id_combo):
        try:
            return self.model_produto.buscar_produtos_do_combo(id_combo)
        except Exception as e:
            print(f"Erro ao buscar composição do combo {e}")
            return []