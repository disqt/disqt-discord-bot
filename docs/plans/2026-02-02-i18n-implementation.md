# i18n & Tips System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add internationalization (English/French) to both Discord bot and CSS plugin, plus periodic in-game tips.

**Architecture:** JSON translation files in `lang/` directories. Server-wide language setting via config. CSS plugin adds tip timer and welcome message on player connect.

**Tech Stack:** Python 3 / discord.py (bot), C# / CounterStrikeSharp (plugin), JSON (translations)

---

## Part 1: Discord Bot i18n

### Task 1.1: Create French translation file for Discord bot

**Files:**
- Create: `lang/fr.json`

**Step 1: Create the lang directory and French translation file**

Create `lang/fr.json`:
```json
{
  "mode_competitive": "Mode **Compétitif** activé.",
  "mode_ffa": "Mode **FFA Deathmatch** activé.\n- Chacun pour soi\n- Respawn instantané\n- Munitions illimitées",
  "mode_arena": "Mode **Arena** activé.\n- Pas de limite de temps\n- Argent max\n- Armure + casque gratuits",
  "mode_gungame": "Mode **Arms Race (Gungame)** activé.",
  "mode_retake": "Mode **Retake** activé.\n- CTs reprennent le site\n- Équipes aléatoires chaque round",
  "mode_sandbox": "Mode **Sandbox** activé.\n- Temps infini\n- Grenades illimitées\n- Trajectoires visibles\n- Preview d'impact activée",
  "map_changing": "Changement de map vers **{map}**...",
  "command_executed": "Commande exécutée.",
  "bots_added": "**{count}** bot(s) ajouté(s).",
  "bots_kicked": "Tous les bots ont été virés.",
  "bots_difficulty": "Difficulté des bots: **{level}**",
  "error_rcon_auth": "Erreur d'authentification RCON.",
  "error_rcon_connection": "Erreur de connexion: {error}",
  "error_rcon": "Erreur RCON: {error}",
  "error_no_status": "Aucune réponse du serveur."
}
```

**Step 2: Commit**

```bash
git add lang/fr.json
git commit -m "feat(i18n): add French translation file for Discord bot"
```

---

### Task 1.2: Create English translation file for Discord bot

**Files:**
- Create: `lang/en.json`

**Step 1: Create English translation file**

Create `lang/en.json`:
```json
{
  "mode_competitive": "**Competitive** mode activated.",
  "mode_ffa": "**FFA Deathmatch** mode activated.\n- Free for all\n- Instant respawn\n- Unlimited ammo",
  "mode_arena": "**Arena** mode activated.\n- No time limit\n- Max money\n- Free armor + helmet",
  "mode_gungame": "**Arms Race (Gungame)** mode activated.",
  "mode_retake": "**Retake** mode activated.\n- CTs retake the site\n- Random teams each round",
  "mode_sandbox": "**Sandbox** mode activated.\n- Unlimited time\n- Unlimited grenades\n- Visible trajectories\n- Impact preview enabled",
  "map_changing": "Changing map to **{map}**...",
  "command_executed": "Command executed.",
  "bots_added": "**{count}** bot(s) added.",
  "bots_kicked": "All bots kicked.",
  "bots_difficulty": "Bot difficulty: **{level}**",
  "error_rcon_auth": "RCON authentication failed.",
  "error_rcon_connection": "Connection error: {error}",
  "error_rcon": "RCON error: {error}",
  "error_no_status": "No status response received."
}
```

**Step 2: Commit**

```bash
git add lang/en.json
git commit -m "feat(i18n): add English translation file for Discord bot"
```

---

### Task 1.3: Add language loading to bot.py

**Files:**
- Modify: `bot.py`

**Step 1: Add language loading after config import**

Add after line 10 (`from rcon import ...`):
```python
import json
from pathlib import Path
```

**Step 2: Add lang loading in CS2Bot.__init__**

Replace the `__init__` method:
```python
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
```

**Step 3: Commit**

```bash
git add bot.py
git commit -m "feat(i18n): load language file on bot startup"
```

---

### Task 1.4: Add LANGUAGE to config.py

**Files:**
- Modify: `config.py`
- Modify: `.env.example`

