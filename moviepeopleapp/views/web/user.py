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
    peoples = [follow.people_id for follow in Follow.objects.filter(user_id=user.id)]

    mindategood=datetime.datetime.strptime(nowdate, "%Y-%m-%d")
    torelease = Release.objects.filter(country='US', date__gte=mindategood).values_list('movie', flat=True).distinct()
    moviePeople = MoviePeople.objects.filter(movie__id__in=torelease, people__id__in=peoples, role__in=['Actor', 'Director'], movie__adult=False)
    movies = moviePeople.values_list('movie', flat=True).distinct()

    return render(request, 'user/homepage.html', {'movies':movies})

def find_artists(request):
    user=request.user
    return render(request, 'user/find.html', {})

def follows(request):
    user=request.user
    artists = [follow.people for follow in Follow.objects.filter(user_id=user.id)]
    log.info('artists'+str(artists))
    return render(request, 'user/follows.html', {'artists':artists})