from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_type', 'status', 'created_at', 'meeting_date')
    list_filter = ('meeting_type', 'status', 'created_at')
    search_fields = ('title', 'description', 'transcript')
    readonly_fields = ('created_at', 'updated_at', 'summary_json')
    
    fieldsets = (
        ('Meeting Information', {
            'fields': ('title', 'meeting_type', 'description', 'meeting_date')
        }),
        ('Content', {
            'fields': ('transcript', 'recording_file', 'transcript_file')
        }),
        ('Summary', {
            'fields': ('summary_json',),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('status', 'processing_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
