import datetime
from unittest.mock import Mock

import pytest
import pytz
import requests
import allure
from pytest_check import check

from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT, WORLD_CLOCK_API_URL, \
    FAKE_WORLD_CLOCK_API_URL, WHAT_IS_TODAY_URL
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from constants import Roles
from schemas.user_fixture_schema import RegisterUserResponseSchema, UserSchema
import requests
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from pytest_mock import mocker


class WorldClockResponse(BaseModel):
    """
    Стурктура ответа сервера worldclockapi
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="$id")
    current_date_time: str = Field(
        examples=["2025-02-13T21:432Z", "2025-02-13T21:432Z"],
        description='Дата и время в формате ISO 8601 (YYYY-MM-DDTHH:MMZ)',
        alias='currentDateTime')
    utc_offset: str = Field(description='Смещение времени по таймзоне', alias='utcOffset')
    is_day_light_savings_time: bool = Field(alias='isDayLightSavingsTime')
    day_of_the_week: str = Field(description='День недели', alias='dayOfTheWeek')
    time_zone_name: str = Field(description='Название города по таймзоне', alias='timeZoneName')
    current_file_time: int = Field(alias='currentFileTime')
    ordinal_date: str = Field(alias='ordinalDate')
    service_response: None = Field(alias='serviceResponse')


class DateTimeRequest(BaseModel):
    """
    Структура запроса к сервису TodayIsHoliday
    """
    model_config = ConfigDict(populate_by_name=True)

    current_date_time: str = Field(
        examples=["2025-02-13T21:432Z", "2025-02-13T21:432Z"],
        description='Дата и время в формате ISO 8601 (YYYY-MM-DDTHH:MMZ)',
        alias='currentDateTime')


class WhatIsTodayResponse(BaseModel):
    """
    Структура ответа сервиса TodayIsHoliday
    """
    message: str


@allure.step('Получение данных из сервиса worldclockapi')
def get_worldclockap_time() -> WorldClockResponse:
    """
    Функция получает данные текущей даты из сервиса worldclockapi
    :return: Ответ в формате WorldClockResponse
    """
    with allure.step('Отправка GET запроса'):
        with check:
            response = requests.get(WORLD_CLOCK_API_URL)
    with allure.step('Проверка статус кода ответа сервиса'):
        with check:
            assert response.status_code == 200, "Удаленный сервис недоступен"
    with allure.step('Валидация ответа сервиса в WorldClockResponse:'):
        with check:
            return WorldClockResponse(**response.json())


@allure.step('Получение данных из Fake сервиса worldclockapi')
def get_fake_worldclockap_time() -> WorldClockResponse:
    """
    Функция получает данные текущей даты из Fake сервиса worldclockapi
    :return: Ответ в формате WorldClockResponse
    """
    with allure.step('Отправка GET запроса'):
        with check:
            response = requests.get(FAKE_WORLD_CLOCK_API_URL)
    with allure.step('Проверка статус кода ответа сервиса'):
        with check:
            assert response.status_code == 200, "Удаленный сервис недоступен"
    with allure.step('Валидация ответа сервиса в WorldClockResponse:'):
        with check:
            return WorldClockResponse(**response.json())


@allure.epic('Тесты с использованием заглушек, Fake-сервисов')
class TestTodayIsHolidayServiceAPI:

    @allure.title('Проверка работоспособности сервиса worldclockap')
    @pytest.mark.flaky(reruns=3)
    @pytest.mark.integration
    def test_fake_worldclockap(self):
        world_clock_response = get_fake_worldclockap_time()
        with check('Получение даты из ответа'):
            current_date_time = world_clock_response.currentDateTime
            print(f"Текущая дата и время: {current_date_time=}")
        with (allure.step('Проверка совпадения даты и времени')):
            assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    @allure.title('Проверка работоспособности Fake-сервиса what_is_today')
    @pytest.mark.integration
    def test_fake_what_is_today(self):
        world_clock_response = get_fake_worldclockap_time()
        with allure.step('Отправка POST запроса на сервис what_is_today'):
            with check:
                what_is_today_response = requests.post(
                    url=WHAT_IS_TODAY_URL,
                    data=DateTimeRequest(
                        currentDateTime=world_clock_response.currentDateTime).model_dump_json())
        with allure.step('Проверка статус кода ответа сервиса'):
            with check:
                assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        with allure.step('Валидация структуры ответа WhatIsTodayResponse'):
            with check:
                what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        with allure.step('Проверка сообщения ответа'):
            assert what_is_today_data.message == "Сегодня нет праздников в России.", "Сегодня нет праздника!"