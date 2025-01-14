from django import template
from ..models import Comment, Like

register = template.Library()

@register.simple_tag
def get_range(value):
    return range(value)

@register.simple_tag
def get_len_replies(value):
    return Comment.objects.filter(reply_id=value.id).all().count()

@register.simple_tag
def get_liked_username(value): # valueには対象のBookが渡される
    likes = value.like_book.all()
    liked_users = [item.owner.username for item in likes]
    return 'Likes:\n' + ', '.join(liked_users)