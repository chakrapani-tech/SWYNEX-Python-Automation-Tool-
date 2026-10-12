"""SWYNEX Intelligent File Processing & Automation Platform."""

from .config import AppConfig, load_config
from .models import FileRecord, RunSummary

__all__ = ["AppConfig", "FileRecord", "RunSummary", "load_config"]
__version__ = "0.1.0"
