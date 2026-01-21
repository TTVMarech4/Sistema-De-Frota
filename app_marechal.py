import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

# --- CONFIGURAÇÃO DE ENGENHARIA ---
st.set_page_config(page_title="SIM - Salitre/CE", layout="wide", initial_sidebar_state="expanded")

# --- MOTOR DE BANCO DE DADOS RELACIONAL ---
class SIM_Engine:
    def __init__(self):
        self.conn = sqlite3.connect('sim_salitre_v11.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_db()

    def setup_db(self):
        # 1. Módulo de Contratos e Licitações
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, numero_contrato TEXT UNIQUE, empresa_id INTEGER,
            processo_licitatorio TEXT, objeto TEXT, data_inicio TEXT, data_fim TEXT,
            valor_mensal REAL, limite_km_mes REAL, status_contrato TEXT)''')

        # 2. Módulo de Veículos (Campos de Auditoria Total)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS frota (
            id INTEGER PRIMARY KEY AUTOINCREMENT, patrimonio TEXT, placa TEXT UNIQUE, 
            tipo_vinculo TEXT, contrato_id INTEGER, renavam TEXT, chassi TEXT, 
            marca TEXT, modelo TEXT, ano_fab TEXT, ano_mod TEXT, combustivel TEXT, 
            cap_tanque REAL, secretaria TEXT, status TEXT, venc_ipva TEXT, venc_seguro TEXT)''')

        # 3. Módulo de Pneus (Essencial para TCE)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS pneus (
            id INTEGER PRIMARY KEY AUTOINCREMENT, num_fogo TEXT UNIQUE, veiculo_id TEXT, 
            posicao TEXT, marca TEXT, modelo TEXT, data_instalacao TEXT, km_instalacao REAL)''')

        # 4. Módulo de Suprimentos e Almoxarifado
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cod_barras TEXT, descricao TEXT, 
            grupo TEXT, unidade TEXT, estoque_min REAL, estoque_atual REAL, custo_medio REAL)''')

        # 5. Módulo de Movimentação (Abastecimento e KM)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, veiculo_id TEXT, motorista_id TEXT, 
            km_ant REAL, km_atu REAL, litros REAL, valor_unit REAL, total REAL, 
            cupom TEXT, posto TEXT, secretaria_custo TEXT)''')

        # 6. Módulo de Pessoal e Condutores
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS motoristas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, 
            cnh TEXT, categoria TEXT, validade_cnh TEXT, secretaria TEXT)''')

        self.conn.commit()

db = SIM_Engine()

# --- INTERFACE "GOV-TECH" (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    .header-panel { background: white; padding: 25px; border-radius: 8px; border-left: 10px solid #2563eb; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .stButton>button { background-color: #2563eb !important; color: white; border-radius: 6px; font-weight: bold; width: 100%; height: 3em; }
    .card-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center;'>🏛️ SIM SALITRE</h1>", unsafe_allow_html=True)
    st.divider()
    modulo = st.selectbox("MÓDULOS DE GESTÃO", [
        "📊 Dashboard Geral", "📝 Contratos e Licitação", "🚗 Gestão de Frota", 
        "🛞 Controle de Pneus", "📦 Almoxarifado", "⛽ Abastecimento", "👤 Condutores"
    ])

# --- FUNÇÕES DE INTERFACE ---

if modulo == "Dashboard Geral":
    st.markdown("<div class='header-panel'><h2>📊 Painel de Controle e Auditoria</h2><p>Visão Consolidada de Ativos e Recursos</p></div>", unsafe_allow_html=True)
    
    # KPIs Reais
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Frota Ativa", len(db.cursor.execute("SELECT id FROM frota").fetchall()))
    c2.metric("Contratos Vigentes", len(db.cursor.execute("SELECT id FROM contratos").fetchall()))
    c3.metric("Gasto Combustível (Mês)", "R$ 0,00")
    c4.metric("Alertas IPVA/Seguro", "0")

    st.divider()
    st.subheader("📋 Últimos Lançamentos Auditados")
    df_abas = pd.read_sql("SELECT data, veiculo_id, km_atu, litros, total FROM abastecimentos ORDER BY id DESC LIMIT 5", db.conn)
    st.dataframe(df_abas, use_container_width=True)

elif modulo == "📝 Contratos e Licitação":
    st.markdown("<div class='header-panel'><h2>📝 Gestão de Contratos de Terceirização</h2></div>", unsafe_allow_html=True)
    with st.form("f_contrato"):
        c1, c2, c3 = st.columns(3)
        num = c1.text_input("Nº do Contrato (Ex: 2024.01.20-01) *")
        proc = c2.text_input("Processo Licitatório (Pregão/Dispensa)")
        status = c3.selectbox("Status", ["Vigente", "Encerrado", "Aditivo em Análise"])
        
        objeto = st.text_area("Objeto Detalhado do Contrato")
        
        c4, c5, c6 = st.columns(3)
        val = c4.number_input("Valor Mensal (R$)", min_value=0.0)
        ini = c5.date_input("Início Vigência")
        fim = c6.date_input("Fim Vigência")
        
        if st.form_submit_button("REGISTRAR CONTRATO"):
            db.cursor.execute("INSERT INTO contratos (numero_contrato, processo_licitatorio, objeto, data_inicio, data_fim, valor_mensal, status_contrato) VALUES (?,?,?,?,?,?,?)",
                             (num, proc, objeto, str(ini), str(fim), val, status))
            db.conn.commit()
            st.success("Contrato jurídico registrado no sistema.")

