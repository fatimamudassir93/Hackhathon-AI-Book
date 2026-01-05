"""
Ingestion status logging and error reporting
Wrapper around logging_config for ingestion-specific logging
"""
from logging_config import IngestionLogger, get_ingestion_logger

# Re-export for convenience
__all__ = ['IngestionLogger', 'get_ingestion_logger']

# This module serves as an alias/wrapper for the logging_config module
# The actual implementation is in logging_config.py (created in T010)
