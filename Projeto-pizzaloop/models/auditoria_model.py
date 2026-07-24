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

    def buscar_todos(self, limite=200, cargos= None):
        cursor = self.conexao.cursor(dictionary=True)
        try:
           query = "SELECT * FROM auditoria"
           params = []

           if cargos:
               placeholders = ", ".join(["%s"] * len(cargos))
               query += f"WHERE usuario_cargo IN ({placeholders})"
               params.extend(cargos)
            
           query += "ORDER BY data_hora DESC LIMIT %s"
           params.append(cargos)

           cursor.execute(query, params)
           return cursor.fetchal()
        finally:
            cursor.close()