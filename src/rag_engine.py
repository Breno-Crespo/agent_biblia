import os
import streamlit as st  # <--- NOVO IMPORT
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# Garante carregamento das variáveis
load_dotenv()

INDEX_NAME = "bibliagpt-index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Cache para os Embeddings (Eles são pesados para carregar)
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def get_pinecone_client():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("🚨 ERRO: PINECONE_API_KEY não encontrada.")
        return None
    return Pinecone(api_key=api_key)

# Cache para o Retriever (Evita reconectar no Pinecone a cada clique)
@st.cache_resource(show_spinner=False)
def get_retriever(namespace):
    """Conecta ao Pinecone e retorna o buscador (com Cache)."""
    try:
        pc = get_pinecone_client()
        if not pc: return None
        
        index = pc.Index(INDEX_NAME)
        
        vectorstore = PineconeVectorStore(
            index=index,
            embedding=get_embeddings(),
            namespace=namespace
        )
        # Retorna o buscador
        return vectorstore.as_retriever()
    except Exception as e:
        print(f"❌ Erro ao conectar no Pinecone ({namespace}): {e}")
        return None