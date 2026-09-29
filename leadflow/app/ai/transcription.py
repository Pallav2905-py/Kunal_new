"""
LeadFlow — Speech-to-Text Service
Uses faster-whisper. Designed to be swappable with other STT providers.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)

SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}


@runtime_checkable
class STTProvider(Protocol):
    """
    Protocol for speech-to-text providers.
    Implement this to swap Whisper for another provider.
    """

    def transcribe(self, audio_path: str) -> tuple[str, float]:
        """
        Transcribe audio file.
        Returns: (transcript_text, duration_seconds)
        """
        ...


class WhisperProvider:
    """
    faster-whisper based STT provider.
    Model is loaded once and reused across calls.
    """

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None  # lazy load

    def _load_model(self):
        if self._model is None:
            logger.info(
                f"Loading Whisper model: {self.model_size} "
                f"device={self.device} compute_type={self.compute_type}"
            )
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                )
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
        return self._model

    def transcribe(self, audio_path: str) -> tuple[str, float]:
        """Transcribe audio. Returns (text, audio_duration)."""
        start = time.time()
        model = self._load_model()

        logger.info(f"Transcribing: {audio_path}")
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language=None,  # auto-detect
            vad_filter=True,
        )

        transcript_parts = []
        for segment in segments:
            transcript_parts.append(segment.text.strip())

        transcript = " ".join(transcript_parts).strip()
        elapsed = time.time() - start
        duration = getattr(info, "duration", 0.0) or 0.0

        logger.info(
            f"Transcription completed in {elapsed:.1f}s, "
            f"audio duration={duration:.1f}s, "
            f"chars={len(transcript)}"
        )
        return transcript, duration


class TranscriptionService:
    """
    Transcription service. Validates file then delegates to STT provider.
    """

    def __init__(self, provider: STTProvider) -> None:
        self.provider = provider

    def validate_audio_file(self, file_path: str) -> None:
        """Raise ValueError if file is invalid."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
            raise ValueError(
                f"Unsupported audio format: {path.suffix}. "
                f"Supported: {', '.join(SUPPORTED_AUDIO_EXTENSIONS)}"
            )

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 200:
            raise ValueError(f"Audio file too large: {size_mb:.1f}MB (max 200MB)")

    def transcribe(self, audio_path: str) -> tuple[str, float]:
        """
        Validate and transcribe audio.
        Returns: (transcript_text, audio_duration_seconds)
        Raises on validation or transcription failure.
        """
        self.validate_audio_file(audio_path)
        try:
            transcript, duration = self.provider.transcribe(audio_path)
            if not transcript.strip():
                raise ValueError("Transcription produced empty output — check audio quality")
            return transcript, duration
        except Exception as e:
            logger.error(f"Transcription failed for {audio_path}: {e}")
            raise RuntimeError(f"Transcription failed: {e}") from e


def create_transcription_service() -> TranscriptionService:
    """Factory using settings configuration."""
    from app.config import settings
    provider = WhisperProvider(
        model_size=settings.whisper_model_size,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )
    return TranscriptionService(provider)
