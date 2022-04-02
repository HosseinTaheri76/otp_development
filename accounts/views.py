from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import SetPasswordForm
from otp.models import OtpSession
from otp.mixins import ValidatedOtpSessionRequiredMixin
from otp.forms import OtpRequestForm
from otp.helpers import OtpHandler


class SignupView(generic.FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('verify_otp')

    def form_valid(self, form):
        user = form.save()
        OtpSession.start_first_session(user, 'activate_account')
        self.request.session['phone_number'] = user.phone_number
        return super().form_valid(form)


class ActivateAccountView(ValidatedOtpSessionRequiredMixin, generic.View):
    def get(self, request):
        user = self.otp_session.user
        user.is_active = True
        user.save()
        self.otp_session.complete_and_end_session()
        del request.session['phone_number']
        return redirect('login')


class PasswordResetRequest(generic.FormView):
    form_class = OtpRequestForm
    template_name = 'registration/password_reset_request.html'
    success_url = reverse_lazy('verify_otp')

    def form_valid(self, form):
        self.request.session['phone_number'] = form.cleaned_data.get('phone_number')
        return OtpHandler.handle_request_new_session(self.request, form.otp_session, 'my_password_reset')


class PasswordResetView(ValidatedOtpSessionRequiredMixin, generic.FormView):
    form_class = SetPasswordForm
    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.otp_session.user
        return kwargs

    def form_valid(self, form):
        form.save()
        self.otp_session.complete_and_end_session()
        del self.request.session['phone_number']
        return super().form_valid(form)


