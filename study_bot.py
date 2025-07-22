import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Configuration & Setup (same as before) ---
print("Script started. Loading environment variables...")
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GEMMA_API_KEY = os.getenv('GEMMA_API_KEY')

if not DISCORD_BOT_TOKEN or not GEMMA_API_KEY:
    print("!!! FATAL ERROR: Missing DISCORD_BOT_TOKEN or GEMMA_API_KEY in .env file.")
    exit()
print("... Environment variables loaded successfully.")

try:
    print("Configuring Google AI...")
    genai.configure(api_key=GEMMA_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("... Google AI configured successfully.")
except Exception as e:
    print(f"!!! FATAL ERROR: Could not configure Google AI. Error: {e}")
    exit()

PERSONAS = {
    "history": "You are an expert history tutor for history students.",
    "ap-world": "You are an expert history tutor for AP World History students.",
    "math": "You are a patient and skilled math tutor who guides users to the answer.",
    "general": "You are a friendly and helpful AI assistant having a casual conversation. Speak as if you were gen-z"
}
DEFAULT_PERSONA = "You are a friendly and helpful AI assistant."

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is online with true conversational memory.')
    print('----------------------------------------------------')

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    # Determine the bot's persona for this message
    channel_name = message.channel.name.lower()
    persona_prompt = PERSONAS.get(channel_name, DEFAULT_PERSONA)
    
    context_prompt = ""
    user_input = message.content

    # --- THE "MEMORY" SYSTEM: Handling All Replies ---
    # This is the new, powerful part. It works for ANY reply to the bot.
    if message.reference and message.reference.message_id:
        original_message = await message.channel.fetch_message(message.reference.message_id)

        # We only care if the user is replying to us.
        if original_message.author == bot.user:
            # The original message content (text or embed description) becomes our context.
            original_text = original_message.content
            if original_message.embeds:
                original_text += "\n" + original_message.embeds[0].description

            context_prompt = f"""
            You are in a conversation. This was your previous message:
            ---
            {original_text}
            ---
            Now, the user has replied.
            """
            # We don't need the @mention in the reply content
            user_input = user_input.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()

    # --- TRIGGER: We only act if the bot is mentioned OR if it's a direct reply. ---
    if bot.user.mentioned_in(message) or (context_prompt != ""):
        # Show that the bot is thinking
        async with message.channel.typing():
            # Clean the input again just in case it was a mention and not a reply
            cleaned_input = user_input.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()

            # Construct the final prompt for the AI
            final_prompt = f"""
            {persona_prompt}
            {context_prompt}
            The user's message to you is: "{cleaned_input}"

            Analyze their message and respond helpfully. If they are providing answers to a quiz you gave, grade them. If they are asking a follow-up question, answer it.
            """
            
            try:
                response = model.generate_content(final_prompt)
                await message.reply(response.text, mention_author=True)
            except Exception as e:
                await message.reply(f"Sorry, I encountered an error trying to respond. {e}", mention_author=True)

# --- Running the Bot ---
print("All setup complete. Attempting to connect to Discord...")
bot.run(DISCORD_BOT_TOKEN)