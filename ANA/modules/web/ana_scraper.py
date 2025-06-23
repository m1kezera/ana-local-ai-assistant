import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from PIL import Image
from io import BytesIO
import logging

from modules.learning_core import usar_ocr_em_imagem

DOWNLOAD_IMG_DIR = "downloads/temp"

def extrair_dados_do_site(url):
    try:
        logging.info(f"🔎 Extraindo dados do site: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return {
                "status": "erro",
                "mensagem": f"❌ Falha ao acessar o site (HTTP {response.status_code})",
                "dados": None
            }

        soup = BeautifulSoup(response.text, 'html.parser')
        textos = soup.get_text(separator=' ', strip=True)

        imagem_url = None
        imagem_path = None
        texto_ocr = None

        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.lower().endswith(('.svg', '.gif')):
                imagem_url = urljoin(url, src)
                break

        if imagem_url:
            os.makedirs(DOWNLOAD_IMG_DIR, exist_ok=True)
            nome_arquivo = os.path.basename(urlparse(imagem_url).path) or "imagem_extraida.jpg"
            imagem_path = os.path.join(DOWNLOAD_IMG_DIR, nome_arquivo)

            try:
                img_response = requests.get(imagem_url, headers=headers, stream=True, timeout=15)
                if img_response.status_code == 200:
                    img = Image.open(BytesIO(img_response.content)).convert("RGB")
                    img.save(imagem_path)
                    texto_ocr = usar_ocr_em_imagem(imagem_path)
                    logging.info(f"🖼️ Imagem baixada e OCR aplicado: {imagem_path}")
                else:
                    imagem_path = None
            except Exception as img_err:
                logging.warning(f"Erro ao processar imagem: {img_err}")
                imagem_path = None
                texto_ocr = f"(Erro ao processar imagem: {img_err})"

        dados_extraidos = {
            "url": url,
            "texto_extraido": textos[:5000],
            "imagem_detectada": bool(imagem_path),
            "imagem_url": imagem_url,
            "imagem_path": imagem_path,
            "ocr_texto": texto_ocr or ""
        }

        return {
            "status": "ok",
            "mensagem": "✅ Dados extraídos com sucesso.",
            "dados": dados_extraidos
        }

    except Exception as e:
        logging.error(f"❌ Erro ao extrair dados do site: {e}")
        return {
            "status": "erro",
            "mensagem": f"Erro ao extrair dados: {str(e)}",
            "dados": None
        }

# Teste isolado
if __name__ == "__main__":
    resultado = extrair_dados_do_site("https://www.exemplo.com")
    print(resultado)

    if resultado.get("dados", {}).get("imagem_detectada"):
        print("Texto OCR:", resultado["dados"].get("ocr_texto", "")[:500])
