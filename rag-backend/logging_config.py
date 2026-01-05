"""
Logging configuration for ingestion and query tracking
Provides structured logging for RAG operations
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Log levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']

        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"

        return super().format(record)


def setup_logger(
    name: str = "rag_backend",
    level: int = INFO,
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup and configure a logger for RAG operations.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs
        console: Whether to output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()  # Remove existing handlers

    # Console handler with colors
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler (plain text, no colors)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class IngestionLogger:
    """
    Specialized logger for tracking ingestion operations.
    Provides methods for logging ingestion progress and statistics.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the ingestion logger.

        Args:
            log_file: Optional file path for persistent logs
        """
        self.logger = setup_logger(
            name="ingestion",
            level=INFO,
            log_file=log_file,
            console=True
        )
        self.stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }

    def start(self):
        """Mark the start of an ingestion job"""
        self.stats["start_time"] = datetime.now()
        self.logger.info("=" * 60)
        self.logger.info("INGESTION JOB STARTED")
        self.logger.info(f"Start time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)

    def log_file_processing(self, file_path: str):
        """Log processing of a file"""
        self.stats["files_processed"] += 1
        self.logger.info(f"Processing file [{self.stats['files_processed']}]: {file_path}")

    def log_chunks_created(self, count: int, file_path: str):
        """Log chunk creation"""
        self.stats["chunks_created"] += count
        self.logger.info(f"  [OK] Created {count} chunks from {Path(file_path).name}")

    def log_embeddings_generated(self, count: int):
        """Log embedding generation"""
        self.stats["embeddings_generated"] += count
        self.logger.debug(f"  [OK] Generated {count} embeddings")

    def log_upload(self, count: int):
        """Log vector upload to Qdrant"""
        self.logger.info(f"  [OK] Uploaded {count} vectors to Qdrant")

    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log an error"""
        self.stats["errors"] += 1
        self.logger.error(f"  [ERROR] {message}")
        if exception:
            self.logger.error(f"    Exception: {str(exception)}")

    def complete(self):
        """Mark completion and print statistics"""
        self.stats["end_time"] = datetime.now()
        duration = self.stats["end_time"] - self.stats["start_time"]

        self.logger.info("=" * 60)
        self.logger.info("INGESTION JOB COMPLETED")
        self.logger.info(f"End time: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Duration: {duration}")
        self.logger.info("-" * 60)
        self.logger.info("STATISTICS:")
        self.logger.info(f"  Files processed: {self.stats['files_processed']}")
        self.logger.info(f"  Chunks created: {self.stats['chunks_created']}")
        self.logger.info(f"  Embeddings generated: {self.stats['embeddings_generated']}")
        self.logger.info(f"  Errors: {self.stats['errors']}")

        if self.stats["chunks_created"] > 0:
            chunks_per_file = self.stats["chunks_created"] / self.stats["files_processed"]
            self.logger.info(f"  Average chunks per file: {chunks_per_file:.1f}")

        self.logger.info("=" * 60)

        if self.stats["errors"] > 0:
            self.logger.warning(f"[WARNING] Completed with {self.stats['errors']} errors")
        else:
            self.logger.info("[SUCCESS] Completed successfully with no errors")

        return self.stats


class QueryLogger:
    """
    Specialized logger for tracking query operations.
    Logs RAG queries, retrievals, and response generation.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the query logger.

        Args:
            log_file: Optional file path for persistent logs
        """
        self.logger = setup_logger(
            name="query",
            level=INFO,
            log_file=log_file,
            console=True
        )

    def log_query(self, query: str, user_id: Optional[str] = None):
        """Log an incoming query"""
        user_info = f" (user: {user_id})" if user_id else ""
        self.logger.info(f"Query received{user_info}: {query[:100]}...")

    def log_retrieval(self, num_chunks: int, query_time_ms: float):
        """Log vector retrieval"""
        self.logger.info(f"  Retrieved {num_chunks} chunks in {query_time_ms:.2f}ms")

    def log_response(self, response_length: int, total_time_ms: float):
        """Log response generation"""
        self.logger.info(f"  Generated response ({response_length} chars) in {total_time_ms:.2f}ms")

    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log a query error"""
        self.logger.error(f"  ✗ Query error: {message}")
        if exception:
            self.logger.error(f"    Exception: {str(exception)}")


# Global logger instances
_ingestion_logger = None
_query_logger = None


def get_ingestion_logger(log_file: Optional[str] = None) -> IngestionLogger:
    """
    Get or create the global ingestion logger.

    Args:
        log_file: Optional file path for logs

    Returns:
        IngestionLogger instance
    """
    global _ingestion_logger
    if _ingestion_logger is None:
        _ingestion_logger = IngestionLogger(log_file=log_file)
    return _ingestion_logger


def get_query_logger(log_file: Optional[str] = None) -> QueryLogger:
    """
    Get or create the global query logger.

    Args:
        log_file: Optional file path for logs

    Returns:
        QueryLogger instance
    """
    global _query_logger
    if _query_logger is None:
        _query_logger = QueryLogger(log_file=log_file)
    return _query_logger


if __name__ == "__main__":
    # Test the logging configuration
    print("Testing Ingestion Logger:")
    ing_logger = get_ingestion_logger()
    ing_logger.start()
    ing_logger.log_file_processing("test/chapter1.md")
    ing_logger.log_chunks_created(5, "test/chapter1.md")
    ing_logger.log_embeddings_generated(5)
    ing_logger.log_upload(5)
    ing_logger.log_error("Sample error", Exception("Test exception"))
    stats = ing_logger.complete()

    print("\n" + "=" * 60)
    print("Testing Query Logger:")
    query_logger = get_query_logger()
    query_logger.log_query("What is physical AI?", user_id="user123")
    query_logger.log_retrieval(3, 45.5)
    query_logger.log_response(250, 180.2)
