from pymongo import MongoClient


class Database():
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        self.mdb = self.client['makubot-test']
        self.emotes = self.mdb.emotes
        self.servers = self.mdb.servers

    def emotes_get_top(self, guild_id, num=5, emote=None):
        pass

    def emotes_add(self, guild_id, emotes):
        for emote in emotes:
            if not self.emotes_check_exists(guild_id, emote):
                if self.emotes_guild_exists(guild_id):
                    self.emotes.update({'guildId':guild_id}, {'$addToSet': {'emotes': {'name': emote, 'count': 1}}})
                else:
                    self.emotes.insert_one({'guildId': guild_id, 'emotes': [{'name': emote, 'count': 1}]})
            else:
                self.emotes.update({'guildId': guild_id, 'emotes.name': emote}, {'$inc': {'emotes.$.count': 1}}, False, True)

    def emotes_count(self, guild_id, emote):
        query = self.emotes.find_one({'guildId': guild_id})
        if not query:
            return None
        try:
            em = [em for em in query['emotes'] if em.get('name') == emote][0]
            return em['count']
        except:
            return 0
        
    
    def emotes_guild_exists(self, guild_id):
        query = self.emotes.find_one({'guildId': guild_id})
        if query:
            return True
        return False

    def emotes_check_exists(self, guild_id, emote):
        query = self.emotes.find_one({'guildId': guild_id, 'emotes.name': emote})
        if query:
            return True
        return False

db = Database('192.168.0.69')
x = db.emotes_add(369837754290536448, ["draconCute"])
x = db.emotes_add(0, ["draconCute"])
x = db.emotes_add(369837754290536448, ["xy"])
x = db.emotes_count(369837754290536448, "asdasd")
print(x)

