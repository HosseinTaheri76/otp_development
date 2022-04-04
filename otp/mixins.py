from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from .models import OtpSession


class OtpSessionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        phone_number = request.session.get('phone_number')
        self.otp_session = get_object_or_404(OtpSession, user__phone_number=phone_number)
        return super().dispatch(request, *args, **kwargs)


class ValidatedOtpSessionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        phone_number = request.session.get('phone_number')
        if (otp := get_object_or_404(OtpSession, user__phone_number=phone_number)).is_verified_and_valid(request.path):
            self.otp_session = otp
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseNotFound()

