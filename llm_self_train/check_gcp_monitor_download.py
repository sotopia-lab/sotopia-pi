from pipelines import config

from pipelines.cloud_util import list_blobs_with_prefix, download_files_from_gcp, check_gcp_directory_exists
from llm_self_train.pipelines.monitor_processes import monitor_gcp_and_download_to_local

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
