import pytest
from app import app, db
from log_parser import parse_logs

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_create_project(client):
    response = client.post('/api/projects', json={'title': 'Научная работа'})
    assert response.status_code == 201

def test_get_projects(client):
    client.post('/api/projects', json={'title': 'Диплом'})
    response = client.get('/api/projects')
    assert response.status_code == 200
    assert len(response.get_json()) == 1

def test_create_task(client):
    response = client.post('/api/tasks', json={'description': 'Написать главу 1', 'priority': 'High'})
    assert response.status_code == 201

def test_log_parser(client):
    client.post('/api/projects', json={'title': 'Логирование'})
    logs = parse_logs()
    assert isinstance(logs, list)