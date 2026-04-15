from django.contrib import admin
from .models import Camera, Prenotazione

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_struttura', 'prezzo')
    list_filter = ('tipo_struttura',)

@admin.register(Prenotazione)
class PrenotazioneAdmin(admin.ModelAdmin):
    list_display = ('nome_cliente', 'camera', 'data_checkin', 'data_checkout')
    list_filter = ('camera__tipo_struttura',)
