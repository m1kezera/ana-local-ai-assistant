import os
import logging
from modules.learning_core import start_learning
from modules.file_handler import list_files_by_type, move_file
from modules.finance_manager import analisar_pagamento
from modules.system_control import verificar_sistema, criar_pastas_iniciais
from modules.admin_tools import criar_usuario, listar_usuarios
from modules.interface_assistant import InterfaceAssistant  # interface CLI

from modules.ana_core import AnaCore  # Importa a mente da ANA

# Configurações iniciais de log
logging.basicConfig(
    filename='logs/ana.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("🧠 ANA - Assistente Neural Administrativa")
    logging.info("Sistema ANA iniciado")

    # Inicia o módulo cognitivo
    ana = AnaCore()
    ana.nascer()

    if ana.consciente:
        print("⚡ ANA detectou sua pasta de conhecimento.")
        ana.viver()
        return  # Evita continuar se for modo autoconsciente

    modo = input("Escolha o modo de execução: (cli/gui/desktop): ").strip().lower()

    if modo == 'cli':
        assistant = InterfaceAssistant()
        assistant.run()
        return

    elif modo == 'gui' or modo == 'desktop':
        import app_desktop
        app_desktop.main()
        return

    # Fluxo antigo (não interativo)
    base_path = input("Informe o caminho da pasta principal da empresa: ").strip()

    if not os.path.exists(base_path):
        print("❌ Caminho inválido. Encerrando.")
        logging.error(f"Pasta não encontrada: {base_path}")
        return

    # Verifica sistema operacional
    sistema = verificar_sistema()
    print(f"📡 Sistema detectado: {sistema['sistema']} ({sistema['arquitetura']})")

    # Cria subpastas essenciais
    criar_pastas_iniciais(base_path)

    # Inicia escaneamento e aprendizado
    start_learning(base_path)

    # Listar arquivos PDF
    pdfs = list_files_by_type(base_path, ['.pdf'])
    print(f"\n📎 PDFs encontrados: {len(pdfs)}")
    for p in pdfs[:5]:  # Mostra só os 5 primeiros
        print("  -", p)

    # Exemplo de simulação de atraso
    resultado = analisar_pagamento("2025-06-01", 1000)
    print(f"\n💰 Simulação financeira:")
    print(f"  Dias de atraso: {resultado['dias_atraso']}")
    print(f"  Multa: R${resultado['multa']}")
    print(f"  Juros: R${resultado['juros']}")
    print(f"  Total atualizado: R${resultado['total']}")

    # Criação de usuário
    criar_usuario("mikam", "Administrador", permissao=5)
    usuarios = listar_usuarios()
    print(f"\n🔐 Usuários cadastrados:")
    for nome, dados in usuarios.items():
        print(f"  - {nome} ({dados['cargo']}, Permissão {dados['permissao']})")

    print("\n✅ ANA está pronta. Verifique o log em logs/ana.log")


if __name__ == "__main__":
    main()
