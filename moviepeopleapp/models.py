import datetime
import django.contrib.auth.models
from django.db import models

class People(models.Model):
    name = models.CharField(max_length=200)
    tmdb_id = models.PositiveIntegerField(unique = True)
    profile = models.CharField(max_length=50)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class Movie(models.Model):
    name = models.CharField(max_length=200)
    poster = models.CharField(max_length=50)
    backdrop = models.CharField(max_length=50)
    tmdb_id = models.PositiveIntegerField(unique = True)
    imdb_id = models.CharField(max_length=50)
    revenue = models.PositiveIntegerField(null = True)
    homepage = models.CharField(max_length=200)
    popularity = models.FloatField(null = True)
    votes = models.PositiveIntegerField(null = True)
    vote_average = models.FloatField(null = True)
    runtime = models.PositiveIntegerField(null = True)
    date_created = models.DateTimeField(auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField(auto_now = True,default=datetime.datetime.now())
    adult = models.NullBooleanField()
    budget = models.PositiveIntegerField(null = True)

class MovieOverview(models.Model): # I make this a new table as I fear the size of this new, big, presumably infrequently-used field will affect performance of the smaller, more frequently used fields.
    movie =  models.OneToOneField(Movie)
    overview = models.TextField()
    tagline = models.TextField()
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())

class MoviePeople(models.Model):
    movie =  models.ForeignKey(Movie)
    people =  models.ForeignKey(People)
    role = models.CharField(max_length=50) # 'actor', 'director'
    character = models.CharField(max_length=100)
    cast_id = models.PositiveIntegerField(null = True)
    order = models.PositiveIntegerField(null = True)
    department = models.CharField(max_length=50)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())
    class Meta:
        unique_together = ('movie', 'people', 'role', 'character')

class Release(models.Model):
    movie = models.ForeignKey(Movie)
    date = models.DateField() #date without time of release
    country = models.CharField(max_length=3)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now() )
    last_updated = models.DateTimeField( auto_now = True ,default=datetime.datetime.now())
    class Meta:
        unique_together = ('movie', 'country', 'date')


class Trailer(models.Model):
    movie = models.ForeignKey(Movie)
    url = models.CharField(max_length=200)
    date = models.DateTimeField() #date without time on trailer diffusion
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())
    class Meta:
        unique_together = ('movie', 'url') 

class Follow(models.Model):
    user = models.ForeignKey(django.contrib.auth.models.User)
    people = models.ForeignKey(People)
    class Meta:
        unique_together = ('user', 'people')

class MovieGenre(models.Model):
    movie =  models.ForeignKey(Movie)
    genre = models.CharField(max_length=30)
    genre_tmdb_id = models.PositiveIntegerField()
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())
    class Meta:
        unique_together = ('movie', 'genre')

class MovieLanguage(models.Model):
    movie =  models.ForeignKey(Movie)
    language = models.CharField(max_length=10)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())
    class Meta:
        unique_together = ('movie', 'language')

class MovieCountry(models.Model): 
    movie =  models.ForeignKey(Movie)
    country = models.CharField(max_length=10)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())
    class Meta:
        unique_together = ('movie', 'country')

class MovieCompany(models.Model): 
    movie =  models.ForeignKey(Movie)
    company = models.CharField(max_length=100)
    company_tmdb_id = models.PositiveIntegerField(null=True)
    date_created = models.DateTimeField( auto_now_add = True,default=datetime.datetime.now())
    last_updated = models.DateTimeField( auto_now = True,default=datetime.datetime.now())
    class Meta:
        unique_together = ('movie', 'company')

