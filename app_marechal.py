import streamlit as st
import pandas as pd
import sqlite3
import os
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SISTEMA MARECHAL GOV", page_icon="🛡️", layout="wide")

# --- CONEXÃO COMPATÍVEL COM NUVEM (GITHUB/STREAMLIT) ---
# Aqui mudamos para um caminho simples que funciona no servidor
db_path = 'sistema_marechal_nuvem.db'

def conectar_bd():
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
    # Ativa modo de escrita rápida para evitar travamentos
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

conn = conectar_bd()
c = conn.cursor()

# --- INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'usuario' not in st.session_state: st.session_state.usuario = ""
if 'nivel' not in st.session_state: st.session_state.nivel = "USER"
if 'pref_atual' not in st.session_state: st.session_state.pref_atual = ""

# --- CRIAÇÃO DAS TABELAS NO SERVIDOR ---
c.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY, senha TEXT, nivel TEXT, prefeitura TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS prefeituras (nome TEXT PRIMARY KEY)')
c.execute("INSERT OR IGNORE INTO prefeituras (nome) VALUES ('Prefeitura Municipal de Salitre')")
c.execute("INSERT OR IGNORE INTO usuarios (nome, senha, nivel, prefeitura) VALUES (?,?,?,?)", 
          ('Marechal', '12345Agario', 'ADM', 'ADMINISTRAÇÃO CENTRAL'))
conn.commit()

def ir_para(p):
    st.session_state.pagina = p
    st.rerun()

# --- TELA DE ACESSO (LOGIN) ---
if not st.session_state.logado:
    st.title("🛡️ PORTAL DE GESTÃO MUNICIPAL")
    
    c.execute("SELECT nome FROM prefeituras")
    lista_pref = [p[0] for p in c.fetchall()]
    lista_pref.insert(0, "Gestão Central (ADM)")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Login Jurisdicional")
        escolha_pref = st.selectbox("Selecione a jurisdição:", lista_pref)
        u_in = st.text_input("Usuário").strip()
        s_in = st.text_input("Senha", type="password").strip()
        
        if st.button("🔓 ENTRAR NO SISTEMA"):
            c.execute("SELECT nivel, prefeitura FROM usuarios WHERE nome=? AND senha=?", (u_in, s_in))
            res = c.fetchone()
            if res:
                if res[0] == "ADM" or res[1] == escolha_pref:
                    st.session_state.logado = True
                    st.session_state.usuario = u_in
                    st.session_state.nivel = res[0]
                    st.session_state.pref_atual = escolha_pref
                    st.rerun()
                else: st.error(f"Seu usuário não tem permissão para a {escolha_pref}.")
            else: st.error("Credenciais inválidas.")

# --- INTERFACE PRINCIPAL ---
else:
    with st.sidebar:
        st.title("🛡️ MENU MARECHAL")
        st.write(f"👤 **{st.session_state.usuario}**")
        st.write(f"🏢 **Jurisdição:** {st.session_state.pref_atual}")
        st.divider()
        
        if st.sidebar.button("🏠 Início"): ir_para("Home")
        if st.sidebar.button("📊 1. Gerar Planilha"): ir_para("Gerar")
        if st.sidebar.button("⛽ 2. Abastecimentos"): ir_para("Abast")
        if st.sidebar.button("⚙️ 3. Peças (PDF)"): ir_para("Pecas")
        if st.sidebar.button("📉 4. Dashboard"): ir_para("Dash")
        
        if st.session_state.nivel == "ADM":
            st.divider()
            st.subheader("👑 COMANDO ADM")
            if st.sidebar.button("🏛️ Gestão de Prefeituras"): ir_para("Adm_Pref")
            if st.sidebar.button("👥 Cadastro de Equipe"): ir_para("Adm_User")
        
        st.divider()
        if st.sidebar.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- LÓGICA DAS PÁGINAS ---
    p = st.session_state.pagina

    if p == "Home":
        st.title(f"Jurisdição: {st.session_state.pref_atual}")
        st.success("Sistema operacional na nuvem. Acesse pelo celular com o mesmo link.")

    elif p == "Gerar":
        st.title("📊 Gerador de Planilhas")
        st.text_area("Exemplo da planilha:")
        st.button("Configurar")

    elif p == "Abast":
        st.title("⛽ Gestão de Abastecimento")
        st.file_uploader("Importar Planilhas (Excel)", accept_multiple_files=True)

    elif p == "Pecas":
        st.title("⚙️ Extração de Peças (PDF)")
        st.file_uploader("Subir Notas Fiscais", type=["pdf"], accept_multiple_files=True)

    elif p == "Dash":
        st.title("📈 Dashboard de Gastos")
        st.bar_chart(pd.DataFrame({'Custo': [12000, 15000, 13500]}, index=['Nov', 'Dez', 'Jan']))

    elif p == "Adm_Pref":
        st.title("🏛️ Administração de Prefeituras")
        nova = st.text_input("Nome da Prefeitura")
        if st.button("Salvar"):
            c.execute("INSERT OR IGNORE INTO prefeituras VALUES (?)", (nova,))
            conn.commit()
            st.success("Adicionada!")
            st.rerun()

    elif p == "Adm_User":
        st.title("👥 Cadastro de Equipe")
        c.execute("SELECT nome FROM prefeituras")
        prefs = [row[0] for row in c.fetchall()]
        n_u = st.text_input("Nome")
        n_s = st.text_input("Senha")
        n_p = st.selectbox("Vincular à Prefeitura:", prefs)
        if st.button("Confirmar Cadastro"):
            c.execute("INSERT OR REPLACE INTO usuarios (nome, senha, nivel, prefeitura) VALUES (?,?,'USER',?)", (n_u, n_s, n_p))
            conn.commit()
            st.success(f"Funcionário {n_u} cadastrado!")
