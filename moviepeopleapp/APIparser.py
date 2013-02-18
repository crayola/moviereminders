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
import time

log = logging.getLogger(__name__)

apikey="3dffd9e01086f6801f45d2161cd2710d"
RTapikey="5z9vxrv4mrkcdkw2fbymhhdh"

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
      ret += [x['id'] for x in tmp['results']]
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
  dbmovie=parseMovie(idmovie, date)
  #if not dbmovie:
  #  return None
  #rs = requests.get(url, 
  #                  params={
  #                    'api_key': apikey,
  #                    'start_date': date,
  #                    'end_date': enddate,
  #                  })
  #if rs.ok:
  #  changes = rs.json['changes']
  #  fields = [x['key'] for x in rs.json['changes']]
  #else: 
  #  return None # TODO: handle more properly
  #if 'trailers' in fields:
  #  changedtrailers = [y 
  #                     for k in 
  #                     [x['items'] for x in changes if x['key']=='trailers']
  #                     for y in k
  #                     if y['action']=='added'
  #                     and y['iso_639_1']=='en'] # TODO: not update if same trailer both deleted and added
  #  for trailer in changedtrailers:
  #    try:
  #      tmp=[x['sources'] for x in trailer['value'] if x['site']=='YouTube'][0]
  #    except Exception:
  #      continue
  #    tmp.update({'name':trailer['value']['name']})
  #    makeDBtrailers(dbmovie, 
  #                   [tmp], date)
  #if 'releases' in fields:
  #  changedreleases = [y 
  #                     for k in 
  #                     [x['items'] for x in changes if x['key']=='releases']
  #                     for y in k
  #                     if y['action']=='added' or y['action']=='updated'
  #                     ] # TODO: not update if same trailer both deleted and added
  #  tmp = [release['value'] for release in changedreleases]
  #  makeDBreleases(dbmovie, tmp, date)
  #changedcast, changedcrew = [], []
  #if 'cast' in fields:
  #  changedcast = [y 
  #                 for k in 
  #                 [x['items'] for x in changes if x['key']=='cast']
  #                 for y in k
  #                 if y['action']=='added' or y['action']=='updated'
  #                ] # TODO: not update if same trailer both deleted and added
  #  changedcast = [cast['value'] for cast in changedcast]
  #  for x in changedcast: 
  #    x['role']='Actor'
  #if 'crew' in fields:
  #  changedcrew = [y 
  #                 for k in 
  #                 [x['items'] for x in changes if x['key']=='crew']
  #                 for y in k
  #                 if y['action']=='added' or y['action']=='updated'
  #                ] # TODO: not update if same trailer both deleted and added
  #  changedcrew = [crew['value'] for crew in changedcrew]
  #  for x in changedcrew: 
  #    x['character']=''
  #    x['role']=x['job']
  #  updateDBpeople(dbmovie, changedcast+changedcrew, date)
  #if 'general' in fields:
  #  created = [y for k in 
  #             [x['items'] for x in changes if x['key']=='general']
  #             for y in k if y['action']=='created']
  #  if created and dbmovie:
  #    dbmovie.date_info=date
  #    dbmovie.save()
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



def parseMovie(idmovie, date=None):
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
    dbmovie = writeMovie(movie_main, movie_cast, movie_release, movie_trailer, date)
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
        writeMovie(movie_main, movie_cast, movie_release, movie_trailer, date=None)
    return 1;

def Nonetostr(a):
    if a==[] or a is None : a=''
    return(a)


