from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django import forms
from .models import User, Team

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'image')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control mt-1'}),
            'email': forms.EmailInput(attrs={'class': 'form-control mt-1'}),
            'image': forms.FileInput(attrs={'class':'form-control mt-1'}),
        }
        
class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ["title", "description", "public"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Type your new team title...'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder': 'Type a description for your new team here...'}),
            'public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class SearchUserForm(forms.Form):
    search = forms.CharField(label='Search User', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control me-auto',
                                                           'placeholder': 'Type a username...'}))
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'image']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }