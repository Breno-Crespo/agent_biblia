import os
import streamlit as st
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL ---
# Carrega variáveis e previne conflitos com LangSmith
load_dotenv(override=True)
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from utils import criar_pdf_download, gerar_audio
from agents import get_supervisor_chain, get_agente_web, get_agente_rag

# --- LAYOUT E ESTILO ---
st.set_page_config(page_title="BibliaGPT - Conselheiro", page_icon="🕊️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&family=Lato:wght@400;700&display=swap');
    .stApp { background-color: #fdfbf7; }
    div[data-testid="stChatMessageContent"] {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 5px solid #DAA520;
        font-family: 'Lato', sans-serif; color: #2c3e50;
    }
    h1, h2, h3 { font-family: 'Merriweather', serif; color: #5c4033; }
    .stButton>button { 
        width: 100%; border-radius: 8px; border: 1px solid #8B4513; 
        color: #8B4513; background: transparent; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #8B4513; color: white; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #DAA520;'>🕊️ BibliaGPT</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    opcoes = {
        "Devocional": "🙏 **Pastoral:** Conforto e direção para a alma.",
        "Teológico": "📚 **Ensino:** Profundidade doutrinária.",
        "Histórico": "🌍 **Contexto:** Cultura e fatos da época.",
    }
    foco = st.radio("Modo de Conselho:", list(opcoes.keys()))
    st.info(opcoes[foco])
    
    # Área de Download do PDF
    if "ultima_resposta" in st.session_state and st.session_state.ultima_resposta:
        st.markdown("---")
        try:
            pdf_bytes = criar_pdf_download(
                st.session_state.ultima_pergunta,
                st.session_state.ultima_resposta,
                foco,
                st.session_state.ultimo_agente
            )
            st.download_button("📄 Baixar Conselho (PDF)", data=bytes(pdf_bytes), file_name="conselho_biblico.pdf", mime="application/pdf")
        except Exception: 
            pass # Falha silenciosa no PDF para não quebrar a UI
    
    if st.button("🗑️ Nova Conversa"):
        st.session_state.clear()
        st.rerun()

# --- CHAT PRINCIPAL ---
st.title("🕊️ Seu Espaço de Paz e Sabedoria")
st.caption(f"Guiado pelo Espírito de: {foco}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "A paz! Como está seu coração hoje? Estou aqui para te ouvir."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="🕊️" if msg["role"] == "assistant" else "👤").write(msg["content"])

# Player de Áudio (se existir)
if "ultimo_audio" in st.session_state and st.session_state.ultimo_audio:
    st.markdown("---")
    st.audio(st.session_state.ultimo_audio, format="audio/mp3")

# --- LÓGICA DE PROCESSAMENTO ---
prompt = st.chat_input("Conte-me o que te aflige ou qual sua dúvida...")

if prompt:
    # 1. Exibe pergunta do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)
    st.session_state.ultimo_audio = None # Limpa audio anterior
    
    # 2. Histórico para o Agente
    chat_history = [msg for msg in st.session_state.messages if msg["role"] != "system"]

    with st.chat_message("assistant", avatar="🕊️"):
        with st.status("🙏 Buscando discernimento...", expanded=True) as status:
            try:
                # Decisão do Supervisor
                supervisor = get_supervisor_chain()
                rota = supervisor.invoke({"input": prompt}).strip()
                
                if rota == "WEB":
                    status.write("🌍 Analisando contexto atual...")
                    resposta, agente = get_agente_web(prompt, chat_history, foco)
                else:
                    status.write("📖 Consultando as Escrituras...")
                    resposta, agente = get_agente_rag(rota, prompt, chat_history, foco)
                
                status.update(label="✨ Uma palavra foi encontrada.", state="complete", expanded=False)
                
                # Salva estado temporário
                st.session_state.temp_res = resposta
                st.session_state.temp_agente = agente
                
            except Exception as e:
                st.error(f"Perdão, houve um erro técnico: {e}")
                st.stop()

        # 3. Exibição e Pós-Processamento
        if "temp_res" in st.session_state:
            resposta = st.session_state.temp_res
            st.write(resposta)
            
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            st.session_state.ultima_resposta = resposta
            st.session_state.ultima_pergunta = prompt
            st.session_state.ultimo_agente = st.session_state.temp_agente
            
            # Gera Áudio em background
            caminho_audio = gerar_audio(resposta)
            if caminho_audio:
                st.session_state.ultimo_audio = caminho_audio
                st.rerun()