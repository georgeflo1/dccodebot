import discord
from discord.ext import commands
import httpx
import socket
import re
import json


class OSINT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="username", aliases=["kullanicicek", "usercheck"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def username(self, ctx, *, kullanici_adi: str):
        await ctx.defer()

        platformlar = {
            "Instagram": f"https://www.instagram.com/{kullanici_adi}/",
            "Twitter/X": f"https://x.com/{kullanici_adi}",
            "TikTok": f"https://www.tiktok.com/@{kullanici_adi}",
            "GitHub": f"https://github.com/{kullanici_adi}",
            "YouTube": f"https://www.youtube.com/@{kullanici_adi}",
            "Reddit": f"https://www.reddit.com/user/{kullanici_adi}",
            "Twitch": f"https://www.twitch.tv/{kullanici_adi}",
            "Pinterest": f"https://www.pinterest.com/{kullanici_adi}",
            "Telegram": f"https://t.me/{kullanici_adi}",
            "Spotify": f"https://open.spotify.com/user/{kullanici_adi}",
        }

        bulunanlar = []
        bulunmayanlar = []

        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            for platform, url in platformlar.items():
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        bulunanlar.append(f"**{platform}**: {url}")
                    else:
                        bulunmayanlar.append(platform)
                except Exception:
                    bulunmayanlar.append(f"{platform} (hata)")

        embed = discord.Embed(
            title=f"OSINT: {kullanici_adi}",
            color=discord.Color.blue(),
        )

        if bulunanlar:
            embed.add_field(
                name=f"Bulunanlar ({len(bulunanlar)})",
                value="\n".join(bulunanlar),
                inline=False,
            )

        if bulunmayanlar:
            embed.add_field(
                name=f"Bulunamayanlar ({len(bulunmayanlar)})",
                value=", ".join(bulunmayanlar),
                inline=False,
            )

        embed.set_footer(text="Sonuclar her zaman kesin degildir, manuel kontrol gerekli olabilir.")
        await ctx.send(embed=embed)

    @commands.command(name="domain", aliases=["whois", "domainbilgi"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def domain(self, ctx, *, domain_adi: str):
        await ctx.defer()

        domain_adi = domain_adi.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")

        try:
            ip_adresi = socket.gethostbyname(domain_adi)
        except socket.gaierror:
            await ctx.send(f"Domain bulunamadi: `{domain_adi}`")
            return

        embed = domain_bilgisi = discord.Embed(
            title=f"Domain: {domain_adi}",
            color=discord.Color.green(),
        )

        embed.add_field(name="IP Adresi", value=ip_adresi, inline=True)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"http://ip-api.com/json/{ip_adresi}")
                data = response.json()

            if data.get("status") == "success":
                embed.add_field(name="Ulke", value=data.get("country", "?"), inline=True)
                embed.add_field(name="Sehir", value=data.get("city", "?"), inline=True)
                embed.add_field(name="ISP", value=data.get("isp", "?"), inline=True)
                embed.add_field(name="Organizasyon", value=data.get("org", "?"), inline=True)
        except Exception:
            pass

        try:
            ip_parts = ip_adresi.split(".")
            reverse_dns = ".".join(reversed(ip_parts)) + ".in-addr.arpa"
            ptr_records = socket.getaddrinfo(domain_adi, None)
        except Exception:
            pass

        await ctx.send(embed=embed)

    @commands.command(name="dns", aliases=["dnsquery", "dnskayit"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def dns(self, ctx, domain_adi: str, tur: str = "ALL"):
        await ctx.defer()

        tur = tur.upper()
        embed = discord.Embed(
            title=f"DNS: {domain_adi}",
            color=discord.Color.purple(),
        )

        try:
            ip_adresi = socket.gethostbyname(domain_adi)
            embed.add_field(name="A Kaydi", value=ip_adresi, inline=True)
        except Exception:
            embed.add_field(name="A Kaydi", value="Bulunamadi", inline=True)

        try:
            cname = socket.getfqdn(domain_adi)
            if cname != domain_adi:
                embed.add_field(name="CNAME", value=cname, inline=True)
        except Exception:
            pass

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"https://dns.google/resolve?name={domain_adi}&type=ANY"
                )
                data = response.json()

            for record in data.get("Answer", []):
                rtype = record.get("type", 0)
                value = record.get("data", "?")

                type_map = {1: "A", 2: "NS", 5: "CNAME", 15: "MX", 16: "TXT", 28: "AAAA"}
                type_name = type_map.get(rtype, str(rtype))

                if type_name == "MX":
                    embed.add_field(name="MX", value=value, inline=False)
                elif type_name == "TXT":
                    embed.add_field(name="TXT", value=f"`{value}`", inline=False)
                elif type_name == "NS":
                    embed.add_field(name="NS", value=value, inline=True)

        except Exception:
            pass

        embed.set_footer(text="Desteklenen turler: A, AAAA, CNAME, MX, TXT, NS")
        await ctx.send(embed=embed)

    @commands.command(name="email", aliases=["emailkontrol", "emailcheck"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def email(self, ctx, *, email_adresi: str):
        await ctx.defer()

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        gecerli = bool(re.match(email_regex, email_adresi))

        domain = email_adresi.split("@")[1] if gecerli else "?"

        embed = discord.Embed(
            title=f"Email Analizi: {email_adresi}",
            color=discord.Color.orange(),
        )

        embed.add_field(name="Gecerli", value="Evet" if gecerli else "Hayir", inline=True)
        embed.add_field(name="Domain", value=domain, inline=True)

        if gecerli:
            try:
                mx_records = socket.getaddrinfo(domain, 25)
                embed.add_field(name="MX Kaydi", value="Mevcut", inline=True)
            except Exception:
                embed.add_field(name="MX Kaydi", value="Bulunamadi", inline=True)

            try:
                disposable = ["tempmail.com", "throwaway.com", "guerrillamail.com",
                              "mailinator.com", "yopmail.com", "sharklasers.com"]
                if domain.lower() in disposable:
                    embed.add_field(name="Gecici Email", value="Evet (guvenilmez)", inline=True)
                else:
                    embed.add_field(name="Gecici Email", value="Hayir", inline=True)
            except Exception:
                pass

        embed.set_footer(text="Email dogrulama sadece temel kontroller yapar.")
        await ctx.send(embed=embed)

    @commands.command(name="github", aliases=["gh", "gitprofile"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def github(self, ctx, *, kullanici: str):
        await ctx.defer()

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"https://api.github.com/users/{kullanici}")

                if response.status_code == 404:
                    await ctx.send(f"GitHub kullanici bulunamadi: `{kullanici}`")
                    return

                data = response.json()

                repo_response = await client.get(f"https://api.github.com/users/{kullanici}/repos?per_page=100")
                repos = repo_response.json()
                repo_count = len(repos) if isinstance(repos, list) else 0

                embed = discord.Embed(
                    title=f"GitHub: {data.get('login', kullanici)}",
                    url=data.get("html_url", ""),
                    description=data.get("bio", "Bio yok"),
                    color=discord.Color.gray(),
                )

                embed.set_thumbnail(url=data.get("avatar_url", ""))

                embed.add_field(name="Isim", value=data.get("name", "Yok"), inline=True)
                embed.add_field(name="Konum", value=data.get("location", "Yok"), inline=True)
                embed.add_field(name="Blog", value=data.get("blog", "Yok") or "Yok", inline=True)
                embed.add_field(name="Repo Sayisi", value=str(repo_count), inline=True)
                embed.add_field(name="Takipci", value=str(data.get("followers", 0)), inline=True)
                embed.add_field(name="Takip", value=str(data.get("following", 0)), inline=True)
                embed.add_field(name="Kurulus", value=str(data.get("created_at", "?")[:10]), inline=True)

                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Hata: {e}")

    @commands.command(name="subdomain", aliases=["subbul", "subdomainbul"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def subdomain(self, ctx, *, domain_adi: str):
        await ctx.defer()

        domain_adi = domain_adi.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")

        common_subs = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
            "ns3", "ns4", "cpanel", "whm", "webdisk", "autodiscover", "autoconfig",
            "m", "mobile", "imap", "remote", "blog", "webhost", "admin", "test",
            "dev", "staging", "api", "cdn", "assets", "img", "images", "static",
            "vpn", "gateway", "portal", "app", "shop", "store", "beta", "demo",
            "forum", "community", "help", "support", "docs", "wiki", "status",
        ]

        bulunanlar = []

        async with httpx.AsyncClient(follow_redirects=True, timeout=5) as client:
            for sub in common_subs:
                url = f"{sub}.{domain_adi}"
                try:
                    response = await client.get(f"http://{url}")
                    if response.status_code:
                        bulunanlar.append(f"`{url}` (HTTP {response.status_code})")
                except Exception:
                    try:
                        socket.gethostbyname(url)
                        bulunanlar.append(f"`{url}` (DNS var)")
                    except Exception:
                        pass

        embed = discord.Embed(
            title=f"Subdomain: {domain_adi}",
            color=discord.Color.red(),
        )

        if bulunanlar:
            embed.add_field(
                name=f"Bulunanlar ({len(bulunanlar)})",
                value="\n".join(bulunanlar[:20]),
                inline=False,
            )
        else:
            embed.add_field(name="Sonuc", value="Subdomain bulunamadi.", inline=False)

        embed.set_footer(text="Bu komut sinirli subdomain listesi ile calisir.")
        await ctx.send(embed=embed)

    @commands.command(name="telefonbilgi", aliases=["phonebilgi", "telefon", "numarabilgi"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def telefonbilgi(self, ctx, *, numara: str):
        await ctx.defer()

        numara_temiz = re.sub(r'[^0-9+]', '', numara)

        embed = discord.Embed(
            title=f"Telefon Analizi: {numara}",
            color=discord.Color.orange(),
        )

        try:
            if numara_temiz.startswith("+"):
                ulke_kodlari = {
                    "+1": "ABD/Kanada", "+44": "Ingiltere", "+49": "Almanya",
                    "+33": "Fransa", "+39": "Italya", "+34": "Ispanya",
                    "+90": "Turkiye", "+966": "Suudi Arabistan", "+971": "BAE",
                    "+7": "Rusya", "+86": "Cin", "+81": "Japonya",
                    "+82": "Guney Kore", "+91": "Hindistan", "+61": "Avustralya",
                    "+55": "Brezilya", "+52": "Meksika", "+27": "Guney Afrika",
                    "+31": "Hollanda", "+46": "Isvec", "+47": "Norvec",
                    "+48": "Polonya", "+358": "Finlandiya", "+45": "Danimarka",
                    "+353": "Irlanda", "+351": "Portekiz", "+30": "Yunanistan",
                    "+43": "Avusturya", "+41": "Isvicre", "+32": "Belcika",
                }

                for kod, ulke in ulke_kodlari.items():
                    if numara_temiz.startswith(kod):
                        embed.add_field(name="Ulke", value=ulke, inline=True)
                        embed.add_field(name="Ulke Kodu", value=kod, inline=True)
                        break
                else:
                    embed.add_field(name="Ulke Kodu", value=numara_temiz[:4], inline=True)
            else:
                embed.add_field(name="Tur", value="Yerel numara", inline=True)

            uzunluk = len(numara_temiz)
            embed.add_field(name="Numara Uzunlugu", value=str(uzunluk), inline=True)

            if numara_temiz.startswith("+90") or numara_temiz.startswith("0"):
                embed.add_field(name="Ulke", value="Turkiye", inline=True)

                temiz_num = numara_temiz.lstrip("+90").lstrip("0")
                if len(temiz_num) >= 4:
                    operator_kodlari = {
                        "53": "Turkcell", "54": "Turkcell", "50": "Vodafone",
                        "55": "Turkcell", "51": "Vodafone", "52": "Vodafone",
                    }
                    ilk_iki = temiz_num[:2]
                    if ilk_iki in operator_kodlari:
                        embed.add_field(name="Operator", value=operator_kodlari[ilk_iki], inline=True)

            embed.add_field(
                name="Numara Formatlari",
                value=(
                    f"```\n"
                    f"Ham: {numara_temiz}\n"
                    f"Uluslararasi: {numara}\n"
                    f"```\n"
                ),
                inline=False,
            )

        except Exception as e:
            embed.add_field(name="Hata", value=str(e), inline=False)

        embed.set_footer(text="Bu analiz sadece temel bilgiler verir, kesin dogru olmayabilir.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OSINT(bot))
