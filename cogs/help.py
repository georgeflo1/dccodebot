import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = bot.command_prefix

    @commands.command(name="yardim", aliases=["komutlar", "commands"])
    async def yardim(self, ctx):
        embed = discord.Embed(
            title="Kod Yardim Botu - Komutlar",
            description="Tum komutlar asagida listelenmistir.",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="AI Komutlari",
            value=(
                f"`{self.prefix}ai <soru>` - AI'ye herhangi bir soru sor\n"
                f"`{self.prefix}sor <soru>` - AI'ye kod sorusu sor\n"
                f"`{self.prefix}duzelt <kod>` - Kodundaki hatalari bul ve duzelt\n"
                f"`{self.prefix}acikla <dil> <kod>` - Kodu satir satir acikla\n"
                f"`{self.prefix}cevir <dil1> <dil2> <kod>` - Kodu baska dile cevir\n"
                f"`{self.prefix}guvenli <dil> <kod>` - Kod guvenlik analizi yap"
            ),
            inline=False,
        )

        embed.add_field(
            name="Araclar",
            value=(
                f"`{self.prefix}json <veri>` - JSON formatla\n"
                f"`{self.prefix}hash <tur> <metin>` - Metin hashle\n"
                f"`{self.prefix}base64 <encode/decode> <metin>` - Base64 cevir\n"
                f"`{self.prefix}renk <hex>` - Renk kodunu goster"
            ),
            inline=False,
        )

        embed.add_field(
            name="OSINT",
            value=(
                f"`{self.prefix}username <kullanici>` - Kullanici adi sorgula\n"
                f"`{self.prefix}domain <domain>` - Domain bilgisi\n"
                f"`{self.prefix}dns <domain>` - DNS sorgusu\n"
                f"`{self.prefix}email <email>` - Email analizi\n"
                f"`{self.prefix}github <kullanici>` - GitHub profili\n"
                f"`{self.prefix}subdomain <domain>` - Subdomain bul\n"
                f"`{self.prefix}telefonbilgi <numara>` - Telefon numarasi analizi"
            ),
            inline=False,
        )

        embed.add_field(
            name="Bilgi Komutlari",
            value=(
                f"`{self.prefix}diller` - Desteklenen dilleri listele\n"
                f"`{self.prefix}botbilgi` - Bot hakkinda bilgi\n"
                f"`{self.prefix}ping` - Bot gecikmesini goster\n"
                f"`{self.prefix}yaratıcı` - Bot yaraticisini goster\n"
                f"`{self.prefix}hava <sehir>` - Hava durumu ogren\n"
                f"`{self.prefix}ip <adres>` - IP adresi bilgisi"
            ),
            inline=False,
        )

        embed.set_footer(text=f"Prefix: {self.prefix} | Sorulariniz icin komut ustune tiklayin")
        await ctx.send(embed=embed)

    @commands.command(name="botbilgi", aliases=["botinfo", "istatistik"])
    async def botbilgi(self, ctx):
        embed = discord.Embed(
            title="Bot Bilgileri",
            color=discord.Color.green(),
        )
        embed.add_field(name="Sunucu Sayisi", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Kullanici Sayisi", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Komut Sayisi", value=str(len(self.bot.commands)), inline=True)
        embed.add_field(name="Gecikme", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Python", value="3.10+", inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Pong!",
            description=f"Gecikme: **{latency}ms**",
            color=discord.Color.orange() if latency > 200 else discord.Color.green(),
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
