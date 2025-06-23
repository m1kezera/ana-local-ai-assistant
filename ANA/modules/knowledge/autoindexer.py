import os
import json
import spacy

INDEX_PATH = "downloads/ebooks_index.json"
nlp = spacy.load("en_core_web_sm")

# Lista de possíveis temas-chave
TEMAS_RELEVANTES = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural networks",
    "python",
    "data science",
    "programming",
    "statistics",
    "algorithms",
    "robotics"
]

def classificar_temas():
    if not os.path.exists(INDEX_PATH):
        print("⚠️ Nenhum index encontrado.")
        return

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    atualizados = 0

    for nome, dados in index_data.items():
        if dados.get("tema") != "desconhecido":
            continue  # já classificado

        resumo = dados.get("resumo", "").lower()
        doc = nlp(resumo)

        tema_detectado = detectar_tema(doc)
        if tema_detectado:
            index_data[nome]["tema"] = tema_detectado
            atualizados += 1
            print(f"📌 Tema identificado para '{nome}': {tema_detectado}")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"✅ {atualizados} temas atualizados no index.")

def detectar_tema(doc):
    texto = doc.text.lower()
    for tema in TEMAS_RELEVANTES:
        if tema in texto:
            return tema
    return "desconhecido"

# Teste direto
if __name__ == "__main__":
    classificar_temas()
