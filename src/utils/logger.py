import sys
from loguru import logger


def setup_logger(log_level: str = "INFO"):
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    logger.add(
        "logs/bot.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level=log_level,
        encoding="utf-8",
    )
    return logger
