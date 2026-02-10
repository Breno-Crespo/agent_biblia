import os
import streamlit as st
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÃO DE AMBIENTE ---
load_dotenv(override=True)
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Ponte de Segurança para Nuvem (Secrets -> Environ)
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "PINECONE_API_KEY" in st.secrets:
    os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]

# Imports Locais
from utils import criar_pdf_download, gerar_audio
from agents import get_supervisor_chain, get_agente_web, get_agente_rag
from login import render_login

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="BibliaGPT", page_icon="🕊️", layout="wide")

# --- 3. VERIFICAÇÃO DE LOGIN ---
if not render_login():
    st.stop()

# --- 4. CSS BLINDADO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lato:wght@400;700&display=swap');

    /* Força cores globais para ignorar Modo Escuro do celular */
    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
        color: #5C4033; /* Marrom Café */
    }

    /* Fundo Geral (Areia Suave) */
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
        color: #5C4033 !important;
        font-size: 2.5rem;
        margin-bottom: 0;
    }
    .main-header p { color: #8C7B70 !important; font-style: italic; }

    /* --- CORREÇÃO DO TEXTO INVISÍVEL NO CHAT --- */
    div[data-testid="stChatMessageContent"] {
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Força texto escuro dentro dos balões */
    div[data-testid="stChatMessageContent"] p, 
    div[data-testid="stChatMessageContent"] li,
    div[data-testid="stChatMessageContent"] span {
        color: #2c3e50 !important; 
    }

    /* Balão da IA (Fundo Branco) */
    div[data-testid="stChatMessageContent"][data-testid="stChatMessageContent"] {
        background-color: #FFFFFF !important;
        border-left: 4px solid #C5A059;
    }

    /* Balão do Usuário (Fundo Bege) */
    div[data-testid="stChatMessageContent"][style*="flex-direction: row-reverse"] {
        background-color: #EBE5CE !important;
        color: #5C4033 !important;
    }

    /* --- SIDEBAR (Barra Lateral) --- */
    [data-testid="stSidebar"] {
        background-color: #EFEBE0;
        border-right: 1px solid #DZC4B0;
    }
    /* Força textos da sidebar a serem escuros */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #5C4033 !important;
    }
    
    /* Input de Texto (Área de digitar) */
    .stChatInputContainer textarea {
        background-color: #FFFFFF !important;
        color: #333333 !important; /* Texto preto */
        border: 1px solid #C5A059 !important;
    }
    
    /* Botões */
    div.stButton > button {
        color: #5C4033 !important;
        border: 1px solid #C5A059 !important;
        background-color: transparent;
    }
    div.stButton > button:hover {
        background-color: #C5A059 !important;
        color: white !important;
        border: 1px solid #C5A059 !important;
    }

    /* Ajustes Mobile */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.8rem; }
        .stApp { background-color: #FFFBF5; }
        /* Aumenta fonte para leitura fácil */
        div[data-testid="stChatMessageContent"] { font-size: 16px; }
    }
</style>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR (MENU LATERAL) ---
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='margin:0; font-size: 3rem;'>🕊️</h1></div>", unsafe_allow_html=True)
    
    st.markdown("### Modo de Conselho")
    opcoes = {
        "Devocional": "🙏 **Pastoral** (Conforto)",
        "Teológico": "📚 **Ensino** (Doutrina)",
        "Histórico": "🌍 **Contexto** (História)",
    }
    foco = st.radio("Selecione:", list(opcoes.keys()), label_visibility="collapsed")
    st.info(opcoes[foco])
    
    st.markdown("---")
    st.markdown("#### 🕒 Histórico Recente")
    if "messages" in st.session_state:
        # Mostra as últimas 5 mensagens do usuário
        for msg in reversed(st.session_state.messages[-10:]):
            if msg["role"] == "user":
                txt = (msg["content"][:22] + '...') if len(msg["content"]) > 22 else msg["content"]
                st.caption(f"• {txt}")

    st.markdown("---")
    if st.button("🗑️ Nova Conversa", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "A paz! Como posso ajudar seu coração hoje?"}]
        st.session_state.ultimo_audio = None
        st.session_state.ultima_resposta = None
        st.rerun()

# --- 6. CABEÇALHO ---
st.markdown(f"""
<div class="main-header">
    <h1>Conselheira {foco}</h1>
    <p>Guiado pela Sabedoria Eterna</p>
</div>
""", unsafe_allow_html=True)

# --- 7. CHAT PRINCIPAL ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "A paz! Como posso ajudar seu coração hoje?"}]

# Renderiza histórico
for msg in st.session_state.messages:
    avatar = "🕊️" if msg["role"] == "assistant" else "👤"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

# Player de Áudio (Se houver)
if "ultimo_audio" in st.session_state and st.session_state.ultimo_audio:
    st.audio(st.session_state.ultimo_audio, format="audio/mp3")

# Input do Usuário
prompt = st.chat_input("Escreva sua dúvida ou aflição...")

if prompt:
    # Trava de segurança para textos gigantes
    if len(prompt) > 500:
        st.warning("Mensagem muito longa. Por favor, seja breve.")
        st.stop()

    # Adiciona msg do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)
    st.session_state.ultimo_audio = None # Limpa audio anterior
    
    # Histórico Otimizado (Cache de Contexto)
    mensagens_totais = [msg for msg in st.session_state.messages if msg["role"] != "system"]
    chat_history = mensagens_totais[-6:] # Janela de 6 mensagens

    # Processamento da IA
    with st.chat_message("assistant", avatar="🕊️"):
        with st.spinner("🙏 Buscando na Palavra..."):
            try:
                # Classificador
                supervisor = get_supervisor_chain()
                rota = supervisor.invoke({"input": prompt}).strip()
                
                # Roteamento
                if rota == "WEB":
                    resposta, agente = get_agente_web(prompt, chat_history, foco)
                else:
                    resposta, agente = get_agente_rag(rota, prompt, chat_history, foco)
            except Exception as e:
                st.error("Instabilidade momentânea. Tente novamente.")
                st.stop()

        # Exibe e Salva
        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
        
        # Estado para PDF/Audio
        st.session_state.ultima_resposta = resposta
        st.session_state.ultima_pergunta = prompt
        st.session_state.ultimo_agente = agente
        
        # Gera Áudio Automático
        caminho_audio = gerar_audio(resposta)
        if caminho_audio:
            st.session_state.ultimo_audio = caminho_audio
            st.rerun()

# Botão de Download PDF (Centralizado no final)
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
            st.download_button(
                "📥 Baixar Conselho em PDF", 
                data=bytes(pdf_bytes), 
                file_name="conselho_biblico.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )
    except: pass