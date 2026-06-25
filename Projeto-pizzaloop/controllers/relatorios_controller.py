from models.relatorio_model import RelatorioModel


class RelatoriosController:

    def __init__(self, conexao_banco):
        self.model = RelatorioModel(conexao_banco)

    def resumo(self, periodo: str):
        return self.model.obter_resumo(periodo)

    def resumo_pagamentos(self, periodo: str):
        return self.model.obter_resumo_pagamentos(periodo)

    def lucro(self, periodo: str):
        return self.model.obter_lucro(periodo)

    def lucro_por_produto(self, periodo: str):
        return self.model.obter_lucro_por_produto(periodo)

    def vendas_por_dia(self, periodo: str):
        return self.model.obter_vendas_por_dia(periodo)

    def performance_produtos(self, periodo: str):
        return self.model.obter_performance_produtos(periodo)

    def horarios_movimento(self, periodo: str):
        return self.model.obter_horarios_movimento(periodo)

    def metodos_pagamento(self, periodo: str):
        return self.model.obter_metodos_pagamento(periodo)

    def resumo_estoque(self):
        return self.model.obter_resumo_estoque()

    def itens_criticos_estoque(self):
        return self.model.obter_itens_criticos_estoque()

    def movimentacoes_estoque(self, periodo: str):
        return self.model.obter_movimentacoes_estoque(periodo)

    def consumo_por_produto(self, periodo: str):
        return self.model.obter_consumo_por_produto(periodo)
