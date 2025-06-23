import os
import requests
from urllib.parse import urlparse
import logging

DOWNLOAD_DIR = "downloads/temp"

def baixar_arquivo(url):
    try:
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

        nome_arquivo = os.path.basename(urlparse(url).path)
        if not nome_arquivo:
            nome_arquivo = "arquivo_baixado.bin"

        caminho_completo = os.path.join(DOWNLOAD_DIR, nome_arquivo)

        if os.path.exists(caminho_completo):
            logging.info(f"📁 Arquivo já existe: {caminho_completo}")
            return {
                "status": "ok",
                "mensagem": f"🟡 Arquivo já existente: {nome_arquivo}",
                "dados": {"path": caminho_completo}
            }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        resposta = requests.get(url, headers=headers, stream=True, timeout=30)

        if resposta.status_code == 200:
            with open(caminho_completo, 'wb') as f:
                for bloco in resposta.iter_content(chunk_size=8192):
                    if bloco:
                        f.write(bloco)

            tamanho_mb = os.path.getsize(caminho_completo) / (1024**2)
            logging.info(f"✅ Download finalizado: {nome_arquivo} ({tamanho_mb:.2f} MB)")
            return {
                "status": "ok",
                "mensagem": f"✅ Download concluído: {nome_arquivo} ({tamanho_mb:.2f} MB)",
                "dados": {"path": caminho_completo}
            }

        else:
            logging.warning(f"⚠️ Falha no download de {url} - Código HTTP: {resposta.status_code}")
            return {
                "status": "erro",
                "mensagem": f"❌ Falha no download. Código HTTP: {resposta.status_code}",
                "dados": None
            }

    except Exception as e:
        logging.error(f"❌ Erro durante o download de {url}: {e}")
        return {
            "status": "erro",
            "mensagem": f"❌ Erro ao baixar arquivo: {str(e)}",
            "dados": None
        }

# Teste isolado
if __name__ == "__main__":
    url = "https://www.africau.edu/images/default/sample.pdf"
    print(baixar_arquivo(url))
