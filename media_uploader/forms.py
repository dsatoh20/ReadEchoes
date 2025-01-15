from django.forms import ModelForm
from .models import StaticMedia


class StaticMediaForm(ModelForm):
    class Meta:
        model = StaticMedia
        fields = '__all__'
    def __str__(self):
        return self.name