from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QScrollArea,
    QHBoxLayout, QSystemTrayIcon, QMenu, QListWidget, QListWidgetItem,
    QSplitter, QInputDialog, QToolButton, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QIcon
import sys, os, json, logging
from datetime import datetime

from modules.tools import log_manager
log_manager.configurar_logger()
logger = logging.getLogger(__name__)

from modules.interface_assistant import executar_comando_web
from modules.knowledge.vector_core import obter_estatisticas, responder_por_semelhanca
from modules.tools import system_utilities as utils

try:
    from modules.tools import chat_checker
    chat_checker.verificar_e_corrigir_chats()
except Exception as e:
    logger.warning(f"⚠️ Erro ao checar chats corrompidos: {e}")

CHAT_DIR = "chats/"
os.makedirs(CHAT_DIR, exist_ok=True)

class RespostaWorker(QObject):
    finished = pyqtSignal(str)
    pergunta = ""

    def run(self):
        try:
            from modules.ana_llm import responder
            resposta = responder(self.pergunta)
        except Exception as e:
            logger.error(f"Erro na thread RespostaWorker: {e}")
            resposta = f"(Erro ao gerar resposta: {str(e)})"
        self.finished.emit(resposta)

class AprendizadoThread(QThread):
    finished_signal = pyqtSignal(str)
    def run(self):
        try:
            from modules.web.autolearning_fetcher import iniciar_auto_aprendizado
            iniciar_auto_aprendizado()
            self.finished_signal.emit("✅ Aprendizado online executado com sucesso.")
        except Exception as e:
            logger.error(f"Erro no aprendizado online: {e}")
            self.finished_signal.emit(f"❌ Erro durante aprendizado: {e}")