**Step 1: Add LANGUAGE to config.py**

Add at the end of `config.py`:
```python
LANGUAGE = os.getenv("LANGUAGE", "fr")
```

**Step 2: Add to .env.example**

Add line:
```
LANGUAGE=fr
```

**Step 3: Commit**

```bash
git add config.py .env.example
git commit -m "feat(i18n): add LANGUAGE config option"
```

---

### Task 1.5: Update cs2.py to use translations

**Files:**
- Modify: `cogs/cs2.py`

**Step 1: Update CS2Commands to use self.bot.lang**

Replace all hardcoded response strings with lang lookups. Key changes:

For `cs_competitive`:
```python
await interaction.followup.send(self.bot.lang["mode_competitive"])
```

For `cs_arena`:
```python
await interaction.followup.send(self.bot.lang["mode_arena"])
```

For `cs_gungame`:
```python
await interaction.followup.send(self.bot.lang["mode_gungame"])
```

For `cs_retake`:
```python
await interaction.followup.send(self.bot.lang["mode_retake"])
```

For `cs_ffa`:
```python
await interaction.followup.send(self.bot.lang["mode_ffa"])
```

For `cs_sandbox`:
```python
await interaction.followup.send(self.bot.lang["mode_sandbox"])
```

For `cs_map`:
```python
await interaction.followup.send(self.bot.lang["map_changing"].format(map=map_display))
```

For `cs_exec` (success):
```python
await interaction.followup.send(self.bot.lang["command_executed"])
```

For `bot_add`:
```python
await interaction.followup.send(self.bot.lang["bots_added"].format(count=count))
```

For `bot_kick`:
```python
await interaction.followup.send(self.bot.lang["bots_kicked"])
```

For `bot_difficulty`:
```python
await interaction.followup.send(self.bot.lang["bots_difficulty"].format(level=level.name))
```

For all error handlers:
```python
except RCONAuthError:
    await interaction.followup.send(self.bot.lang["error_rcon_auth"])
except RCONConnectionError as e:
    await interaction.followup.send(self.bot.lang["error_rcon_connection"].format(error=e))
except RCONError as e:
    await interaction.followup.send(self.bot.lang["error_rcon"].format(error=e))
```

For `cs_status` (no response):
```python
await interaction.followup.send(self.bot.lang["error_no_status"])
```

**Step 2: Verify syntax**

Run: `python -m py_compile cogs/cs2.py`

**Step 3: Commit**

```bash
git add cogs/cs2.py
git commit -m "feat(i18n): update Discord bot to use translation strings"
```

---

## Part 2: CSS Plugin i18n & Tips

### Task 2.1: Create French translation file for CSS plugin

**Files:**
- Create: `DisqtModes/lang/fr.json`

**Step 1: Create the file**

Create `DisqtModes/lang/fr.json`:
```json
{
  "prefix": "[Disqt]",

  "mode_competitive": "Mode Compétitif activé",
  "mode_ffa": "Mode FFA Deathmatch activé",
  "mode_arena": "Mode Arena activé",
  "mode_gungame": "Mode Arms Race activé",
  "mode_sandbox": "Mode Sandbox activé",

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
  "bots_kicked": "Tous les bots virés",
  "bots_difficulty": "Difficulté bots: {level}",

  "tip_headshot": "Astuce: !headshot active le mode headshot only",
  "tip_pistol": "Astuce: !pistol désactive les armes principales",
  "tip_vampire": "Astuce: !vampire te soigne 25HP à chaque kill",
  "tip_ammo": "Astuce: !ammo active les munitions illimitées",
  "tip_modes": "Astuce: Change de mode avec !ffa !arena !competitive !gungame",
  "tip_bots": "Astuce: !bot add 5 ajoute 5 bots, !bot kick les vire",
  "tip_sandbox": "Astuce: !sandbox pour t'entraîner aux grenades",
  "tip_help": "Astuce: !help pour voir toutes les commandes",

  "welcome": "Bienvenue! Tape !help pour voir les commandes disponibles.",

  "help_title": "=== Commandes disponibles ===",
  "help_modes": "Modes: !competitive !ffa !arena !gungame !sandbox",
  "help_modifiers": "Modifiers: !headshot !pistol !vampire !ammo",
  "help_bots": "Bots: !bot add [n] | !bot kick | !bot difficulty [0-3]"
}
```

