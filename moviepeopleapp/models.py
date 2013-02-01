import datetime
import django.contrib.auth.models
from django.db import models

class People(models.Model):
  name = models.CharField(max_length=200)
  tmdb_id = models.PositiveIntegerField(unique=True)
  profile = models.CharField(max_length=50)
  date_created = models.DateTimeField(auto_now_add=True, 
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True, 
                                      default=datetime.datetime.now())
  importance = models.IntegerField(null=True)

  def __unicode__(self):
    return self.name


class Movie(models.Model):
  name = models.CharField(max_length=200)
  poster = models.CharField(max_length=50)
  backdrop = models.CharField(max_length=50)
  tmdb_id = models.PositiveIntegerField(unique=True)
  imdb_id = models.CharField(max_length=50)
  revenue = models.FloatField(null=True)
  homepage = models.CharField(max_length=200)
  popularity = models.FloatField(null=True)
  RT_id = models.PositiveIntegerField(null=True)
  RT_link = models.CharField(null=True, max_length=200)
  RT_critics_score = models.FloatField(null=True)
  RT_audience_score = models.FloatField(null=True)
  RT_critics_rating = models.CharField(max_length=50, null=True)
  RT_audience_rating = models.CharField(max_length=50, null=True)
  votes = models.PositiveIntegerField(null=True)
  vote_average = models.FloatField(null=True)
  runtime = models.PositiveIntegerField(null=True)
  date_info = models.DateField(null=True)
  date_created = models.DateTimeField(auto_now_add=True, 
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True, 
                                      default=datetime.datetime.now())
  adult = models.NullBooleanField()
  budget = models.FloatField(null = True)

  def __unicode__(self):
    return self.name


class MovieOverview(models.Model): 
  # I make this a new table as I fear the size of this new, big, 
  # presumably infrequently-used field will affect performance 
  # of the smaller, more frequently used fields.
  movie =  models.OneToOneField(Movie)
  overview = models.TextField()
  tagline = models.TextField()
  date_created = models.DateTimeField(auto_now_add=True, 
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True, 
                                      default=datetime.datetime.now())

class MoviePeople(models.Model):
  movie =  models.ForeignKey(Movie)
  people =  models.ForeignKey(People)
  role = models.CharField(max_length=50) # 'actor', 'director'
  character = models.CharField(max_length=100)
  cast_id = models.PositiveIntegerField(null = True)
  order = models.PositiveIntegerField(null = True)
  department = models.CharField(max_length=50)
  date_info = models.DateField(null = True)
  date_created = models.DateTimeField(auto_now_add=True, 
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True, 
                                      default=datetime.datetime.now())

  class Meta:
    unique_together = ('movie', 'people', 'role', 'character')

  def __unicode__(self):
    return self.movie.name + ", " + self.people.name


class Release(models.Model):
  movie = models.ForeignKey(Movie)
  date = models.DateField() #date without time of release
  date_info = models.DateField(null = True)
  country = models.CharField(max_length=3)
  date_created = models.DateTimeField(auto_now_add=True,
                                      default=datetime.datetime.now() )
  last_updated = models.DateTimeField(auto_now=True,
                                      default=datetime.datetime.now())

  class Meta:
    unique_together = ('movie', 'country', 'date')


class Trailer(models.Model):
  movie = models.ForeignKey(Movie)
  url = models.CharField(max_length=200)
  format = models.CharField(max_length=20)
  name = models.CharField(max_length=200)
  size = models.CharField(max_length=10)
  date_info = models.DateField(null=True) #date without time on trailer diffusion
  date_created = models.DateTimeField(auto_now_add=True,
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True,
                                      default=datetime.datetime.now())

  class Meta:
    unique_together = ('movie', 'url') 


class Follow(models.Model):
  user = models.ForeignKey(django.contrib.auth.models.User)
  people = models.ForeignKey(People)

  class Meta:
    unique_together = ('user', 'people')

  def __unicode__(self):
    return self.user.username + ',' + self.people.name


class MovieGenre(models.Model):
  movie =  models.ForeignKey(Movie)
  genre = models.CharField(max_length=30)
  genre_tmdb_id = models.PositiveIntegerField()
  date_created = models.DateTimeField(auto_now_add=True,
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True,
                                      default=datetime.datetime.now())

  class Meta:
    unique_together = ('movie', 'genre')


class CreateAccountToken(models.Model):
  code = models.CharField(max_length=32)
  email = models.CharField(max_length=1023, unique=True)
  date_created = models.DateTimeField(auto_now_add=True,
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True, 
                                      default=datetime.datetime.now())


class MovieLanguage(models.Model):
  movie =  models.ForeignKey(Movie)
  language = models.CharField(max_length=10)
  date_created = models.DateTimeField(auto_now_add=True,
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True, 
                                      default=datetime.datetime.now())

  class Meta:
    unique_together = ('movie', 'language')


class MovieCountry(models.Model): 
  movie =  models.ForeignKey(Movie)
  country = models.CharField(max_length=10)
  date_created = models.DateTimeField(auto_now_add=True, 
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True,
                                      default=datetime.datetime.now())

  class Meta:
    unique_together = ('movie', 'country')


class MovieCompany(models.Model): 
  movie =  models.ForeignKey(Movie)
  company = models.CharField(max_length=200)
  company_tmdb_id = models.PositiveIntegerField(null=True)
  date_created = models.DateTimeField(auto_now_add=True,
                                      default=datetime.datetime.now())
  last_updated = models.DateTimeField(auto_now=True,
                                      default=datetime.datetime.now())

  class Meta:
    unique_together = ('movie', 'company')

