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

def logoutview(request):
    logout(request)
    return HttpResponse(simplejson.dumps({}), mimetype="application/json")




def yourwhispers(request):
    nowdate = datetime.datetime.today().strftime("%Y-%m-%d")
    user=request.user;
    peoples = [follow.people_id for follow in Follow.objects.filter(user_id=user.id)]
    ret_json = {'movies':[]}
    ret_json['movies'] = make_people_movies(peoples, nowdate)
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def unfollow(request):
    user=request.user;

    json_string = request.GET.get('JSON')
    json = simplejson.loads(json_string)
    followee = json['followee']

    people = Follow.objects.get(user_id=user.id, people_id=followee)
    people.delete()
    return HttpResponse(simplejson.dumps({}), mimetype="application/json")


def followees(request):
    user=request.user;
    peoples = Follow.objects.filter(user_id=user.id).order_by('people__name').values('people__name', 'people_id', 'people__profile')
    ret_json = {'people': []}
    for people in peoples:
        ret_json['people'].append({'name': people['people__name'], 'id': people['people_id'], 'profile':people['people__profile']})
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def people_subscribe(request,id):
    user = request.user
    people = People.objects.get(pk=id)
    follows = Follow.objects.filter(user=user,people=people)
    if(follows.count()>0):
        return HttpResponse(simplejson.dumps({"already_follows":True}), mimetype="application/json")
    follow = Follow.objects.create(user=user,people=people)
    log.info("user:"+user.email+" follows:"+people.name)
    return HttpResponse(simplejson.dumps({}), mimetype="application/json")