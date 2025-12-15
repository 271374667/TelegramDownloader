"""
Core module for Telegram Downloader GUI
Contains configuration management and batch generation logic
"""

from .config_manager import SessionConfig, DownloadConfig, FullConfig
from .batch_generator import BatchGenerator

__all__ = ['SessionConfig', 'DownloadConfig', 'FullConfig', 'BatchGenerator']