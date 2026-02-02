# Internationalization & Tips System Design

## Overview

Add i18n support to both the Discord bot and CSS plugin, plus periodic in-game tips to help players discover commands.

## Requirements

- Server-wide language setting (not per-player)
- Support English and French
- Periodic tips every 5 minutes (cycling through commands)
- Welcome message when player joins
- Fix French accent issues in existing messages

---

## File Structure

```
disqt-discord-bot/
  lang/
    en.json
    fr.json
  .env                  # Add LANGUAGE=fr
  cogs/cs2.py          # Update to use lang strings

DisqtModes/
  lang/
    en.json
    fr.json
  config.json          # { "language": "fr", "tip_interval_minutes": 5 }
  DisqtModes.cs        # Update to use lang strings + add tips
```

---

## Translation Files

### French (`fr.json`)

```json
{
  "prefix": "[Disqt]",

  "mode_competitive": "Mode **Compétitif** activé.",
  "mode_ffa": "Mode **FFA Deathmatch** activé.\n- Chacun pour soi\n- Respawn instantané\n- Munitions illimitées",
  "mode_arena": "Mode **Arena** activé.\n- Pas de limite de temps\n- Argent max\n- Armure + casque gratuits",
  "mode_gungame": "Mode **Arms Race (Gungame)** activé.",
  "mode_retake": "Mode **Retake** activé.\n- CTs reprennent le site\n- Équipes aléatoires chaque round",
  "mode_sandbox": "Mode **Sandbox** activé.\n- Temps infini\n- Grenades illimitées\n- Trajectoires visibles\n- Preview d'impact activée",

  "modifier_headshot_on": "Headshot only: ON",
  "modifier_headshot_off": "Headshot only: OFF",
  "modifier_pistol_on": "Pistol only: ON",
  "modifier_pistol_off": "Pistol only: OFF",
  "modifier_vampire_on": "Vampire: ON (+25HP par kill)",
  "modifier_vampire_off": "Vampire: OFF",
  "modifier_ammo_on": "Munitions illimitées: ON",
  "modifier_ammo_off": "Munitions illimitées: OFF",

  "vampire_heal": "+25 HP (vampire)",

  "bots_added": "{count} bot(s) ajouté(s)",
  "bots_kicked": "Tous les bots ont été virés",
  "bots_difficulty": "Difficulté bots: {level}",

  "map_changing": "Changement de map vers **{map}**...",
  "command_executed": "Commande exécutée.",

  "error_rcon_auth": "Erreur d'authentification RCON.",
  "error_rcon_connection": "Erreur de connexion: {error}",
  "error_rcon": "Erreur RCON: {error}",
  "error_no_status": "Aucune réponse du serveur.",

  "tip_headshot": "Astuce: !headshot active le mode headshot only",
  "tip_pistol": "Astuce: !pistol désactive les armes principales",
  "tip_vampire": "Astuce: !vampire te soigne 25HP à chaque kill",
  "tip_ammo": "Astuce: !ammo active les munitions illimitées",
  "tip_modes": "Astuce: Change de mode avec !ffa !arena !competitive !gungame",
  "tip_bots": "Astuce: !bot add 5 ajoute 5 bots, !bot kick les vire",
  "tip_sandbox": "Astuce: !sandbox pour t'entraîner aux grenades",
  "tip_help": "Astuce: !help pour voir toutes les commandes",

  "welcome": "Bienvenue! Tape !help pour voir les commandes disponibles.",

  "help_title": "Commandes disponibles:",
  "help_modes": "Modes: !competitive !ffa !arena !gungame !sandbox",
  "help_modifiers": "Modifiers: !headshot !pistol !vampire !ammo",
  "help_bots": "Bots: !bot add [n] | !bot kick | !bot difficulty [0-3]"
}
```

### English (`en.json`)

