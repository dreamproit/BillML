from asyncio.locks import Semaphore
from glob import glob
import logging

from common.constants.billml import BillMLConstants
from utils.bill_files import get_bill_file_data
from utils.bill_summaries import check_bill_num_of_sections, get_bill_id, getBillParts

logger = logging.getLogger(BillMLConstants.BILLML_DEFAULT_LOGGER_NAME.value)


def get_bills_folders_with_document_file(bill_folder: str):
    """Gets all folders where 'document.xml' exists."""
    folders = glob(f'{bill_folder}/*/text-versions/*/document.xml', recursive=True)
    return folders


async def process_text_version_folder(
    data_filepath, num_bill_sections: int, concurrent_limit: Semaphore
) -> list:
    """Gets all bill data required for 'bill_text_us' dataset row."""
    async with concurrent_limit:
        if num_bill_sections:
            if not await check_bill_num_of_sections(num_bill_sections, data_filepath):
                logger.info(
                    f'Bill with filepath: {data_filepath} has more than: {num_bill_sections} sections.'
                )
                return
        bill_data = await get_bill_file_data(data_filepath)
        bill_sections = bill_data.get('sections')
        bill_title = bill_data.get('title')
        bill_text = ' '.join([section_text['text'] for section_text in bill_sections])
        bill_id = get_bill_id(data_filepath)
        bill_parts = getBillParts(bill_id)
        result = {
            'id': bill_id,
            'congress': bill_parts['congress'],
            'bill_type': bill_parts['billtype'],
            'bill_number': bill_parts['billnum'],
            'bill_version': bill_parts['billversion'],
            'title': bill_title,
            'sections': bill_sections,
            'sections_length': len(bill_sections),
            'text': bill_text,
            'text_length': len(bill_text),
        }
        logger.info(f'Got all required bill data from bill file: "{data_filepath}".')
        return result
