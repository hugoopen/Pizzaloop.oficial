import customtkinter as ctk
from controllers.relatorios_controller import RelatoriosController
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from datetime import datetime

COR_FUNDO      = "#FAF5F3"
COR_CARD       = "#FFFFFF"
COR_BORDA      = "#E8DDD9"
COR_HOVER      = "#FEF3C7"
COR_TEXTO      = "#1C1917"
COR_TEXTO_SUB  = "#78716C"
COR_PRIMARIA   = "#C0392B"
COR_PRIM_H     = "#A93226"
COR_VERDE      = "#16A34A"
COR_VERDE_CLARO= "#DCFCE7"
COR_AZUL       = "#2563EB"
COR_AZUL_CLARO = "#DBEAFE"
COR_AMBER      = "#F59E0B"
COR_AMBER_CLARO= "#FEF3C7"
COR_ROXO       = "#9333EA"
COR_ROXO_CLARO = "#F3E8FF"

W3_C1 = 220
W3_C2 = 130
W3_C3 = 160


def _fmt(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _card(parent, **kw):
    base = dict(fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
    base.update(kw)
    return ctk.CTkFrame(parent, **base)


def _tabela_tres_colunas(parent, cabecalhos, dados, cor_col2=COR_PRIMARIA, cor_col3=COR_PRIMARIA):
    cab = ctk.CTkFrame(parent, fg_color="#F5F0EE", corner_radius=0, height=36)
    cab.pack(fill="x", padx=0)
    cab.pack_propagate(False)

    ctk.CTkLabel(cab, text="", width=16).pack(side="left")
    ctk.CTkLabel(cab, text=cabecalhos[0], width=W3_C1, anchor="w",
                 font=("Arial", 13, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
    ctk.CTkLabel(cab, text=cabecalhos[1], width=W3_C2, anchor="w",
                 font=("Arial", 13, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
    ctk.CTkLabel(cab, text=cabecalhos[2], width=W3_C3, anchor="w",
                 font=("Arial", 13, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")

    ctk.CTkFrame(parent, height=1, fg_color=COR_BORDA).pack(fill="x")

    if not dados:
        ctk.CTkLabel(parent, text="Sem dados no período.",
                     font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(pady=12)
        return

    for idx, row in enumerate(dados):
        cor_linha = COR_CARD if idx % 2 == 0 else "#FAF5F3"
        val2 = row[1] if isinstance(row[1], str) else str(row[1])
        val3 = row[2] if isinstance(row[2], str) else _fmt(float(row[2]))

        linha = ctk.CTkFrame(parent, fg_color=cor_linha, corner_radius=0, height=42)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkLabel(linha, text="", width=16).pack(side="left")
        ctk.CTkLabel(linha, text=str(row[0]), width=W3_C1, anchor="w",
                     font=("Arial", 14), text_color=COR_TEXTO).pack(side="left")
        ctk.CTkLabel(linha, text=val2, width=W3_C2, anchor="w",
                     font=("Arial", 14, "bold"), text_color=cor_col2).pack(side="left")
        ctk.CTkLabel(linha, text=val3, width=W3_C3, anchor="w",
                     font=("Arial", 14, "bold"), text_color=cor_col3).pack(side="left")

        if idx < len(dados) - 1:
            ctk.CTkFrame(parent, height=1, fg_color=COR_BORDA).pack(fill="x")

    ctk.CTkFrame(parent, height=10, fg_color="transparent").pack()


def _exportar_pdf(controlador, periodo):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    except ImportError:
        messagebox.showerror("Dependência faltando",
                             "A biblioteca 'reportlab' não está instalada.\n\n"
                             "Execute:\n  pip install reportlab")
        return

    caminho = filedialog.asksaveasfilename(
        title="Salvar Relatório PDF",
        defaultextension=".pdf",
        initialfile=f"relatorio_pizzaloop_{periodo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
    )
    if not caminho:
        return

    try:
        doc = SimpleDocTemplate(
            caminho, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )

        estilos = getSampleStyleSheet()
        vermelho   = colors.HexColor("#C0392B")
        cinza_esc  = colors.HexColor("#1C1917")
        cinza_med  = colors.HexColor("#78716C")
        cinza_clar = colors.HexColor("#F5F0EE")
        azul       = colors.HexColor("#2563EB")
        verde      = colors.HexColor("#16A34A")
        amber      = colors.HexColor("#F59E0B")

        st_titulo = ParagraphStyle("titulo", parent=estilos["Title"],
                                   fontSize=22, textColor=vermelho,
                                   spaceAfter=4, spaceBefore=0)
        st_sub    = ParagraphStyle("sub", parent=estilos["Normal"],
                                   fontSize=11, textColor=cinza_med,
                                   spaceAfter=6)
        st_secao  = ParagraphStyle("secao", parent=estilos["Heading2"],
                                   fontSize=13, textColor=cinza_esc,
                                   spaceBefore=14, spaceAfter=6)
        st_normal = ParagraphStyle("normal", parent=estilos["Normal"],
                                   fontSize=10, textColor=cinza_esc)
        st_rodape = ParagraphStyle("rodape", parent=estilos["Normal"],
                                   fontSize=8, textColor=cinza_med,
                                   alignment=TA_CENTER)

        rotulos_periodo = {
            "hoje": "Hoje", "7dias": "Últimos 7 dias",
            "30dias": "Últimos 30 dias", "mes": "Este mês", "ano": "Este ano"
        }
        label_per = rotulos_periodo.get(periodo, periodo)

        elementos = []

        elementos.append(Paragraph("🍕 PizzaLoop — Relatório", st_titulo))
        elementos.append(Paragraph(f"Período: {label_per}  ·  Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", st_sub))
        elementos.append(HRFlowable(width="100%", thickness=1, color=vermelho, spaceAfter=10))

        try:
            receita, n_pedidos, ticket = controlador.resumo(periodo)
        except Exception:
            receita, n_pedidos, ticket = 0.0, 0, 0.0

        try:
            _, custo_est, lucro_est, margem_est = controlador.lucro(periodo)
        except Exception:
            custo_est, lucro_est, margem_est = 0.0, 0.0, 0.0

        dados_kpi = [
            ["Receita Total", "Total de Pedidos", "Ticket Médio", "Lucro Líquido"],
            [_fmt(receita), str(n_pedidos), _fmt(ticket),
             f"{_fmt(lucro_est)} ({margem_est:.1f}%)"],
        ]
        t_kpi = Table(dados_kpi, colWidths=["25%", "25%", "25%", "25%"])
        t_kpi.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
            ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
            ("FONTSIZE",    (0, 0), (-1, 0), 9),
            ("TEXTCOLOR",   (0, 1), (-1, 1), vermelho),
            ("TEXTCOLOR",   (3, 1), (3, 1),  verde),
            ("FONTSIZE",    (0, 1), (-1, 1), 13),
            ("FONTNAME",    (0, 1), (-1, 1), "Helvetica-Bold"),
            ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, 1), [colors.white]),
            ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("INNERGRID",   (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("TOPPADDING",  (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_kpi)
        elementos.append(Spacer(1, 10))

        # ── CUSTO TOTAL ────────────────────────────────────────────────
        elementos.append(Paragraph("💸  Custo Total", st_secao))
        cor_amber_bg = colors.HexColor("#FEF3C7")
        cor_verde_bg = colors.HexColor("#DCFCE7")
        cor_verm_bg  = colors.HexColor("#FEE2E2")
        cor_laranja_bg = colors.HexColor("#FFF7ED")
        cor_lucro_bg = cor_verde_bg if lucro_est >= 0 else cor_verm_bg
        cor_lucro_c  = verde if lucro_est >= 0 else vermelho

        dados_custo = [
            ["Quanto foi Gasto", "Quanto vai Ganhar (Lucro)"],
            [_fmt(custo_est), f"{_fmt(lucro_est)}  ({margem_est:.1f}%)"],
            ["Custo estimado com base nos produtos vendidos",
             "Lucro estimado com base nos custos dos produtos"],
        ]
        t_custo = Table(dados_custo, colWidths=["50%", "50%"])
        t_custo.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), cinza_clar),
            ("TEXTCOLOR",     (0, 0), (-1, 0), cinza_med),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 9),
            ("BACKGROUND",    (0, 1), (0, 1),  cor_amber_bg),
            ("TEXTCOLOR",     (0, 1), (0, 1),  amber),
            ("BACKGROUND",    (1, 1), (1, 1),  cor_lucro_bg),
            ("TEXTCOLOR",     (1, 1), (1, 1),  cor_lucro_c),
            ("FONTSIZE",      (0, 1), (-1, 1), 15),
            ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
            ("TEXTCOLOR",     (0, 2), (-1, 2), cinza_med),
            ("FONTSIZE",      (0, 2), (-1, 2), 8),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_custo)
        elementos.append(Spacer(1, 4))

        try:
            _ti_pdf, _ic_pdf, valor_est_custo_pdf = controlador.resumo_estoque()
        except Exception:
            valor_est_custo_pdf = 0.0

        dados_custo2 = [
            ["Custo de Produto", "Custo de Estoque"],
            [_fmt(custo_est), _fmt(valor_est_custo_pdf)],
            ["Total gasto em produtos nos pedidos do período",
             "Valor total investido atualmente no estoque"],
        ]
        t_custo2 = Table(dados_custo2, colWidths=["50%", "50%"])
        t_custo2.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), cinza_clar),
            ("TEXTCOLOR",     (0, 0), (-1, 0), cinza_med),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 9),
            ("BACKGROUND",    (0, 1), (0, 1),  cor_laranja_bg),
            ("TEXTCOLOR",     (0, 1), (0, 1),  colors.HexColor("#C2410C")),
            ("FONTNAME",      (0, 1), (0, 1),  "Helvetica-Bold"),
            ("BACKGROUND",    (1, 1), (1, 1),  colors.HexColor("#EFF6FF")),
            ("TEXTCOLOR",     (1, 1), (1, 1),  azul),
            ("FONTNAME",      (1, 1), (1, 1),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 1), (-1, 1), 14),
            ("TEXTCOLOR",     (0, 2), (-1, 2), cinza_med),
            ("FONTSIZE",      (0, 2), (-1, 2), 8),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_custo2)
        elementos.append(Spacer(1, 10))

        elementos.append(Paragraph("💰  Análise de Lucro por Produto", st_secao))
        try:
            lucro_prod = controlador.lucro_por_produto(periodo)
        except Exception:
            lucro_prod = []

        if lucro_prod:
            cab_l = [["Produto", "Receita", "Custo Est.", "Lucro"]]
            linhas_l = [[str(nome)[:35], _fmt(float(rec)), _fmt(float(cst)), _fmt(float(luc))]
                        for nome, rec, cst, luc in lucro_prod[:8]]
            t_lucro = Table(cab_l + linhas_l, colWidths=["40%", "20%", "20%", "20%"])
            t_lucro.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("TEXTCOLOR",   (3, 1), (3, -1), verde),
                ("FONTNAME",    (3, 1), (3, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_lucro)
        else:
            elementos.append(Paragraph("Sem dados de custo cadastrados.", st_normal))
        elementos.append(Spacer(1, 10))

        try:
            vendas_dia = controlador.vendas_por_dia(periodo)
        except Exception:
            vendas_dia = []

        elementos.append(Paragraph("📊  Vendas por Dia", st_secao))
        if vendas_dia:
            cab = [["Dia", "Pedidos", "Receita"]]
            linhas = [[str(r[0]), str(r[1]), _fmt(float(r[2]))] for r in vendas_dia]
            t_dias = Table(cab + linhas, colWidths=["50%", "20%", "30%"])
            t_dias.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("TEXTCOLOR",   (1, 1), (1, -1), vermelho),
                ("TEXTCOLOR",   (2, 1), (2, -1), vermelho),
                ("FONTNAME",    (1, 1), (2, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_dias)
        else:
            elementos.append(Paragraph("Sem dados no período.", st_normal))
        elementos.append(Spacer(1, 10))

        try:
            top_prod = controlador.performance_produtos(periodo)
        except Exception:
            top_prod = []

        elementos.append(Paragraph("🏆  Top Produtos", st_secao))
        if top_prod:
            medalhas = ["1°", "2°", "3°", "4°", "5°"]
            cab = [["#", "Produto", "Qtd.", "Receita"]]
            linhas = [[medalhas[i] if i < 5 else "-", str(nome)[:40],
                       str(qtd), _fmt(float(rec))]
                      for i, (nome, qtd, rec) in enumerate(top_prod[:5])]
            t_prod = Table(cab + linhas, colWidths=["8%", "50%", "15%", "27%"])
            t_prod.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("FONTNAME",    (0, 1), (0, -1), "Helvetica-Bold"),
                ("TEXTCOLOR",   (0, 1), (0, -1), amber),
                ("TEXTCOLOR",   (2, 1), (3, -1), verde),
                ("FONTNAME",    (2, 1), (3, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_prod)
        else:
            elementos.append(Paragraph("Sem dados no período.", st_normal))
        elementos.append(Spacer(1, 10))

        try:
            metodos = controlador.metodos_pagamento(periodo)
        except Exception:
            metodos = []

        elementos.append(Paragraph("💳  Métodos de Pagamento", st_secao))
        if metodos:
            total_pag = sum(q for _, q, _, _, _ in metodos) or 1
            cab = [["Método", "Pedidos", "Receita", "Pagos", "Pendentes"]]
            linhas = [[str(m) or "Não informado", str(q), _fmt(float(r)), str(pg), str(npg)]
                      for m, q, r, pg, npg in metodos]
            t_pag = Table(cab + linhas, colWidths=["28%", "10%", "10%", "22%", "15%", "15%"])
            t_pag.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("TEXTCOLOR",   (3, 1), (3, -1), azul),
                ("FONTNAME",    (3, 1), (3, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_pag)
        else:
            elementos.append(Paragraph("Sem dados no período.", st_normal))
        elementos.append(Spacer(1, 10))

        try:
            horarios = controlador.horarios_movimento(periodo)
        except Exception:
            horarios = []

        elementos.append(Paragraph("🕐  Horários de Maior Movimento", st_secao))
        if horarios:
            cab = [["Horário", "Pedidos", "Receita"]]
            linhas = [[str(r[0]), str(r[1]), _fmt(float(r[2]))] for r in horarios]
            t_hor = Table(cab + linhas, colWidths=["50%", "20%", "30%"])
            t_hor.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("TEXTCOLOR",   (1, 1), (2, -1), vermelho),
                ("FONTNAME",    (1, 1), (2, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_hor)
        else:
            elementos.append(Paragraph("Sem dados no período.", st_normal))

        # ── ESTOQUE NO PDF ─────────────────────────────────────────────
        elementos.append(Paragraph("📦  Estoque", st_secao))

        try:
            total_itens_pdf, itens_crit_pdf, valor_est_pdf = controlador.resumo_estoque()
        except Exception:
            total_itens_pdf, itens_crit_pdf, valor_est_pdf = 0, 0, 0.0

        dados_est_resumo = [
            ["Total de Itens", "Itens Críticos (abaixo do mínimo)", "Valor Total em Estoque"],
            [str(total_itens_pdf), str(itens_crit_pdf), _fmt(valor_est_pdf)],
        ]
        t_est_res = Table(dados_est_resumo, colWidths=["33%", "34%", "33%"])
        t_est_res.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), cinza_clar),
            ("TEXTCOLOR",     (0, 0), (-1, 0), cinza_med),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 9),
            ("TEXTCOLOR",     (0, 1), (0, 1),  azul),
            ("TEXTCOLOR",     (1, 1), (1, 1),  vermelho if itens_crit_pdf > 0 else verde),
            ("TEXTCOLOR",     (2, 1), (2, 1),  amber),
            ("FONTSIZE",      (0, 1), (-1, 1), 14),
            ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_est_res)
        elementos.append(Spacer(1, 8))

        try:
            criticos_pdf = controlador.itens_criticos_estoque()
        except Exception:
            criticos_pdf = []

        if criticos_pdf:
            elementos.append(Paragraph("⚠  Itens Abaixo do Mínimo", st_secao))
            cab_crit = [["Item", "Categoria", "Atual", "Mínimo", "Und."]]
            linhas_crit = [[str(n)[:30], str(c), f"{a:.1f}", f"{m:.1f}", str(u)]
                           for n, c, a, m, u, _p in criticos_pdf]
            t_crit = Table(cab_crit + linhas_crit, colWidths=["35%", "20%", "15%", "15%", "15%"])
            t_crit.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("TEXTCOLOR",   (2, 1), (2, -1), vermelho),
                ("FONTNAME",    (2, 1), (2, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_crit)
            elementos.append(Spacer(1, 8))

        try:
            movs_pdf = controlador.movimentacoes_estoque(periodo)
        except Exception:
            movs_pdf = []

        elementos.append(Paragraph("🔄  Movimentações de Estoque no Período", st_secao))
        if movs_pdf:
            cab_mov = [["Item", "Tipo", "Qtd.", "Und.", "Data"]]
            linhas_mov = [[str(n)[:25], str(t), f"{q:.1f}", str(u), str(d)[:10]]
                          for n, t, q, u, _o, d in movs_pdf]
            t_mov = Table(cab_mov + linhas_mov, colWidths=["35%", "15%", "15%", "15%", "20%"])
            t_mov.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("TEXTCOLOR",   (1, 1), (1, -1), verde),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_mov)
        else:
            elementos.append(Paragraph("Nenhuma movimentação no período.", st_normal))

        try:
            consumo_pdf = controlador.consumo_por_produto(periodo)
        except Exception:
            consumo_pdf = []

        if consumo_pdf:
            elementos.append(Spacer(1, 8))
            elementos.append(Paragraph("🍕  Consumo de Estoque por Produto Vendido", st_secao))
            cab_cons = [["Produto", "Qtd. Vendida", "Ingrediente", "Consumido", "Und."]]
            linhas_cons = [[str(p)[:25], str(qv), str(it)[:20], f"{c:.2f}", str(u)]
                           for p, qv, c, it, u in consumo_pdf]
            t_cons = Table(cab_cons + linhas_cons,
                           colWidths=["28%", "14%", "26%", "17%", "15%"])
            t_cons.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), cinza_clar),
                ("TEXTCOLOR",   (0, 0), (-1, 0), cinza_med),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("TEXTCOLOR",   (3, 1), (3, -1), amber),
                ("FONTNAME",    (3, 1), (3, -1), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, cinza_clar]),
                ("BOX",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E8DDD9")),
                ("INNERGRID",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E8DDD9")),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elementos.append(t_cons)

        elementos.append(Spacer(1, 20))
        elementos.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E8DDD9"), spaceAfter=6))
        elementos.append(Paragraph(f"PizzaLoop Sistema  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}", st_rodape))

        doc.build(elementos)
        messagebox.showinfo("PDF Exportado", f"Relatório salvo com sucesso em:\n{caminho}")

    except Exception as e:
        messagebox.showerror("Erro ao exportar PDF", f"Não foi possível gerar o PDF:\n{str(e)}")


def renderizar_relatorios(frame_conteudo, janela_raiz, paleta_cores, periodo="7dias"):
    controlador = RelatoriosController(janela_raiz.conn)

    for w in frame_conteudo.winfo_children():
        w.destroy()

    area = ctk.CTkScrollableFrame(frame_conteudo, fg_color=COR_FUNDO,
                                  scrollbar_button_color=COR_BORDA, corner_radius=0)
    area.pack(fill="both", expand=True)

    # ── CABEÇALHO ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(area, fg_color="transparent")
    barra.pack(fill="x", padx=28, pady=(24, 4))
    ctk.CTkLabel(barra, text="Relatórios e Exportação",
                 font=("Arial", 26, "bold"), text_color=COR_TEXTO).pack(side="left")
    ctk.CTkLabel(barra, text="Gere e exporte relatórios detalhados em PDF",
                 font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(side="left", padx=(14, 0))
    ctk.CTkButton(
        barra, text="⬇  Exportar PDF",
        fg_color=COR_PRIMARIA, hover_color=COR_PRIM_H,
        text_color="white", corner_radius=8,
        height=36, font=("Arial", 13, "bold"),
        command=lambda: _exportar_pdf(controlador, periodo)
    ).pack(side="right")
    ctk.CTkFrame(area, height=1, fg_color=COR_BORDA).pack(fill="x", padx=28, pady=(4, 16))

    # ── SELETOR DE PERÍODO ────────────────────────────────────────────
    card_periodo = _card(area)
    card_periodo.pack(fill="x", padx=28, pady=(0, 16))
    linha_per = ctk.CTkFrame(card_periodo, fg_color="transparent")
    linha_per.pack(fill="x", padx=16, pady=14)
    ctk.CTkLabel(linha_per, text="📅  Período:",
                 font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(side="left", padx=(0, 12))

    for rotulo, valor in [("Hoje", "hoje"), ("Últimos 7 dias", "7dias"),
                           ("Últimos 30 dias", "30dias"), ("Este mês", "mes"), ("Este ano", "ano")]:
        ativo = (valor == periodo)
        ctk.CTkButton(
            linha_per, text=rotulo,
            fg_color=COR_PRIMARIA if ativo else COR_CARD,
            text_color="white" if ativo else COR_TEXTO_SUB,
            hover_color=COR_PRIM_H if ativo else COR_HOVER,
            border_width=0 if ativo else 1, border_color=COR_BORDA,
            corner_radius=8, height=34,
            font=("Arial", 13, "bold" if ativo else "normal"),
            command=lambda p=valor: renderizar_relatorios(frame_conteudo, janela_raiz, paleta_cores, p)
        ).pack(side="left", padx=(0, 6))

    # ── KPI CARDS ─────────────────────────────────────────────────────
    try:
        receita, n_pedidos, ticket = controlador.resumo(periodo)
    except Exception:
        receita, n_pedidos, ticket = 0.0, 0, 0.0

    try:
        _, custo_est, lucro_est, margem_est = controlador.lucro(periodo)
    except Exception:
        custo_est, lucro_est, margem_est = 0.0, 0.0, 0.0

    linha_kpi = ctk.CTkFrame(area, fg_color="transparent")
    linha_kpi.pack(fill="x", padx=28, pady=(0, 16))

    def _kpi(parent, titulo, valor, emoji, cor_bg, cor_val, sub=None):
        c = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12,
                         border_width=1, border_color=COR_BORDA, height=100)
        c.pack(side="left", padx=(0, 12), expand=True, fill="x")
        c.pack_propagate(False)
        ib = ctk.CTkFrame(c, fg_color=cor_bg, width=44, height=44, corner_radius=12)
        ib.place(x=14, y=14)
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text=emoji, font=("Arial", 22)).pack(expand=True)
        ctk.CTkLabel(c, text=titulo, font=("Arial", 12), text_color=COR_TEXTO_SUB).place(x=66, y=14)
        ctk.CTkLabel(c, text=valor, font=("Arial", 19, "bold"), text_color=cor_val).place(x=66, y=36)
        if sub:
            ctk.CTkLabel(c, text=sub, font=("Arial", 10), text_color=COR_TEXTO_SUB).place(x=66, y=68)

    _kpi(linha_kpi, "Receita Total",    _fmt(receita),  "💰", "#FEE2E2",      COR_PRIMARIA)
    _kpi(linha_kpi, "Total de Pedidos", str(n_pedidos), "📋", COR_AZUL_CLARO,  COR_AZUL)
    _kpi(linha_kpi, "Ticket Médio",     _fmt(ticket),   "🎯", COR_AMBER_CLARO, COR_AMBER)

    cor_lucro_val = COR_VERDE if lucro_est >= 0 else COR_PRIMARIA
    _kpi(linha_kpi, "Lucro Líquido", _fmt(lucro_est), "📈",
         COR_VERDE_CLARO, cor_lucro_val,
         sub=f"Margem: {margem_est:.1f}%")

    # ── CARD STATUS DE PAGAMENTO ─────────────────────────────────────
    try:
        rec_paga, rec_nao_paga, n_pagos, n_nao_pagos = controlador.resumo_pagamentos(periodo)
    except Exception:
        rec_paga, rec_nao_paga, n_pagos, n_nao_pagos = 0.0, 0.0, 0, 0

    card_pago = _card(area)
    card_pago.pack(fill="x", padx=28, pady=(0, 16))
    ctk.CTkLabel(card_pago, text="Pagamentos: Recebido vs. Pendente",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 4))
    ctk.CTkLabel(card_pago, text="Receita recebida vs. pedidos ainda nao pagos no periodo.",
                 font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(0, 10))

    linha_pago_stat = ctk.CTkFrame(card_pago, fg_color="transparent")
    linha_pago_stat.pack(fill="x", padx=16, pady=(0, 14))
    total_rec_stat = (rec_paga + rec_nao_paga) or 1

    for titulo_s, valor_r_s, valor_n_s, cor_bg_s, cor_txt_s in [
        ("Recebido (Pagos)",    _fmt(rec_paga),     f"{n_pagos} pedido(s)",     COR_VERDE_CLARO, COR_VERDE),
        ("Pendente (Nao Pagos)", _fmt(rec_nao_paga), f"{n_nao_pagos} pedido(s)", "#FEE2E2",       COR_PRIMARIA),
    ]:
        bloco_s = ctk.CTkFrame(linha_pago_stat, fg_color=cor_bg_s, corner_radius=10)
        bloco_s.pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkLabel(bloco_s, text=titulo_s, font=("Arial", 12, "bold"), text_color=cor_txt_s).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(bloco_s, text=valor_r_s, font=("Arial", 20, "bold"), text_color=cor_txt_s).pack(anchor="w", padx=14)
        ctk.CTkLabel(bloco_s, text=valor_n_s, font=("Arial", 11), text_color=cor_txt_s).pack(anchor="w", padx=14, pady=(0, 10))

    pct_pago = int(rec_paga / total_rec_stat * 100)
    barra_f = ctk.CTkFrame(card_pago, fg_color="#F0FDF4", corner_radius=0, height=26)
    barra_f.pack(fill="x")
    barra_f.pack_propagate(False)
    ctk.CTkLabel(barra_f, text=f"  {pct_pago}% recebido", font=("Arial", 11, "bold"), text_color=COR_VERDE).pack(side="left")
    ctk.CTkLabel(barra_f, text=f"{100-pct_pago}% pendente  ", font=("Arial", 11), text_color=COR_PRIMARIA).pack(side="right")

    # ── ANÁLISE DE LUCRO ──────────────────────────────────────────────
    card_lucro = _card(area)
    card_lucro.pack(fill="x", padx=28, pady=(0, 16))
    ctk.CTkLabel(card_lucro, text="💰  Análise de Lucro por Produto",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 4))
    ctk.CTkLabel(card_lucro,
                 text="Baseado no custo cadastrado em cada produto. Cadastre custos para cálculos precisos.",
                 font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(0, 8))

    # Resumo financeiro
    resumo_fin = ctk.CTkFrame(card_lucro, fg_color="transparent")
    resumo_fin.pack(fill="x", padx=16, pady=(0, 10))

    for titulo, val, cor in [
        ("Receita", _fmt(receita), COR_PRIMARIA),
        ("Custo Estimado", _fmt(custo_est), COR_AMBER),
        ("Lucro Estimado", _fmt(lucro_est), COR_VERDE if lucro_est >= 0 else COR_PRIMARIA),
        ("Margem", f"{margem_est:.1f}%", COR_VERDE if margem_est >= 20 else COR_AMBER),
    ]:
        bloco = ctk.CTkFrame(resumo_fin, fg_color="#F5F0EE", corner_radius=8)
        bloco.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(bloco, text=titulo, font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(pady=(8, 2))
        ctk.CTkLabel(bloco, text=val, font=("Arial", 15, "bold"), text_color=cor).pack(pady=(0, 8))

    # Tabela produtos com lucro
    try:
        lucro_por_prod = controlador.lucro_por_produto(periodo)
    except Exception:
        lucro_por_prod = []

    if lucro_por_prod:
        cab_frame = ctk.CTkFrame(card_lucro, fg_color="#F5F0EE", corner_radius=0, height=36)
        cab_frame.pack(fill="x", padx=0)
        cab_frame.pack_propagate(False)
        ctk.CTkLabel(cab_frame, text="", width=16).pack(side="left")
        ctk.CTkLabel(cab_frame, text="Produto",       width=200, anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkLabel(cab_frame, text="Receita",       width=130, anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkLabel(cab_frame, text="Custo Est.",    width=130, anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkLabel(cab_frame, text="Lucro",         width=130, anchor="w", font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkFrame(card_lucro, height=1, fg_color=COR_BORDA).pack(fill="x")

        for idx, (nome, rec, cst, luc) in enumerate(lucro_por_prod):
            cor_linha = COR_CARD if idx % 2 == 0 else "#FAF5F3"
            cor_luc = COR_VERDE if luc >= 0 else COR_PRIMARIA
            linha = ctk.CTkFrame(card_lucro, fg_color=cor_linha, corner_radius=0, height=40)
            linha.pack(fill="x")
            linha.pack_propagate(False)
            ctk.CTkLabel(linha, text="", width=16).pack(side="left")
            ctk.CTkLabel(linha, text=nome[:26],     width=200, anchor="w", font=("Arial", 13), text_color=COR_TEXTO).pack(side="left")
            ctk.CTkLabel(linha, text=_fmt(rec),     width=130, anchor="w", font=("Arial", 13), text_color=COR_TEXTO).pack(side="left")
            ctk.CTkLabel(linha, text=_fmt(cst),     width=130, anchor="w", font=("Arial", 13), text_color=COR_AMBER).pack(side="left")
            ctk.CTkLabel(linha, text=_fmt(luc),     width=130, anchor="w", font=("Arial", 13, "bold"), text_color=cor_luc).pack(side="left")
            if idx < len(lucro_por_prod) - 1:
                ctk.CTkFrame(card_lucro, height=1, fg_color=COR_BORDA).pack(fill="x")
    else:
        ctk.CTkLabel(card_lucro,
                     text="Sem vendas no período ou nenhum custo cadastrado nos produtos.",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(pady=16)

    ctk.CTkFrame(card_lucro, height=10, fg_color="transparent").pack()

    # ── VENDAS POR DIA + TOP PRODUTOS ─────────────────────────────────
    linha_mid = ctk.CTkFrame(area, fg_color="transparent")
    linha_mid.pack(fill="x", padx=28, pady=(0, 16))

    card_dias = _card(linha_mid)
    card_dias.pack(side="left", fill="both", expand=True, padx=(0, 14))
    ctk.CTkLabel(card_dias, text="📊  Vendas por Dia",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 10))

    try:
        vendas_dia = controlador.vendas_por_dia(periodo)
    except Exception:
        vendas_dia = []

    _tabela_tres_colunas(card_dias,
                         ["Dia", "Pedidos", "Receita"],
                         vendas_dia,
                         cor_col2=COR_PRIMARIA,
                         cor_col3=COR_PRIMARIA)

    card_prod = _card(linha_mid, width=300)
    card_prod.pack(side="left", fill="y")
    card_prod.pack_propagate(False)
    ctk.CTkLabel(card_prod, text="🏆  Top Produtos",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 8))

    try:
        top_prod = controlador.performance_produtos(periodo)
    except Exception:
        top_prod = []

    medalhas = ["🥇", "🥈", "🥉"]
    for idx, (nome, qtd, receita_p) in enumerate(top_prod[:5]):
        med = medalhas[idx] if idx < 3 else "  "
        row = ctk.CTkFrame(card_prod, fg_color="#FAF5F3", corner_radius=8)
        row.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(row, text=med, font=("Arial", 18)).pack(side="left", padx=(10, 6), pady=8)
        col = ctk.CTkFrame(row, fg_color="transparent")
        col.pack(side="left", fill="x", expand=True, pady=8)
        ctk.CTkLabel(col, text=nome[:22], font=("Arial", 13, "bold"), text_color=COR_TEXTO).pack(anchor="w")
        ctk.CTkLabel(col, text=f"{qtd} unid.  ·  {_fmt(receita_p)}",
                     font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(anchor="w")

    if not top_prod:
        ctk.CTkLabel(card_prod, text="Sem dados.",
                     font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(pady=16)
    ctk.CTkFrame(card_prod, height=10, fg_color="transparent").pack()

    # ── MÉTODOS DE PAGAMENTO ──────────────────────────────────────────
    card_pag = _card(area)
    card_pag.pack(fill="x", padx=28, pady=(0, 16))
    ctk.CTkLabel(card_pag, text="💳  Métodos de Pagamento",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 8))

    try:
        metodos = controlador.metodos_pagamento(periodo)
    except Exception:
        metodos = []

    linha_pag = ctk.CTkFrame(card_pag, fg_color="transparent")
    linha_pag.pack(fill="x", padx=14, pady=(0, 14))

    cores_m = [COR_PRIMARIA, COR_AZUL, COR_VERDE, COR_AMBER, COR_ROXO]
    bgs_m   = ["#FEE2E2", COR_AZUL_CLARO, COR_VERDE_CLARO, COR_AMBER_CLARO, COR_ROXO_CLARO]
    total_pag = sum(q for _, q, _, _, _ in metodos) or 1

    for idx, (metodo, qtd, receita_m, pagos_m, nao_pagos_m) in enumerate(metodos):
        cor = cores_m[idx % len(cores_m)]
        bg  = bgs_m[idx % len(bgs_m)]
        pct = int(qtd * 100 / total_pag)

        item = ctk.CTkFrame(linha_pag, fg_color=bg, corner_radius=10)
        item.pack(side="left", padx=(0, 10), expand=True, fill="x", pady=4)
        ctk.CTkLabel(item, text=metodo or "Não informado",
                     font=("Arial", 14, "bold"), text_color=cor).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(item, text=f"{qtd} pedidos · {pct}%",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=12)
        ctk.CTkLabel(item, text=_fmt(receita_m),
                     font=("Arial", 15, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=12, pady=(2, 10))

    if not metodos:
        ctk.CTkLabel(card_pag, text="Sem dados no período.",
                     font=("Arial", 14), text_color=COR_TEXTO_SUB).pack(pady=16)

    # ── HORÁRIOS DE MAIOR MOVIMENTO ───────────────────────────────────
    card_hora = _card(area)
    card_hora.pack(fill="x", padx=28, pady=(0, 16))
    ctk.CTkLabel(card_hora, text="🕐  Horários de Maior Movimento",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 10))

    try:
        horarios = controlador.horarios_movimento(periodo)
    except Exception:
        horarios = []

    _tabela_tres_colunas(card_hora,
                         ["Horário", "Pedidos", "Receita"],
                         horarios,
                         cor_col2=COR_PRIMARIA,
                         cor_col3=COR_PRIMARIA)

    # ── ESTOQUE: RESUMO GERAL ─────────────────────────────────────────
    try:
        total_itens, itens_criticos, valor_estoque = controlador.resumo_estoque()
    except Exception:
        total_itens, itens_criticos, valor_estoque = 0, 0, 0.0

    card_est = _card(area)
    card_est.pack(fill="x", padx=28, pady=(0, 16))
    ctk.CTkLabel(card_est, text="📦  Estoque",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 2))
    ctk.CTkLabel(card_est, text="Situação atual do estoque e movimentações no período.",
                 font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(0, 12))

    linha_est_resumo = ctk.CTkFrame(card_est, fg_color="transparent")
    linha_est_resumo.pack(fill="x", padx=16, pady=(0, 12))

    for tit_e, val_e, cor_bg_e, cor_e in [
        ("Total de Itens",     str(total_itens),     COR_AZUL_CLARO,  COR_AZUL),
        ("Itens Críticos",     str(itens_criticos),  "#FEE2E2" if itens_criticos > 0 else COR_VERDE_CLARO,
                                                     COR_PRIMARIA if itens_criticos > 0 else COR_VERDE),
        ("Valor em Estoque",   _fmt(valor_estoque),  COR_AMBER_CLARO, COR_AMBER),
    ]:
        bl = ctk.CTkFrame(linha_est_resumo, fg_color=cor_bg_e, corner_radius=10)
        bl.pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkLabel(bl, text=tit_e, font=("Arial", 11), text_color=cor_e).pack(pady=(10, 2))
        ctk.CTkLabel(bl, text=val_e, font=("Arial", 20, "bold"), text_color=cor_e).pack(pady=(0, 10))

    # Itens críticos (abaixo do mínimo)
    try:
        criticos = controlador.itens_criticos_estoque()
    except Exception:
        criticos = []

    if criticos:
        ctk.CTkLabel(card_est, text="⚠️  Itens Abaixo do Mínimo",
                     font=("Arial", 14, "bold"), text_color=COR_PRIMARIA).pack(anchor="w", padx=16, pady=(4, 6))

        cab_crit = ctk.CTkFrame(card_est, fg_color="#F5F0EE", corner_radius=0, height=34)
        cab_crit.pack(fill="x")
        cab_crit.pack_propagate(False)
        for txt_c, w_c in [("", 16), ("Item", 200), ("Categoria", 120),
                            ("Atual", 80), ("Mínimo", 80), ("Und.", 70)]:
            ctk.CTkLabel(cab_crit, text=txt_c, width=w_c, anchor="w",
                         font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkFrame(card_est, height=1, fg_color=COR_BORDA).pack(fill="x")

        for idx, (nome, cat, atual, minimo, und, _preco) in enumerate(criticos):
            cor_ln = COR_CARD if idx % 2 == 0 else "#FAF5F3"
            ln = ctk.CTkFrame(card_est, fg_color=cor_ln, corner_radius=0, height=38)
            ln.pack(fill="x")
            ln.pack_propagate(False)
            ctk.CTkLabel(ln, text="", width=16).pack(side="left")
            ctk.CTkLabel(ln, text=nome[:26],  width=200, anchor="w", font=("Arial", 13), text_color=COR_TEXTO).pack(side="left")
            ctk.CTkLabel(ln, text=cat,         width=120, anchor="w", font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left")
            ctk.CTkLabel(ln, text=f"{atual:.1f}", width=80, anchor="w", font=("Arial", 13, "bold"), text_color=COR_PRIMARIA).pack(side="left")
            ctk.CTkLabel(ln, text=f"{minimo:.1f}", width=80, anchor="w", font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left")
            ctk.CTkLabel(ln, text=und,          width=70, anchor="w", font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="left")
            if idx < len(criticos) - 1:
                ctk.CTkFrame(card_est, height=1, fg_color=COR_BORDA).pack(fill="x")
    else:
        ctk.CTkLabel(card_est, text="✅  Todos os itens estão acima do estoque mínimo.",
                     font=("Arial", 13), text_color=COR_VERDE).pack(pady=(0, 6))

    # Movimentações no período
    try:
        movs = controlador.movimentacoes_estoque(periodo)
    except Exception:
        movs = []

    ctk.CTkLabel(card_est, text="🔄  Movimentações no Período",
                 font=("Arial", 14, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(12, 6))

    if movs:
        cab_mov = ctk.CTkFrame(card_est, fg_color="#F5F0EE", corner_radius=0, height=34)
        cab_mov.pack(fill="x")
        cab_mov.pack_propagate(False)
        for txt_m, w_m in [("", 16), ("Item", 180), ("Tipo", 90),
                            ("Qtd.", 80), ("Und.", 70), ("Observação", 200), ("Data", 90)]:
            ctk.CTkLabel(cab_mov, text=txt_m, width=w_m, anchor="w",
                         font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkFrame(card_est, height=1, fg_color=COR_BORDA).pack(fill="x")

        cores_tipo = {"Entrada": COR_VERDE, "Saída": COR_PRIMARIA, "Ajuste": COR_AMBER}
        for idx, (nome, tipo, qtd, und, obs, dia) in enumerate(movs):
            cor_ln = COR_CARD if idx % 2 == 0 else "#FAF5F3"
            cor_tipo = cores_tipo.get(tipo, COR_TEXTO_SUB)
            ln = ctk.CTkFrame(card_est, fg_color=cor_ln, corner_radius=0, height=38)
            ln.pack(fill="x")
            ln.pack_propagate(False)
            ctk.CTkLabel(ln, text="", width=16).pack(side="left")
            ctk.CTkLabel(ln, text=nome[:22],  width=180, anchor="w", font=("Arial", 13), text_color=COR_TEXTO).pack(side="left")
            ctk.CTkLabel(ln, text=tipo,        width=90,  anchor="w", font=("Arial", 13, "bold"), text_color=cor_tipo).pack(side="left")
            ctk.CTkLabel(ln, text=f"{qtd:.1f}", width=80, anchor="w", font=("Arial", 13), text_color=COR_TEXTO).pack(side="left")
            ctk.CTkLabel(ln, text=und,          width=70,  anchor="w", font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="left")
            ctk.CTkLabel(ln, text=(obs[:24] if obs else "—"), width=200, anchor="w", font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="left")
            ctk.CTkLabel(ln, text=str(dia)[:10], width=90, anchor="w", font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="left")
            if idx < len(movs) - 1:
                ctk.CTkFrame(card_est, height=1, fg_color=COR_BORDA).pack(fill="x")
    else:
        ctk.CTkLabel(card_est, text="Nenhuma movimentação no período.",
                     font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(pady=(0, 6))

    # Consumo por produto (só aparece se a tabela produto_ingredientes existir)
    try:
        consumo = controlador.consumo_por_produto(periodo)
    except Exception:
        consumo = []

    if consumo:
        ctk.CTkLabel(card_est, text="🍕  Consumo de Estoque por Produto Vendido",
                     font=("Arial", 14, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(12, 6))
        cab_cons = ctk.CTkFrame(card_est, fg_color="#F5F0EE", corner_radius=0, height=34)
        cab_cons.pack(fill="x")
        cab_cons.pack_propagate(False)
        for txt_c, w_c in [("", 16), ("Produto", 190), ("Qtd. Vendida", 110),
                            ("Ingrediente", 160), ("Consumido", 110), ("Und.", 70)]:
            ctk.CTkLabel(cab_cons, text=txt_c, width=w_c, anchor="w",
                         font=("Arial", 12, "bold"), text_color=COR_TEXTO_SUB).pack(side="left")
        ctk.CTkFrame(card_est, height=1, fg_color=COR_BORDA).pack(fill="x")
        for idx, (prod, qtd_v, cons, item, und) in enumerate(consumo):
            cor_ln = COR_CARD if idx % 2 == 0 else "#FAF5F3"
            ln = ctk.CTkFrame(card_est, fg_color=cor_ln, corner_radius=0, height=38)
            ln.pack(fill="x")
            ln.pack_propagate(False)
            ctk.CTkLabel(ln, text="", width=16).pack(side="left")
            ctk.CTkLabel(ln, text=prod[:24],   width=190, anchor="w", font=("Arial", 13), text_color=COR_TEXTO).pack(side="left")
            ctk.CTkLabel(ln, text=str(qtd_v),  width=110, anchor="w", font=("Arial", 13), text_color=COR_AZUL).pack(side="left")
            ctk.CTkLabel(ln, text=item[:20],   width=160, anchor="w", font=("Arial", 13), text_color=COR_TEXTO_SUB).pack(side="left")
            ctk.CTkLabel(ln, text=f"{cons:.2f}", width=110, anchor="w", font=("Arial", 13, "bold"), text_color=COR_AMBER).pack(side="left")
            ctk.CTkLabel(ln, text=und,          width=70,  anchor="w", font=("Arial", 12), text_color=COR_TEXTO_SUB).pack(side="left")
            if idx < len(consumo) - 1:
                ctk.CTkFrame(card_est, height=1, fg_color=COR_BORDA).pack(fill="x")

    ctk.CTkFrame(card_est, height=10, fg_color="transparent").pack()

    # ── CARD CUSTO TOTAL (abaixo de movimentações) ────────────────────
    card_custo = _card(area)
    card_custo.pack(fill="x", padx=28, pady=(0, 28))

    ctk.CTkLabel(card_custo, text="💸  Custo Total",
                 font=("Arial", 16, "bold"), text_color=COR_TEXTO).pack(anchor="w", padx=16, pady=(14, 2))
    ctk.CTkLabel(card_custo,
                 text="Resumo do que foi gasto, lucro esperado e valor investido em estoque.",
                 font=("Arial", 11), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(0, 12))

    # Linha 1: Quanto foi Gasto | Quanto vai Ganhar
    linha_custo1 = ctk.CTkFrame(card_custo, fg_color="transparent")
    linha_custo1.pack(fill="x", padx=16, pady=(0, 10))

    bloco_gasto = ctk.CTkFrame(linha_custo1, fg_color=COR_AMBER_CLARO, corner_radius=12)
    bloco_gasto.pack(side="left", expand=True, fill="x", padx=(0, 10))
    ctk.CTkLabel(bloco_gasto, text="💸  Quanto foi Gasto",
                 font=("Arial", 13, "bold"), text_color=COR_AMBER).pack(anchor="w", padx=16, pady=(14, 4))
    ctk.CTkLabel(bloco_gasto, text=_fmt(custo_est),
                 font=("Arial", 26, "bold"), text_color=COR_AMBER).pack(anchor="w", padx=16)
    ctk.CTkLabel(bloco_gasto, text="Custo estimado com base nos produtos vendidos",
                 font=("Arial", 10), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(2, 14))

    cor_ganho = COR_VERDE if lucro_est >= 0 else COR_PRIMARIA
    cor_ganho_bg = COR_VERDE_CLARO if lucro_est >= 0 else "#FEE2E2"
    bloco_ganho = ctk.CTkFrame(linha_custo1, fg_color=cor_ganho_bg, corner_radius=12)
    bloco_ganho.pack(side="left", expand=True, fill="x")
    ctk.CTkLabel(bloco_ganho, text="📈  Quanto vai Ganhar (Lucro)",
                 font=("Arial", 13, "bold"), text_color=cor_ganho).pack(anchor="w", padx=16, pady=(14, 4))
    ctk.CTkLabel(bloco_ganho, text=_fmt(lucro_est),
                 font=("Arial", 26, "bold"), text_color=cor_ganho).pack(anchor="w", padx=16)
    ctk.CTkLabel(bloco_ganho, text="Lucro estimado com base nos custos dos produtos",
                 font=("Arial", 10), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(2, 14))

    # Linha 2: Custo de Produto | Custo de Estoque
    ctk.CTkFrame(card_custo, height=1, fg_color=COR_BORDA).pack(fill="x", padx=16, pady=(0, 10))

    linha_custo2 = ctk.CTkFrame(card_custo, fg_color="transparent")
    linha_custo2.pack(fill="x", padx=16, pady=(0, 16))

    bloco_prod = ctk.CTkFrame(linha_custo2, fg_color="#FFF7ED", corner_radius=12)
    bloco_prod.pack(side="left", expand=True, fill="x", padx=(0, 10))
    ctk.CTkLabel(bloco_prod, text="🛒  Custo de Produto",
                 font=("Arial", 12, "bold"), text_color="#C2410C").pack(anchor="w", padx=16, pady=(12, 2))
    ctk.CTkLabel(bloco_prod, text=_fmt(custo_est),
                 font=("Arial", 20, "bold"), text_color="#C2410C").pack(anchor="w", padx=16)
    ctk.CTkLabel(bloco_prod, text="Total gasto em produtos para atender os pedidos do período",
                 font=("Arial", 10), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(2, 12))

    bloco_est_custo = ctk.CTkFrame(linha_custo2, fg_color=COR_AZUL_CLARO, corner_radius=12)
    bloco_est_custo.pack(side="left", expand=True, fill="x")
    ctk.CTkLabel(bloco_est_custo, text="📦  Custo de Estoque",
                 font=("Arial", 12, "bold"), text_color=COR_AZUL).pack(anchor="w", padx=16, pady=(12, 2))
    ctk.CTkLabel(bloco_est_custo, text=_fmt(valor_estoque),
                 font=("Arial", 20, "bold"), text_color=COR_AZUL).pack(anchor="w", padx=16)
    ctk.CTkLabel(bloco_est_custo, text="Valor total investido atualmente no estoque",
                 font=("Arial", 10), text_color=COR_TEXTO_SUB).pack(anchor="w", padx=16, pady=(2, 12))
