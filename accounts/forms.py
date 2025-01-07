from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import User, Team

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        
class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ["title", "description", "public"]