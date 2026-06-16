import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st # 🟢 Precisamos importar o Streamlit aqui também

if not firebase_admin._apps:
    # Cofre 'secrets'
    if "firebase" in st.secrets:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("firebase-key.json")
        
    firebase_admin.initialize_app(cred)

db_fire = firestore.client()
# ──────────────────────────────────────────────────────────────────────────

NIVEIS = ["N1 - Ideia", "N2 - Planejamento", "N3 - Execução", "N4 - Implementado", "N0 - Cancelada"]

def cadastrar_usuario_com_email(login, nome, perfil, email, filial="", area="", frente=""):
    login_id = login.strip().lower()
    db_fire.collection("usuarios").document(login_id).set({
        "Nome Completo": nome, "Perfil": perfil, "Ativo": "Sim",
        "Filial": filial, "Área": area, "Frente de Negócio": frente,
        "Data Cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
    })
    
    corpo_email = f"""
    <h1>Bem-vindo ao Programa Essência</h1>
    <p>Olá, <b>{nome}</b>!</p>
    <p>Seu acesso foi liberado pelo nosso Administrador.</p>
    <p><b>Login:</b> {login_id}<br><b>Perfil:</b> {perfil.upper()}</p>
    <p>Acesse o sistema agora mesmo!</p>
    """
    db_fire.collection("mail").add({
        "to": email, "message": {"subject": "Boas-vindas ao Programa Essência", "html": corpo_email}
    })

def inicializar_banco_se_vazio():
    doc = db_fire.collection("usuarios").document("controladoria").get()
    if not doc.exists:
        cadastrar_usuario_com_email("controladoria", "Controladoria", "adm", "controladoria@frigelar.com.br")
        cadastrar_usuario_com_email("diretoria", "Diretoria Executiva", "diretoria", "diretoria@frigelar.com.br")

inicializar_banco_se_vazio()

# ── PLANO DE CONTAS COM FRENTE DE NEGÓCIO ATRELADA ────────────────────────
def ler_plano_contas() -> pd.DataFrame:
    plano = [
        {"ContaOrc": "Energia Elétrica", "ContaCont": "Energia Elétrica CD", "Código": "3.1.2.001", "Frente": "Operações"},
        {"ContaOrc": "Energia Elétrica", "ContaCont": "Energia Elétrica Admin", "Código": "3.1.2.002", "Frente": "Corporativo"},
        {"ContaOrc": "Fretes e Logística", "ContaCont": "Frete Saída", "Código": "3.1.3.001", "Frente": "Supply"},
        {"ContaOrc": "Fretes e Logística", "ContaCont": "Frete Retorno", "Código": "3.1.3.002", "Frente": "Supply"},
        {"ContaOrc": "Matéria Prima", "ContaCont": "Insumo Nacional", "Código": "3.2.2.001", "Frente": "Operações"},
        {"ContaOrc": "TI e Sistemas", "ContaCont": "Licenças de Software", "Código": "4.1.3.001", "Frente": "Corporativo"},
        {"ContaOrc": "Serviços Terceiros", "ContaCont": "Consultoria Financeira", "Código": "4.1.4.001", "Frente": "Financeiro"}
    ]
    return pd.DataFrame(plano)

def ler_areas() -> list:
    return ["Garantia", "SAC", "Logística CD", "Transportes", "TI", "RH", "Controladoria", "Compras", "Lojas"]

# ── AUTENTICAÇÃO E OPERAÇÕES CORE ─────────────────────────────────────────
def autenticar(email_ou_login: str):
    login_limpo = email_ou_login.split("@")[0].strip().lower()
    doc_ref = db_fire.collection("usuarios").document(login_limpo).get()
    if doc_ref.exists:
        u = doc_ref.to_dict()
        if u.get("Ativo") == "Sim":
            return {"login": login_limpo, "nome": u.get("Nome Completo"), "perfil": u.get("Perfil"), "filial": u.get("Filial", ""), "area": u.get("Área", ""), "frente": u.get("Frente de Negócio", "")}
    return None

