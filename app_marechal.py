import streamlit as st
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA CENTRAL ---
st.set_page_config(page_title="CUCKOLD SOCIAL - VIP", layout="wide")

# Inicialização do Banco de Dados Virtual (Simulado)
if 'db_social' not in st.session_state:
    st.session_state.db_social = {
        "videos": {
            "Video_Exemplo_1.mp4": {"likes": 150, "views": 1200, "comments": []},
        },
        "perfis": {
            "05772587374": {"nome": "Marechal", "bio": "Administrador Geral", "posts": 0}
        }
    }

# --- 2. SISTEMA DE SEGURANÇA ---
if 'auth' not in st.session_state: st.session_state.auth = False

def login():
    st.markdown("<h1 style='text-align: center;'>🔞 ACESSO CUCKOLD SOCIAL</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("ENTRAR NA REDE", use_container_width=True):
                if u == "05772587374" and p == "1234":
                    st.session_state.auth = True
                    st.rerun()

# --- 3. INTERFACE SOCIAL (ESTILO XV) ---
if not st.session_state.auth:
    login()
else:
    # --- BARRA SUPERIOR (ESTILO SITE ADULTO) ---
    col_logo, col_search, col_perfil = st.columns([1, 2, 1])
    with col_logo:
        st.subheader("🔥 CUCK-HUB")
    with col_search:
        st.text_input("", placeholder="Pesquisar vídeos, categorias ou perfis...", label_visibility="collapsed")
    with col_perfil:
        if st.button(f"👤 Perfil: {st.session_state.db_social['perfis']['05772587374']['nome']}"):
            st.toast("Acessando suas configurações de perfil...")

    st.write("---")

    # --- MENU LATERAL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.write(f"**@Marechal**")
        menu = st.radio("MENU", ["📺 Home (Mais Vistos)", "⭐ Favoritos", "👥 Comunidade", "📤 Subir Vídeo"])

    # --- CONTEÚDO PRINCIPAL ---
    if menu == "📺 Home (Mais Vistos)":
        st.title("📹 Vídeos Mais Vistos de Cuckold")
        
        # Simulando lista de vídeos (Aqui entrariam os que você baixou)
        vids = list(st.session_state.db_social["videos"].keys())
        
        for v in vids:
            with st.container(border=True):
                col_vid, col_info = st.columns([2, 1])
                
                with col_vid:
                    # Botão de Reprodução incorporado no st.video
                    st.video("https://www.w3schools.com/html/mov_bbb.mp4") # Exemplo: Substituir pelo caminho local
                
                with col_info:
                    st.subheader(v.replace("_", " "))
                    st.write(f"👁️ {st.session_state.db_social['videos'][v]['views']} visualizações")
                    
                    # Sistema de Likes
                    if st.button(f"👍 Like ({st.session_state.db_social['videos'][v]['likes']})", key=f"like_{v}"):
                        st.session_state.db_social['videos'][v]['likes'] += 1
                        st.rerun()
                    
                    st.write("---")
                    st.write("**Comentários:**")
                    for comm in st.session_state.db_social['videos'][v]['comments']:
                        st.caption(f"💬 {comm}")
                    
                    new_comm = st.text_input("Adicionar comentário...", key=f"input_{v}")
                    if st.button("Enviar", key=f"btn_{v}"):
                        st.session_state.db_social['videos'][v]['comments'].append(new_comm)
                        st.rerun()

    elif menu == "📤 Subir Vídeo":
        st.subheader("📤 Central de Upload")
        with st.form("upload_form"):
            titulo = st.text_input("Título do Vídeo")
            tags = st.multiselect("Categorias", ["Amador", "Realidade", "Relato", "Esposa VIP"])
            arquivo = st.file_uploader("Escolha o arquivo MP4", type=["mp4"])
            if st.form_submit_button("PUBLICAR NO SITE"):
                if arquivo and titulo:
                    # Lógica para salvar e adicionar ao banco virtual
                    st.session_state.db_social["videos"][f"{titulo}.mp4"] = {"likes": 0, "views": 0, "comments": []}
                    st.success("Vídeo publicado com sucesso na rede!")
