import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(page_title="SIM - Sistema de Informação Municipal", layout="wide")

# --- BANCO DE DADOS INTEGRAL ---
conn = sqlite3.connect('sim_governo_total.db', check_same_thread=False)
c = conn.cursor()

def total_init():
    # 1. CADASTROS DE APOIO (O QUE O TCE EXIGE)
    c.execute('CREATE TABLE IF NOT EXISTS unidade_gestora (id INTEGER PRIMARY KEY, nome TEXT, cnpj TEXT, sigla TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS fonte_recurso (id INTEGER PRIMARY KEY, codigo TEXT, nome TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS natureza_entrada (id INTEGER PRIMARY KEY, descricao TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS unidades_medida (id INTEGER PRIMARY KEY, sigla TEXT, descricao TEXT)')
    
    # 2. CADASTROS PRINCIPAIS
    c.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo_contabil TEXT, nome_razao TEXT, nome_fantasia TEXT, 
        tipo_pessoa TEXT, cpf_cnpj TEXT UNIQUE, insc_estadual TEXT, logradouro TEXT, numero TEXT, 
        bairro TEXT, cep TEXT, municipio TEXT, uf TEXT, telefone TEXT, email TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS motoristas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, rg TEXT, 
        cnh_numero TEXT, cnh_categoria TEXT, cnh_validade TEXT, data_admissao TEXT, 
        vinculo TEXT, secretaria TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, patrimonio TEXT UNIQUE, placa TEXT UNIQUE, 
        renavam TEXT, chassi TEXT, descricao TEXT, marca TEXT, modelo TEXT, cor TEXT, 
        ano_fabricacao TEXT, ano_modelo TEXT, combustivel_principal TEXT, 
        capacidade_tanque REAL, secretaria_id TEXT, unidade_controle TEXT, status TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS pecas_insumos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo_barras TEXT, descricao TEXT, 
        grupo TEXT, subgrupo TEXT, unidade_compra TEXT, unidade_saida TEXT, 
        fator_conversao REAL, estoque_minimo REAL, estoque_atual REAL, preco_custo REAL)''')

    # 3. MOVIMENTAÇÕES (AUDITÁVEIS)
    c.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT, veiculo_id TEXT, motorista_id TEXT, 
        km_anterior REAL, km_atual REAL, litros REAL, valor_unitario REAL, valor_total REAL, 
        cupom_fiscal TEXT, posto_id TEXT, fonte_recurso_id TEXT, natureza_id TEXT)''')
    
    conn.commit()

total_init()

