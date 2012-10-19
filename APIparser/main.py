import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviepeople.settings")

from django.db.models import Q
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from moviepeopleapp.models import People, MoviePeople, Trailer, Release, Movie, MovieGenre, MovieOverview, MovieLanguage, MovieCountry, MovieCompany
from urllib2 import urlopen, Request, URLError, HTTPError

log = logging.getLogger(__name__)

def frontpage(request):
    return render(request,'frontpage.html',{'test':'test'})


apikey="3dffd9e01086f6801f45d2161cd2710d"

def checkmovie(idmovie, info):
    """Downloads info (main, releases, casts, ..) about movie idmovie from tmdb."""
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
    i=0
    while i < 10:
        try:
            movie_cast=checkmovie(tmdbid, "casts")
            i=10
        except:
            movie_cast=''
            i+=1
    i=0
    while i < 10:
        try:
            movie_release=checkmovie(tmdbid, "releases")
            i=10
        except:
            movie_release=''
            i+=1
    print "id %s: writing to disk" % tmdbid
    f=open("/whispers/dumptmdb%s" % (tmdbid/10000), "a")
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
    return 1;

def Nonetostr(a):
    if a==[] or a==None : a=''
    return(a)


def makeDBmovie(movie_main):
    genres=movie_main['genres']
    languages=[x['iso_639_1'] for x in Nonetostr(movie_main['spoken_languages'])]
    production_companies=movie_main['production_companies']
    countries=[x['iso_3166_1'] for x in Nonetostr(movie_main['production_countries'])]
    try: dbmovie=Movie.objects.get(tmdb_id=Nonetostr(movie_main['id']))
    except: dbmovie=Movie()
    dbmovie.name=Nonetostr(movie_main['title'])
    dbmovie.poster=Nonetostr(movie_main['poster_path'])
    dbmovie.backdrop=Nonetostr(movie_main['backdrop_path'])
    dbmovie.tmdb_id=movie_main['id']
    dbmovie.imdb_id=Nonetostr(movie_main['imdb_id'])
    dbmovie.revenue=movie_main['revenue']
    dbmovie.homepage=Nonetostr(movie_main['homepage'])[:200]
    dbmovie.popularity=movie_main['popularity']
    dbmovie.votes=movie_main['vote_count']
    dbmovie.vote_average=movie_main['vote_average']
    dbmovie.runtime=movie_main['runtime']
    dbmovie.tagline=Nonetostr(movie_main['tagline'])
    dbmovie.adult=movie_main['adult']
    dbmovie.budget=movie_main['budget']
    dbmovie.save()
    for genre in genres:
        try: dbmoviegenre=MovieGenre.objects.get(movie=dbmovie, genre=genre['name'])
        except: dbmoviegenre=MovieGenre()
        dbmoviegenre.movie=dbmovie
        dbmoviegenre.genre=genre['name']
        dbmoviegenre.genre_tmdb_id=genre['id']
        dbmoviegenre.save()
    for company in production_companies:
        try: dbmoviecompany=MovieCompany.objects.get(movie=dbmovie, company=company['name'][:200])
        except: dbmoviecompany=MovieCompany()
        dbmoviecompany.movie=dbmovie
        dbmoviecompany.company=company['name'][:200]
        dbmoviecompany.company_tmdb_id=company['id']
        dbmoviecompany.save()
    for language in languages:
        try: dbmovielanguage=MovieLanguage.objects.get(movie=dbmovie, language=language)
        except: dbmovielanguage=MovieLanguage()
        dbmovielanguage.movie=dbmovie
        dbmovielanguage.language=language
        dbmovielanguage.save()
    for country in countries:
        try: dbmoviecountry=MovieCountry.objects.get(movie=dbmovie, country=country)
        except: dbmoviecountry=MovieCountry()
        dbmoviecountry.movie=dbmovie
        dbmoviecountry.country=country
        dbmoviecountry.save()
    try: dbmovieoverview=MovieOverview.objects.get(movie=dbmovie)
    except: dbmovieoverview=MovieOverview()
    dbmovieoverview.movie=dbmovie
    dbmovieoverview.overview=Nonetostr(movie_main['overview'])
    dbmovieoverview.tagline=Nonetostr(movie_main['tagline'])
    dbmovieoverview.save()
    return dbmovie


def makeDBreleases(dbmovie, movie_release):
    try: dates=movie_release['countries'] 
    except: return 0
    if dates: 
        for date in dates:
            try: dbmovierelease=Release.objects.get(movie=dbmovie, date=date['release_date'])
            except: dbmovierelease=Release()
            dbmovierelease.movie=dbmovie
            dbmovierelease.date=date['release_date'] # TODO: got an error with a date with year 20011-04-11 in tmdb. must make sure this doesn't break (insert null instead). For now (no time) I just fixed the date in the text dump :-/
            dbmovierelease.country=date['iso_3166_1']
            dbmovierelease.save()
    return 1

def makeDBpeople(dbmovie, movie_cast):
    actors=movie_cast['cast']
    crews=movie_cast['crew']
    for actor in actors: makeDBactor(dbmovie, actor)
    for crew in crews: makeDBcrew(dbmovie, crew)
    return 1

def makeDBactor(dbmovie, actor):
    try: dbpeople=People.objects.get(tmdb_id=Nonetostr(actor['id']))
    except: dbpeople=People()
    dbpeople.name=Nonetostr(actor['name'])
    dbpeople.tmdb_id=Nonetostr(actor['id'])
    dbpeople.profile=Nonetostr(actor['profile_path'])
    dbpeople.save()
    try: dbmoviepeople=MoviePeople.objects.get(people=dbpeople, movie=dbmovie, role='Actor', character=Nonetostr(actor['character'])[:100])
    except: dbmoviepeople=MoviePeople()
    dbmoviepeople.movie=dbmovie
    dbmoviepeople.people=dbpeople
    dbmoviepeople.role='Actor'
    dbmoviepeople.department='Acting'
    dbmoviepeople.character=Nonetostr(actor['character'])[:100]
    dbmoviepeople.cast_id=actor['cast_id']
    dbmoviepeople.order=actor['order']
    dbmoviepeople.save()
    return (dbpeople, dbmoviepeople)

def makeDBcrew(dbmovie, crew):
    try: dbpeople=People.objects.get(tmdb_id=Nonetostr(crew['id']))
    except: dbpeople=People()
    dbpeople.name=Nonetostr(crew['name'])
    dbpeople.tmdb_id=Nonetostr(crew['id'])
    dbpeople.profile=Nonetostr(crew['profile_path'])
    dbpeople.save()
    try: dbmoviepeople=MoviePeople.objects.get(people=dbpeople, movie=dbmovie, role=crew['job'])
    except: dbmoviepeople=MoviePeople()
    dbmoviepeople.movie=dbmovie
    dbmoviepeople.people=dbpeople
    dbmoviepeople.role=Nonetostr(crew['job'])
    dbmoviepeople.department=Nonetostr(crew['department'])
    dbmoviepeople.save()
    return (dbpeople, dbmoviepeople)
    


def writeMovie(movie_main, movie_cast, movie_release):
    dbmovie=makeDBmovie(movie_main)
    dbreleases=makeDBreleases(dbmovie, movie_release)
    makeDBpeople(dbmovie, movie_cast)
    return [dbmovie.name]


