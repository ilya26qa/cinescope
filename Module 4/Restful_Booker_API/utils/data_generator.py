import random
import string
from datetime import date
from faker import Faker

faker = Faker()


class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_firstname():
        return faker.first_name()

    @staticmethod
    def generate_random_lastname():
        return faker.last_name()

    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        letters = random.choice(string.ascii_letters)
        digits = random.choice(string.digits)

        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_random_bookingdates():
        """
        Генерация дат бронирования
        Дата выселения не может быть раньше даты заселения
        """
        today = date.today()
        end_of_year = date(today.year, 12, 31)
        checkin = faker.date_between(start_date=today, end_date=end_of_year)
        checkout = faker.date_between(start_date=checkin, end_date=end_of_year)

        return {
            "checkin": f"{checkin}",
            "checkout": f"{checkout}"
        }
