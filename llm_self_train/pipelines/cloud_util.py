from pipelines import config
import os
from google.cloud.storage import Client
from tqdm import tqdm


def upload_dir_to_gcp(source_dir, destination_blob_prefix, bucket_name=config['bucket_name']):
    ''' 
    Uploads a directory to a given destination in GCP storage.

    source_dir: The local directory to upload.
    destination_blob_prefix: The destination directory in GCP storage.
    bucket_name: The name of the bucket to upload to.
    '''
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)
    files_to_upload = [os.path.join(root, file) for root, _, files in os.walk(
        source_dir) for file in files]

    for local_file_path in tqdm(files_to_upload, desc="Uploading files"):
        relative_path = os.path.relpath(local_file_path, source_dir)
        blob_path = os.path.join(destination_blob_prefix, relative_path)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(local_file_path)


def download_dir_from_gcp(source_blob_prefix, destination_dir, bucket_name=config['bucket_name']):
    '''
    Downloads a directory from a given source in GCP storage.

    source_blob_prefix: The source directory in GCP storage.
    destination_dir: The local directory to download to.
    bucket_name: The name of the bucket to download from.
    '''
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = list(bucket.list_blobs())
    blob_paths = [blob.name for blob in blobs]

    for blob_path in tqdm(blob_paths, desc="Downloading files"):
        local_file_path = os.path.join(
            destination_dir, os.path.relpath(blob_path, source_blob_prefix))
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        blob = bucket.blob(blob_path)
        blob.download_to_filename(local_file_path)


def download_files_from_gcp(files_to_download, local_download_dir, bucket_name=config['bucket_name']):
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)

    for file_path in files_to_download:
        blob = bucket.blob(file_path)
        local_path = os.path.join(local_download_dir, file_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        print(f"Downloaded {file_path} to {local_download_dir}")


def list_blobs_with_prefix(directory, prefix, delimiter=None, bucket_name=config['bucket_name']):
    '''
    Lists all blobs in a given bucket with a given prefix.

    bucket_name: The name of the bucket to list blobs from.
    prefix: The prefix to filter blobs by.
    delimiter: The delimiter to use for filtering blobs.
    '''
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)

    if not directory.endswith('/'):
        directory += '/'

    full_prefix = f"{directory}{prefix}"
    blobs = bucket.list_blobs(prefix=full_prefix, delimiter=delimiter)
    # filter out directories, remain files
    return set(blob.name for blob in blobs if not blob.name.endswith('/'))


def check_gcp_directory_exists(directory, bucket_name=config['bucket_name']):
    if not directory.endswith('/'):
        directory += '/'

    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=directory, max_results=1)

    for _ in blobs:
        return True
    return False