```json
{
  "prefix": "[Disqt]",

  "mode_competitive": "**Competitive** mode activated.",
  "mode_ffa": "**FFA Deathmatch** mode activated.\n- Free for all\n- Instant respawn\n- Unlimited ammo",
  "mode_arena": "**Arena** mode activated.\n- No time limit\n- Max money\n- Free armor + helmet",
  "mode_gungame": "**Arms Race (Gungame)** mode activated.",
  "mode_retake": "**Retake** mode activated.\n- CTs retake the site\n- Random teams each round",
  "mode_sandbox": "**Sandbox** mode activated.\n- Unlimited time\n- Unlimited grenades\n- Visible trajectories\n- Impact preview enabled",

  "modifier_headshot_on": "Headshot only: ON",
  "modifier_headshot_off": "Headshot only: OFF",
  "modifier_pistol_on": "Pistol only: ON",
  "modifier_pistol_off": "Pistol only: OFF",
  "modifier_vampire_on": "Vampire: ON (+25HP per kill)",
  "modifier_vampire_off": "Vampire: OFF",
  "modifier_ammo_on": "Infinite ammo: ON",
  "modifier_ammo_off": "Infinite ammo: OFF",

  "vampire_heal": "+25 HP (vampire)",

  "bots_added": "{count} bot(s) added",
  "bots_kicked": "All bots kicked",
  "bots_difficulty": "Bot difficulty: {level}",

  "map_changing": "Changing map to **{map}**...",
  "command_executed": "Command executed.",

  "error_rcon_auth": "RCON authentication failed.",
  "error_rcon_connection": "Connection error: {error}",
  "error_rcon": "RCON error: {error}",
  "error_no_status": "No status response received.",

  "tip_headshot": "Tip: !headshot enables headshot-only mode",
  "tip_pistol": "Tip: !pistol disables primary weapons",
  "tip_vampire": "Tip: !vampire heals you 25HP on each kill",
  "tip_ammo": "Tip: !ammo enables unlimited ammo",
  "tip_modes": "Tip: Switch modes with !ffa !arena !competitive !gungame",
  "tip_bots": "Tip: !bot add 5 adds 5 bots, !bot kick removes them",
  "tip_sandbox": "Tip: !sandbox for grenade practice",
  "tip_help": "Tip: !help to see all commands",

  "welcome": "Welcome! Type !help to see available commands.",

  "help_title": "Available commands:",
  "help_modes": "Modes: !competitive !ffa !arena !gungame !sandbox",
  "help_modifiers": "Modifiers: !headshot !pistol !vampire !ammo",
  "help_bots": "Bots: !bot add [n] | !bot kick | !bot difficulty [0-3]"
}
```

---

## CSS Plugin Config

**`config.json`:**
```json
{
  "language": "fr",
  "tip_interval_minutes": 5,
  "show_welcome_message": true
}
```

---

## CSS Plugin Implementation

### New Components

1. **Config class** - Load `config.json` on startup
2. **Lang class** - Load appropriate `lang/{language}.json`
3. **Tip timer** - Register timer on Load, broadcast tip every N minutes
4. **Welcome event** - Hook `EventPlayerConnectFull`, send welcome message
5. **!help command** - New command to list all available commands

### Tip Rotation

```csharp
private string[] _tipKeys = {
    "tip_headshot", "tip_pistol", "tip_vampire", "tip_ammo",
    "tip_modes", "tip_bots", "tip_sandbox", "tip_help"
};
private int _tipIndex = 0;

private void BroadcastTip()
{
    if (Utilities.GetPlayers().Count(p => p.IsValid && !p.IsBot) == 0)
        return; // Skip if no humans

    var tip = Lang[_tipKeys[_tipIndex]];
    Server.PrintToChatAll($" {Lang["prefix"]} {tip}");
    _tipIndex = (_tipIndex + 1) % _tipKeys.Length;
}
```

---

## Discord Bot Implementation

### Changes

1. **Add `LANGUAGE=fr` to `.env`**
2. **Create `lang/` directory** with JSON files
3. **Load lang on startup** in `bot.py`
4. **Pass lang to cog** via bot instance
5. **Update all responses** in `cogs/cs2.py` to use lang strings

### Example Usage

```python
# bot.py
import json

lang_code = os.getenv("LANGUAGE", "fr")
with open(f"lang/{lang_code}.json", encoding="utf-8") as f:
    bot.lang = json.load(f)

# cogs/cs2.py
await interaction.followup.send(self.bot.lang["mode_arena"])
```

---

## Summary

| Component | Changes |
|-----------|---------|
| CSS Plugin | Add config.json, lang/*.json, tip timer, welcome message, !help |
| Discord Bot | Add LANGUAGE env, lang/*.json, update all response strings |
| Both | Fix French accents, consistent key names |

## Next Steps

1. Create implementation plan with superpowers:writing-plans
2. Set up git worktree for isolated development
3. Implement CSS plugin i18n + tips
4. Implement Discord bot i18n
5. Test both components
6. Deploy
