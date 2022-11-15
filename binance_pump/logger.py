import sys

from loguru import logger

console_log_level: str = "DEBUG"
file_log_level: str = "TRACE"


# remove existing handlers (or handler?)
logger.remove()

# ----- add console handler
logger.add(
    sys.stdout,
    format="<green>{time:YYMMDD HH:mm:ss.SSS}</green> <level>{level:5s}</level>  {message}",
    colorize=True,
    level=console_log_level,
)
