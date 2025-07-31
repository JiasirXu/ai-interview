#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI服务模块
"""

from app.services.spark_service import spark_service, SparkService
from app.services.resume_service import resume_service, ResumeService
from app.services.audio_service import audio_transcription_manager, AudioService, AudioTranscriptionManager
from app.services.vision_service import vision_service, VisionService
from app.services.avatar_service import avatar_service, AvatarService

__all__ = [
    'spark_service', 'SparkService',
    'resume_service', 'ResumeService', 
    'audio_transcription_manager', 'AudioService', 'AudioTranscriptionManager',
    'vision_service', 'VisionService',
    'avatar_service', 'AvatarService'
] 