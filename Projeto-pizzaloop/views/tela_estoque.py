import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from controllers.estoque_controller import EstoqueController, CATEGORIAS_VALIDAS, UNIDADES_VALIDAS
from services import permissao_service

COR_FUNDO        = "#FAF5F3"
COR_CARD         = "#FFFFFF"
COR_BORDA        = "#E8DDD9"
COR_TEXTO        = "#1C1917"
COR_TEXTO_SUB    = "#78716C"
COR_PRIMARIA     = "#C0392B"
COR_PRIM_H       = "#A93226"
COR_VERDE        = "#16A34A"
COR_VERDE_CLARO  = "#DCFCE7"
COR_AMBER        = "#D97706"
COR_AMBER_CLARO  = "#FEF3C7"
COR_AZUL         = "#2563EB"
COR_AZUL_CLARO   = "#DBEAFE"
COR_ROXO         = "#7C3AED"
COR_ROXO_CLARO   = "#EDE9FE"
COR_SEPARADOR    = "#F5F0EE"

CORES_CATEGORIA = {
    "Massa":      ("#D97706", "#FEF3C7"),
    "Carne":      ("#DC2626", "#FEE2E2"),
    "Queijo":     ("#D97706", "#FFFBEB"),
    "Molho":      ("#16A34A", "#DCFCE7"),
    "Bebida":     ("#2563EB", "#DBEAFE"),
    "Embalagem":  ("#7C3AED", "#EDE9FE"),
    "Frios":      ("#0891B2", "#CFFAFE"),
    "Geral":      ("#78716C", "#F5F5F4"),
}

CORES_AVATAR = [
    ("#7C3AED", "#EDE9FE"),
    ("#2563EB", "#DBEAFE"),
    ("#059669", "#D1FAE5"),
    ("#D97706", "#FEF3C7"),
    ("#DB2777", "#FCE7F3"),
    ("#0891B2", "#CFFAFE"),
    ("#C0392B", "#FEE2E2"),
]

W_AVATAR    = 44
W_NOME      = 200
W_CATEGORIA = 120
W_QTD       = 110
W_MINIMO    = 100
W_CUSTO     = 110
W_STATUS    = 90
W_ACOES     = 170


def _iniciais(nome: str) -> str:
    partes = nome.strip().split()
    return "".join(p[0].upper() for p in partes[:2] if p)


def _fmt_qtd(valor, unidade):
    try:
        v = float(valor)
        return f"{int(v)} {unidade}" if v == int(v) else f"{v:.2f} {unidade}"
    except Exception:
        return f"{valor} {unidade}"


