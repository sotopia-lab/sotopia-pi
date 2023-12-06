from pipelines.cloud_util import upload_dir_to_gcp, download_dir_from_gcp, list_blobs_with_prefix, monitor_and_upload
import asyncio
import time

bucket_name = 'pipeline-test-storage' 

source_dir = '/workspace/sotopia-llm/llm_self_train/output_cache/checkpoint-960'
dest_blob_prefix = 'checkpoint-960'

source_blob_prefix = 'checkpoint-960'
dest_dir = '/workspace/sotopia-llm/llm_self_train/checkpoint-hello'

# Call the upload and download function
upload_dir_to_gcp(source_dir, dest_blob_prefix, bucket_name)
download_dir_from_gcp(source_blob_prefix, dest_dir, bucket_name)
print(list_blobs_with_prefix(bucket_name, ""))

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
    await asyncio.gather(monitor_and_upload('./demo_cache', 5, should_stop=should_stop), timer())

asyncio.run(main())
print("Done")