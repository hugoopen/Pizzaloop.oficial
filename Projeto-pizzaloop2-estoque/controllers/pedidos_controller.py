from models.pedido_model import PedidoModel


class PedidoController:

    def __init__(self, conexao_banco):
        self.model_pedido = PedidoModel(conexao_banco)
        self.conexao = conexao_banco

    def buscar_dados_auxiliares(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT id_cliente, nome FROM cliente")
        dicionario_clientes = {nome: id_cli for id_cli, nome in cursor.fetchall()}
        cursor.execute("SELECT id_produto, nome_produto, preco FROM produtos")
        dicionario_produtos = {nome: (id_prod, preco) for id_prod, nome, preco in cursor.fetchall()}
        cursor.close()
        return dicionario_clientes, dicionario_produtos

    def buscar_entregadores_ativos_para_selecao(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute(
                "SELECT id_entregador, nome FROM entregadores WHERE ativo = 1 ORDER BY nome ASC"
            )
            rows = cursor.fetchall()
            cursor.close()
            return {nome: id_ent for id_ent, nome in rows}
        except Exception:
            return {}

    def listar(self):
        return self.model_pedido.listar_pedidos_completos()

    def salvar(self, id_cliente, id_produto, quantidade, preco_unitario,
               status_pedido, metodo_pagamento, id_entregador=None, id_pedido=None,
               tempo_preparo="20 min", pago=0):
        self.model_pedido.salvar_pedido_completo(
            id_cliente, id_produto, quantidade, preco_unitario,
            status_pedido, metodo_pagamento, id_entregador, id_pedido,
            tempo_preparo, pago
        )
        return True

    def alternar_pago(self, id_pedido, pago):
        self.model_pedido.alternar_pago(id_pedido, pago)

    def excluir(self, id_pedido):
        self.model_pedido.excluir(id_pedido)
