import os
import streamlit as st
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÃO ---
load_dotenv(override=True)
os.environ["LANGCHAIN_TRACING_V2"] = "false"

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "PINECONE_API_KEY" in st.secrets:
    os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]

from utils import criar_pdf_download, gerar_audio
from agents import get_supervisor_chain, get_agente_web, get_agente_rag
from login import render_login

# Layout Wide para aproveitar tela, mas vamos controlar a largura com CSS
st.set_page_config(page_title="BibliaGPT", page_icon="🕊️", layout="wide")

# --- 2. LOGIN ---
if not render_login():
    st.stop()

# --- 3. CSS VISUAL (TEMA PERGAMINHO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lato:wght@400;700&display=swap');

    /* Fundo Geral (Areia Quente) */
    .stApp { background-color: #F7F5F0; }

    /* Cabeçalho Centralizado */
    .main-header {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
        border-bottom: 2px solid #E6DCC3;
    }
    .main-header h1 {
        font-family: 'Cinzel', serif;
        color: #5C4033;
        font-size: 2.5rem;
        margin-bottom: 0;
    }
    .main-header p { color: #8C7B70; font-style: italic; }

    /* Cartões de Mensagem (Bolinhas do Chat) */
    div[data-testid="stChatMessageContent"] {
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-family: 'Lato', sans-serif;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* Mensagem da IA (Fundo Branco/Creme) */
    div[data-testid="stChatMessageContent"][data-testid="stChatMessageContent"] {
        background-color: #FFFFFF;
        border-left: 4px solid #C5A059; /* Borda dourada na esquerda */
    }

    /* Mensagem do Usuário (Fundo Bege Escuro para contraste) */
    div[data-testid="stChatMessageContent"][style*="flex-direction: row-reverse"] {
        background-color: #EBE5CE; 
    }

    /* Input de Texto */
    .stChatInputContainer textarea {
        background-color: white;
        border: 1px solid #C5A059;
        border-radius: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #EFEBE0;
        border-right: 1px solid #DZC4B0;
    }
    
    /* Responsividade Mobile */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.8rem; }
        .stApp { background-color: #FFFBF5; } /* Um pouco mais claro no celular */
    }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='margin:0;'>🕊️</h1></div>", unsafe_allow_html=True)
    
    st.markdown("### Modo de Conselho")
    opcoes = {
        "Devocional": "🙏 **Pastoral** (Conforto)",
        "Teológico": "📚 **Ensino** (Doutrina)",
        "Histórico": "🌍 **Contexto** (História)",
    }
    foco = st.radio("Selecione:", list(opcoes.keys()), label_visibility="collapsed")
    st.info(opcoes[foco])
    
    st.markdown("---")
    st.markdown("#### 🕒 Histórico")
    if "messages" in st.session_state:
        # Mostra as últimas 4 perguntas
        for msg in reversed(st.session_state.messages[-8:]):
            if msg["role"] == "user":
                txt = (msg["content"][:22] + '...') if len(msg["content"]) > 22 else msg["content"]
                st.caption(f"• {txt}")

    st.markdown("---")
    if st.button("🗑️ Nova Conversa", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "A paz! Como posso ajudar seu coração hoje?"}]
        st.rerun()

# --- 5. CABEÇALHO (Centralizado e Bonito) ---
st.markdown(f"""
<div class="main-header">
    <h1>Conselheira {foco}</h1>
    <p>Guiado pela Sabedoria Eterna</p>
</div>
""", unsafe_allow_html=True)

# --- 6. CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "A paz! Como posso ajudar seu coração hoje?"}]

for msg in st.session_state.messages:
    avatar = "🕊️" if msg["role"] == "assistant" else "👤"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

# Audio Player (Discreto)
if "ultimo_audio" in st.session_state and st.session_state.ultimo_audio:
    st.audio(st.session_state.ultimo_audio, format="audio/mp3")

# Input
prompt = st.chat_input("Escreva sua dúvida ou aflição...")

if prompt:
    if len(prompt) > 500:
        st.warning("Mensagem muito longa.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)
    st.session_state.ultimo_audio = None
    
    chat_history = [m for m in st.session_state.messages if m["role"] != "system"][-6:]

    with st.chat_message("assistant", avatar="🕊️"):
        with st.spinner("🙏 Buscando na Palavra..."):
            try:
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
        
        st.session_state.ultima_resposta = resposta
        st.session_state.ultima_pergunta = prompt
        st.session_state.ultimo_agente = agente
        
        caminho_audio = gerar_audio(resposta)
        if caminho_audio:
            st.session_state.ultimo_audio = caminho_audio
            st.rerun()

# Botão PDF (Aparece centralizado abaixo do chat)
if "ultima_resposta" in st.session_state and st.session_state.ultima_resposta:
    try:
        pdf_bytes = criar_pdf_download(
            st.session_state.ultima_pergunta,
            st.session_state.ultima_resposta,
            foco,
            st.session_state.ultimo_agente
        )
        col_pdf1, col_pdf2, col_pdf3 = st.columns([1,2,1])
        with col_pdf2:
            st.download_button("📥 Baixar Conselho em PDF", data=bytes(pdf_bytes), file_name="conselho_biblico.pdf", mime="application/pdf", use_container_width=True)
    except: pass