from models.auditoria_model import AuditoriaModel


class AuditoriaController:

    def __init__(self, conexao_banco):
        self.model = AuditoriaModel(conexao_banco)

    def registrar(self, usuario_logado, acao, modulo, detalhe=""):
        """Grava uma linha no log de auditoria.

        usuario_logado: dict com 'email', 'nome' e 'cargo' (vem da sessão,
        carregado no login). Se vier None, grava como 'desconhecido' em vez
        de quebrar a ação principal.
        """
        if usuario_logado is None:
            email, nome, cargo = "desconhecido", "Desconhecido", "desconhecido"
        elif isinstance(usuario_logado, dict):
            email = usuario_logado.get("email", "desconhecido")
            nome = usuario_logado.get("nome", "Desconhecido")
            cargo = usuario_logado.get("cargo", "desconhecido")
        else:
            email = getattr(usuario_logado, "email", "desconhecido")
            nome = getattr(usuario_logado, "nome", "Desconhecido")
            cargo = getattr(usuario_logado, "cargo", "desconhecido")

        self.model.registrar(email, nome, cargo, acao, modulo, detalhe)

    def listar_historico(self, limite=200):
        return self.model.buscar_todos(limite)
