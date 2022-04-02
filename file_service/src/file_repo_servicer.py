import requests
import random
import os
import urllib.request
import yaml

import file_repo_service_pb2 as fr
import file_repo_service_pb2_grpc as frs


class FileNames:
    def __init__(self):
        with open('config.yml', 'r') as config_file:
            config = yaml.safe_load(config_file)
        from pymongo import MongoClient
        client = MongoClient(config['files_repo_url'])
        self.__collection = client['MeetingBotDB']['Files']
    
    def save(self, id, original_name):
        self.__collection.insert_one({'_id': id, 'original_name': original_name})

    def get_name(self, id) -> str:
        return self.__collection.find_one({'_id': id})['original_name']


class FileRepoServicer(frs.FileRepoServiceServicer):
    def __init__(self):
        super().__init__()
        self.__file_names = FileNames()

    def UploadFile(self, request, context):
        new_id = random.randint(1, 999999999)
        tmp_name = f'{new_id}_{request.name}'
        
        urllib.request.urlretrieve(request.download_url, tmp_name)
        with open(tmp_name, 'rb') as f:
            requests.post(f'https://meetingbot-fileservice.herokuapp.com/files/{tmp_name}', data=f.read(), verify=False)
        os.remove(tmp_name)

        self.__file_names.save(new_id, request.name)
        return fr.FileId(id=new_id)


    def DownloadFile(self, request, context):
        original_name = self.__file_names.get_name(request.id)
        return fr.FileInfo(
            name=original_name,
            download_url=f'https://meetingbot-fileservice.herokuapp.com/files/{request.id}_{original_name}'
            )
