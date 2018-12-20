from pymongo import MongoClient
from datetime import datetime, timedelta
import collections


class Database():
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        self.mdb = self.client['makubot-test']
        self.emotes = self.mdb.emotes
        self.servers = self.mdb.servers
        self.reminders = self.mdb.reminders

    def emotes_get_top(self, guild_id, num=5, emote=None):
        #_id = self.emotes.find_one({'guildId': guild_id})['_id']
        rgx = ''
        if emote: 
            rgx = f'.*{emote}.*'
        pipeline = [{'$match': {
                        'guildId': guild_id
                    }
                }, {'$unwind': {
                        'path': '$emotes'
                    }
                }, {'$match': {
                        'emotes.name': {
                            '$regex' : rgx,
                            '$options': 'i'
                        }
                    }
                }, {'$sort': {
                        'emotes.count': -1
                    }
                }, {'$limit': num}]
                
        top = self.emotes.aggregate(pipeline)
        top_emotes = collections.OrderedDict()  # use OrderedDict to guarantee order
        for doc in top:
            doc = doc['emotes']
            top_emotes.update({doc['name']: doc['count']})
        return top_emotes

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

    def reminders_add(self, delta, note, user_id, channel_id, guild_id, send_dm):
        reminder = {
            'dueTime' : datetime.now() + delta,
            'note' : note,
            'userId' : user_id,
            'channelId' : channel_id,
            'guildId' : guild_id, 
            'sendDM' : send_dm
        }
        self.reminders.insert_one(reminder)
        # store reminder
    
    def reminders_get(self):
        query = self.reminders.find({})
        if query:
            return list(query)
        return None

    def reminders_get_expired(self):
        """
        reminders.find({
            dueTime: {
            $lt: Date.now()
            }
        })
        """
        query = self.reminders.find({'dueTime': {'$lt': datetime.now()}})
        if query:
            return list(query)
        return None

    def reminders_delete(self, _id):
        """
        delete reminder by _id
        """
        self.reminders.delete_one({'_id': _id})
    

# db = Database('192.168.0.69')
# x = db.emotes_add(369837754290536448, ["draconCute"])
# x = db.emotes_add(0, ["draconCute"])
# x = db.emotes_add(369837754290536448, ["xy"])
# x = db.emotes_count(369837754290536448, "asdasd")
# db.reminders_add(100, 'test', 123, 456, 789, False)
# x = db.reminders_get_expired()
# for reminder in x:
#     print(reminder)
#     db.reminders_delete(reminder['_id'])