# ========================================================
# SERVIÇO DE PERMISSÕES (RBAC)
# Define o que cada cargo pode VER e EDITAR em cada módulo
# do sistema. É a fonte única de verdade das permissões —
# tanto as telas (Camada 1) quanto os controllers
# (Camada 2) consultam este arquivo.
# ========================================================

# Cargos válidos no sistema
CARGOS_VALIDOS = ["admin", "socio", "funcionario", "entregador"]

# "ver"    -> pode visualizar o módulo / menu aparece na sidebar
# "editar" -> pode criar, editar ou excluir registros do módulo
PERMISSOES = {
    "admin": {
        "dashboard":    {"ver": True, "editar": True},
        "pedidos":      {"ver": True, "editar": True},
        "clientes":     {"ver": True, "editar": True},
        "produtos":     {"ver": True, "editar": True},
        "entregadores": {"ver": True, "editar": True},
        "relatorios":   {"ver": True, "editar": True},
        "estoque":      {"ver": True, "editar": True},
        "funcionarios": {"ver": True, "editar": True},
        "auditoria":    {"ver": True, "editar": False},
    },
    "socio": {
        "dashboard":    {"ver": True, "editar": True},
        "pedidos":      {"ver": True, "editar": True},
        "clientes":     {"ver": True, "editar": True},
        "produtos":     {"ver": True, "editar": True},
        "entregadores": {"ver": True, "editar": True},
        "relatorios":   {"ver": True, "editar": True},
        "estoque":      {"ver": True, "editar": True},
        "funcionarios": {"ver": False, "editar": False},
        "auditoria":    {"ver": True, "editar": False},
    },
    "funcionario": {
        "dashboard":    {"ver": True,  "editar": False},
        "pedidos":      {"ver": True,  "editar": True},
        "clientes":     {"ver": True,  "editar": True},
        "produtos":     {"ver": True,  "editar": False},
        "entregadores": {"ver": False, "editar": False},
        "relatorios":   {"ver": False, "editar": False},
        "estoque":      {"ver": False, "editar": False},
        "funcionarios": {"ver": False, "editar": False},
        "auditoria":    {"ver": False, "editar": False},
    },
    "entregador": {
        "dashboard":    {"ver": False, "editar": False},
        "pedidos":      {"ver": False, "editar": False},
        "clientes":     {"ver": False, "editar": False},
        "produtos":     {"ver": False, "editar": False},
        "entregadores": {"ver": True,  "editar": True},
        "relatorios":   {"ver": False, "editar": False},
        "estoque":      {"ver": False, "editar": False},
        "funcionarios": {"ver": False, "editar": False},
        "auditoria":    {"ver": False, "editar": False},
    },
}

# Ordem de exibição dos módulos na sidebar (módulos "internos", sem ícone
# próprio no menu, como o dashboard, são tratados separadamente na view)
MODULOS_MENU = ["pedidos", "clientes", "produtos", "entregadores", "relatorios", "estoque"]


def _cargo_de(usuario_logado):
    """Aceita tanto um dict {'cargo': ...} quanto um objeto com atributo .cargo"""
    if usuario_logado is None:
        return None
    if isinstance(usuario_logado, dict):
        return usuario_logado.get("cargo")
    return getattr(usuario_logado, "cargo", None)


def pode_ver(usuario_logado, modulo):
    cargo = _cargo_de(usuario_logado)
    if cargo not in PERMISSOES:
        return False
    return PERMISSOES[cargo].get(modulo, {}).get("ver", False)


def pode_editar(usuario_logado, modulo):
    cargo = _cargo_de(usuario_logado)
    if cargo not in PERMISSOES:
        return False
    return PERMISSOES[cargo].get(modulo, {}).get("editar", False)


def modulos_visiveis(usuario_logado):
    """Retorna a lista de módulos do menu que o cargo do usuário pode ver,
    preservando a ordem definida em MODULOS_MENU."""
    return [m for m in MODULOS_MENU if pode_ver(usuario_logado, m)]


def eh_admin(usuario_logado):
    return _cargo_de(usuario_logado) == "admin"
