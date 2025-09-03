# Hackathon Tele Bot

A Telegram bot that scans popular hackathon listing platforms like Devfolio, Unstop, and Dare2Compete, extracts hackathon information using AI-powered Groq API, and sends updates to a Telegram chat.

## Features
- Periodically checks multiple hackathon platforms for new events.
- Uses Groq AI API to extract hackathon details from webpage text.
- Sends formatted hackathon updates to Telegram channels or groups.
- Deduplicates hackathons based on title and date to avoid repeats.
- Provides fallback sample hackathons in case of errors.
- Scheduled to run every 6 hours.

## Technologies Used
- Python 3
- Requests
- BeautifulSoup4
- dotenv for environment variables
- schedule for task scheduling
- Groq AI API for content extraction

## Setup & Installation
1. Clone the repository:
git clone https://github.com/ShresthSamyak/tele_bot


text

2. Install dependencies:
pip install requests
pip install beautifulsoup4
pip install python-dotenv
pip install schedule

text

3. Create a `.env` file with your credentials:
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
GROQ_API_KEY=your_groq_api_key_here

text

4. Run the bot:
python bot.py

text

## Usage
The bot will automatically fetch and send hackathon updates to the configured Telegram chat every 6 hours.

## Troubleshooting
- Ensure your tokens and API keys are correctly set in the `.env` file.
- Check network connectivity.
- Review console logs for errors.

