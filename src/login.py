import streamlit as st
import os
import time

def render_login():
    """
    Renderiza login com 'Enter' funcionando e visual de Card centralizado.
    """
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # --- CSS DO LOGIN ---
    st.markdown("""
    <style>
        .stApp { background-color: #F5F2E9; } /* Fundo Areia Mais Escuro */
        
        /* Estilo do Cartão de Login */
        .login-card {
            background-color: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05); /* Sombra suave */
            text-align: center;
            border: 1px solid #E6DCC3;
            margin-bottom: 20px;
        }
        
        /* Remove padding extra do topo */
        .block-container { padding-top: 5rem; }
        
        /* Botão Dourado */
        div.stButton > button {
            width: 100%;
            background-color: #C5A059;
            color: white;
            border: none;
            padding: 12px;
            font-size: 16px;
            border-radius: 8px;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #8B6914;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- LAYOUT INTELIGENTE ---
    # No PC: [Espaço, Cartão, Espaço]. No Mobile, o Streamlit empilha tudo.
    # Usamos [1, 1, 1] no PC para o cartão ocupar apenas 1/3 da tela (centralizado).
    col1, col2, col3 = st.columns([1, 0.8, 1]) 

    with col2:
        st.markdown("""
        <div class="login-card">
            <h1 style="margin:0; font-size: 50px;">🕊️</h1>
            <h2 style="color: #5C4033; font-family: serif; margin-top: 10px;">Bem-vindo(a)</h2>
            <p style="color: #8D8D8D;">BibliaGPT • Acesso Restrito</p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- FORMULÁRIO (ISSO FAZ O ENTER FUNCIONAR) ---
        with st.form("login_form"):
            senha_digitada = st.text_input("Senha", type="password", placeholder="Digite sua senha aqui...", label_visibility="collapsed")
            
            # Botão de Enviar dentro do form
            submit_button = st.form_submit_button("Entrar no Santuário")
            
            if submit_button:
                senha_correta = os.getenv("APP_PASSWORD")
                if "APP_PASSWORD" in st.secrets:
                    senha_correta = st.secrets["APP_PASSWORD"]
                
                if senha_digitada == senha_correta:
                    st.session_state.password_correct = True
                    st.success("Paz seja convosco. Entrando...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Senha incorreta.")

    return False