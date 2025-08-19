# extensions/github.py

from .base_extension import BaseExtension
import requests

class GitHubExtension(BaseExtension):
    """ Extensão para buscar a última 'release' de um repositório do GitHub. """
    name = "github"

    def check_version(self, config: dict) -> dict:
        repo = config.get('repo')
        if not repo:
            return {'status': 'error', 'message': "'repo' em falta na configuração."}

        api_url = f"https://api.github.com/repos/{repo}/releases/latest"

        try:
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Remove um 'v' inicial se existir (ex: v1.2.3 -> 1.2.3)
            version = data.get('tag_name', '').lstrip('v')

            if version:
                return {'status': 'success', 'version': version}
            else:
                return {'status': 'error', 'message': "Tag de release não encontrada na resposta da API."}

        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': f'Erro de rede ou API: {e}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Erro ao processar resposta: {e}'}
