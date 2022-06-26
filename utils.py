import os
import logging

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT_DIR, "log")


def get_logger(name, file_path=None):
    logger = logging.getLogger(name=name)
    logger.setLevel("DEBUG")
    if file_path:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handler = logging.FileHandler(file_path)

    else:
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
        file_handler = logging.FileHandler(os.path.join(LOG_DIR, "log.txt"))

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
