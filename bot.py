import discord
from discord.ext import commands

from toolbox import (
    S, 
    Database,
    Collection
)



class DB(Database):
    def __init__(self, name: str, host: str, *args, port: int = None, **kwargs):
        super().__init__(name, host, *args, port=port, **kwargs)
        self.gw = Collection(self, "giveaways")


class GiveawayBot(commands.AutoShardedBot):
    def __init__(self, config: dict, *args, **kwargs):
        self.config = S(config)
        super().__init__(
            command_prefix=self.config.prefix,
            intents=discord.Intents.all(),
            chunk_guilds_at_startup=True
        )

        self.ready = False
        self.db = DB(self.config.db_name, self.config.db_host, port=self.config.db_port)


    async def on_ready(self):
        if not self.ready:
            for p in self.config.plugins:
                try:
                    self.load_extension(f"plugins.{p}")
                except Exception as ex:
                    print(f"Failed to load {p} - {ex}")
        
            print("Ready as {0.name}#{0.discriminator} ({0.id})".format(self.user))
            self.ready = True

    
    def run(self):
        super().run(self.config.token)