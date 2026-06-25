# ========================================================
# VIEW DE LOGIN - PIZZALOOP (VERSÃO ULTRA PROFISSIONAL)
# ========================================================

import os
import threading
import re
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from controllers.login_controller import LoginController


def email_e_valido(email):
    """
    Verifica se o e-mail digitado segue um padrão seguro e moderno.
    """
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email.strip()))


def renderizar_login(root, callback_sucesso):
    """
    Renderiza a interface gráfica de login e cadastro do PizzaLoop.
    """
    # 1️⃣ Força o sistema a carregar os dados da janela antes de redimensionar
    root.update_idletasks()
    
    # 2️⃣ Pega a largura e altura exatas da tela do seu notebook
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    
    # 3️⃣ Força a janela a ter o tamanho total do monitor iniciando do canto (0,0)
    root.geometry(f"{largura_tela}x{altura_tela}+0+0")
    
    # 4️⃣ Tenta aplicar o modo imersivo (se o sistema operacional permitir)
    try:
        root.attributes('-fullscreen', True)
    except Exception:
        # Se falhar ou estiver no Mac/Linux, ativa o modo maximizado normal
        root.state('zoomed')

    # Inicializa o controlador passando a conexão ativa do banco de dados
    regras = LoginController(root.conn)
    # ... resto do seu código igual
    
    # ========================================================
    # PALETA DE CORES PROFISSIONAL (PIZZALOOP)
    # ========================================================
    DARK     = "#0d1b2a"  # Cor do painel esquerdo (onde fica a logo)
    ORANGE   = "#ff6b00"  # Cor dos botões principais e links
    ORANGE_H = "#e55f00"  # Hover do botão principal
    LIGHT_BG = "#f5f6f8"  # Fundo geral da janela (lado direito)
    CARD     = "#ffffff"  # Fundo do bloco branco de login
    TEXT     = "#1e293b"  # Texto principal escuro
    TEXT_S   = "#64748b"  # Texto secundário/cinza
    BORDER   = "#e2e8f0"  # Cor das bordas dos inputs

    # ========================================================
    # FRAME ESQUERDO (SIDEBAR ESCURA)
    # ========================================================
    frame_lateral = ctk.CTkFrame(root, width=350, fg_color=DARK, corner_radius=0)
    frame_lateral.pack(side="left", fill="y")
    frame_lateral.pack_propagate(False)

    # Mapeamento dinâmico do caminho da imagem
    pasta_views = os.path.dirname(os.path.abspath(__file__))
    caminho_logo = os.path.join(pasta_views, "..", "assets", "logo_pizzaloop.png")

    try:
        imagem_crua = Image.open(caminho_logo)
        imagem_convertida = imagem_crua.convert("RGBA")
        
        imagem_logo = ctk.CTkImage(
            light_image=imagem_convertida,
            dark_image=imagem_convertida,
            size=(220, 220)
        )
        
        lbl_logo = ctk.CTkLabel(frame_lateral, image=imagem_logo, text="")
        lbl_logo.place(relx=0.5, rely=0.28, anchor="center")
        
    except Exception as e:
        ctk.CTkLabel(frame_lateral, text="🍕", font=("Arial", 61)).place(relx=0.5, rely=0.25, anchor="center")
        ctk.CTkLabel(
            frame_lateral,
            text="Pizzaloop",
            font=("Arial", 29, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.31, anchor="center")

    container_textos = ctk.CTkFrame(frame_lateral, fg_color="transparent")
    container_textos.place(relx=0.5, rely=0.60, anchor="center")

    lbl_titulo_sistema = ctk.CTkLabel(
        container_textos,
        text="Sistema de Gestão\nPizzaria Desktop",
        font=("Arial", 17, "bold"),
        text_color="#94a3b8"
    )
    lbl_titulo_sistema.pack(pady=(0, 12))

    lbl_descricao_sistema = ctk.CTkLabel(
        container_textos,
        text="Controle total de clientes,\npedidos e produtos.",
        font=("Arial", 14),
        text_color="#64748b"
    )
    lbl_descricao_sistema.pack(pady=(0, 25))

    lbl_versao = ctk.CTkLabel(
        container_textos,
        text="Pizzaloop v1.0",
        font=("Arial", 12),
        text_color="#64748b"
    )
    lbl_versao.pack(side="bottom", pady=(0, 20))

    # ========================================================
    # FRAME DIREITO (ÁREA DE LOGIN E FORMULÁRIOS)
    # ========================================================
    frame_principal = ctk.CTkFrame(root, fg_color=LIGHT_BG, corner_radius=0)
    frame_principal.pack(side="right", fill="both", expand=True)

    card = ctk.CTkFrame(
        frame_principal,
        width=430,
        height=540,  # Ligeiramente maior para acomodar melhor os elementos
        fg_color=CARD,
        corner_radius=18,
        border_width=1,
        border_color=BORDER
    )
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    ctk.CTkLabel(card, text="Bem-vindo 👋", font=("Arial", 27, "bold"), text_color=TEXT).pack(pady=(40, 5))
    ctk.CTkLabel(card, text="Entrar na sua conta", font=("Arial", 13), text_color=TEXT_S).pack(pady=(0, 30))

    # INPUT: EMAIL
    ctk.CTkLabel(card, text="Email", font=("Arial", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=70)
    ent_email = ctk.CTkEntry(
        card, placeholder_text="Digite seu email", width=290, height=45, 
        corner_radius=10, border_color=BORDER, fg_color="#f8fafc"
    )
    ent_email.pack(pady=(6, 18))
    ent_email.focus()

    # INPUT: SENHA
    ctk.CTkLabel(card, text="Senha", font=("Arial", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=70)
    
    frame_senha = ctk.CTkFrame(card, fg_color="transparent")
    frame_senha.pack(pady=(5, 10))

    ent_senha = ctk.CTkEntry(
        frame_senha, placeholder_text="Digite sua senha", show="*",
        width=245, height=45, corner_radius=10, border_color=BORDER, fg_color="#f8fafc"
    )
    ent_senha.pack(side="left")

    def toggle_senha():
        if ent_senha.cget("show") == "*":
            ent_senha.configure(show="")
            btn_olho.configure(text="🙈")
        else:
            ent_senha.configure(show="*")
            btn_olho.configure(text="👁")

    btn_olho = ctk.CTkButton(
        frame_senha, text="👁", width=40, height=45,
        fg_color="#edf2f7", hover_color="#dce3ea", text_color="black",
        command=toggle_senha
    )
    btn_olho.pack(side="left", padx=(6, 0))

    # PROCESSAMENTO
    def processar_autenticacao(email, senha):
        sucesso, msg, usuario_logado = regras.autenticar(email, senha)
        root.after(0, lambda: finalizar_login(sucesso, msg, usuario_logado))

    def finalizar_login(sucesso, msg, usuario_logado=None):
        btn_entrar.configure(text="Entrar", state="normal")
        if sucesso:
            ent_email.unbind("<Return>")
            ent_senha.unbind("<Return>")
            callback_sucesso(usuario_logado)
        else:
            messagebox.showerror("Erro de Autenticação", msg)

    def tentar_entrar():
        email_digitado = ent_email.get().strip()
        senha_digitada = ent_senha.get()

        if not email_digitado or not senha_digitada:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha o email e a senha para continuar.")
            return

        if not email_e_valido(email_digitado):
            messagebox.showerror("E-mail Inválido", "O formato do e-mail digitado está incorreto.\nExemplo: nome@empresa.com")
            return

        btn_entrar.configure(text="Carregando...", state="disabled")

        threading.Thread(
            target=processar_autenticacao, 
            args=(email_digitado, senha_digitada), 
            daemon=True
        ).start()

    # BOTÃO ENTRAR
    btn_entrar = ctk.CTkButton(
        card, text="Entrar", width=290, height=48,
        fg_color=ORANGE, hover_color=ORANGE_H, corner_radius=10,
        font=("Arial", 15, "bold"), command=tentar_entrar
    )
    btn_entrar.pack(pady=20)

    ent_email.bind("<Return>", lambda e: tentar_entrar())
    ent_senha.bind("<Return>", lambda e: tentar_entrar())

    # SEÇÃO DE LINKS INTERATIVOS
    link_criar = ctk.CTkLabel(card, text="Criar uma nova conta", cursor="hand2", text_color=ORANGE, font=("Arial", 13, "bold"))
    link_criar.pack(pady=(5, 5))
    
    # Efeitos de Hover para o link de cadastro
    link_criar.bind("<Enter>", lambda e: link_criar.configure(text_color=ORANGE_H, font=("Arial", 13, "bold", "underline")))
    link_criar.bind("<Leave>", lambda e: link_criar.configure(text_color=ORANGE, font=("Arial", 13, "bold")))
    link_criar.bind("<Button-1>", lambda e: abrir_cadastro())

    ctk.CTkLabel(
        card, text="Esqueceu sua senha? Contate o administrador.",
        font=("Arial", 12), text_color=TEXT_S
    ).pack(pady=(5, 0))

    # ========================================================
    # JANELA AUXILIAR: CADASTRO DE NOVOS USUÁRIOS
    # ========================================================
    def abrir_cadastro():
        janela = ctk.CTkToplevel(root)
        janela.geometry("420x420")
        janela.title("Criar Nova Conta")
        janela.attributes("-topmost", True)
        janela.resizable(False, False)
        janela.configure(fg_color=CARD)

        janela.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() // 2) - 210
        y = root.winfo_y() + (root.winfo_height() // 2) - 210
        janela.geometry(f"420x420+{x}+{y}")

        # Atalho para fechar no ESC
        janela.bind("<Escape>", lambda e: janela.destroy())

        ctk.CTkLabel(janela, text="Criar Conta", font=("Arial", 23, "bold"), text_color=TEXT).pack(pady=(25, 20))

        # Campo Email
        ctk.CTkLabel(janela, text="Email Institucional", font=("Arial", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=60)
        campo_email = ctk.CTkEntry(janela, placeholder_text="exemplo@pizzaloop.com", width=300, height=40, border_color=BORDER)
        campo_email.pack(pady=(4, 14))
        campo_email.focus()

        # Campo Senha
        ctk.CTkLabel(janela, text="Senha de Acesso", font=("Arial", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=60)
        campo_senha = ctk.CTkEntry(janela, placeholder_text="Mínimo 6 caracteres", width=300, height=40, show="*", border_color=BORDER)
        campo_senha.pack(pady=(4, 14))

        # Campo Confirmar Senha
        ctk.CTkLabel(janela, text="Confirmar Senha", font=("Arial", 13, "bold"), text_color=TEXT).pack(anchor="w", padx=60)
        campo_confirmar = ctk.CTkEntry(janela, placeholder_text="Repita a senha", width=300, height=40, show="*", border_color=BORDER)
        campo_confirmar.pack(pady=(4, 25))

        # Navegação por teclado inteligente (Enter pula campos)
        campo_email.bind("<Return>", lambda e: campo_senha.focus())
        campo_senha.bind("<Return>", lambda e: campo_confirmar.focus())
        campo_confirmar.bind("<Return>", lambda e: salvar())

        def processar_cadastro(email, senha):
            ok, msg = regras.cadastrar_novo(email, senha)
            root.after(0, lambda: finalizar_cadastro(ok, msg))

        def finalizar_cadastro(ok, msg):
            btn_cadastrar.configure(text="Cadastrar", state="normal")
            if ok:
                messagebox.showinfo("Sucesso", "Conta criada com sucesso!", parent=janela)
                janela.destroy()
            else:
                messagebox.showerror("Erro no Cadastro", msg, parent=janela)

        def salvar():
            email_cadastro = campo_email.get().strip()
            senha_cadastro = campo_senha.get()
            conf_senha = campo_confirmar.get()
            
            if not email_cadastro or not senha_cadastro or not conf_senha:
                messagebox.showerror("Campos Incompletos", "Por favor, preencha todos os campos obrigatórios.", parent=janela)
                return
            
            if not email_e_valido(email_cadastro):
                messagebox.showerror("E-mail Inválido", "Insira um formato de e-mail corporativo válido.", parent=janela)
                return

            if len(senha_cadastro) < 6:
                messagebox.showerror("Senha Fraca", "A senha precisa ter no mínimo 6 caracteres para garantir a segurança.", parent=janela)
                return

            if senha_cadastro != conf_senha:
                messagebox.showerror("Divergência", "As senhas digitadas não coincidem.", parent=janela)
                return

            btn_cadastrar.configure(text="Processando...", state="disabled")
            
            threading.Thread(
                target=processar_cadastro,
                args=(email_cadastro, senha_cadastro),
                daemon=True
            ).start()

        btn_cadastrar = ctk.CTkButton(
            janela, text="Cadastrar", fg_color=ORANGE, hover_color=ORANGE_H,
            width=200, height=44, corner_radius=10,
            font=("Arial", 14, "bold"), command=salvar
        )
        btn_cadastrar.pack()