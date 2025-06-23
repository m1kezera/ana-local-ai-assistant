# modules/memory/context_memory.py

import os
import json
from datetime import datetime

MEMORIA_PATH = r"C:\ANA\data\contexto_memoria.json"

class ContextoMemoria:
    def __init__(self):
        if not os.path.exists(os.path.dirname(MEMORIA_PATH)):
            os.makedirs(os.path.dirname(MEMORIA_PATH), exist_ok=True)
        self.memoria = self._carregar_memoria()

    def _carregar_memoria(self):
        if os.path.exists(MEMORIA_PATH):
            try:
                with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"historico": [], "resumos": []}
        return {"historico": [], "resumos": []}

    def salvar(self):
        with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
            json.dump(self.memoria, f, ensure_ascii=False, indent=2)

    def registrar_interacao(self, texto):
        entrada = {
            "tipo": "usuario",
            "texto": texto,
            "timestamp": str(datetime.now())
        }
        self.memoria["historico"].append(entrada)
        self._limitar_historico()
        self.salvar()

    def registrar_resposta(self, texto):
        resposta = {
            "tipo": "ana",
            "texto": texto,
            "timestamp": str(datetime.now())
        }
        self.memoria["historico"].append(resposta)
        self._limitar_historico()
        self.salvar()

    def salvar_conhecimento(self, resumo_texto):
        entrada = {
            "resumo": resumo_texto,
            "timestamp": str(datetime.now())
        }
        self.memoria["resumos"].append(entrada)
        self.salvar()

    def _limitar_historico(self, limite=50):
        self.memoria["historico"] = self.memoria["historico"][-limite:]

    def obter_ultimo_contexto(self):
        return self.memoria["historico"][-5:]

    def listar_resumos(self):
        return [r["resumo"] for r in self.memoria.get("resumos", [])]