def _fmt_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def renderizar_estoque(frame_conteudo, janela_raiz, paleta_cores):
    usuario_logado = getattr(janela_raiz, "usuario_logado", None)
    controlador = EstoqueController(janela_raiz.conn, usuario_logado)
    pode_editar_estoque = permissao_service.pode_editar(usuario_logado, "estoque")

    for w in frame_conteudo.winfo_children():
        w.destroy()

    area = ctk.CTkScrollableFrame(
        frame_conteudo, fg_color=COR_FUNDO,
        scrollbar_button_color=COR_BORDA, corner_radius=0
    )
    area.pack(fill="both", expand=True)

    def _atualizar():
        renderizar_estoque(frame_conteudo, janela_raiz, paleta_cores)

    # ── CABEÇALHO ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(
        barra, text="Controle de Estoque",
        font=("Arial", 25, "bold"), text_color=COR_TEXTO
    ).pack(side="left")
    if pode_editar_estoque:
        ctk.CTkButton(
            barra, text="+ Novo Item",
            fg_color=COR_PRIMARIA, text_color="white", hover_color=COR_PRIM_H,
            corner_radius=10, height=40, font=("Arial", 13, "bold"),
            command=lambda: _abrir_formulario()
        ).pack(side="right")
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(
        fill="x", padx=28, pady=(4, 14)
    )

    # ── CARREGAR DADOS ────────────────────────────────────────────────
    try:
        lista = controlador.listar_itens()
    except Exception:
        lista = []

    total_itens    = len(lista)
    alertas        = sum(1 for i in lista if float(i.get("quantidade_atual", 0)) < float(i.get("quantidade_minima", 0)))
    categorias_qtd = len(set(i.get("categoria", "Geral") for i in lista))
    custo_total_estoque = sum(
        float(i.get("preco_custo", 0)) * float(i.get("quantidade_atual", 0))
        for i in lista
    )

    # ── CARDS KPI ─────────────────────────────────────────────────────
    linha_kpi = ctk.CTkFrame(area, fg_color="transparent")
    linha_kpi.pack(fill="x", padx=28, pady=(0, 16))

    def _kpi(parent, titulo, valor, emoji, cor_bg, cor_val):
        c = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12,
                         border_width=1, border_color=COR_BORDA, height=80)
        c.pack(side="left", padx=(0, 12), expand=True, fill="x")
        c.pack_propagate(False)
        ib = ctk.CTkFrame(c, fg_color=cor_bg, width=36, height=36, corner_radius=8)
        ib.place(x=12, y=12)
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text=emoji, font=("Arial", 17)).pack(expand=True)
        ctk.CTkLabel(c, text=titulo, font=("Arial", 11),
                     text_color=COR_TEXTO_SUB).place(x=56, y=12)
        ctk.CTkLabel(c, text=str(valor), font=("Arial", 19, "bold"),
                     text_color=cor_val).place(x=56, y=32)

    _kpi(linha_kpi, "Total de Itens",     total_itens,                  "📦", COR_AZUL_CLARO,  COR_AZUL)
    _kpi(linha_kpi, "Alertas de Estoque", alertas,                      "⚠️", COR_AMBER_CLARO, COR_AMBER if alertas == 0 else COR_PRIMARIA)
    _kpi(linha_kpi, "Categorias",         categorias_qtd,               "🏷️", COR_ROXO_CLARO, COR_ROXO)
    _kpi(linha_kpi, "Custo Total Estoque",_fmt_moeda(custo_total_estoque),"💰", COR_VERDE_CLARO, COR_VERDE)

    # ── FORMULÁRIO CADASTRO / EDIÇÃO ──────────────────────────────────
    def _abrir_formulario(dados=None):
        eh_edicao = dados is not None

        form = ctk.CTkToplevel(janela_raiz)
        form.title("Editar Item" if eh_edicao else "Novo Item de Estoque")
        form.geometry("440x580")
        form.attributes("-topmost", True)
        form.grab_set()
        form.focus_force()
        form.update_idletasks()
        lx = (form.winfo_screenwidth()  - 440) // 2
        ly = (form.winfo_screenheight() - 580) // 2
        form.geometry(f"440x580+{lx}+{ly}")

        ctk.CTkLabel(
            form,
            text="Editar Item" if eh_edicao else "Novo Item de Estoque",
            font=("Arial", 19, "bold"),
        ).pack(pady=(20, 4))

        corpo = ctk.CTkScrollableFrame(form, fg_color="transparent",
                                       scrollbar_button_color=COR_BORDA, corner_radius=0)
        corpo.pack(fill="both", expand=True, padx=10)

        def _campo(label, placeholder, parent=corpo):
            ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"),
                         anchor="w").pack(anchor="w", padx=40)
            e = ctk.CTkEntry(parent, placeholder_text=placeholder, width=320, height=38)
            e.pack(pady=(2, 10))
            return e

        e_nome = _campo("Nome do item *", "Ex: Massa de Pizza")

        ctk.CTkLabel(corpo, text="Categoria", font=("Arial", 12, "bold"),
                     anchor="w").pack(anchor="w", padx=40)
        combo_categoria = ctk.CTkComboBox(corpo, values=CATEGORIAS_VALIDAS,
                                          width=320, height=38)
        combo_categoria.pack(pady=(2, 10))

        e_qtd    = _campo("Quantidade atual *", "Ex: 50")

        ctk.CTkLabel(corpo, text="Unidade de medida", font=("Arial", 12, "bold"),
                     anchor="w").pack(anchor="w", padx=40)
        combo_unidade = ctk.CTkComboBox(corpo, values=UNIDADES_VALIDAS,
                                        width=320, height=38)
        combo_unidade.pack(pady=(2, 10))

        e_minimo = _campo("Quantidade mínima (alerta)", "Ex: 10")
        e_custo  = _campo("Preço de custo por unidade (R$)", "Ex: 2.50")

        if dados:
            e_nome.insert(0,    dados.get("nome_item", ""))
            combo_categoria.set(dados.get("categoria", "Geral"))
            e_qtd.insert(0,     str(dados.get("quantidade_atual", 0)))
            combo_unidade.set(  dados.get("unidade_medida", "unidade"))
            e_minimo.insert(0,  str(dados.get("quantidade_minima", 0)))
            e_custo.insert(0,   str(dados.get("preco_custo", "0")))
        else:
            combo_categoria.set("Geral")
            combo_unidade.set("unidade")

        lbl_erro = ctk.CTkLabel(corpo, text="", font=("Arial", 12), text_color="#DC2626")
        lbl_erro.pack(pady=(0, 4))

        def _salvar():
            ok, msg = controlador.validar_e_salvar(
                e_nome.get(), combo_categoria.get(), e_qtd.get(),
                combo_unidade.get(), e_minimo.get(),
                dados.get("id_item") if dados else None,
                e_custo.get(),
            )
            if ok:
                form.destroy()
                _atualizar()
            else:
                lbl_erro.configure(text=msg)

        ctk.CTkButton(
            form, text="💾 Salvar",
            fg_color=COR_PRIMARIA, hover_color=COR_PRIM_H,
            text_color="white", width=220, height=42,
            corner_radius=10, font=("Arial", 12, "bold"),
            command=_salvar,
        ).pack(pady=16)

    # ── FORMULÁRIO DE MOVIMENTAÇÃO ────────────────────────────────────
    def _abrir_movimentacao(dados_item):
        mov = ctk.CTkToplevel(janela_raiz)
        mov.title(f"Movimentar: {dados_item.get('nome_item')}")
        mov.geometry("400x420")
        mov.attributes("-topmost", True)
        mov.grab_set()
        mov.focus_force()
        mov.update_idletasks()
        lx = (mov.winfo_screenwidth()  - 400) // 2
        ly = (mov.winfo_screenheight() - 420) // 2
        mov.geometry(f"400x420+{lx}+{ly}")

        ctk.CTkLabel(mov, text="Movimentar Estoque",
                     font=("Arial", 18, "bold")).pack(pady=(18, 2))
        ctk.CTkLabel(mov, text=dados_item.get("nome_item", ""),
                     font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(pady=(0, 10))

        ctk.CTkLabel(mov, text="Tipo de movimentação",
                     font=("Arial", 12, "bold"), anchor="w").pack(anchor="w", padx=40)
        combo_tipo = ctk.CTkComboBox(mov, values=["Entrada", "Saída", "Ajuste"],
                                     width=300, height=38)
        combo_tipo.set("Entrada")
        combo_tipo.pack(pady=(2, 12))

        ctk.CTkLabel(mov, text="Quantidade *",
                     font=("Arial", 12, "bold"), anchor="w").pack(anchor="w", padx=40)
        e_qtd = ctk.CTkEntry(mov, placeholder_text="Ex: 10", width=300, height=38)
        e_qtd.pack(pady=(2, 12))

        ctk.CTkLabel(mov, text="Observação (opcional)",
                     font=("Arial", 12, "bold"), anchor="w").pack(anchor="w", padx=40)
        e_obs = ctk.CTkEntry(mov, placeholder_text="Ex: Compra semanal",
                             width=300, height=38)
        e_obs.pack(pady=(2, 12))

        lbl_erro = ctk.CTkLabel(mov, text="", font=("Arial", 12), text_color="#DC2626")
        lbl_erro.pack(pady=(0, 4))

        def _salvar_mov():
            ok, msg = controlador.registrar_movimentacao(
                dados_item["id_item"], combo_tipo.get(), e_qtd.get(), e_obs.get()
            )
            if ok:
                mov.destroy()
                _atualizar()
            else:
                lbl_erro.configure(text=msg)

        ctk.CTkButton(
            mov, text="✅ Registrar",
            fg_color=COR_VERDE, hover_color="#15803D",
            text_color="white", width=200, height=42,
            corner_radius=10, font=("Arial", 12, "bold"),
            command=_salvar_mov,
        ).pack(pady=10)

    # ── JANELA DE HISTÓRICO ───────────────────────────────────────────
    def _abrir_historico(dados_item):
        hist = ctk.CTkToplevel(janela_raiz)
        hist.title(f"Histórico: {dados_item.get('nome_item')}")
        hist.geometry("520x480")
        hist.attributes("-topmost", True)
        hist.grab_set()
        hist.focus_force()
        hist.update_idletasks()
        lx = (hist.winfo_screenwidth()  - 520) // 2
        ly = (hist.winfo_screenheight() - 480) // 2
        hist.geometry(f"520x480+{lx}+{ly}")

        ctk.CTkLabel(hist, text=f"Histórico — {dados_item.get('nome_item')}",
                     font=("Arial", 17, "bold")).pack(pady=(18, 10))

        lista_mov = controlador.buscar_historico(dados_item["id_item"])

        scroll = ctk.CTkScrollableFrame(hist, fg_color="#F8F8F8", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        if not lista_mov:
            ctk.CTkLabel(scroll, text="Nenhuma movimentação registrada.",
                         font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(pady=30)
        else:
            TIPO_COR   = {"Entrada": COR_VERDE, "Saída": COR_PRIMARIA, "Ajuste": COR_AMBER}
            TIPO_SINAL = {"Entrada": "+", "Saída": "−", "Ajuste": "="}
            for mov in lista_mov:
                tipo  = mov.get("tipo", "")
                qtd   = mov.get("quantidade", 0)
                obs   = mov.get("observacao", "") or ""
                dh    = mov.get("data_hora")
                cor   = TIPO_COR.get(tipo, COR_TEXTO_SUB)
                sinal = TIPO_SINAL.get(tipo, "")
                try:
                    data_fmt = dh.strftime("%d/%m/%Y %H:%M") if dh else "--"
                except Exception:
                    data_fmt = str(dh)

                row = ctk.CTkFrame(scroll, fg_color=COR_CARD, corner_radius=8,
                                   border_width=1, border_color=COR_BORDA)
                row.pack(fill="x", padx=4, pady=4)

                lado = ctk.CTkFrame(row, fg_color="transparent")
                lado.pack(side="left", padx=12, pady=8, fill="x", expand=True)
                ctk.CTkLabel(lado, text=f"{sinal} {qtd}  •  {tipo}",
                             font=("Arial", 13, "bold"), text_color=cor, anchor="w").pack(anchor="w")
                ctk.CTkLabel(lado, text=obs if obs else "Sem observação",
                             font=("Arial", 11), text_color=COR_TEXTO_SUB, anchor="w").pack(anchor="w")
                ctk.CTkLabel(row, text=data_fmt,
                             font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(side="right", padx=12)

    # ── LISTA VAZIA ───────────────────────────────────────────────────
    if not lista:
        ctk.CTkLabel(area, text="Nenhum item cadastrado no estoque.",
                     font=("Arial", 15), text_color=COR_TEXTO_SUB).pack(pady=50)
        return

    # ── TABELA ────────────────────────────────────────────────────────
    card_tabela = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=14,
                               border_width=1, border_color=COR_BORDA)
    card_tabela.pack(fill="x", padx=28, pady=(0, 28))

    cab = ctk.CTkFrame(card_tabela, fg_color=COR_SEPARADOR, corner_radius=0, height=38)
    cab.pack(fill="x")
    cab.pack_propagate(False)

    def _montar_cabecalho_estoque(t, w, anc="w"):
        ctk.CTkLabel(cab, text=t, width=w, anchor=anc, font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")

    ctk.CTkLabel(cab, text="", width=14).pack(side="left")
    _montar_cabecalho_estoque("",            W_AVATAR,    "center")
    _montar_cabecalho_estoque("Item",        W_NOME)
    _montar_cabecalho_estoque("Categoria",   W_CATEGORIA, "center")
    _montar_cabecalho_estoque("Quantidade",  W_QTD)
    _montar_cabecalho_estoque("Mínimo",      W_MINIMO)
    _montar_cabecalho_estoque("Custo Unit.", W_CUSTO)
    _montar_cabecalho_estoque("Status",      W_STATUS,    "center")
    _montar_cabecalho_estoque("Ações",       W_ACOES,     "center")

    ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    def _confirmar_exclusao(dados_item):
        if messagebox.askyesno(
            "Confirmar",
            f"Excluir \"{dados_item.get('nome_item')}\" e todo o histórico?"
        ):
            ok, msg = controlador.excluir(dados_item["id_item"])
            if ok:
                _atualizar()
            else:
                messagebox.showerror("Erro", msg)

    for idx, item in enumerate(lista):
        cor_txt_av, cor_bg_av = CORES_AVATAR[idx % len(CORES_AVATAR)]
        iniciais   = _iniciais(item.get("nome_item", "?"))
        nome       = item.get("nome_item", "")
        categoria  = item.get("categoria", "Geral")
        qtd_atual  = float(item.get("quantidade_atual", 0))
        qtd_min    = float(item.get("quantidade_minima", 0))
        unidade    = item.get("unidade_medida", "unidade")
        preco_custo= float(item.get("preco_custo", 0) or 0)
        abaixo_min = qtd_atual < qtd_min

        cor_linha = COR_CARD if idx % 2 == 0 else "#FAF5F3"
        cor_cat_txt, cor_cat_bg = CORES_CATEGORIA.get(categoria, ("#78716C", "#F5F5F4"))

        linha = ctk.CTkFrame(card_tabela, fg_color=cor_linha, corner_radius=0, height=46)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkLabel(linha, text="", width=14).pack(side="left")

        celula_av = ctk.CTkFrame(linha, fg_color="transparent", width=W_AVATAR, height=46)
        celula_av.pack(side="left")
        celula_av.pack_propagate(False)
        ctk.CTkLabel(celula_av, text=iniciais, font=("Arial", 11, "bold"),
                     text_color=cor_txt_av).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(linha, text=nome, width=W_NOME, anchor="w",
                     font=("Arial", 13, "bold"), text_color=COR_TEXTO).pack(side="left")

        celula_cat = ctk.CTkFrame(linha, fg_color="transparent", width=W_CATEGORIA, height=46)
        celula_cat.pack(side="left")
        celula_cat.pack_propagate(False)
        badge_cat = ctk.CTkFrame(celula_cat, fg_color=cor_cat_bg, corner_radius=8,
                                 width=W_CATEGORIA - 24, height=24)
        badge_cat.place(relx=0.5, rely=0.5, anchor="center")
        badge_cat.pack_propagate(False)
        ctk.CTkLabel(badge_cat, text=categoria, font=("Arial", 11, "bold"),
                     text_color=cor_cat_txt).pack(expand=True)

        ctk.CTkLabel(linha, text=_fmt_qtd(qtd_atual, unidade), width=W_QTD, anchor="w",
                     font=("Arial", 13), text_color=COR_TEXTO).pack(side="left")

        ctk.CTkLabel(linha, text=_fmt_qtd(qtd_min, unidade), width=W_MINIMO, anchor="w",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left")

        # Custo unitário
        cor_custo = COR_VERDE if preco_custo > 0 else COR_TEXTO_SUB
        ctk.CTkLabel(linha, text=_fmt_moeda(preco_custo), width=W_CUSTO, anchor="w",
                     font=("Arial", 13), text_color=cor_custo).pack(side="left")

        if abaixo_min:
            cor_st, bg_st, txt_st = COR_AMBER, COR_AMBER_CLARO, "⚠ Baixo"
        else:
            cor_st, bg_st, txt_st = COR_VERDE, COR_VERDE_CLARO, "✓ OK"

        celula_st = ctk.CTkFrame(linha, fg_color="transparent", width=W_STATUS, height=46)
        celula_st.pack(side="left")
        celula_st.pack_propagate(False)
        badge_st = ctk.CTkFrame(celula_st, fg_color=bg_st, corner_radius=8,
                                width=W_STATUS - 24, height=24)
        badge_st.place(relx=0.5, rely=0.5, anchor="center")
        badge_st.pack_propagate(False)
        ctk.CTkLabel(badge_st, text=txt_st, font=("Arial", 11, "bold"),
                     text_color=cor_st).pack(expand=True)

        dados_item = dict(item)

        celula_acoes = ctk.CTkFrame(linha, fg_color="transparent", width=W_ACOES, height=46)
        celula_acoes.pack(side="left")
        celula_acoes.pack_propagate(False)
        linha_acoes = ctk.CTkFrame(celula_acoes, fg_color="transparent")
        linha_acoes.place(relx=0.5, rely=0.5, anchor="center")

        if pode_editar_estoque:
            ctk.CTkButton(
                linha_acoes, text="+ / −",
                fg_color=COR_VERDE, hover_color="#15803D",
                text_color="white", height=28, width=52,
                corner_radius=6, font=("Arial", 11, "bold"),
                command=lambda d=dados_item: _abrir_movimentacao(d)
            ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            linha_acoes, text="📋",
            fg_color=COR_AZUL_CLARO, hover_color="#BFDBFE",
            text_color=COR_AZUL, height=28, width=30,
            corner_radius=6, font=("Arial", 12),
            command=lambda d=dados_item: _abrir_historico(d)
        ).pack(side="left", padx=(0, 4))

        if pode_editar_estoque:
            ctk.CTkButton(
                linha_acoes, text="✏",
                fg_color=COR_AZUL_CLARO, text_color=COR_AZUL, hover_color="#BFDBFE",
                height=28, width=30, corner_radius=6, font=("Arial", 12), border_width=0,
                command=lambda d=dados_item: _abrir_formulario(d)
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                linha_acoes, text="🗑",
                fg_color="#FEE2E2", text_color=COR_PRIMARIA, hover_color="#FECACA",
                height=28, width=30, corner_radius=6, font=("Arial", 13), border_width=0,
                command=lambda d=dados_item: _confirmar_exclusao(d)
            ).pack(side="left")

        if idx < len(lista) - 1:
            ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")
