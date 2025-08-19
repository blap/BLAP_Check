# extensions/base_extension.py

from abc import ABC, abstractmethod

class BaseExtension(ABC):
    """
    A classe base abstrata para todas as extensões de verificação.
    Define um "contrato" que todas as extensões devem seguir.
    """

    # O nome único da extensão, usado na UI e internamente.
    name = "Base"

    @abstractmethod
    def check_version(self, config: dict) -> dict:
        """
        O método principal que cada extensão deve implementar.

        Args:
            config (dict): A configuração específica para esta verificação
                           (ex: {'repo': 'user/project'} para o GitHub).

        Returns:
            dict: Um dicionário com o resultado, como:
                  {'status': 'success', 'version': '1.2.3'} ou
                  {'status': 'error', 'message': 'Mensagem de erro.'}
        """
        pass
