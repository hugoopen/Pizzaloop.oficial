import customtkinter as ctk
from tkinter import messagebox
from controllers.pedidos_controller import PedidoController

# ── CONFIGURAÇÃO DE CORES ─────────────────────────────────────────────
COR_FUNDO          = "#FAF5F3"
COR_CARD           = "#FFFFFF"
COR_BORDA          = "#E8DDD9"
COR_HOVER          = "#FEF3C7"
COR_TEXTO          = "#1C1917"
COR_TEXTO_SUB      = "#78716C"
COR_PRIMARIA       = "#C0392B"
COR_PRIM_H         = "#A93226"
COR_VERDE          = "#16A34A"
COR_VERDE_CLARO    = "#DCFCE7"
COR_AZUL           = "#2563EB"
COR_AZUL_CLARO     = "#DBEAFE"
COR_AMBER          = "#F59E0B"
COR_AMBER_CLARO    = "#FEF3C7"

# ── DIMENSÕES DAS COLUNAS DA TABELA ──────────────────────────────────
W_ID          = 40
W_CLIENTE     = 150
W_PRODUTO     = 150
W_QTD         = 40
W_VALOR       = 90
W_PGTO        = 120
W_ENTREGADOR  = 110
W_STATUS      = 100
W_DATA        = 100
W_ACOES       = 110
W_PAGO        = 74

STATUS_CORES = {
    "entregue":   ("#DCFCE7", "#15803D"),
    "preparo":    ("#FEF3C7", "#D97706"),
    "caminho":    ("#DBEAFE", "#1D4ED8"),
    "cancelado":  ("#FEE2E2", "#DC2626"),
    "aguardando": ("#F1F5F9", "#475569"),
}


def _tag_status(status: str) -> str:
    s = (status or "").lower()
    if "entreg" in s:                   return "entregue"
    if "preparo" in s:                  return "preparo"
    if "caminho" in s or "saiu" in s:   return "caminho"
    if "cancel" in s:                   return "cancelado"
    return "aguardando"


