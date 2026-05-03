import sys
import requests

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Test signup
url = "http://127.0.0.1:8000/api/auth/signup"
data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
