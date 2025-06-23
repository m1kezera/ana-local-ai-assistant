import os
import json
import faiss
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from datetime import datetime

VEC_PATH = "knowledge/embeddings/vector_data.json"
IDX_PATH = "knowledge/embeddings/vector.index"
MODEL_NAME = "all-MiniLM-L6-v2"
DB_NAME = "ANA_DB"
COL_NAME = "ebooks"

model = SentenceTransformer(MODEL_NAME)
index = None
texts = []
metadados = []
carregado = False

# MongoDB
mongo = MongoClient("mongodb://localhost:27017/")
db = mongo[DB_NAME]
if COL_NAME not in db.list_collection_names():
    db.create_collection(COL_NAME)
colecao = db[COL_NAME]

def carregar_base():
    global index, texts, metadados, carregado
    if carregado:
        return

    os.makedirs(os.path.dirname(VEC_PATH), exist_ok=True)

    if os.path.exists(IDX_PATH) and os.path.exists(VEC_PATH):
        try:
            index = faiss.read_index(IDX_PATH)
            with open(VEC_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                texts[:] = data.get("texts", [])
                metadados[:] = data.get("metadados", [])
            carregado = True
        except Exception as e:
            index = faiss.IndexFlatL2(384)
            texts.clear()
            metadados.clear()
            print(f"(⚠️ Falha ao carregar base vetorial existente: {e})")
    else:
        index = faiss.IndexFlatL2(384)
        texts.clear()
        metadados.clear()
        carregado = True

def salvar_base():
    faiss.write_index(index, IDX_PATH)
    with open(VEC_PATH, "w", encoding="utf-8") as f:
        json.dump({"texts": texts, "metadados": metadados}, f, ensure_ascii=False, indent=2)

def hash_arquivo(caminho):
    h = hashlib.sha1()
    with open(caminho, 'rb') as f:
        while True:
            bloco = f.read(8192)
            if not bloco:
                break
            h.update(bloco)
    return h.hexdigest()

def vetorizar_conhecimento(origem: str, texto: str):
    carregar_base()
    hash_doc = hash_arquivo(origem)

    if colecao.find_one({"hash": hash_doc}):
        print(f"⏩ {os.path.basename(origem)} já vetorizado.")
        return

    texto_limpo = texto.strip().replace("\n", " ")[:1000]
    vetor = model.encode([texto_limpo])
    index.add(np.array(vetor).astype("float32"))
    texts.append(texto_limpo)
    metadados.append({"origem": origem})
    salvar_base()

    colecao.insert_one({
        "nome": os.path.basename(origem),
        "hash": hash_doc,
        "data_indexacao": datetime.now(),
        "tamanho": os.path.getsize(origem),
        "vetorizado": True
    })
    print(f"🧠 Vetor aprendido com: {os.path.basename(origem)}")

def buscar_por_semelhanca(pergunta: str, top_k=3):
    carregar_base()
    if not texts:
        return ["(ℹ️ A base vetorial ainda está vazia. ANA precisa de mais aprendizado.)"]

    vetor_q = model.encode([pergunta])
    dist, idx = index.search(np.array(vetor_q).astype("float32"), top_k)

    resultados = []
    for i in idx[0]:
        if 0 <= i < len(texts):
            origem = metadados[i]["origem"]
            trecho = texts[i][:300]
            resultados.append(f"📖 Origem: {origem}\n📝 Trecho: {trecho}")
    return resultados if resultados else ["(Nenhum trecho relevante encontrado.)"]

def responder_por_semelhanca(pergunta: str):
    carregar_base()
    if not texts:
        return "📭 Ainda não tenho base suficiente para responder com vetores. Continue me ensinando!"

    vetor_q = model.encode([pergunta])
    dist, idx = index.search(np.array(vetor_q).astype("float32"), 1)
    i = idx[0][0]
    if 0 <= i < len(texts):
        origem = metadados[i]["origem"]
        resposta = texts[i][:400]
        return f"🔎 (Base vetorial: {os.path.basename(origem)})\n{resposta}"
    return "🔍 Nenhuma resposta similar foi encontrada na base vetorial."

def obter_estatisticas():
    carregar_base()
    return {
        "vetores": len(texts),
        "arquivos_lidos": len(set(m["origem"] for m in metadados))
    }
