import streamlit as st
import os
import re

# --- TENTA IMPORTAR YT-DLP ---
try:
    import yt_dlp
    YDL_AVAILABLE = True
except ImportError:
    YDL_AVAILABLE = False

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SIM - Ultra Downloader", layout="centered")

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

# --- INTERFACE ---
else:
    st.title("🎥 Ultra Downloader Pro")
    st.info("Suporte para YouTube, Instagram, X, e outros sites de vídeo.")
    
    if not YDL_AVAILABLE:
        st.error("Instale 'yt-dlp' no seu arquivo requirements.txt")
    else:
        url_raw = st.text_input("Cole o link do vídeo aqui:", placeholder="https://...")

        if url_raw:
            if st.button("PROCESSAR E BAIXAR"):
                # 1. LIMPEZA DA URL (Remove lixo de rastreio)
                url = url_raw.split('?')[0]
                
                if os.path.exists("video_result.mp4"):
                    os.remove("video_result.mp4")

                with st.spinner("Quebrando protocolos de segurança..."):
                    try:
                        ydl_opts = {
                            # Tenta o melhor formato MP4 compatível
                            'format': 'best[ext=mp4]/best', 
                            'outtmpl': 'video_result.mp4',
                            'noplaylist': True,
                            # Opções para sites com bloqueio
                            'check_formats': True,
                            'ignoreerrors': False,
                            'logtostderr': False,
                            'quiet': True,
                            'no_warnings': True,
                            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        
                        if os.path.exists("video_result.mp4") and os.path.getsize("video_result.mp4") > 0:
                            st.success("Sucesso! O vídeo foi capturado.")
                            st.video("video_result.mp4")
                            
                            with open("video_result.mp4", "rb") as f:
                                st.download_button("💾 Salvar no Computador", f, "video_sim.mp4", "video/mp4")
                        else:
                            st.error("O site de origem bloqueou a extração ou a URL é inválida.")
                        
                    except Exception as e:
                        st.error("Erro: Este site específico possui uma proteção que impede o download direto pelo servidor.")
                        st.debug(str(e))

    if st.sidebar.button("Logout"):
        st.session_state.logado = False
        st.rerun()
