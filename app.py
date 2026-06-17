import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import time
import os
import dados as db
import io

# ── CONFIGURAÇÃO DE PÁGINA MASTER ──────────────────────────────────────────────
st.set_page_config(page_title="Programa Essência", page_icon="💡", layout="wide", initial_sidebar_state="expanded")

def obter_bg_base64(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as image_file: return base64.b64encode(image_file.read()).decode()
    return ""

bg_base64 = obter_bg_base64("image_7e68ea.jpg")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .fade-in { animation: fadeIn 0.5s forwards; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.05) !important; border-radius: 8px !important;
        padding: 12px 16px !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 8px !important; width: 100% !important; display: flex !important;
        align-items: center !important; transition: all 0.2s ease-in-out !important; cursor: pointer !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p { color: #ffffff !important; font-size: 15px !important; margin: 0 !important; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background-color: rgba(255, 255, 255, 0.1) !important; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background-color: #ffffff !important; border-color: #ffffff !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { font-weight: 700 !important; color: #185FA5 !important; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    .stButton > button { background-color: #185FA5 !important; color: white !important; border-radius: 8px !important; font-weight: 600 !important; border: none !important; }
    .stButton > button:hover { background-color: #104a85 !important; }
    .kpi-container { background: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; }
    .kpi-title { font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; }
    .kpi-value { font-size: 26px; font-weight: 700; color: #0f172a; margin-top: 8px; }
    .badge { font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; display: inline-block; }
    .badge-n0 { background: #FEE2E2; color: #991B1B; } .badge-n1 { background: #E0F2FE; color: #1E3A8A; }
    .badge-n2 { background: #DCFCE7; color: #166534; } .badge-n3 { background: #FEF3C7; color: #92400E; }
    .badge-n4 { background: #D1FAE5; color: #14532D; }
    .comentario-box { background: #f8fafc; border-left: 4px solid #185FA5; padding: 12px; border-radius: 4px 8px 8px 4px; font-size: 13px; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("usuario"):
    st.markdown(f"""
    <style>
        .stApp {{ background-image: url("data:image/jpg;base64,{bg_base64}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        [data-testid="stForm"] {{ background: rgba(255, 255, 255, 0.95) !important; backdrop-filter: blur(15px) !important; padding: 40px; border-radius: 16px; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.5); max-width: 420px; margin: 0 auto; }}
        div[data-baseweb="input"] {{ position: relative !important; height: 44px !important; background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; transition: all 0.2s ease-in-out !important; }}
        div[data-baseweb="input"]:focus-within {{ border-color: #185FA5 !important; box-shadow: 0 0 0 2px rgba(24, 95, 165, 0.2) !important; }}
        div[data-baseweb="input"] input {{ padding-left: 42px !important; height: 100% !important; background-color: transparent !important; }}
        div[data-baseweb="input"]:has(input[aria-label*="E-mail"])::before {{ content: ''; position: absolute !important; left: 14px !important; top: 50% !important; transform: translateY(-50%) !important; width: 18px !important; height: 18px !important; background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z'%3E%3C/path%3E%3Cpolyline points='22,6 12,13 2,6'%3E%3C/polyline%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: center; pointer-events: none; }}
        div[data-baseweb="input"]:has(input[type="password"])::before {{ content: ''; position: absolute !important; left: 14px !important; top: 50% !important; transform: translateY(-50%) !important; width: 18px !important; height: 18px !important; background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2' ry='2'%3E%3C/rect%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'%3E%3C/path%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: center; pointer-events: none; }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""<style>[data-testid="stForm"] { background: #ffffff !important; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; width: 100%; }</style>""", unsafe_allow_html=True)

if "usuario" not in st.session_state: st.session_state.usuario = None

def brl(v):
    try: return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def gerar_badge(nivel):
    n = str(nivel)[:2]
    classes = {"N0": "badge-n0", "N1": "badge-n1", "N2": "badge-n2", "N3": "badge-n3", "N4": "badge-n4"}
    return f'<span class="badge {classes.get(n, "badge-n1")}">{nivel}</span>'

# ── TELA DE LOGIN ────────────────────────────────────────────────────────
def tela_login():
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h2 style='text-align: center; color: #0f172a;'>Bem-vindo(a)</h2>", unsafe_allow_html=True)
            login = st.text_input("Usuário (Login)", placeholder="ex: usuário", icon=":material/person:")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", icon=":material/lock:")
            if st.form_submit_button("Entrar", width="stretch", type="primary"):
                if login.strip() and senha.strip():
                    user_info = db.autenticar(login.strip(), senha.strip())
                    if user_info:
                        st.session_state.usuario = user_info
                        st.rerun()
                    else: st.error("Usuário ou senha incorretos (ou inativo).")
                else: st.warning("Preencha login e senha.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── NAVEGAÇÃO ────────────────────────────────────────────────────────────
def painel_principal():
    u = st.session_state.usuario
    hora = datetime.now().hour
    saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px 0px 20px 0px;">
            <span style="font-size: 18px; font-weight: 700; color: #ffffff;">{saudacao}, {u['nome'].split()[0]}!</span>
            <p style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Perfil: {u['perfil'].upper()}</p>
        </div>
        """, unsafe_allow_html=True)
        opcoes_menu = []
        if u["perfil"] in ("craque", "lider", "adm"):
            opcoes_menu.extend(["Cadastro de Oportunidade", "Minhas Oportunidades"])
        if u["perfil"] in ("lider", "adm", "diretoria"):
            opcoes_menu.append("Painel Executivo")
        if u["perfil"] == "adm":
            opcoes_menu.extend(["Comitê de Despesas (N1)", "Validação Controladoria", "Painel de Acessos"])
        pagina = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        if st.button("Sair do Sistema", use_container_width=True):
            st.session_state.usuario = None; st.rerun()

    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    if pagina == "Cadastro de Oportunidade": pagina_cadastro()
    elif pagina == "Minhas Oportunidades": pagina_tabela()
    elif pagina == "Painel Executivo": pagina_painel_integrado()
    elif pagina == "Comitê de Despesas (N1)": pagina_comite()
    elif pagina == "Validação Controladoria": pagina_controladoria()
    elif pagina == "Painel de Acessos": pagina_admin()
    st.markdown('</div>', unsafe_allow_html=True)

# ── CADASTRO ─────────────────────────────────────────────────────────────
def pagina_cadastro():
    u = st.session_state.usuario
    st.markdown('<h2 style="color: #0f172a;">Cadastro de Oportunidade</h2>', unsafe_allow_html=True)
    df_pc = db.ler_plano_contas()

    with st.container(border=True):
        st.markdown("##### 1. Detalhes do Escopo")
        titulo = st.text_input("Título da Melhoria *", max_chars=50)
        descricao = st.text_area("Descrição da Melhoria *", max_chars=600)
        col1, col2 = st.columns(2)
        with col1:
            dono = st.text_input("Dono da Oportunidade *")
            filial_sel = st.selectbox("Filial *", [""] + db.ler_filiais())
        with col2:
            cc_dono = st.selectbox("Centro de Custo (CC Dono) *", [""] + db.ler_centros_custo())

        st.markdown("<br>##### 2. Classificação Contábil", unsafe_allow_html=True)
        col_g2, col_g3 = st.columns(2)
        with col_g2:
            contas_orc_filtradas = sorted(df_pc["ContaOrc"].unique().tolist())
            conta_orc_sel = st.selectbox("Conta Orçamento *", [""] + contas_orc_filtradas)
        with col_g3:
            contas_cont_filtradas = df_pc[df_pc["ContaOrc"] == conta_orc_sel] if conta_orc_sel else pd.DataFrame()
            opcoes_conta_cont = [f"{row['Código']} - {row['ContaCont']}" for _, row in contas_cont_filtradas.iterrows()]
            conta_cont_sel = st.selectbox("Conta Contábil / Código *", [""] + opcoes_conta_cont)

        frente_detectada = ""
        if conta_cont_sel:
            codigo_selecionado = conta_cont_sel.split(" - ")[0]
            try: frente_detectada = df_pc[df_pc["Código"] == codigo_selecionado].iloc[0]["Frente"]
            except: pass
            st.info(f"Frente de Negócio atrelada automaticamente: **{frente_detectada}**")

        st.markdown("<br>##### 3. Planejamento Financeiro Inicial", unsafe_allow_html=True)
        ganho_2026 = st.number_input("Ganho Estimado 2026 (R$) *", min_value=0.0, step=100.0, key="ganho_2026_cadastro")

        if st.button("Salvar Registro (N1)", use_container_width=True, type="primary", key="btn_salvar_n1"):
            if not (titulo.strip() and descricao.strip() and dono.strip() and cc_dono and conta_orc_sel and conta_cont_sel and filial_sel):
                st.error("Preencha todos os campos obrigatórios (*).")
            else:
                dados_op = {
                    "titulo": titulo, "descricao": descricao, "dono": dono,
                    "cc_dono": cc_dono, "conta_orc": conta_orc_sel,
                    "conta_cont": conta_cont_sel.split(" - ")[-1],
                    "filial": filial_sel,
                    "frente_automatica": frente_detectada, "ganho_2026": ganho_2026
                }
                db.cadastrar_oportunidade(dados_op, u)
                st.success("Oportunidade enviada para aprovação do Comitê (N1)!")
                time.sleep(1.5); st.rerun()

# ── MINHAS OPORTUNIDADES — FORMATO SCO ───────────────────────────────────
def pagina_tabela():
    u = st.session_state.usuario
    st.markdown('<h2 style="color: #0f172a;">Minhas Oportunidades</h2>', unsafe_allow_html=True)

    df = db.ler_oportunidades()
    if df.empty:
        st.info("Nenhuma oportunidade cadastrada.")
        return

    # Filtro por perfil
    if u["perfil"] == "craque":
        df = df[df["Craque"].str.lower() == u["nome"].lower()]
    elif u["perfil"] == "lider":
        df = df[df["Frente de Negócio"].str.lower() == u["frente"].lower()]

    if df.empty:
        st.info("Nenhuma oportunidade encontrada para o seu perfil.")
        return

    # Garante colunas de meses e trimestres
    for m in range(1, 13):
        col = f"Mês {m}"
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0.0)

    df["Total Estimado 2026"] = pd.to_numeric(df["Total Estimado 2026"], errors="coerce").fillna(0.0)
    df["Nível"] = df["Nível"].astype(str).str.strip()
    df["1° TRI"] = df["Mês 1"] + df["Mês 2"] + df["Mês 3"]
    df["2° TRI"] = df["Mês 4"] + df["Mês 5"] + df["Mês 6"]
    df["3° TRI"] = df["Mês 7"] + df["Mês 8"] + df["Mês 9"]
    df["4° TRI"] = df["Mês 10"] + df["Mês 11"] + df["Mês 12"]

    # ── FILTROS ────────────────────────────────────────────────────────────────
    st.markdown("##### Filtros")
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    with col_f1:
        filtro_status = st.selectbox("Status", ["Todos"] + sorted(df["Nível"].unique().tolist()), key="f_status")
    with col_f2:
        filtro_frente = st.selectbox("Frente", ["Todos"] + sorted(df["Frente de Negócio"].dropna().unique().tolist()), key="f_frente")
    with col_f3:
        filtro_dono = st.selectbox("Dono", ["Todos"] + sorted(df["Dono da Oportunidade"].dropna().unique().tolist()), key="f_dono")
    with col_f4:
        filtro_cc = st.selectbox("CC Dono", ["Todos"] + sorted(df["CC Dono"].dropna().unique().tolist()), key="f_cc")
    with col_f5:
        filtro_filial = st.selectbox("Filial", ["Todos"] + sorted(df["Filial"].dropna().unique().tolist()), key="f_filial")

    # Aplica filtros
    df_filtrado = df.copy()
    if filtro_status != "Todos": df_filtrado = df_filtrado[df_filtrado["Nível"] == filtro_status]
    if filtro_frente != "Todos": df_filtrado = df_filtrado[df_filtrado["Frente de Negócio"] == filtro_frente]
    if filtro_dono   != "Todos": df_filtrado = df_filtrado[df_filtrado["Dono da Oportunidade"] == filtro_dono]
    if filtro_cc     != "Todos": df_filtrado = df_filtrado[df_filtrado["CC Dono"] == filtro_cc]
    if filtro_filial != "Todos": df_filtrado = df_filtrado[df_filtrado["Filial"] == filtro_filial]

    # ── TABELA FORMATO SCO ─────────────────────────────────────────────────────
    colunas_sel = [c for c in [
        "Título", "Comentário da Semana", "Nível", "Frente de Negócio",
        "Conta Orçamento", "Conta Contábil", "1° TRI", "2° TRI", "3° TRI", "4° TRI",
        "Total Estimado 2026", "Dono da Oportunidade", "CC Dono", "Filial",
        "Data Cadastro (N1)", "ID"
    ] if c in df_filtrado.columns]

    df_display = df_filtrado[colunas_sel].copy().rename(columns={
        "Título": "Descrição da Oportunidade",
        "Nível": "Status",
        "Frente de Negócio": "Grupo Contábil / Frente",
        "Total Estimado 2026": "Total",
        "Dono da Oportunidade": "Dono",
        "Data Cadastro (N1)": "Data N1",
    })

    for col in ["1° TRI", "2° TRI", "3° TRI", "4° TRI", "Total"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda v: f"R$ {float(v):,.0f}".replace(",", ".") if v != "" else "R$ 0"
            )

    st.markdown(f"**{len(df_filtrado)} oportunidade(s) encontrada(s)**")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── PAINEL DE AÇÕES (só líder e adm) ──────────────────────────────────────
    if u["perfil"] in ("lider", "adm"):
        st.markdown("---")
        st.markdown("##### Ações na Oportunidade")

        opcoes_sel = ["Selecione uma oportunidade..."] + [
            f"#{row['ID']} — {str(row.get('Título', row.get('Descrição', '')))[:60]}"
            for _, row in df_filtrado.iterrows()
        ]
        sel = st.selectbox("Selecione para editar", opcoes_sel, key="sel_op")

        if sel != "Selecione uma oportunidade...":
            id_sel = sel.split("—")[0].replace("#", "").strip()
            row = df_filtrado[df_filtrado["ID"] == id_sel].iloc[0]
            nivel_atual = str(row["Nível"]).strip()

            with st.container(border=True):
                st.markdown(f"**{row.get('Título', '')}** — `{nivel_atual}`")

                # Comentário
                with st.form(f"form_coment_{id_sel}"):
                    novo_coment = st.text_area("Adicionar Comentário da Semana:")
                    if st.form_submit_button("💬 Salvar Comentário"):
                        if novo_coment.strip():
                            db.adicionar_comentario(id_sel, novo_coment, u)
                            st.success("Comentário salvo!")
                            st.rerun()
                        else:
                            st.warning("Digite um comentário antes de salvar.")

                # Mudança de nível
                st.markdown("**Movimentar Nível:**")

                if "N2" in nivel_atual:
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("▶ Iniciar Execução (N2 → N3)", key=f"n3_{id_sel}", use_container_width=True):
                            db.movimentar_nivel(id_sel, "N3 - Execução", u)
                            st.success("Movido para N3 - Execução!"); st.rerun()
                    with c2:
                        if st.button("✖ Cancelar (→ N0)", key=f"n0_n2_{id_sel}", use_container_width=True):
                            db.movimentar_nivel(id_sel, "N0 - Cancelada", u)
                            st.success("Oportunidade cancelada."); st.rerun()

                elif "N3" in nivel_atual:
                    submetido = row.get("Submetido Controladoria", False)
                    c1, c2 = st.columns(2)
                    with c1:
                        if not submetido:
                            if st.button("📋 Submeter para Controladoria (→ N4)", key=f"sub_{id_sel}", type="primary", use_container_width=True):
                                db.submeter_para_controladoria(id_sel)
                                st.success("Enviado para validação da Controladoria!"); st.rerun()
                        else:
                            st.warning("⏳ Aguardando validação da Controladoria.")
                    with c2:
                        if st.button("✖ Cancelar (→ N0)", key=f"n0_n3_{id_sel}", use_container_width=True):
                            db.movimentar_nivel(id_sel, "N0 - Cancelada", u)
                            st.success("Oportunidade cancelada."); st.rerun()

                elif "N1" in nivel_atual:
                    st.info("ℹ️ Em N1 — aprovação para N2 é feita pelo Comitê de Despesas.")
                elif "N4" in nivel_atual:
                    st.success("✅ Oportunidade já implementada (N4).")
                elif "N0" in nivel_atual:
                    st.error("Oportunidade cancelada (N0).")

# ── COMITÊ (N1 → N2) ─────────────────────────────────────────────────────
def pagina_comite():
    st.markdown('<h2 style="color: #0f172a;">Comitê de Despesas (Aprovação N1)</h2>', unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: return
    df_n1 = df[df["Nível"] == "N1 - Ideia"]
    if df_n1.empty: st.success("Nenhuma ideia aguardando aprovação no momento."); return
    for _, row in df_n1.iterrows():
        with st.container(border=True):
            titulo_display = row.get("Título", "") if row.get("Título", "") else row['Descrição']
            st.markdown(f"**#{row['ID']} - {titulo_display}**")
            st.write(f"Craque: {row['Craque']} | Filial: {row.get('Filial','')} | Ganho 2026: {brl(row.get('Total Estimado 2026',0))}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Aprovar (Mover p/ N2)", key=f"apr_{row['ID']}", use_container_width=True):
                    db.movimentar_nivel(row['ID'], "N2 - Planejamento", st.session_state.usuario); st.rerun()
            with c2:
                if st.button("❌ Rejeitar (Mover p/ N0)", key=f"rej_{row['ID']}", use_container_width=True):
                    db.movimentar_nivel(row['ID'], "N0 - Cancelada", st.session_state.usuario); st.rerun()

# ── CONTROLADORIA (N3 → N4) ───────────────────────────────────────────────
def pagina_controladoria():
    st.markdown('<h2 style="color: #0f172a;">Validação Controladoria (Aprovação N4)</h2>', unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: return
    df_n3 = df[(df["Nível"] == "N3 - Execução") & (df["Submetido Controladoria"] == True)]
    if df_n3.empty: st.success("Nenhuma ideia aguardando validação de implementação."); return
    for _, row in df_n3.iterrows():
        with st.container(border=True):
            titulo_display = row.get("Título", "") if row.get("Título", "") else row['Descrição']
            st.markdown(f"**#{row['ID']} - {titulo_display}**")
            st.write(f"Frente: {row['Frente de Negócio']} | {brl(row.get('Total Estimado 2026',0))}")
            if st.button("🏆 Validar Savings e Marcar como Implementado (N4)", key=f"val_{row['ID']}", type="primary"):
                db.movimentar_nivel(row['ID'], "N4 - Implementado", st.session_state.usuario); st.rerun()

# ── PAINEL EXECUTIVO ──────────────────────────────────────────────────────
def pagina_painel_integrado():
    u = st.session_state.usuario
    st.markdown('<h2 style="color: #0f172a;">Painel Executivo</h2>', unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: st.info("Sem dados para análise."); return

    df["Nível"] = df["Nível"].astype(str).str.strip()
    df["Frente de Negócio"] = df["Frente de Negócio"].astype(str).str.strip()
    df["Total Estimado 2026"] = pd.to_numeric(df["Total Estimado 2026"], errors='coerce').fillna(0.0)

    if u["perfil"] == "lider": df = df[df["Frente de Negócio"].str.lower() == u["frente"].lower()]
    df_ativas = df[df["Nível"] != "N0 - Cancelada"]

    tab_dash, tab_evo, tab_gerencial, tab_excel = st.tabs(["📊 Dashboard Geral", "📈 Evolução Macro", "📑 Relatório Gerencial", "📥 Base Excel"])

    with tab_dash:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="kpi-container"><div class="kpi-title">Ideias Ativas</div><div class="kpi-value">{len(df_ativas)}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-container"><div class="kpi-title">Potencial 2026</div><div class="kpi-value" style="color: #16a34a;">{brl(df_ativas["Total Estimado 2026"].sum())}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-container"><div class="kpi-title">Implementadas</div><div class="kpi-value">{len(df[df["Nível"] == "N4 - Implementado"])}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-container"><div class="kpi-title">Canceladas</div><div class="kpi-value" style="color: #991B1B;">{len(df[df["Nível"] == "N0 - Cancelada"])}</div></div>', unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1: st.write("Distribuição por Nível"); st.bar_chart(df["Nível"].value_counts(), color="#185FA5")
        with g2: st.write("Potencial por Frente"); st.bar_chart(df_ativas.groupby("Frente de Negócio")["Total Estimado 2026"].sum(), color="#16a34a")

    with tab_evo:
        df_ativas["Semana"] = df_ativas["Data Cadastro (N1)"].apply(lambda x: "Semana " + str(x.split("/")[1]) if pd.notna(x) and x else "Desconhecida")
        evolucao = df_ativas.groupby(["Semana", "Nível"])["Total Estimado 2026"].sum().unstack().fillna(0)
        st.bar_chart(evolucao)

    with tab_gerencial:
        orc_data = db.ler_orcamento()
        frentes = db.ler_frentes()

        if u["perfil"] == "adm":
            with st.expander("⚙️ Ajustar Metas Orçadas (Apenas ADM)"):
                with st.form("form_orc"):
                    cols_orc = st.columns(len(frentes))
                    vals_orc = {}
                    for i, f in enumerate(frentes):
                        vals_orc[f] = cols_orc[i].number_input(f, value=float(orc_data.get(f, 0.0)), step=10000.0)
                    if st.form_submit_button("Salvar Novos Orçamentos", type="primary"):
                        db.salvar_orcamento(vals_orc)
                        st.success("Metas atualizadas!"); time.sleep(1); st.rerun()

        relatorio = []
        for f in frentes:
            realizado = df[(df["Frente de Negócio"] == f) & (df["Nível"] == "N4 - Implementado")]["Total Estimado 2026"].sum()
            orc = orc_data.get(f, 0.0)
            relatorio.append({"Frente": f, "Orçado": brl(orc), "Realizado N4": brl(realizado), "Atingimento": f"{(realizado/orc*100) if orc>0 else 0:.1f}%"})
        st.dataframe(pd.DataFrame(relatorio), use_container_width=True, hide_index=True)

    with tab_excel:
        st.write("Base de dados consolidada com aberturas trimestrais.")
        for m in range(1, 13):
            if f"Mês {m}" not in df.columns: df[f"Mês {m}"] = 0.0
            else: df[f"Mês {m}"] = pd.to_numeric(df[f"Mês {m}"], errors="coerce").fillna(0.0)

        df_ex = pd.DataFrame()
        df_ex["Grupo Contábil"] = df.get("Frente de Negócio", "")
        df_ex["Conta Orçamento"] = df.get("Conta Orçamento", "")
        df_ex["Desc. Conta Contábil"] = df.get("Conta Contábil", "")
        df_ex["Descrição da Oportunidade"] = df.get("Título", df.get("Descrição", ""))
        df_ex["1° TRI"] = df["Mês 1"] + df["Mês 2"] + df["Mês 3"]
        df_ex["2° TRI"] = df["Mês 4"] + df["Mês 5"] + df["Mês 6"]
        df_ex["3° TRI"] = df["Mês 7"] + df["Mês 8"] + df["Mês 9"]
        df_ex["4° TRI"] = df["Mês 10"] + df["Mês 11"] + df["Mês 12"]
        df_ex["Total"] = df["Total Estimado 2026"]
        df_ex["Status"] = df.get("Nível", "")
        df_ex["Dono da Oportunidade"] = df.get("Dono da Oportunidade", "")
        df_ex["Centro de Custo do Dono da Oportunidade"] = df.get("CC Dono", "")
        df_ex["Filial"] = df.get("Filial", "")

        st.dataframe(df_ex, use_container_width=True, hide_index=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_ex.to_excel(writer, index=False, sheet_name='Oportunidades')
        st.download_button(
            label="📥 Fazer Download em Excel (.xlsx)",
            data=buffer.getvalue(), file_name=f"Base_Oportunidades_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel", type="primary"
        )

# ── PAINEL DE ACESSOS ─────────────────────────────────────────────────────
def pagina_admin():
    st.markdown('<h2 style="color: #0f172a;">⚙️ Painel de Acessos e Sistema</h2>', unsafe_allow_html=True)
    tab_novo, tab_edit, tab_import = st.tabs(["➕ Novo Usuário", "✏️ Editar Usuários", "📤 Importar Planilha (Excel)"])

    with tab_novo:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                login = st.text_input("Login (sem @)", key="novo_login")
                email_usuario = st.text_input("E-mail corporativo", key="novo_email")
                nome = st.text_input("Nome Completo", key="novo_nome")
                perfil = st.selectbox("Perfil", ["craque", "lider", "adm", "diretoria"], key="novo_perfil")
            with col2:
                senha = st.text_input("Senha Inicial *", type="password", key="novo_senha")
                frente = st.selectbox("Frente", [""] + db.ler_frentes(), key="novo_frente")
                filial = st.selectbox("Filial", [""] + db.ler_filiais(), key="novo_filial")
            if st.button("Cadastrar Usuário", use_container_width=True, type="primary"):
                if login.strip() and nome.strip() and senha.strip():
                    db.cadastrar_usuario_manual(login, nome, perfil, email_usuario, filial, "", frente, senha)
                    st.success(f"Usuário '{login}' criado com sucesso!")
                else:
                    st.error("Preencha Login, Nome e Senha Inicial.")

    with tab_edit:
        df_usuarios = db.ler_usuarios()
        if not df_usuarios.empty:
            usuario_alvo = st.selectbox("Selecione o Usuário:", [""] + df_usuarios["login"].tolist())
            if usuario_alvo:
                dados_atuais = df_usuarios[df_usuarios["login"] == usuario_alvo].iloc[0]
                with st.form("form_edicao"):
                    c1, c2 = st.columns(2)
                    edit_nome   = c1.text_input("Nome", value=dados_atuais.get("nome", ""))
                    edit_email  = c1.text_input("E-mail", value=dados_atuais.get("email", ""))
                    lista_perfis = ["craque", "lider", "adm", "diretoria"]
                    idx_perfil = lista_perfis.index(dados_atuais.get("perfil", "craque")) if dados_atuais.get("perfil", "craque") in lista_perfis else 0
                    edit_perfil = c1.selectbox("Perfil", lista_perfis, index=idx_perfil)
                    lista_frentes = [""] + db.ler_frentes()
                    idx_frente = lista_frentes.index(dados_atuais.get("frente", "")) if dados_atuais.get("frente", "") in lista_frentes else 0
                    edit_frente = c2.selectbox("Frente", lista_frentes, index=idx_frente)
                    lista_filiais = [""] + db.ler_filiais()
                    filial_atual = dados_atuais.get("filial", "")
                    idx_filial = lista_filiais.index(filial_atual) if filial_atual in lista_filiais else 0
                    edit_filial = c2.selectbox("Filial", lista_filiais, index=idx_filial)
                    edit_senha  = c2.text_input("Nova Senha (deixe em branco para manter)", type="password")
                    if st.form_submit_button("Salvar Alterações", type="primary"):
                        db.atualizar_usuario_completo(usuario_alvo, edit_nome, edit_email, edit_perfil, edit_frente, edit_filial, edit_senha)
                        st.success("Usuário atualizado!"); time.sleep(1); st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown("#### ⚠️ Zona de Perigo")
                    st.write("A exclusão é permanente e o usuário perderá acesso imediatamente.")
                    if st.button(f"🗑️ Excluir '{usuario_alvo}' definitivamente"):
                        db.excluir_usuario(usuario_alvo)
                        st.success(f"Usuário {usuario_alvo} apagado!"); time.sleep(1.5); st.rerun()
        else:
            st.info("Nenhum usuário cadastrado.")

    with tab_import:
        st.write("Faça o upload da planilha base legada. O sistema criará as ideias automaticamente.")
        arquivo_excel = st.file_uploader("Selecione a Planilha (.xlsx)", type=["xlsx"])
        if arquivo_excel and st.button("🚀 Processar e Importar Planilha", type="primary"):
            try:
                df_import = pd.read_excel(arquivo_excel)
                db.importar_base_excel(df_import, st.session_state.usuario)
                st.success("Planilha importada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao ler a planilha: {e}")

def main():
    if not st.session_state.usuario: tela_login()
    else: painel_principal()

if __name__ == "__main__": main()
