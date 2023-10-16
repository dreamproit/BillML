from asyncio.locks import Semaphore
from datetime import datetime
from glob import glob
from pathlib import Path
import json
import logging
import os
import re

from bs4 import BeautifulSoup
import aiofiles
import lxml

from common.constants.billml import BillMLConstants
from utils.bill_files import get_bill_file_data, get_bill_id

logger = logging.getLogger(BillMLConstants.BILLML_DEFAULT_LOGGER_NAME.value)


async def check_bill_num_of_sections(num_sections: int, bill_filepath: str) -> bool:
    """Checks bills's number of sections with provided limit and return bool of that comparison."""
    async with aiofiles.open(bill_filepath, "r") as xml:
        soup = BeautifulSoup(await xml.read(), features="xml")
    sections = soup.findAll('section')
    if not sections:
        logger.info('No sections')
        return False
    logger.info(
        f'Bill with filepath: "{bill_filepath}" has: "{len(sections)}" section(s).'
    )
    return len(sections) <= num_sections


def get_bills_types_folders_paths(
    base_folder: str, congresses: list, bills_types: list
) -> dict:
    """Gets filepaths for bill types folders."""
    congreses_bills_folders = {}
    if not congresses:
        congresses = sorted(os.listdir(base_folder))
    if not congresses:
        logger.warning(f'No congresses found in folder: {base_folder}')
        return
    for congress in congresses:
        congreses_bills_folders[int(congress)] = [
            os.path.join(base_folder, congress, 'bills', bill_type)
            for bill_type in bills_types
        ]
    return congreses_bills_folders


def get_bills_folders_with_data_json_file(root_folder):
    """Gets filepaths where 'data.json' file exists."""
    file_paths = glob(f'{root_folder}/*/data.json', recursive=True)
    return file_paths


async def get_bill_data_json_info(data_json_path: str):
    """Gets info from 'data.json' file."""
    async with aiofiles.open(data_json_path, 'r') as f:
        bill_data_json = json.loads(await f.read())
    summary = bill_data_json.get('summary')
    bill_titles = bill_data_json.get('titles')
    official_title = next(item for item in bill_titles if item['type'] == 'official')
    return {'summary': summary, 'title': official_title}


def get_bills_folders_with_document_file(bill_folder: str):
    """Gets folders where 'document.xml' file exists."""
    return glob(f'{bill_folder}/text-versions/*/document.xml', recursive=True)


def get_latest_document_filepath(document_folders: list):
    """Gets latest bill file path based on date in bill metadata."""
    NAMESPACES = {
        'dc': 'http://purl.org/dc/elements/1.1/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    }
    bills_to_compare = {}
    for document_filepath in document_folders:
        logger.info(f'Processing document filepath: {document_filepath}')
        default_date = datetime.strptime('1900-01-01', '%Y-%m-%d')
        try:
            bill_tree = lxml.etree.parse(document_filepath)
        except lxml.etree.XMLSyntaxError as exc:
            logger.error(
                f'Bill with filepath: {document_filepath} has invalid XML syntax.'
            )
            logger.exception(exc)
            continue

        try:
            bill_date = bill_tree.xpath('//dc:date/text()', namespaces=NAMESPACES)[0]
        except IndexError:
            logger.info(
                f'Bill with filepath: {document_filepath} has no date, default_date: "{default_date}" used.'
            )
            bills_to_compare[document_filepath] = default_date
            continue

        try:
            bill_date = datetime.strptime(bill_date, '%Y-%m-%d')
        except ValueError as exc:
            logger.error(
                f'Bill with filepath: {document_filepath} has invalid date format: "{bill_date}".'
            )
            logger.exception(exc)
            bills_to_compare[document_filepath] = default_date
            continue
        bills_to_compare[document_filepath] = bill_date
    if not bills_to_compare:
        logger.info(f'No bills to compare in folder: {document_folders}')
        return
    oldest_bill_document = max(bills_to_compare.items(), key=lambda x: x[1])[0]
    logger.info(
        f'Oldest bill file: "{oldest_bill_document}" with date: "{bills_to_compare[oldest_bill_document]}"'
    )
    return oldest_bill_document


def getBillParts(filename):
    """Gets dict with 'congress, billtype, billnum, billversion' from provided filename by matching with regex template."""  # noqa
    m1 = re.match(
        (
            r'(?:BILLS-)?(?P<congress>\d{3})(?P<billtype>[a-z]+)(?P<billnum>\d+)'
            r'(?P<billversion>[a-z]+)?(?:\.(?P<filetype>[a-z]{3}))?'
        ),
        filename,
    )
    if m1 is not None:
        billPartsDict = m1.groupdict()
    else:
        return None
    return billPartsDict


async def get_bill_data(bill_folder: str, num_bill_sections: int):
    """Gets all bill text data required for 'bill_summary_us' dataset row."""
    document_folders = get_bills_folders_with_document_file(bill_folder)
    if not document_folders:
        return
    latest_document_filepath = get_latest_document_filepath(document_folders)
    if not latest_document_filepath:
        return
    if num_bill_sections:
        if not await check_bill_num_of_sections(
            num_bill_sections, latest_document_filepath
        ):
            logger.info(
                f'Bill with filepath: {latest_document_filepath} has more than: {num_bill_sections} sections.'
            )
            return
    else:
        logger.info('Skipping check for number of sections.')
    bill_data = await get_bill_file_data(latest_document_filepath)
    bill_sections = bill_data.get('sections')
    bill_text = ' '.join([section_text['text'] for section_text in bill_sections])
    bill_id = get_bill_id(latest_document_filepath)
    bill_parts = getBillParts(bill_id)
    result = {
        'id': bill_id,
        'congress': bill_parts['congress'],
        'bill_type': bill_parts['billtype'],
        'bill_number': bill_parts['billnum'],
        'bill_version': bill_parts['billversion'],
        'sections': bill_sections,
        'sections_length': len(bill_sections),
        'text': bill_text,
        'text_length': len(bill_text),
    }
    logger.info(f'Got Bill data from bill file: {latest_document_filepath}')
    return result


async def process_bill_type_folder(
    data_filepath, num_bill_sections: int, concurrent_limit: Semaphore
) -> list:
    """Gets all bill data required for 'bill_summary_us' dataset row."""
    async with concurrent_limit:
        data_json = await get_bill_data_json_info(data_filepath)
        summary = data_json.get('summary')
        if not summary:
            logger.info(f'data.json with filepath: "{data_filepath}" has no summary.')
            return
        title = data_json.get('title')
        if not title:
            logger.info(f'data.json with filepath: "{data_filepath}" has no title.')
            return
        logger.info(f'Got Bill summary and title from file: "{data_filepath}"')
        bill_folder = Path(data_filepath).parent.absolute()
        bill_data = await get_bill_data(bill_folder, num_bill_sections)
        if not bill_data:
            return
        bill_data['summary'] = summary['text']
        bill_data['summary_length'] = len(summary['text'])
        bill_data['title'] = title['title']
        return bill_data
