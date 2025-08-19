# extensions/regex_pattern.py

from .base_extension import BaseExtension
import requests
import re

class RegexPatternExtension(BaseExtension):
    """ Extensão para o método clássico de verificação por Expressão Regular. """
    name = "regex_pattern"

    def check_version(self, config: dict) -> dict:
        url = config.get('url')
        pattern = config.get('pattern')

        if not url or not pattern:
            return {'status': 'error', 'message': 'URL ou Padrão em falta na configuração.'}

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            match = re.search(pattern, response.text)

            if match:
                version = match.group(1) if match.groups() else match.group(0)
                return {'status': 'success', 'version': version}
            else:
                return {'status': 'error', 'message': 'Padrão não encontrado.'}
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': f'Erro de rede: {e}'}
