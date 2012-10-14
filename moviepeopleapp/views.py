import logging
from django.db.models import Q

from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from moviepeopleapp.models import People, MoviePeople, Trailer, Release

log = logging.getLogger(__name__)

def frontpage(request):
    return render(request,'frontpage.html',{'test':'test'})


def autocomplete(request):
    log.info('test')
    json_string = request.GET.get('JSON')
    log.info('json_string'+json_string)
    json = simplejson.loads(json_string)
    keywords = json['name'].split(' ')
    ret_json = {'peoples':[]}
    peoples = People.objects.filter(Q(first_name__icontains=json['name'])|Q(last_name__icontains=json['name']))
    log.info('peoples:'+str(peoples.count()))
    for people in peoples:
        people_map = {
            'id' : people.id,
            'first_name' : people.first_name,
            'last_name' : people.last_name
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