import asyncio
import logging

from common.constants.billml import BillMLConstants
from schemas.bill_texts import BillTextUsItemSchema
from utils.bill_files import save_jsonl_file
from utils.bill_summaries import get_bills_types_folders_paths
from utils.bill_texts import get_bills_folders_with_document_file, process_text_version_folder

logger = logging.getLogger(BillMLConstants.BILLML_DEFAULT_LOGGER_NAME.value)


async def create_bill_texts_dataset_tasks(
    congress_bill_types_folders, num_bill_sections, concurrent_limit
):
    tasks = []
    for bill_type_folder in congress_bill_types_folders:
        text_versions_folders = get_bills_folders_with_document_file(bill_type_folder)
        logger.info(
            f'Creating tasks for bill type folder: "{bill_type_folder}" with "{len(text_versions_folders)}" '
            'text-versions folders.'
        )
        for data_filepath in text_versions_folders:
            tasks.append(
                asyncio.ensure_future(
                    process_text_version_folder(
                        data_filepath, num_bill_sections, concurrent_limit
                    )
                )
            )
    return tasks


async def create_dataset(
    data_folder: str,
    output_filepath: str,
    congresses: list = '*',
    bill_types: list = BillMLConstants.BILLML_DEFAULT_BILL_TYPES.value,
    num_bill_sections: int = None,
) -> None:
    """Creates 'bill_text_us' dataset from uscongress bills data."""
    concurrent_limit = asyncio.Semaphore(
        BillMLConstants.BILLML_LOCAL_FILESYSTEM_CONCURRENCY_LIMIT.value
    )
    bill_types_to_process = get_bills_types_folders_paths(
        data_folder,
        congresses,
        bill_types,
    )
    for congress, congress_bill_types_folders in bill_types_to_process.items():
        tasks = await create_bill_texts_dataset_tasks(
            congress_bill_types_folders, num_bill_sections, concurrent_limit
        )
        if tasks:
            logger.info(
                f'Starting processing number of tasks: "{len(tasks)}" for congress: "{congress}".'
            )
            gathered_tasks = asyncio.gather(*tasks)
            results = await gathered_tasks

            results = [
                BillTextUsItemSchema(**item).model_dump() for item in results if item
            ]
            logger.info(
                f'Congress: "{congress}" have "{len(results)}" bills with required data.'
            )
            save_jsonl_file(results, output_filepath)
            del tasks
            del gathered_tasks
            del results
