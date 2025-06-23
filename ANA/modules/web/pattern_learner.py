import os
import json
from bs4 import BeautifulSoup

# Caminho base onde os padrões serão salvos
PADRAO_DIR = r"C:\ANA\data"
PADRAO_PATH = os.path.join(PADRAO_DIR, "padroes_sites.json")
os.makedirs(PADRAO_DIR, exist_ok=True)

PALAVRAS_CHAVE_UTEIS = ["login", "aceitar", "entrar", "buscar", "download", "submit", "next"]

def extrair_padroes(html, site_nome):
    soup = BeautifulSoup(html, "html.parser")
    padroes = {
        "botoes": [],
        "inputs": [],
        "links": []
    }

    # 🔘 Botões
    for btn in soup.find_all("button"):
        atr = _extrair_atributos(btn)
        if _padrao_util(atr):
            padroes["botoes"].append(atr)

    # 🔤 Inputs
    for inp in soup.find_all("input"):
        atr = _extrair_atributos(inp)
        if _padrao_util(atr):
            padroes["inputs"].append(atr)

    # 🔗 Links de download
    for link in soup.find_all("a", href=True):
        if any(ext in link["href"].lower() for ext in [".pdf", ".epub", "download"]):
            atr = _extrair_atributos(link)
            padroes["links"].append(atr)

    # 🔁 Remover duplicatas (baseado em conjunto de atributos úteis)
    for key in padroes:
        padroes[key] = _remover_duplicatas(padroes[key])

    _salvar_padroes(site_nome, padroes)
    return padroes

def _extrair_atributos(tag):
    return {
        "tag": tag.name,
        "text": tag.text.strip() if tag.text else "",
        "id": tag.get("id"),
        "class": tag.get("class"),
        "name": tag.get("name"),
        "placeholder": tag.get("placeholder"),
        "onclick": tag.get("onclick"),
        "href": tag.get("href"),
        "type": tag.get("type")
    }

def _padrao_util(atr):
    texto = (atr.get("text") or "") + " " + (atr.get("placeholder") or "") + " " + str(atr.get("name") or "")
    texto = texto.lower()
    return any(p in texto for p in PALAVRAS_CHAVE_UTEIS)

def _remover_duplicatas(lista):
    vistos = set()
    filtrados = []
    for item in lista:
        chave = (
            item.get("text"),
            item.get("id"),
            str(item.get("class")),
            item.get("name"),
            item.get("placeholder"),
            item.get("href"),
            item.get("onclick")
        )
        if chave not in vistos:
            vistos.add(chave)
            filtrados.append(item)
    return filtrados

def _salvar_padroes(site_nome, padroes):
    try:
        if os.path.exists(PADRAO_PATH):
            with open(PADRAO_PATH, "r", encoding="utf-8") as f:
                todos = json.load(f)
        else:
            todos = {}

        todos[site_nome] = padroes
        with open(PADRAO_PATH, "w", encoding="utf-8") as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)

        print(f"💾 Padrões salvos para o site '{site_nome}' com:")
        print(f"   → {len(padroes['botoes'])} botões, {len(padroes['inputs'])} inputs, {len(padroes['links'])} links")

    except Exception as e:
        print(f"❌ Erro ao salvar padrões: {e}")
