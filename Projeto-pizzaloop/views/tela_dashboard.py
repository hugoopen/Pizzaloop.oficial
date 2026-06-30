import customtkinter as ctk
import tkinter as tk
import datetime

from controllers.dashboard_controller import DashboardController

COR_FUNDO        = "#FAF5F3"
COR_CARD         = "#FFFFFF"
COR_BORDA        = "#E8DDD9"
COR_TEXTO        = "#1C1917"
COR_TEXTO_SUB    = "#78716C"
COR_PRIMARIA     = "#C0392B"
COR_VERDE        = "#16A34A"
COR_VERDE_CLARO  = "#DCFCE7"
COR_AZUL         = "#2563EB"
COR_AZUL_CLARO   = "#DBEAFE"
COR_AMBER        = "#F59E0B"
COR_AMBER_CLARO  = "#FEF3C7"
COR_VERMELHO_BG  = "#FEE2E2"
COR_ROXO         = "#9333EA"
COR_ROXO_CLARO   = "#F3E8FF"

STATUS_CORES = {
    "entregue":   ("#DCFCE7", "#15803D"),
    "preparo":    ("#FEF3C7", "#D97706"),
    "caminho":    ("#DBEAFE", "#1D4ED8"),
    "cancelado":  ("#FEE2E2", "#DC2626"),
    "aguardando": ("#F1F5F9", "#475569"),
}

COLUNAS_STATUS = [
    ("Aguardando",  "⏸",  "#F1F5F9", "#475569", "#E2E8F0"),
    ("Em preparo",  "⏳",  COR_AMBER_CLARO, "#D97706", "#FDE68A"),
    ("A caminho",   "🛵",  COR_AZUL_CLARO, "#1D4ED8", "#BFDBFE"),
]

W_ID     = 45
W_CLI    = 160
W_PROD   = 160
W_VAL    = 100
W_PGTO   = 130
W_STATUS = 115
W_DATA   = 110

INTERVALO_ATUALIZACAO_MS = 30_000  # 30 segundos


def _criar_card(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14,
                        border_width=1, border_color=COR_BORDA, **kw)


def _tag_status(status: str) -> str:
    s = (status or "").lower()
    if "entreg" in s:                    return "entregue"
    if "preparo" in s or "prepar" in s:  return "preparo"
    if "saiu" in s or "caminho" in s:    return "caminho"
    if "cancel" in s:                    return "cancelado"
    return "aguardando"


def _card_kpi(parent, titulo, valor, subtexto, cor_valor, emoji, cor_icone_bg):
    card = _criar_card(parent, height=130)
    card.pack(side="left", padx=(0, 14), expand=True, fill="x")
    card.pack_propagate(False)

    fundo_icone = ctk.CTkFrame(card, fg_color=cor_icone_bg, width=52, height=52, corner_radius=14)
    fundo_icone.place(x=18, y=18)
    fundo_icone.pack_propagate(False)
    ctk.CTkLabel(fundo_icone, text=emoji, font=("Arial", 24)).pack(expand=True)

    ctk.CTkLabel(card, text=titulo, font=("Arial", 13), text_color=COR_TEXTO_SUB).place(x=84, y=20)
    ctk.CTkLabel(card, text=valor, font=("Arial", 22, "bold"), text_color=cor_valor).place(x=84, y=42)
    ctk.CTkLabel(card, text=subtexto, font=("Arial", 12), text_color=COR_TEXTO_SUB).place(x=18, y=102)


