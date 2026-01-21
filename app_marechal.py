import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- CONFIGURAÇÃO DE UI ENTERPRISE ---
st.set_page_config(page_title="SIM - LS Sistemas v2026", layout="wide", initial_sidebar_state="expanded")

# --- ENGINE DE DADOS RELACIONAL (REPLICA DO DICIONÁRIO LS) ---
class LS_Replica_Engine:
    def __init__(self):
        self.conn = sqlite3.connect('ls_replica_integral.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # SEGURANÇA ( LOGIN REPLICADO )
        self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, login TEXT UNIQUE, password TEXT, name TEXT)')
        
        # CADASTRO DE FORNECEDORES ( COPIA IDENTICA DO FORMULÁRIO LS )
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, person_type TEXT, document TEXT UNIQUE, name TEXT, fancy_name TEXT,
            state_reg TEXT, city_reg TEXT, zip_code TEXT, address TEXT, number TEXT, complement TEXT,
            neighborhood TEXT, city TEXT, state TEXT, phone TEXT, email TEXT,
            bank_name TEXT, bank_agency TEXT, bank_account TEXT, provider_type TEXT, status TEXT)''')

        # CADASTRO DE VEÍCULOS ( FICHA TÉCNICA TOTAL )
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, plate TEXT UNIQUE, heritage_code TEXT, renavam TEXT, chassi TEXT,
            brand TEXT, model TEXT, color TEXT, year_fab TEXT, year_mod TEXT, fuel_type TEXT, 
            tank_capacity REAL, initial_km REAL, secretary TEXT, link_type TEXT, contract_num TEXT, status TEXT)''')

        # USUÁRIO DE ACESSO SOLICITADO
        pw = hashlib.sha256("1234".encode()).hexdigest()
        self.cursor.execute("INSERT OR IGNORE INTO users (login, password, name) VALUES (?,?,?)", 
                           ("05772587374", pw, "MARECHAL ADM"))
        self.conn.commit()

db = LS_Replica_Engine()

