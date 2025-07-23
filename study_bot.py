import discord
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Configuration & Setup ---
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
    model = genai.GenerativeModel('gemma-3-27b-it')
    print("... Google AI configured successfully.")
except Exception as e:
    print(f"!!! FATAL ERROR: Could not configure Google AI. Error: {e}")
    exit()

PERSONAS = {
    "history": "You are an expert history tutor for history students.",
    "ap-world": "You are an expert history tutor for AP World History students.",
    "math": "You are a patient and skilled math tutor who guides users to the answer.",
    "general": "You are a friendly and helpful AI assistant having a casual conversation. Speak as if you were gen-z.",
    "debate-hall": "You are a debate moderator. Your role is to be neutral, introduce topics, and summarize arguments when asked."
}
DEFAULT_PERSONA = "You are a friendly and helpful AI assistant."

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is online with thread-based debate features.')
    print('----------------------------------------------------')

@bot.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # --- NEW, REORDERED LOGIC ---

    # 1. First, check for commands inside a thread where the bot is mentioned.
    if isinstance(message.channel, discord.Thread) and bot.user.mentioned_in(message):
        try:
            # Fetch the thread's parent message to see if the bot started it.
            # This is a robust way to confirm it's a "debate thread".
            parent_message = await message.channel.parent.fetch_message(message.channel.id)
            if parent_message.author == bot.user:
                cleaned_input_thread = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip().lower()
                
                # Keyword to trigger summarization
                if cleaned_input_thread.startswith("summarize") or cleaned_input_thread.startswith("recap"):
                    async with message.channel.typing():
                        # Fetch the message history of the thread
                        history = [msg async for msg in message.channel.history(limit=100, oldest_first=True)]
                        
                        transcript = "--- DEBATE TRANSCRIPT ---\n"
                        for msg in history:
                            # Clean up the transcript: exclude the bot's own starting embed and empty messages
                            if not (msg.author == bot.user and msg.embeds):
                                if msg.content:
                                    transcript += f"- {msg.author.display_name}: {msg.content}\n"
                        
                        # A highly specific, direct prompt for the summarization task
                        summary_prompt = f"""
                        You are a neutral debate moderator AI. Your one and only task right now is to summarize the following debate transcript.
                        Read the transcript carefully and provide a concise, unbiased summary of the main arguments. Do not add any conversational fluff, greetings, or ask for more information. Just provide the summary.

                        {transcript}
                        --- END TRANSCRIPT ---
                        """
                        response = model.generate_content(summary_prompt)
                        summary_embed = discord.Embed(
                            title="Summary of the Debate",
                            description=response.text,
                            color=discord.Color.gold()
                        )
                        await message.channel.send(embed=summary_embed)
                    return # CRITICAL: Stop all further processing to avoid a double reply.
        except discord.NotFound:
            # This can happen if the original starter message was deleted. We can safely ignore it.
            pass
        except Exception as e:
            await message.channel.send(f"An error occurred while trying to summarize: {e}")
            return # Stop processing on error too.

    # 2. If it's not a thread command, proceed with the normal conversational logic.
    
    # Determine the bot's persona for this message
    channel_name = message.channel.name.lower()
    persona_prompt = PERSONAS.get(channel_name, DEFAULT_PERSONA)
    
    context_prompt = ""
    user_input = message.content

    # Reply Memory System
    if message.reference and message.reference.message_id:
        original_message = await message.channel.fetch_message(message.reference.message_id)
        if original_message.author == bot.user:
            original_text = original_message.content
            if original_message.embeds:
                original_text += "\n" + original_message.embeds[0].description
            context_prompt = f"You are in a conversation. This was your previous message:\n---\n{original_text}\n---\nNow, the user has replied."
            user_input = user_input.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()

    # Main Trigger: Mention or Reply
    if bot.user.mentioned_in(message) or context_prompt:
        async with message.channel.typing():
            cleaned_input = user_input.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
            
            # Debate Command Logic
            if cleaned_input.lower().startswith("debate"):
                # Use replace with a count of 1 to only remove the first instance
                topic = cleaned_input.lower().replace("debate", "", 1).strip()
                if not topic:
                    await message.reply("Please provide a topic for the debate! Example: `@historiabot debate The effectiveness of the League of Nations`")
                    return
                try:
                    debate_prompt = f"Generate a brief, neutral introduction and two opposing opening statements for a debate on the topic: '{topic}'."
                    response = model.generate_content(debate_prompt)
                    
                    embed = discord.Embed(
                        title=f"Debate Topic: {topic.title()}",
                        description=response.text,
                        color=discord.Color.dark_gold()
                    )
                    embed.set_footer(text="Join the thread below to participate!")
                    
                    debate_starter_message = await message.reply(embed=embed)
                    
                    # Create the thread on that message
                    thread_name = f"Debate: {topic[:80]}" # Trim topic to fit Discord's name limit
                    await debate_starter_message.create_thread(
                        name=thread_name,
                        auto_archive_duration=1440  # Keep thread active for 24 hours of inactivity
                    )
                except Exception as e:
                    await message.reply(f"Sorry, I had trouble starting the debate. Error: {e}")
                return # Stop processing after creating the debate.

            # General Conversation Logic
            final_prompt = f"{persona_prompt}\n{context_prompt}\nThe user's message to you is: \"{cleaned_input}\"\nAnalyze their message and respond helpfully."
            try:
                response = model.generate_content(final_prompt)
                await message.reply(response.text, mention_author=True)
            except Exception as e:
                await message.reply(f"Sorry, I encountered an error trying to respond. {e}", mention_author=True)

# --- Running the Bot ---
print("All setup complete. Attempting to connect to Discord...")
bot.run(DISCORD_BOT_TOKEN)