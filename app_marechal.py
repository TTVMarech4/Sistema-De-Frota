import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- TESTE DE DEPENDÊNCIAS ---
try:
    import openpyxl
    import xlsxwriter
except ImportError:
    st.error("🚨 ERRO CRÍTICO: Ferramentas de Excel não instaladas. Verifique o arquivo requirements.txt no seu GitHub.")

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SISTEMA MARECHAL GOV", page_icon="🛡️", layout="wide")

db_path = 'sistema_marechal_nuvem.db'
conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
c = conn.cursor()

# Inicialização de Variáveis de Sessão
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"

# Criação de Tabelas
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
    st.title("🛡️ PORTAL DE GESTÃO MUNICIPAL")
    c.execute("SELECT nome FROM prefeituras")
    lista_pref = [p[0] for p in c.fetchall()]
    lista_pref.insert(0, "Gestão Central (ADM)")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pref_sel = st.selectbox("Selecione a jurisdição:", lista_pref)
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

# --- SISTEMA ---
else:
    with st.sidebar:
        st.title("🛡️ MENU")
        st.write(f"👤 **{st.session_state.usuario}**")
        st.write(f"🏢 **{st.session_state.pref_atual}**")
        st.divider()
        if st.button("🏠 Início"): ir_para("Home")
        if st.button("📊 1. Gerar/Alterar Planilha"): ir_para("Gerar")
        if st.button("⛽ 2. Abastecimentos"): ir_para("Abast")
        if st.button("📈 4. Dashboard"): ir_para("Dash")
        
        if st.session_state.nivel == "ADM":
            st.divider()
            if st.button("🏛️ Gestão de Prefeituras"): ir_para("Adm_Pref")
            if st.button("👥 Cadastro de Equipe"): ir_para("Adm_User")
        
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- LÓGICA DE GERAR/ALTERAR PLANILHA ---
    if st.session_state.pagina == "Gerar":
        st.title("📊 Inteligência de Planilhas")
        arquivo = st.file_uploader("Importar Planilha", type=["xlsx", "csv"])
        
        if arquivo:
            try:
                df = pd.read_excel(arquivo) if arquivo.name.endswith('.xlsx') else pd.read_csv(arquivo)
                st.success("Planilha lida!")
                st.write("Colunas detectadas:", list(df.columns))
                
                col_sel = st.selectbox("Alterar qual coluna?", ["Nenhuma"] + list(df.columns))
                if col_sel != "Nenhuma":
                    novo_val = st.text_input(f"Novo valor para {col_sel}:")
                    if st.button("Aplicar"):
                        df[col_sel] = novo_val
                        st.dataframe(df.head())
                
                # Botão de Exportar
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 DOWNLOAD PLANILHA CORRIGIDA", output.getvalue(), "planilha_corrigida.xlsx")
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
