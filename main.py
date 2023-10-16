from datetime import datetime
import logging

import asyncclick as click

from common.constants.billml import BillMLConstants
from core.bill_summaries import create_dataset as create_bill_summaries_dataset
from core.bill_texts import create_dataset as create_bill_text_dataset

logger = logging.getLogger(BillMLConstants.BILLML_DEFAULT_LOGGER_NAME.value)

SUPPORTED_DATASETS_MAPPING = {
    BillMLConstants.BILLML_BILL_SUMMARIES_US_DATASET_NAME.value: create_bill_summaries_dataset,
    BillMLConstants.BILLML_BILL_TEXT_US_DATASET_NAME.value: create_bill_text_dataset,
}


@click.command()
@click.option(
    '-dn',
    '--dataset_names',
    'dataset_names',
    required=False,
    multiple=True,
    help='The name of the dataset(s) to create.',
)
@click.option(
    '-sl',
    '--sections_limit',
    'sections_limit',
    required=False,
    multiple=False,
    help=(
        'The number of sections that bill should have to be included in the dataset. '
        'We will include all bills with number of sections >= sections_limit.'
    ),
)
@click.option(
    '-cti',
    '--congresses_to_include',
    'congresses_to_include',
    required=False,
    multiple=True,
    help='Series of congress numbers to include in the dataset.If not provided, all congresses will be included.',
)
@click.option(
    '-bti',
    '--bill_types_to_include',
    'bill_types_to_include',
    required=False,
    multiple=True,
    default=BillMLConstants.BILLML_DEFAULT_BILL_TYPES.value,
    help='Series of bill types to include in the dataset. If not provided, all bill types will be included.',
)
async def main(
    dataset_names: tuple = None,
    sections_limit: int = None,
    congresses_to_include: tuple = None,
    bill_types_to_include: tuple = None,
) -> None:
    """Main func for creation of a dataset via CLI commands."""
    for dataset_name in dataset_names:
        try:
            handler_func = SUPPORTED_DATASETS_MAPPING[dataset_name]
        except KeyError as exc:
            logger.error(f'Unsupported dataset name: "{dataset_name}".')
            logger.exception(exc)
            continue
        output_filepath = (
            f'{BillMLConstants.BILLML_DATASETS_STORAGE_FILEPATH.value}/{dataset_name}/'
            f'{dataset_name}_{datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")}.jsonl'
        )
        logger.info(
            f'Creating dataset: "{dataset_name}" with params: '
            f'congresses={congresses_to_include}, bill_types={bill_types_to_include}, '
            f'output_filepath={output_filepath}.'
        )
        # logger.info(f'Dataset handler function: "{handler_func.__name__}".')
        await handler_func(
            data_folder=BillMLConstants.DATA_FOLDER_FILEPATH.value,
            congresses=congresses_to_include,
            bill_types=bill_types_to_include,
            num_bill_sections=sections_limit,
            output_filepath=output_filepath,
        )


if __name__ == '__main__':

    from utils.logs.log import project_logger as logger

    try:
        main(_anyio_backend='asyncio')  # or asyncio
    except Exception as exc:
        logger.error('Error durring dataset creation:')
        logger.exception(exc)
