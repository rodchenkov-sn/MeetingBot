from tinydb import TinyDB, Query


class Bd:
    def __init__(self):
        self.db = TinyDB('mainjson')

    def save(self, url, id, name):
        self.db.table('files').insert({'url': url, 'id': id, 'name': name})

    def get(self, id):
        File = Query()
        res = self.db.table('files').search(File.id == id)
        return res[0]['url'], res[0]['name']

    def create(self):
        self.cursor.execute("CREATE TABLE FILES (id INTEGER PRIMARY KEY, url TEXT, name VARCHAR[50])")
