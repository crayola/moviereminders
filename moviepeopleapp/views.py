import logging
import os
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Q
import datetime

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


log = logging.getLogger(__name__)

@ensure_csrf_cookie
def frontpage(request):
  if(request.user.is_anonymous()):
    log.info("frontpage hit")
  else:
    log.info("frontpage, user:"+str(request.user.email))
  loginform = AuthenticationForm()
  return render(request,'frontpage.html', {'test':'test', 'signinform': loginform})

def createAccount(request, token_code):
  try: 
    token = CreateAccountToken.objects.get(code=token_code)
  except CreateAccountToken.DoesNotExist:
    return render(request, 'badToken.html')
  user = User.objects.get(username=token.email)
  new = user.check_password('*')
  if request.method == 'POST': 
    form = SetPasswordForm(data=request.POST, user=user)
    if form.is_valid():
      password=request.POST['new_password1']
      user.set_password(password)
      user.save()
      #token.delete() # token is single use only!
      log.info("Account created for:" + user.username)
      if new:
        return render(request, 'accountCreated.html')
      else:
        return render(request, 'passwordUpdated.html')
  else:
    form = SetPasswordForm(user)
    log.info("create_account page opened by:"+token.email)
    return render(request, 'create_account.html', {'form':form, 'user':user, 'token':token_code})


def signin(request):
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


def logoutview(request):
  logout(request)
  return HttpResponse(simplejson.dumps({}), mimetype="application/json")


def load_sample_db(request):
  import moviepeopleapp.APIparser as APIparser
  log.info('Parsing!')
  [APIparser.parseMovie(x) for x in range(1000)]
  log.info('Done parsing.')
  APIparser.buildImportance(1, 10000)
  log.info('Done building importance.')
  return HttpResponse('All done! Now please rebuild the index: manage.py rebuild_index.')


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
    ret_json = {'peoples':[]}
    for result in autocomplete:
        people = result.object
        people_map = {
            'id' : people.id,
            'name' : people.name,
            'profile' : people.profile
        }
        ret_json['peoples'].append(people_map)
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
    ret_json = {
            'id' : people.id,
            'name' : people.name,
            'profile' : people.profile
        }
    return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def yourwhispers(request):
  nowdate = datetime.datetime.today().strftime("%Y-%m-%d")
  user=request.user;
  peoples = [follow.people_id for follow in Follow.objects.filter(user_id=user.id)]
  ret_json = {'movies':[]}
  for people in peoples:
    ret_json['movies'] += make_people_movies(people, nowdate)
  return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def unfollow(request):
  user=request.user;

  json_string = request.GET.get('JSON')
  json = simplejson.loads(json_string)
  followee = json['followee']

  people = Follow.objects.get(user_id=user.id, people_id=followee)
  people.delete()
  return HttpResponse(simplejson.dumps({}), mimetype="application/json")


def followees(request):
  user=request.user;
  peoples = [follow.people for follow in Follow.objects.filter(user_id=user.id)]
  ret_json = {'people': []}
  for people in peoples:
    ret_json['people'].append({'name': people.name, 'id': people.id, 'profile':people.profile})
  return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")


def people_movies(request,id):
  ret_json={'movies':make_people_movies(id)}
  return HttpResponse(simplejson.dumps(ret_json), mimetype="application/json")

def make_people_movies(id, mindate = "1900-01-01"):
    #mindate = datetime.datetime.strptime(mindate, "%Y-%m-%d")
    people = People.objects.get(pk=id)
    ret_json = []
    moviePeoples = MoviePeople.objects.filter(people=people, role__in=['Actor', 'Director'])
    # select which movies to show
    def keyfun(movie):
      try: 
        return str(Release.objects.filter(movie=movie)[0].date)
      except Exception:
        return "3000"
    movies = sorted(set([x.movie for x in moviePeoples]), 
                    key=keyfun,
                    reverse=True)
    for movie in movies:
        #if len(ret_json['movies']) >= 5: break
        movie_map = {
            'id':movie.id,
            'poster':movie.poster,
            'name':movie.name,
            'trailers':[],
        }
        moviepeople_actor = None
        moviepeoples_actor = MoviePeople.objects.filter(
          movie=movie, people=people, role='Actor')
        if moviepeoples_actor:
          moviepeople_actor = sorted(
            moviepeoples_actor, key=lambda k: k.order)[0]
          moviepeople_actor = {k:getattr(moviepeople_actor, k) for k
                             in ['id', 'character', 'order']}
        movie_map['moviepeople_actor'] = moviepeople_actor
        moviepeoples_director = MoviePeople.objects.filter(
          movie=movie, people=people, role='Director')
        movie_map['moviepeople_director']=bool(moviepeoples_director)
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
            release_map = {
                "date": release.strftime("%Y-%m-%d")
                }
        except Exception:
            release_map = {
                "date": "1970-01-01"
                }
            continue
        movie_map['release'] = release_map
        ret_json.append(movie_map)
    return ret_json;

def sendToken(request, new=False):
    json = simplejson.loads(request.GET.get('JSON'))
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
    json = simplejson.loads(request.GET.get('JSON'))
    email = json['email']
    log.info("signup:"+email)
    users = User.objects.filter(username=email)
    if(len(users)>0):
      return HttpResponse(simplejson.dumps({"already_exists":True}), mimetype="application/json")
    user = User.objects.create_user(email, email, '*')
    user.save()
    user = authenticate(username=email,password='*')
    login(request, user)
    log.info("user:"+user.email+" logged in")

    sendToken(request, new=True)

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

