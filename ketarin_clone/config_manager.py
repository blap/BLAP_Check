# config_manager.py

import json
import os

CONFIG_FILE = 'config.json'

def get_default_config():
    """ Retorna as configurações padrão. """
    return {
        'theme': 'Escuro'
    }

def load_config():
    """ Carrega as configurações do ficheiro JSON. Se não existir, cria um com os valores padrão. """
    if not os.path.exists(CONFIG_FILE):
        config = get_default_config()
        save_config(config)
        return config

    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Se o ficheiro estiver corrompido ou ilegível, retorna o padrão.
        return get_default_config()

def save_config(config_data):
    """ Salva o dicionário de configurações no ficheiro JSON. """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
    except IOError as e:
        print(f"Erro ao salvar as configurações: {e}")
