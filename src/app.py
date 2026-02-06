import os
import streamlit as st
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÃO INICIAL ---
load_dotenv(override=True)
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Importa as funções (certifique-se que os arquivos estão na mesma pasta)
from utils import criar_pdf_download, gerar_audio
from agents import get_supervisor_chain, get_agente_web, get_agente_rag

# --- 2. LAYOUT E ESTILO ---
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
    .stSidebar { background-color: #f5f5f5; border-right: 1px solid #ddd; }
    .history-btn { text-align: left; font-size: 0.8rem; padding: 5px; color: #555; }
</style>
""", unsafe_allow_html=True)

# --- 3. SISTEMA DE SEGURANÇA (LOGIN) ---
def check_password():
    """Retorna True se o usuário digitou a senha correta."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # Campo de senha
    st.markdown("<h1 style='text-align: center;'>🔒 Área Restrita</h1>", unsafe_allow_html=True)
    st.write(" ")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Digite a Senha de Acesso:", type="password")
        if st.button("Entrar"):
            # Verifica se a senha bate com a config (Local ou Secrets)
            senha_secreta = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD")
            
            if pwd == senha_secreta:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("🚫 Senha incorreta.")
    return False

if not check_password():
    st.stop()  # Para tudo se não tiver senha

# --- 4. SIDEBAR (Histórico e Controles) ---
with st.sidebar:
    st.markdown("### 🕊️ BibliaGPT")
    
    # Seletor de Modo
    opcoes = {
        "Devocional": "🙏 **Pastoral:** Conforto e direção.",
        "Teológico": "📚 **Ensino:** Profundidade doutrinária.",
        "Histórico": "🌍 **Contexto:** Cultura e fatos.",
    }
    foco = st.radio("Modo:", list(opcoes.keys()))
    st.caption(opcoes[foco])
    st.markdown("---")
    
    # HISTÓRICO VISUAL (Igual Gemini)
    st.markdown("#### 🕒 Histórico Recente")
    if "messages" in st.session_state:
        # Pega as mensagens do usuário, inverte a ordem (mais recente primeiro)
        for i, msg in enumerate(reversed(st.session_state.messages)):
            if msg["role"] == "user":
                # Mostra apenas os primeiros 30 caracteres
                texto_curto = (msg["content"][:30] + '...') if len(msg["content"]) > 30 else msg["content"]
                st.markdown(f"🔹 *{texto_curto}*")
    
    st.markdown("---")
    
    # Botões de Ação
    if "ultima_resposta" in st.session_state and st.session_state.ultima_resposta:
        try:
            pdf_bytes = criar_pdf_download(
                st.session_state.ultima_pergunta,
                st.session_state.ultima_resposta,
                foco,
                st.session_state.ultimo_agente
            )
            st.download_button("📄 Baixar PDF", data=bytes(pdf_bytes), file_name="conselho.pdf", mime="application/pdf")
        except: pass
        
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.clear()
        st.session_state.password_correct = True # Mantém logado
        st.rerun()

# --- 5. CHAT PRINCIPAL ---
st.title("Sua Paz Diária")
st.caption(f"Guiado pelo Espírito de: {foco}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "A paz! Como posso ajudar seu coração hoje?"}]

# Exibe mensagens
for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="🕊️" if msg["role"] == "assistant" else "👤").write(msg["content"])

# Player de Áudio
if "ultimo_audio" in st.session_state and st.session_state.ultimo_audio:
    st.audio(st.session_state.ultimo_audio, format="audio/mp3")

# Input do Usuário
prompt = st.chat_input("Escreva sua dúvida ou aflição...")

if prompt:
    # Segurança: Limita tamanho da pergunta para evitar injeção gigante
    if len(prompt) > 500:
        st.error("Sua mensagem é muito longa. Por favor, resuma em até 500 caracteres.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)
    st.session_state.ultimo_audio = None
    
    # Histórico Otimizado (Cache de Memória)
    mensagens_totais = [msg for msg in st.session_state.messages if msg["role"] != "system"]
    chat_history = mensagens_totais[-6:] # Janela de contexto (últimas 6)

    with st.chat_message("assistant", avatar="🕊️"):
        with st.status("🙏 Buscando discernimento...", expanded=True) as status:
            try:
                # Cache de Recurso para evitar re-conexão
                # (A lógica de cache está no rag_engine.py, aqui chamamos normal)
                supervisor = get_supervisor_chain()
                rota = supervisor.invoke({"input": prompt}).strip()
                
                if rota == "WEB":
                    status.write("🌍 Olhando para o mundo...")
                    resposta, agente = get_agente_web(prompt, chat_history, foco)
                else:
                    status.write("📖 Abrindo as Escrituras...")
                    resposta, agente = get_agente_rag(rota, prompt, chat_history, foco)
                
                status.update(label="✨ Resposta encontrada", state="complete", expanded=False)
                
            except Exception as e:
                st.error(f"Erro técnico: {e}")
                st.stop()

        # Renderiza Resposta
        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
        
        # Salva estado para PDF/Áudio
        st.session_state.ultima_resposta = resposta
        st.session_state.ultima_pergunta = prompt
        st.session_state.ultimo_agente = agente
        
        # Gera Áudio
        caminho_audio = gerar_audio(resposta)
        if caminho_audio:
            st.session_state.ultimo_audio = caminho_audio
            st.rerun()