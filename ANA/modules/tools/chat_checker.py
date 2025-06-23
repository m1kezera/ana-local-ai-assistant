import os
import json

CHAT_DIR = "chats/"
CORROMPIDOS_DIR = os.path.join(CHAT_DIR, "corrompidos")
os.makedirs(CORROMPIDOS_DIR, exist_ok=True)

def verificar_e_corrigir_chats():
    total = 0
    corrompidos = 0
    detalhes = []

    for arquivo in os.listdir(CHAT_DIR):
        if not arquivo.endswith(".json"):
            continue

        caminho = os.path.join(CHAT_DIR, arquivo)

        # Ignorar diretórios (inclusive "corrompidos")
        if os.path.isdir(caminho):
            continue

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                json.load(f)
            total += 1
        except json.JSONDecodeError as e:
            corrompidos += 1
            detalhes.append(f"{arquivo} → {e}")
            os.rename(caminho, os.path.join(CORROMPIDOS_DIR, arquivo))
        except Exception as e:
            detalhes.append(f"{arquivo} → Erro inesperado: {e}")

    print(f"\n✅ Verificação concluída. Válidos: {total}, Corrompidos movidos: {corrompidos}")
    return {
        "validos": total,
        "corrompidos": corrompidos,
        "detalhes": detalhes
    }
