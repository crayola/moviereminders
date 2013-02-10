from django import template
from django.template import context
from django.utils.safestring import mark_safe
from longerusername.forms import AuthenticationForm
from moviepeople.settings import STATIC_URL
from moviepeopleapp.models import Follow

register = template.Library()

def artist_box(artist):
    html=  '<div class="artist-box">'
    if(artist.profile != ''):
        html+=  '<img src="http://cf2.imgobject.com/t/p/w342'+artist.profile+'"/>'
    else:
        html+=  '<img src="'+STATIC_URL+'img/question_mark.png"/>'
    html+=  '<div class="follow-btn-box">'
    html+=   '<a class="btn btn-follow btn-large" artist-id="'+str(artist.id)+'">Follow <br/>'+artist.name+'</a>'
    html+=  '</div>'
    html+= '</div>'
    return mark_safe(html)

register.filter('artist_box', artist_box)