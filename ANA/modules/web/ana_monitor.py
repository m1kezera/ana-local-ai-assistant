import schedule
import time
import threading
from modules.web.ana_webagent import WebAgent

class AnaMonitor:
    def __init__(self):
        self.agente = WebAgent()
        self.jobs = []

    def agendar_comando(self, texto_comando, horario="10:00"):
        def tarefa():
            resposta = self.agente.interpretar_comando(texto_comando)
            print(f"[ANA Monitor] {resposta['mensagem']}")
            # Aqui futuramente podemos enviar para interface/log

        job = schedule.every().day.at(horario).do(tarefa)
        self.jobs.append(job)
        print(f"[ANA Monitor] Comando agendado: '{texto_comando}' às {horario}")

    def iniciar_monitoramento(self):
        def loop():
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        print("[ANA Monitor] Monitoramento iniciado em segundo plano.")

# Exemplo de uso isolado
if __name__ == "__main__":
    monitor = AnaMonitor()
    monitor.agendar_comando("baixar https://www.africau.edu/images/default/sample.pdf", "10:00")
    monitor.iniciar_monitoramento()

    while True:
        time.sleep(10)  # Mantém o script rodando
