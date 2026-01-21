import streamlit as st
import os
import yt_dlp

# --- CONFIGURAÇÃO DE SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- INTERFACE ---
if not st.session_state.logado:
    # (Mantenha seu código de login aqui)
    st.title("Acesso Restrito")
    u = st.text_input("Operador")
    if st.button("Entrar") and u == "05772587374":
        st.session_state.logado = True
        st.rerun()

else:
    st.title("🎥 Downloader Pro - Modo Bypass")
    st.write("Operador: 05772587374")

    # 1. ÁREA DE COOKIES (O segredo para não dar erro)
    st.info("Passo 1: No seu navegador, use a extensão 'Get cookies.txt' no site do vídeo e suba o arquivo aqui.")
    cookie_file = st.file_uploader("Upload cookies.txt", type=['txt'])
    
    # 2. ÁREA DO LINK
    url = st.text_input("Passo 2: Cole o link do vídeo:")

    if url and st.button("BAIXAR AGORA"):
        cookie_path = "cookies_temp.txt"
        video_path = "video_baixado.mp4"
        
        # Se você subiu os cookies, o sistema salva e usa eles
        if cookie_file:
            with open(cookie_path, "wb") as f:
                f.write(cookie_file.getbuffer())

        with st.spinner("Derrubando proteção do site..."):
            try:
                if os.path.exists(video_path): os.remove(video_path)

                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': video_path,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }

                # ATIVA OS COOKIES SE DISPONÍVEIS
                if cookie_file:
                    ydl_opts['cookiefile'] = cookie_path

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
                    st.success("Vídeo capturado com sucesso!")
                    st.video(video_path)
                    with open(video_path, "rb") as f:
                        st.download_button("💾 Salvar no PC", f, "video.mp4", "video/mp4")
                else:
                    st.error("O site bloqueou o servidor mesmo com os cookies.")

            except Exception as e:
                st.error(f"Falha técnica: {str(e)}")
            
            # Limpa os cookies após o uso por segurança
            if os.path.exists(cookie_path): os.remove(cookie_path)
