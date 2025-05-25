from django.contrib import admin
from .models import Screener, ScreenerCondition

class ScreenerConditionInline(admin.TabularInline):
    model = ScreenerCondition
    extra = 1

@admin.register(Screener)
class ScreenerAdmin(admin.ModelAdmin):
    inlines = [ScreenerConditionInline]

@admin.register(ScreenerCondition)
class ScreenerConditionAdmin(admin.ModelAdmin):
    list_display = ("screener", "left_indicator", "operator", "right_indicator", "constant", "logic_with_next")
