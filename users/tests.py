from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from graphene.test import Client

from hunar.schema import schema
from users.models.users import User


class AuthMutationsTests(TestCase):
    def setUp(self):
        self.client = Client(schema)

    def test_register_user(self):
        response = self.client.execute(
            """
            mutation {
                registerUser(email: \"test@example.com\", password: \"StrongPass123\") {
                    token
                    user {
                        email
                    }
                }
            }
            """
        )

        self.assertIsNone(response.get("errors"))
        self.assertEqual(response["data"]["registerUser"]["user"]["email"], "test@example.com")
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_login_with_password(self):
        User.objects.create_user(email="login@example.com", password="StrongPass123")

        response = self.client.execute(
            """
            mutation {
                loginUser(email: \"login@example.com\", password: \"StrongPass123\") {
                    token
                    user {
                        email
                    }
                }
            }
            """
        )

        self.assertIsNone(response.get("errors"))
        self.assertEqual(response["data"]["loginUser"]["user"]["email"], "login@example.com")

    def test_login_with_otp(self):
        user = User.objects.create_user(email="otp@example.com", password="StrongPass123")
        user.otp_code = "123456"
        user.otp_created_at = timezone.now()
        user.save(update_fields=["otp_code", "otp_created_at"])

        response = self.client.execute(
            """
            mutation {
                loginUser(email: \"otp@example.com\", otp: \"123456\") {
                    token
                    user {
                        email
                    }
                }
            }
            """
        )

        self.assertIsNone(response.get("errors"))
        self.assertEqual(response["data"]["loginUser"]["user"]["email"], "otp@example.com")

    @patch('users.schema.send_mail')
    def test_send_otp_sends_email(self, mock_send_mail):
        User.objects.create_user(email="otpmail@example.com", password="StrongPass123")

        response = self.client.execute(
            """
            mutation {
                sendOtp(email: \"otpmail@example.com\") {
                    success
                    message
                }
            }
            """
        )

        self.assertIsNone(response.get("errors"))
        self.assertTrue(response["data"]["sendOtp"]["success"])
        mock_send_mail.assert_called_once()
