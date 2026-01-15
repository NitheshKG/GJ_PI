import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app
from config import Config

class TestConfig(Config):
    TESTING = True
    # Use a dummy secret key for testing
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config.from_object(TestConfig)
    
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()
