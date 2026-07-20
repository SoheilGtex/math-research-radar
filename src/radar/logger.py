import logging
import os
from logging.handlers import RotatingFileHandler


def setup_global_logger() -> logging.Logger:
    """
    Configure enterprise-grade logging that outputs to both the console
    and a rotating log file to ensure long-term observability.
    """
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times if instantiated repeatedly
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Console Handler (for CI/CD and terminal output)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 2. File Handler (Rotating at 5MB, keeping up to 3 backups)
        file_handler = RotatingFileHandler(
            filename="logs/pipeline.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logging.getLogger("pipeline")