import logging
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Проверяем, есть ли уже обработчики
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler_file = logging.FileHandler("log.log", mode="w")
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler_file.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(handler_file)
    return logger
