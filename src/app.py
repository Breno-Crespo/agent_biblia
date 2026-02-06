import os
import streamlit as st
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÃO DE AMBIENTE ---
load_dotenv(override=True)
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Ponte de Segurança para Nuvem
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "PINECONE_API_KEY" in st.secrets:
    os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]

# Imports Locais
from utils import criar_pdf_download, gerar_audio
from agents import get_supervisor_chain, get_agente_web, get_agente_rag
from login import render_login  # <--- NOVO IMPORT

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="BibliaGPT", page_icon="🕊️", layout="wide")

# --- 3. VERIFICAÇÃO DE LOGIN (Modularizada) ---
if not render_login():
    st.stop() # Para aqui se não estiver logado

# --- 4. ESTILO "SAND & MOBILE" (CSS AVANÇADO) ---
st.markdown("""
<style>
    /* Fonte e Cores Globais */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&family=Lato:wght@400;700&display=swap');
    
    /* Fundo geral (Tom Areia Suave) */
    .stApp { background-color: #FDFBF7; }
    
    /* Área de Chat (Cartões) */
    div[data-testid="stChatMessageContent"] {
        background-color: #FFFFFF; 
        border-radius: 15px; 
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        border: 1px solid #F0EAD6; /* Borda bege sutil */
        font-family: 'Lato', sans-serif; 
        color: #4A4A4A;
    }
    
    /* Ajustes para Mobile (Telas pequenas) */
    @media (max-width: 768px) {
        /* Aumenta o tamanho da fonte para leitura fácil */
        div[data-testid="stChatMessageContent"] { font-size: 16px; }
        
        /* Ajusta padding do topo para não cortar título */
        .block-container { padding-top: 2rem; padding-left: 1rem; padding-right: 1rem; }
        
        /* Botões full-width no mobile */
        div.stButton > button { width: 100%; margin-bottom: 10px; }
    }
    
    /* Sidebar (Menu Lateral) */
    section[data-testid="stSidebar"] {
        background-color: #F7F5F0; /* Bege um pouco mais escuro */
        border-right: 1px solid #E6DCC3;
    }
    
    /* Input de Texto (Onde digita) */
    .stChatInputContainer textarea {
        background-color: #FFFFFF;
        border: 1px solid #D2B48C; /* Tan */
    }
    
    /* Títulos */
    h1, h2, h3 { font-family: 'Merriweather', serif; color: #5C4033; }
</style>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR (Navegação) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #DAA520;'>🕊️ Menu</h2>", unsafe_allow_html=True)
    
    opcoes = {
        "Devocional": "🙏 **Pastoral** (Conforto)",
        "Teológico": "📚 **Ensino** (Doutrina)",
        "Histórico": "🌍 **Contexto** (Cultura)",
    }
    foco = st.radio("Modo:", list(opcoes.keys()))
    st.caption(opcoes[foco])
    st.markdown("---")
    
    # Histórico Rápido
    st.markdown("#### 🕒 Recente")
    if "messages" in st.session_state:
        for msg in reversed(st.session_state.messages[-5:]): # Mostra só as últimas 5
            if msg["role"] == "user":
                txt = (msg["content"][:25] + '...') if len(msg["content"]) > 25 else msg["content"]
                st.caption(f"🔹 {txt}")
    
    st.markdown("---")
    if st.button("🗑️ Nova Conversa"):
        st.session_state.messages = [{"role": "assistant", "content": "A paz! Como posso ajudar seu coração hoje?"}]
        st.rerun()

# --- 6. CHAT PRINCIPAL ---
col_head1, col_head2 = st.columns([1, 5])
with col_head1:
    st.markdown("# 🕊️")
with col_head2:
    st.markdown(f"### Conselheira {foco}")

# Inicializa Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "A paz! Como posso ajudar seu coração hoje?"}]

# Renderiza Mensagens
for msg in st.session_state.messages:
    avatar = "🕊️" if msg["role"] == "assistant" else "👤"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

# Player de Áudio
if "ultimo_audio" in st.session_state and st.session_state.ultimo_audio:
    st.audio(st.session_state.ultimo_audio, format="audio/mp3")

# Input
prompt = st.chat_input("Digite sua dúvida aqui...")

if prompt:
    if len(prompt) > 500:
        st.warning("Mensagem muito longa. Tente resumir.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)
    st.session_state.ultimo_audio = None
    
    # Histórico Otimizado
    mensagens_totais = [msg for msg in st.session_state.messages if msg["role"] != "system"]
    chat_history = mensagens_totais[-6:]

    with st.chat_message("assistant", avatar="🕊️"):
        # Spinner customizado com cor dourada
        with st.spinner("🙏 Buscando sabedoria..."):
            try:
                # Cache de conexão
                supervisor = get_supervisor_chain()
                rota = supervisor.invoke({"input": prompt}).strip()
                
                if rota == "WEB":
                    resposta, agente = get_agente_web(prompt, chat_history, foco)
                else:
                    resposta, agente = get_agente_rag(rota, prompt, chat_history, foco)
                
            except Exception as e:
                st.error("Instabilidade momentânea. Tente novamente.")
                st.stop()

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
        
        # Salva dados para PDF/Audio
        st.session_state.ultima_resposta = resposta
        st.session_state.ultima_pergunta = prompt
        st.session_state.ultimo_agente = agente
        
        # Audio Auto-play (Opcional, pode remover se ficar chato no mobile)
        caminho_audio = gerar_audio(resposta)
        if caminho_audio:
            st.session_state.ultimo_audio = caminho_audio
            st.rerun()

# Botão de PDF flutuante no final da resposta
if "ultima_resposta" in st.session_state and st.session_state.ultima_resposta:
    try:
        pdf_bytes = criar_pdf_download(
            st.session_state.ultima_pergunta,
            st.session_state.ultima_resposta,
            foco,
            st.session_state.ultimo_agente
        )
        st.download_button("📄 Baixar PDF", data=bytes(pdf_bytes), file_name="conselho.pdf", mime="application/pdf", use_container_width=True)
    except: pass