def makeDBmovie(movie_main, date):
    genres=movie_main['genres']
    languages=[x['iso_639_1'] for x in movie_main.get('spoken_languages', [])]
    production_companies=movie_main.get('production_companies')
    countries=[x['iso_3166_1'][:2] for x in movie_main.get('production_countries', [])]
    dbmovie, created=Movie.objects.get_or_create(tmdb_id=movie_main.get('id'))
    dbmovie.name=(movie_main.get('title') or '')[:200]
    dbmovie.poster=(movie_main.get('poster_path') or '')[:50]
    dbmovie.backdrop=(movie_main.get('backdrop_path') or '')[:50]
    dbmovie.imdb_id=(movie_main.get('imdb_id') or '')[:50]
    dbmovie.revenue=movie_main.get('revenue')
    dbmovie.homepage=(movie_main.get('homepage') or '')[:200]
    dbmovie.popularity=movie_main.get('popularity')
    dbmovie.votes=movie_main.get('vote_count')
    dbmovie.vote_average=movie_main.get('vote_average')
    dbmovie.runtime=movie_main.get('runtime')
    dbmovie.adult=movie_main.get('adult')
    dbmovie.budget=movie_main.get('budget')
    try: 
      RTdata=getRTdata(dbmovie)
      dbmovie.RT_id = RTdata['id']
      dbmovie.RT_link = RTdata['links']['alternate'][:200]
      dbmovie.RT_critics_score = RTdata['ratings']['critics_score']
      dbmovie.RT_audience_score = RTdata['ratings']['audience_score']
      dbmovie.RT_critics_rating = RTdata['ratings']['critics_rating']
      dbmovie.RT_audience_rating = RTdata['ratings']['audience_rating']
    except:
      pass
    if created: dbmovie.date_info=date
    dbmovie.save()

    MovieGenre.objects.filter(movie=dbmovie).exclude(genre__in=[x['name'] for x in genres]).delete()
    for genre in genres:
        MovieGenre.objects.get_or_create(movie=dbmovie, genre=genre['name'], defaults={'genre_tmdb_id':genre['id']})

    MovieCompany.objects.filter(movie=dbmovie).exclude(company__in=[x['name'][:200] for x in production_companies]).delete()
    for company in production_companies:
        MovieCompany.objects.get_or_create(movie=dbmovie, company=company['name'][:200], defaults={'company_tmdb_id': company['id']})

    MovieLanguage.objects.filter(movie=dbmovie).exclude(language__in=languages).delete()
    for language in languages:
        MovieLanguage.objects.get_or_create(movie=dbmovie, language=language)

    MovieCountry.objects.filter(movie=dbmovie).exclude(country__in=countries).delete()
    for country in countries:
        MovieCountry.objects.get_or_create(movie=dbmovie, country=country)

    dbmovieoverview=MovieOverview.objects.get_or_create(movie=dbmovie)[0]
    dbmovieoverview.overview=Nonetostr(movie_main['overview'])
    dbmovieoverview.tagline=Nonetostr(movie_main['tagline'])
    dbmovieoverview.save()

    return dbmovie


def makeDBreleases(dbmovie, movie_release, date_info=None):
    Release.objects.filter(movie=dbmovie).exclude(country__in=[date['iso_3166_1'][:2] for date in movie_release]).delete()
    for date in movie_release:
      try: pydate = datetime.datetime.strptime(date['release_date'], '%Y-%m-%d')
      except ValueError: continue
      dbmovierelease, created = Release.objects.get_or_create(movie=dbmovie, country=date['iso_3166_1'][:2], defaults={'date': pydate})
      dbmovierelease.date = pydate
      if created: dbmovierelease.date_info = date_info
      dbmovierelease.save()
    return 1

def makeDBtrailers(dbmovie, movie_trailer, date=None):
  Trailer.objects.filter(movie=dbmovie).exclude(url__in=[x['source'][:200] for x in movie_trailer if x.get('source')]).delete()
  for trailer in [x for x in movie_trailer if x.get('source')]:
    dbmovietrailer, created=Trailer.objects.get_or_create(movie=dbmovie, url=trailer['source'][:200])
    dbmovietrailer.size=(trailer.get('size') or '')[:10]
    dbmovietrailer.format='youtube'
    dbmovietrailer.name=trailer.get('name')
    if created: dbmovietrailer.date_info = date
    dbmovietrailer.save()
  return 1