def ler_oportunidades() -> pd.DataFrame:
    docs = db_fire.collection("oportunidades").stream()
    lista = [{**doc.to_dict(), "ID": doc.id} for doc in docs]
    if not lista: return pd.DataFrame()
    df = pd.DataFrame(lista)
    
    # TRAVA DE SEGURANÇA: Garante que as novas colunas existam mesmo em cadastros antigos
    if "Total Estimado 2026" not in df.columns: 
        df["Total Estimado 2026"] = 0.0
    if "Submetido Controladoria" not in df.columns: 
        df["Submetido Controladoria"] = False
        
    return df.fillna("")

def cadastrar_oportunidade(dados: dict, usuario: dict) -> str:
    hoje = datetime.now().strftime("%d/%m/%Y")
    nova = {
        "Nível": "N1 - Ideia", 
        "Título": dados.get("titulo",""), # 🟢 LINHA ADICIONADA AQUI
        "Descrição": dados.get("descricao",""), 
        "Comentário da Semana": "",
        "Conta Orçamento": dados.get("conta_orc",""), 
        "Conta Contábil": dados.get("conta_cont",""), 
        "Dono da Oportunidade": dados.get("dono",""), 
        "CC Dono": dados.get("cc_dono",""), 
        "Craque": usuario.get("nome",""), 
        "Filial": usuario.get("filial",""), 
        "Área": dados.get("area_ideia",""), 
        "Frente de Negócio": dados.get("frente_automatica",""), 
        "Data Cadastro (N1)": hoje, 
        "Total Estimado 2026": float(dados.get("ganho_2026", 0)),
        "Submetido Controladoria": False
    }
    doc_ref = db_fire.collection("oportunidades").add(nova)
    return doc_ref[1].id[:6]

def movimentar_nivel(id_, novo_nivel, usuario):
    db_fire.collection("oportunidades").document(id_).update({"Nível": novo_nivel})

def submeter_para_controladoria(id_):
    db_fire.collection("oportunidades").document(id_).update({"Submetido Controladoria": True})

def adicionar_comentario(id_, texto, usuario):
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    autor = usuario.get("nome","?")
    doc_ref = db_fire.collection("oportunidades").document(id_)
    comentario_atual = doc_ref.get().to_dict().get("Comentário da Semana", "")
    texto_final = (comentario_atual + f"\n[{hoje} - {autor}] {texto}").strip()
    doc_ref.update({"Comentário da Semana": texto_final})

def atualizar_oportunidade(id_, campos, usuario):
    db_fire.collection("oportunidades").document(id_).update(campos)

# ── GESTÃO MANUAL DE USUÁRIOS ──────────────────────────────

def cadastrar_usuario_manual(login, nome, perfil, email, filial, area, frente, senha):
    novo_usuario = {
        "login": login,
        "nome": nome,
        "Nome Completo": nome, # Duplicado por segurança para retrocompatibilidade
        "perfil": perfil,
        "Perfil": perfil,
        "email": email,
        "filial": filial,
        "Filial": filial,
        "area": area,
        "frente": frente,
        "Frente de Negócio": frente,
        "senha": senha, 
        "Ativo": "Sim"
    }
    db_fire.collection("usuarios").document(login.lower()).set(novo_usuario)

def ler_usuarios():
    docs = db_fire.collection("usuarios").stream()
    lista = []
    for doc in docs:
        d = doc.to_dict()
        d["login"] = doc.id
        # Padroniza chaves para a tabela do ADM
        if "nome" not in d: d["nome"] = d.get("Nome Completo", "")
        if "perfil" not in d: d["perfil"] = d.get("Perfil", "")
        lista.append(d)
        
    if not lista: 
        import pandas as pd
        return pd.DataFrame()
    
    import pandas as pd
    return pd.DataFrame(lista)

def atualizar_senha_usuario(login, nova_senha):
    db_fire.collection("usuarios").document(login).update({"senha": nova_senha})

