from datetime import timedelta
from random import randint
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from . import exceptions

User = get_user_model()


class OtpSession(models.Model):
    SESSION_EXPIRES_AFTER = 180
    VERIFIED_SESSION_EXPIRES_AFTER = 300
    FAILURE_TOLERANCE = 3

    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    code = models.PositiveIntegerField()
    datetime_session_expires = models.DateTimeField()
    target_view_name = models.CharField(max_length=75)
    is_verified = models.BooleanField(default=False)
    failures = models.PositiveSmallIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    datetime_verified_session_expires = models.DateTimeField(null=True)

    @classmethod
    def _initialize_session(cls, instance, target_view_name):
        instance.code = randint(1000, 9999)
        instance.target_view_name = target_view_name
        instance.datetime_session_expires = timezone.now() + timedelta(seconds=cls.SESSION_EXPIRES_AFTER)
        instance.save()

    @classmethod
    def start_first_session(cls, user, target_view_name):
        instance = cls(user_id=user.id)
        cls._initialize_session(instance, target_view_name)
        instance.send_code_via_sms()

    def send_code_via_sms(self):
        print(f'{self.code} sent to {self.user.phone_number}')

    def start_new_session(self, target_view_name=None):
        if not self.is_blocked:
            if self.datetime_session_expires < timezone.now():
                self._initialize_session(self, target_view_name or self.target_view_name)
                self.send_code_via_sms()
                return
            raise exceptions.ActiveOtpSessionExists
        raise exceptions.OtpSessionBlocked

    def _code_valid(self):
        if self.failures > 0:
            self.failures = 0
        self.is_verified = True
        self.datetime_verified_session_expires = timezone.now() + timedelta(seconds=self.VERIFIED_SESSION_EXPIRES_AFTER)
        self.save()
        return True

    def _code_invalid(self):
        self.failures += 1
        if self.failures > self.FAILURE_TOLERANCE:
            self.is_blocked = True
            self.save()
            raise exceptions.OtpSessionBlocked
        self.save()
        return False

    def verify_session(self, code):
        if not self.is_blocked:
            if self.datetime_session_expires > timezone.now():
                if self.code == code:
                    return self._code_valid()
                return self._code_invalid()
            raise exceptions.OtpSessionExpired
        raise exceptions.OtpSessionBlocked

    @classmethod
    def get_otp_session_by_phone_number(cls, phone_number):
        try:
            return cls.objects.get(user__phone_number=phone_number)
        except cls.DoesNotExist:
            return None

    def is_verified_and_valid(self, request_path):
        return (
                self.is_verified and
                self.datetime_verified_session_expires and
                self.datetime_verified_session_expires > timezone.now() and
                reverse(self.target_view_name) == request_path
        )

    def complete_and_end_session(self):
        self.is_verified = False
        self.datetime_verified_session_expires = None
        self.datetime_session_expires = timezone.now()
        self.save()

    def remaining_seconds(self):
        return (self.datetime_session_expires - timezone.now()).seconds
