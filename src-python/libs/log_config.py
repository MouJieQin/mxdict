import sys
import io
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from colorama import init, Fore, Style

init(autoreset=True)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class CustomFormatter(logging.Formatter):
    LEVEL_COLOR = {
        logging.DEBUG: Fore.LIGHTBLACK_EX,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.LIGHTRED_EX
    }
    RESET = Style.RESET_ALL

    def format(self, record):
        time_str = self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")
        color = self.LEVEL_COLOR.get(record.levelno, "")
        level_str = f"{color}[{record.levelname.lower()}]{self.RESET}"
        thread_str = f"[thread {record.thread}]"
        file_line_str = f"[{record.filename}:{record.lineno}]"
        msg = record.getMessage()

        full_line = f"[{time_str}] {level_str} {thread_str} {file_line_str} {msg}"
        return full_line


def setup_logger():
    logger = logging.getLogger()
    logger.handlers.clear()

    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_level_name = os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_name, logging.INFO)
    logger.setLevel(log_level)

    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [thread %(thread)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = TimedRotatingFileHandler(
        filename="logs/run.log",
        when="D",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()