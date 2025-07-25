import asyncio

import discord
import google.generativeai as genai
from discord import app_commands
from discord.ext import commands


class Study(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model = genai.GenerativeModel("gemma-3-27b-it")

    @app_commands.command(
        name="ask",
        description="Get a quick one to two sentence answer to your question.",
    )
    @app_commands.describe(question="The question you want to ask.")
    async def ask_command(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer(thinking=True)
        try:
            quick_answer_prompt = f"You are a helpful AI assistant. Provide a one to two sentence answer to the following question: '{question}'"
            response = self.model.generate_content(quick_answer_prompt)
            await interaction.followup.send(response.text)
        except Exception as e:
            await interaction.followup.send(
                f"Sorry, I couldn't answer that question right now. Error: {e}"
            )

    @app_commands.command(
        name="outline",
        description="Generate a structured essay outline for a given prompt.",
    )
    @app_commands.describe(prompt="The essay prompt you want an outline for.")
    async def outline_command(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(thinking=True)
        try:
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

keep it under 4000 characters.

The user's essay prompt is: '{prompt}'
"""
            response = self.model.generate_content(outline_prompt)
            response_text = response.text

            char_limit = 4096

            embed = discord.Embed(
                title=f'Essay Outline: "{prompt[:200]}"', color=discord.Color.purple()
            )
            embed.set_footer(
                text="Use this outline as a guide to structure your writing."
            )

            if len(response_text) <= char_limit:
                embed.description = response_text
                await interaction.followup.send(embed=embed)
            else:
                embed.description = "The generated outline is too long for a single message. Here it is in parts:"
                await interaction.followup.send(embed=embed)

                for i in range(0, len(response_text), char_limit):
                    chunk = response_text[i : i + char_limit]
                    await interaction.channel.send(chunk)

        except Exception as e:
            await interaction.followup.send(
                f"Sorry, I had trouble generating that outline. Error: {e}"
            )

    @app_commands.command(name="pomodoro", description="Start a Pomodoro study timer.")
    @app_commands.describe(
        study_minutes="How long you want to study for (default: 25).",
        break_minutes="How long of a break you want (default: 5).",
    )
    async def pomodoro_command(
        self,
        interaction: discord.Interaction,
        study_minutes: int = 25,
        break_minutes: int = 5,
    ):
        await interaction.response.send_message(
            f"🍅 **Pomodoro Timer Started!**\n\nTime to focus, {interaction.user.mention}! Your **{study_minutes}-minute** study session has begun. I'll let you know when it's time for a break."
        )

        study_seconds = study_minutes * 60
        break_seconds = break_minutes * 60

        await asyncio.sleep(study_seconds)

        await interaction.channel.send(
            f"🎉 **Break Time, {interaction.user.mention}!**\n\nGreat work! Your **{break_minutes}-minute** break starts now. Relax and recharge!"
        )

        await asyncio.sleep(break_seconds)

        await interaction.channel.send(
            f"💪 **Break's Over, {interaction.user.mention}!**\n\nTime to get back to it. You can start another session with `/pomodoro`."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Study(bot))