# ── ATUALIZAÇÃO DA FUNÇÃO AUTENTICAR ──────────────────────────────────────────
def autenticar(login, senha):
    doc = db_fire.collection("usuarios").document(login.lower()).get()
    
    if doc.exists:
        dados_usuario = doc.to_dict()
        senha_banco = dados_usuario.get("senha", "")
        ativo_banco = dados_usuario.get("Ativo", dados_usuario.get("ativo", "Não"))
        
        if senha_banco == senha and ativo_banco in ["Sim", True, "sim"]:
            # Padroniza a sessão do usuário
            dados_usuario["login"] = doc.id
            if "nome" not in dados_usuario: dados_usuario["nome"] = dados_usuario.get("Nome Completo", "Usuário")
            if "perfil" not in dados_usuario: dados_usuario["perfil"] = dados_usuario.get("Perfil", "craque")
            if "frente" not in dados_usuario: dados_usuario["frente"] = dados_usuario.get("Frente de Negócio", "")
            return dados_usuario
            
    return None

# ── EDIÇÃO DE USUÁRIO ──────────────────────────────────────────
def atualizar_usuario_completo(login, nome, email, perfil, frente, filial, nova_senha):
    atualizacao = {
        "nome": nome, "Nome Completo": nome,
        "email": email,
        "perfil": perfil, "Perfil": perfil,
        "frente": frente, "Frente de Negócio": frente,
        "filial": filial, "Filial": filial
    }
    if nova_senha.strip(): 
        atualizacao["senha"] = nova_senha.strip()
        
    db_fire.collection("usuarios").document(login).update(atualizacao)

# ── IMPORTAÇÃO DE EXCEL ────────────────────────────────────────
def importar_base_excel(df, u):
    from datetime import datetime
    import uuid  
    
    # 🟢 HIGIENIZADOR 1: Apaga linhas que são apenas formatação fantasma
    df = df.dropna(how='all')
    df = df.fillna("")
    
    for index, row in df.iterrows():
        titulo = str(row.get("Descrição da Oportunidade", "")).strip()
        
        # 🟢 HIGIENIZADOR 2: Se o título estiver vazio, ignora e pula para a próxima linha!
        if not titulo or titulo.lower() == "nan":
            continue
            
        frente = str(row.get("Grupo Contábil", "")).strip()
        conta_orc = str(row.get("Conta Orçamento", "")).strip()
        conta_cont = str(row.get("Desc. Conta Contábil", "")).strip()
        dono = str(row.get("Dono da Oportunidade", "")).strip()
        cc_dono = str(row.get("Centro de Custo do Dono da Oportunidade", "")).strip()
        filial = str(row.get("Filial", "")).strip()
        nivel = str(row.get("Status", "N1 - Ideia")).strip()
        
        total_str = str(row.get("Total", "0"))
        try: total = float(total_str) if total_str != "" else 0.0
        except: total = 0.0
        
        id_unico = str(uuid.uuid4()).split("-")[0][:6].upper()
        
        nova_ideia = {
            "ID": id_unico, 
            "Título": titulo, "Descrição": titulo, 
            "Dono da Oportunidade": dono, "CC Dono": cc_dono,
            "Conta Orçamento": conta_orc, "Conta Contábil": conta_cont,
            "Frente de Negócio": frente, "Filial": filial, "Nível": nivel,
            "Craque": u.get("nome", "Importação Automática"), 
            "Total Estimado 2026": total,
            "Data Cadastro (N1)": datetime.now().strftime("%d/%m/%Y"),
            "Ativo": True
        }
        db_fire.collection("oportunidades").document(id_unico).set(nova_ideia)

# ── FUNÇÕES DO ORÇAMENTO EDITÁVEL (RELATÓRIO GERENCIAL) ───────────────────────
def ler_orcamento():
    """Lê as metas orçadas do banco. Se não existir, traz os padrões."""
    try:
        doc = db_fire.collection("config").document("orcamento").get()
        if doc.exists: return doc.to_dict()
    except: pass
    return {"Operações": 1500000.0, "Supply": 800000.0, "Financeiro": 500000.0, "Corporativo": 300000.0}

def salvar_orcamento(dados):
    """Salva os novos orçamentos definidos pelo ADM no banco."""
    db_fire.collection("config").document("orcamento").set(dados)

        # ── NOVA FUNÇÃO DE EXCLUSÃO DE USUÁRIO ──────────────────────────────────────────
def excluir_usuario(login):
    """Apaga o documento do usuário definitivamente do banco de dados."""
    db_fire.collection("usuarios").document(login).delete()

# NÃO MEXER NO CÓDIGO QUE ESTÁ DANDO CERTO
