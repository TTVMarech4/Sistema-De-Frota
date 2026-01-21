import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="SIM - Salitre/CE", layout="wide", initial_sidebar_state="expanded")

# --- MOTOR DE DADOS (ARQUITETURA RELACIONAL) ---
class SIM_ERP:
    def __init__(self):
        self.conn = sqlite3.connect('sim_salitre_v8.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_db()

    def setup_db(self):
        # Tabelas de Apoio (Configurações)
        self.cursor.execute('CREATE TABLE IF NOT EXISTS unidade_gestora (id INTEGER PRIMARY KEY, nome TEXT, cnpj TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS fonte_recurso (id INTEGER PRIMARY KEY, cod TEXT, nome TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS unidades_medida (id INTEGER PRIMARY KEY, sigla TEXT, nome TEXT)')
        
        # Tabelas Principais (Cadastros)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, razao_social TEXT, nome_fantasia TEXT, 
            cnpj_cpf TEXT UNIQUE, insc_estadual TEXT, logradouro TEXT, numero TEXT, 
            bairro TEXT, cep TEXT, cidade TEXT, uf TEXT, telefone TEXT, email TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS motoristas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, rg TEXT, 
            cnh TEXT, cat TEXT, validade TEXT, matricula TEXT, secretaria TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, patrimonio TEXT UNIQUE, placa TEXT UNIQUE, 
            renavam TEXT, chassi TEXT, descricao TEXT, marca TEXT, modelo TEXT, cor TEXT, 
            ano_fab TEXT, ano_mod TEXT, combustivel TEXT, cap_tanque REAL, secretaria TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cod_barras TEXT, descricao TEXT, 
            grupo TEXT, subgrupo TEXT, unid_medida TEXT, estoque_atual REAL, custo_medio REAL)''')

        # Tabelas de Movimentação (Auditáveis)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, veiculo_id TEXT, motorista_id TEXT, 
            km_ant REAL, km_atu REAL, litros REAL, valor_unit REAL, total REAL, 
            cupom TEXT, posto TEXT, fonte_id TEXT)''')
        
        self.conn.commit()

erp = SIM_ERP()

