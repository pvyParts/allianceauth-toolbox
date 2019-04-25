from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'toolbox'

urlpatterns = [
    url(r'^notes/$', views.eve_note_board, name='eve_note_board'),
    url(r'^blacklist/$', views.blacklist, name='blacklist'),
    url(r'^search_name/$', views.search_name, name='search_name'),
    url(r'^add_note/(?P<eve_id>(\d)*)/$', views.add_note, name='add_note'),
    url(r'^edit_note/(?P<note_id>(\d)*)/$', views.edit_note, name='edit_note'),
    url(r'^add_comment/(?P<note_id>(\d)*)/$', views.add_comment, name='add_comment')
]
