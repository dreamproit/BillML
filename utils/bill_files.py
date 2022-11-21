import os
import re

import aiofiles
from bs4 import BeautifulSoup
from bs4.element import Tag
from lxml import etree

NAMESPACES = {'uslm': 'https://xml.house.gov/schemas/uslm/1.0'}


def _get_text(element, sep='\n'):
    """
    recursive parsing and cleaning of text from beatiful soup elements
    :param element: bs4.element.Tag
    :param sep: separotor between elements
    :return:
    """
    children = []
    if isinstance(element, Tag):
        children = list(element.children)
    if not children:
        txt = element.getText().strip()
        txt = re.sub(' +', ' ', txt)
        return txt.replace('\n', '')
    text = ''
    for child in children:
        text += _get_text(child, sep) + ' '
    if element.name == 'header':
        # better to separate text if it's a header
        sep = '\n'
    return text + sep if text else ''


def parse_soup_section(section):
    raw_text = _get_text(section, sep=' ')
    raw_text = re.sub(' +', ' ', raw_text)
    raw_text = raw_text.replace(' .', '.')
    raw_text = re.sub('\n ?', '\n', raw_text)
    raw_text = re.sub('\n+', '\n', raw_text).strip()
    section_id = section.attrs.get('id')
    nested = []
    info = {'text': raw_text,
            'id': section_id}
    for child in section.children:
        if not isinstance(child, Tag):
            continue
        if child.name in ('header', 'heading'):
            info['header'] = child.text
        if 'subsection' in child.name:
            nested.append(parse_soup_section(child))
    if nested:
        info['nested'] = nested
    return info


def _get_file_ext(filename):
    return filename.split('.')[-1]


def get_all_file_paths(root_folder, ext):
    """
    Recursive reading folder including all subfolders to find
    all files with required extension

    :param root_folder: folder to scan
    :param ext: file extension to grab
    :return: list of full filenames to read
    """
    filenames = list()
    for root_path, folders, files in os.walk(root_folder):
        filenames += [os.path.join(root_path, f) for f in files if _get_file_ext(f) == ext]
        for folder in folders:
            filenames += get_all_file_paths(folder, ext)
    return filenames


def get_enum(section) -> str:
    enum_path = section.xpath('enum')
    if len(enum_path) > 0:
        return enum_path[0].text
    return ''


def get_header(section) -> str:
    header_path = section.xpath('header')
    if len(header_path) > 0:
        return header_path[0].text
    return ''


def sec_to_dict(section):
    data = {'section_text': etree.tostring(section, method="text", encoding="unicode"),
            'section_xml': etree.tostring(section, method="xml", encoding="unicode"),
            'section_number': '',
            'section_header': ''}
    if (section.xpath('header') and len(section.xpath('header')) > 0
            and section.xpath('enum') and len(section.xpath('enum')) > 0):
        data['section_number'] = get_enum(section)
        data['section_header'] = get_header(section)
    return data


def xml_to_sections(xml_path: str):
    """
    Parses the xml file into sections
    """
    bill_tree = etree.parse(xml_path)
    sections = bill_tree.xpath('//uslm:section', namespaces=NAMESPACES)
    if len(sections) == 0:
        print('No sections found in ', xml_path)
        return []
    return [sec_to_dict(section) for section in sections]


def xml_to_text(xml_path: str, level: str = 'section', separator: str = '\n*****\n') -> str:
    """
    Parses the xml file and returns the text of the body element, if any
    """
    bill_tree = etree.parse(xml_path)
    sections = bill_tree.xpath('//uslm:' + level, namespaces=NAMESPACES)
    if not sections:
        print('No sections found')
        return ''
    return separator.join([etree.tostring(section, method="text", encoding="unicode") for section in sections])


async def get_bill_sections(bill_filepath: str):
    async with aiofiles.open(bill_filepath, "r") as xml:
        soup = BeautifulSoup(await xml.read(), features="xml")
    sections = soup.findAll('section')
    parsed = [parse_soup_section(sec) for sec in sections]
    return parsed
