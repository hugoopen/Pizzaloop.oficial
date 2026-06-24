import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from controllers.cliente_controller import ClienteController
from utils.formatadores import (
    aplicar_mascara_tel, aplicar_mascara_cpf,
    formatar_cpf, formatar_telefone
)

COR_FUNDO       = "#FAF5F3"
COR_CARD        = "#FFFFFF"
COR_BORDA       = "#E8DDD9"
COR_TEXTO       = "#1C1917"
COR_TEXTO_SUB   = "#78716C"
COR_PRIMARIA    = "#C0392B"
COR_PRIM_H      = "#A93226"
COR_AZUL        = "#2563EB"
COR_AZUL_CLARO  = "#DBEAFE"
COR_VERDE       = "#16A34A"
COR_VERDE_CLARO = "#DCFCE7"
COR_AMBER       = "#D97706"
COR_AMBER_CLARO = "#FEF3C7"
COR_SEPARADOR   = "#F5F0EE"

CORES_AVATAR = [
    ("#7C3AED", "#EDE9FE"),
    ("#2563EB", "#DBEAFE"),
    ("#059669", "#D1FAE5"),
    ("#D97706", "#FEF3C7"),
    ("#DB2777", "#FCE7F3"),
    ("#0891B2", "#CFFAFE"),
    ("#C0392B", "#FEE2E2"),
]

LIMIAR_VIP = 3  # pedidos necessários para badge VIP


def _iniciais(nome: str) -> str:
    partes = nome.strip().split()
    return "".join(p[0].upper() for p in partes[:2] if p)


def _fmt_moeda(valor) -> str:
    try:
        return (f"R$ {float(valor):,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", "."))
    except Exception:
        return "R$ 0,00"


def _fmt_data(data_obj) -> str:
    if data_obj is None:
        return "—"
    try:
        return data_obj.strftime("%d/%m/%Y")
    except Exception:
        return str(data_obj)


