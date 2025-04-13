import discord
from discord.ext import commands
import aiohttp
import re
import os
from dotenv import load_dotenv  # ✅ STEP 1: Import dotenv and os

load_dotenv()  # ✅ STEP 2: Load the .env file

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # ✅ STEP 3: Get your token from .env

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

API_URL = "http://api.alquran.cloud/v1/ayah/{}/en.asad"

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

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
            await message.channel.send("End verse must be greater than start verse.")
            return

        await message.channel.send(f"Fetching verses {start_ayah} to {end_ayah} from Surah {surah}...")

        async with aiohttp.ClientSession() as session:
            verses = []
            for ayah_num in range(start_ayah, end_ayah + 1):
                ayah_id = f"{surah}:{ayah_num}"
                async with session.get(API_URL.format(ayah_id)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        verse_text = data['data']['text']
                        verses.append(f"**{surah}:{ayah_num}** – {verse_text}")
                    else:
                        verses.append(f"Could not fetch verse {surah}:{ayah_num}")

            await message.channel.send("\n".join(verses))

    await bot.process_commands(message)

# ✅ STEP 4: Use the token from the environment
bot.run(TOKEN)
