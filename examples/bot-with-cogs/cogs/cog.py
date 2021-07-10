from discord import VoiceChannel
from discord.ext import commands
from dcactivity import DCApplication


class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def youtube(self, ctx, channel: VoiceChannel):
        link = await self.bot.dcactivity.create_link(channel, DCApplication.youtube)
        await ctx.send(link)

def setup(bot):
    bot.add_cog(MyCog(bot))