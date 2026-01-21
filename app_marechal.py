import streamlit as st
import os
import yt_dlp

# --- LOGIN ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🛡️ ACESSO RESTRITO")
    u = st.text_input("USUÁRIO")
    if st.button("ENTRAR") and u == "05772587374":
        st.session_state.logado = True
        st.rerun()
else:
    st.title("🤖 AI BRUTE FORCE EXTRACTOR")
    st.warning("MODO AGRESSIVO: Forçando extração de URL não suportada.")

    cookie_raw = st.text_area("Injeção de Cookie (Opcional):", placeholder="Cole o cookie aqui...")
    url_raw = st.text_input("URL do Vídeo:")

    if st.button("FORÇAR QUEBRA DE PROTOCOLO"):
        # IA de Limpeza: Remove o lixo do final da URL que causa o erro
        url = url_raw.split('?')[0]
        
        video_out = "force_capture.mp4"
        if os.path.exists(video_out): os.remove(video_out)

        with st.spinner("🤖 IA simulando navegador e capturando tráfego bruto..."):
            try:
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': video_out,
                    # O SEGREDO: Força o yt-dlp a tratar como link genérico
                    'force_generic_extractor': True, 
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'quiet': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }

                if cookie_raw:
                    ydl_opts['http_headers'] = {'Cookie': cookie_raw}

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Tenta extrair e baixar na marra
                    ydl.download([url])

                if os.path.exists(video_out) and os.path.getsize(video_out) > 0:
                    st.success("✅ IA EXTRAIU O VÍDEO BRUTO!")
                    st.video(video_out)
                    with open(video_out, "rb") as f:
                        st.download_button("💾 SALVAR AGORA", f, "video_raw.mp4", "video/mp4")
                else:
                    st.error("❌ Erro: O site usa criptografia de fragmentos (HLS/Dash) que o servidor não consegue unir sem o FFmpeg.")
                    st.info("💡 Marechal, o servidor do Streamlit é limitado. Para esses links pesados, você deve rodar no seu PC.")

            except Exception as e:
                st.error(f"Falha Crítica: {str(e)}")

    if st.sidebar.button("LOGOUT"):
        st.session_state.logado = False
        st.rerun()
