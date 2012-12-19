import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviepeople.settings")

from django.db.models import Q
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from moviepeopleapp.models import (People, MoviePeople, Trailer, 
                                   Release, Movie, MovieGenre, 
                                   MovieOverview, MovieLanguage, 
                                   MovieCountry, MovieCompany)
from urllib2 import urlopen, Request, URLError, HTTPError
import requests
import datetime

log = logging.getLogger(__name__)

apikey="3dffd9e01086f6801f45d2161cd2710d"

#def checkmovie(idmovie, info):
#    """Downloads info (main, releases, casts, ..) about movie idmovie from tmdb."""
#    if info=="main":
#        url="http://api.themoviedb.org/3/movie/%s?api_key=%s" % (idmovie, apikey)
#    else: url="http://api.themoviedb.org/3/movie/%s/%s?api_key=%s" % (idmovie, info, apikey)
#    request = Request(url)
#    request.add_header("Accept", "application/json")
#    read=0
#    while read==0:
#        try:
#            req = urlopen(request, timeout=3)
#            read=1
#        except HTTPError:
#            print("HTTP error.")
#            raise
#        except URLError:
#            read=0
#            print("Timeout -- trying again.")
#    parsed=0
#    while parsed==0:
#        try:
#            ret=simplejson.load(req)
#            parsed=1
#        except Exception:
#            parsed=0
#            print("JSON issue, probably socket.timeout.")
#    return ret
#

def pullMovie(idmovie):
  """Downloads info (main, releases, casts, ..) about movie idmovie from tmdb."""
  url="http://api.themoviedb.org/3/movie/%s" % idmovie
  rs = requests.get(url, 
                    params={
                      'api_key': apikey,
                      'append_to_response': 'trailers,releases,casts,changes',
                    })
  if rs.ok:
    return rs.json
  else: 
    return None

