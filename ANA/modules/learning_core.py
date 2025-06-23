import os
import logging
import json
import fitz  # PyMuPDF
from ebooklib import epub
from bs4 import BeautifulSoup
from docx import Document
from PIL import Image
import pytesseract

from modules.knowledge.vector_core import vetorizar_conhecimento

LOG_LEARNING = os.path.join("C:", os.sep, "ANA", "logs", "learning_content.log")
INDEX_JSON = os.path.join("C:", os.sep, "ANA", "downloads", "ebooks_index.json")


def start_learning(base_path):
    logging.info(f"Iniciando varredura na pasta: {base_path}")
    print(f"📁 ANA está aprendendo sobre a pasta: {base_path}")

    for root, dirs, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()

            if ext == ".pdf":
                print(f"📘 Lendo PDF: {full_path}")
                aprender_de_pdf(full_path)
            elif ext == ".epub":
                print(f"📗 Lendo EPUB: {full_path}")
                aprender_de_epub(full_path)
            elif ext == ".docx":
                print(f"📙 Lendo DOCX: {full_path}")
                aprender_de_docx(full_path)
            elif ext == ".txt":
                print(f"📄 Lendo TXT: {full_path}")
                aprender_de_txt(full_path)
            elif ext in [".png", ".jpg", ".jpeg"]:
                print(f"🖼️ Lendo imagem via OCR: {full_path}")
                aprender_de_imagem(full_path)
            else:
                logging.info(f"🔍 Ignorado (formato não suportado ainda): {file}")

    logging.info("📚 Varredura concluída.")
    print("✅ Varredura concluída.")


def aprender_de_pdf(caminho):
    try:
        texto_total = ""
        doc = fitz.open(caminho)
        for pagina in doc:
            texto_total += pagina.get_text()

        _registrar_conteudo_aprendido(caminho, texto_total)
        vetorizar_conhecimento(caminho, texto_total)
        registrar_index_ebook(caminho, texto_total)

    except Exception as e:
        print(f"❌ Erro ao ler PDF: {caminho} → {str(e)}")
        logging.error(f"Erro PDF: {caminho} - {e}")


def aprender_de_epub(caminho):
    try:
        livro = epub.read_epub(caminho)
        texto = ""
        for item in livro.get_items():
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                texto += soup.get_text()

        _registrar_conteudo_aprendido(caminho, texto)
        vetorizar_conhecimento(caminho, texto)
        registrar_index_ebook(caminho, texto)

    except Exception as e:
        print(f"❌ Erro ao ler EPUB: {caminho} → {str(e)}")
        logging.error(f"Erro EPUB: {caminho} - {e}")


def aprender_de_docx(caminho):
    try:
        texto = ""
        doc = Document(caminho)
        for par in doc.paragraphs:
            texto += par.text + "\n"

        _registrar_conteudo_aprendido(caminho, texto)
        vetorizar_conhecimento(caminho, texto)
        registrar_index_ebook(caminho, texto)

    except Exception as e:
        print(f"❌ Erro ao ler DOCX: {caminho} → {str(e)}")
        logging.error(f"Erro DOCX: {caminho} - {e}")


def aprender_de_txt(caminho):
    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            texto = f.read()

        _registrar_conteudo_aprendido(caminho, texto)
        vetorizar_conhecimento(caminho, texto)
        registrar_index_ebook(caminho, texto)

    except Exception as e:
        print(f"❌ Erro ao ler TXT: {caminho} → {str(e)}")
        logging.error(f"Erro TXT: {caminho} - {e}")


def aprender_de_imagem(caminho):
    texto = usar_ocr_em_imagem(caminho)
    if texto:
        _registrar_conteudo_aprendido(caminho, texto)
        vetorizar_conhecimento(caminho, texto)
        registrar_index_ebook(caminho, texto)


def usar_ocr_em_imagem(caminho_imagem):
    try:
        imagem = Image.open(caminho_imagem)
        texto = pytesseract.image_to_string(imagem, lang='por+eng')
        return texto.strip()
    except Exception as e:
        print(f"❌ Erro ao executar OCR em {caminho_imagem}: {e}")
        logging.error(f"OCR erro: {caminho_imagem} - {e}")
        return ""


def _registrar_conteudo_aprendido(origem, texto):
    texto_limpo = texto.strip().replace("\n", " ")
    if not texto_limpo or len(texto_limpo) < 30:
        print(f"⚠️ Conteúdo muito pequeno ou vazio: {origem}")
        return

    trecho = texto_limpo[:3000]
    os.makedirs(os.path.dirname(LOG_LEARNING), exist_ok=True)

    with open(LOG_LEARNING, "a", encoding="utf-8") as log:
        log.write(f"\n--- {os.path.basename(origem)} ---\n")
        log.write(trecho)
        log.write("\n\n")

    print(f"✅ Aprendido: {os.path.basename(origem)}")
    logging.info(f"Aprendizado registrado: {origem}")


def registrar_index_ebook(caminho, texto):
    os.makedirs(os.path.dirname(INDEX_JSON), exist_ok=True)
    if os.path.exists(INDEX_JSON):
        with open(INDEX_JSON, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    else:
        index_data = {}

    nome = os.path.basename(caminho)
    origem = "desconhecida"
    if "pdfdrive" in caminho.lower():
        origem = "pdfdrive"
    elif "gutenberg" in caminho.lower():
        origem = "gutenberg"

    resumo = texto.strip().replace("\n", " ")[:600]

    index_data[nome] = {
        "origem": origem,
        "caminho": caminho,
        "resumo": resumo,
        "tema": "desconhecido"
    }

    with open(INDEX_JSON, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
