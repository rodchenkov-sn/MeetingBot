import random

import file_repo_service_pb2 as fr
import file_repo_service_pb2_grpc as frs


class FileNames:
    def __init__(self):
        self.__names = {}
    
    def save(self, id: int, name: str) -> None:
        self.__names[id] = name

    def get_name(self, id: int) -> str:
        return self.__names[id]


class FileRepoServicer(frs.FileRepoServiceServicer):
    def __init__(self):
        super().__init__()
        self.__file_names = FileNames()

    def UploadFile(self, request, context):
        new_id = random.randint(1, 999999999)
        self.__file_names.save(new_id, request.name)
        return fr.FileId(id=new_id)


    def DownloadFile(self, request, context):
        original_name = self.__file_names.get_name(request.id)
        return fr.FileInfo(
            name=original_name,
            download_url=f'https://test_download.org/{request.id}_{original_name}'
            )
