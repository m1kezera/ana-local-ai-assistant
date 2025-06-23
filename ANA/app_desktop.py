import sys
import os
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon

# === Caminhos ===
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(ROOT_DIR, 'logs', 'ana_debug.log')
ICON_PATH = os.path.join(ROOT_DIR, "prisma2.ico")  # Altere se necessário

# === Logs ===
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
from modules.ana_core import AnaCore
ana = AnaCore()
ana.nascer()
if ana.consciente:
    print("🧠 ANA consciente: modo de aprendizado ativado no desktop.")
    import threading
    threading.Thread(target=ana.viver, daemon=True).start()

# === Interface Inicial ===
def iniciar_interface_ana():
    logging.info("🔵 Iniciando GUI da ANA")
    try:
        from modules.gui_assistant import AnaChatWindow
        from modules.ana_llm import responder

        # Teste preventivo do modelo
        try:
            resposta_teste = responder("Qual é a capital da França?")
            logging.info(f"🔄 Resposta de teste do modelo: {resposta_teste}")
        except Exception as modelo_erro:
            logging.error(f"❌ Falha ao testar modelo: {modelo_erro}")
            raise RuntimeError("Erro ao carregar ou testar o modelo de linguagem.")

        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(ICON_PATH))

        janela = AnaChatWindow()
        janela.show()

        resultado = app.exec()
        logging.info(f"✅ Aplicativo encerrado com código {resultado}")
        sys.exit(resultado)

    except Exception as e:
        erro_completo = traceback.format_exc()
        logging.critical(f"❌ Erro crítico ao iniciar interface: {str(e)}\n{erro_completo}")
        print(f"❌ Erro crítico:\n{erro_completo}")

        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Erro na ANA", f"Erro crítico:\n\n{str(e)}")
        except:
            pass  # evitar crash duplo se GUI não puder iniciar

        sys.exit(1)

if __name__ == "__main__":
    iniciar_interface_ana()