def listChangedMovies(date):
  """Downloads info (main, releases, casts, ..) about movie idmovie from tmdb."""
  page = 0
  total_pages = 1
  enddate= (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
  url="http://api.themoviedb.org/3/movie/changes"
  ret = []
  while (page != total_pages):
    page += 1
    rs = requests.get(url, 
                      params={
                        'page': page,
                        'api_key': apikey,
                        'start_date': date,
                        'end_date': enddate,
                      })
    if rs.ok:
      tmp = rs.json
      total_pages = tmp['total_pages']
      ret.extend([x['id'] for x in tmp['results']])
  return ret


def movieChanges(idmovie, date):
  enddate= (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
  url="http://api.themoviedb.org/3/movie/%s/changes" % idmovie
  rs = requests.get(url, 
                    params={
                      'api_key': apikey,
                      'start_date': date,
                      'end_date': enddate,
                    })
  return rs.json['changes']

def movieUpdate(idmovie, date):
  enddate= (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
  url="http://api.themoviedb.org/3/movie/%s/changes" % idmovie
  dbmovie=parseMovie(idmovie)
  if not dbmovie:
    return None
  rs = requests.get(url, 
                    params={
                      'api_key': apikey,
                      'start_date': date,
                      'end_date': enddate,
                    })
  if rs.ok:
    changes = rs.json['changes']
    fields = [x['key'] for x in rs.json['changes']]
  else: 
    return None # TODO: handle more properly
  if 'trailers' in fields:
    changedtrailers = [y 
                       for k in 
                       [x['items'] for x in changes if x['key']=='trailers']
                       for y in k
                       if y['action']=='added'
                       and y['iso_639_1']=='en'] # TODO: not update if same trailer both deleted and added
    for trailer in changedtrailers:
      try:
        tmp=[x['sources'] for x in trailer['value'] if x['site']=='YouTube'][0]
      except Exception:
        continue
      tmp.update({'name':trailer['value']['name']})
      makeDBtrailers(dbmovie, 
                     [tmp], date)
  if 'releases' in fields:
    changedreleases = [y 
                       for k in 
                       [x['items'] for x in changes if x['key']=='releases']
                       for y in k
                       if y['action']=='added' or y['action']=='updated'
                       ] # TODO: not update if same trailer both deleted and added
    tmp = [release['value'] for release in changedreleases]
    makeDBreleases(dbmovie, tmp, date)
  changedcast, changedcrew = [], []
  if 'cast' in fields:
    changedcast = [y 
                   for k in 
                   [x['items'] for x in changes if x['key']=='cast']
                   for y in k
                   if y['action']=='added' or y['action']=='updated'
                  ] # TODO: not update if same trailer both deleted and added
    changedcast = [cast['value'] for cast in changedcast]
    for x in changedcast: 
      x['role']='Actor'
  if 'crew' in fields:
    changedcrew = [y 
                   for k in 
                   [x['items'] for x in changes if x['key']=='crew']
                   for y in k
                   if y['action']=='added' or y['action']=='updated'
                  ] # TODO: not update if same trailer both deleted and added
    changedcrew = [crew['value'] for crew in changedcrew]
    for x in changedcrew: 
      x['character']=''
      x['role']=x['job']
    updateDBpeople(dbmovie, changedcast+changedcrew, date)
  if 'general' in fields:
    created = [y for k in 
               [x['items'] for x in changes if x['key']=='general']
               for y in k if y['action']=='created']
    if created and dbmovie:
      dbmovie.date_info=date
      dbmovie.save()
  return dbmovie




#tmp1 = listChangedMovies('2012-10-06')
#print(tmp1)
#
#trailers = []
#for i in tmp1:
#  tmp = movieChanges(i, '2012-10-06')
#  if 'cast' in [x['key'] for x in tmp]:
#    trailers.append(i)
#
#for i in trailers:
#  parseMovie(i)
#  print(i)
#

def processChanges(date):
  for i in listChangedMovies(date):
    print(i, movieUpdate(i, date))

#[APIparser.processChanges('2012-10-%s' % x) for x in range(27, 32)]
#[APIparser.processChanges('2012-11-%s' % x) for x in ['01', '02', '03', '04', '05', '06', '07', '08', '09'] + range(10, 32)]


#
#def parseMovie(tmdbid):
#    try:
#        movie_main=checkmovie(tmdbid, "main")
#    except Exception:
#        print("id %s: no movie" % tmdbid)
#        return 0
#    i=0
#    while i < 10:
#        try:
#            movie_cast=checkmovie(tmdbid, "casts")
#            i=10
#        except Exception:
#            movie_cast=''
#            i+=1
#    i=0
#    while i < 10:
#        try:
#            movie_release=checkmovie(tmdbid, "releases")
#            i=10
#        except Exception:
#            movie_release=''
#            i+=1
#    print("id %s: writing to disk" % tmdbid)
#    f=open("/whispers/moviepeople/dumptmdb%s" % (tmdbid/10000), "a")
#    simplejson.dump({"main": movie_main, "casts": movie_cast, "releases": movie_release}, f)
#    f.write("\n")
#    f.close()
#    return 1
#
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



def parseMovie(idmovie):
  movie = pullMovie(idmovie)
  if movie:
    movie_main=movie
    if "casts" in movie:
      movie_cast = movie.get("casts")
    else:
      movie_cast = None
    if "releases" in movie:
      movie_release=movie.get("releases")
    else:
      movie_release = None
    if "trailers" in movie:
      movie_trailer=movie.get("trailers")
    else:
      movie_trailer = None
    dbmovie = writeMovie(movie_main, movie_cast, movie_release, movie_trailer)
    log.info('Parsed movie: ' + str(dbmovie))
    return dbmovie
  else: 
    return None


def parseDump(dumpfile):
    for movie in [simplejson.loads(line) for line in open(dumpfile)]:
        movie_main=movie["main"]
        movie_cast=movie["casts"]
        movie_release=movie["releases"]
        movie_trailer=movie["trailers"]
        writeMovie(movie_main, movie_cast, movie_release, movie_trailer)
    return 1;

def Nonetostr(a):
    if a==[] or a is None : a=''
    return(a)


def makeDBmovie(movie_main):
    genres=movie_main['genres']
    languages=[x['iso_639_1'] for x in Nonetostr(movie_main['spoken_languages'])]
    production_companies=movie_main['production_companies']
    countries=[x['iso_3166_1'][:2] for x in Nonetostr(movie_main['production_countries'])]
    try: dbmovie=Movie.objects.get(tmdb_id=Nonetostr(movie_main['id']))
    except Exception: dbmovie=Movie()
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
        except Exception: dbmoviegenre=MovieGenre()
        dbmoviegenre.movie=dbmovie
        dbmoviegenre.genre=genre['name']
        dbmoviegenre.genre_tmdb_id=genre['id']
        dbmoviegenre.save()
    for company in production_companies:
        try: dbmoviecompany=MovieCompany.objects.get(movie=dbmovie, company=company['name'][:200])
        except Exception: dbmoviecompany=MovieCompany()
        dbmoviecompany.movie=dbmovie
        dbmoviecompany.company=company['name'][:200]
        dbmoviecompany.company_tmdb_id=company['id']
        dbmoviecompany.save()
    for language in languages:
        try: dbmovielanguage=MovieLanguage.objects.get(movie=dbmovie, language=language)
        except Exception: dbmovielanguage=MovieLanguage()
        dbmovielanguage.movie=dbmovie
        dbmovielanguage.language=language
        dbmovielanguage.save()
    for country in countries:
        try: dbmoviecountry=MovieCountry.objects.get(movie=dbmovie, country=country)
        except Exception: dbmoviecountry=MovieCountry()
        dbmoviecountry.movie=dbmovie
        dbmoviecountry.country=country
        dbmoviecountry.save()
    try: dbmovieoverview=MovieOverview.objects.get(movie=dbmovie)
    except Exception: dbmovieoverview=MovieOverview()
    dbmovieoverview.movie=dbmovie
    dbmovieoverview.overview=Nonetostr(movie_main['overview'])
    dbmovieoverview.tagline=Nonetostr(movie_main['tagline'])
    dbmovieoverview.save()
    return dbmovie


def makeDBreleases(dbmovie, movie_release, date_info=None):
    if movie_release: 
      for date in movie_release:
        try: dbmovierelease=Release.objects.get(movie=dbmovie, date=date['release_date'])
        except Exception: dbmovierelease=Release()
        dbmovierelease.movie=dbmovie
        dbmovierelease.date=date['release_date'] # TODO: got an error with a date with year 20011-04-11 in tmdb. must make sure this doesn't break (insert null instead). For now (no time) I just fixed the date in the text dump :-/
        dbmovierelease.country=date['iso_3166_1'][:2]
        if date_info: dbmovierelease.date_info = date_info
        dbmovierelease.save()
    return 1

def makeDBtrailers(dbmovie, movie_trailer, date=None):
  for trailer in movie_trailer:
    try:
      dbmovietrailer=Trailer.objects.get(movie=dbmovie, url=trailer['source'][:200])
    except (Trailer.DoesNotExist, KeyError):
      dbmovietrailer=Trailer()
    dbmovietrailer.movie=dbmovie
    dbmovietrailer.url=trailer.get('source')[:200]
    dbmovietrailer.size=trailer.get('size')
    dbmovietrailer.format='youtube'
    dbmovietrailer.name=trailer.get('name')
    if date: dbmovietrailer.date_info = date
    dbmovietrailer.save()
  return 1

def updateDBpeople(dbmovie, peoples, date):
  for people in peoples:
    #print(people)
    try: dbmoviepeople=MoviePeople.objects.get(movie=dbmovie, people=People.objects.get(tmdb_id=people['person_id']), role=people['role'], character=Nonetostr(people.get('character'))[:100])
    except Exception: return None
    dbmoviepeople.date_info = date
    dbmoviepeople.save()
  return dbmovie


def makeDBpeople(dbmovie, movie_cast):
    try: actors=movie_cast['cast']
    except Exception: actors=[]
    try: crews=movie_cast['crew']
    except Exception: crews=[]
    for actor in actors: makeDBactor(dbmovie, actor)
    for crew in crews: makeDBcrew(dbmovie, crew)
    return 1

def makeDBactor(dbmovie, actor):
    try: dbpeople=People.objects.get(tmdb_id=Nonetostr(actor['id']))
    except Exception: dbpeople=People()
    dbpeople.name=Nonetostr(actor['name'])[:200]
    dbpeople.tmdb_id=Nonetostr(actor['id'])
    dbpeople.profile=Nonetostr(actor['profile_path'])
    dbpeople.save()
    try: dbmoviepeople=MoviePeople.objects.get(people=dbpeople, movie=dbmovie, role='Actor', character=Nonetostr(actor['character'])[:100])
    except Exception: dbmoviepeople=MoviePeople()
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
    try: 
      dbpeople=People.objects.get(tmdb_id=Nonetostr(crew['id']))
    except Exception: dbpeople=People()
    dbpeople.name=Nonetostr(crew['name'])
    dbpeople.tmdb_id=Nonetostr(crew['id'])
    dbpeople.profile=Nonetostr(crew['profile_path'])
    dbpeople.save()
    try: 
      dbmoviepeople = MoviePeople.objects.get(people=dbpeople, 
                                              movie=dbmovie, 
                                              role=crew['job'])
    except Exception: 
      dbmoviepeople=MoviePeople()
    dbmoviepeople.movie=dbmovie
    dbmoviepeople.people=dbpeople
    dbmoviepeople.role=Nonetostr(crew['job'])
    dbmoviepeople.department=Nonetostr(crew['department'])
    dbmoviepeople.save()
    return (dbpeople, dbmoviepeople)



def writeMovie(movie_main, movie_cast, movie_release, movie_trailer):
    dbmovie=makeDBmovie(movie_main)
    try:
      dbreleases=makeDBreleases(dbmovie, movie_release['countries'])
    except Exception:
      pass
    if movie_trailer: makeDBtrailers(dbmovie, movie_trailer.get('youtube'))
    if movie_cast: makeDBpeople(dbmovie, movie_cast)
    return dbmovie


def buildImportance(a, b):
  for i in People.objects.filter(id__gte=a, id__lte=b):
    if i.id % 100 == 0: print(i.id)
    i.importance=sum(
            [6-(min(6, (x.order or 10))) for x in MoviePeople.objects.filter(people=i, role='Actor')] + 
            [6 for x in MoviePeople.objects.filter(people=i, role='Director')]
    )
    i.save()
  return 1



#[parseMovie(x) for x in range(1000, 5000)]
