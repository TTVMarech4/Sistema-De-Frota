import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- CONFIGURAÇÃO DE SISTEMA CORPORATIVO ---
st.set_page_config(page_title="SIM - Gestão de Frota e Suprimentos", layout="wide", initial_sidebar_state="expanded")

# --- ENGINE DE DADOS (ARQUITETURA LS SISTEMAS) ---
class LSSystemClone:
    def __init__(self):
        self.conn = sqlite3.connect('ls_gestao_integral.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_complete_db()

    def setup_complete_db(self):
        # 1. SEGURANÇA E ACESSO
        self.cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, login TEXT UNIQUE, senha TEXT, nome TEXT, nivel TEXT)')
        
        # 2. ESTRUTURA ORGANIZACIONAL
        self.cursor.execute('CREATE TABLE IF NOT EXISTS unidades_gestoras (id INTEGER PRIMARY KEY, nome TEXT, cnpj TEXT, sigla TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS secretarias (id INTEGER PRIMARY KEY, nome TEXT, responsavel TEXT)')

        # 3. CADASTROS TÉCNICOS (O CORAÇÃO DO SITE QUE VOCÊ MANDOU)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_pessoa TEXT, cpf_cnpj TEXT UNIQUE, razao_social TEXT, 
            nome_fantasia TEXT, insc_estadual TEXT, insc_municipal TEXT, cep TEXT, logradouro TEXT, 
            numero TEXT, bairro TEXT, cidade TEXT, uf TEXT, telefone TEXT, email TEXT, 
            banco TEXT, agencia TEXT, conta TEXT, status TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT UNIQUE, patrimonio TEXT, renavam TEXT, 
            chassi TEXT, marca TEXT, modelo TEXT, ano_fab TEXT, ano_mod TEXT, combustivel TEXT, 
            cap_tanque REAL, secretaria TEXT, vinculo TEXT, status TEXT)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS motoristas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, cnh TEXT, 
            categoria TEXT, validade TEXT, secretaria TEXT)''')

        # 4. SUPRIMENTOS E LOGÍSTICA
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, unidade TEXT, grupo TEXT, 
            estoque_atual REAL, estoque_min REAL, custo_medio REAL)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, veiculo_id TEXT, motorista_id TEXT, 
            km_ant REAL, km_atu REAL, litros REAL, valor_unit REAL, total REAL, cupom TEXT, posto TEXT)''')

        # Criação do usuário solicitado
        senha_h = hashlib.sha256("1234".encode()).hexdigest()
        self.cursor.execute("INSERT OR IGNORE INTO usuarios (login, senha, nome, nivel) VALUES (?,?,?,?)", 
                           ("05772587374", senha_h, "ADMINISTRADOR MASTER", "MASTER"))
        self.conn.commit()

db = LSSystemClone()

# --- LÓGICA DE SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False

