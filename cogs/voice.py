import discord
from discord.ext import commands, tasks


class VoiceKeepAlive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channel_id = None
        self.auto_reconnect.start()

    def cog_unload(self):
        self.auto_reconnect.cancel()

    @tasks.loop(seconds=30)
    async def auto_reconnect(self):
        if self.target_channel_id is None:
            return

        target = self.bot.get_channel(self.target_channel_id)
        if target is None:
            self.target_channel_id = 1528448911478620334
            return

        for guild in self.bot.guilds:
            vc = guild.voice_client
            if vc is None:
                try:
                    await target.connect()
                except Exception:
                    pass
            elif vc.channel is None or vc.channel.id != self.target_channel_id:
                try:
                    await vc.move_to(target)
                except Exception:
                    pass

    @auto_reconnect.before_loop
    async def before_auto_reconnect(self):
        await self.bot.wait_until_ready()

    @commands.command(name="seskatil", aliases=["joinspace", "ses", "katil"])
    @commands.has_permissions(administrator=True)
    async def seskatil(self, ctx, *, kanal: discord.VoiceChannel = None):
        if kanal is None:
            if ctx.author.voice and ctx.author.voice.channel:
                kanal = ctx.author.voice.channel
            else:
                await ctx.send("Bir ses kanalinda olman lazim veya kanal adi yaz: `!seskatil #kanal`")
                return

        try:
            if ctx.voice_client:
                await ctx.voice_client.move_to(kanal)
            else:
                await kanal.connect()
        except Exception as e:
            await ctx.send(f"Ses kanalina katilamadim: {e}")
            return

        self.target_channel_id = kanal.id

        embed = discord.Embed(
            title="Ses Kanalina Katildi",
            description=f"**{kanal.name}** kanalina katildim. Artik surekli burada kalacagim.",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="sescik", aliases=["leave", "ayril", "sescikar"])
    @commands.has_permissions(administrator=True)
    async def sescik(self, ctx):
        self.target_channel_id = None

        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            embed = discord.Embed(
                title="Ses Kanalindan Ayrildi",
                description="Ses kanalindan ciktim.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Zaten bir ses kanalinda degilim.")

    @commands.command(name="seshatirlat", aliases=["voiceping", "sesbilgi"])
    async def seshatirlat(self, ctx):
        if ctx.voice_client and ctx.voice_client.channel:
            kanal = ctx.voice_client.channel
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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        vc = member.guild.voice_client
        if vc is None or vc.channel is None:
            return

        if len(vc.channel.members) == 1 and vc.channel.members[0].bot:
            if self.target_channel_id:
                channel = self.bot.get_channel(self.target_channel_id)
                if channel:
                    try:
                        await vc.move_to(channel)
                    except Exception:
                        pass


async def setup(bot):
    await bot.add_cog(VoiceKeepAlive(bot))