def _desenhar_grafico(canvas_grafico, dados):
    """
    Desenha o gráfico de linha de faturamento da semana.
    Cada item de `dados` é (rotulo_dia, valor, data).
    """
    canvas_grafico.delete("all")
    larg = canvas_grafico.winfo_width()
    alt  = canvas_grafico.winfo_height()
    if larg < 10 or alt < 10:
        return

    if not dados:
        canvas_grafico.create_text(
            larg // 2, alt // 2,
            text="Sem vendas nos últimos 7 dias",
            font=("Arial", 13), fill=COR_TEXTO_SUB
        )
        return

    pad_left  = 72
    pad_right = 24
    pad_top   = 28
    pad_bot   = 42

    area_larg = larg - pad_left - pad_right
    area_alt  = alt  - pad_top  - pad_bot

    valores  = [v for _, v, _ in dados]
    max_val  = max(valores) if max(valores) > 0 else 1
    import math
    teto = math.ceil(max_val / 100) * 100 if max_val < 10_000 else math.ceil(max_val / 1_000) * 1_000
    teto = max(teto, 1)

    n = len(dados)

    LINHAS_GRADE = 4
    for i in range(LINHAS_GRADE + 1):
        frac  = i / LINHAS_GRADE
        y_gr  = pad_top + area_alt - int(area_alt * frac)
        val_y = teto * frac

        for xi in range(pad_left, larg - pad_right, 8):
            canvas_grafico.create_line(xi, y_gr, xi + 4, y_gr,
                                       fill="#E8DDD9", width=1)

        if val_y < 1000:
            txt_y = f"R${val_y:.0f}"
        else:
            txt_y = f"R${val_y/1000:.1f}k"
        canvas_grafico.create_text(pad_left - 6, y_gr, text=txt_y,
                                   font=("Arial", 10), fill=COR_TEXTO_SUB,
                                   anchor="e")

    canvas_grafico.create_line(pad_left, pad_top + area_alt,
                               larg - pad_right, pad_top + area_alt,
                               fill="#D1C7C3", width=2)

    def _x_ponto(i):
        if n == 1:
            return pad_left + area_larg // 2
        return pad_left + int(i * area_larg / (n - 1))

    def _y_ponto(val):
        return pad_top + area_alt - int(area_alt * val / teto)

    pontos = [(_x_ponto(i), _y_ponto(val)) for i, (_, val, _) in enumerate(dados)]

    base_y = pad_top + area_alt
    poligono = []
    for x, y in pontos:
        poligono += [x, y]
    poligono += [pontos[-1][0], base_y, pontos[0][0], base_y]

    canvas_grafico.create_polygon(
        poligono,
        fill="#FDDEDE",
        outline="",
        smooth=True
    )

    if len(pontos) >= 2:
        coords_linha = []
        for x, y in pontos:
            coords_linha += [x, y]
        canvas_grafico.create_line(
            *coords_linha,
            fill=COR_PRIMARIA,
            width=3,
            smooth=True,
            joinstyle="round",
            capstyle="round"
        )

    for i, (dia, val, _) in enumerate(dados):
        x, y = pontos[i]
        canvas_grafico.create_line(x, pad_top + area_alt,
                                   x, pad_top + area_alt + 6,
                                   fill="#D1C7C3", width=1)
        canvas_grafico.create_text(x, pad_top + area_alt + 18,
                                   text=dia,
                                   font=("Arial", 11, "bold"),
                                   fill=COR_TEXTO_SUB)

    RAIO = 5
    tooltips = {}

    for i, (dia, val, _) in enumerate(dados):
        x, y = pontos[i]

        canvas_grafico.create_oval(x - RAIO - 1, y - RAIO - 1,
                                   x + RAIO + 1, y + RAIO + 1,
                                   fill="#E8DDD9", outline="")

        oval_id = canvas_grafico.create_oval(
            x - RAIO, y - RAIO, x + RAIO, y + RAIO,
            fill=COR_PRIMARIA, outline="#FFFFFF", width=2
        )

        if val > 0:
            label_val = (f"R${val:,.0f}"
                         .replace(",", "X").replace(".", ",").replace("X", "."))
            label_w = len(label_val) * 7 + 4
            ly = y - RAIO - 2
            if x + RAIO + 6 + label_w > larg - pad_right:
                lx  = x - RAIO - 6
                anc = "e"
                rx0, rx1 = lx - label_w, lx + 2
            else:
                lx  = x + RAIO + 6
                anc = "w"
                rx0, rx1 = lx - 2, lx + label_w
            canvas_grafico.create_rectangle(
                rx0, ly - 9, rx1, ly + 9,
                fill=COR_CARD, outline="", width=0
            )
            canvas_grafico.create_text(lx, ly,
                                       text=label_val,
                                       font=("Arial", 10, "bold"),
                                       fill=COR_PRIMARIA,
                                       anchor=anc)

        tooltips[oval_id] = (x, y, dia, val)

    tooltip_box = [None, None]

    def _mostrar_tooltip(event):
        _esconder_tooltip()
        item = canvas_grafico.find_closest(event.x, event.y)[0]
        if item not in tooltips:
            return
        px, py, dia_tt, val_tt = tooltips[item]
        label = (f"{dia_tt}:  R$ {val_tt:,.2f}"
                 .replace(",", "X").replace(".", ",").replace("X", "."))
        tx = px
        ty = py - RAIO - 28
        if tx + 90 > larg:
            tx = larg - 95
        if tx - 90 < 0:
            tx = 95
        if ty < 4:
            ty = py + RAIO + 10

        r = canvas_grafico.create_rectangle(
            tx - 72, ty - 12, tx + 72, ty + 14,
            fill="#1C1917", outline="", width=0
        )
        t = canvas_grafico.create_text(
            tx, ty, text=label,
            font=("Arial", 11, "bold"), fill="#FFFFFF"
        )
        tooltip_box[0] = r
        tooltip_box[1] = t

    def _esconder_tooltip(event=None):
        for obj in tooltip_box:
            if obj:
                try:
                    canvas_grafico.delete(obj)
                except Exception:
                    pass
        tooltip_box[0] = None
        tooltip_box[1] = None

    canvas_grafico.bind("<Motion>", _mostrar_tooltip)
    canvas_grafico.bind("<Leave>",  _esconder_tooltip)


