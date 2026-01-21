import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="SIM - Gestão Pública Salitre", layout="wide")

# --- BANCO DE DADOS (BLINDADO) ---
# Mudamos o nome do arquivo para garantir que as tabelas sejam criadas do zero corretamente
conn = sqlite3.connect('sim_final_tce.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # 1. FORNECEDORES (Completo)
    c.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf_cnpj TEXT UNIQUE, 
                 tipo TEXT, logradouro TEXT, numero TEXT, bairro TEXT, cep TEXT, 
                 estado TEXT, municipio TEXT, email TEXT, telefone TEXT)''')
    
    # 2. MOTORISTAS (Completo)
    c.execute('''CREATE TABLE IF NOT EXISTS motoristas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, 
                 cnh_num TEXT, cnh_val TEXT, cnh_cat TEXT, matricula TEXT)''')
    
    # 3. VEÍCULOS (Todos os campos do TCE)
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT UNIQUE, patrimonio TEXT, 
                 descricao TEXT, renavam TEXT, chassi TEXT, marca TEXT, modelo TEXT, 
                 cor TEXT, combustivel TEXT, secretaria TEXT, situacao TEXT)''')
    
    # 4. PEÇAS E INSUMOS (Estoque)
    c.execute('''CREATE TABLE IF NOT EXISTS pecas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, unidade TEXT, 
                 grupo TEXT, estoque_min REAL, estoque_atual REAL, custo REAL)''')
    
    # 5. ABASTECIMENTO (Auditável)
    c.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, placa TEXT, 
                 motorista TEXT, km_atual REAL, litros REAL, preco REAL, 
                 total REAL, cupom TEXT, posto TEXT)''')

    # Garantir que existe um veículo administrativo para evitar erros de busca inicial
    c.execute("INSERT OR IGNORE INTO veiculos (placa, descricao, situacao) VALUES ('ADMIN-01', 'VEICULO DO SISTEMA', 'ATIVO')")
    conn.commit()

# Executa a inicialização
init_db()

# --- INTERFACE PROFISSIONAL ---
st.markdown("""
    <style>
    .main-header { background: #1e293b; padding: 15px; color: white; border-radius: 5px; border-left: 10px solid #10b981; margin-bottom: 20px; }
    .sidebar-title { color: #f8f9fa; font-weight: bold; font-size: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Dashboard"

with st.sidebar:
    st.markdown("<div class='sidebar-title'>SIM SALITRE</div>", unsafe_allow_html=True)
    st.divider()
    menu = st.selectbox("📂 MENU PRINCIPAL", ["DASHBOARD", "CADASTROS", "MOVIMENTOS", "RELATÓRIOS"])
    
    if menu == "CADASTROS":
        submenu = st.radio("Selecione o Cadastro:", ["Fornecedor", "Motorista", "Veículo", "Peças/Estoque"])
    elif menu == "MOVIMENTOS":
        submenu = st.radio("Selecione o Movimento:", ["Abastecimento", "Ordem de Serviço", "Entrada de Peças"])
    else:
        submenu = "Geral"

# --- LÓGICA DE PÁGINAS ---

if menu == "DASHBOARD":
    st.markdown("<div class='main-header'>📊 PAINEL EXECUTIVO - GESTÃO DE ATIVOS</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Frota Total", c.execute("SELECT COUNT(*) FROM veiculos").fetchone()[0])
    c2.metric("Motoristas", c.execute("SELECT COUNT(*) FROM motoristas").fetchone()[0])
    c3.metric("Fornecedores", c.execute("SELECT COUNT(*) FROM fornecedores").fetchone()[0])
    gasto = c.execute("SELECT SUM(total) FROM abastecimentos").fetchone()[0] or 0
    c4.metric("Gasto Total (R$)", f"{gasto:,.2f}")

    st.divider()
    st.subheader("🏁 Veículos Cadastrados no Sistema")
    df_v = pd.read_sql("SELECT placa, descricao, secretaria, situacao FROM veiculos", conn)
    st.table(df_v)

elif submenu == "Fornecedor":
    st.subheader("📝 Cadastro de Fornecedor")
    with st.form("f_forn"):
        col1, col2 = st.columns([3, 1])
        nome = col1.text_input("Razão Social / Nome")
        doc = col2.text_input("CPF / CNPJ")
        col3, col4, col5 = st.columns([3, 1, 2])
        rua = col3.text_input("Logradouro")
        num = col4.text_input("Nº")
        bairro = col5.text_input("Bairro")
        if st.form_submit_button("Salvar Fornecedor"):
            c.execute("INSERT INTO fornecedores (nome, cpf_cnpj, logradouro, numero, bairro) VALUES (?,?,?,?,?)", (nome, doc, rua, num, bairro))
            conn.commit()
            st.success("Fornecedor Registrado!")

elif submenu == "Veículo":
    st.subheader("🚗 Cadastro de Veículo (Ficha Completa)")
    with st.form("f_veic"):
        c1, c2, c3 = st.columns(3)
        placa = c1.text_input("Placa *")
        pat = c2.text_input("Nº Patrimônio")
        desc = c3.text_input("Descrição (Ex: Van Escolar)")
        c4, c5, c6 = st.columns(3)
        ren = c4.text_input("RENAVAM")
        cha = c5.text_input("CHASSI")
        sec = c6.selectbox("Secretaria", ["Saúde", "Educação", "Infraestrutura", "Gabinete"])
        if st.form_submit_button("Salvar Veículo"):
            c.execute("INSERT INTO veiculos (placa, patrimonio, descricao, renavam, chassi, secretaria) VALUES (?,?,?,?,?,?)", (placa, pat, desc, ren, cha, sec))
            conn.commit()
            st.success("Veículo salvo no patrimônio municipal!")

elif submenu == "Abastecimento":
    st.subheader("⛽ Movimentação de Combustível")
    with st.form("f_abast"):
        # Busca placas reais para o select
        placas_db = [p[0] for p in c.execute("SELECT placa FROM veiculos").fetchall()]
        c1, c2, c3 = st.columns(3)
        v_sel = c1.selectbox("Veículo", placas_db)
        km = c2.number_input("Odômetro Atual", min_value=0.0)
        litros = c3.number_input("Litros", min_value=0.0)
        c4, c5, c6 = st.columns(3)
        preco = c4.number_input("Preço Unitário", min_value=0.0)
        cupom = c5.text_input("Nº Cupom Fiscal")
        posto = c6.text_input("Posto")
        if st.form_submit_button("Lançar"):
            total = litros * preco
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            c.execute("INSERT INTO abastecimentos (data, placa, km_atual, litros, preco, total, cupom, posto) VALUES (?,?,?,?,?,?,?,?)", 
                      (data_atual, v_sel, km, litros, preco, total, cupom, posto))
            conn.commit()
            st.success("Abastecimento registrado!")

elif menu == "RELATÓRIOS":
    st.subheader("📋 Relatório Geral de Movimentação")
    op = st.radio("Tipo", ["Abastecimentos", "Veículos", "Fornecedores"], horizontal=True)
    if op == "Abastecimentos":
        df = pd.read_sql("SELECT * FROM abastecimentos", conn)
    elif op == "Veículos":
        df = pd.read_sql("SELECT * FROM veiculos", conn)
    else:
        df = pd.read_sql("SELECT * FROM fornecedores", conn)
    st.dataframe(df, use_container_width=True)
