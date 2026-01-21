import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime, date

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="SIM - Frota Municipal Salitre", layout="wide", initial_sidebar_state="expanded")

# --- BANCO DE DADOS (ARQUITETURA DE ERP) ---
db_path = 'sim_salitre_blindado.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

def init_db():
    # VEÍCULOS (Completo TCE)
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, codigo_patrimonio TEXT, placa TEXT UNIQUE, 
                 renavam TEXT, chassi TEXT, descricao TEXT, marca TEXT, modelo TEXT, 
                 ano_fab TEXT, ano_mod TEXT, cor TEXT, combustivel_tipo TEXT, 
                 secretaria TEXT, situacao TEXT, tipo_aquisicao TEXT, data_aquisicao TEXT, 
                 valor_aquisicao REAL, km_inicial REAL, capacidade_tanque REAL)''')
    
    # ABASTECIMENTOS
    c.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, placa TEXT, 
                 motorista TEXT, km_registro REAL, litros REAL, preco_unit REAL, 
                 total REAL, posto TEXT, cupom TEXT, tipo_combustivel TEXT)''')
    
    # MANUTENÇÕES
    c.execute('''CREATE TABLE IF NOT EXISTS manutenções (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, placa TEXT, 
                 tipo_servico TEXT, fornecedor TEXT, valor_total REAL, 
                 km_na_os REAL, descricao_pecas TEXT, status_os TEXT)''')
    
    # MOTORISTAS
    c.execute('''CREATE TABLE IF NOT EXISTS motoristas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, 
                 cnh_num TEXT, cnh_cat TEXT, cnh_val TEXT, matricula TEXT, status TEXT)''')

    # USUÁRIOS
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (cpf TEXT PRIMARY KEY, senha TEXT)')
    c.execute("INSERT OR IGNORE INTO usuarios VALUES ('05772587374', '1234')")
    conn.commit()

init_db()

