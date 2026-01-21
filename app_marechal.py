import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

# --- CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(page_title="SIM - Salitre/CE", layout="wide", initial_sidebar_state="expanded")

# --- ENGINE DE DADOS RELACIONAL (AUDITÁVEL) ---
class SIM_Audit_Engine:
    def __init__(self):
        self.conn = sqlite3.connect('sim_salitre_v10.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # 1. CONTRATOS DE LOCAÇÃO (O que faltava)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, numero_contrato TEXT UNIQUE, empresa_id INTEGER,
            processo_licitatorio TEXT, objeto TEXT, data_inicio TEXT, data_fim TEXT,
            valor_mensal REAL, limite_km_mes REAL, valor_km_excedente REAL)''')

        # 2. VEÍCULOS (Com vínculo de contrato)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS frota (
            id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT UNIQUE, patrimonio TEXT, 
            tipo_vinculo TEXT, contrato_id INTEGER, descricao TEXT, marca TEXT, modelo TEXT, 
            renavam TEXT, chassi TEXT, ano_fab TEXT, ano_mod TEXT, comb TEXT, cap_tanque REAL, 
            secretaria TEXT, status TEXT, data_venc_seguro TEXT, data_venc_ipva TEXT)''')

        # 3. FORNECEDORES E EMPRESAS DE LOCAÇÃO
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome_razao TEXT, cnpj_cpf TEXT UNIQUE, 
            tipo_servico TEXT, logradouro TEXT, cidade TEXT, uf TEXT, fone TEXT, email TEXT)''')

        # 4. MOVIMENTAÇÕES (ABASTECIMENTO E MANUTENÇÃO)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, veiculo_id TEXT, motorista_id TEXT, 
            km_ant REAL, km_atu REAL, litros REAL, total REAL, cupom TEXT, posto TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS motoristas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, cnh TEXT, 
            cat TEXT, validade TEXT, vinculo TEXT, secretaria TEXT)''')

        self.conn.commit()

db = SIM_Audit_Engine()

# --- CSS: INTERFACE DE ALTA DENSIDADE (TIPO SAP) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e293b; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    .header-box { background: #ffffff; padding: 20px; border-radius: 4px; border-top: 4px solid #3b82f6; box-shadow: 0 1px 2px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .label-custom { font-weight: bold; color: #475569; font-size: 0.9rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f5f9; border-radius: 4px 4px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO PRINCIPAL ---
with st.sidebar:
    st.markdown("<h2 style='color:white; text-align:center;'>🏛️ SIM SALITRE</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("MÓDULOS DO SISTEMA", 
                   ["📊 Dashboard de Controle", "📝 Gestão de Contratos", "🚗 Frota & Ativos", 
                    "👤 Gestão de Pessoal", "⛽ Movimentação/Logística", "📑 Auditoria TCE"])

# --- MÓDULO 1: GESTÃO DE CONTRATOS (A SOLUÇÃO QUE FALTAVA) ---
if menu == "📝 Gestão de Contratos":
    st.markdown("<div class='header-box'><h2>📑 Gestão de Contratos de Locação e Prestação</h2></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Cadastrar Contrato", "Contratos Ativos"])
    
    with tab1:
        with st.form("form_contrato"):
            c1, c2, c3 = st.columns(3)
            num_con = c1.text_input("Número do Contrato/Pregão *")
            proc = c2.text_input("Processo Licitatório")
            
            # Busca fornecedores que prestam serviço de locação
            forn_list = db.cursor.execute("SELECT id, nome_razao FROM fornecedores").fetchall()
            forn_sel = c3.selectbox("Empresa Contratada", [f"{f[0]} - {f[1]}" for f in forn_list] if forn_list else ["Cadastre a Empresa primeiro"])
            
            objeto = st.text_area("Objeto do Contrato (Descrição detalhada)")
            
            c4, c5, c6 = st.columns(3)
            d_ini = c4.date_input("Início da Vigência")
            d_fim = c5.date_input("Fim da Vigência")
            valor = c6.number_input("Valor Mensal do Contrato (R$)", min_value=0.0)
            
            c7, c8 = st.columns(2)
            limite_km = c7.number_input("Franquia de KM Mensal", min_value=0.0)
            valor_exced = c8.number_input("Valor KM Excedente", min_value=0.0)
            
            if st.form_submit_button("REGISTRAR CONTRATO"):
                db.cursor.execute("INSERT INTO contratos (numero_contrato, empresa_id, processo_licitatorio, objeto, data_inicio, data_fim, valor_mensal, limite_km_mes, valor_km_excedente) VALUES (?,?,?,?,?,?,?,?,?)",
                                 (num_con, forn_sel.split(' - ')[0], proc, objeto, str(d_ini), str(d_fim), valor, limite_km, valor_exced))
                db.conn.commit()
                st.success("Contrato vinculado com sucesso!")

