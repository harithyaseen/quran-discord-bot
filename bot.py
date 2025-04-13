import discord
from discord.ext import commands
import aiohttp
import re
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

TOKEN = os.getenv("DISCORD_TOKEN")  # Make sure you have your bot token in the .env file
API_URL = "https://api.alquran.cloud/v1/ayah/{0}/editions/quran-simple"  # Adjust based on your API

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="Q", intents=intents)  # Prefix is "Q" now for your format

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Avoid the bot responding to itself
    if message.author.bot:
        return

    # Check if the message matches the Q<surah>:<ayah> or Q<surah>:<ayah>-<ayah> format
    match = re.match(r"Q(\d+):(\d+)(?:-(\d+))?", message.content.strip())
    if match:
        surah = int(match.group(1))
        start_ayah = int(match.group(2))
        end_ayah = int(match.group(3)) if match.group(3) else start_ayah

        if end_ayah < start_ayah:
            await message.channel.send("End verse must be greater than start verse.")
            return

        # Send a message to confirm the bot is fetching the verses
        await message.channel.send(f"Fetching verses {start_ayah} to {end_ayah} from Surah {surah}...")

        # Fetch the verses from the API
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

            # Send the verses to the Discord channel
            await message.channel.send("\n".join(verses))

    # Process other commands if needed
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(TOKEN)

