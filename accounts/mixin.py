from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render

from config import settings

class VerifyEmailMixin :
    email_template_name = 'accounts/verification.html'
    token_generator = default_token_generator

    def send_verification_email(self, user) :
        token = self.token_generator.make_token(user)
        url = self.build_verification_link(user, token)
        subject = '가입 축하드립니다!'
        message = '인증하세요{}'.format(url)
        html_message = render(self.request, self.email_template_name, {'url' : url}).content.decode('utf-8')
        user.email_user(subject, message, from_email = settings.EMAIL_HOST_USER, html_message = html_message)
        messages.info(self.request, '가입 축하드립니다. 인증해주세요')

    def build_verification_link(self, user, token) :
        return '{}/accounts/{}/verify/{}/'.format(self.request.META.get('HTTP_ORIGIN'), user.pk, token)