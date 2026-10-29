from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def auth_headers():
    response = client.post('/api/v1/auth/login', json={'email':'admin@neurolab.local','password':'NeuroLab2026!'})
    assert response.status_code == 200
    return {'Authorization': f"Bearer {response.json()['access_token']}"}

def test_login_and_me():
    headers = auth_headers()
    assert client.get('/api/v1/auth/me', headers=headers).status_code == 200

def test_project_creation_requires_auth_and_saves():
    assert client.get('/api/v1/projects').status_code == 401
    response = client.post('/api/v1/projects', headers=auth_headers(), json={'name':'Prueba API','description':'Proyecto test','family':'Feedforward'})
    assert response.status_code == 201
    assert response.json()['name'] == 'Prueba API'

def test_architecture_is_validated_server_side():
    response = client.post('/api/v1/architectures/validate', headers=auth_headers(), json={'name':'Red base','family':'Feedforward','input_units':2,'hidden_layers':2,'units_per_layer':8,'output_units':1,'activation':'relu'})
    assert response.status_code == 200
    assert response.json()['valid'] is True
    assert response.json()['architecture']['parameter_estimate'] > 0

def test_real_training_returns_metrics():
    response = client.post('/api/v1/training-jobs', headers=auth_headers(), json={'epochs':5,'learning_rate':0.05,'seed':42})
    assert response.status_code == 200
    assert response.json()['status'] == 'COMPLETED'
    assert len(response.json()['history']) == 5