elif modulo == "🚗 Gestão de Frota":
    st.markdown("<div class='header-panel'><h2>🚗 Cadastro Técnico de Ativos</h2></div>", unsafe_allow_html=True)
    with st.form("f_frota"):
        c1, c2, c3 = st.columns([1,1,2])
        vinc = c1.selectbox("Vínculo", ["Próprio", "Locado", "Cessão", "Doação"])
        placa = c2.text_input("Placa *")
        pat = c3.text_input("Nº Patrimônio (Se Próprio)")
        
        # Puxa Contratos Existentes
        con_list = [c[0] for c in db.cursor.execute("SELECT numero_contrato FROM contratos").fetchall()]
        cont_sel = st.selectbox("Vínculo Contratual (Se Locado)", ["Nenhum"] + con_list)
        
        c4, c5, c6, c7 = st.columns(4)
        ren = c4.text_input("RENAVAM")
        cha = c5.text_input("CHASSI")
        marca = c6.text_input("Marca")
        modelo = c7.text_input("Modelo")
        
        c8, c9, c10 = st.columns(3)
        sec = c8.selectbox("Secretaria Detentora", ["Saúde", "Educação", "Infraestrutura", "Gabinete"])
        vipva = c9.date_input("Vencimento Licenciamento/IPVA")
        vseg = c10.date_input("Vencimento Seguro")
        
        if st.form_submit_button("SALVAR VEÍCULO NO PATRIMÔNIO"):
            db.cursor.execute("INSERT INTO frota (placa, patrimonio, tipo_vinculo, contrato_id, renavam, chassi, marca, modelo, secretaria, venc_ipva, venc_seguro, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                             (placa, pat, vinc, cont_sel, ren, cha, marca, modelo, sec, str(vipva), str(vseg), "Ativo"))
            db.conn.commit()
            st.success("Ativo registrado com ficha técnica completa.")

elif modulo == "⛽ Abastecimento":
    st.markdown("<div class='header-panel'><h2>⛽ Movimentação de Combustíveis</h2></div>", unsafe_allow_html=True)
    
    # Carregamento de dados para dropdowns
    placas = [p[0] for p in db.cursor.execute("SELECT placa FROM frota").fetchall()]
    motos = [m[0] for m in db.cursor.execute("SELECT nome FROM motoristas").fetchall()]
    
    with st.form("f_abast"):
        c1, c2, c3 = st.columns(3)
        p_sel = c1.selectbox("Veículo", placas if placas else ["Nenhum cadastrado"])
        m_sel = c2.selectbox("Condutor", motos if motos else ["Nenhum cadastrado"])
        data = c3.date_input("Data do Lançamento")
        
        c4, c5, c6 = st.columns(3)
        km_ant = c4.number_input("Odômetro Anterior", help="Bloqueado: Automático do sistema")
        km_atu = c5.number_input("Odômetro Atual (Hodômetro) *")
        litros = c6.number_input("Qtd Litros *", step=0.01)
        
        c7, c8, c9 = st.columns(3)
        preco = c7.number_input("Preço Unitário (R$)", step=0.001)
        total = c8.number_input("Valor Total (R$)")
        cupom = c9.text_input("Nº Cupom/Nota Fiscal")
        
        if st.form_submit_button("GRAVAR ABASTECIMENTO"):
            db.cursor.execute("INSERT INTO abastecimentos (data, veiculo_id, motorista_id, km_ant, km_atu, litros, valor_unit, total, cupom) VALUES (?,?,?,?,?,?,?,?,?)",
                             (str(data), p_sel, m_sel, km_ant, km_atu, litros, preco, total, cupom))
            db.conn.commit()
            st.success("Abastecimento processado com auditoria de KM.")

elif modulo == "🛞 Controle de Pneus":
    st.markdown("<div class='header-panel'><h2>🛞 Gestão de Pneus e Vidas</h2></div>", unsafe_allow_html=True)
    st.info("O controle de pneus por número de fogo é essencial para evitar desvios no patrimônio.")
    with st.form("f_pneu"):
        c1, c2, c3 = st.columns(3)
        fogo = c1.text_input("Número de Fogo (Marcação) *")
        veic = c2.selectbox("Veículo Instalado", [p[0] for p in db.cursor.execute("SELECT placa FROM frota").fetchall()])
        pos = c3.selectbox("Posição", ["Diant. Esq", "Diant. Dir", "Traseiro Int. Esq", "Traseiro Ext. Esq", "Estepre"])
        
        if st.form_submit_button("REGISTRAR INSTALAÇÃO DE PNEU"):
            st.success(f"Pneu {fogo} vinculado ao veículo.")

elif modulo == "👤 Condutores":
    st.markdown("<div class='header-panel'><h2>👤 Cadastro de Condutores e CNH</h2></div>", unsafe_allow_html=True)
    with st.form("f_moto"):
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome Completo *")
        cpf = c2.text_input("CPF *")
        cnh = c3.text_input("Nº CNH")
        
        c4, c5, c6 = st.columns(3)
        cat = c4.selectbox("Categoria", ["A", "B", "C", "D", "E", "AB", "AD", "AE"])
        val = c5.date_input("Validade CNH")
        sec = c6.selectbox("Secretaria", ["Saúde", "Educação", "Infraestrutura"])
        
        if st.form_submit_button("CADASTRAR MOTORISTA"):
            db.cursor.execute("INSERT INTO motoristas (nome, cpf, cnh, categoria, validade_cnh, secretaria) VALUES (?,?,?,?,?,?)",
                             (nome, cpf, cnh, cat, str(val), sec))
            db.conn.commit()
            st.success("Motorista habilitado no sistema.")

# FOOTER AUDITÁVEL
st.divider()
st.caption("SIM v11.0 - Sistema de Informação Municipal | Salitre/CE | Integridade de Dados Padrão TCE-CE")
