from django.shortcuts import redirect
from django.contrib import messages
from . import exceptions


class OtpHandler:
    config = {
        exceptions.OtpSessionBlocked: {
            'redirect_url': '/',
            'message': 'your access to otp request has been blocked due to exceeding limit of failures.'
        },
        exceptions.OtpSessionExpired: {
            'redirect_url': 'verify_otp',
            'message': 'this session has expired please request for code again'
        },
        exceptions.ActiveOtpSessionExists: {
            'redirect_url': 'verify_otp',
            'message': 'you cannot request for code for {} more seconds.'
        }
    }

    @staticmethod
    def handle_request_new_session(request, otp_session, target_view_name=None):
        try:
            otp_session.start_new_session(target_view_name)
            return redirect('verify_otp')
        except (exceptions.ActiveOtpSessionExists, exceptions.OtpSessionBlocked) as e:
            config = OtpHandler.config[e.__class__]
            message = config['message']
            if isinstance(e, exceptions.ActiveOtpSessionExists):
                message = message.format(otp_session.remaining_seconds())
            messages.add_message(request, messages.ERROR, message)
            return redirect(config['redirect_url'])

    @staticmethod
    def handle_verify_session(request, otp_session, code):
        try:
            if otp_session.verify_session(code):
                return redirect(otp_session.target_view_name)
            messages.add_message(request, messages.ERROR, 'the code is invalid')
            return redirect('verify_otp')
        except (exceptions.OtpSessionBlocked, exceptions.OtpSessionExpired) as e:
            messages.add_message(request, messages.ERROR, OtpHandler.config[e.__class__]['messages'])
            return redirect(OtpHandler.config[e.__class__]['redirect_url'])





