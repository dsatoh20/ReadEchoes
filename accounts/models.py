from django.db import models
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from django.utils.translation import gettext_lazy as _
from PIL import Image
import io


class UserManager(BaseUserManager):
    def _create_user(self, email, username, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields,
        )

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields['is_active'] = True
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self._create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(
        verbose_name=_("username"),
        max_length=255,
        unique=True
    )
    email = models.EmailField(
        verbose_name=_("email"),
        unique=False, # 開発環境ではoauthからemailが提供されないので
        null=True,
        blank=True,
    )
    
    image = models.ImageField(upload_to='profile/', blank=True)
    
    is_superuser = models.BooleanField(
        verbose_name=_("is_superuer"),
        default=False
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_("created_at"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updateded_at"),
        auto_now=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
class Team(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_owner')
    title = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    members = models.ManyToManyField(User, related_name='team_members')
    public = models.BooleanField(default=False)
    
    found_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class InviteTeam(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_team_owner')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.owner) + 'joined' + str(self.team)
    
# 画像処理のための関数
def expand2square(pil_img, background_color=0):
    # マージンを追加して正方形にする
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result