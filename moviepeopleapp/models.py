import datetime
from django.db import models

class User(models.Model):
    email = models.CharField(max_length=200)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class People(models.Model):
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class Movie(models.Model):
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class MoviePeople(models.Model):
    movie =  models.ForeignKey(Movie)
    people =  models.ForeignKey(People)
    role = models.CharField(max_length=200) # 'actor', 'director'
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class Release(models.Model):
    movie = models.ForeignKey(Movie)
    date = models.DateField() #date without time of release
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now() )
    last_updated = models.DateTimeField( auto_now = True ,default=datetime.datetime.now())

class Trailer(models.Model):
    movie = models.ForeignKey(Movie)
    url = models.CharField(max_length=200)
    date = models.DateTimeField() #date without time on trailer diffusion
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class Follow(models.Model):
    user = models.ForeignKey(User)
    people = models.ForeignKey(People)

class Poster(models.Model):
    movie = models.ForeignKey(Movie)
    url = models.CharField(max_length=200)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class Backdrop(models.Model):
    movie = models.ForeignKey(Movie)
    url = models.CharField(max_length=200)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())




