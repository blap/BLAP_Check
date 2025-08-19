import pytest
import os

# Configure Kivy for testing
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

# The following is needed to make Kivy work on a headless server
from kivy.config import Config
if not Config.has_section('graphics'):
    Config.add_section('graphics')
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '240')
Config.set('graphics', 'show_cursor', '0')

if not Config.has_section('core'):
    Config.add_section('core')
Config.set('core', 'window', 'mock')

# It's important to import Kivy modules AFTER setting the config
from main import KetarinCloneApp
from unittest.mock import Mock, patch

@pytest.fixture
def app_instance():
    """
    Fixture to create an instance of the app and manually build its widget tree.
    """
    # Patch dependencies that are called in build()
    with patch('database.manager.initialize_database'), \
         patch('config_manager.load_config', return_value={'theme': 'Escuro'}) as mock_load_config:

        app = KetarinCloneApp()

        # Manually call build() to populate app.root and app.config
        app.root = app.build()
        app.config = mock_load_config()

        yield app

        app = None


def test_app_builds(app_instance):
    """A simple test to ensure the app can be instantiated and builds its root widget."""
    assert app_instance is not None
    assert app_instance.root is not None

def test_change_theme(app_instance):
    """Tests the theme changing logic."""
    with patch('config_manager.save_config') as mock_save_config, \
         patch.object(app_instance, 'apply_theme') as mock_apply_theme:

        app_instance.change_theme('Claro')

        assert app_instance.config['theme'] == 'Claro'
        mock_save_config.assert_called_once_with(app_instance.config)
        mock_apply_theme.assert_called_once()

def test_refresh_app_list_logic(app_instance):
    """
    Tests the data transformation logic within refresh_app_list by mocking the widget tree.
    """
    mock_db_apps = [
        {'id': 1, 'name': 'App A', 'local_version': '1.0.0', 'latest_version': '2.0.0'},
        {'id': 2, 'name': 'App B', 'local_version': '1.1.0', 'latest_version': '1.1.0'},
        {'id': 3, 'name': 'App C', 'local_version': None, 'latest_version': '3.0.0'},
    ]

    with patch('database.manager.get_all_applications', return_value=mock_db_apps) as mock_get_apps:
        # Create a mock for the RecycleView widget that has a 'data' attribute
        mock_rv = Mock()
        mock_rv.data = []

        # Create a mock for the 'ids' object that allows attribute access
        mock_ids = Mock()
        mock_ids.app_list_rv = mock_rv

        # Create a mock for the screen that has our mock 'ids' object
        mock_screen = Mock()
        mock_screen.ids = mock_ids

        # Patch the app's root ScreenManager to return our mock screen
        with patch.object(app_instance.root, 'get_screen', return_value=mock_screen):
            app_instance.refresh_app_list()

            mock_get_apps.assert_called_once()

            # Check the data that was assigned to our mock RecycleView
            processed_data = mock_rv.data
            assert len(processed_data) == 3

            assert processed_data[0]['ids.app_version_label.text'] == '1.0.0 -> 2.0.0'
            assert processed_data[1]['ids.app_version_label.text'] == '1.1.0 (Atualizado)'
            assert processed_data[2]['ids.app_version_label.text'] == 'Última: 3.0.0'
