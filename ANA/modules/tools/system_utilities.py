# modules/tools/system_utilities.py

import os
import socket
import platform
import shutil
import subprocess
from pymongo import MongoClient
from modules.knowledge.autoindexer import classificar_temas

def verificar_conexao_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def obter_ip_local():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "🌐 IP local indisponível no momento."

def ping_google():
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        subprocess.check_output(["ping", param, "1", "8.8.8.8"], stderr=subprocess.DEVNULL)
        return "📡 Latência verificada com sucesso. ANA está conectada."
    except subprocess.CalledProcessError:
        return "❌ Falha ao pingar o Google. A conexão pode estar instável."

def conectar_mongodb():
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
        client.server_info()
        dbs = client.list_database_names()
        return f"✅ MongoDB conectado com sucesso.\n📁 Bases detectadas: {', '.join(dbs) if dbs else '(nenhuma encontrada)'}"
    except Exception as e:
        return f"❌ Erro ao conectar ao MongoDB:\n{e}"

def listar_ebooks_index():
    index_path = "downloads/ebooks/ebooks_index.json"
    if not os.path.exists(index_path):
        return "⚠️ Index de eBooks não encontrado. ANA ainda não aprendeu com nenhum."
    with open(index_path, "r", encoding="utf-8") as f:
        dados = f.read()
    return f"📘 Conteúdo atual de `ebooks_index.json`:\n\n{dados[:1500]}..."

def abrir_pasta_ebooks():
    pasta = os.path.abspath("downloads/ebooks/")
    try:
        if platform.system() == "Windows":
            os.startfile(pasta)
        elif platform.system() == "Darwin":
            subprocess.call(["open", pasta])
        else:
            subprocess.call(["xdg-open", pasta])
        return f"📂 Pasta de eBooks aberta: {pasta}"
    except Exception as e:
        return f"❌ Erro ao abrir a pasta de eBooks:\n{e}"

def rodar_indexador():
    try:
        classificar_temas()
        return "🧬 Indexação temática executada com sucesso. ANA está mais inteligente!"
    except Exception as e:
        return f"❌ Erro ao indexar os temas:\n{e}"

def limpar_tela_chat(chat_layout):
    for i in reversed(range(chat_layout.count())):
        widget = chat_layout.itemAt(i).widget()
        if widget:
            widget.setParent(None)
    return "🧹 Tela da conversa foi limpa com sucesso."

def espaco_disco_livre():
    try:
        total, usado, livre = shutil.disk_usage(os.getcwd())
        livre_gb = round(livre / (1024**3), 2)
        return f"💽 Espaço livre disponível no disco: {livre_gb} GB"
    except Exception as e:
        return f"❌ Falha ao verificar o espaço em disco:\n{e}"

def verificar_chats():
    try:
        from modules.tools.chat_checker import verificar_e_corrigir_chats
        resultado = verificar_e_corrigir_chats()
        resumo = f"✔️ Válidos: {resultado['validos']}\n❌ Corrompidos movidos: {resultado['corrompidos']}"
        if resultado["corrompidos"] > 0:
            resumo += "\n🧹 Arquivos corrompidos foram movidos para 'chats/corrompidos'."
        return resumo
    except Exception as e:
        return f"❌ Erro ao verificar chats:\n{e}"

def abrir_pasta_screenshots():
    caminho = r"C:\ANA\screenshots"
    if not os.path.exists(caminho):
        return "❌ Pasta de screenshots não encontrada."
    try:
        os.startfile(caminho)
        return "📸 Pasta de screenshots aberta com sucesso."
    except Exception as e:
        return f"❌ Falha ao abrir pasta de screenshots:\n{e}"
