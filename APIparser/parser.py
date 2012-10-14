import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviepeople.settings")

from django.db.models import Q
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie
from urllib2 import urlopen


log = logging.getLogger(__name__)

def frontpage(request):
    return render(request,'frontpage.html',{'test':'test'})


apikey="5z9vxrv4mrkcdkw2fbymhhdh"
#http://api.rottentomatoes.com/api/public/v1.0/movies.json?apikey=5z9vxrv4mrkcdkw2fbymhhdh&q=aca&page_limit=10

def queryMovies(searchquery, apikey=apikey):
    from urllib2 import urlopen
    from django.utils import simplejson
    req = urlopen("http://api.rottentomatoes.com/api/public/v1.0/movies.json?apikey=%s&q=%s&page_limit=50" % (apikey, searchquery))
    return simplejson.load(req)

#tmp=queryMovies("indiana").get('movies')


def checkAPI():
    from urllib2 import urlopen
    from django.utils import simplejson
    req = urlopen("http://api.rottentomatoes.com/api/public/v1.0/movies/770672024.json?apikey=%s" % apikey)
    return simplejson.load(req)




def parseMovie(movie):
    from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie
    from django.utils import simplejson
    title=movie.get('title')
    tmp1=Movie.objects.filter(name=title)
    tmp2=Release.objects.filter(date=movie.get('release_dates').get('theater'))
    if (len([x.id for x in tmp1].intersect([y.movie_id for y in tmp2])) > 0):
        dbmovie=tmp[0]
    else:
        dbmovie=Movie(name=title)
    dbmovie.save()
    cast=movie.get('abridged_cast')
    people=[role.get('name') for role in cast]
    date=movie.get('release_dates').get('theater')
    if date==None: date="1970-01-01" # TODO: fix this!!
    Release(movie=dbmovie, date=date).save()
    for role in people:
        tmp=People.objects.filter(name=role)
        if len(tmp) > 0:
            dbpeople=tmp[0]
        else: 
            dbpeople=People(name=role)
        dbpeople.save()
        MoviePeople(people=dbpeople, movie=dbmovie, role="actor").save()
    # need to do director, but one API call per movie required :-/
    return [title,date,people]

#[parseMovie(movie) for movie in queryMovies('titanic').get('movies') if movie.]

def parseMoviesSearch(query):
    tmp=[parseMovie(movie) for movie in queryMovies(query).get('movies') if
	    all([movie.get('ratings').get('critics_score')>0, 
		movie.get('ratings').get('audience_score')>0])
	    ]
    return "Done query %s. Processed %i movies." % (query, len(tmp))
#queryMovies('dark').get('movies')[0]

