import discord
from discord.ext import commands
import httpx


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ip", aliases=["ipbilgi", "ipinfo"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ip(self, ctx, adres: str):
        await ctx.defer()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://ip-api.com/json/{adres}")
                data = response.json()

            if data.get("status") == "fail":
                await ctx.send(f"IP adresi bulunamadi: `{adres}`")
                return

            embed = discord.Embed(
                title=f"IP Bilgisi: {data.get('query', adres)}",
                color=discord.Color.blue(),
            )

            embed.add_field(name="Ulke", value=data.get("country", "Bilinmiyor"), inline=True)
            embed.add_field(name="Sehir", value=data.get("city", "Bilinmiyor"), inline=True)
            embed.add_field(name="Bolge", value=data.get("regionName", "Bilinmiyor"), inline=True)
            embed.add_field(name="ISP", value=data.get("isp", "Bilinmiyor"), inline=True)
            embed.add_field(name="Organizasyon", value=data.get("org", "Bilinmiyor"), inline=True)
            embed.add_field(name="AS", value=data.get("as", "Bilinmiyor"), inline=True)
            embed.add_field(name="Enlem", value=str(data.get("lat", "Bilinmiyor")), inline=True)
            embed.add_field(name="Boylam", value=str(data.get("lon", "Bilinmiyor")), inline=True)
            embed.add_field(name="Timezone", value=data.get("timezone", "Bilinmiyor"), inline=True)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Hata olustu: {e}")

    @commands.command(name="json", aliases=["formatjson", "jsonformat"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def json_format(self, ctx, *, veri: str):
        import json

        try:
            parsed = json.loads(veri)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)

            if len(formatted) > 1900:
                await ctx.send(f"JSON cok uzun:\n```json\n{formatted[:1900]}...\n```")
            else:
                await ctx.send(f"```json\n{formatted}\n```")
        except json.JSONDecodeError as e:
            await ctx.send(f"Gecersiz JSON: {e}")

    @commands.command(name="hash", aliases=["md5", "sha256"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hash(self, ctx, tur: str = "sha256", *, metin: str = None):
        if metin is None:
            metin = tur
            tur = "sha256"

        import hashlib

        tur = tur.lower()
        if tur == "md5":
            result = hashlib.md5(metin.encode()).hexdigest()
        elif tur == "sha1":
            result = hashlib.sha1(metin.encode()).hexdigest()
        elif tur == "sha256":
            result = hashlib.sha256(metin.encode()).hexdigest()
        elif tur == "sha512":
            result = hashlib.sha512(metin.encode()).hexdigest()
        else:
            await ctx.send("Desteklenen turler: `md5`, `sha1`, `sha256`, `sha512`")
            return

        embed = discord.Embed(
            title=f"{tur.upper()} Hash",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Girdi", value=f"```\n{metin}\n```", inline=False)
        embed.add_field(name="Sonuc", value=f"```\n{result}\n```", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="base64", aliases=["b64"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def base64_cmd(self, ctx, tur: str, *, metin: str):
        import base64

        tur = tur.lower()

        if tur == "encode" or tur == "sifrele":
            result = base64.b64encode(metin.encode()).decode()
            embed = discord.Embed(
                title="Base64 Sifreleme",
                color=discord.Color.green(),
            )
        elif tur == "decode" or tur == "coz":
            try:
                result = base64.b64decode(metin.encode()).decode()
            except Exception:
                await ctx.send("Gecersiz Base64 verisi!")
                return
            embed = discord.Embed(
                title="Base64 Cozme",
                color=discord.Color.blue(),
            )
        else:
            await ctx.send("Kullanim: `!base64 encode <metin>` veya `!base64 decode <metin>`")
            return

        embed.add_field(name="Girdi", value=f"```\n{metin}\n```", inline=False)
        embed.add_field(name="Sonuc", value=f"```\n{result}\n```", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="renk", aliases=["color", "renkbul"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def renk(self, ctx, hex_kod: str):
        hex_kod = hex_kod.lstrip("#")

        try:
            r = int(hex_kod[0:2], 16)
            g = int(hex_kod[2:4], 16)
            b = int(hex_kod[4:6], 16)
        except ValueError:
            await ctx.send("Gecersiz hex kodu! Ornek: `!renk FF5733`")
            return

        embed = discord.Embed(
            title=f"Renk: #{hex_kod.upper()}",
            color=discord.Color.from_rgb(r, g, b),
        )
        embed.add_field(name="RGB", value=f"R: {r}, G: {g}, B: {b}", inline=True)
        embed.add_field(name="Hex", value=f"#{hex_kod.upper()}", inline=True)
        embed.set_thumbnail(url=f"https://singlecolorimage.com/get/{hex_kod}/200x200")
        await ctx.send(embed=embed)

    @commands.command(name="hava", aliases=["weather", "havadurumu"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hava(self, ctx, *, sehir: str):
        await ctx.defer()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://wttr.in/{sehir}?format=j1",
                    headers={"Accept": "application/json"},
                )
                data = response.json()

            current = data.get("current_condition", [{}])[0]
            area = data.get("nearest_area", [{}])[0]

            temp_c = current.get("temp_C", "?")
            feels_like = current.get("FeelsLikeC", "?")
            humidity = current.get("humidity", "?")
            wind_speed = current.get("windspeedKmph", "?")
            wind_dir = current.get("winddir16Point", "?")
            desc = current.get("weatherDesc", [{}])[0].get("value", "Bilinmiyor")
            visibility = current.get("visibility", "?")
            pressure = current.get("pressure", "?")
            uv = current.get("uvIndex", "?")

            area_name = area.get("areaName", [{}])[0].get("value", sehir)
            country = area.get("country", [{}])[0].get("value", "?")

            emoji_map = {
                "sunny": "☀️",
                "clear": "🌙",
                "partly cloudy": "⛅",
                "cloudy": "☁️",
                "overcast": "☁️",
                "mist": "🌫️",
                "fog": "🌫️",
                "light rain": "🌦️",
                "moderate rain": "🌧️",
                "heavy rain": "🌧️",
                "light snow": "🌨️",
                "snow": "❄️",
                "thunderstorm": "⛈️",
                "rain": "🌧️",
            }

            desc_lower = desc.lower()
            emoji = "🌡️"
            for key, val in emoji_map.items():
                if key in desc_lower:
                    emoji = val
                    break

            embed = discord.Embed(
                title=f"{emoji} {area_name}, {country} Hava Durumu",
                color=discord.Color.from_rgb(100, 180, 255),
            )

            embed.add_field(name="Durum", value=desc, inline=True)
            embed.add_field(name="Sicaklik", value=f"{temp_c}°C", inline=True)
            embed.add_field(name="Hissedilen", value=f"{feels_like}°C", inline=True)
            embed.add_field(name="Nem", value=f"%{humidity}", inline=True)
            embed.add_field(name="Ruzgar", value=f"{wind_speed} km/s {wind_dir}", inline=True)
            embed.add_field(name="Gorus", value=f"{visibility} km", inline=True)
            embed.add_field(name="Basinc", value=f"{pressure} hPa", inline=True)
            embed.add_field(name="UV Indeksi", value=uv, inline=True)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Hava durumu alinamadi: {e}")


async def setup(bot):
    await bot.add_cog(Tools(bot))
