
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from . import views

LogOut = LogoutView.as_view()

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.UserRegistration, name = 'signup'),
    path('login/', views.UserLogin, name = 'login'),
    path('resend_verify_email/', views.ResendMail, name = 'resend'),
    path('<pk>/verify/<token>/', views.UserVerification, name = 'verify'),
    path('logout/', LogOut, name='logout'),
    #path('password/', views.change_password, name = 'change_password'), 
    path('user_update/', views.update_user, name = 'user_update'),
    #path('upload_profile/', views.upload_profile, name = 'upload_profile'),
]