def renderizar_clientes(frame_conteudo, janela_raiz, paleta_cores):
    controlador = ClienteController(janela_raiz.conn)

    for w in frame_conteudo.winfo_children():
        w.destroy()

    area = ctk.CTkScrollableFrame(
        frame_conteudo, fg_color=COR_FUNDO,
        scrollbar_button_color=COR_BORDA, corner_radius=0
    )
    area.pack(fill="both", expand=True)

    def _atualizar():
        renderizar_clientes(frame_conteudo, janela_raiz, paleta_cores)

    # ── CABEÇALHO ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(
        barra, text="Clientes",
        font=("Arial", 25, "bold"), text_color=COR_TEXTO
    ).pack(side="left")
    ctk.CTkButton(
        barra, text="+ Novo Cliente",
        fg_color=COR_PRIMARIA, text_color="white", hover_color=COR_PRIM_H,
        corner_radius=10, height=40, font=("Arial", 13, "bold"),
        command=lambda: _abrir_formulario_cliente()
    ).pack(side="right")
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(
        fill="x", padx=28, pady=(4, 16)
    )

    # ── CARREGAR CLIENTES COM ESTATÍSTICAS ────────────────────────────
    try:
        lista = controlador.listar_clientes_com_estatisticas()
    except Exception:
        try:
            lista = controlador.listar_clientes()
        except Exception:
            lista = []

    # ── CARDS KPI DE RESUMO ───────────────────────────────────────────
    total      = len(lista)
    total_vip  = sum(1 for c in lista if (c.get("total_pedidos") or 0) >= LIMIAR_VIP)

    linha_kpi = ctk.CTkFrame(area, fg_color="transparent")
    linha_kpi.pack(fill="x", padx=28, pady=(0, 18))

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

    _kpi(linha_kpi, "Total Clientes", total,     "👥", COR_AZUL_CLARO,  COR_AZUL)
    _kpi(linha_kpi, "Clientes VIP",   total_vip, "⭐", COR_AMBER_CLARO, COR_AMBER)
    _kpi(linha_kpi, "Novos (mês)",    "–",       "🆕", COR_VERDE_CLARO, COR_VERDE)

    # ── FORMULÁRIO DE CADASTRO / EDIÇÃO ───────────────────────────────
    def _abrir_formulario_cliente(dados_cliente=None):
        eh_edicao = dados_cliente is not None

        form = ctk.CTkToplevel(janela_raiz)
        form.title("Editar Cliente" if eh_edicao else "Novo Cliente")
        form.geometry("460x780")
        form.attributes("-topmost", True)
        form.grab_set()
        form.focus_force()
        form.update_idletasks()
        lx = (form.winfo_screenwidth()  - 460) // 2
        ly = (form.winfo_screenheight() - 780) // 2
        form.geometry(f"460x780+{lx}+{ly}")

        ctk.CTkLabel(
            form,
            text="Editar Cliente" if eh_edicao else "Novo Cliente",
            font=("Arial", 20, "bold"),
        ).pack(pady=20)

        corpo = ctk.CTkScrollableFrame(form, fg_color="transparent",
                                       scrollbar_button_color=COR_BORDA, corner_radius=0)
        corpo.pack(fill="both", expand=True)

        def _campo(label, placeholder, parent=corpo):
            ctk.CTkLabel(parent, text=label,
                         font=("Arial", 12, "bold"), anchor="w").pack(anchor="w", padx=50)
            e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                             width=320, height=40)
            e.pack(pady=(2, 8))
            return e

        e_nome  = _campo("Nome completo *", "João Silva")
        e_email = _campo("E-mail", "joao@email.com")
        e_tel   = _campo("Telefone", "(11) 99999-9999")
        e_tel.bind("<KeyRelease>", aplicar_mascara_tel)
        e_cpf   = _campo("CPF *", "000.000.000-00")
        e_cpf.bind("<KeyRelease>", aplicar_mascara_cpf)
        
        e_cep      = _campo("CEP *", "00000-000")
        e_endereco = _campo("Logradouro", "Rua das Flores")

        # ── MÁSCARA AUTOMÁTICA EM TEMPO REAL PARA O CEP ───────────────────
        def aplicar_mascara_cep(event):
            # Ignora teclas de controle como Backspace, Tab, Setas, etc.
            if event.keysym in ("Backspace", "Delete", "Tab", "Left", "Right", "Up", "Down"):
                return

            conteudo = e_cep.get()
            # Remove qualquer caractere que não seja número
            apenas_numeros = "".join(c for c in conteudo if c.isdigit())
            
            # Limita a 8 números (que viram 9 caracteres com o "-")
            apenas_numeros = apenas_numeros[:8]

            # Monta o formato 00000-000 dinamicamente
            if len(apenas_numeros) > 5:
                cep_formatado = f"{apenas_numeros[:5]}-{apenas_numeros[5:]}"
            else:
                cep_formatado = apenas_numeros

            # Atualiza o campo mantendo o cursor no final
            e_cep.delete(0, "end")
            e_cep.insert(0, cep_formatado)

        e_cep.bind("<KeyRelease>", aplicar_mascara_cep)

        linha_num_bai = ctk.CTkFrame(corpo, fg_color="transparent")
        linha_num_bai.pack(pady=(0, 8))

        ctk.CTkLabel(linha_num_bai, text="Número",
                     font=("Arial", 12, "bold"), anchor="w", width=110).grid(
            row=0, column=0, sticky="w")
        ctk.CTkLabel(linha_num_bai, text="Bairro",
                     font=("Arial", 12, "bold"), anchor="w").grid(
            row=0, column=1, sticky="w", padx=(10, 0))

        e_numero = ctk.CTkEntry(linha_num_bai, placeholder_text="Ex: 123",
                                height=40, width=110)
        e_numero.grid(row=1, column=0, sticky="ew")
        e_bairro = ctk.CTkEntry(linha_num_bai, placeholder_text="Ex: Centro",
                                height=40, width=195)
        e_bairro.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        e_cidade = _campo("Cidade", "Ex: São Paulo")

        if dados_cliente:
            e_nome.insert(0,     dados_cliente.get("nome", ""))
            e_email.insert(0,    dados_cliente.get("email", "") or "")
            e_tel.insert(0,      formatar_telefone(str(dados_cliente.get("telefone", ""))))
            e_cpf.insert(0,      formatar_cpf(str(dados_cliente.get("cpf", ""))))
            e_cep.insert(0,      dados_cliente.get("cep", "") or "")
            e_endereco.insert(0, dados_cliente.get("endereco", "") or "")
            e_numero.insert(0,   dados_cliente.get("numero", "") or "")
            e_bairro.insert(0,   dados_cliente.get("bairro", "") or "")
            e_cidade.insert(0,   dados_cliente.get("cidade", "") or "")

        lbl_erro = ctk.CTkLabel(corpo, text="", font=("Arial", 12), text_color="#DC2626")
        lbl_erro.pack(pady=(4, 0))

        def _salvar():
            cep = e_cep.get().strip()

            if not cep:
                lbl_erro.configure(text="O campo CEP é obrigatório!")
                e_cep.focus_set()
                return
            elif len(cep) != 9 or "-" not in cep:
                lbl_erro.configure(text="CEP inválido! Use o formato 00000-000.")
                e_cep.focus_set()
                return

            ok, msg = controlador.validar_e_salvar(
                e_nome.get(), e_tel.get(), e_cpf.get(),
                e_email.get(),
                cep, e_endereco.get(),
                e_numero.get(), e_bairro.get(), e_cidade.get(),
                dados_cliente.get("id_cliente") if dados_cliente else None
            )
            if ok:
                form.destroy()
                _atualizar()
            else:
                lbl_erro.configure(text=msg)

        ctk.CTkButton(
            form,
            text="💾 Salvar",
            fg_color=COR_PRIMARIA,
            hover_color=COR_PRIM_H,
            text_color="white",
            width=220,
            height=42,
            corner_radius=10,
            font=("Arial", 12, "bold"),
            command=_salvar,
        ).pack(pady=20)

    # ── GRADE DE CARDS DE CLIENTE ─────────────────────────────────────
    if not lista:
        ctk.CTkLabel(area, text="Nenhum cliente cadastrado.",
                     font=("Arial", 15), text_color=COR_TEXTO_SUB).pack(pady=40)
        return

    def _construir_card(linha_frame, col, idx, cli):
        cor_txt_av, cor_bg_av = CORES_AVATAR[idx % len(CORES_AVATAR)]
        iniciais  = _iniciais(cli.get("nome", "?"))
        tel       = formatar_telefone(str(cli.get("telefone", "") or ""))
        email_val = cli.get("email", "") or ""
        endereco  = cli.get("endereco", "") or ""
        numero    = cli.get("numero", "") or ""
        bairro    = cli.get("bairro", "") or ""
        cidade    = cli.get("cidade", "") or ""

        partes_end = []
        if endereco:
            partes_end.append(f"{endereco}{', ' + numero if numero else ''}")
        if bairro:
            partes_end.append(bairro)
        if cidade:
            partes_end.append(cidade)
        end_fmt = " – ".join(partes_end) if partes_end else "—"
        if len(end_fmt) > 38:
            end_fmt = end_fmt[:35] + "..."

        total_ped = cli.get("total_pedidos", 0) or 0
        total_gst = cli.get("total_gasto", 0) or 0
        ult_ped   = _fmt_data(cli.get("ultimo_pedido"))
        eh_vip    = int(total_ped) >= LIMIAR_VIP
        dados_cli = dict(cli)

        pad_x = (0, 7) if col == 0 else (7, 0)
        card = ctk.CTkFrame(linha_frame, fg_color=COR_CARD, corner_radius=12,
                             border_width=1, border_color=COR_BORDA)
        card.grid(row=0, column=col, sticky="ew", padx=pad_x)

        # ── Popup menu do ⋮ ──────────────────────────────────────────
        def _popup(evt, d=dados_cli):
            m = tk.Menu(janela_raiz, tearoff=0, font=("Arial", 13))
            m.add_command(label="✏  Editar",  command=lambda: _abrir_formulario_cliente(d))
            m.add_command(label="🗑  Excluir", command=lambda: _confirmar_exclusao(d))
            try:
                m.tk_popup(evt.x_root, evt.y_root)
            finally:
                m.grab_release()

        # Cabeçalho
        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=14, pady=(10, 0))

        av = ctk.CTkFrame(cab, fg_color=cor_bg_av, width=40, height=40, corner_radius=20)
        av.pack(side="left")
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=iniciais, font=("Arial", 14, "bold"),
                     text_color=cor_txt_av).pack(expand=True)

        info_nome = ctk.CTkFrame(cab, fg_color="transparent")
        info_nome.pack(side="left", padx=(10, 0), fill="x", expand=True)
        ctk.CTkLabel(info_nome, text=cli.get("nome", ""), anchor="w",
                     font=("Arial", 14, "bold"), text_color=COR_TEXTO).pack(anchor="w")

        if eh_vip:
            ctk.CTkLabel(info_nome, text="VIP", anchor="w",
                         font=("Arial", 11), text_color=COR_AMBER).pack(anchor="w")
        else:
            ctk.CTkLabel(info_nome, text="Regular", anchor="w",
                         font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(anchor="w")

        btn_menu = ctk.CTkButton(
            cab, text="⋮",
            fg_color="transparent", text_color=COR_TEXTO_SUB,
            hover_color=COR_SEPARADOR, width=26, height=26,
            corner_radius=6, font=("Arial", 16), border_width=0,
            command=None
        )
        btn_menu.pack(side="right")
        btn_menu.bind("<Button-1>", _popup)

        # Contato
        contato = ctk.CTkFrame(card, fg_color="transparent")
        contato.pack(fill="x", padx=14, pady=(6, 6))

        def _linha_contato(icone, texto):
            if not texto or texto == "—":
                return
            fr = ctk.CTkFrame(contato, fg_color="transparent")
            fr.pack(fill="x", pady=1)
            ctk.CTkLabel(fr, text=icone, font=("Arial", 12),
                         text_color=COR_TEXTO_SUB, width=18).pack(side="left")
            ctk.CTkLabel(fr, text=texto, font=("Arial", 13),
                         text_color=COR_TEXTO_SUB, anchor="w").pack(side="left", padx=(4, 0))

        _linha_contato("✉", email_val or None)
        _linha_contato("📞", tel or None)
        _linha_contato("📍", end_fmt if end_fmt != "—" else None)

        if not email_val and not tel and end_fmt == "—":
            ctk.CTkLabel(contato, text="Sem contato cadastrado",
                         font=("Arial", 12), text_color=COR_BORDA).pack(anchor="w")

        # Stats
        ctk.CTkFrame(card, height=1, fg_color=COR_BORDA).pack(fill="x")

        stats = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
        stats.pack(fill="x", pady=(6, 8))
        for sc in range(5):
            stats.columnconfigure(sc, weight=1 if sc % 2 == 0 else 0)

        def _stat_col(sc, titulo, valor, cor_val=COR_TEXTO):
            fr = ctk.CTkFrame(stats, fg_color="transparent")
            fr.grid(row=0, column=sc, sticky="ew", padx=6)
            ctk.CTkLabel(fr, text=titulo, font=("Arial", 11),
                         text_color=COR_TEXTO_SUB).pack(anchor="w")
            ctk.CTkLabel(fr, text=str(valor), font=("Arial", 14, "bold"),
                         text_color=cor_val).pack(anchor="w")

        _stat_col(0, "Total Pedidos", str(total_ped))
        ctk.CTkFrame(stats, width=1, fg_color=COR_BORDA).grid(row=0, column=1, sticky="ns", pady=2)
        _stat_col(2, "Total Gasto", _fmt_moeda(total_gst), COR_PRIMARIA)
        ctk.CTkFrame(stats, width=1, fg_color=COR_BORDA).grid(row=0, column=3, sticky="ns", pady=2)
        _stat_col(4, "Último Pedido", ult_ped)

    for i in range(0, len(lista), 2):
        linha_frame = ctk.CTkFrame(area, fg_color="transparent")
        linha_frame.pack(fill="x", padx=28, pady=(0, 14))
        linha_frame.columnconfigure(0, weight=1)
        linha_frame.columnconfigure(1, weight=1)
        _construir_card(linha_frame, 0, i, lista[i])
        if i + 1 < len(lista):
            _construir_card(linha_frame, 1, i + 1, lista[i + 1])

    def _confirmar_exclusao(dados_cli):
        if messagebox.askyesno("Confirmar",
                                f"Excluir o cliente \"{dados_cli.get('nome')}\"?"):
            controlador.excluir(dados_cli.get("id_cliente"))
            _atualizar()