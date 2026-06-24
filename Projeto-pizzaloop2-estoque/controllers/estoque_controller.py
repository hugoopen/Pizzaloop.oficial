from models.estoque_model import EstoqueModel
from controllers.auditoria_controller import AuditoriaController
from services import permissao_service

CATEGORIAS_VALIDAS = ["Massa", "Carne", "Queijo", "Molho", "Bebida", "Embalagem", "Frios", "Geral"]
UNIDADES_VALIDAS   = ["unidade", "kg", "g", "litro", "ml", "pacote", "caixa"]

MSG_SEM_PERMISSAO = "Você não tem permissão para alterar o estoque. Fale com o administrador."


class EstoqueController:

    def __init__(self, conexao_banco, usuario_logado=None):
        self.model = EstoqueModel(conexao_banco)
        self.auditoria = AuditoriaController(conexao_banco)
        self.usuario_logado = usuario_logado

    def _pode_editar(self):
        return permissao_service.pode_editar(self.usuario_logado, "estoque")

    def listar_itens(self):
        return self.model.buscar_todos()

    def validar_e_salvar(self, nome_item, categoria, quantidade_str,
                          unidade_medida, minimo_str, id_item=None, preco_custo_str="0"):
        # Camada 2 (segurança real): revalida a permissão antes de executar,
        # mesmo que a tela já tenha tentado esconder o botão.
        if not self._pode_editar():
            return False, MSG_SEM_PERMISSAO

        if not nome_item.strip():
            return False, "O nome do item é obrigatório."

        try:
            quantidade = float(quantidade_str.replace(",", "."))
            if quantidade < 0:
                return False, "A quantidade não pode ser negativa."
        except ValueError:
            return False, "Quantidade inválida. Use apenas números."

        try:
            minimo = float(minimo_str.replace(",", "."))
            if minimo < 0:
                return False, "A quantidade mínima não pode ser negativa."
        except ValueError:
            return False, "Quantidade mínima inválida. Use apenas números."

        try:
            preco_custo = float(str(preco_custo_str).replace(",", ".")) if preco_custo_str else 0.0
            if preco_custo < 0:
                return False, "O preço de custo não pode ser negativo."
        except ValueError:
            return False, "Preço de custo inválido. Use apenas números."

        try:
            self.model.salvar(
                nome_item.strip(), categoria, quantidade,
                unidade_medida, minimo, id_item, preco_custo
            )
            self.auditoria.registrar(
                self.usuario_logado,
                acao="editou" if id_item else "criou",
                modulo="estoque",
                detalhe=f"Item '{nome_item.strip()}' (qtd: {quantidade} {unidade_medida})",
            )
            return True, "Item salvo com sucesso!"
        except Exception as e:
            return False, f"Erro no banco de dados: {str(e)}"

    def excluir(self, id_item):
        if not self._pode_editar():
            return False, MSG_SEM_PERMISSAO

        try:
            self.model.excluir(id_item)
            self.auditoria.registrar(
                self.usuario_logado,
                acao="excluiu",
                modulo="estoque",
                detalhe=f"Item id={id_item} removido do estoque",
            )
            return True, "Item excluído com sucesso!"
        except Exception as e:
            return False, f"Erro ao excluir: {str(e)}"

    def registrar_movimentacao(self, id_item, tipo, quantidade_str, observacao=""):
        if not self._pode_editar():
            return False, MSG_SEM_PERMISSAO

        try:
            quantidade = float(quantidade_str.replace(",", "."))
            if quantidade <= 0:
                return False, "A quantidade deve ser maior que zero."
        except ValueError:
            return False, "Quantidade inválida."

        try:
            self.model.registrar_movimentacao(id_item, tipo, quantidade, observacao)
            self.auditoria.registrar(
                self.usuario_logado,
                acao="editou",
                modulo="estoque",
                detalhe=f"Movimentação '{tipo}' de {quantidade} no item id={id_item}",
            )
            return True, f"{tipo} registrada com sucesso!"
        except Exception as e:
            return False, f"Erro ao registrar movimentação: {str(e)}"

    def buscar_historico(self, id_item):
        return self.model.buscar_movimentacoes(id_item)

    def contar_alertas(self):
        return self.model.contar_itens_abaixo_minimo()
