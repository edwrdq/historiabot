import asyncio
import os

import discord
import google.generativeai as genai
from discord.ext import commands
from dotenv import load_dotenv

# --- Configuration & Setup ---
print("Script started. Loading environment variables...")
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")

if not DISCORD_BOT_TOKEN or not GEMMA_API_KEY:
    print("!!! FATAL ERROR: Missing DISCORD_BOT_TOKEN or GEMMA_API_KEY in .env file.")
    exit()
print("... Environment variables loaded successfully.")

try:
    print("Configuring Google AI...")
    genai.configure(api_key=GEMMA_API_KEY)
    print("... Google AI configured successfully.")
except Exception as e:
    print(f"!!! FATAL ERROR: Could not configure Google AI. Error: {e}")
    exit()

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# --- Main Bot Execution ---
async def main():
    """Loads cogs and runs the bot."""
    print("Loading cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"  -> Loaded '{filename}'")
            except Exception as e:
                print(f"!!! ERROR: Failed to load cog '{filename}'.")
                print(f"     {e}")
    print("... Cogs loaded successfully.")

    print("\nAll setup complete. Attempting to connect to Discord...")
    await bot.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except discord.errors.LoginFailure:
        print(
            "!!! FATAL ERROR: Improper token has been passed. Check your DISCORD_BOT_TOKEN in the .env file."
        )
    except Exception as e:
        print(f"!!! FATAL ERROR: An unexpected error occurred: {e}")
