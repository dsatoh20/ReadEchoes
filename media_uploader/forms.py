from django.forms import ModelForm
from .models import StaticMedia


class StaticMediaForm(ModelForm):
    class Meta:
        model = StaticMedia
        fields = '__all__'