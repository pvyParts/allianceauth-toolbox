from django.db import models
from model_utils import Choices


class EveNote(models.Model):
    eve_id = models.IntegerField()
    eve_name = models.CharField(max_length=500)
    _category_enum = Choices('alliance', 'character', 'corporation')
    eve_catagory = models.CharField(max_length=30, choices=_category_enum)

    blacklisted = models.BooleanField(default=False)
    restricted = models.BooleanField(default=False)
    ultra_restricted = models.BooleanField(default=False)

    added_by = models.CharField(max_length=500)
    added_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    
    # character additions
    corporation_id = models.IntegerField(null=True, default=None)
    corporation_name = models.CharField(max_length=500, null=True, default=None)
    
    # corp/character additions
    alliance_id = models.IntegerField(null=True, default=None)
    alliance_name = models.CharField(max_length=500, null=True, default=None)

    def __str__(self):
        return "%s added by: %s" % (self.eve_name, self.added_by)

    class Meta:
        permissions = (
            ('view_basic_eve_notes', 'Can View own corps notes'),
            ('add_basic_eve_notes', 'Can Add own corp members to notes'),
            ('view_eve_notes', 'Can view all eve notes'),
            ('add_new_eve_notes', 'Can add new eve notes'),
            ('add_to_blacklist', 'Can add to Blacklist'),
            ('view_eve_blacklist', 'Can View the Blacklist'),
            ('view_restricted_eve_notes', 'Can View restricted eve notes'),
            ('view_ultra_restricted_eve_notes', 'Can View ultra_restricted eve notes'),
            ('add_restricted_eve_notes', 'Can Add restricted eve notes'),
            ('add_ultra_restricted_eve_notes', 'Can Add ultra_restricted eve notes')
        )


class EveNoteComment(models.Model):
    eve_note = models.ForeignKey(EveNote, on_delete=models.CASCADE, related_name='comment')
    added_by = models.CharField(max_length=500)
    comment = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
    restricted = models.BooleanField(default=False)
    ultra_restricted = models.BooleanField(default=False)

    def __str__(self):
        return "Comment on: %s added by: %s" % (self.eve_note.eve_name, self.added_by)

    class Meta:
        permissions = (
            ('view_eve_note_comments', 'Can view eve note comments'),
            ('add_new_eve_note_comments', 'Can add comments on eve notes'),
            ('view_eve_note_restricted_comments', 'Can view restricted eve note comments'),
            ('add_new_eve_note_restricted_comments', 'Can add new restricted comments to eve notes'),
            ('view_eve_note_ultra_restricted_comments', 'Can view ultra restricted eve note comments'),
            ('add_new_eve_note_ultra_restricted_comments', 'Can add new ultra restricted comments to eve notes'),
        )


class ApiKey(models.Model):
    api_hash = models.CharField(max_length=255, null=True, default=None, unique=True)
    name = models.CharField(max_length=255, null=True, default=None)


class ApiKeyLog(models.Model):
    apikey = models.ForeignKey(ApiKey, on_delete=models.CASCADE)
    json = models.TextField(null=True, default=None)
    date_accessed = models.DateTimeField(auto_now=True)


class CharacterMining(models.Model):
    character_id = models.BigIntegerField()
    character_name = models.CharField(max_length=500)
    last_update = models.DateTimeField(auto_now_add=True)
    month = models.IntegerField()
    year = models.IntegerField()
    isk_total = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=None)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=None)

    class Meta:
        permissions = (
            ('view_own_character_mining', 'Can View Personal Mining Taxes'),
            ('admin_alliance_mining', 'Can View all Ledger Data'),
            ('admin_corporation_mining', 'Can View Own Corps Ledger Data'),

        )


class CharacterMiningObservation(models.Model):
    character = models.ForeignKey(CharacterMining, on_delete=models.CASCADE)
    ore_name = models.CharField(max_length=500)
    ore_type = models.IntegerField()
    count = models.IntegerField()
    value = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=None)

class CharacterPayment(models.Model):
    character_id = models.BigIntegerField()
    character_name = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=None)
    date = models.DateTimeField()
    trans_id = models.BigIntegerField()

class MoonExtraction(models.Model):
    structure_id = models.BigIntegerField()
    structure_name = models.CharField(max_length=500)
    moon_name = models.CharField(max_length=500)
    extraction_complete = models.DateTimeField()

    last_update = models.DateTimeField(auto_now_add=True)

class MoonExtractionOre(models.Model):
    moon_timer = models.ForeignKey(MoonExtraction, on_delete=models.CASCADE)
    ore = models.CharField(max_length=500)
    ore_percentage = models.DecimalField(max_digits=6, decimal_places=2)
    total_m3 = models.BigIntegerField()
    mined_m3 = models.BigIntegerField()


class FilterBase(models.Model):

    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}: {self.description}"

    def process_filter(self, user: User):
        raise NotImplementedError("Please Create a filter function!")

    def audit_filter(self, user: User):
        raise NotImplementedError("Please Create a audit function!")


class ToolboxEveNoteFilter(FilterBase):
    class Meta:
        verbose_name = "Smart Filter: User Has Flagged/Blacklisted Char"
        verbose_name_plural = verbose_name

    def process_filter(self, user: User):
        return self.audit_filter(User.objects.filter(pk=user.pk))[user.pk]['check']

    def audit_filter(self, users):
        blacklisted_char = EveNote.objects.filter(blacklisted=True, 
                                    eve_catagory='character').values('eve_id')
        blacklisted_corp = EveNote.objects.filter(blacklisted=True, 
                                    eve_catagory='corporation').values('eve_id')
        blacklisted_alli = EveNote.objects.filter(blacklisted=True, 
                                    eve_catagory='alliance').values('eve_id')
        co = CharacterOwnership.objects.filter((
                            Q(character__character_id__in=blacklisted_char) | 
                            Q(character__corporation_id__in=blacklisted_corp) | 
                            Q(character__alliance_id__in=blacklisted_alli)),
                            user__in=users).values('user__id', 'character__character_name')

        chars = defaultdict(list)
        for c in co:
            chars[c['user__id']].append(c['character__character_name'])

        output = defaultdict(lambda: {"message": "", "check": True})
        for c, char_list in chars.items():
            output[c] = {"message": ", ".join(char_list), "check": False}
        return output

