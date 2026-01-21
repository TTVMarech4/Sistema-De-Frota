import streamlit as st
import yt_dlp
import os

# --- CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(page_title="SIM - Downloader", layout="centered")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- CSS ESTILO CLEAN ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .main-card { background: white; padding: 30px; border-radius: 10px; border-top: 5px solid #3c8dbc; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("login_sim"):
            st.markdown("<h2 style='text-align:center;'>SIM LOGIN</h2>", unsafe_allow_html=True)
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR"):
                if u == "05772587374" and p == "1234":
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Acesso negado")

# --- INTERFACE DE DOWNLOAD ---
else:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("🎥 Video Downloader & Player")
    st.write(f"Conectado como: **05772587374**")
    
    url = st.text_input("Cole o link do vídeo aqui (YouTube, Instagram, etc):", placeholder="https://www.youtube.com/watch?v=...")

    if url:
        if st.button("PROCESSAR VÍDEO"):
            with st.spinner("Extraindo vídeo..."):
                try:
                    # Configuração para baixar o vídeo
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': 'video_baixado.%(ext)s', # Nome temporário
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        
                        st.success(f"Vídeo encontrado: **{info.get('title')}**")
                        
                        # Opção para Assistir
                        st.subheader("📺 Assistir no Site")
                        st.video(filename)
                        
                        # Opção para Baixar
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="💾 Baixar Arquivo para o PC",
                                data=file,
                                file_name=filename,
                                mime="video/mp4"
                            )
                except Exception as e:
                    st.error(f"Erro ao processar link: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
