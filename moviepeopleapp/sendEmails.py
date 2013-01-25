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
  log.info("Sending email about " + newMP.unicode() + " to " + user.unicode() + ".")
    json = simplejson.loads(request.GET.get('JSON'))
      subject = 'Welcome to Whispers!'
      html_content = '<p>Hi, thanks for joining whispers,</p>'
      html_content += '<p>Set up a password for accessing your account whenever you like by following this link:<br/>'
      html_content += '<p><a href="'+link+'">'+link+'</a></p>'
      html_content += '<p></p><p>Thanks,<br/>Whispers team</p>'
    msg = EmailMultiAlternatives(subject, html_content, 'Whispers <whispers.updates@whispers.io>', [user.name])
    msg.attach_alternative(html_content, "text/html")
    log.info(msg.send())

    return HttpResponse(simplejson.dumps({"already_exists":True}), mimetype="application/json")

