import streamlit as st
import pandas as pd
from datetime import datetime, date
import base64, time, os, io
import dados as db

st.set_page_config(
    page_title="Programa Essência",
    page_icon="Logo_Essencia.png" if os.path.exists("Logo_Essencia.png") else "💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def obter_bg_base64(caminho):
    if os.path.exists(caminho):
        with open(caminho,"rb") as f: return base64.b64encode(f.read()).decode()
    return ""

bg_base64 = obter_bg_base64("image_7e68ea.jpg")

# ── CSS GLOBAL ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html,body,[class*="css"]{font-family:'Segoe UI','Segoe UI Web (West European)',sans-serif !important;}
.fade-in{animation:fadeIn 0.5s forwards;}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
section[data-testid="stSidebar"] div[role="radiogroup"] label>div:first-child{display:none!important;}
section[data-testid="stSidebar"] div[role="radiogroup"] label{
  background-color:rgba(255,255,255,0.05)!important;border-radius:8px!important;
  padding:12px 16px!important;border:1px solid rgba(255,255,255,0.1)!important;
  margin-bottom:8px!important;width:100%!important;display:flex!important;
  align-items:center!important;transition:all 0.2s!important;cursor:pointer!important;}
section[data-testid="stSidebar"] div[role="radiogroup"] label p{color:#fff!important;font-size:15px!important;margin:0!important;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background-color:rgba(255,255,255,0.1)!important;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background-color:#fff!important;border-color:#fff!important;box-shadow:0 4px 6px rgba(0,0,0,0.1)!important;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p{font-weight:700!important;color:#185FA5!important;}
section[data-testid="stSidebar"]{background-color:#0f172a!important;}
.stButton>button{background-color:#185FA5!important;color:white!important;border-radius:8px!important;font-weight:600!important;border:none!important;}
.stButton>button:hover{background-color:#104a85!important;}
.kpi-container{background:#fff;padding:20px;border-radius:12px;border:1px solid #e2e8f0;text-align:center;}
.kpi-title{font-size:13px;font-weight:600;color:#64748b;text-transform:uppercase;}
.kpi-value{font-size:26px;font-weight:700;color:#0f172a;margin-top:8px;}
.kpi-value-green{font-size:26px;font-weight:700;color:#16a34a;margin-top:8px;}
.kpi-value-orange{font-size:26px;font-weight:700;color:#f97316;margin-top:8px;}
/* Cabeçalho tabela SCO — aplica em todos os dataframes */
thead tr th {
    background-color: #0f172a !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}
thead tr th div {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("usuario"):
    st.markdown(f"""<style>
    .stApp{{background-image:url("data:image/jpg;base64,{bg_base64}");background-size:cover;background-position:center;background-attachment:fixed;}}
    [data-testid="stForm"]{{background:rgba(255,255,255,0.95)!important;backdrop-filter:blur(15px)!important;padding:40px;border-radius:16px;box-shadow:0 12px 32px rgba(0,0,0,0.3);max-width:420px;margin:0 auto;}}
    div[data-baseweb="input"]{{position:relative!important;height:44px!important;background-color:#fff!important;border:1px solid #cbd5e1!important;border-radius:8px!important;}}
    div[data-baseweb="input"]:focus-within{{border-color:#185FA5!important;box-shadow:0 0 0 2px rgba(24,95,165,0.2)!important;}}
    div[data-baseweb="input"] input{{padding-left:12px!important;height:100%!important;background-color:transparent!important;}}
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>[data-testid="stForm"]{background:#fff!important;padding:30px;border-radius:12px;border:1px solid #e2e8f0;width:100%;}</style>""", unsafe_allow_html=True)
    logo = obter_bg_base64("barra_frigelar.png")
    if logo:
        st.markdown(f'<div style="margin-bottom:12px;"><img src="data:image/png;base64,{logo}" style="width:100%;display:block;"></div>', unsafe_allow_html=True)

if "usuario" not in st.session_state: st.session_state.usuario = None

def brl(v):
    try: return f"R$ {float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "R$ 0,00"

def brl_k(v):
    try:
        v = float(v)
        if abs(v) >= 1000: return f"R$ {v/1000:,.1f}k".replace(",",".")
        return f"R$ {v:,.0f}".replace(",",".")
    except: return "R$ 0"

def esta_atrasada(row):
    hoje = datetime.now().date()
    nivel = str(row.get("Nível","")).strip()
    try:
        if "N2" in nivel:
            prev = row.get("Data Prevista N3","")
            if prev:
                d = datetime.strptime(prev.strip(), "%d/%m/%Y").date()
                return hoje > d
        if "N3" in nivel:
            prev = row.get("Data Prevista N4","")
            if prev:
                d = datetime.strptime(prev.strip(), "%d/%m/%Y").date()
                return hoje > d
    except: pass
    return False

# ── HELPER: monta tabela SCO ──────────────────────────────────────────────────
def fmt_data_curta(val):
    """Converte dd/mm/aaaa → mm/aaaa. Retorna vazio se inválido."""
    s = str(val).strip()
    if not s or s == "nan": return ""
    partes = s.split("/")
    if len(partes) >= 3: return f"{partes[1]}/{partes[2]}"
    if len(partes) == 2: return s  # já mm/aaaa
    return s

def montar_tabela_sco(df_in):
    df = df_in.copy()
    meses_abs = db.gerar_colunas_meses_absolutos()  # jan_2026 ... dez_2028

    # garante meses absolutos numéricos
    for m in meses_abs:
        if m not in df.columns: df[m] = 0.0
        else: df[m] = pd.to_numeric(df[m], errors="coerce").fillna(0.0)

    df["Total Estimado 2026"] = pd.to_numeric(df.get("Total Estimado 2026",0), errors="coerce").fillna(0.0)

    # trimestres calculados APENAS pelos meses absolutos de 2026
    nomes = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    tri1 = [f"{nomes[i]}_2026" for i in range(0,3)]   # jan-mar
    tri2 = [f"{nomes[i]}_2026" for i in range(3,6)]   # abr-jun
    tri3 = [f"{nomes[i]}_2026" for i in range(6,9)]   # jul-set
    tri4 = [f"{nomes[i]}_2026" for i in range(9,12)]  # out-dez

    def soma_meses(df, cols):
        return sum(df[c] if c in df.columns else 0 for c in cols)

    df["1°TRI 26"] = soma_meses(df, tri1)
    df["2°TRI 26"] = soma_meses(df, tri2)
    df["3°TRI 26"] = soma_meses(df, tri3)
    df["4°TRI 26"] = soma_meses(df, tri4)

    # formata datas para mm/aaaa
    cols_data = ["Data Realizada N1","Data Prevista N2","Data Realizada N2",
                 "Data Prevista N3","Data Realizada N3","Data Prevista N4","Data Realizada N4"]
    for c in cols_data:
        if c in df.columns:
            df[c] = df[c].apply(fmt_data_curta)

    # Título SEMPRE primeiro, depois o restante
    colunas_base = ["Título","Comentário da Semana","Nível","Grupo Contábil","Frente de Negócio",
        "Conta Orçamento","Conta Contábil",
        "Data Realizada N1","Data Prevista N2","Data Realizada N2",
        "Data Prevista N3","Data Realizada N3","Data Prevista N4","Data Realizada N4",
        "1°TRI 26","2°TRI 26","3°TRI 26","4°TRI 26","Total Estimado 2026",
        "Dono da Oportunidade","CC Dono","Filial","Craque","Area Craque"]
    cols = [c for c in colunas_base if c in df.columns]
    if "Título" not in cols and "Título" in df.columns:
        cols = ["Título"] + cols

    df_d = df[cols].copy().rename(columns={
        "Título":"Título da Oportunidade","Nível":"Status",
        "Frente de Negócio":"Frente","Total Estimado 2026":"Total 2026",
        "Dono da Oportunidade":"Dono","Data Realizada N1":"N1 (Real)",
        "Data Prevista N2":"N2 (Prev)","Data Realizada N2":"N2 (Real)",
        "Data Prevista N3":"N3 (Prev)","Data Realizada N3":"N3 (Real)",
        "Data Prevista N4":"N4 (Prev)","Data Realizada N4":"N4 (Real)",
        "Area Craque":"Área Craque",
    })
    for col in ["1°TRI 26","2°TRI 26","3°TRI 26","4°TRI 26","Total 2026"]:
        if col in df_d.columns:
            df_d[col] = df_d[col].apply(lambda v: brl_k(v) if v != "" else "R$ 0")
    return df_d

def gerar_excel_sco(df_in) -> bytes:
    """Gera Excel com todas as colunas do documento + meses absolutos."""
    import re
    df = df_in.copy()
    meses_abs = db.gerar_colunas_meses_absolutos()  # jan_2026 etc (com underscore)

    # garante meses absolutos numéricos
    for m in meses_abs:
        if m not in df.columns: df[m] = 0.0
        else: df[m] = pd.to_numeric(df[m], errors="coerce").fillna(0.0)
    for i in range(1, 13):
        col = f"M{i}"
        if col not in df.columns: df[col] = 0.0
        else: df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # padrão de mês absoluto legado (com barra): jan/2026, fev/2027 etc
    padrao_mes_legado = re.compile(r'^(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)/\d{4}$')

    colunas_priority = [
        "Título","Descrição","Nível","Grupo Contábil","Frente de Negócio",
        "Conta Orçamento","Conta Contábil","Dono da Oportunidade","CC Dono",
        "Filial","Craque","Area Craque","Comentário da Semana",
        "Justificativa Cancelamento","ID","Submetido Controladoria",
        "Data Realizada N1","Data Prevista N2","Data Realizada N2",
        "Data Prevista N3","Data Realizada N3","Data Prevista N4","Data Realizada N4",
        "Total Estimado 2026",
        "M1","M2","M3","M4","M5","M6","M7","M8","M9","M10","M11","M12",
    ] + meses_abs

    # extras: qualquer coluna que não seja priority, não seja interna (_) e não seja mês legado
    extras = [
        c for c in df.columns
        if c not in colunas_priority
        and not c.startswith("_")
        and not padrao_mes_legado.match(str(c))
    ]
    todas = [c for c in colunas_priority if c in df.columns] + [c for c in extras if c in df.columns]

    cols_laranja = {
        "Data Prevista N2","Data Prevista N3","Data Prevista N4",
        "Total Estimado 2026","M1","M2","M3","M4","M5","M6",
        "M7","M8","M9","M10","M11","M12"
    } | set(meses_abs)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df[todas].to_excel(writer, index=False, sheet_name="SCO")
        wb = writer.book; ws = writer.sheets["SCO"]
        fmt_azul    = wb.add_format({"bold":True,"bg_color":"#0f172a","font_color":"#ffffff","border":1,"text_wrap":True})
        fmt_laranja = wb.add_format({"bold":True,"bg_color":"#f97316","font_color":"#ffffff","border":1,"text_wrap":True})
        for i, col in enumerate(todas):
            fmt = fmt_laranja if col in cols_laranja else fmt_azul
            label = db.chave_para_label(col) if col in set(meses_abs) else col
            ws.write(0, i, label, fmt)
            ws.set_column(i, i, max(len(label)+2, 14))
    return buf.getvalue()

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def tela_login():
    col1,col2,col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<br><br><br>",unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h2 style='text-align:center;color:#0f172a;'>Bem-vindo(a)</h2>",unsafe_allow_html=True)
            login = st.text_input("Usuário",placeholder="seu login",icon=":material/person:")
            senha = st.text_input("Senha",type="password",placeholder="sua senha",icon=":material/lock:")
            if st.form_submit_button("Entrar",width="stretch",type="primary"):
                if login.strip() and senha.strip():
                    ui = db.autenticar(login.strip(),senha.strip())
                    if ui: st.session_state.usuario=ui; st.rerun()
                    else: st.error("Usuário ou senha incorretos.")
                else: st.warning("Preencha login e senha.")

# ── NAVEGAÇÃO ─────────────────────────────────────────────────────────────────
def painel_principal():
    u = st.session_state.usuario
    hora = datetime.now().hour
    saudacao = "Bom dia" if hora<12 else "Boa tarde" if hora<18 else "Boa noite"
    with st.sidebar:
        st.markdown(f'<div style="padding:10px 0 20px 0;"><span style="font-size:18px;font-weight:700;color:#fff;">{saudacao}, {u["nome"].split()[0]}!</span><p style="font-size:12px;color:#94a3b8;margin-top:4px;">Perfil: {u["perfil"].upper()}</p></div>',unsafe_allow_html=True)
        menu = []
        if u["perfil"] in ("craque","lider","adm"): menu.extend(["Cadastro de Oportunidade","SCO - Oportunidades"])
        if u["perfil"] in ("lider","adm","diretoria"): menu.append("Painel Executivo")
        if u["perfil"]=="adm": menu.extend(["Comitê de Despesas (N1)","Validação Controladoria","Painel de Acessos","Log de Alterações"])
        pagina = st.radio("Nav",menu,label_visibility="collapsed")
        st.markdown("<br><hr style='border-color:rgba(255,255,255,0.1);'>",unsafe_allow_html=True)
        if st.button("Sair",use_container_width=True): st.session_state.usuario=None; st.rerun()

    st.markdown('<div class="fade-in">',unsafe_allow_html=True)
    if pagina=="Cadastro de Oportunidade": pagina_cadastro()
    elif pagina=="SCO - Oportunidades": pagina_sco()
    elif pagina=="Painel Executivo": pagina_painel_integrado()
    elif pagina=="Comitê de Despesas (N1)": pagina_comite()
    elif pagina=="Validação Controladoria": pagina_controladoria()
    elif pagina=="Painel de Acessos": pagina_admin()
    elif pagina=="Log de Alterações": pagina_log()
    st.markdown('</div>',unsafe_allow_html=True)

# ── CADASTRO ──────────────────────────────────────────────────────────────────
def pagina_cadastro():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Cadastro de Oportunidade</h2>',unsafe_allow_html=True)
    df_pc = db.ler_plano_contas()
    with st.container(border=True):
        st.markdown("##### 1. Detalhes do Escopo")
        titulo = st.text_input("Título da Melhoria *", max_chars=80)
        descricao = st.text_area("Descrição da Melhoria *", max_chars=600)
        col1,col2 = st.columns(2)
        with col1:
            dono = st.text_input("Dono da Oportunidade *")
            filial_sel = st.selectbox("Filial *",[""] + db.ler_filiais())
            grupo_contabil = st.selectbox("Grupo Contábil *",["","ADM","COM","IND"])
        with col2:
            cc_dono = st.selectbox("Centro de Custo (CC Dono) *",[""] + db.ler_centros_custo())

        st.markdown("<br>##### 2. Classificação Contábil",unsafe_allow_html=True)
        cg2,cg3 = st.columns(2)
        with cg2:
            contas_orc = sorted(df_pc["ContaOrc"].unique().tolist())
            conta_orc_sel = st.selectbox("Conta Orçamento *",[""] + contas_orc)
        with cg3:
            filtradas = df_pc[df_pc["ContaOrc"]==conta_orc_sel] if conta_orc_sel else pd.DataFrame()
            opcoes_cont = [f"{r['Código']} - {r['ContaCont']}" for _,r in filtradas.iterrows()]
            conta_cont_sel = st.selectbox("Conta Contábil *",[""] + opcoes_cont)
        frente_det = ""
        if conta_cont_sel:
            cod = conta_cont_sel.split(" - ")[0]
            try: frente_det = df_pc[df_pc["Código"]==cod].iloc[0]["Frente"]
            except: pass
            st.info(f"Frente detectada automaticamente: **{frente_det}**")

        st.markdown("<br>##### 3. Valor e Datas Iniciais",unsafe_allow_html=True)
        cv,cd1,cd2 = st.columns(3)
        with cv: ganho = st.number_input("Ganho Estimado 2026 (R$) *",min_value=0.0,step=100.0)
        with cd1: dpn3 = st.text_input("Data Prevista N3 (dd/mm/aaaa)")
        with cd2: dpn4 = st.text_input("Data Prevista N4 (dd/mm/aaaa)")

        if st.button("Salvar Registro (N1)",use_container_width=True,type="primary"):
            if not (titulo.strip() and descricao.strip() and dono.strip() and cc_dono and conta_orc_sel and conta_cont_sel and filial_sel and grupo_contabil):
                st.error("Preencha todos os campos obrigatórios (*).")
            elif db.titulo_ja_existe(titulo):
                st.error(f"Já existe uma oportunidade com o título '{titulo}'. Escolha outro.")
            else:
                db.cadastrar_oportunidade({
                    "titulo":titulo,"descricao":descricao,"grupo_contabil":grupo_contabil,
                    "dono":dono,"cc_dono":cc_dono,"conta_orc":conta_orc_sel,
                    "conta_cont":conta_cont_sel.split(" - ",1)[-1],
                    "filial":filial_sel,"frente_automatica":frente_det,
                    "ganho_2026":ganho,"data_prev_n3":dpn3,"data_prev_n4":dpn4,
                    "area_craque": u.get("area_craque","")
                }, u)
                st.success("Oportunidade enviada para aprovação do Comitê (N1)!"); time.sleep(1.5); st.rerun()

# ── SCO - OPORTUNIDADES ───────────────────────────────────────────────────────
def pagina_sco():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">SCO - Oportunidades</h2>',unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: st.info("Nenhuma oportunidade cadastrada."); return
    df["Nível"] = df["Nível"].astype(str).str.strip()
    if u["perfil"]=="craque": df = df[df["Craque"].str.lower()==u["nome"].lower()]
    elif u["perfil"]=="lider": df = df[df["Frente de Negócio"].str.lower()==u["frente"].lower()]
    if df.empty: st.info("Nenhuma oportunidade encontrada para seu perfil."); return

    # ── FILTROS ────────────────────────────────────────────────────────────────
    st.markdown("##### Filtros")
    def opt(col): return sorted(df[col].dropna().astype(str).unique().tolist()) if col in df.columns else []

    col_f = st.columns(4)
    with col_f[0]: f_status = st.multiselect("Status", opt("Nível"), default=[], key="f_status", placeholder="Todos")
    with col_f[1]: f_frente = st.multiselect("Frente", opt("Frente de Negócio"), default=[], key="f_frente", placeholder="Todas")
    with col_f[2]: f_gc     = st.multiselect("Grupo Contábil", ["ADM","COM","IND"], default=[], key="f_gc", placeholder="Todos")
    with col_f[3]: f_filial = st.multiselect("Filial", opt("Filial"), default=[], key="f_filial", placeholder="Todas")

    col_f2 = st.columns(4)
    with col_f2[0]: f_dono   = st.multiselect("Dono", opt("Dono da Oportunidade"), default=[], key="f_dono", placeholder="Todos")
    with col_f2[1]: f_cc     = st.multiselect("CC Dono", opt("CC Dono"), default=[], key="f_cc", placeholder="Todos")
    with col_f2[2]: f_craque = st.multiselect("Craque", opt("Craque"), default=[], key="f_craque", placeholder="Todos")
    with col_f2[3]: f_conta  = st.multiselect("Conta Orç.", opt("Conta Orçamento"), default=[], key="f_conta", placeholder="Todas")

    col_txt = st.columns(3)
    with col_txt[0]: txt_tit  = st.text_input("🔍 Título", key="txt_tit")
    with col_txt[1]: txt_desc = st.text_input("🔍 Descrição", key="txt_desc")
    with col_txt[2]: txt_cc   = st.text_input("🔍 Conta Contábil", key="txt_cc")

    if st.button("🔄 Limpar Filtros", key="limpar"):
        for k in ["f_status","f_frente","f_gc","f_filial","f_dono","f_cc","f_craque","f_conta","txt_tit","txt_desc","txt_cc"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    df_f = df.copy()
    if f_status:  df_f = df_f[df_f["Nível"].isin(f_status)]
    if f_frente:  df_f = df_f[df_f["Frente de Negócio"].isin(f_frente)]
    if f_gc and "Grupo Contábil" in df_f.columns: df_f = df_f[df_f["Grupo Contábil"].isin(f_gc)]
    if f_filial:  df_f = df_f[df_f["Filial"].isin(f_filial)]
    if f_dono:    df_f = df_f[df_f["Dono da Oportunidade"].isin(f_dono)]
    if f_cc:      df_f = df_f[df_f["CC Dono"].isin(f_cc)]
    if f_craque:  df_f = df_f[df_f["Craque"].isin(f_craque)]
    if f_conta:   df_f = df_f[df_f["Conta Orçamento"].isin(f_conta)]
    if txt_tit.strip():  df_f = df_f[df_f["Título"].astype(str).str.contains(txt_tit,case=False,na=False)]
    if txt_desc.strip(): df_f = df_f[df_f.get("Descrição",pd.Series(dtype=str)).astype(str).str.contains(txt_desc,case=False,na=False)]
    if txt_cc.strip():   df_f = df_f[df_f["Conta Contábil"].astype(str).str.contains(txt_cc,case=False,na=False)]

    # sinaliza atrasadas — reset de índice para alinhar corretamente
    df_f = df_f.reset_index(drop=True)
    df_f["_atrasada"] = df_f.apply(esta_atrasada, axis=1)

    # subtotal considerando filtros
    total_filtrado = pd.to_numeric(df_f["Total Estimado 2026"], errors="coerce").fillna(0.0).sum()
    col_info, col_total = st.columns([3,1])
    with col_info: st.markdown(f"**{len(df_f)} oportunidade(s) filtrada(s)**")
    with col_total: st.markdown(f"**Subtotal 2026: {brl_k(total_filtrado)}**")

    df_disp = montar_tabela_sco(df_f).reset_index(drop=True)
    atrasadas = df_f["_atrasada"].values

    def highlight_atraso(row):
        if atrasadas[row.name]:
            return ["background-color: #fef9c3; color: #713f12;"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_disp.style.apply(highlight_atraso, axis=1),
        use_container_width=True,
        hide_index=True
    )

    # botão exportar — todas as colunas do documento
    excel_bytes = gerar_excel_sco(df_f)
    st.download_button("📥 Exportar Excel", data=excel_bytes,
        file_name=f"SCO_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.ms-excel")

    # ── PAINEL DE AÇÕES ────────────────────────────────────────────────────────
    if u["perfil"] in ("lider","adm"):
        st.markdown("---")
        st.markdown("##### Ações na Oportunidade")
        opcoes = ["Selecione..."] + [str(r.get("Título",""))[:70] for _,r in df_f.iterrows()]
        sel = st.selectbox("Selecione para editar",opcoes,key="sel_op")
        if sel != "Selecione...":
            matches = df_f[df_f["Título"].astype(str).str[:70]==sel.strip()]
            if matches.empty: st.warning("Não encontrada."); return
            row = matches.iloc[0]; id_sel = row["ID"]; nivel_atual = str(row["Nível"]).strip()

            tab_c, tab_e, tab_n = st.tabs(["💬 Comentário","✏️ Editar Campos","🔄 Movimentar Nível"])

            with tab_c:
                hist = str(row.get("Comentário da Semana","")).strip()
                if hist: st.markdown(f"**Histórico:**\n\n{hist}"); st.divider()
                with st.form(f"fc_{id_sel}"):
                    nc = st.text_area("Novo comentário:")
                    if st.form_submit_button("💬 Salvar",type="primary"):
                        if nc.strip(): db.adicionar_comentario(id_sel,nc,u); st.success("Salvo!"); st.rerun()
                        else: st.warning("Digite algo.")

            with tab_e:
                df_pc = db.ler_plano_contas()
                st.info("""ℹ️ **Guia de preenchimento de datas e valores:**
- **Data N3** = data prevista para início da execução da ideia.
- **Data N4** = data prevista para início da **captura do ganho**.
- Os valores M1 a M12 representam os ganhos projetados **a partir do mês em que a ideia entra em N4**.
- Exemplo: se a Data N4 prevista é agosto/2026, M1 = ago/26, M2 = set/26, M3 = out/26, e assim por diante.
- O sistema mapeará automaticamente para os meses absolutos na exportação Excel.""")

                with st.form(f"fe_{id_sel}"):
                    nova_desc = st.text_area("Descrição", value=str(row.get("Descrição","")), max_chars=600)
                    novo_gc = st.selectbox("Grupo Contábil", ["ADM","COM","IND"],
                        index=["ADM","COM","IND"].index(row.get("Grupo Contábil","ADM")) if row.get("Grupo Contábil","ADM") in ["ADM","COM","IND"] else 0)

                    ce1,ce2 = st.columns(2)
                    with ce1:
                        contas_orc = sorted(df_pc["ContaOrc"].unique().tolist())
                        idx_orc = contas_orc.index(row.get("Conta Orçamento","")) if row.get("Conta Orçamento","") in contas_orc else 0
                        nova_orc = st.selectbox("Conta Orçamento", contas_orc, index=idx_orc)
                    with ce2:
                        filt = df_pc[df_pc["ContaOrc"]==nova_orc]
                        opts = [f"{r['Código']} - {r['ContaCont']}" for _,r in filt.iterrows()]
                        nova_cont_sel = st.selectbox("Conta Contábil", opts if opts else [""], index=0)

                    nova_frente = ""
                    if nova_cont_sel and " - " in nova_cont_sel:
                        try: nova_frente = df_pc[df_pc["Código"]==nova_cont_sel.split(" - ")[0]].iloc[0]["Frente"]
                        except: pass
                    if nova_frente: st.info(f"Frente detectada: **{nova_frente}**")

                    cd1e,cd2e = st.columns(2)
                    nd3 = cd1e.text_input("Data Prevista N3 (dd/mm/aaaa)", value=str(row.get("Data Prevista N3","")))
                    nd4 = cd2e.text_input("Data Prevista N4 (dd/mm/aaaa)", value=str(row.get("Data Prevista N4","")))

                    st.markdown("**Valores mensais de economia (M1 a M12):**")
                    cols_m = st.columns(6)
                    vals_m = {}
                    for i in range(1,13):
                        with cols_m[(i-1)%6]:
                            v_atual = float(row.get(f"M{i}",0) or 0)
                            vals_m[f"M{i}"] = st.number_input(f"M{i}", value=v_atual, step=100.0, key=f"m{i}_{id_sel}")

                    if st.form_submit_button("✏️ Salvar Edições",type="primary"):
                        campos = {
                            "Descrição": nova_desc, "Grupo Contábil": novo_gc,
                            "Conta Orçamento": nova_orc,
                            "Conta Contábil": nova_cont_sel.split(" - ",1)[-1] if nova_cont_sel else "",
                            "Frente de Negócio": nova_frente,
                            "Data Prevista N3": nd3, "Data Prevista N4": nd4,
                        }
                        for k,v in vals_m.items(): campos[k] = v
                        db.editar_campos_oportunidade(id_sel, campos, u)
                        st.success("Campos atualizados!"); st.rerun()

            with tab_n:
                st.markdown(f"**Status atual:** `{nivel_atual}`")

                if "N1" in nivel_atual:
                    st.info("ℹ️ Em N1 — aprovação para N2 é feita pelo Comitê de Despesas.")
                    st.markdown("---")
                    if st.button("✖ Cancelar esta ideia (→N0)", key=f"n0n1_{id_sel}", use_container_width=True):
                        db.movimentar_nivel(id_sel,"N0 - Cancelada",u); st.success("Cancelada."); st.rerun()

                elif "N2" in nivel_atual:
                    dpn3 = str(row.get("Data Prevista N3","")).strip()
                    dpn4 = str(row.get("Data Prevista N4","")).strip()
                    vals_ok = any(float(row.get(f"M{i}",0) or 0) > 0 for i in range(1,13))
                    if not dpn3 or not dpn4 or not vals_ok:
                        st.warning("⚠️ Para avançar para N3 preencha: Data Prevista N3, Data Prevista N4 e ao menos um valor mensal (M1–M12) na aba ✏️ Editar Campos.")
                    else:
                        if st.button("▶ Iniciar Execução (N2→N3)", key=f"n3_{id_sel}", use_container_width=True, type="primary"):
                            db.movimentar_nivel(id_sel,"N3 - Execução",u); st.success("Movido para N3!"); st.rerun()
                    st.markdown("---")
                    if st.button("✖ Cancelar esta ideia (→N0)", key=f"n0n2_{id_sel}", use_container_width=True):
                        db.movimentar_nivel(id_sel,"N0 - Cancelada",u); st.success("Cancelada."); st.rerun()

                elif "N3" in nivel_atual:
                    sub = row.get("Submetido Controladoria",False)
                    if not sub:
                        if st.button("📋 Submeter para Controladoria (→N4)", key=f"sub_{id_sel}", type="primary", use_container_width=True):
                            db.submeter_para_controladoria(id_sel,u); st.success("Enviado!"); st.rerun()
                    else:
                        st.warning("⏳ Aguardando validação da Controladoria.")
                    st.markdown("---")
                    if st.button("✖ Cancelar esta ideia (→N0)", key=f"n0n3_{id_sel}", use_container_width=True):
                        db.movimentar_nivel(id_sel,"N0 - Cancelada",u); st.success("Cancelada."); st.rerun()

                elif "N4" in nivel_atual:
                    st.success("✅ Implementada (N4).")
                    st.markdown("---")
                    if st.button("↩ Reabrir (N4→N3)", key=f"reabrir_{id_sel}", use_container_width=True):
                        db.movimentar_nivel(id_sel,"N3 - Execução",u); st.success("Reaberta para N3."); st.rerun()

                elif "N0" in nivel_atual:
                    st.error("Ideia cancelada (N0).")
                    st.markdown("---")
                    if st.button("↩ Reativar (N0→N1)", key=f"reativar_{id_sel}", use_container_width=True):
                        db.movimentar_nivel(id_sel,"N1 - Ideia",u); st.success("Reativada para N1."); st.rerun()

# ── COMITÊ (N1→N2) ────────────────────────────────────────────────────────────
def pagina_comite():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Comitê de Despesas (Aprovação N1)</h2>',unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: return
    df["Nível"] = df["Nível"].astype(str).str.strip()
    df_n1 = df[df["Nível"]=="N1 - Ideia"]
    if df_n1.empty: st.success("Nenhuma ideia aguardando aprovação."); return

    st.markdown(f"**{len(df_n1)} oportunidade(s) aguardando**")
    st.dataframe(montar_tabela_sco(df_n1.copy()), use_container_width=True, hide_index=True)

    st.markdown("---")
    opcoes = ["Selecione..."] + [str(r.get("Título",""))[:70] for _,r in df_n1.iterrows()]
    sel = st.selectbox("Selecione para aprovar/rejeitar", opcoes, key="sel_comite")
    if sel != "Selecione...":
        matches = df_n1[df_n1["Título"].astype(str).str[:70]==sel.strip()]
        if matches.empty: return
        row = matches.iloc[0]; id_sel = row["ID"]
        with st.container(border=True):
            st.markdown(f"**{row.get('Título','')}** | {row.get('Craque','')} | {brl(row.get('Total Estimado 2026',0))}")
            c1,c2 = st.columns(2)
            with c1:
                if st.button("✅ Aprovar (N1→N2)",key=f"apr_{id_sel}",use_container_width=True,type="primary"):
                    db.movimentar_nivel(id_sel,"N2 - Planejamento",u); st.success("Aprovada!"); st.rerun()
            with c2:
                with st.form(f"form_rej_{id_sel}"):
                    just = st.text_area("Justificativa para rejeição *")
                    if st.form_submit_button("❌ Rejeitar (→N0)",use_container_width=True):
                        if just.strip():
                            db.movimentar_nivel(id_sel,"N0 - Cancelada",u,justificativa=just)
                            st.success("Rejeitada."); st.rerun()
                        else: st.error("Informe a justificativa para rejeitar.")

# ── CONTROLADORIA (N3→N4) ─────────────────────────────────────────────────────
def pagina_controladoria():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Validação Controladoria (Aprovação N4)</h2>',unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: return
    df["Nível"] = df["Nível"].astype(str).str.strip()
    df_n3 = df[(df["Nível"]=="N3 - Execução")&(df["Submetido Controladoria"]==True)]
    if df_n3.empty: st.success("Nenhuma ideia aguardando validação."); return

    st.markdown(f"**{len(df_n3)} oportunidade(s) aguardando**")
    st.dataframe(montar_tabela_sco(df_n3.copy()), use_container_width=True, hide_index=True)

    st.markdown("---")
    opcoes = ["Selecione..."] + [str(r.get("Título",""))[:70] for _,r in df_n3.iterrows()]
    sel = st.selectbox("Selecione para validar", opcoes, key="sel_ctrl")
    if sel != "Selecione...":
        matches = df_n3[df_n3["Título"].astype(str).str[:70]==sel.strip()]
        if matches.empty: return
        row = matches.iloc[0]; id_sel = row["ID"]
        with st.container(border=True):
            st.markdown(f"**{row.get('Título','')}** | {row.get('Frente de Negócio','')} | {brl(row.get('Total Estimado 2026',0))}")
            if st.button("🏆 Validar Savings — Implementado (N4)",key=f"val_{id_sel}",type="primary",use_container_width=True):
                db.movimentar_nivel(id_sel,"N4 - Implementado",u); st.success("Implementado!"); st.rerun()

# ── PAINEL EXECUTIVO ──────────────────────────────────────────────────────────
def pagina_painel_integrado():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">Painel Executivo</h2>',unsafe_allow_html=True)
    df = db.ler_oportunidades()
    if df.empty: st.info("Sem dados."); return

    df["Nível"] = df["Nível"].astype(str).str.strip()
    df["Frente de Negócio"] = df["Frente de Negócio"].astype(str).str.strip()
    df["Total Estimado 2026"] = pd.to_numeric(df["Total Estimado 2026"],errors="coerce").fillna(0.0)

    # Filtros globais painel
    frentes = db.ler_frentes()
    niveis_opcoes = ["N1 - Ideia","N2 - Planejamento","N3 - Execução","N4 - Implementado","N0 - Cancelada"]
    cf1,cf2 = st.columns(2)
    with cf1: f_frente_p = st.multiselect("Filtrar por Frente",frentes,default=[],key="pf_frente",placeholder="Todas")
    with cf2: f_nivel_p  = st.multiselect("Filtrar por Nível",niveis_opcoes,default=[],key="pf_nivel",placeholder="Todos")

    df_p = df.copy()
    if u["perfil"]=="lider": df_p = df_p[df_p["Frente de Negócio"].str.lower()==u["frente"].lower()]
    if f_frente_p: df_p = df_p[df_p["Frente de Negócio"].isin(f_frente_p)]
    if f_nivel_p:  df_p = df_p[df_p["Nível"].isin(f_nivel_p)]

    df_ativas = df_p[df_p["Nível"]!="N0 - Cancelada"]
    orc_data = db.ler_orcamento()
    total_orcado = sum(orc_data.get(f,0.0) for f in frentes)
    total_realizado = df_p[df_p["Nível"]=="N4 - Implementado"]["Total Estimado 2026"].sum()

    tab_dash, tab_matriz, tab_evo, tab_ger, tab_excel = st.tabs([
        "📊 Dashboard", "📋 Matriz & Comparativo", "📈 Evolução", "📑 Rel. Gerencial", "📥 Base Excel"
    ])

    with tab_dash:
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.markdown(f'<div class="kpi-container"><div class="kpi-title">Ideias Ativas</div><div class="kpi-value">{len(df_ativas)}</div></div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-container"><div class="kpi-title">Potencial 2026</div><div class="kpi-value-green">{brl_k(df_ativas["Total Estimado 2026"].sum())}</div></div>',unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-container"><div class="kpi-title">Implementadas (N4)</div><div class="kpi-value">{len(df_p[df_p["Nível"]=="N4 - Implementado"])}</div></div>',unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-container"><div class="kpi-title">Total Orçado</div><div class="kpi-value-orange">{brl_k(total_orcado)}</div></div>',unsafe_allow_html=True)
        c5.markdown(f'<div class="kpi-container"><div class="kpi-title">Realizado vs Orçado</div><div class="kpi-value">{(total_realizado/total_orcado*100) if total_orcado>0 else 0:.1f}%</div></div>',unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("**Ideias por Nível**")
            vc = df_p["Nível"].value_counts()
            st.bar_chart(vc, color="#185FA5")
            st.markdown("**Ideias por Frente**")
            fi = df_ativas.groupby("Frente de Negócio").size()
            st.bar_chart(fi, color="#16a34a")
        with g2:
            st.markdown("**Valores por Nível**")
            vv = df_p.groupby("Nível")["Total Estimado 2026"].sum()
            st.bar_chart(vv, color="#185FA5")
            st.markdown("**Valores por Frente**")
            fv = df_ativas.groupby("Frente de Negócio")["Total Estimado 2026"].sum()
            st.bar_chart(fv, color="#16a34a")

    with tab_matriz:
        niveis_ativos = ["N1 - Ideia","N2 - Planejamento","N3 - Execução","N4 - Implementado"]
        st.markdown("#### Posição Atual — Frentes × Níveis")
        linhas = []
        for frente in frentes:
            linha = {"Frente": frente}
            total_fr = 0.0; total_qtd = 0
            for nivel in niveis_ativos:
                sub = df_p[(df_p["Frente de Negócio"]==frente) & (df_p["Nível"]==nivel)]
                qtd = len(sub); val = sub["Total Estimado 2026"].sum()
                nc = nivel.split(" - ")[0]
                linha[f"{nc} Qtd"] = qtd
                linha[f"{nc} R$"] = brl_k(val)
                linha[f"_{nc}_val"] = val
                total_fr += val; total_qtd += qtd
            linha["Total Qtd"] = total_qtd
            linha["Total R$"] = brl_k(total_fr)
            linhas.append(linha)
        total_row = {"Frente": "TOTAL"}
        for nivel in niveis_ativos:
            nc = nivel.split(" - ")[0]
            sub = df_p[df_p["Nível"]==nivel]
            total_row[f"{nc} Qtd"] = len(sub)
            total_row[f"{nc} R$"] = brl_k(sub["Total Estimado 2026"].sum())
            total_row[f"_{nc}_val"] = sub["Total Estimado 2026"].sum()
        total_row["Total Qtd"] = len(df_p[df_p["Nível"].isin(niveis_ativos)])
        total_row["Total R$"] = brl_k(df_p[df_p["Nível"].isin(niveis_ativos)]["Total Estimado 2026"].sum())
        linhas.append(total_row)
        cols_ex = ["Frente"] + [f"{n.split(' - ')[0]} Qtd" for n in niveis_ativos] +                   [f"{n.split(' - ')[0]} R$" for n in niveis_ativos] + ["Total Qtd","Total R$"]
        df_matriz = pd.DataFrame(linhas)[cols_ex]
        st.dataframe(df_matriz, use_container_width=True, hide_index=True)

        st.markdown("---")
        col_snap1, col_snap2 = st.columns([2,1])
        with col_snap2:
            if u["perfil"] == "adm":
                if st.button("📸 Registrar posição desta semana", type="primary", use_container_width=True):
                    semana_id = db.salvar_snapshot(df_p, u)
                    st.success(f"Snapshot registrado: {semana_id}"); st.rerun()

        snaps = db.ler_snapshots()
        if len(snaps) >= 2:
            st.markdown("#### Comparativo com semana anterior")
            snap_atual = snaps[0]; snap_ant = snaps[1]
            st.caption(f"Comparando **{snap_atual['data']}** (atual) vs **{snap_ant['data']}** (anterior)")

            def indexar(snap):
                idx = {}
                for r in snap.get("dados",[]):
                    n = r["nivel"]; f = r["frente"]
                    if n not in idx: idx[n] = {}
                    idx[n][f] = {"qtd": r["qtd"], "valor": r["valor"]}
                return idx

            atual_idx = indexar(snap_atual)
            ant_idx   = indexar(snap_ant)
            textos = []
            for nivel in niveis_ativos:
                frentes_com_mudanca = []
                delta_total_val = 0.0; delta_total_qtd = 0
                for frente in frentes:
                    v_at = atual_idx.get(nivel,{}).get(frente,{}).get("valor",0.0)
                    v_an = ant_idx.get(nivel,{}).get(frente,{}).get("valor",0.0)
                    q_at = atual_idx.get(nivel,{}).get(frente,{}).get("qtd",0)
                    q_an = ant_idx.get(nivel,{}).get(frente,{}).get("qtd",0)
                    dv = v_at - v_an; dq = q_at - q_an
                    if abs(dv) > 0.01 or dq != 0:
                        sv = "+" if dv >= 0 else ""
                        sq = "+" if dq >= 0 else ""
                        det = f"{frente}: {sv}{brl_k(dv)}"
                        if dq != 0: det += f" ({sq}{dq} ideia{'s' if abs(dq)!=1 else ''})"
                        frentes_com_mudanca.append(det)
                        delta_total_val += dv; delta_total_qtd += dq
                if frentes_com_mudanca:
                    sv = "+" if delta_total_val >= 0 else ""
                    sq = "+" if delta_total_qtd >= 0 else ""
                    resumo = f"**{nivel}:** potencial {sv}{brl_k(delta_total_val)}"
                    if delta_total_qtd != 0:
                        resumo += f", {sq}{delta_total_qtd} ideia{'s' if abs(delta_total_qtd)!=1 else ''}"
                    resumo += f". Por frente — " + "; ".join(frentes_com_mudanca) + "."
                    textos.append(resumo)
            if textos:
                for t in textos: st.markdown(f"- {t}")
            else:
                st.info("Nenhuma variação entre os dois últimos snapshots.")
        elif len(snaps) == 1:
            st.info(f"Snapshot de {snaps[0]['data']} registrado. Registre mais um na próxima semana para ver o comparativo.")
        else:
            st.info("Nenhum snapshot registrado ainda. Clique em '📸 Registrar posição desta semana' para começar.")

    with tab_evo:
        df_ev = df_ativas.copy()
        df_ev["Semana"] = df_ev["Data Cadastro (N1)"].apply(
            lambda x: f"Sem.{x.split('/')[1]}/{x.split('/')[2]}" if pd.notna(x) and x and "/" in str(x) else "?")
        evo = df_ev.groupby(["Semana","Nível"])["Total Estimado 2026"].sum().unstack().fillna(0)
        st.markdown("**Evolução por Semana de Cadastro**")
        st.bar_chart(evo)
    with tab_ger:
        if u["perfil"]=="adm":
            with st.expander("⚙️ Ajustar Metas Orçadas"):
                with st.form("form_orc"):
                    cols_orc = st.columns(len(frentes))
                    vals_orc = {f: cols_orc[i].number_input(f, value=float(orc_data.get(f,0.0)), step=10000.0) for i,f in enumerate(frentes)}
                    if st.form_submit_button("Salvar", type="primary"):
                        db.salvar_orcamento(vals_orc); st.success("Atualizado!"); time.sleep(1); st.rerun()

        relatorio = []
        for f in frentes:
            df_f2 = df_p[df_p["Frente de Negócio"]==f]
            n1 = df_f2[df_f2["Nível"]=="N1 - Ideia"]["Total Estimado 2026"].sum()
            n2 = df_f2[df_f2["Nível"]=="N2 - Planejamento"]["Total Estimado 2026"].sum()
            n3 = df_f2[df_f2["Nível"]=="N3 - Execução"]["Total Estimado 2026"].sum()
            n4 = df_f2[df_f2["Nível"]=="N4 - Implementado"]["Total Estimado 2026"].sum()
            total = n1+n2+n3+n4
            orc = orc_data.get(f, 0.0)
            relatorio.append({
                "Frente": f,
                "N1 - Ideia": brl_k(n1),
                "N2 - Planejamento": brl_k(n2),
                "N3 - Execução": brl_k(n3),
                "N4 - Implementado": brl_k(n4),
                "Total": brl_k(total),
                "Orçado": brl_k(orc),
                "% Ating. (N4/Orç.)": f"{(n4/orc*100) if orc>0 else 0:.1f}%"
            })
        st.dataframe(pd.DataFrame(relatorio), use_container_width=True, hide_index=True)

    with tab_excel:
        for i in range(1,13):
            if f"M{i}" not in df_p.columns: df_p[f"M{i}"] = 0.0
            else: df_p[f"M{i}"] = pd.to_numeric(df_p[f"M{i}"], errors="coerce").fillna(0.0)
        excel_p = gerar_excel_sco(df_p)
        st.download_button("📥 Download Excel", data=excel_p,
            file_name=f"Base_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel", type="primary")


# ── LOG ────────────────────────────────────────────────────────────────────────
def pagina_log():
    st.markdown('<h2 style="color:#0f172a;">Log de Alterações</h2>',unsafe_allow_html=True)
    df_log = db.ler_logs()
    if df_log.empty: st.info("Nenhuma alteração registrada."); return
    cl1,cl2,cl3 = st.columns(3)
    with cl1: f_tipo = st.selectbox("Tipo",["Todos"]+sorted(df_log["tipo_acao"].dropna().unique().tolist()),key="lt")
    with cl2: f_user = st.selectbox("Usuário",["Todos"]+sorted(df_log["usuario"].dropna().unique().tolist()),key="lu")
    with cl3: txt_log = st.text_input("🔍 Buscar",key="lb")
    df_lf = df_log.copy()
    if f_tipo!="Todos": df_lf = df_lf[df_lf["tipo_acao"]==f_tipo]
    if f_user!="Todos": df_lf = df_lf[df_lf["usuario"]==f_user]
    if txt_log.strip(): df_lf = df_lf[df_lf["descricao"].astype(str).str.contains(txt_log,case=False,na=False)]
    cols = [c for c in ["data_hora","usuario","tipo_acao","descricao","id_oportunidade"] if c in df_lf.columns]
    df_ld = df_lf[cols].rename(columns={"data_hora":"Data/Hora","usuario":"Usuário","tipo_acao":"Tipo","descricao":"Descrição","id_oportunidade":"ID Oport."})
    st.markdown(f"**{len(df_ld)} registro(s)**")
    st.dataframe(df_ld,use_container_width=True,hide_index=True)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf,engine="xlsxwriter") as w: df_ld.to_excel(w,index=False,sheet_name="Log")
    st.download_button("📥 Exportar Log",data=buf.getvalue(),
        file_name=f"Log_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",mime="application/vnd.ms-excel")

# ── PAINEL DE ACESSOS ─────────────────────────────────────────────────────────
def pagina_admin():
    u = st.session_state.usuario
    st.markdown('<h2 style="color:#0f172a;">⚙️ Painel de Acessos</h2>',unsafe_allow_html=True)
    tab_novo,tab_edit,tab_import,tab_hist = st.tabs([
        "➕ Novo Usuário","✏️ Editar Usuários","📤 Importar Oportunidades","📅 Importar Histórico"
    ])

    with tab_novo:
        with st.container(border=True):
            c1,c2 = st.columns(2)
            with c1:
                login  = st.text_input("Login",key="nl")
                email  = st.text_input("E-mail",key="ne")
                nome   = st.text_input("Nome Completo",key="nn")
                perfil = st.selectbox("Perfil",["craque","lider","adm","diretoria"],key="np")
            with c2:
                senha      = st.text_input("Senha *",type="password",key="ns")
                frente     = st.selectbox("Frente",[""] + db.ler_frentes(),key="nfr")
                filial     = st.selectbox("Filial",[""] + db.ler_filiais(),key="nfi")
                area_craque = st.text_input("Área Craque (para perfil craque)",key="nac",
                    help="Identifica a área de responsabilidade do craque. Ex: Controladoria, TI, Logística CD")
            if st.button("Cadastrar Usuário",use_container_width=True,type="primary"):
                if login.strip() and nome.strip() and senha.strip():
                    db.cadastrar_usuario_manual(login,nome,perfil,email,filial,"",frente,senha,area_craque)
                    db.registrar_log(u,"CADASTRO USUÁRIO",f"Novo: {login}")
                    st.success(f"Usuário '{login}' criado!")
                else: st.error("Preencha Login, Nome e Senha.")

    with tab_edit:
        df_us = db.ler_usuarios()
        if not df_us.empty:
            alvo = st.selectbox("Selecione o Usuário",[""] + df_us["login"].tolist())
            if alvo:
                d = df_us[df_us["login"]==alvo].iloc[0]
                with st.form("form_ed"):
                    c1,c2 = st.columns(2)
                    en = c1.text_input("Nome",value=d.get("nome",""))
                    ee = c1.text_input("E-mail",value=d.get("email",""))
                    lp = ["craque","lider","adm","diretoria"]
                    ep = c1.selectbox("Perfil",lp,index=lp.index(d.get("perfil","craque")) if d.get("perfil","craque") in lp else 0)
                    eac = c1.text_input("Área Craque",value=d.get("area_craque",""))
                    lf = [""]+db.ler_frentes()
                    ef = c2.selectbox("Frente",lf,index=lf.index(d.get("frente","")) if d.get("frente","") in lf else 0)
                    lfil = [""]+db.ler_filiais()
                    efil = c2.selectbox("Filial",lfil,index=lfil.index(d.get("filial","")) if d.get("filial","") in lfil else 0)
                    es = c2.text_input("Nova Senha (em branco = manter)",type="password")
                    if st.form_submit_button("Salvar",type="primary"):
                        db.atualizar_usuario_completo(alvo,en,ee,ep,ef,efil,es,u,eac)
                        st.success("Atualizado!"); time.sleep(1); st.rerun()
                st.markdown("<br>",unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown("#### ⚠️ Zona de Perigo")
                    if st.button(f"🗑️ Excluir '{alvo}' definitivamente"):
                        db.excluir_usuario(alvo,u); st.success("Excluído!"); time.sleep(1.5); st.rerun()
        else: st.info("Nenhum usuário cadastrado.")

    with tab_import:
        st.markdown("**Passo 1:** Baixe a planilha padrão, preencha e reimporte.")
        padrao = db.gerar_planilha_padrao()
        st.download_button("📥 Baixar Planilha Padrão",data=padrao,
            file_name="Modelo_Importacao_Essencia.xlsx",mime="application/vnd.ms-excel")
        st.markdown("**Passo 2:** Importe o arquivo preenchido.")
        arquivo = st.file_uploader("Selecione o arquivo (.xlsx)",type=["xlsx"])
        if arquivo and st.button("🚀 Processar e Importar",type="primary"):
            try:
                df_imp = pd.read_excel(arquivo)
                count = db.importar_base_excel(df_imp,u)
                st.success(f"{count} oportunidade(s) importada(s) com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")

    with tab_hist:
        st.markdown("#### Importar Histórico de Snapshots Semanais")
        st.markdown("Use esta aba para carregar posições de semanas anteriores ao sistema. Será feito 1 ou 2 vezes.")
        st.markdown("**Passo 1:** Baixe o modelo, preencha com os dados históricos e reimporte.")
        hist_padrao = db.gerar_planilha_historico_padrao()
        st.download_button("📥 Baixar Modelo de Histórico", data=hist_padrao,
            file_name="Modelo_Historico_Snapshots.xlsx", mime="application/vnd.ms-excel")
        st.markdown("**Passo 2:** Importe o arquivo preenchido.")
        arq_hist = st.file_uploader("Selecione o histórico (.xlsx)", type=["xlsx"], key="up_hist")
        if arq_hist and st.button("🚀 Importar Histórico", type="primary", key="btn_hist"):
            try:
                df_h = pd.read_excel(arq_hist)
                count_h = db.importar_historico_snapshots(df_h, u)
                st.success(f"{count_h} semana(s) importada(s) com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")

        # lista snapshots existentes
        snaps = db.ler_snapshots()
        if snaps:
            st.markdown("---")
            st.markdown(f"**{len(snaps)} snapshot(s) registrado(s):**")
            df_snaps = pd.DataFrame([{"Semana": s["semana"], "Data": s["data"], "Registrado por": s.get("registrado_por","")} for s in snaps])
            st.dataframe(df_snaps, use_container_width=True, hide_index=True)

def main():
    if not st.session_state.usuario: tela_login()
    else: painel_principal()

if __name__=="__main__": main()
