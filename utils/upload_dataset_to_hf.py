from huggingface_hub import HfApi
import click

from common.constants.billml import BillMLConstants


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
    '-hfdn',
    '--hf_dataset_name',
    'hf_dataset_name',
    required=False,
    multiple=False,
    help='The filepath of the sample dataset.',
)
@click.option(
    '-hfpir',
    '--hf_path_in_repo',
    'hf_path_in_repo',
    required=False,
    multiple=False,
    help='The filepath of the sample dataset.',
)
def main(
    source_dataset_filepath: str = None,
    hf_dataset_name: str = None,
    hf_path_in_repo: str = None,
) -> None:
    """Uploads dataset to hugging face."""
    if not source_dataset_filepath or not hf_dataset_name or not hf_path_in_repo:
        logger.error(
            'Please provide the filepath of the source dataset and the name of the dataset on hugging face and file '
            'path for dataset name inside hugging face repo.'
        )
        return
    api = HfApi(
        token=BillMLConstants.BILLML_BACKUP_DATASET_HF_TOKEN.value,
    )
    api.upload_file(
        path_or_fileobj=source_dataset_filepath,
        path_in_repo=hf_path_in_repo,
        repo_id=hf_dataset_name,
        repo_type="dataset",
    )
    logger.info(f'Dataset "{hf_dataset_name}" uploaded to hugging face.')


if __name__ == '__main__':

    from utils.logs.log import project_logger as logger

    main()
