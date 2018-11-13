from pymongo import MongoClient


class Database():
    def __init__(self, mongo_url):
        self.mdb = MongoClient(mongo_url)
        self.emotes = self.mdb.emotes
        self.servers = self.mdb.servers

    def emotes_get_top(server_id, num=5, emote=None):
        pass

    def emotes_add(server_id, emotes):
        pass

    def emotes_count(server_id, emote):
        pass


