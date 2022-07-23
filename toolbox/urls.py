from django.urls import re_path

from . import views

app_name = 'toolbox'

urlpatterns = [
    re_path(r'^set/$', views.toolbox_set_search_character, name='set'),
    re_path(r'^notes/$', views.eve_note_board, name='eve_note_board'),
    re_path(r'^blacklist/$', views.blacklist, name='blacklist'),
    re_path(r'^search_name/$', views.search_name, name='search_name'),
    re_path(r'^add_note/(?P<eve_id>(\d)*)/$', views.add_note, name='add_note'),
    re_path(r'^get_add_note/(?P<eve_id>(\d)*)/$', views.get_add_evenote, name='modal_add'),
    re_path(r'^get_comments/(?P<evenote_id>(\d)*)/$', views.get_evenote_comments, name='modal_comment'),
    re_path(r'^get_edit_note/(?P<evenote_id>(\d)*)/$', views.get_edit_evenote, name='modal_edit'),
    re_path(r'^get_add_comment/(?P<evenote_id>(\d)*)/$', views.get_add_comment, name='modal_add_comment'),
    re_path(r'^search_names/$', views.search_names, name='search_names'),
    re_path(r'^edit_note/(?P<note_id>(\d)*)/$', views.edit_note, name='edit_note'),
    re_path(r'^add_comment/(?P<note_id>(\d)*)/$', views.add_comment, name='add_comment'),
    re_path(r'^mining/(?P<character_id>(\d)*)/$', views.view_character_mining, name='view_character_mining'),
    re_path(r'^mining/$', views.view_character_mining, name='view_character_mining'),
    re_path(r'^mining/admin/$', views.admin_character_mining, name='admin_character_mining'),
]
