using System.Text.Json;
using System.Text.RegularExpressions;
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
    public override string ModuleVersion => "1.2.0";
    public override string ModuleAuthor => "Disqt";

    private PluginConfig _config = new();
    private Dictionary<string, string> _lang = new();
    private List<string> _availableMaps = new();

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
        LoadMaps();

        Console.WriteLine($"[DisqtModes] Loaded with language: {_config.Language}, {_availableMaps.Count} maps");

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

    private void LoadMaps()
    {
        _availableMaps.Clear();

        // CS2 maps directory: game/csgo/maps/
        // ModuleDirectory is typically: game/csgo/addons/counterstrikesharp/plugins/DisqtModes
        var gameDir = Path.GetFullPath(Path.Combine(ModuleDirectory, "..", "..", "..", ".."));
        var mapsDir = Path.Combine(gameDir, "maps");

        if (Directory.Exists(mapsDir))
        {
            // Get .vpk files (CS2 map format)
            var mapFiles = Directory.GetFiles(mapsDir, "*.vpk")
                .Select(f => Path.GetFileNameWithoutExtension(f))
                .Where(m => m.StartsWith("de_") || m.StartsWith("cs_") || m.StartsWith("ar_"))
                .Where(m => !m.EndsWith("_vanity"))
                .Distinct()
                .OrderBy(m => m)
                .ToList();

            _availableMaps.AddRange(mapFiles);
        }

        // Fallback to default maps if none found
        if (_availableMaps.Count == 0)
        {
            _availableMaps.AddRange(new[] {
                "de_ancient", "de_anubis", "de_dust2", "de_inferno", "de_mirage",
                "de_nuke", "de_overpass", "de_train", "de_vertigo",
                "cs_italy", "cs_office", "ar_baggage", "ar_shoots"
            });
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
        player.PrintToChat($" {L("help_maps")}");
    }

    // ========== MAPS ==========

    [ConsoleCommand("css_maps", "List available maps")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnMapsCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;

        var defusal = _availableMaps.Where(m => m.StartsWith("de_")).ToList();
        var hostage = _availableMaps.Where(m => m.StartsWith("cs_")).ToList();
        var armsrace = _availableMaps.Where(m => m.StartsWith("ar_")).ToList();

        player.PrintToChat($" {L("prefix")} {L("maps_title")} ({_availableMaps.Count})");

        if (defusal.Count > 0)
            player.PrintToChat($" {L("maps_defusal")}: {string.Join(", ", defusal)}");
        if (hostage.Count > 0)
            player.PrintToChat($" {L("maps_hostage")}: {string.Join(", ", hostage)}");
        if (armsrace.Count > 0)
            player.PrintToChat($" {L("maps_armsrace")}: {string.Join(", ", armsrace)}");

        player.PrintToChat($" {L("maps_usage")}");
    }

    private static readonly Regex WorkshopUrlPattern = new(@"steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)", RegexOptions.Compiled);

    [ConsoleCommand("css_map", "Change map")]
    [CommandHelper(minArgs: 1, usage: "<mapname or workshop URL>", whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnMapCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;

        var input = command.GetArg(1);
        var workshopMatch = WorkshopUrlPattern.Match(input);

        if (workshopMatch.Success)
        {
            var workshopId = workshopMatch.Groups[1].Value;
            Broadcast(L("map_workshop_loading", ("id", workshopId)));
            Server.ExecuteCommand($"host_workshop_map {workshopId}");
        }
        else if (_availableMaps.Contains(input.ToLower()))
        {
            Broadcast(L("map_changing", ("map", input)));
            Server.ExecuteCommand($"changelevel {input}");
        }
        else
        {
            player.PrintToChat($" {L("prefix")} {L("map_not_found", ("map", input))}");
        }
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
