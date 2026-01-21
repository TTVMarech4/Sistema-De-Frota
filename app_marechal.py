import streamlit as st
import pandas as pd
import sqlite3
import io
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SISTEMA MARECHAL AI", page_icon="🤖", layout="wide")

db_path = 'sistema_marechal_nuvem.db'
conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
c = conn.cursor()

# Inicialização de Variáveis
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'df_processado' not in st.session_state: st.session_state.df_processado = None

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
    st.title("🛡️ PORTAL MARECHAL - COMANDO IA")
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
        st.write(f"👤 {st.session_state.usuario}")
        st.divider()
        if st.button("🏠 Início"): ir_para("Home")
        if st.button("🤖 IA de Planilhas"): ir_para("Gerar")
        if st.button("🏛️ Prefeituras"): ir_para("Adm_Pref")
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    if st.session_state.pagina == "Gerar":
        st.title("🤖 Processador Inteligente de Planilhas")
        
        arquivo = st.file_uploader("📂 Suba a planilha aqui", type=["xlsx", "csv"])
        
        if arquivo:
            # Carregar planilha original apenas uma vez
            df = pd.read_excel(arquivo) if arquivo.name.endswith('.xlsx') else pd.read_csv(arquivo)
            st.write("### Preview da Planilha Original:")
            st.dataframe(df.head(5))
            
            st.divider()
            comando = st.text_input("🤖 Marechal, o que devo fazer com esses dados?", placeholder="Ex: Deixe tudo em maiúsculo, troque 10 por 20, limpe os vazios...")
            
            if st.button("🚀 Executar Inteligência"):
                # CRIAMOS UMA CÓPIA PARA NÃO MEXER NA ORIGINAL
                df_temp = df.copy()
                cmd = comando.lower()
                
                with st.spinner("IA Processando..."):
                    # 1. Comando de Maiúsculas
                    if "maiúsculo" in cmd or "maiuscula" in cmd:
                        df_temp = df_temp.applymap(lambda x: x.upper() if isinstance(x, str) else x)
                        st.success("✅ Texto convertido!")

                    # 2. Comando de Limpeza (Vazios)
                    if "limpar" in cmd or "vazio" in cmd:
                        df_temp = df_temp.fillna("NÃO INFORMADO")
                        st.success("✅ Espaços vazios preenchidos!")

                    # 3. Comando de Substituição Inteligente (Ex: "troque X por Y")
                    if "troque" in cmd or "mude" in cmd or "substitua" in cmd:
                        try:
                            # Tenta extrair o que trocar (Lógica: troque VALOR1 por VALOR2)
                            partes = cmd.split(" por ")
                            alvo = partes[0].split(" ")[-1] # Pega a última palavra antes do 'por'
                            novo = partes[1]
                            df_temp = df_temp.replace(alvo, novo)
                            df_temp = df_temp.replace(alvo.upper(), novo.upper())
                            st.success(f"✅ Substituído '{alvo}' por '{novo}'!")
                        except:
                            st.error("Diga no formato: 'troque VALOR por NOVOVALOR'")

                    # 4. Comando de Cálculo (Ex: "somar 100")
                    if "somar" in cmd:
                        try:
                            num = float(''.join(filter(str.isdigit, cmd)))
                            cols_num = df_temp.select_dtypes(include=['number']).columns
                            df_temp[cols_num] = df_temp[cols_num] + num
                            st.success(f"✅ Adicionado {num} às colunas numéricas!")
                        except: pass

                    st.session_state.df_processado = df_temp
                    st.write("### ✅ Resultado da IA:")
                    st.dataframe(df_temp.head(10))

            # DOWNLOAD DO RESULTADO
            if st.session_state.df_processado is not None:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    st.session_state.df_processado.to_excel(writer, index=False)
                st.download_button("📥 BAIXAR PLANILHA PROCESSADA", output.getvalue(), "resultado_ia.xlsx")

    # (Página de Prefeituras mantida para você não perder o controle)
    elif st.session_state.pagina == "Adm_Pref":
        st.title("🏛️ Administração")
        nova = st.text_input("Nova Prefeitura")
        if st.button("Salvar"):
            c.execute("INSERT OR IGNORE INTO prefeituras VALUES (?)", (nova,))
            conn.commit()
            st.success("Salvo!")
            st.rerun()
