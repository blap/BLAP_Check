# Ketarin Clone

Este é um projeto de código aberto, um clone simplificado do popular atualizador de aplicações [Ketarin](http://ketarin.org/). A aplicação permite aos utilizadores gerir uma lista de software e verificar automaticamente as versões mais recentes, utilizando diferentes métodos de extração de informação.

## Funcionalidades

- **Gestão de Aplicações**: Adicione, edite e remova aplicações da sua lista de monitorização.
- **Verificação de Versões**: Compara a versão que tem localmente com a versão mais recente encontrada online.
- **Sistema de Extensões**: A verificação de versões é feita através de um sistema de extensões, permitindo diferentes métodos para diferentes fontes.
  - **GitHub Releases**: Verifica a última release de um repositório no GitHub.
  - **Padrão Regex**: Extrai a versão de qualquer página web através de uma expressão regular.
- **Interface Gráfica Simples**: Uma interface de utilizador construída com o framework Kivy, que mostra o estado de cada aplicação (atualizada, desatualizada, etc.).
- **Base de Dados Local**: Utiliza DuckDB para armazenar a lista de aplicações de forma eficiente.
- **Download de Ficheiros**: Inclui uma funcionalidade para descarregar a versão mais recente (atualmente com URL de placeholder).

## Como Funciona

A aplicação funciona com base num sistema de "extensões". Para cada aplicação que adiciona, escolhe um método de verificação:

1.  **GitHub**: Se o software estiver no GitHub, pode simplesmente fornecer o nome do repositório (ex: `kivy/kivy`). A aplicação irá usar a API do GitHub para encontrar a tag da "última release".
2.  **Regex Pattern**: Para outras fontes, como websites que não têm uma API formal, pode especificar uma URL e uma expressão regular (regex). A aplicação irá descarregar o conteúdo da página e aplicar o regex para encontrar o número da versão.

A aplicação armazena esta configuração e, quando solicitada, executa a verificação, compara as versões e atualiza o estado visual na lista.

## Instalação e Execução

Para executar esta aplicação localmente, siga os seguintes passos:

1.  **Clonar o Repositório**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd ketarin-clone
    ```

2.  **Criar um Ambiente Virtual** (Recomendado)
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Instalar as Dependências**
    O projeto utiliza as dependências listadas no ficheiro `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Executar a Aplicação**
    ```bash
    python main.py
    ```
    A aplicação irá criar automaticamente um diretório `data/` com o ficheiro da base de dados `app_database.db`.

    Alternativamente, pode usar os scripts de execução:
    - No Linux/macOS: `./run.sh`
    - No Windows: `run.bat`

## Criando uma Versão Portátil (Standalone)

Este projeto inclui scripts para empacotar a aplicação numa versão portátil que não requer uma instalação de Python ou dependências no sistema de destino.

1.  **Certifique-se de que as dependências de desenvolvimento estão instaladas**, incluindo o `PyInstaller`:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Execute o script de build para o seu sistema operativo:**
    - **No Linux/macOS:**
      ```bash
      ./build.sh
      ```
      Isto irá gerar um ficheiro `dist/KetarinClone-linux-portable.zip`.

    - **No Windows:**
      ```bat
      build.bat
      ```
      Isto irá gerar uma pasta `dist/KetarinClone`. Pode compactar esta pasta para a partilhar.

## Como Utilizar

1.  **Adicionar uma Aplicação**:
    - Clique no botão "Adicionar".
    - Preencha o nome da aplicação e a versão que tem atualmente instalada (se aplicável).
    - Selecione o método de verificação (ex: `github` ou `regex_pattern`).
    - No campo "Configuração da Extensão", introduza o valor necessário:
        - Para `github`: o repositório no formato `utilizador/projeto` (ex: `kivy/kivy`).
        - Para `regex_pattern`: um JSON com a `url` e o `pattern` (ex: `{"url": "https://kivy.org", "pattern": "Kivy-([\\d.]+)-"}`).
    - Clique em "Guardar".

2.  **Verificar Atualizações**:
    - Selecione uma aplicação na lista e clique em "Verificar Selecionada".
    - Para verificar todas as aplicações de uma só vez, clique em "Verificar Todas".
    - O estado da aplicação será atualizado na lista para indicar se está atualizada ou se existe uma nova versão.

## Extensibilidade: Criar uma Nova Extensão

É possível adicionar novos métodos de verificação (ex: para o GitLab, SourceForge, etc.) criando uma nova extensão.

1.  Crie um novo ficheiro Python no diretório `extensions/` (ex: `gitlab_extension.py`).
2.  No ficheiro, crie uma classe que herde de `BaseExtension`.
3.  Defina o atributo `name` com um identificador único para a sua extensão.
4.  Implemente o método `check_version(self, config: dict) -> dict`. Este método recebe um dicionário de configuração e deve retornar um dicionário com o estado e a versão encontrada.

**Exemplo de Esqueleto:**
```python
# extensions/nova_extension.py
from .base_extension import BaseExtension
import requests

class NovaExtension(BaseExtension):
    name = "nova_fonte"

    def check_version(self, config: dict) -> dict:
        # A sua lógica para encontrar a versão vai aqui.
        # Ex: fazer um pedido a uma nova API.
        api_url = config.get('url_api')
        try:
            # ...
            version = "1.2.3" # Versão encontrada
            return {'status': 'success', 'version': version}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
```
A aplicação irá carregar automaticamente a sua nova extensão ao iniciar.

## Executar os Testes

O projeto inclui um conjunto de testes para garantir a qualidade do código. Para os executar, pode usar os scripts fornecidos:

- No Linux/macOS: `./run_tests.sh`
- No Windows: `run_tests.bat`

Alternativamente, pode executar o `pytest` diretamente:
```bash
pytest
```

## Dependências Principais

- [Kivy](https://kivy.org/): Framework para a construção da interface gráfica.
- [DuckDB](https://duckdb.org/): Base de dados SQL analítica, usada aqui pelo seu simplicity e performance.
- [Requests](https://requests.readthedocs.io/): Biblioteca para fazer pedidos HTTP.
- [Pytest](https://docs.pytest.org/): Framework para testes.
