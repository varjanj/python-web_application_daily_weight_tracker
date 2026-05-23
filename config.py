import logging
from pathlib import Path


class Config:
    # General application settings
    APP_TITLE = "Weight Tracker & Analytics"
    SIDEBAR_TITLE = "Navigation"
    SIDEBAR_TAB1 = "Insert Weight"
    SIDEBAR_TAB2 = "History & Trends"
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

    # NEW: UI configuration
    PAGINATION_ROWS_PER_PAGE = 10
    FORECAST_WEEKS_AHEAD = 4

    # NEW: Tab Names
    TAB_SUMMARY_NAME = "📊 Summary & Trend"
    SUBHEADER1 = "Current Overview & Forecast"
    SUBHEADER2 = "Weight Trend Chart"

    TAB_BLOCKS_NAME = "🧱 Weekly Blocks"
    SUBHEADER3 = "Weekly Blocks Overview"

    TAB_HISTORY_NAME = "📜 Full History Log"
    SUBHEADER4 = "Complete History Log"

    # Color Palette for Conditional Formatting (Light Theme Pastel Colors)
    COLOR_SUCCESS_BG = "#d4edda"  # Light Green Background
    COLOR_SUCCESS_TX = "#155724"  # Dark Green Text
    
    COLOR_DANGER_BG  = "#f8d7da"  # Light Red Background
    COLOR_DANGER_TX  = "#721c24"  # Dark Red Text

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