# --- CSS: CLONAGEM VISUAL (CORES E ESPAÇAMENTO LS) ---
st.markdown("""
    <style>
    .main { background-color: #ecf0f5; }
    [data-testid="stSidebar"] { background-color: #222d32 !important; }
    .stHeader { background-color: #3c8dbc !important; }
    .box-header { background: #ffffff; padding: 15px; border-top: 3px solid #3c8dbc; border-radius: 3px; box-shadow: 0 1px 1px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .ls-label { font-size: 12px; font-weight: bold; color: #333; margin-bottom: 5px; }
    .stButton>button { background-color: #00a65a !important; color: white; border: none; padding: 10px 25px; font-weight: bold; }
    .top-bar { background-color: #3c8dbc; padding: 10px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- FLUXO DE LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<div style='text-align:center; padding: 50px;'><h2 style='color:#3c8dbc;'>LS SISTEMAS</h2><p>Gestão de Frotas</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("LOGIN"):
                p_hash = hashlib.sha256(p.encode()).hexdigest()
                valid = db.cursor.execute("SELECT * FROM users WHERE login=? AND password=?", (u, p_hash)).fetchone()
                if valid:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Acesso Negado.")
else:
    # --- INTERFACE LOGADA ---
    st.markdown(f"<div class='top-bar'><span><b>SIM</b> | Sistema de Informação Municipal</span><span>Usuário: 05772587374 | <a href='/' style='color:white;'>Sair</a></span></div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div style='padding:10px; color:white;'><b>MENU PRINCIPAL</b></div>", unsafe_allow_html=True)
        mod = st.selectbox("", ["DASHBOARD", "CADASTROS", "MOVIMENTAÇÃO", "CONFIGURAÇÕES"])
        st.divider()
        if mod == "CADASTROS":
            page = st.radio("Selecione a Tabela:", ["Fornecedores", "Veículos", "Motoristas", "Produtos", "Secretarias"])
        elif mod == "MOVIMENTAÇÃO":
            page = st.radio("Selecione a Operação:", ["Abastecimento", "Entrada NF", "Ordem de Serviço"])
        else: page = "Home"

    # --- REPLICA FORNECEDOR ( 100% IGUAL AO SITE ) ---
    if mod == "CADASTROS" and page == "Fornecedores":
        st.markdown("<div class='box-header'><h4><i class='fa fa-edit'></i> Cadastro de Fornecedor</h4></div>", unsafe_allow_html=True)
        
        with st.form("full_provider_form"):
            st.warning("Campos com * são obrigatórios.")
            
            # Linha 1: Identidade
            c1, c2, c3, c4 = st.columns([1, 1.5, 2.5, 2])
            p_type = c1.selectbox("Tipo de Pessoa *", ["Jurídica", "Física"])
            doc = c2.text_input("CPF/CNPJ *")
            name = c3.text_input("Razão Social *")
            fancy = c4.text_input("Nome Fantasia")

            # Linha 2: Fiscal
            c5, c6, c7 = st.columns(3)
            s_reg = c5.text_input("Inscrição Estadual")
            m_reg = c6.text_input("Inscrição Municipal")
            p_kind = c7.selectbox("Tipo de Fornecedor", ["Combustíveis", "Peças", "Serviços", "Locação", "Outros"])

            # Linha 3: Endereço
            st.markdown("---")
            c8, c9, c10, c11 = st.columns([1, 2, 1, 1.5])
            zip_c = c8.text_input("CEP")
            addr = c9.text_input("Logradouro (Rua/Av)")
            num = c10.text_input("Número")
            comp = c11.text_input("Complemento")

            c12, c13, c14, c15 = st.columns([2, 2, 1, 2])
            neigh = c12.text_input("Bairro")
            city = c13.text_input("Cidade")
            uf = c14.selectbox("UF", ["CE", "PI", "PE", "RN", "PB", "MA", "BA"])
            email = c15.text_input("E-mail")

            # Linha 4: Financeiro
            st.markdown("---")
            st.markdown("<b>DADOS BANCÁRIOS</b>", unsafe_allow_html=True)
            c16, c17, c18 = st.columns(3)
            b_name = c16.text_input("Banco")
            b_ag = c17.text_input("Agência")
            b_acc = c18.text_input("Conta Corrente")

            if st.form_submit_button("GRAVAR REGISTRO"):
                db.cursor.execute("""INSERT INTO providers (person_type, document, name, fancy_name, state_reg, city_reg, zip_code, address, number, complement, neighborhood, city, state, email, bank_name, bank_agency, bank_account, provider_type, status) 
                                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                  (p_type, doc, name, fancy, s_reg, m_reg, zip_c, addr, num, comp, neigh, city, uf, email, b_name, b_ag, b_acc, p_kind, "ATIVO"))
                db.conn.commit()
                st.success("Fornecedor inserido com sucesso na base de dados.")

    # --- REPLICA VEÍCULO ( 100% IGUAL AO SITE ) ---
    elif mod == "CADASTROS" and page == "Veículos":
        st.markdown("<div class='box-header'><h4><i class='fa fa-car'></i> Cadastro de Veículos</h4></div>", unsafe_allow_html=True)
        with st.form("vehicle_form"):
            c1, c2, c3, c4 = st.columns(4)
            plate = c1.text_input("Placa *")
            h_code = c2.text_input("Nº Patrimônio")
            renavam = c3.text_input("RENAVAM")
            chassi = c4.text_input("CHASSI")

            c5, c6, c7, c8 = st.columns(4)
            brand = c5.text_input("Marca")
            model = c6.text_input("Modelo")
            color = c7.text_input("Cor")
            fuel = c8.selectbox("Combustível", ["Diesel S10", "Diesel S500", "Gasolina", "Etanol", "Flex", "Gás"])

            c9, c10, c11, c12 = st.columns(4)
            y_f = c9.text_input("Ano Fab.")
            y_m = c10.text_input("Ano Mod.")
            tank = c11.number_input("Cap. Tanque (L)")
            i_km = c12.number_input("Odômetro Inicial")

            c13, c14, c15 = st.columns(3)
            sec = c13.selectbox("Secretaria Detentora", ["Saúde", "Educação", "Infraestrutura", "Gabinete"])
            v_type = c14.selectbox("Vínculo", ["Próprio", "Locado", "Cessão"])
            c_num = c15.text_input("Nº Contrato (Se locado)")

            if st.form_submit_button("SALVAR VEÍCULO"):
                db.cursor.execute("""INSERT INTO vehicles (plate, heritage_code, renavam, chassi, brand, model, color, year_fab, year_mod, fuel_type, tank_capacity, initial_km, secretary, link_type, contract_num, status) 
                                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                  (plate, h_code, renavam, chassi, brand, model, color, y_f, y_m, fuel, tank, i_km, sec, v_type, c_num, "ATIVO"))
                db.conn.commit()
                st.success("Veículo catalogado com sucesso.")

    # --- DASHBOARD ---
    elif mod == "DASHBOARD":
        st.markdown("<div class='box-header'><h4>Visão Geral do Município</h4></div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Veículos Ativos", len(db.cursor.execute("SELECT id FROM vehicles").fetchall()))
        c2.metric("Fornecedores", len(db.cursor.execute("SELECT id FROM providers").fetchall()))
        c3.metric("Contratos Vigentes", "0")
        c4.metric("Consumo Mensal", "R$ 0,00")
        
        st.divider()
        st.markdown("<b>LISTAGEM DE FORNECEDORES (AUDITORIA)</b>", unsafe_allow_html=True)
        df = pd.read_sql("SELECT name as 'Razão Social', document as 'CNPJ/CPF', city as 'Cidade', status FROM providers", db.conn)
        st.dataframe(df, use_container_width=True)

# --- FOOTER ---
st.markdown("<center><small>SIM v15.0 | Padrão LS Sistemas | Salitre-CE</small></center>", unsafe_allow_html=True)
