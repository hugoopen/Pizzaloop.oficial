from models.entrega_model import EntregaModel


class EntregaController:

    def __init__(self, conexao_banco):
        self.model = EntregaModel(conexao_banco)

    def obter_estatisticas(self):
        return self.model.obter_estatisticas()

    def listar(self):
        return self.model.listar_entregas()

    def listar_pedidos_disponiveis(self):
        return self.model.listar_pedidos_sem_entrega()

    def salvar(self, id_pedido, nome_entregador, telefone_entregador,
               veiculo, endereco_entrega, tempo_estimado, status_entrega,
               id_entrega=None):
        self.model.salvar(id_pedido, nome_entregador, telefone_entregador,
                          veiculo, endereco_entrega, tempo_estimado,
                          status_entrega, id_entrega)

    def excluir(self, id_entrega):
        self.model.excluir(id_entrega)
