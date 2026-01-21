import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="MARECHAL COMMAND CENTER", page_icon="🛡️", layout="wide")

# Conexão segura
db_path = 'sistema_marechal_nuvem.db'
conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
c = conn.cursor()

# Inicialização de Estado
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'df_trabalho' not in st.session_state: st.session_state.df_trabalho = None

# Tabelas
c.execute('CREATE TABLE IF NOT EXISTS usuarios (nome TEXT PRIMARY KEY, senha TEXT, nivel TEXT, prefeitura TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS prefeituras (nome TEXT PRIMARY KEY)')
c.execute("INSERT OR IGNORE INTO prefeituras (nome) VALUES ('Prefeitura Municipal de Salitre')")
c.execute("INSERT OR IGNORE INTO usuarios VALUES ('Marechal', '12345Agario', 'ADM', 'ADMINISTRAÇÃO CENTRAL')")
conn.commit()

# --- INTERFACE DE ACESSO ---
if not st.session_state.logado:
    st.title("🛡️ PORTAL MARECHAL v20.0")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("Operador")
        s = st.text_input("Senha", type="password")
        if st.button("🔓 ACESSAR"):
            c.execute("SELECT nivel, prefeitura FROM usuarios WHERE nome=? AND senha=?", (u, s))
            res = c.fetchone()
            if res:
                st.session_state.logado, st.session_state.usuario = True, u
                st.session_state.nivel, st.session_state.pref_atual = res[0], res[1]
                st.rerun()
            else: st.error("Acesso negado.")

# --- SISTEMA ---
else:
    with st.sidebar:
        st.title("🕹️ COMANDO")
        st.write(f"Operador: {st.session_state.usuario}")
        st.divider()
        if st.button("🏠 Início"): st.session_state.pagina = "Home"; st.rerun()
        if st.button("🤖 IA e Planilhas"): st.session_state.pagina = "IA"; st.rerun()
        if st.button("🏛️ Gestão ADM"): st.session_state.pagina = "ADM"; st.rerun()
        if st.button("🚪 Sair"): st.session_state.logado = False; st.rerun()

    if st.session_state.pagina == "IA":
        st.title("🤖 Cérebro de Processamento de Dados")
        
        arquivo = st.file_uploader("📂 Importar Planilha para o Sistema", type=["xlsx", "csv"])
        
        if arquivo:
            if st.session_state.df_trabalho is None:
                if arquivo.name.endswith('.xlsx'):
                    st.session_state.df_trabalho = pd.read_excel(arquivo)
                else:
                    st.session_state.df_trabalho = pd.read_csv(arquivo)

            st.subheader("🛠️ Editor em Tempo Real")
            st.info("Dica: Você pode editar qualquer célula abaixo clicando nela, ou usar o comando de IA.")
            
            # EDITOR INTERATIVO (O usuário pode mudar qualquer coisa na mão)
            df_editado = st.data_editor(st.session_state.df_trabalho, num_rows="dynamic", use_container_width=True)
            st.session_state.df_trabalho = df_editado

            st.divider()
            
            # COMANDO DE IA GLOBAL
            st.subheader("🧠 Comando Rápido da IA")
            col_cmd, col_btn = st.columns([3,1])
            with col_cmd:
                comando = st.text_input("Ex: Troque 'Ativo' por 'Inativo', mude tudo para maiúsculo, limpe zeros...")
            with col_btn:
                if st.button("🚀 EXECUTAR"):
                    cmd = comando.lower()
                    df_temp = st.session_state.df_trabalho.copy()
                    
                    if "maiúsculo" in cmd or "maiuscula" in cmd:
                        df_temp = df_temp.applymap(lambda x: str(x).upper() if isinstance(x, str) else x)
                    
                    if "troque" in cmd or "substitua" in cmd:
                        try:
                            # Tenta pegar "troque A por B"
                            partes = cmd.split(" por ")
                            alvo = partes[0].split(" ")[-1].strip()
                            novo = partes[1].strip()
                            # Substitui em qualquer lugar da planilha
                            df_temp = df_temp.astype(str).replace(alvo, novo)
                            # Tenta também a versão em maiúsculo
                            df_temp = df_temp.replace(alvo.upper(), novo.upper())
                        except: st.error("Use o formato: troque X por Y")
                    
                    st.session_state.df_trabalho = df_temp
                    st.rerun()

            # DOWNLOAD
            st.divider()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                st.session_state.df_trabalho.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 BAIXAR PLANILHA FINAL",
                data=output.getvalue(),
                file_name="processado_marechal.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            if st.button("🗑️ Limpar e Subir Outra"):
                st.session_state.df_trabalho = None
                st.rerun()

    elif st.session_state.pagina == "Home":
        st.header(f"Bem-vindo à Gestão Central - {st.session_state.pref_atual}")
        st.write("Selecione a ferramenta de IA no menu para começar o tratamento de dados.")

    elif st.session_state.pagina == "ADM":
        st.title("🏛️ Administração")
        n_pref = st.text_input("Nova Prefeitura")
        if st.button("Cadastrar"):
            c.execute("INSERT OR IGNORE INTO prefeituras VALUES (?)", (n_pref,))
            conn.commit()
            st.success("Registrado!")
