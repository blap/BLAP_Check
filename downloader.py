# downloader.py

import requests
from kivy.clock import mainthread

def download_file(url, destination, progress_callback, completion_callback):
    """
    Descarrega um ficheiro em streaming, reportando o progresso.

    Args:
        url (str): A URL do ficheiro a ser descarregado.
        progress_callback (function): Função a ser chamada com a percentagem de progresso.
        completion_callback (function): Função a ser chamada quando o download termina (com sucesso ou erro).
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                if total_size > 0:
                    progress = (downloaded_size / total_size) * 100
                    # Usamos o decorador @mainthread no callback para segurança
                    progress_callback(progress)

        completion_callback(True, "Download concluído com sucesso!")

    except requests.exceptions.RequestException as e:
        completion_callback(False, f"Erro de rede: {e}")
    except Exception as e:
        completion_callback(False, f"Ocorreu um erro: {e}")
