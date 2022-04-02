from django import forms
from .models import OtpSession


class OtpVerificationForm(forms.Form):
    code = forms.IntegerField(max_value=9999, min_value=1000)


class OtpRequestForm(forms.Form):
    phone_number = forms.RegexField('^09[0-9]{9}$')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if otp := OtpSession.get_otp_session_by_phone_number(phone_number):
            self.otp_session = otp
            return phone_number
        raise forms.ValidationError('user with given phone number does not exists.')
