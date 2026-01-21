import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DE ALTO NÍVEL (INTERFACE LS STYLE) ---
st.set_page_config(page_title="SIM - LS Sistemas Mirror", layout="wide", initial_sidebar_state="expanded")

# --- BANCO DE DADOS RELACIONAL ROBUSTO ---
class SIM_LS:
    def __init__(self):
        self.conn = sqlite3.connect('sim_ls_salitre.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # CADASTROS ESTRUTURAIS (O que o sistema LS exige)
        self.cursor.execute('CREATE TABLE IF NOT EXISTS unidades_gestoras (id INTEGER PRIMARY KEY, nome TEXT, cnpj TEXT, sigla TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS secretarias (id INTEGER PRIMARY KEY, nome TEXT, unidade_gestora_id INTEGER)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS naturezas_operacao (id INTEGER PRIMARY KEY, codigo TEXT, descricao TEXT, tipo TEXT)')
        
        # FORNECEDORES (Completo conforme o link)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_pessoa TEXT, cpf_cnpj TEXT UNIQUE, 
            razao_social TEXT, nome_fantasia TEXT, insc_estadual TEXT, insc_municipal TEXT,
            cep TEXT, logradouro TEXT, numero TEXT, bairro TEXT, cidade TEXT, uf TEXT,
            telefone TEXT, email TEXT, banco TEXT, agencia TEXT, conta TEXT)''')

        # VEÍCULOS (Ficha Técnica LS)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT UNIQUE, patrimonio TEXT, 
            renavam TEXT, chassi TEXT, marca TEXT, modelo TEXT, cor TEXT, ano_fab TEXT, 
            ano_mod TEXT, combustivel TEXT, cap_tanque REAL, odometro_inicial REAL, 
            secretaria_id INTEGER, status TEXT, tipo_vinculo TEXT, num_contrato TEXT)''')

        # ESTOQUE / PEÇAS (Com Fator de Conversão)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, unidade_entrada TEXT, 
            unidade_saida TEXT, fator_conversao REAL, estoque_min REAL, estoque_atual REAL, grupo TEXT)''')

        # MOVIMENTAÇÃO (Auditável)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, veiculo_id TEXT, motorista_id TEXT, 
            km_ant REAL, km_atu REAL, litros REAL, valor_unit REAL, total REAL, cupom TEXT, posto_id INTEGER)''')

        self.conn.commit()

db = SIM_LS()

