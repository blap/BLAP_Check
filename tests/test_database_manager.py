import pytest
from database import manager as db_manager
import os
import duckdb

# This fixture will be used by tests that need a database.
@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    """
    For each test, monkeypatch the DB_FILE to use a temporary file-based database.
    This ensures tests are isolated and reflect the file-based nature of the app.
    """
    temp_db_file = tmp_path / "test_app.db"
    monkeypatch.setattr(db_manager, 'DB_FILE', str(temp_db_file))
    # Also monkeypatch the makedirs call to avoid creating a 'data' dir in repo root
    monkeypatch.setattr(os, 'makedirs', lambda name, exist_ok=False: None)
    return str(temp_db_file)


def test_initialize_database(temp_db):
    """
    Tests if the database and the 'applications' table are created.
    """
    db_manager.initialize_database()

    # Connect to the temporary database file to check its state
    con = duckdb.connect(database=temp_db, read_only=True)
    tables = con.execute("SHOW TABLES;").fetchall()
    con.close()

    assert ('applications',) in tables

def test_add_and_get_all_applications(temp_db):
    """
    Tests adding applications and retrieving them.
    """
    db_manager.initialize_database()

    app1 = {'name': 'App Z', 'local_version': '1.0', 'extension_id': 'github', 'extension_config': 'z/z'}
    app2 = {'name': 'App A', 'local_version': '2.0', 'extension_id': 'regex', 'extension_config': 'a/a'}

    db_manager.add_application(app1)
    db_manager.add_application(app2)

    apps = db_manager.get_all_applications()

    assert len(apps) == 2
    # Check if they are ordered by name
    assert apps[0]['name'] == 'App A'
    assert apps[1]['name'] == 'App Z'
    assert apps[0]['local_version'] == '2.0'

def test_update_application(temp_db):
    """
    Tests updating an existing application.
    """
    db_manager.initialize_database()

    app_data = {'name': 'My App', 'local_version': '1.0', 'extension_id': 'github', 'extension_config': 'user/repo'}
    db_manager.add_application(app_data)

    apps = db_manager.get_all_applications()
    app_id = apps[0]['id']

    updated_data = {'name': 'My Updated App', 'local_version': '1.1', 'extension_id': 'regex', 'extension_config': 'new/config'}
    db_manager.update_application(app_id, updated_data)

    updated_app = db_manager.get_all_applications()[0]

    assert updated_app['name'] == 'My Updated App'
    assert updated_app['local_version'] == '1.1'
    assert updated_app['extension_id'] == 'regex'

def test_delete_application(temp_db):
    """
    Tests deleting an application.
    """
    db_manager.initialize_database()

    app_data = {'name': 'To Be Deleted', 'local_version': '1.0', 'extension_id': 'github', 'extension_config': 'delete/me'}
    db_manager.add_application(app_data)

    apps = db_manager.get_all_applications()
    assert len(apps) == 1

    app_id = apps[0]['id']
    db_manager.delete_application(app_id)

    apps_after_delete = db_manager.get_all_applications()
    assert len(apps_after_delete) == 0

def test_update_app_latest_version(temp_db):
    """
    Tests updating only the latest_version of an application.
    """
    db_manager.initialize_database()

    app_data = {'name': 'Test App', 'local_version': '1.0', 'extension_id': 'github', 'extension_config': 'test/repo'}
    db_manager.add_application(app_data)

    app_id = db_manager.get_all_applications()[0]['id']

    db_manager.update_app_latest_version(app_id, '2.0')

    updated_app = db_manager.get_all_applications()[0]
    assert updated_app['latest_version'] == '2.0'
    assert updated_app['local_version'] == '1.0' # Ensure other fields are untouched
