import customtkinter as ctk
from tkinter import messagebox
from controllers.entregador_controller import EntregadorController
from utils.formatadores import (
    aplicar_mascara_tel, aplicar_mascara_cpf,
    formatar_cpf, formatar_telefone
)

COR_FUNDO        = "#FAF5F3"
COR_CARD         = "#FFFFFF"
COR_BORDA        = "#E8DDD9"
COR_HOVER        = "#FEF3C7"
COR_TEXTO        = "#1C1917"
COR_TEXTO_SUB    = "#78716C"
COR_PRIMARIA     = "#C0392B"
COR_PRIM_H       = "#A93226"
COR_VERDE        = "#16A34A"
COR_VERDE_CLARO  = "#DCFCE7"
COR_AZUL         = "#2563EB"
COR_AZUL_CLARO   = "#DBEAFE"
COR_AMBER        = "#F59E0B"
COR_AMBER_CLARO  = "#FEF3C7"

CORES_AVATAR = [
    ("#7C3AED", "#EDE9FE"),
    ("#2563EB", "#DBEAFE"),
    ("#059669", "#D1FAE5"),
    ("#D97706", "#FEF3C7"),
    ("#DB2777", "#FCE7F3"),
    ("#0891B2", "#CFFAFE"),
    ("#C0392B", "#FEE2E2"),
]

W_AVATAR   = 46
W_NOME     = 180
W_TEL      = 145
W_VEICULO  = 100
W_PLACA    = 90
W_STATUS   = 90
W_ACOES    = 140


def _iniciais_entregador(nome: str) -> str:
    partes = nome.strip().split()
    return "".join(p[0].upper() for p in partes[:2] if p)


