import os
import glob
import shutil
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image
from controllers.produto_controller import ProdutoController

COR_FUNDO_TELA       = "#f8fafc"
COR_FUNDO_CARD       = "#ffffff"
COR_BORDA_CARD       = "#e2e8f0"
COR_TITULO           = "#b91c1c"
COR_TEXTO_SECUNDARIO = "#475569"
COR_HOVER_FUNDO      = "#f1f5f9"
COR_VERMELHA         = "#991b1b"
COR_AMBER_CLARO      = "#fef3c7"

COR_LARANJA = "#f97316"
COR_VERDE   = "#16a34a"
COR_AZUL    = "#2563eb"
COR_ROXO    = "#7c3aed"

CATEGORIAS_DISPONIVEIS = ["Todas", "Salgada", "Doce", "Bebida", "Combo", "Adicional"]

EMOJI_CATEGORIAS = {
    "Todas":     "⊞ Todas",
    "Salgada":   "🍕 Pizzas Salgadas",
    "Doce":      "🍫 Pizzas Doces",
    "Bebida":    "🥤 Bebidas",
    "Combo":     "🍕🥤 Combos / Meio a Meio",
    "Adicional": "➕ Adicionais",
}

EMOJI_CARD_PADRAO = {
    "salgada":   "🍕",
    "doce":      "🍫",
    "bebida":    "🥤",
    "combo":     "🍕🥤",
    "adicional": "➕",
    "todas":     "📦"
}

EXTENSOES_VALIDAS  = {".png", ".jpg", ".jpeg", ".webp"}
TAMANHO_MAXIMO_MB  = 5
QUANTIDADE_COLUNAS = 3

PASTA_IMAGENS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "imagens_produtos"))

_cache_imagens: dict = {}


def _invalidar_cache(id_produto):
    if id_produto in _cache_imagens:
        _cache_imagens.pop(id_produto, None)


def _carregar_imagem(caminho_banco, id_produto):
    if id_produto in _cache_imagens:
        return _cache_imagens[id_produto]

    os.makedirs(PASTA_IMAGENS, exist_ok=True)
    caminho_real = None

    for ext in [".png", ".webp", ".jpg", ".jpeg"]:
        teste_caminho = os.path.join(PASTA_IMAGENS, f"{id_produto}{ext}")
        if os.path.exists(teste_caminho):
            caminho_real = teste_caminho
            break

    if not caminho_real and caminho_banco:
        nome_arquivo = os.path.basename(str(caminho_banco))
        teste_caminho = os.path.join(PASTA_IMAGENS, nome_arquivo)
        if os.path.exists(teste_caminho):
            caminho_real = teste_caminho

    if not caminho_real:
        return None

    try:
        with Image.open(caminho_real) as img_disco:
            img = img_disco.convert("RGBA")
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
            _cache_imagens[id_produto] = ctk_img
            return ctk_img
    except Exception as e:
        print(f"[tela_produtos] Erro ao carregar imagem id={id_produto}: {e}")
        return None


def _validar_arquivo_imagem(caminho):
    ext = os.path.splitext(caminho)[1].lower()
    if ext not in EXTENSOES_VALIDAS:
        return False, f"Formato não suportado: '{ext}'.\nUse: {', '.join(EXTENSOES_VALIDAS)}"

    tamanho_mb = os.path.getsize(caminho) / (1024 * 1024)
    if tamanho_mb > TAMANHO_MAXIMO_MB:
        return False, f"Imagem muito grande ({tamanho_mb:.1f} MB).\nMáximo permitido: {TAMANHO_MAXIMO_MB} MB."

    return True, ""


def _copiar_para_pasta_interna(caminho_original, id_produto):
    os.makedirs(PASTA_IMAGENS, exist_ok=True)

    padrao_busca = os.path.join(PASTA_IMAGENS, f"{id_produto}.*")
    for arquivo_antigo in glob.glob(padrao_busca):
        try: os.remove(arquivo_antigo)
        except: pass

    extensao = os.path.splitext(caminho_original)[1].lower()
    nome_arquivo = f"{id_produto}{extensao}"
    caminho_destino = os.path.join(PASTA_IMAGENS, nome_arquivo)

    shutil.copy2(caminho_original, caminho_destino)
    return nome_arquivo


