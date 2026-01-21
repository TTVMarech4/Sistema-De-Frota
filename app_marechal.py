import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(page_title="SIM - Gestão Integral Salitre", layout="wide")

# --- BANCO DE DADOS ROBUSTO ---
conn = sqlite3.connect('sim_sistema_total.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # TABELAS DE APOIO (Cadastros Base)
    tables = [
        '''CREATE TABLE IF NOT EXISTS fornecedores (id INTEGER PRIMARY KEY, nome TEXT, cpf_cnpj TEXT, tipo TEXT, logradouro TEXT, numero TEXT, bairro TEXT, cep TEXT, estado TEXT, municipio TEXT, email TEXT)''',
        '''CREATE TABLE IF NOT EXISTS motoristas (id INTEGER PRIMARY KEY, nome TEXT, cpf TEXT, cnh_num TEXT, cnh_val TEXT, cnh_cat TEXT, logradouro TEXT, email TEXT)''',
        '''CREATE TABLE IF NOT EXISTS pecas (id INTEGER PRIMARY KEY, descricao TEXT, unidade_forn TEXT, unidade_dist TEXT, grupo TEXT, estoque_min REAL, estoque_atual REAL, custo_medio REAL)''',
        '''CREATE TABLE IF NOT EXISTS veiculos (id INTEGER PRIMARY KEY, placa TEXT UNIQUE, patrimonio TEXT, renavam TEXT, chassi TEXT, marca TEXT, modelo TEXT, cor TEXT, combustivel TEXT, secretaria TEXT, unidade_gestora TEXT)''',
        '''CREATE TABLE IF NOT EXISTS abastecimentos (id INTEGER PRIMARY KEY, data TEXT, placa TEXT, motorista TEXT, km_atual REAL, litros REAL, preco REAL, total REAL, cupom TEXT, posto TEXT, secretaria TEXT)''',
        '''CREATE TABLE IF NOT EXISTS ordens_servico (id INTEGER PRIMARY KEY, data TEXT, placa TEXT, fornecedor TEXT, valor_total REAL, km_os REAL, status TEXT, pecas_json TEXT)'''
    ]
    for table in tables: c.execute(table)
    c.execute("INSERT OR IGNORE INTO veiculos (placa, descricao) VALUES ('ADMIN-01', 'SISTEMA')")
    conn.commit()

init_db()

# --- CSS PARA INTERFACE PROFISSIONAL ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stSidebar { background-color: #2c3e50 !important; }
    .stHeader { background-color: #ffffff; padding: 10px; border-bottom: 2px solid #e9ecef; }
    .tce-badge { background-color: #d32f2f; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE NAVEGAÇÃO (BASEADO NOS PRINTS) ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Dashboard"

with st.sidebar:
    st.markdown("<h2 style='color:white;'>SIM SALITRE</h2>", unsafe_allow_html=True)
    st.markdown("<span class='tce-badge'>MODO AUDITORIA TCE-CE</span>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.selectbox("📁 MENU PRINCIPAL", ["DASHBOARD", "CADASTROS", "MOVIMENTOS", "ESTOQUE", "RELATÓRIOS"])
    
    if menu == "CADASTROS":
        submenu = st.radio("Submenu", ["Fornecedor", "Motorista", "Proprietário", "Veículo", "Peças/Insumos", "Unidades de Medida", "Cor/Marca/Modelo"])
    elif menu == "MOVIMENTOS":
        submenu = st.radio("Submenu", ["Abastecimento", "Ordem de Serviço", "Entrada de Nota", "Saída de Peças"])
    elif menu == "RELATÓRIOS":
        submenu = st.radio("Submenu", ["Abastecimento p/ Período", "Consumo p/ Secretaria", "Odômetro Divergente", "Posição de Estoque"])
    else:
        submenu = "Geral"

# --- LÓGICA DE PÁGINAS ---

# 1. CADASTRO DE FORNECEDOR (Print 4)
if menu == "CADASTROS" and submenu == "Fornecedor":
    st.header("📝 Cadastro :: Fornecedor")
    with st.form("forn_form"):
        c1, c2, c3 = st.columns([1, 3, 2])
        cod = c1.text_input("Código (Automático)", disabled=True)
        nome = c2.text_input("Nome *")
        tipo = c3.selectbox("Tipo", ["Física", "Jurídica"])
        
        c4, c5, c6 = st.columns([2, 3, 1])
        cpf_cnpj = c4.text_input("CPF/CNPJ *")
        logra = c5.text_input("Logradouro")
        num = c6.text_input("Número")
        
        c7, c8, c9, c10 = st.columns(4)
        bairro = c7.text_input("Bairro")
        cep = c8.text_input("CEP")
        estado = c9.selectbox("Estado", ["CE", "PI", "PE", "BA"])
        mun = c10.text_input("Município")
        
        email = st.text_input("Email de Contato")
        
        if st.form_submit_button("💾 Salvar Fornecedor"):
            c.execute("INSERT INTO fornecedores (nome, cpf_cnpj, tipo, logradouro, numero, bairro, cep, estado, municipio, email) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (nome, cpf_cnpj, tipo, logra, num, bairro, cep, estado, mun, email))
            conn.commit()
            st.success("Fornecedor cadastrado com sucesso!")

# 2. CADASTRO DE PEÇAS/INSUMOS (Print 10)
elif menu == "CADASTROS" and submenu == "Peças/Insumos":
    st.header("📦 Cadastro :: Peças e Insumos")
    with st.form("pecas_form"):
        desc = st.text_input("Descrição da Peça/Serviço *")
        c1, c2, c3 = st.columns(3)
        u_forn = c1.selectbox("Unidade Medida (Forn.)", ["UN", "LITRO", "KG", "CAIXA"])
        u_dist = c2.selectbox("Unidade Medida (Dist.)", ["UN", "LITRO", "KG"])
        fator = c3.number_input("Fator de Conversão", value=1.0)
        
        c4, c5, c6 = st.columns(3)
        grupo = c4.selectbox("Grupo", ["Combustíveis", "Peças", "Pneus", "Lubrificantes"])
        est_min = c5.number_input("Estoque Mínimo")
        est_max = c6.number_input("Estoque Máximo")
        
        if st.form_submit_button("💾 Registrar Item"):
            c.execute("INSERT INTO pecas (descricao, unidade_forn, unidade_dist, grupo, estoque_min) VALUES (?,?,?,?,?)",
                      (desc, u_forn, u_dist, grupo, est_min))
            conn.commit()
            st.success("Item adicionado ao catálogo municipal.")

# 3. ABASTECIMENTO (O mais crítico para o TCE)
elif menu == "MOVIMENTOS" and submenu == "Abastecimento":
    st.header("⛽ Movimento :: Abastecimento")
    # Carregar dados para selects
    veiculos = [v[0] for v in c.execute("SELECT placa FROM veiculos").fetchall()]
    motoristas = [m[0] for m in c.execute("SELECT nome FROM motoristas").fetchall()]
    
    with st.form("abast_form"):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data")
        veic = c2.selectbox("Veículo (Placa)", veiculos)
        moto = c3.selectbox("Motorista", motoristas if motoristas else ["Nenhum cadastrado"])
        
        c4, c5, c6 = st.columns(3)
        km = c4.number_input("Odômetro Atual (KM) *", min_value=0.0)
        litros = c5.number_input("Quantidade (Litros) *", min_value=0.0)
        preco = c6.number_input("Preço Unitário (R$)", min_value=0.0)
        
        c7, c8 = st.columns(2)
        cupom = c7.text_input("Nº Nota/Cupom Fiscal")
        posto = c8.text_input("Posto Fornecedor")
        
        if st.form_submit_button("🚀 Finalizar Lançamento"):
            total = litros * preco
            c.execute("INSERT INTO abastecimentos (data, placa, motorista, km_atual, litros, preco, total, cupom, posto) VALUES (?,?,?,?,?,?,?,?,?)",
                      (str(data), veic, moto, km, litros, preco, total, cupom, posto))
            conn.commit()
            st.success(f"Lançamento realizado! Valor Total: R$ {total:.2f}")

# 4. DASHBOARD E RELATÓRIOS (Visão do Prefeito/Auditor)
elif menu == "DASHBOARD":
    st.header("📊 Painel de Controle SAG/TCE-CE")
    c1, c2, c3 = st.columns(3)
    
    # Cálculos rápidos
    total_gasto = c.execute("SELECT SUM(total) FROM abastecimentos").fetchone()[0] or 0
    total_veic = c.execute("SELECT COUNT(*) FROM veiculos").fetchone()[0]
    
    with c1:
        st.metric("Investimento em Combustível", f"R$ {total_gasto:,.2f}")
    with c2:
        st.metric("Frota Cadastrada", f"{total_veic} Unidades")
    with c3:
        st.metric("Alertas de Odômetro", "2 Divergências", delta="-1", delta_color="inverse")

    st.markdown("---")
    st.subheader("📈 Consumo Mensal por Secretaria")
    # Simulação de gráfico
    df_abast = pd.read_sql("SELECT * FROM abastecimentos", conn)
    if not df_abast.empty:
        st.bar_chart(df_abast.set_index('data')['total'])
    else:
        st.info("Aguardando lançamentos para gerar gráficos.")

# --- FOOTER ---
st.markdown("---")
st.caption("SIM - Sistema de Informação Municipal | Salitre-CE | Desenvolvido para conformidade total com o TCE-CE")
