import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SISTEMA MARECHAL AI", page_icon="🛡️", layout="wide")

db_path = 'sistema_marechal_nuvem.db'
conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
c = conn.cursor()

# Inicialização de Variáveis
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"

# Tabelas
c.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY, senha TEXT, nivel TEXT, prefeitura TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS prefeituras (nome TEXT PRIMARY KEY)')
c.execute("INSERT OR IGNORE INTO prefeituras (nome) VALUES ('Prefeitura Municipal de Salitre')")
c.execute("INSERT OR IGNORE INTO usuarios VALUES ('Marechal', '12345Agario', 'ADM', 'ADMINISTRAÇÃO CENTRAL')")
conn.commit()

def ir_para(p):
    st.session_state.pagina = p
    st.rerun()

# --- LOGIN ---
if not st.session_state.logado:
    st.title("🛡️ PORTAL MARECHAL - IA INTEGRADA")
    c.execute("SELECT nome FROM prefeituras")
    lista_pref = [p[0] for p in c.fetchall()]
    lista_pref.insert(0, "Gestão Central (ADM)")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pref_sel = st.selectbox("Jurisdição", lista_pref)
        u_in = st.text_input("Usuário").strip()
        s_in = st.text_input("Senha", type="password").strip()
        if st.button("🔓 ENTRAR"):
            c.execute("SELECT nivel, prefeitura FROM usuarios WHERE nome=? AND senha=?", (u_in, s_in))
            res = c.fetchone()
            if res and (res[0] == "ADM" or res[1] == pref_sel):
                st.session_state.logado, st.session_state.usuario = True, u_in
                st.session_state.nivel, st.session_state.pref_atual = res[0], pref_sel
                st.rerun()
            else: st.error("Acesso negado.")

# --- SISTEMA COM IA ---
else:
    with st.sidebar:
        st.title("🛡️ COMANDO AI")
        st.write(f"👤 **{st.session_state.usuario}**")
        st.write(f"🏢 **{st.session_state.pref_atual}**")
        st.divider()
        if st.button("🏠 Início"): ir_para("Home")
        if st.button("🤖 1. IA de Planilhas"): ir_para("Gerar")
        if st.button("⛽ 2. Abastecimentos"): ir_para("Abast")
        if st.button("📈 4. Dashboard"): ir_para("Dash")
        
        if st.session_state.nivel == "ADM":
            st.divider()
            if st.button("🏛️ Gestão de Prefeituras"): ir_para("Adm_Pref")
            if st.button("👥 Cadastro de Equipe"): ir_para("Adm_User")
        
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- MÓDULO DE IA DE PLANILHAS ---
    if st.session_state.pagina == "Gerar":
        st.title("🤖 Inteligência Artificial de Dados")
        st.write("Suba sua planilha e dê ordens diretas para a IA processar.")
        
        arquivo = st.file_uploader("📂 Importar Arquivo", type=["xlsx", "csv"])
        
        if arquivo:
            df = pd.read_excel(arquivo) if arquivo.name.endswith('.xlsx') else pd.read_csv(arquivo)
            st.success("✅ Planilha carregada e escaneada pela IA.")
            
            st.subheader("🧠 Comando à IA do Marechal")
            comando = st.text_input("O que você quer que eu faça na planilha?", placeholder="Ex: Formate a coluna Data ou Calcule o total da coluna Valor...")
            
            if st.button("🚀 Executar Comando"):
                with st.spinner("Processando dados com inteligência..."):
                    try:
                        # Lógica de processamento de comandos comuns (IA Heurística)
                        if "maiúsculo" in comando.lower():
                            df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)
                            st.toast("Texto convertido para maiúsculo!")
                        
                        elif "limpar" in comando.lower():
                            df = df.fillna(0)
                            st.toast("Valores vazios limpos!")
                        
                        elif "data" in comando.lower():
                            for col in df.columns:
                                if "data" in col.lower():
                                    df[col] = pd.to_datetime(df[col]).dt.strftime('%d/%m/%Y')
                            st.toast("Datas formatadas!")

                        st.session_state['df_ai'] = df
                        st.write("### ✅ Resultado do Processamento")
                        st.dataframe(df.head(10))
                    except Exception as e:
                        st.error(f"Erro no processamento da IA: {e}")

            # Download do resultado da IA
            if 'df_ai' in st.session_state:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    st.session_state['df_ai'].to_excel(writer, index=False)
                st.download_button("📥 BAIXAR PLANILHA PROCESSADA PELA IA", output.getvalue(), "ia_marechal_final.xlsx")

    # (Home e Adm continuam as mesmas)
    elif st.session_state.pagina == "Home":
        st.title(f"Bem-vindo, Marechal.")
        st.info("A IA está ativa no módulo 1. Pronta para processar planilhas de Salitre ou qualquer prefeitura.")
    
    elif st.session_state.pagina == "Adm_Pref":
        st.title("🏛️ Controle de Prefeituras")
        n = st.text_input("Nome da Prefeitura")
        if st.button("Salvar"):
            c.execute("INSERT OR IGNORE INTO prefeituras VALUES (?)", (n,))
            conn.commit()
            st.success("Adicionada!")
            st.rerun()
