<<<<<<< HEAD
from pipelines.cloud_util import upload_dir_to_gcp, download_dir_from_gcp, list_blobs_with_prefix, monitor_and_upload
import asyncio
||||||| parent of 79b09d6... Feature/cloud utils (#130)
from pipelines.gcp_util import upload_to_gcp, download_from_gcp, monitor_and_upload
import asyncio
=======
from pipelines import config

from pipelines.cloud_util import upload_dir_to_gcp, download_dir_from_gcp, list_blobs_with_prefix, monitor_and_upload
from llm_self_train.pipelines.monitor_processes import monitor_local_and_upload_to_gcp

>>>>>>> 79b09d6... Feature/cloud utils (#130)
import time

<<<<<<< HEAD
bucket_name = 'pipeline-test-storage' 
||||||| parent of 79b09d6... Feature/cloud utils (#130)
object_location = '/Users/zhengyangqi/Desktop/template-demo.txt'  # Replace with your file path
oauth2_token_location = './resources/gcp_auth.token'      # Replace with your OAuth2 token
content_type = 'application/json; charset=utf-8'      # Replace with the content type of your object
bucket_name = 'pipeline-test-storage'        # Replace with your bucket name
object_name = 'test/test.txt'        # Replace with your object name
save_to_location = './test.txt'
=======
bucket_name = 'pipeline-test-storage' 

source_dir = '/workspace/sotopia-llm/llm_self_train/output_cache/checkpoint-960'
dest_blob_prefix = 'checkpoint-960'
>>>>>>> 79b09d6... Feature/cloud utils (#130)

<<<<<<< HEAD
source_dir = '/workspace/sotopia-llm/llm_self_train/output_cache/checkpoint-960'
dest_blob_prefix = 'checkpoint-960'

source_blob_prefix = 'checkpoint-960'
dest_dir = '/workspace/sotopia-llm/llm_self_train/checkpoint-hello'

# Call the upload and download function
upload_dir_to_gcp(source_dir, dest_blob_prefix, bucket_name)
download_dir_from_gcp(source_blob_prefix, dest_dir, bucket_name)
print(list_blobs_with_prefix(bucket_name, ""))
||||||| parent of 79b09d6... Feature/cloud utils (#130)
# Call the upload function
response = upload_to_gcp(object_name, object_location, oauth2_token_location, bucket_name, content_type)
print(response.text)
response = download_from_gcp(object_name, save_to_location, oauth2_token_location, bucket_name)
print(response.text)
=======
source_blob_prefix = 'checkpoint-960'
dest_dir = '/workspace/sotopia-llm/llm_self_train/checkpoint-hello'

# Call the upload and download function
upload_dir_to_gcp(source_dir, dest_blob_prefix, bucket_name)
print(list_blobs_with_prefix(bucket_name, ""))
>>>>>>> 79b09d6... Feature/cloud utils (#130)

run_sft_completed = False

def should_stop(run_sft_completed):
    return run_sft_completed.value

<<<<<<< HEAD
async def timer(timeout=60*2):
    await asyncio.sleep(timeout)
||||||| parent of 79b09d6... Feature/cloud utils (#130)
async def timer():
    await asyncio.sleep(15)
=======
def timer(timeout, run_sft_completed):
    time.sleep(timeout)
>>>>>>> 79b09d6... Feature/cloud utils (#130)
    print("Stopping...")
    run_sft_completed.value = True
    
<<<<<<< HEAD
async def main():
    await asyncio.gather(monitor_and_upload('./demo_cache', 5, should_stop=should_stop), timer())
||||||| parent of 79b09d6... Feature/cloud utils (#130)
async def hello():
    await asyncio.gather(monitor_and_upload('./demo_cache', 5, should_stop=should_stop), timer())
=======
def main():
    run_sft_completed = multiprocessing.Value('b', False)

    # Process for monitoring and uploading
    monitor_process = multiprocessing.Process(target=monitor_and_upload_wrapper, args=('./demo_cache', 5, lambda: should_stop(run_sft_completed)))
>>>>>>> 79b09d6... Feature/cloud utils (#130)

<<<<<<< HEAD
asyncio.run(main())
print("Done")
||||||| parent of 79b09d6... Feature/cloud utils (#130)
asyncio.run(hello())
print("Done")
=======
    # Process for timer
    timer_process = multiprocessing.Process(target=timer, args=(120, run_sft_completed))

    monitor_process.start()
    timer_process.start()

    monitor_process.join()
    timer_process.join()

    print("Done")
    
if __name__ == '__main__':
    main()
>>>>>>> 79b09d6... Feature/cloud utils (#130)
