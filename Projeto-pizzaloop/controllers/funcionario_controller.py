import re
import bcrypt
from typing import Tuple
from models.login_model import LoginModel
from controllers.auditoria_controller import AuditoriaController
from services.permissao_service import CARGOS_VALIDOS


class FuncionarioController:
    """Usado exclusivamente pela tela de Gerenciar Funcionários (admin).

    Reaproveita a tabela 'login' (mesma do autenticação) e adiciona a
    validação de cargo + registro de auditoria nas alterações.
    """

    def __init__(self, conexao_banco, usuario_logado=None):
        self.model = LoginModel(conexao_banco)
        self.auditoria = AuditoriaController(conexao_banco)
        self.usuario_logado = usuario_logado

    def _validar_email(self, email: str) -> bool:
        padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(padrao, email))

    def listar(self):
        return self.model.listar_usuarios()

    def cadastrar(self, nome: str, email: str, senha: str, cargo: str) -> Tuple[bool, str]:
        nome = nome.strip()
        email = email.strip().lower()

        if not nome or not email or not senha or not cargo:
            return False, "Preencha todos os campos."

        if not self._validar_email(email):
            return False, "Formato de e-mail inválido."

        if cargo not in CARGOS_VALIDOS:
            return False, "Cargo inválido."

        if len(senha) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres."

        try:
            senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
        except Exception:
            return False, "Erro interno ao processar a senha."

        try:
            self.model.criar_usuario(email, senha_hash, nome, cargo)
        except Exception:
            return False, "Este e-mail já está cadastrado ou o banco está inacessível."

        self.auditoria.registrar(
            self.usuario_logado, acao="criou", modulo="funcionarios",
            detalhe=f"Cadastrou '{nome}' ({email}) como {cargo}",
        )
        return True, "Funcionário cadastrado com sucesso!"

    def alterar_cargo(self, email: str, novo_cargo: str) -> Tuple[bool, str]:
        if novo_cargo not in CARGOS_VALIDOS:
            return False, "Cargo inválido."
        try:
            self.model.atualizar_cargo(email, novo_cargo)
        except Exception as e:
            return False, f"Erro ao atualizar cargo: {e}"

        self.auditoria.registrar(
            self.usuario_logado, acao="editou", modulo="funcionarios",
            detalhe=f"Alterou cargo de {email} para {novo_cargo}",
        )
        return True, "Cargo atualizado."

    def alterar_nome(self, email: str, novo_nome: str) -> Tuple[bool, str]:
        novo_nome = novo_nome.strip()
        if not novo_nome:
            return False, "O nome não pode ficar em branco."
        try:
            self.model.atualizar_nome(email, novo_nome)
        except Exception as e:
            return False, f"Erro ao atualizar nome: {e}"

        self.auditoria.registrar(
            self.usuario_logado, acao="editou", modulo="funcionarios",
            detalhe=f"Alterou nome de {email} para '{novo_nome}'",
        )
        return True, "Nome atualizado."

    def alternar_situacao(self, email: str, ativar: bool) -> Tuple[bool, str]:
        if self.usuario_logado and isinstance(self.usuario_logado, dict) and \
           self.usuario_logado.get("email", "").lower() == email.lower() and not ativar:
            return False, "Você não pode desativar a própria conta."

        try:
            self.model.atualizar_situacao(email, ativar)
        except Exception as e:
            return False, f"Erro ao atualizar situação: {e}"

        self.auditoria.registrar(
            self.usuario_logado, acao="editou", modulo="funcionarios",
            detalhe=f"{'Ativou' if ativar else 'Desativou'} a conta de {email}",
        )
        return True, "Situação atualizada."
