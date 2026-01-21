import streamlit as st
import pandas as pd
import sqlite3
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Frota", page_icon="🚗", layout="wide")

# --- ESTILIZAÇÃO CSS (REPLICANDO A BARRA ESCURA E O LOOK DA FOTO) ---
st.markdown("""
    <style>
    /* Estilo da Barra Superior */
    .nav-bar {
        background-color: #343a40;
        padding: 10px;
        display: flex;
        align-items: center;
        color: white;
        font-family: sans-serif;
        border-top: 3px solid #28a745; /* Linha verde no topo */
        margin-bottom: 20px;
    }
    .nav-title {
        font-weight: bold;
        margin-right: 30px;
        font-size: 18px;
    }
    .nav-item {
        margin-right: 20px;
        color: #adb5bd;
        cursor: pointer;
        font-size: 15px;
    }
    /* Ajuste do fundo */
    .stApp {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
db_path = 'sistema_marechal_v3.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS usuarios (cpf TEXT PRIMARY KEY, senha TEXT)')
c.execute("INSERT OR IGNORE INTO usuarios VALUES ('05772587374', '1234')")
conn.commit()

# --- ESTADO DO LOGIN ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #d93043;'>Frota</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>entre para iniciar a sessão</p>", unsafe_allow_html=True)
        
        cpf = st.text_input("CPF")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            c.execute("SELECT * FROM usuarios WHERE cpf=? AND senha=?", (cpf, senha))
            if c.fetchone():
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")

# --- TELA PRINCIPAL (IGUAL À FOTO) ---
else:
    # Criando a Barra Superior via HTML/Markdown
    st.markdown(f"""
        <div class="nav-bar">
            <div class="nav-title">PREFEITURA MUNICIPAL DE SALITRE</div>
            <div class="nav-item">📁 Cadastros ▾</div>
            <div class="nav-item">💼 Movimentos ▾</div>
            <div class="nav-item">📊 Relatórios ▾</div>
            <div class="nav-item">🛠️ Utilitários ▾</div>
            <div style="margin-left: auto; padding-right: 20px;">👤</div>
        </div>
    """, unsafe_allow_html=True)

    # Menu Lateral Streamlit para funcionalidades reais
    with st.sidebar:
        st.header("Comandos")
        opcao = st.selectbox("Selecione uma Função:", 
                            ["Dashboard", "Importar Planilha", "IA de Processamento"])
        
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # Conteúdo da Página
    if opcao == "Dashboard":
        st.subheader("Painel de Controle")
        st.write("Bem-vindo ao sistema de gestão, Marechal.")
        
    elif opcao == "Importar Planilha":
        st.subheader("Módulo de Importação")
        file = st.file_uploader("Suba sua planilha aqui", type=['xlsx', 'csv'])
        if file:
            df = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
            st.dataframe(df)
