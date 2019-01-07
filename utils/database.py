from pymongo import MongoClient
from datetime import datetime, timedelta
import collections


class Database():
    def __init__(self, mongo_url, db_name, bot):
        self.bot = bot
        self.client = MongoClient(mongo_url)
        self.mdb = self.client[db_name]
        self.emotes = self.mdb.emotes
        self.servers = self.mdb.servers
        self.reminders = self.mdb.reminders
        self.prefix_load()

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

    def family_add(self, user_id):
        bot = self.mdb.bot
        doc = bot.find_one({})
        if doc is not None:
            if 'family' in doc:
                if user_id in doc['family']:
                    return
            else:
                bot.update_one({'_id': doc['_id']}, {'$push': {'family': [user_id]}})
        else:
            bot.insert_one({'family': [user_id]})
        bot.update({'_id':doc['_id']}, {'$addToSet': {'family': user_id}})
    
    def family_is_member(self, user_id):
        bot = self.mdb.bot
        doc = bot.find_one({})
        if doc is None:
            return False
        if 'family' in doc:
            if user_id in doc['family']:
                return True
        return False

    def prefix_load(self):
        """ loads all prefixes into prefixes[guildId] on self.bot """
        self.bot.prefix = dict()
        docs = self.servers.find({})
        for doc in docs:
            try:
                prefix = doc['config']['prefix']
                guild_id = doc['guildId']
                self.bot.prefix[guild_id] = prefix
            except:
                pass  # we don't bother, server config might not contain a prefix

    def prefix_set(self, guild_id, prefix):
        """ set the prefix of a guild_id """
        # self.servers.update({'guildId': guild_id}, {'guildId': guild_id,'config': {'prefix': prefix}}, upsert=True)
        try:
            guild = self.servers.find_one({'guildId': guild_id})
            if not guild:
                self.servers.insert({'guildId': guild_id, 'config': {'prefix': prefix}})
            else:
                self.servers.update({'guildId': guild_id}, {'$set': {'config.prefix': prefix}})
            self.bot.prefix[guild_id] = prefix
            return True
        except:
            return False

    def logging_get(self, guild_id):
        """ returns logging configuration for guild """
        guild = self.servers.find_one({'guildId': guild_id})
        try:
            return guild['logging']
        except:
            return None
    
    def logging_set_channel(self, guild_id, channel_id):
        """ set the channel for logging for this guild """
        try:
            guild = self.servers.find_one({'guildId': guild_id})
            if not guild:
                self.servers.insert({'guildId': guild_id, 'logging': {'channel': channel_id}})
            else:
                self.servers.update({'guildId': guild_id}, {'$set': {'logging.channel': channel_id}})
            return True
        except:
            return False
        
    def logging_set_key(self, guild_id, key, state):
        """ enable disable logging features """
        guild = self.servers.find_one({'guildId': guild_id})
        if not guild:
            return False  # no point setting this if there is no channel configured
        else:
            self.servers.update({'guildId': guild_id}, {'$set': {f'logging.{key}': state}})
        return True

    