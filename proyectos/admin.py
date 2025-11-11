from django.contrib import admin
from .models import Proyecto

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cliente', 'fecha_inicio')
    search_fields = ('nombre', 'cliente')
    list_filter = ('fecha_inicio',)
    ordering = ('-fecha_inicio',)
