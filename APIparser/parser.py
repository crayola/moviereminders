import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviepeople.settings")

from django.db.models import Q
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie
from urllib2 import urlopen, Request, URLError, HTTPError

log = logging.getLogger(__name__)

def frontpage(request):
    return render(request,'frontpage.html',{'test':'test'})


apikey="3dffd9e01086f6801f45d2161cd2710d"

def checkmovie(idmovie, info):
    if info=="main":
        url="http://api.themoviedb.org/3/movie/%s?api_key=%s" % (idmovie, apikey)
    else: url="http://api.themoviedb.org/3/movie/%s/%s?api_key=%s" % (idmovie, info, apikey)
    request = Request(url)
    request.add_header("Accept", "application/json")
    read=0
    while read==0:
        try:
            req = urlopen(request, timeout=3)
            read=1
        except HTTPError:
            print "HTTP error."
            raise
        except URLError:
            read=0
            print "Timeout -- trying again."
    parsed=0
    while parsed==0:
        try:
            ret=simplejson.load(req)
            parsed=1
        except:
            parsed=0
            print "JSON issue, probably socket.timeout."
    return ret



def parseMovie(tmdbid):
    try:
        movie_main=checkmovie(tmdbid, "main")
    except:
        print "id %s: no movie" % tmdbid
        return 0
    movie_cast=checkmovie(tmdbid, "casts")
    movie_release=checkmovie(tmdbid, "releases")
    print "id %s: writing to disk" % tmdbid
    f=open("/home/ubuntu/dumptmdb%s" % (tmdbid/10000), "a")
    simplejson.dump({"main": movie_main, "casts": movie_cast, "releases": movie_release}, f)
    f.write("\n")
    f.close()
    return 1
    #title=movie_main['title']
    #(poster, backdrop) = (movie_main['poster_path'], movie_main['backdrop_path'])
    #if not(poster): poster=''
    #if not(backdrop): backdrop=''
    #dbmovie=Movie(name=title, poster=poster, backdrop=backdrop)
    #dbmovie.save()
    #date=[x['release_date'] for x in movie_release['countries'] if x['iso_3166_1']=='US']
    #if date: Release(movie=dbmovie, date=date[0]).save()
    #people=[x['name'] for x in movie_cast['cast']]
    #director=[x['name'] for x in movie_cast['crew'] if x['job']=='Director']
    #for role in people:
    #    tmp=People.objects.filter(name=role)
    #    if len(tmp) > 0:
    #        dbpeople=tmp[0]
    #    else: 
    #        dbpeople=People(name=role)
    #    dbpeople.save()
    #    MoviePeople(people=dbpeople, movie=dbmovie, role="actor").save()
    #for role in director:
    #    #print director
    #    tmp=People.objects.filter(name=role)
    #    if len(tmp) > 0:
    #        dbpeople=tmp[0]
    #    else: 
    #        dbpeople=People(name=role)
    #    dbpeople.save()
    #    MoviePeople(people=dbpeople, movie=dbmovie, role="director").save()
    #return [title,date,people]



def parseDump(dumpfile):
    for movie in [simplejson.loads(line) for line in open(dumpfile)]:
        movie_main=movie["main"]
        movie_cast=movie["casts"]
        movie_release=movie["releases"]
        writeMovie(movie_main, movie_cast, movie_release)


def writeMovie(movie_main, movie_cast, movie_release):
    title=movie_main['title']
    (poster, backdrop) = (movie_main['poster_path'], movie_main['backdrop_path'])
    if not(poster): poster=''
    if not(backdrop): backdrop=''
    dbmovie=Movie(name=title, poster=poster, backdrop=backdrop)
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
        #print director
        tmp=People.objects.filter(name=role)
        if len(tmp) > 0:
            dbpeople=tmp[0]
        else: 
            dbpeople=People(name=role)
        dbpeople.save()
        MoviePeople(people=dbpeople, movie=dbmovie, role="director").save()
    return [title,date,people]
