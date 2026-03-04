from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from .models.auth_model import User
from .models.travel_model import Destination, Hotel, ImageAsset


class RegistrationSecurityTests(APITestCase):
    def test_register_ignores_admin_role_input(self):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "StrongPass123!",
            "role": "admin",
        }
        response = self.client.post(reverse("auth_register"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["role"], "user")
        self.assertEqual(User.objects.get(username="alice").role, "user")


class AdminCrudMultipartTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="AdminPass123!",
            role="admin",
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_destination_with_images_multipart(self):
        image = SimpleUploadedFile("photo.jpg", b"fake-image-bytes", content_type="image/jpeg")
        payload = {
            "name": "Jeddah",
            "country": "Saudi Arabia",
            "flight_cost": "300.00",
            "daily_living_cost": "120.00",
            "is_coastal": True,
            "description": "Coastal destination",
            "best_seasons": "summer,winter",
            "images": [image],
        }
        response = self.client.post(reverse("admin-destinations-list"), payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Destination.objects.count(), 1)
        self.assertEqual(ImageAsset.objects.filter(destination_id=response.data["id"]).count(), 1)


class AIChatFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="UserPass123!",
            role="user",
        )
        self.client.force_authenticate(user=self.user)
        self.destination = Destination.objects.create(
            name="Abha",
            country="Saudi Arabia",
            flight_cost="250.00",
            daily_living_cost="80.00",
            is_coastal=False,
            description="Mountain destination",
            best_seasons="summer,spring",
        )
        self.hotel = Hotel.objects.create(
            destination=self.destination,
            name="Abha Peak Hotel",
            stars=4,
            price_per_night="130.00",
            is_sea_view=False,
        )

    @override_settings(OPENROUTER_API_KEY=None)
    def test_ai_chat_returns_options_with_session(self):
        response = self.client.post(reverse("ai_chat_plan"), {"prompt": "أبغى رحلة مناسبة"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "missing_info")
        self.assertTrue(response.data.get("session_id"))

        session_id = response.data["session_id"]
        response2 = self.client.post(
            reverse("ai_chat_plan"),
            {"prompt": "ميزانيتي 2000 دولار، 4 أيام، شخصين، جبلية، 4 نجوم", "session_id": session_id},
            format="json",
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["status"], "options_presented")
        self.assertGreaterEqual(len(response2.data.get("options", [])), 1)
