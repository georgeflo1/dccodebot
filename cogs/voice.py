import discord
from discord.ext import commands


class VoiceKeepAlive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = None

    @commands.command(name="seskatil", aliases=["joinspace", "ses", "katil"])
    @commands.has_permissions(administrator=True)
    async def seskatil(self, ctx, *, kanal: discord.VoiceChannel = None):
        if kanal is None:
            kanal = ctx.author.voice.channel
            if kanal is None:
                await ctx.send("Bir ses kanalinda olman lazim veya kanal adi yaz: `!seskatil #kanal`")
                return

        if ctx.voice_client:
            await ctx.voice_client.move_to(kanal)
        else:
            await kanal.connect()

        self.voice_channel = kanal

        embed = discord.Embed(
            title="Ses Kanalina Katildi",
            description=f"**{kanal.name}** kanalina katildim. Artik surekli burada kalacagim.",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="sescik", aliases=["leave", "ayril", "sescikar"])
    @commands.has_permissions(administrator=True)
    async def sescik(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.voice_channel = None

            embed = discord.Embed(
                title="Ses Kanalindan Ayrildi",
                description="Ses kanalindan ciktim.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Zaten bir ses kanalinda degilim.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        vc = member.guild.voice_client
        if vc is None:
            return

        if len(vc.channel.members) == 1 and vc.channel.members[0].bot:
            pass

    @commands.command(name="seshatirlat", aliases=["voiceping", "sesbilgi"])
    async def seshatirlat(self, ctx):
        if ctx.voice_client:
            kanal = ctx.voice_client.channel
            sure = 0
            if ctx.voice_client.connected_since:
                import time
                sure = int(time.time() - ctx.voice_client.connected_at.timestamp())

            embed = discord.Embed(
                title="Ses Durumu",
                description=f"**{kanal.name}** kanalinda aktifim.",
                color=discord.Color.blue(),
            )
            embed.add_field(name="Kanal", value=kanal.name, inline=True)
            embed.add_field(name="Uye Sayisi", value=str(len(kanal.members)), inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Hicbir ses kanalinda degilim. `!seskatil` ile katil.")


async def setup(bot):
    await bot.add_cog(VoiceKeepAlive(bot))
