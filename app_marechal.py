import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DE ENGENHARIA ---
st.set_page_config(page_title="SIM - Sistema de Informação Municipal", layout="wide", initial_sidebar_state="expanded")

# --- DATABASE ENGINE RELACIONAL (BLINDADO) ---
class SIM_Engine:
    def __init__(self):
        self.conn = sqlite3.connect('sim_salitre_v9.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Tabelas Master de Auditoria
        queries = [
            '''CREATE TABLE IF NOT EXISTS fornecedores (id INTEGER PRIMARY KEY, razao_social TEXT, nome_fantasia TEXT, cnpj_cpf TEXT UNIQUE, insc_estadual TEXT, logradouro TEXT, bairro TEXT, cidade TEXT, uf TEXT, email TEXT, fone TEXT)''',
            '''CREATE TABLE IF NOT EXISTS motoristas (id INTEGER PRIMARY KEY, nome TEXT, cpf TEXT UNIQUE, cnh TEXT, cat TEXT, validade TEXT, vinculo TEXT, secretaria TEXT)''',
            '''CREATE TABLE IF NOT EXISTS frota (id INTEGER PRIMARY KEY, patrimonio TEXT UNIQUE, placa TEXT UNIQUE, renavam TEXT, chassi TEXT, descricao TEXT, marca TEXT, modelo TEXT, ano_fab TEXT, ano_mod TEXT, comb TEXT, cap_tanque REAL, secretaria TEXT, status TEXT)''',
            '''CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY, cod_peca TEXT, descricao TEXT, unidade TEXT, grupo TEXT, estoque_atual REAL, preco_custo REAL)''',
            '''CREATE TABLE IF NOT EXISTS abastecimentos (id INTEGER PRIMARY KEY, data TEXT, veiculo_id TEXT, motorista_id TEXT, km_ant REAL, km_atu REAL, litros REAL, preco REAL, total REAL, cupom TEXT, posto TEXT)'''
        ]
        for q in queries: self.cursor.execute(q)
        self.conn.commit()

db = SIM_Engine()

# --- INTERFACE "ENTERPRISE" (CSS CUSTOMIZADO) ---
st.markdown("""
    <style>
    /* Reset de Design */
    .stApp { background-color: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Industrial */
    [data-testid="stSidebar"] { background-color: #0f172a !important; color: white !important; }
    .sidebar-header { padding: 20px; text-align: center; border-bottom: 1px solid #1e293b; }
    
    /* Cabeçalhos e Cards */
    .header-panel { background: #ffffff; padding: 1.5rem; border-radius: 8px; border-left: 10px solid #10b981; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; }
    .metric-box { background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; }
    
    /* Formulários de Alta Densidade */
    .stTextInput>div>div>input, .stSelectbox>div>div>select { background-color: #f8fafc !important; border-radius: 4px !important; }
    .stButton>button { background-color: #2563eb !important; color: white !important; border-radius: 4px; padding: 10px 20px; font-weight: 600; width: 100%; }
    
    /* Tabelas */
    .dataframe { font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO HIERÁRQUICA ---
if 'menu' not in st.session_state: st.session_state.menu = "Home"

with st.sidebar:
    st.markdown("<div class='sidebar-header'><h2>🏛️ SIM SALITRE</h2><small>SISTEMA MUNICIPAL INTEGRADO</small></div>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("📦 **MÓDULO PATRIMÔNIO**")
    if st.button("🏢 Cadastro de Fornecedores"): st.session_state.menu = "Forn"
    if st.button("🚚 Gestão da Frota Ativa"): st.session_state.menu = "Frota"
    if st.button("👤 Registro de Condutores"): st.session_state.menu = "Moto"
    
    st.divider()
    st.markdown("⛽ **MÓDULO LOGÍSTICA**")
    if st.button("⛽ Lançar Abastecimento"): st.session_state.menu = "Abast"
    if st.button("🛠️ Ordens de Serviço (OS)"): st.session_state.menu = "OS"
    if st.button("📦 Estoque de Peças"): st.session_state.menu = "Estoque"
    
    st.divider()
    st.markdown("📊 **CONTROLADORIA**")
    if st.button("📋 Auditoria de Consumo"): st.session_state.menu = "Audit"
    if st.button("🚪 Logout"): st.session_state.menu = "Home"

# --- RENDERIZAÇÃO DE MÓDULOS ---

def view_frota():
    st.markdown("<div class='header-panel'><h2>🚚 Gestão da Frota Municipal</h2><p>Identificação de Ativos e Unidades Gestoras</p></div>", unsafe_allow_html=True)
    with st.form("form_frota"):
        c1, c2, c3, c4 = st.columns(4)
        pat = c1.text_input("Nº Patrimônio (TCE)")
        placa = c2.text_input("Placa *")
        ren = c3.text_input("RENAVAM")
        cha = c4.text_input("CHASSI")
        
        c5, c6, c7, c8 = st.columns([2,1,1,1])
        desc = c5.text_input("Descrição (Ex: Caminhão Pipa Volvo VM 270)")
        marca = c6.text_input("Marca")
        modelo = c7.text_input("Modelo")
        cor = c8.text_input("Cor")
        
        c9, c10, c11, c12 = st.columns(4)
        afab = c9.text_input("Ano Fab.")
        amod = c10.text_input("Ano Mod.")
        comb = c11.selectbox("Combustível", ["Diesel S10", "Diesel S500", "Gasolina Comum", "Etanol", "Flex"])
        cap = c12.number_input("Capacidade Tanque (L)")
        
        c13, c14 = st.columns(2)
        sec = c13.selectbox("Secretaria Detentora", ["Saúde", "Educação", "Infraestrutura", "Gabinete", "Finanças"])
        status = c14.selectbox("Situação Atual", ["Ativo/Operacional", "Manutenção Preventiva", "Manutenção Corretiva", "Aguardando Leilão"])
        
        if st.form_submit_button("💾 SALVAR CADASTRO NO PATRIMÔNIO"):
            db.cursor.execute("INSERT INTO frota (patrimonio, placa, renavam, chassi, descricao, marca, modelo, ano_fab, ano_mod, comb, cap_tanque, secretaria, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             (pat, placa, ren, cha, desc, marca, modelo, afab, amod, comb, cap, sec, status))
            db.conn.commit()
            st.success("Ativo registrado com sucesso.")

def view_abastecimento():
    st.markdown("<div class='header-panel'><h2>⛽ Movimentação de Combustíveis</h2><p>Lançamento Auditável de Consumo</p></div>", unsafe_allow_html=True)
    
    # Carregamento de Dados Relacionais
    placas = [p[0] for p in db.cursor.execute("SELECT placa FROM frota").fetchall()]
    motos = [m[0] for m in db.cursor.execute("SELECT nome FROM motoristas").fetchall()]
    
    with st.form("form_abast"):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data da Operação")
        veic = c2.selectbox("Veículo (Placa)", placas if placas else ["Cadastre um veículo"])
        moto = c3.selectbox("Condutor", motos if motos else ["Cadastre um motorista"])
        
        c4, c5, c6 = st.columns(3)
        km_ant = c4.number_input("Odômetro Anterior (Leitura)", value=0.0)
        km_atu = c5.number_input("Odômetro Atual (Hodômetro) *", value=0.0)
        litros = c6.number_input("Litros Abastecidos *", step=0.01)
        
        c7, c8, c9 = st.columns(3)
        preco = c7.number_input("Valor Unitário (R$)", step=0.001)
        cupom = c8.text_input("Nº Nota Fiscal / Cupom")
        posto = c9.text_input("Fornecedor / Posto")
        
        if st.form_submit_button("🚀 PROCESSAR LANÇAMENTO"):
            total = litros * preco
            db.cursor.execute("INSERT INTO abastecimentos (data, veiculo_id, motorista_id, km_ant, km_atu, litros, preco, total, cupom, posto) VALUES (?,?,?,?,?,?,?,?,?,?)",
                             (str(data), veic, moto, km_ant, km_atu, litros, preco, total, cupom, posto))
            db.conn.commit()
            st.success(f"Abastecimento Gravado. Custo Total: R$ {total:.2f}")

# --- DASHBOARD CENTRAL ---
if st.session_state.menu == "Home":
    st.markdown("<div class='header-panel'><h2>📊 Painel de Controle de Gestão Municipal</h2><p>SIM - Salitre-CE | Auditoria e Transparência</p></div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("<div class='metric-box'><small>FROTA TOTAL</small><h3>45</h3></div>", unsafe_allow_html=True)
    c2.markdown("<div class='metric-box'><small>MOTORISTAS</small><h3>22</h3></div>", unsafe_allow_html=True)
    c3.markdown("<div class='metric-box'><small>CONSUMO MÊS</small><h3>R$ 48.520</h3></div>", unsafe_allow_html=True)
    c4.markdown("<div class='metric-box'><small>ALERTAS SAG</small><h3 style='color:red;'>3</h3></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("🏁 Monitoramento em Tempo Real")
    df_abast = pd.read_sql("SELECT data, veiculo_id, km_atu, litros, total, cupom FROM abastecimentos ORDER BY id DESC LIMIT 5", db.conn)
    st.table(df_abast)

elif st.session_state.menu == "Frota": view_frota()
elif st.session_state.menu == "Abast": view_abastecimento()
elif st.session_state.menu == "Forn":
    st.markdown("<div class='header-panel'><h2>🏢 Cadastro de Credenciados</h2></div>", unsafe_allow_html=True)
    with st.form("f_forn"):
        c1, c2 = st.columns([3,1])
        razao = c1.text_input("Razão Social *")
        cnpj = c2.text_input("CNPJ / CPF *")
        c3, c4 = st.columns(2)
        end = c3.text_input("Logradouro")
        contato = c4.text_input("Email / Telefone")
        if st.form_submit_button("REGISTRAR FORNECEDOR"):
            db.cursor.execute("INSERT INTO fornecedores (razao_social, cnpj_cpf, logradouro, email) VALUES (?,?,?,?)", (razao, cnpj, end, contato))
            db.conn.commit()
            st.success("Fornecedor Habilitado.")
