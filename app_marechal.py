import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="SIM - Gestão Pública Salitre", layout="wide")

# --- BANCO DE DADOS (ESTRUTURA DE AUDITORIA) ---
db_path = 'sim_tce_ceara.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
c = conn.cursor()

def init_db():
    # VEÍCULOS (Campos exigidos pelo TCE: Patrimônio, Chassi, Renavam, Tipo de Aquisição)
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 codigo_patrimonio TEXT, placa TEXT, renavam TEXT, chassi TEXT,
                 descricao TEXT, marca TEXT, modelo TEXT, ano_fab TEXT, ano_mod TEXT,
                 combustivel TEXT, secretaria TEXT, situacao TEXT,
                 tipo_aquisicao TEXT, data_aquisicao TEXT, valor_aquisicao REAL)''')
    
    # ABASTECIMENTO (Controle de Cupom, KM Inicial/Final, Lotação)
    c.execute('''CREATE TABLE IF NOT EXISTS abastecimentos (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 data TEXT, veiculo_id INTEGER, motorista_id INTEGER,
                 km_anterior REAL, km_atual REAL, litros REAL, 
                 valor_unitario REAL, valor_total REAL, posto TEXT, cupom_fiscal TEXT)''')
    
    # MOTORISTAS (Vínculo e CNH)
    c.execute('''CREATE TABLE IF NOT EXISTS motoristas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT, cpf TEXT, matricula TEXT, cnh_numero TEXT, 
                 cnh_categoria TEXT, cnh_validade TEXT, vinculo TEXT)''')
    
    # USUÁRIO ADM
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (cpf TEXT PRIMARY KEY, senha TEXT)')
    c.execute("INSERT OR IGNORE INTO usuarios VALUES ('05772587374', '1234')")
    conn.commit()

init_db()

# --- INTERFACE ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pagina' not in st.session_state: st.session_state.pagina = "Dashboard"

if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>SIM - TCE/CE</h1>", unsafe_allow_html=True)
    with st.container():
        _, col, _ = st.columns([1,1,1])
        with col:
            u = st.text_input("CPF")
            s = st.text_input("Senha", type="password")
            if st.button("ACESSAR"):
                if u == "05772587374" and s == "1234":
                    st.session_state.logado = True
                    st.rerun()

else:
    # Cabeçalho de Prestação de Contas
    st.markdown("""<div style='background-color:#1E293B; padding:15px; color:white; border-bottom:5px solid #10B981;'>
                <b>SIM - SISTEMA DE INFORMAÇÃO MUNICIPAL</b> | Prestação de Contas TCE-CE | Salitre-CE</div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("Módulos TCE")
        if st.button("📊 Painel de Controle (SAG)") : st.session_state.pagina = "Dashboard"
        if st.button("🚗 Cadastro de Frota"): st.session_state.pagina = "Frota"
        if st.button("⛽ Controle de Abastecimento"): st.session_state.pagina = "Abastecimento"
        if st.button("👥 Cadastro de Condutores"): st.session_state.pagina = "Condutores"
        if st.button("🛠️ Manutenções e OS"): st.session_state.pagina = "Manut"
        st.divider()
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- PÁGINA: CADASTRO DE FROTA (COMPLETO) ---
    if st.session_state.pagina == "Frota":
        st.header("📦 Gestão de Patrimônio e Frota")
        with st.form("cad_veic_tce"):
            c1, c2, c3 = st.columns([1, 2, 2])
            patrimonio = c1.text_input("Nº Patrimônio (TCE)")
            placa = c2.text_input("Placa (Mercosul)")
            descricao = c3.text_input("Descrição (Ex: Caminhão Pipa)")
            
            c4, c5, c6 = st.columns(3)
            renavam = c4.text_input("RENAVAM")
            chassi = c5.text_input("CHASSI")
            situacao = c6.selectbox("Situação Atual", ["Ativo", "Baixado", "Leilão", "Manutenção"])
            
            c7, c8, c9 = st.columns(3)
            secretaria = c7.selectbox("Secretaria Vinculada", ["Saúde", "Educação", "Infraestrutura", "Assistência Social", "Gabinete"])
            tipo_aq = c8.selectbox("Tipo de Aquisição", ["Próprio", "Locado", "Cessão", "Doação"])
            valor_aq = c9.number_input("Valor de Aquisição (R$)", min_value=0.0)
            
            if st.form_submit_button("✅ Salvar no Sistema"):
                c.execute("INSERT INTO veiculos (codigo_patrimonio, placa, renavam, chassi, descricao, situacao, secretaria, tipo_aquisicao, valor_aquisicao) VALUES (?,?,?,?,?,?,?,?,?)",
                          (patrimonio, placa, renavam, chassi, descricao, situacao, secretaria, tipo_aq, valor_aq))
                conn.commit()
                st.success("Veículo registrado para auditoria!")

    # --- PÁGINA: ABASTECIMENTO (COMPLETO PARA AUDITORIA) ---
    elif st.session_state.pagina == "Abastecimento":
        st.header("⛽ Lançamento de Abastecimento (SIM/TCE)")
        with st.form("form_abast"):
            c1, c2 = st.columns(2)
            # Busca veículos do banco
            df_v = pd.read_sql("SELECT id, placa, descricao FROM veiculos", conn)
            veiculo_sel = c1.selectbox("Veículo", df_v['placa'] + " - " + df_v['descricao'])
            motorista = c2.text_input("Motorista (Matrícula/Nome)")
            
            c3, c4, c5 = st.columns(3)
            km_ant = c3.number_input("KM Anterior", value=0.0)
            km_atual = c4.number_input("KM Atual (No ato do abast.)")
            litros = c5.number_input("Quantidade (Litros)", value=0.0)
            
            c6, c7, c8 = st.columns(3)
            preco = c6.number_input("Preço Unitário (R$)", value=0.0)
            fiscal = c7.text_input("Nº Cupom/Nota Fiscal")
            posto = c8.text_input("Posto Credenciado")
            
            if st.form_submit_button("🚀 Finalizar Lançamento"):
                val_total = litros * preco
                c.execute("INSERT INTO abastecimentos (veiculo_id, km_anterior, km_atual, litros, valor_unitario, valor_total, cupom_fiscal, posto) VALUES (?,?,?,?,?,?,?,?)",
                          (veiculo_sel, km_ant, km_atual, litros, preco, val_total, fiscal, posto))
                conn.commit()
                st.success("Abastecimento auditado e salvo!")

    # --- RELATÓRIOS ---
    st.divider()
    st.subheader("📋 Registros Atuais")
    if st.session_state.pagina == "Frota":
        df_show = pd.read_sql("SELECT * FROM veiculos", conn)
        st.dataframe(df_show, use_container_width=True)
    elif st.session_state.pagina == "Abastecimento":
        df_show = pd.read_sql("SELECT * FROM abastecimentos", conn)
        st.dataframe(df_show, use_container_width=True)
