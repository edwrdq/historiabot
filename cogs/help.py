import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows a list of all available commands.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Historiabot Help",
            description="Here is a list of all my commands:",
            color=discord.Color.blurple()
        )

        # Get all application commands from the tree
        commands_list = self.bot.tree.get_commands()

        for command in commands_list:
            # Don't list the help command itself
            if command.name == "help":
                continue
            embed.add_field(name=f"/{command.name}", value=command.description, inline=False)
        
        embed.set_footer(text="Use a command to get started!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.bot):
    await bot.add_cog(Help(bot))
