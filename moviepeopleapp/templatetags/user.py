from django import template
from django.template import context
from longerusername.forms import AuthenticationForm
from moviepeopleapp.models import Follow

register = template.Library()

def follows_count(user):
    count = Follow.objects.filter(user_id=user.id).count()
    return count

register.filter('follows_count', follows_count)