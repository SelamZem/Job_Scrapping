import sys
import requests

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

url = "https://landing.jobs/api/v1/jobs"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}
params = {'remote': 'true'}

response = requests.get(url, headers=headers, params=params, timeout=30)
data = response.json()

if isinstance(data, list) and len(data) > 0:
    print("First job structure:")
    for key in data[0].keys():
        print(f"  {key}: {data[0][key]}")
