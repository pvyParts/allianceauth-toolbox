import logging

from celery import shared_task
from .models import EveNote
from esi.clients import esi_client_factory

logger = logging.getLogger(__name__)

@shared_task
def update_old_eve_notes():
    character_notes = EveNote.objects.filter(eve_catagory='character', corporation_id__isnull=True)
    c = esi_client_factory()

    for character in character_notes:
        print("Updating %s"%character.eve_name)
        char_info = c.Character.get_characters_character_id(character_id=character.eve_id).result()
        character.corporation_id = char_info.get('corporation_id')

        corp_info = c.Corporation.get_corporations_corporation_id(
            corporation_id=char_info.get('corporation_id')).result()
        character.corporation_name = corp_info.get('name')

        if corp_info.get('alliance_id', False):
            character.alliance_id = corp_info.get('alliance_id')
            alliance_info = c.Alliance.get_alliances_alliance_id(alliance_id=corp_info.get('alliance_id')).result()
            character.alliance_name = alliance_info.get('name')

        character.save()
