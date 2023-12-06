from pipelines import config
from pipelines.cloud_util import upload_dir_to_gcp, download_files_from_gcp, list_blobs_with_prefix, check_gcp_directory_exists
import os
import time

def monitor_local_and_upload_to_gcp(local_directory_to_monitor, destination_dir, check_interval=60, should_stop=lambda: False, bucket_name=config['bucket_name']):
    '''
    Monitors a directory and uploads new subdirectories to GCP

    Parameters:
        local_directory_to_monitor (str): Directory to monitor for new subdirectories
        gcp_bucket_name (str): GCP bucket name for uploading
        check_interval (int): Time interval (in seconds) to check for new subdirectories
    '''
    already_uploaded = set()
    while True:
        try:
            if not os.path.exists(local_directory_to_monitor):
                os.makedirs(local_directory_to_monitor)

            current_subdirectories = {d for d in os.listdir(
                local_directory_to_monitor) if os.path.isdir(os.path.join(local_directory_to_monitor, d))}
            new_subdirectories = current_subdirectories - already_uploaded

            if not new_subdirectories:
                if should_stop() == True:
                    return
                else:
                    print(
                        f"No new subdirectories found. Checking again in {check_interval} seconds...")
                    time.sleep(check_interval)

            for subdir in new_subdirectories:
                subdir_path = os.path.join(local_directory_to_monitor, subdir)
                destination_blob_prefix = os.path.join(
                    destination_dir, subdir)
                print(f"Uploading {subdir} to GCP at {destination_blob_prefix}...")
                upload_dir_to_gcp(subdir_path, destination_blob_prefix)
                already_uploaded.add(subdir)
                print(f"Uploaded {subdir} to GCP.")

        except Exception as e:
            print(f"An error occurred: {e}")


def monitor_gcp_and_download_to_local(directory_to_monitor, local_download_dir, check_interval=60, should_stop=lambda: False, bucket_name=config['bucket_name']):
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
                directory=config['selftrain_improve_gcp_dir'], prefix=config['checkpoint_prefix'], delimiter="")
            new_files = current_files - downloaded_files

            if not new_files:
                print(
                    f"No new files found on GCP. Checking again in {check_interval} seconds...")
                time.sleep(check_interval)

            download_files_from_gcp(
                files_to_download=list(new_files), local_download_dir=local_download_dir)
            downloaded_files = current_files

        except Exception as e:
            print(f"An error occurred: {e}")
