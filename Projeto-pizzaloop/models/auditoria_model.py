class AuditoriaModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def registrar(self, usuario_email, usuario_nome, usuario_cargo, acao, modulo, detalhe=""):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                """INSERT INTO auditoria
                       (usuario_email, usuario_nome, usuario_cargo, acao, modulo, detalhe)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (usuario_email, usuario_nome, usuario_cargo, acao, modulo, detalhe)
            )
            self.conexao.commit()
        except Exception:
            # Auditoria nunca deve travar a ação principal do usuário.
            self.conexao.rollback()
        finally:
            cursor.close()

    def buscar_todos(self, limite=200):
        cursor = self.conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM auditoria ORDER BY data_hora DESC LIMIT %s",
                (limite,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
