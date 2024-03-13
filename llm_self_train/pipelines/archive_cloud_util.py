import asyncio
import os
import zipfile

import requests
from pipelines import config


async def monitor_and_upload(
    directory_to_monitor,
    check_interval=60,
    should_stop=lambda: False,
    oauth2_token_location=config["oauth2_token_location"],
    bucket_name=config["bucket_name"],
):
    """
    Monitors a directory and uploads new subdirectories to GCP

    Parameters:
        directory_to_monitor (str): Directory to monitor for new subdirectories
        gcp_bucket_name (str): GCP bucket name for uploading
        oauth2_token_location (str): The location of the OAuth2 token
        check_interval (int): Time interval (in seconds) to check for new subdirectories
    """
    already_uploaded = set()
    while True:
        try:
            if not os.path.exists(directory_to_monitor):
                os.makedirs(directory_to_monitor)

            current_subdirectories = {
                d
                for d in os.listdir(directory_to_monitor)
                if os.path.isdir(os.path.join(directory_to_monitor, d))
            }
            new_subdirectories = current_subdirectories - already_uploaded

            if not new_subdirectories:
                if should_stop() == True:
                    return
                else:
                    print(
                        f"No new subdirectories found. Checking again in {check_interval} seconds..."
                    )
                    await asyncio.sleep(check_interval)

            for subdir in new_subdirectories:
                subdir_path = os.path.join(directory_to_monitor, subdir)
                zip_name = f"{subdir}.zip"

                print(f"Zipping {subdir}...")
                zip_directory(subdir_path, zip_name)
                print(f"Zipped {subdir}.")

                print(f"Uploading {zip_name} to GCP...")
                response = upload_to_gcp(zip_name, zip_name)
                already_uploaded.add(subdir)
                print(f"Uploaded {subdir} to GCP.")
                print(response.text)

        except Exception as e:
            print(f"An error occurred: {e}")


def upload_to_gcp(
    object_name,
    object_location,
    oauth2_token_location=config["oauth2_token_location"],
    bucket_name=config["bucket_name"],
    content_type="application/json; charset=utf-8",
):
    """
    Uploads a file to a bucket in Google Cloud Storage

    Parameters:
        object_location (str): The location of the file to upload
        oauth2_token_location (str): The location of the OAuth2 token
        content_type (str): The content type of the object
        bucket_name (str): The name of the bucket to upload to
        object_name (str): The name of the object to upload
    """
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket_name}/o?uploadType=media&name={object_name}"
    with open(oauth2_token_location, "r") as file:
        oauth2_token = str(file.read())

    headers = {
        "Authorization": f"Bearer {oauth2_token}",
        "Content-Type": content_type,
    }

    with open(object_location, "rb") as file:
        data = file.read()

    response = requests.post(url, headers=headers, data=data)
    return response


def download_from_gcp(
    object_name,
    save_to_location,
    oauth2_token_location=config["oauth2_token_location"],
    bucket_name=config["bucket_name"],
):
    """
    Downloads a file from a bucket in Google Cloud Storage

    Parameters:
        oauth2_token_location (str): The location of the OAuth2 token
        bucket_name (str): The name of the bucket to download from
        object_name (str): The name of the object to download
        save_to_location (str): The location to save the file to
    """
    if "/" in object_name:
        object_name = object_name.replace("/", "%2F")

    url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o/{object_name}?alt=media"

    with open(oauth2_token_location, "r") as file:
        oauth2_token = str(file.read())

    headers = {"Authorization": f"Bearer {oauth2_token}"}

    response = requests.get(url, headers=headers)
    with open(save_to_location, "wb") as file:
        file.write(response.content)
    return response


def zip_directory(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Create a relative path for files to keep the directory structure
                relative_path = os.path.relpath(
                    os.path.join(root, file), os.path.dirname(folder_path)
                )
                zipf.write(os.path.join(root, file), arcname=relative_path)


def unzip_directory(zip_name, folder_path):
    with zipfile.ZipFile(zip_name, "r") as zipf:
        zipf.extractall(folder_path)
