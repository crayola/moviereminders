from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #web
    url(r'^$', 'moviepeopleapp.views.frontpage', name='home'),

    #auth
    url(r'^login/([a-z]+)$', 'moviepeopleapp.views.createAccount'),
    url(r'^thanks/([a-z]+)$', 'moviepeopleapp.views.accountCreated'),
    url(r'^signin$', 'moviepeopleapp.views.signin'),
    url(r'^logout$', 'moviepeopleapp.views.logoutview'),

    #admin
    url(r'^admin/', include(admin.site.urls)),

    #API
    url(r'^api/people/autocomplete$', 'moviepeopleapp.views.autocomplete'),
    url(r'^api/people/manualsearch$', 'moviepeopleapp.views.manualsearch'),
    url(r'^api/people/(\d+)/movies$', 'moviepeopleapp.views.people_movies'),
    url(r'^api/yourwhispers$', 'moviepeopleapp.views.yourwhispers'),
    url(r'^api/followees$', 'moviepeopleapp.views.followees'),
    url(r'^api/unfollow$', 'moviepeopleapp.views.unfollow'),
    url(r'^api/people/(\d+)/subscribe$', 'moviepeopleapp.views.people_subscribe'),
    url(r'^api/signup$', 'moviepeopleapp.views.signup'),
    url(r'^api/forgot$', 'moviepeopleapp.views.sendToken')
)

if settings.LOCAL == True:
   urlpatterns += patterns('',
                           #local
                           url(r'^loadsampledb/', 'moviepeopleapp.views.load_sample_db')
                          )
