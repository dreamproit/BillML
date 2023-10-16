#!/bin/sh

DATASETS_FOLDER="datasets_data"

if [ $BILLML_BACKUP_DATASET_DATA_CLOUD_PROVIDER = "s3" ]
    then
        # sync datasets data
        DATASETS_LOCAL_PATH=$BILLML_DATASETS_STORAGE_FILEPATH
        DATASETS_BUCKET_PATH=s3://$BILLML_BACKUP_DATASET_DATA_BUCKET_NAME/$DATASETS_FOLDER
        echo "Syncing bills data path: '$DATASETS_LOCAL_PATH' with the cloud storage: '$DATASETS_BUCKET_PATH'"
        AWS_ACCESS_KEY_ID=$BILLML_BACKUP_DATASET_DATA_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$BILLML_BACKUP_DATASET_DATA_SECRET_KEY aws s3 sync $DATASETS_LOCAL_PATH $DATASETS_BUCKET_PATH
else
    echo "Non suported cloud provider: '$BILLML_BACKUP_BILLS_DATA_CLOUD_PROVIDER'"
fi
