import json
import os
from django.conf import settings

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import requests
except ImportError:
    requests = None


class LLMService:
    """Service to handle LLM integration for meeting summarization"""
    
    SUMMARY_PROMPT = """
Analyze the following meeting transcript and provide a structured JSON response with the following fields:
1. summary: A concise 2-3 sentence summary of the meeting
2. key_points: A list of 3-5 main discussion points
3. decisions: A list of decisions made during the meeting
4. action_items: A list of objects with 'task', 'owner' (if mentioned), and 'due_date' (if mentioned)
5. agenda: A list of topics discussed with brief descriptions

Transcript:
{transcript}

Respond with ONLY valid JSON, no additional text.
"""

    @staticmethod
    def generate_summary(transcript, service=None):
        """Generate meeting summary using LLM"""
        # If no specific service requested, pick the first available configured provider.
        if not service:
            # prefer OpenAI if key present
            if getattr(settings, 'OPENAI_API_KEY', None) and openai:
                service = 'openai'
            elif getattr(settings, 'GOOGLE_API_KEY', None) and genai:
                service = 'google'
            elif getattr(settings, 'HUGGINGFACE_API_KEY', None) and requests:
                service = 'huggingface'
            else:
                raise ValueError("No LLM provider configured. Set OPENAI_API_KEY, GOOGLE_API_KEY, or HUGGINGFACE_API_KEY in your environment.")

        if service == 'openai':
            return LLMService._openai_summary(transcript)
        elif service == 'google':
            return LLMService._google_summary(transcript)
        elif service == 'huggingface':
            return LLMService._huggingface_summary(transcript)
        else:
            raise ValueError(f"Unknown transcription service: {service}")
    
    @staticmethod
    def _openai_summary(transcript):
        """Generate summary using OpenAI"""
        if not openai or not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        openai.api_key = settings.OPENAI_API_KEY
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a meeting summarization expert. Analyze meeting transcripts and provide structured summaries."
                    },
                    {
                        "role": "user",
                        "content": LLMService.SUMMARY_PROMPT.format(transcript=transcript)
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            summary_json = json.loads(content)
            return summary_json
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    @staticmethod
    def _google_summary(transcript):
        """Generate summary using Google Generative AI"""
        if not genai or not settings.GOOGLE_API_KEY:
            raise ValueError("Google API key not configured")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(
                LLMService.SUMMARY_PROMPT.format(transcript=transcript)
            )
            
            content = response.text
            summary_json = json.loads(content)
            return summary_json
        except Exception as e:
            raise Exception(f"Google API error: {str(e)}")
    
    @staticmethod
    def _huggingface_summary(transcript):
        """Generate summary using HuggingFace API"""
        if not settings.HUGGINGFACE_API_KEY:
            raise ValueError("HuggingFace API key not configured")
        
        try:
            headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
            api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            
            payload = {"inputs": transcript[:512]}  # Truncate to model limits
            
            response = requests.post(api_url, headers=headers, json=payload)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                summary = result[0].get('summary_text', '')
            else:
                summary = str(result)
            
            # Return a structured response
            return {
                "summary": summary,
                "key_points": [],
                "decisions": [],
                "action_items": [],
                "agenda": []
            }
        except Exception as e:
            raise Exception(f"HuggingFace API error: {str(e)}")
    
    @staticmethod
    def extract_transcript_from_audio(audio_file_path, service=None):
        """Extract transcript from audio file"""
        # If no explicit service provided, pick one that is configured and available.
        if not service:
            if getattr(settings, 'OPENAI_API_KEY', None) and openai:
                service = 'openai'
            elif getattr(settings, 'GOOGLE_API_KEY', None) and genai:
                service = 'google'
            else:
                raise ValueError("No transcription provider configured. Set OPENAI_API_KEY or GOOGLE_API_KEY in your .env and restart the app.")

        if service == 'openai':
            return LLMService._openai_transcribe(audio_file_path)
        elif service == 'google':
            return LLMService._google_transcribe(audio_file_path)
        else:
            raise ValueError(f"Transcription not supported for service: {service}")
    
    @staticmethod
    def _openai_transcribe(audio_file_path):
        """Transcribe audio using OpenAI Whisper"""
        if not openai or not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        openai.api_key = settings.OPENAI_API_KEY
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                transcript_response = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file
                )
            
            return transcript_response['text']
        except Exception as e:
            raise Exception(f"OpenAI transcription error: {str(e)}")
    
    @staticmethod
    def _google_transcribe(audio_file_path):
        """Transcribe audio using Google Cloud Speech-to-Text"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("Google API key not configured")
        
        try:
            from google.cloud import speech
            from google.oauth2 import service_account
            
            client = speech.SpeechClient()
            
            with open(audio_file_path, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            
            response = client.recognize(config=config, audio=audio)
            
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
        except Exception as e:
            raise Exception(f"Google transcription error: {str(e)}")


def ensure_json_format(func):
    """Decorator to ensure function returns valid JSON"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, dict):
                return result
            elif isinstance(result, str):
                return json.loads(result)
            else:
                return result
        except json.JSONDecodeError:
            return {
                "summary": "",
                "key_points": [],
                "decisions": [],
                "action_items": [],
                "agenda": []
            }
    return wrapper
