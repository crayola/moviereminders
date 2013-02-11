import logging
import os
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q
import datetime
from django.template import Template

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
from moviepeopleapp.templatetags.artist import artist_box_front, artist_pic_url


log = logging.getLogger(__name__)

def loginAjax(request):
    #redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if request.POST:
        json=simplejson.loads(request.POST.get('JSON'))
        #errors = manipulator.get_validation_errors(request.POST)
        user = authenticate(username = json['username'], password = json['password'])
        if user is not None and user.is_active:
            login(request, user)
            ret_json = {'auth': True, 'username': user.username}
            log.info("Sign in:" + user.username)
        else:
            ret_json = {'auth': False}
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def autocomplete(request):
    #get term
    json_string = request.GET.get('JSON')
    json = simplejson.loads(json_string)
    term = json['term']

    #get results
    autocomplete = SearchQuerySet().autocomplete(name_autocomplete=term)
    #autocomplete = SearchQuerySet().all()
    log.info("term:"+term+" results:"+str(autocomplete.count()))

    #create response
    autocomplete = sorted(autocomplete, key=lambda k: -(k.object.importance or 0))
    ret_json = {'artists':[]}
    for result in autocomplete:
        people = result.object
        try:
            Follow.objects.get(user=request.user, people=people)
            follow=True
        except Exception:
            follow=False
        people_map = {
            'id': people.id,
            'name': people.name,
            'profile': people.profile,
            'follow': follow,
            'box':artist_box_front(people)
        }
        ret_json['artists'].append(people_map)
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def manualsearch(request):
    #get term
    json_string = request.GET.get('JSON')
    json = simplejson.loads(json_string)
    term = json['term']
    if len(term) < 3: return None

    #get results
    try:
        people = People.objects.filter(name__icontains=term)
        people = sorted(people, key=lambda k: -(k.importance or 0))[0]
        log.info("term: "+term+" results:"+people.name)
    except Exception:
        log.info("term: "+ term + " not found")
        return None

    #create response
    try:
        Follow.objects.get(user=request.user, people=people)
        follow=True
    except Exception:
        follow=False
    ret_json = {
        'id' : people.id,
        'name' : people.name,
        'profile' : people.profile,
        'follow': follow
    }
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")

#follow an artist on the frontpage
#store in session, will be lost if person does not create an account
def frontpageFollow(request):
    json = simplejson.loads(request.GET.get('JSON'))
    artistId = json['artist_id']
    artist = People.objects.get(pk=artistId)
    #save in session
    if('front_follows' not in request.session):
        request.session['front_follows'] = []
    request.session['front_follows'].append(artist)
    request.session.save()
    log.info('front-following artist:'+artist.name+' id:'+str(artist.id))
    log.info('request.session[front_follows]:'+str(request.session['front_follows']))
    #find a new artist
    artist_random = artists = People.objects.order_by('?')[0]
    t = Template('artist_box')
    box = artist_box_front(artist_random)
    #create map of artist
    artistMap = {'id':artist.id,'name':artist.name,'pic_url':artist_pic_url(artist)}
    return HttpResponse(simplejson.dumps({
        'artist_box':box,
        'artist':artistMap
    }), mimetype="application/json")

#send password token
def sendToken(request, new=False):
    json = simplejson.loads(request.GET.get('json'))
    email = json['email']
    log.info("Token for:"+email)
    user = User.objects.get(username=email)
    #create auth token & send confirmation email
    token_code = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for x in range(32))
    log.info("token_code:"+token_code)
    [token.delete() for token in CreateAccountToken.objects.filter(email=email)]
    token = CreateAccountToken.objects.create(code=token_code,email=email)
    token.save()
    link = settings.SERVER_URL+'login/'+token_code
    if new:
        subject = 'Welcome to Whispers!'
        html_content = '<p>Hi, thanks for joining whispers,</p>'
        html_content += '<p>Set up a password for accessing your account whenever you like by following this link:<br/>'
        html_content += '<p><a href="'+link+'">'+link+'</a></p>'
        html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
    else:
        subject = 'Your Whispers password renewal.'
        html_content = '<p>Set up a new password by following this link:<br/>'
        html_content += '<p><a href="'+link+'">'+link+'</a></p>'
        html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
    msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@whispers.io>', [email])
    msg.attach_alternative(html_content, "text/html")
    log.info(msg.send())

    return HttpResponse(simplejson.dumps({"already_exists":True}), mimetype="application/json")

def signup(request):
    #get email
    json = simplejson.loads(request.GET.get('json'))
    email = json['email']
    log.info("signup:"+email)
    users = User.objects.filter(username=email)
    if(len(users)>0):
        log.info('Account already exists:'+email)
        return HttpResponse(simplejson.dumps({"already_exists":True}), mimetype="application/json")
    user = User.objects.create_user(email, email, '*')
    user.save()
    user = authenticate(username=email,password='*')
    login(request, user)
    log.info("user:"+user.email+" logged in")

    #create the follows
    log.info('request.session[front_follows]:'+str(request.session['front_follows']))
    if 'front_follows' in request.session:
        for artist in request.session['front_follows']:
            if(Follow.objects.filter(user=user,people=artist).count()<=0):
                Follow.objects.create(user=user,people=artist)

    sendToken(request, new=True)

    return HttpResponse(simplejson.dumps({}), mimetype="application/json")


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