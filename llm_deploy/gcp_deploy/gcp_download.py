from google.cloud import storage
import os

def download_directory(bucket_name, prefix, local_destination_dir):
    """Download a 'directory' from GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix)  # Get list of files in the directory
    for blob in blobs:
        directory_structure = os.path.join(local_destination_dir, blob.name)
        directory = os.path.dirname(directory_structure)

        # Create local directory structure if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Download the blob to a local file
        blob.download_to_filename(directory_structure)
        print(f"Blob {blob.name} downloaded to {directory_structure}.")

# Replace these variables with your details
bucket_name = "runpod_storgage"
directory_prefix = "webarena-mistral-7b-ckpt_v2/checkpoint-3203"  # The trailing slash is important for directories
local_destination_dir = "/work/haofeiy/webarena-mistral-7b-ckpt_v2"

download_directory(bucket_name, directory_prefix, local_destination_dir)
