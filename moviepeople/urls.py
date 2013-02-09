from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    #WEB - GUEST
    url(r'^$', 'moviepeopleapp.views.web.guest.frontpage', name='home'),
    url(r'^faq$', 'moviepeopleapp.views.web.guest.faq', name='webFAQ'),
    url(r'^login/([a-z]+)$', 'moviepeopleapp.views.web.guest.createAccount'),

    #WEB - USER

    #JS - GUEST
    url(r'^signin$', 'moviepeopleapp.views.js.guest.login'),
    url(r'^api/signup$', 'moviepeopleapp.views.js.guest.signup'),
    url(r'^api/forgot$', 'moviepeopleapp.views.js.guest.sendToken'),
    url(r'^api/people/autocomplete$', 'moviepeopleapp.views.js.guest.autocomplete'),
    url(r'^api/people/manualsearch$', 'moviepeopleapp.views.js.guest.manualsearch'),

    #JS - USER
    url(r'^logout$', 'moviepeopleapp.views.js.user.logoutview'),
    url(r'^api/people/(\d+)/movies$', 'moviepeopleapp.user.js.guest.people_movies'),
    url(r'^api/yourwhispers$', 'moviepeopleapp.views.js.user.yourwhispers'),
    url(r'^api/followees$', 'moviepeopleapp.views.js.user.followees'),
    url(r'^api/unfollow$', 'moviepeopleapp.views.js.user.unfollow'),
    url(r'^api/people/(\d+)/subscribe$', 'moviepeopleapp.views.js.user.people_subscribe'),


    #python admin
    url(r'^admin/', include(admin.site.urls)),

)

if settings.LOCAL == True:
   urlpatterns += patterns('',
       #DEV
       url(r'^loadsampledb/', 'moviepeopleapp.views.dev.load_sample_db')
    )
