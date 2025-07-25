import os

import discord
import requests
from discord.ext import commands, tasks

CHANGELOG_CHANNEL_ID = os.getenv("CHANGELOG_CHANNEL_ID")
if CHANGELOG_CHANNEL_ID:
    try:
        CHANGELOG_CHANNEL_ID = int(CHANGELOG_CHANNEL_ID)
    except (ValueError, TypeError):
        print(
            "!!! WARNING: CHANGELOG_CHANNEL_ID is not a valid integer. Commit tracking will be disabled."
        )
        CHANGELOG_CHANNEL_ID = None
GITHUB_REPO = os.getenv("GITHUB_REPO")


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


class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_commit_sha = None
        if CHANGELOG_CHANNEL_ID and GITHUB_REPO:
            self.check_for_new_commits.start()

    def cog_unload(self):
        self.check_for_new_commits.cancel()

    @tasks.loop(minutes=10)
    async def check_for_new_commits(self):
        if not CHANGELOG_CHANNEL_ID or not GITHUB_REPO:
            return

        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/commits"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            commits = response.json()

            if not commits:
                return

            latest_commit_sha = commits[0]["sha"]

            if self.last_commit_sha is None:
                self.last_commit_sha = latest_commit_sha
                print(
                    f"Commit tracking initialized. Starting with commit: {latest_commit_sha[:7]}"
                )
                return

            if latest_commit_sha != self.last_commit_sha:
                new_commits = []
                for commit in commits:
                    if commit["sha"] == self.last_commit_sha:
                        break
                    new_commits.append(commit)

                if new_commits:
                    channel = self.bot.get_channel(CHANGELOG_CHANNEL_ID)
                    if channel:
                        print(
                            f"Found {len(new_commits)} new commit(s). Sending to #{channel.name}."
                        )
                        for commit_data in reversed(new_commits):
                            commit = commit_data["commit"]
                            author = commit["author"]["name"]
                            message = commit["message"]
                            sha = commit_data["sha"]
                            url = commit_data["html_url"]

                            emoji = get_commit_emoji(message)
                            title = message.splitlines()[0]

                            embed = discord.Embed(
                                title=f"{emoji} {title}",
                                url=url,
                                description=f"```\n{message}\n```\nby {author}",
                                color=discord.Color.blue(),
                            )
                            embed.set_footer(text=f"Commit: {sha[:7]}")
                            await channel.send(embed=embed)
                    else:
                        print(
                            f"!!! ERROR: Could not find changelog channel with ID {CHANGELOG_CHANNEL_ID}"
                        )

                self.last_commit_sha = latest_commit_sha

        except requests.RequestException as e:
            print(f"!!! WARNING: Could not fetch commits from GitHub: {e}")
        except Exception as e:
            print(f"!!! ERROR: An unexpected error occurred in the commit checker: {e}")

    @commands.command()
    @commands.is_owner()
    async def force_check(self, ctx: commands.Context):
        """Manually triggers the GitHub commit check."""
        await ctx.send("Manually triggering commit check...", delete_after=10)
        await self.check_for_new_commits()
        await ctx.send("Commit check complete.", delete_after=10)

    @force_check.error
    async def force_check_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("Sorry, only the bot owner can use this command.", delete_after=10)
        else:
            await ctx.send(f"An error occurred: {error}", delete_after=10)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot))
