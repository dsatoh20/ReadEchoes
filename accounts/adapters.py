# accounts/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    pass
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data
        user.username = data.get('login')  # GitHubの場合
        user.email = data.get('email')
        if 'google' in sociallogin.account.provider:  # Googleの場合
            user.username = data.get('name')  # Google APIの応答に合わせて調整する
        user.save()
        return user