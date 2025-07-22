# Discord Study Bot

This is a Discord bot that uses the Google Gemini API to act as a study bot. It can take on different personas depending on the channel it's in, and it has a basic memory system to understand conversational context.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.x
- A Discord account and a bot token. You can find instructions on how to get a bot token [here](https://discordpy.readthedocs.io/en/stable/discord.html).
- A Google Gemini API key. You can get one [here](https://makersuite.google.com/).

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/your_username_/your_project_name.git
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

## Usage

The bot's persona is determined by the name of the channel it is in. The available personas are:

-   `history`: A history tutor
-   `ap-world`: An AP World History tutor
-   `math`: A math tutor
-   `general`: A general-purpose AI assistant

To interact with the bot, you can either @mention it or reply to one of its messages.

## Running the Bot

To run the bot, execute the following command:

```sh
python study_bot.py
```
