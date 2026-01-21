import streamlit as st
import os

# --- TENTA IMPORTAR A BIBLIOTECA DE DOWNLOAD ---
try:
    import yt_dlp
    YDL_AVAILABLE = True
except ImportError:
    YDL_AVAILABLE = False

# --- CONFIGURAÇÃO E SESSÃO ---
st.set_page_config(page_title="SIM - Downloader", layout="centered")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align:center;'>SIM LOGIN</h2>", unsafe_allow_html=True)
        with st.form("login_sim"):
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
    st.title("🎥 Video Downloader & Player")
    st.write(f"Operador: **05772587374**")
    
    if not YDL_AVAILABLE:
        st.error("⚠️ Erro: A biblioteca 'yt-dlp' não foi encontrada. Crie o arquivo 'requirements.txt' com o nome 'yt-dlp' dentro para funcionar.")
    else:
        url = st.text_input("Cole o link do vídeo aqui:", placeholder="https://...")

        if url:
            if st.button("BAIXAR E ASSISTIR"):
                with st.spinner("Processando... isso pode levar alguns segundos."):
                    try:
                        # Pasta temporária para o download
                        save_path = "video_temp.mp4"
                        
                        ydl_opts = {
                            'format': 'best',
                            'outtmpl': save_path,
                            'noplaylist': True,
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        
                        st.success("Vídeo pronto!")
                        
                        # Player de Vídeo
                        st.video(save_path)
                        
                        # Botão de Download para o PC
                        with open(save_path, "rb") as f:
                            st.download_button(
                                label="💾 Salvar no meu Computador",
                                data=f,
                                file_name="video_baixado.mp4",
                                mime="video/mp4"
                            )
                            
                    except Exception as e:
                        st.error(f"Erro ao baixar: {e}")

    if st.sidebar.button("Logout"):
        st.session_state.logado = False
        st.rerun()
