from django.contrib import admin
from .models import NewsCheck

@admin.register(NewsCheck)
class NewsCheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_fake', 'confidence_score', 'created_at']
    list_filter = ['is_fake', 'created_at']
    search_fields = ['news_text']

