import requests

from requests.auth import HTTPBasicAuth

BASE_URL = 'http://127.0.0.1:5000'

def test_login_api():
  
    response = requests.get(BASE_URL+'/login_api', auth=HTTPBasicAuth('username', 'thisisthesecretkey'))
  
    assert response.status_code == 200
    assert 'token' in response.json()

    if 'token' in response.json():
        dic = response.json()
        token = dic['token']

def test_login_linkedin():
    response = requests.get(BASE_URL+'/api/login_linkedin')

    assert response.status_code == 403
    assert response.json() == {"message": "Token is missing"}

    # test with old token
    response = requests.get(BASE_URL+'/api/login_linkedin?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYmlrYXNoIiwiZXhwIjoxNjU2MTM5NTM1fQ.it3PQ8oOaKhbnjEVgoGcquvTWjD_si75zoKdmKahe2A')
    assert response.status_code == 403
    assert response.json() == {"message": "Token has expired"}


def test_get_your_own_profile():
    response = requests.get(BASE_URL+'/login_api', auth=HTTPBasicAuth('username', 'thisisthesecretkey'))
    if 'token' in response.json():
        dic = response.json()
        token = dic['token']

    response = requests.get(BASE_URL+'/api/me?token='+token)
    # as it is not authenticated
    assert response.json() == {"message": "Not authenticated with linkedin credentials"}
