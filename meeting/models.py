from django.db import models
from django.utils import timezone
import json


class Meeting(models.Model):
    MEETING_TYPES = [
        ('team_meeting', 'Team Meeting'),
        ('interview', 'Interview'),
        ('client_call', 'Client Call'),
        ('standup', 'Standup'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    meeting_type = models.CharField(max_length=50, choices=MEETING_TYPES, default='team_meeting')
    description = models.TextField(blank=True, null=True)
    
    # Meeting link for online meetings (Google Meet, Zoom, Teams, etc.)
    meeting_link = models.URLField(blank=True, null=True, help_text="Google Meet, Zoom, or Teams link")
    
    # Transcript and file handling
    transcript = models.TextField(blank=True, null=True)
    transcript_file = models.FileField(upload_to='transcripts/', blank=True, null=True)
    recording_file = models.FileField(upload_to='recordings/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meeting_date = models.DateTimeField(default=timezone.now)
    
    # AI Summary (stored as JSON)
    summary_json = models.JSONField(null=True, blank=True)
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_error = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['meeting_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_meeting_type_display()}"
    
    @property
    def summary(self):
        """Extract summary from JSON"""
        if self.summary_json:
            return self.summary_json.get('summary', '')
        return ''
    
    @property
    def key_points(self):
        """Extract key points from JSON"""
        if self.summary_json:
            return self.summary_json.get('key_points', [])
        return []
    
    @property
    def decisions(self):
        """Extract decisions from JSON"""
        if self.summary_json:
            return self.summary_json.get('decisions', [])
        return []
    
    @property
    def action_items(self):
        """Extract action items from JSON"""
        if self.summary_json:
            return self.summary_json.get('action_items', [])
        return []
    
    @property
    def agenda(self):
        """Extract agenda from JSON"""
        if self.summary_json:
            return self.summary_json.get('agenda', [])
        return []
