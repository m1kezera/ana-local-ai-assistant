import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

PADRAO_PATH = r"C:\ANA\data\padroes_sites.json"
MEMORIA_PATH = r"C:\ANA\data\memoria_interacao.json"

PALAVRAS_ACAO = ["download", "aceitar", "buscar", "submit", "start", "begin", "entrar"]

def carregar_padroes(site_nome):
    if not os.path.exists(PADRAO_PATH):
        return None
    with open(PADRAO_PATH, "r", encoding="utf-8") as f:
        todos = json.load(f)
    return todos.get(site_nome, {})

def carregar_memoria():
    if os.path.exists(MEMORIA_PATH):
        with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_memoria(memoria):
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

def agir_com_base_nos_padroes(driver, site_nome):
    padroes = carregar_padroes(site_nome)
    memoria = carregar_memoria()

    if not padroes:
        print(f"⚠️ Nenhum padrão salvo para '{site_nome}'.")
        return

    memoria[site_nome] = memoria.get(site_nome, [])
    clicados = 0

    for botao in padroes.get("botões", []):
        texto = (botao.get("text") or "").lower()
        if any(p in texto for p in PALAVRAS_ACAO) and botao not in memoria[site_nome]:
            sucesso = tentar_click(driver, botao)
            if sucesso:
                print(f"🤖 Ação realizada: clicou em '{texto}'.")
                memoria[site_nome].append(botao)
                clicados += 1
                time.sleep(2)

    salvar_memoria(memoria)
    print(f"🧠 Interação automática finalizada ({clicados} ações realizadas).")

def tentar_click(driver, padrao):
    try:
        if padrao["id"]:
            elem = driver.find_element(By.ID, padrao["id"])
        elif padrao["name"]:
            elem = driver.find_element(By.NAME, padrao["name"])
        elif padrao["class"]:
            classe = padrao["class"][0] if isinstance(padrao["class"], list) else padrao["class"]
            elem = driver.find_element(By.CLASS_NAME, classe)
        elif padrao["text"]:
            xpath = f"//button[contains(text(), '{padrao['text']}')]"
            elem = driver.find_element(By.XPATH, xpath)
        else:
            return False

        elem.click()
        return True
    except (NoSuchElementException, ElementNotInteractableException):
        return False
    except Exception as e:
        print(f"❌ Erro ao clicar: {e}")
        return False
