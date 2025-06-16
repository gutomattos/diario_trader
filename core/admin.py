from django.contrib import admin
from .models import Trade, IBOV, CDI, Estrategia

# Register your models here.
admin.site.register(Trade)
admin.site.register(IBOV)
admin.site.register(CDI)

@admin.register(Estrategia)
class EstrategiaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ordem")
    list_editable = ("ordem",)
    ordering = ("ordem", "nome")
    search_fields = ("nome",)
