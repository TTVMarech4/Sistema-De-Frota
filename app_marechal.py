import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SISTEMA MARECHAL GOV", page_icon="🛡️", layout="wide")

db_path = 'sistema_marechal_nuvem.db'
conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
c = conn.cursor()

# Inicialização de Variáveis
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"

# Tabelas Base
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
        pref_sel = st.selectbox("Jurisdição", lista_pref)
        u_in = st.text_input("Usuário")
        s_in = st.text_input("Senha", type="password")
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
        st.write(f"👤 {st.session_state.usuario} | 🏢 {st.session_state.pref_atual}")
        if st.button("🏠 Início"): ir_para("Home")
        if st.button("📊 1. Gerar/Alterar Planilha"): ir_para("Gerar")
        if st.button("⛽ 2. Abastecimentos"): ir_para("Abast")
        if st.button("⚙️ 3. Peças (PDF)"): ir_para("Pecas")
        if st.button("📉 4. Dashboard"): ir_para("Dash")
        if st.session_state.nivel == "ADM":
            st.divider()
            if st.button("🏛️ Gestão de Prefeituras"): ir_para("Adm_Pref")
            if st.button("👥 Cadastro de Equipe"): ir_para("Adm_User")
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- PÁGINA: GERAR / ALTERAR PLANILHA ---
    if st.session_state.pagina == "Gerar":
        st.title("📊 Inteligência e Manipulação de Planilhas")
        st.write("Importe sua planilha, escolha as alterações e exporte a versão final.")
        
        arquivo_subido = st.file_uploader("Importar Planilha (XLSX ou CSV)", type=["xlsx", "csv"])
        
        if arquivo_subido:
            # Lendo a planilha
            if arquivo_subido.name.endswith('.csv'):
                df = pd.read_csv(arquivo_subido)
            else:
                df = pd.read_excel(arquivo_subido)
            
            st.success("Planilha importada com sucesso!")
            st.write("### 🔍 Colunas detectadas na sua planilha:")
            st.info(f"Campos encontrados: {', '.join(df.columns)}")
            
            st.write("---")
            st.subheader("🛠️ O que você deseja alterar?")
            
            col_para_alterar = st.selectbox("Selecione a coluna que deseja modificar:", ["Nenhuma"] + list(df.columns))
            
            if col_para_alterar != "Nenhuma":
                tipo_alteracao = st.radio("Tipo de alteração:", ["Substituir Texto/Valor", "Somar Valor", "Limpar Coluna"])
                
                if tipo_alteracao == "Substituir Texto/Valor":
                    valor_antigo = st.text_input("Valor atual para buscar:")
                    valor_novo = st.text_input("Novo valor para inserir:")
                    if st.button("Aplicar Substituição"):
                        df[col_para_alterar] = df[col_para_alterar].replace(valor_antigo, valor_novo)
                        st.session_state['df_editado'] = df
                        st.success("Alteração aplicada!")

                elif tipo_alteracao == "Somar Valor":
                    valor_soma = st.number_input("Valor a ser somado em toda a coluna:", value=0.0)
                    if st.button("Aplicar Soma"):
                        df[col_para_alterar] = pd.to_numeric(df[col_para_alterar], errors='coerce') + valor_soma
                        st.session_state['df_editado'] = df
                        st.success("Soma aplicada!")

            st.write("### 📄 Prévia da Nova Planilha")
            st.dataframe(df.head(10))

            # EXPORTAR (Download)
            st.write("---")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Planilha_Marechal')
            
            st.download_button(
                label="📥 EXPORTAR PLANILHA ALTERADA (DOWNLOAD)",
                data=output.getvalue(),
                file_name="planilha_marechal_atualizada.xlsx",
                mime="application/vnd.ms-excel"
            )

    # (Outras páginas permanecem como antes para garantir funcionalidade)
    elif st.session_state.pagina == "Home":
        st.title(f"Jurisdição: {st.session_state.pref_atual}")
        st.write("Sistema operacional. Utilize o menu lateral para gerenciar os dados da prefeitura.")
    
    elif st.session_state.pagina == "Abast":
        st.title("⛽ Abastecimentos")
        st.file_uploader("Importar dados de combustível", accept_multiple_files=True)

    elif st.session_state.pagina == "Adm_Pref":
        st.title("🏛️ Administração de Prefeituras")
        nova = st.text_input("Nome da Nova Prefeitura")
        if st.button("Salvar"):
            c.execute("INSERT OR IGNORE INTO prefeituras VALUES (?)", (nova,))
            conn.commit()
            st.success("Adicionada!")
            st.rerun()
