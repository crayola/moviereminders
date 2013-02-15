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
from django.shortcuts import render, redirect
from django.utils.datetime_safe import date
from haystack.query import SearchQuerySet
from moviepeople import settings
import moviepeople.settings
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie, Follow, CreateAccountToken
from urllib2 import urlopen
from django.views.decorators.csrf import ensure_csrf_cookie

#env = Environment(loader=PackageLoader('moviepeopleapp', 'templates'))
log = logging.getLogger(__name__)

@ensure_csrf_cookie
def frontpage(request):
  if(request.user.is_anonymous()):
    log.info("frontpage hit")
    #take 8 artists randomly
    #artists = People.objects.order_by('?')[0:8]
    #artists = People.objects.exclude(importance__isnull=True).order_by('-importance')[0:8]
    artists = People.objects.filter(name__in=['Quentin Tarantino', 'Johnny Depp', 'Emma Stone', 'Joss Whedon', 'Danny Boyle', 'Ryan Gosling', 'Ellen Page', 'Daniel Radcliffe'])
    if('fpartists' not in request.session):
        request.session['fpartists'] = []
    request.session['fpartists'] += artists
    return render(request, 'guest/frontpagev2.html', {'artists':artists})
  else:
    log.info("frontpage, user:"+str(request.user.email))
    return redirect('/home')


def faq(request):
    return render(request, 'guest/faq.html',{})


def createAccount(request, token_code):
  try: 
    token = CreateAccountToken.objects.get(code=token_code)
  except CreateAccountToken.DoesNotExist:
    return render(request, 'badToken.html')
  user = User.objects.get(username=token.email)
  new = user.check_password('*')
  if request.method == 'POST': 
    form = SetPasswordForm(data=request.POST, user=user)
    if form.is_valid():
      password=request.POST['new_password1']
      user.set_password(password)
      user.save()
      #token.delete() # token is single use only!
      log.info("Account created for:" + user.username)
      if new:
        return render(request, 'accountCreated.html')
      else:
        return render(request, 'passwordUpdated.html')
  else:
    form = SetPasswordForm(user)
    log.info("create_account page opened by:"+token.email)
    return render(request, 'create_account.html', {'form':form, 'user':user, 'token':token_code})












