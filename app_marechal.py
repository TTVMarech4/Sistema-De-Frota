import streamlit as st
import pandas as pd
import sqlite3
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Frota - Sistema de Gestão", layout="wide")

# --- BANCO DE DADOS (ESTRUTURA COMPLETA) ---
db_path = 'sistema_marechal_fiel.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

def setup_db():
    # Tabelas baseadas nas imagens
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (cpf TEXT PRIMARY KEY, senha TEXT)')
    c.execute("INSERT OR IGNORE INTO usuarios VALUES ('05772587374', '1234')")
    
    # Veículo Completo
    c.execute('''CREATE TABLE IF NOT EXISTS veiculo (
                 codigo INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, placa TEXT, 
                 renavam TEXT, chassi TEXT, ano_fabricacao TEXT, ano_modelo TEXT, 
                 cor TEXT, marca TEXT, modelo TEXT, combustivel TEXT, situacao TEXT)''')
    
    # Motorista Completo
    c.execute('''CREATE TABLE IF NOT EXISTS motorista (
                 codigo INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT, 
                 rg TEXT, cnh_numero TEXT, cnh_validade TEXT, cnh_categoria TEXT, telefone TEXT)''')
    
    # Tabelas Simples (Código, Descrição, Sigla)
    for t in ['cor', 'marca', 'modelo', 'combustivel', 'grupo', 'subgrupo', 'unidade_medida']:
        c.execute(f'CREATE TABLE IF NOT EXISTS {t} (codigo INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, sigla TEXT)')
    conn.commit()

setup_db()

# --- CSS PARA FIDELIDADE VISUAL ---
st.markdown("""
    <style>
    /* Topo do site */
    header[data-testid="stHeader"] { background-color: #343a40; border-top: 5px solid #28a745; }
    /* Menu Lateral */
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
    .menu-divider { border-top: 1px solid #bbb; margin: 10px 0; }
    /* Inputs */
    .stTextInput>div>div>input { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGAÇÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'tela' not in st.session_state: st.session_state.tela = "Home"

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #d93043;'>Frota</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>entre para iniciar a sessão</p>", unsafe_allow_html=True)
        cpf_log = st.text_input("CPF")
        pass_log = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            c.execute("SELECT * FROM usuarios WHERE cpf=? AND senha=?", (cpf_log, pass_log))
            if c.fetchone():
                st.session_state.logado = True
                st.rerun()
            else: st.error("Acesso Negado")

# --- TELA PRINCIPAL (100% FIEL) ---
else:
    st.markdown("""<div style='background-color:#343a40; padding:12px; color:white; font-weight:bold;'>
                PREFEITURA MUNICIPAL DE SALITRE</div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("Menu Principal")
        with st.expander("📂 CADASTROS", expanded=True):
            # Botões agrupados com divisores como na imagem original
            if st.button("Fornecedor"): st.session_state.tela = "Fornecedor"
            if st.button("Motorista"): st.session_state.tela = "Motorista"
            if st.button("Proprietário"): st.session_state.tela = "Proprietário"
            st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)
            
            if st.button("Grupo"): st.session_state.tela = "Grupo"
            if st.button("Subgrupo"): st.session_state.tela = "Subgrupo"
            if st.button("Unidade de Medida"): st.session_state.tela = "Unidade de Medida"
            if st.button("Peças/Insumos"): st.session_state.tela = "Peças/Insumos"
            st.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)
            
            if st.button("Cor"): st.session_state.tela = "Cor"
            if st.button("Marca"): st.session_state.tela = "Marca"
            if st.button("Modelo"): st.session_state.tela = "Modelo"
            if st.button("Combustível"): st.session_state.tela = "Combustível"
            if st.button("Veículo"): st.session_state.tela = "Veículo"
        
        st.divider()
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- FORMULÁRIOS DETALHADOS ---
    t = st.session_state.tela
    
    if t == "Home":
        st.subheader("Bem-vindo ao Sistema de Gestão - Salitre")
        st.info("Utilize o menu lateral para acessar os formulários de cadastro.")

    elif t == "Veículo":
        st.subheader("Cadastro :: Veículo")
        with st.form("form_veic"):
            c1, c2, c3 = st.columns([1, 4, 2])
            c1.text_input("Código", placeholder="Novo", disabled=True)
            desc = c2.text_input("Descrição *")
            placa = c3.text_input("Placa *")
            
            c4, c5, c6 = st.columns(3)
            renavam = c4.text_input("Renavam")
            chassi = c5.text_input("Chassi")
            situacao = c6.selectbox("Situação", ["Ativo", "Inativo", "Manutenção"])
            
            c7, c8, c9, c10 = st.columns(4)
            afab = c7.text_input("Ano Fab.")
            amod = c8.text_input("Ano Mod.")
            cor_v = c9.text_input("Cor")
            marca_v = c10.text_input("Marca")
            
            if st.form_submit_button("Salvar"):
                c.execute("INSERT INTO veiculo (descricao, placa, renavam, chassi, ano_fabricacao, ano_modelo, cor, marca, situacao) VALUES (?,?,?,?,?,?,?,?,?)",
                          (desc, placa, renavam, chassi, afab, amod, cor_v, marca_v, situacao))
                conn.commit()
                st.success("Registrado!")

    elif t in ["Cor", "Marca", "Modelo", "Combustível"]:
        st.subheader(f"Cadastro :: {t}")
        with st.form("form_simples"):
            c1, c2, c3 = st.columns([1, 4, 1])
            c1.text_input("Código", placeholder="Novo", disabled=True)
            nome = c2.text_input("Descrição *")
            sigla = c3.text_input("Sigla")
            if st.form_submit_button("Salvar"):
                tab = t.lower().replace(" ", "_")
                c.execute(f"INSERT INTO {tab} (nome, sigla) VALUES (?,?)", (nome, sigla))
                conn.commit()
                st.success("Salvo!")

    elif t == "Motorista":
        st.subheader("Cadastro :: Motorista")
        with st.form("form_moto"):
            c1, c2, c3 = st.columns([1, 3, 2])
            c1.text_input("Código", placeholder="Novo", disabled=True)
            nome = c2.text_input("Nome *")
            cpf = c3.text_input("CPF *")
            
            c4, c5, c6 = st.columns(3)
            rg = c4.text_input("RG")
            cnh = c5.text_input("Nº CNH")
            cat = c6.text_input("Cat. CNH")
            
            if st.form_submit_button("Salvar"):
                c.execute("INSERT INTO motorista (nome, cpf, rg, cnh_numero, cnh_categoria) VALUES (?,?,?,?,?)",
                          (nome, cpf, rg, cnh, cat))
                conn.commit()
                st.success("Motorista Salvo!")

    # EXIBIÇÃO DA TABELA (BUSCA POR CÓDIGO)
    if t != "Home":
        st.divider()
        st.write(f"### Pesquisa de {t}")
        tab_name = t.lower().replace(" ", "_")
        try:
            df = pd.read_sql(f"SELECT * FROM {tab_name}", conn)
            st.dataframe(df, use_container_width=True)
        except: pass