def _abrir_formulario_produto(janela_raiz, controlador, on_sucesso, dados_produto=None):
    eh_edicao = dados_produto is not None
    id_prod   = dados_produto["id_produto"] if eh_edicao else None

    janela = ctk.CTkToplevel(janela_raiz)
    janela.geometry("540x720")
    janela.title("Editar Produto" if eh_edicao else "Novo Produto")
    janela.attributes("-topmost", True)
    janela.focus_force()

    def _fechar_formulario_seguro():
        try: janela.grab_release()
        except: pass
        try:
            for id_tarefa in janela.eval('after info').split():
                janela.after_cancel(id_tarefa)
        except: pass
        try: janela.destroy()
        except: pass

    janela.protocol("WM_DELETE_WINDOW", _fechar_formulario_seguro)

    ctk.CTkLabel(
        janela,
        text="Editar Detalhes do Produto" if eh_edicao else "Cadastrar Novo Produto",
        font=("Arial", 18, "bold")
    ).pack(pady=(15, 5))

    abas = ctk.CTkTabview(janela, width=480, height=540)
    abas.pack(padx=20, fill="both", expand=True)

    tab_dados = abas.add("Informações Básicas")
    tab_combo = abas.add("Composição do Combo / Sabores")

    def _criar_campo(sub_pai, label, placeholder):
        frame_campo = ctk.CTkFrame(sub_pai, fg_color="transparent")
        frame_campo.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(frame_campo, text=label, font=("Arial", 12, "bold")).pack(anchor="w")
        entry = ctk.CTkEntry(frame_campo, placeholder_text=placeholder, height=32)
        entry.pack(fill="x", pady=(2, 0))
        return entry

    campo_nome = _criar_campo(tab_dados, "Nome do Produto *", "Ex: Pizza Calabresa")

    # ----------------------------------------------------
    # CONTAINER: BLOCO DE PREÇO SIMPLES (PRODUTOS TRADICIONAIS)
    # ----------------------------------------------------
    frame_preco_simples = ctk.CTkFrame(tab_dados, fg_color="transparent")
    frame_preco_simples.pack(fill="x", padx=15, pady=2)
    
    ctk.CTkLabel(frame_preco_simples, text="Preço de venda (R$)", font=("Arial", 12, "bold")).pack(anchor="w")
    campo_preco = ctk.CTkEntry(frame_preco_simples, placeholder_text="Ex: 45.00", height=32)
    campo_preco.pack(fill="x", pady=(2, 4))
    
    ctk.CTkLabel(frame_preco_simples, text="Custo de produção (R$)", font=("Arial", 12, "bold")).pack(anchor="w")
    campo_custo = ctk.CTkEntry(frame_preco_simples, placeholder_text="Ex: 18.00", height=32)
    campo_custo.pack(fill="x", pady=(2, 0))

    # ----------------------------------------------------
    # CONTAINER: MÚLTIPLOS TAMANHOS (EXCLUSIVO PIZZAS)
    # ----------------------------------------------------
    frame_multi_tamanhos = ctk.CTkFrame(tab_dados, border_width=1, border_color="#cbd5e1")
    
    ctk.CTkLabel(frame_multi_tamanhos, text="Variações de Preço por Tamanho", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")
    ctk.CTkLabel(frame_multi_tamanhos, text="Tamanho", font=("Arial", 11, "underline")).grid(row=1, column=0, padx=5, pady=2)
    ctk.CTkLabel(frame_multi_tamanhos, text="Fatias", font=("Arial", 11, "underline")).grid(row=1, column=1, padx=5, pady=2)
    ctk.CTkLabel(frame_multi_tamanhos, text="Preço (R$)", font=("Arial", 11, "underline")).grid(row=1, column=2, padx=5, pady=2)

    # Inputs das variações de tamanho
    ctk.CTkLabel(frame_multi_tamanhos, text="Pequena (P):").grid(row=2, column=0, padx=10, pady=4, sticky="w")
    txt_f_p = ctk.CTkEntry(frame_multi_tamanhos, width=45, justify="center"); txt_f_p.insert(0, "4"); txt_f_p.grid(row=2, column=1, padx=5, pady=4)
    txt_p_p = ctk.CTkEntry(frame_multi_tamanhos, placeholder_text="0.00", width=120); txt_p_p.grid(row=2, column=2, padx=10, pady=4)

    ctk.CTkLabel(frame_multi_tamanhos, text="Média (M):").grid(row=3, column=0, padx=10, pady=4, sticky="w")
    txt_f_m = ctk.CTkEntry(frame_multi_tamanhos, width=45, justify="center"); txt_f_m.insert(0, "6"); txt_f_m.grid(row=3, column=1, padx=5, pady=4)
    txt_p_m = ctk.CTkEntry(frame_multi_tamanhos, placeholder_text="0.00", width=120); txt_p_m.grid(row=3, column=2, padx=10, pady=4)

    ctk.CTkLabel(frame_multi_tamanhos, text="Grande (G):").grid(row=4, column=0, padx=10, pady=4, sticky="w")
    txt_f_g = ctk.CTkEntry(frame_multi_tamanhos, width=45, justify="center"); txt_f_g.insert(0, "8"); txt_f_g.grid(row=4, column=1, padx=5, pady=4)
    txt_p_g = ctk.CTkEntry(frame_multi_tamanhos, placeholder_text="0.00", width=120); txt_p_g.grid(row=4, column=2, padx=10, pady=4)

    ctk.CTkLabel(frame_multi_tamanhos, text="Família:").grid(row=5, column=0, padx=10, pady=4, sticky="w")
    txt_f_fam = ctk.CTkEntry(frame_multi_tamanhos, width=45, justify="center"); txt_f_fam.insert(0, "12"); txt_f_fam.grid(row=5, column=1, padx=5, pady=4)
    txt_p_fam = ctk.CTkEntry(frame_multi_tamanhos, placeholder_text="0.00", width=120); txt_p_fam.grid(row=5, column=2, padx=10, pady=4)


    frame_cat = ctk.CTkFrame(tab_dados, fg_color="transparent")
    frame_cat.pack(fill="x", padx=15, pady=5)
    ctk.CTkLabel(frame_cat, text="Categoria", font=("Arial", 12, "bold")).pack(anchor="w")

    def monitorar_categoria(categoria_selecionada):
        if categoria_selecionada in ["Salgada", "Doce"]:
            frame_preco_simples.pack_forget()
            frame_multi_tamanhos.pack(fill="x", padx=15, pady=8)
            label_aviso_combo.configure(text="")
        elif categoria_selecionada == "Combo":
            frame_multi_tamanhos.pack_forget()
            frame_preco_simples.pack(fill="x", padx=15, pady=2)
            abas.set("Composição do Combo / Sabores")
            label_aviso_combo.configure(text="⚠️ Configure os sabores/itens na aba de composição.")
        else:
            frame_multi_tamanhos.pack_forget()
            frame_preco_simples.pack(fill="x", padx=15, pady=2)
            label_aviso_combo.configure(text="")

    campo_categoria = ctk.CTkComboBox(
        frame_cat,
        values=["Salgada", "Doce", "Bebida", "Combo", "Adicional"],
        height=35,
        command=monitorar_categoria
    )
    campo_categoria.pack(fill="x", pady=(2, 0))

    frame_desc = ctk.CTkFrame(tab_dados, fg_color="transparent")
    frame_desc.pack(fill="x", padx=15, pady=5)
    ctk.CTkLabel(frame_desc, text="Descrição", font=("Arial", 12, "bold")).pack(anchor="w")
    campo_descricao = ctk.CTkTextbox(frame_desc, height=60)
    campo_descricao.pack(fill="x", pady=(2, 0))

    label_aviso_combo = ctk.CTkLabel(tab_dados, text="", font=("Arial", 11), text_color=COR_LARANJA)
    label_aviso_combo.pack(pady=2)

    # --- ABA 2 (COMPOSIÇÃO DO COMBO) ---
    var_tipo_combo = ctk.StringVar(value="normal")
    frame_radios = ctk.CTkFrame(tab_combo, fg_color="transparent")
    frame_radios.pack(fill="x", pady=5)

    def alternar_modo_combo():
        if var_tipo_combo.get() == "metade":
            label_instrucao.configure(text="Selecione os sabores permitidos (Cálculo: metade mais cara):")
            campo_preco.configure(placeholder_text="Preço Automático (Metade mais cara)")
        else:
            label_instrucao.configure(text="Selecione os itens inclusos neste Combo:")
            campo_preco.configure(placeholder_text="Ex: 29.90")

    ctk.CTkRadioButton(frame_radios, text="Combo Tradicional", variable=var_tipo_combo, value="normal", command=alternar_modo_combo).pack(side="left", padx=20)
    ctk.CTkRadioButton(frame_radios, text="Pizza Meio a Meio", variable=var_tipo_combo, value="metade", command=alternar_modo_combo).pack(side="left", padx=20)

    label_instrucao = ctk.CTkLabel(tab_combo, text="Selecione os itens vinculados:", font=("Arial", 11, "italic"), text_color=COR_TEXTO_SECUNDARIO)
    label_instrucao.pack(anchor="w", padx=10, pady=(5, 0))

    frame_produtos_combo = ctk.CTkScrollableFrame(tab_combo, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
    frame_produtos_combo.pack(fill="both", expand=True, padx=5, pady=5)
    lista_checkboxes_produtos = []

    def carregar_produtos_disponiveis():
        if not janela.winfo_exists(): return
        for widget in frame_produtos_combo.winfo_children(): widget.destroy()
        lista_checkboxes_produtos.clear()

        sabores_salvos = controlador.obter_produtos_do_combo(id_prod) if eh_edicao else []
        todos_itens = controlador.listar_para_view()

        for prod in todos_itens:
            if prod.get("categoria", "Salgada").lower() == "combo" or (eh_edicao and prod.get("id_produto") == id_prod):
                continue

            chk = ctk.CTkCheckBox(
                frame_produtos_combo,
                text=f"{prod['nome_produto']} (R$ {prod['preco']:.2f})",
                font=("Arial", 11),
                checkbox_width=18,
                checkbox_height=18
            )
            chk.pack(anchor="w", padx=10, pady=5)

            if prod["id_produto"] in sabores_salvos:
                chk.select()

            lista_checkboxes_produtos.append({
                "id_produto": prod["id_produto"],
                "checkbox": chk,
                "preco": prod["preco"]
            })

    def _inicializacao_ui_segura():
        if not janela.winfo_exists(): return

        carregar_produtos_disponiveis()

        if eh_edicao:
            campo_nome.insert(0, dados_produto.get("nome_produto", ""))
            desc_antiga = dados_produto.get("descricao") or ""
            campo_descricao.insert("1.0", str(desc_antiga).strip())

            cat_atual = dados_produto.get("categoria", "Salgada")
            campo_categoria.set(cat_atual)
            monitorar_categoria(cat_atual)

            if cat_atual in ["Salgada", "Doce"]:
                # Puxa os múltiplos tamanhos do banco de dados
                tamanhos_salvos = controlador.obter_tamanhos_do_produto(id_prod)
                if tamanhos_salvos:
                    if "Pequena" in tamanhos_salvos: txt_p_p.insert(0, str(tamanhos_salvos["Pequena"]["preco"]))
                    if "Média" in tamanhos_salvos:   txt_p_m.insert(0, str(tamanhos_salvos["Média"]["preco"]))
                    if "Grande" in tamanhos_salvos:  txt_p_g.insert(0, str(tamanhos_salvos["Grande"]["preco"]))
                    if "Família" in tamanhos_salvos: txt_p_fam.insert(0, str(tamanhos_salvos["Família"]["preco"]))
            else:
                campo_preco.insert(0, str(dados_produto.get("preco", "")))
                custo_val = dados_produto.get("custo", 0) or 0
                if custo_val: campo_custo.insert(0, str(custo_val))

            if cat_atual == "Combo":
                if "metade" in str(desc_antiga).lower() or "sabor" in campo_nome.get().lower():
                    var_tipo_combo.set("metade")
                alternar_modo_combo()
                abas.set("Composição do Combo / Sabores")
            else:
                abas.set("Informações Básicas")
        else:
            campo_categoria.set("Salgada")
            monitorar_categoria("Salgada")
            abas.set("Informações Básicas")

    janela.after(100, _inicializacao_ui_segura)

    def _salvar():
        nome      = campo_nome.get().strip()
        categoria = campo_categoria.get()
        descricao = campo_descricao.get("1.0", "end").strip()

        if not nome:
            messagebox.showerror("Erro", "O nome do produto é obrigatório.", parent=janela)
            return

        id_prod_seguro = str(id_prod) if id_prod is not None else None

        if categoria in ["Salgada", "Doce"]:
            # Agrupa os valores da UI para enviar para o novo método do controlador
            dados_tamanhos = {
                "Pequena": {"fatias": int(txt_f_p.get() or 4), "preco": txt_p_p.get().strip()},
                "Média":   {"fatias": int(txt_f_m.get() or 6), "preco": txt_p_m.get().strip()},
                "Grande":  {"fatias": int(txt_f_g.get() or 8), "preco": txt_p_g.get().strip()},
                "Família": {"fatias": int(txt_f_fam.get() or 12), "preco": txt_p_fam.get().strip()}
            }
            
            sucesso, mensagem = controlador.validar_e_salvar_com_tamanhos(
                nome_produto=nome,
                categoria_produto=categoria,
                descricao_produto=descricao,
                dados_tamanhos=dados_tamanhos,
                id_produto=id_prod_seguro
            )
        elif categoria == "Combo":
            ids_vinculados = [str(item["id_produto"]) for item in lista_checkboxes_produtos if item["checkbox"].get() == 1]

            if len(ids_vinculados) < 2:
                messagebox.showerror("Erro", "Selecione pelo menos 2 sabores para salvar o combo.", parent=janela)
                return

            if var_tipo_combo.get() == "metade":
                precos_sel = [item["preco"] for item in lista_checkboxes_produtos if item["checkbox"].get() == 1]
                preco_final = str(max(precos_sel))
            else:
                preco_final = campo_preco.get().strip() if campo_preco.get() else "0.00"

            sucesso, mensagem = controlador.validar_e_salvar_combo(
                nome_combo=nome,
                texto_preco=preco_final,
                ids_produtos_associados=ids_vinculados,
                id_produto=id_prod_seguro,
                descricao_combo=descricao,
                texto_custo=campo_custo.get().strip()
            )
        else:
            preco_raw = campo_preco.get().strip()
            custo_raw = campo_custo.get().strip()
            if not preco_raw:
                messagebox.showerror("Erro", "O preço é obrigatório.", parent=janela)
                return
            sucesso, mensagem = controlador.validar_e_salvar(
                nome, preco_raw, id_prod, descricao, categoria, custo_raw
            )

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem, parent=janela)
            _fechar_formulario_seguro()
            on_sucesso()
        else:
            messagebox.showerror("Erro", mensagem, parent=janela)

    ctk.CTkButton(
        janela,
        text="💾 Salvar Produto",
        fg_color=COR_VERMELHA,
        hover_color="#7f1d1d",
        text_color="white",
        height=40,
        corner_radius=8,
        font=("Arial", 12, "bold"),
        command=_salvar,
    ).pack(fill="x", padx=30, pady=15)


def _criar_comando_troca_imagem(id_produto, label_icone, botao_remover, controlador):
    def trocar():
        caminho = filedialog.askopenfilename(
            title="Selecionar imagem do produto",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp")],
        )
        if not caminho: return

        valido, erro = _validar_arquivo_imagem(caminho)
        if not valido:
            messagebox.showerror("Imagem inválida", erro)
            return

        try:
            nome_arquivo_salvo = _copiar_para_pasta_interna(caminho, id_produto)
            _invalidar_cache(id_produto)
            ctk_img = _carregar_imagem(nome_arquivo_salvo, id_produto)

            if ctk_img and isinstance(ctk_img, ctk.CTkImage):
                label_icone.configure(image=ctk_img, text="")
                label_icone.image = ctk_img

            if controlador.atualizar_caminho_imagem(id_produto, nome_arquivo_salvo):
                botao_remover.place(relx=0.15, rely=0.85, anchor="center")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar imagem:\n{e}")
    return trocar


def _criar_comando_remover_imagem(id_produto, label_icone, botao_remover, categoria, controlador):
    def remover():
        if not messagebox.askyesno("Confirmar", "Deseja remover a foto deste produto?"): return
        try:
            if controlador.atualizar_caminho_imagem(id_produto, None):
                _invalidar_cache(id_produto)
                cat_chave = categoria.lower()
                emoji = EMOJI_CARD_PADRAO.get(cat_chave, "🍕")

                label_icone.configure(text=emoji, font=("Arial", 75), image="")
                label_icone.image = None
                botao_remover.place_forget()

                padrao_busca = os.path.join(PASTA_IMAGENS, f"{id_produto}.*")
                for f in glob.glob(padrao_busca): os.remove(f)

                messagebox.showinfo("Sucesso", "Foto removida com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover imagem:\n{e}")
    return remover


def _acao_excluir(id_produto, controlador, on_atualizar):
    if not messagebox.askyesno("Confirmar", "Deseja excluir este produto?"): return

    sucesso, mensagem = controlador.excluir(id_produto)
    if sucesso:
        _invalidar_cache(id_produto)
        padrao_busca = os.path.join(PASTA_IMAGENS, f"{id_produto}.*")
        for f in glob.glob(padrao_busca):
            try: os.remove(f)
            except: pass
        on_atualizar()
    else:
        messagebox.showerror("Erro", mensagem)


def _construir_cabecalho(pai, janela_raiz, controlador, on_atualizar):
    frame = ctk.CTkFrame(pai, fg_color="transparent")
    frame.pack(fill="x", padx=28, pady=(20, 10))

    ctk.CTkLabel(
        frame, text="Cardápio Digital",
        font=("Arial", 26, "bold"), text_color="#0f172a"
    ).pack(side="left")

    ctk.CTkButton(
        frame, text="+ Novo Item",
        fg_color=COR_VERMELHA, hover_color="#7f1d1d",
        text_color="white", width=130, height=36,
        corner_radius=6, font=("Arial", 12, "bold"),
        command=lambda: _abrir_formulario_produto(janela_raiz, controlador, on_atualizar),
    ).pack(side="right")


def _construir_filtros(pai, frame_conteudo, janela_raiz, paleta_cores, controlador, filtro_ativo):
    card = ctk.CTkFrame(pai, fg_color="#ffffff", corner_radius=8, border_width=1, border_color=COR_BORDA_CARD)
    card.pack(fill="x", padx=28, pady=(10, 0))

    frame_btns = ctk.CTkFrame(card, fg_color="transparent")
    frame_btns.pack(fill="x", padx=8, pady=8)

    for chave in CATEGORIAS_DISPONIVEIS:
        ativo = (chave == filtro_ativo)

        cor_fundo = COR_TITULO if ativo else "#ffffff"
        cor_texto = "white"    if ativo else COR_TEXTO_SECUNDARIO
        cor_hover = COR_VERMELHA if ativo else COR_HOVER_FUNDO

        ctk.CTkButton(
            frame_btns,
            text=EMOJI_CATEGORIAS[chave],
            fg_color=cor_fundo,
            text_color=cor_texto,
            hover_color=cor_hover,
            corner_radius=6,
            height=32,
            font=("Arial", 11, "bold" if ativo else "normal"),
            border_width=0 if ativo else 1,
            border_color=COR_BORDA_CARD,
            command=lambda cat=chave: renderizar_produtos(
                frame_conteudo, janela_raiz, paleta_cores, controlador, filtro_ativo=cat
            ),
        ).pack(side="left", padx=(0, 6))


def _construir_card(pai, produto, controlador, on_atualizar, linha, column):
    id_produto        = produto["id_produto"]
    nome_produto      = produto["nome_produto"]
    preco_produto     = produto["preco"]
    custo_produto     = float(produto.get("custo", 0) or 0)
    descricao_produto = produto.get("descricao") or "Item preparado com ingredientes selecionados."
    categoria_produto = produto.get("categoria", "Salgada")

    card = ctk.CTkFrame(
        pai, fg_color=COR_FUNDO_CARD, corner_radius=10,
        border_width=1, border_color=COR_BORDA_CARD,
        width=240, height=400,
    )
    card.grid(row=linha, column=column, padx=6, pady=8, sticky="nsew")
    card.grid_propagate(False)

    frame_img = ctk.CTkFrame(card, fg_color="transparent", width=180, height=155)
    frame_img.pack(side="top", pady=(15, 5))
    frame_img.pack_propagate(False)

    label_icone = ctk.CTkLabel(frame_img, text="")
    label_icone.pack(expand=True)

    ctk_img = _carregar_imagem(produto.get("imagem", ""), id_produto)

    if ctk_img and isinstance(ctk_img, ctk.CTkImage):
        label_icone.configure(image=ctk_img, text="")
        label_icone.image = ctk_img
    else:
        cat_chave = categoria_produto.lower()
        emoji = EMOJI_CARD_PADRAO.get(cat_chave, "🍕")
        label_icone.configure(text=emoji, font=("Arial", 70), image="")
        label_icone.image = None

    btn_trocar = ctk.CTkButton(
        frame_img, text="📷", width=28, height=28, corner_radius=14,
        fg_color="#ffffff", hover_color="#f1f5f9", text_color="#0f172a",
        font=("Arial", 12), border_width=1, border_color="#cbd5e1",
    )
    btn_trocar.place(relx=0.85, rely=0.85, anchor="center")

    btn_remover_img = ctk.CTkButton(
        frame_img, text="🗑️", width=28, height=28, corner_radius=14,
        fg_color="#ffffff", hover_color="#fee2e2", text_color="#ef4444",
        font=("Arial", 10), border_width=1, border_color="#fca5a5",
    )
    if ctk_img and isinstance(ctk_img, ctk.CTkImage):
        btn_remover_img.place(relx=0.15, rely=0.85, anchor="center")

    btn_trocar.configure(
        command=_criar_comando_troca_imagem(id_produto, label_icone, btn_remover_img, controlador)
    )
    btn_remover_img.configure(
        command=_criar_comando_remover_imagem(id_produto, label_icone, btn_remover_img, categoria_produto, controlador)
    )

    card_nome_texto = str(nome_produto)
    if len(card_nome_texto) > 24:
        card_nome_texto = card_nome_texto[:22] + "..."

    ctk.CTkLabel(
        card, text=card_nome_texto,
        font=("Arial", 14, "bold"), text_color=COR_TITULO, justify="center"
    ).pack(side="top", pady=(5, 2), padx=10)

    ctk.CTkLabel(
        card, text=descricao_produto,
        font=("Arial", 11), text_color=COR_TEXTO_SECUNDARIO,
        wraplength=200, justify="center"
    ).pack(side="top", padx=15, pady=(0, 2))

    # Formatação de exibição do preço no card (caso seja pizza, pode mostrar o valor base ou 'A partir de')
    if categoria_produto in ["Salgada", "Doce"]:
        card_preco_texto = "Vários tamanhos"
    else:
        card_preco_texto = f"R$ {preco_produto:.2f}" if isinstance(preco_produto, (int, float)) else f"R$ {preco_produto}"

    ctk.CTkLabel(
        card, text=card_preco_texto,
        font=("Arial", 14, "bold"), text_color="#0f172a"
    ).pack(side="top", pady=(2, 0))

    # Custo e margem
    if custo_produto > 0 and isinstance(preco_produto, (int, float)) and preco_produto > 0:
        margem_pct = ((preco_produto - custo_produto) / preco_produto) * 100
        cor_margem = COR_VERDE if margem_pct >= 30 else ("#D97706" if margem_pct >= 10 else "#DC2626")
        ctk.CTkLabel(
            card, text=f"Custo: R$ {custo_produto:.2f}  ·  Margem: {margem_pct:.0f}%",
            font=("Arial", 10), text_color=cor_margem
        ).pack(side="top", pady=(0, 2))
    elif custo_produto > 0:
        ctk.CTkLabel(
            card, text=f"Custo: R$ {custo_produto:.2f}",
            font=("Arial", 10), text_color=COR_TEXTO_SECUNDARIO
        ).pack(side="top", pady=(0, 2))

    frame_acoes = ctk.CTkFrame(card, fg_color="transparent")
    frame_acoes.pack(side="bottom", fill="x", pady=(0, 15), padx=20)

    ctk.CTkButton(
        frame_acoes, text="Ver detalhes",
        fg_color="#ffffff", hover_color="#f1f5f9",
        text_color=COR_TITULO, font=("Arial", 11, "bold"),
        border_width=1, border_color=COR_TITULO,
        corner_radius=6, height=30,
        command=lambda d=produto: _abrir_formulario_produto(
            frame_img.winfo_toplevel(), controlador, on_atualizar, d
        ),
    ).pack(fill="x", side="left", expand=True, padx=(0, 4))

    ctk.CTkButton(
        frame_acoes, text="🗑️",
        fg_color="transparent", hover_color="#fee2e2",
        text_color="#ef4444", font=("Arial", 12),
        width=30, height=30, corner_radius=6,
        command=lambda:_acao_excluir(id_produto, controlador, on_atualizar),
    ).pack(side="right")


def _construir_rodape(pai, todos_produtos):
    frame = ctk.CTkFrame(pai, fg_color="transparent")
    frame.pack(fill="x", padx=28, pady=(10, 15))

    categorias_unicas = len(set(p.get("categoria", "Salgada") for p in todos_produtos))

    estatisticas = [
        ("Total de Itens", str(len(todos_produtos)), "🍕", COR_LARANJA),
        ("Categorias",     str(categorias_unicas),   "📦", COR_AZUL),
    ]

    for titulo, valor, emoji, cor in estatisticas:
        card = ctk.CTkFrame(
            frame, fg_color="#ffffff", corner_radius=6,
            border_width=1, border_color=COR_BORDA_CARD, height=65
        )
        card.pack(side="left", fill="x", expand=True, padx=4)
        ctk.CTkLabel(card, text=f"{emoji} {titulo}: {valor}", font=("Arial", 11, "bold"), text_color=COR_TEXTO_SECUNDARIO).pack(expand=True)


def renderizar_produtos(frame_conteudo, janela_raiz, paleta_cores, controlador=None, filtro_ativo="Todas"):
    if controlador is None:
        conexao = getattr(janela_raiz, "conn", None) or getattr(janela_raiz, "conexao", None)
        controlador = ProdutoController(conexao)

    todos_produtos = controlador.listar_para_view()
    lista_produtos = (
        todos_produtos if filtro_ativo == "Todas"
        else [p for p in todos_produtos if p.get("categoria", "Salgada").lower() == filtro_ativo.lower()]
    )

    def on_atualizar():
        renderizar_produtos(frame_conteudo, janela_raiz, paleta_cores, controlador, filtro_ativo)

    for widget in frame_conteudo.winfo_children():
        widget.destroy()

    _construir_cabecalho(frame_conteudo, janela_raiz, controlador, on_atualizar)
    _construir_filtros(frame_conteudo, frame_conteudo, janela_raiz, paleta_cores, controlador, filtro_ativo)

    area_scroll = ctk.CTkScrollableFrame(frame_conteudo, fg_color="transparent")
    area_scroll.pack(fill="both", expand=True, padx=28, pady=10)

    for col in range(QUANTIDADE_COLUNAS):
        area_scroll.grid_columnconfigure(col, weight=1, uniform="coluna_card")

    if not lista_produtos:
        lbl_erro = ctk.CTkLabel(
            area_scroll,
            text="Nenhum produto cadastrado nesta categoria.",
            font=("Arial", 12), text_color=COR_TEXTO_SECUNDARIO,
        )
        lbl_erro.grid(row=0, column=0, columnspan=QUANTIDADE_COLUNAS, pady=30, sticky="nsew")
    else:
        for pos, produto in enumerate(lista_produtos):
            linha, column = divmod(pos, QUANTIDADE_COLUNAS)
            area_scroll.grid_rowconfigure(linha, weight=0)
            _construir_card(area_scroll, produto, controlador, on_atualizar, linha, column)

    _construir_rodape(frame_conteudo, todos_produtos)