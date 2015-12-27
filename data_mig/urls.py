from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'data_mig.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',  'signups.views.login'),
    url(r'^accounts/login/$',  'signups.views.login'),
    url(r'^accounts/auth/$',  'signups.views.auth_view'),    
    url(r'^accounts/logout/$', 'signups.views.logout'),
    url(r'^accounts/loggedin/$', 'signups.views.loggedin'),
    url(r'^accounts/invalid/$', 'signups.views.invalid_login'),    
    url(r'^accounts/register/$', 'signups.views.register_user'),
    url(r'^accounts/register_success/$', 'signups.views.register_success'),
    url(r'^convert/done/$', 'signups.views.convert'),
    url(r'^get_tables/$', 'signups.views.get_tables'),
    url(r'^schema/$', 'signups.views.get_schema'),
    url(r'^get_data/$', 'signups.views.get_data'),
    url(r'^tconvert/$', 'signups.views.tconvert'),
    url(r'^send_zipfile/$', 'signups.views.send_zipfile'),
)

