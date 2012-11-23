from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

def boofun(request):
  from django.http import HttpResponse
  return HttpResponse('boo')

urlpatterns = patterns('',
    #web
    url(r'^$', 'moviepeopleapp.views.frontpage', name='home'),
    url(r'^login/([a-z]+)$', 'moviepeopleapp.views.createAccount'),

    #test
    url(r'^test/$', 'moviepeople.urls.boofun'),

    #admin
    url(r'^admin/', include(admin.site.urls)),

    #API
    url(r'^api/people/autocomplete$', 'moviepeopleapp.views.autocomplete'),
    url(r'^api/people/(\d+)/movies$', 'moviepeopleapp.views.people_movies'),
    url(r'^api/people/(\d+)/subscribe$', 'moviepeopleapp.views.people_subscribe'),
    url(r'^api/signup$', 'moviepeopleapp.views.signup'),
)
