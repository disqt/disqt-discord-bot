# Disqt Discord Bot + DisqtModes CS2 Plugin

This repository contains two components:

1. **Discord Bot** (Python) -- Slash-command interface for controlling a CS2 dedicated server via RCON
2. **DisqtModes** (C# / CounterStrikeSharp) -- In-game plugin providing modifiers, bot management, workshop map loading, and tip rotation

## Discord Bot

### Architecture

| File | Purpose |
|------|---------|
| `bot.py` | Entry point. Defines `CS2Bot` subclass, loads language file, syncs slash commands, runs a 30-second presence loop that queries the server via RCON for map name and player count |
| `cogs/cs2.py` | All slash commands live here as a single `CS2Commands` cog. Commands are grouped under `/cs`. Role check via `has_allowed_role()` decorator |
| `rcon.py` | Async Source RCON client (`RCONClient`). Implements the Source RCON protocol over TCP with `asyncio.open_connection`. Each `execute_rcon()` call opens a fresh connection, authenticates, sends one command, and disconnects |
| `config.py` | Loads `.env` via `python-dotenv` and exposes config as module-level constants |
| `lang/` | i18n JSON files (`fr.json`, `en.json`). Bot loads the file matching the `LANGUAGE` env var at startup |

### Request Flow

```
Discord slash command
  -> has_allowed_role() check (Discord role name match)
  -> _rcon() helper
  -> RCONClient: TCP connect -> auth packet -> command packet -> read response -> disconnect
  -> format and send response back to Discord
```

### Slash Commands

All commands are under the `/cs` group and require the configured Discord role.

| Command | Description |
|---------|-------------|
| `/cs exec <command>` | Execute an arbitrary console command via RCON |
| `/cs map <name_or_url>` | Change map (supports map names and Steam Workshop URLs) |
| `/cs maps` | List available playable maps (de\_, cs\_, ar\_ prefixes) |
| `/cs status` | Show server status and connected players |
| `/cs bot add [count]` | Add 1-10 bots |
| `/cs bot kick` | Kick all bots |
| `/cs bot difficulty <level>` | Set bot difficulty (Facile/Normal/Difficile/Expert) |

Mode switching is handled in-game by **GameModeManager** (`!mode` command), not the Discord bot. The bot previously had `/cs gungame`, `/cs competitive`, etc. but these were removed because they used raw `game_type/game_mode` RCON commands that bypassed GameModeManager and didn't load the correct plugins.

### Configuration

Environment variables loaded from `.env` (see `.env.example`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | -- | Discord bot token |
| `CS2_RCON_HOST` | No | `127.0.0.1` | CS2 server IP |
| `CS2_RCON_PORT` | No | `27015` | CS2 RCON port |
| `CS2_RCON_PASSWORD` | Yes | -- | CS2 RCON password |
| `ALLOWED_ROLE_NAME` | No | `Membres` | Discord role required to use commands |
| `LANGUAGE` | No | `fr` | Language code for bot responses (`fr`, `en`) |

### Build and Run

```bash
pip install -r requirements.txt
python bot.py
```

Dependencies: `discord.py>=2.3.0`, `python-dotenv>=1.0.0`

### Deployment

Runs as systemd service `disqt-bot` under user `cs` at `/home/cs/disqt-bot/`.

```bash
sudo systemctl restart disqt-bot
```

## DisqtModes Plugin

### Architecture

Single file plugin: `DisqtModes/DisqtModes.cs`

- Extends `BasePlugin` from CounterStrikeSharp
- Targets .NET 8.0
- Registers event handlers for `PlayerDeath`, `PlayerSpawn`, `PlayerConnectFull`
- Chat commands registered via `[ConsoleCommand]` attributes (players use `!command` in chat)

### Features

**Modifiers** (toggle on/off):
- `!headshot` -- Headshot-only mode (`mp_damage_headshot_only`)
- `!pistol` -- Pistol-only mode (strips primary weapons on spawn)
- `!vampire` -- Heal +25 HP on kill
- `!ammo` -- Infinite ammo (`sv_infinite_ammo 2`)

**Bot Management**:
- `!bot add [count] [ct|t]` -- Add bots (1-10, optional team)
- `!bot kick [ct|t]` -- Kick bots (optional team filter)
- `!bot difficulty [0-3]` -- Set difficulty (maps user 0-3 to CS2 internal 2-5, kicks and re-adds bots to apply)

**Other**:
- `!workshop <URL or ID>` -- Load a Steam Workshop map
- `!help` -- Show all available commands
- Tip rotation: broadcasts gameplay tips at configurable interval
- Welcome message for connecting players

### Plugin Configuration

`DisqtModes/config.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `language` | `fr` | Language code for in-game messages |
| `tip_interval_minutes` | `5` | Minutes between tip broadcasts |
| `show_welcome_message` | `true` | Show welcome message to connecting players |

Localization files: `DisqtModes/lang/fr.json`, `DisqtModes/lang/en.json`

### Build

```bash
cd DisqtModes && dotnet build -c Release
```

Output: `DisqtModes/bin/Release/net8.0/DisqtModes.dll`

### Deploy

Copy the built DLL and lang files to the CounterStrikeSharp plugins directory on the server, then restart:

```bash
ssh cs "cp /home/cs/disqt-bot/DisqtModes/bin/Release/net8.0/DisqtModes.dll /home/cs/cs2/game/csgo/addons/counterstrikesharp/plugins/DisqtModes/"
ssh cs "cp -r /home/cs/disqt-bot/DisqtModes/lang /home/cs/cs2/game/csgo/addons/counterstrikesharp/plugins/DisqtModes/"
ssh cs "/home/cs/stop-cs2.sh && sleep 3 && /home/cs/start-cs2.sh"
```

## Known Issues

### bot_add Sometimes Adds Extra Bots

`!bot add 1` can add 2 bots. Investigated mitigations (all applied but issue persists):
- `bot_join_after_player 0`
- `bot_quota 0` with `bot_quota_mode "normal"`
- `mp_autoteambalance 0` and `mp_limitteams 0`

Suspected cause: CS2 engine behavior or game mode configs resetting bot cvars.

### Weapon Strip During Iteration

Never modify weapon collections during iteration. The `StripPrimaryWeapon` method collects weapons into a list first with `.ToList()`, then removes them in a separate loop. This avoids a crash caused by modifying `MyWeapons` while enumerating it.