def _desenhar_grafico_barras(canvas, dados):
    """
    Desenha gráfico de barras com faturamento por dia da semana.
    Cada item de `dados` é (rotulo_dia, valor, data) — já vem pronto e
    ordenado do Model, com os 7 dias preenchidos (inclusive zerados).
    """
    canvas.delete("all")
    larg = canvas.winfo_width()
    alt  = canvas.winfo_height()
    if larg < 10 or alt < 10:
        return

    valores_ordenados = dados

    pad_left  = 72
    pad_right = 20
    pad_top   = 45
    pad_bot   = 46

    area_larg = larg - pad_left - pad_right
    area_alt  = alt  - pad_top  - pad_bot

    import math
    max_val = max((v for _, v, _ in valores_ordenados), default=1)
    if max_val == 0:
        canvas.create_text(larg // 2, alt // 2,
                           text="Sem vendas nos últimos 7 dias",
                           font=("Arial", 13), fill=COR_TEXTO_SUB)
        return

    teto = math.ceil(max_val / 100) * 100 if max_val < 10_000 else math.ceil(max_val / 1_000) * 1_000
    teto = max(teto, 1)

    LINHAS = 4
    for i in range(LINHAS + 1):
        frac = i / LINHAS
        y_gr = pad_top + area_alt - int(area_alt * frac)
        val_y = teto * frac
        for xi in range(pad_left, larg - pad_right, 8):
            canvas.create_line(xi, y_gr, xi + 4, y_gr, fill="#E8DDD9", width=1)
        txt_y = f"R${val_y/1000:.1f}k" if val_y >= 1000 else f"R${val_y:.0f}"
        canvas.create_text(pad_left - 6, y_gr, text=txt_y,
                           font=("Arial", 10), fill=COR_TEXTO_SUB, anchor="e")

    canvas.create_line(pad_left, pad_top + area_alt,
                       larg - pad_right, pad_top + area_alt,
                       fill="#D1C7C3", width=2)

    n = len(valores_ordenados)
    espaco_total = area_larg / n
    largura_barra = espaco_total * 0.55

    hoje = datetime.date.today()

    for i, (dia, val, data_item) in enumerate(valores_ordenados):
        x_centro = pad_left + espaco_total * i + espaco_total / 2
        x0 = x_centro - largura_barra / 2
        x1 = x_centro + largura_barra / 2

        altura_barra = int(area_alt * val / teto) if val > 0 else 2
        y0 = pad_top + area_alt - altura_barra
        y1 = pad_top + area_alt

        eh_hoje = (data_item == hoje)
        cor_barra = COR_PRIMARIA if eh_hoje else "#D97070"
        cor_borda  = "#A02020" if eh_hoje else "#B85555"

        canvas.create_rectangle(x0 + 3, y0 + 3, x1 + 3, y1,
                                 fill="#E0C8C8", outline="", width=0)

        canvas.create_rectangle(x0, y0, x1, y1,
                                 fill=cor_barra, outline=cor_borda, width=1)

        canvas.create_rectangle(x0, y0, x1, y0 + 6,
                                 fill=cor_barra, outline="", width=0)

        if val > 0:
            label_val = (f"R${val:,.0f}"
                         .replace(",", "X").replace(".", ",").replace("X", "."))
            canvas.create_text(x_centro, y0 - 10,
                                text=label_val,
                                font=("Arial", 9, "bold"),
                                fill=COR_PRIMARIA)

        cor_label = COR_TEXTO if eh_hoje else COR_TEXTO_SUB
        peso_label = "bold" if eh_hoje else "normal"
        canvas.create_text(x_centro, pad_top + area_alt + 18,
                            text=dia,
                            font=("Arial", 11, peso_label),
                            fill=cor_label)

        canvas.create_line(x_centro, pad_top + area_alt,
                            x_centro, pad_top + area_alt + 6,
                            fill="#D1C7C3", width=1)

    idx_hoje = next((i for i, (_, _, d) in enumerate(valores_ordenados) if d == hoje), None)

    if idx_hoje is not None:
        x_hoje = pad_left + espaco_total * idx_hoje + espaco_total / 2
        val_hoje = valores_ordenados[idx_hoje][1]

        if val_hoje > 0:
            y_badge = pad_top + area_alt - int(area_alt * val_hoje / teto) - 26
            canvas.create_rectangle(x_hoje - 22, y_badge - 8,
                                      x_hoje + 22, y_badge + 8,
                                      fill=COR_PRIMARIA, outline="", width=0)
            canvas.create_text(x_hoje, y_badge,
                                text="Hoje", font=("Arial", 9, "bold"),
                                fill="#FFFFFF")


