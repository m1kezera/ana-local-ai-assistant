import os
import logging
from llama_cpp import Llama

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

print("🔥 LLM carregando de:", os.path.abspath(__file__))

MODEL_PATH = "models/openhermes/openhermes-2.5.Q4_K_M.gguf"

model = None

try:
    model = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=6,         # Use o número de threads do seu CPU
        n_gpu_layers=0       # 0 = somente CPU
    )
    logger.info("✅ OpenHermes 2.5 carregado com sucesso via llama-cpp-python.")
except Exception as e:
    logger.critical(f"❌ Falha ao carregar modelo OpenHermes 2.5: {e}")
    model = None

def responder(pergunta: str) -> str:
    if not model:
        logger.warning("❌ Modelo não carregado.")
        return "(❌ O modelo não foi carregado corretamente.)"

    prompt = f"""
<|system|>
Você é a ANA, uma inteligência artificial local criada por Mikhael Ravi Medeiros Coelho.
Responda com clareza, inteligência e empatia.
<|user|>
{pergunta.strip()}
<|assistant|>
""".strip()

    try:
        resultado = model(prompt, max_tokens=512, temperature=0.7, top_p=0.95)
        return resultado["choices"][0]["text"].strip() or "(🤔 Ainda estou processando essa informação...)"
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        return f"(Erro ao gerar resposta: {str(e)})"
