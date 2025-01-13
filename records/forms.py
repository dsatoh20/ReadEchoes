from django.db import models
from django import forms
from django.forms import ModelForm
from .models import Book, Comment
from accounts.models import Team
from django.db.models import Q

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['team', 'title', 'first_author', 'score', 'summary', 'report']
        widgets = {
            'team': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Type or paste a book title here...'}),
            'first_author': forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Type or paste its first author name here...'}),
            'score': forms.NumberInput(attrs={'class': 'form-range', 
                                              'type': 'range',
                                              'min': 1,
                                              'max': 10}),
            'summary': forms.Textarea(attrs={'class': 'form-control',
                                             'placeholder': 'Type a summary for this book here...',
                                             'id': 'floatingTextarea'}),
            'report': forms.Textarea(attrs={'class': 'form-control',
                                            'placeholder': 'Type your view for this book here ...',
                                            'id': 'floatingTextarea'}),
        }
    def __init__(self, *args, user=None, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        if user:
            teams = Team.objects.filter(Q(members=user)|Q(owner=user)).distinct()
            self.fields['team'].choices = [(item.id, item.title) for item in teams]
            
class BookUpdateForm(ModelForm):
    class Meta:
        model = Book
        fields = ['team', 'title', 'first_author', 'pub_year', 'score', 'summary', 'report']
        
        widgets = {
            'team': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Type or paste a book title here...'}),
            'first_author': forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Type or paste its first author name here...'}),
            'pub_year': forms.NumberInput(attrs={'class': 'form-control',
                                                  'placeholder': 'Publication year'}),
            'score': forms.NumberInput(attrs={'class': 'form-range', 
                                              'type': 'range',
                                              'min': 1,
                                              'max': 10}),
            'summary': forms.Textarea(attrs={'class': 'form-control',
                                             'placeholder': 'Type a summary for this book here...',
                                             'id': 'floatingTextarea'}),
            'report': forms.Textarea(attrs={'class': 'form-control',
                                            'placeholder': 'Type your view for this book here ...',
                                            'id': 'floatingTextarea'}),
        }
    def __init__(self, *args, user=None, **kwargs):
        super(BookUpdateForm, self).__init__(*args, **kwargs)
        if user:
            teams = Team.objects.filter(Q(members=user)|Q(owner=user)).distinct()
            self.fields['team'].choices = [(item.id, item.title) for item in teams]

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control',
                                             'placeholder': 'Type a comment within 140 characters...',
                                             'id': 'floatingTextarea'}),
        }
        
class TeamSelectForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_teams = Team.objects.filter(Q(members=user)|Q(owner=user)).distinct() if user.username != '' else Team.objects.none()
        choices = [('-', '-')] + [('All', 'All')] + [(team.id, team.title) for team in \
                available_teams] + [('Public', 'Public')]
        self.fields['team'] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={'class':'form-select rounded-start'}),
            required=False,
        )
    def clean_team(self):
        team = self.cleaned_data['team']
        if team == '-':
            raise forms.ValidationError('Select one team.')
        return team