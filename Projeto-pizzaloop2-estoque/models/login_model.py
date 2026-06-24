# ========================================================
# MODEL DE LOGIN
# Integrado com: rollback, cursor.close() no finally (da pizzaloop)
# Mantendo nomes e estrutura do pizzaloop_replit
# ========================================================

class LoginModel:

    def __init__(self, conexao_banco):
        self.conexao = conexao_banco

    def buscar_usuario(self, email_digitado):
        """Mantido por compatibilidade: retorna só a senha (usado internamente
        pelo fluxo de verificação de senha com hash dummy)."""
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "SELECT senha FROM login WHERE email = %s",
                (email_digitado,)
            )
            resultado = cursor.fetchone()
            return resultado
        finally:
            cursor.close()

    def buscar_usuario_completo(self, email_digitado):
        """Retorna nome, senha (hash), cargo e situação (ativo) do usuário,
        usado para montar a sessão (usuario_logado) após o login."""
        cursor = self.conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT email, nome, senha, cargo, ativo FROM login WHERE email = %s",
                (email_digitado,)
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def criar_usuario(self, email_novo, senha_nova, nome_novo="", cargo_novo="funcionario"):
        # Converte bytes do bcrypt para string para o MySQL
        if isinstance(senha_nova, bytes):
            senha_nova = senha_nova.decode("utf-8")

        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "INSERT INTO login (email, nome, senha, cargo, ativo) VALUES (%s, %s, %s, %s, 1)",
                (email_novo, nome_novo, senha_nova, cargo_novo)
            )
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            raise e
        finally:
            cursor.close()

    def listar_usuarios(self):
        cursor = self.conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT email, nome, cargo, ativo FROM login ORDER BY nome ASC"
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def atualizar_situacao(self, email, ativo):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "UPDATE login SET ativo = %s WHERE email = %s",
                (1 if ativo else 0, email)
            )
            self.conexao.commit()
        finally:
            cursor.close()

    def atualizar_cargo(self, email, novo_cargo):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "UPDATE login SET cargo = %s WHERE email = %s",
                (novo_cargo, email)
            )
            self.conexao.commit()
        finally:
            cursor.close()

    def atualizar_nome(self, email, novo_nome):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "UPDATE login SET nome = %s WHERE email = %s",
                (novo_nome, email)
            )
            self.conexao.commit()
        finally:
            cursor.close()
