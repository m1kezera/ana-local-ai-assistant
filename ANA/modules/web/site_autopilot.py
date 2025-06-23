import os
import json
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException
)

# Caminho dos padrões aprendidos
PADRAO_PATH = r"C:\ANA\data\padroes_sites.json"

# Palavras-chave que indicam botões úteis
PALAVRAS_CLICAVEIS = ["aceitar", "accept", "download", "entrar", "login", "buscar", "submit", "get", "read", "continuar"]

def carregar_padroes(site_nome):
    if not os.path.exists(PADRAO_PATH):
        print("⚠️ Nenhum padrão encontrado.")
        return None

    try:
        with open(PADRAO_PATH, "r", encoding="utf-8") as f:
            todos = json.load(f)
        return todos.get(site_nome)
    except Exception as e:
        print(f"❌ Erro ao carregar padrões: {e}")
        return None

def interagir_com_pagina(driver, site_nome):
    padroes = carregar_padroes(site_nome)
    if not padroes:
        print(f"🚫 Nenhum padrão disponível para o site '{site_nome}'.")
        return

    print(f"🤖 Iniciando interação automática com base em padrões de '{site_nome}'.")

    clicados = 0

    # 🔘 Botões
    for botao in padroes.get("botões", []):
        texto = (botao.get("text") or "").lower()
        if any(p in texto for p in PALAVRAS_CLICAVEIS):
            if _tentar_click(driver, botao):
                print(f"✅ Botão '{texto}' clicado.")
                clicados += 1
                time.sleep(2)

    # 🔗 Links de download ou leitura
    for link in padroes.get("links", []):
        texto = (link.get("text") or "").lower()
        href = link.get("href")
        if href and any(p in texto or p in href for p in PALAVRAS_CLICAVEIS):
            if _tentar_click(driver, link, tag="a"):
                print(f"🔗 Link '{texto or href}' clicado.")
                clicados += 1
                time.sleep(2)

    if clicados == 0:
        print("ℹ️ Nenhum elemento relevante foi clicado.")
    else:
        print(f"🧠 Total de interações realizadas: {clicados}")

def _tentar_click(driver, padrao, tag="button"):
    try:
        if padrao["id"]:
            elem = driver.find_element(By.ID, padrao["id"])
        elif padrao["name"]:
            elem = driver.find_element(By.NAME, padrao["name"])
        elif padrao["class"]:
            classe = padrao["class"][0] if isinstance(padrao["class"], list) else padrao["class"]
            elem = driver.find_element(By.CLASS_NAME, classe)
        elif padrao["text"]:
            xpath = f"//{tag}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{padrao['text'].lower()}')]"
            elem = driver.find_element(By.XPATH, xpath)
        else:
            return False

        elem.click()
        return True
    except (NoSuchElementException, ElementNotInteractableException, WebDriverException):
        return False
    except Exception as e:
        print(f"❌ Erro ao clicar no elemento: {e}")
        return False
