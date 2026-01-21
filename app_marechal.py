import streamlit as st
import pandas as pd
import sqlite3
import os
import io

# --- CONFIGURAÇÃO E CONEXÃO BLINDADA (FORA DO ONEDRIVE) ---
st.set_page_config(page_title="SISTEMA MARECHAL GOV v13.0", page_icon="🛡️", layout="wide")

db_path = os.path.join(os.environ['LOCALAPPDATA'], 'sistema_marechal_final.db')

def conectar_bd():
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=60)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

conn = conectar_bd()
c = conn.cursor()

# --- INICIALIZAÇÃO DE VARIÁVEIS ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"

# --- CONFIGURAÇÃO DE TABELAS ---
c.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY, senha TEXT, nivel TEXT, prefeitura TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS prefeituras (nome TEXT PRIMARY KEY)')
c.execute("INSERT OR IGNORE INTO prefeituras (nome) VALUES ('Prefeitura Municipal de Salitre')")
c.execute("INSERT OR IGNORE INTO usuarios (nome, senha, nivel, prefeitura) VALUES (?,?,?,?)", 
          ('Marechal', '12345Agario', 'ADM', 'ADMINISTRAÇÃO CENTRAL'))
conn.commit()

def ir_para(p):
    st.session_state.pagina = p
    st.rerun()

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("🛡️ PORTAL DE GESTÃO MUNICIPAL - ACESSO RESTRITO")
    
    c.execute("SELECT nome FROM prefeituras")
    lista_pref = [p[0] for p in c.fetchall()]
    lista_pref.insert(0, "Gestão Central (ADM)")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Login de Operador")
        escolha_pref = st.selectbox("Selecione a jurisdição:", lista_pref)
        u_in = st.text_input("Usuário").strip()
        s_in = st.text_input("Senha", type="password").strip()
        
        if st.button("🔓 ENTRAR NO SISTEMA"):
            c.execute("SELECT nivel, prefeitura FROM usuarios WHERE nome=? AND senha=?", (u_in, s_in))
            res = c.fetchone()
            if res:
                # O ADM pode entrar em qualquer prefeitura. O USER só na dele.
                if res[0] == "ADM" or res[1] == escolha_pref:
                    st.session_state.logado = True
                    st.session_state.usuario = u_in
                    st.session_state.nivel = res[0]
                    st.session_state.pref_atual = escolha_pref
                    st.rerun()
                else: st.error(f"Seu usuário não tem permissão para a {escolha_pref}.")
            else: st.error("Credenciais inválidas.")

# --- INTERFACE PRINCIPAL ---
else:
    with st.sidebar:
        st.title("🛡️ MENU MARECHAL")
        st.write(f"👤 **{st.session_state.usuario}** ({st.session_state.nivel})")
        st.write(f"🏢 **Jurisdição:** {st.session_state.pref_atual}")
        st.divider()
        
        # Opções para Todos os Usuários
        if st.sidebar.button("🏠 Início"): ir_para("Home")
        if st.sidebar.button("📊 1. Gerar Planilha"): ir_para("Gerar")
        if st.sidebar.button("⛽ 2. Abastecimentos"): ir_para("Abast")
        if st.sidebar.button("⚙️ 3. Peças (PDF)"): ir_para("Pecas")
        if st.sidebar.button("📉 4. Dashboard"): ir_para("Dash")
        
        # Opções Exclusivas do ADM (Marechal)
        if st.session_state.nivel == "ADM":
            st.divider()
            st.subheader("👑 GESTÃO SUPREMA")
            if st.sidebar.button("🏛️ Criar/Remover Prefeituras"): ir_para("Adm_Pref")
            if st.sidebar.button("👥 Cadastrar Operadores"): ir_para("Adm_User")
        
        st.divider()
        if st.sidebar.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- LÓGICA DAS PÁGINAS ---
    p = st.session_state.pagina

    if p == "Home":
        st.title(f"Bem-vindo à Gestão de {st.session_state.pref_atual}")
        st.info("Sistema operando em modo seguro. Selecione um módulo no menu lateral.")

    elif p == "Gerar":
        st.title("📊 Gerador de Planilhas Automático")
        st.text_area("Exemplo da planilha para espelhamento:")
        st.text_input("Campos de atualização obrigatória:")
        st.button("Configurar Automação")

    elif p == "Abast":
        st.title("⛽ Gestão de Abastecimento e Consumo")
        st.write("Análise por Data, Ano e Tipo de Combustível (Gasolina/Diesel).")
        st.file_uploader("Importar Planilhas de Frota", accept_multiple_files=True)
        # Exemplo de Resumo que o usuário verá
        st.subheader("Resumo Mensal por Combustível")
        st.table(pd.DataFrame({'Combustível': ['Diesel', 'Gasolina'], 'Total (L)': [0, 0]}))

    elif p == "Pecas":
        st.title("⚙️ Extração de Notas Fiscais (PDF)")
        st.write("O sistema lerá Descrição, Unidade e Valor Unitário.")
        st.file_uploader("Arraste os arquivos PDF aqui", type=["pdf"], accept_multiple_files=True)
        st.button("Iniciar Extração Estratégica")

    elif p == "Dash":
        st.title("📈 Dashboard de Inteligência Governamental")
        st.bar_chart(pd.DataFrame({'Gasto': [12000, 15000, 13500]}, index=['Nov', 'Dez', 'Jan']))
        st.download_button("📥 Download Relatório Completo (Excel)", data=b"", file_name="dashboard.xlsx")

    elif p == "Adm_Pref":
        st.title("🏛️ Controle de Jurisdições")
        col_c, col_r = st.columns(2)
        with col_c:
            st.subheader("Cadastrar")
            nova = st.text_input("Nome da Prefeitura")
            if st.button("Salvar Prefeitura"):
                c.execute("INSERT OR IGNORE INTO prefeituras VALUES (?)", (nova,))
                conn.commit()
                st.success(f"{nova} adicionada!")
                st.rerun()
        with col_r:
            st.subheader("Remover")
            c.execute("SELECT nome FROM prefeituras")
            prefs = [row[0] for row in c.fetchall()]
            remover = st.selectbox("Selecione para excluir:", prefs)
            if st.button("❌ EXCLUIR PREFEITURA"):
                c.execute("DELETE FROM prefeituras WHERE nome=?", (remover,))
                conn.commit()
                st.warning(f"{remover} removida do sistema.")
                st.rerun()

    elif p == "Adm_User":
        st.title("👥 Gestão de Operadores e Vínculos")
        c.execute("SELECT nome FROM prefeituras")
        prefs_disp = [row[0] for row in c.fetchall()]
        
        n_u = st.text_input("Nome do Operador")
        n_s = st.text_input("Senha")
        n_p = st.selectbox("Vincular à Prefeitura:", prefs_disp)
        n_v = st.radio("Nível de Acesso:", ["USER", "ADM"])
        
        if st.button("💾 Gravar Novo Operador"):
            c.execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (n_u, n_s, n_v, n_p))
            conn.commit()
            st.success(f"Operador {n_u} vinculado à {n_p} com sucesso!")
