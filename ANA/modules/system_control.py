import logging
import platform
import os
import subprocess

MASTER_OVERRIDE = True  # Failsafe para obedecer ao usuário acima de tudo

def verificar_sistema():
    sistema = platform.system()
    versao = platform.version()
    arquitetura = platform.architecture()[0]
    logging.info(f"Sistema detectado: {sistema}, Versão: {versao}, Arquitetura: {arquitetura}")
    return {
        "sistema": sistema,
        "versao": versao,
        "arquitetura": arquitetura
    }

def criar_pastas_iniciais(base_path):
    subpastas = ["documentos", "financeiro", "contratos", "temporarios"]
    for pasta in subpastas:
        full_path = os.path.join(base_path, pasta)
        os.makedirs(full_path, exist_ok=True)
        logging.info(f"Pasta criada/verificada: {full_path}")

def abrir_programa(programa):
    if not MASTER_OVERRIDE:
        return "⚠️ Comando bloqueado por failsafe."
    try:
        subprocess.Popen(programa, shell=True)
        return f"✅ Programa '{programa}' iniciado."
    except Exception as e:
        return f"❌ Erro ao iniciar '{programa}': {str(e)}"

def executar_comando(cmd):
    if not MASTER_OVERRIDE:
        return "⚠️ Execução bloqueada por failsafe."
    try:
        resultado = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return resultado.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Erro na execução: {e.output.strip()}"

def listar_arquivos(caminho):
    try:
        return os.listdir(caminho)
    except Exception as e:
        return [f"Erro ao listar: {str(e)}"]

def failsafe_status():
    return "🔒 Ativo (ANA obedece apenas ao usuário)" if MASTER_OVERRIDE else "⚠️ Desativado (ANA pode agir livremente)"

def ativar_failsafe():
    global MASTER_OVERRIDE
    MASTER_OVERRIDE = True
    return "✅ Failsafe ativado. ANA agora está sob comando total do usuário."

def desativar_failsafe():
    global MASTER_OVERRIDE
    MASTER_OVERRIDE = False
    return "⚠️ Failsafe desativado. ANA pode agir por conta própria."
