import os

import file_repo_service_pb2
import file_repo_service_pb2_grpc
import requests
import bd
import random

HOST = '127.0.0.1:10800'

FILE_FOLDER_HOST = "~/PycharmProjects/m"

UPLOAD_DIRECTORY = f"{FILE_FOLDER_HOST}/project/api_uploaded_files"


class FileRepoServicer(file_repo_service_pb2_grpc.FileRepoServiceServicer):
    def UploadFile(self, request, context):
        url = request.download_url
        r = requests.get(url, allow_redirects=True)
        open(os.path.join(UPLOAD_DIRECTORY, request.name), 'wb').write(r.content)
        idnew = random.getrandbits(32)
        bd.Bd().save(f"{HOST}/files/{request.name}", idnew, request.name)
        return file_repo_service_pb2.FileId(id=idnew)

    def DownloadFile(self, request, context):
        url, name = bd.Bd().get(request.id)
        return file_repo_service_pb2.FileInfo(download_url=url, name=name)
