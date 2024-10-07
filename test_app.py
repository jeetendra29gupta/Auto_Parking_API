import pytest
from auto_car_documentation_main import app


# Test configuration: disables database writes and runs in testing mode
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_all_autos_empty(client):
    """Test GET /auto when no autos exist"""
    response = client.get('/auto')
    assert response.status_code == 200
    assert response.json == []


def test_create_auto(client):
    """Test POST /auto to create a new auto"""
    new_auto = {
        "parking_name": "Test Parking",
        "parking_price": 5.0
    }
    response = client.post('/auto', json=new_auto)
    assert response.status_code == 201
    assert 'auto_id' in response.json


def test_get_auto(client):
    """Test GET /auto/<id> to retrieve an existing auto"""
    # Assuming an auto with ID 1 exists
    response = client.get('/auto/1')
    assert response.status_code == 200
    assert response.json['parking_name'] == 'Test Parking'


def test_update_auto(client):
    """Test PUT /auto/<id> to update an auto"""
    updated_auto = {
        "parking_name": "Updated Parking",
        "parking_price": 15.0
    }
    response = client.put('/auto/1', json=updated_auto)
    assert response.status_code == 200


def test_delete_auto(client):
    """Test DELETE /auto/<id> to delete an auto"""
    response = client.delete('/auto/1')
    assert response.status_code == 204


def test_auto_not_found(client):
    """Test GET /auto/<id> when the auto is not found"""
    response = client.get('/auto/999')
    assert response.status_code == 404
