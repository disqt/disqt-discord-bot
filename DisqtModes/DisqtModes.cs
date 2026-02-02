using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API.Modules.Commands;
using CounterStrikeSharp.API.Modules.Utils;

namespace DisqtModes;

public class DisqtModes : BasePlugin
{
    public override string ModuleName => "Disqt Modes";
    public override string ModuleVersion => "1.0.0";
    public override string ModuleAuthor => "Disqt";

    private bool _headshotOnly = false;
    private bool _pistolOnly = false;
    private bool _vampireMode = false;
    private bool _infiniteAmmo = false;

    public override void Load(bool hotReload)
    {
        Logger.LogInformation("DisqtModes loaded!");
        RegisterEventHandler<EventPlayerDeath>(OnPlayerDeath);
        RegisterEventHandler<EventPlayerSpawn>(OnPlayerSpawn);
    }

    // ========== MODIFIERS ==========

    [ConsoleCommand("css_headshot", "Toggle headshot-only mode")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnHeadshotCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;
        _headshotOnly = !_headshotOnly;
        Server.ExecuteCommand($"mp_damage_headshot_only {(_headshotOnly ? 1 : 0)}");
        Server.PrintToChatAll($" [Disqt] Headshot only: {(_headshotOnly ? "ON" : "OFF")}");
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
        Server.PrintToChatAll($" [Disqt] Pistol only: {(_pistolOnly ? "ON" : "OFF")}");
    }

    [ConsoleCommand("css_vampire", "Toggle vampire mode (heal on kill)")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnVampireCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;
        _vampireMode = !_vampireMode;
        Server.PrintToChatAll($" [Disqt] Vampire: {(_vampireMode ? "ON (+25HP on kill)" : "OFF")}");
    }

    [ConsoleCommand("css_ammo", "Toggle infinite ammo")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnAmmoCommand(CCSPlayerController? player, CommandInfo command)
    {
        if (player == null || !player.IsValid) return;
        _infiniteAmmo = !_infiniteAmmo;
        Server.ExecuteCommand($"sv_infinite_ammo {(_infiniteAmmo ? 2 : 0)}");
        Server.PrintToChatAll($" [Disqt] Infinite ammo: {(_infiniteAmmo ? "ON" : "OFF")}");
    }

    // ========== GAME MODES ==========

    [ConsoleCommand("css_competitive", "Competitive mode")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnCompetitiveCommand(CCSPlayerController? player, CommandInfo command)
    {
        Server.ExecuteCommand("game_type 0; game_mode 1; mp_restartgame 1");
        Server.PrintToChatAll(" [Disqt] Mode Competitif active");
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
        Server.PrintToChatAll(" [Disqt] Mode FFA Deathmatch active");
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
        Server.PrintToChatAll(" [Disqt] Mode Arena active");
    }

    [ConsoleCommand("css_gungame", "Arms Race")]
    [CommandHelper(whoCanExecute: CommandUsage.CLIENT_ONLY)]
    public void OnGungameCommand(CCSPlayerController? player, CommandInfo command)
    {
        Server.ExecuteCommand("game_type 1; game_mode 0; mp_restartgame 1");
        Server.PrintToChatAll(" [Disqt] Mode Arms Race active");
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
        Server.PrintToChatAll(" [Disqt] Mode Sandbox active");
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
                Server.PrintToChatAll($" [Disqt] {count} bot(s) ajoute(s)");
                break;
            case "kick":
                Server.ExecuteCommand("bot_kick");
                Server.PrintToChatAll(" [Disqt] Tous les bots vires");
                break;
            case "difficulty":
                if (command.ArgCount > 2)
                {
                    Server.ExecuteCommand($"bot_difficulty {command.GetArg(2)}");
                    Server.PrintToChatAll($" [Disqt] Difficulte bots: {command.GetArg(2)}");
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
        attacker.PrintToChat(" [Disqt] +25 HP (vampire)");
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
