import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

ALLOWED_GUILD_ID = 1528448910329249852

@bot.check
async def guild_only(ctx):
    if ctx.guild and ctx.guild.id == ALLOWED_GUILD_ID:
        return True
    raise commands.CheckFailure("Bu bot sadece yetkili sunucuda calisir.")

INITIAL_EXTENSIONS = [
    "cogs.help",
    "cogs.code_ai",
    "cogs.code_utils",
    "cogs.tools",
    "cogs.osint",
]

CREATOR_ID = 1083108476882006026
bot.creator_name = None

@bot.event
async def on_ready():
    print(f"Bot giris yapti: {bot.user} (ID: {bot.user.id})")
    print(f"Sunucu sayisi: {len(bot.guilds)}")
    print(f"Komut on ek: {PREFIX}")
    try:
        creator = await bot.fetch_user(CREATOR_ID)
        bot.creator_name = creator.name
        print(f"Yaratici: {bot.creator_name}")
    except:
        bot.creator_name = "Bilinmiyor"
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{PREFIX}yardim | Kod yardimi"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Bu komut bulunamadi. `{PREFIX}yardim` ile komutlara bakabilirsin.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Eksik parametre! Dogru kullanin: `{PREFIX}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Bu komutu tekrar kullanmak icin {error.retry_after:.1f} saniye bekleyin.")
    elif isinstance(error, commands.CheckFailure):
        return
    else:
        await ctx.send(f"Hata olustu: {error}")
        raise error

@bot.command(name="reload")
@commands.is_owner()
async def reload_cog(ctx, *, cog_name: str):
    try:
        await bot.reload_extension(cog_name)
        await ctx.send(f"`{cog_name}` basariyla yeniden yuklendi.")
    except Exception as e:
        await ctx.send(f"Yeniden yukleme basarisiz: {e}")

CREATOR_ID = 1083108476882006026

@bot.command(name="yaratıcı", aliases=["sahip", "owner", "creator", "kimin", "kimyapti"])
async def yaratici(ctx):
    creator = await bot.fetch_user(CREATOR_ID)
    embed = discord.Embed(
        title="Yaratici",
        description=f"Bu bot **{creator.name}** tarafindan yazildi.",
        color=discord.Color.gold(),
    )
    embed.set_thumbnail(url=creator.display_avatar.url)
    embed.add_field(name="Discord", value=f"{creator.name}#{creator.discriminator}", inline=True)
    embed.add_field(name="ID", value=str(CREATOR_ID), inline=True)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    async def main():
        async with bot:
            for ext in INITIAL_EXTENSIONS:
                await bot.load_extension(ext)
            await bot.start(TOKEN)
    import asyncio
    asyncio.run(main())
