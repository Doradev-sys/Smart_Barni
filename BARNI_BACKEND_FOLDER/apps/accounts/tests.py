from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin1", password="StrongPass123!", role=User.Role.ADMIN
        )

    def test_admin_can_register_waiter(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "username": "waiter1",
            "first_name": "Abel",
            "last_name": "T",
            "email": "abel@example.com",
            "phone_number": "0911000000",
            "role": "WAITER",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
        }
        response = self.client.post(reverse("accounts:register_staff"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="waiter1", role="WAITER").exists())

    def test_non_admin_cannot_register_staff(self):
        waiter = User.objects.create_user(
            username="waiter2", password="StrongPass123!", role=User.Role.WAITER
        )
        self.client.force_authenticate(waiter)
        payload = {
            "username": "kitchen1",
            "role": "KITCHEN_STAFF",
            "password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
        }
        response = self.client.post(reverse("accounts:register_staff"), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_returns_tokens_and_role(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "admin1", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["role"], "ADMIN")

    def test_login_failed_wrong_password_logs_attempt(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "admin1", "password": "wrong"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(
            reverse("accounts:login"),
            {"username": "admin1", "password": "StrongPass123!"},
        )
        refresh = login.data["refresh"]
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse("accounts:logout"), {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
