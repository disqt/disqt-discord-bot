import asyncio
import json
import logging
import re
import sys
from pathlib import Path

import discord
from discord.ext import commands, tasks

import config
from rcon import execute_rcon, RCONError

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

        # Load language file
        lang_code = getattr(config, 'LANGUAGE', 'fr')
        lang_path = Path(__file__).parent / "lang" / f"{lang_code}.json"
        with open(lang_path, encoding="utf-8") as f:
            self.lang = json.load(f)
        logger.info(f"Loaded language: {lang_code}")

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

        # Start the presence update loop
        if not self.update_presence.is_running():
            self.update_presence.start()

    @tasks.loop(seconds=30)
    async def update_presence(self):
        """Update bot presence with server status."""
        try:
            status = await execute_rcon(
                config.CS2_RCON_HOST,
                config.CS2_RCON_PORT,
                config.CS2_RCON_PASSWORD,
                "status"
            )

            # Parse map name from spawngroup (e.g., "[1: de_nuke | main lump")
            map_match = re.search(r"\[1:\s+(\S+)\s+\|", status)
            map_name = map_match.group(1) if map_match else "?"

            # Parse player count
            players_match = re.search(r"players\s+:\s+(\d+)\s+humans", status)
            humans = int(players_match.group(1)) if players_match else 0

            # Get max players from sv_visiblemaxplayers
            maxplayers_response = await execute_rcon(
                config.CS2_RCON_HOST,
                config.CS2_RCON_PORT,
                config.CS2_RCON_PASSWORD,
                "sv_visiblemaxplayers"
            )
            maxplayers_match = re.search(r"=\s*(\d+)", maxplayers_response)
            max_players = int(maxplayers_match.group(1)) if maxplayers_match else 10

            player_str = f"{humans}/{max_players}"

            # Build presence string: de_dust2 (2/10)
            presence_text = f"{map_name} ({player_str})"

            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=presence_text
                )
            )

        except RCONError as e:
            logger.warning(f"Failed to update presence: {e}")
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Hors ligne"
                )
            )
        except Exception as e:
            logger.error(f"Presence update error: {e}")

    @update_presence.before_loop
    async def before_update_presence(self):
        """Wait until bot is ready before starting presence updates."""
        await self.wait_until_ready()


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
