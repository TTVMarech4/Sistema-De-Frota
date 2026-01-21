import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Frota - Salitre", layout="wide")

# --- BANCO DE DADOS ---
db_path = 'frota_salitre_v21.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

# Criar tabelas básicas e de sistema
c.execute('CREATE TABLE IF NOT EXISTS usuarios (cpf TEXT PRIMARY KEY, senha TEXT)')
c.execute("INSERT OR IGNORE INTO usuarios VALUES ('05772587374', '1234')")

# Função para criar tabelas complexas automaticamente se não existirem
def inicializar_banco():
    # Tabelas com múltiplos campos baseadas nas suas fotos
    c.execute('''CREATE TABLE IF NOT EXISTS fornecedor (codigo INTEGER PRIMARY KEY AUTOINCREMENT, 
                 nome TEXT, tipo TEXT, cpf_cnpj TEXT, logradouro TEXT, numero TEXT, bairro TEXT, cep TEXT, email TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS motorista (codigo INTEGER PRIMARY KEY AUTOINCREMENT, 
                 nome TEXT, cpf TEXT, logradouro TEXT, cnh_numero TEXT, cnh_validade TEXT, cnh_categoria TEXT, email TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pecas_insumos (codigo INTEGER PRIMARY KEY AUTOINCREMENT, 
                 descricao TEXT, unidade TEXT, grupo TEXT, estoque_min REAL, estoque_atual REAL, valor_custo REAL)''')
    
    # Tabelas simples (apenas código e nome)
    simples = ['cor', 'marca', 'modelo', 'grupo', 'subgrupo', 'combustivel', 'veiculo', 'unidade_medida']
    for t in simples:
        c.execute(f'CREATE TABLE IF NOT EXISTS {t} (codigo INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)')
    conn.commit()

inicializar_banco()

# --- ESTADOS ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'tela_atual' not in st.session_state: st.session_state.tela_atual = "Home"

# --- INTERFACE DE LOGIN ---
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>Frota</h1>", unsafe_allow_html=True)
    with st.container():
        _, col_login, _ = st.columns([1,1,1])
        with col_login:
            cpf = st.text_input("CPF")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                c.execute("SELECT * FROM usuarios WHERE cpf=? AND senha=?", (cpf, senha))
                if c.fetchone():
                    st.session_state.logado = True
                    st.rerun()
                else: st.error("Erro no login")

# --- SISTEMA APÓS LOGIN ---
else:
    # Cabeçalho
    st.markdown("""<div style='background-color:#343a40; padding:10px; color:white; border-top:5px solid #28a745;'>
                PREFEITURA MUNICIPAL DE SALITRE</div>""", unsafe_allow_html=True)

    # MENU LATERAL (Exatamente como na sua imagem)
    with st.sidebar:
        st.title("Menu")
        with st.expander("📂 CADASTROS", expanded=True):
            cad_list = ["Fornecedor", "Motorista", "Proprietário", "---", 
                        "Grupo", "Subgrupo", "Unidade de Medida", "Peças/Insumos", "---",
                        "Cor", "Marca", "Modelo", "Combustível", "Veículo"]
            for item in cad_list:
                if item == "---": st.divider()
                elif st.button(item, key=item): 
                    st.session_state.tela_atual = item
                    st.rerun()

    # --- LÓGICA DE TELAS ESPECÍFICAS ---
    t = st.session_state.tela_atual
    
    if t == "Home":
        st.subheader("Bem-vindo ao Sistema de Gestão de Frota")
        st.write("Selecione um item no menu para cadastrar.")

    # 1. TELA DE FORNECEDOR (Baseada na Foto)
    elif t == "Fornecedor":
        st.header("Cadastro :: Fornecedor")
        with st.form("form_forn"):
            col1, col2, col3 = st.columns([1, 3, 2])
            col1.text_input("Código", disabled=True, placeholder="Automático")
            nome = col2.text_input("Nome *")
            cpf_cnpj = col3.text_input("CPF / CNPJ *")
            
            col4, col5 = st.columns([4, 1])
            logra = col4.text_input("Logradouro")
            num = col5.text_input("Número")
            
            col6, col7, col8 = st.columns(3)
            bairro = col6.text_input("Bairro")
            cep = col7.text_input("CEP")
            email = col8.text_input("Email")
            
            if st.form_submit_button("💾 Salvar"):
                c.execute("INSERT INTO fornecedor (nome, cpf_cnpj, logradouro, numero, bairro, cep, email) VALUES (?,?,?,?,?,?,?)",
                          (nome, cpf_cnpj, logra, num, bairro, cep, email))
                conn.commit()
                st.success("Fornecedor Salvo!")

    # 2. TELA DE MOTORISTA (Baseada na Foto)
    elif t == "Motorista":
        st.header("Cadastro :: Motorista")
        with st.form("form_moto"):
            col1, col2, col3 = st.columns([1, 3, 2])
            col1.text_input("Código", disabled=True)
            nome = col2.text_input("Nome *")
            cpf = col3.text_input("CPF *")
            
            st.write("--- Habilitação ---")
            c1, c2, c3 = st.columns(3)
            num_cnh = c1.text_input("Número CNH")
            val_cnh = c2.date_input("Validade")
            cat_cnh = c3.selectbox("Categoria", ["A", "B", "C", "D", "E", "AB"])
            
            if st.form_submit_button("💾 Salvar"):
                c.execute("INSERT INTO motorista (nome, cpf, cnh_numero, cnh_validade, cnh_categoria) VALUES (?,?,?,?,?)",
                          (nome, cpf, num_cnh, str(val_cnh), cat_cnh))
                conn.commit()
                st.success("Motorista Salvo!")

    # 3. TELA DE PEÇAS/INSUMOS (Baseada na Foto)
    elif t == "Peças/Insumos":
        st.header("Cadastro :: Peças/Insumos")
        with st.form("form_pecas"):
            desc = st.text_input("Descrição *")
            c1, c2, c3 = st.columns(3)
            und = c1.selectbox("Unidade", ["Litro", "Unidade", "Kg", "Peça"])
            grp = c2.text_input("Grupo")
            est_min = c3.number_input("Estoque Mínimo", value=0.0)
            
            if st.form_submit_button("💾 Salvar"):
                c.execute("INSERT INTO pecas_insumos (descricao, unidade, grupo, estoque_min) VALUES (?,?,?,?)",
                          (desc, und, grp, est_min))
                conn.commit()
                st.success("Item Salvo!")

    # 4. TELAS SIMPLES (Cor, Marca, Modelo, etc)
    else:
        st.header(f"Cadastro :: {t}")
        with st.form(f"form_{t}"):
            col_id, col_nome = st.columns([1, 5])
            col_id.text_input("Código", disabled=True, placeholder="Auto")
            nome_simples = col_nome.text_input(f"Nome da {t} *")
            
            if st.form_submit_button("💾 Salvar"):
                tab_name = t.lower().replace(" ", "_")
                c.execute(f"INSERT INTO {tab_name} (nome) VALUES (?)", (nome_simples,))
                conn.commit()
                st.success(f"{t} salva com sucesso!")

    # MOSTRAR TABELA DE BUSCA NO FINAL DE CADA TELA
    if t != "Home":
        st.divider()
        st.subheader(f"Lista de {t}s (Pesquisa por Código)")
        tab_search = t.lower().replace(" ", "_")
        try:
            df = pd.read_sql(f"SELECT * FROM {tab_search}", conn)
            st.dataframe(df, use_container_width=True)
        except: st.write("Nenhum dado encontrado.")
