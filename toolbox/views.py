from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from esi.clients import esi_client_factory
from esi.decorators import token_required
from esi.models import Token

from .models import EveNote, EveNoteComment, CharacterMining, CharacterMiningObservation, ApiKey, ApiKeyLog, CharacterPayment, ToolboxSearchCharacter
from .forms import SearchEveName, EveNoteForm, AddComment
import json
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import FloatField, F, ExpressionWrapper
from django.db.models import Subquery, OuterRef
from django.utils.dateparse import parse_datetime
from django.template.loader import render_to_string
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.timerboard.models import Timer

import logging
import datetime
from django.utils import timezone
from django.db.models.functions import Coalesce
logger = logging.getLogger(__name__)
from . import providers

# Create your views here... *don't tell me what to do...*

@login_required
@permission_required(['toolbox.add_basic_eve_notes', 'toolbox.add_new_eve_notes'])
@token_required(['esi-search.search_structures.v1'])
def toolbox_set_search_character(request, token):
    if token:
        char = EveCharacter.objects.get(character_id=token.character_id)
        char, _ = ToolboxSearchCharacter.objects.update_or_create(
            user=request.user,
            defaults={
                "character": char
            }
        )
        messages.success(request, ("Linked Search Character: {}".format(token.character_name)))
    return redirect("toolbox:eve_note_board")


def get_search_char(user):
    try:
        char = ToolboxSearchCharacter.objects.get(user=user)
        return char.character
    except ToolboxSearchCharacter.DoesNotExist:
        return False


