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

    @cs_group.command(name="exec", description="Executer une commande console sur le serveur")
    @has_allowed_role()
    @app_commands.describe(command="Commande console (ex: sv_cheats 1, mp_restartgame 1)")
    async def cs_exec(self, interaction: discord.Interaction, command: str):
        """Executer une commande console sur le serveur."""
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

    @cs_group.command(name="map", description="Changer la map actuelle")
    @has_allowed_role()
    @app_commands.describe(map_name="Nom de map (de_dust2, de_mirage) ou URL Steam Workshop")
    async def cs_map(self, interaction: discord.Interaction, map_name: str):
        """Changer la map actuelle."""
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
            await interaction.followup.send(f"Changement de map vers **{map_display}**...")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="1v1", description="Charger la config 1v1 (warmup, overtime, etc.)")
    @has_allowed_role()
    async def cs_1v1(self, interaction: discord.Interaction):
        """Charger la config 1v1."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} switching to 1v1 mode")

        try:
            await self._rcon("exec 1v1")
            await interaction.followup.send("Config **1v1** chargée.")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="wingman", description="Passer en mode Wingman (2v2)")
    @has_allowed_role()
    async def cs_wingman(self, interaction: discord.Interaction):
        """Passer en mode Wingman."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} switching to wingman mode")

        try:
            await self._rcon("game_type 0; game_mode 2; mp_restartgame 1")
            await interaction.followup.send("Mode **Wingman** activé.")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="competitive", description="Passer en mode Compétitif (5v5)")
    @has_allowed_role()
    async def cs_competitive(self, interaction: discord.Interaction):
        """Passer en mode Competitive."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} switching to competitive mode")

        try:
            await self._rcon("game_type 0; game_mode 1; mp_restartgame 1")
            await interaction.followup.send("Mode **Compétitif** active.")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="ffa", description="Passer en mode FFA Deathmatch (chacun pour soi)")
    @has_allowed_role()
    async def cs_ffa(self, interaction: discord.Interaction):
        """Passer en mode FFA Deathmatch."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} switching to FFA mode")

        try:
            await self._rcon("game_type 1; game_mode 2; mp_teammates_are_enemies 1; mp_restartgame 1")
            await interaction.followup.send("Mode **FFA Deathmatch** activé.")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="sandbox", description="Mode entraînement sandbox (temps infini, trajectoires)")
    @has_allowed_role()
    async def cs_sandbox(self, interaction: discord.Interaction):
        """Mode entrainement grenades."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} switching to sandbox mode")

        # Practice mode settings
        commands = [
            "sv_cheats 1",
            "bot_kick",
            "mp_limitteams 0",
            "mp_autoteambalance 0",
            "mp_roundtime 60",
            "mp_roundtime_defuse 60",
            "mp_freezetime 0",
            "mp_warmup_end",
            "sv_infinite_ammo 1",
            "ammo_grenade_limit_total 5",
            "sv_grenade_trajectory 1",
            "sv_grenade_trajectory_time 10",
            "sv_grenade_trajectory_prac_pipreview 1",
            "mp_buytime 9999",
            "mp_buy_anywhere 1",
            "mp_maxmoney 60000",
            "mp_startmoney 60000",
            "mp_restartgame 1",
        ]

        try:
            await self._rcon("; ".join(commands))
            await interaction.followup.send(
                "Mode **Sandbox** activé.\n"
                "- Temps infini\n"
                "- Grenades illimitées\n"
                "- Trajectoires visibles\n"
                "- Preview d'impact active"
            )
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

    @cs_group.command(name="status", description="Afficher les infos du serveur et les joueurs connectés")
    @has_allowed_role()
    async def cs_status(self, interaction: discord.Interaction):
        """Afficher les infos du serveur et les joueurs connectes."""
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
        description="Gestion des bots IA",
        parent=cs_group
    )

    @bot_group.command(name="add", description="Ajouter des bots IA pour jouer")
    @has_allowed_role()
    @app_commands.describe(count="Nombre de bots (1-10, defaut: 1)")
    async def bot_add(self, interaction: discord.Interaction, count: Optional[int] = 1):
        """Ajouter des bots IA pour jouer."""
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

    @bot_group.command(name="kick", description="Virer tous les bots du serveur")
    @has_allowed_role()
    async def bot_kick(self, interaction: discord.Interaction):
        """Virer tous les bots du serveur."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} kicking all bots")

        try:
            await self._rcon("bot_kick")
            await interaction.followup.send("Tous les bots ont ete vires.")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")

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
        """Changer la difficulte des bots."""
        await interaction.response.defer()

        logger.info(f"User {interaction.user} setting bot difficulty to {level.name}")

        try:
            await self._rcon(f"bot_difficulty {level.value}")
            await interaction.followup.send(f"Difficulté des bots: **{level.name}**")
        except RCONAuthError:
            await interaction.followup.send("RCON authentication failed.")
        except RCONConnectionError as e:
            await interaction.followup.send(f"Connection error: {e}")
        except RCONError as e:
            await interaction.followup.send(f"RCON error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(CS2Commands(bot))
