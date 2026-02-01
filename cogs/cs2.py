import re
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import config
from rcon import execute_rcon, RCONError, RCONAuthError, RCONConnectionError

logger = logging.getLogger(__name__)


def has_allowed_role():
    """Check if user has the allowed role."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False

        member = interaction.user
        if isinstance(member, discord.Member):
            for role in member.roles:
                if role.name == config.ALLOWED_ROLE_NAME:
                    return True

        await interaction.response.send_message(
            f"You need the **{config.ALLOWED_ROLE_NAME}** role to use this command.",
            ephemeral=True
        )
        return False

    return app_commands.check(predicate)


class CS2Commands(commands.Cog):
    """CS2 server control commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _rcon(self, command: str) -> str:
        """Execute RCON command and return response."""
        return await execute_rcon(
            config.CS2_RCON_HOST,
            config.CS2_RCON_PORT,
            config.CS2_RCON_PASSWORD,
            command
        )

    cs_group = app_commands.Group(name="cs", description="CS2 server commands")

    @cs_group.command(name="exec")
    @has_allowed_role()
    @app_commands.describe(command="The RCON command to execute")
    async def cs_exec(self, interaction: discord.Interaction, command: str):
        """Execute a raw RCON command on the CS2 server."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} executing: {command}")

        try:
            response = await self._rcon(command)

            if response:
                # Truncate long responses
                if len(response) > 1900:
                    response = response[:1900] + "\n... (truncated)"
                await interaction.followup.send(f"```\n{response}\n```")
            else:
                await interaction.followup.send("Command executed (no response).")

        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="map")
    @has_allowed_role()
    @app_commands.describe(map_name="Map name or Steam Workshop URL")
    async def cs_map(self, interaction: discord.Interaction, map_name: str):
        """Change the current map. Supports map names and Workshop URLs."""
        await interaction.response.defer()

        # Check if it's a workshop URL
        workshop_pattern = r"steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)"
        match = re.search(workshop_pattern, map_name)

        if match:
            workshop_id = match.group(1)
            command = f"host_workshop_map {workshop_id}"
            map_display = f"Workshop map {workshop_id}"
        else:
            command = f"changelevel {map_name}"
            map_display = map_name

        logger.info(f"User {interaction.user} changing map to: {map_display}")

        try:
            await self._rcon(command)
            await interaction.followup.send(f"Changing map to **{map_display}**...")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="1v1")
    @has_allowed_role()
    async def cs_1v1(self, interaction: discord.Interaction):
        """Switch to 1v1 mode configuration."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} switching to 1v1 mode")

        try:
            await self._rcon("exec 1v1")
            await interaction.followup.send("Executed **1v1** config.")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="status")
    @has_allowed_role()
    async def cs_status(self, interaction: discord.Interaction):
        """Show CS2 server status."""
        await interaction.response.defer()

        try:
            response = await self._rcon("status")

            if response:
                if len(response) > 1900:
                    response = response[:1900] + "\n... (truncated)"
                await interaction.followup.send(f"```\n{response}\n```")
            else:
                await interaction.followup.send("No status response received.")

        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    # Bot subcommand group
    bot_group = app_commands.Group(
        name="bot",
        description="Bot management commands",
        parent=cs_group
    )

    @bot_group.command(name="add")
    @has_allowed_role()
    @app_commands.describe(count="Number of bots to add (default: 1)")
    async def bot_add(self, interaction: discord.Interaction, count: Optional[int] = 1):
        """Add bots to the server."""
        await interaction.response.defer()

        count = max(1, min(count, 10))  # Clamp between 1 and 10

        logger.info(f"User {interaction.user} adding {count} bot(s)")

        try:
            for _ in range(count):
                await self._rcon("bot_add")

            await interaction.followup.send(f"Added **{count}** bot(s).")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @bot_group.command(name="kick")
    @has_allowed_role()
    async def bot_kick(self, interaction: discord.Interaction):
        """Kick all bots from the server."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} kicking all bots")

        try:
            await self._rcon("bot_kick")
            await interaction.followup.send("Kicked all bots.")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(CS2Commands(bot))
