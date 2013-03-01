from moviepeopleapp.models import MoviePeople, Follow
from django.contrib import admin
import django.contrib.auth

from django.template import RequestContext
from django.conf.urls.defaults import patterns, url, include
from django.shortcuts import render_to_response

from django.http import HttpResponse



def some_view(request):
		entry = 'boo'
		#return HttpResponse('Hey!')
		#return render_to_response(review_template, {'as'
		#		}, context_instance=RequestContext(request))


class MyAdminSite(admin.AdminSite):
	#review_template = 'admin/my_test/myentry/review.html'

	def get_urls(self):
		from django.conf.urls import patterns, url

		urls = patterns('myadmin/',
			url(r'^my_view/$', self.admin_view(some_view), name='someview')
			)
		urls += super(MyAdminSite, self).get_urls()
		return urls

#	def get_urls(self):
#		my_urls = patterns('',
#				(r'^$', self.admin_view(self.app_index)),
#				(r'\d+/review/$', self.admin_view(self.review)),
#				)
#		return my_urls

MyAdmin = MyAdminSite()
print(MyAdmin.urls)
print(patterns('', url(r'^myadmin/', include(MyAdmin.urls))))

#
#class MyEntryAdmin(admin.ModelAdmin):
#	review_template = 'admin/my_test/myentry/review.html'
#
#	def get_urls(self):
#		urls = super(MyEntryAdmin, self).get_urls()
#		my_urls = patterns('',
#				(r'\d+/review/$', self.admin_site.admin_view(self.review)),
#				)
#		return my_urls + urls
#
#	def review(self, request, id):
#		entry = 'boo'
#		return render_to_response(self.review_template, {'as'
#				}, context_instance=RequestContext(request))
#

admin.site.register(MoviePeople)
admin.site.register(Follow)
MyAdmin.register(Reminder)
#admin.site.register(Follow, admin_class=MyEntryAdmin)




