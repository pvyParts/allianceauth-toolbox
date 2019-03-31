from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from esi.clients import esi_client_factory

from .models import EveNote, EveNoteComment
from .forms import EditNote, SearchEveName, AddEveNote, AddComment, AddRestrictedComment

import logging

# Create your views here... *don't tell me what to do....*


@login_required
@permission_required('toolbox.view_eve_notes')
def eve_note_board(request):
    eve_notes = EveNote.objects.all().prefetch_related('comment')
    blacklist = EveNote.objects.filter(blacklisted=True).prefetch_related('comment')
    context = {
        'add_note': request.user.has_perm('toolbox.add_new_eve_notes'),
        'edit_note': request.user.has_perm('toolbox.add_new_eve_notes'),
        'add_comment': request.user.has_perm('toolbox.add_new_eve_note_comments'),
        'add_restricted_comment': request.user.has_perm('toolbox.add_new_eve_note_restricted_comments'),
        'view_comment': request.user.has_perm('toolbox.view_eve_note_comments'),
        'view_restricted_comment': request.user.has_perm('toolbox.view_eve_note_restricted_comments'),
        'notes': eve_notes,
        'blacklist': blacklist,
    }

    return render(request, 'toolbox/evenotes.html', context=context)


@login_required
@permission_required('toolbox.view_eve_blacklist')
def blacklist(request):
    blacklist = EveNote.objects.filter(blacklisted=True)
    context = {
        'blacklist': blacklist,
    }

    return render(request, 'toolbox/blacklist.html', context=context)


@login_required
@permission_required('toolbox.add_new_eve_notes')
def search_name(request):
    if request.method == 'POST':
        form = SearchEveName(request.POST)

        # check whether it's valid:
        if form.is_valid():
            name = form.cleaned_data['name']
            c = esi_client_factory()
            hits = c.Search.get_search(search=name, categories=['character', 'corporation', 'alliance']).result()
            corps = hits.get('corporation', [])
            chars = hits.get('character', [])
            alliance = hits.get('alliance', [])
            names_list = []
            if corps:
                names_list += corps
            if chars:
                names_list += chars
            if alliance:
                names_list += alliance
            names = c.Universe.post_universe_names(ids=names_list).result()
            return render(request, 'toolbox/search_name.html', {'form': form, 'names': names})
    else:
        form = SearchEveName()
        return render(request, 'toolbox/search_name.html', {'form': form})

@login_required
@permission_required('toolbox.add_new_eve_notes')
def add_note(request, eve_id=None):
    if eve_id:
        if request.method == 'POST':
            form = AddEveNote(request.POST)

            # check whether it's valid:
            if form.is_valid():
                EveNote.objects.create(eve_name=request.POST.get('eve_name'),
                                       eve_catagory=request.POST.get('eve_cat'),
                                       blacklisted=form.cleaned_data['blacklisted'],
                                       reason=form.cleaned_data['reason'],
                                       added_by=request.user.profile.main_character.character_name,
                                       eve_id=eve_id)
                return redirect('toolbox:eve_note_board')
        else:
            c = esi_client_factory()
            name = c.Universe.post_universe_names(ids=[eve_id]).result()[0]
            form = AddEveNote()
            return render(request, 'toolbox/add_note.html', {'form':form, 'name': name})
    else:
        return render(request, 'toolbox/evenotes.html')


@login_required
@permission_required('toolbox.add_new_eve_notes')
def edit_note(request, note_id=None):
    if request.method == 'POST':
        form = EditNote(request.POST)

        # check whether it's valid:
        if form.is_valid():
            jb = EveNote.objects.get(id=request.POST.get('note_id'))
            jb.reason = form.cleaned_data['reason']
            jb.blacklisted = form.cleaned_data['blacklisted']
            jb.save()
            messages.info(request, "Edit Successful")
            return redirect('toolbox:eve_note_board')
    else:
        note = EveNote.objects.get(pk=note_id)
        form = EditNote(initial={'reason': note.reason,
                                 'blacklisted': note.blacklisted})
        return render(request, 'toolbox/edit_note.html', {'form': form, 'note': note})


@login_required
@permission_required('toolbox.add_new_eve_note_comments')
def add_comment(request, note_id=None):
    if request.method == 'POST':
        form = AddComment(request.POST)

        # check whether it's valid:
        if form.is_valid():
            EveNoteComment.objects.create(added_by=request.user.profile.main_character.character_name,
                                          eve_note_id=note_id,
                                          comment=form.cleaned_data['comment'],
                                          restricted=False)
            messages.info(request, "Comment Added")
            return redirect('toolbox:eve_note_board')
    else:
        form = AddComment()
        note = EveNote.objects.get(pk=note_id)
        return render(request, 'toolbox/add_comment.html', {'form': form, 'note': note})


@login_required
@permission_required('toolbox.add_new_eve_note_restricted_comments')
def add_restricted_comment(request, note_id=None):
    if request.method == 'POST':
        form = AddRestrictedComment(request.POST)

        # check whether it's valid:
        if form.is_valid():
            EveNoteComment.objects.create(added_by=request.user.profile.main_character.character_name,
                                          eve_note_id=note_id,
                                          comment=form.cleaned_data['comment'],
                                          restricted=True)
            messages.info(request, "Comment Added")
            return redirect('toolbox:eve_note_board')
    else:
        form = AddRestrictedComment()
        note = EveNote.objects.get(pk=note_id)
        return render(request, 'toolbox/add_restricted_comment.html', {'form': form, 'note': note})
