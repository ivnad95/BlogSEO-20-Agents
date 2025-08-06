"""Logger utility with colored console output and Streamlit support."""

import logging
import sys
from typing import Optional, Union
from enum import Enum

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class LogLevel(Enum):
    """Log levels enum."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        logging.DEBUG: Fore.CYAN if COLORAMA_AVAILABLE else "",
        logging.INFO: Fore.GREEN if COLORAMA_AVAILABLE else "",
        logging.WARNING: Fore.YELLOW if COLORAMA_AVAILABLE else "",
        logging.ERROR: Fore.RED if COLORAMA_AVAILABLE else "",
        logging.CRITICAL: Fore.RED + Style.BRIGHT if COLORAMA_AVAILABLE else "",
    }
    
    RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else ""
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.msg = f"{log_color}{record.msg}{self.RESET}"
        return super().format(record)


class BlogLogger:
    """Enhanced logger with Streamlit and colored console support."""
    
    def __init__(
        self,
        name: str = "BlogSEO",
        level: Union[LogLevel, int] = LogLevel.INFO,
        use_streamlit: bool = True,
        use_console: bool = True,
        log_file: Optional[str] = None
    ):
        self.name = name
        self.use_streamlit = use_streamlit and STREAMLIT_AVAILABLE
        self.use_console = use_console
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value if isinstance(level, LogLevel) else level)
        self.logger.handlers.clear()
        
        # Console handler with colors
        if use_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level.value if isinstance(level, LogLevel) else level)
            
            if COLORAMA_AVAILABLE:
                console_format = ColoredFormatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            else:
                console_format = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level.value if isinstance(level, LogLevel) else level)
            file_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, streamlit_display: bool = False):
        """Log debug message."""
        self.logger.debug(message)
        if self.use_streamlit and streamlit_display:
            st.text(f"🔍 DEBUG: {message}")
    
    def info(self, message: str, streamlit_display: bool = True):
        """Log info message."""
        self.logger.info(message)
        if self.use_streamlit and streamlit_display:
            st.info(message)
    
    def warning(self, message: str, streamlit_display: bool = True):
        """Log warning message."""
        self.logger.warning(message)
        if self.use_streamlit and streamlit_display:
            st.warning(message)
    
    def error(self, message: str, streamlit_display: bool = True):
        """Log error message."""
        self.logger.error(message)
        if self.use_streamlit and streamlit_display:
            st.error(message)
    
    def critical(self, message: str, streamlit_display: bool = True):
        """Log critical message."""
        self.logger.critical(message)
        if self.use_streamlit and streamlit_display:
            st.error(f"🚨 CRITICAL: {message}")
    
    def success(self, message: str, streamlit_display: bool = True):
        """Log success message (info level with special formatting)."""
        self.logger.info(f"✅ {message}")
        if self.use_streamlit and streamlit_display:
            st.success(message)
    
    def progress(self, message: str, progress_value: Optional[float] = None):
        """Show progress message."""
        self.logger.info(f"⏳ {message}")
        if self.use_streamlit:
            if progress_value is not None:
                st.progress(progress_value, text=message)
            else:
                st.spinner(message)


# Global logger instance
logger = BlogLogger()


def get_logger(name: Optional[str] = None, **kwargs) -> BlogLogger:
    """Get a logger instance.
    
    Args:
        name: Logger name (default: BlogSEO)
        **kwargs: Additional arguments for BlogLogger
    
    Returns:
        BlogLogger instance
    """
    if name:
        return BlogLogger(name=name, **kwargs)
    return logger
