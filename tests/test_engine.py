import pytest
import sys
from engine import ExtensionManager
from extensions.base_extension import BaseExtension
from unittest.mock import Mock

@pytest.fixture
def fake_extensions_path(tmp_path):
    """
    Creates a temporary directory with fake extension files for testing.
    Returns a tuple of (parent_path, extensions_dir_name)
    """
    parent_dir = tmp_path
    extensions_dir_name = "my_fake_extensions"
    extensions_dir = parent_dir / extensions_dir_name
    extensions_dir.mkdir()

    (extensions_dir / "__init__.py").touch()

    (extensions_dir / "ext1.py").write_text("""
from extensions.base_extension import BaseExtension
class MyExt1(BaseExtension):
    name = "ext1"
    def check_version(self, config): return None
""")

    (extensions_dir / "ext2.py").write_text("""
from extensions.base_extension import BaseExtension
class MyExt2(BaseExtension):
    name = "ext2"
    def check_version(self, config): return None
""")

    (extensions_dir / "not_an_ext.py").write_text("class NotAnExtension: pass")
    (extensions_dir / "bad_syntax.py").write_text("def foo()")

    return str(parent_dir), extensions_dir_name


def test_load_extensions(fake_extensions_path):
    """
    Tests that ExtensionManager correctly loads valid extensions and ignores invalid ones.
    """
    parent_dir, extensions_dir_name = fake_extensions_path

    # Add the temp parent directory to python path so the package can be found
    sys.path.insert(0, parent_dir)

    manager = ExtensionManager(path=extensions_dir_name)

    # Clean up sys.path
    sys.path.pop(0)

    assert len(manager.extensions) == 2
    assert "ext1" in manager.extensions
    assert "ext2" in manager.extensions
    assert isinstance(manager.extensions["ext1"], BaseExtension)
    assert manager.extensions["ext1"].name == "ext1"

def test_run_check_success(monkeypatch):
    """
    Tests that run_check correctly calls the extension's check_version method.
    """
    # We create a manager but prevent it from loading real extensions
    # by patching os.listdir to return an empty list.
    monkeypatch.setattr('os.listdir', lambda path: [])
    manager = ExtensionManager()

    # Now we manually add a mock extension
    mock_extension = Mock(spec=BaseExtension)
    mock_extension.name = "mock_ext"
    mock_result = {'status': 'success', 'version': 'mocked'}
    mock_extension.check_version.return_value = mock_result

    manager.extensions['mock_ext'] = mock_extension

    config = {'foo': 'bar'}
    result = manager.run_check('mock_ext', config)

    mock_extension.check_version.assert_called_once_with(config)
    assert result == mock_result

def test_run_check_extension_not_found(monkeypatch):
    """
    Tests that run_check returns an error if the extension name is not found.
    """
    # Patch listdir to ensure no extensions are loaded
    monkeypatch.setattr('os.listdir', lambda path: [])
    manager = ExtensionManager()
    result = manager.run_check('non_existent_ext', {})

    assert result['status'] == 'error'
    assert "não encontrada" in result['message']
