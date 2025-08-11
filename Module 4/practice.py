import requests
response = requests.get("https://auth.dev-cinescope.coconutqa.ru", timeout=5)
print(response.status_code)