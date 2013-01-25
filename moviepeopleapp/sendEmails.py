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
  sendNewMPs(newMPs, day)
  #sendNewTrailers(newTrailers)
  #sendNewReleases(newReleases)

def sendNewMPs(newMPs):
  for newMP in newMPs:
    [sendMPmail(newMP, x.user) for x in Follow.objects.filter(people = newMP.people)]
  log.info("Done sending emails about new announcements.")
    


def checkNewStuff(day):

def sendMPmail(newMP, user):
  log.info("Sending email about " + newMP.__unicode__() + " to " + user.__unicode__() + ".")
  subject = 'Whispers.io has news for you!'
  html_content = '<p>Hi,</p>'
  html_content += '<p>As a follower of ' + newMP.people.name + " we thought you'd like to know that he is going to star in a new movie, " + newMP.movie.name + ".</p>"
  html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
  msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@whispers.io>', [user.username])
  msg.attach_alternative(html_content, "text/html")
  log.info(msg.send())
  return 1

