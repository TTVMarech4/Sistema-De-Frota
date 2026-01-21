import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Frota - Salitre", page_icon="🚗", layout="wide")

# --- BANCO DE DADOS (Criação Dinâmica de Tabelas) ---
db_path = 'sistema_marechal_final.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

# Tabela de Usuários (Login)
c.execute('CREATE TABLE IF NOT EXISTS usuarios (cpf TEXT PRIMARY KEY, senha TEXT)')
c.execute("INSERT OR IGNORE INTO usuarios VALUES ('05772587374', '1234')")
conn.commit()

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] { background-color: #343a40; border-top: 5px solid #28a745; }
    .stButton>button { width: 100%; text-align: left; padding-left: 10px; border: none; background: transparent; color: #333; }
    .stButton>button:hover { background-color: #f0f2f6; color: #d93043; }
    .menu-divider { border-top: 1px solid #ddd; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADOS DO SISTEMA ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'tela_atual' not in st.session_state: st.session_state.tela_atual = "Home"

# --- FUNÇÃO DE CADASTRO GENÉRICO ---
def tela_cadastro(nome_item):
    st.subheader(f"📝 Cadastro de {nome_item}")
    
    # Cria tabela no banco se não existir
    tabela = nome_item.lower().replace(" ", "_").replace("/", "_")
    c.execute(f'CREATE TABLE IF NOT EXISTS {tabela} (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)')
    conn.commit()
    
    with st.form(key=f"form_{tabela}", clear_on_submit=True):
        novo_nome = st.text_input(f"Nome do(a) {nome_item}:")
        if st.form_submit_button(f"Salvar {nome_item}"):
            if novo_nome:
                c.execute(f"INSERT INTO {tabela} (nome) VALUES (?)", (novo_nome,))
                conn.commit()
                st.success(f"{nome_item} cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha o nome.")
    
    st.divider()
    st.write(f"### {nome_item}s Cadastrados")
    df = pd.read_sql(f"SELECT nome as '{nome_item}' FROM {tabela}", conn)
    st.dataframe(df, use_container_width=True)

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #d93043;'>Frota</h1>", unsafe_allow_html=True)
        cpf = st.text_input("CPF")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            c.execute("SELECT * FROM usuarios WHERE cpf=? AND senha=?", (cpf, senha))
            if c.fetchone():
                st.session_state.logado = True
                st.rerun()
            else: st.error("Credenciais inválidas.")

# --- TELA PRINCIPAL ---
else:
    st.markdown("""<div style="background-color: #343a40; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                <h4 style="color: white; margin: 0;">PREFEITURA MUNICIPAL DE SALITRE</h4></div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("Menu Principal")
        if st.button("🏠 Home"): st.session_state.tela_atual = "Home"; st.rerun()
        
        with st.expander("📂 CADASTROS", expanded=True):
            # Lista de botões conforme sua imagem
            cadastros = [
                "Fornecedor", "Motorista", "Proprietário", "---",
                "Grupo", "Subgrupo", "Unidade de Medida", "Peças/Insumos", "---",
                "Cor", "Marca", "Modelo", "Combustível", "Veículo", "---",
                "Fonte de Recurso", "Unidade Gestora", "Unidade de Controle", "---",
                "Natureza da Entrada", "Natureza da Saída", "Tipo de Documento", "Modalidade de Compra"
            ]
            
            for item in cadastros:
                if item == "---":
                    st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)
                else:
                    if st.button(f"👤 {item}"):
                        st.session_state.tela_atual = item
                        st.rerun()

        st.divider()
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- RENDERIZAÇÃO DA TELA SELECIONADA ---
    if st.session_state.tela_atual == "Home":
        st.title("Bem-vindo, Marechal")
        st.write("Selecione uma opção no menu lateral para iniciar os cadastros da Prefeitura de Salitre.")
    else:
        tela_cadastro(st.session_state.tela_atual)
