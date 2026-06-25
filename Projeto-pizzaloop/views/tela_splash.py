import os
import customtkinter as ctk
from PIL import Image


class TelaSplash(ctk.CTkToplevel):
    """
    View da tela de splash exibida na inicialização do sistema.
    Responsabilidade: apenas apresentar a animação/logo por N milissegundos,
    depois invocar o callback de conclusão fornecido pelo Controller.
    """

    # Duração padrão da splash em milissegundos
    DURACAO_MS: int = 3000

    def __init__(self, master, callback_conclusao: callable, duracao_ms: int = DURACAO_MS):
        """
        Parâmetros
        ----------
        master            : janela raiz (Tk / CTk) criada no main
        callback_conclusao: função chamada pelo Controller quando a splash termina
        duracao_ms        : tempo de exibição em milissegundos (padrão 3 000)
        """
        super().__init__(master)

        self._callback_conclusao = callback_conclusao
        self._duracao_ms = duracao_ms

        self._configurar_janela()
        self._construir_widgets()

        # Agenda o fechamento automático
        self.after(self._duracao_ms, self._encerrar)

    # ── Configuração da janela ────────────────────────────────────────────────

    def _configurar_janela(self) -> None:
        self.title("")
        self.resizable(False, False)
        self.overrideredirect(True)          # sem barra de título
        self.attributes("-topmost", True)    # fica acima de outras janelas

        largura, altura = 420, 340
        larg_tela = self.winfo_screenwidth()
        alt_tela  = self.winfo_screenheight()
        x = (larg_tela - largura) // 2
        y = (alt_tela  - altura)  // 2
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        self.configure(fg_color="#FFFFFF")

    # ── Construção dos widgets ────────────────────────────────────────────────

    def _construir_widgets(self) -> None:
        # Container central
        container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        container.pack(expand=True, fill="both")

        # ── Logo ──────────────────────────────────────────────────────────────
        pasta_views  = os.path.dirname(os.path.abspath(__file__))
        caminho_logo = os.path.join(pasta_views, "..", "assets", "logo_pizzaloop.png")

        try:
            imagem_crua = Image.open(caminho_logo)
            imagem_logo = ctk.CTkImage(
                light_image=imagem_crua,
                dark_image=imagem_crua,
                size=(160, 160),
            )
            ctk.CTkLabel(container, image=imagem_logo, text="").pack(pady=(40, 8))

        except Exception:
            ctk.CTkLabel(
                container,
                text="🍕",
                font=("Arial", 56),
                text_color="#C0392B",
            ).pack(pady=(40, 8))

        # ── Textos ────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            container,
            text="PizzaLoop",
            font=("Arial", 28, "bold"),
            text_color="#C0392B",
        ).pack()

        ctk.CTkLabel(
            container,
            text="Gestão de Pizzaria",
            font=("Arial", 14),
            text_color="#6B5E5A",
        ).pack(pady=(2, 20))

        # ── Barra de progresso ────────────────────────────────────────────────
        self._barra = ctk.CTkProgressBar(
            container,
            width=260,
            height=6,
            corner_radius=4,
            fg_color="#F0E8E5",
            progress_color="#C0392B",
        )
        self._barra.set(0)
        self._barra.pack(pady=(0, 8))

        self._lbl_status = ctk.CTkLabel(
            container,
            text="Carregando...",
            font=("Arial", 11),
            text_color="#B0A09C",
        )
        self._lbl_status.pack()

        # Inicia a animação da barra
        self._animar_barra(0)

    # ── Animação ──────────────────────────────────────────────────────────────

    def _animar_barra(self, passo: int) -> None:
        """Incrementa a barra de progresso ao longo de DURACAO_MS."""
        total_passos = self._duracao_ms // 30   # atualiza a cada ~30 ms
        progresso    = min(passo / total_passos, 1.0)

        self._barra.set(progresso)

        if progresso >= 1.0:
            self._lbl_status.configure(text="Pronto!")
        elif progresso > 0.6:
            self._lbl_status.configure(text="Quase lá...")
        else:
            self._lbl_status.configure(text="Carregando...")

        if passo < total_passos:
            self.after(30, lambda: self._animar_barra(passo + 1))

    # ── Encerramento ──────────────────────────────────────────────────────────

    def _encerrar(self) -> None:
        """Destrói a splash e entrega o controle ao Controller via callback."""
        self.destroy()
        self._callback_conclusao()