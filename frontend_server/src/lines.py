import yaml

from pymongo import MongoClient
from typing import Optional, List


class LinesRepo:
    def __init__(self) -> None:
        with open('config.yml', 'r') as config_file:
            config = yaml.safe_load(config_file)
        cluster = config['mongodb_cluster']
        client = MongoClient(cluster)
        db = client['localization']
        self.__users = db['users']
        self.__lines = db['lines']
        self.__languages = db['languages']

    def get_line(self, _name: str, _user_id: int) -> str:
        language = self.get_user_language(_user_id)
        line_doc = self.__lines.find_one({'_id': _name})
        if language is None or line_doc is None:
            return ''
        else:
            translations = line_doc['translations']
            for transl in translations:
                if transl['language'] == language:
                    line = transl['text']
                    return line

    def get_user_language(self, _user_id: int) -> Optional[str]:
        user_doc = self.__users.find_one({'_id': _user_id})
        if user_doc is None:
            self.__users.insert_one({'_id': _user_id, 'language': 'en'})
            user_doc = self.__users.find_one({'_id': _user_id})
        if user_doc is None:
            return None
        else:
            user_language = user_doc['language']
            return user_language

    def update_user_language(self, _user_id: int, _language: str) -> Optional[str]:
        languages = self.get_all_languages()
        if _language in languages:
            self.__users.update_one(
                {'_id': _user_id},
                {"$set": {'language': _language}}
            )
            updated_language = self.get_user_language(_user_id)
            return updated_language
        else:
            return None

    def get_all_languages(self) -> Optional[List[str]]:
        language_docs = self.__languages.find()
        languages = []
        if language_docs is None:
            return None
        else:
            for l_d in language_docs:
                languages.append(l_d['_id'])
            return languages