**Step 2: Commit**

```bash
git add DisqtModes/lang/fr.json
git commit -m "feat(i18n): add French translation file for CSS plugin"
```

---

### Task 2.2: Create English translation file for CSS plugin

**Files:**
- Create: `DisqtModes/lang/en.json`

**Step 1: Create the file**

Create `DisqtModes/lang/en.json`:
```json
{
  "prefix": "[Disqt]",

  "mode_competitive": "Competitive mode activated",
  "mode_ffa": "FFA Deathmatch mode activated",
  "mode_arena": "Arena mode activated",
  "mode_gungame": "Arms Race mode activated",
  "mode_sandbox": "Sandbox mode activated",

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

  "tip_headshot": "Tip: !headshot enables headshot-only mode",
  "tip_pistol": "Tip: !pistol disables primary weapons",
  "tip_vampire": "Tip: !vampire heals you 25HP on each kill",
  "tip_ammo": "Tip: !ammo enables unlimited ammo",
  "tip_modes": "Tip: Switch modes with !ffa !arena !competitive !gungame",
  "tip_bots": "Tip: !bot add 5 adds 5 bots, !bot kick removes them",
  "tip_sandbox": "Tip: !sandbox for grenade practice",
  "tip_help": "Tip: !help to see all commands",

  "welcome": "Welcome! Type !help to see available commands.",

  "help_title": "=== Available commands ===",
  "help_modes": "Modes: !competitive !ffa !arena !gungame !sandbox",
  "help_modifiers": "Modifiers: !headshot !pistol !vampire !ammo",
  "help_bots": "Bots: !bot add [n] | !bot kick | !bot difficulty [0-3]"
}
```

**Step 2: Commit**

```bash
git add DisqtModes/lang/en.json
git commit -m "feat(i18n): add English translation file for CSS plugin"
```

---

### Task 2.3: Create config.json for CSS plugin

**Files:**
- Create: `DisqtModes/config.json`

**Step 1: Create the config file**

Create `DisqtModes/config.json`:
```json
{
  "language": "fr",
  "tip_interval_minutes": 5,
  "show_welcome_message": true
}
```

**Step 2: Commit**

```bash
git add DisqtModes/config.json
git commit -m "feat: add config.json for CSS plugin"
```

---

### Task 2.4: Rewrite CSS plugin with i18n and tips

**Files:**
- Modify: `DisqtModes/DisqtModes.cs`

**Step 1: Replace entire file with new implementation**

