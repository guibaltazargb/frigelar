import streamlit as st
import pandas as pd
from datetime import datetime, date
import dados as db

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Programa Essência",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main { background: #f8fafc; }

  /* Sidebar */
  section[data-testid="stSidebar"] { background: linear-gradient(180deg,#0a1628,#0d2240); }
  section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
  section[data-testid="stSidebar"] .stRadio label { font-size:13px; padding:4px 0; }

  /* KPIs */
  .kpi-blue { background:#E6F1FB; border:1px solid #B5D4F4; border-radius:12px; padding:16px 18px; }
  .kpi-green { background:#EAF3DE; border:1px solid #C0DD97; border-radius:12px; padding:16px 18px; }
  .kpi-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; }
  .kpi-blue .kpi-label { color:#185FA5; }
  .kpi-green .kpi-label { color:#3B6D11; }
  .kpi-val { font-size:26px; font-weight:600; }
  .kpi-blue .kpi-val { color:#0D2240; }
  .kpi-green .kpi-val { color:#1B3D06; }

  /* Badges de nível */
  .badge { font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px; display:inline-block; }
  .badge-n0 { background:#F5C6C6; color:#7B1A1A; }
  .badge-n1 { background:#E6F1FB; color:#185FA5; }
  .badge-n2 { background:#EAF3DE; color:#3B6D11; }
  .badge-n3 { background:#FAEEDA; color:#854F0B; }
  .badge-n4 { background:#E1F5EE; color:#0F6E56; }

  /* Cards */
  .card { background:#fff; border-radius:14px; border:.5px solid #e2e8f0;
          padding:18px 20px; box-shadow:0 1px 3px rgba(0,0,0,.04); margin-bottom:12px; }

  /* Comentário */
  .comentario-box { background:#f8fafc; border-left:3px solid #185FA5;
                    padding:10px 14px; border-radius:0 8px 8px 0;
                    font-size:12px; color:#334155; white-space:pre-wrap; }

  /* Título da página */
  .page-title { font-size:22px; font-weight:600; color:#0D2240; margin-bottom:4px; }
  .page-sub   { font-size:13px; color:#94a3b8; margin-bottom:20px; }

  /* Alerta de complemento */
  .aviso-complemento { background:#FAEEDA; border:1px solid #FAC775;
                       border-radius:10px; padding:10px 14px; font-size:13px; color:#854F0B; }

  /* Tabela customizada */
  .stDataFrame { border-radius:12px; overflow:hidden; }

  /* Botões */
  .stButton > button { border-radius:9px; font-weight:600; font-size:13px; }
  div[data-testid="stForm"] .stButton > button[kind="primaryFormSubmit"] {
    background:#185FA5; color:#fff; border:none;
  }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ── Helpers ───────────────────────────────────────────────────────────────────
def brl(v):
    try: return f"R$ {float(v):,.0f}".replace(",",".")
    except: return "R$ 0"

def badge(nivel):
    key = nivel[:2] if nivel else "N1"
    cls = {"N0":"badge-n0","N1":"badge-n1","N2":"badge-n2","N3":"badge-n3","N4":"badge-n4"}.get(key,"badge-n1")
    return f'<span class="badge {cls}">{nivel}</span>'

def kpi(label, valor, tipo="blue"):
    return f"""<div class="kpi-{tipo}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-val">{valor}</div>
    </div>"""

def tem_campos_faltando(row):
    obrigatorios = ["Descrição","Grupo Contábil","Conta Orçamento","Conta Contábil","Dono da Oportunidade"]
    return any(str(row.get(c,"")).strip() == "" for c in obrigatorios)

# ── TELA DE LOGIN ──────────────────────────────────────────────────────────────
def tela_login():
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:24px;">
          <span style="font-size:32px; font-weight:700; color:#0D2240;">Essência</span>
          <span style="font-size:32px; color:#3B6D11;">.</span><br>
          <span style="font-size:13px; color:#94a3b8;">Programa de Redução de Custos</span>
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_login"):
            login = st.text_input("Usuário", placeholder="Digite seu login")
            submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            if submitted:
                if not login.strip():
                    st.error("Digite seu login.")
                else:
                    usuario = db.autenticar(login.strip())
                    if usuario:
                        st.session_state.usuario = usuario
                        st.rerun()
                    else:
                        st.error("Usuário não encontrado. Verifique com a Controladoria.")
        st.caption("Acesso controlado — apenas usuários cadastrados")

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
def sidebar():
    u = st.session_state.usuario
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:8px 0 16px;">
          <div style="font-size:20px;font-weight:700;color:#fff;">Essência<span style="color:#639922;">.</span></div>
          <div style="font-size:10px;color:#475569;margin-top:2px;">Programa de Redução de Custos</div>
        </div>
        <div style="background:rgba(255,255,255,.06);border-radius:10px;padding:10px 12px;margin-bottom:16px;">
          <div style="font-size:13px;font-weight:600;color:#fff;">{u['nome']}</div>
          <div style="font-size:11px;color:#64748b;margin-top:2px;">{u['perfil'].upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        perfil = u["perfil"]
        opcoes = ["📋 Cadastro de Oportunidade", "📊 Tabela de Oportunidades",
                  "📈 Dashboard", "📉 Evolução Macro",
                  "⚠️ Ideias em Atraso", "📑 Relatório Gerencial"]

        # Craque não vê relatório gerencial nem evolução macro completa
        if perfil == "craque":
            opcoes = ["📋 Cadastro de Oportunidade", "📊 Tabela de Oportunidades", "📈 Dashboard"]

        pagina = st.radio("", opcoes, label_visibility="collapsed")

        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.usuario = None
            st.rerun()

    return pagina

# ── FILTROS de visibilidade ────────────────────────────────────────────────────
def filtrar_por_perfil(df: pd.DataFrame, usuario: dict) -> pd.DataFrame:
    perfil = usuario.get("perfil","")
    if perfil == "craque":
        return df[df["Craque"].str.lower() == usuario["nome"].lower()]
    elif perfil == "lider":
        return df[df["Frente de Negócio"].str.lower() == usuario.get("frente","").lower()]
    return df  # adm vê tudo

# ── PÁGINA: CADASTRO ───────────────────────────────────────────────────────────
def pagina_cadastro():
    u = st.session_state.usuario
    st.markdown('<div class="page-title">📋 Cadastro de Oportunidade</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Registre uma nova ideia de redução de custos</div>', unsafe_allow_html=True)

    pc = db.ler_plano_contas()
    grupos = sorted(pc["Grupo"].unique().tolist())

    with st.form("form_cadastro", clear_on_submit=True):
        st.markdown("**Identificação**")
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_area("Descrição *", max_chars=300,
                help="Identificador da ideia — seja sucinto mas claro.")
        with col2:
            dono = st.text_input("Dono da Oportunidade *")

        st.markdown("**Classificação Contábil**")
        col1, col2, col3 = st.columns(3)
        with col1:
            grupo = st.selectbox("Grupo Contábil *", [""] + grupos)
        with col2:
            contas_orc = [""] + sorted(pc[pc["Grupo"]==grupo]["ContaOrc"].unique().tolist()) if grupo else [""]
            conta_orc = st.selectbox("Conta Orçamento *", contas_orc)
        with col3:
            contas_cont = [""] + sorted(pc[(pc["Grupo"]==grupo)&(pc["ContaOrc"]==conta_orc)]["ContaCont"].unique().tolist()) if conta_orc else [""]
            conta_cont = st.selectbox("Conta Contábil *", contas_cont)

        col1, col2 = st.columns(2)
        with col1:
            cc_dono = st.text_input("CC Dono da Oportunidade *")
        with col2:
            st.text_input("Craque", value=u["nome"], disabled=True)

        st.markdown("**Estimativa de Redução 2026 (opcional)**")
        meses = db.MESES
        cols = st.columns(6)
        vals_mes = {}
        for idx, m in enumerate(meses):
            with cols[idx % 6]:
                vals_mes[m] = st.number_input(m, min_value=0, value=0, step=1000, key=f"m_{m}")

        col1, col2 = st.columns(2)
        with col1:
            total_2027 = st.number_input("Estimativa Total 2027 (opcional)", min_value=0, value=0, step=1000)
        with col2:
            total_2028 = st.number_input("Estimativa Total 2028 (opcional)", min_value=0, value=0, step=1000)

        total_2026 = sum(vals_mes.values())
        st.info(f"Total 2026 calculado: {brl(total_2026)}")

        submitted = st.form_submit_button("💾 Cadastrar Oportunidade", type="primary", use_container_width=True)
        if submitted:
            erros = []
            if not descricao.strip(): erros.append("Descrição obrigatória.")
            if not dono.strip():      erros.append("Dono da Oportunidade obrigatório.")
            if not grupo:             erros.append("Grupo Contábil obrigatório.")
            if not conta_orc:         erros.append("Conta Orçamento obrigatória.")
            if not conta_cont:        erros.append("Conta Contábil obrigatória.")
            if not cc_dono.strip():   erros.append("CC Dono obrigatório.")
            if erros:
                for e in erros: st.error(e)
            else:
                dados_cad = {
                    "descricao": descricao, "dono": dono,
                    "grupo": grupo, "conta_orc": conta_orc, "conta_cont": conta_cont,
                    "cc_dono": cc_dono, "total_2027": total_2027, "total_2028": total_2028,
                }
                for m in meses:
                    dados_cad[f"est_{m.lower()}"] = vals_mes[m]
                novo_id = db.cadastrar_oportunidade(dados_cad, u)
                st.success(f"✅ Oportunidade #{novo_id} cadastrada com sucesso!")

# ── PÁGINA: TABELA ─────────────────────────────────────────────────────────────
def pagina_tabela():
    u = st.session_state.usuario
    st.markdown('<div class="page-title">📊 Tabela de Oportunidades</div>', unsafe_allow_html=True)

    df = filtrar_por_perfil(db.ler_oportunidades(), u)

    # Avisos de complemento
    faltando = df[df.apply(tem_campos_faltando, axis=1)]
    if not faltando.empty:
        st.markdown(f'<div class="aviso-complemento">⚠️ <b>{len(faltando)} ideia(s)</b> com cadastro incompleto — campos obrigatórios faltando.</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Filtros
    with st.expander("🔍 Filtros", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            f_nivel = st.multiselect("Nível", options=df["Nível"].unique().tolist())
        with col2:
            f_frente = st.multiselect("Frente", options=df["Frente de Negócio"].unique().tolist())
        with col3:
            f_area = st.multiselect("Área", options=df["Área"].unique().tolist())
        with col4:
            f_craque = st.multiselect("Craque", options=df["Craque"].unique().tolist())
        col5, col6 = st.columns(2)
        with col5:
            f_grupo = st.multiselect("Grupo Contábil", options=df["Grupo Contábil"].unique().tolist())
        with col6:
            f_dono = st.multiselect("Dono da Oportunidade", options=df["Dono da Oportunidade"].unique().tolist())

    # Aplica filtros
    df_f = df.copy()
    if f_nivel:   df_f = df_f[df_f["Nível"].isin(f_nivel)]
    if f_frente:  df_f = df_f[df_f["Frente de Negócio"].isin(f_frente)]
    if f_area:    df_f = df_f[df_f["Área"].isin(f_area)]
    if f_craque:  df_f = df_f[df_f["Craque"].isin(f_craque)]
    if f_grupo:   df_f = df_f[df_f["Grupo Contábil"].isin(f_grupo)]
    if f_dono:    df_f = df_f[df_f["Dono da Oportunidade"].isin(f_dono)]

    st.markdown(f"**{len(df_f)} oportunidade(s) encontrada(s)**")

    # Exibe cada linha como card expandível
    for _, row in df_f.iterrows():
        nivel_key = str(row["Nível"])[:2]
        cor_borda = {"N0":"#F5C6C6","N1":"#B5D4F4","N2":"#C0DD97","N3":"#FAC775","N4":"#9FE1CB"}.get(nivel_key,"#e2e8f0")

        with st.expander(f"#{row['ID']} — {row['Descrição'][:60]}  |  {row['Nível']}  |  {brl(row['Total 2026'])}/ano"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Craque:** {row['Craque']}")
                st.markdown(f"**Área:** {row['Área']} | **Filial:** {row['Filial']}")
                st.markdown(f"**Frente:** {row['Frente de Negócio']}")
                st.markdown(f"**Dono:** {row['Dono da Oportunidade']} | **CC:** {row['CC Dono']}")
            with col2:
                st.markdown(f"**Grupo:** {row['Grupo Contábil']}")
                st.markdown(f"**Conta Orç.:** {row['Conta Orçamento']}")
                st.markdown(f"**Conta Cont.:** {row['Conta Contábil']}")
            with col3:
                st.markdown(f"**Total 2026:** {brl(row['Total 2026'])}")
                st.markdown(f"**Total 2027:** {brl(row['Total 2027'])}")
                st.markdown(f"**Total 2028:** {brl(row['Total 2028'])}")
                st.markdown(f"**Cadastro:** {row['Data Cadastro (N1)']}")

            # Histórico e datas
            col4, col5 = st.columns(2)
            with col4:
                st.markdown(f"**Histórico:** {row['Histórico de Níveis']}")
                if row["Data Esperada N3"]: st.markdown(f"**Prev. N3:** {row['Data Esperada N3']}")
                if row["Data Esperada N4"]: st.markdown(f"**Prev. N4:** {row['Data Esperada N4']}")
            with col5:
                datas_r = [(f"N{n}", row[f"Data Realizada N{n}"]) for n in ["0","2","3","4"] if row.get(f"Data Realizada N{n}","")]
                for label, dt in datas_r:
                    st.markdown(f"**Real. {label}:** {dt}")

            # Comentário
            st.markdown("**Comentário da Semana:**")
            if row["Comentário da Semana"].strip():
                st.markdown(f'<div class="comentario-box">{row["Comentário da Semana"]}</div>', unsafe_allow_html=True)
            else:
                st.caption("Nenhum comentário ainda.")

            # Ações (comentário + edição + movimentação)
            _acoes_oportunidade(row, u)

def _acoes_oportunidade(row, u):
    perfil = u.get("perfil","")
    id_ = row["ID"]
    st.markdown("---")

    # ── Adicionar comentário (todos os perfis) ──
    with st.expander("💬 Adicionar comentário"):
        with st.form(f"form_coment_{id_}"):
            texto = st.text_area("Comentário", max_chars=500, key=f"coment_txt_{id_}")
            if st.form_submit_button("Enviar"):
                if texto.strip():
                    db.adicionar_comentario(id_, texto.strip(), u)
                    st.success("Comentário adicionado!"); st.rerun()
                else:
                    st.error("Digite um comentário.")

    # ── Movimentar nível ──
    pode_mover = perfil in ("lider","adm")
    if pode_mover:
        with st.expander("🔄 Movimentar Nível"):
            with st.form(f"form_nivel_{id_}"):
                novo_nivel = st.selectbox("Novo nível", db.NIVEIS, key=f"sel_nivel_{id_}")
                if st.form_submit_button("Confirmar movimentação"):
                    try:
                        db.movimentar_nivel(id_, novo_nivel, u)
                        st.success(f"Nível atualizado para {novo_nivel}!"); st.rerun()
                    except PermissionError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Erro: {e}")

    # ── Editar campos ──
    pode_editar = perfil in ("lider","adm")
    if pode_editar:
        with st.expander("✏️ Editar Oportunidade"):
            confirmacao = st.checkbox("Confirmo que desejo alterar esta oportunidade", key=f"confirm_{id_}")
            if confirmacao:
                pc = db.ler_plano_contas()
                grupos = sorted(pc["Grupo"].unique().tolist())
                with st.form(f"form_edit_{id_}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nova_desc = st.text_area("Descrição", value=row["Descrição"], max_chars=300)
                        novo_dono = st.text_input("Dono da Oportunidade", value=row["Dono da Oportunidade"])
                        novo_cc   = st.text_input("CC Dono", value=row["CC Dono"])
                    with col2:
                        novo_grupo = st.selectbox("Grupo Contábil", [""] + grupos,
                            index=([""] + grupos).index(row["Grupo Contábil"]) if row["Grupo Contábil"] in grupos else 0)
                        contas_orc = sorted(pc[pc["Grupo"]==novo_grupo]["ContaOrc"].unique().tolist()) if novo_grupo else []
                        nova_conta_orc = st.selectbox("Conta Orçamento", [""] + contas_orc)
                        contas_cont = sorted(pc[(pc["Grupo"]==novo_grupo)&(pc["ContaOrc"]==nova_conta_orc)]["ContaCont"].unique().tolist()) if nova_conta_orc else []
                        nova_conta_cont = st.selectbox("Conta Contábil", [""] + contas_cont)

                    # Datas esperadas (líder e adm)
                    col3, col4 = st.columns(2)
                    with col3:
                        data_esp_n3 = st.text_input("Data Esperada N3 (dd/mm/aaaa)", value=row["Data Esperada N3"])
                    with col4:
                        data_esp_n4 = st.text_input("Data Esperada N4 (dd/mm/aaaa)", value=row["Data Esperada N4"])

                    st.markdown("**Estimativas mensais 2026**")
                    meses = db.MESES
                    cols_m = st.columns(6)
                    vals_mes = {}
                    for idx, m in enumerate(meses):
                        with cols_m[idx % 6]:
                            cur = float(row.get(f"Est. {m}/26", 0) or 0)
                            vals_mes[m] = st.number_input(m, min_value=0, value=int(cur), step=1000, key=f"edit_m_{id_}_{m}")

                    col5, col6 = st.columns(2)
                    with col5:
                        total_2027 = st.number_input("Total 2027", min_value=0, value=int(float(row.get("Total 2027",0) or 0)), step=1000)
                    with col6:
                        total_2028 = st.number_input("Total 2028", min_value=0, value=int(float(row.get("Total 2028",0) or 0)), step=1000)

                    if st.form_submit_button("💾 Salvar alterações", type="primary"):
                        campos = {
                            "Descrição": nova_desc,
                            "Dono da Oportunidade": novo_dono,
                            "CC Dono": novo_cc,
                            "Grupo Contábil": novo_grupo,
                            "Conta Orçamento": nova_conta_orc,
                            "Conta Contábil": nova_conta_cont,
                            "Data Esperada N3": data_esp_n3,
                            "Data Esperada N4": data_esp_n4,
                            "Total 2027": total_2027,
                            "Total 2028": total_2028,
                        }
                        for m in meses:
                            campos[f"Est. {m}/26"] = vals_mes[m]
                        db.atualizar_oportunidade(id_, campos, u)
                        st.success("Oportunidade atualizada!"); st.rerun()

# ── PÁGINA: DASHBOARD ──────────────────────────────────────────────────────────
def pagina_dashboard():
    u = st.session_state.usuario
    st.markdown('<div class="page-title">📈 Dashboard</div>', unsafe_allow_html=True)
    df = filtrar_por_perfil(db.ler_oportunidades(), u)
    df_ativas = df[df["Nível"] != "N0 - Cancelada"]

    # KPIs
    total = len(df_ativas)
    pot_2026 = df_ativas["Total 2026"].sum()
    impl = len(df_ativas[df_ativas["Nível"] == "N4 - Implementado"])
    em_and = len(df_ativas[df_ativas["Nível"] != "N4 - Implementado"])

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(kpi("Total de Ideias", total, "blue"), unsafe_allow_html=True)
    with col2: st.markdown(kpi("Potencial 2026", brl(pot_2026), "green"), unsafe_allow_html=True)
    with col3: st.markdown(kpi("Implementadas (N4)", impl, "blue"), unsafe_allow_html=True)
    with col4: st.markdown(kpi("Em Andamento", em_and, "green"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Distribuição por Nível**")
        por_nivel = df_ativas["Nível"].value_counts().reset_index()
        por_nivel.columns = ["Nível","Qtd"]
        st.bar_chart(por_nivel.set_index("Nível"), color="#185FA5")

    with col2:
        st.markdown("**Potencial 2026 por Frente (R$)**")
        por_frente = df_ativas.groupby("Frente de Negócio")["Total 2026"].sum().reset_index()
        por_frente.columns = ["Frente","Total 2026"]
        st.bar_chart(por_frente.set_index("Frente"), color="#3B6D11")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Potencial 2026 por Conta Orçamento (R$)**")
        por_conta = df_ativas.groupby("Conta Orçamento")["Total 2026"].sum().reset_index()
        st.bar_chart(por_conta.set_index("Conta Orçamento"), color="#185FA5")

    with col4:
        st.markdown("**Nº de Ideias por Área**")
        por_area = df_ativas["Área"].value_counts().reset_index()
        por_area.columns = ["Área","Qtd"]
        st.bar_chart(por_area.set_index("Área"), color="#3B6D11")

# ── PÁGINA: EVOLUÇÃO MACRO ─────────────────────────────────────────────────────
def pagina_evolucao():
    u = st.session_state.usuario
    st.markdown('<div class="page-title">📉 Evolução Macro</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Valor acumulado esperado por nível ao longo das semanas</div>', unsafe_allow_html=True)

    df = filtrar_por_perfil(db.ler_oportunidades(), u)
    df_ativas = df[df["Nível"] != "N0 - Cancelada"]

    # Simula evolução semanal por data de movimentação
    st.info("A evolução macro é calculada com base nas datas realizadas de movimentação de nível.")

    # Agrupa por semana/nível com base nas datas realizadas
    niveis_datas = {
        "N2 - Planejamento": "Data Realizada N2",
        "N3 - Execução":     "Data Realizada N3",
        "N4 - Implementado": "Data Realizada N4",
    }

    frames = []
    for nivel, col_data in niveis_datas.items():
        sub = df_ativas[df_ativas[col_data].str.strip() != ""][[col_data,"Total 2026"]].copy()
        if sub.empty: continue
        sub["Data"] = pd.to_datetime(sub[col_data], format="%d/%m/%Y", errors="coerce")
        sub = sub.dropna(subset=["Data"])
        sub["Semana"] = sub["Data"].dt.to_period("W").apply(lambda r: str(r.start_time.date()))
        ag = sub.groupby("Semana")["Total 2026"].sum().reset_index()
        ag["Nível"] = nivel
        frames.append(ag)

    if frames:
        df_ev = pd.concat(frames)
        pivot = df_ev.pivot_table(index="Semana", columns="Nível", values="Total 2026", aggfunc="sum").fillna(0).cumsum()
        st.line_chart(pivot)
    else:
        st.warning("Ainda não há movimentações de nível registradas para gerar a evolução.")

# ── PÁGINA: IDEIAS EM ATRASO ───────────────────────────────────────────────────
def pagina_atraso():
    u = st.session_state.usuario
    st.markdown('<div class="page-title">⚠️ Ideias em Atraso</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Oportunidades com data prevista de avanço ultrapassada</div>', unsafe_allow_html=True)

    df = filtrar_por_perfil(db.ler_oportunidades(), u)
    hoje = datetime.now().date()

    def esta_atrasada(row):
        nivel = str(row["Nível"])[:2]
        if nivel in ("N0","N4"): return False
        if nivel in ("N1","N2"):
            dt = row.get("Data Esperada N3","")
        else:
            dt = row.get("Data Esperada N4","")
        if not str(dt).strip(): return False
        try:
            return datetime.strptime(dt, "%d/%m/%Y").date() < hoje
        except: return False

    df_at = df[df.apply(esta_atrasada, axis=1)].copy()

    if df_at.empty:
        st.success("✅ Nenhuma ideia em atraso no momento.")
        return

    st.warning(f"**{len(df_at)} ideia(s) em atraso**")
    for _, row in df_at.iterrows():
        nivel = str(row["Nível"])[:2]
        dt_prev = row["Data Esperada N3"] if nivel in ("N1","N2") else row["Data Esperada N4"]
        try:
            dias = (hoje - datetime.strptime(dt_prev, "%d/%m/%Y").date()).days
        except: dias = "?"
        st.markdown(f"""
        <div class="card" style="border-left:4px solid #A32D2D;">
          <b>#{row['ID']}</b> — {row['Descrição']}<br>
          <span style="font-size:12px;color:#64748b;">
            {row['Nível']} | {row['Frente de Negócio']} | {row['Craque']}
          </span><br>
          <span style="color:#A32D2D;font-size:12px;font-weight:600;">
            ⏰ Previsto: {dt_prev} — {dias} dia(s) em atraso
          </span>
        </div>
        """, unsafe_allow_html=True)

# ── PÁGINA: RELATÓRIO GERENCIAL ────────────────────────────────────────────────
def pagina_gerencial():
    u = st.session_state.usuario
    st.markdown('<div class="page-title">📑 Relatório Gerencial</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Orçado vs Realizado por frente — valores imputados na aba Orçado do Excel</div>', unsafe_allow_html=True)

    df = filtrar_por_perfil(db.ler_oportunidades(), u)
    df_impl = df[df["Nível"] == "N4 - Implementado"]
    orc = db.ler_orcado()

    anos = [2026, 2027, 2028]
    ano_sel = st.selectbox("Ano", anos)

    orc_ano = orc[orc["Ano"] == str(ano_sel)][["Frente","Total"]].rename(columns={"Total":"Orçado"})

    # Realizado: soma do total do ano das implementadas
    col_real = f"Total {ano_sel}"
    if col_real in df_impl.columns:
        real = df_impl.groupby("Frente de Negócio")[col_real].sum().reset_index()
        real.columns = ["Frente","Realizado"]
    else:
        real = pd.DataFrame(columns=["Frente","Realizado"])

    df_ger = orc_ano.merge(real, on="Frente", how="left").fillna(0)
    df_ger["Orçado"]    = pd.to_numeric(df_ger["Orçado"],    errors="coerce").fillna(0)
    df_ger["Realizado"] = pd.to_numeric(df_ger["Realizado"], errors="coerce").fillna(0)
    df_ger["% Ating."]  = (df_ger["Realizado"] / df_ger["Orçado"].replace(0,1) * 100).round(1)
    df_ger["Gap"]       = df_ger["Realizado"] - df_ger["Orçado"]

    # Formata para exibição
    df_show = df_ger.copy()
    for col in ["Orçado","Realizado","Gap"]:
        df_show[col] = df_show[col].apply(brl)
    df_show["% Ating."] = df_show["% Ating."].astype(str) + "%"
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Realizado vs Orçado por Frente (R$)**")
    chart_data = df_ger.set_index("Frente")[["Orçado","Realizado"]]
    st.bar_chart(chart_data)

    # Distribuição por nível
    st.markdown("**Potencial em cada Nível**")
    por_nivel = df[df["Nível"] != "N0 - Cancelada"].groupby("Nível")["Total 2026"].sum().reset_index()
    por_nivel.columns = ["Nível","Total 2026"]
    por_nivel["Total 2026 (R$)"] = por_nivel["Total 2026"].apply(brl)
    st.dataframe(por_nivel[["Nível","Total 2026 (R$)"]], use_container_width=True, hide_index=True)

# ── ROTEADOR PRINCIPAL ─────────────────────────────────────────────────────────
def main():
    if not st.session_state.usuario:
        tela_login()
        return

    pagina = sidebar()

    if   "Cadastro"    in pagina: pagina_cadastro()
    elif "Tabela"      in pagina: pagina_tabela()
    elif "Dashboard"   in pagina: pagina_dashboard()
    elif "Evolução"    in pagina: pagina_evolucao()
    elif "Atraso"      in pagina: pagina_atraso()
    elif "Gerencial"   in pagina: pagina_gerencial()

if __name__ == "__main__":
    main()
