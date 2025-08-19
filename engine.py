# engine.py

import os
import importlib
from extensions.base_extension import BaseExtension

class ExtensionManager:
    """ Encontra, carrega e gere todas as extensões disponíveis. """
    def __init__(self, path='extensions'):
        self.extensions = {}
        self.load_extensions(path)

    def load_extensions(self, path):
        """ Carrega dinamicamente os módulos de extensão do diretório especificado. """
        print(f"A carregar extensões de '{path}'...")
        try:
            # Importa o pacote para obter o seu caminho no sistema de ficheiros
            package = importlib.import_module(path)
            package_path = os.path.dirname(package.__file__)
        except (ImportError, AttributeError):
            # Se o pacote não for encontrado, não podemos carregar extensões
            print(f"Aviso: Pacote de extensão '{path}' não encontrado ou inválido.")
            return

        for filename in os.listdir(package_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    # Usa importação relativa dentro do pacote
                    module = importlib.import_module(f".{module_name}", package=path)
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if isinstance(item, type) and issubclass(item, BaseExtension) and item is not BaseExtension:
                            instance = item()
                            self.extensions[instance.name] = instance
                            print(f"  - Extensão '{instance.name}' carregada.")
                except Exception as e:
                    print(f"Erro ao carregar a extensão '{module_name}': {e}")

    def run_check(self, extension_name, config):
        """ Executa a verificação usando a extensão especificada. """
        if extension_name in self.extensions:
            return self.extensions[extension_name].check_version(config)
        else:
            return {'status': 'error', 'message': f"Extensão '{extension_name}' não encontrada."}

# Criamos uma instância única para ser usada em toda a aplicação
extension_manager = ExtensionManager()
