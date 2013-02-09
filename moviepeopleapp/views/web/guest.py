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
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('moviepeopleapp', 'templates'))
log = logging.getLogger(__name__)

@ensure_csrf_cookie
def frontpage(request):
  if(request.user.is_anonymous()):
    log.info("frontpage hit")
  else:
    log.info("frontpage, user:"+str(request.user.email))
  return render(request, 'guest/frontpage.html', {})

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


def people_movies(request,id):
  ret_json={'movies':make_people_movies([id])}
  return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")

def make_people_movies(id, mindate = "1900-01-01"):
    #mindate = datetime.datetime.strptime(mindate, "%Y-%m-%d")
    #people = People.objects.filter(pk__in=id)
    ret_json = []
    #moviePeoples = MoviePeople.objects.filter(people__in=people, role__in=['Actor', 'Director'], movie__adult=False)
    # select which movies to show

    #def keyfun(movie):
    #  try: 
    #    return str(Release.objects.filter(movie=movie)[0].date)
    #  except Exception:
    #    return "3000"
    #movies = sorted(set([x.movie for x in moviePeoples]), 
    #                key=keyfun,
    #                reverse=True)
    
#    moviePeoples_actor = MoviePeople.objects.filter(people__id__in=id, role='Actor', movie__adult=False).order_by('people', 'movie', 'order')
#    log.info(moviePeoples_actor[0])
#    moviePeoples_director = MoviePeople.objects.filter(people__id__in=id, role='Director', movie__adult=False)
#
    #movies = moviePeoples_director.values_list('movie', flat=True).distinct() | moviePeoples_actor.values_list('movie', flat=True).distinct()

    if mindate == "1900-01-01":
      moviePeople = MoviePeople.objects.filter(people__id__in=id, role__in=['Actor', 'Director'], movie__adult=False)
      movies = moviePeople.values_list('movie', flat=True).distinct()
    else:
      mindategood=datetime.datetime.strptime(mindate, "%Y-%m-%d")
      torelease = Release.objects.filter(country='US', date__gte=mindategood).values_list('movie', flat=True).distinct()
      moviePeople = MoviePeople.objects.filter(movie__id__in=torelease, people__id__in=id, role__in=['Actor', 'Director'], movie__adult=False)
      movies = moviePeople.values_list('movie', flat=True).distinct()

    
    for movie_id in movies:
        #if len(ret_json['movies']) >= 5: break
        movie = Movie.objects.get(pk=movie_id)

        movie_map = {
            'id':movie.id,
            'RT_critics_score': movie.RT_critics_score,
            'RT_audience_score': movie.RT_audience_score,
            'RT_critics_rating': movie.RT_critics_rating,
            'RT_audience_rating': movie.RT_audience_rating,
            'poster':movie.poster,
            'name':movie.name,
            'trailers':[],
            'people':[],
            #{'id':people.id,
            #          'name':people.name,
            #          'profile':people.profile},
        }

        #moviepeople = moviePeoples_actor.filter(movie_id=movie_id) | moviePeoples_director.filter(movie_id=movie_id)
        moviepeople = moviePeople.filter(movie=movie)
        peoples = moviepeople.values_list('people', flat=True).distinct()
        for people_id in peoples:
          people = People.objects.get(id=people_id)
          tmp={}
          tmp['id'] = people.id
          tmp['name'] = people.name
          tmp['profile'] = people.profile
          tmp['roles'] = list(moviepeople.filter(people=people).values('role', 'character', 'order'))
          movie_map['people'].append(tmp)

       # moviepeople_actor = None
       # moviepeoples_actor = MoviePeople.objects.filter(
       #   movie=movie, people=people, role='Actor')
       # if moviepeoples_actor:
       #   moviepeople_actor = sorted(
       #     moviepeoples_actor, key=lambda k: k.order)[0]
       #   moviepeople_actor = {k:getattr(moviepeople_actor, k) for k
       #                      in ['id', 'character', 'order']}
       # movie_map['moviepeople_actor'] = moviepeople_actor
       # moviepeoples_director = MoviePeople.objects.filter(
       #   movie=movie, people=people, role='Director')
       # movie_map['moviepeople_director']=bool(moviepeoples_director)

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
            try:
              release = Release.objects.filter(movie=movie, country="US")[0].date
            except Exception:
              release = Release.objects.filter(movie=movie) #[0]
              release = min([x.date for x in release])
            if release.strftime("%Y-%m-%d") < mindate: continue
            movie_map['release'] = release.strftime("%Y-%m-%d")
        except Exception:
            #movie_map['release'] = "1970-01-01"
            continue
        ret_json.append(movie_map)
    
    return ret_json;










