import streamlit as st
import os
import time

def render_login():
    """
    Renderiza a tela de login com estilo Mobile-First e tema Areia.
    Retorna True se logado, False se não.
    """
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # --- CSS ESPECÍFICO PARA A TELA DE LOGIN ---
    st.markdown("""
    <style>
        .stApp {
            background-color: #FDFBF7; /* Tom Areia Suave */
        }
        .login-card {
            background-color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            margin-top: 50px;
            border: 1px solid #E6DCC3;
        }
        .stTextInput input {
            background-color: #FAFAFA;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
        }
        div.stButton > button {
            width: 100%;
            background-color: #DAA520;
            color: white;
            border-radius: 10px;
            height: 50px;
            font-size: 18px;
            font-weight: bold;
            border: none;
        }
        div.stButton > button:hover {
            background-color: #B8860B;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- INTERFACE DE LOGIN ---
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <h1 style="color: #8B4513; margin-bottom: 0;">🕊️</h1>
            <h2 style="color: #5C4033; font-family: sans-serif;">Bem-vindo(a)</h2>
            <p style="color: #888; font-size: 14px;">BibliaGPT - Orientação Espiritual</p>
        </div>
        """, unsafe_allow_html=True)
        
        senha_digitada = st.text_input("Senha de Acesso", type="password", label_visibility="collapsed", placeholder="Digite a senha...")
        
        if st.button("Entrar"):
            # Lógica de verificação (Prioriza Secrets, depois .env)
            senha_correta = os.getenv("APP_PASSWORD")
            if "APP_PASSWORD" in st.secrets:
                senha_correta = st.secrets["APP_PASSWORD"]
            
            if senha_digitada == senha_correta:
                st.session_state.password_correct = True
                st.success("Acesso permitido! Entrando...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("🔒 Senha incorreta.")

    return False