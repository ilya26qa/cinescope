import copy

from faker import Faker
from Restful_Booker_API.constants import BASE_URL, BOOKING_ENDPOINT, HEADERS

faker = Faker()


class TestBookings:
    def test_create_booking(self, requester, test_booking):
        """
        Тест на создание бронирования. Очень много проверок в одной тестовой функции, возможно стоит разделить на
        отдельные тесты, но не уверен, так как все проверки относятся к созданию бронирования
        :param requester: Фикстура.
        :param test_booking: Фикстура.
        """
        response = requester.send_request(
            method="POST",
            endpoint=BOOKING_ENDPOINT,
            data=test_booking,
        )

        booking_id = response.json().get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert response.json()["booking"]["firstname"] == test_booking["firstname"], "Заданное имя не совпадает"
        assert response.json()["booking"]["totalprice"] == test_booking["totalprice"], ("Заданная стоимость не "
                                                                                              "совпадает")
        # Проверяем, что бронирование можно получить по ID

        get_booking = requester.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}"
        )
        assert get_booking.json()["lastname"] == test_booking["lastname"], "Заданная фамилия не совпадает"

    def test_change_all_data_booking(self, requester, get_token, created_booking, test_booking):
        response = requester.send_request(
            method="PUT",
            endpoint=f"{BOOKING_ENDPOINT}/{created_booking['id']}",
            data=test_booking
        )

        for key, value in response.json().items():
            assert created_booking.get(key) == value, f'{key} не совпадает'

    def test_patch_booking(self, auth_session, test_booking):
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=test_booking)
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

    def test_create_booking_without_required_fields(self, auth_session, test_booking):
        payload = copy.deepcopy(test_booking)
        payload.pop("firstname")
        customer_lastname = payload["lastname"]
        get_count = auth_session.get(f"{BASE_URL}/booking", params={"lastname": customer_lastname})
        booking_count = len(get_count.json())

        create_booking = auth_session.post(f"{BASE_URL}/booking", json=payload)
        assert create_booking.status_code in (500, 400), 'статус код отличается от ожидаемого'

        count_after_try = auth_session.get(f"{BASE_URL}/booking", params={"lastname": customer_lastname})
        booking_count_after_try = len(count_after_try.json())
        assert booking_count == booking_count_after_try, 'создана бронь без обязательных полей'

    def test_patch_booking_incorrect_type(self, auth_session, test_booking):
        create_booking = auth_session.post(f"{BASE_URL}/booking", json=test_booking)
        booking_id = create_booking.json().get("bookingid")

        int_lastname = faker.random_int()
        patch_booking = auth_session.patch(f"{BASE_URL}/booking/{booking_id}", json={"lastname": int_lastname})
        assert patch_booking.status_code in (400, 500), 'частичное обновление с некорректным типом данных прошел'

        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.json().get("lastname") != int_lastname, 'изменено поле на неправильный тип данных'