def _construir_painel_tempo_real(parent, controlador, janela_raiz):
    """
    Monta (ou reconstrói) o painel de pedidos em aberto agrupados por status.
    Retorna o card principal para ser usado como âncora dos after().
    """
    card_painel = _criar_card(parent)
    card_painel.pack(fill="x", padx=28, pady=(0, 18))

    cab_painel = ctk.CTkFrame(card_painel, fg_color="transparent")
    cab_painel.pack(fill="x", padx=18, pady=(14, 0))

    ctk.CTkLabel(cab_painel, text="🔴  Pedidos em Aberto",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(side="left")

    hora_atual = datetime.datetime.now().strftime("%H:%M:%S")
    lbl_hora = ctk.CTkLabel(cab_painel,
                             text=f"Atualizado às {hora_atual}  ·  atualiza a cada 30s",
                             font=("Arial", 12), text_color=COR_TEXTO_SUB)
    lbl_hora.pack(side="left", padx=(10, 0))

    ctk.CTkButton(
        cab_painel, text="↻ Atualizar",
        fg_color=COR_AZUL_CLARO, text_color=COR_AZUL, hover_color="#BFDBFE",
        height=30, corner_radius=8, font=("Arial", 13), border_width=0,
        command=lambda: _recarregar_painel(card_painel, controlador, janela_raiz, lbl_hora)
    ).pack(side="right")

    ctk.CTkFrame(card_painel, height=1, fg_color=COR_BORDA).pack(fill="x", padx=0, pady=(10, 0))

    try:
        grupos = controlador.buscar_pedidos_em_aberto_por_status()
    except Exception:
        grupos = {"Aguardando": [], "Em preparo": [], "A caminho": []}

    total_abertos = sum(len(v) for v in grupos.values())

    if total_abertos == 0:
        ctk.CTkLabel(card_painel,
                     text="✅  Nenhum pedido em aberto no momento.",
                     font=("Arial", 15), text_color=COR_VERDE).pack(pady=20)
        return card_painel

    grade = ctk.CTkFrame(card_painel, fg_color="transparent")
    grade.pack(fill="x", padx=14, pady=14)

    for nome_col, emoji_col, cor_bg_col, cor_txt_col, cor_borda_col in COLUNAS_STATUS:
        lista_pedidos = grupos.get(nome_col, [])
        quantidade    = len(lista_pedidos)

        col = ctk.CTkFrame(grade, fg_color=cor_bg_col, corner_radius=12,
                            border_width=1, border_color=cor_borda_col)
        col.pack(side="left", padx=(0, 12), expand=True, fill="both")

        cab_col = ctk.CTkFrame(col, fg_color="transparent")
        cab_col.pack(fill="x", padx=12, pady=(12, 6))
        ctk.CTkLabel(cab_col, text=f"{emoji_col}  {nome_col}",
                     font=("Arial", 14, "bold"), text_color=cor_txt_col).pack(side="left")

        badge_count = ctk.CTkFrame(cab_col, fg_color=cor_txt_col,
                                    width=28, height=22, corner_radius=11)
        badge_count.pack(side="right")
        badge_count.pack_propagate(False)
        ctk.CTkLabel(badge_count, text=str(quantidade),
                     font=("Arial", 12, "bold"), text_color="white").pack(expand=True)

        ctk.CTkFrame(col, height=1, fg_color=cor_borda_col).pack(fill="x", padx=0)

        if not lista_pedidos:
            ctk.CTkLabel(col, text="Nenhum pedido",
                         font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(pady=14)
            continue

        for ped in lista_pedidos[:6]:
            val_fmt = (
                f"R$ {float(ped.get('valor_total', 0)):,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            dh = ped.get("data_hora")
            hora_ped = dh.strftime("%H:%M") if dh else "--"

            mini = ctk.CTkFrame(col, fg_color=COR_CARD, corner_radius=8,
                                 border_width=1, border_color=COR_BORDA)
            mini.pack(fill="x", padx=8, pady=(6, 0))

            linha1 = ctk.CTkFrame(mini, fg_color="transparent")
            linha1.pack(fill="x", padx=10, pady=(8, 2))
            ctk.CTkLabel(linha1, text=f"#{ped.get('id_pedidos', '')}",
                         font=("Arial", 12, "bold"), text_color=cor_txt_col).pack(side="left")
            ctk.CTkLabel(linha1, text=hora_ped,
                         font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="right")

            ctk.CTkLabel(mini,
                         text=str(ped.get("nome_cliente", ""))[:22],
                         font=("Arial", 13, "bold"), text_color=COR_TEXTO,
                         anchor="w").pack(fill="x", padx=10)
            ctk.CTkLabel(mini,
                         text=str(ped.get("nome_produto", ""))[:22],
                         font=("Arial", 12), text_color=COR_TEXTO_SUB,
                         anchor="w").pack(fill="x", padx=10)
            ctk.CTkLabel(mini,
                         text=val_fmt,
                         font=("Arial", 13, "bold"), text_color=COR_PRIMARIA,
                         anchor="w").pack(fill="x", padx=10, pady=(0, 8))

        if len(lista_pedidos) > 6:
            ctk.CTkLabel(col,
                         text=f"+ {len(lista_pedidos) - 6} mais...",
                         font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(pady=(4, 8))
        else:
            ctk.CTkFrame(col, height=8, fg_color="transparent").pack()

    return card_painel


def _recarregar_painel(card_painel, controlador, janela_raiz, lbl_hora):
    """Atualiza o label de hora e reconstrói o conteúdo do painel dentro do card."""
    hora_atual = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        lbl_hora.configure(text=f"Atualizado às {hora_atual}  ·  atualiza a cada 30s")
    except Exception:
        return

    filhos = card_painel.winfo_children()
    for w in filhos[2:]:
        w.destroy()

    try:
        grupos = controlador.buscar_pedidos_em_aberto_por_status()
    except Exception:
        grupos = {"Aguardando": [], "Em preparo": [], "A caminho": []}

    total_abertos = sum(len(v) for v in grupos.values())

    if total_abertos == 0:
        ctk.CTkLabel(card_painel,
                     text="✅  Nenhum pedido em aberto no momento.",
                     font=("Arial", 15), text_color=COR_VERDE).pack(pady=20)
        return

    grade = ctk.CTkFrame(card_painel, fg_color="transparent")
    grade.pack(fill="x", padx=14, pady=14)

    for nome_col, emoji_col, cor_bg_col, cor_txt_col, cor_borda_col in COLUNAS_STATUS:
        lista_pedidos = grupos.get(nome_col, [])
        quantidade    = len(lista_pedidos)

        col = ctk.CTkFrame(grade, fg_color=cor_bg_col, corner_radius=12,
                            border_width=1, border_color=cor_borda_col)
        col.pack(side="left", padx=(0, 12), expand=True, fill="both")

        cab_col = ctk.CTkFrame(col, fg_color="transparent")
        cab_col.pack(fill="x", padx=12, pady=(12, 6))
        ctk.CTkLabel(cab_col, text=f"{emoji_col}  {nome_col}",
                     font=("Arial", 14, "bold"), text_color=cor_txt_col).pack(side="left")
        badge_count = ctk.CTkFrame(cab_col, fg_color=cor_txt_col,
                                    width=28, height=22, corner_radius=11)
        badge_count.pack(side="right")
        badge_count.pack_propagate(False)
        ctk.CTkLabel(badge_count, text=str(quantidade),
                     font=("Arial", 12, "bold"), text_color="white").pack(expand=True)

        ctk.CTkFrame(col, height=1, fg_color=cor_borda_col).pack(fill="x")

        if not lista_pedidos:
            ctk.CTkLabel(col, text="Nenhum pedido",
                         font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(pady=14)
            continue

        for ped in lista_pedidos[:6]:
            val_fmt = (
                f"R$ {float(ped.get('valor_total', 0)):,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            dh = ped.get("data_hora")
            hora_ped = dh.strftime("%H:%M") if dh else "--"

            mini = ctk.CTkFrame(col, fg_color=COR_CARD, corner_radius=8,
                                 border_width=1, border_color=COR_BORDA)
            mini.pack(fill="x", padx=8, pady=(6, 0))

            linha1 = ctk.CTkFrame(mini, fg_color="transparent")
            linha1.pack(fill="x", padx=10, pady=(8, 2))
            ctk.CTkLabel(linha1, text=f"#{ped.get('id_pedidos', '')}",
                         font=("Arial", 12, "bold"), text_color=cor_txt_col).pack(side="left")
            ctk.CTkLabel(linha1, text=hora_ped,
                         font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="right")
            ctk.CTkLabel(mini, text=str(ped.get("nome_cliente", ""))[:22],
                         font=("Arial", 13, "bold"), text_color=COR_TEXTO, anchor="w").pack(fill="x", padx=10)
            ctk.CTkLabel(mini, text=str(ped.get("nome_produto", ""))[:22],
                         font=("Arial", 12), text_color=COR_TEXTO_SUB, anchor="w").pack(fill="x", padx=10)
            ctk.CTkLabel(mini, text=val_fmt,
                         font=("Arial", 13, "bold"), text_color=COR_PRIMARIA,
                         anchor="w").pack(fill="x", padx=10, pady=(0, 8))

        if len(lista_pedidos) > 6:
            ctk.CTkLabel(col, text=f"+ {len(lista_pedidos) - 6} mais...",
                         font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(pady=(4, 8))
        else:
            ctk.CTkFrame(col, height=8, fg_color="transparent").pack()


def _agendar_proxima_atualizacao(card_painel, controlador, janela_raiz, lbl_hora):
    """Agenda a próxima atualização e salva o ID do after() no card para cancelamento."""
    def _executar():
        try:
            card_painel.winfo_exists()
        except Exception:
            return
        if not card_painel.winfo_exists():
            return
        _recarregar_painel(card_painel, controlador, janela_raiz, lbl_hora)
        _agendar_proxima_atualizacao(card_painel, controlador, janela_raiz, lbl_hora)

    id_after = card_painel.after(INTERVALO_ATUALIZACAO_MS, _executar)
    card_painel._id_after_refresh = id_after


def renderizar_dashboard(frame_conteudo, janela_raiz, paleta_cores):
    controlador = DashboardController(janela_raiz.conn)
    frame_conteudo.configure(fg_color=COR_FUNDO)

    area = ctk.CTkScrollableFrame(frame_conteudo, fg_color=COR_FUNDO,
                                   scrollbar_button_color=COR_BORDA, corner_radius=0)
    area.pack(fill="both", expand=True)

    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(barra, text="Visão Geral", font=("Arial", 26, "bold"),
                 text_color=COR_TEXTO).pack(side="left")
    ctk.CTkLabel(barra, text="Painel de controle da pizzaria",
                 font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(side="left", padx=(14, 0))
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(fill="x", padx=28, pady=(4, 18))

    try:
        resumo = controlador.pegar_dados_resumo()
    except Exception:
        resumo = {"pedidos_hoje": "–", "pedidos": "–", "faturamento": "R$ –",
                  "ticket_medio": "R$ –", "clientes": "–"}

    linha_kpi = ctk.CTkFrame(area, fg_color="transparent")
    linha_kpi.pack(fill="x", padx=28, pady=(0, 18))
    _card_kpi(linha_kpi, "Vendas Hoje",   resumo["pedidos_hoje"], "pedidos realizados hoje",
              COR_PRIMARIA, "🛒", COR_VERMELHO_BG)
    _card_kpi(linha_kpi, "Total Pedidos", resumo["pedidos"],      "desde o início",
              COR_AZUL, "📋", COR_AZUL_CLARO)
    _card_kpi(linha_kpi, "Ticket Médio",  resumo["ticket_medio"], "por pedido",
              COR_AMBER, "💰", COR_AMBER_CLARO)
    _card_kpi(linha_kpi, "Clientes",      resumo["clientes"],     "cadastrados",
              COR_VERDE, "👥", COR_VERDE_CLARO)

    card_painel = _construir_painel_tempo_real(area, controlador, janela_raiz)

    cab_painel = card_painel.winfo_children()[0]
    lbl_hora   = [w for w in cab_painel.winfo_children()
                  if isinstance(w, ctk.CTkLabel) and "Atualizado" in (w.cget("text") or "")]
    lbl_hora   = lbl_hora[0] if lbl_hora else ctk.CTkLabel(card_painel, text="")

    _agendar_proxima_atualizacao(card_painel, controlador, janela_raiz, lbl_hora)

    linha_meio = ctk.CTkFrame(area, fg_color="transparent")
    linha_meio.pack(fill="x", padx=28, pady=(0, 18))

    card_grafico = _criar_card(linha_meio)
    card_grafico.pack(side="left", fill="both", expand=True, padx=(0, 14))

    try:
        dados_semana = controlador.pegar_vendas_semana()
    except Exception as e:
        print(f"Erro ao buscar vendas da semana: {e}")
        dados_semana = []

    total_semana = sum(v for _, v, _ in dados_semana)
    total_semana_fmt = (
        f"R$ {total_semana:,.2f}"
        .replace(",", "X").replace(".", ",").replace("X", ".")
    )

    cab_graf = ctk.CTkFrame(card_grafico, fg_color="transparent")
    cab_graf.pack(fill="x", padx=18, pady=(16, 2))
    ctk.CTkLabel(cab_graf, text="📊  Faturamento da Semana",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(side="left")
    ctk.CTkLabel(cab_graf, text=total_semana_fmt,
                 font=("Arial", 16, "bold"), text_color=COR_PRIMARIA).pack(side="right")

    ctk.CTkLabel(card_grafico, text="Receita por dia nos últimos 7 dias",
                 font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=18, pady=(0, 10))

    canvas_g = tk.Canvas(card_grafico, height=240, bg=COR_CARD, highlightthickness=0)
    canvas_g.pack(fill="x", padx=14, pady=(0, 16))

    def _redraw(event=None):
        canvas_g.update_idletasks()
        _desenhar_grafico(canvas_g, dados_semana)

    canvas_g.bind("<Configure>", _redraw)
    canvas_g.after(200, _redraw)

    card_top = _criar_card(linha_meio, width=260)
    card_top.pack(side="left", fill="y")
    card_top.pack_propagate(False)
    ctk.CTkLabel(card_top, text="🏆  Mais Vendidas",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=18, pady=(16, 4))
    ctk.CTkLabel(card_top, text="Top produtos do período",
                 font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=18, pady=(0, 10))

    medalhas = ["🥇", "🥈", "🥉"]
    try:
        from controllers.relatorios_controller import RelatoriosController
        top_produtos = RelatoriosController(janela_raiz.conn).performance_produtos("7dias")[:3]
    except Exception:
        top_produtos = []

    for idx, item in enumerate(top_produtos):
        nome, qtd, _ = item
        row = ctk.CTkFrame(card_top, fg_color="#FAF5F3", corner_radius=8)
        row.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(row, text=medalhas[idx], font=("Arial", 20)).pack(side="left", padx=(10, 6), pady=8)
        col = ctk.CTkFrame(row, fg_color="transparent")
        col.pack(side="left", fill="x", expand=True, pady=8)
        ctk.CTkLabel(col, text=nome[:22], font=("Arial", 13, "bold"),
                     text_color=COR_TEXTO).pack(anchor="w")
        ctk.CTkLabel(col, text=f"{qtd} unid.", font=("Arial", 12),
                     text_color=COR_TEXTO_SUB).pack(anchor="w")

    if not top_produtos:
        ctk.CTkLabel(card_top, text="Sem dados no período",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(pady=20)

    card_barras = _criar_card(area)
    card_barras.pack(fill="x", padx=28, pady=(0, 18))

    cab_barras = ctk.CTkFrame(card_barras, fg_color="transparent")
    cab_barras.pack(fill="x", padx=18, pady=(16, 2))
    ctk.CTkLabel(cab_barras, text="📊  Faturamento por Dia da Semana",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(side="left")
    badge_hoje = ctk.CTkFrame(cab_barras, fg_color=COR_VERMELHO_BG,
                               corner_radius=8, height=24)
    badge_hoje.pack(side="left", padx=(12, 0))
    badge_hoje.pack_propagate(False)
    ctk.CTkLabel(badge_hoje, text="  ● Hoje em destaque  ",
                 font=("Arial", 11, "bold"), text_color=COR_PRIMARIA).pack(expand=True, padx=4)

    ctk.CTkLabel(card_barras, text="Receita total acumulada por dia nos últimos 7 dias",
                 font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=18, pady=(0, 10))

    canvas_barras = tk.Canvas(card_barras, height=260, bg=COR_CARD, highlightthickness=0)
    canvas_barras.pack(fill="x", padx=14, pady=(0, 16))

    def _redraw_barras(event=None):
        canvas_barras.update_idletasks()
        _desenhar_grafico_barras(canvas_barras, dados_semana)

    canvas_barras.bind("<Configure>", _redraw_barras)
    canvas_barras.after(300, _redraw_barras)

    card_tabela = _criar_card(area)
    card_tabela.pack(fill="x", padx=28, pady=(0, 28))

    ctk.CTkLabel(card_tabela, text="📋  Pedidos Recentes",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=18, pady=(16, 8))

    try:
        pedidos = controlador.pegar_ultimas_visitas(10)
    except Exception:
        pedidos = []

    cab = ctk.CTkFrame(card_tabela, fg_color="#F5F0EE", corner_radius=0, height=36)
    cab.pack(fill="x", padx=0)
    cab.pack_propagate(False)

    ctk.CTkLabel(cab, text="", width=14).pack(side="left")
    for txt, w, anc in [
        ("#",         W_ID,     "center"),
        ("Cliente",   W_CLI,    "w"),
        ("Produto",   W_PROD,   "w"),
        ("Valor",     W_VAL,    "w"),
        ("Pagamento", W_PGTO,   "w"),
        ("Status",    W_STATUS, "w"),
        ("Data",      W_DATA,   "w"),
    ]:
        ctk.CTkLabel(cab, text=txt, width=w, anchor=anc,
                     font=("Arial", 13, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")

    ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    if not pedidos:
        ctk.CTkLabel(card_tabela, text="Nenhum pedido encontrado.",
                     font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(pady=20)

    for idx, ped in enumerate(pedidos):
        valor   = ped.get("valor_total", 0)
        val_fmt = f"R$ {float(valor):,.2f}".replace(",","X").replace(".",",").replace("X",".")
        tag     = _tag_status(ped.get("status_pedido", ""))
        cor_bg_st, cor_txt_st = STATUS_CORES.get(tag, (COR_CARD, COR_TEXTO_SUB))
        cor_linha = COR_CARD if idx % 2 == 0 else "#FAF5F3"
        if tag == "entregue":
            cor_linha = "#F0FDF4"

        linha = ctk.CTkFrame(card_tabela, fg_color=cor_linha, corner_radius=0, height=42)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkLabel(linha, text="", width=14).pack(side="left")

        def _cel(txt, w, anc="w", cor=COR_TEXTO):
            ctk.CTkLabel(linha, text=str(txt), width=w, anchor=anc,
                         font=("Arial", 14), text_color=cor).pack(side="left")

        _cel(ped.get("id_pedidos", ""),              W_ID,   "center", COR_TEXTO_SUB)
        _cel(str(ped.get("nome_cliente", ""))[:20],  W_CLI)
        _cel(str(ped.get("nome_produto", ""))[:20],  W_PROD)
        _cel(val_fmt,                                W_VAL)
        _cel(str(ped.get("metodo_pagamento", "–")), W_PGTO, "w", COR_TEXTO_SUB)

        badge = ctk.CTkFrame(linha, fg_color=cor_bg_st, corner_radius=8,
                             width=W_STATUS - 8, height=22)
        badge.pack(side="left", pady=10)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=str(ped.get("status_pedido", "–")),
                     font=("Arial", 12, "bold"), text_color=cor_txt_st).pack(expand=True)

        _cel(str(ped.get("data_formatada", "")),     W_DATA, "w", COR_TEXTO_SUB)

        if idx < len(pedidos) - 1:
            ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    ctk.CTkFrame(card_tabela, height=10, fg_color="transparent").pack()