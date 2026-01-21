import streamlit as st

# --- 1. CONFIGURAÇÃO INICIAL (DEVE SER A PRIMEIRA COISA) ---
st.set_page_config(page_title="SIM - Cadastro de Fornecedor", layout="wide", initial_sidebar_state="expanded")

# --- 2. INICIALIZAÇÃO SEGURA DO ESTADO (EVITA O ERRO QUE VOCÊ TEVE) ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'menu_escolha' not in st.session_state:
    st.session_state.menu_escolha = "Fornecedor"

# --- 3. CSS PARA REPLICAR O DESIGN DO SITE ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2c3e50 !important; }
    .main-header { background-color: #3c8dbc; padding: 10px; color: white; font-weight: bold; margin-bottom: 20px; }
    .form-header { background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; border-radius: 4px; display: flex; justify-content: space-between; margin-bottom: 10px; }
    .mandatory { color: red; font-weight: bold; }
    label { font-weight: bold !important; font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br><div style='text-align:center;'><h2>SIM</h2><p>Acesso ao Sistema</p></div>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR"):
                if u == "05772587374" and p == "1234":
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Erro de autenticação.")

# --- 5. INTERFACE DO SISTEMA ---
else:
    # Barra Superior
    st.markdown("""<div class='main-header'>🏛️ SIM - SALITRE / CE <span style='float:right;'>👤 05772587374</span></div>""", unsafe_allow_html=True)

    # Menu Lateral
    with st.sidebar:
        st.markdown("### 📂 NAVEGAÇÃO")
        menu_principal = st.selectbox("Módulo", ["CADASTROS", "MOVIMENTOS", "RELATÓRIOS"])
        st.divider()
        if menu_principal == "CADASTROS":
            st.session_state.menu_escolha = st.radio("Selecione:", ["Fornecedor", "Veículo", "Motorista", "Peças/Insumos"])

    # --- TELA DE FORNECEDOR (CÓPIA DO PRINT) ---
    if st.session_state.menu_escolha == "Fornecedor":
        st.markdown("<div class='form-header'><b>Cadastro :: Fornecedor</b></div>", unsafe_allow_html=True)
        
        # Botões de Ação Superior
        c_btn = st.columns([10, 0.5, 0.5, 0.5])
        c_btn[1].button("💾")
        c_btn[2].button("🧹")
        c_btn[3].button("🔍")

        st.markdown("---")
        
        # Linha 1
        l1_c1, l1_c2, l1_c3, l1_c4 = st.columns([1.5, 4, 2, 2.5])
        l1_c1.text_input("Código", disabled=True, placeholder="Auto")
        l1_c2.markdown("Nome <span class='mandatory'>*</span>", unsafe_allow_html=True)
        l1_c2.text_input("", label_visibility="collapsed", key="n1")
        l1_c3.selectbox("Tipo", ["Selecione", "Física", "Jurídica"])
        l1_c4.markdown("CPF <span class='mandatory'>*</span>", unsafe_allow_html=True)
        l1_c4.text_input("", label_visibility="collapsed", key="n2")

        # Linha 2
        l2_c1, l2_c2, l2_c3 = st.columns([2.5, 5, 2.5])
        l2_c1.selectbox("Tipo Logradouro", ["Selecione", "Rua", "Avenida", "Praça"])
        l2_c2.text_input("Logradouro")
        l2_c3.text_input("Número")

        # Linha 3
        l3_c1, l3_c2, l3_c3, l3_c4, l3_c5 = st.columns([2.5, 2.5, 2, 1.5, 1.5])
        l3_c1.text_input("Complemento")
        l3_c2.text_input("Bairro")
        l3_c3.text_input("CEP")
        l3_c4.selectbox("Estado", ["--", "CE", "PI", "PE"])
        l3_c5.selectbox("Município", ["Selecione"])

        # Linha 4
        st.text_input("email")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
