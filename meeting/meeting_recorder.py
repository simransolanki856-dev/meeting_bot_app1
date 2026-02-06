"""
Meeting Recorder Service
Handles joining online meetings, recording audio/video, and extracting transcripts
"""

import re
import subprocess
import os
import json
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MeetingRecorder:
    """Records meetings from Google Meet, Zoom, Teams, etc."""
    
    @staticmethod
    def extract_meeting_id(meeting_link):
        """Extract meeting ID from various meeting platform links"""
        
        # Google Meet pattern
        google_meet_pattern = r'meet\.google\.com/([a-z-]+)'
        match = re.search(google_meet_pattern, meeting_link)
        if match:
            return {
                'platform': 'google_meet',
                'meeting_id': match.group(1),
                'link': meeting_link
            }
        
        # Zoom pattern
        zoom_pattern = r'zoom\.us/j/(\d+)'
        match = re.search(zoom_pattern, meeting_link)
        if match:
            return {
                'platform': 'zoom',
                'meeting_id': match.group(1),
                'link': meeting_link
            }
        
        # Teams pattern
        teams_pattern = r'teams\.microsoft\.com/l/meetup-join/(.+)'
        match = re.search(teams_pattern, meeting_link)
        if match:
            return {
                'platform': 'teams',
                'meeting_id': match.group(1),
                'link': meeting_link
            }
        
        return None
    
    @staticmethod
    def join_and_record_meeting(meeting_link, duration_minutes=60, output_file=None):
        """
        Join a meeting and record audio
        
        Args:
            meeting_link: URL of the meeting
            duration_minutes: How long to record
            output_file: Where to save the recording
            
        Returns:
            dict with recording status and file path
        """
        
        meeting_info = MeetingRecorder.extract_meeting_id(meeting_link)
        
        if not meeting_info:
            return {
                'success': False,
                'error': 'Invalid meeting link format',
                'platform': None
            }
        
        platform = meeting_info['platform']
        
        if output_file is None:
            output_file = os.path.join(
                settings.MEDIA_ROOT,
                'recordings',
                f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            )
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        try:
            if platform == 'google_meet':
                return MeetingRecorder._record_google_meet(meeting_info, duration_minutes, output_file)
            elif platform == 'zoom':
                return MeetingRecorder._record_zoom(meeting_info, duration_minutes, output_file)
            elif platform == 'teams':
                return MeetingRecorder._record_teams(meeting_info, duration_minutes, output_file)
        except Exception as e:
            logger.error(f"Error recording {platform} meeting: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'platform': platform
            }
    
    @staticmethod
    def _record_google_meet(meeting_info, duration_minutes, output_file):
        """
        Record Google Meet meeting using Selenium and PyAudio
        Requires: selenium, google-chrome, pyaudio
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import pyaudio
            import wave
            import threading
            
            # Setup Chrome options
            options = webdriver.ChromeOptions()
            options.add_argument('--use-fake-ui-for-media-stream')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Initialize recording
            CHUNK = 1024
            FORMAT = pyaudio.paFloat32
            CHANNELS = 1
            RATE = 44100
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                          input=True, frames_per_buffer=CHUNK)
            
            frames = []
            recording = True
            
            def record_audio():
                """Record audio in background thread"""
                while recording:
                    try:
                        data = stream.read(CHUNK, exception_on_overflow=False)
                        frames.append(data)
                    except Exception as e:
                        logger.error(f"Audio recording error: {e}")
            
            # Start browser
            driver = webdriver.Chrome(options=options)
            driver.get(meeting_info['link'])
            
            # Start recording in background
            record_thread = threading.Thread(target=record_audio)
            record_thread.daemon = True
            record_thread.start()
            
            # Wait for meeting to load and recording duration
            import time
            time.sleep(duration_minutes * 60)
            
            # Stop recording
            recording = False
            record_thread.join(timeout=5)
            
            # Save audio file
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            wf = wave.open(output_file, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Close browser
            driver.quit()
            
            return {
                'success': True,
                'platform': 'google_meet',
                'output_file': output_file,
                'message': f'Successfully recorded Google Meet for {duration_minutes} minutes'
            }
        
        except ImportError as e:
            return {
                'success': False,
                'platform': 'google_meet',
                'error': f'Missing dependencies: {str(e)}. Install: pip install selenium pyaudio'
            }
        except Exception as e:
            return {
                'success': False,
                'platform': 'google_meet',
                'error': f'Recording failed: {str(e)}'
            }
    
    @staticmethod
    def _record_zoom(meeting_info, duration_minutes, output_file):
        """
        Record Zoom meeting
        Note: Zoom has built-in recording - this is alternative method
        """
        return {
            'success': False,
            'platform': 'zoom',
            'error': 'Use Zoom\'s built-in recording feature (Record to Cloud or Local)',
            'note': 'For automated Zoom recording, enable Zoom SDK integration'
        }
    
    @staticmethod
    def _record_teams(meeting_info, duration_minutes, output_file):
        """
        Record Teams meeting
        Note: Teams has built-in recording - this is alternative method
        """
        return {
            'success': False,
            'platform': 'teams',
            'error': 'Use Teams\' built-in recording feature (Start Recording)',
            'note': 'For automated Teams recording, enable Teams Bot SDK'
        }


class AudioExtractor:
    """Extract audio from various media formats"""
    
    @staticmethod
    def extract_audio_from_video(video_file, output_audio_file=None):
        """
        Extract audio from video file using ffmpeg
        Supports: MP4, WebM, MKV, AVI, MOV, etc.
        """
        if output_audio_file is None:
            base = os.path.splitext(video_file)[0]
            output_audio_file = f"{base}.wav"
        
        try:
            # Check if ffmpeg is available
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            
            # Extract audio
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # Audio codec
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Channels
                '-q:a', '9',  # Quality
                output_audio_file,
                '-y'  # Overwrite output
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output_file': output_audio_file,
                    'message': 'Audio extracted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
        
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'ffmpeg not found. Install: apt-get install ffmpeg'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class MeetingBotRecorder:
    """
    Complete meeting bot that joins meetings and creates recordings
    """
    
    def __init__(self, meeting_link, duration_minutes=60):
        self.meeting_link = meeting_link
        self.duration_minutes = duration_minutes
        self.recording_file = None
        self.audio_file = None
        self.transcript = None
    
    def record_meeting(self):
        """Start recording the meeting"""
        result = MeetingRecorder.join_and_record_meeting(
            self.meeting_link,
            self.duration_minutes
        )
        
        if result['success']:
            self.recording_file = result['output_file']
            return result
        else:
            return result
    
    def extract_audio(self):
        """Extract audio from recording if needed"""
        if self.recording_file and self.recording_file.endswith(('.mp4', '.webm', '.mkv')):
            result = AudioExtractor.extract_audio_from_video(self.recording_file)
            if result['success']:
                self.audio_file = result['output_file']
                return result
        else:
            self.audio_file = self.recording_file
            return {'success': True, 'message': 'Recording is already audio format'}
    
    def get_status(self):
        """Get current recording status"""
        return {
            'meeting_link': self.meeting_link,
            'recording_file': self.recording_file,
            'audio_file': self.audio_file,
            'transcript': self.transcript,
            'duration': self.duration_minutes
        }
