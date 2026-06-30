# ========================================================
# CONTROLLER DE LOGIN - PIZZALOOP (VERSÃO ATUALIZADA)
# Integrado com: bcrypt (Apenas Admin), Texto Limpo (Funcionários),
# validação de email, MAX_TENTATIVAS e proteção contra timing attacks.
# ========================================================
import time
import re
import bcrypt
from typing import Tuple
from models.login_model import LoginModel


class LoginController:

    MAX_TENTATIVAS = 5
    _tentativas: dict = {}

    # Hash dummy válido para evitar ataques de temporização
    _DUMMY_HASH = b"$2b$12$k9Od1HYqzhRbGdR..ZWwBumuCh34zhDe6UMUXnmWxzDEqwUV6OCbW"

    def __init__(self, conexao_banco):
        self.model_login = LoginModel(conexao_banco)

    def _validar_email(self, email: str) -> bool:
        padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(padrao, email))

    def _validar_forca_senha(self, senha: str) -> Tuple[bool, str]:
        if len(senha) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres."
        if not any(c.isdigit() for c in senha):
            return False, "A senha deve conter ao menos um número."
        if not any(c.isalpha() for c in senha):
            return False, "A senha deve conter ao menos uma letra."
        return True, ""

    def autenticar(self, email_digitado: str, senha_digitada: str):
        """Retorna (sucesso: bool, mensagem: str, usuario_logado: dict|None).

        usuario_logado contém {'email', 'nome', 'cargo'} e é o que alimenta
        a sessão usada pela sidebar e pelos controllers para checar permissão.
        """
        if not email_digitado or not senha_digitada:
            return False, "Preencha todos os campos!", None

        email = email_digitado.strip().lower()

        # Verifica limite de tentativas de login
        tentativas_feitas = self._tentativas.get(email, 0)
        if tentativas_feitas >= self.MAX_TENTATIVAS:
            return False, (
                f"Conta bloqueada após {self.MAX_TENTATIVAS} tentativas.\n"
                "Reinicie o sistema ou fale com o administrador."
            ), None

        # Busca os dados do usuário na Model
        dados_usuario = self.model_login.buscar_usuario_completo(email)

        if dados_usuario:
            senha_hash_banco = dados_usuario["senha"]
            # Normaliza o cargo para evitar problemas com maiúsculas/minúsculas
            cargo = str(dados_usuario.get("cargo", "funcionario")).strip().lower()
            usuario_existe = True
        else:
            senha_hash_banco = self._DUMMY_HASH
            cargo = "funcionario"
            usuario_existe = False

        # ========================================================
        # LÓGICA DE VALIDAÇÃO MISTA (ADMIN vs FUNCIONÁRIO)
        # ========================================================
        try:
            if ( not usuario_existe) or (usuario_existe and cargo == "admin"):
                # Se for administrador, valida usando bcrypt
                hash_para_verificar = (
                    senha_hash_banco.encode("utf-8")
                    if isinstance(senha_hash_banco, str)
                    else senha_hash_banco
                )
                senha_correta = bcrypt.checkpw(
                    senha_digitada.encode("utf-8"),
                    hash_para_verificar
                )
            else:
                # Se for funcionário (ou usuário inexistente), compara o texto limpo direto
                senha_correta = (senha_hash_banco == senha_digitada)

        except Exception as e:
            # Se der erro de tipo ou formato no bcrypt, cai aqui.
            # print(f"DEBUG Erro Interno: {e}") # Descomente se precisar debugar no terminal
            return False, "Erro interno ao verificar a senha.", None

        # Verificação do resultado da autenticação
        if not (usuario_existe and senha_correta):
            time.sleep(2.0)
            self._tentativas[email] = tentativas_feitas + 1
            tentativas_restantes = self.MAX_TENTATIVAS - self._tentativas[email]

            if tentativas_restantes > 0:
                return False, f"E-mail ou senha incorretos.\n({tentativas_restantes} tentativa(s) restante(s))", None
            else:
                return False, (
                    f"Conta bloqueada após {self.MAX_TENTATIVAS} tentativas.\n"
                    "Reinicie o sistema ou fale com o administrador."
                ), None

        # Verifica se a conta está ativa no sistema
        if not dados_usuario.get("ativo", 1):
            return False, "Este usuário está desativado. Fale com o administrador.", None

        # Limpa as tentativas após o sucesso
        self._tentativas.pop(email, None)

        # Monta a sessão do usuário logado
        usuario_logado = {
            "email": dados_usuario["email"],
            "nome": dados_usuario.get("nome") or email,
            "cargo": dados_usuario.get("cargo") or "funcionario",
        }
        return True, "Login realizado!", usuario_logado

    def cadastrar_novo(self, email_novo: str, senha_nova: str, nome_novo: str = "", cargo_novo: str = "funcionario") -> Tuple[bool, str]:
        """Método utilizado para criação de novos usuários (Geralmente via tela de cadastro)."""
        if not email_novo or not senha_nova:
            return False, "Preencha todos os campos!"

        email = email_novo.strip().lower()

        if not self._validar_email(email):
            return False, "Formato de e-mail inválido."

        senha_valida, msg_senha = self._validar_forca_senha(senha_nova)
        if not senha_valida:
            return False, msg_senha

        cargo_formatado = cargo_novo.strip().lower()

        # Só aplica bcrypt se o cargo cadastrado for administrador
        if cargo_formatado == "admin":
            try:
                senha_final = bcrypt.hashpw(
                    senha_nova.encode("utf-8"),
                    bcrypt.gensalt()
                )
            except Exception:
                return False, "Erro interno ao processar a senha de administrador."
        else:
            # Para funcionários, mantém a string limpa em formato de texto
            senha_final = senha_nova

        try:
            self.model_login.criar_usuario(email, senha_final, nome_novo.strip(), cargo_novo)
            return True, "Usuário cadastrado com sucesso!"
        except Exception:
            return False, "Este e-mail já está cadastrado ou o servidor de banco de dados está inacessível."