# --- CSS: DESIGN ENTERPRISE ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stSidebar { background-color: #1a202c !important; }
    .header-box { background: #2d3748; padding: 20px; color: white; border-radius: 10px; border-left: 15px solid #48bb78; margin-bottom: 25px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2b6cb0; color: white; }
    .divider { border-top: 2px solid #e2e8f0; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO POR MODULOS ---
if 'aba' not in st.session_state: st.session_state.aba = "Dashboard"

with st.sidebar:
    st.markdown("<h2 style='color:white; text-align:center;'>🏛️ SIM SALITRE</h2>", unsafe_allow_html=True)
    st.divider()
    
    with st.expander("📂 CADASTROS", expanded=True):
        if st.button("🏢 Unidade Gestora"): st.session_state.aba = "UG"
        if st.button("🚚 Fornecedores"): st.session_state.aba = "FORN"
        if st.button("👤 Motoristas"): st.session_state.aba = "MOTO"
        if st.button("🚗 Veículos"): st.session_state.aba = "VEIC"
        if st.button("📦 Peças e Insumos"): st.session_state.aba = "PECA"
        if st.button("📏 Unidades de Medida"): st.session_state.aba = "UNID"
    
    with st.expander("🔄 MOVIMENTAÇÃO"):
        if st.button("⛽ Abastecimento"): st.session_state.aba = "ABAS"
        if st.button("🛠️ Ordem de Serviço"): st.session_state.aba = "OS"
        if st.button("📥 Entrada de Estoque"): st.session_state.aba = "ENTRADA"

    with st.expander("📊 RELATÓRIOS TCE"):
        if st.button("📋 Média de Consumo"): st.session_state.aba = "REL_CONS"
        if st.button("📑 Histórico por Veículo"): st.session_state.aba = "REL_HIST"

# --- RENDERIZAÇÃO DE TELAS ---

# TELA: VEÍCULOS (COMPLETA)
if st.session_state.aba == "VEIC":
    st.markdown("<div class='header-box'><h2>Cadastro Técnico de Veículos e Máquinas</h2></div>", unsafe_allow_html=True)
    with st.form("f_veic"):
        c1, c2, c3, c4 = st.columns(4)
        pat = c1.text_input("Nº Patrimônio *")
        placa = c2.text_input("Placa *")
        ren = c3.text_input("RENAVAM")
        cha = c4.text_input("CHASSI")
        
        c5, c6, c7 = st.columns([2,1,1])
        desc = c5.text_input("Descrição Completa (Marca/Modelo/Versão) *")
        cor = c6.text_input("Cor")
        comb = c7.selectbox("Combustível", ["Diesel S10", "Diesel S500", "Gasolina Comum", "Gasolina Aditivada", "Etanol"])
        
        c8, c9, c10, c11 = st.columns(4)
        afab = c8.text_input("Ano Fab.")
        amod = c9.text_input("Ano Mod.")
        sec = c10.selectbox("Secretaria", ["Saúde", "Educação", "Infraestrutura", "Ação Social", "Gabinete"])
        status = c11.selectbox("Status", ["Ativo", "Manutenção", "Baixado", "Reserva"])
        
        if st.form_submit_button("SALVAR REGISTRO PATRIMONIAL"):
            c.execute("INSERT INTO veiculos (patrimonio, placa, renavam, chassi, descricao, cor, combustivel_principal, ano_fabricacao, ano_modelo, secretaria_id, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                      (pat, placa, ren, cha, desc, cor, comb, afab, amod, sec, status))
            conn.commit()
            st.success("Veículo catalogado com sucesso.")

# TELA: ABASTECIMENTO (AUDITORIA TCE)
elif st.session_state.aba == "ABAS":
    st.markdown("<div class='header-box'><h2>Registro de Abastecimento e Hodômetro</h2></div>", unsafe_allow_html=True)
    with st.form("f_abas"):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data da Operação")
        # Puxa dados reais do banco para os selects
        veiculos = [v[0] for v in c.execute("SELECT placa FROM veiculos").fetchall()]
        v_sel = c2.selectbox("Veículo (Placa)", veiculos if veiculos else ["Cadastre um veículo primeiro"])
        motoristas = [m[0] for m in c.execute("SELECT nome FROM motoristas").fetchall()]
        m_sel = c3.selectbox("Motorista", motoristas if motoristas else ["Cadastre um motorista"])
        
        c4, c5, c6 = st.columns(3)
        km_ant = c4.number_input("KM Anterior (Sugerido)", help="Último KM registrado no sistema")
        km_atu = c5.number_input("KM Atual no Ato *")
        litros = c6.number_input("Quantidade de Litros *", step=0.01)
        
        c7, c8, c9 = st.columns(3)
        preco = c7.number_input("Preço Unitário (R$)", step=0.001)
        cupom = c8.text_input("Nº Cupom Fiscal / Nota")
        natureza = c9.selectbox("Natureza", ["Consumo Próprio", "Convênio", "Extraordinário"])
        
        if st.form_submit_button("FINALIZAR E GERAR COMPROVANTE"):
            total = litros * preco
            c.execute("INSERT INTO abastecimentos (data_hora, veiculo_id, motorista_id, km_anterior, km_atual, litros, valor_unitario, valor_total, cupom_fiscal, natureza_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (str(data), v_sel, m_sel, km_ant, km_atu, litros, preco, total, cupom, natureza))
            conn.commit()
            st.success(f"Lançamento processado. Média: {((km_atu-km_ant)/litros if litros>0 else 0):.2f} KM/L")

# TELA: FORNECEDORES (DETALHADO)
elif st.session_state.aba == "FORN":
    st.subheader("Gerenciamento de Fornecedores e Credenciados")
    with st.form("f_forn"):
        c1, c2, c3 = st.columns([2,1,1])
        razao = c1.text_input("Razão Social *")
        cnpj = c2.text_input("CNPJ / CPF *")
        tipo = c3.selectbox("Tipo de Fornecedor", ["Posto de Combustível", "Oficina", "Peças", "Locadora"])
        
        c4, c5, c6 = st.columns([3,1,2])
        end = c4.text_input("Endereço Completo")
        mun = c5.text_input("Município")
        email = c6.text_input("Email para Notas Fiscais")
        
        if st.form_submit_button("CADASTRAR FORNECEDOR"):
            c.execute("INSERT INTO fornecedores (nome_razao, cpf_cnpj, tipo_pessoa, logradouro, municipio, email) VALUES (?,?,?,?,?,?)",
                      (razao, cnpj, tipo, end, mun, email))
            conn.commit()
            st.success("Fornecedor habilitado no sistema.")

# TELA: DASHBOARD (VISÃO GERAL)
else:
    st.markdown("<div class='header-box'><h2>Painel de Gestão e Transparência</h2></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Veículos na Frota", len(c.execute("SELECT id FROM veiculos").fetchall()))
    c2.metric("Motoristas Ativos", len(c.execute("SELECT id FROM motoristas").fetchall()))
    c3.metric("Abastecimentos (Mês)", len(c.execute("SELECT id FROM abastecimentos").fetchall()))
    
    st.divider()
    st.subheader("📋 Últimos Lançamentos Auditados")
    df = pd.read_sql("SELECT data_hora, veiculo_id, km_atual, litros, valor_total, cupom_fiscal FROM abastecimentos ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df, use_container_width=True)
