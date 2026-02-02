import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CS2_RCON_HOST = os.getenv("CS2_RCON_HOST", "127.0.0.1")
CS2_RCON_PORT = int(os.getenv("CS2_RCON_PORT", "27015"))
CS2_RCON_PASSWORD = os.getenv("CS2_RCON_PASSWORD")
ALLOWED_ROLE_NAME = os.getenv("ALLOWED_ROLE_NAME", "Membres")
LANGUAGE = os.getenv("LANGUAGE", "fr")
