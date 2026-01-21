import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="SIM - Frota Municipal", layout="wide", initial_sidebar_state="expanded")

# --- BANCO DE DADOS ---
db_path = 'sim_governo_v1.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (cpf TEXT PRIMARY KEY, senha TEXT, nome TEXT)')
    c.execute("INSERT OR IGNORE INTO usuarios VALUES ('05772587374', '1234', 'MARECHAL')")
    # Tabelas de Gestão
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 placa TEXT, modelo TEXT, marca TEXT, secretaria TEXT, status TEXT)''')
    conn.commit()

init_db()

# --- ESTILO VISUAL (PADRÃO ERP GOVERNAMENTAL) ---
st.markdown("""
    <style>
    /* Fundo e Sidebar */
    .stApp { background-color: #F0F2F5; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; color: white; }
    
    /* Cabeçalho do SIM */
    .sim-header {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
        padding: 15px;
        color: white;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 5px solid #10B981;
    }
    
    /* Cards de Indicadores */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-bottom: 4px solid #3B82F6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'menu_ativo' not in st.session_state: st.session_state.menu_ativo = "Dashboard"

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#1E293B;'>SIM</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Sistema de Informação Municipal</p>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("CPF", value="05772587374")
            s = st.text_input("Senha", type="password", value="1234")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if u == "05772587374" and s == "1234":
                    st.session_state.logado = True
                    st.rerun()
                else: st.error("Dados incorretos")

# --- INTERFACE DO SISTEMA ---
else:
    # Cabeçalho Superior
    st.markdown("""
        <div class="sim-header">
            <div>
                <span style="font-size:20px; font-weight:bold;">🏛️ SIM - GESTÃO DE FROTA</span><br>
                <span style="font-size:12px; opacity:0.8;">Prefeitura Municipal de Salitre - CE</span>
            </div>
            <div style="text-align:right;">
                <span style="font-size:14px;">Usuário: <b>MARECHAL</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Menu Lateral
    with st.sidebar:
        st.markdown("<h2 style='color:white;'>Navegação</h2>", unsafe_allow_html=True)
        if st.button("📊 Dashboard Geral"): st.session_state.menu_ativo = "Dashboard"
        if st.button("🚗 Cadastro de Veículos"): st.session_state.menu_ativo = "Veiculos"
        if st.button("⛽ Abastecimento"): st.session_state.menu_ativo = "Abast"
        if st.button("🛠️ Manutenções"): st.session_state.menu_ativo = "Manut"
        if st.button("👥 Motoristas"): st.session_state.menu_ativo = "Moto"
        st.divider()
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- LÓGICA DAS PÁGINAS ---
    if st.session_state.menu_ativo == "Dashboard":
        # Indicadores no topo
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown('<div class="metric-card">Total Veículos<br><h2>42</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown('<div class="metric-card">Em Uso<br><h2 style="color:green;">38</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown('<div class="metric-card">Manutenção<br><h2 style="color:red;">4</h2></div>', unsafe_allow_html=True)
        with c4: st.markdown('<div class="metric-card">Consumo Mês<br><h2>R$ 15k</h2></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos
        g1, g2 = st.columns(2)
        with g1:
            st.write("### ⛽ Consumo por Secretaria")
            fig = px.pie(values=[40, 25, 20, 15], names=['Saúde', 'Educação', 'Obras', 'Gabinete'])
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.write("### 📈 Gastos nos últimos 6 meses")
            fig2 = px.line(x=["Ago", "Set", "Out", "Nov", "Dez", "Jan"], y=[12, 15, 14, 18, 22, 15])
            st.plotly_chart(fig2, use_container_width=True)

    elif st.session_state.menu_ativo == "Veiculos":
        st.subheader("🚗 Cadastro e Gerenciamento de Veículos")
        with st.expander("➕ Adicionar Novo Veículo"):
            with st.form("cad_veiculo"):
                v1, v2, v3 = st.columns(3)
                placa = v1.text_input("Placa")
                marca = v2.text_input("Marca")
                modelo = v3.text_input("Modelo")
                v4, v5 = st.columns(2)
                secretaria = v4.selectbox("Secretaria", ["Saúde", "Educação", "Infraestrutura", "Gabinete"])
                tipo = v5.selectbox("Tipo", ["Próprio", "Locado"])
                if st.form_submit_button("Salvar Veículo"):
                    st.success("Veículo registrado no SIM!")

        st.write("### Frota Ativa")
        # Exemplo de tabela de sistema profissional
        df_exemplo = pd.DataFrame({
            'Placa': ['OSC-1234', 'HTX-9090', 'PMA-0011'],
            'Modelo': ['L200 Triton', 'Fiat Uno', 'Ônibus Escolar'],
            'Secretaria': ['Saúde', 'Obras', 'Educação'],
            'Status': ['Disponível', 'Em Rota', 'Manutenção']
        })
        st.table(df_exemplo)

    elif st.session_state.menu_ativo == "Abast":
        st.subheader("⛽ Controle de Abastecimento")
        st.info("Módulo de integração com postos credenciados.")
        st.date_input("Filtrar por data")
        st.button("Gerar Relatório de Consumo (PDF)")
