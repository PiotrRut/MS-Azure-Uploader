import os, sys
from azure.storage.blob import BlobServiceClient, ContentSettings


def validate():
    if len(sys.argv) < 3:
        exit("Please provide the name of your container name as first argument, and the path to your folder as second")
    else:
        return True


def upload_all():
    # Initialize the connection to Azure storage account
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_CON_STR'))
    image_content_setting = ContentSettings(content_type='image/jpeg')
    # Go through all files and upload them to storage
    all_file_names = [f for f in os.listdir(sys.argv[2])
                      if os.path.isfile(os.path.join(sys.argv[2], f))]
    for file in all_file_names:
        blob_client = blob_service_client.get_blob_client(container=sys.argv[1], blob=file)
        with open(os.path.join(sys.argv[2], file), "rb") as data:
            blob_client.upload_blob(data, content_settings=image_content_setting)


if __name__ == "__main__":
    isValidated = validate()
    if isValidated:
        print("Starting upload")
        upload_all()
        print(f"All files successfully uploaded to {sys.argv[1]} container")