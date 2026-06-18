import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import time
import os
import dados as db
import io

st.set_page_config(page_title="Programa Essência", page_icon="Logo Essencia.png", layout="wide", initial_sidebar_state="expanded")

def obter_bg_base64(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as f: return base64.b64encode(f.read()).decode()
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
        background-color: rgba(255,255,255,0.05) !important; border-radius: 8px !important;
        padding: 12px 16px !important; border: 1px solid rgba(255,255,255,0.1) !important;
        margin-bottom: 8px !important; width: 100% !important; display: flex !important;
        align-items: center !important; transition: all 0.2s ease-in-out !important; cursor: pointer !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p { color: #ffffff !important; font-size: 15px !important; margin: 0 !important; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background-color: rgba(255,255,255,0.1) !important; }
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
</style>
""", unsafe_allow_html=True)

if st.session_state.get("usuario"):
    logo_base64 = obter_bg_base64("barra_frigelar.png")
    if logo_base64:
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <img src="data:image/png;base64,{logo_base64}" style="width:100%; display:block;">
        </div>
        """, unsafe_allow_html=True)

if not st.session_state.get("usuario"):
    st.markdown(f"""
    <style>
        .stApp {{ background-image: url("data:image/jpg;base64,{bg_base64}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        [data-testid="stForm"] {{ background: rgba(255,255,255,0.95) !important; backdrop-filter: blur(15px) !important; padding: 40px; border-radius: 16px; box-shadow: 0 12px 32px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.5); max-width: 420px; margin: 0 auto; }}
        div[data-baseweb="input"] {{ position: relative !important; height: 44px !important; background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; transition: all 0.2s ease-in-out !important; }}
        div[data-baseweb="input"]:focus-within {{ border-color: #185FA5 !important; box-shadow: 0 0 0 2px rgba(24,95,165,0.2) !important; }}
        div[data-baseweb="input"] input {{ padding-left: 42px !important; height: 100% !important; background-color: transparent !important; }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""<style>[data-testid="stForm"] { background: #ffffff !important; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; width: 100%; }</style>""", unsafe_allow_html=True)

if "usuario" not in st.session_state: st.session_state.usuario = None

def brl(v):
    try: return f"R$ {float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "R$ 0,00"

def brl_int(v):
    try: return f"R$ {float(v):,.0f}".replace(",",".")
    except: return "R$ 0"

# ── HELPER: monta tabela SCO a partir de um DataFrame ────────────────────────
def montar_tabela_sco(df_in):
    for m in range(1, 13):
        col = f"Mês {m}"
        if col not in df_in.columns: df_in[col] = 0.0
        else: df_in[col] = pd.to_numeric(df_in[col], errors="coerce").fillna(0.0)
    df_in["Total Estimado 2026"] = pd.to_numeric(df_in["Total Estimado 2026"], errors="coerce").fillna(0.0)
    df_in["1° TRI"] = df_in["Mês 1"] + df_in["Mês 2"] + df_in["Mês 3"]
    df_in["2° TRI"] = df_in["Mês 4"] + df_in["Mês 5"] + df_in["Mês 6"]
    df_in["3° TRI"] = df_in["Mês 7"] + df_in["Mês 8"] + df_in["Mês 9"]
    df_in["4° TRI"] = df_in["Mês 10"] + df_in["Mês 11"] + df_in["Mês 12"]

    colunas = [c for c in [
        "Título", "Comentário da Semana", "Nível", "Frente de Negócio",
        "Conta Orçamento", "Conta Contábil", "1° TRI", "2° TRI", "3° TRI", "4° TRI",
        "Total Estimado 2026", "Dono da Oportunidade", "CC Dono", "Filial",
        "Data Cadastro (N1)", "Data Prevista N3", "Data Prevista N4"
    ] if c in df_in.columns]

    df_disp = df_in[colunas].copy().rename(columns={
        "Título": "Descrição da Oportunidade",
        "Nível": "Status",
        "Frente de Negócio": "Grupo Contábil / Frente",
        "Total Estimado 2026": "Total",
        "Dono da Oportunidade": "Dono",
        "Data Cadastro (N1)": "Data N1",
    })
    for col in ["1° TRI","2° TRI","3° TRI","4° TRI","Total"]:
        if col in df_disp.columns:
            df_disp[col] = df_disp[col].apply(lambda v: brl_int(v) if v != "" else "R$ 0")
    return df_disp

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def tela_login():
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h2 style='text-align:center;color:#0f172a;'>Bem-vindo(a)</h2>", unsafe_allow_html=True)
            login = st.text_input("Usuário (Login)", placeholder="ex: usuário", icon=":material/person:")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", icon=":material/lock:")
            if st.form_submit_button("Entrar", width="stretch", type="primary"):
                if login.strip() and senha.strip():
                    user_info = db.autenticar(login.strip(), senha.strip())
                    if user_info: st.session_state.usuario = user_info; st.rerun()
                    else: st.error("Usuário ou senha incorretos (ou inativo).")
                else: st.warning("Preencha login e senha.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── NAVEGAÇÃO ─────────────────────────────────────────────────────────────────
def painel_principal():
    u = st.session_state.usuario
    hora = datetime.now().hour
    saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:10px 0 20px 0;">
            <span style="font-size:18px;font-weight:700;color:#ffffff;">{saudacao}, {u['nome'].split()[0]}!</span>
            <p style="font-size:12px;color:#94a3b8;margin-top:4px;">Perfil: {u['perfil'].upper()}</p>
        </div>""", unsafe_allow_html=True)

        opcoes_menu = []
        if u["perfil"] in ("craque","lider","adm"):
            opcoes_menu.extend(["Cadastro de Oportunidade","SCO - Oportunidades"])
        if u["perfil"] in ("lider","adm","diretoria"):
            opcoes_menu.append("Painel Executivo")
        if u["perfil"] == "adm":
            opcoes_menu.extend(["Comitê de Despesas (N1)","Validação Controladoria","Painel de Acessos","Log de Alterações"])

        pagina = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")
        st.markdown("<br><hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        if st.button("Sair do Sistema", use_container_width=True):
            st.session_state.usuario = None; st.rerun()

    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    if pagina == "Cadastro de Oportunidade":      pagina_cadastro()
    elif pagina == "SCO - Oportunidades":          pagina_sco()
    elif pagina == "Painel Executivo":             pagina_painel_integrado()
    elif pagina == "Comitê de Despesas (N1)":      pagina_comite()
    elif pagina == "Validação Controladoria":       pagina_controladoria()
    elif pagina == "Painel de Acessos":            pagina_admin()
    elif pagina == "Log de Alterações":            pagina_log()
    st.markdown('</div>', unsafe_allow_html=True)

# ── CADASTRO ──────────────────────────────────────────────────────────────────
def pagina_cadastro():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Cadastro de Oportunidade</h2>', unsafe_allow_html=True)
    df_pc = db.ler_plano_contas()

    with st.container(border=True):
        st.markdown("##### 1. Detalhes do Escopo")
        titulo = st.text_input("Título da Melhoria *", max_chars=80)
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
            contas_orc = sorted(df_pc["ContaOrc"].unique().tolist())
            conta_orc_sel = st.selectbox("Conta Orçamento *", [""] + contas_orc)
        with col_g3:
            filtradas = df_pc[df_pc["ContaOrc"] == conta_orc_sel] if conta_orc_sel else pd.DataFrame()
            opcoes_cont = [f"{r['Código']} - {r['ContaCont']}" for _, r in filtradas.iterrows()]
            conta_cont_sel = st.selectbox("Conta Contábil / Código *", [""] + opcoes_cont)

        frente_detectada = ""
        if conta_cont_sel:
            cod = conta_cont_sel.split(" - ")[0]
            try: frente_detectada = df_pc[df_pc["Código"] == cod].iloc[0]["Frente"]
            except: pass
            st.info(f"Frente de Negócio atrelada automaticamente: **{frente_detectada}**")

        st.markdown("<br>##### 3. Planejamento Financeiro e Datas", unsafe_allow_html=True)
        col_v, col_d1, col_d2 = st.columns(3)
        with col_v:
            ganho_2026 = st.number_input("Ganho Estimado 2026 (R$) *", min_value=0.0, step=100.0)
        with col_d1:
            data_prev_n3 = st.text_input("Data Prevista N3 (dd/mm/aaaa)")
        with col_d2:
            data_prev_n4 = st.text_input("Data Prevista N4 (dd/mm/aaaa)")

        if st.button("Salvar Registro (N1)", use_container_width=True, type="primary"):
            if not (titulo.strip() and descricao.strip() and dono.strip() and cc_dono and conta_orc_sel and conta_cont_sel and filial_sel):
                st.error("Preencha todos os campos obrigatórios (*).")
            elif db.titulo_ja_existe(titulo):
                st.error(f"Já existe uma oportunidade com o título '{titulo}'. Escolha um título diferente.")
            else:
                dados_op = {
                    "titulo": titulo, "descricao": descricao, "dono": dono,
                    "cc_dono": cc_dono, "conta_orc": conta_orc_sel,
                    "conta_cont": conta_cont_sel.split(" - ", 1)[-1],
                    "filial": filial_sel, "frente_automatica": frente_detectada,
                    "ganho_2026": ganho_2026, "data_prev_n3": data_prev_n3, "data_prev_n4": data_prev_n4
                }
                db.cadastrar_oportunidade(dados_op, u)
                st.success("Oportunidade enviada para aprovação do Comitê (N1)!")
                time.sleep(1.5); st.rerun()

# ── SCO - OPORTUNIDADES ───────────────────────────────────────────────────────
def pagina_sco():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">SCO - Oportunidades</h2>', unsafe_allow_html=True)

    df = db.ler_oportunidades()
    if df.empty: st.info("Nenhuma oportunidade cadastrada."); return

    df["Nível"] = df["Nível"].astype(str).str.strip()
    if u["perfil"] == "craque":
        df = df[df["Craque"].str.lower() == u["nome"].lower()]
    elif u["perfil"] == "lider":
        df = df[df["Frente de Negócio"].str.lower() == u["frente"].lower()]

    if df.empty: st.info("Nenhuma oportunidade encontrada para o seu perfil."); return

    # ── FILTROS ────────────────────────────────────────────────────────────────
    st.markdown("##### Filtros")
    cols_f = st.columns(7)
    def opt(col_df): return ["Todos"] + sorted(df[col_df].dropna().astype(str).unique().tolist()) if col_df in df.columns else ["Todos"]

    with cols_f[0]: f_status   = st.selectbox("Status",         opt("Nível"),                key="f_status")
    with cols_f[1]: f_frente   = st.selectbox("Frente",         opt("Frente de Negócio"),    key="f_frente")
    with cols_f[2]: f_dono     = st.selectbox("Dono",           opt("Dono da Oportunidade"), key="f_dono")
    with cols_f[3]: f_cc       = st.selectbox("CC Dono",        opt("CC Dono"),              key="f_cc")
    with cols_f[4]: f_filial   = st.selectbox("Filial",         opt("Filial"),               key="f_filial")
    with cols_f[5]: f_conta    = st.selectbox("Conta Orç.",     opt("Conta Orçamento"),      key="f_conta")
    with cols_f[6]: f_craque   = st.selectbox("Craque",         opt("Craque"),               key="f_craque")

    # Filtros de texto
    st.markdown("")
    cols_t = st.columns(3)
    with cols_t[0]: txt_titulo   = st.text_input("🔍 Buscar por Título",        key="txt_titulo")
    with cols_t[1]: txt_descricao = st.text_input("🔍 Buscar por Descrição",   key="txt_desc")
    with cols_t[2]: txt_conta_cont = st.text_input("🔍 Buscar por Conta Cont.", key="txt_ccont")

    df_f = df.copy()
    if f_status  != "Todos": df_f = df_f[df_f["Nível"] == f_status]
    if f_frente  != "Todos": df_f = df_f[df_f["Frente de Negócio"] == f_frente]
    if f_dono    != "Todos": df_f = df_f[df_f["Dono da Oportunidade"] == f_dono]
    if f_cc      != "Todos": df_f = df_f[df_f["CC Dono"] == f_cc]
    if f_filial  != "Todos": df_f = df_f[df_f["Filial"] == f_filial]
    if f_conta   != "Todos": df_f = df_f[df_f["Conta Orçamento"] == f_conta]
    if f_craque  != "Todos": df_f = df_f[df_f["Craque"] == f_craque]
    if txt_titulo.strip():      df_f = df_f[df_f["Título"].astype(str).str.contains(txt_titulo, case=False, na=False)]
    if txt_descricao.strip():   df_f = df_f[df_f.get("Descrição", pd.Series(dtype=str)).astype(str).str.contains(txt_descricao, case=False, na=False)]
    if txt_conta_cont.strip():  df_f = df_f[df_f["Conta Contábil"].astype(str).str.contains(txt_conta_cont, case=False, na=False)]

    st.markdown(f"**{len(df_f)} oportunidade(s) encontrada(s)**")
    st.dataframe(montar_tabela_sco(df_f.copy()), use_container_width=True, hide_index=True)

    # ── PAINEL DE AÇÕES ────────────────────────────────────────────────────────
    if u["perfil"] in ("lider","adm"):
        st.markdown("---")
        st.markdown("##### Ações na Oportunidade")
        opcoes = ["Selecione uma oportunidade..."] + [
            f"{str(r.get('Título',''))[:70]}" for _, r in df_f.iterrows()
        ]
        sel = st.selectbox("Selecione para editar", opcoes, key="sel_op")

        if sel != "Selecione uma oportunidade...":
            titulo_sel = sel.strip()
            matches = df_f[df_f["Título"].astype(str).str[:70] == titulo_sel]
            if matches.empty: st.warning("Oportunidade não encontrada."); return
            row = matches.iloc[0]
            id_sel = row["ID"]
            nivel_atual = str(row["Nível"]).strip()

            tab_coment, tab_edit, tab_nivel = st.tabs(["💬 Comentário", "✏️ Editar Campos", "🔄 Movimentar Nível"])

            # ── COMENTÁRIO ─────────────────────────────────────────────────────
            with tab_coment:
                historico = str(row.get("Comentário da Semana","")).strip()
                if historico:
                    st.markdown(f"**Histórico:**\n\n{historico}")
                    st.divider()
                with st.form(f"form_coment_{id_sel}"):
                    novo_coment = st.text_area("Novo comentário:")
                    if st.form_submit_button("💬 Salvar Comentário", type="primary"):
                        if novo_coment.strip():
                            db.adicionar_comentario(id_sel, novo_coment, u)
                            st.success("Comentário salvo!"); st.rerun()
                        else: st.warning("Digite um comentário antes de salvar.")

            # ── EDIÇÃO DE CAMPOS ───────────────────────────────────────────────
            with tab_edit:
                df_pc = db.ler_plano_contas()
                with st.form(f"form_edit_{id_sel}"):
                    st.markdown("**Campos editáveis pelo Líder / ADM:**")
                    nova_descricao = st.text_area("Descrição", value=str(row.get("Descrição","")), max_chars=600)

                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        contas_orc = sorted(df_pc["ContaOrc"].unique().tolist())
                        idx_orc = contas_orc.index(row.get("Conta Orçamento","")) if row.get("Conta Orçamento","") in contas_orc else 0
                        nova_conta_orc = st.selectbox("Conta Orçamento", contas_orc, index=idx_orc)
                    with col_e2:
                        filtradas = df_pc[df_pc["ContaOrc"] == nova_conta_orc]
                        opcoes_cont = [f"{r['Código']} - {r['ContaCont']}" for _, r in filtradas.iterrows()]
                        conta_cont_atual = f"{row.get('Código','')} - {row.get('Conta Contábil','')}".strip(" -")
                        idx_cont = opcoes_cont.index(conta_cont_atual) if conta_cont_atual in opcoes_cont else 0
                        nova_conta_cont_sel = st.selectbox("Conta Contábil", opcoes_cont if opcoes_cont else [""], index=idx_cont if opcoes_cont else 0)

                    nova_frente = ""
                    if nova_conta_cont_sel and " - " in nova_conta_cont_sel:
                        cod = nova_conta_cont_sel.split(" - ")[0]
                        try: nova_frente = df_pc[df_pc["Código"] == cod].iloc[0]["Frente"]
                        except: pass
                    if nova_frente: st.info(f"Frente detectada: **{nova_frente}**")

                    st.markdown("**Valores por Trimestre (R$):**")
                    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
                    v1 = col_t1.number_input("1° TRI", value=float(row.get("Mês 1",0) or 0)+float(row.get("Mês 2",0) or 0)+float(row.get("Mês 3",0) or 0), step=100.0)
                    v2 = col_t2.number_input("2° TRI", value=float(row.get("Mês 4",0) or 0)+float(row.get("Mês 5",0) or 0)+float(row.get("Mês 6",0) or 0), step=100.0)
                    v3 = col_t3.number_input("3° TRI", value=float(row.get("Mês 7",0) or 0)+float(row.get("Mês 8",0) or 0)+float(row.get("Mês 9",0) or 0), step=100.0)
                    v4 = col_t4.number_input("4° TRI", value=float(row.get("Mês 10",0) or 0)+float(row.get("Mês 11",0) or 0)+float(row.get("Mês 12",0) or 0), step=100.0)

                    col_d1, col_d2 = st.columns(2)
                    nova_data_n3 = col_d1.text_input("Data Prevista N3", value=str(row.get("Data Prevista N3","")))
                    nova_data_n4 = col_d2.text_input("Data Prevista N4", value=str(row.get("Data Prevista N4","")))

                    if st.form_submit_button("✏️ Salvar Edições", type="primary"):
                        campos = {
                            "Descrição": nova_descricao,
                            "Conta Orçamento": nova_conta_orc,
                            "Conta Contábil": nova_conta_cont_sel.split(" - ",1)[-1] if nova_conta_cont_sel else "",
                            "Frente de Negócio": nova_frente,
                            "Total Estimado 2026": v1+v2+v3+v4,
                            "Mês 1": round(v1/3,2), "Mês 2": round(v1/3,2), "Mês 3": round(v1/3,2),
                            "Mês 4": round(v2/3,2), "Mês 5": round(v2/3,2), "Mês 6": round(v2/3,2),
                            "Mês 7": round(v3/3,2), "Mês 8": round(v3/3,2), "Mês 9": round(v3/3,2),
                            "Mês 10": round(v4/3,2), "Mês 11": round(v4/3,2), "Mês 12": round(v4/3,2),
                            "Data Prevista N3": nova_data_n3,
                            "Data Prevista N4": nova_data_n4,
                        }
                        db.editar_campos_oportunidade(id_sel, campos, u)
                        st.success("Campos atualizados com sucesso!"); st.rerun()

            # ── MOVIMENTAR NÍVEL ───────────────────────────────────────────────
            with tab_nivel:
                st.markdown(f"**Status atual:** `{nivel_atual}`")
                if "N2" in nivel_atual:
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("▶ Iniciar Execução (N2 → N3)", key=f"n3_{id_sel}", use_container_width=True):
                            db.movimentar_nivel(id_sel, "N3 - Execução", u); st.success("Movido para N3!"); st.rerun()
                    with c2:
                        if st.button("✖ Cancelar (→ N0)", key=f"n0n2_{id_sel}", use_container_width=True):
                            db.movimentar_nivel(id_sel, "N0 - Cancelada", u); st.success("Cancelada."); st.rerun()
                elif "N3" in nivel_atual:
                    submetido = row.get("Submetido Controladoria", False)
                    c1, c2 = st.columns(2)
                    with c1:
                        if not submetido:
                            if st.button("📋 Submeter para Controladoria (→ N4)", key=f"sub_{id_sel}", type="primary", use_container_width=True):
                                db.submeter_para_controladoria(id_sel, u); st.success("Enviado!"); st.rerun()
                        else:
                            st.warning("⏳ Aguardando validação da Controladoria.")
                    with c2:
                        if st.button("✖ Cancelar (→ N0)", key=f"n0n3_{id_sel}", use_container_width=True):
                            db.movimentar_nivel(id_sel, "N0 - Cancelada", u); st.success("Cancelada."); st.rerun()
                elif "N1" in nivel_atual:
                    st.info("ℹ️ Em N1 — aprovação para N2 é feita pelo Comitê de Despesas.")
                elif "N4" in nivel_atual:
                    st.success("✅ Já implementada (N4).")
                elif "N0" in nivel_atual:
                    st.error("Oportunidade cancelada (N0).")

# ── COMITÊ (N1 → N2) ─────────────────────────────────────────────────────────
def pagina_comite():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Comitê de Despesas (Aprovação N1)</h2>', unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: return
    df["Nível"] = df["Nível"].astype(str).str.strip()
    df_n1 = df[df["Nível"] == "N1 - Ideia"]
    if df_n1.empty: st.success("Nenhuma ideia aguardando aprovação no momento."); return

    st.markdown(f"**{len(df_n1)} oportunidade(s) aguardando aprovação**")
    st.dataframe(montar_tabela_sco(df_n1.copy()), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### Ações")
    opcoes = ["Selecione uma oportunidade..."] + [str(r.get("Título",""))[:70] for _, r in df_n1.iterrows()]
    sel = st.selectbox("Selecione para aprovar/rejeitar", opcoes, key="sel_comite")

    if sel != "Selecione uma oportunidade...":
        matches = df_n1[df_n1["Título"].astype(str).str[:70] == sel.strip()]
        if matches.empty: return
        row = matches.iloc[0]
        id_sel = row["ID"]
        with st.container(border=True):
            st.markdown(f"**{row.get('Título','')}** | {row.get('Craque','')} | {brl(row.get('Total Estimado 2026',0))}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Aprovar (N1 → N2)", key=f"apr_{id_sel}", use_container_width=True, type="primary"):
                    db.movimentar_nivel(id_sel, "N2 - Planejamento", u); st.success("Aprovada para N2!"); st.rerun()
            with c2:
                if st.button("❌ Rejeitar (→ N0)", key=f"rej_{id_sel}", use_container_width=True):
                    db.movimentar_nivel(id_sel, "N0 - Cancelada", u); st.success("Rejeitada."); st.rerun()

# ── CONTROLADORIA (N3 → N4) ───────────────────────────────────────────────────
def pagina_controladoria():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Validação Controladoria (Aprovação N4)</h2>', unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: return
    df["Nível"] = df["Nível"].astype(str).str.strip()
    df_n3 = df[(df["Nível"] == "N3 - Execução") & (df["Submetido Controladoria"] == True)]
    if df_n3.empty: st.success("Nenhuma ideia aguardando validação de implementação."); return

    st.markdown(f"**{len(df_n3)} oportunidade(s) aguardando validação**")
    st.dataframe(montar_tabela_sco(df_n3.copy()), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### Ações")
    opcoes = ["Selecione uma oportunidade..."] + [str(r.get("Título",""))[:70] for _, r in df_n3.iterrows()]
    sel = st.selectbox("Selecione para validar", opcoes, key="sel_ctrl")

    if sel != "Selecione uma oportunidade...":
        matches = df_n3[df_n3["Título"].astype(str).str[:70] == sel.strip()]
        if matches.empty: return
        row = matches.iloc[0]
        id_sel = row["ID"]
        with st.container(border=True):
            st.markdown(f"**{row.get('Título','')}** | {row.get('Frente de Negócio','')} | {brl(row.get('Total Estimado 2026',0))}")
            if st.button("🏆 Validar Savings — Marcar como Implementado (N4)", key=f"val_{id_sel}", type="primary", use_container_width=True):
                db.movimentar_nivel(id_sel, "N4 - Implementado", u); st.success("Implementado!"); st.rerun()

# ── PAINEL EXECUTIVO ──────────────────────────────────────────────────────────
def pagina_painel_integrado():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Painel Executivo</h2>', unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: st.info("Sem dados para análise."); return

    df["Nível"] = df["Nível"].astype(str).str.strip()
    df["Frente de Negócio"] = df["Frente de Negócio"].astype(str).str.strip()
    df["Total Estimado 2026"] = pd.to_numeric(df["Total Estimado 2026"], errors="coerce").fillna(0.0)
    if u["perfil"] == "lider": df = df[df["Frente de Negócio"].str.lower() == u["frente"].lower()]
    df_ativas = df[df["Nível"] != "N0 - Cancelada"]

    tab_dash, tab_evo, tab_gerencial, tab_excel = st.tabs(["📊 Dashboard","📈 Evolução","📑 Relatório Gerencial","📥 Base Excel"])

    with tab_dash:
        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(f'<div class="kpi-container"><div class="kpi-title">Ideias Ativas</div><div class="kpi-value">{len(df_ativas)}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-container"><div class="kpi-title">Potencial 2026</div><div class="kpi-value" style="color:#16a34a;">{brl(df_ativas["Total Estimado 2026"].sum())}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-container"><div class="kpi-title">Implementadas</div><div class="kpi-value">{len(df[df["Nível"]=="N4 - Implementado"])}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-container"><div class="kpi-title">Canceladas</div><div class="kpi-value" style="color:#991B1B;">{len(df[df["Nível"]=="N0 - Cancelada"])}</div></div>', unsafe_allow_html=True)
        g1,g2 = st.columns(2)
        with g1: st.write("Distribuição por Nível"); st.bar_chart(df["Nível"].value_counts(), color="#185FA5")
        with g2: st.write("Potencial por Frente"); st.bar_chart(df_ativas.groupby("Frente de Negócio")["Total Estimado 2026"].sum(), color="#16a34a")

    with tab_evo:
        df_ativas = df_ativas.copy()
        df_ativas["Semana"] = df_ativas["Data Cadastro (N1)"].apply(lambda x: "Sem."+str(x.split("/")[1]) if pd.notna(x) and x else "?")
        evolucao = df_ativas.groupby(["Semana","Nível"])["Total Estimado 2026"].sum().unstack().fillna(0)
        st.bar_chart(evolucao)

    with tab_gerencial:
        orc_data = db.ler_orcamento()
        frentes = db.ler_frentes()
        if u["perfil"] == "adm":
            with st.expander("⚙️ Ajustar Metas Orçadas (Apenas ADM)"):
                with st.form("form_orc"):
                    cols_orc = st.columns(len(frentes))
                    vals_orc = {f: cols_orc[i].number_input(f, value=float(orc_data.get(f,0.0)), step=10000.0) for i,f in enumerate(frentes)}
                    if st.form_submit_button("Salvar", type="primary"):
                        db.salvar_orcamento(vals_orc); st.success("Metas atualizadas!"); time.sleep(1); st.rerun()
        relatorio = []
        for f in frentes:
            realizado = df[(df["Frente de Negócio"]==f)&(df["Nível"]=="N4 - Implementado")]["Total Estimado 2026"].sum()
            orc = orc_data.get(f, 0.0)
            relatorio.append({"Frente":f,"Orçado":brl(orc),"Realizado N4":brl(realizado),"Atingimento":f"{(realizado/orc*100) if orc>0 else 0:.1f}%"})
        st.dataframe(pd.DataFrame(relatorio), use_container_width=True, hide_index=True)

    with tab_excel:
        for m in range(1,13):
            if f"Mês {m}" not in df.columns: df[f"Mês {m}"] = 0.0
            else: df[f"Mês {m}"] = pd.to_numeric(df[f"Mês {m}"], errors="coerce").fillna(0.0)
        df_ex = pd.DataFrame({
            "Grupo Contábil": df.get("Frente de Negócio",""),
            "Conta Orçamento": df.get("Conta Orçamento",""),
            "Desc. Conta Contábil": df.get("Conta Contábil",""),
            "Descrição da Oportunidade": df.get("Título", df.get("Descrição","")),
            "1° TRI": df["Mês 1"]+df["Mês 2"]+df["Mês 3"],
            "2° TRI": df["Mês 4"]+df["Mês 5"]+df["Mês 6"],
            "3° TRI": df["Mês 7"]+df["Mês 8"]+df["Mês 9"],
            "4° TRI": df["Mês 10"]+df["Mês 11"]+df["Mês 12"],
            "Total": df["Total Estimado 2026"],
            "Status": df.get("Nível",""),
            "Dono": df.get("Dono da Oportunidade",""),
            "CC Dono": df.get("CC Dono",""),
            "Filial": df.get("Filial",""),
        })
        st.dataframe(df_ex, use_container_width=True, hide_index=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_ex.to_excel(writer, index=False, sheet_name="Oportunidades")
        st.download_button("📥 Download Excel", data=buffer.getvalue(),
            file_name=f"Base_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel", type="primary")

# ── LOG DE ALTERAÇÕES ─────────────────────────────────────────────────────────
def pagina_log():
    st.markdown('<h2 style="color:#0f172a;">Log de Alterações</h2>', unsafe_allow_html=True)
    df_log = db.ler_logs()
    if df_log.empty: st.info("Nenhuma alteração registrada ainda."); return

    st.markdown("##### Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        tipos = ["Todos"] + sorted(df_log["tipo_acao"].dropna().unique().tolist())
        f_tipo = st.selectbox("Tipo de Ação", tipos, key="log_tipo")
    with col2:
        users = ["Todos"] + sorted(df_log["usuario"].dropna().unique().tolist())
        f_user = st.selectbox("Usuário", users, key="log_user")
    with col3:
        txt_busca = st.text_input("🔍 Buscar na Descrição", key="log_busca")

    df_f = df_log.copy()
    if f_tipo != "Todos": df_f = df_f[df_f["tipo_acao"] == f_tipo]
    if f_user != "Todos": df_f = df_f[df_f["usuario"] == f_user]
    if txt_busca.strip(): df_f = df_f[df_f["descricao"].astype(str).str.contains(txt_busca, case=False, na=False)]

    colunas_log = [c for c in ["data_hora","usuario","tipo_acao","descricao","id_oportunidade"] if c in df_f.columns]
    df_disp = df_f[colunas_log].rename(columns={
        "data_hora": "Data/Hora", "usuario": "Usuário",
        "tipo_acao": "Tipo de Ação", "descricao": "Descrição",
        "id_oportunidade": "ID Oportunidade"
    })
    st.markdown(f"**{len(df_disp)} registro(s)**")
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_disp.to_excel(writer, index=False, sheet_name="Log")
    st.download_button("📥 Exportar Log em Excel", data=buffer.getvalue(),
        file_name=f"Log_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.ms-excel")

# ── PAINEL DE ACESSOS ─────────────────────────────────────────────────────────
def pagina_admin():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">⚙️ Painel de Acessos e Sistema</h2>', unsafe_allow_html=True)
    tab_novo, tab_edit, tab_import = st.tabs(["➕ Novo Usuário","✏️ Editar Usuários","📤 Importar Planilha"])

    with tab_novo:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                login   = st.text_input("Login", key="novo_login")
                email   = st.text_input("E-mail", key="novo_email")
                nome    = st.text_input("Nome Completo", key="novo_nome")
                perfil  = st.selectbox("Perfil", ["craque","lider","adm","diretoria"], key="novo_perfil")
            with c2:
                senha   = st.text_input("Senha Inicial *", type="password", key="novo_senha")
                frente  = st.selectbox("Frente", [""]+db.ler_frentes(), key="novo_frente")
                filial  = st.selectbox("Filial", [""]+db.ler_filiais(), key="novo_filial")
            if st.button("Cadastrar Usuário", use_container_width=True, type="primary"):
                if login.strip() and nome.strip() and senha.strip():
                    db.cadastrar_usuario_manual(login, nome, perfil, email, filial, "", frente, senha)
                    db.registrar_log(u, "CADASTRO USUÁRIO", f"Novo usuário: {login}")
                    st.success(f"Usuário '{login}' criado!")
                else: st.error("Preencha Login, Nome e Senha.")

    with tab_edit:
        df_users = db.ler_usuarios()
        if not df_users.empty:
            alvo = st.selectbox("Selecione o Usuário:", [""]+df_users["login"].tolist())
            if alvo:
                d = df_users[df_users["login"]==alvo].iloc[0]
                with st.form("form_edicao"):
                    c1, c2 = st.columns(2)
                    edit_nome   = c1.text_input("Nome", value=d.get("nome",""))
                    edit_email  = c1.text_input("E-mail", value=d.get("email",""))
                    lista_p = ["craque","lider","adm","diretoria"]
                    edit_perfil = c1.selectbox("Perfil", lista_p, index=lista_p.index(d.get("perfil","craque")) if d.get("perfil","craque") in lista_p else 0)
                    lista_f = [""]+db.ler_frentes()
                    edit_frente = c2.selectbox("Frente", lista_f, index=lista_f.index(d.get("frente","")) if d.get("frente","") in lista_f else 0)
                    lista_fil = [""]+db.ler_filiais()
                    edit_filial = c2.selectbox("Filial", lista_fil, index=lista_fil.index(d.get("filial","")) if d.get("filial","") in lista_fil else 0)
                    edit_senha  = c2.text_input("Nova Senha (em branco = manter)", type="password")
                    if st.form_submit_button("Salvar Alterações", type="primary"):
                        db.atualizar_usuario_completo(alvo, edit_nome, edit_email, edit_perfil, edit_frente, edit_filial, edit_senha, u)
                        st.success("Usuário atualizado!"); time.sleep(1); st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown("#### ⚠️ Zona de Perigo")
                    if st.button(f"🗑️ Excluir '{alvo}' definitivamente"):
                        db.excluir_usuario(alvo, u); st.success("Usuário excluído!"); time.sleep(1.5); st.rerun()
        else: st.info("Nenhum usuário cadastrado.")

    with tab_import:
        st.write("Faça upload da planilha base legada.")
        arquivo = st.file_uploader("Selecione (.xlsx)", type=["xlsx"])
        if arquivo and st.button("🚀 Processar e Importar", type="primary"):
            try:
                df_import = pd.read_excel(arquivo)
                db.importar_base_excel(df_import, u)
                st.success("Planilha importada com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")

def main():
    if not st.session_state.usuario: tela_login()
    else: painel_principal()

if __name__ == "__main__": main()
