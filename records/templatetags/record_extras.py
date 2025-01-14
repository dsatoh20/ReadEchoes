from django import template
from ..models import Comment

register = template.Library()

@register.simple_tag
def get_range(value):
    return range(value)

@register.simple_tag
def get_len_replies(value):
    return Comment.objects.filter(reply_id=value.id).all().count()