def renderizar_entregadores(frame_conteudo, janela_raiz, paleta_cores):
    controlador = EntregadorController(janela_raiz.conn)

    for w in frame_conteudo.winfo_children():
        w.destroy()

    area = ctk.CTkScrollableFrame(frame_conteudo, fg_color=COR_FUNDO,
                                   scrollbar_button_color=COR_BORDA, corner_radius=0)
    area.pack(fill="both", expand=True)

    def _atualizar_tela_entregadores():
        renderizar_entregadores(frame_conteudo, janela_raiz, paleta_cores)

    # ── CABEÇALHO ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(barra, text="Entregadores",
                 font=("Arial", 25, "bold"), text_color=COR_TEXTO).pack(side="left")
    ctk.CTkButton(
        barra, text="+ Novo Entregador",
        fg_color=COR_PRIMARIA, text_color="white", hover_color=COR_PRIM_H,
        corner_radius=10, height=40, font=("Arial", 13, "bold"),
        command=lambda: _abrir_formulario_entregador()
    ).pack(side="right")
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(fill="x", padx=28, pady=(4, 14))

    # ── CARREGAR ENTREGADORES ──────────────────────────────────────────
    try:
        lista_entregadores = controlador.listar_todos_entregadores()
    except Exception:
        lista_entregadores = []

    # ── CARDS RESUMO ──────────────────────────────────────────────────
    linha_res = ctk.CTkFrame(area, fg_color="transparent")
    linha_res.pack(fill="x", padx=28, pady=(0, 14))

    def _exibir_card_resumo(parent, titulo, valor, emoji, cor_bg, cor_val):
        c = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12,
                          border_width=1, border_color=COR_BORDA, height=80)
        c.pack(side="left", padx=(0, 12), expand=True, fill="x")
        c.pack_propagate(False)
        ib = ctk.CTkFrame(c, fg_color=cor_bg, width=36, height=36, corner_radius=8)
        ib.place(x=12, y=12)
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text=emoji, font=("Arial", 17)).pack(expand=True)
        ctk.CTkLabel(c, text=titulo, font=("Arial", 11), text_color=COR_TEXTO_SUB).place(x=56, y=12)
        ctk.CTkLabel(c, text=valor, font=("Arial", 19, "bold"), text_color=cor_val).place(x=56, y=32)

    total_entregadores    = len(lista_entregadores)
    total_ativos          = sum(1 for e in lista_entregadores if e.get("ativo", 1))
    total_inativos        = total_entregadores - total_ativos

    _exibir_card_resumo(linha_res, "Total",    str(total_entregadores), "🛵", "#FEE2E2",      COR_PRIMARIA)
    _exibir_card_resumo(linha_res, "Ativos",   str(total_ativos),       "✅", COR_VERDE_CLARO, COR_VERDE)
    _exibir_card_resumo(linha_res, "Inativos", str(total_inativos),     "⏸", COR_AMBER_CLARO, COR_AMBER)

    # ── FORMULÁRIO DE CADASTRO / EDIÇÃO DE ENTREGADOR ─────────────────
    def _abrir_formulario_entregador(dados_entregador=None):
        form = ctk.CTkToplevel(janela_raiz)
        form.title("Ficha do Entregador")
        form.geometry("440x540")
        form.attributes("-topmost", True)
        form.grab_set()
        form.configure(fg_color=COR_FUNDO)
        form.update_idletasks()
        lx = (form.winfo_screenwidth() - 440) // 2
        ly = (form.winfo_screenheight() - 540) // 2
        form.geometry(f"440x540+{lx}+{ly}")

        ctk.CTkLabel(form, text="Ficha do Entregador",
                     font=("Arial", 21, "bold"), text_color=COR_TEXTO).pack(pady=(20, 14))

        def _criar_campo_formulario(label, placeholder):
            ctk.CTkLabel(form, text=label, font=("Arial", 13),
                         text_color=COR_TEXTO_SUB, anchor="w").pack(fill="x", padx=30)
            e = ctk.CTkEntry(form, placeholder_text=placeholder, height=42, corner_radius=8,
                              border_color=COR_BORDA, fg_color="#FDFAF9", font=("Arial", 13))
            e.pack(fill="x", padx=30, pady=(2, 10))
            return e

        e_nome     = _criar_campo_formulario("Nome completo", "Ex: Carlos Souza")
        e_tel      = _criar_campo_formulario("Telefone", "(11) 99999-9999")
        e_tel.bind("<KeyRelease>", aplicar_mascara_tel)
        e_cpf      = _criar_campo_formulario("CPF", "000.000.000-00")
        e_cpf.bind("<KeyRelease>", aplicar_mascara_cpf)
        e_veiculo  = _criar_campo_formulario("Veículo", "Ex: Moto, Carro, Bicicleta")
        e_placa    = _criar_campo_formulario("Placa (se houver)", "Ex: ABC-1234")

        if dados_entregador:
            e_nome.insert(0, dados_entregador.get("nome", ""))
            e_tel.insert(0, formatar_telefone(str(dados_entregador.get("telefone", ""))))
            e_cpf.insert(0, formatar_cpf(str(dados_entregador.get("cpf", ""))))
            e_veiculo.insert(0, dados_entregador.get("veiculo", ""))
            e_placa.insert(0, dados_entregador.get("placa", ""))

        lbl_erro = ctk.CTkLabel(form, text="", font=("Arial", 12), text_color="#DC2626")
        lbl_erro.pack()

        def _salvar_dados_entregador():
            ok, msg = controlador.validar_e_salvar_entregador(
                e_nome.get(), e_tel.get(), e_cpf.get(),
                e_veiculo.get(), e_placa.get(),
                dados_entregador.get("id_entregador") if dados_entregador else None
            )
            if ok:
                form.destroy()
                _atualizar_tela_entregadores()
            else:
                lbl_erro.configure(text=msg)

        ctk.CTkButton(form, text="Salvar Entregador",
                      fg_color=COR_PRIMARIA, hover_color=COR_PRIM_H, text_color="white",
                      height=44, corner_radius=10, font=("Arial", 14, "bold"),
                      command=_salvar_dados_entregador).pack(fill="x", padx=30, pady=(4, 0))

    # ── TABELA DE ENTREGADORES ─────────────────────────────────────────
    if not lista_entregadores:
        ctk.CTkLabel(area, text="Nenhum entregador cadastrado.",
                     font=("Arial", 15), text_color=COR_TEXTO_SUB).pack(pady=40)
        return

    card_tabela = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=14,
                                border_width=1, border_color=COR_BORDA)
    card_tabela.pack(fill="x", padx=28, pady=(0, 28))

    # Cabeçalho da tabela
    cab = ctk.CTkFrame(card_tabela, fg_color="#F5F0EE", corner_radius=0, height=38)
    cab.pack(fill="x")
    cab.pack_propagate(False)

    ctk.CTkLabel(cab, text="", width=W_AVATAR,  font=("Arial", 12)).pack(side="left", padx=(14, 0))
    ctk.CTkLabel(cab, text="Nome",    width=W_NOME,    anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
    ctk.CTkLabel(cab, text="Telefone",width=W_TEL,     anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
    ctk.CTkLabel(cab, text="Veículo", width=W_VEICULO, anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
    ctk.CTkLabel(cab, text="Placa",   width=W_PLACA,   anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
    ctk.CTkLabel(cab, text="Status",  width=W_STATUS,  anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
    ctk.CTkLabel(cab, text="Ações",   width=W_ACOES,   anchor="center", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")

    ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    # Linhas de dados
    for idx, entregador in enumerate(lista_entregadores):
        cor_txt_av, cor_bg_av = CORES_AVATAR[idx % len(CORES_AVATAR)]
        iniciais  = _iniciais_entregador(entregador.get("nome", "?"))
        tel_fmt   = formatar_telefone(str(entregador.get("telefone", "")))
        ativo     = bool(entregador.get("ativo", 1))
        cor_linha = COR_CARD if idx % 2 == 0 else "#FAF5F3"

        linha = ctk.CTkFrame(card_tabela, fg_color=cor_linha, corner_radius=0, height=46)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        # Círculo com iniciais
        av = ctk.CTkFrame(linha, fg_color=cor_bg_av, width=30, height=30, corner_radius=15)
        av.pack(side="left", padx=(14, 0), pady=8)
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=iniciais, font=("Arial", 11, "bold"),
                     text_color=cor_txt_av).pack(expand=True)

        ctk.CTkLabel(linha, text=entregador.get("nome", ""),  width=W_NOME,    anchor="w",
                     font=("Arial", 13), text_color=COR_TEXTO).pack(side="left", padx=(6, 0))
        ctk.CTkLabel(linha, text=tel_fmt,                      width=W_TEL,     anchor="w",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkLabel(linha, text=entregador.get("veiculo","–"),width=W_VEICULO, anchor="w",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkLabel(linha, text=entregador.get("placa","–"),  width=W_PLACA,   anchor="w",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left")

        # Badge de status ativo/inativo
        cor_st = COR_VERDE if ativo else COR_AMBER
        bg_st  = COR_VERDE_CLARO if ativo else COR_AMBER_CLARO
        txt_st = "Ativo" if ativo else "Inativo"
        badge = ctk.CTkFrame(linha, fg_color=bg_st, corner_radius=8, width=60, height=24)
        badge.pack(side="left", pady=11)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=txt_st, font=("Arial", 11, "bold"),
                     text_color=cor_st).pack(expand=True)

        dados_ent = dict(entregador)

        ctk.CTkButton(
            linha, text="✏ Editar",
            fg_color=COR_AZUL_CLARO, text_color=COR_AZUL, hover_color="#BFDBFE",
            height=28, width=74, corner_radius=6, font=("Arial", 12), border_width=0,
            command=lambda d=dados_ent: _abrir_formulario_entregador(d)
        ).pack(side="left", padx=(6, 4))

        ctk.CTkButton(
            linha, text="🗑",
            fg_color="#FEE2E2", text_color=COR_PRIMARIA, hover_color="#FECACA",
            height=28, width=34, corner_radius=6, font=("Arial", 13), border_width=0,
            command=lambda d=dados_ent: _confirmar_exclusao_entregador(d)
        ).pack(side="left")

        if idx < len(lista_entregadores) - 1:
            ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    def _confirmar_exclusao_entregador(dados_ent):
        if messagebox.askyesno("Confirmar", f"Excluir o entregador \"{dados_ent.get('nome')}\"?"):
            controlador.excluir_entregador(dados_ent.get("id_entregador"))
            _atualizar_tela_entregadores()
