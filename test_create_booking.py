import pytest
from faker import Faker
from constants import HEADERS, BASE_URL

faker = Faker()


class TestBookings:
    def test_create_booking(self, auth_session, booking_data):
        # Создаём бронирование
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        assert create_booking.status_code == 200, "Ошибка при создании брони"

        booking_id = create_booking.json().get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert create_booking.json()["booking"]["firstname"] == booking_data["firstname"], "Заданное имя не совпадает"
        assert create_booking.json()["booking"]["totalprice"] == booking_data["totalprice"], ("Заданная стоимость не "
                                                                                              "совпадает")
        # Проверяем, что бронирование можно получить по ID
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data["lastname"], "Заданная фамилия не совпадает"

        # Удаляем бронирование
        deleted_booking = auth_session.delete(f"{BASE_URL}/booking/{booking_id}")
        assert deleted_booking.status_code == 201, "Бронь не удалилась"

        # Проверяем, что бронирование больше недоступно
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 404, "Бронь не удалилась"

    def test_change_all_data_booking1(self, auth_session, booking_data):
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        assert create_booking.status_code == 200, "Ошибка при создании брони"

        booking_id = create_booking.json().get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"

        new_payload = {
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "totalprice": faker.random_int(min=100, max=100000),
            "depositpaid": False,
            "bookingdates": {
                    "checkin": "2028-04-05",
                    "checkout": "2028-04-08"
            },
            "additionalneeds": "blowjob"
        }

        # первый вариант
        change_booking = auth_session.put(f"{BASE_URL}/booking/{booking_id}", json=new_payload)
        assert change_booking.status_code == 200, 'Бронь не изменена'
        assert change_booking.json() == new_payload, 'Ответ по запросу не совпадает'
        # второй вариант
        assert change_booking.json()["firstname"] == new_payload["firstname"], 'имя не совпадает'
        assert change_booking.json()["lastname"] == new_payload["lastname"], 'фамилия не совпадает'
        assert change_booking.json()["totalprice"] == new_payload["totalprice"], 'цена не совпадает'
        assert change_booking.json()["depositpaid"] == False, 'статус оплаты не совпадает'
        assert (change_booking.json()["bookingdates"]["checkin"] ==
                new_payload["bookingdates"]["checkin"]), 'дата заезда не совпадает'
        assert (change_booking.json()["bookingdates"]["checkout"] ==
                new_payload["bookingdates"]["checkout"]), 'дата выезда не совпадает'
        # третий вариант
        for key, value in new_payload.items():
            assert change_booking.json().get(key) == value, f'{key} не совпадает'


