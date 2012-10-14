from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     url(r'^$', 'moviepeopleapp.views.frontpage', name='home'),

    url(r'^api/people/autocomplete$', 'moviepeopleapp.views.autocomplete'),
    url(r'^api/people/(\d+)/movies$', 'moviepeopleapp.views.people_movies'),
    url(r'^api/people/(\d+)/subscribe$', 'moviepeopleapp.views.people_subscribe')
    # url(r'^moviepeople/', include('moviepeople.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
