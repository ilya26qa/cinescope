import copy

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

    def test_change_all_data_booking(self, auth_session, booking_data):
        # может создание бронирование нужно вынести в фикстуру?
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=booking_data)

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
        change_booking = auth_session.put(f"{BASE_URL}/booking/{booking_id}", json=new_payload)

        for key, value in new_payload.items():
            assert change_booking.json().get(key) == value, f'{key} не совпадает'

    def test_patch_booking(self, auth_session, booking_data):
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        booking_id = create_booking.json().get("bookingid")

        new_payload = {
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "bookingdates": {
                "checkin": "2021-04-05",
                "checkout": "2022-04-08"
            }
        }
        patch_booking = auth_session.patch(f"{BASE_URL}/booking/{booking_id}", json=new_payload)
        assert patch_booking.status_code == 200, 'не удалось пропатчить'
        print(create_booking.json())
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")

        for key, value in get_booking.json().items():
            if key in new_payload:
                assert new_payload[key] == get_booking.json().get(key), f'значение {key} не изменилось, а должно'
            else:
                assert value == create_booking.json()["booking"].get(key), (f'изменилось значение {key}, которое не'
                                                                            f' должно меняться ')

    def test_get_incorrect_booking(self, auth_session):
        incorrect_id = faker.random_letters(5)
        get_booking = auth_session.get(f"{BASE_URL}/booking/{incorrect_id}")
        assert get_booking.status_code == 404, 'ожидался 404 статус код'
        assert get_booking.text == 'Not Found'

    def test_create_booking_without_required_fields(self, auth_session, booking_data):
        payload = copy.deepcopy(booking_data)
        payload.pop("firstname")
        customer_lastname = payload["lastname"]
        get_count = auth_session.get(f"{BASE_URL}/booking", params={"lastname": customer_lastname})
        booking_count = len(get_count.json())

        create_booking = auth_session.post(f"{BASE_URL}/booking", json=payload)
        assert create_booking.status_code in (500, 400), 'статус код отличается от ожидаемого'

        count_after_try = auth_session.get(f"{BASE_URL}/booking", params={"lastname": customer_lastname})
        booking_count_after_try = len(count_after_try.json())
        assert booking_count == booking_count_after_try, 'создана бронь без обязательных полей'

    def test_patch_booking_incorrect_type(self, auth_session, booking_data):
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
        booking_id = create_booking.json().get("bookingid")

        int_lastname = faker.random_int()
        patch_booking = auth_session.patch(f"{BASE_URL}/booking/{booking_id}", json={"lastname": int_lastname})
        assert patch_booking.status_code in (400, 500), 'частичное обновление с некорректным типом данных прошел'

        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.json().get("lastname") != int_lastname, 'изменено поле на неправильный тип данных'


