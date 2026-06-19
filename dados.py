import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    if "firebase" in st.secrets:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db_fire = firestore.client()
NIVEIS = ["N1 - Ideia", "N2 - Planejamento", "N3 - Execução", "N4 - Implementado", "N0 - Cancelada"]

# ── INICIALIZAÇÃO ──────────────────────────────────────────────────────────────
def inicializar_banco_se_vazio():
    doc = db_fire.collection("usuarios").document("controladoria").get()
    if not doc.exists:
        cadastrar_usuario_manual("controladoria","Controladoria","adm","controladoria@frigelar.com.br","","","Financeiro","essencia2026")
        cadastrar_usuario_manual("diretoria","Diretoria Executiva","diretoria","diretoria@frigelar.com.br","","","","essencia2026")

inicializar_banco_se_vazio()

# ── LOG ────────────────────────────────────────────────────────────────────────
def registrar_log(usuario, tipo_acao, descricao, id_oportunidade=""):
    db_fire.collection("logs").add({
        "usuario": usuario.get("nome","?"),
        "login": usuario.get("login","?"),
        "tipo_acao": tipo_acao,
        "descricao": descricao,
        "id_oportunidade": id_oportunidade,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

def ler_logs() -> pd.DataFrame:
    docs = db_fire.collection("logs").order_by("data_hora", direction=firestore.Query.DESCENDING).limit(500).stream()
    lista = [doc.to_dict() for doc in docs]
    if not lista: return pd.DataFrame()
    return pd.DataFrame(lista)

# ── PLANO DE CONTAS ────────────────────────────────────────────────────────────
def ler_plano_contas() -> pd.DataFrame:
    plano = [
        {"Código":"3.1.5.06.002","ContaCont":"Agua","ContaOrc":"Água","Frente":"Consumo"},
        {"Código":"3.1.9.05.002","ContaCont":"Agua","ContaOrc":"Água","Frente":"Consumo"},
        {"Código":"3.1.9.05.003","ContaCont":"Alugueis","ContaOrc":"Alugueis","Frente":"Consumo"},
        {"Código":"3.1.9.05.004","ContaCont":"(-) Pis/Cofins Sobre Alugueis","ContaOrc":"Alugueis","Frente":"Consumo"},
        {"Código":"3.1.9.05.094","ContaCont":"Despesas Com Condominios","ContaOrc":"Alugueis","Frente":"Consumo"},
        {"Código":"3.1.9.05.105","ContaCont":"Multa Em Decorrencia Por Rescisão De Contrato","ContaOrc":"Alugueis","Frente":"Consumo"},
        {"Código":"3.1.9.05.114","ContaCont":"Carta Fianca","ContaOrc":"Alugueis","Frente":"Consumo"},
        {"Código":"3.1.5.06.045","ContaCont":"Taxas E Emolumentos","ContaOrc":"Cartório","Frente":"Financeiro"},
        {"Código":"3.1.8.06.013","ContaCont":"Cartorios","ContaOrc":"Cartório","Frente":"Financeiro"},
        {"Código":"3.1.8.06.052","ContaCont":"Taxas E Emolumentos","ContaOrc":"Cartório","Frente":"Financeiro"},
        {"Código":"3.1.9.05.012","ContaCont":"Cartorios","ContaOrc":"Cartório","Frente":"Financeiro"},
        {"Código":"3.1.9.05.061","ContaCont":"Taxas E Emolumentos","ContaOrc":"Cartório","Frente":"Financeiro"},
        {"Código":"3.1.8.06.003","ContaCont":"Provisão Comissão Impulsiona","ContaOrc":"Comissão Impulsiona","Frente":"Financeiro"},
        {"Código":"3.1.8.06.004","ContaCont":"Comissão Impulsiona","ContaOrc":"Comissão Impulsiona","Frente":"Financeiro"},
        {"Código":"3.1.8.06.089","ContaCont":"Provisao Comissao Impulsiona - Exclusao","ContaOrc":"Comissão Impulsiona","Frente":"Financeiro"},
        {"Código":"3.1.5.06.054","ContaCont":"Servicos Prestados Por Terceiros Pj","ContaOrc":"Comissão Instaladores","Frente":"Indústria"},
        {"Código":"3.1.8.06.056","ContaCont":"Servicos Prestados Por Terceiros","ContaOrc":"Comissão Instaladores","Frente":"Indústria"},
        {"Código":"3.1.8.06.079","ContaCont":"Servicos Prestados Por Terceiros Pf","ContaOrc":"Comissão Instaladores","Frente":"Indústria"},
        {"Código":"3.1.8.06.080","ContaCont":"Comissões De Terceiros Pf Sobre Vendas","ContaOrc":"Comissão Instaladores","Frente":"Indústria"},
        {"Código":"3.1.8.06.081","ContaCont":"Comissões De Terceiros Pj Sobre Vendas","ContaOrc":"Comissão Instaladores","Frente":"Indústria"},
        {"Código":"3.1.8.01.002","ContaCont":"Comissoes Vendedores","ContaOrc":"Comissões - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.9.05.008","ContaCont":"Assessoria Juridica - Tributario","ContaOrc":"Consultoria Contábil","Frente":"Financeiro"},
        {"Código":"3.1.9.05.017","ContaCont":"Despesas Com Auditoria","ContaOrc":"Consultoria Contábil","Frente":"Financeiro"},
        {"Código":"3.1.9.05.020","ContaCont":"Consultoria Em Contabilidade","ContaOrc":"Consultoria Contábil","Frente":"Financeiro"},
        {"Código":"3.1.9.05.091","ContaCont":"Assessoria Juridica - Societario","ContaOrc":"Consultoria Contábil","Frente":"Financeiro"},
        {"Código":"3.1.9.05.108","ContaCont":"Consultoria Juridica","ContaOrc":"Consultoria Contábil","Frente":"Financeiro"},
        {"Código":"3.1.9.05.047","ContaCont":"Consultorias Ambientais","ContaOrc":"Consultorias Ambientais","Frente":"Financeiro"},
        {"Código":"3.1.5.06.049","ContaCont":"Consultoria Assistencia Medica","ContaOrc":"Consultorias De Rh","Frente":"Produtividade"},
        {"Código":"3.1.8.06.020","ContaCont":"Consultoria Assistencia Medica","ContaOrc":"Consultorias De Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.018","ContaCont":"Consultoria Assistencia Medica","ContaOrc":"Consultorias De Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.071","ContaCont":"Consultoria Em Recursos Humanos","ContaOrc":"Consultorias De Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.019","ContaCont":"Consultoria De Sistemas","ContaOrc":"Consultorias De Ti","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.104","ContaCont":"Serviços De Cloud","ContaOrc":"Consultorias De Ti","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.021","ContaCont":"Consultoria Em Gestao","ContaOrc":"Consultorias Em Cobrança","Frente":"Financeiro"},
        {"Código":"3.1.9.05.085","ContaCont":"Consultoria Em Cobrança","ContaOrc":"Consultorias Em Cobrança","Frente":"Financeiro"},
        {"Código":"3.1.5.06.007","ContaCont":"Bens De Natureza Permanente","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.011","ContaCont":"Copias E Fotocopias","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.020","ContaCont":"Material De Limpeza E Cozinha","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.028","ContaCont":"Material De Uso E Consumo","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.029","ContaCont":"Materias De Seguranca","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.036","ContaCont":"Residuos Nao Reciclaveis","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.037","ContaCont":"Segurança Do Trabalho","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.047","ContaCont":"Uniformes E Equipamentos","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.8.06.011","ContaCont":"Bens De Natureza Permanente","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.8.06.019","ContaCont":"Copias E Fotocopias","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.8.06.028","ContaCont":"Material De Limpeza E Cozinha","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.8.06.038","ContaCont":"Material De Uso E Consumo","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.8.06.039","ContaCont":"Materiais De Seguranca","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.8.06.048","ContaCont":"Servicos De Instalacao","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.8.06.053","ContaCont":"Uniformes E Equipamentos","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.009","ContaCont":"Assinaturas Jornais, Revistas E Tv","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.010","ContaCont":"Bens De Natureza Permanente","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.023","ContaCont":"Copias E Fotocopias","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.050","ContaCont":"Material De Uso E Consumo","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.051","ContaCont":"Material De Limpeza E Cozinha","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.052","ContaCont":"Materias De Seguranca","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.056","ContaCont":"Seguranca Trabalho","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.062","ContaCont":"Uniformes E Equipamentos","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.106","ContaCont":"Despesas Com Epi´S","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.9.05.116","ContaCont":"Despesas Com Recepcoes E Homenagens","ContaOrc":"Consumo E Bens De Pequeno Valor","Frente":"Consumo"},
        {"Código":"3.1.5.06.032","ContaCont":"Postais/Malotes","ContaOrc":"Correios","Frente":"Consumo"},
        {"Código":"3.1.8.06.041","ContaCont":"Postais/Malotes","ContaOrc":"Correios","Frente":"Consumo"},
        {"Código":"3.1.9.05.054","ContaCont":"Postais/Malotes","ContaOrc":"Correios","Frente":"Consumo"},
        {"Código":"3.1.9.05.006","ContaCont":"Depreciação Direito De Uso Ifrs16","ContaOrc":"Depreciação Direito De Uso","Frente":"Consumo"},
        {"Código":"3.1.8.06.084","ContaCont":"Rede Autorizada - Importados","ContaOrc":"Desenvolvimento De Produtos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.085","ContaCont":"Peças Em Garantia - Importados","ContaOrc":"Desenvolvimento De Produtos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.086","ContaCont":"Mao De Obra Em Garantia - Importados","ContaOrc":"Desenvolvimento De Produtos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.087","ContaCont":"Servico Tecnico Regulamentado - Importados","ContaOrc":"Desenvolvimento De Produtos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.088","ContaCont":"Amostra/Protótipo De Produtos - Importados","ContaOrc":"Desenvolvimento De Produtos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.094","ContaCont":"Despesas Com Vendas/Amostras","ContaOrc":"Desenvolvimento De Produtos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.099","ContaCont":"Despesa Com Produtos Em Garantia Eos","ContaOrc":"Desenvolvimento De Produtos","Frente":"Financeiro"},
        {"Código":"3.1.5.06.058","ContaCont":"Industrializacao Por Encomenda","ContaOrc":"Despachante","Frente":"Financeiro"},
        {"Código":"3.1.8.06.050","ContaCont":"Servicos Prest.Despachantes Aduaneiros","ContaOrc":"Despachante","Frente":"Financeiro"},
        {"Código":"3.1.8.06.093","ContaCont":"Bonificacoes Sobre Vendas","ContaOrc":"Despesas Com Vendas Eos","Frente":"Financeiro"},
        {"Código":"3.1.8.07.004","ContaCont":"Despesa Campanha De Vendas Eos","ContaOrc":"Despesas Com Vendas Eos","Frente":"Financeiro"},
        {"Código":"3.1.8.07.009","ContaCont":"Propaganda, Publicidade E Anuncios – Importados","ContaOrc":"Despesas Com Vendas Eos","Frente":"Financeiro"},
        {"Código":"3.1.5.06.009","ContaCont":"Conducao","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.5.06.012","ContaCont":"Despesas Com Viagens","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.5.06.023","ContaCont":"Locacao De Veiculos","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.8.04.001","ContaCont":"Hospedagem","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.8.04.002","ContaCont":"Alimentação","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.8.04.006","ContaCont":"Locação De Veículo","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.8.04.007","ContaCont":"Transporte","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.8.06.017","ContaCont":"Conducao","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.8.06.033","ContaCont":"Locacao De Veiculos","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.9.05.015","ContaCont":"Conducao","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.9.05.034","ContaCont":"Locacao De Veiculos","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.9.05.063","ContaCont":"Hospedagem","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.9.05.069","ContaCont":"Despesas Com Viagens","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.9.05.078","ContaCont":"Viagens","ContaOrc":"Despesas Com Viagens","Frente":"Financeiro"},
        {"Código":"3.1.8.01.018","ContaCont":"Cursos E Treinamentos","ContaOrc":"Despesas De Rh - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.021","ContaCont":"Temporarios","ContaOrc":"Despesas De Rh - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.06.073","ContaCont":"Despesa Com Transferência De Funcionários","ContaOrc":"Despesas De Rh - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.06.092","ContaCont":"Despesa Gastos Com Funcionarios","ContaOrc":"Despesas De Rh - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.06.024","ContaCont":"Despesas Indedutiveis","ContaOrc":"Despesas Indedutiveis","Frente":"Financeiro"},
        {"Código":"3.1.9.05.025","ContaCont":"Despesas Indedutiveis","ContaOrc":"Despesas Indedutiveis","Frente":"Financeiro"},
        {"Código":"3.1.9.05.102","ContaCont":"Despesas Indedutiveis Cartão Corporativo","ContaOrc":"Despesas Indedutiveis","Frente":"Financeiro"},
        {"Código":"3.1.5.03.016","ContaCont":"Cursos E Treinamentos","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.02.017","ContaCont":"Cursos E Treinamentos","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.02.021","ContaCont":"Temporarios","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.041","ContaCont":"Serviço De Limpeza","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.064","ContaCont":"Patrocínio Cultural","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.070","ContaCont":"Contribuicao Sindical","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.075","ContaCont":"Ajuda De Custo Para Transferencia","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.083","ContaCont":"Entidades De Classe","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.090","ContaCont":"Assessoria Juridica - Trabalhista","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.092","ContaCont":"Despesa Com Transferência De Funcionários","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.9.05.093","ContaCont":"Despesa Gastos Com Funcionarios","ContaOrc":"Despesas Rh","Frente":"Produtividade"},
        {"Código":"3.1.8.06.062","ContaCont":"Despesa C/ Manutenção Loja Virtual","ContaOrc":"E-Commerce","Frente":"Digital"},
        {"Código":"3.1.8.06.072","ContaCont":"Despesa Com Vendas E-Commerce","ContaOrc":"E-Commerce","Frente":"Digital"},
        {"Código":"3.1.8.07.002","ContaCont":"Despesa Com Vendas E-Commerce","ContaOrc":"E-Commerce","Frente":"Digital"},
        {"Código":"3.1.9.03.001","ContaCont":"Contribuicao Fgts","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.03.002","ContaCont":"Contribuicao Inss","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.04.001","ContaCont":"Provisao P/13.Salario","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.04.002","ContaCont":"Provisao P/Ferias","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.04.003","ContaCont":"Provisao Fgts S/13.Salario","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.04.004","ContaCont":"Provisao Fgts S/Ferias","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.04.005","ContaCont":"Provisao Inss S/13.Salario","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.04.006","ContaCont":"Provisao Inss S/Ferias","ContaOrc":"Encargos Sociais - Adm","Frente":"Produtividade"},
        {"Código":"3.1.5.04.001","ContaCont":"Contribuicao Fgts","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.04.002","ContaCont":"Contribuicao Inss","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.05.001","ContaCont":"Provisao P/13.Salario","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.05.002","ContaCont":"Provisao P/Ferias","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.05.003","ContaCont":"Provisao Fgts S/13.Salario","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.05.004","ContaCont":"Provisao Fgts S/Ferias","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.05.005","ContaCont":"Provisao Inss S/13.Salario","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.05.006","ContaCont":"Provisao Inss S/Ferias","ContaOrc":"Encargos Sociais - Custo","Frente":"Produtividade"},
        {"Código":"3.1.8.02.001","ContaCont":"Contribuicao Inss","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.02.002","ContaCont":"Contribuicao Fgts","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.03.001","ContaCont":"Provisao P/13.Salario","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.03.002","ContaCont":"Provisao P/Ferias","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.03.003","ContaCont":"Provisao Fgts S/13.Salario","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.03.004","ContaCont":"Provisao Fgts S/Ferias","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.03.005","ContaCont":"Provisao Inss S/13.Salario","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.03.006","ContaCont":"Provisao Inss S/Ferias","ContaOrc":"Encargos Sociais - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.9.05.048","ContaCont":"Despesas Com Endomarketing","ContaOrc":"Endomarketing","Frente":"Produtividade"},
        {"Código":"3.1.9.05.082","ContaCont":"Despesas Natalinas","ContaOrc":"Endomarketing","Frente":"Produtividade"},
        {"Código":"3.1.5.06.013","ContaCont":"Energia Eletrica","ContaOrc":"Energia","Frente":"Consumo"},
        {"Código":"3.1.8.06.025","ContaCont":"Energia Eletrica","ContaOrc":"Energia","Frente":"Consumo"},
        {"Código":"3.1.9.05.026","ContaCont":"Energia Eletrica","ContaOrc":"Energia","Frente":"Consumo"},
        {"Código":"3.1.9.05.111","ContaCont":"Consultorias Expansão","ContaOrc":"Expansão","Frente":"Facilities"},
        {"Código":"3.1.8.06.023","ContaCont":"Despesas C/Provisão Para Credito De Liquid Duvidosa","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.067","ContaCont":"Desp. C/ Prov. Dev. Duvidosos - Societario","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.071","ContaCont":"Perdas Com Operações De Vendas/Clientes","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.075","ContaCont":"(-) Despesas C/Prov. P/Credito De Liquid Duvidosa - Exclusão","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.077","ContaCont":"(-) Despesas C/Prov. Dev. Duvidosos - Societario - Exclusão","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.078","ContaCont":"Perdas Com Operações De Vendas/Clientes - Web","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.096","ContaCont":"Desp C/Perdas Estimadas Cred Liq Duvidosa Mktplace - Adicao","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.098","ContaCont":"Despesas De Perdas Com Creditos Incobraveis Cartao Fgl","ContaOrc":"Financeiras/Pcld - Vendas","Frente":"Financeiro"},
        {"Código":"3.1.5.06.015","ContaCont":"Fretes E Carretos","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.5.06.016","ContaCont":"Fretes S/Devolucoes","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.5.06.017","ContaCont":"Fretes S/Garantias","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.05.001","ContaCont":"Fretes S/Vendas","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.05.002","ContaCont":"Fretes E Carretos","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.05.003","ContaCont":"Fretes S/Devolucoes","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.05.004","ContaCont":"Fretes S/Garantias","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.05.005","ContaCont":"Provisão Fretes A Pagar","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.05.007","ContaCont":"Proviso Fretes - Adicao","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.05.008","ContaCont":"(-) Provisao Fretes - Exclusao","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.8.06.063","ContaCont":"Despesas C/ Entregas De Clientes","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.9.05.028","ContaCont":"Fretes E Carretos","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.9.05.101","ContaCont":"Despesas C/ Entregas De Clientes","ContaOrc":"Frete","Frente":"Logística"},
        {"Código":"3.1.5.06.008","ContaCont":"Combustiveis E Lubrificantes","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.5.06.014","ContaCont":"Pedágio/Estacionamento","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.5.06.025","ContaCont":"Manutencao De Veiculos","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.8.04.003","ContaCont":"Combustível","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.8.04.004","ContaCont":"Pedágio/Estacionamento","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.8.04.005","ContaCont":"Manutenção/Lavagem","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.8.06.014","ContaCont":"Combustiveis E Lubrificantes","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.8.06.026","ContaCont":"Pedágio/Estacionamento","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.8.06.031","ContaCont":"Manutenção/Lavagem Veículos","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.8.06.035","ContaCont":"Manutencao De Veiculos","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.9.05.013","ContaCont":"Combustiveis E Lubrificantes","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.9.05.036","ContaCont":"Manutencao De Veiculos","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.9.05.039","ContaCont":"Manutenção/Lavagem Veículos","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.9.05.040","ContaCont":"Multas / Infrações Veiculos","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.9.05.053","ContaCont":"Pedágio/Estacionamento","ContaOrc":"Frota","Frente":"Financeiro"},
        {"Código":"3.1.5.06.052","ContaCont":"Despesa De Garantia Sem Retorno","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.8.06.055","ContaCont":"Despesa Garantia De Clientes","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.8.06.066","ContaCont":"Despesa Garantia De Fornecedor","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.8.06.068","ContaCont":"Despesa Garantia Sem Retorno - Com","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.8.06.069","ContaCont":"Despesa Icms St Garantia","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.9.05.081","ContaCont":"Despesas Com Perda Fornecedor","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.9.05.095","ContaCont":"Despesa Icms St Garantia","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.9.05.099","ContaCont":"Despesa Garantia De Fornecedor","ContaOrc":"Garantia","Frente":"Logística"},
        {"Código":"3.1.8.06.054","ContaCont":"Despesa Icms Protocolo 21/11","ContaOrc":"Impostos E Taxas","Frente":"Financeiro"},
        {"Código":"3.1.9.06.001","ContaCont":"Impostos E Taxas Federais","ContaOrc":"Impostos E Taxas","Frente":"Financeiro"},
        {"Código":"3.1.9.06.002","ContaCont":"Impostos E Taxas Estaduais","ContaOrc":"Impostos E Taxas","Frente":"Financeiro"},
        {"Código":"3.1.9.06.007","ContaCont":"Despesas Com Icms - St - Pagto. Indevido Ou A Maior","ContaOrc":"Impostos E Taxas","Frente":"Financeiro"},
        {"Código":"3.1.8.06.082","ContaCont":"Despesas Legais Lojas","ContaOrc":"Impostos E Taxas Fin","Frente":"Financeiro"},
        {"Código":"3.1.9.05.110","ContaCont":"Despesas Legais Lojas","ContaOrc":"Impostos E Taxas Fin","Frente":"Financeiro"},
        {"Código":"3.1.9.06.003","ContaCont":"Impostos E Taxas Municipais","ContaOrc":"Impostos E Taxas Fin","Frente":"Financeiro"},
        {"Código":"3.1.9.06.006","ContaCont":"Taxas Federais","ContaOrc":"Impostos E Taxas Fin","Frente":"Financeiro"},
        {"Código":"3.1.9.06.008","ContaCont":"Taxas Estaduais","ContaOrc":"Impostos E Taxas Fin","Frente":"Financeiro"},
        {"Código":"3.1.9.06.009","ContaCont":"Iptu","ContaOrc":"Impostos E Taxas Fin","Frente":"Financeiro"},
        {"Código":"3.1.8.06.009","ContaCont":"Assessoria Juridica","ContaOrc":"Jurídico","Frente":"Financeiro"},
        {"Código":"3.1.8.06.029","ContaCont":"Judiciais","ContaOrc":"Jurídico","Frente":"Financeiro"},
        {"Código":"3.1.9.05.031","ContaCont":"Judiciais","ContaOrc":"Jurídico","Frente":"Financeiro"},
        {"Código":"3.1.9.05.076","ContaCont":"Honorarios Profissionais Pf","ContaOrc":"Jurídico","Frente":"Financeiro"},
        {"Código":"3.1.9.05.089","ContaCont":"Assessoria Juridica - Civil","ContaOrc":"Jurídico","Frente":"Financeiro"},
        {"Código":"3.1.5.06.021","ContaCont":"Lanches E Refeicoes","ContaOrc":"Lanches E Refeições","Frente":"Produtividade"},
        {"Código":"3.1.5.06.057","ContaCont":"Despesa C/ Visitas A Clientes","ContaOrc":"Lanches E Refeições","Frente":"Produtividade"},
        {"Código":"3.1.8.06.030","ContaCont":"Lanches E Refeicoes","ContaOrc":"Lanches E Refeições","Frente":"Produtividade"},
        {"Código":"3.1.9.05.032","ContaCont":"Lanches E Refeicoes","ContaOrc":"Lanches E Refeições","Frente":"Produtividade"},
        {"Código":"3.1.9.05.029","ContaCont":"Licenças De Uso","ContaOrc":"Licenças Ti","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.109","ContaCont":"Aluguel De Licenças","ContaOrc":"Licenças Ti","Frente":"Tecnologia"},
        {"Código":"3.1.8.06.032","ContaCont":"Locacao De Maq E Equiptos","ContaOrc":"Locação Máq Equip.","Frente":"Logística"},
        {"Código":"3.1.9.05.033","ContaCont":"Locacao De Maq E Equiptos","ContaOrc":"Locação Máq Equip.","Frente":"Logística"},
        {"Código":"3.1.5.06.030","ContaCont":"Pallet","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.5.06.033","ContaCont":"Pre Operacionais-Industria","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.5.06.038","ContaCont":"Serviço De Armazenagem","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.5.06.039","ContaCont":"Servicos De Beneficiamento","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.8.06.015","ContaCont":"Combustíveis Empilhadeira","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.8.06.040","ContaCont":"Pallet","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.8.06.047","ContaCont":"Serviço De Armazenagem","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.9.05.046","ContaCont":"Manutenção Logistica","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.9.05.098","ContaCont":"Pallet","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.9.05.112","ContaCont":"Despesa Tratamento De Residuos","ContaOrc":"Logística","Frente":"Logística"},
        {"Código":"3.1.8.06.018","ContaCont":"Conservacao De Bens E Intalacoes","ContaOrc":"Manutenção - Adm","Frente":"Consumo"},
        {"Código":"3.1.8.06.034","ContaCont":"Manutencao De Maq.E Equipamentos","ContaOrc":"Manutenção - Adm","Frente":"Consumo"},
        {"Código":"3.1.8.06.036","ContaCont":"Manutencao E Conservacao","ContaOrc":"Manutenção - Adm","Frente":"Consumo"},
        {"Código":"3.1.9.05.016","ContaCont":"Conservacao De Bens E Instalacoes","ContaOrc":"Manutenção - Adm","Frente":"Consumo"},
        {"Código":"3.1.9.05.035","ContaCont":"Manutencao De Maq.E Equipamentos","ContaOrc":"Manutenção - Adm","Frente":"Consumo"},
        {"Código":"3.1.9.05.037","ContaCont":"Manutencao E Conservacao","ContaOrc":"Manutenção - Adm","Frente":"Consumo"},
        {"Código":"3.1.9.05.057","ContaCont":"Servicos De Instalacao","ContaOrc":"Manutenção - Adm","Frente":"Consumo"},
        {"Código":"3.1.9.05.065","ContaCont":"Doacoes Funcriança","ContaOrc":"Marketing - Adm","Frente":"Digital"},
        {"Código":"3.1.9.05.117","ContaCont":"Doacoes Fundo Do Idoso","ContaOrc":"Marketing - Adm","Frente":"Digital"},
        {"Código":"3.1.5.06.035","ContaCont":"Eventos/Convencoes Diversas","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.06.001","ContaCont":"Adesivos De Publicidade","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.06.002","ContaCont":"Despesas Com Feiras E Eventos Comerciais","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.06.008","ContaCont":"Anuncios E Publicacoes","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.06.012","ContaCont":"Brindes E Doacoes","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.06.044","ContaCont":"Propaganda, Publicidade E Anuncios","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.06.045","ContaCont":"Eventos/Convencoes Diversas","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.07.001","ContaCont":"Propaganda, Publicidade E Anuncios","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.07.018","ContaCont":"Campanha Copa 2026","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.9.05.007","ContaCont":"Anuncios E Publicacoes","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.9.05.011","ContaCont":"Brindes E Doacoes","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.9.05.027","ContaCont":"Eventos/Convencoes Diversas","ContaOrc":"Marketing - Vendas","Frente":"Digital"},
        {"Código":"3.1.8.06.074","ContaCont":"Despesa Com Marketplace","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.003","ContaCont":"Despesa Com Marketplace","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.005","ContaCont":"Despesa Com Marketplace Madeira","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.006","ContaCont":"Despesa Com Marketplace Tatyx","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.007","ContaCont":"Despesa Com Marketplace Leroy","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.008","ContaCont":"Despesa Com Marketplace Carrefour","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.010","ContaCont":"Despesa Com Marketplace Mercado Livre","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.011","ContaCont":"Despesa Com Marketplace Kabum","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.012","ContaCont":"Despesa Com Marketplace B2W","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.015","ContaCont":"Outras Despesas Com Marketplace","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.016","ContaCont":"Provisao Despesa Com Marketplace (Comissao) - Adicao","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.07.017","ContaCont":"(-) Provisao Despesa Com Marketplace (Comissao) - Exclusao","ContaOrc":"Marketplace","Frente":"Digital"},
        {"Código":"3.1.8.06.064","ContaCont":"Material De Embalagem","ContaOrc":"Material De Embalagem - Vendas","Frente":"Consumo"},
        {"Código":"3.1.5.06.050","ContaCont":"Provisao Para Perda De Estoques - Industrial","ContaOrc":"Obsoletos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.060","ContaCont":"Provisao Para Perda De Estoques - Comercial","ContaOrc":"Obsoletos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.076","ContaCont":"(-) Despesas C/Prov.P/Perda De Estoques Comercial - Exclusão","ContaOrc":"Obsoletos","Frente":"Financeiro"},
        {"Código":"3.1.9.05.080","ContaCont":"Provisao Para Perda De Estoques","ContaOrc":"Obsoletos","Frente":"Financeiro"},
        {"Código":"3.1.8.06.065","ContaCont":"Outras Consultorias","ContaOrc":"Outras Consultorias","Frente":"Financeiro"},
        {"Código":"3.1.9.05.077","ContaCont":"Honorarios Profissionais Pj","ContaOrc":"Outras Consultorias","Frente":"Financeiro"},
        {"Código":"3.1.9.05.084","ContaCont":"Outras Consultorias","ContaOrc":"Outras Consultorias","Frente":"Financeiro"},
        {"Código":"3.1.5.06.010","ContaCont":"Conservacao De Bens E Intalacoes","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.5.06.022","ContaCont":"Locacao De Maq E Equiptos","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.5.06.024","ContaCont":"Manutencao De Maq.E Equipamentos","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.5.06.026","ContaCont":"Manutencao E Conservacao","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.5.06.027","ContaCont":"Manutencao Seguranca","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.5.06.031","ContaCont":"Outras Consultorias E Assessorias","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.5.06.040","ContaCont":"Servicos De Instalacao","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.5.06.048","ContaCont":"Combustíveis Empilhadeira","ContaOrc":"Outras Indústria","Frente":"Indústria"},
        {"Código":"3.1.9.01.001","ContaCont":"Pro-Labore","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.001","ContaCont":"Salarios E Ordenados","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.003","ContaCont":"Horas Extras","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.004","ContaCont":"Gratificacoes","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.005","ContaCont":"Indenizacoes Trabalhistas","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.006","ContaCont":"Participação Nos Lucros E Resultados","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.007","ContaCont":"Assistencia Medica/Odontologica","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.008","ContaCont":"Auxilio Creche","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.009","ContaCont":"Aviso Previo E Indenizacoes","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.010","ContaCont":"Estagiarios","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.011","ContaCont":"Programa De Alimentacao Do Trabalhador","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.012","ContaCont":"Vale Transporte","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.013","ContaCont":"Seguro De Vida Em Grupo","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.014","ContaCont":"Admissionais/Demissionais","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.015","ContaCont":"Medicina Do Trabalho","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.016","ContaCont":"Reclamatória Trabalhista","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.018","ContaCont":"13 Salario","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.019","ContaCont":"Ferias","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.9.02.020","ContaCont":"Farmacia","ContaOrc":"Pessoal - Adm","Frente":"Produtividade"},
        {"Código":"3.1.5.03.001","ContaCont":"Salarios E Ordenados","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.002","ContaCont":"Horas Extras","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.003","ContaCont":"Gratificacoes","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.004","ContaCont":"Indenizacoes Trabalhistas","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.005","ContaCont":"Participação Nos Lucros E Resultados","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.006","ContaCont":"Assistencia Medica/Odontologica","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.008","ContaCont":"Aviso Previo E Indenizacoes","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.009","ContaCont":"Estagiarios","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.010","ContaCont":"Programa De Alimentacao Do Trabalhador","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.011","ContaCont":"Vale Transporte","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.013","ContaCont":"Admissionais/Demissionais","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.014","ContaCont":"Medicina Do Trabalho","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.015","ContaCont":"Reclamatória Trabalhista","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.019","ContaCont":"Ferias","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.03.021","ContaCont":"Temporarios","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.5.06.059","ContaCont":"Despesa Gastos Com Funcionarios","ContaOrc":"Pessoal - Custo","Frente":"Produtividade"},
        {"Código":"3.1.8.01.001","ContaCont":"Salarios E Ordenados","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.003","ContaCont":"Horas Extras","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.004","ContaCont":"Gratificacoes","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.006","ContaCont":"Indenizacoes Trabalhistas","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.007","ContaCont":"Participação Nos Lucros E Resultados","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.008","ContaCont":"Assistencia Medica/Odontologica","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.009","ContaCont":"Auxilio Creche","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.010","ContaCont":"Aviso Previo E Indenizacoes","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.011","ContaCont":"Estagiarios","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.012","ContaCont":"Programa De Alimentacao Do Trabalhador","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.013","ContaCont":"Vale Transporte","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.014","ContaCont":"Seguro De Vida Em Grupo","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.015","ContaCont":"Admissionais/Demissionais","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.016","ContaCont":"Medicina Do Trabalho","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.017","ContaCont":"Reclamatória Trabalhista","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.019","ContaCont":"13 Salario","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.8.01.020","ContaCont":"Ferias","ContaOrc":"Pessoal - Vendas","Frente":"Produtividade"},
        {"Código":"3.1.9.05.113","ContaCont":"Despesas Com Desenvolvimento E Implantação De Sistemas","ContaOrc":"Projetos","Frente":"Produtividade"},
        {"Código":"3.1.9.05.055","ContaCont":"Premios De Seguros","ContaOrc":"Seguros","Frente":"Financeiro"},
        {"Código":"3.1.9.05.118","ContaCont":"Servico De Atendimento Ao Consumidor","ContaOrc":"Serviço De Atendimento Ao Consumidor","Frente":"Digital"},
        {"Código":"3.1.8.06.049","ContaCont":"Instalação De Soluções","ContaOrc":"Serviços De Terceiros","Frente":"Produtividade"},
        {"Código":"3.1.9.05.042","ContaCont":"Servicos Prestados Por Terceiros Pf","ContaOrc":"Serviços De Terceiros","Frente":"Produtividade"},
        {"Código":"3.1.9.05.043","ContaCont":"Servicos Prestados Por Terceiros Pj","ContaOrc":"Serviços De Terceiros","Frente":"Produtividade"},
        {"Código":"3.1.9.05.115","ContaCont":"Transporte De Valores","ContaOrc":"Serviços De Terceiros","Frente":"Produtividade"},
        {"Código":"3.1.8.06.070","ContaCont":"Material De Informática","ContaOrc":"Serviços Terceiros Ti","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.058","ContaCont":"Servicos De Terceiros Adm","ContaOrc":"Serviços Terceiros Ti","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.088","ContaCont":"Material De Informática","ContaOrc":"Serviços Terceiros Ti","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.107","ContaCont":"Manutenção, Suporte Em Ti","ContaOrc":"Serviços Terceiros Ti","Frente":"Tecnologia"},
        {"Código":"3.1.5.06.043","ContaCont":"Servicos De Vigilancia","ContaOrc":"Serviços Vigilância","Frente":"Facilities"},
        {"Código":"3.1.8.06.037","ContaCont":"Manutencao Seguranca","ContaOrc":"Serviços Vigilância","Frente":"Facilities"},
        {"Código":"3.1.8.06.051","ContaCont":"Servicos De Vigilancia","ContaOrc":"Serviços Vigilância","Frente":"Facilities"},
        {"Código":"3.1.9.05.038","ContaCont":"Manutencao Seguranca","ContaOrc":"Serviços Vigilância","Frente":"Facilities"},
        {"Código":"3.1.9.05.060","ContaCont":"Serviço De Vigilância","ContaOrc":"Serviços Vigilância","Frente":"Facilities"},
        {"Código":"3.1.8.06.005","ContaCont":"Taxa Administradora Cartão","ContaOrc":"Tarifa Cartão","Frente":"Financeiro"},
        {"Código":"3.1.8.06.006","ContaCont":"Aluguel Maquina Cartao Credito","ContaOrc":"Tarifa Cartão","Frente":"Financeiro"},
        {"Código":"3.1.5.06.046","ContaCont":"Comunicação/Telefonia","ContaOrc":"Telefonia Adm","Frente":"Tecnologia"},
        {"Código":"3.1.8.06.016","ContaCont":"Comunicação/Telefonia","ContaOrc":"Telefonia Adm","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.014","ContaCont":"Comunicação/Telefonia","ContaOrc":"Telefonia Adm","Frente":"Tecnologia"},
        {"Código":"3.1.9.05.103","ContaCont":"Dados E Internet","ContaOrc":"Telefonia Adm","Frente":"Tecnologia"},
        {"Código":"3.1.8.06.022","ContaCont":"Despesa C/ Visitas A Clientes","ContaOrc":"Verba Comercial","Frente":"Financeiro"},
        {"Código":"3.1.8.06.083","ContaCont":"Despesas Com Vendas Lojas","ContaOrc":"Verba Comercial","Frente":"Financeiro"},
        {"Código":"3.2.1.01.012","ContaCont":"DESPESAS C/ TITULOS DE CLIENTES","ContaOrc":"Tarifa Boleto","Frente":"Financeiro"},
    ]
    return pd.DataFrame(plano)

# ── LISTAS AUXILIARES ──────────────────────────────────────────────────────────
def ler_centros_custo() -> list:
    return [
        "10.02 - Corp – Facilities","20.01 - TI - Backoffice","20.02 - TI - Sistemas",
        "20.03 - TI - Governança","20.04 - TI - Infra","20.05 - Seguranca","20.06 - TI - Digital",
        "20.08 - TI - Arquitetura","21.01 - Fin - Controladoria","21.02 - Fin - Contabilidade",
        "21.03 - Fin - Fiscal - Apuração","21.04 - Auditoria","21.05 - Fin - Fiscal - Sustentação",
        "21.06 - Fin - Backoffice","22.01 - Filiais - Admnistrativo","22.02 - Integra - Contas a Receber",
        "22.03 - Integra - Contas a Pagar","22.04 - Corp - Administrativo","22.05 - Fin - Tesouraria",
        "22.07 - Fin - Crédito","22.08 - Fin - Cobrança","23.01 - RH - Backoffice","23.03 - RH - DHO",
        "23.04 - RH - Recrutamento e Seleção","23.05 - RH - Consultoria Interna",
        "23.06 - RH - Depart. Pessoal","23.07 - RH - Remuneração","24.01 - Fin - Jurídico",
        "24.02 - Prevenção E Perdas","25.01 - Dept - Projetos","30.01 - Administrativo Vendas",
        "30.02 - Filiais - Equipe Vendas","30.03 - Filiais - Equipe Vendas II",
        "30.04 - Inteligência de Mercado","30.05 - Ecommerce","30.06 - Filiais - Logistica",
        "30.07 - Equipe Negócio - Câmara","30.08 - Equipe Negócio - VRF","30.09 - SAC Vendas",
        "30.10 - B2B","30.11 - Programa Impulsiona","30.12 - SAC","30.91 - Filiais - Gerentes",
        "30.92 - Filiais - Regionais","30.96 - Filiais - Despesas filiais","30.97 - Filiais - TI",
        "31.01 - Marketing","31.03 - E-Commerce Marketing","32.03 - Logística - Planejamento",
        "32.04 - Garantia Nacional","32.06 - Logistica - Pós Venda","32.07 - Logística - Backoffice",
        "33.02 - Compras Nacional - Backoffice","33.03 - EOS - Backoffice",
        "33.05 - Logística - Gestão de Frete","33.06 - Compras Nacional - Abastecimento",
        "33.07 - Div Eletro - Desenvol Produto","33.08 - Compras Nacional - Comercial",
        "33.09 - Compras Nacional - Doméstica","33.10 - Compras Nacional - Sell Out",
        "33.11 - EOS Peças - Vendas","33.12 - EOS Peças - Compras","33.13 - EOS Peças - Importação",
        "33.14 - Div Eletro - Marketing","33.15 - Div Eletro - Compras","33.16 - Div Eletro - Pós vendas",
        "33.17 - Compras Nacional - AC","34.01 - Filiais - Manutenção","34.02 - Integra - Compras Indiretas",
        "34.03 - Expansão","34.04 - Integra - Fiscal Escrituração","40.01 - Indústria - Administração",
        "40.03 - Indústria - Vendas Externas","40.05 - Indústria - Produção",
    ]

def ler_filiais() -> list:
    return [
        "1 - PORTO ALEGRE (RS)","2 - OSASCO (SP)","3 - CURITIBA (PR)","4 - SAO PAULO (SP)",
        "5 - OSASCO (SP)","6 - RECIFE (PE)","7 - RIBEIRAO PRETO (SP)","8 - RIO DE JANEIRO (RJ)",
        "9 - JOAO PESSOA (PB)","10 - PORTO ALEGRE (RS)","11 - EXTREMA (MG)","12 - PORTO ALEGRE (RS)",
        "13 - VITORIA (ES)","14 - CACHOEIRINHA (RS)","15 - CURITIBA (PR)","16 - CACHOEIRINHA (RS)",
        "17 - ITAITINGA (CE)","18 - SAO PAULO (SP)","19 - CAMPINAS (SP)",
        "20 - SAO JOSE DO RIO PRETO (SP)","21 - GOIANIA (GO)","22 - JOAO PESSOA (PB)",
        "23 - SAO PAULO (SP)","24 - FORTALEZA (CE)","25 - VILA VELHA (ES)","26 - JOAO PESSOA (PB)",
        "27 - VILA VELHA (ES)","28 - CACHOEIRINHA (RS)","29 - CURITIBA (PR)","30 - PORTO ALEGRE (RS)",
        "31 - BRASILIA (DF)","32 - BELO HORIZONTE (MG)","33 - SAO JOSE (SC)","34 - SAO PAULO (SP)",
        "35 - SALVADOR (BA)","36 - NATAL (RN)","37 - BELEM (PA)","38 - ANANINDEUA (PA)",
        "39 - MANAUS (AM)","40 - VILA VELHA (ES)","41 - RECIFE (PE)","42 - CAMPINAS (SP)",
        "43 - UBERLANDIA (MG)","44 - SAO JOSE DOS CAMPOS (SP)","45 - PIRACICABA (SP)",
        "46 - GUARULHOS (SP)","47 - MANAUS (AM)","48 - ITAJAI (SC)","49 - NAVEGANTES (SC)",
        "50 - OSASCO (SP)","51 - RIO DE JANEIRO (RJ)","52 - EXTREMA (MG)","53 - CUIABA (MT)",
        "54 - FLORIANOPOLIS (SC)","55 - CUIABA (MT)","56 - SANTOS (SP)","57 - TERESINA (PI)",
        "58 - SOROCABA (SP)","59 - SAO PAULO (SP)","60 - SAO BERNARDO DO CAMPO (SP)",
        "61 - RIO DE JANEIRO (RJ)","62 - SAO PAULO (SP)","63 - CAMPO GRANDE (MS)","64 - OSASCO (SP)",
        "65 - MACEIO (AL)","66 - SAO PAULO (SP)","67 - JOINVILLE (SC)","68 - LONDRINA (PR)",
        "69 - OSASCO (SP)","70 - GARUVA (SC)","71 - VILA VELHA (ES)","72 - CANOAS (RS)",
        "73 - SIMOES FILHO (BA)","74 - LAURO DE FREITAS (BA)","75 - TERESINA (PI)","76 - CAJAMAR (SP)",
        "77 - NOVO HAMBURGO (RS)","78 - ANANINDEUA (PA)","79 - PASSO FUNDO (RS)",
        "80 - FEIRA DE SANTANA (BA)","81 - APARECIDA DE GOIANIA (GO)","82 - BRASILIA (DF)",
        "83 - ANAPOLIS (GO)","84 - SAO JOSE DO RIO PRETO (SP)","85 - PORTO ALEGRE (RS)",
        "86 - FORTALEZA (CE)",
    ]

def ler_frentes() -> list:
    return ["Consumo","Digital","Facilities","Financeiro","Indústria","Logística","Produtividade","Tecnologia"]

# ── MESES ABSOLUTOS (jan/2026 a dez/2028) ─────────────────────────────────────
def gerar_colunas_meses_absolutos():
    meses = []
    nomes = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    for ano in [2026, 2027, 2028]:
        for m in nomes:
            meses.append(f"{m}/{ano}")
    return meses

def mapear_valores_para_meses_absolutos(data_n4_str, valores_mensais):
    """Recebe data N4 (dd/mm/aaaa) e lista de 12 valores, retorna dict {mes_abs: valor}"""
    resultado = {m: 0.0 for m in gerar_colunas_meses_absolutos()}
    if not data_n4_str or len(valores_mensais) != 12:
        return resultado
    try:
        partes = data_n4_str.strip().split("/")
        mes_inicio = int(partes[1])
        ano_inicio = int(partes[2])
        for i, val in enumerate(valores_mensais):
            mes_abs = mes_inicio + i
            ano_abs = ano_inicio + (mes_abs - 1) // 12
            mes_abs = ((mes_abs - 1) % 12) + 1
            nomes = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
            chave = f"{nomes[mes_abs-1]}/{ano_abs}"
            if chave in resultado:
                resultado[chave] = float(val)
    except:
        pass
    return resultado

# ── AUTENTICAÇÃO ───────────────────────────────────────────────────────────────
def autenticar(login, senha):
    doc = db_fire.collection("usuarios").document(login.lower()).get()
    if doc.exists:
        d = doc.to_dict()
        senha_banco = d.get("senha","")
        ativo = d.get("Ativo", d.get("ativo","Não"))
        if senha_banco == senha and ativo in ["Sim", True, "sim"]:
            d["login"] = doc.id
            if "nome" not in d: d["nome"] = d.get("Nome Completo","Usuário")
            if "perfil" not in d: d["perfil"] = d.get("Perfil","craque")
            if "frente" not in d: d["frente"] = d.get("Frente de Negócio","")
            return d
    return None

# ── OPORTUNIDADES ──────────────────────────────────────────────────────────────
def titulo_ja_existe(titulo, id_excluir=""):
    for doc in db_fire.collection("oportunidades").stream():
        if doc.id == id_excluir: continue
        if doc.to_dict().get("Título","").strip().lower() == titulo.strip().lower():
            return True
    return False

def ler_oportunidades() -> pd.DataFrame:
    docs = db_fire.collection("oportunidades").stream()
    lista = [{**doc.to_dict(), "ID": doc.id} for doc in docs]
    if not lista: return pd.DataFrame()
    df = pd.DataFrame(lista)
    if "Total Estimado 2026" not in df.columns: df["Total Estimado 2026"] = 0.0
    if "Submetido Controladoria" not in df.columns: df["Submetido Controladoria"] = False
    return df.fillna("")

def cadastrar_oportunidade(dados, usuario):
    hoje = datetime.now().strftime("%d/%m/%Y")
    nova = {
        "Nível": "N1 - Ideia",
        "Título": dados.get("titulo",""),
        "Descrição": dados.get("descricao",""),
        "Grupo Contábil": dados.get("grupo_contabil",""),
        "Comentário da Semana": "",
        "Conta Orçamento": dados.get("conta_orc",""),
        "Conta Contábil": dados.get("conta_cont",""),
        "Dono da Oportunidade": dados.get("dono",""),
        "CC Dono": dados.get("cc_dono",""),
        "Craque": usuario.get("nome",""),
        "Filial": dados.get("filial", usuario.get("filial","")),
        "Frente de Negócio": dados.get("frente_automatica",""),
        "Data Cadastro (N1)": hoje,
        "Data Realizada N1": hoje,
        "Data Prevista N2": "", "Data Realizada N2": "",
        "Data Prevista N3": dados.get("data_prev_n3",""),
        "Data Realizada N3": "",
        "Data Prevista N4": dados.get("data_prev_n4",""),
        "Data Realizada N4": "",
        "Total Estimado 2026": float(dados.get("ganho_2026",0)),
        "Submetido Controladoria": False,
    }
    for i in range(1,13): nova[f"M{i}"] = 0.0
    doc_ref = db_fire.collection("oportunidades").add(nova)
    id_gerado = doc_ref[1].id
    registrar_log(usuario, "CADASTRO", f"Nova oportunidade: {nova['Título']}", id_gerado)
    return id_gerado

def movimentar_nivel(id_, novo_nivel, usuario, justificativa=""):
    doc = db_fire.collection("oportunidades").document(id_).get()
    nivel_anterior = doc.to_dict().get("Nível","?") if doc.exists else "?"
    hoje = datetime.now().strftime("%d/%m/%Y")
    update = {"Nível": novo_nivel}
    if "N3" in novo_nivel: update["Data Realizada N3"] = hoje
    if "N4" in novo_nivel: update["Data Realizada N4"] = hoje
    if "N2" in novo_nivel: update["Data Realizada N2"] = hoje
    if justificativa: update["Justificativa Cancelamento"] = justificativa
    db_fire.collection("oportunidades").document(id_).update(update)
    desc = f"{nivel_anterior} → {novo_nivel}"
    if justificativa: desc += f" | Justificativa: {justificativa}"
    registrar_log(usuario, "MUDANÇA DE NÍVEL", desc, id_)

def submeter_para_controladoria(id_, usuario):
    db_fire.collection("oportunidades").document(id_).update({"Submetido Controladoria": True})
    registrar_log(usuario, "SUBMETIDO CONTROLADORIA", "Enviado para validação N4", id_)

def adicionar_comentario(id_, texto, usuario):
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    autor = usuario.get("nome","?")
    doc_ref = db_fire.collection("oportunidades").document(id_)
    atual = doc_ref.get().to_dict().get("Comentário da Semana","")
    novo = (atual + f"\n[{hoje} - {autor}] {texto}").strip()
    doc_ref.update({"Comentário da Semana": novo})
    registrar_log(usuario, "COMENTÁRIO", f"{texto[:60]}", id_)

def editar_campos_oportunidade(id_, campos, usuario):
    # Se tem Data Prevista N4 e valores mensais, mapeia para meses absolutos
    data_n4 = campos.get("Data Prevista N4","")
    valores_m = [campos.get(f"M{i}",0) for i in range(1,13)]
    if data_n4 and any(v != 0 for v in valores_m):
        meses_abs = mapear_valores_para_meses_absolutos(data_n4, valores_m)
        campos.update(meses_abs)
    # Recalcula total
    total = sum(float(campos.get(f"M{i}",0) or 0) for i in range(1,13))
    if total > 0: campos["Total Estimado 2026"] = total
    db_fire.collection("oportunidades").document(id_).update(campos)
    registrar_log(usuario, "EDIÇÃO DE CAMPOS", f"Campos: {', '.join(list(campos.keys())[:5])}", id_)

# ── USUÁRIOS ───────────────────────────────────────────────────────────────────
def cadastrar_usuario_manual(login, nome, perfil, email, filial, area, frente, senha):
    db_fire.collection("usuarios").document(login.lower()).set({
        "login": login, "nome": nome, "Nome Completo": nome,
        "perfil": perfil, "Perfil": perfil, "email": email,
        "filial": filial, "Filial": filial, "area": area,
        "frente": frente, "Frente de Negócio": frente,
        "senha": senha, "Ativo": "Sim"
    })

def ler_usuarios():
    lista = []
    for doc in db_fire.collection("usuarios").stream():
        d = doc.to_dict(); d["login"] = doc.id
        if "nome" not in d: d["nome"] = d.get("Nome Completo","")
        if "perfil" not in d: d["perfil"] = d.get("Perfil","")
        lista.append(d)
    if not lista: return pd.DataFrame()
    return pd.DataFrame(lista)

def atualizar_usuario_completo(login, nome, email, perfil, frente, filial, nova_senha, usuario_logado=None):
    upd = {"nome":nome,"Nome Completo":nome,"email":email,"perfil":perfil,"Perfil":perfil,
           "frente":frente,"Frente de Negócio":frente,"filial":filial,"Filial":filial}
    if nova_senha.strip(): upd["senha"] = nova_senha.strip()
    db_fire.collection("usuarios").document(login).update(upd)
    if usuario_logado: registrar_log(usuario_logado,"EDIÇÃO USUÁRIO",f"Editado: {login}")

def excluir_usuario(login, usuario_logado=None):
    db_fire.collection("usuarios").document(login).delete()
    if usuario_logado: registrar_log(usuario_logado,"EXCLUSÃO USUÁRIO",f"Excluído: {login}")

# ── ORÇAMENTO ──────────────────────────────────────────────────────────────────
def ler_orcamento():
    try:
        doc = db_fire.collection("config").document("orcamento").get()
        if doc.exists: return doc.to_dict()
    except: pass
    return {f: 0.0 for f in ler_frentes()}

def salvar_orcamento(dados):
    db_fire.collection("config").document("orcamento").set(dados)

# ── IMPORTAÇÃO EXCEL ───────────────────────────────────────────────────────────
def gerar_planilha_padrao() -> bytes:
    colunas = [
        "Título","Descrição","Grupo Contábil (ADM/COM/IND)",
        "Conta Orçamento","Desc. Conta Contábil","Dono da Oportunidade",
        "Centro de Custo do Dono da Oportunidade","Filial","Status",
        "Total Estimado 2026","Data Prevista N3","Data Prevista N4",
        "M1","M2","M3","M4","M5","M6","M7","M8","M9","M10","M11","M12"
    ]
    df_padrao = pd.DataFrame(columns=colunas)
    buf = __import__("io").BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
        df_padrao.to_excel(w, index=False, sheet_name="Importação")
        ws = w.sheets["Importação"]
        fmt = w.book.add_format({"bold":True,"bg_color":"#0f172a","font_color":"#ffffff"})
        for i, col in enumerate(colunas):
            ws.write(0, i, col, fmt)
            ws.set_column(i, i, max(len(col)+4, 18))
    return buf.getvalue()

def importar_base_excel(df, u):
    import uuid
    df = df.dropna(how="all").fillna("")
    count = 0
    for _, row in df.iterrows():
        titulo = str(row.get("Título","")).strip()
        if not titulo or titulo.lower() == "nan": continue
        id_unico = str(uuid.uuid4()).split("-")[0][:6].upper()
        try: total = float(str(row.get("Total Estimado 2026","0")))
        except: total = 0.0
        nova = {
            "ID": id_unico, "Título": titulo,
            "Descrição": str(row.get("Descrição", titulo)).strip(),
            "Grupo Contábil": str(row.get("Grupo Contábil (ADM/COM/IND)","")).strip(),
            "Dono da Oportunidade": str(row.get("Dono da Oportunidade","")).strip(),
            "CC Dono": str(row.get("Centro de Custo do Dono da Oportunidade","")).strip(),
            "Conta Orçamento": str(row.get("Conta Orçamento","")).strip(),
            "Conta Contábil": str(row.get("Desc. Conta Contábil","")).strip(),
            "Filial": str(row.get("Filial","")).strip(),
            "Nível": str(row.get("Status","N1 - Ideia")).strip(),
            "Craque": u.get("nome","Importação"),
            "Total Estimado 2026": total,
            "Data Prevista N3": str(row.get("Data Prevista N3","")).strip(),
            "Data Prevista N4": str(row.get("Data Prevista N4","")).strip(),
            "Data Cadastro (N1)": datetime.now().strftime("%d/%m/%Y"),
            "Data Realizada N1": datetime.now().strftime("%d/%m/%Y"),
            "Data Realizada N2":"","Data Realizada N3":"","Data Realizada N4":"",
            "Submetido Controladoria": False,
            "Comentário da Semana": "",
        }
        for i in range(1,13):
            try: nova[f"M{i}"] = float(str(row.get(f"M{i}","0")))
            except: nova[f"M{i}"] = 0.0
        # mapeia meses absolutos
        if nova["Data Prevista N4"]:
            vals = [nova[f"M{i}"] for i in range(1,13)]
            meses_abs = mapear_valores_para_meses_absolutos(nova["Data Prevista N4"], vals)
            nova.update(meses_abs)
        db_fire.collection("oportunidades").document(id_unico).set(nova)
        count += 1
    registrar_log(u,"IMPORTAÇÃO EXCEL",f"{count} oportunidades importadas")
    return count

# NÃO MEXER NO CÓDIGO QUE ESTÁ DANDO CERTO
