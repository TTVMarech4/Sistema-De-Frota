import streamlit as st
import os
import yt_dlp
import re

# --- CONFIGURAÇÃO DE SEGURANÇA ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🛡️ SIM - ACESSO MILITAR")
    u = st.text_input("USUÁRIO")
    p = st.text_input("SENHA", type="password")
    if st.button("AUTENTICAR"):
        if u == "05772587374" and p == "1234":
            st.session_state.logado = True
            st.rerun()
else:
    st.title("🤖 AI SESSION HIJACKER")
    st.write("Status: **Ataque de Cookies Ativo**")

    # CAMPO PARA COLAR OS COOKIES DIRETAMENTE (MAIS RÁPIDO QUE ARQUIVO)
    cookie_raw = st.text_area("Cole aqui o texto do seu COOKIE (Injeção Direta):", 
                             placeholder="ex: user_id=123; sess_id=abc; ...", height=100)
    
    url = st.text_input("URL do Vídeo Protegido:")

    if st.button("QUEBRAR DEFESA E EXTRAIR"):
        if not cookie_raw:
            st.warning("⚠️ Sem os cookies, a barreira de IP dificilmente cairá.")
        
        video_file = "payload_video.mp4"
        if os.path.exists(video_file): os.remove(video_file)

        with st.spinner("🤖 IA simulando sua sessão no servidor..."):
            try:
                # O TRUQUE DA IA: Converte texto de cookie em arquivo que o motor entende
                cookie_path = "session_inject.txt"
                if cookie_raw:
                    # Formata o cookie para o padrão Netscape que o yt-dlp exige
                    # Ou tenta passar via header direto (mais agressivo)
                    with open(cookie_path, "w") as f:
                        f.write(cookie_raw)

                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': video_file,
                    'quiet': False,
                    'no_warnings': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'nocheckcertificate': True,
                    # INJEÇÃO DE COOKIES VIA STRING (AI BYPASS)
                }

                if cookie_raw:
                    # Tenta injetar os cookies via header customizado caso o arquivo falhe
                    ydl_opts['http_headers'] = {
                        'Cookie': cookie_raw,
                        'Referer': url.split('com')[0] + 'com/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists(video_file) and os.path.getsize(video_file) > 0:
                    st.success("✅ SUCESSO! Barreira de IP ignorada via Cookie Injection.")
                    st.video(video_file)
                    with open(video_file, "rb") as f:
                        st.download_button("💾 BAIXAR AGORA", f, "video_blindado.mp4", "video/mp4")
                else:
                    st.error("❌ A barreira física de IP é absoluta. O site detectou que o Cookie veio de um IP diferente do seu.")
                    st.info("💡 Solução Final: Você precisa baixar o vídeo em 'Localhost' (seu PC) usando este mesmo código.")

            except Exception as e:
                st.error(f"Erro no Sequestro de Sessão: {str(e)}")

    if st.sidebar.button("LOGOUT"):
        st.session_state.logado = False
        st.rerun()
