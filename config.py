import logging
from pathlib import Path


class Config:
    # General application settings
    APP_TITLE = "Weight Tracker & Analytics"
    DATA_FILE_NAME = "weight_data.csv"
    AVERAGE_DAYS_WINDOW = 7
    WELCOME_MESSAGE = "Welcome! This will be your daily weight tracker."

    # Logging settings
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

    # Define log directory and file using pathlib
    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "weight_tracker.log"

    @classmethod
    def initialize_project(cls):
        # Create logs directory if it does not exist
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Configure the logging system
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format=cls.LOG_FORMAT,
            datefmt=cls.LOG_DATE_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )


