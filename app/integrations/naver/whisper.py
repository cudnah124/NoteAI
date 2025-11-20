"""
Naver Clova Speech (Whisper-like) Integration
"""
import aiohttp
import logging
from typing import Optional, BinaryIO
from app.core.config import settings

logger = logging.getLogger(__name__)


class WhisperService:
    """Service for speech-to-text transcription using Naver Clova Speech"""
    
    def __init__(self):
        self.api_url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt"
        self.api_key = settings.NAVER_API_KEY
        self.api_secret = settings.NAVER_API_SECRET
        
    async def transcribe_audio(
        self, 
        audio_data: bytes,
        language: str = "ko-KR"
    ) -> Optional[str]:
        """
        Transcribe audio to text using Naver Clova Speech API
        
        Args:
            audio_data: Audio file content in bytes
            language: Language code (ko-KR, en-US, ja-JP, zh-CN)
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            headers = {
                "X-NCP-APIGW-API-KEY-ID": self.api_key,
                "X-NCP-APIGW-API-KEY": self.api_secret,
                "Content-Type": "application/octet-stream"
            }
            
            params = {"lang": language}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    params=params,
                    data=audio_data,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        transcript = result.get("text", "")
                        logger.info(f"Transcription successful, length: {len(transcript)}")
                        return transcript
                    else:
                        error_text = await response.text()
                        logger.error(f"Transcription failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None
    
    async def extract_audio_from_video(self, video_data: bytes) -> Optional[bytes]:
        """
        Extract audio track from video file
        
        Args:
            video_data: Video file content in bytes
            
        Returns:
            Audio data in bytes or None if failed
        """
        try:
            # This would require ffmpeg or similar tool
            # For now, return the video data as-is (assuming it contains audio)
            # In production, you'd use:
            # - ffmpeg to extract audio: ffmpeg -i input.mp4 -vn -acodec pcm_s16le output.wav
            # - or use python libraries like pydub, moviepy
            
            logger.warning("Audio extraction not implemented, using video data directly")
            return video_data
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return None
    
    async def transcribe_video(
        self,
        video_data: bytes,
        language: str = "ko-KR"
    ) -> Optional[str]:
        """
        Transcribe video by extracting audio and converting to text
        
        Args:
            video_data: Video file content in bytes
            language: Language code
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Extract audio from video
            audio_data = await self.extract_audio_from_video(video_data)
            if not audio_data:
                logger.error("Failed to extract audio from video")
                return None
            
            # Transcribe audio
            transcript = await self.transcribe_audio(audio_data, language)
            return transcript
            
        except Exception as e:
            logger.error(f"Error transcribing video: {e}")
            return None
