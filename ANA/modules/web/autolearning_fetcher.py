import os
import time
import hashlib
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pymongo import MongoClient

from modules.web.ana_chromebot import ChromeBot
from modules.web.ana_downloader import baixar_arquivo
from modules.web.pattern_learner import extrair_padroes
from modules.web.web_brain import agir_com_base_nos_padroes
from modules.ana_core import AnaCore

BASE_DIR = r"C:\ANA"
LOG_PATH = os.path.join(BASE_DIR, "logs", "learning.log")
EBOOK_DIR_BASE = os.path.join(BASE_DIR, "downloads", "ebooks")

AUTO_SITES = [
    {
        "nome": "pdfdrive",
        "url": "https://www.pdfdrive.com/search?q=inteligencia+artificial",
        "download_host": "www.pdfdrive.com"
    },
    {
        "nome": "gutenberg",
        "url": "https://www.gutenberg.org/ebooks/search/?query=artificial+intelligence",
        "download_host": "www.gutenberg.org"
    }
]

PALAVRAS_CHAVE = ["inteligencia", "artificial", "machine", "deep", "neural", "python", "ai"]

def _hash_arquivo(path):
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def iniciar_auto_aprendizado():
    print("🧠 Iniciando aprendizado autônomo da ANA com fontes online...")
    ana = AnaCore()
    ana.nascer()

    for site in AUTO_SITES:
        print(f"\n🌐 Acessando site: {site['nome']}")
        pasta_site = os.path.join(EBOOK_DIR_BASE, site["nome"])
        os.makedirs(pasta_site, exist_ok=True)

        try:
            navegador = ChromeBot(headless=False)
            if not navegador.driver:
                raise Exception("Falha ao iniciar Chrome.")

            navegador.driver.get(site["url"])
            time.sleep(5)

            html = navegador.driver.page_source
            if len(html.strip()) < 100:
                raise Exception("Página carregada parece vazia.")

            _salvar_screenshot(site["nome"], navegador)
            _clicar_botao_aceitar(navegador)
            extrair_padroes(navegador.driver.page_source, site["nome"])
            agir_com_base_nos_padroes(navegador.driver, site["nome"])

            html = navegador.driver.page_source
            links_pdf = _buscar_links_pdf(html, site["download_host"])
            total = 0

            for link in links_pdf:
                nome_arquivo = os.path.basename(urlparse(link).path)
                if not any(p in nome_arquivo.lower() for p in PALAVRAS_CHAVE):
                    continue

                destino = os.path.join(pasta_site, nome_arquivo)
                if os.path.exists(destino):
                    print(f"📁 Já existe localmente: {nome_arquivo}")
                    if _hash_existente(destino):
                        print("🔁 Já registrado. Pulando...")
                        continue

                print(f"⬇️ Baixando: {nome_arquivo}")
                resultado = baixar_arquivo(link)

                if resultado.get("status") == "ok" and resultado.get("dados"):
                    caminho = resultado["dados"].get("path")
                    if not caminho or not os.path.exists(caminho):
                        print(f"⚠️ Caminho inválido para {nome_arquivo}. Pulando.")
                        continue

                    os.replace(caminho, destino)
                    if _hash_existente(destino):
                        print("🔁 Já registrado após mover. Pulando...")
                        continue

                    print(f"📚 Aprendendo com: {os.path.basename(destino)}")
                    ana.extrair_texto_pdf(destino)
                    ana.aprender_de_todos()  # ANA agora cuidará da indexação e do Mongo
                    _registrar_log(site["nome"], destino)
                    total += 1
                else:
                    print(f"❌ Falha ao baixar: {link}")

                time.sleep(2)

            print(f"✅ {total} arquivos processados de {site['nome']}")
            time.sleep(3)

        except Exception as e:
            print(f"❌ Erro ao processar site {site['nome']}: {e}")
        finally:
            try:
                navegador.driver.quit()
            except:
                pass

    print("\n🧠 Aprendizado automático finalizado.")

def _salvar_screenshot(site_nome, navegador):
    try:
        screenshot_dir = os.path.join(BASE_DIR, "screenshots", site_nome)
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        navegador.driver.save_screenshot(screenshot_path)
        print(f"📷 Screenshot salva: {screenshot_path}")
    except Exception as e:
        print(f"⚠️ Falha ao salvar screenshot: {e}")

def _buscar_links_pdf(html, base_host):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith(".pdf") or "download" in href:
            full_url = urljoin(f"https://{base_host}", href)
            links.append(full_url)
    return links

def _clicar_botao_aceitar(navegador):
    try:
        buttons = navegador.driver.find_elements("tag name", "button")
        for btn in buttons:
            texto = btn.text.strip().lower()
            if "aceitar" in texto or "accept" in texto:
                btn.click()
                print("🍪 Botão 'aceitar' clicado.")
                time.sleep(2)
                return
    except Exception:
        pass

def _registrar_log(site, arquivo_path):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] {site} → {arquivo_path}\n")

def _hash_existente(path):
    hash_val = _hash_arquivo(path)
    db = MongoClient("mongodb://localhost:27017/")["ANA_DB"]
    return db["ebooks"].find_one({"hash": hash_val}) is not None
