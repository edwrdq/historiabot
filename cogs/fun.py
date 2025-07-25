import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="flight", description="Shows a picture of Flight.")
    async def flight_command(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1397346577458270409/1397458909274439711/images.png?ex=6881cc87&is=68807b07&hm=9c151c18d093f262f0358c56c113ab81fda99ddfbae77f17afa4f146b6d7cb34&"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pretzel", description="Shows a picture of a pretzel.")
    async def pretzel_command(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/198658294007463936/1398373974936780932/image0.jpg?ex=688520c0&is=6883cf40&hm=6161d6435609ada648d7a417b51f3bc4d7504753df12bfed8b0ad4a9344d9c82&"
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
