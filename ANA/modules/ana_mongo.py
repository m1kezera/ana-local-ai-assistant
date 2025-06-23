# modules/ana_mongo.py

import os
import threading
import requests
from pymongo import MongoClient
from datetime import datetime

BASE_DIR = r"C:\ANA\content_diverse"
EBOOKS_DIR = os.path.join(BASE_DIR, "ebooks")
LOG_FILE = os.path.join(BASE_DIR, "logs", "ana_mongo.log")
MONGO_URI = "mongodb://localhost:27017"  # Ajuste conforme necessário

MONGO_EBOOKS = [
    {
        "title": "The Little MongoDB Book",
        "url": "https://openmymind.net/mongodb.pdf"
    },
    {
        "title": "MongoDB: The Definitive Guide",
        "url": "https://pepa.holla.cz/wp-content/uploads/2016/07/MongoDB-The-Definitive-Guide-2nd-Edition.pdf"
    }
]

def _log(msg):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def baixar_ebooks_mongo():
    os.makedirs(EBOOKS_DIR, exist_ok=True)
    for ebook in MONGO_EBOOKS:
        path = os.path.join(EBOOKS_DIR, ebook['title'] + ".pdf")
        if not os.path.exists(path):
            try:
                r = requests.get(ebook['url'], timeout=30)
                with open(path, "wb") as f:
                    f.write(r.content)
                _log(f"E-book baixado: {ebook['title']}")
                print(f"📚 E-book baixado: {ebook['title']}")
            except Exception as e:
                _log(f"Erro ao baixar {ebook['title']}: {e}")
        else:
            _log(f"E-book já existente: {ebook['title']}")

def conectar_e_explorar(chat_callback=None):
    try:
        client = MongoClient(MONGO_URI)
        dbs = client.list_database_names()
        msg = f"🔌 Conectado ao MongoDB. Bancos encontrados: {dbs}"
        _log(msg)
        if chat_callback:
            chat_callback(msg)

        for db_name in dbs:
            db = client[db_name]
            cols = db.list_collection_names()
            info = f"📁 DB '{db_name}': coleções = {cols}"
            _log(info)
            if chat_callback:
                chat_callback(info)
            for col in cols:
                count = db[col].count_documents({})
                detail = f"  - '{db_name}.{col}': {count} documentos"
                _log(detail)
                if chat_callback:
                    chat_callback(detail)
        client.close()
    except Exception as e:
        err = f"❌ Falha ao conectar/explorar MongoDB: {e}"
        _log(err)
        if chat_callback:
            chat_callback(err)

def self_setup(chat_callback=None):
    _log("Inicializando módulo ana_mongo...")
    t1 = threading.Thread(target=baixar_ebooks_mongo)
    t2 = threading.Thread(target=conectar_e_explorar, args=(chat_callback,))
    t1.start(); t2.start()
    t1.join(); t2.join()
    final = "✅ ana_mongo configurado: ebooks baixados e MongoDB explorado."
    _log(final)
    if chat_callback:
        chat_callback(final)
