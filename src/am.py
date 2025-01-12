import os
import sys
from helpers import show_help, parser

from azure.storage.blob import BlobServiceClient, ContentSettings, ContainerClient

try:
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_CON_STR'))
except:
    exit("Error: Please define your Azure connection string before continuing.")


# Decide which function to run based on user input
def decider():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'upload':
            if len(sys.argv) <= 3:
                exit("Please provide the name of your container name as first argument, and the path to your folder as "
                     "second.\nThe correct format is: 'am.py upload <container> <path>'")
            else:
                # Did the user provide a valid path?
                if not os.path.exists(sys.argv[3]):
                    exit("Error: Please provide a valid path")
                # If they did, is that path a folder?
                if not os.path.isdir(sys.argv[3]):
                    exit("Error: Path is not a folder")
                # If it is, does it contain any files?
                if os.path.exists(sys.argv[3]) and not os.listdir(sys.argv[3]):
                    exit("Error: Directory is empty")

                # If all above are true, proceed to upload files
                print("Starting upload...")
                upload_all()
                print(f"All files successfully uploaded to {sys.argv[2]} container")
        elif sys.argv[1] == 'list':
            if len(sys.argv) <= 4:
                exit(
                    "Please provide command arguments in this order: acc_connection_uri, container_name, sas_token")
            list_blobs()
        elif sys.argv[1] == 'download':
            if len(sys.argv) <= 4:
                exit(
                    "Please provide command arguments in this order: acc_connection_uri, container_name, sas_token")
            download_blobs()
        elif sys.argv[1] == 'cc':
            if len(sys.argv) <= 2:
                exit("Please provide a name for your new container")
            create_container()
        elif sys.argv[1] == 'dc':
            if len(sys.argv) <= 2:
                exit("Please provide a name for the container to be deleted")
            delete_container()
        elif sys.argv[1] == 'lc':
            list_containers()

    else:
        exit('\nError: Invalid command. Use "am.py --help" for available commands')


# Upload all blobs from a specified folder to a specified container
def upload_all():
    # Initialize the connection to Azure storage account
    image_content_setting = ContentSettings(content_type='image/jpeg')
    # Go through all files in provided directory
    files = [f for f in os.listdir(sys.argv[3])]
    for file in files:
        blob_client = blob_service_client.get_blob_client(container=sys.argv[2], blob=file)
        with open(os.path.join(sys.argv[3], file), "rb") as data:
            # Upload all files to Azure
            blob_client.upload_blob(data, content_settings=image_content_setting)


# Print a list of all blobs in a specified container
def list_blobs():
    container_client = ContainerClient(sys.argv[2], sys.argv[3], sys.argv[4])
    blobs = container_client.list_blobs()

    print("Listing all blobs:")
    for blob in blobs:
        print(blob.name + '\n')


# Download all blobs, or specified blob, to a folder
def download_blobs():
    download_dir = './downloads'
    container_client = ContainerClient(sys.argv[2], sys.argv[3], sys.argv[4])
    blobs = container_client.list_blobs()

    print("Starting download...")
    # If we have 6 arguments, the user has specified a blob to download as last argument
    if len(sys.argv) == 6:
        # If download dir doesn't exist, make it first
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
            with open(os.path.join(download_dir, sys.argv[5]), "wb") as file:
                file.write(container_client.get_blob_client(sys.argv[5]).download_blob().readall())
                print(f"Downloaded file: {sys.argv[5]}")
        else:
            with open(os.path.join(download_dir, sys.argv[5]), "wb") as file:
                file.write(container_client.get_blob_client(sys.argv[5]).download_blob().readall())
                print(f"Downloaded file: {sys.argv[5]}")
    # Otherwise download all blobs in container
    else:
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
            for blob in blobs:
                with open(os.path.join(download_dir, blob.name), "wb") as file:
                    file.write(container_client.get_blob_client(blob.name).download_blob().readall())
                    print(f"Downloaded file: {blob.name}")
        else:
            for blob in blobs:
                with open(os.path.join(download_dir, blob.name), "wb") as file:
                    file.write(container_client.get_blob_client(blob.name).download_blob().readall())
                    print(f"Downloaded file: {blob.name}")
    print(f"Successfully downloaded your specified files to the {download_dir} folder")


# List all containers
def list_containers():
    container_list = blob_service_client.list_containers()
    for container in container_list:
        print(f"Container: {container['name']}\n")


# Create a new container
def create_container():
    blob_service_client.create_container(sys.argv[2])
    print(f"Container: '{sys.argv[2]}' created")


# Delete a container
def delete_container():
    blob_service_client.delete_container(sys.argv[2])
    print(f"Container '{sys.argv[2]}' has been deleted")


if __name__ == "__main__":
    decider()
    show_help()