```csharp
using System.Text.Json;
using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API.Modules.Commands;
using CounterStrikeSharp.API.Modules.Timers;
using CounterStrikeSharp.API.Modules.Utils;

namespace DisqtModes;

public class PluginConfig
{
    public string Language { get; set; } = "fr";
    public int TipIntervalMinutes { get; set; } = 5;
    public bool ShowWelcomeMessage { get; set; } = true;
}

public class DisqtModes : BasePlugin
{
    public override string ModuleName => "Disqt Modes";
    public override string ModuleVersion => "1.1.0";
    public override string ModuleAuthor => "Disqt";

    private PluginConfig _config = new();
    private Dictionary<string, string> _lang = new();

    private bool _headshotOnly = false;
    private bool _pistolOnly = false;
    private bool _vampireMode = false;
    private bool _infiniteAmmo = false;

    private readonly string[] _tipKeys = {
        "tip_headshot", "tip_pistol", "tip_vampire", "tip_ammo",
        "tip_modes", "tip_bots", "tip_sandbox", "tip_help"
    };
    private int _tipIndex = 0;

    public override void Load(bool hotReload)
    {
        LoadConfig();
        LoadLanguage();

        Console.WriteLine($"[DisqtModes] Loaded with language: {_config.Language}");

        RegisterEventHandler<EventPlayerDeath>(OnPlayerDeath);
        RegisterEventHandler<EventPlayerSpawn>(OnPlayerSpawn);
        RegisterEventHandler<EventPlayerConnectFull>(OnPlayerConnect);

        // Start tip timer
        AddTimer(_config.TipIntervalMinutes * 60f, BroadcastTip, TimerFlags.REPEAT);
    }

    private void LoadConfig()
    {
        var configPath = Path.Combine(ModuleDirectory, "config.json");
        if (File.Exists(configPath))
        {
            var json = File.ReadAllText(configPath);
            _config = JsonSerializer.Deserialize<PluginConfig>(json) ?? new PluginConfig();
        }
    }

    private void LoadLanguage()
    {
        var langPath = Path.Combine(ModuleDirectory, "lang", $"{_config.Language}.json");
        if (File.Exists(langPath))
        {
            var json = File.ReadAllText(langPath);
            _lang = JsonSerializer.Deserialize<Dictionary<string, string>>(json) ?? new();
        }
    }

    private string L(string key) => _lang.TryGetValue(key, out var val) ? val : key;

    private string L(string key, params (string, object)[] replacements)
    {
        var text = L(key);
        foreach (var (placeholder, value) in replacements)
            text = text.Replace($"{{{placeholder}}}", value.ToString());
        return text;
    }

    private void Broadcast(string message)
    {
        Server.PrintToChatAll($" {L("prefix")} {message}");
    }

    private void BroadcastTip()
    {
        var humans = Utilities.GetPlayers().Count(p => p.IsValid && !p.IsBot);
        if (humans == 0) return;

        Broadcast(L(_tipKeys[_tipIndex]));
        _tipIndex = (_tipIndex + 1) % _tipKeys.Length;
    }

    // ========== EVENTS ==========

    private HookResult OnPlayerConnect(EventPlayerConnectFull @event, GameEventInfo info)
    {
        if (!_config.ShowWelcomeMessage) return HookResult.Continue;

        var player = @event.Userid;
        if (player == null || !player.IsValid || player.IsBot) return HookResult.Continue;

        AddTimer(2f, () => {
            if (player.IsValid)
                player.PrintToChat($" {L("prefix")} {L("welcome")}");
        });

        return HookResult.Continue;
    }

    // ========== HELP ==========

    [ConsoleCommand("css_help", "Show available commands")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnHelpCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;

        player.PrintToChat($" {L("prefix")} {L("help_title")}");
        player.PrintToChat($" {L("help_modes")}");
        player.PrintToChat($" {L("help_modifiers")}");
        player.PrintToChat($" {L("help_bots")}");
    }

    // ========== MODIFIERS ==========

    [ConsoleCommand("css_headshot", "Toggle headshot-only mode")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnHeadshotCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;
        _headshotOnly = !_headshotOnly;
        Server.ExecuteCommand($"mp_damage_headshot_only {(_headshotOnly ? 1 : 0)}");
        Broadcast(L(_headshotOnly ? "modifier_headshot_on" : "modifier_headshot_off"));
    }

    [ConsoleCommand("css_pistol", "Toggle pistol-only mode")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnPistolCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;
        _pistolOnly = !_pistolOnly;

        if (_pistolOnly)
        {
            foreach (var p in Utilities.GetPlayers().Where(p => p.IsValid && p.PawnIsAlive))
                StripPrimaryWeapon(p);
            Server.ExecuteCommand("mp_ct_default_primary \"\"");
            Server.ExecuteCommand("mp_t_default_primary \"\"");
        }
        else
        {
            Server.ExecuteCommand("mp_ct_default_primary \"weapon_m4a1\"");
            Server.ExecuteCommand("mp_t_default_primary \"weapon_ak47\"");
        }
        Broadcast(L(_pistolOnly ? "modifier_pistol_on" : "modifier_pistol_off"));
    }

    [ConsoleCommand("css_vampire", "Toggle vampire mode (heal on kill)")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnVampireCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;
        _vampireMode = !_vampireMode;
        Broadcast(L(_vampireMode ? "modifier_vampire_on" : "modifier_vampire_off"));
    }

    [ConsoleCommand("css_ammo", "Toggle infinite ammo")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnAmmoCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;
        _infiniteAmmo = !_infiniteAmmo;
        Server.ExecuteCommand($"sv_infinite_ammo {(_infiniteAmmo ? 2 : 0)}");
        Broadcast(L(_infiniteAmmo ? "modifier_ammo_on" : "modifier_ammo_off"));
    }

    // ========== GAME MODES ==========

    [ConsoleCommand("css_competitive", "Competitive mode")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnCompetitiveCommand(CCSPlayerController? player, CommandInfo command)
    {
        Server.ExecuteCommand("game_type 0; game_mode 1; mp_restartgame 1");
        Broadcast(L("mode_competitive"));
    }

    [ConsoleCommand("css_ffa", "FFA Deathmatch")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnFFACommand(CCSPlayerController? player, CommandInfo command)
    {
        var cmds = "game_type 1; game_mode 2; mp_teammates_are_enemies 1; " +
                   "mp_autoteambalance 0; mp_limitteams 0; mp_buytime 60000; " +
                   "sv_infinite_ammo 2; mp_randomspawn 1; " +
                   "mp_respawn_on_death_ct 1; mp_respawn_on_death_t 1; " +
                   "mp_respawnwavetime_ct 1; mp_respawnwavetime_t 1; mp_restartgame 1";
        Server.ExecuteCommand(cmds);
        Broadcast(L("mode_ffa"));
    }

    [ConsoleCommand("css_arena", "Arena mode (no time limit)")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnArenaCommand(CCSPlayerController? player, CommandInfo command)
    {
        var cmds = "game_type 0; game_mode 1; mp_maxrounds 30; " +
                   "mp_roundtime 60; mp_roundtime_defuse 60; mp_freezetime 3; " +
                   "mp_buytime 15; mp_startmoney 16000; mp_maxmoney 16000; " +
                   "mp_free_armor 2; mp_restartgame 1";
        Server.ExecuteCommand(cmds);
        Broadcast(L("mode_arena"));
    }

    [ConsoleCommand("css_gungame", "Arms Race")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnGungameCommand(CCSPlayerController? player, CommandInfo command)
    {
        Server.ExecuteCommand("game_type 1; game_mode 0; mp_restartgame 1");
        Broadcast(L("mode_gungame"));
    }

    [ConsoleCommand("css_sandbox", "Practice/sandbox mode")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnSandboxCommand(CCSPlayerController? player, CommandInfo command)
    {
        var cmds = "sv_cheats 1; bot_kick; mp_limitteams 0; mp_autoteambalance 0; " +
                   "mp_roundtime 60; mp_roundtime_defuse 60; mp_freezetime 0; " +
                   "mp_warmup_end; sv_infinite_ammo 1; ammo_grenade_limit_total 5; " +
                   "sv_grenade_trajectory 1; sv_grenade_trajectory_time 10; " +
                   "sv_grenade_trajectory_prac_pipreview 1; mp_buytime 9999; " +
                   "mp_buy_anywhere 1; mp_maxmoney 60000; mp_startmoney 60000; " +
                   "mp_restartgame 1";
        Server.ExecuteCommand(cmds);
        Broadcast(L("mode_sandbox"));
    }

    // ========== BOT COMMANDS ==========

    [ConsoleCommand("css_bot", "Bot management: add/kick/difficulty")]
    [CommandHelper(minArgs: 1, usage: "<add|kick|difficulty> [value]", whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnBotCommand(CCSPlayerController? player, CommandInfo command)
    {
        var action = command.GetArg(1).ToLower();
        switch (action)
        {
            case "add":
                int count = 1;
                if (command.ArgCount > 2) int.TryParse(command.GetArg(2), out count);
                count = Math.Clamp(count, 1, 10);
                for (int i = 0; i < count; i++) Server.ExecuteCommand("bot_add");
                Broadcast(L("bots_added", ("count", count)));
                break;
            case "kick":
                Server.ExecuteCommand("bot_kick");
                Broadcast(L("bots_kicked"));
                break;
            case "difficulty":
                if (command.ArgCount > 2)
                {
                    var level = command.GetArg(2);
                    Server.ExecuteCommand($"bot_difficulty {level}");
                    Broadcast(L("bots_difficulty", ("level", level)));
                }
                break;
        }
    }

    // ========== EVENT HANDLERS ==========

    private HookResult OnPlayerDeath(EventPlayerDeath @event, GameEventInfo info)
    {
        if (!_vampireMode) return HookResult.Continue;
        var attacker = @event.Attacker;
        if (attacker == null || !attacker.IsValid || !attacker.PawnIsAlive) return HookResult.Continue;
        if (attacker == @event.Userid) return HookResult.Continue;

        var pawn = attacker.PlayerPawn.Value;
        if (pawn == null) return HookResult.Continue;

        pawn.Health = Math.Min(pawn.Health + 25, 100);
        Utilities.SetStateChanged(pawn, "CBaseEntity", "m_iHealth");
        attacker.PrintToChat($" {L("prefix")} {L("vampire_heal")}");
        return HookResult.Continue;
    }

    private HookResult OnPlayerSpawn(EventPlayerSpawn @event, GameEventInfo info)
    {
        if (!_pistolOnly) return HookResult.Continue;
        var player = @event.Userid;
        if (player == null || !player.IsValid) return HookResult.Continue;
        AddTimer(0.1f, () => StripPrimaryWeapon(player));
        return HookResult.Continue;
    }

    private void StripPrimaryWeapon(CCSPlayerController player)
    {
        var pawn = player.PlayerPawn.Value;
        if (pawn?.WeaponServices == null) return;

        foreach (var weapon in pawn.WeaponServices.MyWeapons)
        {
            if (weapon.Value == null) continue;
            var weaponData = weapon.Value.As<CCSWeaponBase>().VData;
            if (weaponData?.GearSlot == gear_slot_t.GEAR_SLOT_RIFLE)
                weapon.Value.Remove();
        }
    }
}
```

