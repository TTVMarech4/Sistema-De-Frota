import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SISTEMA MARECHAL GOV", page_icon="🛡️", layout="wide")

# Banco de dados persistente no servidor
db_path = 'sistema_marechal_nuvem.db'
conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
c = conn.cursor()

# Inicialização de Variáveis de Sessão
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"

# Criação de Tabelas (Executa apenas uma vez)
c.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY, senha TEXT, nivel TEXT, prefeitura TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS prefeituras (nome TEXT PRIMARY KEY)')
c.execute("INSERT OR IGNORE INTO prefeituras (nome) VALUES ('Prefeitura Municipal de Salitre')")
c.execute("INSERT OR IGNORE INTO usuarios VALUES ('Marechal', '12345Agario', 'ADM', 'ADMINISTRAÇÃO CENTRAL')")
conn.commit()

def ir_para(p):
    st.session_state.pagina = p
    st.rerun()

# --- TELA DE ACESSO ---
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

# --- INTERFACE LOGADA ---
else:
    with st.sidebar:
        st.title("🛡️ MENU")
        st.write(f"👤 **{st.session_state.usuario}**")
        st.write(f"🏢 **Jurisdição:** {st.session_state.pref_atual}")
        st.divider()
        if st.button("🏠 Início"): ir_para("Home")
        if st.button("📊 1. Gerar/Alterar Planilha"): ir_para("Gerar")
        if st.button("⛽ 2. Abastecimentos"): ir_para("Abast")
        if st.button("⚙️ 3. Peças (PDF)"): ir_para("Pecas")
        if st.button("📈 4. Dashboard"): ir_para("Dash")
        
        if st.session_state.nivel == "ADM":
            st.divider()
            st.subheader("👑 COMANDO ADM")
            if st.button("🏛️ Gestão de Prefeituras"): ir_para("Adm_Pref")
            if st.button("👥 Cadastro de Equipe"): ir_para("Adm_User")
        
        st.divider()
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- LÓGICA DE GERAR/ALTERAR PLANILHA ---
    if st.session_state.pagina == "Gerar":
        st.title("📊 Inteligência de Planilhas")
        st.info("O sistema fará o scan das colunas e permitirá edições estratégicas.")
        
        arquivo = st.file_uploader("Importar Planilha (XLSX ou CSV)", type=["xlsx", "csv"])
        
        if arquivo:
            try:
                # Tenta ler o arquivo
                if arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo, engine='openpyxl') # Define abertamente o motor
                
                st.success("Planilha lida com sucesso!")
                st.write("### 🔍 Colunas Encontradas:")
                st.code(", ".join(df.columns))
                
                # Interface de Alteração
                st.divider()
                col_edit, op_edit = st.columns(2)
                with col_edit:
                    col_selecionada = st.selectbox("Qual coluna alterar?", ["Selecione..."] + list(df.columns))
                with op_edit:
                    if col_selecionada != "Selecione...":
                        novo_valor = st.text_input(f"Novo valor para a coluna {col_selecionada}:")
                        if st.button("💡 Aplicar Alteração Geral"):
                            df[col_selecionada] = novo_valor
                            st.session_state['df_temp'] = df
                            st.toast("Alterado!")

                st.write("### 📄 Prévia dos Dados")
                st.dataframe(df.head(10))

                # Exportação
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 DOWNLOAD PLANILHA ALTERADA",
                    data=output.getvalue(),
                    file_name="planilha_marechal_corrigida.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

    # Demais páginas (mantidas para funcionamento total)
    elif st.session_state.pagina == "Home":
        st.title(f"Jurisdição: {st.session_state.pref_atual}")
        st.write("Bem-vindo ao comando central. Use o menu à esquerda.")
    
    elif st.session_state.pagina == "Adm_Pref":
        st.title("🏛️ Administração de Prefeituras")
        n = st.text_input("Nome da Nova Prefeitura")
        if st.button("Adicionar"):
            c.execute("INSERT OR IGNORE INTO prefeituras VALUES (?)", (n,))
            conn.commit()
            st.success("Adicionada!")
            st.rerun()

    elif st.session_state.pagina == "Adm_User":
        st.title("👥 Cadastro de Equipe")
        c.execute("SELECT nome FROM prefeituras")
        prefs = [r[0] for r in c.fetchall()]
        n_u = st.text_input("Nome")
        n_s = st.text_input("Senha")
        n_p = st.selectbox("Vincular à Prefeitura", prefs)
        if st.button("Confirmar"):
            c.execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,'USER',?)", (n_u, n_s, n_p))
            conn.commit()
            st.success("Cadastrado!")
