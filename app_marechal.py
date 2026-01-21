import streamlit as st

# --- ESTILO ESPECÍFICO PARA O FORMULÁRIO (CSS CUSTOM) ---
st.markdown("""
    <style>
    .form-header {
        background-color: #f8f9fa;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .btn-container {
        display: flex;
        gap: 5px;
    }
    .stTextInput label, .stSelectbox label {
        font-weight: bold !important;
        font-size: 13px !important;
    }
    .mandatory { color: red; }
    </style>
""", unsafe_allow_html=True)

def tela_fornecedor():
    # Cabeçalho do Formulário com Botões de Ação (Canto Superior Direito)
    st.markdown("""
        <div class='form-header'>
            <span style='font-size: 16px; font-weight: bold;'>Cadastro :: Fornecedor</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Simulação dos botões de ação do print (Salvar, Limpar, Buscar)
    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns([8, 0.6, 0.6, 0.6])
    with c_btn2: st.button("💾", help="Salvar")
    with c_btn3: st.button("🧹", help="Limpar")
    with c_btn4: st.button("🔍", help="Pesquisar")

    # --- PRIMEIRA LINHA ---
    st.markdown("---")
    l1_c1, l1_c2, l1_c3, l1_c4 = st.columns([1.5, 4, 2, 2.5])
    with l1_c1:
        st.text_input("Código", disabled=True, placeholder="Automático")
    with l1_c2:
        st.markdown("Nome <span class='mandatory'>*</span>", unsafe_allow_html=True)
        st.text_input("", label_visibility="collapsed", key="forn_nome")
    with l1_c3:
        st.selectbox("Tipo", ["Selecione", "Física", "Jurídica"], key="forn_tipo")
    with l1_c4:
        st.markdown("CPF <span class='mandatory'>*</span>", unsafe_allow_html=True)
        st.text_input("", label_visibility="collapsed", key="forn_cpf")

    # --- SEGUNDA LINHA ---
    l2_c1, l2_c2, l2_c3 = st.columns([2.5, 5, 2.5])
    with l2_c1:
        st.selectbox("Tipo Logradouro", ["Selecione", "Rua", "Avenida", "Praça", "Rodovia", "Travessa"], key="forn_tp_log")
    with l2_c2:
        st.text_input("Logradouro", key="forn_logradouro")
    with l2_c3:
        st.text_input("Número", key="forn_num")

    # --- TERCEIRA LINHA ---
    l3_c1, l3_c2, l3_c3, l3_c4, l3_c5 = st.columns([2.5, 2.5, 2, 1.5, 1.5])
    with l3_c1:
        st.text_input("Complemento", key="forn_comp")
    with l3_c2:
        st.text_input("Bairro", key="forn_bairro")
    with l3_c3:
        st.text_input("CEP", key="forn_cep")
    with l3_c4:
        st.selectbox("Estado", ["--", "CE", "PI", "PE", "RN", "PB"], key="forn_uf")
    with l3_c5:
        st.selectbox("Município", ["Selecione"], key="forn_mun")

    # --- QUARTA LINHA ---
    st.text_input("email", key="forn_email")

# Executa a tela dentro da estrutura do menu anterior
if st.session_state.logado:
    # (O código do menu lateral continua aqui, chamando a função abaixo se 'Fornecedor' estiver selecionado)
    # Se escolha == "Fornecedor":
    tela_fornecedor()
