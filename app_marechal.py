import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA CENTRAL ---
st.set_page_config(page_title="PORTAL CUCKOLD - VIP", layout="wide", initial_sidebar_state="collapsed")

# Criar pasta de acervo se não existir
LIBRARY_DIR = "acervo_vids"
if not os.path.exists(LIBRARY_DIR):
    os.makedirs(LIBRARY_DIR)

# --- 2. SISTEMA DE SEGURANÇA (LOGIN) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔐 ACESSO RESTRITO</h1>", unsafe_allow_stdio=True)
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            u = st.text_input("Operador", placeholder="Digite seu CPF ou Usuário")
            p = st.text_input("Senha de Comando", type="password")
            if st.button("DESBLOQUEAR PORTAL", use_container_width=True):
                if u == "05772587374" and p == "1234": # Configure sua senha aqui
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas.")

# --- 3. O SITE COMPLETO ---
if not st.session_state.auth:
    login()
else:
    # Cabeçalho do Site
    st.title("🔥 PORTAL CUCKOLD VIP")
    st.write(f"Bem-vindo, Operador **05772587374**")
    
    tabs = st.tabs(["📺 Galeria de Vídeos", "📥 Upload/Captura", "⚙️ Configurações"])

    # ABA 1: O SITE (VISÃO DO USUÁRIO)
    with tabs[0]:
        st.subheader("Filmes Recentes")
        videos = [f for f in os.listdir(LIBRARY_DIR) if f.endswith(('.mp4', '.mkv', '.mov'))]
        
        if not videos:
            st.info("O acervo está vazio. Use a aba de Captura para adicionar vídeos.")
        else:
            # Cria uma grade de vídeos (3 por linha)
            cols = st.columns(3)
            for i, vid in enumerate(videos):
                with cols[i % 3]:
                    st.write(f"**{vid.replace('.mp4', '')}**")
                    st.video(os.path.join(LIBRARY_DIR, vid))
                    st.button(f"Remover {i}", key=f"del_{i}", help="Deletar vídeo")

    # ABA 2: FERRAMENTA DE ABASTECIMENTO
    with tabs[1]:
        st.subheader("Capturar Novo Conteúdo")
        # Aqui você pode integrar o código de download anterior
        st.info("Integre aqui o seu robô V36 para baixar direto para a pasta 'acervo_vids'")
        
        uploaded_file = st.file_uploader("Ou suba um vídeo do seu PC:", type=['mp4'])
        if uploaded_file is not None:
            with open(os.path.join(LIBRARY_DIR, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Vídeo adicionado ao acervo!")

    # ABA 3: ADMINISTRAÇÃO
    with tabs[2]:
        if st.button("LIMPAR TODO O SITE"):
            for f in os.listdir(LIBRARY_DIR):
                os.remove(os.path.join(LIBRARY_DIR, f))
            st.rerun()
        
        if st.sidebar.button("LOGOUT"):
            st.session_state.auth = False
            st.rerun()
