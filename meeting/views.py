from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Meeting
from .serializers import MeetingListSerializer, MeetingSummarySerializer, MeetingCreateSerializer
from .llm_service import LLMService
from .meeting_recorder import MeetingBotRecorder, MeetingRecorder
import json
import threading


class MeetingViewSet(viewsets.ModelViewSet):
    """API ViewSet for Meeting CRUD operations"""
    
    queryset = Meeting.objects.all()
    serializer_class = MeetingListSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'meeting_type']
    ordering_fields = ['created_at', 'meeting_date', 'meeting_type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return different serializers based on action"""
        if self.action == 'retrieve':
            return MeetingSummarySerializer
        elif self.action == 'create':
            return MeetingCreateSerializer
        return MeetingListSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new meeting and generate summary"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the meeting
        meeting = serializer.save()
        
        # Generate summary asynchronously or synchronously
        try:
            # Get transcript
            transcript = meeting.transcript
            
            if not transcript and meeting.recording_file:
                # Extract transcript from audio file
                file_path = meeting.recording_file.path
                try:
                    transcript = LLMService.extract_transcript_from_audio(file_path)
                    meeting.transcript = transcript
                    meeting.save()
                except Exception as e:
                    meeting.status = 'failed'
                    meeting.processing_error = f"Transcription failed: {str(e)}"
                    meeting.save()
                    return Response(
                        {'error': f'Transcription failed: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Generate summary from transcript
            meeting.status = 'processing'
            meeting.save()
            
            try:
                summary_json = LLMService.generate_summary(transcript)
                meeting.summary_json = summary_json
                meeting.status = 'completed'
                meeting.processing_error = None
            except Exception as e:
                meeting.status = 'failed'
                meeting.processing_error = str(e)
            
            meeting.save()
        
        except Exception as e:
            meeting.status = 'failed'
            meeting.processing_error = str(e)
            meeting.save()
        
        # Return the created meeting
        output_serializer = MeetingSummarySerializer(meeting)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific meeting with full details"""
        meeting = self.get_object()
        serializer = MeetingSummarySerializer(meeting)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """List all meetings with filtering"""
        # Add filtering by meeting_type if provided
        meeting_type = request.query_params.get('meeting_type', None)
        if meeting_type:
            self.queryset = self.queryset.filter(meeting_type=meeting_type)
        
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['delete'])
    def delete_meeting(self, request, pk=None):
        """Delete a specific meeting"""
        meeting = self.get_object()
        meeting.delete()
        return Response(
            {'message': 'Meeting deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'])
    def regenerate_summary(self, request, pk=None):
        """Regenerate summary for a meeting"""
        meeting = self.get_object()
        
        if not meeting.transcript:
            return Response(
                {'error': 'No transcript available for this meeting'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            meeting.status = 'processing'
            meeting.save()
            
            summary_json = LLMService.generate_summary(meeting.transcript)
            meeting.summary_json = summary_json
            meeting.status = 'completed'
            meeting.processing_error = None
            meeting.save()
            
            serializer = MeetingSummarySerializer(meeting)
            return Response(serializer.data)
        except Exception as e:
            meeting.status = 'failed'
            meeting.processing_error = str(e)
            meeting.save()
            return Response(
                {'error': f'Summary generation failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def download_summary(self, request, pk=None):
        """Download summary as text"""
        meeting = self.get_object()
        
        if not meeting.summary_json:
            return Response(
                {'error': 'No summary available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate text content
        content = f"""MEETING SUMMARY REPORT
        
Meeting Title: {meeting.title}
Meeting Type: {meeting.get_meeting_type_display()}
Date: {meeting.meeting_date.strftime('%Y-%m-%d %H:%M:%S')}
Created: {meeting.created_at.strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}

SUMMARY:
{meeting.summary}

{'='*80}

KEY POINTS:
"""
        
        for point in meeting.key_points:
            content += f"• {point}\n"
        
        content += f"\n{'='*80}\n\nDECISIONS:\n"
        for decision in meeting.decisions:
            content += f"• {decision}\n"
        
        content += f"\n{'='*80}\n\nACTION ITEMS:\n"
        for item in meeting.action_items:
            task = item.get('task', '') if isinstance(item, dict) else item
            owner = item.get('owner', 'N/A') if isinstance(item, dict) else 'N/A'
            due_date = item.get('due_date', 'N/A') if isinstance(item, dict) else 'N/A'
            content += f"• Task: {task}\n  Owner: {owner}\n  Due Date: {due_date}\n\n"
        
        content += f"\n{'='*80}\n\nAGENDA:\n"
        for topic in meeting.agenda:
            topic_name = topic.get('topic', '') if isinstance(topic, dict) else topic
            description = topic.get('description', '') if isinstance(topic, dict) else ''
            content += f"• {topic_name}\n  {description}\n\n"
        
        return Response(
            {'content': content},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def join_meeting(self, request):
        """Join a Google Meet/Zoom/Teams meeting and record it"""
        meeting_link = request.data.get('meeting_link')
        title = request.data.get('title')
        meeting_type = request.data.get('meeting_type', 'team_meeting')
        duration_minutes = int(request.data.get('duration_minutes', 60))
        
        if not meeting_link:
            return Response(
                {'error': 'Meeting link is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate meeting link format
        meeting_info = MeetingRecorder.extract_meeting_id(meeting_link)
        if not meeting_info:
            return Response(
                {'error': 'Invalid meeting link format. Supported: Google Meet, Zoom, Microsoft Teams'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create meeting record
        meeting = Meeting.objects.create(
            title=title or f"Meeting from {meeting_info['platform']}",
            meeting_type=meeting_type,
            meeting_link=meeting_link,
            status='processing'
        )
        
        # Start recording in background thread
        def record_and_summarize():
            try:
                # Record meeting
                recorder = MeetingBotRecorder(meeting_link, duration_minutes)
                recording_result = recorder.record_meeting()
                
                if not recording_result['success']:
                    meeting.status = 'failed'
                    meeting.processing_error = f"Recording failed: {recording_result.get('error', 'Unknown error')}"
                    meeting.save()
                    return
                
                # Extract audio if needed
                audio_result = recorder.extract_audio()
                if not audio_result['success']:
                    meeting.processing_error = f"Audio extraction failed: {audio_result.get('error', 'Unknown error')}"
                    # Continue with recording file anyway
                
                audio_file = recorder.audio_file or recorder.recording_file
                
                # Transcribe audio
                transcript = LLMService.extract_transcript_from_audio(audio_file)
                meeting.transcript = transcript
                meeting.save()
                
                # Generate summary
                summary_data = LLMService.generate_summary(transcript)
                if summary_data:
                    meeting.summary_json = summary_data
                    meeting.status = 'completed'
                else:
                    meeting.status = 'failed'
                    meeting.processing_error = 'Failed to generate summary'
                
                meeting.save()
            
            except Exception as e:
                meeting.status = 'failed'
                meeting.processing_error = str(e)
                meeting.save()
        
        # Run recording in background
        thread = threading.Thread(target=record_and_summarize)
        thread.daemon = True
        thread.start()
        
        return Response(
            {
                'id': meeting.id,
                'title': meeting.title,
                'meeting_link': meeting_link,
                'status': 'recording',
                'message': f'Recording {meeting_info["platform"]} meeting for {duration_minutes} minutes. You will be notified when complete.',
                'platform': meeting_info['platform']
            },
            status=status.HTTP_201_CREATED
        )


def index(request):
    """Home page"""
    return render(request, 'meeting/index.html')


def create_meeting(request):
    """Create meeting page"""
    return render(request, 'meeting/create_meeting.html')


def meeting_result(request, meeting_id):
    """Meeting result page"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    return render(request, 'meeting/meeting_result.html', {'meeting': meeting})


def meeting_history(request):
    """Meeting history page"""
    return render(request, 'meeting/meeting_history.html')