class ChatBubble(QWidget):
    def __init__(self, text, is_user=True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setStyleSheet(f"""
            background-color: {'#0B93F6' if is_user else '#2C2C2C'};
            border-radius: 15px;
            color: {'white' if is_user else '#D0D0D0'};
            padding: 10px;
        """)

        if is_user:
            layout.addStretch()
            layout.addWidget(label)
        else:
            layout.addWidget(label)
            layout.addStretch()

        self.setSizePolicy(label.sizePolicy())

class AnaChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANA - Assistente Neural Administrativa")
        self.resize(1000, 600)
        self.chat_file = None
        self.historico = []
        self.bolha_pensando = None

        icon_path = r"C:\ANA\prisma2.ico"
        self.setWindowIcon(QIcon(icon_path))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self.sidebar.itemClicked.connect(self.carregar_conversa)
        self.sidebar.itemDoubleClicked.connect(self.renomear_conversa)

        self.botao_novo = QPushButton("➕ Novo Chat")
        self.botao_novo.clicked.connect(self.criar_novo_chat)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.botao_novo)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar_layout)

        self.chat_panel = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_panel)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_content = QWidget()
        self.chat_messages = QVBoxLayout(self.chat_content)
        self.chat_messages.addStretch(1)
        self.scroll_area.setWidget(self.chat_content)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Digite sua mensagem aqui...")
        self.input_line.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)

        self.engr_button = QToolButton()
        self.engr_button.setText("⚙️")
        self.engr_button.setStyleSheet("background-color: #2D2D2D; color: white; border-radius: 10px; padding: 4px;")
        self.engr_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(self)
        menu.addAction("🧠 Iniciar aprendizado online", lambda: self.resposta_recebida("🔄 " + self._executar_aprendizado_online()))
        menu.addAction("🍃 Conectar ao MongoDB", lambda: self.resposta_recebida(utils.conectar_mongodb()))
        menu.addAction("📊 Mostrar status vetorial", lambda: self.resposta_recebida(self._mostrar_status()))
        menu.addAction("🧬 Rodar indexação temática", lambda: self.resposta_recebida(utils.rodar_indexador()))
        menu.addAction("📂 Abrir pasta de eBooks", lambda: self.resposta_recebida(utils.abrir_pasta_ebooks()))
        menu.addAction("📘 Listar eBooks aprendidos", lambda: self.resposta_recebida(utils.listar_ebooks_index()))
        menu.addAction("🌐 Verificar internet", lambda: self.resposta_recebida("✅ Online" if utils.verificar_conexao_internet() else "🔒 Offline"))
        menu.addAction("📸 Abrir screenshots", lambda: self.resposta_recebida(utils.abrir_pasta_screenshots()))
        menu.addAction("🧹 Limpar conversa", lambda: self._limpar_chat())
        menu.addAction("🧪 Verificar chats corrompidos", lambda: self.resposta_recebida(utils.verificar_chats()))
        self.engr_button.setMenu(menu)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.engr_button)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)

        self.chat_layout.addWidget(self.scroll_area)
        self.chat_layout.addLayout(input_layout)

        splitter.addWidget(sidebar_container)
        splitter.addWidget(self.chat_panel)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #E0E0E0; }
            QListWidget { background-color: #1B1B1B; border-right: 1px solid #333; color: #FFFFFF; }
            QPushButton { background-color: #333333; color: white; border: none; padding: 6px; }
            QPushButton:hover { background-color: #444; }
            QLineEdit { background-color: #1E1E1E; border: 1px solid #333; border-radius: 10px; padding: 8px; color: #E0E0E0; }
        """)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_path))
        tray_menu = QMenu()
        tray_menu.addAction("Restaurar ANA", self.show)
        tray_menu.addAction("Sair", self.close_app)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self._carregar_sidebar()
        self.criar_novo_chat(padrao=True)
        QTimer.singleShot(1000, lambda: self.resposta_recebida("🌞 Olá Mikhael, estou acordada. O que deseja explorar hoje?"))

    def scroll_to_bottom(self):
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()))

    def resposta_recebida(self, texto):
        if self.bolha_pensando:
            self.chat_messages.removeWidget(self.bolha_pensando)
            self.bolha_pensando.deleteLater()
            self.bolha_pensando = None
        bubble = ChatBubble(texto, is_user=False)
        self.chat_messages.insertWidget(self.chat_messages.count() - 1, bubble)
        self.scroll_to_bottom()
        self.salvar_chat(texto, "ana")

    def send_message(self):
        pergunta = self.input_line.text().strip()
        if not pergunta:
            return
        self.input_line.clear()
        bubble = ChatBubble(pergunta, is_user=True)
        self.chat_messages.insertWidget(self.chat_messages.count() - 1, bubble)
        self.scroll_to_bottom()
        self.salvar_chat(pergunta, "user")

        self.bolha_pensando = ChatBubble("💬 ANA está pensando...", is_user=False)
        self.chat_messages.insertWidget(self.chat_messages.count() - 1, self.bolha_pensando)
        self.scroll_to_bottom()

        self.worker = RespostaWorker()
        self.worker.pergunta = pergunta
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.resposta_recebida)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def salvar_chat(self, texto, tipo):
        if not self.chat_file:
            return
        self.historico.append({"texto": texto, "tipo": tipo})
        with open(self.chat_file, "w", encoding="utf-8") as f:
            json.dump(self.historico, f, ensure_ascii=False, indent=2)

    def _executar_aprendizado_online(self):
        self.aprendizado_thread = AprendizadoThread()
        self.aprendizado_thread.finished_signal.connect(self.resposta_recebida)
        self.aprendizado_thread.start()
        return "🔄 Iniciando aprendizado online..."

    def _mostrar_status(self):
        estat = obter_estatisticas()
        return f"📃 Arquivos lidos: {estat['arquivos_lidos']}\n🧠 Vetores armazenados: {estat['vetores']}"

    def _limpar_chat(self):
        while self.chat_messages.count():
            item = self.chat_messages.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.chat_messages.addStretch(1)
        self.historico = []

    def criar_novo_chat(self, padrao=False):
        nome = datetime.now().strftime("chat_%Y%m%d_%H%M%S") if padrao else QInputDialog.getText(self, "Novo Chat", "Nome do chat:")[0]
        if not nome:
            return
        nome = nome.strip().replace(" ", "_").lower()
        self.chat_file = os.path.join(CHAT_DIR, f"{nome}.json")
        self.historico = []
        with open(self.chat_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        self._carregar_sidebar()
        self._limpar_chat()

    def _carregar_sidebar(self):
        self.sidebar.clear()
        for f in sorted(os.listdir(CHAT_DIR)):
            if f.endswith(".json"):
                item = QListWidgetItem(os.path.splitext(f)[0])
                self.sidebar.addItem(item)

    def carregar_conversa(self, item):
        caminho = os.path.join(CHAT_DIR, f"{item.text()}.json")
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                self.historico = json.load(f)
            self.chat_file = caminho
            self._limpar_chat()
            for msg in self.historico:
                if isinstance(msg, dict) and 'texto' in msg and 'tipo' in msg:
                    bolha = ChatBubble(msg["texto"], is_user=(msg["tipo"] == "user"))
                    self.chat_messages.insertWidget(self.chat_messages.count() - 1, bolha)
            self.scroll_to_bottom()
        except Exception as e:
            logger.warning(f"Erro ao carregar chat {caminho}: {e}")
            QMessageBox.warning(self, "Erro ao carregar chat", str(e))

    def renomear_conversa(self, item):
        novo_nome, ok = QInputDialog.getText(self, "Renomear Chat", "Novo nome:", text=item.text())
        if ok and novo_nome:
            antigo_path = os.path.join(CHAT_DIR, f"{item.text()}.json")
            novo_path = os.path.join(CHAT_DIR, f"{novo_nome}.json")
            if os.path.exists(antigo_path):
                os.rename(antigo_path, novo_path)
            item.setText(novo_nome)

    def close_app(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AnaChatWindow()
    janela.show()
    sys.exit(app.exec())
