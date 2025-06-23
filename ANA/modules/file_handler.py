# modules/file_handler.py

import os
import shutil
import logging

def list_files_by_type(base_path, extensions):
    """Lista arquivos que possuem uma das extensões especificadas."""
    matched_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                matched_files.append(full_path)
    return matched_files

def move_file(source, destination_folder):
    """Move um arquivo para uma pasta destino, criando a pasta se necessário."""
    os.makedirs(destination_folder, exist_ok=True)
    destination = os.path.join(destination_folder, os.path.basename(source))
    shutil.move(source, destination)
    logging.info(f"Arquivo movido para: {destination}")
    return destination
