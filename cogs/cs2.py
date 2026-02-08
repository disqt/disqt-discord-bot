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

    cs_group = app_commands.Group(name="cs", description="Commandes du serveur CS2 Disqt")

    @cs_group.command(name="exec", description="Exécuter une commande console sur le serveur")
    @has_allowed_role()
    @app_commands.describe(command="Commande console (ex: sv_cheats 1, mp_restartgame 1)")
    async def cs_exec(self, interaction: discord.Interaction, command: str):
        """Exécuter une commande console sur le serveur."""
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
                await interaction.followup.send(self.bot.lang["command_executed"])

        except RCONAuthError:
            await interaction.followup.send(self.bot.lang["error_rcon_auth"])
        except RCONConnectionError as e:
            await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
        except RCONError as e:
            await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))

    @cs_group.command(name="map", description="Changer la map actuelle")
    @has_allowed_role()
    @app_commands.describe(map_name="Nom de map (de_dust2, de_mirage) ou URL Steam Workshop")
    async def cs_map(self, interaction: discord.Interaction, map_name: str):
        """Changer la map actuelle."""
        await interaction.response.defer()

        # Check if it's a workshop URL
        workshop_pattern = r"steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)"
        match = re.search(workshop_pattern, map_name)

        try:
            if match:
                workshop_id = match.group(1)
                command = f"host_workshop_map {workshop_id}"
                map_display = f"Workshop map {workshop_id}"
            else:
                # Validate map exists before changing
                maps_response = await self._rcon("maps *")
                # CS2 returns tab-separated map names without .bsp extension
                available_maps = [m.strip().lower() for m in maps_response.split() if m.strip()]

                if map_name.lower() not in available_maps:
                    await interaction.followup.send(
                        self.bot.lang["error_map_not_found"].format(map=map_name)
                    )
                    return

                command = f"changelevel {map_name}"
                map_display = map_name

            logger.info(f"User {interaction.user} changing map to: {map_display}")
            await self._rcon(command)
            await interaction.followup.send(self.bot.lang["map_changing"].format(map=map_display))
        except RCONAuthError:
            await interaction.followup.send(self.bot.lang["error_rcon_auth"])
        except RCONConnectionError as e:
            await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
        except RCONError as e:
            await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))

    @cs_group.command(name="maps", description="Lister les maps disponibles sur le serveur")
    @has_allowed_role()
    async def cs_maps(self, interaction: discord.Interaction):
        """Lister les maps disponibles sur le serveur."""
        await interaction.response.defer()

        try:
            maps_response = await self._rcon("maps *")
            all_maps = [m.strip() for m in maps_response.split() if m.strip()]

            # Filter to only playable maps (de_, cs_, ar_ prefixes)
            playable_maps = sorted([m for m in all_maps if m.startswith(('de_', 'cs_', 'ar_')) and not m.endswith('_vanity')])

            if playable_maps:
                maps_list = "\n".join(playable_maps)
                await interaction.followup.send(
                    self.bot.lang["maps_list"].format(count=len(playable_maps), maps=maps_list)
                )
            else:
                await interaction.followup.send(self.bot.lang["maps_none"])

        except RCONAuthError:
            await interaction.followup.send(self.bot.lang["error_rcon_auth"])
        except RCONConnectionError as e:
            await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
        except RCONError as e:
            await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))

    @cs_group.command(name="status", description="Afficher les infos du serveur et les joueurs connectés")
    @has_allowed_role()
    async def cs_status(self, interaction: discord.Interaction):
        """Afficher les infos du serveur et les joueurs connectés."""
        await interaction.response.defer()

        try:
            response = await self._rcon("status")

            if response:
                if len(response) > 1900:
                    response = response[:1900] + "\n... (truncated)"
                await interaction.followup.send(f"```\n{response}\n```")
            else:
                await interaction.followup.send(self.bot.lang["error_no_status"])

        except RCONAuthError:
            await interaction.followup.send(self.bot.lang["error_rcon_auth"])
        except RCONConnectionError as e:
            await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
        except RCONError as e:
            await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))

    # Bot subcommand group
    bot_group = app_commands.Group(
        name="bot",
        description="Gestion des bots IA",
        parent=cs_group
    )

    @bot_group.command(name="add", description="Ajouter des bots IA pour jouer")
    @has_allowed_role()
    @app_commands.describe(count="Nombre de bots (1-10, défaut: 1)")
    async def bot_add(self, interaction: discord.Interaction, count: Optional[int] = 1):
        """Ajouter des bots IA pour jouer."""
        await interaction.response.defer()

        count = max(1, min(count, 10))  # Clamp between 1 and 10

        logger.info(f"User {interaction.user} adding {count} bot(s)")

        try:
            for _ in range(count):
                await self._rcon("bot_add")

            await interaction.followup.send(self.bot.lang["bots_added"].format(count=count))
        except RCONAuthError:
            await interaction.followup.send(self.bot.lang["error_rcon_auth"])
        except RCONConnectionError as e:
            await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
        except RCONError as e:
            await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))

    @bot_group.command(name="kick", description="Virer tous les bots du serveur")
    @has_allowed_role()
    async def bot_kick(self, interaction: discord.Interaction):
        """Virer tous les bots du serveur."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} kicking all bots")

        try:
            await self._rcon("bot_kick")
            await interaction.followup.send(self.bot.lang["bots_kicked"])
        except RCONAuthError:
            await interaction.followup.send(self.bot.lang["error_rcon_auth"])
        except RCONConnectionError as e:
            await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
        except RCONError as e:
            await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))

    @bot_group.command(name="difficulty", description="Changer la difficulté des bots")
    @has_allowed_role()
    @app_commands.describe(level="Niveau de difficulté")
    @app_commands.choices(level=[
        app_commands.Choice(name="Facile", value=0),
        app_commands.Choice(name="Normal", value=1),
        app_commands.Choice(name="Difficile", value=2),
        app_commands.Choice(name="Expert", value=3),
    ])
    async def bot_difficulty(self, interaction: discord.Interaction, level: app_commands.Choice[int]):
        """Changer la difficulté des bots."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} setting bot difficulty to {level.name}")

        try:
            await self._rcon(f"bot_difficulty {level.value}")
            await interaction.followup.send(self.bot.lang["bots_difficulty"].format(level=level.name))
        except RCONAuthError:
            await interaction.followup.send(self.bot.lang["error_rcon_auth"])
        except RCONConnectionError as e:
            await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
        except RCONError as e:
            await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))


async def setup(bot: commands.Bot):
    await bot.add_cog(CS2Commands(bot))
