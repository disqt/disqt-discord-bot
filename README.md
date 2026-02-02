# Disqt CS2 Discord Bot

A Discord bot for controlling a CS2 dedicated server via RCON.

## Features

- `/cs exec <command>` - Execute arbitrary RCON commands
- `/cs map <name_or_workshop_url>` - Change maps (supports Workshop URLs)
- `/cs 1v1` - Execute 1v1 config
- `/cs bot add [count]` - Add bots (1-10)
- `/cs bot kick` - Kick all bots
- `/cs status` - Show server status

## Setup

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Enable "Message Content Intent" under Privileged Gateway Intents
6. Go to OAuth2 > URL Generator:
   - Select `bot` and `applications.commands` scopes
   - Select `Send Messages` permission
7. Use the generated URL to invite the bot to your server

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Edit `.env`:
```
DISCORD_TOKEN=your_discord_bot_token_here
CS2_RCON_HOST=195.201.114.132
CS2_RCON_PORT=27015
CS2_RCON_PASSWORD=your_rcon_password_here
ALLOWED_ROLE_NAME=Membres
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python bot.py
```

## Deployment (Systemd)

Create `/etc/systemd/system/disqt-bot.service`:

```ini
[Unit]
Description=Disqt Discord Bot
After=network.target

[Service]
Type=simple
User=cs
WorkingDirectory=/home/cs/disqt-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable disqt-bot
sudo systemctl start disqt-bot
```

## Security

- Only users with the configured role (default: "Membres") can use commands
- RCON password is stored in environment variables, never committed
- All command executions are logged
