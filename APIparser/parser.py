import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviepeople.settings")

from django.db.models import Q
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie
from urllib2 import urlopen, Request

log = logging.getLogger(__name__)

def frontpage(request):
    return render(request,'frontpage.html',{'test':'test'})


#http://api.rottentomatoes.com/api/public/v1.0/movies.json?apikey=5z9vxrv4mrkcdkw2fbymhhdh&q=aca&page_limit=10
apikey="3dffd9e01086f6801f45d2161cd2710d"

def checkmovie(idmovie, info):
    if info=="main":
        url="http://api.themoviedb.org/3/movie/%s?api_key=%s" % (idmovie, apikey)
    else: url="http://api.themoviedb.org/3/movie/%s/%s?api_key=%s" % (idmovie, info, apikey)
    request = Request(url)
    request.add_header("Accept", "application/json")
    req = urlopen(request)
    return simplejson.load(req)


#def queryMovies(searchquery, apikey=apikey):
#    req = urlopen("http://api.rottentomatoes.com/api/public/v1.0/movies.json?apikey=%s&q=%s&page_limit=50" % (apikey, searchquery))
#    return simplejson.load(req)

#tmp=queryMovies("indiana").get('movies')

#
#def checkAPI():
#    from urllib2 import urlopen
#    from django.utils import simplejson
#    req = urlopen("http://api.rottentomatoes.com/api/public/v1.0/movies/770672024.json?apikey=%s" % apikey)
#    return simplejson.load(req)
#

#def parseMovie(movie):
#    title=movie.get('title')
#    tmp1=Movie.objects.filter(name=title)
#    tmp2=Release.objects.filter(date=movie.get('release_dates').get('theater'))
#    if (len([x.id for x in tmp1].intersect([y.movie_id for y in tmp2])) > 0):
#        dbmovie=tmp[0]
#    else:
#        dbmovie=Movie(name=title)
#    dbmovie.save()
#    cast=movie.get('abridged_cast')
#    people=[role.get('name') for role in cast]
#    date=movie.get('release_dates').get('theater')
#    if date==None: date="1970-01-01" # TODO: fix this!!
#    Release(movie=dbmovie, date=date).save()
#    for role in people:
#        tmp=People.objects.filter(name=role)
#        if len(tmp) > 0:
#            dbpeople=tmp[0]
#        else: 
#            dbpeople=People(name=role)
#        dbpeople.save()
#        MoviePeople(people=dbpeople, movie=dbmovie, role="actor").save()
#    # need to do director, but one API call per movie required :-/
#    return [title,date,people]

def parseMovie(tmdbid):
    try:
        movie_main=checkmovie(tmdbid, "main")
    except:
        print "no movie for id %s" % tmdbid
        return 0
    movie_cast=checkmovie(tmdbid, "casts")
    movie_release=checkmovie(tmdbid, "releases")
    movie_images=checkmovie(tmdbid, "images")

    f=open("/home/ubuntu/dumptmdb", "a")
    simplejson.dump({"main": movie_main, "casts": movie_cast, "releases": movie_release}, f)
    f.close()

    title=movie_main['title']
    dbmovie=Movie(name=title)
    dbmovie.save()

    date=[x['release_date'] for x in movie_release['countries'] if x['iso_3166_1']=='US']
    if date: Release(movie=dbmovie, date=date[0]).save()

    people=[x['name'] for x in movie_cast['cast']]
    director=[x['name'] for x in movie_cast['crew'] if x['job']=='Director']
    for role in people:
        tmp=People.objects.filter(name=role)
        if len(tmp) > 0:
            dbpeople=tmp[0]
        else: 
            dbpeople=People(name=role)
        dbpeople.save()
        MoviePeople(people=dbpeople, movie=dbmovie, role="actor").save()
    for role in director:
        print director
        tmp=People.objects.filter(name=role)
        if len(tmp) > 0:
            dbpeople=tmp[0]
        else: 
            dbpeople=People(name=role)
        dbpeople.save()
        MoviePeople(people=dbpeople, movie=dbmovie, role="director").save()

    for poster in [x['file_path'] for x in movie_images['posters']]:
        Poster(url=poster, movie=dbmovie).save()

    for poster in [x['file_path'] for x in movie_images['backdrops']]:
        Backdrop(url=poster, movie=dbmovie).save()
    # need to do director, but one API call per movie required :-/
    return [title,date,people]

#[parseMovie(movie) for movie in queryMovies('titanic').get('movies') if movie.]

#def parseMoviesSearch(query):
#    tmp=[parseMovie(movie) for movie in queryMovies(query).get('movies') if
#	    all([movie.get('ratings').get('critics_score')>0, 
#		movie.get('ratings').get('audience_score')>0])
#	    ]
#    return "Done query %s. Processed %i movies." % (query, len(tmp))
#queryMovies('dark').get('movies')[0]

