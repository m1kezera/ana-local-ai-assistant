# modules/mongo_core.py

import os
import requests
from pymongo import MongoClient
from datetime import datetime

BASE_DIR = os.getenv("ANA_BASE_DIR", r"C:\ANA")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads", "ebooks", "mongo")
LOG_PATH = os.path.join(BASE_DIR, "logs", "mongo_core.log")
MONGO_URI = os.getenv("ANA_MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("ANA_DB_NAME", "ANA_DB")

class MongoCore:
    def __init__(self):
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.log("MongoCore iniciado e conectado a ANA_DB.")

    def log(self, msg: str):
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")

    def listar_collections(self):
        cols = self.db.list_collection_names()
        self.log(f"Listando coleções: {cols}")
        return cols

    def contar_documentos(self, collection: str):
        count = self.db[collection].count_documents({})
        self.log(f"Contagem em '{collection}': {count} docs")
        return count

    def diagnosticar_db(self):
        info = {}
        for col in self.listar_collections():
            info[col] = self.contar_documentos(col)
        return info

    def baixar_ebook_mongo(self):
        url = "https://downloads.mongodb.com/docs/mongodb-v6.0.pdf"
        local = os.path.join(DOWNLOADS_DIR, "mongodb_manual_v6.pdf")
        if not os.path.exists(local):
            r = requests.get(url)
            if r.status_code == 200:
                with open(local, "wb") as f:
                    f.write(r.content)
                self.log("📥 Manual MongoDB v6 baixado.")
                return local
            else:
                self.log(f"❌ Falha ao baixar manual MongoDB: HTTP {r.status_code}")
                return None
        self.log("📁 Manual MongoDB já existente.")
        return local
