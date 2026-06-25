from models.cliente_model import ClienteModel


class ClienteController:

    def __init__(self, conexao_banco):
        self.model_cliente = ClienteModel(conexao_banco)

    def listar_clientes(self):
        """Lista simples (sem estatísticas) — mantido por compatibilidade."""
        return self.model_cliente.buscar_todos()

    def listar_clientes_com_estatisticas(self):
        """Lista com total_pedidos, total_gasto e ultimo_pedido por cliente."""
        return self.model_cliente.buscar_todos_com_estatisticas()

    def validar_e_salvar(self, nome_cliente, telefone_com_mascara, cpf_com_mascara,
                          email="",
                          cep="", endereco="", numero="", bairro="", cidade="",
                          id_cliente=None):
        telefone_limpo = ''.join(filter(str.isdigit, telefone_com_mascara))
        cpf_limpo = ''.join(filter(str.isdigit, cpf_com_mascara))

        if not nome_cliente.strip():
            return False, "Nome é obrigatório."

        if len(cpf_limpo) != 11:
            return False, "CPF deve ter 11 dígitos."

        try:
            self.model_cliente.salvar_dados(
                nome_cliente.strip(), telefone_limpo, cpf_limpo,
                email.strip(),
                cep.strip(), endereco.strip(), numero.strip(),
                bairro.strip(), cidade.strip(),
                id_cliente
            )
            return True, "Cliente salvo com sucesso!"
        except Exception as erro:
            return False, f"Erro no banco de dados: {str(erro)}"

    def excluir(self, id_cliente):
        self.model_cliente.excluir(id_cliente)
