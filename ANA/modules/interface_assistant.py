import logging
from modules.brain.ana_brain import AnaBrain
from modules.web.ana_webagent import WebAgent
from modules.knowledge.vector_core import responder_por_semelhanca

class InterfaceAssistant:
    def __init__(self):
        self.brain = AnaBrain()
        self.web_agent = WebAgent()
        logging.info("🧠 Interface da ANA inicializada com sucesso.")

    def show_welcome(self):
        print("\n🤖 ANA - Assistente Neural Administrativa")
        print("Digite 'ajuda' para comandos ou 'sair' para encerrar.\n")

    def show_help(self):
        print("📘 Comandos disponíveis:")
        print("  aprender <conceito> <texto>     - Ensina um novo conceito para ANA")
        print("  consultar <pergunta>            - Faz uma pergunta ao conhecimento aprendido")
        print("  resumo                          - Mostra um resumo geral do que foi aprendido")
        print("  baixar/extrair/navegar <url>   - Executa ações com o agente Web")
        print("  ajuda                           - Exibe esta lista de comandos")
        print("  sair                            - Encerra a ANA\n")

    def run(self):
        self.show_welcome()

        while True:
            user_input = input("ANA> ").strip()
            if not user_input:
                continue

            cmd = user_input.split()[0].lower()

            if cmd == "sair":
                print("👋 Até logo! Encerrando ANA.")
                break

            elif cmd == "ajuda":
                self.show_help()

            elif cmd == "resumo":
                resumo = self.brain.summarize()
                print(f"📚 {resumo}")

            elif cmd == "aprender":
                parts = user_input.split(maxsplit=2)
                if len(parts) < 3:
                    print("⚠️ Uso correto: aprender <conceito> <texto>")
                    continue
                conceito, texto = parts[1], parts[2]
                self.brain.learn(conceito, texto)
                print(f"✅ Conceito '{conceito}' aprendido com sucesso.")

            elif cmd == "consultar":
                pergunta = user_input[9:].strip()
                if not pergunta:
                    print("⚠️ Uso correto: consultar <pergunta>")
                    continue
                resposta = self.brain.query(pergunta)

                if not resposta.strip() or "não aprendi" in resposta.lower():
                    print("🤔 Resposta direta não encontrada. Buscando nos arquivos vetoriais...")
                    resposta_vetorial = responder_por_semelhanca(pergunta)
                    print(f"🔍 {resposta_vetorial}")
                else:
                    print(f"💡 Resposta: {resposta}")

            elif cmd in ["baixar", "extrair", "navegar"]:
                resposta = self.executar_comando_web(user_input)
                print(f"🌐 WebAgent: {resposta}")

            else:
                print("❓ Comando não reconhecido. Digite 'ajuda' para ver a lista de comandos disponíveis.")

    def executar_comando_web(self, comando: str) -> str:
        try:
            resultado = self.web_agent.interpretar_comando(comando)
            return resultado.get("mensagem", "(⚠️ Nenhuma resposta recebida do WebAgent.)")
        except Exception as e:
            logging.error(f"Erro ao executar comando web: {e}")
            return f"(❌ Erro ao executar comando web: {str(e)})"

# Instância global da interface, usada também pela GUI
_assistant_instance = InterfaceAssistant()

def executar_comando_web(comando: str) -> str:
    return _assistant_instance.executar_comando_web(comando)
