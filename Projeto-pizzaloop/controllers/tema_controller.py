# controllers/tema_controller.py

import customtkinter as ctk

from utils.fullscreen import configurar_fullscreen
from banco.connect import connect_to_database
from models.tema_model import TemaModel
from views.tela_sistema       import TelaSistema
from views.tela_login         import renderizar_login
from views.tela_dashboard     import renderizar_dashboard
from views.tela_produtos      import renderizar_produtos
from views.tela_clientes      import renderizar_clientes
from views.tela_pedidos       import renderizar_pedidos
from views.tela_relatorios    import renderizar_relatorios
from views.tela_entregadores  import renderizar_entregadores


class SistemaController:

    def __init__(self):
        self.tema_model = TemaModel()
        ctk.set_appearance_mode(self.tema_model.tema)

        self.paletas = {
            "light": {
                "fundo":       "#FAF5F3",
                "sidebar":     "#FFFFFF",
                "primaria":    "#C0392B",
                "ativa":       "#F59E0B",
                "ativa_fundo": "#FEF3C7",
                "ativa_texto": "#B45309",
                "card":        "#FFFFFF",
                "borda":       "#E8DDD9",
                "texto":       "#1C1917",
                "texto_sub":   "#78716C",
                "botao":       "#FF6B00",
                "editar":      "#4CAF50",
                "excluir":     "#F44336",
                "texto_claro": "#FFFFFF",
            },
            "dark": {
                "fundo":       "#0C0A09",
                "sidebar":     "#1C1917",
                "primaria":    "#C0392B",
                "ativa":       "#F59E0B",
                "ativa_fundo": "#292524",
                "ativa_texto": "#F59E0B",
                "card":        "#1C1917",
                "borda":       "#292524",
                "texto":       "#F5F5F4",
                "texto_sub":   "#A8A29E",
                "botao":       "#FF6B00",
                "editar":      "#4CAF50",
                "excluir":     "#F44336",
                "texto_claro": "#FFFFFF",
            },
        }

        self.paleta_cores = self.paletas[self.tema_model.tema]
        self.conexao_banco = connect_to_database()
        self.janela_principal = None

    def iniciar(self):
        self.janela_login = ctk.CTk()
        configurar_fullscreen(self.janela_login)
        self.janela_login.title("PizzaLoop — Login")
        self.janela_login.geometry("1200x700")
        self.janela_login.conn = self.conexao_banco
        renderizar_login(self.janela_login, self.iniciar_interface_principal)
        self.janela_login.mainloop()

    def iniciar_interface_principal(self):
        if hasattr(self, "janela_login"):
            self.janela_login.destroy()

        self.janela_principal = TelaSistema(
            self.paleta_cores,
            self.mudar_tela,
            self.alternar_tema
        )
        self.janela_principal.conn = self.conexao_banco

        self.janela_principal.geometry("1000x500")
        self.janela_principal.update_idletasks()
        self.janela_principal.state('zoomed')

        configurar_fullscreen(self.janela_principal)
        self.janela_principal.update()

        self.mudar_tela("dashboard")
        self.janela_principal.mainloop()

    def mudar_tela(self, nome_tela_destino):
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
        }

        if nome_tela_destino in mapa_telas:
            mapa_telas[nome_tela_destino](
                self.janela_principal.main_frame,
                self.janela_principal,
                self.paleta_cores
            )

    def alternar_tema(self):
        novo = "dark" if self.tema_model.tema == "light" else "light"
        self.tema_model.salvar(novo)
        ctk.set_appearance_mode(novo)
        self.paleta_cores = self.paletas[novo]
        self.janela_principal.aplicar_tema(self.paleta_cores)
        self.mudar_tela(self.janela_principal.tela_ativa)