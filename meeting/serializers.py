from rest_framework import serializers
from .models import Meeting


class MeetingListSerializer(serializers.ModelSerializer):
    """Serializer for listing meetings"""
    meeting_type_display = serializers.CharField(source='get_meeting_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'meeting_type', 'meeting_type_display',
            'status', 'status_display', 'created_at', 'meeting_date',
            'meeting_link'
        ]


class MeetingSummarySerializer(serializers.ModelSerializer):
    """Serializer for meeting summary details"""
    meeting_type_display = serializers.CharField(source='get_meeting_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    summary = serializers.SerializerMethodField()
    key_points = serializers.SerializerMethodField()
    decisions = serializers.SerializerMethodField()
    action_items = serializers.SerializerMethodField()
    agenda = serializers.SerializerMethodField()
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'meeting_type', 'meeting_type_display',
            'description', 'transcript', 'created_at', 'meeting_date',
            'status', 'status_display', 'summary', 'key_points',
            'decisions', 'action_items', 'agenda', 'meeting_link'
        ]
    
    def get_summary(self, obj):
        return obj.summary
    
    def get_key_points(self, obj):
        return obj.key_points
    
    def get_decisions(self, obj):
        return obj.decisions
    
    def get_action_items(self, obj):
        return obj.action_items
    
    def get_agenda(self, obj):
        return obj.agenda


class MeetingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating meetings"""
    
    class Meta:
        model = Meeting
        fields = ['title', 'meeting_type', 'description', 'transcript', 'recording_file', 'meeting_date', 'meeting_link']
    
    def validate_recording_file(self, value):
        """Validate uploaded file"""
        if value:
            # Check file size
            if value.size > 100 * 1024 * 1024:  # 100MB
                raise serializers.ValidationError("File size too large. Maximum 100MB allowed.")
            
            # Check file extension
            allowed_extensions = ['mp3', 'wav', 'mp4', 'webm', 'm4a']
            ext = value.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
                )
        
        return value
    
    def validate_meeting_link(self, value):
        """Validate meeting link"""
        if value:
            # Check if it's a valid meeting platform
            valid_platforms = ['meet.google.com', 'zoom.us', 'teams.microsoft.com']
            if not any(platform in value for platform in valid_platforms):
                raise serializers.ValidationError(
                    "Invalid meeting link. Supported: Google Meet, Zoom, Microsoft Teams"
                )
        return value
    
    def validate(self, data):
        """Ensure either transcript, recording file, or meeting link is provided"""
        if not data.get('transcript') and not data.get('recording_file') and not data.get('meeting_link'):
            raise serializers.ValidationError(
                "Either a transcript, a recording file, or a meeting link must be provided."
            )
        return data
