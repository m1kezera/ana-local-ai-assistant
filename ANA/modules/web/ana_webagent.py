import json
import os
import logging
from modules.web import ana_chromebot, ana_scraper, ana_downloader

WEB_MEMORY_PATH = "modules/web/web_memory.json"

class WebAgent:
    def __init__(self):
        self.memory = self.carregar_memoria()
        logging.info("🌐 WebAgent inicializado com memória de navegação.")

    def carregar_memoria(self):
        if os.path.exists(WEB_MEMORY_PATH):
            try:
                with open(WEB_MEMORY_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Erro ao carregar memória do WebAgent: {e}")
        return {}

    def salvar_memoria(self):
        try:
            with open(WEB_MEMORY_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Erro ao salvar memória do WebAgent: {e}")

    def interpretar_comando(self, comando):
        comando = comando.strip().lower()
        logging.info(f"🧭 Interpretando comando Web: {comando}")

        if "baixar" in comando:
            return self.formatar_resposta(self.acao_baixar(comando))

        elif "extrair" in comando or "ler site" in comando:
            return self.formatar_resposta(self.acao_extrair(comando))

        elif "navegar" in comando or "clicar" in comando:
            return self.formatar_resposta(self.acao_navegar(comando))

        return self.formatar_resposta("❌ Comando não reconhecido pelo WebAgent.", status="erro")

    def acao_baixar(self, comando):
        url = self.extrair_url_do_comando(comando)
        if url:
            resultado = ana_downloader.baixar_arquivo(url)
            return f"⬇️ Download concluído: {resultado}"
        return "❌ URL não encontrada no comando de download."

    def acao_extrair(self, comando):
        url = self.extrair_url_do_comando(comando)
        if url:
            dados = ana_scraper.extrair_dados_do_site(url)
            return dados
        return "❌ URL não encontrada para extração de conteúdo."

    def acao_navegar(self, comando):
        url = self.extrair_url_do_comando(comando)
        if url:
            return ana_chromebot.executar_comando_no_site(comando, url)
        return "❌ URL não encontrada para navegação assistida."

    def extrair_url_do_comando(self, comando):
        palavras = comando.split()
        for palavra in palavras:
            if palavra.startswith("http://") or palavra.startswith("https://"):
                return palavra
        return None

    def formatar_resposta(self, resposta, status="ok"):
        if isinstance(resposta, str):
            return {
                "status": status,
                "mensagem": resposta,
                "dados": None
            }
        elif isinstance(resposta, dict):
            return {
                "status": status,
                "mensagem": "✅ Operação realizada com sucesso.",
                "dados": resposta
            }
        else:
            return {
                "status": "erro",
                "mensagem": "❌ Resposta inesperada do WebAgent.",
                "dados": None
            }

# Execução isolada para teste
if __name__ == "__main__":
    agente = WebAgent()
    resposta = agente.interpretar_comando("extrair https://exemplo.com")
    print(json.dumps(resposta, indent=2, ensure_ascii=False))
