import pytest
import requests_mock
from downloader import download_file
from unittest.mock import Mock

def test_download_file_success(tmp_path, requests_mock):
    """
    Tests successful file download.
    """
    url = "http://example.com/file.zip"
    destination = tmp_path / "file.zip"
    file_content = b"some binary file content"

    # Explicitly set the Content-Length header for the progress calculation
    headers = {'Content-Length': str(len(file_content))}
    requests_mock.get(url, content=file_content, headers=headers)

    progress_callback = Mock()
    completion_callback = Mock()

    download_file(url, str(destination), progress_callback, completion_callback)

    # Check if file was created and content is correct
    assert destination.exists()
    assert destination.read_bytes() == file_content

    # Check callbacks
    progress_callback.assert_called_with(100.0)
    completion_callback.assert_called_once_with(True, "Download concluído com sucesso!")

def test_download_file_network_error(tmp_path, requests_mock):
    """
    Tests download failure due to network error.
    """
    url = "http://example.com/file.zip"
    destination = tmp_path / "file.zip"

    requests_mock.get(url, status_code=404)

    progress_callback = Mock()
    completion_callback = Mock()

    download_file(url, str(destination), progress_callback, completion_callback)

    assert not destination.exists()
    progress_callback.assert_not_called()
    completion_callback.assert_called_once()
    # Check the arguments of the call
    args, kwargs = completion_callback.call_args
    assert args[0] is False
    assert "Erro de rede" in args[1]

def test_download_no_content_length(tmp_path, requests_mock):
    """
    Tests download where content-length header is missing.
    """
    url = "http://example.com/file.zip"
    destination = tmp_path / "file.zip"
    file_content = b"some content"

    # Mock response without Content-Length header
    requests_mock.get(url, content=file_content, headers={})

    progress_callback = Mock()
    completion_callback = Mock()

    download_file(url, str(destination), progress_callback, completion_callback)

    assert destination.exists()
    assert destination.read_bytes() == file_content

    # Progress callback should not have been called as total_size is 0
    progress_callback.assert_not_called()
    completion_callback.assert_called_once_with(True, "Download concluído com sucesso!")
