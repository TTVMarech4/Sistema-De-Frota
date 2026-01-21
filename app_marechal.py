import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- CONFIGURAÇÃO VISUAL DA PÁGINA ---
st.set_page_config(page_title="Frota - Login", page_icon="🚗", layout="centered")

# CSS para replicar exatamente o visual da sua imagem
st.markdown("""
    <style>
    .main {
        background-color: #e6e6e6;
    }
    .stApp {
        background-color: #e6e6e6;
    }
    .login-box {
        background-color: white;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .title-frota {
        color: #d93043;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .subtitle-login {
        color: #333;
        font-size: 18px;
        margin-bottom: 30px;
    }
    div.stButton > button {
        background-color: #d93043;
        color: white;
        width: 100%;
        border-radius: 5px;
        height: 45px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DATOS (ZERA TUDO E RECOMEÇA) ---
db_path = 'sistema_marechal_v2.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

# Criação das tabelas limpas
c.execute('DROP TABLE IF EXISTS usuarios')
c.execute('DROP TABLE IF EXISTS prefeituras')
c.execute('CREATE TABLE usuarios (cpf TEXT PRIMARY KEY, senha TEXT, nivel TEXT, prefeitura TEXT)')
c.execute('CREATE TABLE prefeituras (nome TEXT PRIMARY KEY)')

# CADASTRO INICIAL DO MARECHAL (Conforme solicitado)
c.execute("INSERT INTO usuarios VALUES ('05772587374', '1234', 'ADM', 'ADMINISTRAÇÃO CENTRAL')")
c.execute("INSERT INTO prefeituras VALUES ('Prefeitura de Salitre')")
conn.commit()

# --- ESTADOS DO SISTEMA ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Login"

# --- TELA DE LOGIN (DESIGN FIEL À IMAGEM) ---
if not st.session_state.logado:
    # Centralização manual na tela
    _, col_central, _ = st.columns([1, 2, 1])
    
    with col_central:
        st.markdown('<div class="title-frota" style="text-align: center;">Frota</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle-login" style="text-align: center;">entre para iniciar a sessão</div>', unsafe_allow_html=True)
        
        cpf_input = st.text_input("", placeholder="CPF", label_visibility="collapsed")
        senha_input = st.text_input("", placeholder="Senha", type="password", label_visibility="collapsed")
        
        # Alinhamento do botão à direita como na imagem
        col_btn_1, col_btn_2 = st.columns([2, 1])
        with col_btn_2:
            if st.button("Entrar"):
                c.execute("SELECT nivel, prefeitura FROM usuarios WHERE cpf=? AND senha=?", (cpf_input, senha_input))
                user = c.fetchone()
                if user:
                    st.session_state.logado = True
                    st.session_state.nivel = user[0]
                    st.session_state.pref_atual = user[1]
                    st.session_state.pagina = "Home"
                    st.rerun()
                else:
                    st.error("CPF ou Senha incorretos.")

# --- INTERFACE PÓS-LOGIN (ESTRUTURA INICIAL) ---
else:
    st.sidebar.title("🛡️ Sistema Marechal")
    st.sidebar.write(f"Nível: **{st.session_state.nivel}**")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

    if st.session_state.pagina == "Home":
        st.title("Bem-vindo ao Novo Comando")
        st.info("O sistema foi zerado e está pronto para receber as novas funções.")
        
        # Aqui vamos construir as opções que você quiser de novo.
