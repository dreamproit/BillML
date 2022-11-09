import asyncio
import itertools
import os
from datetime import datetime

import jsonlines
from dotenv import load_dotenv

from utils.datasets import (get_bills_types_folders_paths,
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
_log = setup_logging(os.path.basename(__file__))


async def main(data_folder: str, congresses: list, bill_types: list, num_bill_sections: int) -> None:
    bill_types_to_process = get_bills_types_folders_paths(
        data_folder, congresses, bill_types,
    )
    for congress, congress_bill_types_folders in bill_types_to_process.items():
        _log.debug(f'PROCESSING CONGRESS: {congress}')
        tasks = []
        for bill_type_folder in congress_bill_types_folders:
            tasks.append(
                asyncio.ensure_future(
                    process_bill_type_folder(bill_type_folder, num_bill_sections)
                )
            )
        gathered_tasks = asyncio.gather(*tasks)
        results = await gathered_tasks
        output_filepath = f'./output/{congress}_{datetime.utcnow().strftime("%d-%m-%Y_%H:%M:%S")}.jsonl'
        with open(output_filepath, 'w') as f:
            writer = jsonlines.Writer(f)
            final_bills_data = list(itertools.chain.from_iterable(results))
            writer.write_all(final_bills_data)


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
