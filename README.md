# Telegram Bot

## Environment Variables

Before running the bot, configure the following environment variables:

- `BOT_TOKEN` – Telegram bot token from [BotFather](https://t.me/botfather).  
- `API_URL` – URL of the backend (FastAPI service). Example: `http://backend:8000`.  
- `API_KEY` – Secret token (`SECRET_TOKEN`) that must match the backend.  
- `ADMIN_CHAT_ID` – Telegram chat ID of the admin. The bot will send notifications about new forms to this chat.  
- `REDIS_URL` – Redis connection URL, e.g.: `redis://user:password@localhost:6379/0`.  

## Run without Docker

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables (example for Linux/macOS):
   ```bash
   export BOT_TOKEN="your_bot_token"
   export API_URL="http://localhost:8000"
   export API_KEY="your_secret_token"
   export ADMIN_CHAT_ID="123456789"
   export REDIS_URL="redis://localhost:6379/0"
   ```

3. Start the bot:
   ```bash
   python bot.py
   ```

## Run with Docker

1. Build the image:
   ```bash
   docker build -t telegram-bot .
   ```

2. Run the container:
   ```bash
   docker run -d \
     -e BOT_TOKEN=your_bot_token \
     -e API_URL=http://backend:8000 \
     -e API_KEY=your_secret_token \
     -e ADMIN_CHAT_ID=123456789 \
     -e REDIS_URL=redis://localhost:6379/0 \
     telegram-bot
    ```