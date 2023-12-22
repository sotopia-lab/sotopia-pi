from pipelines import config

from pipelines.cloud_util import upload_dir_to_gcp, download_dir_from_gcp, list_blobs_with_prefix, monitor_and_upload
from pipelines.monitor_proc import monitor_local_and_upload_to_gcp

import time

bucket_name = 'pipeline-test-storage' 

source_dir = '/workspace/sotopia-llm/llm_self_train/output_cache/checkpoint-960'
dest_blob_prefix = 'checkpoint-960'

source_blob_prefix = 'checkpoint-960'
dest_dir = '/workspace/sotopia-llm/llm_self_train/checkpoint-hello'

# Call the upload and download function
upload_dir_to_gcp(source_dir, dest_blob_prefix, bucket_name)
print(list_blobs_with_prefix(bucket_name, ""))

run_sft_completed = False

def should_stop(run_sft_completed):
    return run_sft_completed.value

def timer(timeout, run_sft_completed):
    time.sleep(timeout)
    print("Stopping...")
    run_sft_completed.value = True
    
def main():
    run_sft_completed = multiprocessing.Value('b', False)

    # Process for monitoring and uploading
    monitor_process = multiprocessing.Process(target=monitor_and_upload_wrapper, args=('./demo_cache', 5, lambda: should_stop(run_sft_completed)))

    # Process for timer
    timer_process = multiprocessing.Process(target=timer, args=(120, run_sft_completed))

    monitor_process.start()
    timer_process.start()

    monitor_process.join()
    timer_process.join()

    print("Done")
    
if __name__ == '__main__':
    main()