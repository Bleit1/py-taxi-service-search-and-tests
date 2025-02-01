import re
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from taxi.models import Manufacturer, Car, Driver

User = get_user_model()


def get_search_results(html):
    """
    Извлекает содержимое блока с id="driver-search-results".
    Если не найдено, возвращает весь HTML.
    """
    match = re.search(r'<div id="driver-search-results">(.*?)</div>', html, re.DOTALL)
    return match.group(1) if match else html


class SearchTests(TestCase):
    def setUp(self):
        # Создаём пользователя и авторизуемся (так как доступ к страницам ограничен)
        self.user = User.objects.create_user(
            username="admin.user",
            password="12345",
            license_number="ABC123"
        )
        self.client.force_login(self.user)

        # Создаём производителей
        self.manufacturer1 = Manufacturer.objects.create(name="Toyota", country="Japan")
        self.manufacturer2 = Manufacturer.objects.create(name="Ford", country="USA")
        self.manufacturer3 = Manufacturer.objects.create(name="BMW", country="Germany")

        # Создаём автомобили
        self.car1 = Car.objects.create(model="Camry", manufacturer=self.manufacturer1)
        self.car2 = Car.objects.create(model="Corolla", manufacturer=self.manufacturer1)
        self.car3 = Car.objects.create(model="Mustang", manufacturer=self.manufacturer2)

        # Создаём водителей (кроме self.user)
        self.driver2 = User.objects.create_user(
            username="johndoe",
            password="password",
            license_number="XYZ987"
        )
        self.driver3 = User.objects.create_user(
            username="janedoe",
            password="password",
            license_number="LMN456"
        )

    def test_driver_search(self):
        url = reverse("taxi:driver-list")

        # Поиск по "test" должен вернуть только пользователя "testuser"
        response = self.client.get(url, {"q": "test"})
        content = response.content.decode()
        search_results = get_search_results(content)
        self.assertIn("testuser", search_results)
        self.assertNotIn("johndoe", search_results)
        self.assertNotIn("janedoe", search_results)

        # Поиск по "john" должен вернуть только "johndoe"
        response = self.client.get(url, {"q": "john"})
        content = response.content.decode()
        search_results = get_search_results(content)
        self.assertIn("johndoe", search_results)
        self.assertNotIn("testuser", search_results)
        self.assertNotIn("janedoe", search_results)
