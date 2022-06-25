import requests

from requests.auth import HTTPBasicAuth
token = None

def test_login_api():
  
    response = requests.get('http://127.0.0.1:5000/login_api', auth=HTTPBasicAuth('username', 'thisisthesecretkey'))
  
    assert response.status_code == 200
    assert 'token' in response.json()

    if 'token' in response.json():
        dic = response.json()
        token = dic['token']
