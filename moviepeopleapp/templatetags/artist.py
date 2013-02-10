from django import template
from django.template import context
from django.utils.safestring import mark_safe
from longerusername.forms import AuthenticationForm
from moviepeople.settings import STATIC_URL
from moviepeopleapp.models import Follow

register = template.Library()

def artist_box(artist):
    html=  '<div class="artist-box">'
    html+=  '<img src="'+artist_pic_url(artist)+'"/>'
    html+=  '<div class="follow-btn-box">'
    html+=   '<a class="btn btn-follow btn-large" artist-id="'+str(artist.id)+'">Follow <br/>'+artist.name+'</a>'
    html+=  '</div>'
    html+= '</div>'
    return mark_safe(html)

def artist_pic_url(artist):
    if(artist.profile != ''):
        return 'http://cf2.imgobject.com/t/p/w342'+artist.profile
    else:
        return STATIC_URL+'img/question_mark.png'

register.filter('artist_box', artist_box)
register.filter('artist_pic_url', artist_pic_url)