import streamlit as st

# --- CONFIGURAÇÃO DA VITRINE ---
st.set_page_config(page_title="CUCK-HUB ELITE", layout="wide")

# Banco de Dados de Vídeos (Simulado para os seus 100 vídeos)
if 'acervo' not in st.session_state:
    st.session_state.acervo = [
        {"id": 1, "titulo": "Cuckold Realidade: O Encontro", "views": "15k", "likes": 450, "url": "link_do_video_1"},
        {"id": 2, "titulo": "Esposa VIP: Relato Amador", "views": "8k", "likes": 120, "url": "link_do_video_2"},
        # A lista cresce conforme você adiciona
    ]

# --- INTERFACE ESTILO GRADE (GRID) ---
st.title("🔞 ACERVO VIP: OS MAIS VISTOS")
st.write("---")

# Filtros de Busca
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    busca = st.text_input("🔍 Pesquisar no acervo de 100 vídeos...", placeholder="Ex: Amador, Realidade...")

# Exibição dos Vídeos
cols = st.columns(3) # 3 vídeos por linha para parecer o XV

for i, video in enumerate(st.session_state.acervo):
    with cols[i % 3]:
        with st.container(border=True):
            # Placeholder da Thumbnail (Capa)
            st.image("https://placehold.co/600x400/333/FFF?text=CUCKOLD+VIDEO", use_container_width=True)
            
            st.subheader(video["titulo"])
            
            c1, c2 = st.columns(2)
            c1.caption(f"👁️ {video['views']}")
            c2.caption(f"👍 {video['likes']} Likes")
            
            if st.button(f"▶️ ASSISTIR AGORA", key=f"play_{video['id']}", use_container_width=True):
                st.session_state.video_ativo = video
                st.rerun()

# --- PLAYER EXPANSÍVEL (QUANDO CLICA EM ASSISTIR) ---
if 'video_ativo' in st.session_state:
    st.divider()
    st.header(f"📺 Reproduzindo: {st.session_state.video_ativo['titulo']}")
    
    col_play, col_chat = st.columns([2, 1])
    
    with col_play:
        # Aqui entra o seu vídeo baixado ou o link direto
        st.video("https://www.w3schools.com/html/mov_bbb.mp4") 
        
        if st.button("❌ Fechar Player"):
            del st.session_state.video_ativo
            st.rerun()

    with col_chat:
        st.write("💬 **Comentários da Comunidade**")
        st.text_area("Deixe seu relato...", height=100)
        st.button("Publicar Comentário")
