import allure
import pytest
from pytest_check import check

from schemas.user_entity_schema import User
from utils.data_generator import DataGenerator
from constants import AUTH_ERR_MSG
from schemas.user_fixture_schema import UserSchema, UserFixtureSchema, RegisterUserResponseSchema
from schemas.auth_shema import LoginRequestSchema, LoginResponseSchema


@allure.epic('Функционал Auth')
@allure.feature('Проверка функциональности авторизации пользователя')
class TestAuth:

    @allure.title("Тест успешной регистрации пользователя")
    def test_register_user(self, test_user: UserSchema, admin: User):
        """
        Тест на регистрацию пользователя.
        """
        with check:
            response = admin.api.auth_api.register_user(test_user, expected_status=201)
        with allure.step('Валидация тела ответа по схеме RegisterUserResponseSchema'):
            with check:
                response_data = RegisterUserResponseSchema.model_validate_json(response.text)
        with allure.step('Проверка статус-кода'):
            with check:
                assert response_data.email == test_user.email, "Email не совпадает"
        admin.api.user_api.delete_user(response_data.id, expected_status=200)

    @allure.title("Тест успешного логина пользователя")
    def test_login_user(self, super_admin: User, registered_user: UserFixtureSchema):
        """
        Тест на авторизацию пользователя.
        """
        with check:
            login_data = LoginRequestSchema(email=registered_user.email, password=registered_user.password)
            response = super_admin.api.auth_api.login_user(login_data, expected_status=200)
        with allure.step('Валидация тела ответа по схеме LoginResponseSchema'):
            with check:
                response_data = LoginResponseSchema.model_validate_json(response.text)
        with allure.step('Проверка статус-кода'):
            with check:
                assert response_data.email == registered_user.email, "Email не совпадает"
        super_admin.api.user_api.delete_user(response_data.id, expected_status=200)

    @allure.title("Тест логина пользователя с неверным паролем")
    def test_login_user_with_incorrect_password(self, admin: User, registered_user: UserFixtureSchema):
        """
        Тест логина пользователя с неверным паролем
        :param admin: User-сессия с правами ADMIN
        :param registered_user: Зарегистрированный пользователь в UserFixtureSchema
        """
        with check:
            login_data = LoginRequestSchema(email=registered_user.email, password=DataGenerator.generate_random_password())
            response = admin.api.auth_api.login_user(login_data, expected_status=401)
        response_data = response.json()
        with allure.step('Проверка сообщения в теле ответа'):
            with check:
                assert response_data['message'] == AUTH_ERR_MSG, \
                    f"Expected error message: '{AUTH_ERR_MSG}', got '{response_data['message']}'"
        admin.api.user_api.delete_user(registered_user.id, expected_status=200)
