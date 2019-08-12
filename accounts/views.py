from django import forms
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView
from django.views.generic.base import TemplateView, View
from django.contrib import messages 
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.decorators import method_decorator

from config import settings
from .forms import UserRegistrationForm, VerificationEmailForm, CustomUserChangeForm
from .mixin import VerifyEmailMixin

# 유저 회원가입
class UserRegistrationView(VerifyEmailMixin, CreateView) :
    model = get_user_model()
    form_class = UserRegistrationForm
    success_url = '/'
    verify_url = '/accounts/verify/'
    template_name = 'accounts/signup.html'

    def form_valid(self, form) :
        response = super().form_valid(form)
        if form.instance :
           self.send_verification_email(form.instance)
        return response
    
UserRegistration = UserRegistrationView.as_view()

# 이메일 인증
class UserVerificationView(TemplateView) :
    model = get_user_model()
    redirect_url = '/'
    token_generator = default_token_generator

    def get(self, request, *args, **kwargs) :
        if self.is_valid_token(**kwargs) :
            messages.info(request, '인증 완료')
        else :
            messages.error(request, '인증 실패')
        return HttpResponseRedirect(self.redirect_url)
    
    def is_valid_token(self, **kwargs) :
        pk = kwargs.get('pk')
        token = kwargs.get('token')
        user = self.model.objects.get(pk = pk)
        is_valid = self.token_generator.check_token(user, token)
        if is_valid :
            user.is_active = True
            user.save()
        return is_valid

UserVerification = UserVerificationView.as_view()

# 이메일 재전송
class ResendVerifyEmailView(VerifyEmailMixin, FormView):
    model = get_user_model()
    form_class = VerificationEmailForm
    success_url = '/'
    template_name = 'accounts/resend_email.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = self.model.objects.get(email = email)
        except self.model.DoesNotExist:
            messages.error(self.request, '알 수 없는 사용자 입니다.')
        else:
            self.send_verification_email(user)
        return super().form_valid(form)

ResendMail = ResendVerifyEmailView.as_view()

# 로그인
class UserLoginView(LoginView) :
    template_name = 'accounts/login.html'

    def form_invalid(self, form) :
        messages.error(self.request, '로그인에 실패하였습니다', extra_tags = 'danger')
        return super().form_invalid(form)

UserLogin = UserLoginView.as_view()

# 비밀번호 변경

#@login_required
#def change_password(request):
#    if request.method == 'POST':
#        form = PasswordChangeForm(request.user, request.POST)
#        if form.is_valid():
#            user = form.save()
#            update_session_auth_hash(request, user)  # Important!
#            messages.success(request, 'Your password was successfully updated!')
#           
#            return redirect('/')
#        else:
#            messages.error(request, 'Please correct the error below.')
#    else:
#        form = PasswordChangeForm(request.user)
#    return render(request, 'accounts/change_pw.html', {
#        'form': form
#    })

# 회원정보 변경

@login_required
def update_user(request) :

    user = get_user_model()

    if request.method == 'POST' :

        user_change_form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)

        #user_change_form.username = request.POST.get(_('name'))
        #user_change_form.old_password = request.POST.get('old_password')
        #user_change_form.password1 = request.POST.get('password1')
        #user_change_form.password2 = request.POST.get('password2')

        if user_change_form.is_valid() :
            user = user_change_form.save(commit = False)

            old_password = user_change_form.cleaned_data['old_password']
            if not user.check_password(old_password) :
                raise ValidationError("이전 비밀번호가 틀렸습니다!")

            user_change_form.clean_new_password2()

            user.name = user_change_form.cleaned_data['name']
            user.set_password(user_change_form.cleaned_data['password1'])
            
            if request.FILES.get('profile_image') :
                user.profile_image = request.FILES.get('profile_image')
            
            user.save()
            
            return redirect('/')
        
        else :

            raise ValidationError("잘못된 양식입니다.")

    else : 
        user_change_form = CustomUserChangeForm(instance = request.user)
        context = {
            'form' : user_change_form
        }

        return render(request, 'accounts/update_user.html', context)