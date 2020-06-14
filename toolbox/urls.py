from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'toolbox'

urlpatterns = [
    url(r'^notes/$', views.eve_note_board, name='eve_note_board'),
    url(r'^blacklist/$', views.blacklist, name='blacklist'),
    url(r'^search_name/$', views.search_name, name='search_name'),
    url(r'^add_note/(?P<eve_id>(\d)*)/$', views.add_note, name='add_note'),
    url(r'^get_add_note/(?P<eve_id>(\d)*)/$', views.get_add_evenote, name='modal_add'),
    url(r'^get_comments/(?P<evenote_id>(\d)*)/$', views.get_evenote_comments, name='modal_comment'),
    url(r'^get_edit_note/(?P<evenote_id>(\d)*)/$', views.get_edit_evenote, name='modal_edit'),
    url(r'^get_add_comment/(?P<evenote_id>(\d)*)/$', views.get_add_comment, name='modal_add_comment'),
    url(r'^search_names/$', views.search_names, name='search_names'),
    url(r'^edit_note/(?P<note_id>(\d)*)/$', views.edit_note, name='edit_note'),
    url(r'^add_comment/(?P<note_id>(\d)*)/$', views.add_comment, name='add_comment'),

    url(r'^mining/(?P<character_id>(\d)*)/$', views.view_character_mining, name='view_character_mining'),
    url(r'^mining/$', views.view_character_mining, name='view_character_mining'),
    url(r'^mining/admin/$', views.admin_character_mining, name='admin_character_mining'),
]
