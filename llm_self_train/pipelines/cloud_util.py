<<<<<<< HEAD
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


async def monitor_local_and_upload_to_gcp(directory_to_monitor, check_interval=60, should_stop=lambda: False, bucket_name=config['bucket_name']):
    '''
    Monitors a directory and uploads new subdirectories to GCP

    Parameters:
        directory_to_monitor (str): Directory to monitor for new subdirectories
        gcp_bucket_name (str): GCP bucket name for uploading
        check_interval (int): Time interval (in seconds) to check for new subdirectories
    '''
    already_uploaded = set()
    while True:
        try:
            if not os.path.exists(directory_to_monitor):
                os.makedirs(directory_to_monitor)

            current_subdirectories = {d for d in os.listdir(
                directory_to_monitor) if os.path.isdir(os.path.join(directory_to_monitor, d))}
            new_subdirectories = current_subdirectories - already_uploaded

            if not new_subdirectories:
                if should_stop() == True:
                    return
                else:
                    print(
                        f"No new subdirectories found. Checking again in {check_interval} seconds...")
                    await asyncio.sleep(check_interval)

            for subdir in new_subdirectories:
                if should_stop() == True:
                    return
                subdir_path = os.path.join(directory_to_monitor, subdir)
                print(f"Uploading {subdir} to GCP...")
                upload_dir_to_gcp(subdir_path, subdir)
                already_uploaded.add(subdir)
                print(f"Uploaded {subdir} to GCP.")

        except Exception as e:
            print(f"An error occurred: {e}")


async def monitor_gcp_and_download_to_local(directory_to_monitor, local_download_dir, check_interval=60, should_stop=lambda: False, bucket_name=config['bucket_name']):
    '''
    Monitors a directory on GCP and download new subdirectories to local computer/server

    Parameters:
        directory_to_monitor (str): Directory to monitor for new subdirectories
        gcp_bucket_name (str): GCP bucket name for downloading
        check_interval (int): Time interval (in seconds) to check for new subdirectories
    '''
    downloaded_files = set()
    while not should_stop():
        try:
            if not check_gcp_directory_exists(directory_to_monitor):
                print("ERROR: Directory to be monitored not found on GCP.")
                return

            current_files = list_blobs_with_prefix(
                directory=config['selftrain_improve_gcp_dir'], prefix=config['blob_prefix'], delimiter="")
            new_files = current_files - downloaded_files

            if not new_files:
                print(
                    f"No new files found on GCP. Checking again in {check_interval} seconds...")
                await asyncio.sleep(check_interval)

            download_files_from_gcp(
                files_to_download=list(new_files), local_download_dir=local_download_dir)
            downloaded_files = current_files

        except Exception as e:
            print(f"An error occurred: {e}")
||||||| parent of 79b09d6... Feature/cloud utils (#130)
=======
from pipelines import config
import os
import asyncio
from google.cloud.storage import Client, transfer_manager
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
>>>>>>> 79b09d6... Feature/cloud utils (#130)
