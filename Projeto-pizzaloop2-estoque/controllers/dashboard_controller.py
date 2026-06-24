from models.dashboard_model import DashboardModel


class DashboardController:

    def __init__(self, conexao_banco):
        self.model_dashboard = DashboardModel(conexao_banco)

    def pegar_dados_resumo(self):
        total_clientes, total_pedidos, faturamento_total, pedidos_hoje, ticket_medio = \
            self.model_dashboard.obter_estatisticas()
        return {
            "clientes":     str(total_clientes),
            "pedidos":      str(total_pedidos),
            "faturamento":  self._formatar_moeda(faturamento_total),
            "pedidos_hoje": str(pedidos_hoje),
            "ticket_medio": self._formatar_moeda(ticket_medio),
        }

    def pegar_ultimas_visitas(self, limite=8):
        return self.model_dashboard.obter_ultimos_pedidos(limite)

    def pegar_vendas_semana(self):
        return self.model_dashboard.obter_vendas_semana()

    def buscar_pedidos_em_aberto_por_status(self):
        """Retorna dicionário {status: [lista de pedidos]} para o painel de tempo real."""
        return self.model_dashboard.obter_pedidos_abertos_por_status()

    def _formatar_moeda(self, valor_numerico):
        return (
            f"R$ {float(valor_numerico):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
