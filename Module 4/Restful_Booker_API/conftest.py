import os
import pytest
import requests
from cloudscraper import session

from dotenv import load_dotenv
from faker import Faker
from utils.data_generator import DataGenerator
from constants import *
from custom_requester.custom_requester import CustomRequester

load_dotenv()
faker = Faker()


@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope="session")
def test_booking():
    """
    Генерация данных для случайного бронирования в тестах.
    """
    firstname = DataGenerator.generate_random_firstname()
    lastname = DataGenerator.generate_random_lastname()
    bookingdates = DataGenerator.generate_random_bookingdates()

    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": faker.random_int(min=1000, max=10000),
        "depositpaid": faker.boolean(),
        "bookingdates": bookingdates,
        "additionalneeds": ''.join(faker.random_letters())
    }


@pytest.fixture(scope="session")
def created_booking(requester, test_booking):
    """
    Фикстура для создания тестового бронирования и получения данных о нем.
    """
    response = requester.send_request(
        method="POST",
        endpoint=BOOKING_ENDPOINT,
        data=test_booking,
        expected_status=200
    )
    response_data = response.json()
    created_booking = test_booking.copy()
    created_booking["id"] = response_data["bookingid"]
    yield created_booking
    pass


@pytest.fixture(scope="session")
def get_token(requester):
    response = requester.send_request(
        method="POST",
        endpoint=AUTH_ENDPOINT,
        data={
            "username": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
        }
    )
    token = response.json()["token"]
    requester.set_my_cookies(token=token)
