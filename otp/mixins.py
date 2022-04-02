from django.http import HttpResponseNotFound
from .models import OtpSession


class OtpSessionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        otp = OtpSession.get_otp_session_by_phone_number(request.session.get('phone_number'))
        if otp:
            self.otp_session = otp
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseNotFound()


class ValidatedOtpSessionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        otp = OtpSession.get_otp_session_by_phone_number(request.session.get('phone_number'))
        if otp and otp.is_verified_and_valid(request.path):
            self.otp_session = otp
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseNotFound()