# --- CSS: REPLICA DE INTERFACE LS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    [data-testid="stSidebar"] { background-color: #2c3e50 !important; }
    .main-header { background: #fff; padding: 10px 20px; border-bottom: 2px solid #3c8dbc; margin-bottom: 20px; display: flex; justify-content: space-between; }
    .form-section { background: #fff; padding: 20px; border-radius: 5px; border-top: 3px solid #d2d6de; box-shadow: 0 1px 1px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .section-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .stButton>button { background-color: #3c8dbc; color: white; border-radius: 3px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://via.placeholder.com/300x80?text=LS+SISTEMAS+CLONE", use_container_width=True)
        with st.form("login"):
            st.subheader("Acesso ao Sistema")
            user = st.text_input("CPF / Usuário")
            pwd = st.text_input("Senha", type="password")
            if st.form_submit_button("Acessar"):
                pwd_h = hashlib.sha256(pwd.encode()).hexdigest()
                res = db.cursor.execute("SELECT * FROM usuarios WHERE login=? AND senha=?", (user, pwd_h)).fetchone()
                if res:
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

# --- SISTEMA PÓS-LOGIN ---
else:
    # Cabeçalho Superior
    st.markdown(f"""
        <div class='main-header'>
            <span style='font-weight:bold; color:#3c8dbc;'>🏛️ SIM - GESTÃO MUNICIPAL INTEGRADA</span>
            <span>👤 Conectado como: 05772587374 | <a href='https://google.com' style='color:red;'>Sair</a></span>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Profissional
    with st.sidebar:
        st.markdown("### 🛠️ MÓDULOS")
        menu = st.selectbox("Escolha o Módulo", ["📊 DASHBOARD", "📝 CADASTROS", "🔄 MOVIMENTAÇÃO", "📉 RELATÓRIOS"])
        st.divider()
        
        if menu == "CADASTROS":
            aba = st.radio("Opções:", ["🏢 Unidade Gestora", "🚚 Fornecedores", "🚗 Veículos", "👤 Motoristas", "📦 Produtos"])
        elif menu == "MOVIMENTAÇÃO":
            aba = st.radio("Opções:", ["⛽ Abastecimento", "🛠️ Ordem de Serviço", "📥 Entrada de Nota"])
        else:
            aba = "Geral"

    # --- TELA FORNECEDOR (IGUAL AO LINK LS) ---
    if menu == "CADASTROS" and aba == "🚚 Fornecedores":
        st.subheader("Cadastro de Fornecedor")
        with st.container():
            st.markdown("<div class='form-section'>", unsafe_allow_html=True)
            with st.form("forn_ls"):
                st.markdown("<p class='section-title'>DADOS GERAIS</p>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1, 2, 3])
                tp = c1.selectbox("Tipo Pessoa", ["Jurídica", "Física"])
                doc = c2.text_input("CPF / CNPJ *")
                razao = c3.text_input("Razão Social *")
                
                c4, c5, c6 = st.columns(3)
                fant = c4.text_input("Nome Fantasia")
                ie = c5.text_input("Insc. Estadual")
                im = c6.text_input("Insc. Municipal")
                
                st.markdown("<p class='section-title'>ENDEREÇO</p>", unsafe_allow_html=True)
                c7, c8, c9 = st.columns([1, 3, 1])
                cep = c7.text_input("CEP")
                rua = c8.text_input("Logradouro")
                n = c9.text_input("Nº")
                
                c10, c11, c12 = st.columns(3)
                ba = c10.text_input("Bairro")
                cid = c11.text_input("Cidade")
                uf = c12.selectbox("UF", ["CE", "PI", "PE", "RN", "PB", "MA"])
                
                st.markdown("<p class='section-title'>DADOS BANCÁRIOS</p>", unsafe_allow_html=True)
                c13, c14, c15 = st.columns(3)
                bank = c13.text_input("Banco")
                ag = c14.text_input("Agência")
                cc = c15.text_input("Conta Corrente")
                
                if st.form_submit_button("💾 SALVAR REGISTRO"):
                    db.cursor.execute("INSERT INTO fornecedores (tipo_pessoa, cpf_cnpj, razao_social, nome_fantasia, insc_estadual, insc_municipal, cep, logradouro, numero, bairro, cidade, uf, banco, agencia, conta, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                     (tp, doc, razao, fant, ie, im, cep, rua, n, ba, cid, uf, bank, ag, cc, "ATIVO"))
                    db.conn.commit()
                    st.success("Fornecedor cadastrado com sucesso!")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- TELA VEÍCULO ---
    elif menu == "CADASTROS" and aba == "🚗 Veículos":
        st.subheader("Cadastro de Ativos")
        with st.form("veic_ls"):
            c1, c2, c3, c4 = st.columns(4)
            placa = c1.text_input("Placa *")
            pat = c2.text_input("Nº Patrimônio")
            ren = c3.text_input("RENAVAM")
            cha = c4.text_input("CHASSI")
            
            c5, c6, c7 = st.columns(3)
            desc = c5.text_input("Descrição / Modelo")
            comb = c6.selectbox("Combustível", ["Diesel S10", "Diesel S500", "Gasolina", "Etanol", "Flex"])
            sec = c7.selectbox("Secretaria", ["Saúde", "Educação", "Infraestrutura", "Ação Social"])
            
            if st.form_submit_button("GRAVAR VEÍCULO"):
                db.cursor.execute("INSERT INTO veiculos (placa, patrimonio, renavam, chassi, modelo, combustivel, secretaria, status) VALUES (?,?,?,?,?,?,?,?)",
                                 (placa, pat, ren, cha, desc, comb, sec, "ATIVO"))
                db.conn.commit()
                st.success("Veículo catalogado.")

    # --- TELA DASHBOARD ---
    elif menu == "📊 DASHBOARD":
        st.subheader("Indicadores de Gestão")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Frota Ativa", len(db.cursor.execute("SELECT id FROM veiculos").fetchall()))
        c2.metric("Fornecedores", len(db.cursor.execute("SELECT id FROM fornecedores").fetchall()))
        c3.metric("Custos Mês", "R$ 0,00")
        c4.metric("Consumo Médio", "0.0 KM/L")
        
        st.divider()
        st.markdown("### 📋 Últimos Fornecedores Cadastrados")
        df_f = pd.read_sql("SELECT razao_social, cpf_cnpj, cidade, status FROM fornecedores ORDER BY id DESC LIMIT 5", db.conn)
        st.table(df_f)

# --- FOOTER ---
st.markdown("<br><hr><center>SIM v14.0 | Salitre-CE | Auditoria Padrão TCE</center>", unsafe_allow_html=True)
