import streamlit as st
import os
import yt_dlp

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SIM - Downloader Total", layout="centered")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# (O código de login permanece o mesmo)
if st.session_state.logado:
    st.title("🎥 Downloader de Alta Potência")
    st.write("Status: **Operacional** | Operador: **05772587374**")

    # Upload de Cookies (Essencial para sites adultos)
    cookie_file = st.file_uploader("Subir cookies.txt (Opcional, mas recomendado)", type=['txt'])
    
    url_input = st.text_input("Cole a URL do vídeo aqui:")

    if url_input and st.button("FORÇAR CAPTURA"):
        # 1. LIMPEZA TOTAL DA URL (Deixa apenas o link base)
        url = url_input.split('?')[0]
        
        video_path = "video_extraido.mp4"
        cookie_path = "cookies_temp.txt"

        if cookie_file:
            with open(cookie_path, "wb") as f:
                f.write(cookie_file.getbuffer())

        with st.spinner("Lutando contra a proteção do site..."):
            try:
                if os.path.exists(video_path): os.remove(video_path)

                ydl_opts = {
                    # FORMATO: Tenta MP4 primeiro, se não der, pega o melhor disponível
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': video_path,
                    'noplaylist': True,
                    # ESTA OPÇÃO É O SEGREDO: Força a tentativa mesmo em URLs 'não suportadas'
                    'check_formats': False, 
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'quiet': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }

                if cookie_file:
                    ydl_opts['cookiefile'] = cookie_path

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Tenta baixar
                    error_code = ydl.download([url])
                
                if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                    st.success("Derrubamos a trava! Vídeo processado.")
                    st.video(video_path)
                    with open(video_path, "rb") as f:
                        st.download_button("💾 Salvar no Dispositivo", f, "video_sim.mp4", "video/mp4")
                else:
                    st.error("O site bloqueou a extração direta. Verifique se o link está correto ou use um novo arquivo de cookies.")

            except Exception as e:
                st.error(f"Erro na extração: {str(e)}")
            
            finally:
                if os.path.exists(cookie_path): os.remove(cookie_path)

    if st.sidebar.button("Logout"):
        st.session_state.logado = False
        st.rerun()
