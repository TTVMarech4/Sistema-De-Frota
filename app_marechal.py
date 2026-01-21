import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="SIM - LS Enterprise", layout="wide", initial_sidebar_state="expanded")

# --- ENGINE DE SEGURANÇA E DADOS ---
class LS_Engine:
    def __init__(self):
        self.conn = sqlite3.connect('ls_enterprise_salitre.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Tabelas de Sistema
        self.cursor.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, login TEXT UNIQUE, senha TEXT, nome TEXT, perfil TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS unidades_gestoras (id INTEGER PRIMARY KEY, nome TEXT, cnpj TEXT, sigla TEXT)')
        
        # Cadastro de Fornecedor (Engenharia Reversa LS)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_pessoa TEXT, cpf_cnpj TEXT UNIQUE, 
            razao_social TEXT, nome_fantasia TEXT, insc_estadual TEXT, insc_municipal TEXT,
            cep TEXT, logradouro TEXT, numero TEXT, bairro TEXT, cidade TEXT, uf TEXT,
            telefone TEXT, email TEXT, banco TEXT, agencia TEXT, conta TEXT, status TEXT)''')
        
        # Cadastro de Veículos (High Density)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT UNIQUE, patrimonio TEXT, 
            renavam TEXT, chassi TEXT, marca TEXT, modelo TEXT, ano_fab TEXT, 
            ano_mod TEXT, comb TEXT, cap_tanque REAL, secretaria TEXT, status TEXT)''')

        # Usuário Padrão (Conforme seu acesso)
        senha_hash = hashlib.sha256("1234".encode()).hexdigest()
        self.cursor.execute("INSERT OR IGNORE INTO usuarios (login, senha, nome, perfil) VALUES (?,?,?,?)", 
                           ("05772587374", senha_hash, "MARECHAL ADMINISTRADOR", "MASTER"))
        self.conn.commit()

db = LS_Engine()

# --- GESTÃO DE SESSÃO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- CSS CUSTOMIZADO (PADRÃO CORPORATIVO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
    .header-top { background: #2c3e50; color: white; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; }
    .sidebar-active { background-color: #34495e !important; border-left: 5px solid #3498db; }
    .data-grid-header { background: #e9ecef; padding: 10px; font-weight: bold; border: 1px solid #dee2e6; }
    </style>
""", unsafe_allow_html=True)

# --- TELA DE LOGIN (100% IGUAL AO FLUXO) ---
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.image("https://via.placeholder.com/200x60?text=SIM+SALITRE", use_container_width=True)
        st.subheader("Acesso ao Sistema")
        usuario = st.text_input("Usuário (CPF)")
        senha = st.text_input("Senha", type="password")
        
        if st.button("ENTRAR"):
            senha_h = hashlib.sha256(senha.encode()).hexdigest()
            user_data = db.cursor.execute("SELECT * FROM usuarios WHERE login=? AND senha=?", (usuario, senha_h)).fetchone()
            if user_data:
                st.session_state.autenticado = True
                st.session_state.user_nome = user_data[3]
                st.rerun()
            else:
                st.error("Credenciais inválidas")
        st.markdown("</div>", unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---
if not st.session_state.autenticado:
    tela_login()
else:
    # Top Bar
    st.markdown(f"""
        <div class='header-top'>
            <span>🏛️ SIM - SALITRE/CE | LS SISTEMAS</span>
            <span>👤 {st.session_state.user_nome} | <a href='#' style='color:white;'>Sair</a></span>
        </div>
    """, unsafe_allow_html=True)

    # Menu Lateral
    with st.sidebar:
        st.markdown("### 📂 NAVEGAÇÃO")
        menu = st.selectbox("Módulos", ["DASHBOARD", "CADASTROS", "MOVIMENTAÇÃO", "RELATÓRIOS"])
        st.divider()
        
        if menu == "CADASTROS":
            sub = st.radio("Selecione:", ["🏢 Unidade Gestora", "🚚 Fornecedores", "👤 Motoristas", "🚗 Veículos", "📦 Peças/Produtos"])
        elif menu == "MOVIMENTAÇÃO":
            sub = st.radio("Selecione:", ["⛽ Abastecimento", "🛠️ Ordem de Serviço", "📥 Entrada NF"])
        else:
            sub = "Geral"

    # --- MÓDULO FORNECEDOR (REVERSO COMPLETO) ---
    if menu == "CADASTROS" and "Fornecedores" in sub:
        st.subheader("📝 Cadastro de Fornecedor - LS Enterprise")
        
        with st.expander("➕ Adicionar Novo Fornecedor", expanded=True):
            with st.form("form_forn"):
                # Seção 1: Identificação
                st.markdown("**1. IDENTIFICAÇÃO**")
                c1, c2, c3 = st.columns([1,2,3])
                t_pessoa = c1.selectbox("Tipo", ["Jurídica", "Física"])
                doc = c2.text_input("CNPJ / CPF *")
                razao = c3.text_input("Razão Social *")
                
                c4, c5, c6 = st.columns(3)
                fantasia = c4.text_input("Nome Fantasia")
                ie = c5.text_input("Insc. Estadual")
                im = c6.text_input("Insc. Municipal")
                
                # Seção 2: Localização
                st.markdown("**2. ENDEREÇO E CONTATO**")
                c7, c8, c9 = st.columns([1,3,1])
                cep = c7.text_input("CEP")
                rua = c8.text_input("Logradouro")
                num = c9.text_input("Nº")
                
                c10, c11, c12, c13 = st.columns([2,2,1,2])
                bairro = c10.text_input("Bairro")
                cidade = c11.text_input("Cidade")
                uf = c12.selectbox("UF", ["CE", "PI", "PE", "RN", "PB"])
                email = c13.text_input("Email Corporativo")
                
                # Seção 3: Dados Bancários
                st.markdown("**3. DADOS PARA PAGAMENTO**")
                c14, c15, c16 = st.columns(3)
                banco = c14.text_input("Banco")
                ag = c15.text_input("Agência")
                conta = c16.text_input("Conta")
                
                if st.form_submit_button("💾 SALVAR REGISTRO"):
                    db.cursor.execute("INSERT INTO fornecedores (tipo_pessoa, cpf_cnpj, razao_social, nome_fantasia, cep, logradouro, numero, bairro, cidade, uf, email, banco, agencia, conta, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                     (t_pessoa, doc, razao, fantasia, cep, rua, num, bairro, cidade, uf, email, banco, ag, conta, "ATIVO"))
                    db.conn.commit()
                    st.success("Fornecedor cadastrado na base municipal!")

        # Listagem (DataGrid LS)
        st.markdown("**Fornecedores Cadastrados**")
        df_f = pd.read_sql("SELECT id, razao_social, cpf_cnpj, cidade, telefone FROM fornecedores", db.conn)
        st.dataframe(df_f, use_container_width=True)

    # --- MÓDULO DASHBOARD ---
    elif menu == "DASHBOARD":
        st.subheader("📊 Resumo Operacional")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Veículos Ativos", len(db.cursor.execute("SELECT id FROM veiculos").fetchall()))
        c2.metric("Fornecedores", len(db.cursor.execute("SELECT id FROM fornecedores").fetchall()))
        c3.metric("Abastecimentos/Mês", "0")
        c4.metric("Valor Total Gasto", "R$ 0,00")
        
        st.divider()
        st.info("Sistema de Informação Municipal - Versão 13.0 | Salitre-CE")
