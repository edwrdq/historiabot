import discord
import google.generativeai as genai
import os
from discord.ext import tasks
from dotenv import load_dotenv
from discord import app_commands # Import app_commands for slash commands
import requests

# --- Configuration & Setup ---
print("Script started. Loading environment variables...")
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GEMMA_API_KEY = os.getenv('GEMMA_API_KEY')
CHANGELOG_CHANNEL_ID = os.getenv('CHANGELOG_CHANNEL_ID')
GITHUB_REPO = os.getenv('GITHUB_REPO')

if not DISCORD_BOT_TOKEN or not GEMMA_API_KEY:
    print("!!! FATAL ERROR: Missing DISCORD_BOT_TOKEN or GEMMA_API_KEY in .env file.")
    exit()
if not CHANGELOG_CHANNEL_ID or not GITHUB_REPO:
    print("!!! WARNING: Missing CHANGELOG_CHANNEL_ID or GITHUB_REPO in .env file. Commit tracking will be disabled.")
else:
    try:
        CHANGELOG_CHANNEL_ID = int(CHANGELOG_CHANNEL_ID)
    except ValueError:
        print("!!! FATAL ERROR: CHANGELOG_CHANNEL_ID in .env file is not a valid integer.")
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
tree = app_commands.CommandTree(bot) # Initialize the CommandTree

# --- GitHub Commit Tracking ---
LAST_COMMIT_SHA = None

def get_commit_emoji(commit_message):
    """Returns an emoji based on the commit type."""
    if commit_message.startswith("feat"):
        return "✨"
    elif commit_message.startswith("fix"):
        return "🐛"
    elif commit_message.startswith("docs"):
        return "📚"
    elif commit_message.startswith("style"):
        return "💎"
    elif commit_message.startswith("refactor"):
        return "🔨"
    elif commit_message.startswith("perf"):
        return "🚀"
    elif commit_message.startswith("test"):
        return "🚨"
    elif commit_message.startswith("chore"):
        return "🔧"
    else:
        return "📝"

@tasks.loop(minutes=10)
async def check_for_new_commits():
    global LAST_COMMIT_SHA
    if not CHANGELOG_CHANNEL_ID or not GITHUB_REPO:
        return # Don't run if the feature is not configured

    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/commits"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        commits = response.json()

        if not commits:
            return

        latest_commit_sha = commits[0]['sha']

        if LAST_COMMIT_SHA is None:
            LAST_COMMIT_SHA = latest_commit_sha
            print(f"Commit tracking initialized. Starting with commit: {latest_commit_sha[:7]}")
            return

        if latest_commit_sha != LAST_COMMIT_SHA:
            new_commits = []
            for commit in commits:
                if commit['sha'] == LAST_COMMIT_SHA:
                    break
                new_commits.append(commit)

            if new_commits:
                channel = bot.get_channel(CHANGELOG_CHANNEL_ID)
                if channel:
                    print(f"Found {len(new_commits)} new commit(s). Sending to #{channel.name}.")
                    for commit_data in reversed(new_commits):
                        commit = commit_data['commit']
                        author = commit['author']['name']
                        message = commit['message']
                        sha = commit_data['sha']
                        url = commit_data['html_url']
                        
                        emoji = get_commit_emoji(message)
                        title = message.splitlines()[0]

                        embed = discord.Embed(
                            title=f"{emoji} {title}",
                            url=url,
                            description=f"```\n{message}\n```\nby {author}",
                            color=discord.Color.blue()
                        )
                        embed.set_footer(text=f"Commit: {sha[:7]}")
                        await channel.send(embed=embed)
                else:
                    print(f"!!! ERROR: Could not find changelog channel with ID {CHANGELOG_CHANNEL_ID}")


            LAST_COMMIT_SHA = latest_commit_sha

    except requests.RequestException as e:
        print(f"!!! WARNING: Could not fetch commits from GitHub: {e}")
    except Exception as e:
        print(f"!!! ERROR: An unexpected error occurred in the commit checker: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is online with thread-based debate features.')
    print('Syncing slash commands...')
    await tree.sync() # Sync slash commands when the bot is ready
    print('Slash commands synced successfully.')
    if CHANGELOG_CHANNEL_ID and GITHUB_REPO:
        print("Starting commit tracking loop...")
        check_for_new_commits.start()
    print('----------------------------------------------------')

# --- NEW: /ask Slash Command ---
@tree.command(name="ask", description="Get a quick one to two sentence answer to your question.")
@app_commands.describe(question="The question you want to ask.")
async def ask_command(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True) # Acknowledge the command quickly
    try:
        # Prompt for a concise, 1-2 sentence answer
        quick_answer_prompt = f"You are a helpful AI assistant. Provide a one to two sentence answer to the following question: '{question}'"
        response = model.generate_content(quick_answer_prompt)
        await interaction.followup.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"Sorry, I couldn't answer that question right now. Error: {e}")

# --- NEW: /outline Slash Command ---
@tree.command(name="outline", description="Generate a structured essay outline for a given prompt.")
@app_commands.describe(prompt="The essay prompt you want an outline for.")
async def outline_command(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    try:
        # A detailed prompt to guide the AI in creating a high-quality outline
        outline_prompt = f"""
You are an expert academic writing assistant. Your task is to generate a clear, structured, and helpful essay outline based on the user's prompt.

The outline must include the following components:
1.  **Thesis Statement:** A strong, arguable thesis statement that directly answers the prompt.
2.  **Introduction:** A brief suggestion for a hook to grab the reader's attention.
3.  **Body Paragraphs (3-4):**
    *   A clear topic sentence for each paragraph.
    *   Bulleted points suggesting specific evidence, examples, or arguments to include.
4.  **Conclusion:** A suggestion for how to summarize the main points and restate the thesis.

Do not write the full essay. Focus on providing a logical structure and actionable points.

The user's essay prompt is: '{prompt}'
"""
        response = model.generate_content(outline_prompt)
        response_text = response.text
        
        # Discord's character limit for embeds is 4096
        char_limit = 4096
        
        embed = discord.Embed(
            title=f"Essay Outline: \"{prompt[:200]}\"", # Truncate prompt for title
            color=discord.Color.purple()
        )
        embed.set_footer(text="Use this outline as a guide to structure your writing.")

        # If the text is within the limit, send it in one go.
        if len(response_text) <= char_limit:
            embed.description = response_text
            await interaction.followup.send(embed=embed)
        else:
            # If the text is too long, split it and send in multiple messages.
            embed.description = "The generated outline is too long for a single message. Here it is in parts:"
            await interaction.followup.send(embed=embed)
            
            # Split the text into chunks
            for i in range(0, len(response_text), char_limit):
                chunk = response_text[i:i + char_limit]
                await interaction.channel.send(chunk)

    except Exception as e:
        await interaction.followup.send(f"Sorry, I had trouble generating that outline. Error: {e}")


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
