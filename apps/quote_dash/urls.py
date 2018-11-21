from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index), 
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^dashboard$', views.dashboard),
    url(r'^logout$', views.logout),
    url(r'^myaccount/(?P<user_id>\d+)$', views.editacc), 
    url(r'^replace$', views.replace), 
    url(r'^user/(?P<user_id>\d+)$', views.user_quotes), 
    url(r'^add_quote$', views.add_quote),
    url(r'^liked/(?P<quote_id>\d+)/(?P<user_id>\d+)$', views.liked_quote), 
    url(r'^deletequote/(?P<quote_id>\d+)$', views.delete_quote), 
]
