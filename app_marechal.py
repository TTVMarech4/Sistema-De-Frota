import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA CENTRAL ---
st.set_page_config(page_title="FitAI - Coach Digital", layout="wide", page_icon="💪")

# Inicialização do Banco de Dados de Evolução
if 'historico' not in st.session_state:
    st.session_state.historico = []

# --- SIDEBAR: PERFIL DO USUÁRIO ---
with st.sidebar:
    st.header("👤 Perfil Físico")
    nome = st.text_input("Nome Completo", "Marechal")
    peso = st.number_input("Peso Atual (kg)", min_value=30.0, max_value=250.0, value=80.0)
    altura = st.number_input("Altura (m)", min_value=1.0, max_value=2.5, value=1.75)
    idade = st.number_input("Idade", min_value=12, max_value=100, value=25)
    objetivo = st.selectbox("Objetivo", ["Perda de Gordura", "Ganho de Massa (Bulking)", "Manutenção / Definição"])
    
    # Cálculo automático de IMC
    imc = peso / (altura ** 2)
    st.metric("Seu IMC", f"{imc:.2f}")

# --- CORPO PRINCIPAL ---
st.title(f"🚀 Bem-vindo ao FitAI, {nome}!")

tabs = st.tabs(["📋 Minha Dieta", "🏋️ Meu Treino", "📈 Evolução", "🤖 Falar com IA Coach"])

# --- ABA 1: DIETA GERADA ---
with tabs[0]:
    st.subheader("🍎 Plano Alimentar Inteligente")
    if st.button("Gerar Nova Dieta com IA"):
        with st.spinner("IA calculando macros..."):
            # Aqui simulamos a resposta da IA baseada nos dados do sidebar
            st.success("Dieta Gerada!")
            st.markdown(f"""
            ### Sugestão para {objetivo}:
            * **Café da Manhã:** 3 ovos mexidos + 1 fruta.
            * **Almoço:** 150g de proteína + 200g de carboidrato limpo + salada.
            * **Jantar:** Proteína leve + legumes à vontade.
            """)

# --- ABA 2: TREINO ---
with tabs[1]:
    st.subheader("💪 Ficha de Treino Personalizada")
    nivel = st.select_slider("Nível de Experiência", options=["Iniciante", "Intermediário", "Avançado"])
    frequencia = st.slider("Dias por semana", 1, 7, 5)
    
    if st.button("Montar Cronograma"):
        st.info(f"Gerando treino {nivel} para {frequencia} dias na semana...")
        # Exemplo de tabela de treino
        df_treino = pd.DataFrame({
            "Exercício": ["Supino Reto", "Agachamento", "Puxada Alta", "Rosca Direta"],
            "Séries": [4, 4, 3, 3],
            "Repetições": ["10-12", "8-10", "12", "15"]
        })
        st.table(df_treino)

# --- ABA 3: EVOLUÇÃO ---
with tabs[2]:
    st.subheader("📊 Acompanhamento de Resultados")
    col1, col2 = st.columns(2)
    with col1:
        nova_medida = st.number_input("Registrar novo peso hoje:", value=peso)
        if st.button("Salvar Medida"):
            st.session_state.historico.append({"Data": datetime.now().strftime("%d/%m/%y"), "Peso": nova_medida})
    
    if st.session_state.historico:
        df_hist = pd.DataFrame(st.session_state.historico)
        st.line_chart(df_hist.set_index("Data"))

# --- ABA 4: IA COACH (CHATBOT) ---
with tabs[3]:
    st.subheader("💬 Converse com seu Treinador IA")
    msg = st.chat_input("Ex: Posso trocar o arroz por batata doce?")
    if msg:
        st.chat_message("user").write(msg)
        st.chat_message("assistant").write(f"Como seu Coach, vejo que seu objetivo é {objetivo}. Sim, você pode trocar, desde que mantenha a mesma proporção de carboidratos...")
