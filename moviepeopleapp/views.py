import logging
import os
import random
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q

from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from haystack.query import SearchQuerySet
from moviepeople import settings
import moviepeople.settings
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie, Follow, CreateAccountToken
from urllib2 import urlopen


log = logging.getLogger(__name__)

def frontpage(request):
    if(request.user.is_anonymous()):
        log.info("frontpage hit")
    else:
        log.info("frontpage, user:"+str(request.user.email))
    return render(request,'frontpage.html',{'test':'test'})

def createAccount(request, token_code):
    token = CreateAccountToken.objects.get(code=token_code)
    log.info("create_account page opened by:"+token.email)
    return render(request,'create_account.html',{})

def autocomplete(request):
    #get term
    json_string = request.GET.get('JSON')
    json = simplejson.loads(json_string)
    term = json['term']

    #get results
    autocomplete = SearchQuerySet().autocomplete(name_autocomplete=term)
    log.info("term:"+term+" results:"+str(autocomplete.count()))

    #create response
    ret_json = {'peoples':[]}
    for result in autocomplete:
        people = result.object
        people_map = {
            'id' : people.id,
            'name' : people.name,
            'profile' : people.profile
        }
        ret_json['peoples'].append(people_map)
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")

def people_movies(request,id):
    people = People.objects.get(pk=id)
    ret_json={'movies':[]}
    moviePeoples = MoviePeople.objects.filter(people=people)
    # select which movies to show
    def keyfun(movie):
      try: 
        return str(Release.objects.filter(movie=movie)[0].date)
      except Exception:
        return "3000"
    movies = sorted(set([x.movie for x in moviePeoples]), 
                    key=keyfun,
                    reverse=True)
    for movie in movies:
        if len(ret_json['movies']) >= 5: break
        movie_map = {
            'id':movie.id,
            'name':movie.name,
            'trailers':[],
        }
        moviepeople_actor = None
        moviepeoples_actor = MoviePeople.objects.filter(
          movie=movie, people=people, role='Actor')
        if moviepeoples_actor:
          moviepeople_actor = sorted(
            moviepeoples_actor, key=lambda k: k.order)[0]
          moviepeople_actor = {k:getattr(moviepeople_actor, k) for k
                             in ['id', 'character', 'order']}
        movie_map['moviepeople_actor'] = moviepeople_actor
        moviepeoples_director = MoviePeople.objects.filter(
          movie=movie, people=people, role='Director')
        movie_map['moviepeople_director']=bool(moviepeoples_director)
        trailers = Trailer.objects.filter(movie=movie)
        for trailer in trailers:
            trailer_map = {
                'id':trailer.id,
                'url':trailer.url,
            }
            if trailer.date_info: 
              trailer_map['date'] = trailer.date_info.strftime("%Y-%m-%d")
            movie_map['trailers'].append(trailer_map)
        try: 
            release = Release.objects.filter(movie=movie)[0]
            release_map = {
                "date": release.date.strftime("%Y-%m-%d")
                }
        except Exception:
            release_map = {
                "date": "1970-01-01"
                }
            continue
        movie_map['release'] = release_map
        ret_json['movies'].append(movie_map)
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")

def signup(request):
    #get email
    json = simplejson.loads(request.GET.get('JSON'))
    email = json['email']
    log.info("signup:"+email)
    users = User.objects.filter(username=email)
    if(users.count()>0):
        return HttpResponse(simplejson.dumps({"already_exists":True}), mimetype="application/json")
    user = User.objects.create_user(email, email, '*')
    user.save()
    user = authenticate(username=email,password='*')
    login(request, user)
    log.info("user:"+user.email+" logged in")

    #create auth token & send confirmation email
    token_code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for x in range(32))
    log.info("token_code:"+token_code)
    token = CreateAccountToken.objects.create(code=token_code,email=email)
    token.save()
    link = settings.SERVER_URL+'login/'+token_code
    subject = 'Welcome to Whispers - get excited about upcoming movies!'
    html_content = '<p>Hi, thanks for joining whispers,</p>'
    html_content += '<p>Set up a password for accessing your account whenever you like by following this link:<br/>'
    html_content += '<p><a href="'+link+'">'+link+'</a></p>'
    html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
    msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@gmail.com>', [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return HttpResponse(simplejson.dumps({}), mimetype="application/json")


def people_subscribe(request,id):
    user = request.user
    people = People.objects.get(pk=id)
    follows = Follow.objects.filter(user=user,people=people)
    if(follows.count()>0):
        return HttpResponse(simplejson.dumps({"already_follows":True}), mimetype="application/json")
    follow = Follow.objects.create(user=user,people=people)
    log.info("user:"+user.email+" follows:"+people.name)
    return HttpResponse(simplejson.dumps({}), mimetype="application/json")

