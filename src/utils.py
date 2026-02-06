import re
import asyncio
import edge_tts
import tempfile
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(139, 69, 19)
        self.cell(0, 10, 'BibliaGPT - Orientacao Espiritual', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def limpar_texto_seguro(texto):
    """Remove emojis e caracteres incompatíveis com PDF Latin-1."""
    substituicoes = {"🕊️": "", "🙏": "", "📖": "Livro:", "✨": "", "–": "-", "“": '"', "”": '"'}
    for k, v in substituicoes.items():
        texto = texto.replace(k, v)
    return texto.encode('latin-1', 'replace').decode('latin-1')

def criar_pdf_download(pergunta, resposta, foco, agente):
    pdf = PDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, limpar_texto_seguro(f"Duvida: {pergunta}"))
    
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 10, limpar_texto_seguro(f"Guia: {agente} | Modo: {foco}"))
    pdf.ln(5)
    
    # Resposta
    pdf.set_font("Times", "", 12)
    texto_limpo = limpar_texto_seguro(resposta)
    # Remove markdown básico
    texto_limpo = texto_limpo.replace("**", "").replace("### ", "").replace("---", "")
    pdf.multi_cell(0, 8, texto_limpo)
    
    return pdf.output(dest='S').encode('latin-1')

async def _gerar_audio_async(texto, output_file):
    communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural")
    await communicate.save(output_file)

def gerar_audio(texto):
    try:
        texto_limpo = re.sub(r'[*#_`]', '', texto)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            asyncio.run(_gerar_audio_async(texto_limpo, fp.name))
            return fp.name
    except: return None