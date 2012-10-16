import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q

from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from haystack.query import SearchQuerySet
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie, Follow
from urllib2 import urlopen


log = logging.getLogger(__name__)

def frontpage(request):
    if(request.user.is_anonymous()):
        log.info("frontpage hit")
    else:
        log.info("frontpage, user:"+str(request.user.email))
    return render(request,'frontpage.html',{'test':'test'})

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
            'name' : people.name
        }
        ret_json['peoples'].append(people_map)
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")

def people_movies(request,id):
    people = People.objects.get(pk=id)
    ret_json={'movies':[]}
    moviePeoples = MoviePeople.objects.filter(people=people)
    for moviePeople in moviePeoples:
        movie = moviePeople.movie
        movie_map = {
            'id':movie.id,
            'name':movie.name,
            'trailers':[]
        }
        trailers = Trailer.objects.filter(movie=movie)
        for trailer in trailers:
            trailer_map = {
                'id':trailer.id,
                'url':trailer.url
            }
            movie_map['trailers'].append(trailer_map)
        release = Release.objects.get(movie=movie)
        release_map = {
            "date": release.date.strftime("%Y-%m-%d")
        }
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
