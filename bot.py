import asyncio
import logging
import sys

import discord
from discord.ext import commands

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CS2Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            description="CS2 Server Control Bot"
        )

    async def setup_hook(self):
        # Load the CS2 cog
        await self.load_extension("cogs.cs2")
        logger.info("Loaded CS2 commands cog")

        # Sync commands globally
        await self.tree.sync()
        logger.info("Synced slash commands")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")


async def main():
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set in environment")
        sys.exit(1)

    if not config.CS2_RCON_PASSWORD:
        logger.error("CS2_RCON_PASSWORD not set in environment")
        sys.exit(1)

    logger.info(f"RCON target: {config.CS2_RCON_HOST}:{config.CS2_RCON_PORT}")
    logger.info(f"Required role: {config.ALLOWED_ROLE_NAME}")

    bot = CS2Bot()

    async with bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
