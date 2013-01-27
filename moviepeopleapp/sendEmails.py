import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviepeople.settings")

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import date
from moviepeopleapp.models import (People, MoviePeople, Trailer, 
                                   Release, Movie, MovieGenre, 
                                   MovieOverview, MovieLanguage, 
                                   MovieCountry, MovieCompany, Follow)
from urllib2 import urlopen, Request, URLError, HTTPError
import requests
import datetime
from django.core.mail import send_mail, EmailMultiAlternatives

log = logging.getLogger(__name__)


def sendUpdates(day):
  (newMPs, newTrailers, newReleases) = checkNewStuff(day)
  sendNewMPs(newMPs)
  sendNewTrailers(newTrailers)
  sendNewReleases(newReleases)
  return 1

def checkNewStuff(day):
  date= (datetime.datetime.strptime(day, "%Y-%m-%d")).date()
  newMPs = [x for x in MoviePeople.objects.filter(date_info=day) if (lambda x: min([y.date for y in x])  > date if x else True)(Release.objects.filter(movie=x.movie))]
  newTrailers_movies = [(x.movie, x.url) for x in Trailer.objects.filter(date_info=day) if (lambda x: min([y.date for y in x])  > date if x else True)(Release.objects.filter(movie=x.movie))] 
  newTrailers_MPs = [(MoviePeople.objects.filter(movie=x[0]), x[0], x[1]) for x in newTrailers_movies]
  newReleases_movies = [(x.movie, date + datetime.timedelta(7)) for x in Release.objects.filter(date=date + datetime.timedelta(7), country='US') if (lambda x: min([y.date for y in x])  > date if x else True)(Release.objects.filter(movie=x.movie))] 
  newReleases_MPs = [(MoviePeople.objects.filter(movie=x[0]), x[0], x[1]) for x in newReleases_movies]
  return (newMPs, newTrailers_MPs, newReleases_MPs)

def sendNewMPs(newMPs):
  for newMP in newMPs:
    [sendMPmail(newMP, x.user) for x in Follow.objects.filter(people = newMP.people)]
  log.info("Done sending emails about new announcements.")

def sendNewTrailers(movies):
  for newMPs in movies:
    for newMP in newMPs[0]:
      [sendTrailermail(newMP, x.user, newMPs[2]) for x in Follow.objects.filter(people = newMP.people)] # TODO: what if two followees in same movie
  log.info("Done sending emails about new trailers.")

def sendNewReleases(movies):
  for newMPs in movies:
    for newMP in newMPs[0]:
      [sendReleasemail(newMP, x.user, newMPs[2]) for x in Follow.objects.filter(people = newMP.people)] # TODO: what if two followees in same movie
  log.info("Done sending emails about new releases.")



def sendTrailermail(newMP, user, url):
  log.info("Sending email about " + newMP.__unicode__() + " trailer to " + user.__unicode__() + ".")
  print(user)
  subject = 'Whispers.io has news for you!'
  html_content = '<p>Hi,</p>'
  html_content += '<p>As a follower of ' + newMP.people.name + ", we thought you'd like to know that a new trailer for " + newMP.movie.name + " is available.</p>"
  html_content += '<p>You can find it at http://www.youtu.be/' + url + '</p>'
  html_content += '<p>Enjoy!</p>'
  html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
  msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@whispers.io>', [user.username])
  msg.attach_alternative(html_content, "text/html")
  log.info(msg.send())
  return 1


def sendReleasemail(newMP, user, day):
  log.info("Sending email about " + newMP.__unicode__() + " release to " + user.__unicode__() + ".")
  print(user)
  subject = 'Whispers.io has news for you!'
  html_content = '<p>Hi,</p>'
  html_content += '<p>As a follower of ' + newMP.people.name + ", we thought you'd like to know the release of " + newMP.movie.name + " is imminent!</p>"
  html_content += '<p>It will be out on ' + day.strftime('%Y-%m-%d') + ' in the US.</p>'
  html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
  msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@whispers.io>', [user.username])
  msg.attach_alternative(html_content, "text/html")
  log.info(msg.send())
  return 1


def sendMPmail(newMP, user):
  log.info("Sending email about " + newMP.__unicode__() + " to " + user.__unicode__() + ".")
  print(user)
  subject = 'Whispers.io has news for you!'
  html_content = '<p>Hi,</p>'
  html_content += '<p>As a follower of ' + newMP.people.name + ", we thought you'd like to know that he is going to star in a new movie, " + newMP.movie.name + ".</p>"
  html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
  msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@whispers.io>', [user.username])
  msg.attach_alternative(html_content, "text/html")
  log.info(msg.send())
  return 1

