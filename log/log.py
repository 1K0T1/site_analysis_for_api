from loguru import logger
import logging
from pathlib import Path

path_log = Path(__file__).parent / "server.log"
# path_log.mkdir(parents=True, exist_ok=True)


# логирование
def log_server():
    werk = logging.getLogger("werkzeug")
    flsk = logging.getLogger("flask.app")

    werk.handlers.clear()
    flsk.handlers.clear()

    logger.remove()
    logger.add(
        path_log,
        level="INFO",
        format="<green>{time: YYYY-MM-DD HH-ss-mm}</green> | <yellow>{level}</yellow> | {name}:{function}:{line} - <level>{message}</level> - {exception}",
        rotation="20 MB",
        retention="2 days",
    )
