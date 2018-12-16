import json

class Config():
    @staticmethod
    def get_config():
        try:
            with open("config.json", "r") as read_file:
                config = json.load(read_file)
        except FileNotFoundError:
            config = dict()
        return config

    @staticmethod
    def set_config(config):
        if not all(k in config for k in ('token', 'prefix', 'game', 'mongodb')):
            raise ValueError

        with open("config.json", "w") as write_file:
            json.dump(config, write_file)
    
    @staticmethod
    def set_token(token):
        config = Config.get_config()
        config['token'] = token
        Config.set_config(config)
    
    @staticmethod
    def set_prefix(prefix):
        config = Config.get_config()
        config['prefix'] = prefix
        Config.set_config(config)

    @staticmethod
    def set_game(game):
        config = Config.get_config()
        config['game'] = game
        Config.set_config(config)
    
    @staticmethod
    def set_mongodb(mongodb):
        config = Config.get_config()
        config['mongodb'] = mongodb
        Config.set_config(mongodb)