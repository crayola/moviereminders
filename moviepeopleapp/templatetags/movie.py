from django import template
from django.template import context
from django.utils.safestring import mark_safe
from longerusername.forms import AuthenticationForm
from moviepeople.settings import STATIC_URL
from moviepeopleapp.models import Follow
from moviepeopleapp.templatetags.artist import artist_pic_url

register = template.Library()

def movie_box_home(movie_map):

    movie=movie_map['movie']
    artists_follow=movie_map['artists_follow']
    release_date=movie_map['release_date']

    html=  '<div class="movie-box">'
    html+=  '<img src="'+movie_poster_url(movie)+'"/>'
    html+=  '<div class="movie-box-title">'
    html+=   '<h1 class="title">'+movie.name+'</h1><hr/>'
    html+=   '<div class="release">'+str(release_date)+"</div>"
    html+=  '</div>'
    for artist in artists_follow:
        html+= '<div class="artist-pic">'
        html+= '<img src="'+artist_pic_url(artist)+'"/>'
        html+= '</div>'
    html+=  '<span class="is"></span>'
    html+=  '<div class="trailer">'
    html+=  '</div>'
    html+= '</div>'
    return mark_safe(html)

def movie_poster_url(movie):
    if(movie.poster != ''):
        return 'http://cf2.imgobject.com/t/p/w185'+movie.poster
    else:
        return STATIC_URL+'img/question_mark.png'

register.filter('movie_box_home', movie_box_home)
register.filter('movie_poster_url', movie_poster_url)