def renderizar_pedidos(frame_conteudo, janela_raiz, paleta_cores, filtro_status=None):
    controlador = PedidoController(janela_raiz.conn)

    # Limpeza segura dos widgets anteriores
    for w in frame_conteudo.winfo_children():
        w.destroy()

    area = ctk.CTkScrollableFrame(
        frame_conteudo, fg_color=COR_CARD,
        scrollbar_button_color=COR_BORDA, corner_radius=0
    )
    area.pack(fill="both", expand=True)

    # Callback central de atualização
    def _atualizar():
        renderizar_pedidos(frame_conteudo, janela_raiz, paleta_cores, filtro_status)

    # ── CABEÇALHO ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    
    ctk.CTkLabel(
        barra, text="Gestão de Pedidos",
        font=("Arial", 25, "bold"), text_color=COR_TEXTO
    ).pack(side="left")
    
    ctk.CTkButton(
        barra, text="+ Novo Pedido",
        fg_color=COR_PRIMARIA, text_color="white", hover_color=COR_PRIM_H,
        corner_radius=10, height=40, font=("Arial", 13, "bold"),
        command=lambda: _abrir_formulario_pedido()
    ).pack(side="right")
    
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(fill="x", padx=28, pady=(4, 12))

    # ── CARREGAR DADOS DO BANCO ───────────────────────────────────────
    try:
        todos_pedidos = controlador.listar()
    except Exception:
        todos_pedidos = []

    # ── CARDS METRICAS / ESTATÍSTICAS ─────────────────────────────────
    em_preparo  = sum(1 for p in todos_pedidos if "preparo" in (p.get("status_pedido") or "").lower())
    faturamento = sum(float(p.get("valor_total", 0)) for p in todos_pedidos)
    fat_fmt     = f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    linha_stats = ctk.CTkFrame(area, fg_color="transparent")
    linha_stats.pack(fill="x", padx=28, pady=(0, 14))

    def _exibir_card_estatistica(parent, titulo, valor, emoji, cor_bg, cor_txt):
        c = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12,
                         border_width=1, border_color=COR_BORDA, height=90)
        c.pack(side="left", padx=(0, 12), expand=True, fill="x")
        c.pack_propagate(False)
        
        ib = ctk.CTkFrame(c, fg_color=cor_bg, width=40, height=40, corner_radius=10)
        ib.place(x=14, y=14)
        ib.pack_propagate(False)
        
        ctk.CTkLabel(ib, text=emoji, font=("Arial", 19)).pack(expand=True)
        ctk.CTkLabel(c, text=titulo, font=("Arial", 11), text_color=COR_TEXTO_SUB).place(x=62, y=14)
        ctk.CTkLabel(c, text=valor,  font=("Arial", 18, "bold"), text_color=cor_txt).place(x=62, y=34)

    _exibir_card_estatistica(linha_stats, "Pedidos Hoje",  str(len(todos_pedidos)), "🛒", "#FEE2E2",      COR_PRIMARIA)
    _exibir_card_estatistica(linha_stats, "Em Preparo",    str(em_preparo),          "⏳", COR_AMBER_CLARO, COR_AMBER)
    _exibir_card_estatistica(linha_stats, "Total Pedidos", str(len(todos_pedidos)),  "📋", COR_AZUL_CLARO,  COR_AZUL)
    _exibir_card_estatistica(linha_stats, "Faturamento",   fat_fmt,                  "💰", COR_VERDE_CLARO, COR_VERDE)

    # ── FILTROS (ABAS) ────────────────────────────────────────────────
    card_abas = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
    card_abas.pack(fill="x", padx=28, pady=(0, 12))
    linha_abas = ctk.CTkFrame(card_abas, fg_color="transparent")
    linha_abas.pack(fill="x", padx=12, pady=10)

    abas = [
        ("⊞  Todos", None), 
        ("⏸  Aguardando", "aguardando"),
        ("⏳  Em Preparo", "preparo"),
        ("🛵  A Caminho", "caminho"), 
        ("✓  Entregue", "entregue"),
        ("✕  Cancelado", "cancelado")
    ]

    for rotulo, filtro in abas:
        ativo = (filtro == filtro_status)
        ctk.CTkButton(
            linha_abas, text=rotulo,
            fg_color=COR_PRIMARIA if ativo else COR_CARD,
            text_color="white" if ativo else COR_TEXTO_SUB,
            hover_color=COR_PRIM_H if ativo else COR_HOVER,
            border_width=0 if ativo else 1, border_color=COR_BORDA,
            corner_radius=8, height=34,
            font=("Arial", 12, "bold" if ativo else "normal"),
            command=lambda f=filtro: renderizar_pedidos(frame_conteudo, janela_raiz, paleta_cores, f)
        ).pack(side="left", padx=(0, 6))

    # ── FILTRAR LISTA ─────────────────────────────────────────────────
    if filtro_status:
        lista = [p for p in todos_pedidos if filtro_status.lower() in (p.get("status_pedido") or "").lower()]
    else:
        lista = todos_pedidos

    # ── TABELA DE DADOS ───────────────────────────────────────────────
    card_tabela = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
    card_tabela.pack(fill="x", padx=28, pady=(0, 28))

    cab = ctk.CTkFrame(card_tabela, fg_color="#F5F0EE", corner_radius=0, height=38)
    cab.pack(fill="x")
    cab.pack_propagate(False)

    def _montar_cabecalho_tabela(t, w, anc="w"):
        ctk.CTkLabel(cab, text=t, width=w, anchor=anc, font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")

    ctk.CTkLabel(cab, text="", width=14).pack(side="left")
    _montar_cabecalho_tabela("#",         W_ID,         "center")
    _montar_cabecalho_tabela("Cliente",    W_CLIENTE)
    _montar_cabecalho_tabela("Produto",    W_PRODUTO)
    _montar_cabecalho_tabela("Qtd",        W_QTD,         "center")
    _montar_cabecalho_tabela("Valor",      W_VALOR)
    _montar_cabecalho_tabela("Pagamento",  W_PGTO)
    _montar_cabecalho_tabela("Entregador", W_ENTREGADOR)
    _montar_cabecalho_tabela("Status",      W_STATUS)
    _montar_cabecalho_tabela("Data",        W_DATA)
    _montar_cabecalho_tabela("Ações",       W_ACOES,       "center")
    _montar_cabecalho_tabela("Pago",         W_PAGO,        "center")

    ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    if not lista:
        ctk.CTkLabel(card_tabela, text="Nenhum pedido encontrado.", font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(pady=24)

    # ── DETALHAMENTO DE FUNÇÕES (SUB-MÉTODOS INTERNOS) ────────────────
    def _marcar_pago(dados_ped, novo_pago):
        try:
            controlador.alternar_pago(dados_ped['id_pedidos'], novo_pago)
            _atualizar()
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel atualizar o pagamento:\n{e}")

    def _confirmar_exclusao_pedido(dados_ped):
        id_ped = dados_ped.get('id_pedidos')
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir o pedido #{id_ped}?"):
            try:
                controlador.excluir(id_ped)
                _atualizar()
            except Exception as e:
                messagebox.showerror("Erro ao Excluir", f"Não foi possível deletar o pedido:\n{e}")

    def _abrir_formulario_pedido(dados_pedido=None):
        try:
            dic_clientes, dic_produtos = controlador.buscar_dados_auxiliares()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar dados auxiliares:\n{e}")
            return

        dic_entregadores = controlador.buscar_entregadores_ativos_para_selecao()
        opcoes_entregadores = ["— Sem entregador —"] + list(dic_entregadores.keys())

        form = ctk.CTkToplevel(janela_raiz)
        form.title("Formulário de Pedido")
        form.geometry("460x730") 
        form.attributes("-topmost", True)
        form.grab_set()
        form.configure(fg_color=COR_FUNDO)
        
        form.update_idletasks()
        lx = (form.winfo_screenwidth() - 460) // 2
        ly = (form.winfo_screenheight() - 730) // 2
        form.geometry(f"460x730+{lx}+{ly}")

        ctk.CTkLabel(form, text="Inserir / Editar Pedido", font=("Arial", 21, "bold"), text_color=COR_TEXTO).pack(pady=(20, 14))

        def _lbl(txt):
            ctk.CTkLabel(form, text=txt, font=("Arial", 13), text_color=COR_TEXTO_SUB, anchor="w").pack(fill="x", padx=30)

        _lbl("Cliente")
        cb_cliente = ctk.CTkComboBox(form, values=list(dic_clientes.keys()), height=38, corner_radius=8,
                                     border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        cb_cliente.pack(fill="x", padx=30, pady=(2, 8))

        _lbl("Produto")
        cb_produto = ctk.CTkComboBox(form, values=list(dic_produtos.keys()), height=38, corner_radius=8,
                                     border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        cb_produto.pack(fill="x", padx=30, pady=(2, 8))

        _lbl("Quantidade")
        e_qtd = ctk.CTkEntry(form, placeholder_text="1", height=38, corner_radius=8,
                             border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_qtd.pack(fill="x", padx=30, pady=(2, 8))

        _lbl("Status")
        e_status = ctk.CTkComboBox(form, values=["Aguardando", "Em preparo", "A caminho", "Entregue", "Cancelado"],
                                   height=38, corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_status.pack(fill="x", padx=30, pady=(2, 8))

        _lbl("Pagamento")
        e_pagto = ctk.CTkComboBox(form, values=["Dinheiro", "Cartão Débito", "Cartão Crédito", "PIX"],
                                  height=38, corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        e_pagto.pack(fill="x", padx=30, pady=(2, 8))

        _lbl("Entregador (opcional)")
        cb_entregador = ctk.CTkComboBox(form, values=opcoes_entregadores, height=38, corner_radius=8,
                                        border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
        cb_entregador.set("— Sem entregador —")
        cb_entregador.pack(fill="x", padx=30, pady=(2, 8))

        _lbl("Status de Pagamento")
        cb_status_pagamento = ctk.CTkComboBox(
            form,
            values=["Pendente (Não Pago)", "Pago"],
            height=38, corner_radius=8, border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13)
        )
        cb_status_pagamento.set("Pendente (Não Pago)")
        cb_status_pagamento.pack(fill="x", padx=30, pady=(2, 8))

        if dados_pedido:
            cb_cliente.set(dados_pedido.get("nome_cliente", ""))
            cb_produto.set(dados_pedido.get("nome_produto", ""))
            e_qtd.insert(0, str(dados_pedido.get("quantidade", 1)))
            e_status.set(dados_pedido.get("status_pedido", ""))
            e_pagto.set(dados_pedido.get("metodo_pagamento", ""))
            nome_ent = dados_pedido.get("nome_entregador") or "— Sem entregador —"
            cb_entregador.set(nome_ent)
            pago_atual = int(dados_pedido.get("pago", 0))
            cb_status_pagamento.set("Pago" if pago_atual else "Pendente (Não Pago)")

        lbl_erro = ctk.CTkLabel(form, text="", font=("Arial", 12), text_color="#DC2626")
        lbl_erro.pack()

        def _salvar_pedido():
            nome_cli  = cb_cliente.get()
            nome_prod = cb_produto.get()
            
            if nome_cli not in dic_clientes or nome_prod not in dic_produtos:
                lbl_erro.configure(text="Selecione cliente e produto válidos.")
                return
                
            id_cli         = dic_clientes[nome_cli]
            id_prod, preco = dic_produtos[nome_prod]
            nome_ent_sel   = cb_entregador.get()
            id_entregador  = dic_entregadores.get(nome_ent_sel, None)
            tempo_preparo  = dados_pedido.get("tempo_preparo", "20 min") if dados_pedido else "20 min"
            
            try:
                qtd = int(e_qtd.get() or 1)
                pago_selecionado = 1 if cb_status_pagamento.get() == "Pago" else 0
                controlador.salvar(
                    id_cli, id_prod, qtd, preco,
                    e_status.get(), e_pagto.get(),
                    id_entregador,
                    dados_pedido.get("id_pedidos") if dados_pedido else None,
                    tempo_preparo,
                    pago_selecionado
                )
                form.destroy()
                _atualizar()
            except Exception as ex:
                lbl_erro.configure(text=str(ex))

        ctk.CTkButton(
            form, text="Salvar Pedido",
            fg_color=COR_PRIMARIA, hover_color=COR_PRIM_H, text_color="white",
            height=44, corner_radius=10, font=("Arial", 14, "bold"),
            command=_salvar_pedido
        ).pack(fill="x", padx=30, pady=(10, 0))

    # ── MONTAGEM DAS LINHAS DA TABELA (LOOP DE DADOS) ─────────────────
    for idx, ped in enumerate(lista):
        valor   = float(ped.get("valor_total", 0))
        val_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        status_atual = ped.get("status_pedido", "")
        tag     = _tag_status(status_atual)
        cor_bg_st, cor_txt_st = STATUS_CORES.get(tag, (COR_CARD, COR_TEXTO_SUB))

        linha = ctk.CTkFrame(card_tabela, fg_color=COR_CARD, corner_radius=0, height=46)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkLabel(linha, text="", width=14).pack(side="left")

        def _adicionar_celula(txt, w, anc="w", cor=COR_TEXTO):
            lbl = ctk.CTkLabel(linha, text=str(txt), width=w, anchor=anc, font=("Arial", 13), text_color=cor)
            lbl.pack(side="left")
            return lbl

        _adicionar_celula(ped.get("id_pedidos", ""),               W_ID,         "center", COR_TEXTO_SUB)
        _adicionar_celula(str(ped.get("nome_cliente", ""))[:18],   W_CLIENTE)
        _adicionar_celula(str(ped.get("nome_produto", ""))[:18],   W_PRODUTO)
        _adicionar_celula(ped.get("browse_qtd", ped.get("quantidade", "")), W_QTD, "center")
        _adicionar_celula(val_fmt,                                  W_VALOR)
        _adicionar_celula(str(ped.get("metodo_pagamento", "–")),    W_PGTO,       "w", COR_TEXTO_SUB)
        _adicionar_celula(str(ped.get("nome_entregador") or "–")[:14], W_ENTREGADOR, "w", COR_TEXTO_SUB)

        # Container para a Badge de Status colorido
        badge = ctk.CTkFrame(linha, fg_color=cor_bg_st, corner_radius=8, width=W_STATUS - 8, height=24)
        badge.pack(side="left", pady=11)
        badge.pack_propagate(False)
        
        ctk.CTkLabel(
            badge, text=str(status_atual),
            font=("Arial", 11, "bold"), text_color=cor_txt_st
        ).pack(expand=True)

        _adicionar_celula(str(ped.get("data_formatada", "")),       W_DATA,       "w", COR_TEXTO_SUB)

        # Isolamento do dicionário por linha para o escopo dos botões de ação
        dados_ped = dict(ped)
        
        ctk.CTkButton(
            linha, text="✏ Editar",
            fg_color=COR_AZUL_CLARO, text_color=COR_AZUL, hover_color="#BFDBFE",
            height=28, width=72, corner_radius=6, font=("Arial", 12), border_width=0,
            command=lambda d=dados_ped: _abrir_formulario_pedido(d)
        ).pack(side="left", padx=(2, 4))

        ctk.CTkButton(
            linha, text="🗑",
            fg_color="#FEE2E2", text_color=COR_PRIMARIA, hover_color="#FECACA",
            height=28, width=34, corner_radius=6, font=("Arial", 13), border_width=0,
            command=lambda d=dados_ped: _confirmar_exclusao_pedido(d)
        ).pack(side="left")

        # -- Botao Pago/Nao Pago
        pago_atual = int(dados_ped.get("pago", 0))
        novo_pago  = 0 if pago_atual else 1
        ctk.CTkButton(
            linha,
            text="V Pago" if pago_atual else "X Pagar",
            fg_color=COR_VERDE_CLARO if pago_atual else "#FEE2E2",
            text_color=COR_VERDE if pago_atual else COR_PRIMARIA,
            hover_color="#BBF7D0" if pago_atual else "#FECACA",
            height=28, width=70, corner_radius=6,
            font=("Arial", 11, "bold"), border_width=0,
            command=lambda d=dados_ped, np=novo_pago: _marcar_pago(d, np)
        ).pack(side="left", padx=(6, 0))

        if idx < len(lista) - 1:
            ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")