@login_required
def eve_note_board(request):
    add_perms = request.user.has_perm('toolbox.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('toolbox.add_new_eve_notes')
    view_perms = request.user.has_perm('toolbox.view_basic_eve_notes')
    view_global_perms = request.user.has_perm('toolbox.view_eve_notes')

    if not (view_perms or view_global_perms):
        messages.error(request, "No Permissions")
        return redirect('authentication:dashboard')

    restricted = request.user.has_perm('toolbox.add_restricted_eve_notes')
    ultra_restricted = request.user.has_perm('toolbox.add_ultra_restricted_eve_notes')

    eve_notes = None

    if view_global_perms or add_global_perms:
        eve_notes = EveNote.objects.filter(restricted=False,
                                           ultra_restricted=False).prefetch_related('comment')
        #  Restricted view
        if restricted:
            if eve_notes:
                eve_notes = eve_notes | EveNote.objects.filter(restricted=True).prefetch_related('comment')
            else:
                eve_notes = EveNote.objects.filter(restricted=True).prefetch_related('comment')

        #  Ultra Restricted view
        if ultra_restricted:
            if eve_notes:
                eve_notes = eve_notes | EveNote.objects.filter(ultra_restricted=True).prefetch_related('comment')
            else:
                eve_notes = EveNote.objects.filter(ultra_restricted=True).prefetch_related('comment')

    else:
        #  Basic Level
        eve_notes = EveNote.objects.filter(corporation_id=request.user.profile.main_character.corporation_id,
                                           restricted=False,
                                           ultra_restricted=False).prefetch_related('comment')

    context = {
        'add_note': (add_perms or add_global_perms),
        'view_restricted_note': request.user.has_perm('toolbox.view_restricted_eve_notes'),
        'view_ultra_restricted_note': request.user.has_perm('toolbox.view_ultra_restricted_eve_notes'),
        'add_blacklist': request.user.has_perm('toolbox.add_to_blacklist'),
        'edit_note': request.user.has_perm('toolbox.add_new_eve_notes'),
        'add_comment': request.user.has_perm('toolbox.add_new_eve_note_comments'),
        'add_restricted_comment': request.user.has_perm('toolbox.add_new_eve_note_restricted_comments'),
        'add_ultra_restricted_comment': request.user.has_perm('toolbox.add_new_eve_note_ultra_restricted_comments'),
        'view_comment': request.user.has_perm('toolbox.view_eve_note_comments'),
        'view_restricted_comment': request.user.has_perm('toolbox.view_eve_note_restricted_comments'),
        'view_ultra_restricted_comment': request.user.has_perm('toolbox.view_eve_note_ultra_restricted_comments'),
        "search_char": get_search_char(request.user),
        'notes': eve_notes
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
def search_name(request):
    add_perms = request.user.has_perm('toolbox.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('toolbox.add_new_eve_notes')

    if not (add_perms or add_global_perms):
        messages.info(request, "No Permissions")
        return redirect('toolbox:eve_note_board')

    if request.method == 'POST':
        form = SearchEveName(request.POST)

        # check whether it's valid:
        if form.is_valid():
            name = form.cleaned_data['name']
            try:
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
            except:
                messages.error(request,
                               "ESI Error. Please Try again later.")
                return redirect('toolbox:eve_note_board')

            context = {'form': form,
                       'names': names,
                       'restricted_perms': add_global_perms
                       }
            return render(request, 'toolbox/search_name.html', context)
    else:
        form = SearchEveName()
        return render(request, 'toolbox/search_name.html', {'form': form})

@login_required
def add_note(request, eve_id=None):
    add_perms = request.user.has_perm('toolbox.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('toolbox.add_new_eve_notes')

    if not (add_perms or add_global_perms):
        messages.info(request, "No Permissions")
        return redirect('toolbox:eve_note_board')

    if eve_id:
        if request.method == 'POST':
            form = EveNoteForm(request.POST)

            # check whether it's valid:
            if form.is_valid():
                restricted = form.cleaned_data['restricted']
                ultra_restricted = form.cleaned_data['ultra_restricted']

                if ultra_restricted:
                    restricted = False
                blacklisted = form.cleaned_data['blacklisted']

                if restricted or ultra_restricted:
                    blacklisted = False

                EveNote.objects.create(eve_name=request.POST.get('eve_name'),
                                       eve_catagory=request.POST.get('eve_cat'),
                                       alliance_id=request.POST.get('alliance_id', None),
                                       alliance_name=request.POST.get('alliance_name', None),
                                       corporation_id=request.POST.get('corporation_id', None),
                                       corporation_name=request.POST.get('corporation_name', None),
                                       blacklisted=blacklisted,
                                       restricted=restricted,
                                       ultra_restricted=ultra_restricted,
                                       reason=form.cleaned_data['reason'],
                                       added_by=request.user.profile.main_character.character_name,
                                       eve_id=eve_id)

                return redirect('toolbox:eve_note_board')
    return redirect('toolbox:eve_note_board')

@login_required
@permission_required('toolbox.add_new_eve_notes')
def edit_note(request, note_id=None):
    if request.method == 'POST':
        form = EveNoteForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            restricted = form.cleaned_data['restricted']
            ultra_restricted = form.cleaned_data['ultra_restricted']
            if ultra_restricted:
                restricted = False
            blacklisted = form.cleaned_data['blacklisted']
            if restricted or ultra_restricted:
                blacklisted = False
            jb = EveNote.objects.get(id=request.POST.get('note_id'))
            jb.reason = form.cleaned_data['reason']
            jb.blacklisted = blacklisted
            jb.restricted = restricted
            jb.ultra_restricted = ultra_restricted
            jb.save()
            messages.info(request, "Edit Successful")
            return redirect('toolbox:eve_note_board')
    else:
        note = EveNote.objects.get(pk=note_id)
        form = EveNoteForm(initial={'reason': note.reason,
                                    'blacklisted': note.blacklisted,
                                    'restricted': note.restricted,
                                    'ultra_restricted': note.ultra_restricted})
        context = {'form': form,
                   'note': note,
                   'add_blacklist': request.user.has_perm('toolbox.add_to_blacklist'),
                   'add_restricted_note': request.user.has_perm('toolbox.add_restricted_eve_notes'),
                   'add_ultra_restricted_note': request.user.has_perm('toolbox.add_ultra_restricted_eve_notes')}

        return render(request, 'toolbox/edit_note.html', context)


@login_required
@permission_required('toolbox.add_new_eve_note_comments')
def add_comment(request, note_id=None):
    if request.method == 'POST':
        form = AddComment(request.POST)

        # check whether it's valid:
        if form.is_valid():
            restricted = form.cleaned_data['restricted']
            ultra_restricted = form.cleaned_data['ultra_restricted']
            if ultra_restricted:
                restricted = False

            EveNoteComment.objects.create(added_by=request.user.profile.main_character.character_name,
                                          eve_note_id=note_id,
                                          comment=form.cleaned_data['comment'],
                                          restricted=restricted,
                                          ultra_restricted=ultra_restricted)
            messages.info(request, "Comment Added")
            return redirect('toolbox:eve_note_board')
    else:
        form = AddComment()
        note = EveNote.objects.get(pk=note_id)
        context = {'form': form,
                   'note': note,
                   'add_restricted': request.user.has_perm('toolbox.add_new_eve_note_restricted_comments'),
                   'add_ultra_restricted': request.user.has_perm('toolbox.add_new_eve_note_ultra_restricted_comments')}

        return render(request, 'toolbox/add_comment.html', context)


@csrf_exempt
def input_moon_api(request):
    try:
        if request.method == "POST":
            api_tokens = list(ApiKey.objects.all().values_list('api_hash', flat=True))
            if request.META['HTTP_X_API_TOKEN'] in api_tokens:
                log = ApiKeyLog()
                log.apikey = ApiKey.objects.get(api_hash = request.META['HTTP_X_API_TOKEN'])
                data = request.body.decode('utf-8')
                log.json = "%s" % (data,)
                log.save()

                received_json_data = json.loads(data)
                month = received_json_data['month']
                year = received_json_data['year']

                for player, details in received_json_data['player_data'].items():
                    character_ob, created = CharacterMining.objects.update_or_create(
                                                character_id = details['char_id'],
                                                character_name = player,
                                                month = month,
                                                year = year,
                                                defaults = {
                                                    'isk_total': details['totals_isk'],
                                                    'tax_total': details['tax_isk']
                                                    }
                                            )

                    if not created: #purge data from whats been mined for this char
                        CharacterMiningObservation.objects.filter(character=character_ob).delete()
                    ore_obs = []
                    for ore, ore_details in details['ores'].items(): # add it all back in.
                        ore_obs.append(CharacterMiningObservation(
                                        character = character_ob,
                                        ore_name = ore,
                                        ore_type = ore_details['type_id'],
                                        count = ore_details['count'],
                                        value = ore_details['value']
                                        )
                                    )
                    CharacterMiningObservation.objects.bulk_create(ore_obs)
                return HttpResponse('OK')
            else:
                raise Http404
        else:
            raise Http404
    except:
        logging.exception("Messsage")
        raise Http404


@csrf_exempt
def input_timer_api(request):
    try:
        if request.method == "POST":
            api_tokens = list(ApiKey.objects.all().values_list('api_hash', flat=True))
            if request.META['HTTP_X_API_TOKEN'] in api_tokens:
                log = ApiKeyLog()
                log.apikey = ApiKey.objects.get(api_hash = request.META['HTTP_X_API_TOKEN'])
                data = request.body.decode('utf-8')
                log.json = "%s" % (data,)
                log.save()

                received_json_data = json.loads(data)

                Timer.objects.create(
                    details=received_json_data.get("details", ""),
                    system=received_json_data.get("system", ""),
                    planet_moon=received_json_data.get("planet_moon", ""),
                    structure=received_json_data.get("structure", ""),
                    objective="Friendly",
                    eve_time=parse_datetime(received_json_data.get("eve_time")),
                    eve_corp=EveCorporationInfo.objects.get(corporation_id=1639878825)
                )

                return HttpResponse('OK')
            else:
                raise Http404
        else:
            raise Http404
    except:
        logging.exception("Messsage")
        raise Http404


@csrf_exempt
def input_wallet_api(request):
    try:
        if request.method == "POST":
            api_tokens = list(ApiKey.objects.all().values_list('api_hash', flat=True))
            if request.META['HTTP_X_API_TOKEN'] in api_tokens:
                log = ApiKeyLog()
                log.apikey = ApiKey.objects.get(api_hash = request.META['HTTP_X_API_TOKEN'])
                data = request.body.decode('utf-8')
                log.json = "%s" % (data,)
                log.save()

                received_json_data = json.loads(data)
                all_trans_ids = set(CharacterPayment.objects.all().values_list('trans_id', flat=True))
                for details in received_json_data:
                    if details['trans_id'] not in all_trans_ids:
                        CharacterPayment.objects.update_or_create(
                            character_id = details['char_id'],
                            character_name = details['name'],
                            amount = details['amount'],
                            trans_id = details['trans_id'],
                            date = details['date'],
                        )

                return HttpResponse('OK')
            else:
                raise Http404
        else:
            raise Http404
    except:
        logging.exception("Messsage")
        raise Http404


@login_required
@permission_required('toolbox.view_own_character_mining')
def view_character_mining(request, character_id=None):
    if character_id is None:
        character = request.user.profile.main_character
    else:
        if request.user.has_perm('toolbox.admin_alliance_mining'):
            character = EveCharacter.objects.get(character_id=character_id).character_ownership.user.profile.main_character
        else:
            character = request.user.profile.main_character

    character_list = character.character_ownership.user.character_ownerships.all().select_related('character')
    character_ids = set(character_list.values_list('character__character_id', flat=True))
    all_payment = CharacterPayment.objects.filter(character_id__in=character_ids)
    all_payments = all_payment.aggregate(total_isk=Coalesce(Sum('amount'),0))['total_isk']
    all_mining_chars = CharacterMining.objects.filter(character_id__in=character_ids)\
        .values('character_id')\
        .annotate(
            total_tax=Sum('tax_total')
        ).annotate(
            total_isk=Sum('isk_total')
        ).annotate(
            character_name=F('character_name')
        )
    all_obs = CharacterMiningObservation.objects.filter(character__character_id__in=character_ids)
    total_tax = all_mining_chars.aggregate(total_taxes=Coalesce(Sum('tax_total'),0))['total_taxes']
    total_isk = all_mining_chars.aggregate(total_isk=Coalesce(Sum('isk_total'),0))['total_isk']
    char_breakdown = {}
    for ob in all_obs:
        if ob.character.character_name in char_breakdown:
            if ob.ore_name in char_breakdown[ob.character.character_name]['ores']:
                char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["value"] = char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["value"] + ob.value
                char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["count"] = char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["count"] + ob.count
            else:
                char_breakdown[ob.character.character_name]['ores'][ob.ore_name] = {}
                char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["value"] = ob.value
                char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["count"] = ob.count
        else:
            char_breakdown[ob.character.character_name]= {}
            char_breakdown[ob.character.character_name]['id'] = ob.character.character_id
            char_breakdown[ob.character.character_name]['ores'] = {}
            char_breakdown[ob.character.character_name]['ores'][ob.ore_name] = {}
            char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["value"] = ob.value
            char_breakdown[ob.character.character_name]['ores'][ob.ore_name]["count"] = ob.count


    context = {'characters': all_mining_chars,
               'all_obs': char_breakdown,
               'char_list': character_list,
               'total_tax': total_tax,
               'total_isk': total_isk,
               'all_payments':all_payments,
               'all_payment': all_payment
               }

    return render(request, 'toolbox/character_mining.html', context)


@login_required
def admin_character_mining(request):


    if request.user.has_perm('toolbox.admin_alliance_mining'):
        linked_chars = EveCharacter.objects.filter(character_ownership__isnull=False)
    elif request.user.has_perm('toolbox.admin_corporation_mining'):
        linked_chars = EveCharacter.objects.filter(character_ownership__isnull=False,
                        character_ownership__user__profile__main_character__corporation_id=request.user.profile.main_character.corporation_id)
    else:
        raise PermissionDenied('You do not have permission to be here. This has been Logged!')


    linked_chars = linked_chars.select_related('character_ownership', 'character_ownership__user__profile__main_character')\
                                .prefetch_related('character_ownership__user__character_ownerships')\
                                .annotate(
                                    total_payments=Coalesce(
                                        Subquery(
                                            CharacterPayment.objects.filter(
                                                character_id=OuterRef('character_id'))
                                                .order_by()
                                                .values('character_id')
                                                .annotate(total_isks=Sum('amount'))
                                                .values('total_isks')
                                        )
                                    ,0
                                    )
                                ).annotate(
                                    total_tax=Coalesce(
                                        Subquery(
                                            CharacterMining.objects.filter(
                                                character_id=OuterRef('character_id'))
                                                .order_by()
                                                .values('character_id')
                                                .annotate(tax_totals=Sum('tax_total'))
                                                .values('tax_totals')
                                        )
                                    ,0
                                    )
                                ).annotate(
                                    total_mined=Coalesce(
                                        Subquery(
                                            CharacterMining.objects.filter(
                                                character_id=OuterRef('character_id'))
                                                .order_by()
                                                .values('character_id')
                                                .annotate(total_mined=Sum('isk_total'))
                                                .values('total_mined')
                                        )
                                    ,0
                                    )
                                ).values('character_id',
                                         'total_tax',
                                         'total_mined',
                                         'total_payments',
                                         'character_ownership__user__profile__main_character__character_id',
                                         'character_ownership__user__profile__main_character__character_name',
                                         'character_ownership__user__profile__main_character__corporation_name',
                                         'character_ownership__user__profile__main_character__alliance_name'
                                         )

    linked_char_breakdown = {}
    linked_ids = []
    total_owed_tax = 0
    for ob in linked_chars:
        if int(ob['total_tax']) > 1 or ob['total_payments'] > 0:
            main = ob['character_ownership__user__profile__main_character__character_name']
            if main is not None:
                if main in linked_char_breakdown:
                    linked_char_breakdown[main]['total_tax'] += int(ob['total_tax'])
                    linked_char_breakdown[main]['total_mined'] += int(ob['total_mined'])
                    linked_char_breakdown[main]['total_payments'] += ob['total_payments']
                else:
                    linked_char_breakdown[main]= {}
                    linked_char_breakdown[main]['id'] = ob['character_ownership__user__profile__main_character__character_id']
                    linked_char_breakdown[main]['corp'] = ob['character_ownership__user__profile__main_character__corporation_name']
                    linked_char_breakdown[main]['alliance'] = ob['character_ownership__user__profile__main_character__alliance_name']
                    linked_char_breakdown[main]['total_tax'] = int(ob['total_tax'])
                    linked_char_breakdown[main]['total_mined'] = int(ob['total_mined'])
                    linked_char_breakdown[main]['total_payments'] = ob['total_payments']
                linked_ids.append(ob['character_id'])

        total_owed_tax += (int(ob['total_tax']) - ob['total_payments'])

    month = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).month
    year = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).year

    month_totals = CharacterMining.objects.filter(month=month, year=year)\
        .values('character_id')\
        .aggregate(
            total_tax=Coalesce(Sum('tax_total'), 0), total_mined=Coalesce(Sum('isk_total'), 0)
        )

    all_time_totals = CharacterMining.objects.all()\
        .values('character_id')\
        .aggregate(
            total_tax=Coalesce(Sum('tax_total'), 0), total_mined=Coalesce(Sum('isk_total'), 0)
        )

    unlinked_chars = CharacterMining.objects.exclude(
        character_id__in=linked_ids) \
        .values('character_id')\
        .annotate(
            total_tax=Sum('tax_total')
        ).annotate(
            total_mined=Sum('isk_total')
        ).annotate(
            character_name=F('character_name')
        )

    total_unlinked_isk = unlinked_chars.aggregate(Sum('total_tax'))

    context = {
               'linked_char_breakdown': linked_char_breakdown,
               'unlinked_char_breakdown': unlinked_chars,
               'total_owed_tax': total_owed_tax,
               'total_unlinked_isk': total_unlinked_isk,
               'month_totals': month_totals,
               'all_time_totals': all_time_totals
    }

    return render(request, 'toolbox/character_mining_admin.html', context)

    
@login_required
@permission_required('toolbox.add_new_eve_note_comments')
def get_evenote_comments(request, evenote_id=None):
    comments = EveNote.objects.prefetch_related('comment').get(id=evenote_id).comment.all()
    ctx = {
        'comments': comments,
        'add_blacklist': request.user.has_perm('toolbox.add_to_blacklist'),
        'add_ultra_restricted_note': request.user.has_perm('toolbox.add_ultra_restricted_eve_notes'),
        'add_restricted_note': request.user.has_perm('toolbox.add_restricted_eve_notes')

    }
    return HttpResponse(render_to_string('toolbox/modal_comments.html', ctx))


@login_required
@permission_required('toolbox.add_new_eve_notes')
def get_edit_evenote(request, evenote_id=None):
    note = EveNote.objects.get(id=evenote_id)
    ctx = {
        'note': note,
        'add_blacklist': request.user.has_perm('toolbox.add_to_blacklist'),
        'add_ultra_restricted_note': request.user.has_perm('toolbox.add_ultra_restricted_eve_notes'),
        'add_restricted_note': request.user.has_perm('toolbox.add_restricted_eve_notes')

    }
    return HttpResponse(render_to_string('toolbox/modal_edit_note.html', ctx, request=request))

@login_required
@permission_required('toolbox.add_new_eve_note_comments')
def get_add_comment(request, evenote_id=None):
    note = EveNote.objects.get(id=evenote_id)
    ctx = {
        'note': note,
        'add_blacklist': request.user.has_perm('toolbox.add_to_blacklist'),
        'add_ultra_restricted_note': request.user.has_perm('toolbox.add_ultra_restricted_eve_notes'),
        'add_restricted_note': request.user.has_perm('toolbox.add_restricted_eve_notes')

    }
    return HttpResponse(render_to_string('toolbox/modal_add_comment.html', ctx, request=request))

@login_required
@permission_required('toolbox.add_new_eve_notes')
def get_add_evenote(request, eve_id=None):
    add_perms = request.user.has_perm('toolbox.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('toolbox.add_new_eve_notes')
    message = None
    if not (add_perms or add_global_perms):
        message =  "No Permissions"
        eve_id = None
    
    if eve_id:
        if request.method == 'POST':
            try:
                name = providers.provider.client.Universe.post_universe_names(ids=[eve_id]).result()[0]
                char_info = None
                corp_info = None
                alliance_info = None

                if name.get('category') == 'character':
                    char_info = providers.provider.client.Character.get_characters_character_id(character_id=eve_id).result()
                    corp_info = providers.provider.client.Corporation.get_corporations_corporation_id(corporation_id=char_info.get('corporation_id')).result()
                    if corp_info.get('alliance_id', False):
                        alliance_info = providers.provider.client.Alliance.get_alliances_alliance_id(alliance_id=corp_info.get('alliance_id')).result()

                elif name.get('category') == 'corporation':
                    corp_info = providers.provider.client.Corporation.get_corporations_corporation_id(corporation_id=eve_id).result()
                    if corp_info.get('alliance_id', False):
                        alliance_info = providers.provider.client.Alliance.get_alliances_alliance_id(alliance_id=corp_info.get('alliance_id')).result()
                
                if not add_global_perms:
                    if not (name.get('category') == 'character'):
                        message = "You can only add people from your own corp, Please contact a Diplo to add this note."
                    else:
                        if not int(request.user.profile.main_character.corporation_id) == int(char_info.get('corporation_id')):
                            message = "You can only add people from your own corp, Please contact a Diplo to add this note."

                if not message:
                    form = EveNoteForm()

                    context = {'form': form,
                            'name': name,
                            'char_info': char_info,
                            'corp_info': corp_info,
                            'alliance_info': alliance_info,
                            'add_blacklist': request.user.has_perm('toolbox.add_to_blacklist'),
                            'add_ultra_restricted_note': request.user.has_perm('toolbox.add_ultra_restricted_eve_notes'),
                            'add_restricted_note': request.user.has_perm('toolbox.add_restricted_eve_notes')}
                    return HttpResponse(render_to_string('toolbox/add_note.html', context, request=request))

            except:
                message = "ESI Error. Please Try again later."

            
    context = {'names': False,
                'searched': False,
                'message': message,
                'restricted_perms': add_global_perms
                }
    return HttpResponse(render_to_string('toolbox/search_name.html', context, request=request))


@login_required
def search_names(request):
    add_perms = request.user.has_perm('toolbox.add_basic_eve_notes')
    add_global_perms = request.user.has_perm('toolbox.add_new_eve_notes')

    if not (add_perms or add_global_perms):
        messages.info(request, "No Permissions")
        return redirect('toolbox:eve_note_board')
    names = None
    searched = False
    message = False
    if request.method == 'POST':
        # check whether it's valid:
        name = request.POST.get('name')
        try:
            search_char = get_search_char(request.user)
            token = Token.get_token(search_char.character_id, ['esi-search.search_structures.v1'])
            hits = providers.provider.client.Search.get_characters_character_id_search(
                search=name, categories=['character', 'corporation', 'alliance'], character_id=search_char.character_id, token=token.valid_access_token()).result()
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
            if len(names_list) > 0:
                names = providers.provider.client.Universe.post_universe_names(ids=names_list).result()
            searched = name
        except Exception as e:
            logger.error(e)
            message = e.message
            #messages.error(request,
            #                "ESI Error. Please Try again later.")
            #return redirect('toolbox:eve_note_board')

    context = {'names': names,
                'searched': searched,
                'message': message,
                'restricted_perms': add_global_perms
                }
    return HttpResponse(render_to_string('toolbox/search_name.html', context, request=request))

