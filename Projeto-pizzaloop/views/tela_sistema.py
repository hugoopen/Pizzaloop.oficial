import os
from PIL import Image
import customtkinter as ctk
from utils.fullscreen import configurar_fullscreen  # Importa o utilitário adicionado
from services import permissao_service


class TelaSistema(ctk.CTk):

    def __init__(self, paleta_cores, callback_navegacao, callback_tema,
                 usuario_logado=None, callback_logout=None):
        super().__init__()

        self.title("PizzaLoop — Gestão de Pizzaria")
        
        # ── INTEGRAÇÃO DO ESC E F11 CORRIGIDOS ──────────────────────────
        configurar_fullscreen(self)

        self.paleta_cores = paleta_cores
        self.callback_navegacao = callback_navegacao
        self.callback_tema = callback_tema
        self.usuario_logado = usuario_logado
        self.callback_logout = callback_logout
        self.tela_ativa = "dashboard"

        COR_SIDEBAR     = paleta_cores["sidebar"]
        COR_BORDA_SIDE  = paleta_cores["borda"]
        COR_TEXTO_MENU  = paleta_cores["texto_sub"]
        COR_ATIVA_FUNDO = paleta_cores["ativa_fundo"]
        COR_PRIMARIA    = paleta_cores["primaria"]

        # ── SIDEBAR ────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=COR_SIDEBAR,
            border_width=1,
            border_color=COR_BORDA_SIDE
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # ── LOGO ───────────────────────────────────────────────────────
        frame_logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_logo.pack(fill="x", padx=20, pady=(20, 4))

        pasta_views = os.path.dirname(os.path.abspath(__file__))
        caminho_logo = os.path.join(pasta_views, "..", "assets", "logo_pizzaloop.png")

        try:
            imagem_crua = Image.open(caminho_logo)
            imagem_logo = ctk.CTkImage(
                light_image=imagem_crua,
                dark_image=imagem_crua,
                size=(150, 150)
            )
            lbl_logo = ctk.CTkLabel(frame_logo, image=imagem_logo, text="")
            lbl_logo.pack(anchor="center", pady=(10, 0))

        except Exception:
            coluna_logo = ctk.CTkFrame(frame_logo, fg_color="transparent")
            coluna_logo.pack(side="left", padx=(10, 0))
            ctk.CTkLabel(frame_logo, text="🍕", font=("Arial", 28), text_color=COR_PRIMARIA).pack(side="left")
            ctk.CTkLabel(coluna_logo, text="PizzaLoop", font=("Arial", 17, "bold"), text_color=COR_PRIMARIA).pack(anchor="w")
            ctk.CTkLabel(coluna_logo, text="Gestão de Pizzaria", font=("Arial", 10), text_color=COR_TEXTO_MENU).pack(anchor="w")

        # Divisória
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COR_BORDA_SIDE).pack(
            fill="x", padx=16, pady=(16, 14)
        )

        # Label "MENU"
        ctk.CTkLabel(
            self.sidebar,
            text="MENU",
            font=("Arial", 10, "bold"),
            text_color="#B0A09C"
        ).pack(anchor="w", padx=24, pady=(0, 8))

        # ── ITENS DE NAVEGAÇÃO ─────────────────────────────────────────
        itens_menu_completo = [
            ("📊", "Dashboard",    "dashboard"),
            ("🛒", "Pedidos",      "pedidos"),
            ("👥", "Clientes",     "clientes"),
            ("🍕", "Produtos",     "produtos"),
            ("🛵", "Entregadores", "entregadores"),
            ("📈", "Relatórios",   "relatorios"),
            ("📦", "Estoque",       "estoque"),
        ]

        # Camada 1 (UX): só mostra no menu o que o cargo do usuário pode ver.
        # "dashboard" fica sempre visível; os demais passam pela permissão.
        self.itens_menu = [
            item for item in itens_menu_completo
            if item[2] == "dashboard" or permissao_service.pode_ver(self.usuario_logado, item[2])
        ]

        # Itens exclusivos do admin
        if permissao_service.eh_admin(self.usuario_logado):
            self.itens_menu.append(("🔐", "Funcionários", "funcionarios"))
            self.itens_menu.append(("🕒", "Auditoria", "auditoria"))

        self.botoes_nav = {}

        for emoji, rotulo, destino in self.itens_menu:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {emoji}  {rotulo}",
                anchor="w",
                fg_color="transparent",
                text_color=COR_TEXTO_MENU,
                hover_color=COR_ATIVA_FUNDO,
                corner_radius=10,
                height=44,
                font=("Arial", 13),
                border_width=0,
                command=lambda d=destino: callback_navegacao(d)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.botoes_nav[destino] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(expand=True, fill="both")

        # Divisória antes do rodapé
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COR_BORDA_SIDE).pack(
            fill="x", padx=16, pady=(0, 14)
        )

        # Botão Novo Pedido (só aparece para quem tem acesso a Pedidos)
        if permissao_service.pode_ver(self.usuario_logado, "pedidos"):
            ctk.CTkButton(
                self.sidebar,
                text="+ Novo Pedido",
                fg_color=COR_PRIMARIA,
                text_color="#FFFFFF",
                hover_color="#A93226",
                corner_radius=10,
                height=40,
                font=("Arial", 12, "bold"),
                border_width=0,
                command=lambda: callback_navegacao("pedidos")
            ).pack(fill="x", padx=16, pady=(0, 12))

        # Avatar / usuário
        self.frame_user = ctk.CTkFrame(self.sidebar, fg_color=COR_ATIVA_FUNDO, corner_radius=10)
        self.frame_user.pack(fill="x", padx=16, pady=(0, 20))

        ctk.CTkLabel(
            self.frame_user,
            text="👤",
            font=("Arial", 22)
        ).pack(side="left", padx=(12, 8), pady=10)

        col_user = ctk.CTkFrame(self.frame_user, fg_color="transparent")
        col_user.pack(side="left", pady=10)

        nome_usuario = "Usuário"
        cargo_usuario = ""
        if self.usuario_logado:
            if isinstance(self.usuario_logado, dict):
                nome_usuario = self.usuario_logado.get("nome") or self.usuario_logado.get("email", "Usuário")
                cargo_usuario = self.usuario_logado.get("cargo", "")
            else:
                nome_usuario = getattr(self.usuario_logado, "nome", "Usuário")
                cargo_usuario = getattr(self.usuario_logado, "cargo", "")

        ctk.CTkLabel(
            col_user,
            text=nome_usuario,
            font=("Arial", 11, "bold"),
            text_color=paleta_cores["texto"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            col_user,
            text=cargo_usuario.capitalize() if cargo_usuario else "Logado",
            font=("Arial", 10),
            text_color=paleta_cores["texto_sub"]
        ).pack(anchor="w")

        # Botão Sair (logout real: volta para a tela de login, importante
        # já que vários cargos usam o mesmo computador)
        ctk.CTkButton(
            self.sidebar,
            text="→  Sair",
            anchor="w",
            fg_color="transparent",
            text_color="#B0A09C",
            hover_color=COR_ATIVA_FUNDO,
            corner_radius=8,
            height=36,
            font=("Arial", 12),
            border_width=0,
            command=self._sair
        ).pack(fill="x", padx=12, pady=(0, 4))

        # Botão Tema (Modificado para chamar o alternador interno seguro)
        icone = "☀️" if ctk.get_appearance_mode().lower() == "dark" else "🌙"
        self.btn_tema = ctk.CTkButton(
            self.sidebar,
            text=f"  {icone}  Tema",
            anchor="w",
            fg_color="transparent",
            text_color="#B0A09C",
            hover_color=COR_ATIVA_FUNDO,
            corner_radius=8,
            height=36,
            font=("Arial", 12),
            border_width=0,
            command=self._alternar_tema_seguro
        )
        self.btn_tema.pack(fill="x", padx=12, pady=(0, 8))

        # ── ÁREA DE CONTEÚDO PRINCIPAL ─────────────────────────────────
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.paleta_cores["fundo"],
            corner_radius=0
        )
        self.main_frame.pack(side="left", fill="both", expand=True)

    # ── LOGOUT ──────────────────────────────────────────────────────────
    def _sair(self):
        """Fecha a sessão atual e volta para a tela de login, em vez de
        fechar o programa inteiro — importante porque vários cargos usam
        o mesmo computador, em turnos diferentes."""
        if self.callback_logout:
            self.callback_logout()
        else:
            self.quit()

    # ── FUNÇÃO INTERNA PARA CORREÇÃO DO TEMA ──────────────────────────
    def _alternar_tema_seguro(self):
        """Alterna a janela entre Light e Dark e força a atualização de cores"""
        if ctk.get_appearance_mode().lower() == "dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
            
        # Executa o callback externo (que troca o dicionário de cores no main.py)
        if self.callback_tema:
            self.callback_tema()

    def atualizar_sidebar_ativa(self, nome_tela):
        self.tela_ativa = nome_tela
        p = self.paleta_cores

        for destino, btn in self.botoes_nav.items():
            if destino == nome_tela:
                btn.configure(
                    fg_color=p["ativa_fundo"],
                    text_color=p["ativa_texto"],
                    font=("Arial", 13, "bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=p["texto_sub"],
                    font=("Arial", 13)
                )

    def aplicar_tema(self, p):
        """Esta função recebe as novas cores vindas do controller/main e atualiza a UI"""
        self.paleta_cores = p

        # Redesenha os elementos principais com os novos tons
        self.configure(fg_color=p["fundo"])
        self.sidebar.configure(fg_color=p["sidebar"], border_color=p["borda"])
        self.main_frame.configure(fg_color=p["fundo"])
        self.frame_user.configure(fg_color=p["ativa_fundo"])

        # Atualiza dinamicamente o emoji do botão
        icone = "☀️" if ctk.get_appearance_mode().lower() == "dark" else "🌙"
        self.btn_tema.configure(
            text=f"  {icone}  Tema",
            text_color=p["texto_sub"],
            hover_color=p["ativa_fundo"]
        )

        self.atualizar_sidebar_ativa(self.tela_ativa)