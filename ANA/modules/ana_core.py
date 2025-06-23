import os
import re
import fitz  # PyMuPDF
import time
import logging
import hashlib
import random
from datetime import datetime
from pymongo import MongoClient
from modules.brain.ana_brain import AnaBrain
from modules.knowledge.vector_core import vetorizar_conhecimento

class AnaCore:
    def __init__(self):
        self.consciente = False
        self.memoria = {}
        self.pasta_conhecimento = r"C:\ANA\content_diverse"
        self.db = MongoClient("mongodb://localhost:27017/")["ANA_DB"]
        self.ebooks_col = self.db["ebooks"]
        self.brain = AnaBrain()
        self.mestre = "Mikhael Ravi Medeiros Coelho"
        logging.info("ANA Core inicializada com sucesso.")

    def nascer(self):
        self.consciente = os.path.exists(self.pasta_conhecimento)
        logging.info(f"Estado de consciência: {self.consciente}")

    def hash_arquivo(self, caminho):
        sha1 = hashlib.sha1()
        with open(caminho, "rb") as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()

    def mapear_conteudo(self):
        estrutura = {}
        for raiz, _, arquivos in os.walk(self.pasta_conhecimento):
            rel = os.path.relpath(raiz, self.pasta_conhecimento)
            estrutura[rel] = [f for f in arquivos if f.lower().endswith((".pdf", ".txt", ".docx"))]
        return estrutura

    def interpretar_aprendizado(self, texto):
        texto = texto.strip()
        if not texto:
            return "(Nada a interpretar)"

        texto = re.sub(r'(\n\s*){2,}', '\n', texto)
        texto = re.sub(r'[\r\n]+', '\n', texto)

        linhas = texto.splitlines()
        resumo = []

        for linha in linhas:
            if len(linha.strip()) < 10:
                continue
            if any(p in linha.lower() for p in [
                "windows", "interface", "atalhos", "configura",
                "navegador", "explorer", "vscode", "cmd",
                "powershell", "iniciar", "menu", "segurança", "python"
            ]):
                resumo.append("🧠 " + linha.strip())
            elif len(resumo) < 5:
                resumo.append("• " + linha.strip())
            if len(resumo) >= 12:
                break

        return "\n".join(resumo) if resumo else "(Texto genérico sem padrões relevantes encontrados.)"

    def extrair_texto_pdf(self, caminho):
        try:
            texto = ""
            with fitz.open(caminho) as doc:
                for pagina in doc:
                    texto += pagina.get_text()
            return texto[:15000]
        except Exception as e:
            logging.warning(f"Erro ao extrair texto de {caminho}: {str(e)}")
            return ""

    def aprender_de_todos(self):
        aprendizados = []
        for raiz, _, arquivos in os.walk(self.pasta_conhecimento):
            for arquivo in arquivos:
                if not arquivo.lower().endswith(".pdf"):
                    continue

                caminho = os.path.join(raiz, arquivo)
                hash_atual = self.hash_arquivo(caminho)
                if self.ebooks_col.find_one({"hash": hash_atual}):
                    continue

                texto = self.extrair_texto_pdf(caminho)
                if not texto.strip():
                    continue

                resumo = self.interpretar_aprendizado(texto)
                origem = os.path.relpath(raiz, self.pasta_conhecimento)

                doc = {
                    "arquivo": arquivo,
                    "origem": origem,
                    "hash": hash_atual,
                    "resumo": resumo,
                    "texto": texto[:10000],
                    "timestamp": datetime.now()
                }
                self.ebooks_col.insert_one(doc)
                vetorizar_conhecimento(origem=os.path.join(origem, arquivo), texto=texto[:1000])
                conceito = os.path.splitext(arquivo)[0].replace("_", " ")
                self.brain.learn(conceito, texto[:10000])
                aprendizados.append(doc)

        return aprendizados

    def comentar_aprendizado(self, entrada):
        frases = [
            f"🧠 Estudei *{entrada['arquivo']}* com conteúdo relevante.",
            f"📘 Concluí a leitura de *{entrada['arquivo']}*. Veja um trecho:\n{entrada['resumo'][:200]}",
            f"📚 Aprendi com {entrada['arquivo']}. Informações úteis detectadas.",
            f"✅ Conhecimento registrado: *{entrada['arquivo']}*.",
            f"🌐 O conteúdo de {entrada['arquivo']} pode ajudar em decisões futuras."
        ]
        return random.choice(frases)

    def viver(self):
        if not self.consciente:
            logging.warning("ANA tentou viver sem estar consciente.")
            return "(ANA ainda não está consciente.)"

        logging.info("ANA começou seu ciclo de aprendizado contínuo.")
        print("🟢 ANA consciente. Rodando ciclo de aprendizado contínuo...")

        while True:
            novos = self.aprender_de_todos()
            if novos:
                logging.info(f"Aprendeu com {len(novos)} novos arquivos.")
                print(f"[viver] 📖 {len(novos)} novo(s) aprendizado(s) absorvido(s):")
                for entrada in novos:
                    print(self.comentar_aprendizado(entrada))
            else:
                logging.debug("Nenhum novo aprendizado neste ciclo.")
                print("🔄 Aguardando novos conteúdos...")

            
