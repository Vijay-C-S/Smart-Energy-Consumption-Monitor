from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get('/api/status')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_admin_page_contains_working_login_script():
    response = client.get('/')

    assert response.status_code == 200
    html = response.text
    script_start = html.index('<script>')
    script_end = html.index('</script>', script_start)

    assert html.index('<!-- Charts Row -->') < script_start
    assert 'function doLogin()' in html[script_start:script_end]
