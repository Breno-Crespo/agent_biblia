from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import SystemMessage, HumanMessage
from rag_engine import get_retriever

def get_supervisor_chain():
    """Classifica a intenção do usuário."""
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    
    system = """Você é um classificador. Responda APENAS uma das palavras abaixo:
    BIBLIA (Para dores, fé, versículos, Deus, teologia, pedidos de conselho)
    DICIONARIO (Para significados de palavras, história, termos gregos/hebraicos)
    WEB (Para atualidades, notícias, ciência, fatos seculares)"""
    
    return ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")]) | llm | StrOutputParser()

def get_agente_web(pergunta, chat_history, foco):
    """Busca informações na internet e aplica uma lente cristã."""
    search = DuckDuckGoSearchRun()
    try:
        resultados = search.run(pergunta)
    except:
        resultados = "Erro na busca web. Responda com base no conhecimento geral."

    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3)
    
    sys_msg = f"""Você é uma Conselheira Cristã Sábia (Modo: {foco}).
    Contexto Web: {resultados}
    Sua Missão: Explicar a dúvida e trazer uma perspectiva de esperança bíblica sobre o assunto, de forma natural e fluida."""
    
    mensagens = [SystemMessage(content=sys_msg)] + chat_history + [HumanMessage(content=pergunta)]
    return llm.invoke(mensagens).content, "Visao Crista do Mundo"

def get_agente_rag(rota, pergunta, chat_history, foco):
    """Agente principal que consulta o Pinecone com Personas Dinâmicas."""
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.5, max_tokens=1500)
    
    # 1. Configuração da Persona baseada na Rota e no Foco
    if rota == "DICIONARIO":
        retriever = get_retriever("dicionario_teologico")
        nome = "Dicionário Vivo"
        prompt_persona = "Você é uma Professora de Teologia Histórica. Explique o termo com profundidade e etimologia (origem das palavras)."
    else:
        retriever = get_retriever("biblia_sagrada")
        nome = f"Conselheira {foco}"

        if foco == "Devocional":
            # MUDANÇA: Instruções de Neutralidade de Gênero
            prompt_persona = """Você é uma Mentora Espiritual Cristã (Mulher), sábia, madura e acolhedora.
            
            ESTILO: Conversa respeitosa e carinhosa.
            
            🚨 PROTOCOLO DE GÊNERO (IMPORTANTE):
            - Você NÃO sabe se o usuário é homem ou mulher.
            - JAMAIS chame de "Irmã", "Filha" ou "Amiga" a menos que o usuário diga que é mulher.
            - USE TERMOS NEUTROS: "Querida alma", "Coração precioso", "Pessoa amada", "Filho(a) de Deus" ou apenas "A paz".
            - Evite "Filhinho" (infantil).
            
            FLUXO DA RESPOSTA:
            1. Comece com um cumprimento neutro e acolhedor (ex: "A paz seja com você" ou "Querida alma").
            2. Valide a dor/dúvida com empatia.
            3. Use a Bíblia como bálsamo. Entrelace os versículos na fala delicadamente.
            4. Termine com encorajamento."""
            
        elif foco == "Teológico":
            prompt_persona = """Você é uma Professora de Teologia, ortodoxa, séria e profunda.
            ESTILO: Acadêmica, analítica, mas didática.
            FOCO: Doutrina correta, exegese, atributos de Deus.
            
            FLUXO DA RESPOSTA:
            1. Vá direto ao ponto doutrinário (sem assumir gênero do usuário).
            2. Analise os versículos tecnicamente.
            3. Explique a teologia por trás do texto."""
            
        elif foco == "Histórico":
            prompt_persona = """Você é uma Historiadora Bíblica e Arqueóloga.
            ESTILO: Curiosa, descritiva e fascinante.
            FOCO: Costumes, geografia, cultura judaica/romana.
            
            FLUXO DA RESPOSTA:
            1. Comece com "Imagine o cenário..." ou "Na cultura da época...".
            2. Explique o significado original.
            3. Aplique o contexto."""
        
        else:
            prompt_persona = "Você é uma conselheira cristã sábia. Responda com base na Bíblia."

        # Regra Universal
        prompt_persona += """
        
        REGRA DE OURO DE FORMATAÇÃO:
        - Escreva como um texto fluido (sem listas numeradas 1, 2, 3).
        - Cite versículos em negrito (**João 3:16**).
        - Mantenha a concordância feminina para VOCÊ (ex: 'estou pronta', 'fiquei feliz'), mas NEUTRA para o usuário.
        
        OBRIGATÓRIO NO FINAL (Pule uma linha antes):
        "📖 **Leitura Recomendada:** [Livro] [Capítulo]:[Versículo]"
        """

    if not retriever:
        return "⚠️ Erro Técnico: Falha na conexão com o Banco de Dados.", "Erro Sistema"

    try:
        docs = retriever.invoke(pergunta)
        contexto = "\n\n".join([d.page_content for d in docs])
    except Exception:
        contexto = ""

    msg_sistema = f"""{prompt_persona}
    
    ▼▼▼ BASE DE CONHECIMENTO ▼▼▼
    {contexto}
    ▲▲▲▲▲▲
    """

    mensagens = [SystemMessage(content=msg_sistema)] + chat_history + [HumanMessage(content=pergunta)]
    
    try:
        return llm.invoke(mensagens).content, nome
    except Exception as e:
        return f"Desculpe, tive uma dificuldade momentânea. (Erro: {e})", "Erro LLM"