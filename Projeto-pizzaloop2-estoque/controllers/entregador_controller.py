from models.entregador_model import EntregadorModel


class EntregadorController:

    def __init__(self, conexao_banco):
        self.model_entregador = EntregadorModel(conexao_banco)

    def listar_todos_entregadores(self):
        return self.model_entregador.buscar_todos_entregadores()

    def listar_entregadores_ativos_para_selecao(self):
        """Retorna dicionário {nome: id_entregador} com entregadores ativos para usar em ComboBox."""
        lista = self.model_entregador.buscar_entregadores_ativos()
        return {e["nome"]: e["id_entregador"] for e in lista}

    def validar_e_salvar_entregador(self, nome_entregador, telefone_com_mascara,
                                     cpf_com_mascara, veiculo_entregador,
                                     placa_veiculo, id_entregador=None):
        telefone_limpo = ''.join(filter(str.isdigit, telefone_com_mascara))
        cpf_limpo = ''.join(filter(str.isdigit, cpf_com_mascara))
        if not nome_entregador.strip():
            return False, "Nome é obrigatório."
        if len(cpf_limpo) != 11:
            return False, "CPF deve ter 11 dígitos."
        try:
            self.model_entregador.salvar_dados_entregador(
                nome_entregador.strip(), telefone_limpo, cpf_limpo,
                veiculo_entregador.strip(), placa_veiculo.strip().upper(),
                id_entregador
            )
            return True, "Entregador salvo com sucesso!"
        except Exception as erro:
            return False, f"Erro no banco de dados: {str(erro)}"

    def alternar_status_entregador(self, id_entregador):
        self.model_entregador.alternar_status_ativo_entregador(id_entregador)

    def excluir_entregador(self, id_entregador):
        self.model_entregador.excluir_entregador(id_entregador)
