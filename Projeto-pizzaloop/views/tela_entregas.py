import customtkinter as ctk
from tkinter import messagebox
from controllers.entrega_controller import EntregaController

COR_FUNDO       = "#FAF5F3"
COR_CARD        = "#FFFFFF"
COR_BORDA       = "#E8DDD9"
COR_HOVER       = "#FEF3C7"
COR_TEXTO       = "#1C1917"
COR_TEXTO_SUB   = "#78716C"
COR_PRIMARIA    = "#C0392B"
COR_PRIM_H      = "#A93226"
COR_VERDE       = "#16A34A"
COR_VERDE_CLARO = "#DCFCE7"
COR_AZUL        = "#2563EB"
COR_AZUL_CLARO  = "#DBEAFE"
COR_AMBER       = "#F59E0B"
COR_AMBER_CLARO = "#FEF3C7"
COR_LARANJA     = "#EA580C"
COR_LARANJA_BG  = "#FFEDD5"

STATUS_CORES = {
    "Preparando": ("#DBEAFE", "#1D4ED8"),
    "Em Rota":    ("#FFEDD5", "#EA580C"),
    "Entregue":   ("#DCFCE7", "#15803D"),
    "Cancelado":  ("#FEE2E2", "#DC2626"),
}


def renderizar_entregas(frame_conteudo, janela_raiz, paleta_cores, filtro=None):
    controlador = EntregaController(janela_raiz.conn)

    for w in frame_conteudo.winfo_children():
        w.destroy()

    area = ctk.CTkScrollableFrame(frame_conteudo, fg_color=COR_FUNDO,
                                   scrollbar_button_color=COR_BORDA, corner_radius=0)
    area.pack(fill="both", expand=True)

    def _atualizar():
        renderizar_entregas(frame_conteudo, janela_raiz, paleta_cores, filtro)

    # ── CABEÇALHO ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(barra, text="Gestão de Entregas",
                 font=("Arial", 25, "bold"), text_color=COR_TEXTO).pack(side="left")
    ctk.CTkLabel(barra, text="Acompanhe todas as entregas em tempo real",
                 font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left", padx=(14, 0))
    ctk.CTkButton(
        barra, text="+ Nova Entrega",
        fg_color=COR_PRIMARIA, text_color="white", hover_color=COR_PRIM_H,
        corner_radius=10, height=40, font=("Arial", 13, "bold"),
        command=lambda: _abrir_formulario()
    ).pack(side="right")
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(fill="x", padx=28, pady=(4, 16))

    # ── KPI CARDS ─────────────────────────────────────────────────────
    try:
        preparando, em_rota, entregues_hoje, tempo_medio = controlador.obter_estatisticas()
    except Exception:
        preparando, em_rota, entregues_hoje, tempo_medio = 0, 0, 0, 0

    linha_kpi = ctk.CTkFrame(area, fg_color="transparent")
    linha_kpi.pack(fill="x", padx=28, pady=(0, 18))

    kpis = [
        ("📦", "Preparando",     str(preparando),           "pedidos na cozinha",    "#DBEAFE", COR_AZUL),
        ("🛵", "Em Rota",        str(em_rota),              "entregas em andamento",  COR_LARANJA_BG, COR_LARANJA),
        ("✅", "Entregues Hoje", str(entregues_hoje),       "pedidos concluídos",     COR_VERDE_CLARO, COR_VERDE),
        ("⏱", "Tempo Médio",    f"{tempo_medio}min",       "tempo de entrega",       COR_AMBER_CLARO, COR_AMBER),
    ]

    for emoji, titulo, valor, sub, cor_bg, cor_val in kpis:
        card = ctk.CTkFrame(linha_kpi, fg_color=COR_CARD, corner_radius=14,
                            border_width=1, border_color=COR_BORDA, height=110)
        card.pack(side="left", padx=(0, 14), expand=True, fill="x")
        card.pack_propagate(False)

        ib = ctk.CTkFrame(card, fg_color=cor_bg, width=46, height=46, corner_radius=12)
        ib.place(x=16, y=16)
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text=emoji, font=("Arial", 21)).pack(expand=True)

        ctk.CTkLabel(card, text=titulo, font=("Arial", 12), text_color=COR_TEXTO_SUB).place(x=76, y=18)
        ctk.CTkLabel(card, text=valor,  font=("Arial", 23, "bold"), text_color=cor_val).place(x=76, y=38)
        ctk.CTkLabel(card, text=sub,    font=("Arial", 11), text_color=COR_TEXTO_SUB).place(x=16, y=84)

    # ── ABAS DE FILTRO ─────────────────────────────────────────────────
    card_abas = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=12,
                              border_width=1, border_color=COR_BORDA)
    card_abas.pack(fill="x", padx=28, pady=(0, 14))
    linha_abas = ctk.CTkFrame(card_abas, fg_color="transparent")
    linha_abas.pack(fill="x", padx=12, pady=10)

    for rotulo, f in [("⊞  Todos", None), ("📦  Preparando", "Preparando"),
                       ("🛵  Em Rota", "Em Rota"), ("✅  Entregue", "Entregue"),
                       ("✕  Cancelado", "Cancelado")]:
        ativo = (f == filtro)
        ctk.CTkButton(
            linha_abas, text=rotulo,
            fg_color=COR_PRIMARIA if ativo else COR_CARD,
            text_color="white" if ativo else COR_TEXTO_SUB,
            hover_color=COR_PRIM_H if ativo else COR_HOVER,
            border_width=0 if ativo else 1, border_color=COR_BORDA,
            corner_radius=8, height=34,
            font=("Arial", 12, "bold" if ativo else "normal"),
            command=lambda ff=f: renderizar_entregas(frame_conteudo, janela_raiz, paleta_cores, ff)
        ).pack(side="left", padx=(0, 6))

    # ── CARREGAR ENTREGAS ──────────────────────────────────────────────
    try:
        todas = controlador.listar()
    except Exception:
        todas = []

    lista = [e for e in todas if (filtro is None or e.get("status_entrega") == filtro)]

    # ── TÍTULO DA LISTA ────────────────────────────────────────────────
    tit_frame = ctk.CTkFrame(area, fg_color="transparent")
    tit_frame.pack(fill="x", padx=28, pady=(0, 8))
    ctk.CTkLabel(tit_frame, text="Entregas Ativas",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(side="left")

    # ── FORMULÁRIO ────────────────────────────────────────────────────
    def _abrir_formulario(dados=None):
        try:
            pedidos_disp = controlador.listar_pedidos_disponiveis()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar pedidos:\n{e}")
            return

        form = ctk.CTkToplevel(janela_raiz)
        form.title("Entrega")
        form.geometry("460x620")
        form.attributes("-topmost", True)
        form.grab_set()
        form.configure(fg_color=COR_FUNDO)
        form.update_idletasks()
        lx = (form.winfo_screenwidth() - 460) // 2
        ly = (form.winfo_screenheight() - 620) // 2
        form.geometry(f"460x620+{lx}+{ly}")

        ctk.CTkLabel(form, text="Entrega", font=("Arial", 21, "bold"), text_color=COR_TEXTO).pack(pady=(20, 12))

        def _lbl(txt):
            ctk.CTkLabel(form, text=txt, font=("Arial", 13), text_color=COR_TEXTO_SUB, anchor="w").pack(fill="x", padx=30)

        if dados:
            opcoes_pedido = [f"#{dados.get('id_pedido')}"]
        else:
            opcoes_pedido = [f"#{pid} - {nome}" for pid, nome in pedidos_disp] if pedidos_disp else ["Sem pedidos disponíveis"]

        _lbl("Pedido")
        cb_pedido = ctk.CTkComboBox(form, values=opcoes_pedido, height=40,
                                     corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        cb_pedido.pack(fill="x", padx=30, pady=(2, 10))
        if dados:
            cb_pedido.set(f"#{dados.get('id_pedido')}")

        _lbl("Nome do entregador")
        e_nome = ctk.CTkEntry(form, placeholder_text="Ex: João Santos", height=40,
                               corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_nome.pack(fill="x", padx=30, pady=(2, 10))

        _lbl("Telefone do entregador")
        e_fone = ctk.CTkEntry(form, placeholder_text="Ex: (11) 91234-5678", height=40,
                               corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_fone.pack(fill="x", padx=30, pady=(2, 10))

        _lbl("Veículo")
        e_vei = ctk.CTkEntry(form, placeholder_text="Ex: Moto - ABC-1234", height=40,
                              corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_vei.pack(fill="x", padx=30, pady=(2, 10))

        _lbl("Endereço de entrega")
        e_end = ctk.CTkEntry(form, placeholder_text="Ex: Rua das Flores, 123, Apt 45", height=40,
                              corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_end.pack(fill="x", padx=30, pady=(2, 10))

        _lbl("Tempo estimado (minutos)")
        e_tempo = ctk.CTkEntry(form, placeholder_text="Ex: 30", height=40,
                                corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_tempo.pack(fill="x", padx=30, pady=(2, 10))

        _lbl("Status")
        e_status = ctk.CTkComboBox(form, values=["Preparando", "Em Rota", "Entregue", "Cancelado"],
                                    height=40, corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_status.pack(fill="x", padx=30, pady=(2, 10))

        if dados:
            e_nome.insert(0, dados.get("nome_entregador", ""))
            e_fone.insert(0, dados.get("telefone_entregador", "") or "")
            e_vei.insert(0,  dados.get("veiculo", "") or "")
            e_end.insert(0,  dados.get("endereco_entrega", "") or "")
            e_tempo.insert(0, str(dados.get("tempo_estimado", 30)))
            e_status.set(dados.get("status_entrega", "Preparando"))

        lbl_err = ctk.CTkLabel(form, text="", font=("Arial", 12), text_color="#DC2626")
        lbl_err.pack()

        def _salvar():
            raw_pedido = cb_pedido.get()
            try:
                id_pedido = int(raw_pedido.lstrip("#").split(" ")[0])
            except Exception:
                lbl_err.configure(text="Selecione um pedido válido.")
                return
            nome = e_nome.get().strip()
            if not nome:
                lbl_err.configure(text="Informe o nome do entregador.")
                return
            try:
                tempo = int(e_tempo.get() or 30)
            except ValueError:
                tempo = 30
            try:
                controlador.salvar(
                    id_pedido, nome, e_fone.get(), e_vei.get(),
                    e_end.get(), tempo, e_status.get(),
                    dados.get("id_entrega") if dados else None
                )
                form.destroy()
                _atualizar()
            except Exception as ex:
                lbl_err.configure(text=str(ex))

        ctk.CTkButton(form, text="Salvar Entrega",
                      fg_color=COR_PRIMARIA, hover_color=COR_PRIM_H, text_color="white",
                      height=44, corner_radius=10, font=("Arial", 14, "bold"),
                      command=_salvar).pack(fill="x", padx=30, pady=(4, 0))

    # ── LISTA VAZIA ───────────────────────────────────────────────────
    if not lista:
        ctk.CTkLabel(area, text="Nenhuma entrega encontrada.",
                     font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(pady=30)
        return

    # ── CARDS DE ENTREGA ───────────────────────────────────────────────
    for entrega in lista:
        status = entrega.get("status_entrega", "Preparando")
        cor_bg_st, cor_txt_st = STATUS_CORES.get(status, ("#F1F5F9", "#475569"))
        valor = float(entrega.get("valor_total", 0))
        val_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        card = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=14,
                            border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", padx=28, pady=(0, 12))

        # ── Linha superior ──
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(14, 6))

        icone_map = {"Preparando": "📦", "Em Rota": "🛵", "Entregue": "✅", "Cancelado": "✕"}
        icone = icone_map.get(status, "📦")

        icon_frame = ctk.CTkFrame(topo, fg_color=cor_bg_st, width=44, height=44, corner_radius=10)
        icon_frame.pack(side="left", padx=(0, 12))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text=icone, font=("Arial", 21)).pack(expand=True)

        info_esq = ctk.CTkFrame(topo, fg_color="transparent")
        info_esq.pack(side="left", fill="x", expand=True)

        linha_id = ctk.CTkFrame(info_esq, fg_color="transparent")
        linha_id.pack(anchor="w")
        ctk.CTkLabel(linha_id, text=f"#{entrega.get('id_pedido')}",
                     font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(side="left")

        badge = ctk.CTkFrame(linha_id, fg_color=cor_bg_st, corner_radius=8)
        badge.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(badge, text=status, font=("Arial", 11, "bold"),
                     text_color=cor_txt_st).pack(padx=8, pady=2)

        ctk.CTkLabel(info_esq, text=f"{val_fmt}",
                     font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(anchor="w")

        tempo_est = entrega.get("tempo_estimado", 30)
        ctk.CTkLabel(topo, text=f"⏱ {tempo_est} min",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=COR_BORDA).pack(fill="x", padx=16)

        # ── Linha de detalhes ──
        corpo = ctk.CTkFrame(card, fg_color="transparent")
        corpo.pack(fill="x", padx=16, pady=(10, 6))

        col_cliente = ctk.CTkFrame(corpo, fg_color="transparent")
        col_cliente.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(col_cliente, text="👤  " + str(entrega.get("nome_cliente", "–")),
                     font=("Arial", 13, "bold"), text_color=COR_TEXTO).pack(anchor="w")
        ctk.CTkLabel(col_cliente, text="📞  " + str(entrega.get("telefone_cliente", "–") or "–"),
                     font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(col_cliente, text="📍  " + str(entrega.get("endereco_entrega", "–") or "–"),
                     font=("Arial", 12), text_color=COR_TEXTO_SUB, wraplength=280, justify="left").pack(anchor="w", pady=(2, 0))

        col_entregador = ctk.CTkFrame(corpo, fg_color="transparent")
        col_entregador.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(col_entregador, text="🛵  " + str(entrega.get("nome_entregador", "–")),
                     font=("Arial", 13, "bold"), text_color=COR_TEXTO).pack(anchor="w")
        ctk.CTkLabel(col_entregador, text="📞  " + str(entrega.get("telefone_entregador", "–") or "–"),
                     font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(col_entregador, text=str(entrega.get("veiculo", "–") or "–"),
                     font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(anchor="w", pady=(2, 0))
        if entrega.get("hora_saida_fmt") != "--":
            ctk.CTkLabel(col_entregador, text=f"Saiu às {entrega.get('hora_saida_fmt')}",
                         font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(anchor="w", pady=(2, 0))

        # ── Botões ──
        rodape = ctk.CTkFrame(card, fg_color="transparent")
        rodape.pack(fill="x", padx=16, pady=(6, 12))

        dados_snap = dict(entrega)
        ctk.CTkButton(
            rodape, text="✏ Editar",
            fg_color=COR_AZUL_CLARO, text_color=COR_AZUL, hover_color="#BFDBFE",
            height=30, width=90, corner_radius=6, font=("Arial", 12), border_width=0,
            command=lambda d=dados_snap: _abrir_formulario(d)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            rodape, text="🗑",
            fg_color="#FEE2E2", text_color=COR_PRIMARIA, hover_color="#FECACA",
            height=30, width=36, corner_radius=6, font=("Arial", 13), border_width=0,
            command=lambda d=dados_snap: (
                messagebox.askyesno("Confirmar", f"Excluir entrega #{d.get('id_entrega')}?") and
                (controlador.excluir(d.get("id_entrega")), _atualizar())
            )
        ).pack(side="left")

    ctk.CTkFrame(area, height=20, fg_color="transparent").pack()
