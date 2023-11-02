from itertools import islice
import pathlib
import random
import subprocess

import click
import jsonlines


@click.command()
@click.option(
    '-sdfp',
    '--source_dataset_filepath',
    'source_dataset_filepath',
    required=False,
    multiple=False,
    help='The filepath of the source dataset.',
)
@click.option(
    '-ofp',
    '--output_filepath',
    'output_filepath',
    required=False,
    multiple=False,
    help='The filepath of the sample dataset.',
)
@click.option(
    '-ni',
    '--number_of_items',
    'number_of_items',
    required=False,
    multiple=False,
    default=10,
    help='The number of items from original dataset that must be included in the sample dataset.',
)
def main(
    number_of_items: int,
    source_dataset_filepath: str = None,
    output_filepath: str = None,
) -> None:
    """Create sample dataset from original dataset."""
    if not source_dataset_filepath:
        logger.error('Please provide the filepath of the source dataset.')
        return
    if not output_filepath:
        source_dataset_filename = pathlib.Path(source_dataset_filepath).name
        default_directory = f'samples/{number_of_items}_{source_dataset_filename}'
        logger.warning(
            'No output filepath provided. The sample dataset will be saved in the default directory: '
            f'"{default_directory}".'
        )
        output_filepath = default_directory

    output = subprocess.check_output(["wc", "-l", source_dataset_filepath])
    total_num_lines = int(output.split()[0])

    logger.info(f'Number of lines in the source dataset: "{total_num_lines}".')
    random_line_numbers = random.sample(range(1, total_num_lines + 1), number_of_items)
    logger.info(f'For the sample dataset selected lines: "{random_line_numbers}".')
    with jsonlines.open(output_filepath, mode='w') as writer:
        for line_number in sorted(random_line_numbers):
            with open(source_dataset_filepath, mode='r') as f:
                item_place = range(line_number - 1, line_number + 1)
                item = jsonlines.Reader(islice(f, *item_place)).read()
                writer.write(item)

    logger.info(f'Sample dataset saved in "{output_filepath}".')


if __name__ == '__main__':

    from utils.logs.log import project_logger as logger

    main()
