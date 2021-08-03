import discord
from discord.ext import commands



class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db


    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! ``{round(self.bot.latency * 1000, 2)}ms``")


    @commands.command()
    async def help(self, ctx):
        await ctx.send("🎉 **__Command list__** 🎉\n```\n%start <winners> <length> <prize...> \n%end <giveaway_id> \n%ping \n%help \n```")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("💥 You're miissing the required permissions to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("💥 Looks like you're missing a required command argument.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("💥 Looks like one or more of your passed arguments are not from the correct type.")

def setup(bot):
    bot.add_cog(Meta(bot))