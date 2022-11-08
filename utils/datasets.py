import json
import os
from datetime import datetime
from glob import glob
from pathlib import Path

from bs4 import BeautifulSoup
from lxml import etree

from utils.bill_files import get_bill_sections
from utils.logging import setup_logging

_log = setup_logging(os.path.basename(__file__))


def check_bill_num_of_sections(num_sections: int, bill_filepath: str) -> bool:
    with open(bill_filepath) as xml:
        soup = BeautifulSoup(xml, features="xml")
    sections = soup.findAll('section')
    if not sections:
        _log.debug('No sections')
        return False
    _log.debug(f'Bill with filepath: "{bill_filepath}" have: "{len(sections)}" section(s).')
    return len(sections) <= num_sections


def get_bills_types_folders_paths(base_folder: str, congresses: list, bills_types: list) -> dict:
    congreses_bills_folders = {}
    for congress in congresses:
        congreses_bills_folders[congress] = [
            os.path.join(base_folder, congress, 'bills', bill_type) for bill_type in bills_types
        ]
    return congreses_bills_folders


def get_bills_folders_with_data_json_file(root_folder):
    return glob(f'{root_folder}/*/data.json', recursive=True)


def get_bill_summary(data_json_path: str):
    with open(data_json_path, 'r') as f:
        bill_data_json = json.load(f)
    return bill_data_json.get('summary')


def get_bill_title(data_json_path: str):
    with open(data_json_path, 'r') as f:
        bill_data_json = json.load(f)
        bill_titles = bill_data_json.get('titles')
    return next(item for item in bill_titles if item['type'] == 'official')


def get_bills_folders_with_document_file(bill_folder: str):
    return glob(f'{bill_folder}/text-versions/*/document.xml', recursive=True)


def get_latest_document_filepath(document_folders: list):
    NAMESPACES = {
        'dc': 'http://purl.org/dc/elements/1.1/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    }
    bills_to_compare = {}
    for document_filepath in document_folders:
        _log.debug(f'Processing document filepath: {document_filepath}')
        bill_tree = etree.parse(document_filepath)
        try:
            bill_date = bill_tree.xpath('//dc:date/text()', namespaces=NAMESPACES)[0]
        except IndexError:
            _log.debug(f'Bill with filepath: {document_filepath} have no date.')
            bills_to_compare[document_filepath] = datetime.strptime('1900-01-01', '%Y-%m-%d')
            continue
        bills_to_compare[document_filepath] = datetime.strptime(bill_date, '%Y-%m-%d')
    oldest_bill_document = max(bills_to_compare.items(), key=lambda x: x[1])[0]
    _log.debug(f'Oldest bill file: {oldest_bill_document}')
    return oldest_bill_document


def get_bill_id(bill_filepath: str):
    parts = bill_filepath.split('/')
    return f'{parts[-7]}_{parts[-4]}_{parts[-2]}'


def get_bill_data(bill_folder: str, num_bill_sections: int):
    document_folders = get_bills_folders_with_document_file(bill_folder)
    if not document_folders:
        return
    latest_document_filepath = get_latest_document_filepath(document_folders)
    if not check_bill_num_of_sections(num_bill_sections, latest_document_filepath):
        _log.debug(
            f'Bill with filepath: {latest_document_filepath} have more than: {num_bill_sections} sections.'
        )
        return
    bill_sections = get_bill_sections(latest_document_filepath)
    bill_text = ' '.join([section_text['text'] for section_text in bill_sections])
    result = {
        'id': get_bill_id(latest_document_filepath),
        'sections': bill_sections,
        'text': bill_text,
        'text_len': len(bill_text),
    }
    return result


def process_bill_type_folder(bill_type_folder: str, num_bill_sections: int) -> list:
    _log.debug(f'PROCESSING Bill type folder: "{bill_type_folder}"')
    bill_type_result = []
    data_json_folders = get_bills_folders_with_data_json_file(bill_type_folder)
    for data_filepath in data_json_folders:
        summary = get_bill_summary(data_filepath)
        if not summary:
            _log.debug(f'data.json with filepath: "{data_filepath}" have no summary.')
            continue
        _log.debug(f'PROCESSING Bill summary from file: "{data_filepath}"')
        title = get_bill_title(data_filepath)
        bill_folder = Path(data_filepath).parent.absolute()
        _log.debug(f'PROCESSING Bill data from folder: {bill_folder}')
        bill_data = get_bill_data(bill_folder, num_bill_sections)
        if not bill_data:
            continue
        bill_data['summary'] = summary['text']
        bill_data['summary_len'] = len(summary['text'])
        bill_data['title'] = title['title']
        bill_type_result.append(bill_data)
    return bill_type_result
