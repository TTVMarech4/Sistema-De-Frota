import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA CENTRAL ---
st.set_page_config(page_title="PORTAL VIP", layout="wide")

# Criar pasta de acervo se não existir para evitar erros de diretório
LIBRARY_DIR = "acervo_vids"
if not os.path.exists(LIBRARY_DIR):
    os.makedirs(LIBRARY_DIR)

# --- 2. SISTEMA DE SEGURANÇA (LOGIN) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

def login():
    # Corrigido: unsafe_allow_html=True
    st.markdown("<h1 style='text-align: center;'>🔐 ACESSO RESTRITO</h1>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            st.write("---")
            u = st.text_input("Operador", placeholder="Digite seu CPF ou Usuário")
            p = st.text_input("Senha de Comando", type="password")
            if st.button("DESBLOQUEAR PORTAL", use_container_width=True):
                # Suas credenciais mantidas
                if u == "05772587374" and p == "1234":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas. Acesso negado.")

# --- 3. O SITE COMPLETO (SÓ APARECE APÓS LOGIN) ---
if not st.session_state.auth:
    login()
else:
    # Cabeçalho do Site
    st.title("🔥 PORTAL CUCKOLD VIP")
    st.sidebar.write(f"Sessão Ativa: **Operador 05772587374**")
    
    # Menu lateral para navegação do site
    menu = st.sidebar.radio("Navegação", ["📺 Galeria de Vídeos", "📤 Adicionar Conteúdo", "⚙️ Painel Admin"])

    # ABA 1: GALERIA (O CORAÇÃO DO SITE)
    if menu == "📺 Galeria de Vídeos":
        st.subheader("🎬 Acervo de Filmes")
        videos = [f for f in os.listdir(LIBRARY_DIR) if f.endswith(('.mp4', '.mkv', '.mov'))]
        
        if not videos:
            st.warning("Nenhum vídeo no acervo. Vá em 'Adicionar Conteúdo'.")
        else:
            # Grade de exibição
            cols = st.columns(2) # 2 vídeos por linha para dar destaque
            for i, vid in enumerate(videos):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.write(f"**🎞️ {vid}**")
                        st.video(os.path.join(LIBRARY_DIR, vid))
                        if st.button(f"Excluir", key=f"del_{vid}"):
                            os.remove(os.path.join(LIBRARY_DIR, vid))
                            st.rerun()

    # ABA 2: ADICIONAR CONTEÚDO
    elif menu == "📤 Adicionar Conteúdo":
        st.subheader("Importar Novo Material")
        
        # Upload manual
        up_file = st.file_uploader("Subir vídeo do dispositivo", type=['mp4', 'mov'])
        if up_file:
            with open(os.path.join(LIBRARY_DIR, up_file.name), "wb") as f:
                f.write(up_file.getbuffer())
            st.success("Vídeo adicionado com sucesso!")
            
        st.write("---")
        st.info("💡 Para adicionar vídeos de sites externos, use o seu Robô CMD e depois faça o upload aqui.")

    # ABA 3: ADMINISTRAÇÃO
    elif menu == "⚙️ Painel Admin":
        st.subheader("Configurações do Servidor")
        if st.button("🗑️ LIMPAR TODO O ACERVO"):
            for f in os.listdir(LIBRARY_DIR):
                os.remove(os.path.join(LIBRARY_DIR, f))
            st.success("Acervo resetado.")
            st.rerun()

    if st.sidebar.button("Sair (Logout)"):
        st.session_state.auth = False
        st.rerun()
