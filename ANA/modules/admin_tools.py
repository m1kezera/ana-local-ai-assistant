# modules/admin_tools.py

import logging

usuarios = {}

def criar_usuario(nome, cargo, permissao):
    """Cria um novo usuário com cargo e permissão."""
    if nome not in usuarios:
        usuarios[nome] = {
            "cargo": cargo,
            "permissao": permissao
        }
        logging.info(f"Usuário criado: {nome}, Cargo: {cargo}, Permissão: {permissao}")
    else:
        logging.warning(f"Tentativa de recriar usuário existente: {nome}")

def listar_usuarios():
    """Lista todos os usuários cadastrados."""
    return usuarios

def tem_permissao(nome, nivel_desejado):
    """Verifica se o usuário possui o nível de permissão exigido."""
    user = usuarios.get(nome)
    return user and user["permissao"] >= nivel_desejado