# --- MÓDULO 2: FROTA & ATIVOS (VINCULADO AO CONTRATO) ---
elif menu == "🚗 Frota & Ativos":
    st.markdown("<div class='header-box'><h2>🚗 Cadastro Técnico de Veículos</h2></div>", unsafe_allow_html=True)
    
    with st.form("form_frota"):
        c1, c2, c3 = st.columns([1,1,2])
        tipo_v = c1.selectbox("Tipo de Vínculo", ["Próprio", "Locado", "Cessão", "Doação"])
        placa = c2.text_input("Placa *")
        pat = c3.text_input("Nº Patrimônio (Se Próprio)")
        
        # Campo condicional: Se for locado, pede o contrato
        cont_list = db.cursor.execute("SELECT id, numero_contrato FROM contratos").fetchall()
        id_contrato = st.selectbox("Contrato de Locação (Se aplicável)", ["Nenhum"] + [f"{c[0]} - {c[1]}" for c in cont_list])
        
        c4, c5, c6, c7 = st.columns(4)
        ren = c4.text_input("RENAVAM")
        cha = c5.text_input("CHASSI")
        marca = c6.text_input("Marca")
        modelo = c7.text_input("Modelo")
        
        c8, c9, c10 = st.columns(3)
        sec = c8.selectbox("Secretaria", ["Saúde", "Educação", "Infraestrutura", "Gabinete"])
        v_seg = c9.date_input("Vencimento Seguro")
        v_ipva = c10.date_input("Vencimento IPVA/Licencimento")
        
        if st.form_submit_button("SALVAR ATIVO"):
            cid = id_contrato.split(' - ')[0] if id_contrato != "Nenhum" else None
            db.cursor.execute("INSERT INTO frota (placa, patrimonio, tipo_vinculo, contrato_id, renavam, chassi, marca, modelo, secretaria, data_venc_seguro, data_venc_ipva) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                             (placa, pat, tipo_v, cid, ren, cha, marca, modelo, sec, str(v_seg), str(v_ipva)))
            db.conn.commit()
            st.success("Veículo catalogado.")

# --- MÓDULO 3: ABASTECIMENTO (AUDITORIA DE KM) ---
elif menu == "⛽ Movimentação/Logística":
    st.markdown("<div class='header-box'><h2>⛽ Movimentação de Combustíveis e KM</h2></div>", unsafe_allow_html=True)
    
    placas = [p[0] for p in db.cursor.execute("SELECT placa FROM frota").fetchall()]
    motos = [m[0] for m in db.cursor.execute("SELECT nome FROM motoristas").fetchall()]
    
    with st.form("form_abast"):
        c1, c2, c3 = st.columns(3)
        v_sel = c1.selectbox("Veículo", placas)
        m_sel = c2.selectbox("Motorista", motos)
        data = c3.date_input("Data")
        
        c4, c5, c6 = st.columns(3)
        km_ant = c4.number_input("KM Anterior", help="Última leitura registrada")
        km_atu = c5.number_input("KM Atual (No ato)")
        litros = c6.number_input("Litros")
        
        c7, c8 = st.columns(2)
        cupom = c7.text_input("Cupom Fiscal")
        valor_t = c8.number_input("Valor Total (R$)")
        
        if st.form_submit_button("REGISTRAR"):
            if km_atu <= km_ant:
                st.error("Erro: KM atual não pode ser menor ou igual ao anterior.")
            else:
                db.cursor.execute("INSERT INTO abastecimentos (data, veiculo_id, motorista_id, km_ant, km_atu, litros, total, cupom) VALUES (?,?,?,?,?,?,?,?)",
                                 (str(data), v_sel, m_sel, km_ant, km_atu, litros, valor_t, cupom))
                db.conn.commit()
                st.success("Abastecimento processado.")

# --- DASHBOARD (RESULTADOS) ---
elif menu == "📊 Dashboard de Controle":
    st.markdown("<div class='header-box'><h2>📊 Dashboard de Gestão Integral</h2></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    f_total = db.cursor.execute("SELECT COUNT(*) FROM frota").fetchone()[0]
    locados = db.cursor.execute("SELECT COUNT(*) FROM frota WHERE tipo_vinculo = 'Locado'").fetchone()[0]
    gastos = db.cursor.execute("SELECT SUM(total) FROM abastecimentos").fetchone()[0] or 0
    
    c1.metric("Frota Total", f_total)
    c2.metric("Veículos Locados", locados)
    c3.metric("Gasto Total Comb.", f"R$ {gastos:,.2f}")
    
    st.divider()
    st.subheader("📋 Relatório de Auditoria de Contratos")
    df_contratos = pd.read_sql("""
        SELECT c.numero_contrato, f.nome_razao as empresa, c.valor_mensal, c.data_fim 
        FROM contratos c JOIN fornecedores f ON c.empresa_id = f.id
    """, db.conn)
    st.table(df_contratos)
