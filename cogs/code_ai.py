import os
import discord
from discord.ext import commands
from groq import Groq


GROQ_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = None


def handle_api_error(e):
    err = str(e)
    if "insufficient_quota" in err or "429" in err:
        return "API limit asildi! Biraz bekleyip tekrar deneyin."
    if "invalid_api_key" in err or "401" in err:
        return "Gecersiz API key! .env dosyasindaki GROQ_API_KEY degerini kontrol edin."
    return f"API hatasi: {e}"


class CodeAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = None
        if GROQ_KEY:
            self.client = Groq(api_key=GROQ_KEY)

    def get_prompt(self):
        creator = getattr(self.bot, "creator_name", "Bilinmiyor")
        return f"""Sen yardimsever bir kod asistanisin. Kullanilarin kod sorularini cevapliyorsun.
Yaraticin: {creator}
Kurallarin:
- Kisa ve net cevap ver
- Kod ornekleri ver
- Turkce cevap ver
- Kod bloklarini ``` dili``` seklinde formatla
- Hata varsa acikla ve duzeltme oner
- Gereksiz uzun aciklamalardan kacin
- Eger "seni kim yapti", "yaraticin kim", "sahibin kim" gibi sorular sorulursa, yaraticinin "{creator}" oldugunu soyle."""

    @commands.command(name="sor", aliases=["soru", "question"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sor(self, ctx, *, soru: str):
        if not self.client:
            await ctx.send("Groq API anahtari ayarlanmamis! `.env` dosyasinda `GROQ_API_KEY` gerekli.")
            return

        await ctx.defer()

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.get_prompt()},
                    {"role": "user", "content": soru},
                ],
                max_tokens=2000,
                temperature=0.7,
            )

            cevap = response.choices[0].message.content

            if len(cevap) > 2000:
                parts = [cevap[i : i + 2000] for i in range(0, len(cevap), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                embed = discord.Embed(
                    title="Yanit",
                    description=cevap,
                    color=discord.Color.blue(),
                )
                embed.set_footer(text=f"Soru: {soru[:100]}...")
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(handle_api_error(e))

    @commands.command(name="duzelt", aliases=["fix", "hatalari_bul"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def duzelt(self, ctx, *, kod: str):
        if not self.client:
            await ctx.send("Groq API anahtari ayarlanmamis!")
            return

        await ctx.defer()

        prompt = f"""Asagidaki kodu analiz et. Varsa hatalari bul, acikla ve duzeltilmis versiyonunu ver:

```
{kod}
```

Cevap formati:
1. Bulunan hatalar
2. Aciklama
3. Duzeltilmis kod"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.get_prompt()},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.3,
            )

            cevap = response.choices[0].message.content

            if len(cevap) > 2000:
                parts = [cevap[i : i + 2000] for i in range(0, len(cevap), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                embed = discord.Embed(
                    title="Kod Duzeltme",
                    description=cevap,
                    color=discord.Color.orange(),
                )
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(handle_api_error(e))

    @commands.command(name="acikla", aliases=["explain", "anlat"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def acikla(self, ctx, dil: str, *, kod: str):
        if not self.client:
            await ctx.send("Groq API anahtari ayarlanmamis!")
            return

        await ctx.defer()

        prompt = f"""Asagidaki {dil} kodunu satir satir acikla. Her adimi kolay anlasilir sekilde anlat:

```{dil}
{kod}
```"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.get_prompt()},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.5,
            )

            cevap = response.choices[0].message.content
            if len(cevap) > 2000:
                parts = [cevap[i : i + 2000] for i in range(0, len(cevap), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                embed = discord.Embed(
                    title=f"{dil.upper()} Kod Aciklamasi",
                    description=cevap,
                    color=discord.Color.green(),
                )
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(handle_api_error(e))

    @commands.command(name="cevir", aliases=["convert", "donustur"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def cevir(self, ctx, dil1: str, dil2: str, *, kod: str):
        if not self.client:
            await ctx.send("Groq API anahtari ayarlanmamis!")
            return

        await ctx.defer()

        prompt = f"Asagidaki {dil1} kodunu {dil2} diline cevir. Sadece cevirilmis kodu ver:\n\n```{dil1}\n{kod}\n```"

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.get_prompt()},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.3,
            )

            cevap = response.choices[0].message.content
            if len(cevap) > 2000:
                parts = [cevap[i : i + 2000] for i in range(0, len(cevap), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                embed = discord.Embed(
                    title=f"{dil1.upper()} -> {dil2.upper()} Donusumu",
                    description=cevap,
                    color=discord.Color.purple(),
                )
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(handle_api_error(e))

    @commands.command(name="guvenli", aliases=["security", "guvenlik", "audit"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def guvenli(self, ctx, dil: str, *, kod: str):
        if not self.client:
            await ctx.send("Groq API anahtari ayarlanmamis!")
            return

        await ctx.defer()

        prompt = f"""Asagidaki {dil} kodunun guvenlik analizini yap. Su konulari kontrol et:

1. SQL Injection riski
2. XSS (Cross-Site Scripting) acigi
3. Hardcoded sifre/secret/anahtar
4. Guvensiz dosya okuma/yazma
5. Input dogrulama eksikligi
6. Guvensiz cifreleme
7. Race condition riski
8. Hatali hata yonetimi (bilgi sizintisi)
9. Guvensiz dependency
10. Buffer overflow riski

Her bulgu icin:
- Tehlike seviyesi (YUKSEK / ORTA / DUSUK)
- Aciklama
- Duzeltme onerisi

```
{kod}
```"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.get_prompt()},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.3,
            )

            cevap = response.choices[0].message.content

            if len(cevap) > 2000:
                parts = [cevap[i : i + 2000] for i in range(0, len(cevap), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                embed = discord.Embed(
                    title=f"{dil.upper()} Guvenlik Analizi",
                    description=cevap,
                    color=discord.Color.red(),
                )
                embed.set_footer(text="Tehlike seviyeleri: YUKSEK = kirmizi, ORTA = turuncu, DUSUK = yesil")
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(handle_api_error(e))


async def setup(bot):
    await bot.add_cog(CodeAI(bot))
