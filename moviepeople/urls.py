from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    #WEB - GUEST
    url(r'^$',                              'moviepeopleapp.views.web.guest.frontpage', name='front'),
    url(r'^faq$',                           'moviepeopleapp.views.web.guest.faq', name='webFAQ'),
    url(r'^login/([a-z]+)$',                'moviepeopleapp.views.web.guest.createAccount'),

    #WEB - USER
    url(r'^home$',                          'moviepeopleapp.views.web.user.homepage', name='home'),
    url(r'^find',                           'moviepeopleapp.views.web.user.find_artists', name='find'),
    url(r'^follows',                        'moviepeopleapp.views.web.user.follows', name='follows'),

    #JS - GUEST
    url(r'^api/people/frontFollow',         'moviepeopleapp.views.js.guest.frontpageFollow'),
    url(r'^signin$',                        'moviepeopleapp.views.js.guest.loginAjax'),
    url(r'^api/signup$',                    'moviepeopleapp.views.js.guest.signup'),
    url(r'^api/forgot$',                    'moviepeopleapp.views.js.guest.sendToken'),
    url(r'^api/people/autocomplete$',       'moviepeopleapp.views.js.guest.autocomplete'),
    url(r'^api/people/manualsearch$',       'moviepeopleapp.views.js.guest.manualsearch'),
    url(r'^api/people/(\d+)/movies$',       'moviepeopleapp.views.js.guest.people_movies'),

    #JS - USER
    url(r'^logout$',                        'moviepeopleapp.views.js.user.logoutview'),
    url(r'^api/yourwhispers$',              'moviepeopleapp.views.js.user.yourwhispers'),
    url(r'^api/followees$',                 'moviepeopleapp.views.js.user.followees'),
    url(r'^api/unfollow$',                  'moviepeopleapp.views.js.user.unfollow'),
    url(r'^api/people/(\d+)/subscribe$',    'moviepeopleapp.views.js.user.people_subscribe'),


    #python admin
    url(r'^admin/', include(admin.site.urls)),

)

if settings.LOCAL == True:
   urlpatterns += patterns('',
       #DEV
       url(r'^loadsampledb/',               'moviepeopleapp.views.dev.load_sample_db')
    )
