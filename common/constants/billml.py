import enum
import os


class BillMLConstants(enum.Enum):
    """Constants for BillML."""

    LOG_FORMAT = os.environ.get(
        'BILLML_LOG_FORMAT',
        '%(asctime)s | %(levelname)-8s | %(pathname)s:%(lineno)s | %(funcName)s | %(message)s',
    )
    LOG_OUTPUT_FOLDER = os.environ.get(
        'BILLML_LOG_OUTPUT_FOLDER',
        'logs',
    )
    LOG_FILE_BASE_NAME = os.environ.get(
        'BILLML_LOG_FILE_BASE_NAME',
        'congress_standalone',
    )
    LOG_FILE_INTERVAL_TYPE = os.environ.get(
        'BILLML_LOG_FILE_INTERVAL_TYPE',
        'midnight',
    )
    LOG_FILE_INTERVAL = int(
        os.environ.get(
            'BILLML_LOG_FILE_INTERVAL',
            1,
        )
    )
    DATA_FOLDER_FILEPATH = os.environ.get(
        'CONGRESS_DATA_FOLDER_FILEPATH',
        '/bills_data/data',
    )
    CACHE_FOLDER_FILEPATH = os.environ.get(
        'CONGRESS_CACHE_FOLDER_FILEPATH',
        '/bills_data/cache',
    )
    BILLML_DEFAULT_LOGGER_NAME = 'utils.logs.log'
    LOG_ARCHIVES_MAX_AMOUNT = 30
    LOG_ARCHIVES_MAX_TOTAL_SIZE = 3_221_225_472  # 3GB in bytes
    LOG_BASE_FILENAME_REGEX = r'(?<=)([a-z-_]+)(?=_\d)'
    LOG_FULL_FILE_NAME_REGEX = r'(?<=)({base_name})(?=_\d)'

    BILLML_DATASETS_STORAGE_FILEPATH = os.getenv(
        'BILLML_DATASETS_STORAGE_FILEPATH', '/datasets_data'
    )

    BILLML_DEFAULT_BILL_TYPES = (
        'hconres',
        'hjres',
        'hr',
        'hres',
        's',
        'sconres',
        'sjres',
        'sres',
    )

    BILLML_LOCAL_FILESYSTEM_CONCURRENCY_LIMIT = int(
        os.getenv('BILLML_LOCAL_FILESYSTEM_CONCURRENCY_LIMIT', 4000)
    )

    BILLML_BILL_SUMMARIES_US_DATASET_NAME = 'bill_summary_us'
    BILLML_BILL_TEXT_US_DATASET_NAME = 'bill_text_us'
    BILLML_BACKUP_DATASET_HF_TOKEN = os.getenv(
        'BILLML_BACKUP_DATASET_HF_TOKEN', 'your-hugging-face-token'
    )
