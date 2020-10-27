from django.contrib import admin

# Register your models here.
from .models import EveNote, EveNoteComment, ApiKey, ApiKeyLog, CharacterMining,CharacterPayment


admin.site.register(EveNote)
admin.site.register(EveNoteComment)

admin.site.register(ApiKey)
admin.site.register(ApiKeyLog)

admin.site.register(CharacterPayment)
admin.site.register(CharacterMining)
