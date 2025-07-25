import os

import discord
import google.generativeai as genai
from discord.ext import commands

PERSONAS = {
    "history": "You are an expert history tutor for history students.",
    "ap-world": "You are an expert history tutor for AP World History students.",
    "math": "You are a patient and skilled math tutor who guides users to the answer.",
    "general": "You are a friendly and helpful AI assistant having a casual conversation. Speak as if you were gen-z, but don't overdo it (ex: too many emojis, dated slang, etc).",
    "debate-hall": "You are a debate moderator. Your role is to be neutral, introduce topics, and summarize arguments when asked.",
}
DEFAULT_PERSONA = "You are a friendly and helpful AI assistant."


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = genai.GenerativeModel("gemma-3-27b-it")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")
        print("Bot is online with thread-based debate features.")
        print("Syncing slash commands...")
        await self.bot.tree.sync()
        print("Slash commands synced successfully.")
        print("----------------------------------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if isinstance(message.channel, discord.Thread) and self.bot.user.mentioned_in(
            message
        ):
            try:
                parent_message = await message.channel.parent.fetch_message(
                    message.channel.id
                )
                if parent_message.author == self.bot.user:
                    cleaned_input_thread = (
                        message.content.replace(f"<@!{self.bot.user.id}>", "")
                        .replace(f"<@{self.bot.user.id}>", "")
                        .strip()
                        .lower()
                    )

                    if cleaned_input_thread.startswith(
                        "summarize"
                    ) or cleaned_input_thread.startswith("recap"):
                        async with message.channel.typing():
                            history = [
                                msg
                                async for msg in message.channel.history(
                                    limit=100, oldest_first=True
                                )
                            ]

                            transcript = "--- DEBATE TRANSCRIPT ---\n"
                            for msg in history:
                                if not (msg.author == self.bot.user and msg.embeds):
                                    if msg.content:
                                        transcript += f"- {msg.author.display_name}: {msg.content}\n"

                            summary_prompt = f"""
                            You are a neutral debate moderator AI. Your one and only task right now is to summarize the following debate transcript.
                            Read the transcript carefully and provide a concise, unbiased summary of the main arguments. Do not add any conversational fluff, greetings, or ask for more information. Just provide the summary.

                            {transcript}
                            --- END TRANSCRIPT ---
                            """
                            response = self.model.generate_content(summary_prompt)
                            summary_embed = discord.Embed(
                                title="Summary of the Debate",
                                description=response.text,
                                color=discord.Color.gold(),
                            )
                            await message.channel.send(embed=summary_embed)
                        return
            except discord.NotFound:
                pass
            except Exception as e:
                await message.channel.send(
                    f"An error occurred while trying to summarize: {e}"
                )
                return

        channel_name = message.channel.name.lower()
        persona_prompt = PERSONAS.get(channel_name, DEFAULT_PERSONA)

        context_prompt = ""
        user_input = message.content

        if message.reference and message.reference.message_id:
            original_message = await message.channel.fetch_message(
                message.reference.message_id
            )
            if original_message.author == self.bot.user:
                original_text = original_message.content
                if original_message.embeds:
                    original_text += "\n" + original_message.embeds[0].description
                context_prompt = f"You are in a conversation. This was your previous message:\n---\n{original_text}\n---\nNow, the user has replied."
                user_input = (
                    user_input.replace(f"<@!{self.bot.user.id}>", "")
                    .replace(f"<@{self.bot.user.id}>", "")
                    .strip()
                )

        if self.bot.user.mentioned_in(message) or context_prompt:
            async with message.channel.typing():
                cleaned_input = (
                    user_input.replace(f"<@!{self.bot.user.id}>", "")
                    .replace(f"<@{self.bot.user.id}>", "")
                    .strip()
                )

                if cleaned_input.lower().startswith("debate"):
                    topic = cleaned_input.lower().replace("debate", "", 1).strip()
                    if not topic:
                        await message.reply(
                            "Please provide a topic for the debate! Example: `@historiabot debate The effectiveness of the League of Nations`"
                        )
                        return
                    try:
                        debate_prompt = f"Generate a brief, neutral introduction and two opposing opening statements for a debate on the topic: '{topic}'."
                        response = self.model.generate_content(debate_prompt)

                        embed = discord.Embed(
                            title=f"Debate Topic: {topic.title()}",
                            description=response.text,
                            color=discord.Color.dark_gold(),
                        )
                        embed.set_footer(text="Join the thread below to participate!")

                        debate_starter_message = await message.reply(embed=embed)

                        thread_name = f"Debate: {topic[:80]}"
                        await debate_starter_message.create_thread(
                            name=thread_name, auto_archive_duration=1440
                        )
                    except Exception as e:
                        await message.reply(
                            f"Sorry, I had trouble starting the debate. Error: {e}"
                        )
                    return

                final_prompt = f'{persona_prompt}\n{context_prompt}\nThe user\'s message to you is: "{cleaned_input}"\nAnalyze their message and respond helpfully.'
                try:
                    response = self.model.generate_content(final_prompt)
                    await message.reply(response.text, mention_author=True)
                except Exception as e:
                    await message.reply(
                        f"Sorry, I encountered an error trying to respond. {e}",
                        mention_author=True,
                    )


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
