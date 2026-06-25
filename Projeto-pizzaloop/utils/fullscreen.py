# ========================================================
# utils/fullscreen.py
# Adicionado da pizzaloop — não existia no pizzaloop_replit
# ========================================================

def configurar_fullscreen(janela):
    """
    Configura os atalhos de tela cheia diretamente na raiz da janela.
    Isso faz com que o comando funcione em TODAS as sub-telas e views do sistema.
    """
    def toggle_fullscreen(event=None):
        try:
            raiz = janela.winfo_toplevel()
            # Pega o estado atual da tela cheia
            estado_atual = raiz.attributes("-fullscreen")
            
            if not estado_atual:
                # Entra em tela cheia total
                raiz.attributes("-fullscreen", True)
            else:
                # Sai da tela cheia e força o modo maximizado correto (com a barra do Windows)
                raiz.attributes("-fullscreen", False)
                raiz.state("zoomed")
                
            raiz.update_idletasks() # Força o CustomTkinter a recalcular os tamanhos dos frames
        except Exception:
            pass
        return "break"

    def sair_fullscreen(event=None):
        try:
            raiz = janela.winfo_toplevel()
            # Só executa a saída se realemente ESTIVER em fullscreen, 
            # evitando bugar o app se o usuário apertar ESC na tela normal.
            if raiz.attributes("-fullscreen"):
                raiz.attributes("-fullscreen", False)
                raiz.state("zoomed") # Retorna ao maximizado limpo
                raiz.update_idletasks()
        except Exception:
            pass
        return "break"

    # O segredo para funcionar em todas as telas é o bind_all na janela raiz
    raiz_real = janela.winfo_toplevel()
    
    # Inicia a aplicação maximizada de forma elegante, respeitando os monitores
    raiz_real.state("zoomed")
    
    raiz_real.bind_all("<F11>", toggle_fullscreen)
    raiz_real.bind_all("<Escape>", sair_fullscreen)
    raiz_real.focus_force()