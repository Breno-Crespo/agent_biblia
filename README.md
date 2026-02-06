# 🕊️ BibliaGPT - Conselheiro Teológico com IA

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)
![Groq](https://img.shields.io/badge/AI-Llama3.3_70B-orange)

O **BibliaGPT** é um Assistente Espiritual e Teológico alimentado por Inteligência Artificial. Diferente de chatbots genéricos, ele utiliza **RAG (Retrieval-Augmented Generation)** para consultar uma base de dados vetorial contendo a Bíblia Sagrada e Dicionários Teológicos, garantindo respostas fundamentadas, acolhedoras e precisas.

## ✨ Funcionalidades

* **🧠 Inteligência Pastoral:** Utiliza o modelo **Llama 3.3 70B** (via Groq) para gerar respostas profundas, empáticas e teologicamente ricas.
* **🔍 RAG Avançado:** Busca versículos e explicações em tempo real em um banco de dados vetorial (**Pinecone**), reduzindo alucinações.
* **🎯 Modos de Atuação:**
    * 🙏 **Devocional:** Foco em conforto emocional e direção espiritual.
    * 📚 **Teológico:** Explicações doutrinárias profundas.
    * 🌍 **Histórico:** Contexto cultural e fatos da época bíblica.
* **🔊 Voz de Conforto:** Gera áudio da resposta automaticamente para acessibilidade (Edge TTS).
* **📄 PDF Export:** Permite baixar a orientação espiritual em formato PDF para leitura offline.
* **🌐 Agente Web:** Capaz de buscar notícias atuais na internet e analisá-las sob uma ótica cristã.

## 🛠️ Tecnologias Utilizadas

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Orquestração de IA:** [LangChain](https://www.langchain.com/)
* **LLM (Cérebro):** Groq API (Llama-3.3-70b-versatile)
* **Banco de Dados Vetorial:** [Pinecone](https://www.pinecone.io/) (Serverless)
* **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
* **Áudio:** Edge-TTS
* **Deploy:** Streamlit Community Cloud

## 🚀 Como Rodar Localmente

Siga os passos abaixo para executar o projeto na sua máquina.

### 1. Clone o repositório
```bash
git clone [https://github.com/SEU_USUARIO/biblia-gpt.git](https://github.com/SEU_USUARIO/biblia-gpt.git)
cd biblia-gpt