import discord
from discord.ext import commands

import datetime
import asyncio
import random

from private.duration import Duration
from private.utils import ends_in



class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.bot.loop.create_task(self.update_giveaways())


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def start(self, ctx, winners: int, length: Duration, *, prize: str):
        if winners > 50:
            return await ctx.send("💥 Too many winners.")

        if length.unit is None:
            length.unit = "m"

        seconds = length.to_seconds(ctx)
        until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))

        e = discord.Embed(
            description=f"React with 🎉 to enter! \nEnds in {ends_in(until)}\nHosted by: {ctx.author.mention}",
            timestamp=until
        )
        e.set_author(
            name=prize
        )
        e.set_footer(
            text="Ends at "
        )
        msg = await ctx.send(content="🎉 **GIVEAWAY** 🎉", embed=e)
        await msg.add_reaction("🎉")

        self.db.gw.insert({
            "id": f"{msg.id}",
            "guild": f"{ctx.guild.id}",
            "channel": f"{ctx.channel.id}",
            "by": f"{ctx.author.id}",
            "winners": winners,
            "until": until,
            "prize": prize,
            "participants": []
        })


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def end(self, ctx, giveaway_id: int):
        if not self.db.gw.exists(f"{giveaway_id}"):
            return await ctx.send("💥 This giveaway doesn't exist.")

        g = self.db.gw.get_doc(f"{giveaway_id}")
        await self.end_giveaway(g)

        await ctx.send("👌 Successfully ended the giveaway!", delete_after=5)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        msg_id = payload.message_id
        user_id = payload.user_id

        if str(payload.emoji) != "🎉":
            return
        
        g_id = f"{msg_id}"
        if not self.db.gw.exists(g_id):
            return
        
        # user checks
        if str(user_id) == str(self.bot.user.id):
            return
        if str(user_id) == self.db.gw.get(g_id, "by"):
            return

        participants = self.db.gw.get(g_id, "participants")
        if user_id in participants:
            return

        participants.append(user_id)
        self.db.gw.update(g_id, "participants", participants)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        msg_id = payload.message_id
        user_id = payload.user_id

        if str(payload.emoji) != "🎉":
            return
        
        g_id = f"{msg_id}"
        if not self.db.gw.exists(g_id):
            return

        # user checks
        if str(user_id) == str(self.bot.user.id):
            return
        if str(user_id) == self.db.gw.get(g_id, "by"):
            return
        
        participants = self.db.gw.get(g_id, "participants")
        if user_id not in participants:
            return

        participants.remove(user_id)
        self.db.gw.update(g_id, "participants", participants)


    async def update_giveaways(self):
        while True:
            await asyncio.sleep(30)
            if len(list(self.db.gw.find({}))) > 0:
                for g in self.db.gw.find():
                    if g["until"] < datetime.datetime.utcnow():
                        await self.end_giveaway(g)
                    else:
                        await self.edit_giveaway(g)


    async def end_giveaway(self, g):
        guild = self.bot.get_guild(int(g["guild"]))
        channel = guild.get_channel(int(g["channel"]))
        msg = await channel.fetch_message(g["id"])

        entrants = len(g["participants"])
        old_embed = msg.embeds[0]
        embed = discord.Embed(color=0x2f3136, description=f"**{entrants}** entrants ↗️")

        out = ""
        if entrants <= g["winners"]:
            out = "Not enough entrants to validate any winners!"
            old_embed.description = f"Not enough entrants to validate any winners"
        else:
            winners = random.sample(entrants, g["winners"])
            winners = ", ".join(f"<@{x}>" for x in winners)
            out = f"Congratulations {winners}! You won the **{g['prize']}**!"
            old_embed.description = f"Winner: {winners}"

        await msg.edit(content="🎉 **GIVEAWAY ENDED** 🎉", embed=old_embed)
        await channel.send(content=out, embed=embed)
        
        self.db.gw.delete(g["id"])


    async def edit_giveaway(self, g):
        guild = self.bot.get_guild(int(g["guild"]))
        channel = guild.get_channel(int(g["channel"]))
        msg = await channel.fetch_message(g["id"])

        old_embed = msg.embeds[0]
        old_embed.description = old_embed.description.replace(old_embed.description.split("\n")[1], f"Ends in {ends_in(g['until'])}")
        await msg.edit(embed=old_embed)
        

def setup(bot):
    bot.add_cog(Giveaway(bot))