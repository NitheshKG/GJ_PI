def test_health_check(client):
    """Test that the application health check endpoint works."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_config_loading(app):
    """Test that the app loads configuration correctly."""
    assert app.config['TESTING'] is True

# Note: More comprehensive integration tests requiring DB mocking 
# would be added here in a real production scenario.
# For now, we verify the app structure and basic endpoints.