# --- ESTILIZAÇÃO PROFISSIONAL (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    .main-header { background: #1e293b; padding: 20px; color: white; border-radius: 10px; margin-bottom: 25px; border-left: 8px solid #10b981; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .sidebar-text { font-size: 14px; font-weight: 500; }
    div[data-testid="stExpander"] { background: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Dashboard"

if not st.session_state.logado:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<br><br><h1 style='text-align:center;'>SIM</h1><p style='text-align:center;'>Prefeitura Municipal de Salitre</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("CPF")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if u == "05772587374" and s == "1234":
                    st.session_state.logado = True
                    st.rerun()
                else: st.error("Acesso negado.")
else:
    # --- BARRA SUPERIOR ---
    st.markdown("""<div class="main-header">
                <span style="font-size:24px;">🏛️ SIM - Sistema de Informação Municipal</span><br>
                <span style="opacity:0.8;">Gestão de Frotas e Ativos | Módulo de Prestação de Contas TCE-CE</span>
                </div>""", unsafe_allow_html=True)

    # --- MENU LATERAL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1041/1041916.png", width=100)
        st.markdown("### Navegação Principal")
        if st.button("📊 Dashboard Executivo"): st.session_state.pagina = "Dashboard"
        
        with st.expander("📝 CADASTROS MASTER"):
            if st.button("🚙 Veículos e Máquinas"): st.session_state.pagina = "Cad_Veic"
            if st.button("👥 Motoristas/Operadores"): st.session_state.pagina = "Cad_Moto"
            if st.button("🏢 Fornecedores/Oficinas"): st.session_state.pagina = "Cad_Forn"
        
        with st.expander("⛽ MOVIMENTAÇÃO"):
            if st.button("⛽ Lançar Abastecimento"): st.session_state.pagina = "Mov_Abast"
            if st.button("🛠️ Ordem de Serviço (OS)"): st.session_state.pagina = "Mov_OS"
            if st.button("🛞 Controle de Pneus"): st.session_state.pagina = "Mov_Pneu"

        with st.expander("📑 RELATÓRIOS TCE"):
            if st.button("📈 Média de Consumo"): st.session_state.pagina = "Rel_Cons"
            if st.button("📄 Gastos por Secretaria"): st.session_state.pagina = "Rel_Sec"

        st.divider()
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- PÁGINA: DASHBOARD ---
    if st.session_state.pagina == "Dashboard":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Frota Ativa", "45 Veículos", "OK")
        c2.metric("Gasto Mes (Diesel/Gas)", "R$ 28.450", "+12%")
        c3.metric("OS em Aberto", "6 Ordens", "-2")
        c4.metric("CNH a Vencer", "3 Alertas", "Atenção")
        
        st.write("### 🚨 Alertas de Sistema")
        st.warning("Veículo **OSC-2024 (L200)** atingiu a KM de troca de óleo (10.000 km).")
        st.error("Documentação do **Ônibus Escolar (PMA-9900)** vence em 5 dias.")

    # --- PÁGINA: CADASTRO VEÍCULO (100% COMPLETO) ---
    elif st.session_state.pagina == "Cad_Veic":
        st.subheader("🚙 Cadastro Técnico de Veículo")
        with st.form("form_veic", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            pat = col1.text_input("Número de Patrimônio")
            placa = col2.text_input("Placa *")
            desc = col3.text_input("Descrição (Ex: Ambulância)")
            
            col4, col5, col6, col7 = st.columns(4)
            renavam = col4.text_input("RENAVAM")
            chassi = col5.text_input("CHASSI")
            ano_f = col6.text_input("Ano Fabricação")
            ano_m = col7.text_input("Ano Modelo")
            
            col8, col9, col10 = st.columns(3)
            marca = col8.text_input("Marca")
            modelo = col9.text_input("Modelo")
            comb = col10.selectbox("Combustível Principal", ["Diesel S10", "Gasolina", "Etanol", "Gás Natural"])
            
            col11, col12, col13 = st.columns(3)
            sec = col11.selectbox("Secretaria Detentora", ["Saúde", "Educação", "Infraestrutura", "Gabinete"])
            situ = col12.selectbox("Status", ["Disponível", "Em Uso", "Manutenção", "Reserva"])
            km_i = col13.number_input("KM Inicial", value=0.0)
            
            if st.form_submit_button("💾 SALVAR VEÍCULO"):
                c.execute("INSERT INTO veiculos (codigo_patrimonio, placa, renavam, chassi, descricao, marca, modelo, ano_fab, ano_mod, combustivel_tipo, secretaria, situacao, km_inicial) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (pat, placa, renavam, chassi, desc, marca, modelo, ano_f, ano_m, comb, sec, situ, km_i))
                conn.commit()
                st.success("Veículo cadastrado e pronto para auditoria.")

    # --- PÁGINA: LANÇAR ABASTECIMENTO (AUDITÁVEL) ---
    elif st.session_state.pagina == "Mov_Abast":
        st.subheader("⛽ Lançamento de Abastecimento Profissional")
        with st.form("form_abast"):
            c1, c2, c3 = st.columns(3)
            data_ab = c1.date_input("Data do Abastecimento")
            # Carregar placas do banco
            placas = [p[0] for p in c.execute("SELECT placa FROM veiculos").fetchall()]
            placa_sel = c2.selectbox("Veículo (Placa)", placas)
            motorista = c3.text_input("Motorista Responsável")
            
            c4, c5, c6 = st.columns(3)
            km_reg = c4.number_input("Odômetro (KM Atual)", min_value=0.0)
            litros = c5.number_input("Qtd Litros", min_value=0.0)
            preco = c6.number_input("Preço Unitário (R$)", min_value=0.0)
            
            c7, c8, c9 = st.columns(3)
            posto = c7.text_input("Posto / Fornecedor")
            cupom = c8.text_input("Nº Nota Fiscal / Cupom")
            total = litros * preco
            c9.info(f"Valor Total: R$ {total:.2f}")
            
            if st.form_submit_button("🚀 EFETUAR LANÇAMENTO"):
                c.execute("INSERT INTO abastecimentos (data, placa, motorista, km_registro, litros, preco_unit, total, posto, cupom) VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(data_ab), placa_sel, motorista, km_reg, litros, preco, total, posto, cupom))
                conn.commit()
                st.success("Lançamento efetuado e registrado no histórico do veículo.")

    # --- VISUALIZAÇÃO DE DADOS (TABELA DE AUDITORIA) ---
    st.divider()
    st.write("### 🔍 Consulta de Registros")
    aba = st.session_state.pagina
    if aba == "Cad_Veic":
        df = pd.read_sql("SELECT codigo_patrimonio, placa, descricao, secretaria, situacao FROM veiculos", conn)
        st.dataframe(df, use_container_width=True)
    elif aba == "Mov_Abast":
        df = pd.read_sql("SELECT * FROM abastecimentos ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True)
