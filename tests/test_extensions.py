import pytest
import requests_mock
from extensions.github import GitHubExtension
from extensions.regex_pattern import RegexPatternExtension

# Tests for GitHubExtension
def test_github_success(requests_mock):
    ext = GitHubExtension()
    config = {'repo': 'user/project'}
    api_url = "https://api.github.com/repos/user/project/releases/latest"
    mock_response = {'tag_name': 'v1.2.3'}
    requests_mock.get(api_url, json=mock_response, status_code=200)
    result = ext.check_version(config)
    assert result == {'status': 'success', 'version': '1.2.3'}

def test_github_success_no_v_prefix(requests_mock):
    ext = GitHubExtension()
    config = {'repo': 'user/project'}
    api_url = "https://api.github.com/repos/user/project/releases/latest"
    mock_response = {'tag_name': '1.2.3'}
    requests_mock.get(api_url, json=mock_response, status_code=200)
    result = ext.check_version(config)
    assert result == {'status': 'success', 'version': '1.2.3'}

def test_github_missing_repo_config():
    ext = GitHubExtension()
    result = ext.check_version({})
    assert result['status'] == 'error'
    assert "'repo' em falta" in result['message']

def test_github_api_error(requests_mock):
    ext = GitHubExtension()
    config = {'repo': 'user/project'}
    api_url = "https://api.github.com/repos/user/project/releases/latest"
    requests_mock.get(api_url, status_code=404)
    result = ext.check_version(config)
    assert result['status'] == 'error'
    assert 'Erro de rede ou API' in result['message']

def test_github_malformed_response(requests_mock):
    ext = GitHubExtension()
    config = {'repo': 'user/project'}
    api_url = "https://api.github.com/repos/user/project/releases/latest"
    mock_response = {'foo': 'bar'} # Missing 'tag_name'
    requests_mock.get(api_url, json=mock_response, status_code=200)
    result = ext.check_version(config)
    assert result['status'] == 'error'
    assert 'Tag de release não encontrada' in result['message']

# Tests for RegexPatternExtension
def test_regex_success(requests_mock):
    ext = RegexPatternExtension()
    config = {'url': 'http://example.com', 'pattern': 'Version: (\\d+\\.\\d+)'}
    mock_html = "<html><body>Version: 1.2</body></html>"
    requests_mock.get(config['url'], text=mock_html, status_code=200)
    result = ext.check_version(config)
    assert result == {'status': 'success', 'version': '1.2'}

def test_regex_missing_config():
    ext = RegexPatternExtension()
    result = ext.check_version({'url': 'http://example.com'}) # Missing pattern
    assert result['status'] == 'error'
    assert 'URL ou Padrão em falta' in result['message']

def test_regex_network_error(requests_mock):
    ext = RegexPatternExtension()
    config = {'url': 'http://example.com', 'pattern': 'v(\\d+)'}
    requests_mock.get(config['url'], status_code=500)
    result = ext.check_version(config)
    assert result['status'] == 'error'
    assert 'Erro de rede' in result['message']

def test_regex_pattern_not_found(requests_mock):
    ext = RegexPatternExtension()
    config = {'url': 'http://example.com', 'pattern': 'Version: (\\d+)'}
    mock_html = "<html><body>No version here</body></html>"
    requests_mock.get(config['url'], text=mock_html, status_code=200)
    result = ext.check_version(config)
    assert result['status'] == 'error'
    assert 'Padrão não encontrado' in result['message']
