<<<<<<< HEAD
from pipelines import config
from pipelines.cloud_util import list_blobs_with_prefix, download_files_from_gcp, check_gcp_directory_exists, monitor_gcp_and_download_to_local
from google.cloud.storage import Client
import asyncio
from tqdm import tqdm

# print(config['bucket_name'])
# print(list_blobs_with_prefix(
#     "improve-1", "checkpoint", delimiter=""))
# storage_client = Client()
# bucket = storage_client.bucket(config['bucket_name'])

# blobs = list(bucket.list_blobs())
# blob_paths = [blob.name for blob in blobs]
# print(blob_paths)

# download_files_from_gcp(['improve-1/checkpoint-1020/README.md'],
#                         "/Users/pamela/Documents/capstone/sotopia-llm/llm_self_train")

run_sft_completed = False


def should_stop():
    global run_sft_completed
    return run_sft_completed


async def timer(timeout=60*2):
    await asyncio.sleep(timeout)
    print("Stopping...")
    global run_sft_completed
    run_sft_completed = True


async def main():
    await asyncio.gather(monitor_gcp_and_download_to_local(directory_to_monitor=config["selftrain_improve_gcp_dir"], local_download_dir="/Users/pamela/Documents/capstone/sotopia-llm/llm_self_train", check_interval=60, should_stop=should_stop), timer())

asyncio.run(main())
print("Done")
||||||| parent of 79b09d6... Feature/cloud utils (#130)
=======
from pipelines import config

from pipelines.cloud_util import list_blobs_with_prefix, download_files_from_gcp, check_gcp_directory_exists
from pipelines.monitor_proc import monitor_gcp_and_download_to_local

import multiprocessing
import time

def should_stop(run_sft_completed):
    return run_sft_completed.value

def timer(timeout, run_sft_completed):
    time.sleep(timeout)
    print("Stopping...")
    run_sft_completed.value = True

def main():
    run_sft_completed = multiprocessing.Value('b', False)

    # Process for monitoring and downloading
    monitor_process = multiprocessing.Process(target=monitor_gcp_and_download_to_local, args=("improve-2", "./", 30, lambda: should_stop(run_sft_completed)))

    # Process for timer
    timer_process = multiprocessing.Process(target=timer, args=(60, run_sft_completed))

    monitor_process.start()
    timer_process.start()

    monitor_process.join()
    timer_process.join()

    print("Done")

if __name__ == '__main__':
    main()
>>>>>>> 79b09d6... Feature/cloud utils (#130)
