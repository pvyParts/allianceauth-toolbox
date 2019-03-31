from django.contrib import admin

# Register your models here.
from .models import EveNote, EveNoteComment

admin.site.register(EveNote)
admin.site.register(EveNoteComment)
