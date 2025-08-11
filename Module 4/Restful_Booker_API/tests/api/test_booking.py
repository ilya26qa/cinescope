import copy

from faker import Faker
from Restful_Booker_API.constants import BASE_URL, BOOKING_ENDPOINT, HEADERS
from Restful_Booker_API.utils.data_generator import DataGenerator

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
        # Проверяем, что бронирование можно получить по ID
        assert booking_id is not None, "Идентификатор брони не найден в ответе"

        get_booking = requester.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}"
        )
        assert get_booking.json()["lastname"] == test_booking["lastname"], "Заданная фамилия не совпадает"
        assert response.json()["booking"]["firstname"] == test_booking["firstname"], "Заданное имя не совпадает"
        assert response.json()["booking"]["totalprice"] == test_booking["totalprice"], ("Заданная стоимость не "
                                                                                        "совпадает")

    def test_change_all_data_booking(self, requester, get_token, created_booking, test_booking):
        """
        Тест на изменение всех данных о бронировании
        :param requester:
        :param get_token:
        :param created_booking:
        :param test_booking:
        """
        response = requester.send_request(
            method="PUT",
            endpoint=f"{BOOKING_ENDPOINT}/{created_booking['id']}",
            data=test_booking
        )

        for key, value in response.json().items():
            assert created_booking.get(key) == value, f'{key} не совпадает'

    def test_patch_booking(self, requester, get_token, created_booking):
        """
        Тест на изменение некоторых данных в бронировании
        :param requester:
        :param get_token:
        :param created_booking:
        """
        new_payload = {
            "firstname": DataGenerator.generate_random_firstname(),
            "lastname": DataGenerator.generate_random_lastname(),
            "bookingdates": DataGenerator.generate_random_bookingdates()
        }
        requester.send_request(
            method="PATCH",
            endpoint=f"{BOOKING_ENDPOINT}/{created_booking['id']}",
            data=new_payload
        )
        get_response = requester.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{created_booking['id']}"
        )

        for key, value in get_response.json().items():
            if key in new_payload:
                assert new_payload[key] == get_response.json().get(key), f'значение {key} не изменилось, а должно'
            else:
                assert value == created_booking.get(key), (f'изменилось значение {key}, которое не' 
                                                                            f' должно меняться ')

    def test_get_incorrect_booking(self, requester, get_token):
        """
        Негативный тест на получение несуществующего бронирования
        """
        incorrect_id = faker.random_letters(5)
        response = requester.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{incorrect_id}",
            expected_status=404
        )
        assert response.text == 'Not Found'

    def test_create_booking_without_required_fields(self, requester, get_token, test_booking):
        """
        Негативный тест на попытку создания бронирования без обязательных полей.
        :param requester:
        :param get_token:
        :param test_booking:
        """
        payload = copy.deepcopy(test_booking)
        payload.pop("firstname")
        customer_lastname = payload["lastname"]

        def get_bookings_count():
            booking_count = requester.send_request(
                method="GET",
                endpoint=f"{BOOKING_ENDPOINT}",
                params={"lastname": customer_lastname}
            )
            return len(booking_count.json())

        count_before_try = get_bookings_count()
        requester.send_request(
            method="POST",
            endpoint=f"{BOOKING_ENDPOINT}",
            data=payload,
            expected_status=500
        )
        count_after_try = get_bookings_count()
        assert count_before_try == count_after_try, 'создана бронь без обязательных полей'
