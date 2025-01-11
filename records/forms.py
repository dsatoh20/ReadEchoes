from django.db import models
from django import forms
from django.forms import ModelForm
from .models import Book
from datetime import datetime

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
            teams = user.team_owner.all()
            self.fields['team'].choices = [(item.id, item.title) for item in teams]