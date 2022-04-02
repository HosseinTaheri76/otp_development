import time
from time import sleep
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import OtpSession
from . import exceptions

OtpSession.SESSION_EXPIRES_AFTER = 1
OtpSession.VERIFIED_SESSION_EXPIRES_AFTER = 2


class TestOtpSessionModel(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_user('09124470199', 'mmhs42497686')
        OtpSession.start_first_session(user, 'home')
        self.otp_session = user.otpsession

    def test_first_session_initialized_correctly(self):
        self.assertEqual(
            self.otp_session.datetime_session_expires.replace(microsecond=0),
            (timezone.now() + timedelta(seconds=OtpSession.SESSION_EXPIRES_AFTER)).replace(microsecond=0)
        )

    def test_first_session_verification(self):
        self.assertEqual(self.otp_session.verify_session(self.otp_session.code), True)

    def test_new_session_cannot_start_before_previous_expires(self):
        self.assertRaises(
            exceptions.ActiveOtpSessionExists,
            self.otp_session.start_new_session
        )

    def test_new_session_can_start_after_previous_expires(self):
        sleep(1)
        self.otp_session.start_new_session()
        self.assertEqual(
            self.otp_session.datetime_session_expires.replace(microsecond=0),
            (timezone.now() + timedelta(seconds=OtpSession.SESSION_EXPIRES_AFTER)).replace(microsecond=0)
        )

    def test_invalid_code_fails_and_increases_failures(self):
        sleep(1)
        self.otp_session.start_new_session()
        self.assertEqual(self.otp_session.verify_session(12), False)
        self.assertEqual(self.otp_session.failures, 1)

    def test_exceeding_failures_leads_to_blockage(self):
        sleep(1)
        self.otp_session.start_new_session()
        for num in range(1, OtpSession.FAILURE_TOLERANCE + 1):
            self.assertEqual(self.otp_session.verify_session(num), False)
            self.assertEqual(self.otp_session.failures, num)
        self.assertRaises(
            exceptions.OtpSessionBlocked,
            self.otp_session.verify_session,
            12
        )
        self.assertRaises(exceptions.OtpSessionBlocked, self.otp_session.start_new_session)

    def test_newly_started_session_not_verified_and_valid(self):
        self.assertEqual(self.otp_session.is_verified_and_valid('/'), False)

    def test_verified_session_will_be_valid_in_time_with_correct_request_path(self):
        self.otp_session.verify_session(self.otp_session.code)
        self.assertEqual(self.otp_session.is_verified_and_valid('/'), True)

    def test_verified_session_will_expire(self):
        self.otp_session.verify_session(self.otp_session.code)
        time.sleep(OtpSession.VERIFIED_SESSION_EXPIRES_AFTER)
        self.assertEqual(self.otp_session.is_verified_and_valid('/'), False)

    def test_verified_session_will_not_work_for_another_path(self):
        self.otp_session.verify_session(self.otp_session.code)
        self.assertEqual(self.otp_session.is_verified_and_valid('/products/'), False)

    def test_otp_session_by_phone_number(self):
        self.assertEqual(OtpSession.get_otp_session_by_phone_number('09302844505'), None)
        self.assertEqual(OtpSession.get_otp_session_by_phone_number('09124470199'), self.otp_session)

    def test_completed_and_ended_session_is_not_valid(self):
        self.otp_session.verify_session(self.otp_session.code)
        self.assertEqual(self.otp_session.is_verified_and_valid('/'), True)
        self.otp_session.complete_and_end_session()
        self.assertEqual(self.otp_session.is_verified_and_valid('/'), False)

    def test_newly_started_session_will_use_previous_target_view_if_not_provided(self):
        sleep(OtpSession.SESSION_EXPIRES_AFTER)
        self.otp_session.start_new_session()
        self.assertEqual(self.otp_session.target_view_name, 'home')

    def test_newly_started_session_will_use_provided_target_view_name(self):
        sleep(OtpSession.SESSION_EXPIRES_AFTER)
        self.otp_session.start_new_session('products')
        self.assertEqual(self.otp_session.target_view_name, 'products')

    def test_correct_code_will_clear_failures(self):
        sleep(1)
        self.otp_session.start_new_session()
        for num in range(1, OtpSession.FAILURE_TOLERANCE + 1):
            self.assertEqual(self.otp_session.verify_session(num), False)
            self.assertEqual(self.otp_session.failures, num)
        self.otp_session.verify_session(self.otp_session.code)
        self.assertEqual(self.otp_session.failures, 0)
