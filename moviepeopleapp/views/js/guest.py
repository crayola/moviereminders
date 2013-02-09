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

def login(request):
    #redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if request.POST:
        json=simplejson.loads(request.POST.get('JSON'))
        #errors = manipulator.get_validation_errors(request.POST)
        user = authenticate(username = json['username'], password = json['password'])
        if user is not None and user.is_active:
            login(request, user)
            ret_json = {'auth': True, 'username': user.username}
            log.info("Sign in:" + user.username)
        else:
            ret_json = {'auth': False}
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")




def autocomplete(request):
    #get term
    json_string = request.GET.get('JSON')
    json = simplejson.loads(json_string)
    term = json['term']

    #get results
    autocomplete = SearchQuerySet().autocomplete(name_autocomplete=term)
    #autocomplete = SearchQuerySet().all()
    log.info("term:"+term+" results:"+str(autocomplete.count()))

    #create response
    autocomplete = sorted(autocomplete, key=lambda k: -(k.object.importance or 0))
    ret_json = {'peoples':[]}
    for result in autocomplete:
        people = result.object
        try:
            Follow.objects.get(user=request.user, people=people)
            follow=True
        except Exception:
            follow=False
        people_map = {
            'id': people.id,
            'name': people.name,
            'profile': people.profile,
            'follow': follow
        }
        ret_json['peoples'].append(people_map)
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def manualsearch(request):
    #get term
    json_string = request.GET.get('JSON')
    json = simplejson.loads(json_string)
    term = json['term']
    if len(term) < 3: return None

    #get results
    try:
        people = People.objects.filter(name__icontains=term)
        people = sorted(people, key=lambda k: -(k.importance or 0))[0]
        log.info("term: "+term+" results:"+people.name)
    except Exception:
        log.info("term: "+ term + " not found")
        return None

    #create response
    try:
        Follow.objects.get(user=request.user, people=people)
        follow=True
    except Exception:
        follow=False
    ret_json = {
        'id' : people.id,
        'name' : people.name,
        'profile' : people.profile,
        'follow': follow
    }
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def sendToken(request, new=False):
    json = simplejson.loads(request.GET.get('JSON'))
    email = json['email']
    log.info("Token for:"+email)
    user = User.objects.get(username=email)
    #create auth token & send confirmation email
    token_code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for x in range(32))
    log.info("token_code:"+token_code)
    [token.delete() for token in CreateAccountToken.objects.filter(email=email)]
    token = CreateAccountToken.objects.create(code=token_code,email=email)
    token.save()
    link = settings.SERVER_URL+'login/'+token_code
    if new:
        subject = 'Welcome to Whispers!'
        html_content = '<p>Hi, thanks for joining whispers,</p>'
        html_content += '<p>Set up a password for accessing your account whenever you like by following this link:<br/>'
        html_content += '<p><a href="'+link+'">'+link+'</a></p>'
        html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
    else:
        subject = 'Your Whispers password renewal.'
        html_content = '<p>Set up a new password by following this link:<br/>'
        html_content += '<p><a href="'+link+'">'+link+'</a></p>'
        html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
    msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@whispers.io>', [email])
    msg.attach_alternative(html_content, "text/html")
    log.info(msg.send())

    return HttpResponse(simplejson.dumps({"already_exists":True}), mimetype="application/json")

def signup(request):
    #get email
    json = simplejson.loads(request.GET.get('JSON'))
    email = json['email']
    log.info("signup:"+email)
    users = User.objects.filter(username=email)
    if(len(users)>0):
        return HttpResponse(simplejson.dumps({"already_exists":True}), mimetype="application/json")
    user = User.objects.create_user(email, email, '*')
    user.save()
    user = authenticate(username=email,password='*')
    login(request, user)
    log.info("user:"+user.email+" logged in")

    sendToken(request, new=True)

    return HttpResponse(simplejson.dumps({}), mimetype="application/json")