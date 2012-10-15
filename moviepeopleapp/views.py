import logging
from django.db.models import Q

from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from haystack.query import SearchQuerySet
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie
from urllib2 import urlopen


log = logging.getLogger(__name__)

def frontpage(request):
    return render(request,'frontpage.html',{'test':'test'})

def autocomplete(request):
    #get term
    json_string = request.GET.get('JSON')
    json = simplejson.loads(json_string)
    term = json['term']

    #get results
    autocomplete = SearchQuerySet().autocomplete(name_autocomplete='De')
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

def people_subscribe(request,id):
    people = People.objects.get(pk=id)
    return HttpResponse(simplejson.dumps({}), mimetype="application/json")
