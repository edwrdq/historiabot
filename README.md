# Discord Study Bot

This is a Discord bot that uses the Google Gemini API to act as a study bot. It can take on different personas depending on the channel it's in, and it has a basic memory system to understand conversational context. It also features several slash commands for utility and fun.

## Features

- **Dynamic Personas:** The bot's personality changes based on the channel name.
- **Slash Commands:** A growing list of commands to help with your studies and more.
- **Conversational Memory:** The bot remembers the context of the conversation when you reply to its messages.
- **Debate Moderator:** The bot can start and moderate debates in a dedicated channel.
- **GitHub Integration:** The bot can announce new commits to a changelog channel.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.x
- A Discord account and a bot token. You can find instructions on how to get a bot token [here](https://discordpy.readthedocs.io/en/stable/discord.html).
- A Google Gemini API key. You can get one [here](https://makersuite.google.com/).

### Installation (Local)

1.  Clone the repo
    ```sh
    git clone https://github.com/edwrdq/historiabot
    ```
2.  Create and activate a virtual environment
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install Python packages
    ```sh
    pip install -r requirements.txt
    ```
    

## Configuration

1.  Create a `.env` file in the root of the project.
2.  Add your Discord bot token and Gemini API key to the `.env` file like this:

    ```
    DISCORD_BOT_TOKEN=your_discord_bot_token
    GEMMA_API_KEY=your_gemma_api_key
    ```
3.  (Optional) To enable the GitHub commit tracking feature, add the following to your `.env` file:
    ```
    CHANGELOG_CHANNEL_ID=your_discord_channel_id
    GITHUB_REPO=your_github_username/your_repo_name
    ```

## Usage

### Personas

The bot's persona is determined by the name of the channel it is in. The available personas are:

-   `history`: A history tutor
-   `ap-world`: An AP World History tutor
-   `math`: A math tutor
-   `general`: A general-purpose AI assistant
-   `debate-hall`: A neutral debate moderator.

To interact with the bot, you can either @mention it or reply to one of its messages.

### Slash Commands

-   `/ask <question>`: Get a quick one to two sentence answer to your question.
-   `/outline <prompt>`: Generate a structured essay outline for a given prompt.
-   `/pomodoro [study_minutes] [break_minutes]`: Start a Pomodoro study timer.
-   `/flight`: Shows a picture of Flight.

### Debate

To start a debate, go to the `debate-hall` channel and type `@historiabot debate <topic>`. The bot will create a thread for the debate and provide opening statements. To get a summary of the debate, type `@historiabot summarize` in the debate thread.

## Running the Bot

To run the bot, execute the following command:

```sh
python study_bot.py
```

## Docker

You can run the bot in a containerized environment using Docker.

### Quick Start with Docker Compose

1. Create a `.env` file in the project root with at least:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token
   GEMMA_API_KEY=your_gemma_api_key
   # Optional features
   # CHANGELOG_CHANNEL_ID=123456789012345678
   # GITHUB_REPO=your_github_username/your_repo
   ```
2. Build and start the container in the background:
   ```sh
   docker compose up -d --build
   ```
3. View logs:
   ```sh
   docker compose logs -f
   ```

### Docker CLI (without Compose)

Build the image:
```sh
docker build -t historiabot .
```

Run the container with your `.env` values:
```sh
docker run \
  --name historiabot \
  --env-file .env \
  --restart unless-stopped \
  historiabot
```

### Notes

- The bot requires the Message Content Intent enabled in your Discord application settings since it responds to messages and mentions.
- The project’s `.env` file is not copied into the container image, but it is used at runtime via Compose’s `env_file` or the `--env-file` flag.
- For development convenience, you can live-edit code by uncommenting the `volumes` section in `docker-compose.yml`.
