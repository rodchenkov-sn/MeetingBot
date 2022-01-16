from typing import Optional


class LinesRepo:
    def __init__(self) -> None:
        from pymongo import MongoClient
        cluster = ""
        client = MongoClient(cluster)
        db = client['localization']
        self.__languages = db['languages']
        self.__lines = db['lines']

    def get_line(self, _name: str, _user_id: int) -> str:
        language = self.get_user_language(_user_id)
        line = self.__lines.find_one( { '_id': _name } )
        if language is None or line is None:
            return ''
        else:
            translations = line['translations']
            for translation in translations:
                if translation['language'] == language:
                    return translation['text']

    def get_user_language(self, _user_id: int) -> Optional[str]:
        user_language = self.__languages.find_one( { '_id': _user_id } )
        if user_language is None:
            self.__languages.insert_one( { '_id': _user_id, 'language': 'en' } )
            user_language = self.__languages.find_one( { '_id': _user_id } )
        if user_language is None:
            return None
        else:
            return user_language['language']

    def update_user_language(self, _user_id: int, _language: str):
        self.__languages.update_one(
            { '_id': _user_id },
            { "$set": { 'language': _language } }
        )
