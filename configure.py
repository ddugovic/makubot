import click
import json
from utils import Config

@click.command()
@click.option('--token', help='Change the Bots Discord Token.')
@click.option('--prefix', help='Change the Bots Default Prefix - can be done via command aswell.')
@click.option('--game', help='Change the Bots game-activity - can be done via command aswell.')
@click.option('--mongodb', help='Set the url for mongodb.')
def setup(token, prefix, game):
    try:
        if token:
            Config.set_token(token)
        if prefix:
            Config.set_prefix(prefix)
        if game:
            Config.set_game(game)
        if mongodb:
            Config.set_mongodb(mongodb)
    except ValueError:
        print("ERROR: Not all Configurations set. Use --help to see options.")

if __name__ == '__main__':
    setup()