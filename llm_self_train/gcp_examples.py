from pipelines.gcp_util import upload_to_gcp, download_from_gcp, monitor_and_upload

object_location = '/Users/zhengyangqi/Desktop/template-demo.txt'  # Replace with your file path
oauth2_token_location = './resources/auth_token.key'      # Replace with your OAuth2 token
content_type = 'application/json; charset=utf-8'      # Replace with the content type of your object
bucket_name = 'pipeline-test-storage'        # Replace with your bucket name
object_name = 'test/test.txt'        # Replace with your object name
save_to_location = './test.txt'

# Call the upload function
response = upload_to_gcp(object_name, object_location, oauth2_token_location, bucket_name, content_type)
print(response.text)
response = download_from_gcp(object_name, save_to_location, oauth2_token_location, bucket_name)
print(response.text)

# monitor_and_upload('./test_cache', 5, oauth2_token_location, bucket_name)