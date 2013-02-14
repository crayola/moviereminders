import logging
import os
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q
import datetime

from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.datetime_safe import date
from haystack.query import SearchQuerySet
from moviepeople import settings
import moviepeople.settings
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie, Follow, CreateAccountToken
from urllib2 import urlopen
from django.views.decorators.csrf import ensure_csrf_cookie

log = logging.getLogger(__name__)

@ensure_csrf_cookie
def homepage(request):
    nowdate = datetime.datetime.today().strftime("%Y-%m-%d")
    user=request.user;
    artists = [follow.people_id for follow in Follow.objects.filter(user_id=user.id)]

    mindategood=datetime.datetime.strptime(nowdate, "%Y-%m-%d")
    releases = Release.objects.filter(country='US', date__gte=mindategood)
    torelease = releases.values_list('movie', flat=True).distinct()
    log.info('torelease:'+str(torelease))
    log.info('peoples:'+str(artists))
    movie_artists = MoviePeople.objects.filter(movie__id__in=torelease, people__id__in=artists, role__in=['Actor', 'Director'], movie__adult=False)
    log.info('moviePeople:'+str(movie_artists))
    movie_ids = movie_artists.values_list('movie', flat=True).distinct()
    movies = Movie.objects.filter(id__in=movie_ids)

    movie_map_array = []
    for movie in movies:

        movie_map = {
            'movie':movie,
            'artists_follow':[],
            'artists_nofollow':[],
            'release_date':None
        }

        #find artists followed
        for artist_follow in movie_artists:
            if artist_follow.movie_id == movie.id:
                movie_map['artists_follow'].append(artist_follow.people)

        #find release
        for release in releases:
            if release.movie_id == movie.id:
                movie_map['release_date']= release.date
        movie_map_array.append(movie_map)

    log.info('movie_map_array:'+str(movie_map_array))
    return render(request, 'user/homepage.html', {'movies':movies,'movie_map_array':movie_map_array})

def find_artists(request):
    user=request.user
    return render(request, 'user/find.html', {})

def follows(request):
    user=request.user
    artists = [follow.people for follow in Follow.objects.filter(user_id=user.id)]
    log.info('artists'+str(artists))
    return render(request, 'user/follows.html', {'artists':artists})