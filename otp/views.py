from django.shortcuts import render
from django.views import generic
from .models import OtpSession
from .helpers import OtpHandler
from .forms import OtpVerificationForm
from .mixins import OtpSessionRequiredMixin


class VerifyOtpView(OtpSessionRequiredMixin, generic.FormView):
    form_class = OtpVerificationForm
    template_name = 'otp/verify_otp.html'

    def form_valid(self, form):
        code = int(form.cleaned_data.get('code'))
        return OtpHandler.handle_verify_session(self.request, self.otp_session, code)

