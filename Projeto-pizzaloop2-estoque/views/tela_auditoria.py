# ========================================================
# VIEW: HISTÓRICO DE ALTERAÇÕES (AUDITORIA) — somente Admin
# Mostra quem fez o quê, em qual módulo, e quando.
# ========================================================

import customtkinter as ctk
from controllers.auditoria_controller import AuditoriaController
from services.permissao_service import eh_admin

COR_FUNDO     = "#FAF5F3"
COR_CARD      = "#FFFFFF"
COR_BORDA     = "#E8DDD9"
COR_TEXTO     = "#1C1917"
COR_TEXTO_SUB = "#78716C"
COR_PRIMARIA  = "#C0392B"

CORES_ACAO = {
    "criou":   ("#16A34A", "#DCFCE7"),
    "editou":  ("#2563EB", "#DBEAFE"),
    "excluiu": ("#DC2626", "#FEE2E2"),
}


def renderizar_auditoria(frame_conteudo, janela_raiz, paleta_cores):
    usuario_logado = getattr(janela_raiz, "usuario_logado", None)

    for w in frame_conteudo.winfo_children():
        w.destroy()

    if not eh_admin(usuario_logado):
        ctk.CTkLabel(
            frame_conteudo, text="🔒 Acesso restrito ao administrador.",
            font=("Arial", 16, "bold"), text_color=COR_PRIMARIA
        ).pack(pady=60)
        return

    controlador = AuditoriaController(janela_raiz.conn)

    area = ctk.CTkScrollableFrame(
        frame_conteudo, fg_color=COR_FUNDO,
        scrollbar_button_color=COR_BORDA, corner_radius=0
    )
    area.pack(fill="both", expand=True)

    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(
        barra, text="Histórico de Alterações",
        font=("Arial", 25, "bold"), text_color=COR_TEXTO
    ).pack(side="left")
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(fill="x", padx=28, pady=(4, 14))

    try:
        registros = controlador.listar_historico(limite=200)
    except Exception:
        registros = []

    card_tabela = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
    card_tabela.pack(fill="x", padx=28, pady=(0, 28))

    cab = ctk.CTkFrame(card_tabela, fg_color="#F5F0EE", height=38)
    cab.pack(fill="x")
    cab.pack_propagate(False)

    def _cab(t, w, anc="w"):
        ctk.CTkLabel(cab, text=t, width=w, anchor=anc, font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left", padx=(0, 4))

    ctk.CTkLabel(cab, text="", width=14).pack(side="left")
    _cab("Data/Hora", 150)
    _cab("Usuário", 170)
    _cab("Cargo", 110, "center")
    _cab("Ação", 90, "center")
    _cab("Módulo", 110)
    _cab("Detalhe", 280)

    ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    if not registros:
        ctk.CTkLabel(card_tabela, text="Nenhum registro de auditoria ainda.", text_color=COR_TEXTO_SUB).pack(pady=24)

    for idx, r in enumerate(registros):
        cor_linha = COR_CARD if idx % 2 == 0 else "#FAF5F3"
        linha = ctk.CTkFrame(card_tabela, fg_color=cor_linha, height=42)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        data_hora = r.get("data_hora")
        data_fmt = data_hora.strftime("%d/%m/%Y %H:%M") if data_hora else "—"

        ctk.CTkLabel(linha, text="", width=14).pack(side="left")
        ctk.CTkLabel(linha, text=data_fmt, width=150, anchor="w",
                     font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkLabel(linha, text=r.get("usuario_nome") or r.get("usuario_email", ""), width=170, anchor="w",
                     font=("Arial", 12, "bold"), text_color=COR_TEXTO).pack(side="left")
        ctk.CTkLabel(linha, text=(r.get("usuario_cargo") or "").capitalize(), width=110, anchor="center",
                     font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(side="left")

        cor_txt, cor_bg = CORES_ACAO.get(r.get("acao"), (COR_TEXTO_SUB, "#F1F5F9"))
        celula_acao = ctk.CTkFrame(linha, fg_color="transparent", width=90, height=42)
        celula_acao.pack(side="left")
        celula_acao.pack_propagate(False)
        badge = ctk.CTkFrame(celula_acao, fg_color=cor_bg, corner_radius=8, width=74, height=22)
        badge.place(relx=0.5, rely=0.5, anchor="center")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=(r.get("acao") or "").capitalize(), font=("Arial", 10, "bold"),
                     text_color=cor_txt).pack(expand=True)

        ctk.CTkLabel(linha, text=r.get("modulo", ""), width=110, anchor="w",
                     font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkLabel(linha, text=r.get("detalhe") or "", width=280, anchor="w",
                     font=("Arial", 11), text_color=COR_TEXTO_SUB, wraplength=270).pack(side="left")

        if idx < len(registros) - 1:
            ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")