**Step 2: Verify it compiles**

Run: `dotnet build -c Release` in DisqtModes folder

**Step 3: Commit**

```bash
git add DisqtModes/DisqtModes.cs
git commit -m "feat(i18n): rewrite CSS plugin with i18n, tips, and welcome message"
```

---

## Part 3: Build & Deploy

### Task 3.1: Build and deploy CSS plugin

**Step 1: Build**

```bash
cd DisqtModes
dotnet build -c Release
```

**Step 2: Deploy to server**

```bash
scp -P 24420 bin/Release/net8.0/DisqtModes.dll cs@disqt.com:/tmp/
scp -P 24420 config.json cs@disqt.com:/tmp/DisqtModes_config.json
scp -P 24420 -r lang cs@disqt.com:/tmp/DisqtModes_lang

ssh cs "sudo rm -rf /home/steam/cs2/game/csgo/addons/counterstrikesharp/plugins/DisqtModes/lang"
ssh cs "sudo mv /tmp/DisqtModes.dll /home/steam/cs2/game/csgo/addons/counterstrikesharp/plugins/DisqtModes/"
ssh cs "sudo mv /tmp/DisqtModes_config.json /home/steam/cs2/game/csgo/addons/counterstrikesharp/plugins/DisqtModes/config.json"
ssh cs "sudo mv /tmp/DisqtModes_lang /home/steam/cs2/game/csgo/addons/counterstrikesharp/plugins/DisqtModes/lang"
ssh cs "sudo chown -R steam:steam /home/steam/cs2/game/csgo/addons/counterstrikesharp/plugins/DisqtModes"
```

**Step 3: Reload plugin**

Via RCON or restart server.

---

### Task 3.2: Deploy Discord bot update

**Step 1: Push changes**

```bash
git push origin gamemode-overhaul
```

**Step 2: Create PR and merge**

**Step 3: Deploy on server**

```bash
ssh cs "cd ~/disqt-bot && git pull origin main && sudo systemctl restart disqt-bot"
```

---

## Verification Checklist

- [ ] Discord bot loads language file on startup
- [ ] Discord `/cs arena` shows French message
- [ ] Discord error messages are translated
- [ ] CSS plugin loads config.json
- [ ] CSS plugin loads lang/fr.json
- [ ] In-game `!arena` shows French message
- [ ] Tips broadcast every 5 minutes
- [ ] Welcome message shows on player connect
- [ ] `!help` shows command list
