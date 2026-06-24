# controllers/sistema_controller.py

import customtkinter as ctk

from utils.fullscreen         import configurar_fullscreen
from banco.connect            import connect_to_database
from views.tela_sistema       import TelaSistema
from views.tela_splash        import TelaSplash          # ← novo import
from views.tela_login         import renderizar_login
from views.tela_dashboard     import renderizar_dashboard
from views.tela_produtos      import renderizar_produtos
from views.tela_clientes      import renderizar_clientes
from views.tela_pedidos       import renderizar_pedidos
from views.tela_relatorios    import renderizar_relatorios
from views.tela_entregadores  import renderizar_entregadores
from views.tela_estoque       import renderizar_estoque
from views.tela_funcionarios  import renderizar_funcionarios
from views.tela_auditoria     import renderizar_auditoria
from services                 import permissao_service
from tkinter import messagebox


class SistemaController:

    def __init__(self):
        ctk.set_appearance_mode("light")

    def __init__(self):
        ctk.set_appearance_mode("light")

        self.paleta_cores = {
            "fundo":       "#FAF5F3",
            "sidebar":     "#FFFFFF",
            "primaria":    "#C0392B",
            "ativa":       "#F59E0B",
            "ativa_fundo": "#FEF3C7",
            "ativa_texto": "#FF6B00",  # ← ADICIONADO: Escolha a cor desejada para o texto ativo (ex: Laranja)
            "card":        "#FFFFFF",
            "borda":       "#E8DDD9",
            "texto":       "#1C1917",
            "texto_sub":   "#78716C",
            "botao":       "#FF6B00",
            "editar":      "#4CAF50",
            "excluir":     "#F44336",
            "texto_claro": "#FFFFFF",
        }

        self.conexao_banco = connect_to_database()
        self.janela_principal = None
        self.usuario_logado = None


    # ── 1. Ponto de entrada ───────────────────────────────────────────────────

    def iniciar(self):
        """main.py chama apenas este método."""

        # Janela raiz invisível: dona do CTkToplevel da splash
        self._root = ctk.CTk()
        self._root.withdraw()

        TelaSplash(
            master=self._root,
            callback_conclusao=self._apos_splash,
            duracao_ms=3000,            # ajuste o tempo aqui se quiser
        )

        self._root.mainloop()

    # ── 2. Após splash → abre login ───────────────────────────────────────────

    def _apos_splash(self):
        """Chamado automaticamente pela TelaSplash ao se encerrar."""
        self._root.destroy()            # encerra o loop da splash
        self._abrir_login()

    def _abrir_login(self):
        """Abre a tela de login. Reaproveitada tanto na primeira abertura
        quanto no logout (troca de usuário na mesma máquina)."""
        self.usuario_logado = None
        self.janela_login = ctk.CTk()
        configurar_fullscreen(self.janela_login)
        self.janela_login.title("PizzaLoop — Login")
        self.janela_login.geometry("1200x700")
        self.janela_login.conn = self.conexao_banco
        renderizar_login(self.janela_login, self.iniciar_interface_principal)
        self.janela_login.mainloop()

    # ── 3. Após login → abre sistema ──────────────────────────────────────────

    def iniciar_interface_principal(self, usuario_logado=None):
        if hasattr(self, "janela_login"):
            self.janela_login.destroy()

        self.usuario_logado = usuario_logado

        # CORREÇÃO: Adicionado o terceiro argumento 'self.alternar_tema' para corrigir o TypeError
        self.janela_principal = TelaSistema(
            self.paleta_cores, self.mudar_tela, self.alternar_tema,
            usuario_logado=self.usuario_logado, callback_logout=self.logout,
        )
        self.janela_principal.conn = self.conexao_banco
        self.janela_principal.usuario_logado = self.usuario_logado

        # Força a janela aparecer antes de aplicar fullscreen
        self.janela_principal.deiconify()
        self.janela_principal.focus_force()
        self.janela_principal.update()

        # Agora aplica fullscreen com a janela já visível e com foco
        self.janela_principal.attributes("-fullscreen", True)
        configurar_fullscreen(self.janela_principal)
        self.janela_principal.update_idletasks()

        self.mudar_tela("dashboard")
        self.janela_principal.mainloop()

    # ── 3b. Logout → volta para a tela de login ───────────────────────────────

    def logout(self):
        if self.janela_principal:
            self.janela_principal.destroy()
            self.janela_principal = None
        self._abrir_login()

    # ── 4. Navegação entre telas ──────────────────────────────────────────────

    def mudar_tela(self, nome_tela_destino):
        # Camada de segurança: revalida a permissão antes de renderizar
        # qualquer tela, mesmo que o botão da sidebar não devesse existir.
        if nome_tela_destino != "dashboard" and not permissao_service.pode_ver(self.usuario_logado, nome_tela_destino):
            messagebox.showerror(
                "Acesso não autorizado",
                "Você não tem permissão para acessar esta área do sistema."
            )
            return

        self.janela_principal.atualizar_sidebar_ativa(nome_tela_destino)

        for widget in self.janela_principal.main_frame.winfo_children():
            widget.destroy()

        mapa_telas = {
            "dashboard":    renderizar_dashboard,
            "pedidos":      renderizar_pedidos,
            "clientes":     renderizar_clientes,
            "produtos":     renderizar_produtos,
            "entregadores": renderizar_entregadores,
            "relatorios":   renderizar_relatorios,
            "estoque":      renderizar_estoque,
            "funcionarios": renderizar_funcionarios,
            "auditoria":    renderizar_auditoria,
        }

        if nome_tela_destino in mapa_telas:
            mapa_telas[nome_tela_destino](
                self.janela_principal.main_frame,
                self.janela_principal,
                self.paleta_cores,
            )

    # ── 5. Controle de Aparência / Tema ───────────────────────────────────────

    def alternar_tema(self):
        """Muda o tema do CustomTkinter entre Light (Claro) e Dark (Escuro)"""
        tema_atual = ctk.get_appearance_mode()
        if tema_atual == "Light":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
