from django import template
from ..models import StaticMedia

register = template.Library()

@register.simple_tag
def get_favicon():
    img = StaticMedia.objects.filter(name='favicon').first().image
    return img.url if img else ''
@register.simple_tag
def get_logo120():
    img = StaticMedia.objects.filter(name='logo120').first().image
    return img.url if img else ''
@register.simple_tag
def get_logo256():
    img = StaticMedia.objects.filter(name='logo256').first().image
    return img.url if img else ''
@register.simple_tag
def get_logo512():
    img = StaticMedia.objects.filter(name='logo512').first().image
    return img.url if img else ''
    
