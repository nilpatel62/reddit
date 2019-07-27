from django.conf.urls import url
from RedditApp import views


app_name = 'RedditApp'


urlpatterns = [
    url(r'^$', views.dashboard, name='initialize'),
    url(r'^setting/$', views.settingpage, name='settingpage'),
    url(r'^reddit/$', views.scrapped_data, name='scrapped_data'),
    url(r'^addsetting/$', views.addsetting, name='addsetting'),
    url(r'^sendemail/$', views.sendemail.as_view(), name='sendemail'),
    url(r'^messagedata/$', views.messagedata.as_view(), name='messagedata'),
    url(r'^sendmessage/(?P<type>[\w\-]+)$', views.sendmessage, name='sendmessage'),
    url(r'^message/$', views.SendDMUser.as_view(), name='SendDMUser'),
    url(r'^delete/(?P<status>[\w\s,-]+)$', views.DeleteUser.as_view(), name='DeleteUser'),
    url(r'^deletereddit/(?P<status>[\w\s,-]+)$', views.deletereddit.as_view(), name='deletereddit'),
]