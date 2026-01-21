import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Frota Salitre - Gestão Completa", layout="wide")

# --- BANCO DE DADOS (Estrutura de Tabelas Específicas) ---
db_path = 'frota_salitre_v22.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

def inicializar_tabelas():
    # VEÍCULO (Campo por campo da imagem)
    c.execute('''CREATE TABLE IF NOT EXISTS veiculo (
                 codigo INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, placa TEXT, 
                 renavam TEXT, chassi TEXT, ano_fab TEXT, ano_mod TEXT, 
                 cor TEXT, marca TEXT, modelo TEXT, combustivel TEXT, situacao TEXT)''')
    
    # MOTORISTA (Completo)
    c.execute('''CREATE TABLE IF NOT EXISTS motorista (
                 codigo INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT, 
                 rg TEXT, cnh_numero TEXT, cnh_validade TEXT, cnh_categoria TEXT, 
                 telefone TEXT, endereco TEXT)''')

    # FORNECEDOR (Completo)
    c.execute('''CREATE TABLE IF NOT EXISTS fornecedor (
                 codigo INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, tipo TEXT, 
                 cpf_cnpj TEXT, insc_estadual TEXT, logradouro TEXT, numero TEXT, 
                 bairro TEXT, cep TEXT, cidade TEXT, telefone TEXT)''')

    # MARCA / MODELO / COR / COMBUSTÍVEL (Campos: Código, Nome, Sigla)
    tabelas_simples = ['marca', 'modelo', 'cor', 'combustivel', 'grupo', 'subgrupo', 'unidade_medida']
    for t in tabelas_simples:
        c.execute(f'CREATE TABLE IF NOT EXISTS {t} (codigo INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, sigla TEXT)')
    
    conn.commit()

inicializar_tabelas()

# --- LOGIN PADRÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'tela' not in st.session_state: st.session_state.tela = "Home"

if not st.session_state.logado:
    st.title("Frota")
    with st.container():
        u = st.text_input("CPF (05772587374)")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == '05772587374' and s == '1234':
                st.session_state.logado = True
                st.rerun()

# --- SISTEMA ---
else:
    st.markdown("<div style='background-color:#343a40; padding:10px; color:white;'>PREFEITURA MUNICIPAL DE SALITRE</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.title("Cadastros")
        with st.expander("📂 FORMULÁRIOS", expanded=True):
            btns = ["Veículo", "Motorista", "Fornecedor", "---", "Marca", "Modelo", "Cor", "Combustível"]
            for b in btns:
                if b == "---": st.divider()
                elif st.button(b): st.session_state.tela = b; st.rerun()

    t = st.session_state.tela

    # --- TELA VEÍCULO (COMPLETA) ---
    if t == "Veículo":
        st.header("Cadastro de Veículo")
        with st.form("veic"):
            c1, c2, c3 = st.columns([1, 3, 2])
            cod = c1.text_input("Código", disabled=True)
            nome = c2.text_input("Descrição/Nome do Veículo *")
            placa = c3.text_input("Placa *")
            
            c4, c5, c6 = st.columns(3)
            renavam = c4.text_input("Renavam")
            chassi = c5.text_input("Chassi")
            situacao = c6.selectbox("Situação", ["Ativo", "Inativo", "Manutenção"])
            
            c7, c8, c9, c10 = st.columns(4)
            ano_f = c7.text_input("Ano Fab.")
            ano_m = c8.text_input("Ano Mod.")
            marca = c9.text_input("Marca")
            modelo = c10.text_input("Modelo")

            if st.form_submit_button("Salvar Veículo"):
                c.execute("INSERT INTO veiculo (nome, placa, renavam, chassi, ano_fab, ano_mod, situacao) VALUES (?,?,?,?,?,?,?)",
                          (nome, placa, renavam, chassi, ano_f, ano_m, situacao))
                conn.commit()
                st.success("Veículo Cadastrado!")

    # --- TELA MOTORISTA (COMPLETA) ---
    elif t == "Motorista":
        st.header("Cadastro de Motorista")
        with st.form("moto"):
            c1, c2, c3 = st.columns([1, 3, 2])
            c1.text_input("Código", disabled=True)
            nome = c2.text_input("Nome Completo *")
            cpf = c3.text_input("CPF *")
            
            c4, c5, c6 = st.columns(3)
            rg = c4.text_input("RG")
            cnh = c5.text_input("Nº CNH")
            cat = c6.text_input("Categoria (A, B, D...)")
            
            val = st.date_input("Validade CNH")
            end = st.text_input("Endereço Completo")
            
            if st.form_submit_button("Salvar Motorista"):
                c.execute("INSERT INTO motorista (nome, cpf, rg, cnh_numero, cnh_validade, cnh_categoria, endereco) VALUES (?,?,?,?,?,?,?)",
                          (nome, cpf, rg, cnh, str(val), cat, end))
                conn.commit()
                st.success("Motorista Salvo!")

    # --- TELAS DE MARCA / COR / COMBUSTÍVEL (NOME E SIGLA) ---
    elif t in ["Marca", "Cor", "Combustível", "Modelo"]:
        st.header(f"Cadastro de {t}")
        with st.form("simples"):
            c1, c2, c3 = st.columns([1, 4, 1])
            c1.text_input("Código", disabled=True)
            nome_s = c2.text_input(f"Nome da {t} *")
            sigla_s = c3.text_input("Sigla")
            
            if st.form_submit_button(f"Salvar {t}"):
                tab = t.lower()
                c.execute(f"INSERT INTO {tab} (nome, sigla) VALUES (?,?)", (nome_s, sigla_s))
                conn.commit()
                st.success(f"{t} Cadastrada!")

    # --- BUSCA E VISUALIZAÇÃO (Sempre no final) ---
    if t != "Home":
        st.divider()
        st.subheader(f"Pesquisa de {t}")
        try:
            df = pd.read_sql(f"SELECT * FROM {t.lower()}", conn)
            st.dataframe(df, use_container_width=True)
        except: st.write("Aguardando registros...")
