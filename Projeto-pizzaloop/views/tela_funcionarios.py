# ========================================================
# VIEW: GERENCIAR FUNCIONÁRIOS (somente Admin)
# Permite ao administrador cadastrar sócios, funcionários
# e entregadores, escolher o cargo de cada um e ativar ou
# desativar contas sem perder o histórico.
# ========================================================

import customtkinter as ctk
from tkinter import messagebox
from controllers.funcionario_controller import FuncionarioController
from services.permissao_service import CARGOS_VALIDOS, eh_admin

COR_FUNDO     = "#FAF5F3"
COR_CARD      = "#FFFFFF"
COR_BORDA     = "#E8DDD9"
COR_TEXTO     = "#1C1917"
COR_TEXTO_SUB = "#78716C"
COR_PRIMARIA  = "#C0392B"
COR_PRIM_H    = "#A93226"
COR_VERDE     = "#16A34A"
COR_VERDE_CLARO = "#DCFCE7"
COR_CINZA_CLARO = "#F1F5F9"

NOMES_CARGO = {
    "admin": "Administrador",
    "socio": "Sócio",
    "funcionario": "Funcionário",
    "entregador": "Entregador",
}


def renderizar_funcionarios(frame_conteudo, janela_raiz, paleta_cores):
    usuario_logado = getattr(janela_raiz, "usuario_logado", None)

    for w in frame_conteudo.winfo_children():
        w.destroy()

    # Defesa extra: mesmo que a navegação já tenha sido bloqueada antes de
    # chegar aqui, a tela nunca deve renderizar dados para quem não é admin.
    if not eh_admin(usuario_logado):
        ctk.CTkLabel(
            frame_conteudo, text="🔒 Acesso restrito ao administrador.",
            font=("Arial", 16, "bold"), text_color=COR_PRIMARIA
        ).pack(pady=60)
        return

    controlador = FuncionarioController(janela_raiz.conn, usuario_logado)

    area = ctk.CTkScrollableFrame(
        frame_conteudo, fg_color=COR_FUNDO,
        scrollbar_button_color=COR_BORDA, corner_radius=0
    )
    area.pack(fill="both", expand=True)

    def _atualizar():
        renderizar_funcionarios(frame_conteudo, janela_raiz, paleta_cores)

    # ── CABEÇALHO ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(
        barra, text="Gerenciar Funcionários",
        font=("Arial", 25, "bold"), text_color=COR_TEXTO
    ).pack(side="left")
    ctk.CTkButton(
        barra, text="+ Novo Funcionário",
        fg_color=COR_PRIMARIA, text_color="white", hover_color=COR_PRIM_H,
        corner_radius=10, height=40, font=("Arial", 13, "bold"),
        command=lambda: _abrir_formulario()
    ).pack(side="right")
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(fill="x", padx=28, pady=(4, 14))

    ctk.CTkLabel(
        area,
        text="Defina o cargo de cada pessoa: isso controla o que ela pode ver e alterar no sistema.",
        font=("Arial", 12), text_color=COR_TEXTO_SUB
    ).pack(anchor="w", padx=28, pady=(0, 14))

    # ── EDITAR NOME ───────────────────────────────────────────────────
    def _abrir_editor_nome(email, nome_atual):
        popup = ctk.CTkToplevel(janela_raiz)
        popup.title("Editar Nome")
        popup.geometry("360x200")
        popup.attributes("-topmost", True)
        popup.grab_set()
        popup.focus_force()
        popup.update_idletasks()
        lx = (popup.winfo_screenwidth() - 360) // 2
        ly = (popup.winfo_screenheight() - 200) // 2
        popup.geometry(f"360x200+{lx}+{ly}")

        ctk.CTkLabel(popup, text="Editar Nome", font=("Arial", 17, "bold")).pack(pady=(20, 4))
        ctk.CTkLabel(popup, text=email, font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(pady=(0, 14))

        e_nome = ctk.CTkEntry(popup, width=280, height=38)
        e_nome.insert(0, nome_atual)
        e_nome.pack(pady=(0, 6))
        e_nome.focus()

        lbl_erro = ctk.CTkLabel(popup, text="", font=("Arial", 11), text_color="#DC2626")
        lbl_erro.pack()

        def _salvar_nome():
            ok, msg = controlador.alterar_nome(email, e_nome.get())
            if ok:
                popup.destroy()
                _atualizar()
            else:
                lbl_erro.configure(text=msg)

        e_nome.bind("<Return>", lambda _e: _salvar_nome())

        ctk.CTkButton(
            popup, text="💾 Salvar", fg_color=COR_PRIMARIA, hover_color=COR_PRIM_H,
            text_color="white", width=160, height=38, corner_radius=8,
            font=("Arial", 12, "bold"), command=_salvar_nome,
        ).pack(pady=10)

    # ── FORMULÁRIO DE CADASTRO ─────────────────────────────────────────
    def _abrir_formulario():
        form = ctk.CTkToplevel(janela_raiz)
        form.title("Novo Funcionário")
        form.geometry("420x480")
        form.attributes("-topmost", True)
        form.grab_set()
        form.focus_force()
        form.update_idletasks()
        lx = (form.winfo_screenwidth() - 420) // 2
        ly = (form.winfo_screenheight() - 480) // 2
        form.geometry(f"420x480+{lx}+{ly}")

        ctk.CTkLabel(form, text="Novo Funcionário", font=("Arial", 19, "bold")).pack(pady=(20, 14))

        corpo = ctk.CTkFrame(form, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=10)

        def _campo(label, placeholder, show=None):
            ctk.CTkLabel(corpo, text=label, font=("Arial", 12, "bold"), anchor="w").pack(anchor="w", padx=40)
            e = ctk.CTkEntry(corpo, placeholder_text=placeholder, width=320, height=38, show=show)
            e.pack(pady=(2, 12))
            return e

        e_nome = _campo("Nome completo *", "Ex: João Silva")
        e_email = _campo("E-mail (login) *", "Ex: joao@pizzaloop.com")
        e_senha = _campo("Senha provisória *", "Mínimo 6 caracteres", show="*")

        ctk.CTkLabel(corpo, text="Cargo *", font=("Arial", 12, "bold"), anchor="w").pack(anchor="w", padx=40)
        combo_cargo = ctk.CTkComboBox(
            corpo, values=[NOMES_CARGO[c] for c in CARGOS_VALIDOS], width=320, height=38
        )
        combo_cargo.set(NOMES_CARGO["funcionario"])
        combo_cargo.pack(pady=(2, 14))

        lbl_erro = ctk.CTkLabel(corpo, text="", font=("Arial", 12), text_color="#DC2626")
        lbl_erro.pack(pady=(0, 4))

        def _salvar():
            cargo_chave = next(
                (k for k, v in NOMES_CARGO.items() if v == combo_cargo.get()), "funcionario"
            )
            ok, msg = controlador.cadastrar(e_nome.get(), e_email.get(), e_senha.get(), cargo_chave)
            if ok:
                form.destroy()
                _atualizar()
            else:
                lbl_erro.configure(text=msg)

        ctk.CTkButton(
            form, text="💾 Cadastrar", fg_color=COR_PRIMARIA, hover_color=COR_PRIM_H,
            text_color="white", width=220, height=42, corner_radius=10,
            font=("Arial", 12, "bold"), command=_salvar,
        ).pack(pady=10)

    # ── LISTA DE FUNCIONÁRIOS ────────────────────────────────────────
    try:
        usuarios = controlador.listar()
    except Exception:
        usuarios = []

    card_tabela = ctk.CTkFrame(area, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
    card_tabela.pack(fill="x", padx=28, pady=(0, 28))

    cab = ctk.CTkFrame(card_tabela, fg_color="#F5F0EE", height=38)
    cab.pack(fill="x")
    cab.pack_propagate(False)

    def _cab(t, w, anc="w"):
        ctk.CTkLabel(cab, text=t, width=w, anchor=anc, font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left", padx=(0, 4))

    ctk.CTkLabel(cab, text="", width=14).pack(side="left")
    _cab("Nome", 200)
    _cab("E-mail", 220)
    _cab("Cargo", 150, "center")
    _cab("Situação", 90, "center")
    _cab("Ações", 140, "center")

    ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")

    if not usuarios:
        ctk.CTkLabel(card_tabela, text="Nenhum usuário cadastrado ainda.", text_color=COR_TEXTO_SUB).pack(pady=24)

    for idx, u in enumerate(usuarios):
        cor_linha = COR_CARD if idx % 2 == 0 else "#FAF5F3"
        linha = ctk.CTkFrame(card_tabela, fg_color=cor_linha, height=48)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkLabel(linha, text="", width=14).pack(side="left")
        celula_nome = ctk.CTkFrame(linha, fg_color="transparent", width=200, height=48)
        celula_nome.pack(side="left")
        celula_nome.pack_propagate(False)

        lbl_nome = ctk.CTkLabel(celula_nome, text=u.get("nome") or "—", anchor="w",
                                 font=("Arial", 13, "bold"), text_color=COR_TEXTO)
        lbl_nome.place(x=0, rely=0.5, anchor="w")

        def _editar_nome(email=u.get("email"), nome_atual=u.get("nome") or ""):
            _abrir_editor_nome(email, nome_atual)

        ctk.CTkButton(
            celula_nome, text="✏", width=22, height=22, corner_radius=6,
            fg_color="transparent", text_color=COR_TEXTO_SUB, hover_color=COR_CINZA_CLARO,
            font=("Arial", 12), border_width=0, command=_editar_nome,
        ).place(x=168, rely=0.5, anchor="w")
        ctk.CTkLabel(linha, text=u.get("email", ""), width=220, anchor="w",
                     font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="left")

        celula_cargo = ctk.CTkFrame(linha, fg_color="transparent", width=150, height=48)
        celula_cargo.pack(side="left")
        celula_cargo.pack_propagate(False)
        combo_linha = ctk.CTkComboBox(
            celula_cargo, values=[NOMES_CARGO[c] for c in CARGOS_VALIDOS],
            width=130, height=30, font=("Arial", 11)
        )
        combo_linha.set(NOMES_CARGO.get(u.get("cargo"), "Funcionário"))
        combo_linha.place(relx=0.5, rely=0.5, anchor="center")

        def _trocar_cargo(email=u.get("email"), combo=combo_linha):
            cargo_chave = next((k for k, v in NOMES_CARGO.items() if v == combo.get()), "funcionario")
            ok, msg = controlador.alterar_cargo(email, cargo_chave)
            if not ok:
                messagebox.showerror("Erro", msg)
            _atualizar()

        combo_linha.configure(command=lambda _e, f=_trocar_cargo: f())

        ativo = bool(u.get("ativo", 1))
        celula_status = ctk.CTkFrame(linha, fg_color="transparent", width=90, height=48)
        celula_status.pack(side="left")
        celula_status.pack_propagate(False)
        badge = ctk.CTkFrame(celula_status, fg_color=COR_VERDE_CLARO if ativo else "#FEE2E2",
                              corner_radius=8, width=74, height=24)
        badge.place(relx=0.5, rely=0.5, anchor="center")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="Ativo" if ativo else "Inativo", font=("Arial", 11, "bold"),
                     text_color=COR_VERDE if ativo else COR_PRIMARIA).pack(expand=True)

        celula_acoes = ctk.CTkFrame(linha, fg_color="transparent", width=140, height=48)
        celula_acoes.pack(side="left")
        celula_acoes.pack_propagate(False)

        def _alternar(email=u.get("email"), ativar=not ativo):
            ok, msg = controlador.alternar_situacao(email, ativar)
            if not ok:
                messagebox.showerror("Erro", msg)
            _atualizar()

        ctk.CTkButton(
            celula_acoes, text="Desativar" if ativo else "Ativar",
            fg_color="#FEE2E2" if ativo else COR_VERDE_CLARO,
            text_color=COR_PRIMARIA if ativo else COR_VERDE,
            hover_color="#FECACA" if ativo else "#BBF7D0",
            height=28, width=110, corner_radius=6, font=("Arial", 11, "bold"), border_width=0,
            command=_alternar
        ).place(relx=0.5, rely=0.5, anchor="center")

        if idx < len(usuarios) - 1:
            ctk.CTkFrame(card_tabela, height=1, fg_color=COR_BORDA).pack(fill="x")
