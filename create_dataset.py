import asyncio
import os
from datetime import datetime

import jsonlines
from dotenv import load_dotenv

from utils.datasets import (get_bills_folders_with_data_json_file,
                            get_bills_types_folders_paths,
                            process_bill_type_folder)
from utils.logging import setup_logging

load_dotenv()

TARGET_NUMBER_OF_BILL_SECTIONS = int(os.getenv('TARGET_NUMBER_OF_BILL_SECTIONS', 10))
BILLS_DATA_FOLDER = os.getenv('BILLS_DATA_FOLDER')
CONGRESSES_TO_PROCESS = list(filter(None, os.getenv('CONGRESSES_TO_PROCESS', '117,').split(',')))
BILL_TYPES_TO_PROCESS = list(
    filter(
        None, os.getenv(
            'BILL_TYPES_TO_PROCESS', 'hconres,hjres,hr,hres,s,sconres,sjres,sres'
        ).split(',')
    )
)
CONCURRENCY_LIMIT = int(os.getenv('CONCURRENCY_LIMIT', 4000))
_log = setup_logging(os.path.basename(__file__))


async def main(data_folder: str, congresses: list, bill_types: list, num_bill_sections: int) -> None:
    concurrent_limit = asyncio.Semaphore(CONCURRENCY_LIMIT)
    bill_types_to_process = get_bills_types_folders_paths(
        data_folder, congresses, bill_types,
    )
    tasks = []
    for congress, congress_bill_types_folders in bill_types_to_process.items():
        _log.debug(f'PROCESSING CONGRESS: {congress}')
        for bill_type_folder in congress_bill_types_folders:
            _log.debug(f'PROCESSING Bill type folder: {bill_type_folder}')
            data_json_folders = get_bills_folders_with_data_json_file(bill_type_folder)
            for data_filepath in data_json_folders:
                tasks.append(
                    asyncio.ensure_future(
                        process_bill_type_folder(data_filepath, num_bill_sections, concurrent_limit)
                    )
                )
        gathered_tasks = asyncio.gather(*tasks)
        results = await gathered_tasks

        results = (item for item in results if item)
        output_filepath = f'./output/{congress}_{datetime.utcnow().strftime("%d-%m-%Y_%H:%M:%S")}.jsonl'
        with open(output_filepath, 'w') as f:
            writer = jsonlines.Writer(f)
            writer.write_all(results)


if __name__ == '__main__':
    start_time = datetime.now()
    asyncio.run(
        main(
            data_folder=BILLS_DATA_FOLDER,
            congresses=CONGRESSES_TO_PROCESS,
            bill_types=BILL_TYPES_TO_PROCESS,
            num_bill_sections=TARGET_NUMBER_OF_BILL_SECTIONS,
        )
    )
    time_elapsed = datetime.now() - start_time
    _log.debug('Program exection time (hh:mm:ss.ms) {}'.format(time_elapsed))