# --- CSS: ESTILO SISTEMA DE PREFEITURA ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    [data-testid="stSidebar"] { background-color: #2c3e50 !important; }
    .main-header { background: white; padding: 15px; border-bottom: 2px solid #dee2e6; margin-bottom: 20px; border-left: 5px solid #007bff; }
    .section-title { color: #495057; font-weight: bold; border-bottom: 1px solid #ced4da; margin-bottom: 15px; padding-bottom: 5px; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO LS STYLE ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=SIM+SALITRE", use_container_width=True)
    st.markdown("<p style='text-align:center; color:white;'>Usuário: 05772587374</p>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.selectbox("PRINCIPAL", ["Dashboard", "Cadastros", "Movimentos", "Relatórios"])
    
    if menu == "Cadastros":
        sub = st.radio("Selecione:", ["Unidade Gestora", "Fornecedor", "Motorista", "Veículo", "Produto/Peça", "Natureza de Operação"])
    elif menu == "Movimentos":
        sub = st.radio("Selecione:", ["Entrada de Nota", "Abastecimento", "Ordem de Serviço", "Saída de Estoque"])
    else:
        sub = "Geral"

# --- TELA: FORNECEDOR (IGUAL AO LINK LS) ---
if menu == "Cadastros" and sub == "Fornecedor":
    st.markdown("<div class='main-header'><h3>📝 Cadastro de Fornecedor</h3></div>", unsafe_allow_html=True)
    
    with st.form("f_forn"):
        st.markdown("<p class='section-title'>Dados Identificadores</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 2])
        tipo = c1.selectbox("Tipo", ["Jurídica", "Física"])
        doc = c2.text_input("CPF/CNPJ *")
        razao = c3.text_input("Razão Social *")
        
        c4, c5, c6 = st.columns(3)
        fantasia = c4.text_input("Nome Fantasia")
        ie = c5.text_input("Insc. Estadual")
        im = c6.text_input("Insc. Municipal")
        
        st.markdown("<p class='section-title'>Endereço e Contato</p>", unsafe_allow_html=True)
        c7, c8, c9 = st.columns([1, 3, 1])
        cep = c7.text_input("CEP")
        rua = c8.text_input("Logradouro")
        num = c9.text_input("Nº")
        
        c10, c11, c12 = st.columns(3)
        bairro = c10.text_input("Bairro")
        cidade = c11.text_input("Cidade")
        uf = c12.selectbox("UF", ["CE", "PI", "PE", "BA", "RN"])
        
        st.markdown("<p class='section-title'>Dados Bancários (Para Pagamento)</p>", unsafe_allow_html=True)
        c13, c14, c15 = st.columns(3)
        banco = c13.text_input("Banco")
        ag = c14.text_input("Agência")
        conta = c15.text_input("Conta Corrente")
        
        if st.form_submit_button("💾 SALVAR FORNECEDOR"):
            db.cursor.execute("INSERT INTO fornecedores (tipo_pessoa, cpf_cnpj, razao_social, nome_fantasia, insc_estadual, insc_municipal, cep, logradouro, numero, bairro, cidade, uf, banco, agencia, conta) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             (tipo, doc, razao, fantasia, ie, im, cep, rua, num, bairro, cidade, uf, banco, ag, conta))
            db.conn.commit()
            st.success("Fornecedor registrado com sucesso!")

# --- TELA: VEÍCULO (FICHA TÉCNICA LS) ---
elif menu == "Cadastros" and sub == "Veículo":
    st.markdown("<div class='main-header'><h3>🚗 Cadastro de Veículo</h3></div>", unsafe_allow_html=True)
    
    with st.form("f_veic"):
        c1, c2, c3 = st.columns(3)
        placa = c1.text_input("Placa (Mercosul/Antiga) *")
        pat = c2.text_input("Nº Patrimônio")
        vinculo = c3.selectbox("Vínculo", ["Próprio", "Locado", "Cessão"])
        
        c4, c5, c6, c7 = st.columns(4)
        ren = c4.text_input("RENAVAM")
        cha = c5.text_input("CHASSI")
        marca = c6.text_input("Marca")
        modelo = c7.text_input("Modelo")
        
        c8, c9, c10 = st.columns(3)
        ano_f = c8.text_input("Ano Fab.")
        ano_m = c9.text_input("Ano Mod.")
        comb = c10.selectbox("Combustível", ["Diesel S10", "Diesel S500", "Gasolina", "Etanol", "Flex"])
        
        c11, c12 = st.columns(2)
        sec = c11.selectbox("Secretaria Responsável", ["Educação", "Saúde", "Obras", "Agricultura"])
        contrato = c12.text_input("Nº Contrato (Se Locado)")
        
        if st.form_submit_button("💾 SALVAR VEÍCULO"):
            db.cursor.execute("INSERT INTO veiculos (placa, patrimonio, tipo_vinculo, renavam, chassi, marca, modelo, ano_fab, ano_mod, combustivel, num_contrato) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                             (placa, pat, vinculo, ren, cha, marca, modelo, ano_f, ano_m, comb, contrato))
            db.conn.commit()
            st.success("Veículo catalogado.")

# --- TELA: DASHBOARD ---
elif menu == "Dashboard":
    st.markdown("<div class='main-header'><h3>📊 Painel de Indicadores de Gestão</h3></div>", unsafe_allow_html=True)
    
    # KPIs Rápidos
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Veículos Ativos", len(db.cursor.execute("SELECT id FROM veiculos").fetchall()))
    c2.metric("Fornecedores", len(db.cursor.execute("SELECT id FROM fornecedores").fetchall()))
    c3.metric("OS Pendentes", "0")
    c4.metric("Consumo Combustível", "R$ 0,00")
    
    st.divider()
    st.subheader("📋 Últimas Movimentações")
    df_v = pd.read_sql("SELECT placa, marca, modelo, tipo_vinculo FROM veiculos ORDER BY id DESC LIMIT 10", db.conn)
    st.table(df_v)
