import os

import file_repo_service_pb2
import file_repo_service_pb2_grpc
import requests
import bd
import random

HOST = '127.0.0.1:10800'

FILE_FOLDER_HOST = "."

UPLOAD_DIRECTORY = f"{FILE_FOLDER_HOST}/project/api_uploaded_files"


class FileRepoServicer(file_repo_service_pb2_grpc.FileRepoServiceServicer):
    def UploadFile(self, request, context):
        url = request.download_url
        r = requests.get(url, allow_redirects=True)
        request.post('https://meetingbot-fileservice.herokuapp.com/files', data = r)

    def DownloadFile(self, request, context):
                            return requests.get(f"https://meetingbot-fileservice.herokuapp.com/file/{request.id}")