# --- INTERFACE CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    [data-testid="stSidebar"] { background-color: #1e293b !important; }
    .main-header { 
        background-color: #ffffff; padding: 20px; border-bottom: 3px solid #10b981;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.2em; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if 'aba_atual' not in st.session_state: st.session_state.aba_atual = "Dashboard"

with st.sidebar:
    st.markdown("<h1 style='color:white; text-align:center;'>🏛️ SIM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; text-align:center;'>Sistema de Informação Municipal</p>", unsafe_allow_html=True)
    st.divider()
    
    with st.expander("📁 CADASTROS BASE", expanded=True):
        if st.button("🏢 Unidade Gestora"): st.session_state.aba_atual = "UG"
        if st.button("🚛 Fornecedores"): st.session_state.aba_atual = "FORN"
        if st.button("👤 Motoristas"): st.session_state.aba_atual = "MOTO"
        if st.button("🚗 Frota de Veículos"): st.session_state.aba_atual = "VEIC"
        if st.button("📦 Peças e Insumos"): st.session_state.aba_atual = "PECA"
        if st.button("📏 Unidades de Medida"): st.session_state.aba_atual = "UNID"
    
    with st.expander("🔄 MOVIMENTAÇÃO"):
        if st.button("⛽ Lançar Abastecimento"): st.session_state.aba_atual = "ABAST"
        if st.button("🛠️ Ordem de Serviço"): st.session_state.aba_atual = "OS"
        if st.button("📥 Entrada de Nota Fiscal"): st.session_state.aba_atual = "NF"

    with st.expander("📊 CONTROLADORIA/TCE"):
        if st.button("📈 Média de Consumo"): st.session_state.aba_atual = "REL_MED"
        if st.button("📄 Extrato por Ativo"): st.session_state.aba_atual = "REL_EXT"

# --- RENDERIZAÇÃO DE TELAS (EXEMPLOS DE ALTA FIDELIDADE) ---

def tela_veiculos():
    st.markdown("<div class='main-header'><h2>📦 Gestão de Patrimônio e Frota</h2></div>", unsafe_allow_html=True)
    with st.form("form_veic", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        pat = c1.text_input("Nº Patrimônio (TCE) *")
        placa = c2.text_input("Placa *")
        ren = c3.text_input("RENAVAM")
        cha = c4.text_input("CHASSI")
        
        c5, c6, c7 = st.columns([2,1,1])
        desc = c5.text_input("Descrição Detalhada do Veículo *")
        marca = c6.text_input("Marca")
        modelo = c7.text_input("Modelo")
        
        c8, c9, c10, c11 = st.columns(4)
        afab = c8.text_input("Ano Fab.")
        amod = c9.text_input("Ano Mod.")
        comb = c10.selectbox("Combustível", ["Diesel S10", "Diesel S500", "Gasolina Comum", "Etanol"])
        sec = c11.selectbox("Secretaria", ["Saúde", "Educação", "Infraestrutura", "Gabinete"])
        
        if st.form_submit_button("CADASTRAR ATIVO"):
            erp.cursor.execute("INSERT INTO veiculos (patrimonio, placa, renavam, chassi, descricao, marca, modelo, ano_fab, ano_mod, combustivel, secretaria) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                              (pat, placa, ren, cha, desc, marca, modelo, afab, amod, comb, sec))
            erp.conn.commit()
            st.success("Veículo registrado com sucesso.")

def tela_abastecimento():
    st.markdown("<div class='main-header'><h2>⛽ Registro de Consumo Auditável</h2></div>", unsafe_allow_html=True)
    
    # BUSCA DINÂMICA
    veic_list = [v[0] for v in erp.cursor.execute("SELECT placa FROM veiculos").fetchall()]
    moto_list = [m[0] for m in erp.cursor.execute("SELECT nome FROM motoristas").fetchall()]
    
    with st.form("form_abast"):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data do Lançamento")
        v_sel = c2.selectbox("Veículo (Placa)", veic_list if veic_list else ["Nenhum cadastrado"])
        m_sel = c3.selectbox("Motorista", moto_list if moto_list else ["Nenhum cadastrado"])
        
        c4, c5, c6 = st.columns(3)
        km_ant = c4.number_input("Odômetro Anterior", disabled=True)
        km_atu = c5.number_input("Odômetro Atual *")
        litros = c6.number_input("Litros *", step=0.01)
        
        c7, c8, c9 = st.columns(3)
        preco = c7.number_input("Preço Unitário (R$)", step=0.001)
        cupom = c8.text_input("Nº Cupom/Nota Fiscal")
        posto = c9.text_input("Posto Fornecedor")
        
        if st.form_submit_button("GRAVAR ABASTECIMENTO"):
            total = litros * preco
            erp.cursor.execute("INSERT INTO abastecimentos (data, veiculo_id, motorista_id, km_atu, litros, valor_unit, total, cupom, posto) VALUES (?,?,?,?,?,?,?,?,?)",
                              (str(data), v_sel, m_sel, km_atu, litros, preco, total, cupom, posto))
            erp.conn.commit()
            st.success(f"Lançamento OK. Valor Total: R$ {total:.2f}")

# --- ROTEAMENTO ---
aba = st.session_state.aba_atual
if aba == "Dashboard":
    st.markdown("<div class='main-header'><h2>📊 Painel de Controle SIM - Salitre</h2></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Frota Ativa", f"{len(erp.cursor.execute('SELECT id FROM veiculos').fetchall())} Veíc.")
    c2.metric("Motoristas", f"{len(erp.cursor.execute('SELECT id FROM motoristas').fetchall())}")
    c3.metric("OS Pendentes", "0")
    c4.metric("Consumo Mês", "R$ 0,00")
    st.divider()
    st.info("Sistema operando em modo de conformidade total com o TCE-CE.")

elif aba == "VEIC": tela_veiculos()
elif aba == "ABAST": tela_abastecimento()
elif aba == "FORN":
    st.markdown("<div class='main-header'><h2>🚚 Cadastro de Fornecedores</h2></div>")
    with st.form("f_forn"):
        razao = st.text_input("Razão Social *")
        cnpj = st.text_input("CNPJ/CPF *")
        c1, c2 = st.columns(2)
        end = c1.text_input("Endereço")
        mun = c2.text_input("Município")
        if st.form_submit_button("SALVAR FORNECEDOR"):
            erp.cursor.execute("INSERT INTO fornecedores (razao_social, cnpj_cpf, logradouro, cidade) VALUES (?,?,?,?)", (razao, cnpj, end, mun))
            erp.conn.commit()
            st.success("Fornecedor Salvo.")

# EXIBIÇÃO DE DADOS (DATABASE PREVIEW)
st.divider()
st.subheader("🔍 Histórico de Registros")
try:
    if aba == "VEIC": df = pd.read_sql("SELECT patrimonio, placa, descricao, secretaria FROM veiculos", erp.conn)
    elif aba == "ABAST": df = pd.read_sql("SELECT data, veiculo_id, km_atu, litros, total, cupom FROM abastecimentos", erp.conn)
    elif aba == "FORN": df = pd.read_sql("SELECT razao_social, cnpj_cpf, cidade FROM fornecedores", erp.conn)
    else: df = pd.DataFrame()
    st.dataframe(df, use_container_width=True)
except:
    st.write("Aguardando dados...")
