import discord
from discord.ext import commands
import aiohttp
import re
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = "https://api.alquran.cloud/v1/ayah/{0}/editions/quran-simple,en.sahih"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="Q", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    match = re.match(r"Q(\d+):(\d+)(?:-(\d+))?", message.content.strip())
    if match:
        surah = int(match.group(1))
        start_ayah = int(match.group(2))
        end_ayah = int(match.group(3)) if match.group(3) else start_ayah

        if end_ayah < start_ayah:
            await message.channel.send("❗ End verse must be greater than or equal to start verse.")
            return

        await message.channel.send(f"📖 Fetching verses {start_ayah} to {end_ayah} from Surah {surah}...")

        async with aiohttp.ClientSession() as session:
            verses = []
            for ayah_num in range(start_ayah, end_ayah + 1):
                ayah_id = f"{surah}:{ayah_num}"
                async with session.get(API_URL.format(ayah_id)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            arabic = data['data'][0]['text']
                            english = data['data'][1]['text']
                            verses.append(f"**{surah}:{ayah_num}**\n🇸🇦 {arabic}\n🇬🇧 {english}\n")
                        except (KeyError, IndexError, TypeError):
                            verses.append(f"⚠️ Invalid data for {ayah_id}")
                    else:
                        verses.append(f"❌ Could not fetch verse {ayah_id}")

            # Split message if it's too long
            output = "\n".join(verses)
            if len(output) > 2000:
                chunks = [output[i:i+1900] for i in range(0, len(output), 1900)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(output)

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(TOKEN)
