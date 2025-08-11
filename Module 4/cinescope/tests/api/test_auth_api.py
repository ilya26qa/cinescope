import pytest
import requests
from cinescope.constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthApi:
    def test_register_user(self, requester, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=test_user,
            expected_status=201
        )
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, requester, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=201
        )
        response_data = response.json()
        assert response.status_code in (200, 201), "Ожидался 20х статус код"
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

    def test_successful_login(self, test_user):
        register_url = BASE_URL + REGISTER_ENDPOINT
        response = requests.post(register_url, json=test_user, headers=HEADERS)
        # Логируем ответ для диагностики
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        # Проверки
        assert response.status_code in (201, 200), "Ошибка регистрации пользователя"

        login_url = BASE_URL + LOGIN_ENDPOINT
        new_payload = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = requests.post(login_url, json=new_payload, headers=HEADERS)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code in (200, 201), 'ошибка авторизации'
        assert "accessToken" in response.json(), 'отсутствует поле токена'
        assert response.json().get('user').get('email') == test_user['email']

    def test_failed_login(self, test_user):
        login_url = BASE_URL + LOGIN_ENDPOINT
        new_payload = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = requests.post(login_url, json=new_payload, headers=HEADERS)
        print(f"Requests: {response.json()}")
        assert response.status_code == 401, "статус код отличается от ожидаемого"
        assert response.json().get("message") == "Неверный логин или пароль", "отсутствует поле ошибки в ответе"
