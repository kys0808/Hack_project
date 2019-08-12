
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import os

class UserManager(BaseUserManager) :

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields) :

        if not email :
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)

        return user

    def create_user(self, email = None, password = None, **extra_fields) :

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_expert', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields) :

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_expert', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True :
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True :
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)
    
def validate_image(image):

    ext = os.path.splitext(image.name)[1]
    valid = ['.jpg', '.jpeg', '.png']
    file_size = image.file.size
    limit = 4

    if file_size > limit * 1024 * 1024:
        raise ValidationError("이미지 파일이 너무 큽니다.")
    
    if ext not in valid :
        raise ValidationError("지원하지 않는 이미지 형식입니다.")
    

class User(AbstractBaseUser, PermissionsMixin) :

    email = models.EmailField(
        verbose_name = _('Email Address'),
        max_length = 255, 
        unique = True
    )

    name = models.CharField(
        verbose_name = _('Nick Name'),
        max_length = 30,
        unique = True
    )

    profile_image = models.ImageField(
        verbose_name = _('프로필 이미지'),
        blank = True,
        null = True,
        upload_to = 'profile_image',
        default = None,
        validators = [validate_image]
    )

    is_staff = models.BooleanField(
        verbose_name = _('관리자 권한'),
        default = False
    )

    is_active = models.BooleanField(
        verbose_name = _('사용중'),
        default = False
    )

    is_expert = models.BooleanField(
        verbose_name = _('전문가'),
        default = False
    )

    date_joined  = models.DateTimeField(
        verbose_name = _('가입일'),
        default = timezone.now
    )
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta : 

        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    def email_user(self, subject, message, from_email=None, **kwargs) :

        send_mail(subject, message, from_email, [self.email], **kwargs)