def updateDBpeople(dbmovie, peoples, date):
  cast, crew = peoples['cast'], peoples['crew']
  for x in cast: 
    x['role']='Actor'
  for x in crew: 
    x['character']=''
    x['role']=x['job']
  peoples=cast+crew
  MoviePeople.objects.filter(movie=dbmovie).exclude(people__tmdb_id__in=[people['id'] for people in peoples]).delete()
  for people in set([people['id'] for people in peoples]):
    dbpeople, created=People.objects.get_or_create(tmdb_id=people)
    dbpeople.profile=[(x.get('profile_path','') or '') for x in peoples if x['id'] == people][0]
    dbpeople.name=[x['name'][:200] for x in peoples if x['id'] == people][0]
    dbpeople.save()
    roles = set([x['role'] for x in peoples if x['id'] == people])
    MoviePeople.objects.filter(movie=dbmovie, people=dbpeople).exclude(role__in=roles).delete()
    for role in roles:
      characters = set([(x.get('character', '') or '')[:100] for x in peoples if x['id'] == people and x['role'] == role])
      MoviePeople.objects.filter(movie=dbmovie, people=dbpeople, role=role).exclude(character__in=characters).delete()
    #print(people)
      for character in characters:
        dbmoviepeople, created=MoviePeople.objects.get_or_create(movie=dbmovie, people=dbpeople, role=role, character=character)
        if created: dbmoviepeople.date_info = date
        dictpeople=[x for x in peoples if x['id'] == people and x['role'] == role and (x.get('character', '') or '')[:100] == character][0]
        dbmoviepeople.department='Acting' if role=='Actor' else dictpeople.get('department', '')
        dbmoviepeople.cast_id=dictpeople['cast_id'] if role=='Actor' else None
        dbmoviepeople.order=dictpeople['order'] if role=='Actor' else None
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



def writeMovie(movie_main, movie_cast, movie_release, movie_trailer, date):
    dbmovie=makeDBmovie(movie_main, date)
    try:
      dbreleases=makeDBreleases(dbmovie, movie_release['countries'], date)
    except Exception:
      pass
    if movie_trailer: makeDBtrailers(dbmovie, movie_trailer.get('youtube'), date)
    if movie_cast: updateDBpeople(dbmovie, movie_cast, date)
    return dbmovie



def buildImportance(a, b):
  mindategood = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d") # we want young stuff
  recentmovies = Release.objects.filter(country='US', date__gte=mindategood).values_list('movie', flat=True).distinct() # TODO: this is inefficient, same query runs each time someone follows a person.
  for i in People.objects.filter(id__gte=a, id__lte=b):
    if i.id % 100 == 0: 
      print(i.id)
    i.importance=sum(
            [6-(min(6, x.order)) for x in MoviePeople.objects.filter(people=i, role='Actor', movie__id__in=recentmovies, movie__adult=False, movie__popularity__gt=1, order__lte=5)] + 
            [6 for x in MoviePeople.objects.filter(people=i, movie__id__in=recentmovies, role='Director', movie__adult=False, movie__popularity__gt=1)]
    )
    i.save()
  return 1


def getRTdata(movie):
  url='http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json'
  rs = requests.get(url, 
                    params={
                      'api_key': RTapikey,
                      'type':'imdb',
                      'id':movie.imdb_id[2:],
                    })
  if rs.ok:
    return rs.json
  else: 
    return None

def updateRTscores(movie):
    json = getRTdata(movie)
    print(json)
    try:
      movie.RT_id = json['id']
      movie.RT_link = json['links']['alternate'][:200]
      movie.RT_critics_score = json['ratings'].get('critics_score')
      movie.RT_audience_score = json['ratings'].get('audience_score')
      movie.RT_critics_rating = json['ratings'].get('critics_rating')
      movie.RT_audience_rating = json['ratings'].get('audience_rating')
      movie.save()
      return movie
    except Exception:
      return None


def updateRTscores(popmin, popmax):
  a=(updateRTscore(movie) for movie in Movie.objects.filter(popularity__lte=popmax, popularity__gte=popmin, RT_audience_score__isnull=True).iterator())
  for i in a:
    print(i)
    time.sleep(1)


#a=(updateRTscores(movie) for movie in Movie.objects.filter(popularity__gte=10).iterator())
#for i in a:
#  print(i)


#[parseMovie(x) for x in range(1000, 5000)]


#def nextActor(actors):
#  movies=MoviePeople.objects.filter(people__in=actors).(movies) #TODO
#  actors=MoviePeople.objects.filter(movie__in=movies, order__lte=5).(top 5) #TODO
#  count
#  return max count
