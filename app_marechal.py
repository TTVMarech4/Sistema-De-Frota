import streamlit as st
import os
import time

# --- TENTA IMPORTAR A BIBLIOTECA ---
try:
    import yt_dlp
    YDL_AVAILABLE = True
except ImportError:
    YDL_AVAILABLE = False

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SIM - Downloader Pro", layout="centered")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- LOGIN ---
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
        st.error("⚠️ Biblioteca yt-dlp não instalada no requirements.txt")
    else:
        url = st.text_input("Cole o link (YouTube, Shorts, Instagram):", placeholder="https://...")

        if url:
            if st.button("BAIXAR E ASSISTIR"):
                # Limpa arquivos antigos para não dar conflito
                if os.path.exists("temp_video.mp4"):
                    os.remove("temp_video.mp4")

                with st.spinner("Bypassing links... isso pode levar um momento."):
                    try:
                        # OPÇÕES AVANÇADAS PARA EVITAR ARQUIVO VAZIO
                        ydl_opts = {
                            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                            'outtmpl': 'temp_video.mp4',
                            'noplaylist': True,
                            'quiet': True,
                            'no_warnings': True,
                            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            # Tenta extrair info primeiro
                            info = ydl.extract_info(url, download=True)
                            
                        # Verifica se o arquivo foi realmente criado e tem conteúdo
                        if os.path.exists("temp_video.mp4") and os.path.getsize("temp_video.mp4") > 0:
                            st.success(f"Vídeo: {info.get('title', 'Sucesso')}")
                            
                            # Player
                            st.video("temp_video.mp4")
                            
                            # Botão de Download
                            with open("temp_video.mp4", "rb") as f:
                                st.download_button(
                                    label="💾 Salvar no Computador",
                                    data=f,
                                    file_name="video_sim_baixado.mp4",
                                    mime="video/mp4"
                                )
                        else:
                            st.error("O servidor do site bloqueou o download direto. Tente outro link ou vídeo mais curto.")
                            
                    except Exception as e:
                        st.error(f"Erro técnico: {str(e)}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
