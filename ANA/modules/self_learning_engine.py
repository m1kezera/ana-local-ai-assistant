import os
import time
from pymongo import MongoClient
from datetime import datetime
from modules.memory.context_memory import log_learning
from modules.interface_assistant import notify_user
from modules.ana_core import AnaCore

DB_NAME = "ANA_DB"
COLLECTION_NAME = "learning_logs"

client = MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

ana = AnaCore()
ana.nascer()

def register_learning(filename, resumo, origem):
    entry = {
        "file": filename,
        "origin": origem,
        "interpretation": resumo,
        "timestamp": datetime.now()
    }
    collection.insert_one(entry)
    log_learning(filename, resumo)
    notify_user(resumo)

def self_learning_loop():
    print("[ANA] Self-learning iniciado...")
    while True:
        aprendizados = ana.aprender_de_todos()
        for aprendizado in aprendizados:
            register_learning(
                aprendizado["arquivo"],
                aprendizado["resumo"],
                aprendizado["origem"]
            )
        time.sleep(60)

if __name__ == "__main__":
    self_learning_loop()