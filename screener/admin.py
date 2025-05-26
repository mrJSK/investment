from django.contrib import admin
from .models import Scan, Condition

class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 1

@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ("name", "timeframe", "segment", "created_at")
    inlines = [ConditionInline]

@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("scan", "left_indicator", "operator", "right_indicator", "constant", "logic")
